"""Format conversion-related Pydantic models for Image Studio API."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


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