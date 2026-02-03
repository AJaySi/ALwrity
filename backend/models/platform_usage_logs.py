"""
Platform Usage Analytics Models - Platform Database
Platform-level analytics and monitoring for ALwrity SaaS platform.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional
import uuid

Base = declarative_base()

class PlatformUsageLog(Base):
    """
    Platform-level analytics and monitoring.
    Platform database table for usage tracking and analytics.
    """
    __tablename__ = "platform_usage_logs"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User and subscription references
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    subscription_id = Column(String, ForeignKey("user_subscriptions.id"), nullable=True, index=True)
    
    # Event information
    event_type = Column(String, nullable=False, index=True)  # api_call, content_creation, project_created, etc.
    feature = Column(String, nullable=False, index=True)    # ai_writing, research, persona, etc.
    action = Column(String, nullable=False)                 # create, update, delete, query, etc.
    
    # Resource usage metrics
    tokens_used = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    processing_time_ms = Column(Integer, default=0)
    
    # Request details
    endpoint = Column(String, nullable=True)
    method = Column(String, nullable=True)
    status_code = Column(Integer, nullable=True)
    
    # Content metrics
    content_type = Column(String, nullable=True)  # blog, research, persona, etc.
    content_length = Column(Integer, default=0)
    
    # Geographic and device information
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    country = Column(String, nullable=True)
    
    # Error information
    error_type = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Additional metadata
    usage_metadata = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="usage_logs")
    subscription = relationship("UserSubscription", back_populates="usage_logs")
    
    def __repr__(self):
        return f"<PlatformUsageLog(user_id={self.user_id}, event_type={self.event_type}, cost_usd={self.cost_usd})>"
    
    @property
    def is_successful(self) -> bool:
        """Check if the operation was successful"""
        return self.error_type is None and (self.status_code is None or 200 <= self.status_code < 400)
    
    @property
    def cost_per_token(self) -> Optional[float]:
        """Calculate cost per token if tokens were used"""
        if self.tokens_used > 0:
            return self.cost_usd / self.tokens_used
        return None
    
    def to_dict(self) -> dict:
        """Convert usage log to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "subscription_id": self.subscription_id,
            "event_type": self.event_type,
            "feature": self.feature,
            "action": self.action,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
            "processing_time_ms": self.processing_time_ms,
            "endpoint": self.endpoint,
            "method": self.method,
            "status_code": self.status_code,
            "content_type": self.content_type,
            "content_length": self.content_length,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "country": self.country,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "usage_metadata": self.usage_metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_successful": self.is_successful,
            "cost_per_token": self.cost_per_token
        }
