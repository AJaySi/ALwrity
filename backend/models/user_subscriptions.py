"""
User Subscription Models - Platform Database
Subscription management and billing for ALwrity SaaS platform.
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional
import uuid
import enum

from models.ssot_bases import PlatformBase

Base = PlatformBase


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
            self.status == SubscriptionStatus.ACTIVE.value
            and self.current_period_end > datetime.utcnow()
        )

    @property
    def is_trialing(self) -> bool:
        """Check if subscription is in trial period"""
        return (
            self.status == SubscriptionStatus.TRIALING.value
            and self.trial_end
            and self.trial_end > datetime.utcnow()
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
            "days_until_renewal": self.days_until_renewal,
        }
