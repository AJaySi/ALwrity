"""Face swap-related Pydantic models for Image Studio API."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


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