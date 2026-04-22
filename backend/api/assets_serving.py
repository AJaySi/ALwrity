"""
Assets Serving Router

Serves user-uploaded assets (avatars, voice samples) from workspace storage.
Uses authenticated or query-token access for security.
"""

import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from loguru import logger
from typing import Dict, Any

from middleware.auth_middleware import get_current_user_with_query_token, get_current_user
from api.story_writer.utils.auth import require_authenticated_user
from utils.storage_paths import get_repo_root

router = APIRouter(prefix="/api/assets", tags=["Assets Serving"])

# MIME type map for common audio/image formats (by file extension)
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
    """Resolve an asset file path in the user's workspace.

    Args:
        user_id: Clerk user ID (already validated)
        category: Subdirectory under assets/ (e.g. 'avatars', 'voice_samples')
        filename: The file name (already sanitized)

    Returns:
        Resolved absolute Path to the asset file.
    """
    from utils.storage_paths import sanitize_user_id

    safe_user_id = sanitize_user_id(user_id)
    repo_root = get_repo_root()

    # Primary path: workspace/workspace_{user_id}/assets/{category}/{filename}
    primary = (repo_root / "workspace" / f"workspace_{safe_user_id}" / "assets" / category / filename).resolve()

    # Security: ensure resolved path doesn't escape the workspace
    workspace_dir = (repo_root / "workspace" / f"workspace_{safe_user_id}").resolve()
    if not str(primary).startswith(str(workspace_dir)):
        raise HTTPException(status_code=403, detail="Access denied")

    return primary


def _get_media_type(filename: str) -> str:
    """Determine MIME type from file extension, with a default fallback."""
    ext = Path(filename).suffix.lower()
    return MIME_MAP.get(ext, "application/octet-stream")


@router.get("/{user_id}/avatars/{filename}")
async def serve_avatar(
    user_id: str,
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user_with_query_token),
):
    """Serve avatar images. Supports auth via header or query token for <img> elements."""
    require_authenticated_user(current_user)

    safe_filename = os.path.basename(filename)
    file_path = _resolve_asset_path(user_id, "avatars", safe_filename)

    if not file_path.exists():
        logger.debug(f"[Assets] Avatar not found: {file_path}")
        raise HTTPException(status_code=404, detail="Asset not found")

    media_type = _get_media_type(safe_filename)
    return FileResponse(file_path, media_type=media_type)


@router.get("/{user_id}/voice_samples/{filename}")
async def serve_voice_sample(
    user_id: str,
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user_with_query_token),
):
    """Serve voice sample audio files. Supports auth via header or query token for <audio> elements."""
    require_authenticated_user(current_user)

    safe_filename = os.path.basename(filename)
    file_path = _resolve_asset_path(user_id, "voice_samples", safe_filename)

    if not file_path.exists():
        logger.debug(f"[Assets] Voice sample not found: {file_path}")
        raise HTTPException(status_code=404, detail="Asset not found")

    media_type = _get_media_type(safe_filename)
    logger.debug(f"[Assets] Serving voice sample: {file_path} ({media_type}, {file_path.stat().st_size} bytes)")
    return FileResponse(file_path, media_type=media_type)