"""
WordPress Service for ALwrity
Handles WordPress site connections, content publishing, and media management.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
from loguru import logger
from sqlalchemy.orm import Session

from services.database import get_platform_db_session
from models.oauth_token_models import WordPressSite, WordPressPost


class WordPressService:
    """Main WordPress service class for managing WordPress integrations."""
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize WordPress service with database session."""
        self.db_session = db_session
        self.api_version = "v2"

    def _get_db_session(self) -> Optional[Session]:
        return self.db_session or get_platform_db_session()

    def _cleanup_session(self, db: Optional[Session]) -> None:
        if db is not None and self.db_session is None:
            db.close()
    
    def add_site(self, user_id: str, site_url: str, site_name: str, username: str, app_password: str) -> bool:
        """Add a new WordPress site connection."""
        db = self._get_db_session()
        if not db:
            logger.error("Error adding WordPress site: database session unavailable")
            return False
        try:
            # Validate site URL format
            if not site_url.startswith(('http://', 'https://')):
                site_url = f"https://{site_url}"
            
            # Test connection before saving
            if not self._test_connection(site_url, username, app_password):
                logger.error(f"Failed to connect to WordPress site: {site_url}")
                return False
            
            existing = (
                db.query(WordPressSite)
                .filter(
                    WordPressSite.user_id == user_id,
                    WordPressSite.site_url == site_url,
                )
                .first()
            )
            now = datetime.utcnow()
            if existing:
                existing.site_name = site_name
                existing.username = username
                existing.app_password = app_password
                existing.updated_at = now
                existing.is_active = True
            else:
                db.add(WordPressSite(
                    user_id=user_id,
                    site_url=site_url,
                    site_name=site_name,
                    username=username,
                    app_password=app_password,
                    created_at=now,
                    updated_at=now,
                ))
            db.commit()
            
            logger.info(f"WordPress site added for user {user_id}: {site_name}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding WordPress site: {e}")
            return False
        finally:
            self._cleanup_session(db)
    
    def get_user_sites(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all WordPress sites for a user."""
        db = self._get_db_session()
        if not db:
            logger.error("Error getting WordPress sites: database session unavailable")
            return []
        try:
            records = (
                db.query(WordPressSite)
                .filter(
                    WordPressSite.user_id == user_id,
                    WordPressSite.is_active.is_(True),
                )
                .order_by(WordPressSite.updated_at.desc())
                .all()
            )
            
            sites = []
            for record in records:
                sites.append({
                    'id': record.id,
                    'site_url': record.site_url,
                    'site_name': record.site_name,
                    'username': record.username,
                    'is_active': bool(record.is_active),
                    'created_at': record.created_at,
                    'updated_at': record.updated_at,
                })
            
            logger.info(f"Retrieved {len(sites)} WordPress sites for user {user_id}")
            return sites
                
        except Exception as e:
            logger.error(f"Error getting WordPress sites for user {user_id}: {e}")
            return []
        finally:
            self._cleanup_session(db)
    
    def get_site_credentials(self, site_id: int) -> Optional[Dict[str, str]]:
        """Get credentials for a specific WordPress site."""
        db = self._get_db_session()
        if not db:
            logger.error("Error getting WordPress credentials: database session unavailable")
            return None
        try:
            result = (
                db.query(WordPressSite)
                .filter(
                    WordPressSite.id == site_id,
                    WordPressSite.is_active.is_(True),
                )
                .first()
            )
            
            if result:
                return {
                    'site_url': result.site_url,
                    'username': result.username,
                    'app_password': result.app_password,
                }
            return None
                
        except Exception as e:
            logger.error(f"Error getting credentials for site {site_id}: {e}")
            return None
        finally:
            self._cleanup_session(db)
    
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
        db = self._get_db_session()
        if not db:
            logger.error("Error disconnecting WordPress site: database session unavailable")
            return False
        try:
            db.query(WordPressSite).filter(
                WordPressSite.id == site_id,
                WordPressSite.user_id == user_id,
            ).update(
                {"is_active": False, "updated_at": datetime.utcnow()}
            )
            db.commit()
            
            logger.info(f"WordPress site {site_id} disconnected for user {user_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error disconnecting WordPress site {site_id}: {e}")
            return False
        finally:
            self._cleanup_session(db)
    
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
        db = self._get_db_session()
        if not db:
            logger.error("Error getting WordPress posts: database session unavailable")
            return []
        try:
            posts = []
            records = (
                db.query(WordPressPost, WordPressSite)
                .join(WordPressSite, WordPressPost.site_id == WordPressSite.id)
                .filter(
                    WordPressPost.user_id == user_id,
                    WordPressSite.is_active.is_(True),
                )
                .order_by(WordPressPost.published_at.desc())
                .all()
            )
            for post, site in records:
                posts.append({
                    "id": post.id,
                    "wp_post_id": post.wp_post_id,
                    "title": post.title,
                    "status": post.status,
                    "published_at": post.published_at,
                    "created_at": post.created_at,
                    "site_name": site.site_name,
                    "site_url": site.site_url,
                })
            return posts
        finally:
            self._cleanup_session(db)
