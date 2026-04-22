"""
Assets Serving Router

Serves user-uploaded assets (avatars, voice samples) from workspace storage.
Uses authenticated or query-token access for security.
Audio MIME types are set correctly based on file extension so browsers
can play voice clone previews without NotSupportedError.
"""

import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from loguru import logger
from typing import Dict, Any

from middleware.auth_middleware import get_current_user_with_query_token
from api.story_writer.utils.auth import require_authenticated_user
from utils.storage_paths import get_repo_root, sanitize_user_id

router = APIRouter(prefix="/api/assets", tags=["Assets Serving"])

MIME_MAP = {
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".ogg": "audio/ogg",
    ".opus": "audio/opus",
    ".webm": "audio/webm",
    ".m4a": "audio/mp4",
    ".aac": "audio/aac",
    ".flac": "audio/flac",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}


def _resolve_asset_path(user_id: str, category: str, filename: str) -> Path:
    """Resolve asset path in user workspace with path-traversal protection."""
    safe_user_id = sanitize_user_id(user_id)
    repo_root = get_repo_root()

    file_path = (repo_root / "workspace" / f"workspace_{safe_user_id}" / "assets" / category / filename).resolve()

    workspace_dir = (repo_root / "workspace" / f"workspace_{safe_user_id}").resolve()
    if not str(file_path).startswith(str(workspace_dir)):
        raise HTTPException(status_code=403, detail="Access denied")

    return file_path


def _get_media_type(filename: str) -> str:
    """Determine MIME type from file extension, with fallback."""
    ext = Path(filename).suffix.lower()
    return MIME_MAP.get(ext, "application/octet-stream")


@router.get("/{user_id}/avatars/{filename}")
async def serve_avatar(
    user_id: str,
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user_with_query_token),
):
    """Serve avatar images. Supports auth via Authorization header or ?token= query param."""
    require_authenticated_user(current_user)

    safe_filename = os.path.basename(filename)
    file_path = _resolve_asset_path(user_id, "avatars", safe_filename)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Asset not found")

    media_type = _get_media_type(safe_filename)
    return FileResponse(file_path, media_type=media_type)


@router.get("/{user_id}/voice_samples/{filename}")
async def serve_voice_sample(
    user_id: str,
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user_with_query_token),
):
    """Serve voice sample audio files.

    Supports auth via Authorization header or ?token= query param.
    The ?token= param is essential for <audio> elements and new Audio()
    which cannot send Authorization headers.
    """
    require_authenticated_user(current_user)

    safe_filename = os.path.basename(filename)
    file_path = _resolve_asset_path(user_id, "voice_samples", safe_filename)

    if not file_path.exists():
        logger.info(f"[Assets] Voice sample not found: {file_path}")
        raise HTTPException(status_code=404, detail="Asset not found")

    media_type = _get_media_type(safe_filename)
    file_size = file_path.stat().st_size
    logger.warning(f"[Assets] Serving voice sample: {safe_filename} ({media_type}, {file_size} bytes)")
    return FileResponse(file_path, media_type=media_type)