"""
User Management Models - Platform Database
Central user accounts and authentication for ALwrity SaaS platform.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional
import uuid

Base = declarative_base()

class User(Base):
    """
    Central user accounts and authentication.
    Platform database table for user management.
    """
    __tablename__ = "users"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Authentication fields
    clerk_id = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    
    # User status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Subscription information
    subscription_status = Column(String, default="free")  # free, basic, pro, enterprise
    subscription_id = Column(String, nullable=True)  # Foreign key to user_subscriptions
    
    # User metadata
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    profile_image_url = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    # User preferences (JSON)
    preferences = Column(JSON, default={})
    
    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="user")
    usage_logs = relationship("PlatformUsageLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, subscription_status={self.subscription_status})>"
    
    @property
    def full_name(self) -> Optional[str]:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or None
    
    def to_dict(self) -> dict:
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "clerk_id": self.clerk_id,
            "email": self.email,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "subscription_status": self.subscription_status,
            "subscription_id": self.subscription_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "profile_image_url": self.profile_image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "preferences": self.preferences or {}
        }
