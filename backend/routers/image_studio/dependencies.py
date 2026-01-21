"""Dependency injection for Image Studio API."""

from services.image_studio.studio_manager import ImageStudioManager


def get_studio_manager() -> ImageStudioManager:
    """Get Image Studio Manager instance."""
    return ImageStudioManager()