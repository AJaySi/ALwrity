"""Generation-related Pydantic models for Image Studio API."""

from typing import Optional
from pydantic import BaseModel, Field


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