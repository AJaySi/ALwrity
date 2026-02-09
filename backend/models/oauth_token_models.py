"""
OAuth Token Models
SQLAlchemy models for OAuth token storage in PostgreSQL.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean

from models.enhanced_strategy_models import Base


class BingOAuthToken(Base):
    """OAuth tokens for Bing Webmaster Tools."""

    __tablename__ = "bing_oauth_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_type = Column(String(50), default="bearer")
    expires_at = Column(DateTime, nullable=True)
    scope = Column(Text, nullable=True)
    site_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class WordPressOAuthToken(Base):
    """OAuth tokens for WordPress.com."""

    __tablename__ = "wordpress_oauth_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_type = Column(String(50), default="bearer")
    expires_at = Column(DateTime, nullable=True)
    scope = Column(Text, nullable=True)
    blog_id = Column(Text, nullable=True)
    blog_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class WixOAuthToken(Base):
    """OAuth tokens for Wix."""

    __tablename__ = "wix_oauth_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_type = Column(String(50), default="bearer")
    expires_at = Column(DateTime, nullable=True)
    expires_in = Column(Integer, nullable=True)
    scope = Column(Text, nullable=True)
    site_id = Column(Text, nullable=True)
    member_id = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
