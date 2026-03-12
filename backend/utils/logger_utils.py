"""
Logger utilities to prevent conflicts between different logging configurations.
"""

import hashlib
import json
from loguru import logger
import sys
from typing import Any, Dict, List, Optional


def safe_logger_config(format_string: str, level: str = "INFO"):
    """
    Safely configure logger without removing existing handlers.
    This prevents conflicts with the main logging configuration.
    
    Args:
        format_string: Log format string
        level: Log level
    """
    try:
        # Only add a new handler if we don't already have one with this format
        existing_handlers = logger._core.handlers
        for handler in existing_handlers:
            if hasattr(handler, '_sink') and handler._sink == sys.stdout:
                # Check if format is similar to avoid duplicates
                if hasattr(handler, '_format') and handler._format == format_string:
                    return  # Handler already exists with this format
        
        # Add new handler only if needed
        logger.add(
            sys.stdout,
            level=level,
            format=format_string,
            colorize=True
        )
    except Exception as e:
        # If there's any error, just use the existing logger configuration
        pass


def get_service_logger(service_name: str, format_string: str = None):
    """
    Get a logger for a specific service without conflicting with main configuration.
    
    Args:
        service_name: Name of the service
        format_string: Optional custom format string
        
    Returns:
        Logger instance
    """
    if format_string:
        safe_logger_config(format_string)
    
    return logger.bind(service=service_name)


def _mask_tenant_user_id(tenant_user_id: Optional[str]) -> Optional[str]:
    """Return a stable hash for a tenant user id so logs avoid exposing raw IDs."""
    if not tenant_user_id:
        return None
    return hashlib.sha256(tenant_user_id.encode("utf-8")).hexdigest()[:12]


def emit_routing_event(
    service_logger,
    *,
    flow_type: str,
    route_intent: str,
    provider_selected: Optional[str],
    model_selected: Optional[str],
    preferred_provider: Optional[str],
    fallback_count: int = 0,
    fallback_models_tried: Optional[List[str]] = None,
    tenant_user_id: Optional[str] = None,
    event_name: str = "llm_routing_event",
    level: str = "INFO",
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Emit a standardized structured model-routing event for AI facades."""
    payload: Dict[str, Any] = {
        "event_name": event_name,
        "flow_type": flow_type,
        "route_intent": route_intent,
        "flow_type/route_intent": f"{flow_type}/{route_intent}",
        "provider_selected": provider_selected,
        "model_selected": model_selected,
        "preferred_provider": preferred_provider,
        "fallback_count": fallback_count,
        "fallback_models_tried": fallback_models_tried or [],
        "tenant_user_id": _mask_tenant_user_id(tenant_user_id),
    }
    if extra:
        payload.update(extra)

    log_method = getattr(service_logger, level.lower(), service_logger.info)
    log_method("{}", json.dumps(payload, sort_keys=True))
    return payload
