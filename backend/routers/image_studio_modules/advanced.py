"""Advanced features API endpoints for Image Studio."""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query

from routers.image_studio_modules.models import (
    FaceSwapRequest, FaceSwapResponse, FaceSwapModelsResponse,
    FaceSwapModelRecommendationRequest, FaceSwapModelRecommendationResponse,
    SocialOptimizeRequest, SocialOptimizeResponse, PlatformFormatsResponse,
    TransformImageToVideoRequestModel, TalkingAvatarRequestModel,
    TransformVideoResponse, TransformCostEstimateRequest, TransformCostEstimateResponse
)
from routers.image_studio_modules.utils import _require_user_id
from routers.image_studio_modules.dependencies import get_studio_manager

from services.image_studio import (
    ImageStudioManager, TransformImageToVideoRequest, TalkingAvatarRequest
)
from services.image_studio.face_swap_service import FaceSwapStudioRequest
from services.image_studio.templates import Platform
from middleware.auth_middleware import get_current_user
from utils.logger_utils import get_service_logger

logger = get_service_logger("api.image_studio.advanced")
router = APIRouter()


# ====================
# FACE SWAP STUDIO ENDPOINTS
# ====================

@router.post("/face-swap/process", response_model=FaceSwapResponse, summary="Process Face Swap")
async def process_face_swap(
    request: FaceSwapRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Process face swap request with auto-detection and model selection."""
    try:
        user_id = _require_user_id(current_user, "face swap")
        face_swap_request = FaceSwapStudioRequest(
            base_image_base64=request.base_image_base64,
            face_image_base64=request.face_image_base64,
            model=request.model,
            target_face_index=request.target_face_index,
            target_gender=request.target_gender,
            options=request.options,
        )
        result = await studio_manager.face_swap(face_swap_request, user_id=user_id)
        return FaceSwapResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Face Swap] ❌ Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Face swap failed: {e}")


@router.get("/face-swap/models", response_model=FaceSwapModelsResponse, summary="List available face swap models")
async def get_face_swap_models(
    tier: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get available WaveSpeed face swap models with metadata.

    Query Parameters:
    - tier: Filter by tier ("budget", "mid", "premium")
    """
    try:
        result = studio_manager.get_face_swap_models(tier=tier)
        return FaceSwapModelsResponse(**result)
    except Exception as e:
        logger.error(f"[Face Swap Models] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to load face swap models")


@router.post("/face-swap/recommend", response_model=FaceSwapModelRecommendationResponse, summary="Get face swap model recommendation")
async def recommend_face_swap_model(
    request: FaceSwapModelRecommendationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get recommended face swap model based on image resolutions and user preferences.

    Auto-detects best model when user doesn't specify one.
    """
    try:
        # Get user tier from current_user if available
        user_tier = request.user_tier
        if not user_tier and current_user:
            user_tier = current_user.get("tier") or current_user.get("subscription_tier")

        result = studio_manager.recommend_face_swap_model(
            base_image_resolution=request.base_image_resolution,
            face_image_resolution=request.face_image_resolution,
            user_tier=user_tier,
            preferences=request.preferences,
        )
        return FaceSwapModelRecommendationResponse(**result)
    except Exception as e:
        logger.error(f"[Face Swap Recommend] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get recommendation: {e}")


# ====================
# SOCIAL OPTIMIZER ENDPOINTS
# ====================

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

        # Convert platform strings to Platform enum
        from services.image_studio.templates import Platform
        platforms = []
        for platform_str in request.platforms:
            try:
                platforms.append(Platform(platform_str.lower()))
            except ValueError:
                logger.warning(f"[Social Optimizer] Invalid platform: {platform_str}")
                continue

        if not platforms:
            raise HTTPException(status_code=400, detail="No valid platforms provided")

        # Convert format_names dict keys to Platform enum
        format_names = None
        if request.format_names:
            format_names = {}
            for platform_str, format_name in request.format_names.items():
                try:
                    platform = Platform(platform_str.lower())
                    format_names[platform] = format_name
                except ValueError:
                    logger.warning(f"[Social Optimizer] Invalid platform in format_names: {platform_str}")

        social_request = studio_manager._create_social_request(
            image_base64=request.image_base64,
            platforms=platforms,
            format_names=format_names,
            show_safe_zones=request.show_safe_zones,
            crop_mode=request.crop_mode,
            focal_point=request.focal_point,
            output_format=request.output_format,
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
        from services.image_studio.templates import Platform
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


@router.get("/platform-specs/{platform}", summary="Get Platform Specifications")
async def get_platform_specs(
    platform: Platform,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get specifications and requirements for a specific platform.

    Returns:
    - Supported formats and dimensions
    - File type requirements
    - Maximum file size
    - Best practices

    Args:
        platform: Platform name

    Returns:
        Platform specifications
    """
    try:
        specs = studio_manager.get_platform_specs(platform)
        if not specs:
            raise HTTPException(status_code=404, detail=f"Specifications not found for platform: {platform}")

        return specs

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Get Platform Specs] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ====================
# TRANSFORM STUDIO ENDPOINTS
# ====================

@router.post("/transform/image-to-video", response_model=TransformVideoResponse, summary="Transform Image to Video")
async def transform_image_to_video(
    request: TransformImageToVideoRequestModel,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Transform an image into a video using WAN 2.5.

    This endpoint generates a video from an image and text prompt, with optional audio synchronization.
    Supports resolutions of 480p, 720p, and 1080p, with durations of 5 or 10 seconds.

    Returns:
        Video generation result with URL and metadata
    """
    try:
        user_id = _require_user_id(current_user, "image-to-video transformation")
        logger.info(f"[Transform Studio] Image-to-video request from user {user_id}: resolution={request.resolution}, duration={request.duration}s")

        # Convert request to service request
        transform_request = TransformImageToVideoRequest(
            image_base64=request.image_base64,
            prompt=request.prompt,
            audio_base64=request.audio_base64,
            resolution=request.resolution,
            duration=request.duration,
            negative_prompt=request.negative_prompt,
            seed=request.seed,
            enable_prompt_expansion=request.enable_prompt_expansion,
        )

        result = await studio_manager.transform_image_to_video(transform_request, user_id=user_id)
        return TransformVideoResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Transform Studio] ❌ Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image-to-video transformation failed: {e}")


@router.post("/transform/talking-avatar", response_model=TransformVideoResponse, summary="Create Talking Avatar")
async def create_talking_avatar(
    request: TalkingAvatarRequestModel,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Create a talking avatar video from an image and audio.

    This endpoint generates a video where an avatar lip-syncs to provided audio.
    Supports resolutions of 480p and 720p.

    Returns:
        Video generation result with URL and metadata
    """
    try:
        user_id = _require_user_id(current_user, "talking avatar")
        logger.info(f"[Transform Studio] Talking avatar request from user {user_id}: resolution={request.resolution}")

        avatar_request = TalkingAvatarRequest(
            image_base64=request.image_base64,
            audio_base64=request.audio_base64,
            resolution=request.resolution,
            prompt=request.prompt,
            mask_image_base64=request.mask_image_base64,
            seed=request.seed,
        )

        result = await studio_manager.create_talking_avatar(avatar_request, user_id=user_id)
        return TransformVideoResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Talking Avatar] ❌ Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Talking avatar creation failed: {e}")


@router.post("/transform/estimate-cost", response_model=TransformCostEstimateResponse, summary="Estimate Transform Cost")
async def estimate_transform_cost(
    request: TransformCostEstimateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Estimate the cost of video transformation operations."""
    try:
        user_id = _require_user_id(current_user, "cost estimation")
        logger.info(f"[Transform Cost Estimation] Request from user {user_id}: operation={request.operation}")

        cost_estimate = studio_manager.estimate_transform_cost(
            operation=request.operation,
            resolution=request.resolution,
            duration=request.duration,
        )

        return TransformCostEstimateResponse(**cost_estimate)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Transform Cost Estimation] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Cost estimation failed: {e}")


@router.get("/videos/{user_id}/{video_filename:path}", summary="Serve Transform Studio Video")
async def serve_transform_video(
    user_id: str,
    video_filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Serve a generated video file from transform operations.

    This endpoint serves video files generated by image-to-video and talking avatar operations.
    Files are stored securely and access is validated per user.
    """
    try:
        # Verify user access
        current_user_id = current_user.get("sub") or current_user.get("user_id") or current_user.get("id")
        if current_user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied to this video")

        return await studio_manager.serve_transform_video(user_id, video_filename)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Serve Transform Video] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to serve video")