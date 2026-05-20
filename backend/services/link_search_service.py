"""
Link Search Service — Internal & external link discovery and rewording.

Provides:
  - Internal link search (Exa include_domains scoped to user's website)
  - External link search (Exa general search, optionally excluding user's domain)
  - Reword-with-links (LLM embeds selected links naturally into section/selected text)
"""

import re
from typing import Dict, Any, List, Optional
from loguru import logger

from services.llm_providers.main_text_generation import llm_text_gen


LINK_SEARCH_SYSTEM_PROMPT = """You are an SEO and content linking expert. Your task is to naturally incorporate provided links into text using markdown link syntax, following the best practices below.

## SEO Linking Best Practices

1. **Anchor text must be descriptive and keyword-rich.** Use the surrounding context to create natural, specific anchor text. Never use "click here", "read more", "learn more", or bare URLs as anchors.
   - GOOD: [HubSpot's content marketing statistics](url) — descriptive, includes keywords
   - BAD: [click here](url) — vague, no SEO value
   - BAD: [https://example.com](url) — raw URL, harmful to readability

2. **Match link type to content context:**
   - Internal links: Point anchor text at relevant topic keywords that describe the destination page
   - External links: Cite authoritative sources (research, official docs, industry leaders) using the source name or key finding as anchor text

3. **Link equity (PageRank) distribution:** Spread links naturally. Aim for 1-2 links per paragraph at most. Don't cluster all links together.

4. **Preserve the original text's meaning, tone, structure, and approximate length.** You are inserting links, NOT rewriting the content.

5. **If selected_text is provided, ONLY modify that specific portion.** The rest of section_text must remain IDENTICAL — character-for-character unchanged.

6. **If selected_text is NOT provided, you may insert links throughout the entire section_text.**

7. **Link placement should feel earned, not forced.** Only insert a link where a reader would genuinely want to learn more. If a link doesn't naturally fit, skip it.

8. **Prioritize high-authority external sources** (research papers, official documentation, industry leaders) when linking externally.

9. **Return ONLY the reworded text.** No explanations, no preamble, no markdown code fences. Just the text with [anchor text](url) links embedded."""


LINK_SEARCH_USER_PROMPT = """## Section Heading
{section_heading}

## Full Section Text
{section_text}

{selected_text_block}

## Available Links to Incorporate
{links}

## Instructions
Carefully read the section text above and insert the most relevant links from the "Available Links" list using markdown format: [descriptive anchor text](url).

Remember:
- Use keyword-rich, descriptive anchor text (NOT "click here" or bare URLs)
- Only insert links where they naturally enhance the reader's experience
- Preserve the original text's meaning, tone, and structure
- Aim for 1-2 links per paragraph maximum
- If no links fit naturally, return the text unchanged

Return ONLY the text with links embedded. No explanations."""


def _extract_domain(url: str) -> str:
    """Extract the registered domain from a URL.

    Handles common multi-part TLDs like .co.uk, .com.au, .co.jp, etc.
    Falls back to last two parts for unknown TLDs.
    """
    url = url.strip()
    if not url:
        return ""
    # Add protocol if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    # Remove protocol
    domain = re.sub(r"^https?://", "", url)
    # Remove path and query
    domain = domain.split("/")[0].split("?")[0].split("#")[0]
    # Remove port
    domain = domain.split(":")[0]
    # Remove userinfo (user:pass@)
    if "@" in domain:
        domain = domain.split("@")[-1]
    domain = domain.lower().strip()
    if not domain:
        return ""

    # Known multi-part TLDs (common ccTLDs with second-level domains)
    multi_part_tlds = {
        "co.uk", "org.uk", "ac.uk", "gov.uk", "co.jp", "or.jp", "ne.jp", "ac.jp",
        "co.au", "com.au", "org.au", "net.au", "co.nz", "net.nz", "org.nz",
        "co.in", "net.in", "org.in", "ac.in", "co.kr", "co.za", "org.za", "web.za",
        "com.br", "com.mx", "com.ar", "com.sg", "com.hk", "com.tw", "com.my",
        "com.cn", "org.cn", "net.cn", "ac.ke", "co.ke",
    }
    parts = domain.split(".")
    if len(parts) < 2:
        return domain

    # Check if last two parts form a known multi-part TLD
    last_two = ".".join(parts[-2:])
    if last_two in multi_part_tlds and len(parts) > 2:
        # e.g. blog.example.co.uk → example.co.uk
        return ".".join(parts[-3:])
    # Default: last two parts (example.com)
    return ".".join(parts[-2:])


def _filter_search_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter out results with empty URLs or missing essential fields."""
    filtered = []
    for r in results:
        url = r.get("url", "").strip()
        title = r.get("title", "").strip() or "Untitled"
        if url:
            filtered.append({
                "title": title,
                "url": url,
                "text": r.get("text", ""),
                "publishedDate": r.get("publishedDate", ""),
                "author": r.get("author", ""),
                "score": r.get("score", 0.5),
            })
    return filtered


class LinkSearchService:
    """Service for finding internal/external links and rewording text to include them."""

    async def search_internal(
        self,
        query: str,
        site_url: str,
        user_id: Optional[str] = None,
        num_results: int = 5,
    ) -> Dict[str, Any]:
        """
        Search for internal links (from the user's own website).

        Args:
            query: Search query (section topic/heading)
            site_url: User's website URL to scope search via include_domains
            user_id: Optional user ID for subscription tracking
            num_results: Number of results to return

        Returns:
            {"results": [...], "warnings": [...]}
        """
        warnings = []
        domain = _extract_domain(site_url)

        if not domain:
            return {
                "results": [],
                "warnings": [f"Could not extract domain from '{site_url}'"],
            }

        try:
            from services.blog_writer.research.exa_provider import ExaResearchProvider

            provider = ExaResearchProvider()
            results = await provider.simple_search(
                query=query,
                num_results=num_results,
                user_id=user_id,
                include_domains=[domain],
            )
            filtered = _filter_search_results(results)
            return {"results": filtered, "warnings": warnings}

        except ImportError:
            msg = "Exa provider not available — link search requires Exa API."
            logger.warning(f"[LinkSearchService] {msg}")
            warnings.append(msg)
            return {"results": [], "warnings": warnings}
        except Exception as e:
            logger.error(f"[LinkSearchService] Internal link search failed: {e}")
            warnings.append(f"Search failed: {str(e)}")
            return {"results": [], "warnings": warnings}

    async def search_external(
        self,
        query: str,
        site_url: Optional[str] = None,
        user_id: Optional[str] = None,
        num_results: int = 5,
    ) -> Dict[str, Any]:
        """
        Search for external links (optionally excluding the user's own domain).

        Args:
            query: Search query
            site_url: User's website URL — results from this domain will be excluded
            user_id: Optional user ID for subscription tracking
            num_results: Number of results to return

        Returns:
            {"results": [...], "warnings": [...]}
        """
        warnings = []
        exclude_domains = None

        if site_url:
            domain = _extract_domain(site_url)
            if domain:
                exclude_domains = [domain]

        try:
            from services.blog_writer.research.exa_provider import ExaResearchProvider

            provider = ExaResearchProvider()
            results = await provider.simple_search(
                query=query,
                num_results=num_results,
                user_id=user_id,
                exclude_domains=exclude_domains,
            )
            filtered = _filter_search_results(results)
            return {"results": filtered, "warnings": warnings}

        except ImportError:
            msg = "Exa provider not available — link search requires Exa API."
            logger.warning(f"[LinkSearchService] {msg}")
            warnings.append(msg)
            return {"results": [], "warnings": warnings}
        except Exception as e:
            logger.error(f"[LinkSearchService] External link search failed: {e}")
            warnings.append(f"Search failed: {str(e)}")
            return {"results": [], "warnings": warnings}

    def reword_with_links(
        self,
        section_text: str,
        links: List[Dict[str, str]],
        section_heading: Optional[str] = None,
        selected_text: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Use LLM to reword text, naturally incorporating the selected links.

        Args:
            section_text: Full section text
            links: List of {"url": str, "title": str} dicts
            section_heading: Optional section heading for context
            selected_text: If provided, only reword this portion of the text
            user_id: Optional user ID for LLM routing

        Returns:
            {"reworded_text": str, "warnings": [...]}
        """
        warnings = []

        if not links:
            return {
                "reworded_text": section_text,
                "warnings": ["No links provided — returning original text unchanged."],
            }

        links_text = "\n".join(
            f"- [{link.get('title', 'Untitled')}]({link.get('url', '')}) — {link.get('title', '')}"
            for link in links
        )

        selected_text_block = ""
        if selected_text:
            selected_text_block = f"Selected text to reword (keep surrounding text unchanged):\n{selected_text}"

        prompt = LINK_SEARCH_USER_PROMPT.format(
            section_heading=section_heading or "Blog Section",
            section_text=section_text[:3000],
            selected_text_block=selected_text_block,
            links=links_text,
        )

        try:
            result = llm_text_gen(
                prompt=prompt,
                system_prompt=LINK_SEARCH_SYSTEM_PROMPT,
                json_struct=None,
                max_tokens=3000,
                user_id=user_id,
            )

            raw = result.get("text", "") if isinstance(result, dict) else str(result) if result else ""
            raw = raw.strip()

            # Strip markdown code fences if the LLM wrapped the output
            if raw.startswith("```"):
                match = re.search(r"```(?:markdown|md)?\s*(.*?)\s*```", raw, re.DOTALL)
                if match:
                    raw = match.group(1).strip()

            if not raw:
                warnings.append("LLM returned empty reworded text — returning original.")
                return {"reworded_text": section_text, "warnings": warnings}

            logger.info(f"[LinkSearchService] Reworded text: {len(raw)} chars, {len(links)} links provided")
            return {"reworded_text": raw, "warnings": warnings}

        except Exception as e:
            logger.error(f"[LinkSearchService] Reword failed: {e}")
            warnings.append(f"Reword failed: {str(e)}")
            return {"reworded_text": section_text, "warnings": warnings}


# Per-user service instances (not strictly needed since service is stateless,
# but kept for consistency with chart_service pattern)
_link_search_instances: Dict[str, LinkSearchService] = {}


def get_link_search_service(user_id: Optional[str] = None) -> LinkSearchService:
    """Get or create LinkSearchService for the given user."""
    cache_key = user_id or "default"
    if cache_key not in _link_search_instances:
        _link_search_instances[cache_key] = LinkSearchService()
    return _link_search_instances[cache_key]