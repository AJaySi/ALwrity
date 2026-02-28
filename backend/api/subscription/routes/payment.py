from fastapi import APIRouter, Depends, HTTPException, Request, Header, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
from services.database import get_db
from services.subscription.stripe_service import StripeService
from middleware.auth_middleware import get_current_user
from loguru import logger
from models.subscription_models import SubscriptionTier, BillingCycle
import time
from collections import defaultdict

router = APIRouter()

class CreateCheckoutSessionRequest(BaseModel):
    tier: SubscriptionTier
    billing_cycle: BillingCycle
    success_url: str
    cancel_url: str

class CreatePortalSessionRequest(BaseModel):
    return_url: str


_checkout_rate_limit_window_seconds = 60
_checkout_rate_limit_max_requests = 10
_checkout_attempts_by_user: Dict[str, Any] = defaultdict(list)

@router.post("/create-checkout-session")
async def create_checkout_session(
    payload: CreateCheckoutSessionRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    request: Request = None
):
    """
    Create a Stripe Checkout Session for subscription.
    """
    user_id = current_user.get("sub") or current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    now = time.time()
    attempts = _checkout_attempts_by_user[user_id]
    window_start = now - _checkout_rate_limit_window_seconds
    attempts[:] = [ts for ts in attempts if ts >= window_start]
    attempts.append(now)
    _checkout_attempts_by_user[user_id] = attempts
    if len(attempts) > _checkout_rate_limit_max_requests:
        client_ip = request.client.host if request and request.client else "unknown"
        logger.warning(f"Checkout rate limit exceeded for user_id={user_id}, ip={client_ip}, attempts={len(attempts)} in { _checkout_rate_limit_window_seconds }s")
        raise HTTPException(status_code=429, detail="Too many checkout attempts. Please try again shortly.")

    user_email = current_user.get("email")

    stripe_service = StripeService(db)
    
    try:
        url = stripe_service.create_checkout_session(
            user_id=user_id,
            tier=payload.tier,
            billing_cycle=payload.billing_cycle,
            success_url=payload.success_url,
            cancel_url=payload.cancel_url,
            user_email=user_email
        )
        return {"url": url}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate checkout")

@router.post("/create-portal-session")
async def create_portal_session(
    payload: CreatePortalSessionRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a Stripe Customer Portal session for managing billing.
    """
    user_id = current_user.get("sub") or current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    stripe_service = StripeService(db)
    
    try:
        url = stripe_service.create_portal_session(
            user_id=user_id,
            return_url=payload.return_url
        )
        return {"url": url}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating portal session: {e}")
        raise HTTPException(status_code=500, detail="Failed to access billing portal")

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhooks.
    """
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")

    payload = await request.body()
    stripe_service = StripeService(db)
    
    try:
        # We need to run this potentially in background or await it
        # Since it's async, we can await it directly.
        await stripe_service.handle_webhook(payload, stripe_signature)
        return {"status": "success"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")
