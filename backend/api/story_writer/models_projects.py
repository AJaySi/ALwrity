"""
Story Project API Models

Pydantic models for Story Studio project endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StoryProjectResponse(BaseModel):
    id: int
    project_id: str
    user_id: str
    title: Optional[str] = None
    story_mode: Optional[str] = None
    story_template: Optional[str] = None
    setup: Optional[Dict[str, Any]] = None
    outline: Optional[Dict[str, Any]] = None
    scenes: Optional[List[Dict[str, Any]]] = None
    story_content: Optional[Dict[str, Any]] = None
    anime_bible: Optional[Dict[str, Any]] = None
    media_state: Optional[Dict[str, Any]] = None
    current_phase: Optional[str] = None
    status: str = "draft"
    is_favorite: bool = False
    is_complete: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StoryProjectListResponse(BaseModel):
    projects: List[StoryProjectResponse]
    total: int
    limit: int
    offset: int


class CreateStoryProjectRequest(BaseModel):
    project_id: str = Field(..., description="Unique story project ID")
    title: Optional[str] = Field(None, description="Optional story project title or idea")
    story_mode: Optional[str] = Field(
        None, description="Story mode (marketing or pure) if provided by the UI"
    )
    story_template: Optional[str] = Field(
        None,
        description="Optional story template identifier (e.g. product_story, anime_fiction)",
    )
    setup: Optional[Dict[str, Any]] = Field(
        None,
        description="Initial story setup payload to persist with the project",
    )


class UpdateStoryProjectRequest(BaseModel):
    title: Optional[str] = None
    story_mode: Optional[str] = None
    story_template: Optional[str] = None
    setup: Optional[Dict[str, Any]] = None
    outline: Optional[Dict[str, Any]] = None
    scenes: Optional[List[Dict[str, Any]]] = None
    story_content: Optional[Dict[str, Any]] = None
    anime_bible: Optional[Dict[str, Any]] = None
    media_state: Optional[Dict[str, Any]] = None
    current_phase: Optional[str] = None
    status: Optional[str] = None
    is_complete: Optional[bool] = None

