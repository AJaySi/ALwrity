"""
WordPress Publishing Service
High-level service for publishing content to WordPress sites.
"""

import os
import json
import tempfile
from typing import Optional, Dict, List, Any, Union
from datetime import datetime
from loguru import logger

from .wordpress_service import WordPressService
from .wordpress_content import WordPressContentManager
import sqlite3


class WordPressPublisher:
    """High-level WordPress publishing service."""
    
    def __init__(self, db_path: str = "alwrity.db"):
        """Initialize WordPress publisher."""
        self.wp_service = WordPressService(db_path)
        self.db_path = db_path
    
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
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO wordpress_posts 
                    (user_id, site_id, wp_post_id, title, status, published_at, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, site_id, wp_post_id, title, status, 
                      datetime.now().isoformat() if status == 'publish' else None))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error storing post reference: {e}")
    
    def get_user_posts(self, user_id: str, site_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all posts published by user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if site_id:
                    cursor.execute('''
                        SELECT wp.id, wp.wp_post_id, wp.title, wp.status, wp.published_at, wp.created_at,
                               ws.site_name, ws.site_url
                        FROM wordpress_posts wp
                        JOIN wordpress_sites ws ON wp.site_id = ws.id
                        WHERE wp.user_id = ? AND wp.site_id = ?
                        ORDER BY wp.created_at DESC
                    ''', (user_id, site_id))
                else:
                    cursor.execute('''
                        SELECT wp.id, wp.wp_post_id, wp.title, wp.status, wp.published_at, wp.created_at,
                               ws.site_name, ws.site_url
                        FROM wordpress_posts wp
                        JOIN wordpress_sites ws ON wp.site_id = ws.id
                        WHERE wp.user_id = ?
                        ORDER BY wp.created_at DESC
                    ''', (user_id,))
                
                posts = []
                for row in cursor.fetchall():
                    posts.append({
                        'id': row[0],
                        'wp_post_id': row[1],
                        'title': row[2],
                        'status': row[3],
                        'published_at': row[4],
                        'created_at': row[5],
                        'site_name': row[6],
                        'site_url': row[7]
                    })
                
                return posts
                
        except Exception as e:
            logger.error(f"Error getting user posts: {e}")
            return []
    
    def update_post_status(self, user_id: str, post_id: int, status: str) -> bool:
        """Update post status (draft/publish)."""
        try:
            # Get post info
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT wp.site_id, wp.wp_post_id, ws.site_url, ws.username, ws.app_password
                    FROM wordpress_posts wp
                    JOIN wordpress_sites ws ON wp.site_id = ws.id
                    WHERE wp.id = ? AND wp.user_id = ?
                ''', (post_id, user_id))
                
                result = cursor.fetchone()
                if not result:
                    return False
                
                site_id, wp_post_id, site_url, username, app_password = result
            
            # Update in WordPress
            content_manager = WordPressContentManager(site_url, username, app_password)
            wp_result = content_manager.update_post(wp_post_id, status=status)
            
            if wp_result:
                # Update in database
                cursor.execute('''
                    UPDATE wordpress_posts 
                    SET status = ?, published_at = ?
                    WHERE id = ?
                ''', (status, datetime.now().isoformat() if status == 'publish' else None, post_id))
                conn.commit()
                
                logger.info(f"Post {post_id} status updated to {status}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating post status: {e}")
            return False
    
    def delete_post(self, user_id: str, post_id: int, force: bool = False) -> bool:
        """Delete a WordPress post."""
        try:
            # Get post info
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT wp.site_id, wp.wp_post_id, ws.site_url, ws.username, ws.app_password
                    FROM wordpress_posts wp
                    JOIN wordpress_sites ws ON wp.site_id = ws.id
                    WHERE wp.id = ? AND wp.user_id = ?
                ''', (post_id, user_id))
                
                result = cursor.fetchone()
                if not result:
                    return False
                
                site_id, wp_post_id, site_url, username, app_password = result
            
            # Delete from WordPress
            content_manager = WordPressContentManager(site_url, username, app_password)
            wp_result = content_manager.delete_post(wp_post_id, force=force)
            
            if wp_result:
                # Remove from database
                cursor.execute('DELETE FROM wordpress_posts WHERE id = ?', (post_id,))
                conn.commit()
                
                logger.info(f"Post {post_id} deleted successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting post: {e}")
            return False
