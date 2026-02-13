"""
Podcast API Utility Functions

Helper functions for loading media files and other utilities.
"""

from pathlib import Path
from urllib.parse import urlparse
from fastapi import HTTPException
from loguru import logger

from .constants import PODCAST_AUDIO_DIR, PODCAST_IMAGES_DIR
from utils.media_utils import load_media_bytes


def load_podcast_audio_bytes(audio_url: str) -> bytes:
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
        
        # Podcast audio files are stored in podcast_audio directory
        audio_path = (PODCAST_AUDIO_DIR / filename).resolve()
        
        # Security check: ensure path is within PODCAST_AUDIO_DIR
        if not str(audio_path).startswith(str(PODCAST_AUDIO_DIR)):
            logger.error(f"[Podcast] Attempted path traversal when resolving audio: {audio_url}")
            raise HTTPException(status_code=403, detail="Invalid audio path")
        
        if not audio_path.exists():
            logger.warning(f"[Podcast] Audio file not found: {audio_path}")
            raise HTTPException(status_code=404, detail=f"Audio file not found: {filename}")
        
        return audio_path.read_bytes()
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[Podcast] Failed to load audio: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to load audio: {str(exc)}")


def load_podcast_image_bytes(image_url: str) -> bytes:
    """Load podcast image bytes from URL. Uses centralized media loader."""
    if not image_url:
        raise HTTPException(status_code=400, detail="Image URL is required")
    
    logger.info(f"[Podcast] Loading image from URL: {image_url}")
    
    try:
        # REUSE: Use centralized media loader which handles cross-module lookups
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

