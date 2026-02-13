"""
Bing Analytics Storage API Routes

Provides endpoints for accessing stored Bing analytics data,
historical trends, and performance analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger
import os
import json
from sqlalchemy import and_


def _raise_postgresql_required():
    """Raise error if PostgreSQL not configured."""
    raise ValueError(
        """
 POSTGRESQL REQUIRED - Clean Architecture
        
    ALwrity requires PostgreSQL environment variables to be set:
    - PLATFORM_DATABASE_URL=postgresql://user:pass@host:port/database_name
    - USER_DATA_DATABASE_URL=postgresql://user:pass@host:port/database_name

    This is intentional - we no longer support SQLite or single database setups.
    """
    )

from services.bing_analytics_storage_service import BingAnalyticsStorageService
from middleware.auth_middleware import get_current_user
import os

router = APIRouter(prefix="/bing-analytics", tags=["Bing Analytics Storage"])

# Initialize storage service
from services.database import get_user_db_path

def get_storage_service(user_id: str) -> BingAnalyticsStorageService:
    """Get storage service instance for a specific user."""
    return BingAnalyticsStorageService(user_id)


@router.post("/collect-data")
async def collect_bing_data(
    background_tasks: BackgroundTasks,
    site_url: str = Query(..., description="Site URL to collect data for"),
    days_back: int = Query(30, description="Number of days back to collect data"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Collect and store Bing analytics data for a site.
    This endpoint triggers data collection from Bing API and stores it in the database.
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        logger.info(f"Starting Bing data collection for user {user_id}, site: {site_url}")
        
        storage_service = get_storage_service(user_id)
        
        # Run data collection in background
        background_tasks.add_task(
            storage_service.collect_and_store_data,
            user_id=user_id,
            site_url=site_url,
            days_back=days_back
        )
        
        return {
            "success": True,
            "message": f"Bing data collection started for {site_url}",
            "site_url": site_url,
            "days_back": days_back,
            "status": "collecting"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting Bing data collection: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/summary")
async def get_analytics_summary(
    site_url: str = Query(..., description="Site URL to get analytics for"),
    days: int = Query(30, description="Number of days for analytics summary"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get comprehensive analytics summary for a site over a specified period.
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        logger.info(f"Getting analytics summary for user {user_id}, site: {site_url}, days: {days}")
        
        storage_service = get_storage_service(user_id)
        summary = storage_service.get_analytics_summary(
            user_id=user_id,
            site_url=site_url,
            days=days
        )
        
        if 'error' in summary:
            raise HTTPException(status_code=404, detail=summary['error'])
        
        return {
            "success": True,
            "data": summary,
            "site_url": site_url,
            "period_days": days
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/daily-metrics")
async def get_daily_metrics(
    site_url: str = Query(..., description="Site URL to get daily metrics for"),
    days: int = Query(30, description="Number of days to retrieve"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get daily metrics for a site over a specified period.
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        logger.info(f"Getting daily metrics for user {user_id}, site: {site_url}, days: {days}")
        
        storage_service = get_storage_service(user_id)
        db = storage_service._get_db_session()
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get daily metrics
        daily_metrics = db.query(storage_service.BingDailyMetrics).filter(
            and_(
                storage_service.BingDailyMetrics.user_id == user_id,
                storage_service.BingDailyMetrics.site_url == site_url,
                storage_service.BingDailyMetrics.metric_date >= start_date,
                storage_service.BingDailyMetrics.metric_date <= end_date
            )
        ).order_by(storage_service.BingDailyMetrics.metric_date).all()
        
        db.close()
        
        # Format response
        metrics_data = []
        for metric in daily_metrics:
            metrics_data.append({
                "date": metric.metric_date.isoformat(),
                "total_clicks": metric.total_clicks,
                "total_impressions": metric.total_impressions,
                "total_queries": metric.total_queries,
                "avg_ctr": metric.avg_ctr,
                "avg_position": metric.avg_position,
                "clicks_change": metric.clicks_change,
                "impressions_change": metric.impressions_change,
                "ctr_change": metric.ctr_change,
                "top_queries": json.loads(metric.top_queries) if metric.top_queries else [],
                "collected_at": metric.collected_at.isoformat()
            })
        
        return {
            "success": True,
            "data": metrics_data,
            "site_url": site_url,
            "period_days": days,
            "metrics_count": len(metrics_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting daily metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/top-queries")
async def get_top_queries(
    site_url: str = Query(..., description="Site URL to get top queries for"),
    days: int = Query(30, description="Number of days to analyze"),
    limit: int = Query(50, description="Number of top queries to return"),
    sort_by: str = Query("clicks", description="Sort by: clicks, impressions, or ctr"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get top performing queries for a site over a specified period.
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        if sort_by not in ["clicks", "impressions", "ctr"]:
            raise HTTPException(status_code=400, detail="sort_by must be 'clicks', 'impressions', or 'ctr'")
        
        logger.info(f"Getting top queries for user {user_id}, site: {site_url}, sort_by: {sort_by}")
        
        storage_service = get_storage_service(user_id)
        db = storage_service._get_db_session()
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get raw query data
        query_stats = db.query(storage_service.BingQueryStats).filter(
            and_(
                storage_service.BingQueryStats.user_id == user_id,
                storage_service.BingQueryStats.site_url == site_url,
                storage_service.BingQueryStats.query_date >= start_date,
                storage_service.BingQueryStats.query_date <= end_date
            )
        ).all()
        
        db.close()
        
        if not query_stats:
            return {
                "success": True,
                "data": [],
                "message": "No query data found for the specified period"
            }
        
        # Aggregate queries
        query_aggregates = {}
        for stat in query_stats:
            query = stat.query
            if query not in query_aggregates:
                query_aggregates[query] = {
                    "query": query,
                    "total_clicks": 0,
                    "total_impressions": 0,
                    "avg_ctr": 0,
                    "avg_position": 0,
                    "days_appeared": 0,
                    "category": stat.category,
                    "is_brand": stat.is_brand_query
                }
            
            query_aggregates[query]["total_clicks"] += stat.clicks
            query_aggregates[query]["total_impressions"] += stat.impressions
            query_aggregates[query]["days_appeared"] += 1
            
            # Calculate weighted average position
            if stat.avg_click_position > 0:
                query_aggregates[query]["avg_position"] = (
                    query_aggregates[query]["avg_position"] * (query_aggregates[query]["days_appeared"] - 1) + 
                    stat.avg_click_position
                ) / query_aggregates[query]["days_appeared"]
        
        # Calculate CTR for each query
        for query_data in query_aggregates.values():
            query_data["avg_ctr"] = (
                query_data["total_clicks"] / query_data["total_impressions"] * 100
            ) if query_data["total_impressions"] > 0 else 0
        
        # Sort and limit results
        sorted_queries = sorted(
            list(query_aggregates.values()),
            key=lambda x: x[f"total_{sort_by}"],
            reverse=True
        )[:limit]
        
        return {
            "success": True,
            "data": sorted_queries,
            "site_url": site_url,
            "period_days": days,
            "sort_by": sort_by,
            "total_queries": len(query_aggregates),
            "returned_queries": len(sorted_queries)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting top queries: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/query-details")
async def get_query_details(
    site_url: str = Query(..., description="Site URL"),
    query: str = Query(..., description="Specific query to analyze"),
    days: int = Query(30, description="Number of days to analyze"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get detailed performance data for a specific query.
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        logger.info(f"Getting query details for user {user_id}, query: {query}")
        
        db = storage_service._get_db_session()
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get query stats
        query_stats = db.query(storage_service.BingQueryStats).filter(
            and_(
                storage_service.BingQueryStats.user_id == user_id,
                storage_service.BingQueryStats.site_url == site_url,
                storage_service.BingQueryStats.query == query,
                storage_service.BingQueryStats.query_date >= start_date,
                storage_service.BingQueryStats.query_date <= end_date
            )
        ).order_by(storage_service.BingQueryStats.query_date).all()
        
        db.close()
        
        if not query_stats:
            return {
                "success": True,
                "data": None,
                "message": f"No data found for query: {query}"
            }
        
        # Calculate summary statistics
        total_clicks = sum(stat.clicks for stat in query_stats)
        total_impressions = sum(stat.impressions for stat in query_stats)
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_position = sum(stat.avg_click_position for stat in query_stats if stat.avg_click_position > 0) / len([stat for stat in query_stats if stat.avg_click_position > 0]) if any(stat.avg_click_position > 0 for stat in query_stats) else 0
        
        # Daily performance data
        daily_data = []
        for stat in query_stats:
            daily_data.append({
                "date": stat.query_date.isoformat(),
                "clicks": stat.clicks,
                "impressions": stat.impressions,
                "ctr": stat.ctr,
                "avg_click_position": stat.avg_click_position,
                "avg_impression_position": stat.avg_impression_position
            })
        
        return {
            "success": True,
            "data": {
                "query": query,
                "period_days": days,
                "total_clicks": total_clicks,
                "total_impressions": total_impressions,
                "avg_ctr": round(avg_ctr, 2),
                "avg_position": round(avg_position, 2),
                "days_appeared": len(query_stats),
                "category": query_stats[0].category,
                "is_brand_query": query_stats[0].is_brand_query,
                "daily_performance": daily_data
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting query details: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/sites")
async def get_user_sites(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get list of sites with stored Bing analytics data.
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        logger.info(f"Getting user sites for user {user_id}")
        
        db = storage_service._get_db_session()
        
        # Get unique sites for the user
        sites = db.query(storage_service.BingDailyMetrics.site_url).filter(
            storage_service.BingDailyMetrics.user_id == user_id
        ).distinct().all()
        
        db.close()
        
        sites_data = []
        for site_tuple in sites:
            site_url = site_tuple[0]
            
            # Get latest metrics for each site
            summary = storage_service.get_analytics_summary(user_id, site_url, 7)
            
            sites_data.append({
                "site_url": site_url,
                "latest_summary": summary if 'error' not in summary else None,
                "has_data": 'error' not in summary
            })
        
        return {
            "success": True,
            "data": sites_data,
            "total_sites": len(sites_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user sites: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/generate-daily-metrics")
async def generate_daily_metrics(
    background_tasks: BackgroundTasks,
    site_url: str = Query(..., description="Site URL to generate metrics for"),
    target_date: Optional[str] = Query(None, description="Target date (YYYY-MM-DD), defaults to yesterday"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Generate daily metrics for a specific date from stored raw data.
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Parse target date
        if target_date:
            try:
                target_dt = datetime.strptime(target_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        else:
            target_dt = None
        
        logger.info(f"Generating daily metrics for user {user_id}, site: {site_url}, date: {target_dt}")
        
        storage_service = get_storage_service(user_id)
        
        # Run in background
        background_tasks.add_task(
            storage_service.generate_daily_metrics,
            user_id=user_id,
            site_url=site_url,
            target_date=target_dt
        )
        
        return {
            "success": True,
            "message": f"Daily metrics generation started for {site_url}",
            "site_url": site_url,
            "target_date": target_dt.isoformat() if target_dt else "yesterday"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating daily metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
