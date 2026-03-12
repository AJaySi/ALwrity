"""Workspace directory helpers.

Centralizes directory creation so API/service imports stay side-effect free.
"""

from pathlib import Path
from typing import Iterable, Optional, Set

from services.database import WORKSPACE_DIR


GLOBAL_OPERATIONAL_DIRS = {
    "logs": Path("logs"),
    "temp": Path("temp"),
}


USER_CAPABILITY_DIRS = {
    "core": {
        "config",
        "cache",
        "exports",
        "templates",
        "database",
        "db",
        "data",
    },
    "content": {
        "content",
        "content/images",
        "content/videos",
        "content/audio",
        "content/text",
        "content/youtube",
        "content/story",
    },
    "research": {"research"},
    "media": {"media"},
    "assets": {"assets", "assets/avatars", "assets/voice_samples"},
    "integrations": {"integrations"},
    "ai_services": {"config"},
}


def _sanitize_user_id(user_id: str) -> str:
    return "".join(c for c in user_id if c.isalnum() or c in ("-", "_"))


def ensure_global_operational_dirs(dir_names: Optional[Iterable[str]] = None) -> None:
    """Create only operational global directories (logs/temp), on demand."""
    targets = set(dir_names or GLOBAL_OPERATIONAL_DIRS.keys())
    for name in targets:
        directory = GLOBAL_OPERATIONAL_DIRS.get(name)
        if directory:
            directory.mkdir(parents=True, exist_ok=True)


def ensure_user_workspace_dirs(user_id: str, capabilities: Optional[Iterable[str]] = None) -> Path:
    """Ensure user workspace directories required by capabilities.

    Args:
        user_id: tenant/user identifier.
        capabilities: iterable of capability keys from USER_CAPABILITY_DIRS.
    """
    safe_user_id = _sanitize_user_id(user_id)
    user_dir = Path(WORKSPACE_DIR) / f"workspace_{safe_user_id}"

    requested = set(capabilities or {"core"})
    requested.add("core")

    subdirs: Set[str] = set()
    for capability in requested:
        subdirs.update(USER_CAPABILITY_DIRS.get(capability, set()))

    user_dir.mkdir(parents=True, exist_ok=True)
    for subdir in sorted(subdirs):
        (user_dir / subdir).mkdir(parents=True, exist_ok=True)

    return user_dir

