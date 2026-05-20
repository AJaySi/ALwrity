"""
Wix Integration API Routes

Handles Wix authentication, connection status, and blog publishing.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from typing import Dict, Any, Optional
from loguru import logger
from pydantic import BaseModel
import uuid

from services.wix_service import WixService
from services.integrations.wix_oauth import WixOAuthService
from middleware.auth_middleware import get_current_user
import os
import json
from urllib.parse import urlparse
import requests

router = APIRouter(prefix="/api/wix", tags=["Wix Integration"])
qa_router = APIRouter(prefix="/api/wix/test", tags=["Wix Integration QA"])


def _sanitize_error_message(error: Exception) -> str:
    return " ".join(str(error).split())[:500]


def _normalize_origin(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}"


def _trusted_frontend_origin() -> Optional[str]:
    origins_env = os.getenv("OAUTH_CALLBACK_ALLOWED_ORIGINS", "")
    configured_origins = [
        _normalize_origin(origin)
        for origin in origins_env.split(",")
        if origin.strip()
    ]
    configured_origins = [origin for origin in configured_origins if origin]
    if configured_origins:
        return configured_origins[0]
    return _normalize_origin(os.getenv("FRONTEND_URL"))


def _build_oauth_callback_html(payload: Dict[str, Any], title: str, heading: str, message: str) -> str:
    trusted_origin = _trusted_frontend_origin()
    payload_json = json.dumps(payload)
    target_origin_json = json.dumps(trusted_origin or "")
    heading_html = heading.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    message_html = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>{title}</title></head>
    <body>
      <h1>{heading_html}</h1>
      <p>{message_html}</p>
      <script>
        (function() {{
          var payload = {payload_json};
          var targetOrigin = {target_origin_json};
          var destination = window.opener || window.parent;
          if (destination && targetOrigin) {{
            try {{
              destination.postMessage(payload, targetOrigin);
              window.close();
              return;
            }} catch (_e) {{}}
          }}
        }})();
      </script>
    </body>
    </html>
    """

# Initialize Wix service
wix_service = WixService()

# Initialize Wix OAuth service for token storage
wix_oauth_service = WixOAuthService()


def _get_current_user_id(current_user: dict) -> str:
    user_id = current_user.get("id") if current_user else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing authenticated user context")
    return user_id


def _map_wix_error(exc: Exception, fallback: str = "Wix API request failed") -> HTTPException:
    if isinstance(exc, HTTPException):
        return exc
    if isinstance(exc, requests.HTTPError):
        status = exc.response.status_code if exc.response is not None else None
        if status == 401:
            return HTTPException(status_code=401, detail="Wix authentication expired or invalid")
        if status == 403:
            return HTTPException(status_code=403, detail="Insufficient Wix permissions/scope")
        return HTTPException(status_code=502, detail=fallback)
    if isinstance(exc, requests.RequestException):
        return HTTPException(status_code=502, detail=fallback)
    return HTTPException(status_code=500, detail=str(exc))


def _resolve_valid_wix_token(current_user: dict) -> Dict[str, Any]:
    user_id = _get_current_user_id(current_user)
    tokens = wix_oauth_service.get_user_tokens(user_id)
    if tokens:
        return tokens[0]

    token_status = wix_oauth_service.get_user_token_status(user_id)
    expired_tokens = token_status.get("expired_tokens", [])
    if not expired_tokens:
        raise HTTPException(status_code=401, detail="Wix account not connected")

    latest = expired_tokens[0]
    refresh_token = latest.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Wix token expired and cannot be refreshed")
    try:
        refreshed = wix_service.refresh_access_token(refresh_token)
    except Exception as exc:
        raise _map_wix_error(exc, "Failed to refresh Wix access token")

    wix_oauth_service.update_tokens(
        user_id=user_id,
        access_token=refreshed.get("access_token"),
        refresh_token=refreshed.get("refresh_token", refresh_token),
        expires_in=refreshed.get("expires_in"),
    )

    return {
        "access_token": refreshed.get("access_token"),
        "refresh_token": refreshed.get("refresh_token", refresh_token),
        "member_id": latest.get("member_id"),
        "site_id": latest.get("site_id"),
    }


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
    category_names: Optional[list] = None
    tag_ids: Optional[list] = None
    tag_names: Optional[list] = None
    publish: bool = True
    access_token: Optional[str] = None
    member_id: Optional[str] = None
    seo_metadata: Optional[Dict[str, Any]] = None
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


def _is_wix_test_mode_enabled() -> bool:
    return os.getenv("WIX_TEST_ROUTES_ENABLED", "false").lower() in {"1", "true", "yes", "on"}


def _is_admin_user(current_user: Dict[str, Any]) -> bool:
    email = (current_user.get("email") or "").lower()
    role = current_user.get("role")
    public_metadata = current_user.get("public_metadata")
    if isinstance(public_metadata, dict):
        role = public_metadata.get("role") or role

    admin_emails = {
        e.strip().lower()
        for e in os.getenv("ADMIN_EMAILS", "").split(",")
        if e.strip()
    }
    admin_domain = (os.getenv("ADMIN_EMAIL_DOMAIN") or "").lower().strip()

    return bool(
        role == "admin"
        or (email and email in admin_emails)
        or (email and admin_domain and email.endswith(f"@{admin_domain}"))
    )


def _require_wix_test_access(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    if not _is_wix_test_mode_enabled():
        raise HTTPException(status_code=404, detail="Not found")
    if not _is_admin_user(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/auth/url")
async def get_authorization_url(state: Optional[str] = None, current_user: dict = Depends(get_current_user)) -> Dict[str, str]:
    """
    Get Wix OAuth authorization URL
    
    Args:
        state: Optional state parameter for security
        
    Returns:
        Authorization URL
    """
    try:
        user_id = current_user.get('id') if current_user else None
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")

        oauth_state = state or str(uuid.uuid4())
        oauth_payload = wix_service.get_authorization_url(oauth_state)
        saved = wix_oauth_service.store_pkce_verifier(
            user_id=user_id,
            state=oauth_state,
            code_verifier=oauth_payload["code_verifier"],
            ttl_seconds=600
        )
        if not saved:
            raise HTTPException(status_code=500, detail="Failed to persist OAuth verifier state")
        return {"authorization_url": oauth_payload["authorization_url"], "state": oauth_state}
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
        
        if not request.state:
            raise HTTPException(status_code=400, detail="Missing OAuth state")
        code_verifier = wix_oauth_service.consume_pkce_verifier(user_id=user_id, state=request.state)
        if not code_verifier:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired OAuth state. Please restart Wix connection."
            )
        # Exchange code for tokens
        tokens = wix_service.exchange_code_for_tokens(request.code, code_verifier=code_verifier)
        
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
        user_id = current_user.get('id') if current_user else None
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        if not state:
            raise HTTPException(status_code=400, detail="Missing OAuth state")
        code_verifier = wix_oauth_service.consume_pkce_verifier(user_id=user_id, state=state)
        if not code_verifier:
            raise HTTPException(status_code=400, detail="Invalid or expired OAuth state. Please reconnect Wix.")
        tokens = wix_service.exchange_code_for_tokens(code, code_verifier=code_verifier)
        site_info = wix_service.get_site_info(tokens['access_token'])
        permissions = wix_service.check_blog_permissions(tokens['access_token'])
        
        # Store tokens in database if we have user_id
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

        html = _build_oauth_callback_html(
            payload=payload,
            title="Wix Connected",
            heading="Connection Successful",
            message="Your Wix account was connected. You can close this window."
        )
        return HTMLResponse(content=html, headers={
            "Cross-Origin-Opener-Policy": "unsafe-none",
            "Cross-Origin-Embedder-Policy": "unsafe-none"
        })
    except Exception as e:
        logger.error(f"Wix OAuth GET callback failed: {e}")
        html = _build_oauth_callback_html(
            payload={"type": "WIX_OAUTH_ERROR", "success": False, "error": _sanitize_error_message(e)},
            title="Wix Connection Failed",
            heading="Connection Failed",
            message="There was an issue connecting your Wix account. You can close this window and try again."
        )
        return HTMLResponse(content=html, headers={
            "Cross-Origin-Opener-Policy": "unsafe-none",
            "Cross-Origin-Embedder-Policy": "unsafe-none"
        })


@router.get("/connection/status")
async def get_connection_status(current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Check Wix connection status and permissions.
    Returns connected: false when no tokens are stored (instead of 401).
    """
    try:
        token_info = _resolve_valid_wix_token(current_user)
        access_token = token_info["access_token"]
        site_info = wix_service.get_site_info(access_token)
        permissions = wix_service.check_blog_permissions(access_token)
        return {
            "connected": True,
            "has_permissions": permissions.get("has_permissions", False),
            "site_info": site_info,
            "permissions": permissions
        }
    except HTTPException as e:
        if e.status_code == 401:
            return {"connected": False, "has_permissions": False}
        raise
    except Exception as e:
        logger.error(f"Failed to check connection status: {e}")
        return {"connected": False, "has_permissions": False}


@router.get("/status")
async def get_wix_status(current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get Wix connection status (similar to GSC/WordPress pattern)
    Note: Wix tokens are stored in frontend sessionStorage, so we can't directly check them here.
    The frontend will check sessionStorage and update the UI accordingly.
    """
    try:
        token_info = _resolve_valid_wix_token(current_user)
        site_info = wix_service.get_site_info(token_info["access_token"])
        return {
            "connected": True,
            "sites": [site_info],
            "total_sites": 1,
            "site_info": site_info
        }
    except Exception as e:
        logger.error(f"Failed to get Wix status: {e}")
        mapped = _map_wix_error(e, "Failed to get Wix status")
        raise mapped


@router.post("/publish")
async def publish_to_wix(request: WixPublishRequest, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Publish blog post to Wix using server-stored OAuth tokens.
    
    The backend resolves the access token from the database (via
    _resolve_valid_wix_token), so callers do NOT need to pass
    access_token unless they want to override the stored one.
    """
    try:
        if request.access_token:
            from services.integrations.wix.utils import normalize_token_string
            access_token = normalize_token_string(request.access_token)
        else:
            try:
                token_info = _resolve_valid_wix_token(current_user)
                access_token = token_info["access_token"]
            except HTTPException:
                access_token = None

        if not access_token:
            return {
                "success": False,
                "error": "Wix account not connected. Connect your Wix account first.",
            }

        member_id = request.member_id
        if not member_id:
            member_id = wix_service.extract_member_id_from_access_token(access_token)
        if not member_id:
            member_info = wix_service.get_current_member(access_token)
            member_id = (member_info.get("member") or {}).get("id") or member_info.get("id")
        if not member_id:
            return {
                "success": False,
                "error": "Unable to resolve Wix member ID. Please reconnect your Wix account.",
            }

        # Resolve categories: accept IDs or names (looked up/created)
        category_ids = request.category_ids or request.category_names
        tag_ids = request.tag_ids or request.tag_names

        seo_metadata = request.seo_metadata
        if seo_metadata:
            if not category_ids and seo_metadata.get("blog_categories"):
                category_ids = seo_metadata.get("blog_categories")
            if not tag_ids and seo_metadata.get("blog_tags"):
                tag_ids = seo_metadata.get("blog_tags")

        # Ensure category_ids and tag_ids are lists of strings (not ints)
        if category_ids:
            category_ids = [str(c) for c in category_ids if c is not None]
        if tag_ids:
            tag_ids = [str(t) for t in tag_ids if t is not None]

        result = wix_service.create_blog_post(
            access_token=access_token,
            title=request.title,
            content=request.content,
            cover_image_url=request.cover_image_url,
            category_ids=category_ids,
            tag_ids=tag_ids,
            publish=request.publish,
            member_id=member_id,
            seo_metadata=seo_metadata,
        )
        post = result.get("draftPost") or result.get("post") or result
        raw_url = post.get("url")
        if isinstance(raw_url, dict):
            post_url = raw_url.get("base", "").rstrip("/") + "/" + raw_url.get("path", "").lstrip("/")
        elif isinstance(raw_url, str):
            post_url = raw_url
        else:
            post_url = None
        return {
            "success": True,
            "post_id": str(post.get("id", "")),
            "url": post_url,
            "publish_state": "PUBLISHED" if request.publish else "DRAFT"
        }
    except Exception as e:
        logger.error(f"Failed to publish to Wix: {e}")
        raise _map_wix_error(e, "Failed to publish to Wix")


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
        token_info = _resolve_valid_wix_token(current_user)
        categories = wix_service.get_blog_categories(token_info["access_token"])
        return {
            "success": True,
            "categories": categories
        }
    except Exception as e:
        logger.error(f"Failed to get blog categories: {e}")
        raise _map_wix_error(e, "Failed to fetch Wix blog categories")


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
        token_info = _resolve_valid_wix_token(current_user)
        tags = wix_service.get_blog_tags(token_info["access_token"])
        return {
            "success": True,
            "tags": tags
        }
    except Exception as e:
        logger.error(f"Failed to get blog tags: {e}")
        raise _map_wix_error(e, "Failed to fetch Wix blog tags")


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
        user_id = _get_current_user_id(current_user)
        token_status = wix_oauth_service.get_user_token_status(user_id)
        all_tokens = token_status.get("active_tokens", []) + token_status.get("expired_tokens", [])
        for token in all_tokens:
            token_id = token.get("id")
            if token_id:
                wix_oauth_service.revoke_token(user_id, token_id)
        return {
            "success": True,
            "connected": False,
            "message": "Wix account disconnected successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to disconnect Wix: {e}")
        raise _map_wix_error(e, "Failed to disconnect Wix account")


# =============================================================================
# TEST ENDPOINTS - No authentication required for testing
# =============================================================================

@qa_router.get("/connection/status")
async def get_test_connection_status(_: Dict[str, Any] = Depends(_require_wix_test_access)) -> WixConnectionStatus:
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


@qa_router.get("/auth/url")
async def get_test_authorization_url(state: Optional[str] = None, _: Dict[str, Any] = Depends(_require_wix_test_access)) -> Dict[str, str]:
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
                "url": (
                    "https://www.wix.com/oauth/access?client_id=YOUR_CLIENT_ID"
                    "&redirect_uri=http://localhost:3000/wix/callback"
                    "&response_type=code&scope="
                    "BLOG.CREATE-DRAFT,BLOG.PUBLISH-POST,BLOG.READ-CATEGORY,"
                    "BLOG.CREATE-CATEGORY,BLOG.READ-TAG,BLOG.CREATE-TAG,"
                    "MEDIA.SITE_MEDIA_FILES_IMPORT"
                    "&code_challenge=test&code_challenge_method=S256"
                ),
                "state": state or "test_state",
                "message": "WIX_CLIENT_ID not configured. Please set it in your .env file to get a real authorization URL."
            }
        
        auth_url = wix_service.get_authorization_url(state)
        return {"url": auth_url, "state": state or "test_state"}
    except Exception as e:
        logger.error(f"TEST: Failed to generate authorization URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@qa_router.post("/publish")
async def test_publish_to_wix(request: WixPublishRequest, _: Dict[str, Any] = Depends(_require_wix_test_access)) -> Dict[str, Any]:
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


@qa_router.post("/publish/real")
async def test_publish_real(payload: Dict[str, Any], _: Dict[str, Any] = Depends(_require_wix_test_access)) -> Dict[str, Any]:
    """
    TEST ENDPOINT: Perform a real publish to Wix using a provided access token.

    Notes:
      - Expects request.access_token from the frontend's Wix SDK tokens
      - Derives member_id server-side (required by Wix for third-party apps)
    """
    try:
        # Normalize access_token from payload (could be string, dict, or other format)
        from services.integrations.wix.utils import normalize_token_string
        raw_access_token = payload.get("access_token")
        if not raw_access_token:
            raise HTTPException(status_code=400, detail="Missing access_token")
        
        # Normalize token to string (handles dict with accessToken.value, int, etc.)
        access_token = normalize_token_string(raw_access_token)
        if not access_token:
            # Fallback: try to convert to string directly
            access_token = str(raw_access_token).strip()
            if not access_token or access_token == "None":
                raise HTTPException(status_code=400, detail="Invalid access_token format")

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


@qa_router.post("/category")
async def test_create_category(request: WixCreateCategoryRequest, _: Dict[str, Any] = Depends(_require_wix_test_access)) -> Dict[str, Any]:
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


@qa_router.post("/tag")
async def test_create_tag(request: WixCreateTagRequest, _: Dict[str, Any] = Depends(_require_wix_test_access)) -> Dict[str, Any]:
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
