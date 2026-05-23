"""
WordPress API Routes
REST API endpoints for WordPress integration management.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl
from loguru import logger

from services.integrations.wordpress_service import WordPressService
from services.integrations.wordpress_publisher import WordPressPublisher
from middleware.auth_middleware import get_current_user


router = APIRouter(prefix="/api/wordpress", tags=["WordPress"])


# Pydantic Models
class WordPressSiteRequest(BaseModel):
    site_url: str
    site_name: str
    username: str
    app_password: str


class WordPressSiteResponse(BaseModel):
    id: int
    site_url: str
    site_name: str
    username: str
    is_active: bool
    created_at: str
    updated_at: str


class WordPressPublishRequest(BaseModel):
    site_id: int
    title: str
    content: str
    excerpt: Optional[str] = ""
    featured_image_path: Optional[str] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: str = "draft"
    meta_description: Optional[str] = ""


class WordPressPublishResponse(BaseModel):
    success: bool
    post_id: Optional[int] = None
    post_url: Optional[str] = None
    error: Optional[str] = None


class WordPressPostResponse(BaseModel):
    id: int
    wp_post_id: int
    title: str
    status: str
    published_at: Optional[str]
    created_at: str
    site_name: str
    site_url: str


class WordPressStatusResponse(BaseModel):
    connected: bool
    sites: Optional[List[WordPressSiteResponse]] = None
    total_sites: int = 0


# Initialize services
wp_service = WordPressService()
wp_publisher = WordPressPublisher()


@router.get("/status", response_model=WordPressStatusResponse)
async def get_wordpress_status(user: dict = Depends(get_current_user)):
    """Get WordPress connection status for the current user."""
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        logger.info(f"Checking WordPress status for user: {user_id}")
        
        # Get user's WordPress sites
sites = wp_service.get_user_sites(user_id)

        if sites:
            site_responses = [
                WordPressSiteResponse(
                    id=site['id'],
                    site_url=site['site_url'],
                    site_name=site['site_name'],
                    username=site['username'],
                    is_active=site['is_active'],
                    created_at=site['created_at'],
                    updated_at=site['updated_at']
                )
                for site in sites
            ]

            return WordPressStatusResponse(
                connected=True,
                sites=site_responses,
                total_sites=len(sites)
            )
        else:
            return WordPressStatusResponse(
                connected=False,
                sites=[],
                total_sites=0
            )
            
    except Exception as e:
        logger.error(f"Error getting WordPress status for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking WordPress status: {str(e)}")


@router.post("/sites", response_model=WordPressSiteResponse)
async def add_wordpress_site(
    site_request: WordPressSiteRequest,
    user: dict = Depends(get_current_user)
):
    """Add a new WordPress site connection."""
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        logger.info(f"Adding WordPress site for user {user_id}: {site_request.site_name}")
        
        # Add the site
        success = wp_service.add_site(
            user_id=user_id,
            site_url=site_request.site_url,
            site_name=site_request.site_name,
            username=site_request.username,
            app_password=site_request.app_password
        )
        
        if not success:
            raise HTTPException(
                status_code=400, 
                detail="Failed to connect to WordPress site. Please check your credentials."
            )
        
        # Get the added site info
        sites = wp_service.get_user_sites(user_id)
        if sites:
            latest_site = sites[0]  # Most recent site
            return WordPressSiteResponse(
                id=latest_site['id'],
                site_url=latest_site['site_url'],
                site_name=latest_site['site_name'],
                username=latest_site['username'],
                is_active=latest_site['is_active'],
                created_at=latest_site['created_at'],
                updated_at=latest_site['updated_at']
            )
        else:
            raise HTTPException(status_code=500, detail="Site added but could not retrieve details")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding WordPress site: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding WordPress site: {str(e)}")


@router.get("/sites", response_model=List[WordPressSiteResponse])
async def get_wordpress_sites(user: dict = Depends(get_current_user)):
    """Get all WordPress sites for the current user."""
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        logger.info(f"Getting WordPress sites for user: {user_id}")
        
        sites = wp_service.get_user_sites(user_id)
        
        site_responses = [
            WordPressSiteResponse(
                id=site['id'],
                site_url=site['site_url'],
                site_name=site['site_name'],
                username=site['username'],
                is_active=site['is_active'],
                created_at=site['created_at'],
                updated_at=site['updated_at']
            )
            for site in sites
        ]
        
        logger.info(f"Retrieved {len(sites)} WordPress sites for user {user_id}")
        return site_responses
        
    except Exception as e:
        logger.error(f"Error getting WordPress sites for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving WordPress sites: {str(e)}")


@router.delete("/sites/{site_id}")
async def disconnect_wordpress_site(
    site_id: int,
    user: dict = Depends(get_current_user)
):
    """Disconnect a WordPress site."""
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        logger.info(f"Disconnecting WordPress site {site_id} for user {user_id}")
        
        success = wp_service.disconnect_site(user_id, site_id)
        
        if not success:
            raise HTTPException(
                status_code=404, 
                detail="WordPress site not found or already disconnected"
            )
        
        logger.info(f"WordPress site {site_id} disconnected successfully")
        return {"success": True, "message": "WordPress site disconnected successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disconnecting WordPress site {site_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error disconnecting WordPress site: {str(e)}")


@router.post("/publish", response_model=WordPressPublishResponse)
async def publish_to_wordpress(
    publish_request: WordPressPublishRequest,
    user: dict = Depends(get_current_user)
):
    """Publish content to a WordPress site."""
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        logger.info(f"Publishing to WordPress site {publish_request.site_id} for user {user_id}")
        
        # Publish the content
        result = wp_publisher.publish_blog_post(
            user_id=user_id,
            site_id=publish_request.site_id,
            title=publish_request.title,
            content=publish_request.content,
            excerpt=publish_request.excerpt,
            featured_image_path=publish_request.featured_image_path,
            categories=publish_request.categories,
            tags=publish_request.tags,
            status=publish_request.status,
            meta_description=publish_request.meta_description
        )
        
        if result['success']:
            logger.info(f"Content published successfully to WordPress: {result['post_id']}")
            return WordPressPublishResponse(
                success=True,
                post_id=result['post_id'],
                post_url=result.get('post_url')
            )
        else:
            logger.error(f"Failed to publish content: {result['error']}")
            return WordPressPublishResponse(
                success=False,
                error=result['error']
            )
            
    except Exception as e:
        logger.error(f"Error publishing to WordPress: {e}")
        return WordPressPublishResponse(
            success=False,
            error=f"Error publishing content: {str(e)}"
        )


@router.get("/posts", response_model=List[WordPressPostResponse])
async def get_wordpress_posts(
    site_id: Optional[int] = None,
    user: dict = Depends(get_current_user)
):
    """Get published posts from WordPress sites."""
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        logger.info(f"Getting WordPress posts for user {user_id}, site_id: {site_id}")
        
        posts = wp_service.get_posts_for_site(user_id, site_id) if site_id else wp_service.get_posts_for_all_sites(user_id)
        
        post_responses = [
            WordPressPostResponse(
                id=post['id'],
                wp_post_id=post['wp_post_id'],
                title=post['title'],
                status=post['status'],
                published_at=post['published_at'],
                created_at=post['created_at'],
                site_name=post['site_name'],
                site_url=post['site_url']
            )
            for post in posts
        ]
        
        logger.info(f"Retrieved {len(posts)} WordPress posts for user {user_id}")
        return post_responses
        
    except Exception as e:
        logger.error(f"Error getting WordPress posts for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving WordPress posts: {str(e)}")


@router.put("/posts/{post_id}/status")
async def update_post_status(
    post_id: int,
    status: str,
    user: dict = Depends(get_current_user)
):
    """Update the status of a WordPress post (draft/publish)."""
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        if status not in ['draft', 'publish', 'private']:
            raise HTTPException(
                status_code=400, 
                detail="Invalid status. Must be 'draft', 'publish', or 'private'"
            )
        
        logger.info(f"Updating WordPress post {post_id} status to {status} for user {user_id}")
        
        success = wp_publisher.update_post_status(user_id, post_id, status)
        
        if not success:
            raise HTTPException(
                status_code=404, 
                detail="Post not found or update failed"
            )
        
        logger.info(f"WordPress post {post_id} status updated to {status}")
        return {"success": True, "message": f"Post status updated to {status}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating WordPress post {post_id} status: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating post status: {str(e)}")


@router.delete("/posts/{post_id}")
async def delete_wordpress_post(
    post_id: int,
    force: bool = False,
    user: dict = Depends(get_current_user)
):
    """Delete a WordPress post."""
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        logger.info(f"Deleting WordPress post {post_id} for user {user_id}, force: {force}")
        
        success = wp_publisher.delete_post(user_id, post_id, force)
        
        if not success:
            raise HTTPException(
                status_code=404, 
                detail="Post not found or deletion failed"
            )
        
        logger.info(f"WordPress post {post_id} deleted successfully")
        return {"success": True, "message": "Post deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting WordPress post {post_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting post: {str(e)}")


@router.get("/health")
async def wordpress_health_check():
    """WordPress integration health check."""
    try:
        return {
            "status": "healthy",
            "service": "wordpress",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"WordPress health check failed: {e}")
        raise HTTPException(status_code=500, detail="WordPress service unhealthy")
