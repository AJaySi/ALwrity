"""
Podcast Trends Handler

Endpoints for fetching Google Trends data relevant to podcast topics.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from loguru import logger

from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/trends", tags=["Podcast Trends"])


class PodcastTrendsRequest(BaseModel):
    keywords: List[str] = Field(..., min_length=1, max_length=5, description="1-5 keywords to analyze")
    timeframe: str = Field(default="today 12-m", description="Timeframe: 'today 3-m', 'today 12-m', 'today 5-y', 'all'")
    geo: str = Field(default="US", description="Country code: 'US', 'GB', 'IN', etc.")


class PodcastTrendsResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("", response_model=PodcastTrendsResponse)
async def get_podcast_trends(
    request: PodcastTrendsRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Fetch Google Trends data for podcast topic keywords."""
    user_id = current_user.get("user_id") or current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found")

    try:
        from services.research.trends import GoogleTrendsService
    except (ImportError, RuntimeError) as e:
        logger.error(f"[Podcast Trends] GoogleTrendsService unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail="Google Trends service is currently unavailable. Please try again later."
        )

    try:
        service = GoogleTrendsService()
        result = await service.analyze_trends(
            keywords=request.keywords,
            timeframe=request.timeframe,
            geo=request.geo,
            user_id=user_id,
        )
        return PodcastTrendsResponse(success=True, data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[Podcast Trends] Error fetching trends for {request.keywords}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch trends data: {str(e)}"
        )