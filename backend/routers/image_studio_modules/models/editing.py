"""Editing-related Pydantic models for Image Studio API."""

from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field


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