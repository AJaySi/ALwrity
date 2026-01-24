"""Dependency injection for Image Studio API."""

# Absolute import for services
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from services.image_studio.studio_manager import ImageStudioManager


def get_studio_manager() -> ImageStudioManager:
    """Get Image Studio Manager instance."""
    return ImageStudioManager()