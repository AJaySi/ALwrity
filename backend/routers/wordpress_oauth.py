"""
WordPress OAuth2 Routes
Handles WordPress.com OAuth2 authentication flow.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from typing import Dict, Any, Optional
from pydantic import BaseModel
from loguru import logger
import json
import os
from urllib.parse import urlparse

from services.integrations.wordpress_oauth import WordPressOAuthService
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/wp", tags=["WordPress OAuth"])

# Initialize OAuth service
oauth_service = WordPressOAuthService()


def _sanitize_string(value: Any, max_len: int = 500) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())[:max_len]


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


def _oauth_callback_html(payload: Dict[str, Any], title: str, heading: str, message: str) -> str:
    payload_json = json.dumps(payload)
    target_origin = json.dumps(_trusted_frontend_origin() or "")
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
          var targetOrigin = {target_origin};
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

# Pydantic Models
class WordPressOAuthResponse(BaseModel):
    auth_url: str
    state: str

class WordPressCallbackResponse(BaseModel):
    success: bool
    message: str
    blog_url: Optional[str] = None
    blog_id: Optional[str] = None

class WordPressStatusResponse(BaseModel):
    connected: bool
    sites: list
    total_sites: int

@router.get("/auth/url", response_model=WordPressOAuthResponse)
async def get_wordpress_auth_url(
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Get WordPress OAuth2 authorization URL."""
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID not found.")
        
        auth_data = oauth_service.generate_authorization_url(user_id)
        if not auth_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="WordPress OAuth is not properly configured. Please check that WORDPRESS_CLIENT_ID and WORDPRESS_CLIENT_SECRET environment variables are set with valid WordPress.com application credentials."
            )
        
        return WordPressOAuthResponse(**auth_data)
        
    except Exception as e:
        logger.error(f"Error generating WordPress OAuth URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate WordPress OAuth URL."
        )

@router.get("/callback")
async def handle_wordpress_callback(
    request: Request,
    code: str = Query(..., description="Authorization code from WordPress"),
    state: str = Query(..., description="State parameter for security"),
    error: Optional[str] = Query(None, description="Error from WordPress OAuth")
):
    """Handle WordPress OAuth2 callback."""
    try:
        # Check if JSON response is requested
        wants_json = request.headers.get("accept") == "application/json" or request.query_params.get("format") == "json"

        if error:
            logger.error(f"WordPress OAuth error: {error}")
            if wants_json:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"success": False, "error": error}
                )
            html_content = _oauth_callback_html(
                payload={"type": "WPCOM_OAUTH_ERROR", "success": False, "error": _sanitize_string(error)},
                title="WordPress.com Connection Failed",
                heading="Connection Failed",
                message="There was an error connecting to WordPress.com. You can close this window and try again."
            )
            return HTMLResponse(content=html_content, headers={
                "Cross-Origin-Opener-Policy": "unsafe-none",
                "Cross-Origin-Embedder-Policy": "unsafe-none"
            })
        
        if not code or not state:
            logger.error("Missing code or state parameter in WordPress OAuth callback")
            if wants_json:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"success": False, "error": "Missing parameters"}
                )
            html_content = _oauth_callback_html(
                payload={"type": "WPCOM_OAUTH_ERROR", "success": False, "error": "Missing parameters"},
                title="WordPress.com Connection Failed",
                heading="Connection Failed",
                message="Missing required parameters. You can close this window and try again."
            )
            return HTMLResponse(content=html_content, headers={
                "Cross-Origin-Opener-Policy": "unsafe-none",
                "Cross-Origin-Embedder-Policy": "unsafe-none"
            })
        
        # Exchange code for token
        result = oauth_service.handle_oauth_callback(code, state)
        
        if not result or not result.get('success'):
            logger.error("Failed to exchange WordPress OAuth code for token")
            if wants_json:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"success": False, "error": "Token exchange failed"}
                )
            html_content = _oauth_callback_html(
                payload={"type": "WPCOM_OAUTH_ERROR", "success": False, "error": "Token exchange failed"},
                title="WordPress.com Connection Failed",
                heading="Connection Failed",
                message="Failed to exchange authorization code for access token. You can close this window and try again."
            )
            return HTMLResponse(content=html_content)
        
        # Return success page with postMessage script
        blog_url = result.get('blog_url', '')
        blog_id = result.get('blog_id', '')
        
        if wants_json:
            return JSONResponse(
                content={
                    "success": True,
                    "blog_url": blog_url,
                    "blog_id": blog_id,
                    "sites": [{"blog_url": blog_url, "blog_id": blog_id}] # Simplified for now
                }
            )

        html_content = _oauth_callback_html(
            payload={
                "type": "WPCOM_OAUTH_SUCCESS",
                "success": True,
                "blogUrl": _sanitize_string(blog_url, 300),
                "blogId": _sanitize_string(blog_id, 128)
            },
            title="WordPress.com Connection Successful",
            heading="Connection Successful",
            message="Your WordPress.com site has been connected successfully. You can close this window now."
        )

        return HTMLResponse(content=html_content, headers={
            "Cross-Origin-Opener-Policy": "unsafe-none",
            "Cross-Origin-Embedder-Policy": "unsafe-none"
        })
        
    except Exception as e:
        logger.error(f"Error handling WordPress OAuth callback: {e}")
        html_content = _oauth_callback_html(
            payload={"type": "WPCOM_OAUTH_ERROR", "success": False, "error": "Callback error"},
            title="WordPress.com Connection Failed",
            heading="Connection Failed",
            message="An unexpected error occurred during connection. You can close this window and try again."
        )
        return HTMLResponse(content=html_content, headers={
            "Cross-Origin-Opener-Policy": "unsafe-none",
            "Cross-Origin-Embedder-Policy": "unsafe-none"
        })

@router.get("/status", response_model=WordPressStatusResponse)
async def get_wordpress_oauth_status(
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Get WordPress OAuth connection status."""
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID not found.")
        
        status_data = oauth_service.get_connection_status(user_id)
        return WordPressStatusResponse(**status_data)
        
    except Exception as e:
        logger.error(f"Error getting WordPress OAuth status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get WordPress connection status."
        )

@router.delete("/disconnect/{token_id}")
async def disconnect_wordpress_site(
    token_id: int,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Disconnect a WordPress site."""
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID not found.")
        
        success = oauth_service.revoke_token(user_id, token_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="WordPress token not found or could not be disconnected."
            )
        
        return {"success": True, "message": f"WordPress site disconnected successfully."}
        
    except Exception as e:
        logger.error(f"Error disconnecting WordPress site: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disconnect WordPress site."
        )

@router.get("/health")
async def wordpress_oauth_health():
    """WordPress OAuth health check."""
    return {
        "status": "healthy",
        "service": "wordpress_oauth",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }
