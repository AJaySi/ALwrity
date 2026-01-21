"""Shared utilities for Image Studio API."""

from typing import Dict, Any
from fastapi import HTTPException
from starlette import status

from ...utils.logger_utils import get_service_logger

logger = get_service_logger("api.image_studio")


def _require_user_id(current_user: Dict[str, Any], operation: str) -> str:
    """Ensure user_id is available for protected operations."""
    user_id = (
        current_user.get("sub")
        or current_user.get("user_id")
        or current_user.get("id")
        or current_user.get("clerk_user_id")
    )
    if not user_id:
        logger.error(
            "[Image Studio] ❌ Missing user_id for %s operation - blocking request",
            operation,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user required for image operations.",
        )
    return user_id