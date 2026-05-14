"""
Usage alert functions.
Extracted from usage_tracking_service.py for better maintainability.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from loguru import logger

from models.subscription_models import UsageAlert, UsageSummary, APIProvider, UsageStatus


def check_usage_alerts(user_id: str, provider: APIProvider, 
                       billing_period: str, db: Session, pricing_service):
    """Check if usage alerts should be sent."""
    # Get current usage
    period_keys = {'billing_period': billing_period, 'lookup_periods': [billing_period]}
    summary = db.query(UsageSummary).filter(
        UsageSummary.user_id == user_id,
        UsageSummary.billing_period.in_(period_keys["lookup_periods"])
    ).first()
    
    if not summary:
        return
    
    # Get user limits
    limits = pricing_service.get_user_limits(user_id)
    if not limits:
        return
    
    # Check for alert thresholds (80%, 90%, 100%)
    thresholds = [80, 90, 100]
    
    for threshold in thresholds:
        # Check if alert already sent for this threshold
        existing_alert = db.query(UsageAlert).filter(
            UsageAlert.user_id == user_id,
            UsageAlert.billing_period == billing_period,
            UsageAlert.threshold_percentage == threshold,
            UsageAlert.provider == provider,
            UsageAlert.is_sent == True
        ).first()
        
        if existing_alert:
            continue
        
        # Check if threshold is reached
        provider_name = provider.value
        current_calls = getattr(summary, f"{provider_name}_calls", 0)
        call_limit = limits['limits'].get(f"{provider_name}_calls", 0)
        
        if call_limit > 0:
            usage_percentage = (current_calls / call_limit) * 100
            
            if usage_percentage >= threshold:
                create_usage_alert(
                    user_id=user_id,
                    provider=provider,
                    threshold=threshold,
                    current_usage=current_calls,
                    limit=call_limit,
                    billing_period=billing_period,
                    db=db
                )


def create_usage_alert(user_id: str, provider: APIProvider,
                       threshold: int, current_usage: int, limit: int,
                       billing_period: str, db: Session):
    """Create a usage alert."""
    
    # Determine alert type and severity
    if threshold >= 100:
        alert_type = "limit_reached"
        severity = "error"
        title = f"API Limit Reached - {provider.value.title()}"
        message = f"You have reached your {provider.value} API limit of {limit:,} calls for this billing period."
    elif threshold >= 90:
        alert_type = "usage_warning"
        severity = "warning"
        title = f"API Usage Warning - {provider.value.title()}"
        message = f"You have used {current_usage:,} of {limit:,} {provider.value} API calls ({threshold}% of your limit)."
    else:
        alert_type = "usage_warning"
        severity = "info"
        title = f"API Usage Notice - {provider.value.title()}"
        message = f"You have used {current_usage:,} of {limit:,} {provider.value} API calls ({threshold}% of your limit)."
    
    alert = UsageAlert(
        user_id=user_id,
        alert_type=alert_type,
        threshold_percentage=threshold,
        provider=provider,
        title=title,
        message=message,
        severity=severity,
        billing_period=billing_period
    )
    
    db.add(alert)
    logger.info(f"Created usage alert for {user_id}: {title}")
