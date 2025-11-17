from __future__ import annotations

from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from fastapi import HTTPException, status
from loguru import logger


BASE_DIR = Path(__file__).resolve().parents[3]  # backend/
STORY_IMAGES_DIR = (BASE_DIR / "story_images").resolve()
STORY_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def load_story_image_bytes(image_url: str) -> Optional[bytes]:
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

        file_path = (STORY_IMAGES_DIR / filename).resolve()
        if not str(file_path).startswith(str(STORY_IMAGES_DIR)):
            logger.error(f"[StoryWriter] Attempted path traversal when resolving image: {image_url}")
            return None

        if not file_path.exists():
            logger.warning(f"[StoryWriter] Referenced scene image not found on disk: {file_path}")
            return None

        return file_path.read_bytes()
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to load reference image for video gen: {exc}")
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found: {filename}")

    return resolved


