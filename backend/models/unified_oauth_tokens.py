"""
Unified OAuth Token Model - PostgreSQL Storage

Provides a unified table for storing OAuth tokens across all platforms,
eliminating the need for separate provider-specific tables.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    Index,
    UniqueConstraint,
    func
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any
import json

Base = declarative_base()


class UnifiedOAuthToken(Base):
    """Unified OAuth token storage for all platforms."""
    
    __tablename__ = "unified_oauth_tokens"
    
    # Primary composite key
    provider_id = Column(String(50), primary_key=True, nullable=False)
    user_id = Column(String(255), primary_key=True, nullable=False)
    
    # Token data
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_type = Column(String(50), default="bearer")
    expires_at = Column(DateTime, nullable=True, index=True)
    scope = Column(Text, nullable=True)
    
    # Account information
    account_id = Column(String(255), nullable=True, index=True)
    account_email = Column(String(255), nullable=True)
    account_name = Column(String(255), nullable=True)
    
    # Metadata and lifecycle
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    last_refreshed_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint('provider_id', 'user_id', name='uq_provider_user'),
        Index('idx_unified_oauth_provider_user', 'provider_id', 'user_id'),
        Index('idx_unified_oauth_user', 'user_id'),
        Index('idx_unified_oauth_expires', 'expires_at'),
        Index('idx_unified_oauth_active', 'is_active'),
        Index('idx_unified_oauth_account', 'account_id'),
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get metadata as dictionary."""
        if self.metadata_json:
            try:
                return json.loads(self.metadata_json)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    @metadata.setter
    def metadata(self, value: Dict[str, Any]):
        """Set metadata from dictionary."""
        if value:
            self.metadata_json = json.dumps(value)
        else:
            self.metadata_json = None
    
    def is_expired(self) -> bool:
        """Check if token is expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def needs_refresh(self, buffer_minutes: int = 30) -> bool:
        """Check if token needs refresh within buffer time."""
        if not self.expires_at or not self.refresh_token:
            return False
        
        buffer_time = datetime.utcnow() + timedelta(minutes=buffer_minutes)
        return self.expires_at <= buffer_time
    
    def to_connection_status(self) -> 'ConnectionStatus':
        """Convert to standardized ConnectionStatus."""
        from services.integrations.base import ConnectionStatus
        
        return ConnectionStatus(
            connected=self.is_active and not self.is_expired(),
            provider_id=self.provider_id,
            user_id=self.user_id,
            expires_at=self.expires_at,
            refreshable=bool(self.refresh_token),
            last_checked=self.last_refreshed_at or self.updated_at,
            warnings=self._get_warnings(),
            details={
                'account_id': self.account_id,
                'account_email': self.account_email,
                'account_name': self.account_name,
                'token_type': self.token_type,
                'scope': self.scope,
                'metadata': self.metadata
            }
        )
    
    def _get_warnings(self) -> list:
        """Get warnings for this token."""
        warnings = []
        
        if self.is_expired():
            warnings.append("Token has expired")
        
        if self.needs_refresh():
            warnings.append("Token will expire soon and needs refresh")
        
        if not self.refresh_token and self.expires_at:
            warnings.append("No refresh token available - manual re-auth required")
        
        if not self.is_active:
            warnings.append("Token is inactive")
        
        return warnings


# Migration helper functions
def migrate_provider_tokens_to_unified(session, provider_id: str, provider_model_class, token_mapping_func):
    """
    Migrate tokens from provider-specific table to unified table.
    
    Args:
        session: Database session
        provider_id: Provider identifier (e.g., 'gsc', 'bing', 'wordpress', 'wix')
        provider_model_class: SQLAlchemy model class for provider tokens
        token_mapping_func: Function to convert provider token to unified format
    """
    from loguru import logger
    
    try:
        # Get existing provider tokens
        provider_tokens = session.query(provider_model_class).all()
        migrated_count = 0
        
        for provider_token in provider_tokens:
            # Check if already migrated
            existing = session.query(UnifiedOAuthToken).filter(
                UnifiedOAuthToken.provider_id == provider_id,
                UnifiedOAuthToken.user_id == provider_token.user_id
            ).first()
            
            if existing:
                logger.debug(f"Token already migrated for {provider_id}:{provider_token.user_id}")
                continue
            
            # Convert to unified format
            unified_token = token_mapping_func(provider_token, provider_id)
            if unified_token:
                session.add(unified_token)
                migrated_count += 1
                logger.info(f"Migrated {provider_id} token for user {provider_token.user_id}")
        
        session.commit()
        logger.info(f"Migration complete: {migrated_count} {provider_id} tokens migrated")
        return migrated_count
        
    except Exception as e:
        logger.error(f"Migration failed for {provider_id}: {e}")
        session.rollback()
        return 0


def create_unified_tokens_table():
    """Create the unified tokens table if it doesn't exist."""
    from services.database import get_platform_db_session
    
    try:
        with get_platform_db_session() as session:
            UnifiedOAuthToken.__table__.create(session.bind, checkfirst=True)
            session.commit()
            logger.info("Unified OAuth tokens table created successfully")
    except Exception as e:
        logger.error(f"Failed to create unified tokens table: {e}")
        raise
