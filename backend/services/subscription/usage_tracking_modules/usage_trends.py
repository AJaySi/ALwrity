"""
Usage trends functions.
Extracted from usage_tracking_service.py for better maintainability.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from loguru import logger

        
def get_usage_trends(user_id: str, months: int, db: Session) -> Dict[str, Any]:
    """Get usage trends over time with self-healing from logs."""
    from services.subscription.usage_tracking_helpers import build_billing_periods, query_usage_summaries, self_heal_summaries_from_logs, build_usage_trends_response
    
    periods = build_billing_periods(months)
    summary_dict = query_usage_summaries(db, user_id, periods)
    self_heal_summaries_from_logs(db, user_id, periods, summary_dict)
    return build_usage_trends_response(periods, summary_dict)
