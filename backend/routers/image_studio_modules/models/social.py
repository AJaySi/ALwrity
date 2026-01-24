"""Social optimization-related Pydantic models for Image Studio API."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


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