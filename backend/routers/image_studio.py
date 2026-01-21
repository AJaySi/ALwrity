"""API endpoints for Image Studio operations."""

import base64
from pathlib import Path
from typing import Optional, List, Dict, Any, Literal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Import models from the new models package
from .models import *
from .utils import _require_user_id
from .dependencies import get_studio_manager

# Import feature routers
from .generation import router as generation_router

from services.image_studio import (
    ImageStudioManager,
    CreateStudioRequest,
    EditStudioRequest,
    ControlStudioRequest,
    SocialOptimizerRequest,
    TransformImageToVideoRequest,
    TalkingAvatarRequest,
)
from services.image_studio.face_swap_service import FaceSwapStudioRequest
from services.image_studio.upscale_service import UpscaleStudioRequest
from services.image_studio.templates import Platform, TemplateCategory
from middleware.auth_middleware import get_current_user, get_current_user_with_query_token
from utils.logger_utils import get_service_logger


logger = get_service_logger("api.image_studio")
router = APIRouter(prefix="/api/image-studio", tags=["image-studio"])

# Include feature routers
router.include_router(generation_router, prefix="", tags=["generation"])




# ====================
# EDIT STUDIO ENDPOINTS
# ====================

@router.post("/edit/process", response_model=EditImageResponse, summary="Process Edit Studio request")
async def process_edit_image(
    request: EditImageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Perform Edit Studio operations such as remove background, inpaint, or recolor."""
    try:
        user_id = _require_user_id(current_user, "image editing")
        logger.info(f"[Edit Image] Request from user {user_id}: operation={request.operation}")

        edit_request = EditStudioRequest(
            image_base64=request.image_base64,
            operation=request.operation,
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            mask_base64=request.mask_base64,
            search_prompt=request.search_prompt,
            select_prompt=request.select_prompt,
            background_image_base64=request.background_image_base64,
            lighting_image_base64=request.lighting_image_base64,
            expand_left=request.expand_left,
            expand_right=request.expand_right,
            expand_up=request.expand_up,
            expand_down=request.expand_down,
            provider=request.provider,
            model=request.model,
            style_preset=request.style_preset,
            guidance_scale=request.guidance_scale,
            steps=request.steps,
            seed=request.seed,
            output_format=request.output_format,
            options=request.options or {},
        )

        result = await studio_manager.edit_image(edit_request, user_id=user_id)
        return EditImageResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Edit Image] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image editing failed: {e}")


@router.get("/edit/operations", response_model=EditOperationsResponse, summary="List Edit Studio operations")
async def get_edit_operations(
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Return metadata for supported Edit Studio operations."""
    try:
        operations = studio_manager.get_edit_operations()
        return EditOperationsResponse(operations=operations)
    except Exception as e:
        logger.error(f"[Edit Operations] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to load edit operations")


@router.get("/edit/models", response_model=EditModelsResponse, summary="List available editing models")
async def get_edit_models(
    operation: Optional[str] = None,
    tier: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get available WaveSpeed editing models with metadata.
    
    Query Parameters:
    - operation: Filter by operation type (e.g., "general_edit")
    - tier: Filter by tier ("budget", "mid", "premium")
    """
    try:
        result = studio_manager.get_edit_models(operation=operation, tier=tier)
        return EditModelsResponse(**result)
    except Exception as e:
        logger.error(f"[Edit Models] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to load editing models")


@router.post("/edit/recommend", response_model=EditModelRecommendationResponse, summary="Get model recommendation")
async def recommend_edit_model(
    request: EditModelRecommendationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get recommended editing model based on operation, image resolution, and user preferences.
    
    Auto-detects best model when user doesn't specify one.
    """
    try:
        # Get user tier from current_user if available
        user_tier = request.user_tier
        if not user_tier and current_user:
            # Try to extract from user data (adjust based on your user model)
            user_tier = current_user.get("tier") or current_user.get("subscription_tier")
        
        result = studio_manager.recommend_edit_model(
            operation=request.operation,
            image_resolution=request.image_resolution,
            user_tier=user_tier,
            preferences=request.preferences,
        )
        return EditModelRecommendationResponse(**result)
    except Exception as e:
        logger.error(f"[Edit Recommend] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get recommendation: {e}")


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
# UPSCALE STUDIO ENDPOINTS
# ====================

@router.post("/upscale", response_model=UpscaleImageResponse, summary="Upscale Image")
async def upscale_image(
    request: UpscaleImageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Upscale an image using Stability AI pipelines."""
    try:
        user_id = _require_user_id(current_user, "image upscaling")
        upscale_request = UpscaleStudioRequest(
            image_base64=request.image_base64,
            mode=request.mode,
            target_width=request.target_width,
            target_height=request.target_height,
            preset=request.preset,
            prompt=request.prompt,
        )
        result = await studio_manager.upscale_image(upscale_request, user_id=user_id)
        return UpscaleImageResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Upscale Image] ❌ Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image upscaling failed: {e}")


# ====================
# CONTROL STUDIO ENDPOINTS
# ====================

@router.post("/control/process", response_model=ControlImageResponse, summary="Process Control Studio request")
async def process_control_image(
    request: ControlImageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Perform Control Studio operations such as sketch-to-image, structure control, style control, and style transfer."""
    try:
        user_id = _require_user_id(current_user, "image control")
        logger.info(f"[Control Image] Request from user {user_id}: operation={request.operation}")

        control_request = ControlStudioRequest(
            operation=request.operation,
            prompt=request.prompt,
            control_image_base64=request.control_image_base64,
            style_image_base64=request.style_image_base64,
            negative_prompt=request.negative_prompt,
            control_strength=request.control_strength,
            fidelity=request.fidelity,
            style_strength=request.style_strength,
            composition_fidelity=request.composition_fidelity,
            change_strength=request.change_strength,
            aspect_ratio=request.aspect_ratio,
            style_preset=request.style_preset,
            seed=request.seed,
            output_format=request.output_format,
        )

        result = await studio_manager.control_image(control_request, user_id=user_id)
        return ControlImageResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Control Image] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image control failed: {e}")


@router.get("/control/operations", response_model=ControlOperationsResponse, summary="List Control Studio operations")
async def get_control_operations(
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Return metadata for supported Control Studio operations."""
    try:
        operations = studio_manager.get_control_operations()
        return ControlOperationsResponse(operations=operations)
    except Exception as e:
        logger.error(f"[Control Operations] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to load control operations")


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


# ====================
# PLATFORM SPECS ENDPOINTS
# ====================

@router.get("/platform-specs/{platform}", summary="Get Platform Specifications")
async def get_platform_specs(
    platform: Platform,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager)
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
        
        # Generate video
        result = await studio_manager.transform_image_to_video(transform_request, user_id=user_id)
        
        logger.info(f"[Transform Studio] ✅ Image-to-video completed: cost=${result['cost']:.2f}")
        return TransformVideoResponse(**result)
        
    except ValueError as e:
        logger.error(f"[Transform Studio] ❌ Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Transform Studio] ❌ Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")


@router.post("/transform/talking-avatar", response_model=TransformVideoResponse, summary="Create Talking Avatar")
async def create_talking_avatar(
    request: TalkingAvatarRequestModel,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Create a talking avatar video using InfiniteTalk.
    
    This endpoint generates a video with precise lip-sync from an image and audio file.
    Supports resolutions of 480p and 720p, with videos up to 10 minutes long.
    
    Returns:
        Video generation result with URL and metadata
    """
    try:
        user_id = _require_user_id(current_user, "talking avatar generation")
        logger.info(f"[Transform Studio] Talking avatar request from user {user_id}: resolution={request.resolution}")
        
        # Convert request to service request
        avatar_request = TalkingAvatarRequest(
            image_base64=request.image_base64,
            audio_base64=request.audio_base64,
            resolution=request.resolution,
            prompt=request.prompt,
            mask_image_base64=request.mask_image_base64,
            seed=request.seed,
        )
        
        # Generate video
        result = await studio_manager.create_talking_avatar(avatar_request, user_id=user_id)
        
        logger.info(f"[Transform Studio] ✅ Talking avatar completed: cost=${result['cost']:.2f}")
        return TransformVideoResponse(**result)
        
    except ValueError as e:
        logger.error(f"[Transform Studio] ❌ Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Transform Studio] ❌ Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Talking avatar generation failed: {str(e)}")


@router.post("/transform/estimate-cost", response_model=TransformCostEstimateResponse, summary="Estimate Transform Cost")
async def estimate_transform_cost(
    request: TransformCostEstimateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Estimate cost for transform operations.
    
    Provides cost estimates before generation to help users make informed decisions.
    
    Returns:
        Cost estimation details
    """
    try:
        estimate = studio_manager.estimate_transform_cost(
            operation=request.operation,
            resolution=request.resolution,
            duration=request.duration,
        )
        return TransformCostEstimateResponse(**estimate)
        
    except ValueError as e:
        logger.error(f"[Transform Studio] ❌ Cost estimation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[Transform Studio] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/videos/{user_id}/{video_filename:path}", summary="Serve Transform Studio Video")
async def serve_transform_video(
    user_id: str,
    video_filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user_with_query_token),
):
    """Serve a generated Transform Studio video file.
    
    Args:
        user_id: User ID from URL path
        video_filename: Video filename
        current_user: Authenticated user
        
    Returns:
        Video file response
    """
    try:
        # Verify user has access (must be the owner)
        authenticated_user_id = _require_user_id(current_user, "video access")
        if authenticated_user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: You can only access your own videos"
            )
        
        # Resolve video path
        # __file__ is: backend/routers/image_studio.py
        # We need: backend/transform_videos
        base_dir = Path(__file__).parent.parent.parent
        transform_videos_dir = base_dir / "transform_videos"
        video_path = transform_videos_dir / user_id / video_filename
        
        # Security: Ensure path is within transform_videos directory
        # Prevent directory traversal attacks
        try:
            resolved_video_path = video_path.resolve()
            resolved_base = transform_videos_dir.resolve()
            # Check if video path is within base directory
            resolved_video_path.relative_to(resolved_base)
        except ValueError:
            raise HTTPException(
                status_code=403,
                detail="Invalid video path: path traversal detected"
            )
        
        if not video_path.exists():
            raise HTTPException(status_code=404, detail="Video not found")
        
        return FileResponse(
            path=str(video_path),
            media_type="video/mp4",
            filename=video_filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Transform Studio] Failed to serve video: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ====================
# COMPRESSION STUDIO ENDPOINTS
# ====================

@router.post("/compress", response_model=CompressImageResponse, summary="Compress an image")
async def compress_image(
    request: CompressImageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Compress an image with specified quality and format settings.
    
    Features:
    - Quality control (1-100)
    - Format conversion (JPEG, PNG, WebP)
    - Target size compression
    - Metadata stripping
    - Progressive JPEG support
    """
    try:
        user_id = _require_user_id(current_user, "image compression")
        logger.info(f"[Compression] Request from user {user_id}: format={request.format}, quality={request.quality}")
        
        from services.image_studio.compression_service import CompressionRequest as ServiceRequest
        
        compression_request = ServiceRequest(
            image_base64=request.image_base64,
            quality=request.quality,
            format=request.format,
            target_size_kb=request.target_size_kb,
            strip_metadata=request.strip_metadata,
            progressive=request.progressive,
            optimize=request.optimize,
        )
        
        result = await studio_manager.compress_image(compression_request, user_id=user_id)
        
        return CompressImageResponse(
            success=result.success,
            image_base64=result.image_base64,
            original_size_kb=result.original_size_kb,
            compressed_size_kb=result.compressed_size_kb,
            compression_ratio=result.compression_ratio,
            format=result.format,
            width=result.width,
            height=result.height,
            quality_used=result.quality_used,
            metadata_stripped=result.metadata_stripped,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Compression] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image compression failed: {e}")


@router.post("/compress/batch", response_model=CompressBatchResponse, summary="Compress multiple images")
async def compress_batch(
    request: CompressBatchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Compress multiple images with the same or individual settings."""
    try:
        user_id = _require_user_id(current_user, "batch compression")
        logger.info(f"[Compression] Batch request from user {user_id}: {len(request.images)} images")
        
        from services.image_studio.compression_service import CompressionRequest as ServiceRequest
        
        compression_requests = [
            ServiceRequest(
                image_base64=img.image_base64,
                quality=img.quality,
                format=img.format,
                target_size_kb=img.target_size_kb,
                strip_metadata=img.strip_metadata,
                progressive=img.progressive,
                optimize=img.optimize,
            )
            for img in request.images
        ]
        
        results = await studio_manager.compress_batch(compression_requests, user_id=user_id)
        
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        return CompressBatchResponse(
            success=failed == 0,
            results=[
                CompressImageResponse(
                    success=r.success,
                    image_base64=r.image_base64,
                    original_size_kb=r.original_size_kb,
                    compressed_size_kb=r.compressed_size_kb,
                    compression_ratio=r.compression_ratio,
                    format=r.format,
                    width=r.width,
                    height=r.height,
                    quality_used=r.quality_used,
                    metadata_stripped=r.metadata_stripped,
                )
                for r in results
            ],
            total_images=len(results),
            successful=successful,
            failed=failed,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Compression] ❌ Batch error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch compression failed: {e}")


@router.post("/compress/estimate", response_model=CompressionEstimateResponse, summary="Estimate compression results")
async def estimate_compression(
    request: CompressionEstimateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Estimate compression results without actually compressing the image."""
    try:
        result = await studio_manager.estimate_compression(
            request.image_base64,
            request.format,
            request.quality,
        )
        return CompressionEstimateResponse(**result)
    except Exception as e:
        logger.error(f"[Compression] ❌ Estimate error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Compression estimation failed: {e}")


@router.get("/compress/formats", response_model=CompressionFormatsResponse, summary="Get supported compression formats")
async def get_compression_formats(
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get list of supported compression formats with their capabilities."""
    formats = studio_manager.get_compression_formats()
    return CompressionFormatsResponse(formats=formats)


@router.get("/compress/presets", response_model=CompressionPresetsResponse, summary="Get compression presets")
async def get_compression_presets(
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get predefined compression presets for common use cases."""
    presets = studio_manager.get_compression_presets()
    return CompressionPresetsResponse(presets=presets)


# ====================
# FORMAT CONVERTER ENDPOINTS
# ====================

@router.post("/convert-format", response_model=ConvertFormatResponse, summary="Convert image format")
async def convert_format(
    request: ConvertFormatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Convert an image to a different format.
    
    Features:
    - Multi-format support (PNG, JPEG, WebP, GIF, BMP, TIFF)
    - Transparency preservation
    - Color space conversion
    - Metadata handling
    """
    try:
        user_id = _require_user_id(current_user, "format conversion")
        logger.info(f"[Format Converter] Request from user {user_id}: {request.target_format}")
        
        from services.image_studio.format_converter_service import FormatConversionRequest as ServiceRequest
        
        conversion_request = ServiceRequest(
            image_base64=request.image_base64,
            target_format=request.target_format,
            preserve_transparency=request.preserve_transparency,
            quality=request.quality,
            color_space=request.color_space,
            strip_metadata=request.strip_metadata,
            optimize=request.optimize,
            progressive=request.progressive,
        )
        
        result = await studio_manager.convert_format(conversion_request, user_id=user_id)
        
        return ConvertFormatResponse(
            success=result.success,
            image_base64=result.image_base64,
            original_format=result.original_format,
            target_format=result.target_format,
            original_size_kb=result.original_size_kb,
            converted_size_kb=result.converted_size_kb,
            width=result.width,
            height=result.height,
            transparency_preserved=result.transparency_preserved,
            metadata_preserved=result.metadata_preserved,
            color_space=result.color_space,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Format Converter] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Format conversion failed: {e}")


@router.post("/convert-format/batch", response_model=ConvertFormatBatchResponse, summary="Convert multiple images")
async def convert_format_batch(
    request: ConvertFormatBatchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Convert multiple images to different formats."""
    try:
        user_id = _require_user_id(current_user, "batch format conversion")
        logger.info(f"[Format Converter] Batch request from user {user_id}: {len(request.images)} images")
        
        from services.image_studio.format_converter_service import FormatConversionRequest as ServiceRequest
        
        conversion_requests = [
            ServiceRequest(
                image_base64=img.image_base64,
                target_format=img.target_format,
                preserve_transparency=img.preserve_transparency,
                quality=img.quality,
                color_space=img.color_space,
                strip_metadata=img.strip_metadata,
                optimize=img.optimize,
                progressive=img.progressive,
            )
            for img in request.images
        ]
        
        results = await studio_manager.convert_format_batch(conversion_requests, user_id=user_id)
        
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        return ConvertFormatBatchResponse(
            success=failed == 0,
            results=[
                ConvertFormatResponse(
                    success=r.success,
                    image_base64=r.image_base64,
                    original_format=r.original_format,
                    target_format=r.target_format,
                    original_size_kb=r.original_size_kb,
                    converted_size_kb=r.converted_size_kb,
                    width=r.width,
                    height=r.height,
                    transparency_preserved=r.transparency_preserved,
                    metadata_preserved=r.metadata_preserved,
                    color_space=r.color_space,
                )
                for r in results
            ],
            total_images=len(results),
            successful=successful,
            failed=failed,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Format Converter] ❌ Batch error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch format conversion failed: {e}")


@router.get("/convert-format/supported", response_model=SupportedFormatsResponse, summary="Get supported formats")
async def get_supported_formats(
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get list of supported conversion formats with their capabilities."""
    formats = studio_manager.get_supported_formats()
    return SupportedFormatsResponse(formats=formats)


@router.get("/convert-format/recommendations", response_model=FormatRecommendationsResponse, summary="Get format recommendations")
async def get_format_recommendations(
    source_format: str = Query(..., description="Source format"),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get format recommendations based on source format."""
    recommendations = studio_manager.get_format_recommendations(source_format)
    return FormatRecommendationsResponse(recommendations=recommendations)


# ====================
# HEALTH CHECK
# ====================

@router.get("/health", summary="Health Check")
async def health_check():
    """Health check endpoint for Image Studio.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "image_studio",
        "version": "1.0.0",
        "modules": {
            "create_studio": "available",
            "templates": "available",
            "providers": "available",
            "compression": "available",
        }
    }

