"""
Utility functions for Video Studio router.
"""

import json
import re
from typing import Any
from fastapi import HTTPException
from utils.logger_utils import get_service_logger

logger = get_service_logger("video_studio_router")


def extract_error_message(exc: Exception) -> str:
    """
    Extract user-friendly error message from exception.
    Handles HTTPException with nested error details from WaveSpeed API.
    """
    if isinstance(exc, HTTPException):
        detail = exc.detail
        # If detail is a dict (from WaveSpeed client)
        if isinstance(detail, dict):
            # Try to extract message from nested response JSON
            response_str = detail.get("response", "")
            if response_str:
                try:
                    response_json = json.loads(response_str)
                    if isinstance(response_json, dict) and "message" in response_json:
                        return response_json["message"]
                except (json.JSONDecodeError, TypeError):
                    pass
            # Fall back to error field
            if "error" in detail:
                return detail["error"]
        # If detail is a string
        elif isinstance(detail, str):
            return detail
    
    # For other exceptions, use string representation
    error_str = str(exc)
    
    # Try to extract meaningful message from HTTPException string format
    if "Insufficient credits" in error_str or "insufficient credits" in error_str.lower():
        return "Insufficient WaveSpeed credits. Please top up your account."
    
    # Try to extract JSON message from string
    try:
        json_match = re.search(r'"message"\s*:\s*"([^"]+)"', error_str)
        if json_match:
            return json_match.group(1)
    except Exception:
        pass
    
    return error_str
