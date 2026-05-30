"""
AI Visibility Insights Router
Provides AI Overview detection and visibility analysis from GSC data.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from loguru import logger

from services.gsc_service import GSCService
from services.seo_tools.ai_visibility_insights_service import (
    AIVisibilityInsightsService,
    AIOThresholds,
)
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/ai-visibility", tags=["AI Visibility Insights"])

gsc_service = GSCService()
ai_visibility_service = AIVisibilityInsightsService(gsc_service)


class ThresholdInput(BaseModel):
    impacted_min_impressions: int = Field(500, ge=0, description="Min impressions for AIO impacted detection")
    impacted_max_position: float = Field(4.0, ge=0, le=100, description="Max position for AIO impacted detection")
    impacted_max_ctr: float = Field(2.0, ge=0, le=100, description="Max CTR % for AIO impacted detection")
    opportunity_min_impressions: int = Field(300, ge=0, description="Min impressions for AIO opportunity detection")
    opportunity_min_position: float = Field(4.0, ge=0, description="Min position for AIO opportunity detection")
    opportunity_max_position: float = Field(10.0, ge=0, le=100, description="Max position for AIO opportunity detection")
    opportunity_min_ctr: float = Field(5.0, ge=0, le=100, description="Min CTR % for AIO opportunity detection")


class AIOverviewInsightsRequest(BaseModel):
    site_url: str = Field(..., description="Verified GSC site URL")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD); defaults to 30 days ago")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD); defaults to today")
    thresholds: Optional[ThresholdInput] = None


@router.post("/overview-insights")
def get_ai_overview_insights(
    request: AIOverviewInsightsRequest,
    user: dict = Depends(get_current_user),
):
    """Analyze GSC data for AI Overview impact signals."""
    try:
        user_id = user.get("id") if user else None
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")

        logger.info(
            f"AI Visibility request: site={request.site_url}, user={user_id}, "
            f"dates={request.start_date or 'auto'} to {request.end_date or 'auto'}"
        )

        # Convert threshold input if provided
        thresholds = None
        if request.thresholds:
            thresholds = AIOThresholds(
                impacted_min_impressions=request.thresholds.impacted_min_impressions,
                impacted_max_position=request.thresholds.impacted_max_position,
                impacted_max_ctr=request.thresholds.impacted_max_ctr,
                opportunity_min_impressions=request.thresholds.opportunity_min_impressions,
                opportunity_min_position=request.thresholds.opportunity_min_position,
                opportunity_max_position=request.thresholds.opportunity_max_position,
                opportunity_min_ctr=request.thresholds.opportunity_min_ctr,
            )

        result = ai_visibility_service.analyze(
            user_id=user_id,
            site_url=request.site_url,
            start_date=request.start_date,
            end_date=request.end_date,
            thresholds=thresholds,
        )

        if result.error:
            logger.warning(f"AI Visibility analysis returned error: {result.error}")
            return {
                "success": False,
                "error": result.error,
                "summary": result.summary,
                "impacted_keywords": result.impacted_keywords,
                "opportunity_keywords": result.opportunity_keywords,
                "recommendations": result.recommendations,
            }

        return {
            "success": True,
            "summary": result.summary,
            "impacted_keywords": result.impacted_keywords,
            "opportunity_keywords": result.opportunity_keywords,
            "recommendations": result.recommendations,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI Visibility endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
