"""YouTube API Utilities

Shared utility functions for the YouTube API including authentication helpers,
task execution utilities, and common operations.
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException, status

from utils.logger_utils import get_service_logger

logger = get_service_logger("api.youtube.utils")


def require_authenticated_user(current_user: Dict[str, Any]) -> str:
    """Extract and validate user ID from current user.

    Args:
        current_user: User object from authentication middleware

    Returns:
        str: Validated user ID

    Raises:
        HTTPException: If user is not authenticated
    """
    user_id = current_user.get("id") if current_user else None
    if not user_id:
        logger.error("[YouTubeAPI] Authentication failed - missing user ID")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return str(user_id)


def validate_video_resolution(resolution: str) -> str:
    """Validate and normalize video resolution.

    Args:
        resolution: Video resolution string

    Returns:
        str: Validated resolution

    Raises:
        HTTPException: If resolution is invalid
    """
    from .constants import SUPPORTED_RESOLUTIONS

    if resolution not in SUPPORTED_RESOLUTIONS:
        logger.error(f"[YouTubeAPI] Invalid resolution: {resolution}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid resolution. Supported: {', '.join(SUPPORTED_RESOLUTIONS)}"
        )
    return resolution


def validate_video_type(video_type: Optional[str]) -> Optional[str]:
    """Validate video type if provided.

    Args:
        video_type: Video type string or None

    Returns:
        Optional[str]: Validated video type or None

    Raises:
        HTTPException: If video type is invalid
    """
    if video_type is None:
        return None

    from .constants import SUPPORTED_VIDEO_TYPES

    if video_type not in SUPPORTED_VIDEO_TYPES:
        logger.error(f"[YouTubeAPI] Invalid video type: {video_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid video type. Supported: {', '.join(SUPPORTED_VIDEO_TYPES)}"
        )
    return video_type


def validate_duration_type(duration_type: str) -> str:
    """Validate duration type.

    Args:
        duration_type: Duration type string

    Returns:
        str: Validated duration type

    Raises:
        HTTPException: If duration type is invalid
    """
    from .constants import SUPPORTED_DURATION_TYPES

    if duration_type not in SUPPORTED_DURATION_TYPES:
        logger.error(f"[YouTubeAPI] Invalid duration type: {duration_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid duration type. Supported: {', '.join(SUPPORTED_DURATION_TYPES)}"
        )
    return duration_type


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations.

    Args:
        filename: Original filename

    Returns:
        str: Sanitized filename
    """
    import re
    # Remove or replace dangerous characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores and whitespace
    sanitized = sanitized.strip('_ \t\n\r')
    return sanitized


def generate_video_filename(user_id: str, video_type: str = "video", extension: str = "mp4") -> str:
    """Generate a unique filename for video files.

    Args:
        user_id: User ID
        video_type: Type of video (e.g., "scene", "final")
        extension: File extension

    Returns:
        str: Generated filename
    """
    import uuid
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"user_{user_id}_{video_type}_{timestamp}_{unique_id}.{extension}"


def calculate_video_duration_estimate(scene_count: int, duration_type: str) -> float:
    """Calculate estimated video duration based on scene count and duration type.

    Args:
        scene_count: Number of scenes
        duration_type: Video duration type ("shorts", "medium", "long")

    Returns:
        float: Estimated duration in seconds
    """
    # Average scene duration estimates by video type
    base_durations = {
        "shorts": 45,   # ~45 seconds for shorts
        "medium": 180,  # ~3 minutes for medium
        "long": 480     # ~8 minutes for long
    }

    base_duration = base_durations.get(duration_type, 180)
    # Estimate 15-25 seconds per scene depending on video type
    avg_scene_duration = 20 if duration_type == "shorts" else 25

    return min(base_duration, scene_count * avg_scene_duration)