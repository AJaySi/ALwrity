"""Integration registry with thin adapters for legacy providers."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Callable, Dict, Optional, List, Any

from services.gsc_service import GSCService
from services.integrations.bing_oauth import BingOAuthService
from services.integrations.wordpress_oauth import WordPressOAuthService
from services.integrations.wix_oauth import WixOAuthService
from services.wix_service import WixService

from .base import (
    AuthUrlPayload,
    ConnectionStatus,
    IntegrationProvider,
    ConnectionResult,
    RefreshResult,
    ConnectedAccount,
)
from .enhanced_integration_provider import create_enhanced_provider


class GSCIntegrationProvider:
    key = "gsc"
    display_name = "Google Search Console"

    def __init__(self, service: Optional[GSCService] = None) -> None:
        self._service = service or GSCService()

    def get_auth_url(self, user_id: str, redirect_uri: Optional[str] = None) -> AuthUrlPayload:
        auth_url = self._service.get_oauth_url(user_id)
        return AuthUrlPayload(url=auth_url, provider_id=self.key)

    def handle_callback(self, code: str, state: str) -> ConnectionResult:
        result = self._service.handle_oauth_callback(code, state)
        success = bool(result.get("success")) if isinstance(result, dict) else bool(result)
        return ConnectionResult(
            success=success,
            provider_id=self.key,
            user_id=result.get("user_id") if isinstance(result, dict) else None,
            details=result if isinstance(result, dict) else {},
        )

    def get_connection_status(self, user_id: str) -> ConnectionStatus:
        credentials = self._service.load_user_credentials(user_id)
        if not credentials:
            return ConnectionStatus(
                connected=False,
                provider_id=self.key,
                refreshable=False,
                details={"has_credentials": False},
            )

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
        return ConnectionStatus(
            connected=connected,
            provider_id=self.key,
            expires_at=getattr(credentials, "expiry", None),
            refreshable=bool(refresh_token),
            warnings=["Token expired"] if expired else [],
            details=details,
        )

    def refresh_token(self, user_id: str) -> Optional[RefreshResult]:
        credentials = self._service.load_user_credentials(user_id)
        if not credentials:
            return RefreshResult(
                success=False,
                refreshed=False,
                provider_id=self.key,
                error="No GSC credentials available",
            )
        expired = bool(getattr(credentials, "expired", False))
        return RefreshResult(
            success=True,
            refreshed=expired,
            provider_id=self.key,
            expires_at=getattr(credentials, "expiry", None),
            details={"expired_before_refresh": expired},
        )

    def disconnect(self, user_id: str) -> bool:
        return self._service.revoke_user_access(user_id)

    def list_connected_accounts(self, user_id: str) -> List[ConnectedAccount]:
        return []


class BingIntegrationProvider:
    key = "bing"
    display_name = "Bing Webmaster Tools"

    def __init__(self, service: Optional[BingOAuthService] = None) -> None:
        self._service = service or BingOAuthService()

    def get_auth_url(self, user_id: str, redirect_uri: Optional[str] = None) -> AuthUrlPayload:
        payload = self._service.generate_authorization_url(user_id)
        if not payload or "auth_url" not in payload:
            return AuthUrlPayload(
                url="",
                provider_id=self.key,
                details={"error": "Unable to generate auth URL."},
            )
        return AuthUrlPayload(
            url=payload["auth_url"],
            provider_id=self.key,
            state=payload.get("state"),
            details={"redirect_uri": self._service.redirect_uri},
        )

    def handle_callback(self, code: str, state: str) -> ConnectionResult:
        result = self._service.handle_oauth_callback(code, state)
        success = bool(result.get("success")) if isinstance(result, dict) else bool(result)
        return ConnectionResult(
            success=success,
            provider_id=self.key,
            user_id=result.get("user_id") if isinstance(result, dict) else None,
            details=result if isinstance(result, dict) else {},
        )

    def get_connection_status(self, user_id: str) -> ConnectionStatus:
        status = self._service.get_user_token_status(user_id)
        active_tokens = status.get("active_tokens", [])
        expired_tokens = status.get("expired_tokens", [])
        refreshable_tokens = [
            token for token in (active_tokens + expired_tokens) if token.get("refresh_token")
        ]
        expires_at = _get_soonest_expiry(active_tokens)
        connected = bool(status.get("has_active_tokens") or refreshable_tokens)
        return ConnectionStatus(
            connected=connected,
            provider_id=self.key,
            expires_at=expires_at,
            refreshable=bool(refreshable_tokens),
            warnings=["Token expired"] if status.get("has_expired_tokens") else [],
            details=status,
            error=status.get("error"),
        )

    def refresh_token(self, user_id: str) -> Optional[RefreshResult]:
        status = self._service.get_user_token_status(user_id)
        expired_tokens = status.get("expired_tokens", [])
        active_tokens = status.get("active_tokens", [])
        token = _select_refreshable_token(expired_tokens) or _select_refreshable_token(active_tokens)
        if not token:
            return RefreshResult(
                success=False,
                refreshed=False,
                provider_id=self.key,
                error="No refreshable Bing tokens found",
            )
        refreshed = self._service.refresh_access_token(user_id, token["refresh_token"])
        if not refreshed:
            return RefreshResult(
                success=False,
                refreshed=False,
                provider_id=self.key,
                error="Failed to refresh Bing token",
            )
        expires_at = refreshed.get("expires_at")
        if not expires_at and refreshed.get("expires_in"):
            expires_at = datetime.utcnow() + timedelta(seconds=int(refreshed["expires_in"]))
        return RefreshResult(
            success=True,
            refreshed=True,
            provider_id=self.key,
            expires_at=expires_at,
            details={"token_id": token.get("id")},
        )

    def disconnect(self, user_id: str) -> bool:
        tokens = self._service.get_user_tokens(user_id)
        success = True
        for token in tokens:
            success = self._service.revoke_token(user_id, token["id"]) and success
        return success

    def list_connected_accounts(self, user_id: str) -> List[ConnectedAccount]:
        tokens = self._service.get_user_tokens(user_id)
        return [
            ConnectedAccount(
                account_id=str(token.get("id")),
                name=token.get("site_url"),
                metadata=token,
            )
            for token in tokens
        ]


class WordPressIntegrationProvider:
    key = "wordpress"
    display_name = "WordPress"

    def __init__(self, service: Optional[WordPressOAuthService] = None) -> None:
        self._service = service or WordPressOAuthService()

    def get_auth_url(self, user_id: str, redirect_uri: Optional[str] = None) -> AuthUrlPayload:
        payload = self._service.generate_authorization_url(user_id)
        if not payload or "auth_url" not in payload:
            return AuthUrlPayload(
                url="",
                provider_id=self.key,
                details={"error": "Unable to generate auth URL."},
            )
        return AuthUrlPayload(
            url=payload["auth_url"],
            provider_id=self.key,
            state=payload.get("state"),
            details={"redirect_uri": self._service.redirect_uri},
        )

    def handle_callback(self, code: str, state: str) -> ConnectionResult:
        result = self._service.handle_oauth_callback(code, state)
        success = bool(result.get("success")) if isinstance(result, dict) else bool(result)
        return ConnectionResult(
            success=success,
            provider_id=self.key,
            user_id=result.get("user_id") if isinstance(result, dict) else None,
            details=result if isinstance(result, dict) else {},
        )

    def get_connection_status(self, user_id: str) -> ConnectionStatus:
        status = self._service.get_user_token_status(user_id)
        tokens = status.get("active_tokens", []) or status.get("expired_tokens", [])
        expires_at = _get_soonest_expiry(tokens)
        connected = bool(status.get("has_tokens"))
        return ConnectionStatus(
            connected=connected,
            provider_id=self.key,
            expires_at=expires_at,
            refreshable=False,
            warnings=["Token expired"] if status.get("has_expired_tokens") else [],
            details=status,
            error=status.get("error"),
        )

    def refresh_token(self, user_id: str) -> Optional[RefreshResult]:
        return None

    def disconnect(self, user_id: str) -> bool:
        tokens = self._service.get_user_tokens(user_id)
        success = True
        for token in tokens:
            success = self._service.revoke_token(user_id, token["id"]) and success
        return success

    def list_connected_accounts(self, user_id: str) -> List[ConnectedAccount]:
        tokens = self._service.get_user_tokens(user_id)
        return [
            ConnectedAccount(
                account_id=str(token.get("id")),
                name=token.get("blog_url"),
                metadata=token,
            )
            for token in tokens
        ]


class WixIntegrationProvider:
    key = "wix"
    display_name = "Wix"

    def __init__(self, service: Optional[WixService] = None, oauth: Optional[WixOAuthService] = None) -> None:
        self._service = service or WixService()
        self._oauth = oauth or WixOAuthService()

    def get_auth_url(self, user_id: str, redirect_uri: Optional[str] = None) -> AuthUrlPayload:
        oauth_config = self._service.get_oauth_config()
        self._oauth.store_oauth_state(
            user_id=user_id,
            state=oauth_config["state"],
            code_verifier=oauth_config["code_verifier"],
        )
        oauth_data = {
            "state": oauth_config["state"],
            "codeVerifier": oauth_config["code_verifier"],
            "codeChallenge": oauth_config["code_challenge"],
            "redirectUri": oauth_config["redirect_uri"],
        }
        return AuthUrlPayload(
            url=oauth_config["auth_url"],
            provider_id=self.key,
            state=oauth_config["state"],
            details={
                "oauth_data": oauth_data,
                "redirect_uri": oauth_config["redirect_uri"],
                "client_id": self._service.client_id,
            },
        )

    def handle_callback(self, code: str, state: str) -> ConnectionResult:
        stored_state = self._oauth.consume_oauth_state(state)
        if not stored_state:
            return ConnectionResult(
                success=False,
                provider_id=self.key,
                error="Invalid or expired Wix OAuth state",
            )
        tokens = self._service.exchange_code_for_tokens(code, stored_state["code_verifier"])
        site_info = self._service.get_site_info(tokens["access_token"])
        site_id = site_info.get("siteId") or site_info.get("site_id")
        member_id = None
        try:
            member_id = self._service.extract_member_id_from_access_token(tokens["access_token"])
        except Exception:
            pass
        stored = self._oauth.store_tokens(
            user_id=stored_state["user_id"],
            access_token=tokens["access_token"],
            refresh_token=tokens.get("refresh_token"),
            expires_in=tokens.get("expires_in"),
            token_type=tokens.get("token_type", "Bearer"),
            scope=tokens.get("scope"),
            site_id=site_id,
            member_id=member_id,
        )
        return ConnectionResult(
            success=bool(stored),
            provider_id=self.key,
            user_id=stored_state["user_id"],
            details={"site_info": site_info, "stored": stored},
        )

    def get_connection_status(self, user_id: str) -> ConnectionStatus:
        status = self._oauth.get_user_token_status(user_id)
        active_tokens = status.get("active_tokens", [])
        expired_tokens = status.get("expired_tokens", [])
        refreshable_tokens = [
            token for token in (active_tokens + expired_tokens) if token.get("refresh_token")
        ]
        connected = bool(status.get("has_active_tokens") or refreshable_tokens)
        return ConnectionStatus(
            connected=connected,
            provider_id=self.key,
            expires_at=_get_soonest_expiry(active_tokens),
            refreshable=bool(refreshable_tokens),
            warnings=["Token expired"] if status.get("has_expired_tokens") else [],
            details=status,
            error=status.get("error"),
        )

    def refresh_token(self, user_id: str) -> Optional[RefreshResult]:
        status = self._oauth.get_user_token_status(user_id)
        expired_tokens = status.get("expired_tokens", [])
        active_tokens = status.get("active_tokens", [])
        token = _select_refreshable_token(expired_tokens) or _select_refreshable_token(active_tokens)
        if not token:
            return RefreshResult(
                success=False,
                refreshed=False,
                provider_id=self.key,
                error="No refreshable Wix tokens found",
            )
        refreshed = self._service.refresh_access_token(token["refresh_token"])
        if not refreshed:
            return RefreshResult(
                success=False,
                refreshed=False,
                provider_id=self.key,
                error="Failed to refresh Wix token",
            )
        expires_at = refreshed.get("expires_at")
        if not expires_at and refreshed.get("expires_in"):
            expires_at = datetime.utcnow() + timedelta(seconds=int(refreshed["expires_in"]))
        self._oauth.update_tokens(
            user_id=user_id,
            access_token=refreshed.get("access_token"),
            refresh_token=token.get("refresh_token"),
            expires_in=refreshed.get("expires_in"),
        )
        return RefreshResult(
            success=True,
            refreshed=True,
            provider_id=self.key,
            expires_at=expires_at,
            details={"token_id": token.get("id")},
        )

    def disconnect(self, user_id: str) -> bool:
        tokens = self._oauth.get_user_tokens(user_id)
        success = True
        for token in tokens:
            success = self._oauth.revoke_token(user_id, token["id"]) and success
        return success

    def list_connected_accounts(self, user_id: str) -> List[ConnectedAccount]:
        tokens = self._oauth.get_user_tokens(user_id)
        return [
            ConnectedAccount(
                account_id=str(token.get("id")),
                name=token.get("site_id"),
                metadata=token,
            )
            for token in tokens
        ]


def _get_soonest_expiry(tokens: List[Dict[str, Any]]) -> Optional[datetime]:
    expires_at_values = []
    for token in tokens or []:
        value = token.get("expires_at")
        if not value:
            continue
        if isinstance(value, datetime):
            expires_at_values.append(value)
            continue
        try:
            expires_at_values.append(datetime.fromisoformat(str(value).replace("Z", "+00:00")))
        except Exception:
            continue
    return min(expires_at_values) if expires_at_values else None


def _select_refreshable_token(tokens: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for token in tokens or []:
        if token.get("refresh_token"):
            return token
    return None


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
