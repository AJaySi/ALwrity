"""Shared error normalization helpers for backend API/service layers."""

from __future__ import annotations

import json
from typing import Any, Dict

from fastapi import HTTPException


def extract_error_metadata(exc: Exception) -> Dict[str, Any]:
    """Extract structured HTTP error metadata for polling clients."""
    if isinstance(exc, HTTPException):
        detail = exc.detail
        if isinstance(detail, dict):
            return {
                "error_status": exc.status_code,
                "error_data": detail,
            }
        if isinstance(detail, str):
            return {
                "error_status": exc.status_code,
                "error_data": {
                    "error": detail,
                    "message": detail,
                },
            }
    return {}


def extract_response_message(response_text: str) -> str:
    """Best-effort extraction of provider message from a JSON response string."""
    if not response_text:
        return ""
    try:
        parsed = json.loads(response_text)
        if isinstance(parsed, dict):
            return str(parsed.get("message") or parsed.get("error") or "")
    except (json.JSONDecodeError, TypeError, ValueError):
        return ""
    return ""


def is_insufficient_credits_message(message: str) -> bool:
    """Detect provider top-up/credit exhaustion messages."""
    lowered = (message or "").lower()
    return "insufficient credits" in lowered or "credit" in lowered


def build_wavespeed_topup_detail(operation_type: str) -> Dict[str, Any]:
    """Build unified WaveSpeed top-up payload for frontend subscription modal flows."""
    return {
        "error": "Insufficient WaveSpeed credits",
        "message": "Insufficient credits. Please top up to continue video generation.",
        "provider": "wavespeed",
        "usage_info": {
            "provider": "wavespeed",
            "type": "credits",
            "limit_type": "provider_credits",
            "operation_type": operation_type,
            "action_required": "top_up",
        },
    }


def normalize_wavespeed_topup_http_exception(exc: HTTPException, operation_type: str) -> HTTPException:
    """Convert nested WaveSpeed credit errors into unified HTTP 429 contract."""
    detail = exc.detail if isinstance(exc.detail, dict) else {}
    provider_message = ""

    if isinstance(detail, dict):
        response_text = str(detail.get("response") or "")
        provider_message = extract_response_message(response_text)
        if not provider_message:
            provider_message = str(detail.get("message") or detail.get("error") or "")

    if is_insufficient_credits_message(provider_message):
        return HTTPException(status_code=429, detail=build_wavespeed_topup_detail(operation_type))

    return exc
