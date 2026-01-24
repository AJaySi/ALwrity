"""YouTube API Dependencies

FastAPI dependency injection functions for YouTube API services.
Provides clean separation of service instantiation and dependency management.
"""

from services.youtube.planner import YouTubePlannerService
from services.youtube.scene_builder import YouTubeSceneBuilderService
from services.youtube.renderer import YouTubeVideoRendererService
from services.persona_data_service import PersonaDataService
from services.subscription import PricingService
from services.content_asset_service import ContentAssetService
from services.subscription.preflight_validator import validate_scene_animation_operation


def get_youtube_planner_service() -> YouTubePlannerService:
    """Get YouTube Planner Service instance."""
    return YouTubePlannerService()


def get_youtube_scene_builder_service() -> YouTubeSceneBuilderService:
    """Get YouTube Scene Builder Service instance."""
    return YouTubeSceneBuilderService()


def get_youtube_renderer_service() -> YouTubeVideoRendererService:
    """Get YouTube Video Renderer Service instance."""
    return YouTubeVideoRendererService()


def get_persona_data_service() -> PersonaDataService:
    """Get Persona Data Service instance."""
    return PersonaDataService()


def get_pricing_service() -> PricingService:
    """Get Pricing Service instance."""
    return PricingService()


def get_content_asset_service() -> ContentAssetService:
    """Get Content Asset Service instance."""
    return ContentAssetService()


def get_scene_animation_validator():
    """Get scene animation validation function."""
    return validate_scene_animation_operation