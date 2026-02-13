"""YouTube Video Planning Models

Pydantic models for video planning and script generation functionality.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class VideoPlanRequest(BaseModel):
    """Request model for video planning."""
    user_idea: str = Field(..., description="User's video idea or topic")
    duration_type: str = Field(
        ...,
        pattern="^(shorts|medium|long)$",
        description="Video duration type: shorts (≤60s), medium (1-4min), long (4-10min)"
    )
    video_type: Optional[str] = Field(
        None,
        pattern="^(tutorial|review|educational|entertainment|vlog|product_demo|reaction|storytelling)$",
        description="Video format type: tutorial, review, educational, entertainment, vlog, product_demo, reaction, storytelling"
    )
    target_audience: Optional[str] = Field(
        None,
        description="Target audience description (helps optimize tone, pace, and style)"
    )
    video_goal: Optional[str] = Field(
        None,
        description="Primary goal of the video (educate, sell, entertain, etc.)"
    )
    brand_style: Optional[str] = Field(
        None,
        description="Brand visual aesthetic and style preferences"
    )
    reference_image_description: Optional[str] = Field(
        None,
        description="Optional description of reference image for visual inspiration"
    )
    source_content_id: Optional[str] = Field(
        None,
        description="Optional ID of source content (blog/story) to convert"
    )
    source_content_type: Optional[str] = Field(
        None,
        pattern="^(blog|story)$",
        description="Type of source content: blog or story"
    )
    avatar_url: Optional[str] = Field(
        None,
        description="Optional avatar URL if user uploaded one before plan generation"
    )
    enable_research: Optional[bool] = Field(
        True,
        description="Enable Exa research to enhance plan with current information, trends, and better SEO keywords (default: True)"
    )


class VideoPlanResponse(BaseModel):
    """Response model for video plan."""
    success: bool
    plan: Optional[Dict[str, Any]] = None
    message: str