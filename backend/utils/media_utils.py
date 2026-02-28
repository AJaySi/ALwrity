"""
Media Utility Functions

Centralized helper functions for loading and managing media assets across modules.
Promotes reuse between Podcast, YouTube, and other media-heavy modules.
"""

import logging
import os
from pathlib import Path
from typing import Optional, List
from urllib.parse import urlparse

from services.database import WORKSPACE_DIR

# Configure logging
logger = logging.getLogger(__name__)

# Base Directories
# backend/utils/media_utils.py -> parents[2] = backend/.. = root
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_MEDIA_DIR = ROOT_DIR / "data" / "media"

# Module-specific directories
YOUTUBE_AVATARS_DIR = DATA_MEDIA_DIR / "youtube_avatars"
YOUTUBE_IMAGES_DIR = DATA_MEDIA_DIR / "youtube_images"
PODCAST_IMAGES_DIR = DATA_MEDIA_DIR / "podcast_images"
PODCAST_AVATARS_DIR = PODCAST_IMAGES_DIR / "avatars"

# Ensure directories exist
for directory in [YOUTUBE_AVATARS_DIR, YOUTUBE_IMAGES_DIR, PODCAST_IMAGES_DIR, PODCAST_AVATARS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def resolve_media_path(media_url_or_path: str) -> Optional[Path]:
    """
    Resolve a media URL or filename to a concrete file path on disk.
    
    Handles cross-module lookups (e.g. checking podcast avatars if not found in youtube).
    
    Args:
        media_url_or_path: URL path (e.g. /api/youtube/avatars/foo.png) or filename
        
    Returns:
        Path object if found, None otherwise
    """
    if not media_url_or_path:
        return None
        
    try:
        # Extract filename from URL/path
        if "/" in media_url_or_path or "\\" in media_url_or_path:
            # It's a URL or path
            parsed = urlparse(media_url_or_path)
            path = parsed.path if parsed.scheme else media_url_or_path
            filename = path.split("/")[-1].split("?")[0]
        else:
            # It's just a filename
            filename = media_url_or_path.split("?")[0]
            
        if not filename:
            return None
            
        # Handle workspace avatar assets: /api/assets/{user_id}/avatars/{filename}
        if "/api/assets/" in media_url_or_path and "/avatars/" in media_url_or_path:
            try:
                parsed_path = urlparse(media_url_or_path).path
                parts = parsed_path.split("/")
                if len(parts) >= 6:
                    user_id = parts[3]
                    safe_user_id = "".join(c for c in user_id if c.isalnum() or c in ("-", "_"))
                    if safe_user_id == user_id:
                        safe_filename = os.path.basename(filename)
                        assets_path = Path(WORKSPACE_DIR) / f"workspace_{safe_user_id}" / "assets" / "avatars" / safe_filename
                        if assets_path.exists() and assets_path.is_file():
                            logger.debug(f"[MediaUtils] Resolved assets avatar {media_url_or_path} to {assets_path}")
                            return assets_path
            except Exception as exc:
                logger.error(f"[MediaUtils] Error resolving assets avatar path: {exc}")

        # Define search paths in order of likelihood
        # We search all avatar/image directories
        search_paths: List[Path] = [
            YOUTUBE_AVATARS_DIR / filename,
            PODCAST_AVATARS_DIR / filename,
            YOUTUBE_IMAGES_DIR / filename,
            PODCAST_IMAGES_DIR / filename,
            # Fallback for nested podcast images (if they exist directly in podcast_images)
            PODCAST_IMAGES_DIR / "avatars" / filename 
        ]
        
        # Check specific module based on URL prefix if present
        if "/api/youtube/" in media_url_or_path:
            # Prioritize YouTube paths
            pass # Already first in list
        elif "/api/podcast/" in media_url_or_path:
            # Prioritize Podcast paths
            search_paths = [
                PODCAST_AVATARS_DIR / filename,
                PODCAST_IMAGES_DIR / filename,
                YOUTUBE_AVATARS_DIR / filename,
                YOUTUBE_IMAGES_DIR / filename
            ]
            
        # Iterate and find first existing file
        for path in search_paths:
            if path.exists() and path.is_file():
                logger.debug(f"[MediaUtils] Resolved {media_url_or_path} to {path}")
                return path
                
        logger.warning(f"[MediaUtils] Could not resolve media path for: {media_url_or_path}")
        return None
        
    except Exception as e:
        logger.error(f"[MediaUtils] Error resolving media path: {e}")
        return None


def load_media_bytes(media_url_or_path: str) -> Optional[bytes]:
    """
    Load media bytes from a URL or path with cross-module fallback.
    
    Args:
        media_url_or_path: URL path or filename
        
    Returns:
        File bytes if found, None otherwise
    """
    path = resolve_media_path(media_url_or_path)
    if path:
        try:
            return path.read_bytes()
        except Exception as e:
            logger.error(f"[MediaUtils] Error reading file {path}: {e}")
            return None
    return None
