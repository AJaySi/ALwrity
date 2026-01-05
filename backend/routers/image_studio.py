"""API endpoints for Image Studio operations."""

import base64
from pathlib import Path
from typing import Optional, List, Dict, Any, Literal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

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


class EditModelsResponse(BaseModel):
    """Response model for available editing models."""
    models: List[Dict[str, Any]]
    total: int


class EditModelRecommendationRequest(BaseModel):
    """Request model for model recommendations."""
    operation: str
    image_resolution: Optional[Dict[str, int]] = None
    user_tier: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class EditModelRecommendationResponse(BaseModel):
    """Response model for model recommendations."""
    recommended_model: str
    reason: str
    alternatives: List[Dict[str, Any]]


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
    user_id = (
        current_user.get("sub")
        or current_user.get("user_id")
        or current_user.get("id")
        or current_user.get("clerk_user_id")
    )
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

class FaceSwapRequest(BaseModel):
    base_image_base64: str
    face_image_base64: str
    model: Optional[str] = None
    target_face_index: Optional[int] = None
    target_gender: Optional[str] = None
    options: Optional[Dict[str, Any]] = None


class FaceSwapResponse(BaseModel):
    success: bool
    image_base64: str
    width: int
    height: int
    provider: str
    model: str
    metadata: Dict[str, Any]


class FaceSwapModelsResponse(BaseModel):
    """Response model for available face swap models."""
    models: List[Dict[str, Any]]
    total: int


class FaceSwapModelRecommendationRequest(BaseModel):
    """Request model for face swap model recommendations."""
    base_image_resolution: Optional[Dict[str, int]] = None
    face_image_resolution: Optional[Dict[str, int]] = None
    user_tier: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class FaceSwapModelRecommendationResponse(BaseModel):
    """Response model for face swap model recommendations."""
    recommended_model: str
    reason: str
    alternatives: List[Dict[str, Any]]


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

class ControlImageRequest(BaseModel):
    """Request payload for Control Studio."""

    control_image_base64: str = Field(..., description="Control image (sketch/structure/style) in base64")
    operation: Literal["sketch", "structure", "style", "style_transfer"] = Field(..., description="Control operation")
    prompt: str = Field(..., description="Text prompt for generation")
    style_image_base64: Optional[str] = Field(None, description="Style reference image (for style_transfer only)")
    negative_prompt: Optional[str] = Field(None, description="Negative prompt")
    control_strength: Optional[float] = Field(None, ge=0.0, le=1.0, description="Control strength (sketch/structure)")
    fidelity: Optional[float] = Field(None, ge=0.0, le=1.0, description="Style fidelity (style operation)")
    style_strength: Optional[float] = Field(None, ge=0.0, le=1.0, description="Style strength (style_transfer)")
    composition_fidelity: Optional[float] = Field(None, ge=0.0, le=1.0, description="Composition fidelity (style_transfer)")
    change_strength: Optional[float] = Field(None, ge=0.0, le=1.0, description="Change strength (style_transfer)")
    aspect_ratio: Optional[str] = Field(None, description="Aspect ratio (style operation)")
    style_preset: Optional[str] = Field(None, description="Style preset")
    seed: Optional[int] = Field(None, description="Random seed")
    output_format: str = Field("png", description="Output format")


class ControlImageResponse(BaseModel):
    success: bool
    operation: str
    provider: str
    image_base64: str
    width: int
    height: int
    metadata: Dict[str, Any]


class ControlOperationsResponse(BaseModel):
    operations: Dict[str, Dict[str, Any]]


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

class SocialOptimizeRequest(BaseModel):
    """Request payload for Social Optimizer."""
    image_base64: str = Field(..., description="Source image in base64 or data URL")
    platforms: List[str] = Field(..., description="List of platforms to optimize for")
    format_names: Optional[Dict[str, str]] = Field(None, description="Specific format per platform")
    show_safe_zones: bool = Field(False, description="Include safe zone overlay in output")
    crop_mode: str = Field("smart", description="Crop mode: smart, center, or fit")
    focal_point: Optional[Dict[str, float]] = Field(None, description="Focal point for smart crop (x, y as 0-1)")
    output_format: str = Field("png", description="Output format (png or jpg)")


class SocialOptimizeResponse(BaseModel):
    success: bool
    results: List[Dict[str, Any]]
    total_optimized: int


class PlatformFormatsResponse(BaseModel):
    formats: List[Dict[str, Any]]


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

class TransformImageToVideoRequestModel(BaseModel):
    """Request model for image-to-video transformation."""
    image_base64: str = Field(..., description="Image in base64 or data URL format")
    prompt: str = Field(..., description="Text prompt describing the video")
    audio_base64: Optional[str] = Field(None, description="Optional audio file (wav/mp3, 3-30s, ≤15MB)")
    resolution: Literal["480p", "720p", "1080p"] = Field("720p", description="Output resolution")
    duration: Literal[5, 10] = Field(5, description="Video duration in seconds")
    negative_prompt: Optional[str] = Field(None, description="Negative prompt")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    enable_prompt_expansion: bool = Field(True, description="Enable prompt optimizer")


class TalkingAvatarRequestModel(BaseModel):
    """Request model for talking avatar generation."""
    image_base64: str = Field(..., description="Person image in base64 or data URL")
    audio_base64: str = Field(..., description="Audio file in base64 or data URL (wav/mp3, max 10 minutes)")
    resolution: Literal["480p", "720p"] = Field("720p", description="Output resolution")
    prompt: Optional[str] = Field(None, description="Optional prompt for expression/style")
    mask_image_base64: Optional[str] = Field(None, description="Optional mask for animatable regions")
    seed: Optional[int] = Field(None, description="Random seed")


class TransformVideoResponse(BaseModel):
    """Response model for video generation."""
    success: bool
    video_url: Optional[str] = None
    video_base64: Optional[str] = None
    duration: float
    resolution: str
    width: int
    height: int
    file_size: int
    cost: float
    provider: str
    model: str
    metadata: Dict[str, Any]


class TransformCostEstimateRequest(BaseModel):
    """Request model for cost estimation."""
    operation: Literal["image-to-video", "talking-avatar"] = Field(..., description="Operation type")
    resolution: str = Field(..., description="Output resolution")
    duration: Optional[int] = Field(None, description="Video duration in seconds (for image-to-video)")


class TransformCostEstimateResponse(BaseModel):
    """Response model for cost estimation."""
    estimated_cost: float
    breakdown: Dict[str, Any]
    currency: str
    provider: str
    model: str


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

class CompressImageRequest(BaseModel):
    """Request payload for image compression."""
    image_base64: str = Field(..., description="Image in base64 or data URL format")
    quality: int = Field(85, ge=1, le=100, description="Compression quality (1-100)")
    format: str = Field("jpeg", description="Output format: jpeg, png, webp")
    target_size_kb: Optional[int] = Field(None, ge=10, description="Target file size in KB")
    strip_metadata: bool = Field(True, description="Remove EXIF metadata")
    progressive: bool = Field(True, description="Progressive JPEG encoding")
    optimize: bool = Field(True, description="Optimize encoding")


class CompressImageResponse(BaseModel):
    success: bool
    image_base64: str
    original_size_kb: float
    compressed_size_kb: float
    compression_ratio: float
    format: str
    width: int
    height: int
    quality_used: int
    metadata_stripped: bool


class CompressBatchRequest(BaseModel):
    """Request payload for batch compression."""
    images: List[CompressImageRequest] = Field(..., description="List of images to compress")


class CompressBatchResponse(BaseModel):
    success: bool
    results: List[CompressImageResponse]
    total_images: int
    successful: int
    failed: int


class CompressionEstimateRequest(BaseModel):
    """Request for compression estimation."""
    image_base64: str = Field(..., description="Image in base64 or data URL format")
    format: str = Field("jpeg", description="Output format")
    quality: int = Field(85, ge=1, le=100, description="Quality level")


class CompressionEstimateResponse(BaseModel):
    original_size_kb: float
    estimated_size_kb: float
    estimated_reduction_percent: float
    width: int
    height: int
    format: str


class CompressionFormatsResponse(BaseModel):
    formats: List[Dict[str, Any]]


class CompressionPresetsResponse(BaseModel):
    presets: List[Dict[str, Any]]


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

class ConvertFormatRequest(BaseModel):
    """Request payload for format conversion."""
    image_base64: str = Field(..., description="Image in base64 or data URL format")
    target_format: str = Field(..., description="Target format: png, jpeg, jpg, webp, gif, bmp, tiff")
    preserve_transparency: bool = Field(True, description="Preserve transparency when possible")
    quality: Optional[int] = Field(None, ge=1, le=100, description="Quality for lossy formats (1-100)")
    color_space: Optional[str] = Field(None, description="Color space: sRGB, Adobe RGB")
    strip_metadata: bool = Field(False, description="Remove EXIF metadata")
    optimize: bool = Field(True, description="Optimize encoding")
    progressive: bool = Field(True, description="Progressive JPEG encoding")


class ConvertFormatResponse(BaseModel):
    success: bool
    image_base64: str
    original_format: str
    target_format: str
    original_size_kb: float
    converted_size_kb: float
    width: int
    height: int
    transparency_preserved: bool
    metadata_preserved: bool
    color_space: Optional[str] = None


class ConvertFormatBatchRequest(BaseModel):
    """Request payload for batch format conversion."""
    images: List[ConvertFormatRequest] = Field(..., description="List of images to convert")


class ConvertFormatBatchResponse(BaseModel):
    success: bool
    results: List[ConvertFormatResponse]
    total_images: int
    successful: int
    failed: int


class SupportedFormatsResponse(BaseModel):
    formats: List[Dict[str, Any]]


class FormatRecommendationsResponse(BaseModel):
    recommendations: List[Dict[str, Any]]


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

