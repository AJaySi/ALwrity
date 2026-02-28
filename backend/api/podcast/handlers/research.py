"""
Podcast Research Handlers

Research endpoints using Exa provider and LLM summarization.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from types import SimpleNamespace
import json

from middleware.auth_middleware import get_current_user
from api.story_writer.utils.auth import require_authenticated_user
from services.blog_writer.research.exa_provider import ExaResearchProvider
from services.llm_providers.main_text_generation import llm_text_gen
from services.podcast_bible_service import PodcastBibleService
from loguru import logger
from ..models import (
    PodcastExaResearchRequest,
    PodcastExaResearchResponse,
    PodcastExaSource,
    PodcastExaConfig,
    PodcastResearchInsight,
)

router = APIRouter()


@router.post("/research/exa", response_model=PodcastExaResearchResponse)
async def podcast_research_exa(
    request: PodcastExaResearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Run podcast research via Exa and then use LLM to extract deep insights.
    Uses Podcast Bible and Analysis context for hyper-personalization.
    """
    user_id = require_authenticated_user(current_user)

    queries = [q.strip() for q in request.queries if q and q.strip()]
    if not queries:
        raise HTTPException(status_code=400, detail="At least one query is required for research.")

    exa_cfg = request.exa_config or PodcastExaConfig()
    cfg = SimpleNamespace(
        exa_search_type=exa_cfg.exa_search_type or "auto",
        exa_category=exa_cfg.exa_category,
        exa_include_domains=exa_cfg.exa_include_domains or [],
        exa_exclude_domains=exa_cfg.exa_exclude_domains or [],
        max_sources=exa_cfg.max_sources or 8,
        source_types=[],
    )

    provider = ExaResearchProvider()
    
    # --- Context Building ---
    bible_service = PodcastBibleService()
    bible_context = ""
    if request.bible:
        try:
            from models.podcast_bible_models import PodcastBible
            bible_data = PodcastBible(**request.bible)
            bible_context = bible_service.serialize_bible(bible_data)
        except Exception as exc:
            logger.warning(f"[Podcast Research] Failed to serialize bible: {exc}")

    analysis_context = ""
    if request.analysis:
        analysis_context = f"""
PODCAST ANALYSIS CONTEXT:
Audience: {request.analysis.get('audience', 'General')}
Content Type: {request.analysis.get('content_type', 'Informative')}
Top Keywords: {', '.join(request.analysis.get('top_keywords', []))}
"""

    # Exa search params
    industry = request.bible.get("brand", {}).get("industry", "") if request.bible else ""
    target_audience = ""
    if request.bible:
        audience_dna = request.bible.get("audience", {})
        if audience_dna:
            interests = ", ".join(audience_dna.get("interests", []))
            target_audience = f"Expertise: {audience_dna.get('expertise_level', '')}. Interests: {interests}."

    try:
        # 1. RUN EXA SEARCH
        result = await provider.search(
            prompt=request.topic,
            topic=request.topic,
            industry=industry,
            target_audience=target_audience,
            config=cfg,
            user_id=user_id,
        )
    except Exception as exc:
        logger.error(f"[Podcast Exa Research] Search failed for user {user_id}: {exc}")
        raise HTTPException(status_code=500, detail=f"Exa research failed: {exc}")

    # 2. EXTRACT INSIGHTS VIA LLM
    raw_content = result.get("content", "")
    sources = result.get("sources", [])
    
    summary = ""
    key_insights = []
    
    if raw_content and sources:
        logger.info(f"[Podcast Research] Extracting insights from {len(sources)} sources for user {user_id}")
        
        prompt = f"""
You are an expert research analyst for a high-end podcast production team. 
Your task is to analyze the following research data and extract deep, actionable insights for a podcast episode.

PODCAST CONTEXT:
Topic: {request.topic}
{bible_context}
{analysis_context}

RESEARCH DATA (from {len(sources)} sources):
{raw_content}

TASK:
1. Provide a comprehensive summary (2-3 paragraphs) of the most important findings. Use Markdown for formatting (bolding, lists).
2. Extract 3-5 "Key Insights". Each insight should have a title and a detailed explanation.
3. For each insight, identify which source indices (e.g. 1, 2) it was derived from.

NOTE: The research data includes "Key Highlights", "Summaries", and "Excerpts" from various sources. 
Pay special attention to the "Key Highlights" sections as they contain the most relevant information extracted by the neural search engine.

Return JSON structure:
{{
  "summary": "Detailed markdown summary...",
  "key_insights": [
    {{
      "title": "Insight Title",
      "content": "Detailed markdown content...",
      "source_indices": [1, 2]
    }}
  ]
}}

Requirements:
- Ensure insights are deep, not just superficial facts. Look for trends, expert opinions, and specific data points.
- Tone should be professional, insightful, and ready for a podcast host to discuss.
- Avoid generic filler.
"""
        try:
            llm_response = llm_text_gen(prompt=prompt, user_id=user_id, json_struct=None)
            
            # Normalize response
            if isinstance(llm_response, str):
                data = json.loads(llm_response)
            else:
                data = llm_response
                
            summary = data.get("summary", "")
            key_insights = [PodcastResearchInsight(**insight) for insight in data.get("key_insights", [])]
        except Exception as exc:
            logger.error(f"[Podcast Research] LLM Insight extraction failed: {exc}")
            # Fallback to a basic summary if LLM fails
            summary = f"Research completed for '{request.topic}'. Found {len(sources)} sources."
            
    # Fallback: if summary is still empty (e.g. LLM returned empty string), use raw content first paragraph or basic text
    if not summary:
        if raw_content:
            summary = raw_content[:2000] # Use first 2000 chars of raw content as summary
        else:
            summary = f"Research completed for '{request.topic}'. Found {len(sources)} sources."

    # 3. TRACK USAGE
    try:
        cost_total = 0.0
        if isinstance(result, dict):
            cost_total = result.get("cost", {}).get("total", 0.005) if result.get("cost") else 0.005
        provider.track_exa_usage(user_id, cost_total)
    except Exception as track_err:
        logger.warning(f"[Podcast Exa Research] Failed to track usage: {track_err}")

    sources_payload = []
    for src in sources:
        try:
            sources_payload.append(PodcastExaSource(**src))
        except Exception:
            sources_payload.append(PodcastExaSource(**{
                "title": src.get("title", ""),
                "url": src.get("url", ""),
                "excerpt": src.get("excerpt", ""),
                "published_at": src.get("published_at"),
                "highlights": src.get("highlights"),
                "summary": src.get("summary"),
                "source_type": src.get("source_type"),
                "index": src.get("index"),
                "image": src.get("image"),
                "author": src.get("author"),
            }))

    return PodcastExaResearchResponse(
        sources=sources_payload,
        search_queries=result.get("search_queries", queries) if isinstance(result, dict) else queries,
        summary=summary,
        key_insights=key_insights,
        cost=result.get("cost") if isinstance(result, dict) else None,
        search_type=result.get("search_type") if isinstance(result, dict) else None,
        provider=result.get("provider", "exa") if isinstance(result, dict) else "exa",
        content=raw_content,
    )

