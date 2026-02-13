"""
Canonical OAuth URL endpoints for providers.

**DEPRECATED**: This router is deprecated and will be removed in future versions.
Use unified OAuth router: `/oauth/{provider}/*` instead.

Migration Status:
- Unified OAuth Router: `/oauth/*` - USE THIS INSTEAD
- Provider Migrations: GSC, Bing, WordPress completed
- Frontend Unified Client: Available for all platforms
- Legacy Cleanup: COMPLETE - Only deprecation responses remain

New Endpoint Mappings:
- GET /api/oauth/{provider}/auth-url → GET /oauth/{provider}/auth
- POST /api/oauth/{provider}/callback → POST /oauth/{provider}/callback
- GET /api/oauth/{provider}/status → GET /oauth/{provider}/status
- POST /api/oauth/{provider}/disconnect → POST /oauth/{provider}/disconnect
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Header
from loguru import logger
from pydantic import BaseModel

from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/oauth", tags=["OAuth - DEPRECATED"])

class DeprecationResponse(BaseModel):
    success: bool
    message: str
    new_endpoint: str
    deprecation_date: str

@router.get("/{provider}/auth-url")
async def get_oauth_auth_url(
    provider: str,
    user: Dict[str, Any] = Depends(get_current_user),
    user_agent: Optional[str] = Header(None),
):
    """
    **DEPRECATED**: Get OAuth authorization URL for provider.
    
    Use unified OAuth router instead: GET /oauth/{provider}/auth
    
    This endpoint is deprecated and will be removed in future versions.
    Please migrate to: GET /oauth/{provider}/auth
    """
    # Log deprecation warning
    logger.warning(f"Legacy OAuth endpoint used: /api/oauth/{provider}/auth-url. Please use /oauth/{provider}/auth instead. User-Agent: {user_agent}")
    
    # Normalize provider
    provider_key = provider.lower().strip()
    
    # Return deprecation response with redirect to unified endpoint
    return DeprecationResponse(
        success=False,
        message=f"This endpoint is deprecated. Use unified OAuth router: GET /oauth/{provider}/auth",
        new_endpoint=f"/oauth/{provider}/auth",
        deprecation_date="2026-02-11",
        migration_guide="See: docs/integration/PHASE2_UNIFIED_ROUTER_IMPLEMENTATION_PROGRESS.md"
    )


@router.post("/{provider}/callback")
async def handle_oauth_callback(
    provider: str,
    user: Dict[str, Any] = Depends(get_current_user),
    user_agent: Optional[str] = Header(None),
):
    """
    **DEPRECATED**: Handle OAuth callback for provider.
    
    Use unified OAuth router instead: POST /oauth/{provider}/callback
    
    This endpoint is deprecated and will be removed in future versions.
    Please migrate to: POST /oauth/{provider}/callback
    """
    # Log deprecation warning
    logger.warning(f"Legacy OAuth endpoint used: /api/oauth/{provider}/callback. Please use /oauth/{provider}/callback instead. User-Agent: {user_agent}")
    
    # Normalize provider
    provider_key = provider.lower().strip()
    
    # Return deprecation response with redirect to unified endpoint
    return DeprecationResponse(
        success=False,
        message=f"This endpoint is deprecated. Use unified OAuth router: POST /oauth/{provider}/callback",
        new_endpoint=f"/oauth/{provider}/callback",
        deprecation_date="2026-02-11",
        migration_guide="See: docs/integration/PHASE2_UNIFIED_ROUTER_IMPLEMENTATION_PROGRESS.md"
    )


@router.get("/{provider}/status")
async def get_oauth_status(
    provider: str,
    user: Dict[str, Any] = Depends(get_current_user),
    user_agent: Optional[str] = Header(None),
):
    """
    **DEPRECATED**: Get OAuth status for provider.
    
    Use unified OAuth router instead: GET /oauth/{provider}/status
    
    This endpoint is deprecated and will be removed in future versions.
    Please migrate to: GET /oauth/{provider}/status
    """
    # Log deprecation warning
    logger.warning(f"Legacy OAuth endpoint used: /api/oauth/{provider}/status. Please use /oauth/{provider}/status instead. User-Agent: {user_agent}")
    
    # Normalize provider
    provider_key = provider.lower().strip()
    
    # Return deprecation response with redirect to unified endpoint
    return DeprecationResponse(
        success=False,
        message=f"This endpoint is deprecated. Use unified OAuth router: GET /oauth/{provider}/status",
        new_endpoint=f"/oauth/{provider}/status",
        deprecation_date="2026-02-11",
        migration_guide="See: docs/integration/PHASE2_UNIFIED_ROUTER_IMPLEMENTATION_PROGRESS.md"
    )


@router.post("/{provider}/disconnect")
async def disconnect_oauth(
    provider: str,
    user: Dict[str, Any] = Depends(get_current_user),
    user_agent: Optional[str] = Header(None),
):
    """
    **DEPRECATED**: Disconnect OAuth for provider.
    
    Use unified OAuth router instead: POST /oauth/{provider}/disconnect
    
    This endpoint is deprecated and will be removed in future versions.
    Please migrate to: POST /oauth/{provider}/disconnect
    """
    # Log deprecation warning
    logger.warning(f"Legacy OAuth endpoint used: /api/oauth/{provider}/disconnect. Please use /oauth/{provider}/disconnect instead. User-Agent: {user_agent}")
    
    # Normalize provider
    provider_key = provider.lower().strip()
    
    # Return deprecation response with redirect to unified endpoint
    return DeprecationResponse(
        success=False,
        message=f"This endpoint is deprecated. Use unified OAuth router: POST /oauth/{provider}/disconnect",
        new_endpoint=f"/oauth/{provider}/disconnect",
        deprecation_date="2026-02-11",
        migration_guide="See: docs/integration/PHASE2_UNIFIED_ROUTER_IMPLEMENTATION_PROGRESS.md"
    )
