"""
Wix Integration API Routes

Handles Wix authentication, connection status, and blog publishing.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any, Optional
from loguru import logger
from pydantic import BaseModel

from services.wix_service import WixService
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/wix", tags=["Wix Integration"])

# Initialize Wix service
wix_service = WixService()


class WixAuthRequest(BaseModel):
    """Request model for Wix authentication"""
    code: str
    state: Optional[str] = None


class WixPublishRequest(BaseModel):
    """Request model for publishing to Wix"""
    title: str
    content: str
    cover_image_url: Optional[str] = None
    category_ids: Optional[list] = None
    tag_ids: Optional[list] = None
    publish: bool = True
    # Optional access token for test-real publish flow
    access_token: Optional[str] = None
class WixCreateCategoryRequest(BaseModel):
    access_token: str
    label: str
    description: Optional[str] = None
    language: Optional[str] = None


class WixCreateTagRequest(BaseModel):
    access_token: str
    label: str
    language: Optional[str] = None


class WixConnectionStatus(BaseModel):
    """Response model for Wix connection status"""
    connected: bool
    has_permissions: bool
    site_info: Optional[Dict[str, Any]] = None
    permissions: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.get("/auth/url")
async def get_authorization_url(state: Optional[str] = None) -> Dict[str, str]:
    """
    Get Wix OAuth authorization URL
    
    Args:
        state: Optional state parameter for security
        
    Returns:
        Authorization URL
    """
    try:
        url = wix_service.get_authorization_url(state)
        return {"authorization_url": url}
    except Exception as e:
        logger.error(f"Failed to generate authorization URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/callback")
async def handle_oauth_callback(request: WixAuthRequest, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Handle OAuth callback and exchange code for tokens
    
    Args:
        request: OAuth callback request with code
        current_user: Current authenticated user
        
    Returns:
        Token information and connection status
    """
    try:
        # Exchange code for tokens
        tokens = wix_service.exchange_code_for_tokens(request.code)
        
        # Get site information
        site_info = wix_service.get_site_info(tokens['access_token'])
        
        # Check permissions
        permissions = wix_service.check_blog_permissions(tokens['access_token'])
        
        # TODO: Store tokens securely in database associated with current_user
        # For now, we'll return them (in production, store in encrypted database)
        
        return {
            "success": True,
            "tokens": {
                "access_token": tokens['access_token'],
                "refresh_token": tokens.get('refresh_token'),
                "expires_in": tokens.get('expires_in'),
                "token_type": tokens.get('token_type', 'Bearer')
            },
            "site_info": site_info,
            "permissions": permissions,
            "message": "Successfully connected to Wix"
        }
        
    except Exception as e:
        logger.error(f"Failed to handle OAuth callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connection/status")
async def get_connection_status(current_user: dict = Depends(get_current_user)) -> WixConnectionStatus:
    """
    Check Wix connection status and permissions
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Connection status and permissions
    """
    try:
        # TODO: Retrieve stored tokens from database for current_user
        # For now, we'll return a mock response
        # In production, you'd check if tokens exist and are valid
        
        return WixConnectionStatus(
            connected=False,
            has_permissions=False,
            error="No Wix connection found. Please connect your Wix account first."
        )
        
    except Exception as e:
        logger.error(f"Failed to check connection status: {e}")
        return WixConnectionStatus(
            connected=False,
            has_permissions=False,
            error=str(e)
        )


@router.post("/publish")
async def publish_to_wix(request: WixPublishRequest, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Publish blog post to Wix
    
    Args:
        request: Blog post data
        current_user: Current authenticated user
        
    Returns:
        Published blog post information
    """
    try:
        # TODO: Retrieve stored access token from database for current_user
        # For now, we'll return an error asking user to connect first
        
        return {
            "success": False,
            "error": "Wix account not connected. Please connect your Wix account first.",
            "message": "Use the /api/wix/auth/url endpoint to get the authorization URL"
        }
        
        # Example of what the actual implementation would look like:
        # access_token = get_stored_access_token(current_user['id'])
        # 
        # if not access_token:
        #     raise HTTPException(status_code=401, detail="Wix account not connected")
        # 
        # # Check if token is still valid, refresh if needed
        # try:
        #     site_info = wix_service.get_site_info(access_token)
        # except:
        #     # Token expired, try to refresh
        #     refresh_token = get_stored_refresh_token(current_user['id'])
        #     if refresh_token:
        #         new_tokens = wix_service.refresh_access_token(refresh_token)
        #         access_token = new_tokens['access_token']
        #         # Store new tokens
        #     else:
        #         raise HTTPException(status_code=401, detail="Wix session expired. Please reconnect.")
        # 
        # # Get current member ID (required for third-party apps)
        # member_info = wix_service.get_current_member(access_token)
        # member_id = member_info.get('member', {}).get('id')
        # 
        # if not member_id:
        #     raise HTTPException(status_code=400, detail="Could not retrieve member ID")
        # 
        # # Create blog post
        # result = wix_service.create_blog_post(
        #     access_token=access_token,
        #     title=request.title,
        #     content=request.content,
        #     cover_image_url=request.cover_image_url,
        #     category_ids=request.category_ids,
        #     tag_ids=request.tag_ids,
        #     publish=request.publish,
        #     member_id=member_id  # Required for third-party apps
        # )
        # 
        # return {
        #     "success": True,
        #     "post_id": result.get('draftPost', {}).get('id'),
        #     "url": result.get('draftPost', {}).get('url'),
        #     "message": "Blog post published successfully to Wix"
        # }
        
    except Exception as e:
        logger.error(f"Failed to publish to Wix: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_blog_categories(current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get available blog categories from Wix
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of blog categories
    """
    try:
        # TODO: Retrieve stored access token from database for current_user
        return {
            "success": False,
            "error": "Wix account not connected. Please connect your Wix account first."
        }
        
        # Example implementation:
        # access_token = get_stored_access_token(current_user['id'])
        # if not access_token:
        #     raise HTTPException(status_code=401, detail="Wix account not connected")
        # 
        # categories = wix_service.get_blog_categories(access_token)
        # return {"categories": categories}
        
    except Exception as e:
        logger.error(f"Failed to get blog categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tags")
async def get_blog_tags(current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get available blog tags from Wix
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of blog tags
    """
    try:
        # TODO: Retrieve stored access token from database for current_user
        return {
            "success": False,
            "error": "Wix account not connected. Please connect your Wix account first."
        }
        
        # Example implementation:
        # access_token = get_stored_access_token(current_user['id'])
        # if not access_token:
        #     raise HTTPException(status_code=401, detail="Wix account not connected")
        # 
        # tags = wix_service.get_blog_tags(access_token)
        # return {"tags": tags}
        
    except Exception as e:
        logger.error(f"Failed to get blog tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disconnect")
async def disconnect_wix(current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Disconnect Wix account
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Disconnection status
    """
    try:
        # TODO: Remove stored tokens from database for current_user
        return {
            "success": True,
            "message": "Wix account disconnected successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to disconnect Wix: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# TEST ENDPOINTS - No authentication required for testing
# =============================================================================

@router.get("/test/connection/status")
async def get_test_connection_status() -> WixConnectionStatus:
    """
    TEST ENDPOINT: Check Wix connection status without authentication
    
    Returns:
        Connection status and permissions
    """
    try:
        logger.info("TEST: Checking Wix connection status (no auth required)")
        
        return WixConnectionStatus(
            connected=False,
            has_permissions=False,
            error="No stored tokens found. Please connect your Wix account first."
        )
        
    except Exception as e:
        logger.error(f"TEST: Failed to check connection status: {e}")
        return WixConnectionStatus(
            connected=False,
            has_permissions=False,
            error=str(e)
        )


@router.get("/test/auth/url")
async def get_test_authorization_url(state: Optional[str] = None) -> Dict[str, str]:
    """
    TEST ENDPOINT: Get Wix OAuth authorization URL without authentication
    
    Args:
        state: Optional state parameter for security
        
    Returns:
        Authorization URL for user to visit
    """
    try:
        logger.info("TEST: Generating Wix authorization URL (no auth required)")
        
        # Check if Wix service is properly configured
        if not wix_service.client_id:
            logger.warning("TEST: Wix Client ID not configured, returning mock URL")
            return {
                "url": "https://www.wix.com/oauth/access?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:3000/wix/callback&response_type=code&scope=BLOG.CREATE-DRAFT,BLOG.PUBLISH,MEDIA.MANAGE&code_challenge=test&code_challenge_method=S256",
                "state": state or "test_state",
                "message": "WIX_CLIENT_ID not configured. Please set it in your .env file to get a real authorization URL."
            }
        
        auth_url = wix_service.get_authorization_url(state)
        return {"url": auth_url, "state": state or "test_state"}
    except Exception as e:
        logger.error(f"TEST: Failed to generate authorization URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/publish")
async def test_publish_to_wix(request: WixPublishRequest) -> Dict[str, Any]:
    """
    TEST ENDPOINT: Simulate publishing a blog post to Wix without authentication.

    Returns a fake success response so the frontend can validate the flow.
    """
    try:
        logger.info("TEST: Simulating publish to Wix (no auth required)")
        return {
            "success": True,
            "post_id": "test_post_id",
            "url": "https://example.com/blog/test-post",
            "message": "Simulated blog post published successfully (test mode)"
        }
    except Exception as e:
        logger.error(f"TEST: Failed to simulate publish: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/publish/real")
async def test_publish_real(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    TEST ENDPOINT: Perform a real publish to Wix using a provided access token.

    Notes:
      - Expects request.access_token from the frontend's Wix SDK tokens
      - Derives member_id server-side (required by Wix for third-party apps)
    """
    try:
        access_token = payload.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Missing access_token")

        # Derive current member id from token (try local decode first, then API fallback)
        member_id = wix_service.extract_member_id_from_access_token(access_token)
        if not member_id:
            member_info = wix_service.get_current_member(access_token)
            member_id = (
                (member_info.get("member") or {}).get("id")
                or member_info.get("id")
            )
        if not member_id:
            raise HTTPException(status_code=400, detail="Unable to resolve member_id from token")

        result = wix_service.create_blog_post(
            access_token=access_token,
            title=payload.get("title") or "Untitled",
            content=payload.get("content") or "",
            cover_image_url=payload.get("cover_image_url"),
            category_ids=payload.get("category_ids") or None,
            tag_ids=payload.get("tag_ids") or None,
            publish=bool(payload.get("publish", True)),
            member_id=member_id,
        )

        return {
            "success": True,
            "post_id": (result.get("draftPost") or result.get("post") or {}).get("id"),
            "url": (result.get("draftPost") or result.get("post") or {}).get("url"),
            "message": "Blog post published to Wix",
            "raw": result,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TEST: Real publish failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/category")
async def test_create_category(request: WixCreateCategoryRequest) -> Dict[str, Any]:
    try:
        result = wix_service.create_category(
            access_token=request.access_token,
            label=request.label,
            description=request.description,
            language=request.language,
        )
        return {"success": True, "category": result.get("category", {}), "raw": result}
    except Exception as e:
        logger.error(f"TEST: Create category failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/tag")
async def test_create_tag(request: WixCreateTagRequest) -> Dict[str, Any]:
    try:
        result = wix_service.create_tag(
            access_token=request.access_token,
            label=request.label,
            language=request.language,
        )
        return {"success": True, "tag": result.get("tag", {}), "raw": result}
    except Exception as e:
        logger.error(f"TEST: Create tag failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
