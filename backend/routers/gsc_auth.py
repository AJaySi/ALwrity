"""Google Search Console Authentication Router for ALwrity."""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from loguru import logger
import os

from services.gsc_service import GSCService
from middleware.auth_middleware import get_current_user

# Initialize router
router = APIRouter(prefix="/gsc", tags=["Google Search Console"])

# Initialize GSC service
gsc_service = GSCService()

# Pydantic models
class GSCAnalyticsRequest(BaseModel):
    site_url: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class GSCStatusResponse(BaseModel):
    connected: bool
    sites: Optional[List[Dict[str, Any]]] = None
    last_sync: Optional[str] = None

@router.get("/auth/url")
async def get_gsc_auth_url(user: dict = Depends(get_current_user)):
    """Get Google Search Console OAuth authorization URL."""
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        logger.info(f"Generating GSC OAuth URL for user: {user_id}")
        
        auth_url = gsc_service.get_oauth_url(user_id)
        
        logger.info(f"GSC OAuth URL generated successfully for user: {user_id}")
        return {"auth_url": auth_url}
        
    except Exception as e:
        logger.error(f"Error generating GSC OAuth URL: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating OAuth URL: {str(e)}")

@router.get("/callback")
async def handle_gsc_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(..., description="State parameter for security")
):
    """Handle Google Search Console OAuth callback."""
    try:
        logger.info(f"Handling GSC OAuth callback with code: {code[:10]}...")
        
        success = gsc_service.handle_oauth_callback(code, state)
        
        if success:
            logger.info("GSC OAuth callback handled successfully")
            return {"success": True, "message": "GSC connected successfully"}
        else:
            logger.error("Failed to handle GSC OAuth callback")
            raise HTTPException(status_code=400, detail="Failed to connect GSC")
            
    except Exception as e:
        logger.error(f"Error handling GSC OAuth callback: {e}")
        raise HTTPException(status_code=500, detail=f"Error handling OAuth callback: {str(e)}")

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
    """Get GSC connection status for user."""
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        logger.info(f"Checking GSC status for user: {user_id}")
        
        # Check if user has credentials
        credentials = gsc_service.load_user_credentials(user_id)
        connected = credentials is not None
        
        sites = []
        if connected:
            try:
                sites = gsc_service.get_site_list(user_id)
            except Exception as e:
                logger.warning(f"Could not get sites for user {user_id}: {e}")
                connected = False
        
        status_response = GSCStatusResponse(
            connected=connected,
            sites=sites if connected else None,
            last_sync=None  # Could be enhanced to track last sync time
        )
        
        logger.info(f"GSC status checked for user: {user_id}, connected: {connected}")
        return status_response
        
    except Exception as e:
        logger.error(f"Error checking GSC status: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking status: {str(e)}")

@router.delete("/disconnect")
async def disconnect_gsc(user: dict = Depends(get_current_user)):
    """Disconnect user's Google Search Console account."""
    try:
        user_id = user.get('id')
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")
        
        logger.info(f"Disconnecting GSC for user: {user_id}")
        
        success = gsc_service.revoke_user_access(user_id)
        
        if success:
            logger.info(f"GSC disconnected successfully for user: {user_id}")
            return {"success": True, "message": "GSC disconnected successfully"}
        else:
            logger.error(f"Failed to disconnect GSC for user: {user_id}")
            raise HTTPException(status_code=500, detail="Failed to disconnect GSC")
            
    except Exception as e:
        logger.error(f"Error disconnecting GSC: {e}")
        raise HTTPException(status_code=500, detail=f"Error disconnecting GSC: {str(e)}")

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
