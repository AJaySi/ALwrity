"""
Canonical OAuth URL endpoints for providers.

Why this exists:
- Centralizes OAuth URL generation so the frontend doesn't hardcode origins,
  client IDs, or redirect URIs.
- Ensures redirect validation happens server-side before the UI sends users
  through provider login flows.
"""

from typing import Any, Dict, Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from pydantic import BaseModel

from middleware.auth_middleware import get_current_user
from services.gsc_service import GSCService
from services.integrations.bing_oauth import BingOAuthService
from services.integrations.wordpress_oauth import WordPressOAuthService
from services.wix_service import WixService
from services.oauth_redirects import get_redirect_uri, validate_redirect_uri

router = APIRouter(prefix="/api/oauth", tags=["OAuth"])

bing_service = BingOAuthService()
wordpress_service = WordPressOAuthService()
gsc_service = GSCService()
wix_service = WixService()


class OAuthUrlResponse(BaseModel):
    provider: str
    auth_url: str
    redirect_uri: Optional[str] = None
    client_id: Optional[str] = None
    state: Optional[str] = None
    oauth_data: Optional[Dict[str, Any]] = None
    trusted_origins: Optional[List[str]] = None


@router.get("/{provider}/auth-url", response_model=OAuthUrlResponse)
async def get_oauth_auth_url(
    provider: str,
    user: Dict[str, Any] = Depends(get_current_user),
):
    # Normalize provider once so the logic below stays consistent across calls.
    provider_key = provider.lower().strip()

    try:
        if provider_key == "bing":
            # Bing requires a user-scoped state for CSRF protection and token storage.
            user_id = user.get("id")
            if not user_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID not found.")
            auth_data = bing_service.generate_authorization_url(user_id)
            if not auth_data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Bing OAuth is not properly configured.",
                )
            return OAuthUrlResponse(
                provider="bing",
                auth_url=auth_data["auth_url"],
                state=auth_data.get("state"),
                redirect_uri=bing_service.redirect_uri,
            )

        if provider_key == "wordpress":
            # WordPress also stores a user-scoped state parameter for CSRF protection.
            user_id = user.get("id")
            if not user_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID not found.")
            auth_data = wordpress_service.generate_authorization_url(user_id)
            if not auth_data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="WordPress OAuth is not properly configured.",
                )
            return OAuthUrlResponse(
                provider="wordpress",
                auth_url=auth_data["auth_url"],
                state=auth_data.get("state"),
                redirect_uri=wordpress_service.redirect_uri,
            )

        if provider_key == "gsc":
            # GSC uses Google's Flow builder, but we still validate redirects server-side.
            user_id = user.get("id")
            if not user_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID not found.")
            auth_url = gsc_service.get_oauth_url(user_id)
            return OAuthUrlResponse(
                provider="gsc",
                auth_url=auth_url,
                redirect_uri=get_redirect_uri("GSC", "GSC_REDIRECT_URI"),
            )

        if provider_key == "wix":
            # Wix uses PKCE and needs additional metadata for the SPA callback.
            # We return the PKCE payload so the frontend can persist it for the SDK.
            oauth_config = wix_service.get_oauth_config()
            redirect_uri = oauth_config["redirect_uri"]
            origin = validate_redirect_uri("Wix", redirect_uri)
            oauth_data = {
                "state": oauth_config["state"],
                "codeVerifier": oauth_config["code_verifier"],
                "codeChallenge": oauth_config["code_challenge"],
                "redirectUri": redirect_uri,
            }
            return OAuthUrlResponse(
                provider="wix",
                auth_url=oauth_config["auth_url"],
                redirect_uri=redirect_uri,
                client_id=wix_service.client_id,
                oauth_data=oauth_data,
                trusted_origins=[origin],
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unsupported OAuth provider: {provider_key}",
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error generating OAuth URL for provider '{provider_key}': {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate OAuth URL.",
        )
