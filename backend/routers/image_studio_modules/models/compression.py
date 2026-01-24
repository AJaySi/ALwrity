"""Compression-related Pydantic models for Image Studio API."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


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