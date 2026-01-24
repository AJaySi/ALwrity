"""Input validation functions for Scheduler API"""

from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status
from loguru import logger


def validate_pagination_params(limit: int, offset: int, max_limit: int = 500) -> None:
    """
    Validate pagination parameters.

    Args:
        limit: Requested limit
        offset: Requested offset
        max_limit: Maximum allowed limit

    Raises:
        HTTPException: If validation fails
    """
    if limit < 1 or limit > max_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Limit must be between 1 and {max_limit}"
        )

    if offset < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Offset must be non-negative"
        )


def validate_event_log_cleanup_params(older_than_days: int) -> None:
    """
    Validate event log cleanup parameters.

    Args:
        older_than_days: Number of days to keep logs

    Raises:
        HTTPException: If validation fails
    """
    if older_than_days < 1 or older_than_days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="older_than_days must be between 1 and 365"
        )


def validate_task_trigger_params(task_type: str, task_id: str) -> None:
    """
    Validate manual task trigger parameters.

    Args:
        task_type: Type of task to trigger
        task_id: Task identifier

    Raises:
        HTTPException: If validation fails
    """
    valid_task_types = [
        'oauth_token_monitoring',
        'platform_insights',
        'website_analysis',
        'general'
    ]

    if task_type not in valid_task_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid task_type. Must be one of: {', '.join(valid_task_types)}"
        )

    if not task_id or not isinstance(task_id, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="task_id must be a non-empty string"
        )

    # Basic task_id format validation
    if len(task_id) < 3 or len(task_id) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="task_id must be between 3 and 100 characters"
        )


def validate_user_access(
    requested_user_id: str,
    current_user: Dict[str, Any],
    require_ownership: bool = True
) -> str:
    """
    Validate user access to resources.

    Args:
        requested_user_id: User ID being requested
        current_user: Current authenticated user
        require_ownership: Whether user must own the resource

    Returns:
        Validated user ID to use for operations

    Raises:
        HTTPException: If access is denied
    """
    try:
        authenticated_user_id = (
            current_user.get('sub') or
            current_user.get('user_id') or
            current_user.get('id') or
            current_user.get('clerk_user_id')
        )

        if not authenticated_user_id:
            logger.error("[Validation] No authenticated user ID found in current_user")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authenticated user required"
            )

        if require_ownership and authenticated_user_id != requested_user_id:
            logger.warning(
                f"[Validation] User {authenticated_user_id} attempted to access "
                f"resources for user {requested_user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only access your own resources"
            )

        return authenticated_user_id

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Validation] Error validating user access: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validating user access"
        )


def validate_task_retry_params(task_id: str, reset_failure_count: bool) -> None:
    """
    Validate task retry parameters.

    Args:
        task_id: Task identifier
        reset_failure_count: Whether to reset failure count

    Raises:
        HTTPException: If validation fails
    """
    if not task_id or not isinstance(task_id, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="task_id must be a non-empty string"
        )

    if not isinstance(reset_failure_count, bool):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="reset_failure_count must be a boolean"
        )


def validate_compression_params(
    format_type: Optional[str] = None,
    quality: Optional[int] = None,
    target_size_kb: Optional[int] = None
) -> None:
    """
    Validate image compression parameters.

    Args:
        format_type: Image format (jpeg, png, webp)
        quality: Compression quality (1-100)
        target_size_kb: Target file size in KB

    Raises:
        HTTPException: If validation fails
    """
    if format_type and format_type.lower() not in ['jpeg', 'jpg', 'png', 'webp']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="format must be one of: jpeg, png, webp"
        )

    if quality is not None and (quality < 1 or quality > 100):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="quality must be between 1 and 100"
        )

    if target_size_kb is not None and target_size_kb < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="target_size_kb must be greater than 0"
        )


def validate_conversion_params(
    target_format: str,
    quality: Optional[int] = None
) -> None:
    """
    Validate image format conversion parameters.

    Args:
        target_format: Target image format
        quality: Conversion quality (1-100)

    Raises:
        HTTPException: If validation fails
    """
    valid_formats = ['png', 'jpeg', 'jpg', 'webp', 'gif', 'bmp', 'tiff', 'tif']

    if target_format.lower() not in valid_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"target_format must be one of: {', '.join(valid_formats)}"
        )

    if quality is not None and (quality < 1 or quality > 100):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="quality must be between 1 and 100"
        )