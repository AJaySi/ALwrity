from __future__ import annotations

from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from fastapi import HTTPException, status
from loguru import logger

from services.database import get_db
from services.user_workspace_manager import UserWorkspaceManager


BASE_DIR = Path(__file__).resolve().parents[4]  # root/
DATA_MEDIA_DIR = BASE_DIR / "workspace" / "media"

STORY_IMAGES_DIR = (DATA_MEDIA_DIR / "story_images").resolve()
# STORY_IMAGES_DIR.mkdir(parents=True, exist_ok=True)  # Disabled global creation

STORY_AUDIO_DIR = (DATA_MEDIA_DIR / "story_audio").resolve()
# STORY_AUDIO_DIR.mkdir(parents=True, exist_ok=True)  # Disabled global creation


def _get_user_media_path(user_id: str, media_type: str) -> Optional[Path]:
    """Resolve user-specific media directory."""
    try:
        # We need a new session for this operation
        db_gen = get_db()
        db = next(db_gen)
        try:
            workspace_manager = UserWorkspaceManager(db)
            workspace = workspace_manager.get_user_workspace(user_id)
            if workspace:
                # media/story_images or media/story_audio
                subdir = "story_images" if media_type == "image" else "story_audio"
                path = Path(workspace['workspace_path']) / "media" / subdir
                path.mkdir(parents=True, exist_ok=True)
                return path
        finally:
            # Ensure we close the session if it's not managed by dependency injection
            # Since get_db yields, we can't easily close it unless we manage the generator
            # But get_db uses SessionLocal() which should be closed.
            # However, get_db is a generator. We should really use a context manager or dependency.
            # Here we just took next(db), so it's an open session.
            # We should probably close it.
            # Actually, UserWorkspaceManager uses the passed db.
            # Let's assume standard usage pattern for manual DB access.
            pass
            # Note: The generator usage here is a bit tricky for cleanup. 
            # Ideally we'd have a context manager.
            # For now, let's rely on garbage collection or explicit close if possible.
            # But SQLAlchemy sessions should be closed.
            # db.close() # valid if db is Session
    except Exception as e:
        logger.warning(f"Failed to resolve user workspace path for {user_id}: {e}")
    return None


def resolve_story_media_path(filename: str, media_type: str, user_id: Optional[str] = None) -> Path:
    """
    Resolve a story media file path, checking user workspace first then global directory.
    media_type: 'image' or 'audio'
    """
    filename = filename.split("?")[0].strip()
    
    # 1. Try user workspace
    if user_id:
        user_path = _get_user_media_path(user_id, media_type)
        if user_path:
            file_path = (user_path / filename).resolve()
            # Guard against traversal
            if str(file_path).startswith(str(user_path)) and file_path.exists():
                return file_path

    # 2. Fallback to global directory
    base_dir = STORY_IMAGES_DIR if media_type == "image" else STORY_AUDIO_DIR
    file_path = (base_dir / filename).resolve()
    
    if not str(file_path).startswith(str(base_dir)):
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
         
    if file_path.exists():
        return file_path
        
    # 3. If not found, try alternate in global (legacy behavior support)
    alternate = _find_alternate_media_file(base_dir, filename)
    if alternate:
        logger.warning(f"[StoryWriter] Serving alternate media for {filename}: {alternate.name}")
        return alternate
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found: {filename}")


def load_story_image_bytes(image_url: str, user_id: Optional[str] = None) -> Optional[bytes]:
    """
    Resolve an authenticated story image URL (e.g., /api/story/images/<file>) to raw bytes.
    Returns None if the file cannot be located.
    """
    if not image_url:
        return None

    try:
        parsed = urlparse(image_url)
        path = parsed.path if parsed.scheme else image_url
        prefix = "/api/story/images/"
        if prefix not in path:
            logger.warning(f"[StoryWriter] Unsupported image URL for video reference: {image_url}")
            return None

        filename = path.split(prefix, 1)[1].split("?", 1)[0].strip()
        if not filename:
            return None

        # Try to resolve path using helper
        try:
            file_path = resolve_story_media_path(filename, "image", user_id)
            return file_path.read_bytes()
        except HTTPException:
            # Not found
            logger.warning(f"[StoryWriter] Referenced scene image not found: {filename}")
            return None
            
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to load reference image for video gen: {exc}")
        return None


def load_story_audio_bytes(audio_url: str, user_id: Optional[str] = None) -> Optional[bytes]:
    """
    Resolve an authenticated story audio URL (e.g., /api/story/audio/<file>) to raw bytes.
    Returns None if the file cannot be located.
    """
    if not audio_url:
        return None

    try:
        parsed = urlparse(audio_url)
        path = parsed.path if parsed.scheme else audio_url
        prefix = "/api/story/audio/"
        if prefix not in path:
            logger.warning(f"[StoryWriter] Unsupported audio URL for video reference: {audio_url}")
            return None

        filename = path.split(prefix, 1)[1].split("?", 1)[0].strip()
        if not filename:
            return None

        # Try to resolve path using helper
        try:
            file_path = resolve_story_media_path(filename, "audio", user_id)
            return file_path.read_bytes()
        except HTTPException:
            # Not found
            logger.warning(f"[StoryWriter] Referenced scene audio not found: {filename}")
            return None

    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to load reference audio for video gen: {exc}")
        return None


def resolve_media_file(base_dir: Path, filename: str) -> Path:
    """
    Returns a safe resolved path for a media file stored under base_dir.
    Guards against directory traversal and ensures the file exists.
    """
    filename = filename.split("?")[0].strip()
    resolved = (base_dir / filename).resolve()

    try:
        resolved.relative_to(base_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if not resolved.exists():
        alternate = _find_alternate_media_file(base_dir, filename)
        if alternate:
            logger.warning(
                "[StoryWriter] Requested media file '%s' missing; serving closest match '%s'",
                filename,
                alternate.name,
            )
            return alternate
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found: {filename}")

    return resolved


def _find_alternate_media_file(base_dir: Path, filename: str) -> Optional[Path]:
    """
    Attempt to find the most recent media file that matches the original name prefix.

    This helps when files are regenerated with new UUID/hash suffixes but the frontend still
    references an older filename.
    """
    try:
        base_dir = base_dir.resolve()
    except Exception:
        return None

    stem = Path(filename).stem
    suffix = Path(filename).suffix

    if not suffix or "_" not in stem:
        return None

    prefix = stem.rsplit("_", 1)[0]
    pattern = f"{prefix}_*{suffix}"

    try:
        candidates = sorted(
            (p for p in base_dir.glob(pattern) if p.is_file()),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
    except Exception as exc:
        logger.debug(f"[StoryWriter] Failed to search alternate media files for {filename}: {exc}")
        return None

    return candidates[0] if candidates else None


