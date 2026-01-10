"""
Subscription API Module
Main router that includes all subscription-related endpoints.
"""

from fastapi import APIRouter

from .routes import (
    usage,
    plans,
    subscriptions,
    alerts,
    dashboard,
    logs,
    preflight
)

# Create main router
router = APIRouter(prefix="/api/subscription", tags=["subscription"])

# Include all sub-routers
router.include_router(usage.router, tags=["subscription"])
router.include_router(plans.router, tags=["subscription"])
router.include_router(subscriptions.router, tags=["subscription"])
router.include_router(alerts.router, tags=["subscription"])
router.include_router(dashboard.router, tags=["subscription"])
router.include_router(logs.router, tags=["subscription"])
router.include_router(preflight.router, tags=["subscription"])

__all__ = ["router"]
