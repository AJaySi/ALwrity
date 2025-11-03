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
from services.subscription import UsageTrackingService, PricingService
from services.subscription.schema_utils import ensure_subscription_plan_columns
from middleware.auth_middleware import get_current_user
from models.subscription_models import (
    APIProvider, SubscriptionPlan, UserSubscription, UsageSummary,
    APIProviderPricing, UsageAlert, SubscriptionTier, BillingCycle, UsageStatus
)

router = APIRouter(prefix="/api/subscription", tags=["subscription"])

# Simple in-process cache for dashboard responses to smooth bursts
# Cache key: (user_id). TTL-like behavior implemented via timestamp check
_dashboard_cache: Dict[str, Dict[str, Any]] = {}
_dashboard_cache_ts: Dict[str, float] = {}
_DASHBOARD_CACHE_TTL_SEC = 600.0

@router.get("/usage/{user_id}")
async def get_user_usage(
    user_id: str,
    billing_period: Optional[str] = Query(None, description="Billing period (YYYY-MM)"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get comprehensive usage statistics for a user."""
    
    # Verify user can only access their own data
    if current_user.get('id') != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
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
        # Ensure required columns exist (handles environments without migrations applied yet)
        ensure_subscription_plan_columns(db)
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
                    "ai_text_generation_calls": getattr(plan, 'ai_text_generation_calls_limit', None) or 0,
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
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get user's current subscription information."""
    
    # Verify user can only access their own data
    if current_user.get('id') != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        ensure_subscription_plan_columns(db)
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
                            "ai_text_generation_calls": getattr(free_plan, 'ai_text_generation_calls_limit', None) or 0,
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
                    "ai_text_generation_calls": getattr(subscription.plan, 'ai_text_generation_calls_limit', None) or 0,
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

@router.get("/status/{user_id}")
async def get_subscription_status(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get simple subscription status for enforcement checks."""

    # Verify user can only access their own data
    if current_user.get('id') != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        ensure_subscription_plan_columns(db)
        subscription = db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.is_active == True
        ).first()

        if not subscription:
            # Check if free tier exists
            free_plan = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.tier == SubscriptionTier.FREE,
                SubscriptionPlan.is_active == True
            ).first()

            if free_plan:
                return {
                    "success": True,
                    "data": {
                        "active": True,
                        "plan": "free",
                        "tier": "free",
                        "can_use_api": True,
                        "limits": {
                            "ai_text_generation_calls": getattr(free_plan, 'ai_text_generation_calls_limit', None) or 0,
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
                return {
                    "success": True,
                    "data": {
                        "active": False,
                        "plan": "none",
                        "tier": "none",
                        "can_use_api": False,
                        "reason": "No active subscription or free tier found"
                    }
                }

        # Check if subscription is within valid period; auto-advance if expired and auto_renew
        now = datetime.utcnow()
        if subscription.current_period_end < now:
            if getattr(subscription, 'auto_renew', False):
                # advance period
                try:
                    from services.pricing_service import PricingService
                    pricing = PricingService(db)
                    # reuse helper to ensure current
                    pricing._ensure_subscription_current(subscription)
                except Exception as e:
                    logger.error(f"Failed to auto-advance subscription: {e}")
            else:
                return {
                    "success": True,
                    "data": {
                        "active": False,
                        "plan": subscription.plan.tier.value,
                        "tier": subscription.plan.tier.value,
                        "can_use_api": False,
                        "reason": "Subscription expired"
                    }
                }

        return {
            "success": True,
            "data": {
                "active": True,
                "plan": subscription.plan.tier.value,
                "tier": subscription.plan.tier.value,
                "can_use_api": True,
                "limits": {
                    "ai_text_generation_calls": getattr(subscription.plan, 'ai_text_generation_calls_limit', None) or 0,
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
        logger.error(f"Error getting subscription status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/subscribe/{user_id}")
async def subscribe_to_plan(
    user_id: str,
    subscription_data: dict,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create or update a user's subscription (renewal)."""
    
    # Verify user can only subscribe/renew their own subscription
    if current_user.get('id') != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        ensure_subscription_plan_columns(db)
        plan_id = subscription_data.get('plan_id')
        billing_cycle = subscription_data.get('billing_cycle', 'monthly')

        if not plan_id:
            raise HTTPException(status_code=400, detail="plan_id is required")

        # Get the plan
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == plan_id,
            SubscriptionPlan.is_active == True
        ).first()

        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")

        # Check if user already has an active subscription
        existing_subscription = db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.is_active == True
        ).first()

        now = datetime.utcnow()

        if existing_subscription:
            # Update existing subscription
            existing_subscription.plan_id = plan_id
            existing_subscription.billing_cycle = BillingCycle(billing_cycle)
            existing_subscription.current_period_start = now
            existing_subscription.current_period_end = now + timedelta(
                days=365 if billing_cycle == 'yearly' else 30
            )
            existing_subscription.updated_at = now

            subscription = existing_subscription
        else:
            # Create new subscription
            subscription = UserSubscription(
                user_id=user_id,
                plan_id=plan_id,
                billing_cycle=BillingCycle(billing_cycle),
                current_period_start=now,
                current_period_end=now + timedelta(
                    days=365 if billing_cycle == 'yearly' else 30
                ),
                status=UsageStatus.ACTIVE,
                is_active=True,
                auto_renew=True
            )
            db.add(subscription)

        db.commit()

        # Get current usage BEFORE reset for logging
        current_period = datetime.utcnow().strftime("%Y-%m")
        usage_before = db.query(UsageSummary).filter(
            UsageSummary.user_id == user_id,
            UsageSummary.billing_period == current_period
        ).first()
        
        # Log renewal request details
        logger.info("=" * 80)
        logger.info(f"[SUBSCRIPTION RENEWAL] 🔄 Processing renewal request")
        logger.info(f"   ├─ User: {user_id}")
        logger.info(f"   ├─ Plan: {plan.name} (ID: {plan_id}, Tier: {plan.tier.value})")
        logger.info(f"   ├─ Billing Cycle: {billing_cycle}")
        logger.info(f"   ├─ Period Start: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"   └─ Period End: {subscription.current_period_end.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if usage_before:
            logger.info(f"   📊 Current Usage BEFORE Reset (Period: {current_period}):")
            logger.info(f"      ├─ Gemini: {usage_before.gemini_tokens or 0} tokens / {usage_before.gemini_calls or 0} calls")
            logger.info(f"      ├─ Mistral/HF: {usage_before.mistral_tokens or 0} tokens / {usage_before.mistral_calls or 0} calls")
            logger.info(f"      ├─ OpenAI: {usage_before.openai_tokens or 0} tokens / {usage_before.openai_calls or 0} calls")
            logger.info(f"      ├─ Stability (Images): {usage_before.stability_calls or 0} calls")
            logger.info(f"      ├─ Total Tokens: {usage_before.total_tokens or 0}")
            logger.info(f"      ├─ Total Calls: {usage_before.total_calls or 0}")
            logger.info(f"      └─ Usage Status: {usage_before.usage_status.value}")
        else:
            logger.info(f"   📊 No usage summary found for period {current_period} (will be created on reset)")

        # Clear subscription limits cache to force refresh on next check
        # IMPORTANT: Do this BEFORE resetting usage to ensure cache is cleared first
        try:
            from services.subscription import PricingService
            # Clear cache for this specific user (class-level cache shared across all instances)
            cleared_count = PricingService.clear_user_cache(user_id)
            logger.info(f"   🗑️  Cleared {cleared_count} subscription cache entries for user {user_id}")
            
            # Also expire all SQLAlchemy objects to force fresh reads
            db.expire_all()
            logger.info(f"   🔄 Expired all SQLAlchemy objects to force fresh reads")
        except Exception as cache_err:
            logger.error(f"   ❌ Failed to clear cache after subscribe: {cache_err}")

        # Reset usage status for current billing period so new plan takes effect immediately
        reset_result = None
        try:
            usage_service = UsageTrackingService(db)
            reset_result = await usage_service.reset_current_billing_period(user_id)
            
            # Force commit to ensure reset is persisted
            db.commit()
            
            # Expire all SQLAlchemy objects to force fresh reads
            db.expire_all()
            
            # Re-query usage summary from DB after reset to get fresh data (fresh query)
            usage_after = db.query(UsageSummary).filter(
                UsageSummary.user_id == user_id,
                UsageSummary.billing_period == current_period
            ).first()
            
            # Refresh the usage object if found to ensure we have latest data
            if usage_after:
                db.refresh(usage_after)
            
            if reset_result.get('reset'):
                logger.info(f"   ✅ Usage counters RESET successfully")
                if usage_after:
                    logger.info(f"   📊 New Usage AFTER Reset:")
                    logger.info(f"      ├─ Gemini: {usage_after.gemini_tokens or 0} tokens / {usage_after.gemini_calls or 0} calls")
                    logger.info(f"      ├─ Mistral/HF: {usage_after.mistral_tokens or 0} tokens / {usage_after.mistral_calls or 0} calls")
                    logger.info(f"      ├─ OpenAI: {usage_after.openai_tokens or 0} tokens / {usage_after.openai_calls or 0} calls")
                    logger.info(f"      ├─ Stability (Images): {usage_after.stability_calls or 0} calls")
                    logger.info(f"      ├─ Total Tokens: {usage_after.total_tokens or 0}")
                    logger.info(f"      ├─ Total Calls: {usage_after.total_calls or 0}")
                    logger.info(f"      └─ Usage Status: {usage_after.usage_status.value}")
                else:
                    logger.warning(f"   ⚠️  Usage summary not found after reset - may need to be created on next API call")
            else:
                logger.warning(f"   ⚠️  Reset returned: {reset_result.get('reason', 'unknown')}")
        except Exception as reset_err:
            logger.error(f"   ❌ Failed to reset usage after subscribe: {reset_err}", exc_info=True)
        
        logger.info(f"   ✅ Renewal completed: User {user_id} → {plan.name} ({billing_cycle})")
        logger.info("=" * 80)

        return {
            "success": True,
            "message": f"Successfully subscribed to {plan.name}",
            "data": {
                "subscription_id": subscription.id,
                "plan_name": plan.name,
                "billing_cycle": billing_cycle,
                "current_period_start": subscription.current_period_start.isoformat(),
                "current_period_end": subscription.current_period_end.isoformat(),
                "status": subscription.status.value,
                "limits": {
                    "ai_text_generation_calls": getattr(plan, 'ai_text_generation_calls_limit', None) or 0,
                    "gemini_calls": plan.gemini_calls_limit,
                    "openai_calls": plan.openai_calls_limit,
                    "anthropic_calls": plan.anthropic_calls_limit,
                    "mistral_calls": plan.mistral_calls_limit,
                    "tavily_calls": plan.tavily_calls_limit,
                    "serper_calls": plan.serper_calls_limit,
                    "metaphor_calls": plan.metaphor_calls_limit,
                    "firecrawl_calls": plan.firecrawl_calls_limit,
                    "stability_calls": plan.stability_calls_limit,
                    "monthly_cost": plan.monthly_cost_limit
                }
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subscribing to plan: {e}")
        db.rollback()
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
        ensure_subscription_plan_columns(db)
        # Serve from short TTL cache to avoid hammering DB on bursts
        import time
        now = time.time()
        import os
        nocache = False
        try:
            # Not having direct access to request here; provide env flag override as simple control
            nocache = os.getenv('SUBSCRIPTION_DASHBOARD_NOCACHE', 'false').lower() in {'1','true','yes','on'}
        except Exception:
            nocache = False
        if not nocache and user_id in _dashboard_cache and (now - _dashboard_cache_ts.get(user_id, 0)) < _DASHBOARD_CACHE_TTL_SEC:
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