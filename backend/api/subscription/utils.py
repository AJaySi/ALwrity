"""
Shared utility functions for subscription API routes.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from loguru import logger

from models.subscription_models import SubscriptionPlan


def format_plan_limits(plan: SubscriptionPlan) -> Dict[str, Any]:
    """
    Format subscription plan limits for API response.
    
    Args:
        plan: SubscriptionPlan model instance
        
    Returns:
        Dictionary with formatted limits
    """
    return {
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
        "video_calls": getattr(plan, 'video_calls_limit', 0) or 0,
        "image_edit_calls": getattr(plan, 'image_edit_calls_limit', 0) or 0,
        "audio_calls": getattr(plan, 'audio_calls_limit', 0) or 0,
        "exa_calls": getattr(plan, 'exa_calls_limit', 0) or 0,
        "gemini_tokens": plan.gemini_tokens_limit,
        "openai_tokens": plan.openai_tokens_limit,
        "anthropic_tokens": plan.anthropic_tokens_limit,
        "mistral_tokens": plan.mistral_tokens_limit,
        "monthly_cost": plan.monthly_cost_limit
    }


def handle_schema_error(
    error: Exception,
    db: Session,
    error_str: str,
    retry_func: callable
) -> Any:
    """
    Handle database schema errors by fixing schema and retrying.
    
    Args:
        error: The original exception
        error_str: Lowercase string representation of error
        db: Database session
        retry_func: Function to retry after schema fix
        
    Returns:
        Result from retry_func
        
    Raises:
        HTTPException: If schema fix fails
    """
    if 'no such column' in error_str:
        logger.warning("Missing column detected, attempting schema fix...")
        try:
            import services.subscription.schema_utils as schema_utils
            
            # Reset schema check flags based on error type
            if 'exa_calls_limit' in error_str or 'video_calls_limit' in error_str or \
               'image_edit_calls_limit' in error_str or 'audio_calls_limit' in error_str:
                schema_utils._checked_subscription_plan_columns = False
                from services.subscription.schema_utils import ensure_subscription_plan_columns
                ensure_subscription_plan_columns(db)
            elif 'exa_calls' in error_str or 'exa_cost' in error_str or \
                 'video_calls' in error_str or 'video_cost' in error_str or \
                 'image_edit_calls' in error_str or 'image_edit_cost' in error_str or \
                 'audio_calls' in error_str or 'audio_cost' in error_str:
                schema_utils._checked_usage_summaries_columns = False
                schema_utils._checked_subscription_plan_columns = False
                from services.subscription.schema_utils import ensure_usage_summaries_columns, ensure_subscription_plan_columns
                ensure_usage_summaries_columns(db)
                ensure_subscription_plan_columns(db)
            elif 'actual_provider_name' in error_str:
                schema_utils._checked_api_usage_logs_columns = False
                from services.subscription.schema_utils import ensure_api_usage_logs_columns
                ensure_api_usage_logs_columns(db)
            
            db.expire_all()
            return retry_func()
        except Exception as retry_err:
            logger.error(f"Schema fix and retry failed: {retry_err}")
            raise HTTPException(status_code=500, detail=f"Database schema error: {str(error)}")
    
    raise error
