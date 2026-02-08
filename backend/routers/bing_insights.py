"""
Bing Insights API Routes

Provides endpoints for accessing Bing Webmaster insights and recommendations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from loguru import logger
import os

from services.analytics.insights.bing_insights_service import BingInsightsService
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/bing-insights", tags=["Bing Insights"])

# Initialize insights service
from services.database import get_user_db_path

def get_insights_service(user_id: str) -> BingInsightsService:
    return BingInsightsService()


@router.get("/performance")
async def get_performance_insights(
    site_url: str = Query(..., description="Site URL to analyze"),
    days: int = Query(30, description="Number of days to analyze"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get performance insights including trends and patterns for a Bing Webmaster site.
    """
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        logger.info(f"Getting performance insights for user {user_id}, site: {site_url}")
        
        insights_service = get_insights_service(user_id)
        insights = insights_service.get_performance_insights(user_id, site_url, days)
        
        if 'error' in insights:
            raise HTTPException(status_code=404, detail=insights['error'])
        
        return {
            "success": True,
            "data": insights,
            "site_url": site_url,
            "analysis_period": f"{days} days",
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting performance insights: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/seo")
async def get_seo_insights(
    site_url: str = Query(..., description="Site URL to analyze"),
    days: int = Query(30, description="Number of days to analyze"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get SEO-specific insights and opportunities for a Bing Webmaster site.
    """
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        logger.info(f"Getting SEO insights for user {user_id}, site: {site_url}")
        
        insights_service = get_insights_service(user_id)
        insights = insights_service.get_seo_insights(user_id, site_url, days)
        
        if 'error' in insights:
            raise HTTPException(status_code=404, detail=insights['error'])
        
        return {
            "success": True,
            "data": insights,
            "site_url": site_url,
            "analysis_period": f"{days} days",
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting SEO insights: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/competitive")
async def get_competitive_insights(
    site_url: str = Query(..., description="Site URL to analyze"),
    days: int = Query(30, description="Number of days to analyze"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get competitive analysis and market insights for a Bing Webmaster site.
    """
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        logger.info(f"Getting competitive insights for user {user_id}, site: {site_url}")
        
        insights = insights_service.get_competitive_insights(user_id, site_url, days)
        
        if 'error' in insights:
            raise HTTPException(status_code=404, detail=insights['error'])
        
        return {
            "success": True,
            "data": insights,
            "site_url": site_url,
            "analysis_period": f"{days} days",
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting competitive insights: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/recommendations")
async def get_actionable_recommendations(
    site_url: str = Query(..., description="Site URL to analyze"),
    days: int = Query(30, description="Number of days to analyze"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get actionable recommendations for improving search performance.
    """
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        logger.info(f"Getting actionable recommendations for user {user_id}, site: {site_url}")
        
        recommendations = insights_service.get_actionable_recommendations(user_id, site_url, days)
        
        if 'error' in recommendations:
            raise HTTPException(status_code=404, detail=recommendations['error'])
        
        return {
            "success": True,
            "data": recommendations,
            "site_url": site_url,
            "analysis_period": f"{days} days",
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting actionable recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/comprehensive")
async def get_comprehensive_insights(
    site_url: str = Query(..., description="Site URL to analyze"),
    days: int = Query(30, description="Number of days to analyze"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get comprehensive insights including performance, SEO, competitive, and recommendations.
    """
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        logger.info(f"Getting comprehensive insights for user {user_id}, site: {site_url}")
        
        # Get all types of insights
        insights_service = get_insights_service(user_id)
        performance = insights_service.get_performance_insights(user_id, site_url, days)
        seo = insights_service.get_seo_insights(user_id, site_url, days)
        competitive = insights_service.get_competitive_insights(user_id, site_url, days)
        recommendations = insights_service.get_actionable_recommendations(user_id, site_url, days)
        
        # Check for errors
        errors = []
        if 'error' in performance:
            errors.append(f"Performance insights: {performance['error']}")
        if 'error' in seo:
            errors.append(f"SEO insights: {seo['error']}")
        if 'error' in competitive:
            errors.append(f"Competitive insights: {competitive['error']}")
        if 'error' in recommendations:
            errors.append(f"Recommendations: {recommendations['error']}")
        
        if errors:
            logger.warning(f"Some insights failed: {errors}")
        
        return {
            "success": True,
            "data": {
                "performance": performance,
                "seo": seo,
                "competitive": competitive,
                "recommendations": recommendations
            },
            "site_url": site_url,
            "analysis_period": f"{days} days",
            "generated_at": datetime.now().isoformat(),
            "warnings": errors if errors else None
        }
        
    except Exception as e:
        logger.error(f"Error getting comprehensive insights: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
