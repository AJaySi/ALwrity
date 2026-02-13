"""Transform-related Pydantic models for Image Studio API."""

from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


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

class TransformJobResponse(BaseModel):
    """Response model for async transform job submission."""
    success: bool
    job_id: str
    status: Literal["queued", "processing", "completed", "failed", "cancelled"]
    operation: Literal["image-to-video", "talking-avatar"]
    message: str


class TransformJobStatusResponse(BaseModel):
    """Response model for async transform job status."""
    success: bool
    job_id: str
    status: Literal["queued", "processing", "completed", "failed", "cancelled"]
    operation: Literal["image-to-video", "talking-avatar"]
    progress: float = 0.0
    message: Optional[str] = None
    result: Optional[TransformVideoResponse] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str


class TransformCancelResponse(BaseModel):
    """Response model for transform job cancellation."""
    success: bool
    job_id: str
    status: Literal["cancelled"]
    message: str
