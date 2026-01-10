"""
Dashboard endpoints for comprehensive usage monitoring.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
from loguru import logger
import sqlite3

from services.database import get_db
from services.subscription import UsageTrackingService, PricingService
from services.subscription.schema_utils import ensure_subscription_plan_columns, ensure_usage_summaries_columns
from models.subscription_models import UsageAlert
from ..cache import get_cached_dashboard, set_cached_dashboard

router = APIRouter()


@router.get("/dashboard/{user_id}")
async def get_dashboard_data(
    user_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get comprehensive dashboard data for usage monitoring."""
    
    try:
        ensure_subscription_plan_columns(db)
        ensure_usage_summaries_columns(db)
        
        # Check cache first
        cached_data = get_cached_dashboard(user_id)
        if cached_data:
            return cached_data

        usage_service = UsageTrackingService(db)
        pricing_service = PricingService(db)
        
        # Get current usage stats
        current_usage = usage_service.get_user_usage_stats(user_id)
        
        # Get usage trends (last 6 months)
        trends = usage_service.get_usage_trends(user_id, 6)
        
        # Get user limits
        limits = pricing_service.get_user_limits(user_id)
        
        # Get unread alerts
        alerts = db.query(UsageAlert).filter(
            UsageAlert.user_id == user_id,
            UsageAlert.is_read == False
        ).order_by(UsageAlert.created_at.desc()).limit(5).all()
        
        alerts_data = [
            {
                "id": alert.id,
                "type": alert.alert_type,
                "title": alert.title,
                "message": alert.message,
                "severity": alert.severity,
                "created_at": alert.created_at.isoformat()
            }
            for alert in alerts
        ]
        
        # Calculate cost projections
        current_cost = current_usage.get('total_cost', 0)
        days_in_period = 30
        current_day = datetime.now().day
        projected_cost = (current_cost / current_day) * days_in_period if current_day > 0 else 0
        
        response_payload = {
            "success": True,
            "data": {
                "current_usage": current_usage,
                "trends": trends,
                "limits": limits,
                "alerts": alerts_data,
                "projections": {
                    "projected_monthly_cost": round(projected_cost, 2),
                    "cost_limit": limits.get('limits', {}).get('monthly_cost', 0) if limits else 0,
                    "projected_usage_percentage": (projected_cost / max(limits.get('limits', {}).get('monthly_cost', 1), 1)) * 100 if limits else 0
                },
                "summary": {
                    "total_api_calls_this_month": current_usage.get('total_calls', 0),
                    "total_cost_this_month": current_usage.get('total_cost', 0),
                    "usage_status": current_usage.get('usage_status', 'active'),
                    "unread_alerts": len(alerts_data)
                }
            }
        }
        
        # Cache the response
        set_cached_dashboard(user_id, response_payload)
        return response_payload
    
    except (sqlite3.OperationalError, Exception) as e:
        error_str = str(e).lower()
        if 'no such column' in error_str and ('exa_calls' in error_str or 'exa_cost' in error_str or 'video_calls' in error_str or 'video_cost' in error_str or 'image_edit_calls' in error_str or 'image_edit_cost' in error_str or 'audio_calls' in error_str or 'audio_cost' in error_str):
            logger.warning("Missing column detected in dashboard query, attempting schema fix...")
            try:
                import services.subscription.schema_utils as schema_utils
                schema_utils._checked_usage_summaries_columns = False
                schema_utils._checked_subscription_plan_columns = False
                # Use the already imported functions from top of file
                ensure_usage_summaries_columns(db)
                ensure_subscription_plan_columns(db)
                db.expire_all()
                
                # Retry the query
                usage_service = UsageTrackingService(db)
                pricing_service = PricingService(db)
                
                current_usage = usage_service.get_user_usage_stats(user_id)
                trends = usage_service.get_usage_trends(user_id, 6)
                limits = pricing_service.get_user_limits(user_id)
                
                alerts = db.query(UsageAlert).filter(
                    UsageAlert.user_id == user_id,
                    UsageAlert.is_read == False
                ).order_by(UsageAlert.created_at.desc()).limit(5).all()
                
                alerts_data = [
                    {
                        "id": alert.id,
                        "type": alert.alert_type,
                        "title": alert.title,
                        "message": alert.message,
                        "severity": alert.severity,
                        "created_at": alert.created_at.isoformat()
                    }
                    for alert in alerts
                ]
                
                current_cost = current_usage.get('total_cost', 0)
                days_in_period = 30
                current_day = datetime.now().day
                projected_cost = (current_cost / current_day) * days_in_period if current_day > 0 else 0
                
                response_payload = {
                    "success": True,
                    "data": {
                        "current_usage": current_usage,
                        "trends": trends,
                        "limits": limits,
                        "alerts": alerts_data,
                        "projections": {
                            "projected_monthly_cost": round(projected_cost, 2),
                            "cost_limit": limits.get('limits', {}).get('monthly_cost', 0) if limits else 0,
                            "projected_usage_percentage": (projected_cost / max(limits.get('limits', {}).get('monthly_cost', 1), 1)) * 100 if limits else 0
                        },
                        "summary": {
                            "total_api_calls_this_month": current_usage.get('total_calls', 0),
                            "total_cost_this_month": current_usage.get('total_cost', 0),
                            "usage_status": current_usage.get('usage_status', 'active'),
                            "unread_alerts": len(alerts_data)
                        }
                    }
                }
                
                # Cache the response after successful retry
                set_cached_dashboard(user_id, response_payload)
                return response_payload
            except Exception as retry_err:
                logger.error(f"Schema fix and retry failed: {retry_err}")
                raise HTTPException(status_code=500, detail=f"Database schema error: {str(e)}")
        
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
