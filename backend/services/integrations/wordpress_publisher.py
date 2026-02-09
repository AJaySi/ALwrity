"""
WordPress Publishing Service
High-level service for publishing content to WordPress sites.
"""

import os
from typing import Optional, Dict, List, Any
from datetime import datetime
from loguru import logger

from sqlalchemy.orm import Session

from .wordpress_service import WordPressService
from .wordpress_content import WordPressContentManager
from services.database import get_platform_db_session
from models.oauth_token_models import WordPressPost, WordPressSite


class WordPressPublisher:
    """High-level WordPress publishing service."""
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize WordPress publisher."""
        self.db_session = db_session
        self.wp_service = WordPressService(db_session)

    def _get_db_session(self) -> Optional[Session]:
        return self.db_session or get_platform_db_session()

    def _cleanup_session(self, db: Optional[Session]) -> None:
        if db is not None and self.db_session is None:
            db.close()
    
    def publish_blog_post(self, user_id: str, site_id: int, 
                         title: str, content: str, 
                         excerpt: str = "", 
                         featured_image_path: Optional[str] = None,
                         categories: Optional[List[str]] = None,
                         tags: Optional[List[str]] = None,
                         status: str = 'draft',
                         meta_description: str = "") -> Dict[str, Any]:
        """Publish a blog post to WordPress."""
        try:
            # Get site credentials
            credentials = self.wp_service.get_site_credentials(site_id)
            if not credentials:
                return {
                    'success': False,
                    'error': 'WordPress site not found or inactive',
                    'post_id': None
                }
            
            # Initialize content manager
            content_manager = WordPressContentManager(
                credentials['site_url'],
                credentials['username'],
                credentials['app_password']
            )
            
            # Test connection
            if not content_manager._test_connection():
                return {
                    'success': False,
                    'error': 'Cannot connect to WordPress site',
                    'post_id': None
                }
            
            # Handle featured image
            featured_media_id = None
            if featured_image_path and os.path.exists(featured_image_path):
                try:
                    # Compress image if it's an image file
                    if featured_image_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                        compressed_path = content_manager.compress_image(featured_image_path)
                        featured_media = content_manager.upload_media(
                            compressed_path,
                            alt_text=title,
                            title=title,
                            caption=excerpt
                        )
                        # Clean up temporary file if created
                        if compressed_path != featured_image_path:
                            os.unlink(compressed_path)
                    else:
                        featured_media = content_manager.upload_media(
                            featured_image_path,
                            alt_text=title,
                            title=title,
                            caption=excerpt
                        )
                    
                    if featured_media:
                        featured_media_id = featured_media['id']
                        logger.info(f"Featured image uploaded: {featured_media_id}")
                except Exception as e:
                    logger.warning(f"Failed to upload featured image: {e}")
            
            # Handle categories
            category_ids = []
            if categories:
                for category_name in categories:
                    category_id = content_manager.get_or_create_category(category_name)
                    if category_id:
                        category_ids.append(category_id)
            
            # Handle tags
            tag_ids = []
            if tags:
                for tag_name in tags:
                    tag_id = content_manager.get_or_create_tag(tag_name)
                    if tag_id:
                        tag_ids.append(tag_id)
            
            # Prepare meta data
            meta_data = {}
            if meta_description:
                meta_data['description'] = meta_description
            
            # Create the post
            post_data = content_manager.create_post(
                title=title,
                content=content,
                excerpt=excerpt,
                featured_media_id=featured_media_id,
                categories=category_ids if category_ids else None,
                tags=tag_ids if tag_ids else None,
                status=status,
                meta=meta_data if meta_data else None
            )
            
            if post_data:
                # Store post reference in database
                self._store_post_reference(user_id, site_id, post_data['id'], title, status)
                
                logger.info(f"Blog post published successfully: {title}")
                return {
                    'success': True,
                    'post_id': post_data['id'],
                    'post_url': post_data.get('link'),
                    'featured_media_id': featured_media_id,
                    'categories': category_ids,
                    'tags': tag_ids
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to create WordPress post',
                    'post_id': None
                }
                
        except Exception as e:
            logger.error(f"Error publishing blog post: {e}")
            return {
                'success': False,
                'error': str(e),
                'post_id': None
            }
    
    def _store_post_reference(self, user_id: str, site_id: int, wp_post_id: int, title: str, status: str) -> None:
        """Store post reference in database."""
        db = self._get_db_session()
        if not db:
            logger.error("Error storing post reference: database session unavailable")
            return
        try:
            published_at = datetime.utcnow() if status == 'publish' else None
            db.add(WordPressPost(
                user_id=user_id,
                site_id=site_id,
                wp_post_id=wp_post_id,
                title=title,
                status=status,
                published_at=published_at,
                created_at=datetime.utcnow(),
            ))
            db.commit()
                
        except Exception as e:
            db.rollback()
            logger.error(f"Error storing post reference: {e}")
        finally:
            self._cleanup_session(db)
    
    def get_user_posts(self, user_id: str, site_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all posts published by user."""
        db = self._get_db_session()
        if not db:
            logger.error("Error getting WordPress posts: database session unavailable")
            return []
        try:
            query = (
                db.query(WordPressPost, WordPressSite)
                .join(WordPressSite, WordPressPost.site_id == WordPressSite.id)
                .filter(WordPressPost.user_id == user_id)
            )
            if site_id:
                query = query.filter(WordPressPost.site_id == site_id)
            query = query.order_by(WordPressPost.created_at.desc())
            
            posts = []
            for post, site in query.all():
                posts.append({
                    'id': post.id,
                    'wp_post_id': post.wp_post_id,
                    'title': post.title,
                    'status': post.status,
                    'published_at': post.published_at,
                    'created_at': post.created_at,
                    'site_name': site.site_name,
                    'site_url': site.site_url,
                })
            
            return posts
                
        except Exception as e:
            logger.error(f"Error getting user posts: {e}")
            return []
        finally:
            self._cleanup_session(db)
    
    def update_post_status(self, user_id: str, post_id: int, status: str) -> bool:
        """Update post status (draft/publish)."""
        db = self._get_db_session()
        if not db:
            logger.error("Error updating WordPress post: database session unavailable")
            return False
        try:
            # Get post info
            result = (
                db.query(WordPressPost, WordPressSite)
                .join(WordPressSite, WordPressPost.site_id == WordPressSite.id)
                .filter(WordPressPost.id == post_id, WordPressPost.user_id == user_id)
                .first()
            )
            
            if not result:
                return False
            
            post, site = result
            wp_post_id = post.wp_post_id
            site_url = site.site_url
            username = site.username
            app_password = site.app_password
            
            # Update in WordPress
            content_manager = WordPressContentManager(site_url, username, app_password)
            wp_result = content_manager.update_post(wp_post_id, status=status)
            
            if wp_result:
                # Update in database
                post.status = status
                post.published_at = datetime.utcnow() if status == 'publish' else None
                db.commit()
                
                logger.info(f"Post {post_id} status updated to {status}")
                return True
            
            return False
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating post status: {e}")
            return False
        finally:
            self._cleanup_session(db)
    
    def delete_post(self, user_id: str, post_id: int, force: bool = False) -> bool:
        """Delete a WordPress post."""
        db = self._get_db_session()
        if not db:
            logger.error("Error deleting WordPress post: database session unavailable")
            return False
        try:
            # Get post info
            result = (
                db.query(WordPressPost, WordPressSite)
                .join(WordPressSite, WordPressPost.site_id == WordPressSite.id)
                .filter(WordPressPost.id == post_id, WordPressPost.user_id == user_id)
                .first()
            )
            
            if not result:
                return False
            
            post, site = result
            wp_post_id = post.wp_post_id
            site_url = site.site_url
            username = site.username
            app_password = site.app_password
            
            # Delete from WordPress
            content_manager = WordPressContentManager(site_url, username, app_password)
            wp_result = content_manager.delete_post(wp_post_id, force=force)
            
            if wp_result:
                # Remove from database
                db.delete(post)
                db.commit()
                
                logger.info(f"Post {post_id} deleted successfully")
                return True
            
            return False
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting post: {e}")
            return False
        finally:
            self._cleanup_session(db)
