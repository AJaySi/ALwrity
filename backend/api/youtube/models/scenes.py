"""YouTube Scene Building Models

Pydantic models for scene creation, building, and management functionality.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class SceneBuildRequest(BaseModel):
    """Request model for scene building."""
    video_plan: Dict[str, Any] = Field(..., description="Video plan from planning endpoint")
    custom_script: Optional[str] = Field(
        None,
        description="Optional custom script to use instead of generating from plan"
    )


class SceneBuildResponse(BaseModel):
    """Response model for scene building."""
    success: bool
    scenes: List[Dict[str, Any]] = []
    message: str


class SceneUpdateRequest(BaseModel):
    """Request model for updating a single scene."""
    scene_id: int = Field(..., description="Scene number to update")
    narration: Optional[str] = None
    visual_description: Optional[str] = None
    duration_estimate: Optional[float] = None
    enabled: Optional[bool] = None


class SceneUpdateResponse(BaseModel):
    """Response model for scene update."""
    success: bool
    scene: Optional[Dict[str, Any]] = None
    message: str