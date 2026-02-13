"""YouTube Video Rendering Models

Pydantic models for video rendering, processing, and combination functionality.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class VideoRenderRequest(BaseModel):
    """Request model for video rendering."""
    scenes: List[Dict[str, Any]] = Field(..., description="List of scenes to render")
    video_plan: Dict[str, Any] = Field(..., description="Original video plan")
    resolution: str = Field("720p", pattern="^(480p|720p|1080p)$", description="Video resolution")
    combine_scenes: bool = Field(True, description="Whether to combine scenes into single video")
    voice_id: str = Field("Wise_Woman", description="Voice ID for narration")


class SceneVideoRenderRequest(BaseModel):
    """Request model for rendering a single scene video."""
    scene: Dict[str, Any] = Field(..., description="Single scene data to render")
    video_plan: Dict[str, Any] = Field(..., description="Original video plan (context)")
    resolution: str = Field("720p", pattern="^(480p|720p|1080p)$", description="Video resolution")
    voice_id: str = Field("Wise_Woman", description="Voice ID for narration")
    generate_audio_enabled: bool = Field(False, description="Whether to auto-generate audio if missing (default false)")


class SceneVideoRenderResponse(BaseModel):
    """Response model for single scene video rendering."""
    success: bool
    task_id: Optional[str] = None
    message: str
    scene_number: Optional[int] = None


class CombineVideosRequest(BaseModel):
    """Request model for combining multiple scene videos."""
    scene_video_urls: List[str] = Field(..., description="List of scene video URLs to combine")
    resolution: str = Field("720p", pattern="^(480p|720p|1080p)$", description="Output video resolution")
    title: Optional[str] = Field(None, description="Optional title for the combined video")


class CombineVideosResponse(BaseModel):
    """Response model for combine videos request."""
    success: bool
    task_id: Optional[str] = None
    message: str


class VideoRenderResponse(BaseModel):
    """Response model for video rendering."""
    success: bool
    task_id: Optional[str] = None
    message: str