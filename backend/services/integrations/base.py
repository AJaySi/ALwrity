"""Shared integration interfaces and models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol


@dataclass(frozen=True)
class ConnectionStatus:
    """Normalized connection status for an integration provider."""

    connected: bool
    provider_id: str
    expires_at: Optional[datetime] = None
    refreshable: bool = False
    last_checked: datetime = field(default_factory=datetime.utcnow)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass(frozen=True)
class AuthUrlPayload:
    """Payload for OAuth authorization URL responses."""

    url: str
    provider_id: str
    state: Optional[str] = None
    expires_in: Optional[int] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ConnectionResult:
    """Result from handling OAuth callbacks."""

    success: bool
    provider_id: str
    user_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None


@dataclass(frozen=True)
class RefreshResult:
    """Result from refresh operations."""

    success: bool
    provider_id: str
    refreshed: bool
    expires_at: Optional[datetime] = None
    details: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None


@dataclass(frozen=True)
class ConnectedAccount:
    """Normalized connected account descriptor."""

    account_id: str
    name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class IntegrationProvider(Protocol):
    """Contract for integration providers used by the registry layer."""

    key: str
    display_name: str

    def get_auth_url(self, user_id: str, redirect_uri: Optional[str] = None) -> AuthUrlPayload:
        ...

    def handle_callback(self, code: str, state: str) -> ConnectionResult:
        ...

    def get_connection_status(self, user_id: str) -> ConnectionStatus:
        ...

    def refresh_token(self, user_id: str) -> Optional[RefreshResult]:
        ...

    def disconnect(self, user_id: str) -> bool:
        ...

    def list_connected_accounts(self, user_id: str) -> List[ConnectedAccount]:
        ...
