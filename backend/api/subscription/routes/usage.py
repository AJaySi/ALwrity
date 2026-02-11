"""
Usage statistics endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from loguru import logger

from services.database import get_db
from services.subscription import UsageTrackingService
from ..dependencies import verify_user_access
from middleware.auth_middleware import get_current_user

router = APIRouter()


@router.get("/usage/{user_id}")
async def get_user_usage(
    user_id: str,
    billing_period: Optional[str] = Query(None, description="Billing period (YYYY-MM)"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get comprehensive usage statistics for a user."""
    
    # Verify user can only access their own data
    verify_user_access(user_id, current_user)
    
    try:
        usage_service = UsageTrackingService(db)
        stats = usage_service.get_user_usage_stats(user_id, billing_period)
        
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting user usage: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user usage")


@router.get("/usage/{user_id}/trends")
async def get_usage_trends(
    user_id: str,
    months: int = Query(6, ge=1, le=24, description="Number of months to include"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get usage trends over time."""
    verify_user_access(user_id, current_user)
    
    try:
        usage_service = UsageTrackingService(db)
        trends = usage_service.get_usage_trends(user_id, months)
        
        return {
            "success": True,
            "data": trends
        }
    
    except Exception as e:
        logger.error(f"Error getting usage trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))
