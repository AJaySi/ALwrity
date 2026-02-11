"""
User Content Asset Models - User Data Database
All user-generated content with multi-tenant isolation and RLS.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text, Float
from models.ssot_bases import UserDataBase
from datetime import datetime
from typing import Optional
import uuid

Base = UserDataBase

class UserContentAsset(Base):
    """
    All user-generated content with strict multi-tenant isolation.
    User data database table with Row-Level Security by user_id.
    """
    __tablename__ = "user_content_assets"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Multi-tenant isolation (RLS will enforce this)
    user_id = Column(String, nullable=False, index=True)  # Foreign key to users table (platform DB)
    project_id = Column(String, nullable=True, index=True)  # Foreign key to user_projects
    
    # Content information
    asset_type = Column(String, nullable=False, index=True)  # blog, research, persona, social, email, etc.
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Content data
    content = Column(Text, nullable=True)  # Main content text
    content_html = Column(Text, nullable=True)  # Formatted HTML content
    content_markdown = Column(Text, nullable=True)  # Markdown source
    
    # Content metadata
    word_count = Column(Integer, default=0)
    character_count = Column(Integer, default=0)
    reading_time_minutes = Column(Integer, default=0)
    
    # SEO data
    seo_data = Column(JSON, default={})  # SEO metadata, keywords, descriptions
    meta_title = Column(String, nullable=True)
    meta_description = Column(Text, nullable=True)
    focus_keywords = Column(JSON, default=[])
    
    # Content status and workflow
    status = Column(String, default="draft")  # draft, review, published, archived
    visibility = Column(String, default="private")  # private, public, unlisted
    
    # AI generation metadata
    ai_model_used = Column(String, nullable=True)  # GPT-4, Claude, etc.
    ai_prompt = Column(Text, nullable=True)  # Original AI prompt
    ai_parameters = Column(JSON, default={})  # Temperature, creativity, etc.
    generation_time_ms = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    
    # Content categorization
    category = Column(String, nullable=True)
    tags = Column(JSON, default=[])
    content_tone = Column(String, nullable=True)  # formal, casual, professional, creative
    
    # Performance metrics
    views = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    
    # Publishing information
    published_at = Column(DateTime, nullable=True)
    scheduled_publish_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Version control
    version = Column(Integer, default=1)
    parent_asset_id = Column(String, nullable=True)  # For content variations
    is_latest_version = Column(Boolean, default=True)
    
    # External integrations
    external_url = Column(String, nullable=True)  # Published content URL
    integration_data = Column(JSON, default={})  # Platform-specific data
    
    # Content quality metrics
    readability_score = Column(Float, nullable=True)  # Flesch-Kincaid, etc.
    seo_score = Column(Float, nullable=True)  # SEO optimization score
    engagement_score = Column(Float, nullable=True)  # User engagement metrics
    
    # Content relationships
    linked_assets = Column(JSON, default=[])  # Related content assets
    references = Column(JSON, default=[])  # Sources and references
    
    # Workflow and collaboration
    assigned_to = Column(String, nullable=True)  # User ID of assigned person
    reviewed_by = Column(String, nullable=True)  # User ID of reviewer
    approved_by = Column(String, nullable=True)  # User ID of approver
    
    # Content settings
    settings = Column(JSON, default={})  # Asset-specific settings
    template_id = Column(String, nullable=True)  # Template used for creation
    
    # Analytics and tracking
    analytics_data = Column(JSON, default={})  # Detailed analytics
    a_b_test_data = Column(JSON, default={})  # A/B testing information
    
    # Metadata
    asset_metadata = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_viewed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<UserContentAsset(id={self.id}, user_id={self.user_id}, asset_type={self.asset_type}, title={self.title})>"
    
    @property
    def is_published(self) -> bool:
        """Check if content is published"""
        return self.status == "published" and self.published_at is not None
    
    @property
    def is_draft(self) -> bool:
        """Check if content is in draft status"""
        return self.status == "draft"
    
    @property
    def is_archived(self) -> bool:
        """Check if content is archived"""
        return self.status == "archived"
    
    @property
    def is_expired(self) -> bool:
        """Check if content has expired"""
        return self.expires_at and self.expires_at < datetime.utcnow()
    
    @property
    def days_since_created(self) -> int:
        """Get days since content was created"""
        delta = datetime.utcnow() - self.created_at
        return delta.days
    
    @property
    def days_since_published(self) -> Optional[int]:
        """Get days since content was published"""
        if not self.published_at:
            return None
        delta = datetime.utcnow() - self.published_at
        return delta.days
    
    @property
    def estimated_reading_time(self) -> int:
        """Calculate estimated reading time in minutes"""
        if self.word_count > 0:
            return max(1, self.word_count // 200)  # Average reading speed: 200 words/minute
        return self.reading_time_minutes or 0
    
    def publish(self):
        """Publish the content"""
        self.status = "published"
        self.published_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def archive(self):
        """Archive the content"""
        self.status = "archived"
        self.updated_at = datetime.utcnow()
    
    def update_content_metrics(self, word_count: int, character_count: int):
        """Update content metrics"""
        self.word_count = word_count
        self.character_count = character_count
        self.reading_time_minutes = self.estimated_reading_time
        self.updated_at = datetime.utcnow()
    
    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.last_viewed_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert content asset to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "asset_type": self.asset_type,
            "title": self.title,
            "description": self.description,
            "content": self.content,
            "content_html": self.content_html,
            "content_markdown": self.content_markdown,
            "word_count": self.word_count,
            "character_count": self.character_count,
            "reading_time_minutes": self.reading_time_minutes,
            "seo_data": self.seo_data or {},
            "meta_title": self.meta_title,
            "meta_description": self.meta_description,
            "focus_keywords": self.focus_keywords or [],
            "status": self.status,
            "visibility": self.visibility,
            "ai_model_used": self.ai_model_used,
            "ai_prompt": self.ai_prompt,
            "ai_parameters": self.ai_parameters or {},
            "generation_time_ms": self.generation_time_ms,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
            "category": self.category,
            "tags": self.tags or [],
            "content_tone": self.content_tone,
            "views": self.views,
            "shares": self.shares,
            "likes": self.likes,
            "comments_count": self.comments_count,
            "conversions": self.conversions,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "scheduled_publish_at": self.scheduled_publish_at.isoformat() if self.scheduled_publish_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "version": self.version,
            "parent_asset_id": self.parent_asset_id,
            "is_latest_version": self.is_latest_version,
            "external_url": self.external_url,
            "integration_data": self.integration_data or {},
            "readability_score": self.readability_score,
            "seo_score": self.seo_score,
            "engagement_score": self.engagement_score,
            "linked_assets": self.linked_assets or [],
            "references": self.references or [],
            "assigned_to": self.assigned_to,
            "reviewed_by": self.reviewed_by,
            "approved_by": self.approved_by,
            "settings": self.settings or {},
            "template_id": self.template_id,
            "analytics_data": self.analytics_data or {},
            "a_b_test_data": self.a_b_test_data or {},
            "asset_metadata": self.asset_metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_viewed_at": self.last_viewed_at.isoformat() if self.last_viewed_at else None,
            "is_published": self.is_published,
            "is_draft": self.is_draft,
            "is_archived": self.is_archived,
            "is_expired": self.is_expired,
            "days_since_created": self.days_since_created,
            "days_since_published": self.days_since_published,
            "estimated_reading_time": self.estimated_reading_time
        }
