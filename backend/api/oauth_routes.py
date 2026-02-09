"""
Canonical OAuth URL endpoints for providers.

Why this exists:
- Centralizes OAuth URL generation so the frontend doesn't hardcode origins,
  client IDs, or redirect URIs.
- Ensures redirect validation happens server-side before the UI sends users
  through provider login flows.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from pydantic import BaseModel

from middleware.auth_middleware import get_current_user
from services.integrations.registry import get_provider
from services.oauth_redirects import validate_redirect_uri

router = APIRouter(prefix="/api/oauth", tags=["OAuth"])

class OAuthUrlResponse(BaseModel):
    provider_id: str
    url: str
    state: Optional[str] = None
    expires_in: Optional[int] = None
    details: Optional[Dict[str, Any]] = None


@router.get("/{provider}/auth-url", response_model=OAuthUrlResponse)
async def get_oauth_auth_url(
    provider: str,
    user: Dict[str, Any] = Depends(get_current_user),
):
    # Normalize provider once so the logic below stays consistent across calls.
    provider_key = provider.lower().strip()

    try:
        user_id = user.get("id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID not found.")

        provider_instance = get_provider(provider_key)
        if not provider_instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unsupported OAuth provider: {provider_key}",
            )

        auth_payload = provider_instance.get_auth_url(user_id)
        if not auth_payload.url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{provider_key} OAuth is not properly configured.",
            )
        details = dict(auth_payload.details or {})

        redirect_uri = details.get("redirect_uri")
        if redirect_uri:
            origin = validate_redirect_uri(provider_key, redirect_uri)
            details.setdefault("trusted_origins", [origin])

        return OAuthUrlResponse(
            provider_id=auth_payload.provider_id,
            url=auth_payload.url,
            state=auth_payload.state,
            expires_in=auth_payload.expires_in,
            details=details,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error generating OAuth URL for provider '{provider_key}': {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate OAuth URL.",
        )
