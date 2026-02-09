"""
Persistent Content Cache Service

Provides PostgreSQL-backed caching for blog content generation results to survive server restarts
and provide better cache management across multiple instances.
"""

import hashlib
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from services.database import get_user_data_db_session

Base = declarative_base()


class ContentCacheEntry(Base):
    """Model for content cache entries."""
    __tablename__ = "content_cache_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(255), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True, index=True)
    is_expired = Column(Boolean, default=False, nullable=False)
    
    __table_args__ = (
        Index('idx_content_cache_expires', 'expires_at'),
        Index('idx_content_cache_key', 'cache_key'),
    )


class PersistentContentCache:
    """PostgreSQL-backed cache for blog content generation results with exact parameter matching."""
    
    def __init__(self, max_cache_size: int = 300, cache_ttl_hours: int = 72):
        """
        Initialize persistent content cache.
        
        Args:
            max_cache_size: Maximum number of cached entries
            cache_ttl_hours: Time-to-live for cache entries in hours (longer than research cache since content is expensive)
        """
        self.max_cache_size = max_cache_size
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self.logger = logger.bind(cache="content")
        
        # Ensure table exists
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Ensure cache table exists in database."""
        try:
            with get_user_data_db_session() as session:
                ContentCacheEntry.__table__.create(session.bind, checkfirst=True)
                session.commit()
        except Exception as e:
            self.logger.error(f"Failed to create content cache table: {e}")
    
    def _generate_cache_key(self, prompt: str, additional_params: Dict[str, Any] = None) -> str:
        """Generate a deterministic cache key based on prompt and additional parameters."""
        cache_data = {
            "prompt": prompt,
            "params": additional_params or {}
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_string.encode()).hexdigest()
    
    def get(self, prompt: str, additional_params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached content if available and not expired.
        
        Args:
            prompt: The content generation prompt
            additional_params: Additional parameters that affect content generation
            
        Returns:
            Cached content dict or None if not found/expired
        """
        try:
            cache_key = self._generate_cache_key(prompt, additional_params)
            
            with get_user_data_db_session() as session:
                entry = session.query(ContentCacheEntry).filter(
                    ContentCacheEntry.cache_key == cache_key,
                    ContentCacheEntry.is_expired == False
                ).first()
                
                if entry:
                    # Check if expired
                    if entry.expires_at and datetime.utcnow() > entry.expires_at:
                        entry.is_expired = True
                        session.commit()
                        return None
                    
                    # Update access time and return cached content
                    metadata = json.loads(entry.metadata_json) if entry.metadata_json else {}
                    
                    self.logger.debug(f"Cache hit for key: {cache_key[:16]}...")
                    return {
                        "content": entry.content,
                        "metadata": metadata,
                        "cached_at": entry.created_at.isoformat(),
                        "expires_at": entry.expires_at.isoformat() if entry.expires_at else None
                    }
                
                self.logger.debug(f"Cache miss for key: {cache_key[:16]}...")
                return None
                
        except Exception as e:
            self.logger.error(f"Error retrieving from content cache: {e}")
            return None
    
    def set(self, prompt: str, content: str, additional_params: Dict[str, Any] = None, metadata: Dict[str, Any] = None) -> bool:
        """
        Store content in cache with expiration.
        
        Args:
            prompt: The content generation prompt
            content: Generated content to cache
            additional_params: Additional parameters that affect content generation
            metadata: Additional metadata to store with content
            
        Returns:
            True if successfully cached, False otherwise
        """
        try:
            cache_key = self._generate_cache_key(prompt, additional_params)
            expires_at = datetime.utcnow() + self.cache_ttl
            
            with get_user_data_db_session() as session:
                # Check if entry already exists
                existing = session.query(ContentCacheEntry).filter(
                    ContentCacheEntry.cache_key == cache_key
                ).first()
                
                if existing:
                    # Update existing entry
                    existing.content = content
                    existing.metadata_json = json.dumps(metadata) if metadata else None
                    existing.expires_at = expires_at
                    existing.is_expired = False
                    existing.created_at = datetime.utcnow()
                else:
                    # Create new entry
                    new_entry = ContentCacheEntry(
                        cache_key=cache_key,
                        content=content,
                        metadata_json=json.dumps(metadata) if metadata else None,
                        expires_at=expires_at
                    )
                    session.add(new_entry)
                
                session.commit()
                
                # Clean up old entries if cache is full
                self._cleanup_old_entries(session)
                session.commit()
                
                self.logger.debug(f"Cached content for key: {cache_key[:16]}...")
                return True
                
        except Exception as e:
            self.logger.error(f"Error storing in content cache: {e}")
            return False
    
    def _cleanup_old_entries(self, session):
        """Remove old entries to maintain cache size limit."""
        try:
            # Count total entries
            total_count = session.query(ContentCacheEntry).count()
            
            if total_count > self.max_cache_size:
                # Get oldest entries to remove
                entries_to_remove = session.query(ContentCacheEntry).order_by(
                    ContentCacheEntry.created_at
                ).limit(total_count - self.max_cache_size).all()
                
                for entry in entries_to_remove:
                    session.delete(entry)
                
                self.logger.info(f"Cleaned up {len(entries_to_remove)} old cache entries")
                
            # Also remove expired entries
            expired_count = session.query(ContentCacheEntry).filter(
                ContentCacheEntry.expires_at < datetime.utcnow(),
                ContentCacheEntry.is_expired == False
            ).update({"is_expired": True})
            
            if expired_count > 0:
                self.logger.info(f"Marked {expired_count} entries as expired")
                
        except Exception as e:
            self.logger.error(f"Error during cache cleanup: {e}")
    
    def clear(self) -> bool:
        """Clear all entries from cache."""
        try:
            with get_user_data_db_session() as session:
                deleted_count = session.query(ContentCacheEntry).count()
                session.query(ContentCacheEntry).delete()
                session.commit()
                
                self.logger.info(f"Cleared {deleted_count} entries from content cache")
                return True
                
        except Exception as e:
            self.logger.error(f"Error clearing content cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            with get_user_data_db_session() as session:
                total_entries = session.query(ContentCacheEntry).count()
                expired_entries = session.query(ContentCacheEntry).filter(
                    ContentCacheEntry.is_expired == True
                ).count()
                valid_entries = total_entries - expired_entries
                
                return {
                    "total_entries": total_entries,
                    "valid_entries": valid_entries,
                    "expired_entries": expired_entries,
                    "max_cache_size": self.max_cache_size,
                    "cache_ttl_hours": self.cache_ttl.total_seconds() / 3600,
                    "utilization": (total_entries / self.max_cache_size) * 100 if self.max_cache_size > 0 else 0
                }
                
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {e}")
            return {
                "error": str(e),
                "total_entries": 0,
                "valid_entries": 0,
                "expired_entries": 0,
                "max_cache_size": self.max_cache_size,
                "cache_ttl_hours": self.cache_ttl.total_seconds() / 3600,
                "utilization": 0
            }
