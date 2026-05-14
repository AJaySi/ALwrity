"""
Usage statistics functions.
Extracted from usage_tracking_service.py for better maintainability.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from loguru import logger
from datetime import datetime

from models.subscription_models import UsageSummary, UsageStatus, APIProvider
from services.subscription.usage_tracking_modules.historical_usage import get_all_historical_usage, get_usage_for_period


def get_user_usage_stats(user_id: str, billing_period: str, db: Session, pricing_service) -> Dict[str, Any]:
    """Get comprehensive usage statistics for a user.
    When no billing_period is specified, returns ALL historical usage data.
    When a specific period is given, returns only that period's data."""
    
    if not user_id:
        logger.error("get_user_usage_stats called without user_id")
        raise ValueError("user_id is required")
    
    # If no billing_period requested, return ALL historical data
    if not billing_period:
        return get_all_historical_usage(user_id, db, pricing_service)
    
    # Return data for the specific billing period
    return get_usage_for_period(user_id, billing_period, db, pricing_service)
