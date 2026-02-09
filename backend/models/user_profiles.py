"""
User Profile Models - User Data Database
User preferences and business information with multi-tenant isolation.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional
import uuid

Base = declarative_base()

class UserProfile(Base):
    """
    User preferences and business information.
    User data database table with multi-tenant isolation by user_id.
    """
    __tablename__ = "user_profiles"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Multi-tenant isolation
    user_id = Column(String, nullable=False, index=True)  # Foreign key to users table (platform DB)
    
    # Business information
    business_name = Column(String, nullable=True)
    business_industry = Column(String, nullable=True)
    business_size = Column(String, nullable=True)  # small, medium, large, enterprise
    business_website = Column(String, nullable=True)
    business_description = Column(Text, nullable=True)
    
    # Contact information
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    business_address = Column(JSON, nullable=True)  # Address object
    
    # Content preferences
    content_goals = Column(JSON, default=dict)  # SEO, lead generation, brand awareness, etc.
    target_audience = Column(JSON, default=dict)  # Demographics, interests, pain points
    brand_voice = Column(JSON, default=dict)  # Tone, style, personality traits
    content_types = Column(JSON, default=list)  # blog, social, email, video, etc.
    
    # Writing preferences
    writing_style = Column(String, nullable=True)  # formal, casual, professional, creative
    content_length_preference = Column(String, nullable=True)  # short, medium, long
    seo_focus = Column(Boolean, default=True)
    
    # AI preferences
    preferred_ai_models = Column(JSON, default=list)  # GPT-4, Claude, etc.
    creativity_level = Column(Integer, default=5)  # 1-10 scale
    temperature = Column(Float, default=0.7)  # AI creativity parameter
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=False)
    weekly_reports = Column(Boolean, default=True)
    
    # Integration settings
    integrations = Column(JSON, default=dict)  # Connected tools and services
    api_keys = Column(JSON, default=dict)  # Encrypted API keys for external services
    
    # Metadata
    profile_metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, business_name={self.business_name})>"
    
    @property
    def is_complete(self) -> bool:
        """Check if user profile is complete"""
        required_fields = [
            self.business_name,
            self.business_industry,
            self.content_goals,
            self.target_audience
        ]
        return all(field for field in required_fields)
    
    @property
    def days_since_last_active(self) -> Optional[int]:
        """Get days since user was last active"""
        if not self.last_active_at:
            return None
        delta = datetime.utcnow() - self.last_active_at
        return delta.days
    
    def to_dict(self) -> dict:
        """Convert user profile to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "business_name": self.business_name,
            "business_industry": self.business_industry,
            "business_size": self.business_size,
            "business_website": self.business_website,
            "business_description": self.business_description,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "business_address": self.business_address or {},
            "content_goals": self.content_goals or {},
            "target_audience": self.target_audience or {},
            "brand_voice": self.brand_voice or {},
            "content_types": self.content_types or [],
            "writing_style": self.writing_style,
            "content_length_preference": self.content_length_preference,
            "seo_focus": self.seo_focus,
            "preferred_ai_models": self.preferred_ai_models or [],
            "creativity_level": self.creativity_level,
            "temperature": self.temperature,
            "email_notifications": self.email_notifications,
            "push_notifications": self.push_notifications,
            "weekly_reports": self.weekly_reports,
            "integrations": self.integrations or {},
            "api_keys": self.api_keys or {},
            "profile_metadata": self.profile_metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_active_at": self.last_active_at.isoformat() if self.last_active_at else None,
            "is_complete": self.is_complete,
            "days_since_last_active": self.days_since_last_active
        }
