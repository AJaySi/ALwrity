"""API endpoints for Image Studio operations."""

import base64
from typing import Optional, List, Dict, Any, Literal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from services.image_studio import (
    ImageStudioManager,
    CreateStudioRequest,
    EditStudioRequest,
)
from services.image_studio.upscale_service import UpscaleStudioRequest
from services.image_studio.templates import Platform, TemplateCategory
from middleware.auth_middleware import get_current_user
from utils.logger_utils import get_service_logger


logger = get_service_logger("api.image_studio")
router = APIRouter(prefix="/api/image-studio", tags=["image-studio"])


# ====================
# REQUEST MODELS
# ====================

class CreateImageRequest(BaseModel):
    """Request model for image generation."""
    prompt: str = Field(..., description="Image generation prompt")
    template_id: Optional[str] = Field(None, description="Template ID to use")
    provider: Optional[str] = Field("auto", description="Provider: auto, stability, wavespeed, huggingface, gemini")
    model: Optional[str] = Field(None, description="Specific model to use")
    width: Optional[int] = Field(None, description="Image width in pixels")
    height: Optional[int] = Field(None, description="Image height in pixels")
    aspect_ratio: Optional[str] = Field(None, description="Aspect ratio (e.g., '1:1', '16:9')")
    style_preset: Optional[str] = Field(None, description="Style preset")
    quality: str = Field("standard", description="Quality: draft, standard, premium")
    negative_prompt: Optional[str] = Field(None, description="Negative prompt")
    guidance_scale: Optional[float] = Field(None, description="Guidance scale")
    steps: Optional[int] = Field(None, description="Number of inference steps")
    seed: Optional[int] = Field(None, description="Random seed")
    num_variations: int = Field(1, ge=1, le=10, description="Number of variations (1-10)")
    enhance_prompt: bool = Field(True, description="Enhance prompt with AI")
    use_persona: bool = Field(False, description="Use persona for brand consistency")
    persona_id: Optional[str] = Field(None, description="Persona ID")


class CostEstimationRequest(BaseModel):
    """Request model for cost estimation."""
    provider: str = Field(..., description="Provider name")
    model: Optional[str] = Field(None, description="Model name")
    operation: str = Field("generate", description="Operation type")
    num_images: int = Field(1, ge=1, description="Number of images")
    width: Optional[int] = Field(None, description="Image width")
    height: Optional[int] = Field(None, description="Image height")


class EditImageRequest(BaseModel):
    """Request payload for Edit Studio."""

    image_base64: str = Field(..., description="Primary image payload (base64 or data URL)")
    operation: Literal[
        "remove_background",
        "inpaint",
        "outpaint",
        "search_replace",
        "search_recolor",
        "general_edit",
    ] = Field(..., description="Edit operation to perform")
    prompt: Optional[str] = Field(None, description="Primary prompt/instruction")
    negative_prompt: Optional[str] = Field(None, description="Negative prompt for providers that support it")
    mask_base64: Optional[str] = Field(None, description="Optional mask image in base64")
    search_prompt: Optional[str] = Field(None, description="Search prompt for replace operations")
    select_prompt: Optional[str] = Field(None, description="Select prompt for recolor operations")
    background_image_base64: Optional[str] = Field(None, description="Reference background image")
    lighting_image_base64: Optional[str] = Field(None, description="Reference lighting image")
    expand_left: Optional[int] = Field(0, description="Outpaint expansion in pixels (left)")
    expand_right: Optional[int] = Field(0, description="Outpaint expansion in pixels (right)")
    expand_up: Optional[int] = Field(0, description="Outpaint expansion in pixels (up)")
    expand_down: Optional[int] = Field(0, description="Outpaint expansion in pixels (down)")
    provider: Optional[str] = Field(None, description="Explicit provider override")
    model: Optional[str] = Field(None, description="Explicit model override")
    style_preset: Optional[str] = Field(None, description="Style preset for Stability helpers")
    guidance_scale: Optional[float] = Field(None, description="Guidance scale for general edits")
    steps: Optional[int] = Field(None, description="Inference steps")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    output_format: str = Field("png", description="Output format for edited image")
    options: Optional[Dict[str, Any]] = Field(
        None,
        description="Advanced provider-specific options (e.g., grow_mask)",
    )


class EditImageResponse(BaseModel):
    success: bool
    operation: str
    provider: str
    image_base64: str
    width: int
    height: int
    metadata: Dict[str, Any]


class EditOperationsResponse(BaseModel):
    operations: Dict[str, Dict[str, Any]]


class UpscaleImageRequest(BaseModel):
    image_base64: str
    mode: Literal["fast", "conservative", "creative", "auto"] = "auto"
    target_width: Optional[int] = Field(None, description="Target width in pixels")
    target_height: Optional[int] = Field(None, description="Target height in pixels")
    preset: Optional[str] = Field(None, description="Named preset (web, print, social)")
    prompt: Optional[str] = Field(None, description="Prompt for conservative/creative modes")


class UpscaleImageResponse(BaseModel):
    success: bool
    mode: str
    image_base64: str
    width: int
    height: int
    metadata: Dict[str, Any]


# ====================
# DEPENDENCY
# ====================

def get_studio_manager() -> ImageStudioManager:
    """Get Image Studio Manager instance."""
    return ImageStudioManager()


def _require_user_id(current_user: Dict[str, Any], operation: str) -> str:
    """Ensure user_id is available for protected operations."""
    user_id = current_user.get("sub") or current_user.get("user_id")
    if not user_id:
        logger.error(
            "[Image Studio] ❌ Missing user_id for %s operation - blocking request",
            operation,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user required for image operations.",
        )
    return user_id


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
        }
    }

