"""
User Subscription Models - Platform Database
Subscription management and billing for ALwrity SaaS platform.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from typing import Optional
import uuid
import enum

Base = declarative_base()

class SubscriptionStatus(enum.Enum):
    """Subscription status enumeration"""
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    TRIALING = "trialing"

class BillingCycle(enum.Enum):
    """Billing cycle enumeration"""
    MONTHLY = "monthly"
    YEARLY = "yearly"

class SubscriptionPlan(Base):
    """
    Available subscription plans and their configurations.
    Platform database table for plan definitions.
    """
    __tablename__ = "subscription_plans"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Plan information
    name = Column(String, nullable=False, unique=True)  # Free, Basic, Pro, Enterprise
    display_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Pricing
    price_cents = Column(Integer, nullable=False, default=0)  # Price in cents
    currency = Column(String, nullable=False, default="USD")
    
    # Billing cycles
    monthly_price_cents = Column(Integer, nullable=True)
    yearly_price_cents = Column(Integer, nullable=True)
    
    # Limits and features
    features = Column(JSON, default={})  # Feature flags and limits
    api_tokens_limit = Column(Integer, default=1000)
    projects_limit = Column(Integer, default=10)
    team_members_limit = Column(Integer, default=1)
    
    # Plan metadata
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)  # Visible to users
    sort_order = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="plan")
    
    def __repr__(self):
        return f"<SubscriptionPlan(name={self.name}, price_cents={self.price_cents})>"
    
    def get_price_for_cycle(self, cycle: BillingCycle) -> Optional[int]:
        """Get price for specific billing cycle"""
        if cycle == BillingCycle.MONTHLY:
            return self.monthly_price_cents or self.price_cents
        elif cycle == BillingCycle.YEARLY:
            return self.yearly_price_cents or (self.price_cents * 10)  # 2 months free
        return None
    
    def to_dict(self) -> dict:
        """Convert plan to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "price_cents": self.price_cents,
            "currency": self.currency,
            "monthly_price_cents": self.monthly_price_cents,
            "yearly_price_cents": self.yearly_price_cents,
            "features": self.features or {},
            "api_tokens_limit": self.api_tokens_limit,
            "projects_limit": self.projects_limit,
            "team_members_limit": self.team_members_limit,
            "is_active": self.is_active,
            "is_public": self.is_public,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class UserSubscription(Base):
    """
    User subscription management and billing.
    Platform database table for user subscriptions.
    """
    __tablename__ = "user_subscriptions"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User and plan references
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(String, ForeignKey("subscription_plans.id"), nullable=False, index=True)
    
    # Subscription status
    status = Column(String, default=SubscriptionStatus.ACTIVE.value)
    
    # Billing information
    billing_cycle = Column(String, default=BillingCycle.MONTHLY.value)
    price_cents = Column(Integer, nullable=False)
    currency = Column(String, nullable=False, default="USD")
    
    # Subscription periods
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    trial_start = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)
    canceled_at = Column(DateTime, nullable=True)
    
    # Payment provider information
    stripe_subscription_id = Column(String, nullable=True, unique=True)
    stripe_customer_id = Column(String, nullable=True)
    
    # Usage tracking
    api_tokens_used = Column(Integer, default=0)
    projects_created = Column(Integer, default=0)
    
    # Metadata
    subscription_metadata = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    usage_logs = relationship("PlatformUsageLog", back_populates="subscription")
    
    def __repr__(self):
        return f"<UserSubscription(user_id={self.user_id}, plan_id={self.plan_id}, status={self.status})>"
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active"""
        return (
            self.status == SubscriptionStatus.ACTIVE.value and
            self.current_period_end > datetime.utcnow()
        )
    
    @property
    def is_trialing(self) -> bool:
        """Check if subscription is in trial period"""
        return (
            self.status == SubscriptionStatus.TRIALING.value and
            self.trial_end and
            self.trial_end > datetime.utcnow()
        )
    
    @property
    def days_until_renewal(self) -> Optional[int]:
        """Get days until subscription renewal"""
        if not self.current_period_end:
            return None
        delta = self.current_period_end - datetime.utcnow()
        return max(0, delta.days)
    
    def to_dict(self) -> dict:
        """Convert subscription to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "plan_id": self.plan_id,
            "status": self.status,
            "billing_cycle": self.billing_cycle,
            "price_cents": self.price_cents,
            "currency": self.currency,
            "current_period_start": self.current_period_start.isoformat() if self.current_period_start else None,
            "current_period_end": self.current_period_end.isoformat() if self.current_period_end else None,
            "trial_start": self.trial_start.isoformat() if self.trial_start else None,
            "trial_end": self.trial_end.isoformat() if self.trial_end else None,
            "canceled_at": self.canceled_at.isoformat() if self.canceled_at else None,
            "stripe_subscription_id": self.stripe_subscription_id,
            "stripe_customer_id": self.stripe_customer_id,
            "api_tokens_used": self.api_tokens_used,
            "projects_created": self.projects_created,
            "subscription_metadata": self.subscription_metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "is_trialing": self.is_trialing,
            "days_until_renewal": self.days_until_renewal
        }
