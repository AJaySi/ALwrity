"""YouTube Assets Models

Pydantic models for video assets, file management, and serving functionality.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class VideoListResponse(BaseModel):
    """Response model for listing user videos."""
    videos: List[Dict[str, Any]]
    success: bool = True
    message: str = "Videos fetched successfully"