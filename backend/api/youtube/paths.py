"""Centralized YouTube media paths and runtime directory creation."""

from pathlib import Path
from typing import Iterable, Optional

from services.workspace_dirs import ensure_user_workspace_dirs


BASE_DIR = Path(__file__).resolve().parents[3]
DATA_MEDIA_DIR = BASE_DIR / "workspace" / "media"
YOUTUBE_VIDEO_DIR = DATA_MEDIA_DIR / "youtube_videos"
YOUTUBE_AVATARS_DIR = DATA_MEDIA_DIR / "youtube_avatars"
YOUTUBE_IMAGES_DIR = DATA_MEDIA_DIR / "youtube_images"
YOUTUBE_AUDIO_DIR = DATA_MEDIA_DIR / "youtube_audio"


def ensure_youtube_media_dirs(user_id: str, capabilities: Optional[Iterable[str]] = None) -> None:
    """Ensure YouTube-related media directories at request/runtime."""
    ensure_user_workspace_dirs(user_id, capabilities=capabilities or {"media", "content"})
    for directory in [YOUTUBE_VIDEO_DIR, YOUTUBE_AVATARS_DIR, YOUTUBE_IMAGES_DIR, YOUTUBE_AUDIO_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
