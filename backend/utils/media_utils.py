"""
Media Utility Functions

Centralized helper functions for loading and managing media assets across modules.
Promotes reuse between Podcast, YouTube, and other media-heavy modules.

DEPRECATED: The global DATA_MEDIA_DIR paths below are legacy and will be removed.
New code should use workspace-scoped paths via utils.storage_paths or module-specific
resolvers (e.g., api.podcast.constants.get_podcast_media_dir).
"""

import logging
import os
from pathlib import Path
from typing import Optional, List
from urllib.parse import urlparse

from services.database import WORKSPACE_DIR
from utils.storage_paths import get_repo_root

# Configure logging
logger = logging.getLogger(__name__)

# Base Directories — use get_repo_root() for consistent resolution
ROOT_DIR = get_repo_root()

# DEPRECATED: Global data/media paths — kept for backward-compat read fallback only.
# New writes must go to workspace-scoped paths. Do NOT add new consumers.
DATA_MEDIA_DIR = ROOT_DIR / "data" / "media"

# Module-specific directories (DEPRECATED — use workspace-scoped resolvers instead)
YOUTUBE_AVATARS_DIR = DATA_MEDIA_DIR / "youtube_avatars"
YOUTUBE_IMAGES_DIR = DATA_MEDIA_DIR / "youtube_images"
PODCAST_IMAGES_DIR = DATA_MEDIA_DIR / "podcast_images"
PODCAST_AVATARS_DIR = PODCAST_IMAGES_DIR / "avatars"

def ensure_media_dirs() -> None:
    """Create shared media directories at runtime."""
    for directory in [YOUTUBE_AVATARS_DIR, YOUTUBE_IMAGES_DIR, PODCAST_IMAGES_DIR, PODCAST_AVATARS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def resolve_media_path(media_url_or_path: str, user_id: Optional[str] = None) -> Optional[Path]:
    """
    Resolve a media URL or filename to a concrete file path on disk.
    
    Handles cross-module lookups (e.g. checking podcast avatars if not found in youtube).
    
    Args:
        media_url_or_path: URL path (e.g. /api/youtube/avatars/foo.png) or filename
        user_id: Optional user ID for tenant-scoped resolution (recommended)
        
    Returns:
        Path object if found, None otherwise
    """
    if not media_url_or_path:
        return None

    ensure_media_dirs()
        
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
                    asset_user_id = parts[3]
                    safe_user_id = "".join(c for c in asset_user_id if c.isalnum() or c in ("-", "_"))
                    if safe_user_id == asset_user_id:
                        safe_filename = os.path.basename(filename)
                        assets_path = Path(WORKSPACE_DIR) / f"workspace_{safe_user_id}" / "assets" / "avatars" / safe_filename
                        if assets_path.exists() and assets_path.is_file():
                            logger.debug(f"[MediaUtils] Resolved assets avatar {media_url_or_path} to {assets_path}")
                            return assets_path
            except Exception as exc:
                logger.error(f"[MediaUtils] Error resolving assets avatar path: {exc}")

        # Define search paths in order of likelihood
        # We search all avatar/image directories (DEPRECATED: global paths — kept for backward-compat reads)
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
            # Prioritize Podcast paths: use centralized podcast media resolution
            try:
                # Import the centralized function that checks tenant workspace first
                from api.podcast.constants import get_podcast_media_read_dirs
                podcast_dirs = get_podcast_media_read_dirs("image", user_id=user_id)
                search_paths = []
                for pod_dir in podcast_dirs:
                    # Add both avatar and image subdirectories
                    search_paths.append(pod_dir / "avatars" / filename)
                    search_paths.append(pod_dir / filename)
            except ImportError:
                # Fallback if podcast constants not available
                search_paths = [
                    PODCAST_AVATARS_DIR / filename,
                    PODCAST_IMAGES_DIR / filename,
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


# Audio format magic bytes signatures
_AUDIO_SIGNATURES = [
    (b"\xff\xfb", "mp3"),       # MP3 (MPEG-1 Layer 3, common)
    (b"\xff\xf3", "mp3"),       # MP3 (MPEG-2.5 Layer 3)
    (b"\xff\xf2", "mp3"),       # MP3 (MPEG-2 Layer 3)
    (b"\xff\xfa", "mp3"),       # MP3 (MPEG-2 Layer 3 variant)
    (b"ID3", "mp3"),            # MP3 with ID3 tag
    (b"RIFF", "wav"),           # WAV (RIFF header)
    (b"OggS", "ogg"),           # OGG
    (b"fLaC", "flac"),          # FLAC
    (b"\x1a\x45\xdf\xa3", "webm"),  # WebM / Matroska
    (b"ftyp", "m4a"),           # MP4/M4A (ftyp box follows offset 4)
]


def detect_audio_format(audio_bytes: bytes) -> tuple[str, str]:
    """Detect the actual audio format from content magic bytes.

    Returns:
        Tuple of (format_name, mime_type).
        Falls back to ('wav', 'audio/wav') if no signature matches.
    """
    if not audio_bytes or len(audio_bytes) < 4:
        return "wav", "audio/wav"

    for signature, fmt in _AUDIO_SIGNATURES:
        if signature == b"ftyp":
            # M4A/MP4: 'ftyp' appears at offset 4
            if len(audio_bytes) > 8 and audio_bytes[4:8] == b"ftyp":
                return "m4a", "audio/mp4"
        elif audio_bytes[:len(signature)] == signature:
            mime_map = {
                "mp3": "audio/mpeg",
                "wav": "audio/wav",
                "ogg": "audio/ogg",
                "flac": "audio/flac",
                "webm": "audio/webm",
                "m4a": "audio/mp4",
            }
            return fmt, mime_map.get(fmt, "audio/wav")

    # Check for Opus-in-OGG (Opus magic after OGG pages)
    if b"OpusHead" in audio_bytes[:100]:
        return "ogg", "audio/ogg"

    # Check for MP4/M4A container (atoms starting with size + type)
    if len(audio_bytes) > 8:
        atom_type = audio_bytes[4:8]
        if atom_type in (b"moov", b"mdat", b"free", b"skip"):
            return "m4a", "audio/mp4"

    return "wav", "audio/wav"


def ensure_audio_extension(filename: str, audio_bytes: bytes) -> str:
    """Adjust filename extension to match the actual audio format in audio_bytes.

    Args:
        filename: Original filename (may have wrong extension like .wav for mp3 data)
        audio_bytes: The actual audio data bytes

    Returns:
        Filename with corrected extension based on content format.
    """
    fmt, _ = detect_audio_format(audio_bytes)
    ext_map = {
        "mp3": ".mp3",
        "wav": ".wav",
        "ogg": ".ogg",
        "flac": ".flac",
        "webm": ".webm",
        "m4a": ".m4a",
        "opus": ".ogg",
    }

    correct_ext = ext_map.get(fmt, ".wav")
    path = Path(filename)
    current_ext = path.suffix.lower()

    if current_ext != correct_ext:
        logger.info(f"[MediaUtils] Correcting audio extension: {filename} -> {path.stem}{correct_ext} (detected format: {fmt})")
        return f"{path.stem}{correct_ext}"

    return filename
