"""Integration registry with thin adapters for legacy providers."""

from __future__ import annotations

from typing import Callable, Dict, Optional

from services.gsc_service import GSCService
from services.integrations.bing_oauth import BingOAuthService
from services.integrations.wordpress_oauth import WordPressOAuthService
from services.integrations.wix_oauth import WixOAuthService
from services.wix_service import WixService

from .base import AuthUrlPayload, ConnectionStatus, IntegrationProvider, ConnectionResult, RefreshResult, Account
from .enhanced_integration_provider import create_enhanced_provider


class GSCIntegrationProvider:
    key = "gsc"
    display_name = "Google Search Console"

    def __init__(self, service: Optional[GSCService] = None) -> None:
        self._service = service or GSCService()

    def get_auth_url(self, user_id: str, redirect_uri: Optional[str] = None) -> AuthUrlPayload:
        auth_url = self._service.get_oauth_url(user_id)
        return AuthUrlPayload(
            auth_url=auth_url,
            state=user_id,
            provider_id=self.key
        )

    def handle_callback(self, code: str, state: str) -> ConnectionResult:
        try:
            # GSC handles callback internally through the service
            credentials = self._service.exchange_code_for_tokens(code)
            if not credentials:
                return ConnectionResult(
                    success=False,
                    user_id=state,
                    provider_id=self.key,
                    error="Failed to exchange code for tokens"
                )
            
            return ConnectionResult(
                success=True,
                user_id=state,
                provider_id=self.key,
                access_token=getattr(credentials, 'token', None),
                refresh_token=getattr(credentials, 'refresh_token', None),
                expires_at=getattr(credentials, 'expiry', None),
                scope=getattr(credentials, 'scopes', None),
                account_info={
                    'email': getattr(credentials, 'email', None),
                    'verified': getattr(credentials, 'verified', False)
                }
            )
        except Exception as e:
            return ConnectionResult(
                success=False,
                user_id=state,
                provider_id=self.key,
                error=f"Callback handling failed: {str(e)}"
            )

    def get_connection_status(self, user_id: str) -> ConnectionStatus:
        credentials = self._service.load_user_credentials(user_id)
        if not credentials:
            return ConnectionStatus(
                connected=False,
                provider_id=self.key,
                user_id=user_id,
                details={"has_credentials": False}
            )

        valid = bool(getattr(credentials, "valid", False))
        expired = bool(getattr(credentials, "expired", False))
        refresh_token = getattr(credentials, "refresh_token", None)
        connected = valid or bool(refresh_token)
        
        return ConnectionStatus(
            connected=connected,
            provider_id=self.key,
            user_id=user_id,
            expires_at=getattr(credentials, 'expiry', None),
            refreshable=bool(refresh_token),
            last_checked=getattr(credentials, 'last_checked', None),
            warnings=[] if connected else ["No valid credentials"],
            details={
                "has_credentials": True,
                "valid": valid,
                "expired": expired,
                "scopes": getattr(credentials, "scopes", None),
                "email": getattr(credentials, "email", None)
            }
        )

    def refresh_token(self, user_id: str) -> Optional[RefreshResult]:
        try:
            credentials = self._service.load_user_credentials(user_id)
            if not credentials or not getattr(credentials, 'refresh_token', None):
                return RefreshResult(
                    success=False,
                    user_id=user_id,
                    provider_id=self.key,
                    error="No refresh token available"
                )
            
            # GSC auto-refreshes on load, so we just load and return
            refreshed_credentials = self._service.load_user_credentials(user_id)
            if refreshed_credentials and getattr(refreshed_credentials, 'valid', False):
                return RefreshResult(
                    success=True,
                    user_id=user_id,
                    provider_id=self.key,
                    access_token=getattr(refreshed_credentials, 'token', None),
                    refresh_token=getattr(refreshed_credentials, 'refresh_token', None),
                    expires_at=getattr(refreshed_credentials, 'expiry', None)
                )
            else:
                return RefreshResult(
                    success=False,
                    user_id=user_id,
                    provider_id=self.key,
                    error="Token refresh failed"
                )
        except Exception as e:
            return RefreshResult(
                success=False,
                user_id=user_id,
                provider_id=self.key,
                error=f"Refresh failed: {str(e)}"
            )

    def disconnect(self, user_id: str) -> bool:
        try:
            # GSC doesn't have explicit disconnect, remove credentials from storage
            return self._service.revoke_user_credentials(user_id)
        except Exception as e:
            from loguru import logger
            logger.error(f"GSC disconnect failed for user {user_id}: {e}")
            return False

    def list_connected_accounts(self, user_id: str) -> list[Account]:
        try:
            credentials = self._service.load_user_credentials(user_id)
            if not credentials:
                return []
            
            return [Account(
                account_id=user_id,
                provider_id=self.key,
                display_name=getattr(credentials, 'email', user_id),
                email=getattr(credentials, 'email', None),
                connected_at=getattr(credentials, 'created_at', None),
                expires_at=getattr(credentials, 'expiry', None),
                is_active=getattr(credentials, 'valid', False)
            )]
        except Exception as e:
            from loguru import logger
            logger.error(f"GSC list accounts failed for user {user_id}: {e}")
            return []


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
_INTEGRATION_PROVIDER_FACTORIES: Dict[str, Callable[[], IntegrationProvider]] = {}


def register_provider(provider: IntegrationProvider) -> None:
    """Register an integration provider by its key."""
    _INTEGRATION_PROVIDERS[provider.key] = provider


def register_provider_factory(key: str, factory: Callable[[], IntegrationProvider]) -> None:
    """Register a provider factory for lazy initialization."""
    _INTEGRATION_PROVIDER_FACTORIES[key] = factory


def get_provider(key: str) -> Optional[IntegrationProvider]:
    if key not in _INTEGRATION_PROVIDERS and key in _INTEGRATION_PROVIDER_FACTORIES:
        base_provider = _INTEGRATION_PROVIDER_FACTORIES[key]()
        # Wrap with enhanced error handling
        _INTEGRATION_PROVIDERS[key] = create_enhanced_provider(base_provider)
    return _INTEGRATION_PROVIDERS.get(key)


def list_providers() -> Dict[str, IntegrationProvider]:
    for key in list(_INTEGRATION_PROVIDER_FACTORIES.keys()):
        get_provider(key)
    return dict(_INTEGRATION_PROVIDERS)


def ensure_default_providers_registered() -> None:
    """Register default providers for the Week 3 migration bridge."""
    if _INTEGRATION_PROVIDER_FACTORIES:
        return
    register_provider_factory("gsc", GSCIntegrationProvider)
    register_provider_factory("bing", BingIntegrationProvider)
    register_provider_factory("wordpress", WordPressIntegrationProvider)
    register_provider_factory("wix", WixIntegrationProvider)


# Keep legacy paths in use for onboarding/monitoring until Week 3.
ensure_default_providers_registered()
