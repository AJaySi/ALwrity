"""Blog SEO Recommendation Applier

Applies actionable SEO recommendations to existing blog content using the
provider-agnostic `llm_text_gen` dispatcher. Ensures GPT_PROVIDER parity.

Key design principles:
- Make TARGETED edits, not full rewrites
- Preserve existing content structure and factual claims
- Only modify sections that have applicable recommendations
- Never fabricate statistics, case studies, or citations
- Ground changes in research sources when available
"""

import asyncio
from typing import Dict, Any, List
from utils.logger_utils import get_service_logger

from services.llm_providers.main_text_generation import llm_text_gen


logger = get_service_logger("blog_seo_recommendation_applier")


class BlogSEORecommendationApplier:
    """Apply actionable SEO recommendations to blog content with targeted edits."""

    def __init__(self):
        logger.debug("Initialized BlogSEORecommendationApplier")

    async def apply_recommendations(self, payload: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
        """Apply recommendations and return updated content."""
        
        if not user_id:
            raise ValueError("user_id is required for subscription checking. Please provide Clerk user ID.")

        title = payload.get("title", "Untitled Blog")
        introduction = payload.get("introduction") or ""
        sections: List[Dict[str, Any]] = payload.get("sections", [])
        outline = payload.get("outline", [])
        research = payload.get("research", {})
        recommendations = payload.get("recommendations", [])
        persona = payload.get("persona", {})
        tone = payload.get("tone")
        audience = payload.get("audience")
        competitive_advantage = payload.get("competitive_advantage", "")

        if not sections:
            return {"success": False, "error": "No sections provided for recommendation application"}

        if not recommendations:
            logger.warning("apply_recommendations called without recommendations")
            return {"success": True, "title": title, "sections": sections, "applied": []}

        # Determine which sections actually need changes based on recommendations
        sections_to_edit = self._identify_affected_sections(sections, recommendations)

        prompt = self._build_prompt(
            title=title,
            introduction=introduction,
            sections=sections,
            sections_to_edit=sections_to_edit,
            outline=outline,
            research=research,
            recommendations=recommendations,
            persona=persona,
            tone=tone,
            audience=audience,
            competitive_advantage=competitive_advantage,
        )

        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "introduction": {"type": "string"},
                "sections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "heading": {"type": "string"},
                            "content": {"type": "string"},
                            "notes": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["id", "heading", "content"],
                    },
                },
                "applied_recommendations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "category": {"type": "string"},
                            "summary": {"type": "string"},
                        },
                    },
                },
            },
            "required": ["sections"],
        }

        logger.info("Applying SEO recommendations via llm_text_gen (targeted edit mode)")

        result = await asyncio.to_thread(
            llm_text_gen,
            prompt,
            None,
            schema,
            user_id,
            max_tokens=8192,
        )

        if not result or result.get("error"):
            error_msg = result.get("error", "Unknown error") if result else "No response from text generator"
            logger.error(f"SEO recommendation application failed: {error_msg}")
            return {"success": False, "error": error_msg}

        raw_sections = result.get("sections", []) or []
        normalized_sections: List[Dict[str, Any]] = []

        if len(raw_sections) != len(sections):
            logger.warning(
                f"LLM returned {len(raw_sections)} sections but {len(sections)} were sent. "
                "Extra sections will be ignored; missing sections fall back to original content."
            )

        updated_map: Dict[str, Dict[str, Any]] = {}
        for updated in raw_sections:
            section_id = str(
                updated.get("id")
                or updated.get("section_id")
                or updated.get("heading")
                or ""
            ).strip()

            if not section_id:
                continue

            heading = (
                updated.get("heading")
                or updated.get("title")
                or section_id
            )

            content_text = updated.get("content", "")
            if isinstance(content_text, list):
                content_text = "\n\n".join(str(p).strip() for p in content_text if p)

            updated_map[section_id] = {
                "id": section_id,
                "heading": heading,
                "content": str(content_text).strip(),
                "notes": updated.get("notes", []),
            }

        if not updated_map and raw_sections:
            logger.warning("Updated sections missing identifiers; falling back to positional mapping")

        for index, original in enumerate(sections):
            fallback_id = str(
                original.get("id")
                or original.get("section_id")
                or f"section_{index + 1}"
            ).strip()

            mapped = updated_map.get(fallback_id)

            if not mapped and raw_sections:
                candidate = raw_sections[index] if index < len(raw_sections) else {}
                heading = (
                    candidate.get("heading")
                    or candidate.get("title")
                    or original.get("heading")
                    or original.get("title")
                    or f"Section {index + 1}"
                )
                content_text = candidate.get("content") or original.get("content", "")
                if isinstance(content_text, list):
                    content_text = "\n\n".join(str(p).strip() for p in content_text if p)
                mapped = {
                    "id": fallback_id,
                    "heading": heading,
                    "content": str(content_text).strip(),
                    "notes": candidate.get("notes", []),
                }

            if not mapped:
                mapped = {
                    "id": fallback_id,
                    "heading": original.get("heading") or original.get("title") or f"Section {index + 1}",
                    "content": str(original.get("content", "")).strip(),
                    "notes": original.get("notes", []),
                }

            normalized_sections.append(mapped)

        applied = result.get("applied_recommendations", [])

        logger.info("SEO recommendations applied successfully")

        updated_introduction = result.get("introduction") or ""
        if updated_introduction and updated_introduction != introduction:
            logger.info(f"Introduction updated: {len(updated_introduction)} chars")
        elif not updated_introduction:
            updated_introduction = introduction

        return {
            "success": True,
            "title": result.get("title", title),
            "introduction": updated_introduction,
            "sections": normalized_sections,
            "applied": applied,
        }

    def _identify_affected_sections(self, sections: List[Dict[str, Any]], recommendations: List[Dict[str, Any]]) -> List[str]:
        """Identify which section IDs are likely affected by the recommendations.
        
        Maps recommendation categories to section headings for targeted editing.
        Returns a list of section IDs that should be edited.
        """
        affected_ids = set()
        
        for rec in recommendations:
            category = (rec.get("category") or "").lower()
            rec_text = (rec.get("recommendation") or "").lower()
            
            # Structure recommendations affect first/last sections or all sections
            if category == "structure":
                if sections:
                    affected_ids.add(str(sections[0].get("id", "section_1")))
                    affected_ids.add(str(sections[-1].get("id", f"section_{len(sections)}")))
                    # "Add more sections" or "too many sections" affects all
                    if "more section" in rec_text or "combine" in rec_text or "flow" in rec_text:
                        for s in sections:
                            affected_ids.add(str(s.get("id", "")))
                    continue
            
            # Keyword recommendations affect all sections (keywords should be spread)
            if category == "keywords":
                for s in sections:
                    affected_ids.add(str(s.get("id", "")))
                continue
            
            # Readability affects all sections
            if category == "readability":
                for s in sections:
                    affected_ids.add(str(s.get("id", "")))
                continue
            
            # Content quality — try to match recommendation to specific section headings
            if category in ("content quality", "content", "seo"):
                heading_keywords = {
                    s.get("heading", "").lower(): str(s.get("id", ""))
                    for s in sections
                }
                matched = False
                for heading_lower, section_id in heading_keywords.items():
                    rec_words = rec_text.split()
                    if any(word in heading_lower for word in rec_words if len(word) > 3):
                        affected_ids.add(section_id)
                        matched = True
                if not matched:
                    # Affect first and last sections (intro/conclusion) as common targets
                    if sections:
                        affected_ids.add(str(sections[0].get("id", "section_1")))
                        affected_ids.add(str(sections[-1].get("id", f"section_{len(sections)}")))
        
        # Filter out empty IDs and return
        return [sid for sid in affected_ids if sid]

    def _build_prompt(
        self,
        *,
        title: str,
        introduction: str,
        sections: List[Dict[str, Any]],
        sections_to_edit: List[str],
        outline: List[Dict[str, Any]],
        research: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
        persona: Dict[str, Any],
        tone: str | None,
        audience: str | None,
        competitive_advantage: str = "",
    ) -> str:
        """Construct prompt for applying targeted recommendations."""

        # Build research context block
        research_block = ""
        keyword_analysis = research.get("keyword_analysis", {}) if research else {}
        primary_keywords = ", ".join(keyword_analysis.get("primary", [])[:8]) or "None"
        competitor_analysis = research.get("competitor_analysis", {}) if research else {}
        search_queries = research.get("search_queries", []) if research else []
        suggested_angles = research.get("suggested_angles", []) if research else []
        content_gaps = competitor_analysis.get("content_gaps", []) if competitor_analysis else []
        competitive_advantages = competitor_analysis.get("competitive_advantages", []) if competitor_analysis else []
        
        research_block += f"\nPRIMARY KEYWORDS: {primary_keywords}"
        if content_gaps:
            research_block += f"\nCONTENT GAPS (address these in your edits): {', '.join(content_gaps[:5])}"
        if competitive_advantages:
            research_block += f"\nKEY DIFFERENTIATORS (emphasize these): {', '.join(competitive_advantages[:3])}"
        if competitive_advantage:
            research_block += f"\nPRIMARY ADVANTAGE: {competitive_advantage}"
        if search_queries:
            research_block += f"\nTARGET SEARCH QUERIES: {', '.join(search_queries[:5])}"
        if suggested_angles:
            research_block += f"\nCONTENT ANGLES: {', '.join(suggested_angles[:3])}"

        # Build per-section content with edit markers
        sections_content = []
        for section in sections:
            section_id = str(section.get("id", "section"))
            heading = section.get("heading", "Untitled")
            content = section.get("content", "")
            needs_edit = section_id in sections_to_edit
            
            section_text = f"--- SECTION (ID: {section_id}, Heading: \"{heading}\")"
            if needs_edit:
                section_text += " [NEEDS EDITS based on recommendations]"
            else:
                section_text += " [KEEP AS-IS - no changes needed]"
            section_text += f" ---\n{content}\n"
            sections_content.append(section_text)
        
        sections_str = "\n\n".join(sections_content)

        # Build outline with subheadings and key points
        outline_parts = []
        for item in outline:
            heading = item.get("heading", "Section")
            target_words = item.get("target_words", "N/A")
            subheadings = item.get("subheadings", [])
            key_points = item.get("key_points", [])
            line = f"- {heading} (Target: {target_words} words)"
            if subheadings:
                line += f" | Subheadings: {', '.join(subheadings[:4])}"
            if key_points:
                line += f" | Key points: {', '.join(key_points[:4])}"
            outline_parts.append(line)
        outline_str = "\n".join(outline_parts) if outline_parts else "No outline supplied"

        recommendations_str = []
        for rec in recommendations:
            recommendations_str.append(
                f"Category: {rec.get('category', 'General')} | Priority: {rec.get('priority', 'Medium')}\n"
                f"Recommendation: {rec.get('recommendation', '')}\n"
                f"Impact: {rec.get('impact', '')}\n"
            )

        persona_str = (
            f"Persona: {persona}\n"
            if persona
            else ""
        )

        style_guidance = []
        if tone:
            style_guidance.append(f"Desired tone: {tone}")
        if audience:
            style_guidance.append(f"Target audience: {audience}")
        style_str = "\n".join(style_guidance) if style_guidance else "Maintain current tone and audience alignment."

        intro_text = introduction if introduction else "(No introduction currently — write one ONLY if a recommendation specifically asks for it)"

        prompt = f"""You are a careful SEO content editor making TARGETED edits to an existing blog post. Your job is to apply specific SEO recommendations with PRECISION — not to rewrite the entire post.

CRITICAL RULES — YOU MUST FOLLOW THESE:
1. PRESERVE existing content. Only make MINIMAL, targeted changes to address specific recommendations. Do NOT rewrite sections that are working well.
2. NEVER fabricate statistics, case studies, expert quotes, research data, or specific numbers unless they are explicitly stated in the research context below.
3. NEVER add content that contradicts or goes beyond what the research sources support.
4. KEEP the same emotional tone and writing style as the original content.
5. Return EXACTLY the same number of sections with EXACTLY the same IDs. Do NOT add, remove, or rename sections.
6. For sections marked [KEEP AS-IS], return the content UNCHANGED — copy it verbatim.
7. For sections marked [NEEDS EDITS], make ONLY the specific changes needed to address the applicable recommendations.
8. Do NOT add introductions, conclusions, or case studies unless a recommendation EXPLICITLY asks for one.

{research_block}

PLANNED OUTLINE STRUCTURE:
{outline_str}

CURRENT TITLE: {title}

CURRENT INTRODUCTION:
{intro_text}

CURRENT SECTIONS:
{sections_str}

RECOMMENDATIONS TO APPLY:
{''.join(recommendations_str)}
{persona_str}{style_str}

INSTRUCTIONS:
- For sections marked [KEEP AS-IS]: Copy the content EXACTLY as provided. Do not change a single word.
- For sections marked [NEEDS EDITS]: Make the MINIMUM changes needed to address the recommendations. If a recommendation says "add transition words", add 2-3 transitions — do not rewrite the paragraph. If it says "use more varied vocabulary", replace 2-3 repetitive words — do not rewrite the section.
- If a recommendation asks for an introduction and none exists, write a brief 2-3 sentence introduction that naturally leads into the first section. Do NOT fabricate hooks or statistics.
- If a recommendation asks for a conclusion, append 2-3 sentences summarizing key takeaways to the LAST section. Do NOT fabricate conclusions that don't follow from the actual content.
- Return ALL sections, including the ones you did NOT change.
- Provide a summary of which recommendations you addressed and what specific changes you made.
"""

        return prompt


__all__ = ["BlogSEORecommendationApplier"]