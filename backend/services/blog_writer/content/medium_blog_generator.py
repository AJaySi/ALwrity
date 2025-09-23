"""
Medium Blog Generator Service

Handles generation of medium-length blogs (≤1000 words) using structured AI calls.
"""

import time
import json
from typing import Dict, Any, List
from loguru import logger

from models.blog_models import (
    MediumBlogGenerateRequest,
    MediumBlogGenerateResult,
    MediumGeneratedSection,
    ResearchSource,
)
from services.llm_providers.gemini_provider import gemini_structured_json_response
from services.cache.persistent_content_cache import persistent_content_cache


class MediumBlogGenerator:
    """Service for generating medium-length blog content using structured AI calls."""
    
    def __init__(self):
        self.cache = persistent_content_cache
    
    async def generate_medium_blog_with_progress(self, req: MediumBlogGenerateRequest, task_id: str) -> MediumBlogGenerateResult:
        """Use Gemini structured JSON to generate a medium-length blog in one call."""
        import time
        start = time.time()

        # Prepare sections data for cache key generation
        sections_for_cache = []
        for s in req.sections:
            sections_for_cache.append({
                "id": s.id,
                "heading": s.heading,
                "keyPoints": getattr(s, "key_points", []) or getattr(s, "keyPoints", []),
                "subheadings": getattr(s, "subheadings", []),
                "keywords": getattr(s, "keywords", []),
                "targetWords": getattr(s, "target_words", None) or getattr(s, "targetWords", None),
            })

        # Check cache first
        cached_result = self.cache.get_cached_content(
            keywords=req.researchKeywords or [],
            sections=sections_for_cache,
            global_target_words=req.globalTargetWords or 1000,
            persona_data=req.persona.dict() if req.persona else None,
            tone=req.tone,
            audience=req.audience
        )
        
        if cached_result:
            logger.info(f"Using cached content for keywords: {req.researchKeywords} (saved expensive generation)")
            # Add cache hit marker to distinguish from fresh generation
            cached_result['generation_time_ms'] = 0  # Mark as cache hit
            cached_result['cache_hit'] = True
            return MediumBlogGenerateResult(**cached_result)

        # Cache miss - proceed with AI generation
        logger.info(f"Cache miss - generating new content for keywords: {req.researchKeywords}")

        # Build schema expected from the model
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
                            "wordCount": {"type": "number"},
                            "sources": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {"title": {"type": "string"}, "url": {"type": "string"}},
                                },
                            },
                        },
                    },
                },
            },
        }

        # Compose prompt
        def section_block(s):
            return {
                "id": s.id,
                "heading": s.heading,
                "outline": {
                    "keyPoints": getattr(s, "key_points", []) or getattr(s, "keyPoints", []),
                    "subheadings": getattr(s, "subheadings", []),
                    "keywords": getattr(s, "keywords", []),
                    "targetWords": getattr(s, "target_words", None) or getattr(s, "targetWords", None),
                    "references": [
                        {"title": r.title, "url": r.url} for r in getattr(s, "references", [])
                    ],
                },
            }

        payload = {
            "title": req.title,
            "globalTargetWords": req.globalTargetWords or 1000,
            "persona": req.persona.dict() if req.persona else None,
            "tone": req.tone,
            "audience": req.audience,
            "sections": [section_block(s) for s in req.sections],
        }

        # Build persona-aware system prompt
        persona_context = ""
        if req.persona:
            persona_context = f"""
            PERSONA GUIDELINES:
            - Industry: {req.persona.industry or 'General'}
            - Tone: {req.persona.tone or 'Professional'}
            - Audience: {req.persona.audience or 'General readers'}
            - Persona ID: {req.persona.persona_id or 'Default'}
            
            Write content that reflects this persona's expertise and communication style.
            Use industry-specific terminology and examples where appropriate.
            Maintain consistent voice and authority throughout all sections.
            """
        
        system = (
            "You are a professional blog writer with deep expertise in your field. "
            "Generate high-quality, persona-driven content for each section based on the provided outline. "
            "Write engaging, informative content that follows the section's key points and target word count. "
            "Ensure the content flows naturally and maintains consistent voice and authority. "
            "Format content with proper paragraph breaks using double line breaks (\\n\\n) between paragraphs. "
            "Structure content with clear paragraphs - aim for 2-4 sentences per paragraph. "
            f"{persona_context}"
            "Return ONLY valid JSON with no markdown formatting or explanations."
        )

        # Build persona-specific content instructions
        persona_instructions = ""
        if req.persona:
            industry = req.persona.industry or 'General'
            tone = req.persona.tone or 'Professional'
            audience = req.persona.audience or 'General readers'
            
            persona_instructions = f"""
            PERSONA-DRIVEN CONTENT REQUIREMENTS:
            - Write as an expert in {industry} industry
            - Use {tone} tone appropriate for {audience}
            - Include industry-specific examples and terminology
            - Demonstrate authority and expertise in the field
            - Use language that resonates with {audience}
            - Maintain consistent voice that reflects this persona's expertise
            """
        
        prompt = (
            f"Write blog content for the following sections. Each section should be {req.globalTargetWords or 1000} words total, distributed across all sections.\n\n"
            f"Blog Title: {req.title}\n\n"
            "For each section, write engaging content that:\n"
            "- Follows the key points provided\n"
            "- Uses the suggested keywords naturally\n"
            "- Meets the target word count\n"
            "- Maintains professional tone\n"
            "- References the provided sources when relevant\n"
            "- Breaks content into clear paragraphs (2-4 sentences each)\n"
            "- Uses double line breaks (\\n\\n) between paragraphs for proper formatting\n"
            "- Starts with an engaging opening paragraph\n"
            "- Ends with a strong concluding paragraph\n"
            f"{persona_instructions}\n"
            "IMPORTANT: Format the 'content' field with proper paragraph breaks using \\n\\n between paragraphs.\n\n"
            "Return a JSON object with 'title' and 'sections' array. Each section should have 'id', 'heading', 'content', and 'wordCount'.\n\n"
            f"Sections to write:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
        )

        ai_resp = gemini_structured_json_response(
            prompt=prompt,
            schema=schema,
            temperature=0.2,
            max_tokens=8192,
            system_prompt=system,
        )

        # Check for errors in AI response
        if not ai_resp or ai_resp.get("error"):
            error_msg = ai_resp.get("error", "Empty generation result from model") if ai_resp else "No response from model"
            logger.error(f"AI generation failed: {error_msg}")
            raise Exception(f"AI generation failed: {error_msg}")

        # Normalize output
        title = ai_resp.get("title") or req.title
        out_sections = []
        for s in ai_resp.get("sections", []) or []:
            out_sections.append(
                MediumGeneratedSection(
                    id=str(s.get("id")),
                    heading=s.get("heading") or "",
                    content=s.get("content") or "",
                    wordCount=int(s.get("wordCount") or 0),
                    sources=[
                        # map to ResearchSource shape if possible; keep minimal
                        ResearchSource(title=src.get("title", ""), url=src.get("url", ""))
                        for src in (s.get("sources") or [])
                    ] or None,
                )
            )

        duration_ms = int((time.time() - start) * 1000)
        result = MediumBlogGenerateResult(
            success=True,
            title=title,
            sections=out_sections,
            model="gemini-2.5-flash",
            generation_time_ms=duration_ms,
            safety_flags=None,
        )
        
        # Cache the result for future use
        try:
            self.cache.cache_content(
                keywords=req.researchKeywords or [],
                sections=sections_for_cache,
                global_target_words=req.globalTargetWords or 1000,
                persona_data=req.persona.dict() if req.persona else None,
                tone=req.tone or "professional",
                audience=req.audience or "general",
                result=result.dict()
            )
            logger.info(f"Cached content result for keywords: {req.researchKeywords}")
        except Exception as cache_error:
            logger.warning(f"Failed to cache content result: {cache_error}")
            # Don't fail the entire operation if caching fails
        
        return result
