"""
Podcast Analysis Handlers

Analysis endpoint for podcast ideas.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import json

from middleware.auth_middleware import get_current_user
from api.story_writer.utils.auth import require_authenticated_user
from services.llm_providers.main_text_generation import llm_text_gen
from loguru import logger
from ..models import PodcastAnalyzeRequest, PodcastAnalyzeResponse

router = APIRouter()


@router.post("/analyze", response_model=PodcastAnalyzeResponse)
async def analyze_podcast_idea(
    request: PodcastAnalyzeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Analyze a podcast idea and return podcast-oriented outlines, keywords, and titles.
    This uses the shared LLM provider but with a podcast-specific prompt (not story format).
    """
    user_id = require_authenticated_user(current_user)

    prompt = f"""
You are an expert podcast producer. Given a podcast idea, craft concise podcast-ready assets
that sound like episode plans (not fiction stories).

Podcast Idea: "{request.idea}"
Duration: ~{request.duration} minutes
Speakers: {request.speakers} (host + optional guest)

Return JSON with:
- audience: short target audience description
- content_type: podcast style/format
- top_keywords: 5 podcast-relevant keywords/phrases
- suggested_outlines: 2 items, each with title (<=60 chars) and 4-6 short segments (bullet-friendly, factual)
- title_suggestions: 3 concise episode titles (no cliffhanger storytelling)
- exa_suggested_config: suggested Exa search options to power research (keep conservative defaults to control cost), with:
  - exa_search_type: "auto" | "neural" | "keyword" (prefer "auto" unless clearly news-heavy)
  - exa_category: one of ["research paper","news","company","github","tweet","personal site","pdf","financial report","linkedin profile"]
  - exa_include_domains: up to 3 reputable domains to prioritize (optional)
  - exa_exclude_domains: up to 3 domains to avoid (optional)
  - max_sources: 6-10
  - include_statistics: boolean (true if topic needs fresh stats)
  - date_range: one of ["last_month","last_3_months","last_year","all_time"] (pick recent if time-sensitive)

Requirements:
- Keep language factual, actionable, and suited for spoken audio.
- Avoid narrative fiction tone; focus on insights, hooks, objections, and takeaways.
- Prefer 2024-2025 context when relevant.
"""

    try:
        raw = llm_text_gen(prompt=prompt, user_id=user_id, json_struct=None)
    except HTTPException:
        # Re-raise HTTPExceptions (e.g., 429 subscription limit) - preserve error details
        raise
    except Exception as exc:
        logger.error(f"[Podcast Analyze] Analysis failed for user {user_id}: {exc}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")

    # Normalize response (accept dict or JSON string)
    if isinstance(raw, str):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="LLM returned non-JSON output")
    elif isinstance(raw, dict):
        data = raw
    else:
        raise HTTPException(status_code=500, detail="Unexpected LLM response format")

    audience = data.get("audience") or "Growth-focused professionals"
    content_type = data.get("content_type") or "Interview + insights"
    top_keywords = data.get("top_keywords") or []
    suggested_outlines = data.get("suggested_outlines") or []
    title_suggestions = data.get("title_suggestions") or []

    exa_suggested_config = data.get("exa_suggested_config") or None

    return PodcastAnalyzeResponse(
        audience=audience,
        content_type=content_type,
        top_keywords=top_keywords,
        suggested_outlines=suggested_outlines,
        title_suggestions=title_suggestions,
        exa_suggested_config=exa_suggested_config,
    )

