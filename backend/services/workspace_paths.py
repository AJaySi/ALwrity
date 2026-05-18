"""Canonical workspace path helpers.

This module is the single authority for resolving tenant workspace paths.
"""

from pathlib import Path

from services.database import WORKSPACE_DIR
from utils.storage_paths import sanitize_user_id


def get_workspace_root() -> Path:
    """Return canonical workspace root directory path."""
    return Path(WORKSPACE_DIR)


def get_user_workspace_dir(user_id: str) -> Path:
    """Return canonical tenant workspace directory path for user_id."""
    safe_user_id = sanitize_user_id(user_id)
    return get_workspace_root() / f"workspace_{safe_user_id}"
