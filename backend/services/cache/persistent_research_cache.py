"""
Persistent Research Cache Service

Provides database-backed caching for research results to survive server restarts
and provide better cache management across multiple instances.
"""

import hashlib
import json
import sqlite3
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger


class PersistentResearchCache:
    """Database-backed cache for research results with exact keyword matching."""
    
    def __init__(self, db_path: str = "research_cache.db", max_cache_size: int = 1000, cache_ttl_hours: int = 24):
        """
        Initialize the persistent research cache.
        
        Args:
            db_path: Path to SQLite database file
            max_cache_size: Maximum number of cached entries
            cache_ttl_hours: Time-to-live for cache entries in hours
        """
        self.db_path = db_path
        self.max_cache_size = max_cache_size
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        
        # Ensure database directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS research_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    keywords TEXT NOT NULL,
                    industry TEXT NOT NULL,
                    target_audience TEXT NOT NULL,
                    result_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_key ON research_cache(cache_key)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON research_cache(expires_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON research_cache(created_at)")
            
            conn.commit()
    
    def _generate_cache_key(self, keywords: List[str], industry: str, target_audience: str) -> str:
        """
        Generate a cache key based on exact keyword match.
        
        Args:
            keywords: List of research keywords
            industry: Industry context
            target_audience: Target audience context
            
        Returns:
            MD5 hash of the normalized parameters
        """
        # Normalize and sort keywords for consistent hashing
        normalized_keywords = sorted([kw.lower().strip() for kw in keywords])
        normalized_industry = industry.lower().strip() if industry else "general"
        normalized_audience = target_audience.lower().strip() if target_audience else "general"
        
        # Create a consistent string representation
        cache_string = f"{normalized_keywords}|{normalized_industry}|{normalized_audience}"
        
        # Generate MD5 hash
        return hashlib.md5(cache_string.encode('utf-8')).hexdigest()
    
    def _cleanup_expired_entries(self):
        """Remove expired cache entries from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM research_cache WHERE expires_at < ?",
                (datetime.now().isoformat(),)
            )
            deleted_count = cursor.rowcount
            if deleted_count > 0:
                logger.debug(f"Removed {deleted_count} expired cache entries")
            conn.commit()
    
    def _evict_oldest_entries(self, num_to_evict: int):
        """Evict the oldest cache entries when cache is full."""
        with sqlite3.connect(self.db_path) as conn:
            # Get oldest entries by creation time
            cursor = conn.execute("""
                SELECT id FROM research_cache 
                ORDER BY created_at ASC 
                LIMIT ?
            """, (num_to_evict,))
            
            old_ids = [row[0] for row in cursor.fetchall()]
            
            if old_ids:
                placeholders = ','.join(['?' for _ in old_ids])
                conn.execute(f"DELETE FROM research_cache WHERE id IN ({placeholders})", old_ids)
                logger.debug(f"Evicted {len(old_ids)} oldest cache entries")
            
            conn.commit()
    
    def get_cached_result(self, keywords: List[str], industry: str, target_audience: str) -> Optional[Dict[str, Any]]:
        """
        Get cached research result for exact keyword match.
        
        Args:
            keywords: List of research keywords
            industry: Industry context
            target_audience: Target audience context
            
        Returns:
            Cached research result if found and valid, None otherwise
        """
        cache_key = self._generate_cache_key(keywords, industry, target_audience)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT result_data, expires_at FROM research_cache 
                WHERE cache_key = ? AND expires_at > ?
            """, (cache_key, datetime.now().isoformat()))
            
            row = cursor.fetchone()
            
            if row is None:
                logger.debug(f"Cache miss for keywords: {keywords}")
                return None
            
            # Update access statistics
            conn.execute("""
                UPDATE research_cache 
                SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                WHERE cache_key = ?
            """, (cache_key,))
            conn.commit()
            
            try:
                result_data = json.loads(row[0])
                logger.info(f"Cache hit for keywords: {keywords} (saved API call)")
                return result_data
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in cache for keywords: {keywords}")
                # Remove invalid entry
                conn.execute("DELETE FROM research_cache WHERE cache_key = ?", (cache_key,))
                conn.commit()
                return None
    
    def cache_result(self, keywords: List[str], industry: str, target_audience: str, result: Dict[str, Any]):
        """
        Cache a research result.
        
        Args:
            keywords: List of research keywords
            industry: Industry context
            target_audience: Target audience context
            result: Research result to cache
        """
        cache_key = self._generate_cache_key(keywords, industry, target_audience)
        
        # Cleanup expired entries first
        self._cleanup_expired_entries()
        
        # Check if cache is full and evict if necessary
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM research_cache")
            current_count = cursor.fetchone()[0]
            
            if current_count >= self.max_cache_size:
                num_to_evict = current_count - self.max_cache_size + 1
                self._evict_oldest_entries(num_to_evict)
        
        # Store the result
        expires_at = datetime.now() + self.cache_ttl
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO research_cache 
                (cache_key, keywords, industry, target_audience, result_data, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                cache_key,
                json.dumps(keywords),
                industry,
                target_audience,
                json.dumps(result),
                expires_at.isoformat()
            ))
            conn.commit()
        
        logger.info(f"Cached research result for keywords: {keywords}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        self._cleanup_expired_entries()
        
        with sqlite3.connect(self.db_path) as conn:
            # Get basic stats
            cursor = conn.execute("SELECT COUNT(*) FROM research_cache")
            total_entries = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM research_cache WHERE expires_at > ?", (datetime.now().isoformat(),))
            valid_entries = cursor.fetchone()[0]
            
            # Get most accessed entries
            cursor = conn.execute("""
                SELECT keywords, industry, target_audience, access_count, created_at
                FROM research_cache 
                ORDER BY access_count DESC 
                LIMIT 10
            """)
            top_entries = [
                {
                    'keywords': json.loads(row[0]),
                    'industry': row[1],
                    'target_audience': row[2],
                    'access_count': row[3],
                    'created_at': row[4]
                }
                for row in cursor.fetchall()
            ]
            
            # Get database size
            cursor = conn.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            db_size_bytes = cursor.fetchone()[0]
            db_size_mb = db_size_bytes / (1024 * 1024)
        
        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'expired_entries': total_entries - valid_entries,
            'max_size': self.max_cache_size,
            'ttl_hours': self.cache_ttl.total_seconds() / 3600,
            'database_size_mb': round(db_size_mb, 2),
            'top_accessed_entries': top_entries
        }
    
    def clear_cache(self):
        """Clear all cached entries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM research_cache")
            conn.commit()
        logger.info("Research cache cleared")
    
    def get_cache_entries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent cache entries for debugging."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT keywords, industry, target_audience, created_at, expires_at, access_count
                FROM research_cache 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            return [
                {
                    'keywords': json.loads(row[0]),
                    'industry': row[1],
                    'target_audience': row[2],
                    'created_at': row[3],
                    'expires_at': row[4],
                    'access_count': row[5]
                }
                for row in cursor.fetchall()
            ]


# Global persistent cache instance
persistent_research_cache = PersistentResearchCache()
