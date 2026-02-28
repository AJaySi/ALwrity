"""
Bing Webmaster Analytics API Routes
Provides endpoints for accessing Bing Webmaster Tools analytics data.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from services.integrations.bing_oauth import BingOAuthService
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/bing", tags=["Bing Analytics"])

# Initialize Bing OAuth service
bing_service = BingOAuthService()

@router.get("/query-stats")
async def get_query_stats(
    site_url: str = Query(..., description="The site URL to get query stats for"),
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    page: int = Query(0, description="Page number for pagination"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get search query statistics for a Bing Webmaster site."""
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        logger.info(f"Getting Bing query stats for user {user_id}, site: {site_url}")
        
        # Get query stats from Bing service
        result = bing_service.get_query_stats(
            user_id=user_id,
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
            page=page
        )
        
        if "error" in result:
            logger.error(f"Bing query stats error: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        logger.info(f"Successfully retrieved Bing query stats for {site_url}")
        return {
            "success": True,
            "data": result,
            "site_url": site_url,
            "start_date": start_date,
            "end_date": end_date,
            "page": page
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Bing query stats: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/user-sites")
async def get_user_sites(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get list of user's verified sites from Bing Webmaster."""
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        logger.info(f"Getting Bing user sites for user {user_id}")
        
        # Get user sites from Bing service
        sites = bing_service.get_user_sites(user_id)
        
        logger.info(f"Successfully retrieved {len(sites)} Bing sites for user {user_id}")
        return {
            "success": True,
            "sites": sites,
            "total_sites": len(sites)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Bing user sites: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/query-stats/summary")
async def get_query_stats_summary(
    site_url: str = Query(..., description="The site URL to get query stats summary for"),
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get summarized query statistics for a Bing Webmaster site."""
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        logger.info(f"Getting Bing query stats summary for user {user_id}, site: {site_url}")
        
        # Get query stats from Bing service
        result = bing_service.get_query_stats(
            user_id=user_id,
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
            page=0  # Just get first page for summary
        )
        
        if "error" in result:
            logger.error(f"Bing query stats error: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Extract summary data
        query_data = result.get('d', {})
        queries = query_data.get('results', [])
        
        # Calculate summary statistics
        total_clicks = sum(query.get('Clicks', 0) for query in queries)
        total_impressions = sum(query.get('Impressions', 0) for query in queries)
        total_queries = len(queries)
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_position = sum(query.get('AvgClickPosition', 0) for query in queries) / total_queries if total_queries > 0 else 0
        
        # Get top queries
        top_queries = sorted(queries, key=lambda x: x.get('Clicks', 0), reverse=True)[:5]
        
        summary = {
            "total_queries": total_queries,
            "total_clicks": total_clicks,
            "total_impressions": total_impressions,
            "average_ctr": round(avg_ctr, 2),
            "average_position": round(avg_position, 2),
            "top_queries": [
                {
                    "query": q.get('Query', ''),
                    "clicks": q.get('Clicks', 0),
                    "impressions": q.get('Impressions', 0),
                    "ctr": round(q.get('Clicks', 0) / q.get('Impressions', 1) * 100, 2),
                    "position": q.get('AvgClickPosition', 0)
                }
                for q in top_queries
            ]
        }
        
        logger.info(f"Successfully created Bing query stats summary for {site_url}")
        return {
            "success": True,
            "summary": summary,
            "site_url": site_url,
            "start_date": start_date,
            "end_date": end_date,
            "raw_data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Bing query stats summary: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
