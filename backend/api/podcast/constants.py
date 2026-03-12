"""
Podcast API Constants

Centralized constants and directory configuration for podcast module.
"""

from pathlib import Path
from typing import Literal
from services.story_writer.audio_generation_service import StoryAudioGenerationService

# Directory paths
# router.py is at: backend/api/podcast/router.py
# parents[0] = backend/api/podcast/
# parents[1] = backend/api/
# parents[2] = backend/
# parents[3] = root/
ROOT_DIR = Path(__file__).resolve().parents[3]  # root/
DATA_MEDIA_DIR = ROOT_DIR / "data" / "media"

PODCAST_AUDIO_DIR = (DATA_MEDIA_DIR / "podcast_audio").resolve()
PODCAST_IMAGES_DIR = (DATA_MEDIA_DIR / "podcast_images").resolve()
PODCAST_VIDEOS_DIR = (DATA_MEDIA_DIR / "podcast_videos").resolve()

# Video subdirectory
AI_VIDEO_SUBDIR = Path("AI_Videos")

MediaType = Literal["audio", "image", "video"]


def _sanitize_user_id(user_id: str) -> str:
    return "".join(c for c in user_id if c.isalnum() or c in ("-", "_"))


def get_podcast_media_dir(
    media_type: MediaType,
    user_id: str | None = None,
    *,
    ensure_exists: bool = False,
) -> Path:
    """Resolve podcast media directory (tenant workspace first, legacy global fallback)."""
    media_subdir = {
        "audio": "podcast_audio",
        "image": "podcast_images",
        "video": "podcast_videos",
    }[media_type]

    if user_id:
        tenant_media_dir = ROOT_DIR / "workspace" / f"workspace_{_sanitize_user_id(user_id)}" / "media" / media_subdir
        resolved_dir = tenant_media_dir.resolve()
    else:
        resolved_dir = (DATA_MEDIA_DIR / media_subdir).resolve()

    if ensure_exists:
        resolved_dir.mkdir(parents=True, exist_ok=True)

    return resolved_dir


def get_podcast_media_read_dirs(media_type: MediaType, user_id: str | None = None) -> list[Path]:
    """Return ordered directories to search (tenant path first, then legacy global path)."""
    dirs: list[Path] = []
    if user_id:
        dirs.append(get_podcast_media_dir(media_type, user_id))
    dirs.append(get_podcast_media_dir(media_type, None))
    return dirs


def get_podcast_audio_service(user_id: str | None = None) -> StoryAudioGenerationService:
    """Build audio service lazily so directory creation happens only when needed."""
    output_dir = get_podcast_media_dir("audio", user_id, ensure_exists=True)
    return StoryAudioGenerationService(output_dir=str(output_dir))
