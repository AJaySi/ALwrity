"""Social Optimizer endpoints."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from .models import SocialOptimizeRequest, SocialOptimizeResponse, PlatformFormatsResponse
from .deps import get_studio_manager, _require_user_id
from services.image_studio import ImageStudioManager, SocialOptimizerRequest
from services.image_studio.templates import Platform
from middleware.auth_middleware import get_current_user
from utils.logger_utils import get_service_logger

logger = get_service_logger("api.image_studio")
router = APIRouter(tags=["image-studio"])


@router.post("/social/optimize", response_model=SocialOptimizeResponse, summary="Optimize image for social platforms")
async def optimize_for_social(
    request: SocialOptimizeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Optimize an image for multiple social media platforms with smart cropping and safe zones."""
    try:
        user_id = _require_user_id(current_user, "social optimization")
        logger.info(f"[Social Optimizer] Request from user {user_id}: platforms={request.platforms}")

        platforms = []
        for platform_str in request.platforms:
            try:
                platforms.append(Platform(platform_str.lower()))
            except ValueError:
                logger.warning(f"[Social Optimizer] Invalid platform: {platform_str}")
                continue

        if not platforms:
            raise HTTPException(status_code=400, detail="No valid platforms provided")

        format_names = None
        if request.format_names:
            format_names = {}
            for platform_str, format_name in request.format_names.items():
                try:
                    platform = Platform(platform_str.lower())
                    format_names[platform] = format_name
                except ValueError:
                    logger.warning(f"[Social Optimizer] Invalid platform in format_names: {platform_str}")

        social_request = SocialOptimizerRequest(
            image_base64=request.image_base64,
            platforms=platforms,
            format_names=format_names,
            show_safe_zones=request.show_safe_zones,
            crop_mode=request.crop_mode,
            focal_point=request.focal_point,
            output_format=request.output_format,
            options={},
        )

        result = await studio_manager.optimize_for_social(social_request, user_id=user_id)
        return SocialOptimizeResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Social Optimizer] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Social optimization failed: {e}")


@router.get("/social/platforms/{platform}/formats", response_model=PlatformFormatsResponse, summary="Get platform formats")
async def get_platform_formats(
    platform: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get available formats for a social media platform."""
    try:
        try:
            platform_enum = Platform(platform.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")

        formats = studio_manager.get_social_platform_formats(platform_enum)
        return PlatformFormatsResponse(formats=formats)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Platform Formats] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to load platform formats: {e}")
