"""YouTube Cost Estimation Models

Pydantic models for cost estimation and pricing functionality.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class CostEstimateRequest(BaseModel):
    """Request model for cost estimation."""
    scenes: List[Dict[str, Any]] = Field(..., description="List of scenes to estimate")
    resolution: str = Field("720p", pattern="^(480p|720p|1080p)$", description="Video resolution")
    image_model: Optional[str] = Field("ideogram-v3-turbo", description="Image generation model")


class CostEstimateResponse(BaseModel):
    """Response model for cost estimation."""
    success: bool
    estimate: Optional[Dict[str, Any]] = None
    message: str