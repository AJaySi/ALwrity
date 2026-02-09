"""
WordPress Service for ALwrity
Handles WordPress site connections, content publishing, and media management.
"""

from contextlib import contextmanager
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
from PIL import Image
from loguru import logger
from sqlalchemy import text
from services.database import get_user_data_db_session


class WordPressService:
    """Main WordPress service class for managing WordPress integrations."""
    
    def __init__(self):
        """Initialize WordPress service with database connection."""
        self.api_version = "v2"
        self._ensure_tables()

    @contextmanager
    def _db_session(self):
        db = get_user_data_db_session()
        if db is None:
            raise ValueError("User data database session unavailable")
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    
    def _ensure_tables(self) -> None:
        """Ensure required database tables exist."""
        try:
            with self._db_session() as db:
                # WordPress sites table
                db.execute(text('''
                    CREATE TABLE IF NOT EXISTS wordpress_sites (
                        id BIGSERIAL PRIMARY KEY,
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
                '''))

                # WordPress posts table for tracking published content
                db.execute(text('''
                    CREATE TABLE IF NOT EXISTS wordpress_posts (
                        id BIGSERIAL PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        site_id INTEGER NOT NULL,
                        wordpress_post_id INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        status TEXT DEFAULT 'draft',
                        published_at TIMESTAMP,
                        last_updated_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (site_id) REFERENCES wordpress_sites (id)
                    )
                '''))
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
            
            with self._db_session() as db:
                db.execute(
                    text('''
                        INSERT INTO wordpress_sites
                        (user_id, site_url, site_name, username, app_password, updated_at)
                        VALUES (:user_id, :site_url, :site_name, :username, :app_password, CURRENT_TIMESTAMP)
                        ON CONFLICT (user_id, site_url)
                        DO UPDATE SET site_name = EXCLUDED.site_name,
                                      username = EXCLUDED.username,
                                      app_password = EXCLUDED.app_password,
                                      updated_at = CURRENT_TIMESTAMP
                    '''),
                    {
                        "user_id": user_id,
                        "site_url": site_url,
                        "site_name": site_name,
                        "username": username,
                        "app_password": app_password
                    }
                )
            
            logger.info(f"WordPress site added for user {user_id}: {site_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding WordPress site: {e}")
            return False
    
    def get_user_sites(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all WordPress sites for a user."""
        try:
            with self._db_session() as db:
                rows = db.execute(
                    text('''
                        SELECT id, site_url, site_name, username, is_active, created_at, updated_at
                        FROM wordpress_sites
                        WHERE user_id = :user_id AND is_active = TRUE
                        ORDER BY updated_at DESC
                    '''),
                    {"user_id": user_id}
                ).fetchall()

                sites = []
                for row in rows:
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
            with self._db_session() as db:
                result = db.execute(
                    text('''
                        SELECT site_url, username, app_password
                        FROM wordpress_sites
                        WHERE id = :site_id AND is_active = TRUE
                    '''),
                    {"site_id": site_id}
                ).fetchone()
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
            with self._db_session() as db:
                db.execute(
                    text('''
                        UPDATE wordpress_sites
                        SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                        WHERE id = :site_id AND user_id = :user_id
                    '''),
                    {"site_id": site_id, "user_id": user_id}
                )
            
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
        with self._db_session() as db:
            rows = db.execute(
                text('''
                    SELECT wp.id, wp.wordpress_post_id, wp.title, wp.status, wp.published_at, wp.last_updated_at,
                           ws.site_name, ws.site_url
                    FROM wordpress_posts wp
                    JOIN wordpress_sites ws ON wp.site_id = ws.id
                    WHERE wp.user_id = :user_id AND ws.is_active = TRUE
                    ORDER BY wp.published_at DESC
                '''),
                {"user_id": user_id}
            ).fetchall()
            posts = []
            for post_data in rows:
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
