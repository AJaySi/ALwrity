"""
API usage logs endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Dict, Any, Optional
from loguru import logger
import sqlite3

from services.database import get_db
from services.subscription.log_wrapping_service import LogWrappingService
from services.subscription.schema_utils import ensure_api_usage_logs_columns
from middleware.auth_middleware import get_current_user
from models.subscription_models import APIProvider, APIUsageLog
from ..dependencies import get_user_id_from_token
from ..utils import handle_schema_error

router = APIRouter()


@router.get("/usage-logs")
async def get_usage_logs(
    limit: int = Query(50, ge=1, le=5000, description="Number of logs to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    status_code: Optional[int] = Query(None, description="Filter by HTTP status code"),
    billing_period: Optional[str] = Query(None, description="Filter by billing period (YYYY-MM)"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get API usage logs for the current user.
    
    Query Params:
        - limit: Number of logs to return (1-5000, default: 50)
        - offset: Pagination offset (default: 0)
        - provider: Filter by provider (e.g., "gemini", "openai", "huggingface")
        - status_code: Filter by HTTP status code (e.g., 200 for success, 400+ for errors)
        - billing_period: Filter by billing period (YYYY-MM format)
    
    Returns:
        - List of usage logs with API call details
        - Total count for pagination
    """
    try:
        # Get user_id from current_user
        user_id = get_user_id_from_token(current_user)
        
        # Ensure schema columns exist (especially actual_provider_name)
        ensure_api_usage_logs_columns(db)
        
        # Build query
        query = db.query(APIUsageLog).filter(
            APIUsageLog.user_id == user_id
        )
        
        # Apply filters
        if provider:
            provider_lower = provider.lower()
            # Handle special case: huggingface maps to MISTRAL enum in database
            if provider_lower == "huggingface":
                provider_enum = APIProvider.MISTRAL
            else:
                try:
                    provider_enum = APIProvider(provider_lower)
                except ValueError:
                    # Invalid provider, return empty results
                    return {
                        "logs": [],
                        "total_count": 0,
                        "limit": limit,
                        "offset": offset,
                        "has_more": False
                    }
            query = query.filter(APIUsageLog.provider == provider_enum)
        
        if status_code is not None:
            query = query.filter(APIUsageLog.status_code == status_code)
        
        if billing_period:
            query = query.filter(APIUsageLog.billing_period == billing_period)
        
        # Check and wrap logs if necessary (before getting count)
        wrapping_service = LogWrappingService(db)
        wrap_result = wrapping_service.check_and_wrap_logs(user_id)
        if wrap_result.get('wrapped'):
            logger.info(f"[UsageLogs] Log wrapping completed for user {user_id}: {wrap_result.get('message')}")
            # Rebuild query after wrapping (in case filters changed)
            query = db.query(APIUsageLog).filter(
                APIUsageLog.user_id == user_id
            )
            # Reapply filters
            if provider:
                provider_lower = provider.lower()
                if provider_lower == "huggingface":
                    provider_enum = APIProvider.MISTRAL
                else:
                    try:
                        provider_enum = APIProvider(provider_lower)
                    except ValueError:
                        return {
                            "logs": [],
                            "total_count": 0,
                            "limit": limit,
                            "offset": offset,
                            "has_more": False
                        }
                query = query.filter(APIUsageLog.provider == provider_enum)
            if status_code is not None:
                query = query.filter(APIUsageLog.status_code == status_code)
            if billing_period:
                query = query.filter(APIUsageLog.billing_period == billing_period)
        
        # Get total count
        total_count = query.count()
        
        # Get paginated results, ordered by timestamp descending (most recent first)
        logs = query.order_by(desc(APIUsageLog.timestamp)).offset(offset).limit(limit).all()
        
        # Format logs for response
        formatted_logs = []
        for log in logs:
            # Determine status based on status_code
            status = 'success' if 200 <= log.status_code < 300 else 'failed'
            
            # Handle provider display name - use actual_provider_name if available, otherwise detect from model/endpoint
            # This correctly identifies WaveSpeed, Google, HuggingFace, etc. instead of generic VIDEO/AUDIO/STABILITY
            provider_display = None
            actual_provider_name = None
            
            # Safely get actual_provider_name (column may not exist yet)
            try:
                actual_provider_name = getattr(log, 'actual_provider_name', None)
            except (AttributeError, KeyError):
                actual_provider_name = None
            
            if actual_provider_name:
                # Use the actual provider name (WaveSpeed, Google, HuggingFace, etc.)
                provider_display = actual_provider_name
            else:
                # For old logs without actual_provider_name, detect from model name and endpoint
                from services.subscription.provider_detection import detect_actual_provider
                provider_display = detect_actual_provider(
                    provider_enum=log.provider,
                    model_name=log.model_used,
                    endpoint=log.endpoint
                )
                # Special handling for MISTRAL (HuggingFace)
                if provider_display == "mistral":
                    provider_display = "huggingface"
            
            formatted_logs.append({
                'id': log.id,
                'timestamp': log.timestamp.isoformat() if log.timestamp else None,
                'provider': provider_display,
                'actual_provider_name': actual_provider_name,  # Include for frontend use
                'model_used': log.model_used,
                'endpoint': log.endpoint,
                'method': log.method,
                'tokens_input': log.tokens_input or 0,
                'tokens_output': log.tokens_output or 0,
                'tokens_total': log.tokens_total or 0,
                'cost_input': float(log.cost_input) if log.cost_input else 0.0,
                'cost_output': float(log.cost_output) if log.cost_output else 0.0,
                'cost_total': float(log.cost_total) if log.cost_total else 0.0,
                'response_time': float(log.response_time) if log.response_time else 0.0,
                'status_code': log.status_code,
                'status': status,
                'error_message': log.error_message,
                'billing_period': log.billing_period,
                'retry_count': log.retry_count or 0,
                'is_aggregated': log.endpoint == "[AGGREGATED]"  # Flag to indicate aggregated log
            })
        
        return {
            "logs": formatted_logs,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count
        }
    
    except HTTPException:
        raise
    except (sqlite3.OperationalError, Exception) as e:
        error_str = str(e).lower()
        if 'no such column' in error_str and 'actual_provider_name' in error_str:
            return handle_schema_error(
                e,
                db,
                error_str,
                lambda: get_usage_logs(limit, offset, provider, status_code, billing_period, current_user, db)
            )
        
        logger.error(f"Error getting usage logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get usage logs: {str(e)}")
