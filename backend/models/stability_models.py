"""Pydantic models for Stability AI API requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, List, Union, Literal, Tuple
from enum import Enum


# ==================== ENUMS ====================

class OutputFormat(str, Enum):
    """Supported output formats for images."""
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"


class AudioOutputFormat(str, Enum):
    """Supported output formats for audio."""
    MP3 = "mp3"
    WAV = "wav"


class AspectRatio(str, Enum):
    """Supported aspect ratios."""
    RATIO_21_9 = "21:9"
    RATIO_16_9 = "16:9"
    RATIO_3_2 = "3:2"
    RATIO_5_4 = "5:4"
    RATIO_1_1 = "1:1"
    RATIO_4_5 = "4:5"
    RATIO_2_3 = "2:3"
    RATIO_9_16 = "9:16"
    RATIO_9_21 = "9:21"


class StylePreset(str, Enum):
    """Supported style presets."""
    ENHANCE = "enhance"
    ANIME = "anime"
    PHOTOGRAPHIC = "photographic"
    DIGITAL_ART = "digital-art"
    COMIC_BOOK = "comic-book"
    FANTASY_ART = "fantasy-art"
    LINE_ART = "line-art"
    ANALOG_FILM = "analog-film"
    NEON_PUNK = "neon-punk"
    ISOMETRIC = "isometric"
    LOW_POLY = "low-poly"
    ORIGAMI = "origami"
    MODELING_COMPOUND = "modeling-compound"
    CINEMATIC = "cinematic"
    THREE_D_MODEL = "3d-model"
    PIXEL_ART = "pixel-art"
    TILE_TEXTURE = "tile-texture"


class FinishReason(str, Enum):
    """Generation finish reasons."""
    SUCCESS = "SUCCESS"
    CONTENT_FILTERED = "CONTENT_FILTERED"


class GenerationMode(str, Enum):
    """Generation modes for SD3."""
    TEXT_TO_IMAGE = "text-to-image"
    IMAGE_TO_IMAGE = "image-to-image"


class SD3Model(str, Enum):
    """SD3 model variants."""
    SD3_5_LARGE = "sd3.5-large"
    SD3_5_LARGE_TURBO = "sd3.5-large-turbo"
    SD3_5_MEDIUM = "sd3.5-medium"


class AudioModel(str, Enum):
    """Audio model variants."""
    STABLE_AUDIO_2_5 = "stable-audio-2.5"
    STABLE_AUDIO_2 = "stable-audio-2"


class TextureResolution(str, Enum):
    """Texture resolution for 3D models."""
    RES_512 = "512"
    RES_1024 = "1024"
    RES_2048 = "2048"


class RemeshType(str, Enum):
    """Remesh types for 3D models."""
    NONE = "none"
    TRIANGLE = "triangle"
    QUAD = "quad"


class TargetType(str, Enum):
    """Target types for 3D mesh simplification."""
    NONE = "none"
    VERTEX = "vertex"
    FACE = "face"


class LightSourceDirection(str, Enum):
    """Light source directions."""
    LEFT = "left"
    RIGHT = "right"
    ABOVE = "above"
    BELOW = "below"


class InpaintMode(str, Enum):
    """Inpainting modes."""
    SEARCH = "search"
    MASK = "mask"


# ==================== BASE MODELS ====================

class BaseStabilityRequest(BaseModel):
    """Base request model with common fields."""
    seed: Optional[int] = Field(default=0, ge=0, le=4294967294, description="Random seed for generation")
    output_format: Optional[OutputFormat] = Field(default=OutputFormat.PNG, description="Output image format")


class BaseImageRequest(BaseStabilityRequest):
    """Base request for image operations."""
    negative_prompt: Optional[str] = Field(default=None, max_length=10000, description="What you do not want to see")


# ==================== GENERATE MODELS ====================

class StableImageUltraRequest(BaseImageRequest):
    """Request model for Stable Image Ultra generation."""
    prompt: str = Field(..., min_length=1, max_length=10000, description="Text prompt for image generation")
    aspect_ratio: Optional[AspectRatio] = Field(default=AspectRatio.RATIO_1_1, description="Aspect ratio")
    style_preset: Optional[StylePreset] = Field(default=None, description="Style preset")
    strength: Optional[float] = Field(default=None, ge=0, le=1, description="Image influence strength (required if image provided)")


class StableImageCoreRequest(BaseImageRequest):
    """Request model for Stable Image Core generation."""
    prompt: str = Field(..., min_length=1, max_length=10000, description="Text prompt for image generation")
    aspect_ratio: Optional[AspectRatio] = Field(default=AspectRatio.RATIO_1_1, description="Aspect ratio")
    style_preset: Optional[StylePreset] = Field(default=None, description="Style preset")


class StableSD3Request(BaseImageRequest):
    """Request model for Stable Diffusion 3.5 generation."""
    prompt: str = Field(..., min_length=1, max_length=10000, description="Text prompt for image generation")
    mode: Optional[GenerationMode] = Field(default=GenerationMode.TEXT_TO_IMAGE, description="Generation mode")
    aspect_ratio: Optional[AspectRatio] = Field(default=AspectRatio.RATIO_1_1, description="Aspect ratio (text-to-image only)")
    model: Optional[SD3Model] = Field(default=SD3Model.SD3_5_LARGE, description="SD3 model variant")
    strength: Optional[float] = Field(default=None, ge=0, le=1, description="Image influence strength (image-to-image only)")
    style_preset: Optional[StylePreset] = Field(default=None, description="Style preset")
    cfg_scale: Optional[float] = Field(default=None, ge=1, le=10, description="CFG scale")


# ==================== EDIT MODELS ====================

class EraseRequest(BaseStabilityRequest):
    """Request model for image erasing."""
    grow_mask: Optional[float] = Field(default=5, ge=0, le=20, description="Mask edge growth in pixels")


class InpaintRequest(BaseImageRequest):
    """Request model for image inpainting."""
    prompt: str = Field(..., min_length=1, max_length=10000, description="Text prompt for inpainting")
    grow_mask: Optional[float] = Field(default=5, ge=0, le=100, description="Mask edge growth in pixels")
    style_preset: Optional[StylePreset] = Field(default=None, description="Style preset")


class OutpaintRequest(BaseStabilityRequest):
    """Request model for image outpainting."""
    left: Optional[int] = Field(default=0, ge=0, le=2000, description="Pixels to outpaint left")
    right: Optional[int] = Field(default=0, ge=0, le=2000, description="Pixels to outpaint right")
    up: Optional[int] = Field(default=0, ge=0, le=2000, description="Pixels to outpaint up")
    down: Optional[int] = Field(default=0, ge=0, le=2000, description="Pixels to outpaint down")
    creativity: Optional[float] = Field(default=0.5, ge=0, le=1, description="Creativity level")
    prompt: Optional[str] = Field(default="", max_length=10000, description="Text prompt for outpainting")
    style_preset: Optional[StylePreset] = Field(default=None, description="Style preset")


class SearchAndReplaceRequest(BaseImageRequest):
    """Request model for search and replace."""
    prompt: str = Field(..., min_length=1, max_length=10000, description="Text prompt for replacement")
    search_prompt: str = Field(..., max_length=10000, description="What to search for")
    grow_mask: Optional[float] = Field(default=3, ge=0, le=20, description="Mask edge growth in pixels")
    style_preset: Optional[StylePreset] = Field(default=None, description="Style preset")


class SearchAndRecolorRequest(BaseImageRequest):
    """Request model for search and recolor."""
    prompt: str = Field(..., min_length=1, max_length=10000, description="Text prompt for recoloring")
    select_prompt: str = Field(..., max_length=10000, description="What to select for recoloring")
    grow_mask: Optional[float] = Field(default=3, ge=0, le=20, description="Mask edge growth in pixels")
    style_preset: Optional[StylePreset] = Field(default=None, description="Style preset")


class RemoveBackgroundRequest(BaseStabilityRequest):
    """Request model for background removal."""
    pass  # Only requires image and output_format


class ReplaceBackgroundAndRelightRequest(BaseImageRequest):
    """Request model for background replacement and relighting."""
    subject_image: bytes = Field(..., description="Subject image binary data")
    background_prompt: Optional[str] = Field(default=None, max_length=10000, description="Background description")
    foreground_prompt: Optional[str] = Field(default=None, max_length=10000, description="Subject description")
    preserve_original_subject: Optional[float] = Field(default=0.6, ge=0, le=1, description="Subject preservation")
    original_background_depth: Optional[float] = Field(default=0.5, ge=0, le=1, description="Background depth matching")
    keep_original_background: Optional[bool] = Field(default=False, description="Keep original background")
    light_source_direction: Optional[LightSourceDirection] = Field(default=None, description="Light direction")
    light_source_strength: Optional[float] = Field(default=0.3, ge=0, le=1, description="Light strength")


# ==================== UPSCALE MODELS ====================

class FastUpscaleRequest(BaseStabilityRequest):
    """Request model for fast upscaling."""
    pass  # Only requires image and output_format


class ConservativeUpscaleRequest(BaseImageRequest):
    """Request model for conservative upscaling."""
    prompt: str = Field(..., min_length=1, max_length=10000, description="Text prompt for upscaling")
    creativity: Optional[float] = Field(default=0.35, ge=0.2, le=0.5, description="Creativity level")


class CreativeUpscaleRequest(BaseImageRequest):
    """Request model for creative upscaling."""
    prompt: str = Field(..., min_length=1, max_length=10000, description="Text prompt for upscaling")
    creativity: Optional[float] = Field(default=0.3, ge=0.1, le=0.5, description="Creativity level")
    style_preset: Optional[StylePreset] = Field(default=None, description="Style preset")


# ==================== CONTROL MODELS ====================

class SketchControlRequest(BaseImageRequest):
    """Request model for sketch control."""
    prompt: str = Field(..., min_length=1, max_length=10000, description="Text prompt for generation")
    control_strength: Optional[float] = Field(default=0.7, ge=0, le=1, description="Control strength")
    style_preset: Optional[StylePreset] = Field(default=None, description="Style preset")


class StructureControlRequest(BaseImageRequest):
    """Request model for structure control."""
    prompt: str = Field(..., min_length=1, max_length=10000, description="Text prompt for generation")
    control_strength: Optional[float] = Field(default=0.7, ge=0, le=1, description="Control strength")
    style_preset: Optional[StylePreset] = Field(default=None, description="Style preset")


class StyleControlRequest(BaseImageRequest):
    """Request model for style control."""
    prompt: str = Field(..., min_length=1, max_length=10000, description="Text prompt for generation")
    aspect_ratio: Optional[AspectRatio] = Field(default=AspectRatio.RATIO_1_1, description="Aspect ratio")
    fidelity: Optional[float] = Field(default=0.5, ge=0, le=1, description="Style fidelity")
    style_preset: Optional[StylePreset] = Field(default=None, description="Style preset")


class StyleTransferRequest(BaseImageRequest):
    """Request model for style transfer."""
    prompt: Optional[str] = Field(default="", max_length=10000, description="Text prompt for generation")
    style_strength: Optional[float] = Field(default=1, ge=0, le=1, description="Style strength")
    composition_fidelity: Optional[float] = Field(default=0.9, ge=0, le=1, description="Composition fidelity")
    change_strength: Optional[float] = Field(default=0.9, ge=0.1, le=1, description="Change strength")


# ==================== 3D MODELS ====================

class StableFast3DRequest(BaseStabilityRequest):
    """Request model for Stable Fast 3D."""
    texture_resolution: Optional[TextureResolution] = Field(default=TextureResolution.RES_1024, description="Texture resolution")
    foreground_ratio: Optional[float] = Field(default=0.85, ge=0.1, le=1, description="Foreground ratio")
    remesh: Optional[RemeshType] = Field(default=RemeshType.NONE, description="Remesh algorithm")
    vertex_count: Optional[int] = Field(default=-1, ge=-1, le=20000, description="Target vertex count")


class StablePointAware3DRequest(BaseStabilityRequest):
    """Request model for Stable Point Aware 3D."""
    texture_resolution: Optional[TextureResolution] = Field(default=TextureResolution.RES_1024, description="Texture resolution")
    foreground_ratio: Optional[float] = Field(default=1.3, ge=1, le=2, description="Foreground ratio")
    remesh: Optional[RemeshType] = Field(default=RemeshType.NONE, description="Remesh algorithm")
    target_type: Optional[TargetType] = Field(default=TargetType.NONE, description="Target type")
    target_count: Optional[int] = Field(default=1000, ge=100, le=20000, description="Target count")
    guidance_scale: Optional[float] = Field(default=3, ge=1, le=10, description="Guidance scale")


# ==================== AUDIO MODELS ====================

class TextToAudioRequest(BaseModel):
    """Request model for text-to-audio generation."""
    prompt: str = Field(..., max_length=10000, description="Audio generation prompt")
    duration: Optional[float] = Field(default=190, ge=1, le=190, description="Duration in seconds")
    seed: Optional[int] = Field(default=0, ge=0, le=4294967294, description="Random seed")
    steps: Optional[int] = Field(default=None, description="Sampling steps (model-dependent)")
    cfg_scale: Optional[float] = Field(default=None, ge=1, le=25, description="CFG scale")
    model: Optional[AudioModel] = Field(default=AudioModel.STABLE_AUDIO_2, description="Audio model")
    output_format: Optional[AudioOutputFormat] = Field(default=AudioOutputFormat.MP3, description="Output format")


class AudioToAudioRequest(BaseModel):
    """Request model for audio-to-audio generation."""
    prompt: str = Field(..., max_length=10000, description="Audio generation prompt")
    duration: Optional[float] = Field(default=190, ge=1, le=190, description="Duration in seconds")
    seed: Optional[int] = Field(default=0, ge=0, le=4294967294, description="Random seed")
    steps: Optional[int] = Field(default=None, description="Sampling steps (model-dependent)")
    cfg_scale: Optional[float] = Field(default=None, ge=1, le=25, description="CFG scale")
    model: Optional[AudioModel] = Field(default=AudioModel.STABLE_AUDIO_2, description="Audio model")
    output_format: Optional[AudioOutputFormat] = Field(default=AudioOutputFormat.MP3, description="Output format")
    strength: Optional[float] = Field(default=1, ge=0, le=1, description="Audio influence strength")


class AudioInpaintRequest(BaseModel):
    """Request model for audio inpainting."""
    prompt: str = Field(..., max_length=10000, description="Audio generation prompt")
    duration: Optional[float] = Field(default=190, ge=1, le=190, description="Duration in seconds")
    seed: Optional[int] = Field(default=0, ge=0, le=4294967294, description="Random seed")
    steps: Optional[int] = Field(default=8, ge=4, le=8, description="Sampling steps")
    output_format: Optional[AudioOutputFormat] = Field(default=AudioOutputFormat.MP3, description="Output format")
    mask_start: Optional[float] = Field(default=30, ge=0, le=190, description="Mask start time")
    mask_end: Optional[float] = Field(default=190, ge=0, le=190, description="Mask end time")


# ==================== RESPONSE MODELS ====================

class GenerationResponse(BaseModel):
    """Response model for generation requests."""
    id: str = Field(..., description="Generation ID for async operations")


class ImageGenerationResponse(BaseModel):
    """Response model for direct image generation."""
    image: Optional[str] = Field(default=None, description="Base64 encoded image")
    seed: Optional[int] = Field(default=None, description="Seed used for generation")
    finish_reason: Optional[FinishReason] = Field(default=None, description="Generation finish reason")


class AudioGenerationResponse(BaseModel):
    """Response model for audio generation."""
    audio: Optional[str] = Field(default=None, description="Base64 encoded audio")
    seed: Optional[int] = Field(default=None, description="Seed used for generation")
    finish_reason: Optional[FinishReason] = Field(default=None, description="Generation finish reason")


class GenerationStatusResponse(BaseModel):
    """Response model for generation status."""
    id: str = Field(..., description="Generation ID")
    status: Literal["in-progress"] = Field(..., description="Generation status")


class ErrorResponse(BaseModel):
    """Error response model."""
    id: str = Field(..., description="Error ID")
    name: str = Field(..., description="Error name")
    errors: List[str] = Field(..., description="Error messages")


# ==================== LEGACY V1 MODELS ====================

class TextPrompt(BaseModel):
    """Text prompt for V1 API."""
    text: str = Field(..., max_length=2000, description="Prompt text")
    weight: Optional[float] = Field(default=1.0, description="Prompt weight")


class V1TextToImageRequest(BaseModel):
    """V1 Text-to-image request."""
    text_prompts: List[TextPrompt] = Field(..., min_items=1, description="Text prompts")
    height: Optional[int] = Field(default=512, ge=128, description="Image height")
    width: Optional[int] = Field(default=512, ge=128, description="Image width")
    cfg_scale: Optional[float] = Field(default=7, ge=0, le=35, description="CFG scale")
    samples: Optional[int] = Field(default=1, ge=1, le=10, description="Number of samples")
    steps: Optional[int] = Field(default=30, ge=10, le=50, description="Diffusion steps")
    seed: Optional[int] = Field(default=0, ge=0, le=4294967295, description="Random seed")


class V1ImageToImageRequest(BaseModel):
    """V1 Image-to-image request."""
    text_prompts: List[TextPrompt] = Field(..., min_items=1, description="Text prompts")
    image_strength: Optional[float] = Field(default=0.35, ge=0, le=1, description="Image strength")
    init_image_mode: Optional[str] = Field(default="IMAGE_STRENGTH", description="Init image mode")
    cfg_scale: Optional[float] = Field(default=7, ge=0, le=35, description="CFG scale")
    samples: Optional[int] = Field(default=1, ge=1, le=10, description="Number of samples")
    steps: Optional[int] = Field(default=30, ge=10, le=50, description="Diffusion steps")
    seed: Optional[int] = Field(default=0, ge=0, le=4294967295, description="Random seed")


class V1MaskingRequest(BaseModel):
    """V1 Masking request."""
    text_prompts: List[TextPrompt] = Field(..., min_items=1, description="Text prompts")
    mask_source: str = Field(..., description="Mask source")
    cfg_scale: Optional[float] = Field(default=7, ge=0, le=35, description="CFG scale")
    samples: Optional[int] = Field(default=1, ge=1, le=10, description="Number of samples")
    steps: Optional[int] = Field(default=30, ge=10, le=50, description="Diffusion steps")
    seed: Optional[int] = Field(default=0, ge=0, le=4294967295, description="Random seed")


class V1GenerationArtifact(BaseModel):
    """V1 Generation artifact."""
    base64: str = Field(..., description="Base64 encoded image")
    seed: int = Field(..., description="Generation seed")
    finishReason: str = Field(..., description="Finish reason")


class V1GenerationResponse(BaseModel):
    """V1 Generation response."""
    artifacts: List[V1GenerationArtifact] = Field(..., description="Generated artifacts")


# ==================== USER & ACCOUNT MODELS ====================

class OrganizationMembership(BaseModel):
    """Organization membership details."""
    id: str = Field(..., description="Organization ID")
    name: str = Field(..., description="Organization name")
    role: str = Field(..., description="User role")
    is_default: bool = Field(..., description="Is default organization")


class AccountResponse(BaseModel):
    """Account details response."""
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    profile_picture: str = Field(..., description="Profile picture URL")
    organizations: List[OrganizationMembership] = Field(..., description="Organizations")


class BalanceResponse(BaseModel):
    """Balance response."""
    credits: float = Field(..., description="Credit balance")


class Engine(BaseModel):
    """Engine details."""
    id: str = Field(..., description="Engine ID")
    name: str = Field(..., description="Engine name")
    description: str = Field(..., description="Engine description")
    type: str = Field(..., description="Engine type")


class ListEnginesResponse(BaseModel):
    """List engines response."""
    engines: List[Engine] = Field(..., description="Available engines")


# ==================== MULTIPART FORM MODELS ====================

class MultipartImageRequest(BaseModel):
    """Base multipart request with image."""
    image: bytes = Field(..., description="Image file binary data")


class MultipartAudioRequest(BaseModel):
    """Base multipart request with audio."""
    audio: bytes = Field(..., description="Audio file binary data")


class MultipartMaskRequest(BaseModel):
    """Multipart request with image and mask."""
    image: bytes = Field(..., description="Image file binary data")
    mask: Optional[bytes] = Field(default=None, description="Mask file binary data")


class MultipartStyleTransferRequest(BaseModel):
    """Multipart request for style transfer."""
    init_image: bytes = Field(..., description="Initial image binary data")
    style_image: bytes = Field(..., description="Style image binary data")


class MultipartReplaceBackgroundRequest(BaseModel):
    """Multipart request for background replacement."""
    subject_image: bytes = Field(..., description="Subject image binary data")
    background_reference: Optional[bytes] = Field(default=None, description="Background reference image")
    light_reference: Optional[bytes] = Field(default=None, description="Light reference image")