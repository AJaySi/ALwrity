"""
Podcast Research Handlers

Research endpoints using Exa provider.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from types import SimpleNamespace

from middleware.auth_middleware import get_current_user
from api.story_writer.utils.auth import require_authenticated_user
from services.blog_writer.research.exa_provider import ExaResearchProvider
from loguru import logger
from ..models import (
    PodcastExaResearchRequest,
    PodcastExaResearchResponse,
    PodcastExaSource,
    PodcastExaConfig,
)

router = APIRouter()


@router.post("/research/exa", response_model=PodcastExaResearchResponse)
async def podcast_research_exa(
    request: PodcastExaResearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Run podcast research directly via Exa (no blog writer pipeline).
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
    prompt = request.topic

    try:
        result = await provider.search(
            prompt=prompt,
            topic=request.topic,
            industry="",
            target_audience="",
            config=cfg,
            user_id=user_id,
        )
    except Exception as exc:
        logger.error(f"[Podcast Exa Research] Failed for user {user_id}: {exc}")
        raise HTTPException(status_code=500, detail=f"Exa research failed: {exc}")

    # Track usage if available
    try:
        cost_total = 0.0
        if isinstance(result, dict):
            cost_total = result.get("cost", {}).get("total", 0.005) if result.get("cost") else 0.005
        provider.track_exa_usage(user_id, cost_total)
    except Exception as track_err:
        logger.warning(f"[Podcast Exa Research] Failed to track usage: {track_err}")

    sources_payload = []
    if isinstance(result, dict):
        for src in result.get("sources", []) or []:
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
                }))

    return PodcastExaResearchResponse(
        sources=sources_payload,
        search_queries=result.get("search_queries", queries) if isinstance(result, dict) else queries,
        cost=result.get("cost") if isinstance(result, dict) else None,
        search_type=result.get("search_type") if isinstance(result, dict) else None,
        provider=result.get("provider", "exa") if isinstance(result, dict) else "exa",
        content=result.get("content") if isinstance(result, dict) else None,
    )

