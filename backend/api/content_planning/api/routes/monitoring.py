"""
API Monitoring Routes
Simple endpoints to expose API monitoring and cache statistics.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from loguru import logger

from services.subscription import get_monitoring_stats, get_lightweight_stats
from services.comprehensive_user_data_cache_service import ComprehensiveUserDataCacheService
from services.database import get_db

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

@router.get("/api-stats")
async def get_api_statistics(minutes: int = 5) -> Dict[str, Any]:
    """Get current API monitoring statistics."""
    try:
        stats = await get_monitoring_stats(minutes)
        return {
            "status": "success",
            "data": stats,
            "message": "API monitoring statistics retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting API stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get API statistics")

@router.get("/lightweight-stats")
async def get_lightweight_statistics() -> Dict[str, Any]:
    """Get lightweight stats for dashboard header."""
    try:
        stats = await get_lightweight_stats()
        return {
            "status": "success",
            "data": stats,
            "message": "Lightweight monitoring statistics retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting lightweight stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get lightweight statistics")

@router.get("/cache-stats")
async def get_cache_statistics(db = None) -> Dict[str, Any]:
    """Get comprehensive user data cache statistics."""
    try:
        if not db:
            db = next(get_db())
        
        cache_service = ComprehensiveUserDataCacheService(db)
        cache_stats = cache_service.get_cache_stats()
        
        return {
            "status": "success",
            "data": cache_stats,
            "message": "Cache statistics retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get cache statistics")

@router.get("/health")
async def get_system_health() -> Dict[str, Any]:
    """Get overall system health status."""
    try:
        # Get lightweight API stats
        api_stats = await get_lightweight_stats()
        
        # Get cache stats if available
        cache_stats = {}
        try:
            db = next(get_db())
            cache_service = ComprehensiveUserDataCacheService(db)
            cache_stats = cache_service.get_cache_stats()
        except:
            cache_stats = {"error": "Cache service unavailable"}
        
        # Determine overall health
        system_health = api_stats['status']
        if api_stats['recent_errors'] > 10:
            system_health = "critical"
        
        return {
            "status": "success",
            "data": {
                "system_health": system_health,
                "icon": api_stats['icon'],
                "api_performance": {
                    "recent_requests": api_stats['recent_requests'],
                    "recent_errors": api_stats['recent_errors'],
                    "error_rate": api_stats['error_rate']
                },
                "cache_performance": cache_stats,
                "timestamp": api_stats['timestamp']
            },
            "message": f"System health: {system_health}"
        }
    except Exception as e:
        logger.error(f"Error getting system health: {str(e)}")
        return {
            "status": "error",
            "data": {
                "system_health": "unknown",
                "icon": "⚪",
                "error": str(e)
            },
            "message": "Failed to get system health"
        }
