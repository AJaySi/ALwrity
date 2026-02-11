"""
Unified OAuth Router Architecture
Single entry point for all OAuth operations with dynamic provider routing,
standardized security, and consistent API patterns.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Dict, Any, Optional
from pydantic import BaseModel
from loguru import logger

from services.integrations.registry import get_provider
from services.oauth_redirects import get_trusted_origins_for_redirect
from middleware.auth_middleware import get_current_user


# Initialize unified router
router = APIRouter(prefix="/oauth", tags=["OAuth"])


# Pydantic Models
class OAuthAuthUrlResponse(BaseModel):
    """Response model for OAuth authorization URL."""
    provider_key: str
    display_name: str
    auth_url: str
    state: str
    trusted_origins: list[str]


class OAuthCallbackResponse(BaseModel):
    """Response model for OAuth callback."""
    success: bool
    provider_key: str
    display_name: str
    connected: Optional[bool] = None
    message: str
    error: Optional[str] = None


class OAuthStatusResponse(BaseModel):
    """Response model for OAuth status."""
    provider_key: str
    display_name: str
    connected: bool
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class OAuthProvidersResponse(BaseModel):
    """Response model for available providers."""
    providers: list[Dict[str, Any]]


def _sanitize_response_data(data: Dict[str, Any], provider_key: str) -> Dict[str, Any]:
    """
    Sanitize response data to remove sensitive token information.
    
    Args:
        data: Raw response data
        provider_key: Provider identifier for logging
        
    Returns:
        Dict[str, Any]: Sanitized response data
    """
    # Remove sensitive token fields
    sensitive_fields = {
        'access_token', 'refresh_token', 'accessToken', 'refreshToken',
        'token_secret', 'client_secret', 'private_key'
    }
    
    def remove_sensitive(obj):
        if isinstance(obj, dict):
            return {
                k: remove_sensitive(v) if k not in sensitive_fields else '***REDACTED***'
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [remove_sensitive(item) for item in obj]
        else:
            return obj
    
    try:
        sanitized = remove_sensitive(data)
        logger.debug(f"Sanitized response data for {provider_key}")
        return sanitized
    except Exception as e:
        logger.error(f"Failed to sanitize response data for {provider_key}: {e}")
        # Return safe fallback
        return {
            'error': 'Response sanitization failed',
            'details': str(e)
        }


@router.get("/providers", response_model=OAuthProvidersResponse)
async def get_available_providers(user: dict = Depends(get_current_user)):
    """
    Get list of available OAuth providers.
    
    Returns all registered OAuth providers with their display names and current connection status.
    """
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Get all available providers
        from services.integrations.registry import get_all_providers
        all_providers = get_all_providers()
        
        providers_info = []
        
        for provider_key, provider in all_providers.items():
            # Get connection status for this provider
            try:
                status = await provider.get_connection_status(user_id)
                providers_info.append({
                    "key": provider_key,
                    "display_name": provider.display_name,
                    "connected": status.connected,
                    "details": status.details,
                    "error": status.error
                })
            except Exception as e:
                logger.error(f"Failed to get status for {provider_key}: {e}")
                providers_info.append({
                    "key": provider_key,
                    "display_name": provider.display_name,
                    "connected": False,
                    "error": str(e)
                })
        
        return OAuthProvidersResponse(providers=providers_info)
        
    except Exception as e:
        logger.error(f"Failed to get providers list: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve available providers"
        )


@router.get("/{provider_key}/auth", response_model=OAuthAuthUrlResponse)
async def get_provider_auth_url(
    provider_key: str,
    user: dict = Depends(get_current_user)
):
    """
    Get OAuth authorization URL for a specific provider.
    
    Supports all registered OAuth providers with consistent error handling
    and security validation.
    """
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Get provider
        provider = get_provider(provider_key)
        if not provider:
            raise HTTPException(
                status_code=404,
                detail=f"Provider '{provider_key}' not supported"
            )
        
        # Generate authorization URL
        auth_payload = await provider.get_auth_url(user_id)
        
        if not auth_payload.auth_url:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate {provider.display_name} authorization URL"
            )
        
        # Get trusted origins for this provider
        try:
            trusted_origins = get_trusted_origins_for_redirect(
                provider.display_name, 
                f"{provider_key.upper()}_REDIRECT_URI"
            )
        except Exception as e:
            logger.warning(f"Failed to get trusted origins for {provider_key}: {e}")
            trusted_origins = []
        
        logger.info(f"Generated OAuth URL for {provider_key}, user {user_id}")
        
        return OAuthAuthUrlResponse(
            provider_key=provider_key,
            display_name=provider.display_name,
            auth_url=auth_payload.auth_url,
            state=auth_payload.state,
            trusted_origins=trusted_origins
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth URL generation failed for {provider_key}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate {provider_key} authorization URL"
        )


@router.post("/{provider_key}/callback", response_model=OAuthCallbackResponse)
async def handle_provider_callback(
    provider_key: str,
    code: str,
    state: str,
    user: dict = Depends(get_current_user)
):
    """
    Handle OAuth callback for a specific provider.
    
    Processes OAuth callbacks with standardized validation, token storage,
    and secure response formatting.
    """
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Get provider
        provider = get_provider(provider_key)
        if not provider:
            raise HTTPException(
                status_code=404,
                detail=f"Provider '{provider_key}' not supported"
            )
        
        # Handle callback
        result = await provider.handle_callback(code, state)
        
        if result.success:
            logger.info(f"Successfully connected {provider_key} for user {user_id}")
            return OAuthCallbackResponse(
                success=True,
                provider_key=provider_key,
                display_name=provider.display_name,
                connected=True,
                message=f"Successfully connected to {provider.display_name}"
            )
        else:
            logger.error(f"Failed to connect {provider_key} for user {user_id}: {result.error}")
            return OAuthCallbackResponse(
                success=False,
                provider_key=provider_key,
                display_name=provider.display_name,
                connected=False,
                message=f"Failed to connect to {provider.display_name}",
                error=result.error
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Callback handling failed for {provider_key}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to handle {provider_key} OAuth callback"
        )


@router.get("/{provider_key}/status", response_model=OAuthStatusResponse)
async def get_provider_status(
    provider_key: str,
    user: dict = Depends(get_current_user)
):
    """
    Get connection status for a specific provider.
    
    Returns sanitized connection status with no sensitive token information.
    """
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Get provider
        provider = get_provider(provider_key)
        if not provider:
            raise HTTPException(
                status_code=404,
                detail=f"Provider '{provider_key}' not supported"
            )
        
        # Get connection status
        status = await provider.get_connection_status(user_id)
        
        # Sanitize response data
        sanitized_details = None
        if status.details:
            sanitized_details = _sanitize_response_data(status.details, provider_key)
        
        logger.debug(f"Retrieved status for {provider_key}, user {user_id}: connected={status.connected}")
        
        return OAuthStatusResponse(
            provider_key=provider_key,
            display_name=provider.display_name,
            connected=status.connected,
            details=sanitized_details,
            error=status.error
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check failed for {provider_key}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check {provider_key} connection status"
        )


@router.post("/{provider_key}/refresh")
async def refresh_provider_token(
    provider_key: str,
    user: dict = Depends(get_current_user)
):
    """
    Refresh OAuth token for a specific provider.
    
    Supports token refresh with standardized error handling and logging.
    """
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Get provider
        provider = get_provider(provider_key)
        if not provider:
            raise HTTPException(
                status_code=404,
                detail=f"Provider '{provider_key}' not supported"
            )
        
        # Check if provider supports token refresh
        if not hasattr(provider, 'refresh_token'):
            raise HTTPException(
                status_code=400,
                detail=f"Provider '{provider_key}' does not support token refresh"
            )
        
        # Refresh token
        result = await provider.refresh_token(user_id)
        
        if result.success:
            logger.info(f"Successfully refreshed {provider_key} token for user {user_id}")
            return {
                "success": True,
                "provider_key": provider_key,
                "display_name": provider.display_name,
                "message": f"Successfully refreshed {provider.display_name} token"
            }
        else:
            logger.error(f"Failed to refresh {provider_key} token for user {user_id}: {result.error}")
            return {
                "success": False,
                "provider_key": provider_key,
                "display_name": provider.display_name,
                "message": f"Failed to refresh {provider.display_name} token",
                "error": result.error
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed for {provider_key}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh {provider_key} token"
        )


@router.post("/{provider_key}/disconnect")
async def disconnect_provider(
    provider_key: str,
    user: dict = Depends(get_current_user)
):
    """
    Disconnect OAuth connection for a specific provider.
    
    Removes tokens and revokes access with standardized cleanup.
    """
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        # Get provider
        provider = get_provider(provider_key)
        if not provider:
            raise HTTPException(
                status_code=404,
                detail=f"Provider '{provider_key}' not supported"
            )
        
        # Check if provider supports disconnection
        if not hasattr(provider, 'disconnect'):
            raise HTTPException(
                status_code=400,
                detail=f"Provider '{provider_key}' does not support disconnection"
            )
        
        # Disconnect
        success = await provider.disconnect(user_id)
        
        if success:
            logger.info(f"Successfully disconnected {provider_key} for user {user_id}")
            return {
                "success": True,
                "provider_key": provider_key,
                "display_name": provider.display_name,
                "message": f"Successfully disconnected from {provider.display_name}"
            }
        else:
            logger.warning(f"No active {provider_key} connection found for user {user_id}")
            return {
                "success": False,
                "provider_key": provider_key,
                "display_name": provider.display_name,
                "message": f"No active {provider.display_name} connection found"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disconnection failed for {provider_key}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to disconnect from {provider_key}"
        )


@router.get("/{provider_key}/callback/success")
async def oauth_callback_success_page(provider_key: str):
    """
    Generic OAuth success callback page.
    
    Provides a consistent success page for all OAuth providers.
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{provider_key.title()} Connection Successful</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #f8fafc;
            }}
            .container {{
                text-align: center;
                padding: 2rem;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                max-width: 400px;
            }}
            .success-icon {{
                color: #10b981;
                font-size: 3rem;
                margin-bottom: 1rem;
            }}
            h1 {{
                color: #1f2937;
                margin-bottom: 0.5rem;
            }}
            p {{
                color: #64748b;
                margin-bottom: 1.5rem;
            }}
            .close-btn {{
                background: #3b82f6;
                color: white;
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.875rem;
            }}
            .close-btn:hover {{
                background: #2563eb;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success-icon">✓</div>
            <h1>Connection Successful!</h1>
            <p>Your {provider_key.title()} account has been connected successfully.</p>
            <p>You can close this window and return to the application.</p>
            <button class="close-btn" onclick="window.close()">Close Window</button>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@router.get("/{provider_key}/callback/error")
async def oauth_callback_error_page(
    provider_key: str,
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None)
):
    """
    Generic OAuth error callback page.
    
    Provides a consistent error page for all OAuth providers.
    """
    error_msg = error or "Unknown error"
    error_desc = error_description or "No additional information available"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{provider_key.title()} Connection Failed</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #fef2f2;
            }}
            .container {{
                text-align: center;
                padding: 2rem;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                max-width: 400px;
            }}
            .error-icon {{
                color: #ef4444;
                font-size: 3rem;
                margin-bottom: 1rem;
            }}
            h1 {{
                color: #1f2937;
                margin-bottom: 0.5rem;
            }}
            .error-details {{
                color: #64748b;
                margin-bottom: 1.5rem;
                text-align: left;
                background: #fef2f2;
                padding: 1rem;
                border-radius: 4px;
                border-left: 4px solid #ef4444;
            }}
            .retry-btn {{
                background: #3b82f6;
                color: white;
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.875rem;
                margin-top: 1rem;
            }}
            .retry-btn:hover {{
                background: #2563eb;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="error-icon">✗</div>
            <h1>Connection Failed</h1>
            <p>Failed to connect your {provider_key.title()} account.</p>
            <div class="error-details">
                <strong>Error:</strong> {error_msg}<br>
                <strong>Description:</strong> {error_desc}
            </div>
            <button class="retry-btn" onclick="window.history.back()">Try Again</button>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)
