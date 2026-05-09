"""API endpoints for Image Studio operations."""

import base64
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse

from .image_studio.models import (
    CreateImageRequest, CostEstimationRequest,
    EditImageRequest, EditImageResponse, EditOperationsResponse,
    EditModelsResponse, EditModelRecommendationRequest, EditModelRecommendationResponse,
    UpscaleImageRequest, UpscaleImageResponse,
    FaceSwapRequest, FaceSwapResponse, FaceSwapModelsResponse,
    FaceSwapModelRecommendationRequest, FaceSwapModelRecommendationResponse,
    ControlImageRequest, ControlImageResponse, ControlOperationsResponse,
    SocialOptimizeRequest, SocialOptimizeResponse, PlatformFormatsResponse,
    TransformImageToVideoRequestModel, TalkingAvatarRequestModel,
    TransformVideoResponse, TransformCostEstimateRequest, TransformCostEstimateResponse,
    CompressImageRequest, CompressImageResponse, CompressBatchRequest, CompressBatchResponse,
    CompressionEstimateRequest, CompressionEstimateResponse,
    CompressionFormatsResponse, CompressionPresetsResponse,
    ConvertFormatRequest, ConvertFormatResponse, ConvertFormatBatchRequest, ConvertFormatBatchResponse,
    SupportedFormatsResponse, FormatRecommendationsResponse,
)
from .image_studio.deps import get_studio_manager, _require_user_id
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


# ====================
# CREATE STUDIO ENDPOINTS
# ====================

@router.post("/create", summary="Generate Image")
async def create_image(
    request: CreateImageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager)
):
    """Generate image(s) using Create Studio.
    
    This endpoint supports:
    - Multiple AI providers (Stability AI, WaveSpeed, HuggingFace, Gemini)
    - Template-based generation
    - Custom dimensions and aspect ratios
    - Style presets and quality levels
    - Multiple variations
    - Prompt enhancement
    
    Returns:
        Dictionary with generation results including image data
    """
    try:
        user_id = _require_user_id(current_user, "image generation")
        logger.info(f"[Create Image] Request from user {user_id}: {request.prompt[:100]}")
        
        # Convert request to CreateStudioRequest
        studio_request = CreateStudioRequest(
            prompt=request.prompt,
            template_id=request.template_id,
            provider=request.provider,
            model=request.model,
            width=request.width,
            height=request.height,
            aspect_ratio=request.aspect_ratio,
            style_preset=request.style_preset,
            quality=request.quality,
            negative_prompt=request.negative_prompt,
            guidance_scale=request.guidance_scale,
            steps=request.steps,
            seed=request.seed,
            num_variations=request.num_variations,
            enhance_prompt=request.enhance_prompt,
            use_persona=request.use_persona,
            persona_id=request.persona_id,
        )
        
        # Generate images
        result = await studio_manager.create_image(studio_request, user_id=user_id)
        
        # Convert image bytes to base64 for JSON response
        for idx, img_result in enumerate(result["results"]):
            if "image_bytes" in img_result:
                img_result["image_base64"] = base64.b64encode(img_result["image_bytes"]).decode("utf-8")
                # Remove bytes from response
                del img_result["image_bytes"]
        
        logger.info(f"[Create Image] ✅ Success: {result['total_generated']} images generated")
        return result
        
    except ValueError as e:
        logger.error(f"[Create Image] ❌ Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"[Create Image] ❌ Generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")
    except Exception as e:
        logger.error(f"[Create Image] ❌ Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ====================
# TEMPLATE ENDPOINTS
# ====================

@router.get("/templates", summary="Get Templates")
async def get_templates(
    platform: Optional[Platform] = None,
    category: Optional[TemplateCategory] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager)
):
    """Get available image templates.
    
    Templates provide pre-configured settings for common use cases:
    - Platform-specific dimensions and formats
    - Recommended providers and models
    - Style presets and quality settings
    
    Args:
        platform: Filter by platform (instagram, facebook, twitter, etc.)
        category: Filter by category (social_media, blog_content, ad_creative, etc.)
    
    Returns:
        List of templates
    """
    try:
        templates = studio_manager.get_templates(platform=platform, category=category)
        
        # Convert to dict for JSON response
        templates_dict = [
            {
                "id": t.id,
                "name": t.name,
                "category": t.category.value,
                "platform": t.platform.value if t.platform else None,
                "aspect_ratio": {
                    "ratio": t.aspect_ratio.ratio,
                    "width": t.aspect_ratio.width,
                    "height": t.aspect_ratio.height,
                    "label": t.aspect_ratio.label,
                },
                "description": t.description,
                "recommended_provider": t.recommended_provider,
                "style_preset": t.style_preset,
                "quality": t.quality,
                "use_cases": t.use_cases or [],
            }
            for t in templates
        ]
        
        return {"templates": templates_dict, "total": len(templates_dict)}
        
    except Exception as e:
        logger.error(f"[Get Templates] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/search", summary="Search Templates")
async def search_templates(
    query: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager)
):
    """Search templates by query.
    
    Searches in template names, descriptions, and use cases.
    
    Args:
        query: Search query
    
    Returns:
        List of matching templates
    """
    try:
        templates = studio_manager.search_templates(query)
        
        templates_dict = [
            {
                "id": t.id,
                "name": t.name,
                "category": t.category.value,
                "platform": t.platform.value if t.platform else None,
                "aspect_ratio": {
                    "ratio": t.aspect_ratio.ratio,
                    "width": t.aspect_ratio.width,
                    "height": t.aspect_ratio.height,
                    "label": t.aspect_ratio.label,
                },
                "description": t.description,
                "recommended_provider": t.recommended_provider,
                "style_preset": t.style_preset,
                "quality": t.quality,
                "use_cases": t.use_cases or [],
            }
            for t in templates
        ]
        
        return {"templates": templates_dict, "total": len(templates_dict), "query": query}
        
    except Exception as e:
        logger.error(f"[Search Templates] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/recommend", summary="Recommend Templates")
async def recommend_templates(
    use_case: str,
    platform: Optional[Platform] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager)
):
    """Recommend templates based on use case.
    
    Args:
        use_case: Description of use case (e.g., "product showcase", "blog header")
        platform: Optional platform filter
    
    Returns:
        List of recommended templates
    """
    try:
        templates = studio_manager.recommend_templates(use_case, platform=platform)
        
        templates_dict = [
            {
                "id": t.id,
                "name": t.name,
                "category": t.category.value,
                "platform": t.platform.value if t.platform else None,
                "aspect_ratio": {
                    "ratio": t.aspect_ratio.ratio,
                    "width": t.aspect_ratio.width,
                    "height": t.aspect_ratio.height,
                    "label": t.aspect_ratio.label,
                },
                "description": t.description,
                "recommended_provider": t.recommended_provider,
                "style_preset": t.style_preset,
                "quality": t.quality,
                "use_cases": t.use_cases or [],
            }
            for t in templates
        ]
        
        return {"templates": templates_dict, "total": len(templates_dict), "use_case": use_case}
        
    except Exception as e:
        logger.error(f"[Recommend Templates] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ====================
# PROVIDER ENDPOINTS
# ====================

@router.get("/providers", summary="Get Providers")
async def get_providers(
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager)
):
    """Get available AI providers and their capabilities.
    
    Returns information about:
    - Available models
    - Capabilities
    - Maximum resolution
    - Cost estimates
    
    Returns:
        Dictionary of providers
    """
    try:
        providers = studio_manager.get_providers()
        return {"providers": providers}
        
    except Exception as e:
        logger.error(f"[Get Providers] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ====================
# COST ESTIMATION ENDPOINTS
# ====================

@router.post("/estimate-cost", summary="Estimate Cost")
async def estimate_cost(
    request: CostEstimationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager)
):
    """Estimate cost for image generation operations.
    
    Provides cost estimates before generation to help users make informed decisions.
    
    Args:
        request: Cost estimation request
    
    Returns:
        Cost estimation details
    """
    try:
        resolution = None
        if request.width and request.height:
            resolution = (request.width, request.height)
        
        estimate = studio_manager.estimate_cost(
            provider=request.provider,
            model=request.model,
            operation=request.operation,
            num_images=request.num_images,
            resolution=resolution
        )
        
        return estimate
        
    except Exception as e:
        logger.error(f"[Estimate Cost] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))











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




