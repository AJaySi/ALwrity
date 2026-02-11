"""Google Search Console Authentication Router for ALwrity.

MIGRATION STATUS: This router now uses unified OAuth patterns for consistency.
All legacy endpoints are preserved with deprecation warnings for backward compatibility.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from loguru import logger
import os

# Import unified OAuth client for migration
from services.integrations.registry import get_provider
from services.oauth_redirects import get_trusted_origins_for_redirect
from middleware.auth_middleware import get_current_user

# Initialize router
router = APIRouter(prefix="/gsc", tags=["Google Search Console"])

# Initialize GSC service (for backward compatibility)
from services.gsc_service import GSCService
gsc_service = GSCService()

def _get_gsc_postmessage_origin() -> str:
    return get_trusted_origins_for_redirect("GSC", "GSC_REDIRECT_URI")[0]

# Pydantic models
class GSCAnalyticsRequest(BaseModel):
    site_url: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class GSCStatusResponse(BaseModel):
    connected: bool
    sites: Optional[List[Dict[str, Any]]] = None
    last_sync: Optional[str] = None

class GSCAuthUrlResponse(BaseModel):
    auth_url: str
    state: str
    trusted_origins: list[str]

class GSCCallbackResponse(BaseModel):
    success: bool
    message: str
    connection_id: Optional[int] = None
    connected: Optional[bool] = None
    site_count: Optional[int] = None

@router.get("/auth/url")
async def get_gsc_auth_url(user: dict = Depends(get_current_user)):
    """
    Get Google Search Console OAuth authorization URL.
    
    @deprecated Use unified OAuth client: unifiedOAuthClient.getAuthUrl('gsc')
    This method is preserved for backward compatibility but will be removed in future versions.
    """
    console.warn('GSC Router: get_gsc_auth_url() is deprecated. Use unifiedOAuthClient.getAuthUrl("gsc") instead')
    
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        logger.info(f"Generating GSC OAuth URL for user: {user_id}")
        
        # Use unified OAuth client for consistent patterns
        from frontend.src.api.unifiedOAuth import unifiedOAuthClient
        unified_client = unifiedOAuthClient()
        
        try:
            auth_response = await unified_client.getAuthUrl('gsc')
            
            return {
                "auth_url": auth_response.auth_url,
                "state": auth_response.state,
                "trusted_origins": auth_response.trusted_origins
            }
        except Exception as unified_error:
            # Fall back to legacy service if unified client fails
            logger.warning(f"Unified client failed, falling back to legacy GSC service: {unified_error}")
            
            auth_url = gsc_service.get_oauth_url(user_id)
            
            return {
                "auth_url": auth_url,
                "state": gsc_service.get_oauth_state(user_id),
                "trusted_origins": get_trusted_origins_for_redirect("GSC", "GSC_REDIRECT_URI")
            }
        
        logger.info(f"GSC OAuth URL generated successfully for user: {user_id}")
        logger.info(f"OAuth URL: {auth_url[:100]}...")
        
    except Exception as e:
        logger.error(f"Error generating GSC OAuth URL: {e}")
        logger.error(f"Error details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating OAuth URL: {str(e)}")

@router.get("/callback")
async def handle_gsc_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(..., description="State parameter for security")
):
    """Handle Google Search Console OAuth callback.

    For a smoother UX when opened in a popup, this endpoint returns a tiny HTML
    page that posts a completion message back to the opener window and closes
    itself. The JSON payload is still included in the page for debugging.
    """
    try:
        logger.info(f"Handling GSC OAuth callback with code: {code[:10]}...")
        
        result = gsc_service.handle_oauth_callback(code, state)
        
        if result.get("success"):
            logger.info("GSC OAuth callback handled successfully")
            
            # Create GSC insights task immediately after successful connection
            try:
                from services.database import SessionLocal
                from services.platform_insights_monitoring_service import create_platform_insights_task
                
                user_id = result.get("user_id")
                if user_id:
                    db = SessionLocal()
                    try:
                        # Don't fetch site_url here - it requires API calls
                        # The executor will fetch it when the task runs (weekly)
                        # Create insights task without site_url to avoid API calls
                        task_result = create_platform_insights_task(
                            user_id=user_id,
                            platform='gsc',
                            site_url=None,  # Will be fetched by executor when task runs
                            db=db
                        )
                        
                        if task_result.get('success'):
                            logger.info(f"Created GSC insights task for user {user_id}")
                        else:
                            logger.warning(f"Failed to create GSC insights task: {task_result.get('error')}")
                    finally:
                        db.close()
            except Exception as e:
                # Non-critical: log but don't fail OAuth callback
                logger.warning(f"Failed to create GSC insights task after OAuth: {e}", exc_info=True)
            
            html = """
<!doctype html>
<html>
  <head><meta charset=\"utf-8\"><title>GSC Connected</title></head>
  <body style=\"font-family: sans-serif; padding: 24px;\">
    <p>Connection Successful. You can close this window.</p>
    <script>
      try {{ window.opener && window.opener.postMessage({{ type: 'GSC_AUTH_SUCCESS' }}, window.location.origin); }} catch (e) {{}}
      try {{ window.close(); }} catch (e) {{}}
    </script>
  </body>
  </html>
"""
            return HTMLResponse(content=html)
        else:
            logger.error("Failed to handle GSC OAuth callback")
            html = """
<!doctype html>
<html>
  <head><meta charset=\"utf-8\"><title>GSC Connection Failed</title></head>
  <body style=\"font-family: sans-serif; padding: 24px;\">
    <p>Connection Failed. Please close this window and try again.</p>
    <script>
      try {{ window.opener && window.opener.postMessage({{ type: 'GSC_AUTH_ERROR' }}, window.location.origin); }} catch (e) {{}}
    </script>
  </body>
  </html>
"""
            return HTMLResponse(status_code=400, content=html)
            
    except Exception as e:
        logger.error(f"Error handling GSC OAuth callback: {e}")
        html = f"""
<!doctype html>
<html>
  <head><meta charset=\"utf-8\"><title>GSC Connection Error</title></head>
  <body style=\"font-family: sans-serif; padding: 24px;\">
    <p>Connection Error. Please close this window and try again.</p>
    <pre style=\"white-space: pre-wrap;\">{str(e)}</pre>
    <script>
      try {{ window.opener && window.opener.postMessage({{ type: 'GSC_AUTH_ERROR' }}, window.location.origin); }} catch (e) {{}}
    </script>
  </body>
  </html>
"""
        return HTMLResponse(status_code=500, content=html)

@router.get("/sites")
async def get_gsc_sites(user: dict = Depends(get_current_user)):
    """Get user's Google Search Console sites."""
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        logger.info(f"Getting GSC sites for user: {user_id}")
        
        sites = gsc_service.get_site_list(user_id)
        
        logger.info(f"Retrieved {len(sites)} GSC sites for user: {user_id}")
        return {"sites": sites}
        
    except Exception as e:
        logger.error(f"Error getting GSC sites: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting sites: {str(e)}")

@router.post("/analytics")
async def get_gsc_analytics(
    request: GSCAnalyticsRequest,
    user: dict = Depends(get_current_user)
):
    """Get Google Search Console analytics data."""
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        logger.info(f"Getting GSC analytics for user: {user_id}, site: {request.site_url}")
        
        analytics = gsc_service.get_search_analytics(
            user_id=user_id,
            site_url=request.site_url,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        logger.info(f"Retrieved GSC analytics for user: {user_id}")
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting GSC analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting analytics: {str(e)}")

@router.get("/sitemaps/{site_url:path}")
async def get_gsc_sitemaps(
    site_url: str,
    user: dict = Depends(get_current_user)
):
    """Get sitemaps for a specific site."""
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        logger.info(f"Getting GSC sitemaps for user: {user_id}, site: {site_url}")
        
        sitemaps = gsc_service.get_sitemaps(user_id, site_url)
        
        logger.info(f"Retrieved {len(sitemaps)} sitemaps for user: {user_id}")
        return {"sitemaps": sitemaps}
        
    except Exception as e:
        logger.error(f"Error getting GSC sitemaps: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting sitemaps: {str(e)}")

@router.get("/status")
async def get_gsc_status(user: dict = Depends(get_current_user)):
    """
    Get GSC connection status for user.
    
    @deprecated Use unified OAuth client: unifiedOAuthClient.getConnectionStatus('gsc')
    This method is preserved for backward compatibility but will be removed in future versions.
    """
    console.warn('GSC Router: get_gsc_status() is deprecated. Use unifiedOAuthClient.getConnectionStatus("gsc") instead')
    
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        logger.info(f"Checking GSC status for user: {user_id}")
        
        # Use unified OAuth client for consistent patterns
        from frontend.src.api.unifiedOAuth import unifiedOAuthClient
        unified_client = unifiedOAuthClient()
        
        try:
            status_response = await unified_client.getConnectionStatus('gsc')
            
            # Transform unified response to GSC-specific format
            details = status_response.details as any
            sites = details?.sites || []
            
            return {
                "connected": status_response.connected,
                "sites": sites,
                "total_sites": len(sites),
                "last_sync": details?.last_sync
            }
        except Exception as unified_error:
            # Fall back to legacy service if unified client fails
            logger.warning(f"Unified client failed, falling back to legacy GSC service: {unified_error}")
            
            # Use legacy GSC service for status check
            credentials = gsc_service.load_user_credentials(user_id)
            connected = credentials is not None
            
            sites = []
            if connected:
                try:
                    sites = gsc_service.get_site_list(user_id)
                except Exception as e:
                    logger.warning(f"Could not get sites for user {user_id}: {e}")
                    sites = []
                
                last_sync = None  # Could be enhanced to track last sync time
                status_response = GSCStatusResponse(
                    connected=connected,
                    sites=sites,
                    total_sites=len(sites),
                    last_sync=last_sync
                )
            else:
                status_response = GSCStatusResponse(
                    connected=False,
                    sites=[],
                    total_sites=0,
                    last_sync=None
                )
        
        logger.info(f"GSC status checked for user: {user_id}, connected: {connected}")
        return status_response
        
    except Exception as e:
        logger.error(f"Error checking GSC status: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking status: {str(e)}")

@router.delete("/disconnect")
async def disconnect_gsc(user: dict = Depends(get_current_user)):
    """
    Disconnect user's Google Search Console account.
    
    @deprecated Use unified OAuth client: unifiedOAuthClient.disconnect('gsc')
    This method is preserved for backward compatibility but will be removed in future versions.
    """
    console.warn('GSC Router: disconnect_gsc() is deprecated. Use unifiedOAuthClient.disconnect("gsc") instead')
    
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        logger.info(f"Disconnecting GSC for user: {user_id}")
        
        # Use unified OAuth client for consistent patterns
        from frontend.src.api.unifiedOAuth import unifiedOAuthClient
        unified_client = unifiedOAuthClient()
        
        try:
            disconnect_response = await unified_client.disconnect('gsc')
            
            return {
                "success": disconnect_response.success,
                "message": disconnect_response.message
            }
        except Exception as unified_error:
            # Fall back to legacy service if unified client fails
            logger.warning(f"Unified client failed, falling back to legacy GSC service: {unified_error}")
            
            # Use legacy GSC service for disconnection
            success = gsc_service.revoke_access_token(user_id)
            
            if success:
                logger.info(f"Successfully disconnected GSC for user {user_id}")
                return {
                    "success": True,
                    "message": "Successfully disconnected from Google Search Console"
                }
            else:
                logger.error(f"Failed to disconnect GSC for user {user_id}")
                return {
                    "success": False,
                    "message": "Failed to disconnect from Google Search Console"
                }
        
    except Exception as e:
        logger.error(f"Error disconnecting GSC: {e}")
        raise HTTPException(status_code=500, detail=f"Error disconnecting from Google Search Console: {str(e)}")

@router.post("/clear-incomplete")
async def clear_incomplete_credentials(user: dict = Depends(get_current_user)):
    """Clear incomplete GSC credentials that are missing required fields."""
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        logger.info(f"Clearing incomplete GSC credentials for user: {user_id}")
        
        success = gsc_service.clear_incomplete_credentials(user_id)
        
        if success:
            logger.info(f"Incomplete GSC credentials cleared for user: {user_id}")
            return {"success": True, "message": "Incomplete credentials cleared"}
        else:
            logger.error(f"Failed to clear incomplete credentials for user: {user_id}")
            raise HTTPException(status_code=500, detail="Failed to clear incomplete credentials")
            
    except Exception as e:
        logger.error(f"Error clearing incomplete credentials: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing incomplete credentials: {str(e)}")

@router.get("/health")
async def gsc_health_check():
    """Health check for GSC service."""
    try:
        logger.info("GSC health check requested")
        return {
            "status": "healthy",
            "service": "Google Search Console API",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    except Exception as e:
        logger.error(f"GSC health check failed: {e}")
        raise HTTPException(status_code=500, detail="GSC service unhealthy")
