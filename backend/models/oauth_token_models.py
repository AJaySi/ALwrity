"""
OAuth Token and Integration Models - Platform Database
Stores OAuth tokens, states, and WordPress integration data.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    func,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class GscCredential(Base):
    __tablename__ = "gsc_credentials"

    user_id = Column(String(255), primary_key=True)
    credentials_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class GscDataCache(Base):
    __tablename__ = "gsc_data_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    site_url = Column(String(500), nullable=False)
    data_type = Column(String(100), nullable=False)
    data_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False, index=True)


class GscOauthState(Base):
    __tablename__ = "gsc_oauth_states"

    state = Column(String(255), primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())


class BingOAuthToken(Base):
    __tablename__ = "bing_oauth_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_type = Column(String(50), default="bearer")
    expires_at = Column(DateTime, nullable=True, index=True)
    scope = Column(Text, nullable=True)
    site_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)


class BingOauthState(Base):
    __tablename__ = "bing_oauth_states"

    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(String(255), nullable=False, unique=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True, index=True)


class WordPressOAuthToken(Base):
    __tablename__ = "wordpress_oauth_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_type = Column(String(50), default="bearer")
    expires_at = Column(DateTime, nullable=True, index=True)
    scope = Column(Text, nullable=True)
    blog_id = Column(String(255), nullable=True)
    blog_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)


class WordPressOauthState(Base):
    __tablename__ = "wordpress_oauth_states"

    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(String(255), nullable=False, unique=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True, index=True)


class WixOAuthToken(Base):
    __tablename__ = "wix_oauth_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_type = Column(String(50), default="bearer")
    expires_at = Column(DateTime, nullable=True, index=True)
    expires_in = Column(Integer, nullable=True)
    scope = Column(Text, nullable=True)
    site_id = Column(String(255), nullable=True)
    member_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)


class WordPressSite(Base):
    __tablename__ = "wordpress_sites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    site_url = Column(String(500), nullable=False)
    site_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=False)
    app_password = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "site_url", name="uq_wordpress_sites_user_site"),
    )


class WordPressPost(Base):
    __tablename__ = "wordpress_posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    site_id = Column(Integer, ForeignKey("wordpress_sites.id"), nullable=False, index=True)
    wp_post_id = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)
    status = Column(String(50), default="draft")
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
