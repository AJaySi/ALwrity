"""Google Search Console Authentication Router for ALwrity.

MIGRATION STATUS: This router now uses unified OAuth patterns for consistency.
All legacy endpoints are preserved with deprecation warnings for backward compatibility.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.responses import HTMLResponse
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from loguru import logger
from urllib.parse import parse_qs, urlparse

# Import unified OAuth client for migration
from services.integrations.registry import get_provider
from services.oauth_redirects import get_trusted_origins_for_redirect
from middleware.auth_middleware import get_current_user

# Initialize router
router = APIRouter(prefix="/gsc", tags=["Google Search Console"])

# Initialize GSC service (for backward compatibility)
from services.gsc_service import GSCService
gsc_service = GSCService()


DEPRECATED_GSC_LEGACY_ROUTES_REMOVAL_DATE = "2026-06-30"

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


class GSCDataQualityResponse(BaseModel):
    site_url: str
    permission_level: Optional[str] = None
    has_sufficient_permission: bool
    data_days_available: int
    data_window_start: Optional[str] = None
    data_window_end: Optional[str] = None
    indexing_health: Dict[str, Any]


class GSCCachedOpportunitiesResponse(BaseModel):
    site_url: str
    opportunities: List[Dict[str, Any]]
    generated_from_cache: bool

@router.get("/auth/url")
async def get_gsc_auth_url(request: Request, user: dict = Depends(get_current_user)):
    """
    Get Google Search Console OAuth authorization URL.
    
    @deprecated Use unified OAuth client: unifiedOAuthClient.getAuthUrl('gsc')
    This method is preserved for backward compatibility but will be removed in future versions.
    """
    logger.warning(f'GSC Router: /gsc/auth/url is deprecated; use /oauth/gsc/auth. Planned removal after {DEPRECATED_GSC_LEGACY_ROUTES_REMOVAL_DATE}')
    
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        logger.info(f"Generating GSC OAuth URL for user: {user_id}")
        
        provider = get_provider("gsc")
        if not provider:
            raise HTTPException(status_code=500, detail="GSC provider not registered")

        auth_payload = provider.get_auth_url(user_id)
        if not auth_payload.auth_url:
            raise HTTPException(status_code=500, detail="Failed to generate GSC OAuth URL")

        parsed_query = parse_qs(urlparse(auth_payload.auth_url).query)
        state = parsed_query.get("state", [auth_payload.state or ""])[0]

        trusted_origins = get_trusted_origins_for_redirect("GSC", "GSC_REDIRECT_URI")
        backend_origin = str(request.base_url).rstrip("/")
        if backend_origin not in trusted_origins:
            trusted_origins.append(backend_origin)

        return {
            "auth_url": auth_payload.auth_url,
            "state": state,
            "trusted_origins": trusted_origins
        }
        
        logger.info(f"GSC OAuth URL generated successfully for user: {user_id}")
        
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
      try {{
        const popupNonce = (window.name || '').replace('gsc-auth-', '');
        window.opener && window.opener.postMessage({{ type: 'GSC_AUTH_SUCCESS', nonce: popupNonce }}, window.location.origin);
      }} catch (e) {{}}
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
      try {{
        const popupNonce = (window.name || '').replace('gsc-auth-', '');
        window.opener && window.opener.postMessage({{ type: 'GSC_AUTH_ERROR', nonce: popupNonce }}, window.location.origin);
      }} catch (e) {{}}
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
      try {{
        const popupNonce = (window.name || '').replace('gsc-auth-', '');
        window.opener && window.opener.postMessage({{ type: 'GSC_AUTH_ERROR', nonce: popupNonce }}, window.location.origin);
      }} catch (e) {{}}
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


@router.get("/data-quality", response_model=GSCDataQualityResponse)
async def get_gsc_data_quality(
    site_url: str = Query(..., description="GSC site URL"),
    user: dict = Depends(get_current_user)
):
    """Get immediate data quality checks for onboarding UX."""
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")

        sites = gsc_service.get_site_list(user_id)
        selected_site = next((s for s in sites if s.get("siteUrl") == site_url), None)
        permission_level = selected_site.get("permissionLevel") if selected_site else None
        has_sufficient_permission = permission_level in {"siteOwner", "siteFullUser", "siteRestrictedUser"}

        analytics = gsc_service.get_search_analytics(user_id=user_id, site_url=site_url)
        verification_rows = analytics.get("verification_data", {}).get("rows", [])
        date_keys = [row.get("keys", [None])[0] for row in verification_rows if row.get("keys")]
        date_keys = [d for d in date_keys if isinstance(d, str)]

        data_window_start = min(date_keys) if date_keys else None
        data_window_end = max(date_keys) if date_keys else None

        sitemaps = gsc_service.get_sitemaps(user_id, site_url)
        submitted = 0
        indexed = 0
        for sitemap in sitemaps:
            for content in sitemap.get("contents", []) or []:
                try:
                    submitted += int(content.get("submitted", 0) or 0)
                    indexed += int(content.get("indexed", 0) or 0)
                except (TypeError, ValueError):
                    continue

        indexing_ratio = round((indexed / submitted) * 100, 2) if submitted > 0 else None

        return GSCDataQualityResponse(
            site_url=site_url,
            permission_level=permission_level,
            has_sufficient_permission=has_sufficient_permission,
            data_days_available=len(date_keys),
            data_window_start=data_window_start,
            data_window_end=data_window_end,
            indexing_health={
                "submitted_urls": submitted,
                "indexed_urls": indexed,
                "indexing_ratio": indexing_ratio,
                "sitemaps_count": len(sitemaps)
            }
        )
    except Exception as e:
        logger.error(f"Error getting GSC data quality: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting GSC data quality: {str(e)}")


@router.get("/opportunities", response_model=GSCCachedOpportunitiesResponse)
async def get_gsc_cached_opportunities(
    site_url: str = Query(..., description="GSC site URL"),
    user: dict = Depends(get_current_user)
):
    """Get guided opportunities from cached query analytics."""
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")

        cached = gsc_service.get_latest_cached_analytics(user_id=user_id, site_url=site_url)
        if not cached:
            return GSCCachedOpportunitiesResponse(site_url=site_url, opportunities=[], generated_from_cache=False)

        payload = cached.get("data", {})
        query_rows = payload.get("query_data", {}).get("rows", [])

        opportunities = []
        for row in query_rows:
            keys = row.get("keys", [])
            query = keys[0] if keys else None
            impressions = float(row.get("impressions", 0) or 0)
            ctr = float(row.get("ctr", 0) or 0)
            position = float(row.get("position", 0) or 0)
            clicks = float(row.get("clicks", 0) or 0)

            if query and impressions >= 100 and ctr < 0.03:
                opportunities.append({
                    "query": query,
                    "clicks": int(clicks),
                    "impressions": int(impressions),
                    "ctr": round(ctr * 100, 2),
                    "position": round(position, 2),
                    "recommended_action": "Improve title/meta and align intro to search intent"
                })

        opportunities = sorted(opportunities, key=lambda x: x["impressions"], reverse=True)[:10]

        return GSCCachedOpportunitiesResponse(
            site_url=site_url,
            opportunities=opportunities,
            generated_from_cache=True
        )
    except Exception as e:
        logger.error(f"Error getting GSC opportunities: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting GSC opportunities: {str(e)}")

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
    logger.warning(f'GSC Router: /gsc/status is deprecated; use /oauth/gsc/status. Planned removal after {DEPRECATED_GSC_LEGACY_ROUTES_REMOVAL_DATE}')
    
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        logger.info(f"Checking GSC status for user: {user_id}")
        
        provider = get_provider("gsc")
        if not provider:
            raise HTTPException(status_code=500, detail="GSC provider not registered")

        status_response = provider.get_connection_status(user_id)
        sites = []
        if status_response.connected:
            try:
                sites = gsc_service.get_site_list(user_id)
            except Exception as e:
                logger.warning(f"Could not get sites for user {user_id}: {e}")

        logger.info(f"GSC status checked for user: {user_id}, connected: {status_response.connected}")
        return {
            "connected": status_response.connected,
            "sites": sites,
            "total_sites": len(sites),
            "last_sync": None
        }
        
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
    logger.warning(f'GSC Router: /gsc/disconnect is deprecated; use /oauth/gsc/disconnect. Planned removal after {DEPRECATED_GSC_LEGACY_ROUTES_REMOVAL_DATE}')
    
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        logger.info(f"Disconnecting GSC for user: {user_id}")
        
        provider = get_provider("gsc")
        if not provider:
            raise HTTPException(status_code=500, detail="GSC provider not registered")

        success = provider.disconnect(user_id)

        if success:
            logger.info(f"Successfully disconnected GSC for user {user_id}")
            return {
                "success": True,
                "message": "Successfully disconnected from Google Search Console"
            }

        logger.warning(f"No active GSC connection found for user {user_id}")
        return {
            "success": False,
            "message": "No active Google Search Console connection found"
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
