"""
User Project Models - User Data Database
User workspaces and projects with multi-tenant isolation.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional
import uuid

Base = declarative_base()

class UserProject(Base):
    """
    User workspaces across all features.
    User data database table with multi-tenant isolation by user_id.
    """
    __tablename__ = "user_projects"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Multi-tenant isolation
    user_id = Column(String, nullable=False, index=True)  # Foreign key to users table (platform DB)
    
    # Project information
    project_name = Column(String, nullable=False)
    project_description = Column(Text, nullable=True)
    project_type = Column(String, nullable=False, index=True)  # blog, research, persona, campaign, etc.
    
    # Project status and settings
    status = Column(String, default="active")  # active, archived, deleted
    is_public = Column(Boolean, default=False)  # Shareable project
    is_template = Column(Boolean, default=False)  # Can be used as template
    
    # Project metadata
    project_metadata = Column(JSON, default={})  # Flexible metadata for different project types
    
    # Content and assets
    content_count = Column(Integer, default=0)
    asset_count = Column(Integer, default=0)
    
    # Project settings
    settings = Column(JSON, default={})  # Project-specific settings
    collaboration = Column(JSON, default={})  # Team collaboration settings
    
    # SEO and marketing
    target_keywords = Column(JSON, default=[])  # SEO keywords
    target_audience = Column(JSON, default={})  # Audience demographics
    content_strategy = Column(JSON, default={})  # Content strategy and goals
    
    # Analytics and metrics
    views = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    
    # Template information (if is_template=True)
    template_category = Column(String, nullable=True)
    template_tags = Column(JSON, default=[])
    usage_count = Column(Integer, default=0)  # How many times this template was used
    
    # Parent-child relationships (for project organization)
    parent_project_id = Column(String, nullable=True)  # For sub-projects
    project_order = Column(Integer, default=0)  # Sort order within parent
    
    # External integrations
    external_id = Column(String, nullable=True)  # ID in external systems
    integration_data = Column(JSON, default={})  # Integration-specific data
    
    # Metadata
    project_metadata = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    archived_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<UserProject(id={self.id}, user_id={self.user_id}, project_name={self.project_name}, project_type={self.project_type})>"
    
    @property
    def is_archived(self) -> bool:
        """Check if project is archived"""
        return self.status == "archived"
    
    @property
    def is_deleted(self) -> bool:
        """Check if project is deleted"""
        return self.status == "deleted"
    
    @property
    def days_since_created(self) -> int:
        """Get days since project was created"""
        delta = datetime.utcnow() - self.created_at
        return delta.days
    
    @property
    def days_since_updated(self) -> int:
        """Get days since project was last updated"""
        delta = datetime.utcnow() - self.updated_at
        return delta.days
    
    def add_asset(self):
        """Increment asset count"""
        self.asset_count += 1
        self.updated_at = datetime.utcnow()
    
    def add_content(self):
        """Increment content count"""
        self.content_count += 1
        self.updated_at = datetime.utcnow()
    
    def archive(self):
        """Archive the project"""
        self.status = "archived"
        self.archived_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def delete(self):
        """Soft delete the project"""
        self.status = "deleted"
        self.updated_at = datetime.utcnow()
    
    def publish(self):
        """Publish the project"""
        self.is_public = True
        self.published_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert project to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "project_name": self.project_name,
            "project_description": self.project_description,
            "project_type": self.project_type,
            "status": self.status,
            "is_public": self.is_public,
            "is_template": self.is_template,
            "project_metadata": self.project_metadata or {},
            "content_count": self.content_count,
            "asset_count": self.asset_count,
            "settings": self.settings or {},
            "collaboration": self.collaboration or {},
            "target_keywords": self.target_keywords or [],
            "target_audience": self.target_audience or {},
            "content_strategy": self.content_strategy or {},
            "views": self.views,
            "shares": self.shares,
            "conversions": self.conversions,
            "template_category": self.template_category,
            "template_tags": self.template_tags or [],
            "usage_count": self.usage_count,
            "parent_project_id": self.parent_project_id,
            "project_order": self.project_order,
            "external_id": self.external_id,
            "integration_data": self.integration_data or {},
            "project_metadata": self.project_metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
            "is_archived": self.is_archived,
            "is_deleted": self.is_deleted,
            "days_since_created": self.days_since_created,
            "days_since_updated": self.days_since_updated
        }
