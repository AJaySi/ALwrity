"""
Podcast API Utility Functions

Helper functions for loading media files and other utilities.
"""

from pathlib import Path
from urllib.parse import urlparse
from fastapi import HTTPException
from loguru import logger

from .constants import get_podcast_media_read_dirs
from utils.media_utils import load_media_bytes


def _resolve_podcast_media_file(
    filename: str,
    media_type: str,
    user_id: str | None = None,
    *,
    subdir: Path | None = None,
) -> Path:
    """Resolve podcast media file path from tenant workspace first, then legacy global dir."""
    clean_filename = filename.split("?", 1)[0].strip()
    if not clean_filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    for base_dir in get_podcast_media_read_dirs(media_type, user_id):
        target_dir = (base_dir / subdir).resolve() if subdir else base_dir.resolve()
        candidate = (target_dir / clean_filename).resolve()
        if not str(candidate).startswith(str(target_dir)):
            logger.error(f"[Podcast] Attempted path traversal for {media_type}: {filename}")
            raise HTTPException(status_code=403, detail="Invalid media path")
        if candidate.exists():
            return candidate

    raise HTTPException(status_code=404, detail=f"{media_type.capitalize()} file not found: {clean_filename}")


def load_podcast_audio_bytes(audio_url: str, user_id: str | None = None) -> bytes:
    """Load podcast audio bytes from URL. Only handles /api/podcast/audio/ URLs."""
    if not audio_url:
        raise HTTPException(status_code=400, detail="Audio URL is required")
    
    try:
        parsed = urlparse(audio_url)
        path = parsed.path if parsed.scheme else audio_url
        
        # Only handle /api/podcast/audio/ URLs
        prefix = "/api/podcast/audio/"
        if prefix not in path:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported audio URL format: {audio_url}. Only /api/podcast/audio/ URLs are supported."
            )
        
        filename = path.split(prefix, 1)[1].split("?", 1)[0].strip()
        if not filename:
            raise HTTPException(status_code=400, detail=f"Could not extract filename from URL: {audio_url}")

        audio_path = _resolve_podcast_media_file(filename, "audio", user_id)
        return audio_path.read_bytes()
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[Podcast] Failed to load audio: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to load audio: {str(exc)}")


def load_podcast_image_bytes(image_url: str, user_id: str | None = None) -> bytes:
    """Load podcast image bytes from URL. Resolves from workspace first."""
    if not image_url:
        raise HTTPException(status_code=400, detail="Image URL is required")
    
    logger.info(f"[Podcast] Loading image from URL: {image_url}")
    
    try:
        # Extract filename from URL path
        prefix = "/api/podcast/images/"
        if prefix in image_url:
            filename = image_url.split(prefix, 1)[1].split("?", 1)[0].strip()
            # Handle subdirectories like avatars/
            subdir = None
            if "/" in filename:
                subdir_part = filename.rsplit("/", 1)[0]
                subdir = Path(subdir_part)
                filename = filename.rsplit("/", 1)[1]
            
            try:
                image_path = _resolve_podcast_media_file(filename, "image", user_id, subdir=subdir)
                return image_path.read_bytes()
            except HTTPException:
                pass  # Fall through to centralized loader
        
        # Fall back to centralized media loader
        image_bytes = load_media_bytes(image_url)
        
        if not image_bytes:
            logger.error(f"[Podcast] Image file not found for URL: {image_url}")
            raise HTTPException(status_code=404, detail=f"Image file not found: {image_url}")
            
        logger.info(f"[Podcast] ✅ Successfully loaded image: {len(image_bytes)} bytes")
        return image_bytes
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[Podcast] Failed to load image: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to load image: {str(exc)}")
