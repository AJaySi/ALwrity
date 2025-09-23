"""
Persistent Outline Cache Service

Provides database-backed caching for outline generation results to survive server restarts
and provide better cache management across multiple instances.
"""

import hashlib
import json
import sqlite3
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger


class PersistentOutlineCache:
    """Database-backed cache for outline generation results with exact parameter matching."""
    
    def __init__(self, db_path: str = "outline_cache.db", max_cache_size: int = 500, cache_ttl_hours: int = 48):
        """
        Initialize the persistent outline cache.
        
        Args:
            db_path: Path to SQLite database file
            max_cache_size: Maximum number of cached entries
            cache_ttl_hours: Time-to-live for cache entries in hours (longer than research cache)
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
                CREATE TABLE IF NOT EXISTS outline_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    keywords TEXT NOT NULL,
                    industry TEXT NOT NULL,
                    target_audience TEXT NOT NULL,
                    word_count INTEGER NOT NULL,
                    custom_instructions TEXT,
                    persona_data TEXT,
                    result_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_outline_cache_key ON outline_cache(cache_key)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_outline_expires_at ON outline_cache(expires_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_outline_created_at ON outline_cache(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_outline_keywords ON outline_cache(keywords)")
            
            conn.commit()
    
    def _generate_cache_key(self, keywords: List[str], industry: str, target_audience: str, 
                           word_count: int, custom_instructions: str = None, persona_data: Dict = None) -> str:
        """
        Generate a cache key based on exact parameter match.
        
        Args:
            keywords: List of research keywords
            industry: Industry context
            target_audience: Target audience context
            word_count: Target word count for outline
            custom_instructions: Custom instructions for outline generation
            persona_data: Persona information
            
        Returns:
            MD5 hash of the normalized parameters
        """
        # Normalize and sort keywords for consistent hashing
        normalized_keywords = sorted([kw.lower().strip() for kw in keywords])
        normalized_industry = industry.lower().strip() if industry else "general"
        normalized_audience = target_audience.lower().strip() if target_audience else "general"
        normalized_instructions = custom_instructions.lower().strip() if custom_instructions else ""
        
        # Normalize persona data
        normalized_persona = ""
        if persona_data:
            # Sort persona keys and values for consistent hashing
            persona_str = json.dumps(persona_data, sort_keys=True, default=str)
            normalized_persona = persona_str.lower()
        
        # Create a consistent string representation
        cache_string = f"{normalized_keywords}|{normalized_industry}|{normalized_audience}|{word_count}|{normalized_instructions}|{normalized_persona}"
        
        # Generate MD5 hash
        return hashlib.md5(cache_string.encode('utf-8')).hexdigest()
    
    def _cleanup_expired_entries(self):
        """Remove expired cache entries from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM outline_cache WHERE expires_at < ?",
                (datetime.now().isoformat(),)
            )
            deleted_count = cursor.rowcount
            if deleted_count > 0:
                logger.debug(f"Removed {deleted_count} expired outline cache entries")
            conn.commit()
    
    def _evict_oldest_entries(self, num_to_evict: int):
        """Evict the oldest cache entries when cache is full."""
        with sqlite3.connect(self.db_path) as conn:
            # Get oldest entries by creation time
            cursor = conn.execute("""
                SELECT id FROM outline_cache 
                ORDER BY created_at ASC 
                LIMIT ?
            """, (num_to_evict,))
            
            old_ids = [row[0] for row in cursor.fetchall()]
            
            if old_ids:
                placeholders = ','.join(['?' for _ in old_ids])
                conn.execute(f"DELETE FROM outline_cache WHERE id IN ({placeholders})", old_ids)
                logger.debug(f"Evicted {len(old_ids)} oldest outline cache entries")
            
            conn.commit()
    
    def get_cached_outline(self, keywords: List[str], industry: str, target_audience: str, 
                          word_count: int, custom_instructions: str = None, persona_data: Dict = None) -> Optional[Dict[str, Any]]:
        """
        Get cached outline result for exact parameter match.
        
        Args:
            keywords: List of research keywords
            industry: Industry context
            target_audience: Target audience context
            word_count: Target word count for outline
            custom_instructions: Custom instructions for outline generation
            persona_data: Persona information
            
        Returns:
            Cached outline result if found and valid, None otherwise
        """
        cache_key = self._generate_cache_key(keywords, industry, target_audience, word_count, custom_instructions, persona_data)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT result_data, expires_at FROM outline_cache 
                WHERE cache_key = ? AND expires_at > ?
            """, (cache_key, datetime.now().isoformat()))
            
            row = cursor.fetchone()
            
            if row is None:
                logger.debug(f"Outline cache miss for keywords: {keywords}, word_count: {word_count}")
                return None
            
            # Update access statistics
            conn.execute("""
                UPDATE outline_cache 
                SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                WHERE cache_key = ?
            """, (cache_key,))
            conn.commit()
            
            try:
                result_data = json.loads(row[0])
                logger.info(f"Outline cache hit for keywords: {keywords}, word_count: {word_count} (saved expensive generation)")
                return result_data
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in outline cache for keywords: {keywords}")
                # Remove invalid entry
                conn.execute("DELETE FROM outline_cache WHERE cache_key = ?", (cache_key,))
                conn.commit()
                return None
    
    def cache_outline(self, keywords: List[str], industry: str, target_audience: str, 
                     word_count: int, custom_instructions: str, persona_data: Dict, result: Dict[str, Any]):
        """
        Cache an outline generation result.
        
        Args:
            keywords: List of research keywords
            industry: Industry context
            target_audience: Target audience context
            word_count: Target word count for outline
            custom_instructions: Custom instructions for outline generation
            persona_data: Persona information
            result: Outline result to cache
        """
        cache_key = self._generate_cache_key(keywords, industry, target_audience, word_count, custom_instructions, persona_data)
        
        # Cleanup expired entries first
        self._cleanup_expired_entries()
        
        # Check if cache is full and evict if necessary
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM outline_cache")
            current_count = cursor.fetchone()[0]
            
            if current_count >= self.max_cache_size:
                num_to_evict = current_count - self.max_cache_size + 1
                self._evict_oldest_entries(num_to_evict)
        
        # Store the result
        expires_at = datetime.now() + self.cache_ttl
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO outline_cache 
                (cache_key, keywords, industry, target_audience, word_count, custom_instructions, persona_data, result_data, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cache_key,
                json.dumps(keywords),
                industry,
                target_audience,
                word_count,
                custom_instructions or "",
                json.dumps(persona_data) if persona_data else "",
                json.dumps(result),
                expires_at.isoformat()
            ))
            conn.commit()
        
        logger.info(f"Cached outline result for keywords: {keywords}, word_count: {word_count}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        self._cleanup_expired_entries()
        
        with sqlite3.connect(self.db_path) as conn:
            # Get basic stats
            cursor = conn.execute("SELECT COUNT(*) FROM outline_cache")
            total_entries = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM outline_cache WHERE expires_at > ?", (datetime.now().isoformat(),))
            valid_entries = cursor.fetchone()[0]
            
            # Get most accessed entries
            cursor = conn.execute("""
                SELECT keywords, industry, target_audience, word_count, access_count, created_at
                FROM outline_cache 
                ORDER BY access_count DESC 
                LIMIT 10
            """)
            top_entries = [
                {
                    'keywords': json.loads(row[0]),
                    'industry': row[1],
                    'target_audience': row[2],
                    'word_count': row[3],
                    'access_count': row[4],
                    'created_at': row[5]
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
            conn.execute("DELETE FROM outline_cache")
            conn.commit()
        logger.info("Outline cache cleared")
    
    def get_cache_entries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent cache entries for debugging."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT keywords, industry, target_audience, word_count, custom_instructions, created_at, expires_at, access_count
                FROM outline_cache 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            return [
                {
                    'keywords': json.loads(row[0]),
                    'industry': row[1],
                    'target_audience': row[2],
                    'word_count': row[3],
                    'custom_instructions': row[4],
                    'created_at': row[5],
                    'expires_at': row[6],
                    'access_count': row[7]
                }
                for row in cursor.fetchall()
            ]
    
    def invalidate_cache_for_keywords(self, keywords: List[str]):
        """
        Invalidate all cache entries for specific keywords.
        Useful when research data is updated.
        
        Args:
            keywords: Keywords to invalidate cache for
        """
        normalized_keywords = sorted([kw.lower().strip() for kw in keywords])
        keywords_json = json.dumps(normalized_keywords)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM outline_cache WHERE keywords = ?", (keywords_json,))
            deleted_count = cursor.rowcount
            conn.commit()
        
        if deleted_count > 0:
            logger.info(f"Invalidated {deleted_count} outline cache entries for keywords: {keywords}")


# Global persistent cache instance
persistent_outline_cache = PersistentOutlineCache()
