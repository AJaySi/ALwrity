from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from typing import List, Dict, Any
import secrets
import logging

from .models import (
    FacebookConnectionStatus, 
    FacebookPage, 
    FacebookPublishRequest, 
    FacebookPublishResponse
)
from .auth import require_clerk_user
from .token_store import token_store
from .facebook_client import facebook_client, TokenExpiredError, FacebookAPIError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/social/facebook", tags=["facebook-social"])

@router.get("/connection-status", response_model=FacebookConnectionStatus)
async def get_connection_status(user_data: dict = Depends(require_clerk_user)):
    """Check if user has connected their Facebook account."""
    clerk_user_id = user_data["clerk_user_id"]
    logger.info(f"Checking Facebook connection status for user {clerk_user_id}")
    
    try:
        has_token = token_store.is_token_valid(clerk_user_id)
        
        if has_token:
            # Get pages count for additional info
            user_token = token_store.get_user_token(clerk_user_id)
            if user_token:
                pages = await facebook_client.get_user_pages(user_token)
                logger.info(f"User {clerk_user_id} has {len(pages)} Facebook pages")
                return FacebookConnectionStatus(
                    connected=True,
                    user_id=clerk_user_id,
                    pages_count=len(pages)
                )
        
        logger.info(f"User {clerk_user_id} is not connected to Facebook")
        return FacebookConnectionStatus(
            connected=False,
            user_id=clerk_user_id,
            pages_count=0
        )
        
    except Exception as e:
        logger.error(f"Error checking connection status for user {clerk_user_id}: {str(e)}")
        return FacebookConnectionStatus(
            connected=False,
            user_id=clerk_user_id,
            pages_count=0
        )

@router.get("/oauth/start")
async def start_facebook_oauth(user_data: dict = Depends(require_clerk_user)):
    """Start Facebook OAuth flow."""
    clerk_user_id = user_data["clerk_user_id"]
    
    try:
        # Generate state with user ID for security
        state = f"{secrets.token_urlsafe(32)}|{clerk_user_id}"
        
        # Generate OAuth URL
        oauth_url = facebook_client.generate_oauth_url(state)
        
        logger.info(f"Starting Facebook OAuth for user {clerk_user_id}")
        return RedirectResponse(url=oauth_url)
        
    except Exception as e:
        logger.error(f"Error starting OAuth: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start OAuth flow")

@router.get("/oauth/start-test")
async def start_facebook_oauth_test():
    """Start Facebook OAuth flow for testing (without Clerk authentication)."""
    try:
        # Generate state for testing
        state = f"{secrets.token_urlsafe(32)}|test_user"
        
        # Generate OAuth URL
        oauth_url = facebook_client.generate_oauth_url(state)
        
        logger.info("Starting Facebook OAuth for testing")
        return RedirectResponse(url=oauth_url)
        
    except Exception as e:
        logger.error(f"Error starting OAuth test: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start OAuth flow")

@router.get("/oauth/callback")
async def facebook_oauth_callback(
    code: str = Query(..., description="Authorization code from Facebook"),
    state: str = Query(..., description="State parameter for security")
):
    """Handle Facebook OAuth callback."""
    try:
        # Parse state to get user ID
        if "|" not in state:
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        nonce, clerk_user_id = state.split("|", 1)
        
        # Exchange code for token
        token_data = await facebook_client.exchange_code_for_token(code)
        
        if not token_data.get("access_token"):
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        # Store token
        access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 0)
        
        # Calculate expiration time
        expires_at = None
        if expires_in > 0:
            from datetime import datetime, timedelta
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        success = token_store.store_user_token(clerk_user_id, access_token, expires_at)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to store access token")
        
        logger.info(f"Successfully connected Facebook for user {clerk_user_id}")
        
        # Redirect back to frontend
        frontend_url = "http://localhost:3000/facebook-writer"  # TODO: Make configurable
        return RedirectResponse(url=f"{frontend_url}?facebook_connected=true")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in OAuth callback: {str(e)}")
        raise HTTPException(status_code=500, detail="OAuth callback failed")

@router.get("/pages", response_model=List[FacebookPage])
async def get_facebook_pages(user_data: dict = Depends(require_clerk_user)):
    """Get user's Facebook pages."""
    clerk_user_id = user_data["clerk_user_id"]
    logger.info(f"Fetching Facebook pages for user {clerk_user_id}")
    
    try:
        user_token = token_store.get_user_token(clerk_user_id)
        if not user_token:
            logger.warning(f"User {clerk_user_id} requested pages without Facebook connection")
            raise HTTPException(status_code=401, detail="Facebook not connected")
        
        pages_data = await facebook_client.get_user_pages(user_token)
        
        pages = []
        for page_data in pages_data:
            pages.append(FacebookPage(
                id=page_data["id"],
                name=page_data["name"],
                access_token=page_data["access_token"],
                category=page_data.get("category")
            ))
        
        logger.info(f"Successfully returned {len(pages)} pages for user {clerk_user_id}")
        return pages
        
    except TokenExpiredError as e:
        logger.warning(f"Token expired for user {clerk_user_id}: {str(e)}")
        # Delete expired token
        token_store.delete_user_token(clerk_user_id)
        raise HTTPException(
            status_code=401, 
            detail="Facebook token expired. Please reconnect your account.",
            headers={"X-Reauth-Required": "true"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pages for user {clerk_user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get Facebook pages")

@router.post("/publish", response_model=FacebookPublishResponse)
async def publish_to_facebook(
    request: FacebookPublishRequest,
    user_data: dict = Depends(require_clerk_user)
):
    """Publish a post to Facebook."""
    clerk_user_id = user_data["clerk_user_id"]
    logger.info(f"Publishing post for user {clerk_user_id} to page {request.page_id}")
    
    try:
        # Get user's pages to verify access
        user_token = token_store.get_user_token(clerk_user_id)
        if not user_token:
            logger.warning(f"User {clerk_user_id} attempted to publish without Facebook connection")
            raise HTTPException(status_code=401, detail="Facebook not connected")
        
        pages_data = await facebook_client.get_user_pages(user_token)
        
        # Find the requested page and its access token
        page_access_token = None
        for page_data in pages_data:
            if page_data["id"] == request.page_id:
                page_access_token = page_data["access_token"]
                break
        
        if not page_access_token:
            logger.warning(f"User {clerk_user_id} attempted to publish to unauthorized page {request.page_id}")
            raise HTTPException(status_code=403, detail="Page not found or access denied")
        
        # Publish the post
        result = await facebook_client.publish_post(
            page_id=request.page_id,
            page_access_token=page_access_token,
            message=request.message,
            link=request.link
        )
        
        if result["success"]:
            logger.info(f"Successfully published post {result['post_id']} for user {clerk_user_id} to page {request.page_id}")
            return FacebookPublishResponse(
                success=True,
                post_id=result["post_id"],
                permalink_url=result["permalink_url"]
            )
        else:
            logger.error(f"Failed to publish post for user {clerk_user_id}: {result['error']}")
            return FacebookPublishResponse(
                success=False,
                error=result["error"]
            )
        
    except TokenExpiredError as e:
        logger.warning(f"Token expired during publish for user {clerk_user_id}: {str(e)}")
        # Delete expired token
        token_store.delete_user_token(clerk_user_id)
        return FacebookPublishResponse(
            success=False,
            error="Facebook token expired. Please reconnect your account.",
            details={"reauth_required": True}
        )
    except FacebookAPIError as e:
        logger.error(f"Facebook API error for user {clerk_user_id}: {str(e)}")
        return FacebookPublishResponse(
            success=False,
            error=f"Facebook API error: {str(e)}",
            details={"status_code": e.status_code, "error_code": e.error_code}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing post for user {clerk_user_id}: {str(e)}")
        return FacebookPublishResponse(
            success=False,
            error=f"Publishing failed: {str(e)}"
        )

@router.post("/disconnect")
async def disconnect_facebook(user_data: dict = Depends(require_clerk_user)):
    """Disconnect Facebook account."""
    clerk_user_id = user_data["clerk_user_id"]
    
    try:
        success = token_store.delete_user_token(clerk_user_id)
        
        if success:
            logger.info(f"Successfully disconnected Facebook for user {clerk_user_id}")
            return {"success": True, "message": "Facebook disconnected successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to disconnect Facebook")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disconnecting Facebook: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to disconnect Facebook")

# Test endpoints (without Clerk authentication)
@router.get("/connection-status-test")
async def get_connection_status_test():
    """Test endpoint for connection status (without Clerk authentication)."""
    try:
        # For testing, we'll use the access token from environment
        import os
        access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        
        if not access_token:
            return {"connected": False, "user_id": "test_user", "pages_count": 0}
        
        # Test if token is valid by getting user info
        pages = await facebook_client.get_user_pages(access_token)
        
        return {
            "connected": True,
            "user_id": "test_user",
            "pages_count": len(pages)
        }
        
    except Exception as e:
        logger.error(f"Error checking test connection status: {str(e)}")
        return {"connected": False, "user_id": "test_user", "pages_count": 0}

@router.get("/pages-test")
async def get_facebook_pages_test():
    """Test endpoint for getting Facebook pages (without Clerk authentication)."""
    try:
        import os
        access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        
        if not access_token:
            return []
        
        pages = await facebook_client.get_user_pages(access_token)
        
        # Convert to our page format
        formatted_pages = []
        for page in pages:
            formatted_pages.append({
                "id": page["id"],
                "name": page["name"],
                "access_token": page.get("access_token", ""),
                "category": page.get("category", ""),
                "tasks": page.get("tasks", [])
            })
        
        return formatted_pages
        
    except Exception as e:
        logger.error(f"Error getting test pages: {str(e)}")
        return []
