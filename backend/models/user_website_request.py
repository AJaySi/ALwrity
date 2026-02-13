"""User Website request/response models for ALwrity website automation."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserWebsiteRequest(BaseModel):
    user_id: str = Field(..., description="User ID for website ownership")
    github_repo_url: Optional[str] = Field(None, max_length=500)
    netlify_site_id: Optional[str] = Field(None, max_length=100)
    netlify_site_url: Optional[str] = Field(None, max_length=500)
    preview_url: Optional[str] = Field(None, max_length=500)
    template_type: str = Field("blog", max_length=50)
    status: str = Field("initializing", max_length=20)


class UserWebsiteResponse(BaseModel):
    id: int
    user_id: str
    github_repo_url: Optional[str]
    netlify_site_id: Optional[str]
    netlify_site_url: Optional[str]
    preview_url: Optional[str]
    template_type: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
