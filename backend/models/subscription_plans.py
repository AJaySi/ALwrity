"""
Subscription Plans Models - Platform Database
Available subscription tiers and pricing for ALwrity SaaS platform.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text, Float, Numeric
from sqlalchemy.orm import relationship
from models.ssot_bases import PlatformBase
from datetime import datetime
from typing import Optional
import uuid

Base = PlatformBase

class SubscriptionPlan(Base):
    """
    Available subscription plans and pricing tiers.
    Platform database table for subscription management.
    """
    __tablename__ = "subscription_plans"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Plan identification
    plan_id = Column(String, unique=True, nullable=False, index=True)  # free, basic, pro, enterprise
    name = Column(String, nullable=False)  # Free Plan, Basic Plan, Pro Plan, Enterprise Plan
    description = Column(Text, nullable=True)
    
    # Pricing information
    price_monthly = Column(Numeric(10, 2), nullable=False)  # Monthly price in USD
    price_yearly = Column(Numeric(10, 2), nullable=True)   # Yearly price (optional)
    currency = Column(String, default="USD")
    
    # Plan limits and features
    limits = Column(JSON, default={})  # Usage limits (AI credits, storage, etc.)
    features = Column(JSON, default=[])  # Available features list
    
    # Plan status
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)  # Visible to users
    sort_order = Column(Integer, default=0)  # Display order
    
    # Billing configuration
    billing_interval = Column(String, default="monthly")  # monthly, yearly
    trial_days = Column(Integer, default=0)  # Trial period days
    
    # Integration settings
    stripe_price_id_monthly = Column(String, nullable=True)  # Stripe price ID for monthly
    stripe_price_id_yearly = Column(String, nullable=True)   # Stripe price ID for yearly
    
    # Additional plan data
    extra_data = Column(JSON, default={})  # Additional plan data
    
    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="plan")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SubscriptionPlan(plan_id='{self.plan_id}', name='{self.name}', price_monthly={self.price_monthly})>"
    
    def to_dict(self):
        """Convert plan to dictionary for API responses."""
        return {
            "id": self.id,
            "plan_id": self.plan_id,
            "name": self.name,
            "description": self.description,
            "price_monthly": float(self.price_monthly) if self.price_monthly else None,
            "price_yearly": float(self.price_yearly) if self.price_yearly else None,
            "currency": self.currency,
            "limits": self.limits or {},
            "features": self.features or [],
            "is_active": self.is_active,
            "is_public": self.is_public,
            "trial_days": self.trial_days,
            "billing_interval": self.billing_interval,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
