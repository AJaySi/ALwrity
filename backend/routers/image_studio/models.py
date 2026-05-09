"""Pydantic request/response models for Image Studio API."""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


# ==================== Create Studio ====================

class CreateImageRequest(BaseModel):
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
    provider: str = Field(..., description="Provider name")
    model: Optional[str] = Field(None, description="Model name")
    operation: str = Field("generate", description="Operation type")
    num_images: int = Field(1, ge=1, description="Number of images")
    width: Optional[int] = Field(None, description="Image width")
    height: Optional[int] = Field(None, description="Image height")


# ==================== Edit Studio ====================

class EditImageRequest(BaseModel):
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
    options: Optional[Dict[str, Any]] = Field(None, description="Advanced provider-specific options (e.g., grow_mask)")


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


class EditModelsResponse(BaseModel):
    models: List[Dict[str, Any]]
    total: int


class EditModelRecommendationRequest(BaseModel):
    operation: str
    image_resolution: Optional[Dict[str, int]] = None
    user_tier: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class EditModelRecommendationResponse(BaseModel):
    recommended_model: str
    reason: str
    alternatives: List[Dict[str, Any]]


# ==================== Face Swap Studio ====================

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
    models: List[Dict[str, Any]]
    total: int


class FaceSwapModelRecommendationRequest(BaseModel):
    base_image_resolution: Optional[Dict[str, int]] = None
    face_image_resolution: Optional[Dict[str, int]] = None
    user_tier: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class FaceSwapModelRecommendationResponse(BaseModel):
    recommended_model: str
    reason: str
    alternatives: List[Dict[str, Any]]


# ==================== Upscale Studio ====================

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


# ==================== Control Studio ====================

class ControlImageRequest(BaseModel):
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


# ==================== Social Optimizer ====================

class SocialOptimizeRequest(BaseModel):
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


# ==================== Transform Studio ====================

class TransformImageToVideoRequestModel(BaseModel):
    image_base64: str = Field(..., description="Image in base64 or data URL format")
    prompt: str = Field(..., description="Text prompt describing the video")
    audio_base64: Optional[str] = Field(None, description="Optional audio file (wav/mp3, 3-30s, ≤15MB)")
    resolution: Literal["480p", "720p", "1080p"] = Field("720p", description="Output resolution")
    duration: Literal[5, 10] = Field(5, description="Video duration in seconds")
    negative_prompt: Optional[str] = Field(None, description="Negative prompt")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    enable_prompt_expansion: bool = Field(True, description="Enable prompt optimizer")


class TalkingAvatarRequestModel(BaseModel):
    image_base64: str = Field(..., description="Person image in base64 or data URL")
    audio_base64: str = Field(..., description="Audio file in base64 or data URL (wav/mp3, max 10 minutes)")
    resolution: Literal["480p", "720p"] = Field("720p", description="Output resolution")
    prompt: Optional[str] = Field(None, description="Optional prompt for expression/style")
    mask_image_base64: Optional[str] = Field(None, description="Optional mask for animatable regions")
    seed: Optional[int] = Field(None, description="Random seed")


class TransformVideoResponse(BaseModel):
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
    operation: Literal["image-to-video", "talking-avatar"] = Field(..., description="Operation type")
    resolution: str = Field(..., description="Output resolution")
    duration: Optional[int] = Field(None, description="Video duration in seconds (for image-to-video)")


class TransformCostEstimateResponse(BaseModel):
    estimated_cost: float
    breakdown: Dict[str, Any]
    currency: str
    provider: str
    model: str


# ==================== Compression ====================

class CompressImageRequest(BaseModel):
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
    images: List[CompressImageRequest] = Field(..., description="List of images to compress")


class CompressBatchResponse(BaseModel):
    success: bool
    results: List[CompressImageResponse]
    total_images: int
    successful: int
    failed: int


class CompressionEstimateRequest(BaseModel):
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


# ==================== Format Converter ====================

class ConvertFormatRequest(BaseModel):
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
