"""Blog SEO Recommendation Applier

Applies actionable SEO recommendations to existing blog content using the
provider-agnostic `llm_text_gen` dispatcher. Ensures GPT_PROVIDER parity.
"""

import asyncio
from typing import Dict, Any, List
from utils.logger_utils import get_service_logger

from services.llm_providers.main_text_generation import llm_text_gen


logger = get_service_logger("blog_seo_recommendation_applier")


class BlogSEORecommendationApplier:
    """Apply actionable SEO recommendations to blog content."""

    def __init__(self):
        logger.debug("Initialized BlogSEORecommendationApplier")

    async def apply_recommendations(self, payload: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
        """Apply recommendations and return updated content."""
        
        if not user_id:
            raise ValueError("user_id is required for subscription checking. Please provide Clerk user ID.")

        title = payload.get("title", "Untitled Blog")
        sections: List[Dict[str, Any]] = payload.get("sections", [])
        outline = payload.get("outline", [])
        research = payload.get("research", {})
        recommendations = payload.get("recommendations", [])
        persona = payload.get("persona", {})
        tone = payload.get("tone")
        audience = payload.get("audience")

        if not sections:
            return {"success": False, "error": "No sections provided for recommendation application"}

        if not recommendations:
            logger.warning("apply_recommendations called without recommendations")
            return {"success": True, "title": title, "sections": sections, "applied": []}

        prompt = self._build_prompt(
            title=title,
            sections=sections,
            outline=outline,
            research=research,
            recommendations=recommendations,
            persona=persona,
            tone=tone,
            audience=audience,
        )

        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
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

        logger.info("Applying SEO recommendations via llm_text_gen")

        result = await asyncio.to_thread(
            llm_text_gen,
            prompt,
            None,
            schema,
            user_id,  # Pass user_id for subscription checking
        )

        if not result or result.get("error"):
            error_msg = result.get("error", "Unknown error") if result else "No response from text generator"
            logger.error(f"SEO recommendation application failed: {error_msg}")
            return {"success": False, "error": error_msg}

        raw_sections = result.get("sections", []) or []
        normalized_sections: List[Dict[str, Any]] = []

        # Build lookup table from updated sections using their identifiers
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
                # Fall back to positional match if identifier lookup failed
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
                # Fallback to original content if nothing else available
                mapped = {
                    "id": fallback_id,
                    "heading": original.get("heading") or original.get("title") or f"Section {index + 1}",
                    "content": str(original.get("content", "")).strip(),
                    "notes": original.get("notes", []),
                }

            normalized_sections.append(mapped)

        applied = result.get("applied_recommendations", [])

        logger.info("SEO recommendations applied successfully")

        return {
            "success": True,
            "title": result.get("title", title),
            "sections": normalized_sections,
            "applied": applied,
        }

    def _build_prompt(
        self,
        *,
        title: str,
        sections: List[Dict[str, Any]],
        outline: List[Dict[str, Any]],
        research: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
        persona: Dict[str, Any],
        tone: str | None,
        audience: str | None,
    ) -> str:
        """Construct prompt for applying recommendations."""

        sections_str = []
        for section in sections:
            sections_str.append(
                f"ID: {section.get('id', 'section')}, Heading: {section.get('heading', 'Untitled')}\n"
                f"Current Content:\n{section.get('content', '')}\n"
            )

        outline_str = "\n".join(
            [
                f"- {item.get('heading', 'Section')} (Target words: {item.get('target_words', 'N/A')})"
                for item in outline
            ]
        )

        research_summary = research.get("keyword_analysis", {}) if research else {}
        primary_keywords = ", ".join(research_summary.get("primary", [])[:10]) or "None"

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
            else "Persona: (not provided)\n"
        )

        style_guidance = []
        if tone:
            style_guidance.append(f"Desired tone: {tone}")
        if audience:
            style_guidance.append(f"Target audience: {audience}")
        style_str = "\n".join(style_guidance) if style_guidance else "Maintain current tone and audience alignment."

        prompt = f"""
You are an expert SEO content strategist. Update the blog content to apply the actionable recommendations.

Current Title: {title}

Primary Keywords (for context): {primary_keywords}

Outline Overview:
{outline_str or 'No outline supplied'}

Existing Sections:
{''.join(sections_str)}

Actionable Recommendations to Apply:
{''.join(recommendations_str)}

{persona_str}
{style_str}

Instructions:
1. Carefully apply the recommendations while preserving factual accuracy and research alignment.
2. Keep section identifiers (IDs) unchanged so the frontend can map updates correctly.
3. Improve clarity, flow, and SEO optimization per the guidance.
4. Return updated sections in the requested JSON format.
5. Provide a short summary of which recommendations were addressed.
"""

        return prompt


__all__ = ["BlogSEORecommendationApplier"]


