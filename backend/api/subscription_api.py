"""
Subscription and Usage API Routes
Provides endpoints for subscription management and usage monitoring.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from loguru import logger
from functools import lru_cache

from services.database import get_db
from services.usage_tracking_service import UsageTrackingService
from services.pricing_service import PricingService
from models.subscription_models import (
    APIProvider, SubscriptionPlan, UserSubscription, UsageSummary, 
    APIProviderPricing, UsageAlert, SubscriptionTier
)

router = APIRouter(prefix="/api/subscription", tags=["subscription"])

# Simple in-process cache for dashboard responses to smooth bursts
# Cache key: (user_id). TTL-like behavior implemented via timestamp check
_dashboard_cache: Dict[str, Dict[str, Any]] = {}
_dashboard_cache_ts: Dict[str, float] = {}
_DASHBOARD_CACHE_TTL_SEC = 2.0

@router.get("/usage/{user_id}")
async def get_user_usage(
    user_id: str,
    billing_period: Optional[str] = Query(None, description="Billing period (YYYY-MM)"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get comprehensive usage statistics for a user."""
    
    try:
        usage_service = UsageTrackingService(db)
        stats = usage_service.get_user_usage_stats(user_id, billing_period)
        
        return {
            "success": True,
            "data": stats
        }
    
    except Exception as e:
        logger.error(f"Error getting user usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage/{user_id}/trends")
async def get_usage_trends(
    user_id: str,
    months: int = Query(6, ge=1, le=24, description="Number of months to include"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get usage trends over time."""
    
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

@router.get("/plans")
async def get_subscription_plans(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get all available subscription plans."""
    
    try:
        plans = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.is_active == True
        ).order_by(SubscriptionPlan.price_monthly).all()
        
        plans_data = []
        for plan in plans:
            plans_data.append({
                "id": plan.id,
                "name": plan.name,
                "tier": plan.tier.value,
                "price_monthly": plan.price_monthly,
                "price_yearly": plan.price_yearly,
                "description": plan.description,
                "features": plan.features or [],
                "limits": {
                    "gemini_calls": plan.gemini_calls_limit,
                    "openai_calls": plan.openai_calls_limit,
                    "anthropic_calls": plan.anthropic_calls_limit,
                    "mistral_calls": plan.mistral_calls_limit,
                    "tavily_calls": plan.tavily_calls_limit,
                    "serper_calls": plan.serper_calls_limit,
                    "metaphor_calls": plan.metaphor_calls_limit,
                    "firecrawl_calls": plan.firecrawl_calls_limit,
                    "stability_calls": plan.stability_calls_limit,
                    "gemini_tokens": plan.gemini_tokens_limit,
                    "openai_tokens": plan.openai_tokens_limit,
                    "anthropic_tokens": plan.anthropic_tokens_limit,
                    "mistral_tokens": plan.mistral_tokens_limit,
                    "monthly_cost": plan.monthly_cost_limit
                }
            })
        
        return {
            "success": True,
            "data": {
                "plans": plans_data,
                "total": len(plans_data)
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting subscription plans: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}/subscription")
async def get_user_subscription(
    user_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get user's current subscription information."""
    
    try:
        subscription = db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.is_active == True
        ).first()
        
        if not subscription:
            # Return free tier information
            free_plan = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.tier == SubscriptionTier.FREE
            ).first()
            
            if free_plan:
                return {
                    "success": True,
                    "data": {
                        "subscription": None,
                        "plan": {
                            "id": free_plan.id,
                            "name": free_plan.name,
                            "tier": free_plan.tier.value,
                            "price_monthly": free_plan.price_monthly,
                            "description": free_plan.description,
                            "is_free": True
                        },
                        "status": "free",
                        "limits": {
                            "gemini_calls": free_plan.gemini_calls_limit,
                            "openai_calls": free_plan.openai_calls_limit,
                            "anthropic_calls": free_plan.anthropic_calls_limit,
                            "mistral_calls": free_plan.mistral_calls_limit,
                            "tavily_calls": free_plan.tavily_calls_limit,
                            "serper_calls": free_plan.serper_calls_limit,
                            "metaphor_calls": free_plan.metaphor_calls_limit,
                            "firecrawl_calls": free_plan.firecrawl_calls_limit,
                            "stability_calls": free_plan.stability_calls_limit,
                            "monthly_cost": free_plan.monthly_cost_limit
                        }
                    }
                }
            else:
                raise HTTPException(status_code=404, detail="No subscription plan found")
        
        return {
            "success": True,
            "data": {
                "subscription": {
                    "id": subscription.id,
                    "billing_cycle": subscription.billing_cycle.value,
                    "current_period_start": subscription.current_period_start.isoformat(),
                    "current_period_end": subscription.current_period_end.isoformat(),
                    "status": subscription.status.value,
                    "auto_renew": subscription.auto_renew,
                    "created_at": subscription.created_at.isoformat()
                },
                "plan": {
                    "id": subscription.plan.id,
                    "name": subscription.plan.name,
                    "tier": subscription.plan.tier.value,
                    "price_monthly": subscription.plan.price_monthly,
                    "price_yearly": subscription.plan.price_yearly,
                    "description": subscription.plan.description,
                    "is_free": False
                },
                "limits": {
                    "gemini_calls": subscription.plan.gemini_calls_limit,
                    "openai_calls": subscription.plan.openai_calls_limit,
                    "anthropic_calls": subscription.plan.anthropic_calls_limit,
                    "mistral_calls": subscription.plan.mistral_calls_limit,
                    "tavily_calls": subscription.plan.tavily_calls_limit,
                    "serper_calls": subscription.plan.serper_calls_limit,
                    "metaphor_calls": subscription.plan.metaphor_calls_limit,
                    "firecrawl_calls": subscription.plan.firecrawl_calls_limit,
                    "stability_calls": subscription.plan.stability_calls_limit,
                    "monthly_cost": subscription.plan.monthly_cost_limit
                }
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting user subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pricing")
async def get_api_pricing(
    provider: Optional[str] = Query(None, description="API provider"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get API pricing information."""
    
    try:
        query = db.query(APIProviderPricing).filter(
            APIProviderPricing.is_active == True
        )
        
        if provider:
            try:
                api_provider = APIProvider(provider.lower())
                query = query.filter(APIProviderPricing.provider == api_provider)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")
        
        pricing_data = query.all()
        
        pricing_list = []
        for pricing in pricing_data:
            pricing_list.append({
                "provider": pricing.provider.value,
                "model_name": pricing.model_name,
                "cost_per_input_token": pricing.cost_per_input_token,
                "cost_per_output_token": pricing.cost_per_output_token,
                "cost_per_request": pricing.cost_per_request,
                "cost_per_search": pricing.cost_per_search,
                "cost_per_image": pricing.cost_per_image,
                "cost_per_page": pricing.cost_per_page,
                "description": pricing.description,
                "effective_date": pricing.effective_date.isoformat()
            })
        
        return {
            "success": True,
            "data": {
                "pricing": pricing_list,
                "total": len(pricing_list)
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting API pricing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts/{user_id}")
async def get_usage_alerts(
    user_id: str,
    unread_only: bool = Query(False, description="Only return unread alerts"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of alerts"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get usage alerts for a user."""
    
    try:
        query = db.query(UsageAlert).filter(
            UsageAlert.user_id == user_id
        )
        
        if unread_only:
            query = query.filter(UsageAlert.is_read == False)
        
        alerts = query.order_by(
            UsageAlert.created_at.desc()
        ).limit(limit).all()
        
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                "id": alert.id,
                "type": alert.alert_type,
                "threshold_percentage": alert.threshold_percentage,
                "provider": alert.provider.value if alert.provider else None,
                "title": alert.title,
                "message": alert.message,
                "severity": alert.severity,
                "is_sent": alert.is_sent,
                "sent_at": alert.sent_at.isoformat() if alert.sent_at else None,
                "is_read": alert.is_read,
                "read_at": alert.read_at.isoformat() if alert.read_at else None,
                "billing_period": alert.billing_period,
                "created_at": alert.created_at.isoformat()
            })
        
        return {
            "success": True,
            "data": {
                "alerts": alerts_data,
                "total": len(alerts_data),
                "unread_count": len([a for a in alerts_data if not a["is_read"]])
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting usage alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/{alert_id}/mark-read")
async def mark_alert_read(
    alert_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Mark an alert as read."""
    
    try:
        alert = db.query(UsageAlert).filter(UsageAlert.id == alert_id).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.is_read = True
        alert.read_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "message": "Alert marked as read"
        }
    
    except Exception as e:
        logger.error(f"Error marking alert as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/{user_id}")
async def get_dashboard_data(
    user_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get comprehensive dashboard data for usage monitoring."""
    
    try:
        # Serve from short TTL cache to avoid hammering DB on bursts
        import time
        now = time.time()
        if user_id in _dashboard_cache and (now - _dashboard_cache_ts.get(user_id, 0)) < _DASHBOARD_CACHE_TTL_SEC:
            return _dashboard_cache[user_id]

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
        _dashboard_cache[user_id] = response_payload
        _dashboard_cache_ts[user_id] = now
        return response_payload
    
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))