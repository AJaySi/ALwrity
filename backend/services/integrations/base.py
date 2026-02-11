"""Shared integration interfaces and models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol
from datetime import datetime


@dataclass
class Account:
    """Represents a connected account."""
    account_id: str
    provider_id: str
    display_name: str
    email: Optional[str] = None
    connected_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True


@dataclass
class ConnectionResult:
    """Result of OAuth callback handling."""
    success: bool
    user_id: str
    provider_id: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    scope: Optional[str] = None
    error: Optional[str] = None
    account_info: Optional[Dict[str, Any]] = None


@dataclass
class RefreshResult:
    """Result of token refresh operation."""
    success: bool
    user_id: str
    provider_id: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    error: Optional[str] = None


@dataclass
class ConnectionStatus:
    """Standardized connection status across all providers."""
    connected: bool
    provider_id: str
    user_id: str
    expires_at: Optional[datetime] = None
    refreshable: bool = True
    last_checked: Optional[datetime] = None
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class AuthUrlPayload:
    """Payload for OAuth authorization URL."""
    auth_url: str
    state: str
    provider_id: str
    expires_in: Optional[int] = None
    details: Dict[str, Any] = field(default_factory=dict)


class IntegrationProvider(Protocol):
    """Contract for integration providers used by the registry layer."""

    @property
    def key(self) -> str: ...

    @property
    def display_name(self) -> str: ...

    def get_auth_url(self, user_id: str, redirect_uri: Optional[str] = None) -> AuthUrlPayload: ...

    def handle_callback(self, code: str, state: str) -> ConnectionResult: ...

    def get_connection_status(self, user_id: str) -> ConnectionStatus: ...

    def refresh_token(self, user_id: str) -> Optional[RefreshResult]: ...

    def disconnect(self, user_id: str) -> bool: ...

    def list_connected_accounts(self, user_id: str) -> List[Account]: ...
