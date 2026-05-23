"""Shared workspace path helpers.

Single authority for workspace root and per-user workspace paths.
"""

from pathlib import Path

from utils.storage_paths import get_repo_root, sanitize_user_id


def get_workspace_root() -> Path:
    """Return absolute workspace root directory under repo root."""
    return (get_repo_root() / "workspace").resolve()


def get_user_workspace_dir(user_id: str) -> Path:
    """Return absolute workspace directory for the given user."""
    safe_user_id = sanitize_user_id(user_id)
    return (get_workspace_root() / f"workspace_{safe_user_id}").resolve()
