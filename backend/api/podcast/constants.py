"""
Podcast API Constants

Centralized constants and directory configuration for podcast module.
All workspace paths use utils.storage_paths for root resolution.
"""

import os
from pathlib import Path
from typing import Literal
from loguru import logger
from services.story_writer.audio_generation_service import StoryAudioGenerationService
from utils.storage_paths import get_repo_root, sanitize_user_id as _sanitize_user_id

ROOT_DIR = get_repo_root()

# Video subdirectory (relative to workspace media dir)
AI_VIDEO_SUBDIR = Path("AI_Videos")

# Legacy constants - DEPRECATED, use get_podcast_media_dir() instead
# Kept for backward compatibility with some handlers
PODCAST_AVATARS_SUBDIR = Path("avatars")

MediaType = Literal["audio", "image", "video", "chart"]


def get_podcast_media_dir(
    media_type: MediaType,
    user_id: str | None = None,
    *,
    ensure_exists: bool = False,
) -> Path:
    """
    Resolve podcast media directory (workspace-only for multi-tenant isolation).

    Requires user_id for tenant isolation. Falls back to default workspace
    only if no user_id provided (for backward compat in development).
    Logs a warning in production when user_id is missing.
    """
    media_subdir = {
        "audio": "podcast_audio",
        "image": "podcast_images",
        "video": "podcast_videos",
        "chart": "podcast_charts",
    }[media_type]

    if user_id:
        sanitized = _sanitize_user_id(user_id)
        resolved_dir = (
            ROOT_DIR / "workspace" / f"workspace_{sanitized}" / "media" / media_subdir
        ).resolve()
    else:
        logger.warning(f"[Podcast] get_podcast_media_dir called without user_id for {media_type} — using default workspace. This should not happen in production.")
        resolved_dir = (
            ROOT_DIR / "workspace" / "workspace_alwrity" / "media" / media_subdir
        ).resolve()

    if ensure_exists:
        resolved_dir.mkdir(parents=True, exist_ok=True)

    return resolved_dir


def get_podcast_media_read_dirs(media_type: MediaType, user_id: str | None = None) -> list[Path]:
    """
    Return directories to search for podcast media.
    Now workspace-only (no legacy fallback).
    """
    return [get_podcast_media_dir(media_type, user_id)]


def get_podcast_audio_service(user_id: str | None = None) -> StoryAudioGenerationService:
    """Build audio service lazily so directory creation happens only when needed."""
    output_dir = get_podcast_media_dir("audio", user_id, ensure_exists=True)
    return StoryAudioGenerationService(output_dir=str(output_dir))
