"""
Persistent Content Cache Service

Provides database-backed caching for blog content generation results to survive server restarts
and provide better cache management across multiple instances.
"""

import hashlib
import json
import sqlite3
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger


class PersistentContentCache:
    """Database-backed cache for blog content generation results with exact parameter matching."""
    
    def __init__(self, db_path: str = "content_cache.db", max_cache_size: int = 300, cache_ttl_hours: int = 72):
        """
        Initialize the persistent content cache.
        
        Args:
            db_path: Path to SQLite database file
            max_cache_size: Maximum number of cached entries
            cache_ttl_hours: Time-to-live for cache entries in hours (longer than research cache since content is expensive)
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
                CREATE TABLE IF NOT EXISTS content_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    sections_hash TEXT NOT NULL,
                    global_target_words INTEGER NOT NULL,
                    persona_data TEXT,
                    tone TEXT,
                    audience TEXT,
                    result_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_content_cache_key ON content_cache(cache_key)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_content_expires_at ON content_cache(expires_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_content_created_at ON content_cache(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_content_title ON content_cache(title)")
            
            conn.commit()
    
    def _generate_sections_hash(self, sections: List[Dict[str, Any]]) -> str:
        """
        Generate a hash for sections based on their structure and content.
        
        Args:
            sections: List of section dictionaries with outline information
            
        Returns:
            MD5 hash of the normalized sections
        """
        # Normalize sections for consistent hashing
        normalized_sections = []
        for section in sections:
            normalized_section = {
                'id': section.get('id', ''),
                'heading': section.get('heading', '').lower().strip(),
                'keyPoints': sorted([str(kp).lower().strip() for kp in section.get('keyPoints', [])]),
                'keywords': sorted([str(kw).lower().strip() for kw in section.get('keywords', [])]),
                'subheadings': sorted([str(sh).lower().strip() for sh in section.get('subheadings', [])]),
                'targetWords': section.get('targetWords', 0),
                # Don't include references in hash as they might vary but content should remain similar
            }
            normalized_sections.append(normalized_section)
        
        # Sort sections by id for consistent ordering
        normalized_sections.sort(key=lambda x: x['id'])
        
        # Generate hash
        sections_str = json.dumps(normalized_sections, sort_keys=True)
        return hashlib.md5(sections_str.encode('utf-8')).hexdigest()
    
    def _generate_cache_key(self, keywords: List[str], sections: List[Dict[str, Any]], 
                           global_target_words: int, persona_data: Dict = None, 
                           tone: str = None, audience: str = None) -> str:
        """
        Generate a cache key based on exact parameter match.
        
        Args:
            keywords: Original research keywords (primary cache key)
            sections: List of section dictionaries with outline information
            global_target_words: Target word count for entire blog
            persona_data: Persona information
            tone: Content tone
            audience: Target audience
            
        Returns:
            MD5 hash of the normalized parameters
        """
        # Normalize parameters
        normalized_keywords = sorted([kw.lower().strip() for kw in (keywords or [])])
        sections_hash = self._generate_sections_hash(sections)
        normalized_tone = tone.lower().strip() if tone else "professional"
        normalized_audience = audience.lower().strip() if audience else "general"
        
        # Normalize persona data
        normalized_persona = ""
        if persona_data:
            # Sort persona keys and values for consistent hashing
            persona_str = json.dumps(persona_data, sort_keys=True, default=str)
            normalized_persona = persona_str.lower()
        
        # Create a consistent string representation
        cache_string = f"{normalized_keywords}|{sections_hash}|{global_target_words}|{normalized_tone}|{normalized_audience}|{normalized_persona}"
        
        # Generate MD5 hash
        return hashlib.md5(cache_string.encode('utf-8')).hexdigest()
    
    def _cleanup_expired_entries(self):
        """Remove expired cache entries from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM content_cache WHERE expires_at < ?",
                (datetime.now().isoformat(),)
            )
            deleted_count = cursor.rowcount
            if deleted_count > 0:
                logger.debug(f"Removed {deleted_count} expired content cache entries")
            conn.commit()
    
    def _evict_oldest_entries(self, num_to_evict: int):
        """Evict the oldest cache entries when cache is full."""
        with sqlite3.connect(self.db_path) as conn:
            # Get oldest entries by creation time
            cursor = conn.execute("""
                SELECT id FROM content_cache 
                ORDER BY created_at ASC 
                LIMIT ?
            """, (num_to_evict,))
            
            old_ids = [row[0] for row in cursor.fetchall()]
            
            if old_ids:
                placeholders = ','.join(['?' for _ in old_ids])
                conn.execute(f"DELETE FROM content_cache WHERE id IN ({placeholders})", old_ids)
                logger.debug(f"Evicted {len(old_ids)} oldest content cache entries")
            
            conn.commit()
    
    def get_cached_content(self, keywords: List[str], sections: List[Dict[str, Any]], 
                          global_target_words: int, persona_data: Dict = None, 
                          tone: str = None, audience: str = None) -> Optional[Dict[str, Any]]:
        """
        Get cached content result for exact parameter match.
        
        Args:
            keywords: Original research keywords (primary cache key)
            sections: List of section dictionaries with outline information
            global_target_words: Target word count for entire blog
            persona_data: Persona information
            tone: Content tone
            audience: Target audience
            
        Returns:
            Cached content result if found and valid, None otherwise
        """
        cache_key = self._generate_cache_key(keywords, sections, global_target_words, persona_data, tone, audience)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT result_data, expires_at FROM content_cache 
                WHERE cache_key = ? AND expires_at > ?
            """, (cache_key, datetime.now().isoformat()))
            
            row = cursor.fetchone()
            
            if row is None:
                logger.debug(f"Content cache miss for keywords: {keywords}, sections: {len(sections)}")
                return None
            
            # Update access statistics
            conn.execute("""
                UPDATE content_cache 
                SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                WHERE cache_key = ?
            """, (cache_key,))
            conn.commit()
            
            try:
                result_data = json.loads(row[0])
                logger.info(f"Content cache hit for keywords: {keywords} (saved expensive generation)")
                return result_data
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in content cache for keywords: {keywords}")
                # Remove invalid entry
                conn.execute("DELETE FROM content_cache WHERE cache_key = ?", (cache_key,))
                conn.commit()
                return None
    
    def cache_content(self, keywords: List[str], sections: List[Dict[str, Any]], 
                     global_target_words: int, persona_data: Dict, tone: str, 
                     audience: str, result: Dict[str, Any]):
        """
        Cache a content generation result.
        
        Args:
            keywords: Original research keywords (primary cache key)
            sections: List of section dictionaries with outline information
            global_target_words: Target word count for entire blog
            persona_data: Persona information
            tone: Content tone
            audience: Target audience
            result: Content result to cache
        """
        cache_key = self._generate_cache_key(keywords, sections, global_target_words, persona_data, tone, audience)
        sections_hash = self._generate_sections_hash(sections)
        
        # Cleanup expired entries first
        self._cleanup_expired_entries()
        
        # Check if cache is full and evict if necessary
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM content_cache")
            current_count = cursor.fetchone()[0]
            
            if current_count >= self.max_cache_size:
                num_to_evict = current_count - self.max_cache_size + 1
                self._evict_oldest_entries(num_to_evict)
        
        # Store the result
        expires_at = datetime.now() + self.cache_ttl
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO content_cache 
                (cache_key, title, sections_hash, global_target_words, persona_data, tone, audience, result_data, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cache_key,
                json.dumps(keywords),  # Store keywords as JSON
                sections_hash,
                global_target_words,
                json.dumps(persona_data) if persona_data else "",
                tone or "",
                audience or "",
                json.dumps(result),
                expires_at.isoformat()
            ))
            conn.commit()
        
        logger.info(f"Cached content result for keywords: {keywords}, {len(sections)} sections")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        self._cleanup_expired_entries()
        
        with sqlite3.connect(self.db_path) as conn:
            # Get basic stats
            cursor = conn.execute("SELECT COUNT(*) FROM content_cache")
            total_entries = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM content_cache WHERE expires_at > ?", (datetime.now().isoformat(),))
            valid_entries = cursor.fetchone()[0]
            
            # Get most accessed entries
            cursor = conn.execute("""
                SELECT title, global_target_words, access_count, created_at
                FROM content_cache 
                ORDER BY access_count DESC 
                LIMIT 10
            """)
            top_entries = [
                {
                    'title': row[0],
                    'global_target_words': row[1],
                    'access_count': row[2],
                    'created_at': row[3]
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
            conn.execute("DELETE FROM content_cache")
            conn.commit()
        logger.info("Content cache cleared")
    
    def get_cache_entries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent cache entries for debugging."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT title, global_target_words, tone, audience, created_at, expires_at, access_count
                FROM content_cache 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            return [
                {
                    'title': row[0],
                    'global_target_words': row[1],
                    'tone': row[2],
                    'audience': row[3],
                    'created_at': row[4],
                    'expires_at': row[5],
                    'access_count': row[6]
                }
                for row in cursor.fetchall()
            ]
    
    def invalidate_cache_for_title(self, title: str):
        """
        Invalidate all cache entries for specific title.
        Useful when outline is updated.
        
        Args:
            title: Title to invalidate cache for
        """
        normalized_title = title.lower().strip()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM content_cache WHERE LOWER(title) = ?", (normalized_title,))
            deleted_count = cursor.rowcount
            conn.commit()
        
        if deleted_count > 0:
            logger.info(f"Invalidated {deleted_count} content cache entries for title: {title}")


# Global persistent cache instance
persistent_content_cache = PersistentContentCache()
