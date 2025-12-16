"""
Podcast API Utility Functions

Helper functions for loading media files and other utilities.
"""

from pathlib import Path
from urllib.parse import urlparse
from fastapi import HTTPException
from loguru import logger

from .constants import PODCAST_AUDIO_DIR, PODCAST_IMAGES_DIR


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
    """Load podcast image bytes from URL. Only handles /api/podcast/images/ URLs."""
    if not image_url:
        raise HTTPException(status_code=400, detail="Image URL is required")
    
    logger.info(f"[Podcast] Loading image from URL: {image_url}")
    
    try:
        parsed = urlparse(image_url)
        path = parsed.path if parsed.scheme else image_url
        
        # Only handle /api/podcast/images/ URLs
        prefix = "/api/podcast/images/"
        if prefix not in path:
            logger.error(f"[Podcast] Unsupported image URL format: {image_url}")
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported image URL format: {image_url}. Only /api/podcast/images/ URLs are supported."
            )
        
        filename = path.split(prefix, 1)[1].split("?", 1)[0].strip()
        if not filename:
            logger.error(f"[Podcast] Could not extract filename from URL: {image_url}")
            raise HTTPException(status_code=400, detail=f"Could not extract filename from URL: {image_url}")
        
        logger.info(f"[Podcast] Extracted filename: {filename}")
        logger.info(f"[Podcast] PODCAST_IMAGES_DIR: {PODCAST_IMAGES_DIR}")
        
        # Podcast images are stored in podcast_images directory
        image_path = (PODCAST_IMAGES_DIR / filename).resolve()
        logger.info(f"[Podcast] Resolved image path: {image_path}")
        
        # Security check: ensure path is within PODCAST_IMAGES_DIR
        if not str(image_path).startswith(str(PODCAST_IMAGES_DIR)):
            logger.error(f"[Podcast] Attempted path traversal when resolving image: {image_url} -> {image_path}")
            raise HTTPException(status_code=403, detail="Invalid image path")
        
        if not image_path.exists():
            logger.error(f"[Podcast] Image file not found: {image_path}")
            raise HTTPException(status_code=404, detail=f"Image file not found: {filename}")
        
        image_bytes = image_path.read_bytes()
        logger.info(f"[Podcast] ✅ Successfully loaded image: {len(image_bytes)} bytes from {image_path}")
        return image_bytes
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[Podcast] Failed to load image: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to load image: {str(exc)}")

