"""
WordPress Service for ALwrity
Handles WordPress site connections, content publishing, and media management.
"""

import os
import json
import sqlite3
import base64
import mimetypes
import tempfile
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
from PIL import Image
from loguru import logger


class WordPressService:
    """Main WordPress service class for managing WordPress integrations."""
    
    def __init__(self, db_path: str = "alwrity.db"):
        """Initialize WordPress service with database path."""
        self.db_path = db_path
        self.api_version = "v2"
        self._ensure_tables()
    
    def _ensure_tables(self) -> None:
        """Ensure required database tables exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # WordPress sites table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS wordpress_sites (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        site_url TEXT NOT NULL,
                        site_name TEXT,
                        username TEXT NOT NULL,
                        app_password TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, site_url)
                    )
                ''')
                
                # WordPress posts table for tracking published content
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS wordpress_posts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        site_id INTEGER NOT NULL,
                        wp_post_id INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        status TEXT DEFAULT 'draft',
                        published_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (site_id) REFERENCES wordpress_sites (id)
                    )
                ''')
                
                conn.commit()
                logger.info("WordPress database tables ensured")
                
        except Exception as e:
            logger.error(f"Error ensuring WordPress tables: {e}")
            raise
    
    def add_site(self, user_id: str, site_url: str, site_name: str, username: str, app_password: str) -> bool:
        """Add a new WordPress site connection."""
        try:
            # Validate site URL format
            if not site_url.startswith(('http://', 'https://')):
                site_url = f"https://{site_url}"
            
            # Test connection before saving
            if not self._test_connection(site_url, username, app_password):
                logger.error(f"Failed to connect to WordPress site: {site_url}")
                return False
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO wordpress_sites 
                    (user_id, site_url, site_name, username, app_password, updated_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, site_url, site_name, username, app_password))
                conn.commit()
            
            logger.info(f"WordPress site added for user {user_id}: {site_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding WordPress site: {e}")
            return False
    
    def get_user_sites(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all WordPress sites for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, site_url, site_name, username, is_active, created_at, updated_at
                    FROM wordpress_sites 
                    WHERE user_id = ? AND is_active = 1
                    ORDER BY updated_at DESC
                ''', (user_id,))
                
                sites = []
                for row in cursor.fetchall():
                    sites.append({
                        'id': row[0],
                        'site_url': row[1],
                        'site_name': row[2],
                        'username': row[3],
                        'is_active': bool(row[4]),
                        'created_at': row[5],
                        'updated_at': row[6]
                    })
                
                logger.info(f"Retrieved {len(sites)} WordPress sites for user {user_id}")
                return sites
                
        except Exception as e:
            logger.error(f"Error getting WordPress sites for user {user_id}: {e}")
            return []
    
    def get_site_credentials(self, site_id: int) -> Optional[Dict[str, str]]:
        """Get credentials for a specific WordPress site."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT site_url, username, app_password
                    FROM wordpress_sites 
                    WHERE id = ? AND is_active = 1
                ''', (site_id,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        'site_url': result[0],
                        'username': result[1],
                        'app_password': result[2]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error getting credentials for site {site_id}: {e}")
            return None
    
    def _test_connection(self, site_url: str, username: str, app_password: str) -> bool:
        """Test WordPress site connection."""
        try:
            # Test with a simple API call
            api_url = f"{site_url}/wp-json/wp/v2/users/me"
            response = requests.get(api_url, auth=HTTPBasicAuth(username, app_password), timeout=10)
            
            if response.status_code == 200:
                logger.info(f"WordPress connection test successful for {site_url}")
                return True
            else:
                logger.warning(f"WordPress connection test failed for {site_url}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"WordPress connection test error for {site_url}: {e}")
            return False
    
    def disconnect_site(self, user_id: str, site_id: int) -> bool:
        """Disconnect a WordPress site."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE wordpress_sites 
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND user_id = ?
                ''', (site_id, user_id))
                conn.commit()
            
            logger.info(f"WordPress site {site_id} disconnected for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting WordPress site {site_id}: {e}")
            return False
    
    def get_site_info(self, site_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a WordPress site."""
        try:
            credentials = self.get_site_credentials(site_id)
            if not credentials:
                return None
            
            site_url = credentials['site_url']
            username = credentials['username']
            app_password = credentials['app_password']
            
            # Get site information
            info = {
                'site_url': site_url,
                'username': username,
                'api_version': self.api_version
            }
            
            # Test connection and get basic info
            if self._test_connection(site_url, username, app_password):
                info['connected'] = True
                info['last_checked'] = datetime.now().isoformat()
            else:
                info['connected'] = False
                info['last_checked'] = datetime.now().isoformat()
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting site info for {site_id}: {e}")
            return None

    def get_posts_for_all_sites(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all tracked WordPress posts for all sites of a user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT wp.id, wp.wordpress_post_id, wp.title, wp.status, wp.published_at, wp.last_updated_at,
                       ws.site_name, ws.site_url
                FROM wordpress_posts wp
                JOIN wordpress_sites ws ON wp.site_id = ws.id
                WHERE wp.user_id = ? AND ws.is_active = TRUE
                ORDER BY wp.published_at DESC
            ''', (user_id,))
            posts = []
            for post_data in cursor.fetchall():
                posts.append({
                    "id": post_data[0],
                    "wp_post_id": post_data[1],
                    "title": post_data[2],
                    "status": post_data[3],
                    "published_at": post_data[4],
                    "created_at": post_data[5],
                    "site_name": post_data[6],
                    "site_url": post_data[7]
                })
        return posts