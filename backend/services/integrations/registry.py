"""Integration registry with thin adapters for legacy providers."""

from __future__ import annotations

from typing import Dict, Optional

from services.gsc_service import GSCService
from services.integrations.bing_oauth import BingOAuthService
from services.integrations.wordpress_oauth import WordPressOAuthService
from services.integrations.wix_oauth import WixOAuthService
from services.wix_service import WixService

from .base import AuthUrlPayload, ConnectionStatus, IntegrationProvider


class GSCIntegrationProvider:
    key = "gsc"
    display_name = "Google Search Console"

    def __init__(self, service: Optional[GSCService] = None) -> None:
        self._service = service or GSCService()

    def get_auth_url(self, user_id: str) -> AuthUrlPayload:
        auth_url = self._service.get_oauth_url(user_id)
        return AuthUrlPayload(auth_url=auth_url)

    def get_connection_status(self, user_id: str) -> ConnectionStatus:
        credentials = self._service.load_user_credentials(user_id)
        if not credentials:
            return ConnectionStatus(connected=False, details={"has_credentials": False})

        valid = bool(getattr(credentials, "valid", False))
        expired = bool(getattr(credentials, "expired", False))
        refresh_token = getattr(credentials, "refresh_token", None)
        connected = valid or bool(refresh_token)
        details = {
            "has_credentials": True,
            "valid": valid,
            "expired": expired,
            "scopes": getattr(credentials, "scopes", None),
        }
        return ConnectionStatus(connected=connected, details=details)


class BingIntegrationProvider:
    key = "bing"
    display_name = "Bing Webmaster Tools"

    def __init__(self, service: Optional[BingOAuthService] = None) -> None:
        self._service = service or BingOAuthService()

    def get_auth_url(self, user_id: str) -> AuthUrlPayload:
        payload = self._service.generate_authorization_url(user_id)
        if not payload or "auth_url" not in payload:
            return AuthUrlPayload(auth_url="", details={"error": "Unable to generate auth URL."})
        return AuthUrlPayload(auth_url=payload["auth_url"], state=payload.get("state"))

    def get_connection_status(self, user_id: str) -> ConnectionStatus:
        status = self._service.get_connection_status(user_id)
        return ConnectionStatus(
            connected=bool(status.get("connected")),
            details=status,
            error=status.get("error"),
        )


class WordPressIntegrationProvider:
    key = "wordpress"
    display_name = "WordPress"

    def __init__(self, service: Optional[WordPressOAuthService] = None) -> None:
        self._service = service or WordPressOAuthService()

    def get_auth_url(self, user_id: str) -> AuthUrlPayload:
        payload = self._service.generate_authorization_url(user_id)
        if not payload or "auth_url" not in payload:
            return AuthUrlPayload(auth_url="", details={"error": "Unable to generate auth URL."})
        return AuthUrlPayload(auth_url=payload["auth_url"], state=payload.get("state"))

    def get_connection_status(self, user_id: str) -> ConnectionStatus:
        status = self._service.get_connection_status(user_id)
        return ConnectionStatus(
            connected=bool(status.get("connected")),
            details=status,
            error=status.get("error"),
        )


class WixIntegrationProvider:
    key = "wix"
    display_name = "Wix"

    def __init__(self, service: Optional[WixService] = None, oauth: Optional[WixOAuthService] = None) -> None:
        self._service = service or WixService()
        self._oauth = oauth or WixOAuthService()

    def get_auth_url(self, user_id: str) -> AuthUrlPayload:
        auth_url = self._service.get_authorization_url(state=user_id)
        return AuthUrlPayload(auth_url=auth_url, state=user_id)

    def get_connection_status(self, user_id: str) -> ConnectionStatus:
        status = self._oauth.get_user_token_status(user_id)
        connected = bool(status.get("has_active_tokens"))
        return ConnectionStatus(connected=connected, details=status, error=status.get("error"))


_INTEGRATION_PROVIDERS: Dict[str, IntegrationProvider] = {}


def register_provider(provider: IntegrationProvider) -> None:
    """Register an integration provider by its key."""
    _INTEGRATION_PROVIDERS[provider.key] = provider


def get_provider(key: str) -> Optional[IntegrationProvider]:
    return _INTEGRATION_PROVIDERS.get(key)


def list_providers() -> Dict[str, IntegrationProvider]:
    return dict(_INTEGRATION_PROVIDERS)


# Keep legacy paths in use for onboarding/monitoring until Week 3.
register_provider(GSCIntegrationProvider())
register_provider(BingIntegrationProvider())
register_provider(WordPressIntegrationProvider())
register_provider(WixIntegrationProvider())
