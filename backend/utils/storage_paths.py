from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from loguru import logger

_SAFE_CHARS = {"-", "_"}


def sanitize_user_id(user_id: str) -> str:
    """Return filesystem-safe user id used in workspace folder names."""
    return "".join(c for c in str(user_id) if c.isalnum() or c in _SAFE_CHARS)


def _sanitize_segment(value: str, fallback: str) -> str:
    cleaned = "".join(c for c in str(value) if c.isalnum() or c in _SAFE_CHARS)
    return cleaned or fallback


def find_repo_root() -> Path:
    """Find the project repository root directory.

    Resolution order:
    1. ALWRITY_ROOT_DIR environment variable (explicit override for production)
    2. Deterministic path from this file (storage_paths.py is at utils/)
    3. Walk-up fallback looking for a 'backend/' directory at project root

    Returns an absolute, resolved Path.
    """
    env_root = os.environ.get("ALWRITY_ROOT_DIR")
    if env_root:
        root = Path(env_root).resolve()
        if root.is_dir():
            return root

    # storage_paths.py is at backend/utils/storage_paths.py
    # project root is parents[2] (utils -> backend -> root)
    this_file = Path(__file__).resolve()
    candidate = this_file.parents[2]

    if (candidate / "backend").is_dir():
        return candidate

    # Walk-up fallback for unusual deployments
    current = this_file.parent
    for _ in range(10):
        if (current / "backend").is_dir():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent

    return this_file.parents[2]


def get_repo_root() -> Path:
    """Return repository root as an absolute canonical path."""
    return find_repo_root()


def get_workspace_root() -> Path:
    """Return absolute canonical workspace root."""
    return (get_repo_root() / "workspace").resolve()


def get_user_workspace(user_id: str) -> Path:
    """Return absolute canonical workspace path for a given user."""
    safe_user_id = sanitize_user_id(user_id) or "anonymous"
    return (get_workspace_root() / f"workspace_{safe_user_id}").resolve()


def resolve_user_media_path(
    user_id: str,
    module_name: str,
    media_type: str,
    *subpaths: Iterable[str],
    create: bool = False,
) -> Path:
    """
    Resolve a canonical absolute media path under
    workspace/workspace_<safe_user_id>/media/<module>/<media_type>/...
    """
    safe_module = _sanitize_segment(module_name, "module")
    safe_media_type = _sanitize_segment(media_type, "files")

    base = get_user_workspace(user_id) / "media" / safe_module / safe_media_type
    path = (base.joinpath(*map(str, subpaths))).resolve()

    # Prevent escaping outside user workspace through crafted segments.
    workspace_root = get_user_workspace(user_id)
    if workspace_root not in path.parents and path != workspace_root:
        raise ValueError(f"Resolved path escapes workspace: {path}")

    if create:
        path.mkdir(parents=True, exist_ok=True)

    return path


def get_legacy_video_studio_upload_dirs() -> list[Path]:
    """Known historical global upload directories for Video Studio avatar files."""
    repo_root = get_repo_root()
    return [
        (repo_root / "backend" / "data" / "video_studio" / "uploads").resolve(),
        (repo_root / "backend" / "backend" / "data" / "video_studio" / "uploads").resolve(),
    ]


# Log resolved root at import time for production debugging
logger.info(f"[StoragePaths] Repository root resolved to: {get_repo_root()}")
