"""
Wix Integration API Routes

Handles Wix authentication, connection status, and blog publishing.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from typing import Dict, Any, Optional
from loguru import logger
from pydantic import BaseModel

from services.wix_service import WixService
from services.integrations.wix_oauth import WixOAuthService
from middleware.auth_middleware import get_current_user
import os

router = APIRouter(prefix="/api/wix", tags=["Wix Integration"])

# Initialize Wix service
wix_service = WixService()

# Initialize Wix OAuth service for token storage
wix_oauth_service = WixOAuthService(db_path=os.path.abspath("alwrity.db"))


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
        user_id = current_user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        # Exchange code for tokens
        tokens = wix_service.exchange_code_for_tokens(request.code)
        
        # Get site information to extract site_id and member_id
        site_info = wix_service.get_site_info(tokens['access_token'])
        site_id = site_info.get('siteId') or site_info.get('site_id')
        
        # Extract member_id from token if possible
        member_id = None
        try:
            member_id = wix_service.extract_member_id_from_access_token(tokens['access_token'])
        except Exception:
            pass
        
        # Check permissions
        permissions = wix_service.check_blog_permissions(tokens['access_token'])
        
        # Store tokens securely in database
        stored = wix_oauth_service.store_tokens(
            user_id=user_id,
            access_token=tokens['access_token'],
            refresh_token=tokens.get('refresh_token'),
            expires_in=tokens.get('expires_in'),
            token_type=tokens.get('token_type', 'Bearer'),
            scope=tokens.get('scope'),
            site_id=site_id,
            member_id=member_id
        )
        
        if not stored:
            logger.warning(f"Failed to store Wix tokens for user {user_id}, but OAuth succeeded")
        
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


@router.get("/callback")
async def handle_oauth_callback_get(code: str, state: Optional[str] = None, request: Request = None, current_user: dict = Depends(get_current_user)):
    """HTML callback page for Wix OAuth that exchanges code and notifies opener via postMessage."""
    try:
        tokens = wix_service.exchange_code_for_tokens(code)
        site_info = wix_service.get_site_info(tokens['access_token'])
        permissions = wix_service.check_blog_permissions(tokens['access_token'])
        
        # Store tokens in database if we have user_id
        user_id = current_user.get('id') if current_user else None
        if user_id:
            site_id = site_info.get('siteId') or site_info.get('site_id')
            member_id = None
            try:
                member_id = wix_service.extract_member_id_from_access_token(tokens['access_token'])
            except Exception:
                pass
            
            stored = wix_oauth_service.store_tokens(
                user_id=user_id,
                access_token=tokens['access_token'],
                refresh_token=tokens.get('refresh_token'),
                expires_in=tokens.get('expires_in'),
                token_type=tokens.get('token_type', 'Bearer'),
                scope=tokens.get('scope'),
                site_id=site_id,
                member_id=member_id
            )
            if not stored:
                logger.warning(f"Failed to store Wix tokens for user {user_id} in GET callback")

        # Build success payload for postMessage
        payload = {
            "type": "WIX_OAUTH_SUCCESS",
            "success": True,
            "tokens": {
                "access_token": tokens['access_token'],
                "refresh_token": tokens.get('refresh_token'),
                "expires_in": tokens.get('expires_in'),
                "token_type": tokens.get('token_type', 'Bearer')
            },
            "site_info": site_info,
            "permissions": permissions
        }

        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Wix Connected</title></head>
        <body>
          <script>
            (function() {{
              try {{
                var payload = {payload};
                (window.opener || window.parent).postMessage(payload, '*');
              }} catch (e) {{}}
              window.close();
            }})();
          </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html, headers={
            "Cross-Origin-Opener-Policy": "unsafe-none",
            "Cross-Origin-Embedder-Policy": "unsafe-none"
        })
    except Exception as e:
        logger.error(f"Wix OAuth GET callback failed: {e}")
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Wix Connection Failed</title></head>
        <body>
          <script>
            (function() {{
              try {{
                (window.opener || window.parent).postMessage({{ type: 'WIX_OAUTH_ERROR', success: false, error: '{str(e)}' }}, '*');
              }} catch (e) {{}}
              window.close();
            }})();
          </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html, headers={
            "Cross-Origin-Opener-Policy": "unsafe-none",
            "Cross-Origin-Embedder-Policy": "unsafe-none"
        })


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
        # Check if user has Wix tokens stored in sessionStorage (frontend approach)
        # This is a simplified check - in production you'd store tokens in database
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


@router.get("/status")
async def get_wix_status(current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get Wix connection status (similar to GSC/WordPress pattern)
    Note: Wix tokens are stored in frontend sessionStorage, so we can't directly check them here.
    The frontend will check sessionStorage and update the UI accordingly.
    """
    try:
        # Since Wix tokens are stored in frontend sessionStorage (not backend database),
        # we return a default response. The frontend will check sessionStorage directly.
        return {
            "connected": False,
            "sites": [],
            "total_sites": 0,
            "error": "Wix connection status managed by frontend sessionStorage"
        }
    except Exception as e:
        logger.error(f"Failed to get Wix status: {e}")
        return {
            "connected": False,
            "sites": [],
            "total_sites": 0,
            "error": str(e)
        }


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


@router.post("/refresh-token")
async def refresh_wix_token(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Refresh Wix access token using refresh token
    
    Args:
        request: Dict containing refresh_token
        
    Returns:
        New token information with access_token, refresh_token, expires_in
    """
    try:
        refresh_token = request.get("refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Missing refresh_token")
        
        # Refresh the token
        new_tokens = wix_service.refresh_access_token(refresh_token)
        
        return {
            "success": True,
            "access_token": new_tokens.get("access_token"),
            "refresh_token": new_tokens.get("refresh_token"),
            "expires_in": new_tokens.get("expires_in"),
            "token_type": new_tokens.get("token_type", "Bearer")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to refresh Wix token: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to refresh token: {str(e)}")


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

        # Extract SEO metadata if provided
        seo_metadata = payload.get("seo_metadata")
        
        # Extract category/tag IDs or names
        # Can be either:
        # - IDs: List of UUID strings
        # - Names: List of name strings (will be looked up/created)
        category_ids = payload.get("category_ids") or payload.get("category_names")
        tag_ids = payload.get("tag_ids") or payload.get("tag_names")
        
        # If SEO metadata has categories/tags but they weren't explicitly provided, use them
        if seo_metadata:
            if not category_ids and seo_metadata.get("blog_categories"):
                category_ids = seo_metadata.get("blog_categories")
            if not tag_ids and seo_metadata.get("blog_tags"):
                tag_ids = seo_metadata.get("blog_tags")
        
        result = wix_service.create_blog_post(
            access_token=access_token,
            title=payload.get("title") or "Untitled",
            content=payload.get("content") or "",
            cover_image_url=payload.get("cover_image_url"),
            category_ids=category_ids,
            tag_ids=tag_ids,
            publish=bool(payload.get("publish", True)),
            member_id=member_id,
            seo_metadata=seo_metadata,
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
