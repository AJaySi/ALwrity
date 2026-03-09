"""User Website Request models for ALwrity website maker functionality."""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class WebsiteStatus(str, Enum):
    """Website creation status enum."""
    INITIATED = "initiated"
    PREVIEWING = "previewing"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TemplateType(str, Enum):
    """Website template types."""
    BLOG = "blog"
    PROFILE = "profile"
    SHOP = "shop"
    DONT_KNOW = "dont_know"


class UserWebsiteRequest(BaseModel):
    """Request model for creating/updating user website."""
    user_id: int = Field(..., description="User ID")
    template_type: TemplateType = Field(default=TemplateType.BLOG, description="Website template type")
    business_name: Optional[str] = Field(None, description="Business name")
    business_description: Optional[str] = Field(None, description="Business description")
    status: WebsiteStatus = Field(default=WebsiteStatus.INITIATED, description="Website status")
    github_repo_url: Optional[str] = Field(None, description="GitHub repository URL")
    netlify_site_url: Optional[str] = Field(None, description="Netlify deployed site URL")
    netlify_admin_url: Optional[str] = Field(None, description="Netlify admin URL")
    site_brief: Optional[Dict[str, Any]] = Field(None, description="Generated site brief")
    theme_tokens: Optional[Dict[str, Any]] = Field(None, description="Theme configuration tokens")
    custom_css: Optional[str] = Field(None, description="Custom CSS for theming")
    preview_url: Optional[str] = Field(None, description="Preview site URL")
    deployment_config: Optional[Dict[str, Any]] = Field(None, description="Deployment configuration")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class UserWebsiteResponse(BaseModel):
    """Response model for user website data."""
    id: int
    user_id: int
    template_type: TemplateType
    business_name: Optional[str]
    business_description: Optional[str]
    status: WebsiteStatus
    github_repo_url: Optional[str]
    netlify_site_url: Optional[str]
    netlify_admin_url: Optional[str]
    site_brief: Optional[Dict[str, Any]]
    theme_tokens: Optional[Dict[str, Any]]
    custom_css: Optional[str]
    preview_url: Optional[str]
    deployment_config: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WebsitePreviewRequest(BaseModel):
    """Request model for generating website preview."""
    user_id: int
    intake_data: Dict[str, Any] = Field(..., description="Business intake data")
    template_type: Optional[TemplateType] = Field(None, description="Template type override")


class WebsiteDeploymentRequest(BaseModel):
    """Request model for deploying website."""
    user_id: int
    intake_data: Dict[str, Any] = Field(..., description="Business intake data")
    template_type: Optional[TemplateType] = Field(None, description="Template type override")
    custom_domain: Optional[str] = Field(None, description="Custom domain for deployment")


class WebsiteStatusUpdate(BaseModel):
    """Request model for updating website status."""
    status: WebsiteStatus
    github_repo_url: Optional[str] = None
    netlify_site_url: Optional[str] = None
    netlify_admin_url: Optional[str] = None
    preview_url: Optional[str] = None
    error_message: Optional[str] = None


# Database model for SQLAlchemy
class UserWebsite:
    """SQLAlchemy model for UserWebsite table."""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': getattr(self, 'id', None),
            'user_id': getattr(self, 'user_id', None),
            'template_type': getattr(self, 'template_type', None),
            'business_name': getattr(self, 'business_name', None),
            'business_description': getattr(self, 'business_description', None),
            'status': getattr(self, 'status', None),
            'github_repo_url': getattr(self, 'github_repo_url', None),
            'netlify_site_url': getattr(self, 'netlify_site_url', None),
            'netlify_admin_url': getattr(self, 'netlify_admin_url', None),
            'site_brief': getattr(self, 'site_brief', None),
            'theme_tokens': getattr(self, 'theme_tokens', None),
            'custom_css': getattr(self, 'custom_css', None),
            'preview_url': getattr(self, 'preview_url', None),
            'deployment_config': getattr(self, 'deployment_config', None),
            'error_message': getattr(self, 'error_message', None),
            'created_at': getattr(self, 'created_at', None),
            'updated_at': getattr(self, 'updated_at', None),
        }
