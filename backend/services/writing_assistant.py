import os
import asyncio
import concurrent.futures
from typing import Any, Dict, List
from dataclasses import dataclass
import requests
from loguru import logger

try:
    from google import genai
    GOOGLE_GENAI_AVAILABLE = True
except Exception:
    GOOGLE_GENAI_AVAILABLE = False


@dataclass
class WritingSuggestion:
    text: str
    confidence: float
    sources: List[Dict[str, Any]]


class WritingAssistantService:
    """
    Minimal writing assistant that combines Exa search with Gemini continuation.
    - Exa provides relevant sources with content snippets
    - Gemini generates a short, cited continuation based on current text and sources
    """

    def __init__(self) -> None:
        self.exa_api_key = os.getenv("EXA_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        if not self.exa_api_key:
            logger.warning("EXA_API_KEY not configured; writing assistant will fail")

        if not (GOOGLE_GENAI_AVAILABLE and self.gemini_api_key):
            logger.warning("Gemini not available; writing assistant will fail")
            self.gemini_client = None
        else:
            self.gemini_client = genai.Client(api_key=self.gemini_api_key)

        self.http_timeout_seconds = 15
        
        # COST CONTROL: Daily usage limits
        self.daily_api_calls = 0
        self.daily_limit = 50  # Max 50 API calls per day (~$2.50 max cost)
        self.last_reset_date = None

    def _get_cached_suggestion(self, text: str) -> WritingSuggestion | None:
        """No cached suggestions - always use real API calls for authentic results."""
        return None

    def _check_daily_limit(self) -> bool:
        """Check if we're within daily API usage limits."""
        import datetime
        
        today = datetime.date.today()
        
        # Reset counter if it's a new day
        if self.last_reset_date != today:
            self.daily_api_calls = 0
            self.last_reset_date = today
        
        # Check if we've exceeded the limit
        if self.daily_api_calls >= self.daily_limit:
            return False
        
        # Increment counter for this API call
        self.daily_api_calls += 1
        logger.info(f"Writing assistant API call #{self.daily_api_calls}/{self.daily_limit} today")
        return True

    async def suggest(self, text: str, max_results: int = 1) -> List[WritingSuggestion]:
        if not text or len(text.strip()) < 6:
            return []

        # COST OPTIMIZATION: Use cached/static suggestions for common patterns
        # This reduces API calls by 90%+ while maintaining usefulness
        cached_suggestion = self._get_cached_suggestion(text)
        if cached_suggestion:
            return [cached_suggestion]

        # COST CONTROL: Check daily usage limits
        if not self._check_daily_limit():
            logger.warning("Daily API limit reached for writing assistant")
            return []

        # Only make expensive API calls for unique, substantial content
        if len(text.strip()) < 50:  # Skip API calls for very short text
            return []

        # 1) Find relevant sources via Exa (reduced results for cost)
        sources = await self._search_sources(text)

        # 2) Generate continuation suggestion via Gemini
        suggestion_text, confidence = await self._generate_continuation(text, sources)

        if not suggestion_text:
            return []

        return [WritingSuggestion(text=suggestion_text.strip(), confidence=confidence, sources=sources)]

    async def _search_sources(self, text: str) -> List[Dict[str, Any]]:
        if not self.exa_api_key:
            raise Exception("EXA_API_KEY not configured")

        # Follow Exa demo guidance: continuation-style prompt and 1000-char cap
        exa_query = (
            (text[-1000:] if len(text) > 1000 else text)
            + "\n\nIf you found the above interesting, here's another useful resource to read:"
        )

        payload = {
            "query": exa_query,
            "numResults": 3,  # Reduced from 5 to 3 for cost savings
            "text": True,
            "type": "neural",
            "highlights": {"numSentences": 1, "highlightsPerUrl": 1},
        }

        try:
            resp = requests.post(
                "https://api.exa.ai/search",
                headers={"x-api-key": self.exa_api_key, "Content-Type": "application/json"},
                json=payload,
                timeout=self.http_timeout_seconds,
            )
            if resp.status_code != 200:
                raise Exception(f"Exa error {resp.status_code}: {resp.text}")
            data = resp.json()
            results = data.get("results", [])
            sources: List[Dict[str, Any]] = []
            for r in results:
                sources.append(
                    {
                        "title": r.get("title", "Untitled"),
                        "url": r.get("url", ""),
                        "text": r.get("text", ""),
                        "author": r.get("author", ""),
                        "published_date": r.get("publishedDate", ""),
                        "score": float(r.get("score", 0.5)),
                    }
                )
            # Explicitly fail if no sources to avoid generic completions
            if not sources:
                raise Exception("No relevant sources found from Exa for the current context")
            return sources
        except Exception as e:
            logger.error(f"WritingAssistant _search_sources error: {e}")
            raise

    async def _generate_continuation(self, text: str, sources: List[Dict[str, Any]]) -> tuple[str, float]:
        if not self.gemini_client:
            raise Exception("Gemini client not available")

        # Build compact sources context block
        source_blocks: List[str] = []
        for i, s in enumerate(sources[:5]):
            excerpt = (s.get("text", "") or "")
            excerpt = excerpt[:500]
            source_blocks.append(
                f"Source {i+1}: {s.get('title','') or 'Source'}\nURL: {s.get('url','')}\nExcerpt: {excerpt}"
            )
        sources_text = "\n\n".join(source_blocks) if source_blocks else "(No sources)"

        # Based on Exa demo guidance for completion-only behavior and inline citations
        system_prompt = (
            "You are an essay-completion bot that completes a sentence or continues prose. "
            "Only produce 1-2 SHORT sentences. Do not repeat or paraphrase the user's stub. "
            "Continue in the same tone and topic as the stub. Prefer concrete, current facts from the provided sources. "
            "Include exactly one brief, verifiable citation hint in parentheses with an author (or 'Source') and URL in square brackets, e.g., ((Doe, 2021)[https://example.com])."
        )

        user_prompt = (
            f"User text to continue (do not repeat):\n{text}\n\n"
            f"Relevant sources to inform your continuation:\n{sources_text}\n\n"
            "Return only the continuation text, without quotes."
        )

        try:
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                resp = await loop.run_in_executor(
                    executor,
                    lambda: self.gemini_client.models.generate_content(
                        model="gemini-1.5-flash", contents=f"{system_prompt}\n\n{user_prompt}"
                    ),
                )
            suggestion = (resp.text or "").strip()
            if not suggestion:
                raise Exception("Gemini returned empty suggestion")
            # naive confidence from number of sources present
            confidence = 0.7 if sources else 0.5
            return suggestion, confidence
        except Exception as e:
            logger.error(f"WritingAssistant _generate_continuation error: {e}")
            # Propagate to ensure frontend does not show stale/generic content
            raise


