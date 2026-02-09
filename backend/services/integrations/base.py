"""Shared integration interfaces and models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol


@dataclass(frozen=True)
class ConnectionStatus:
    """Normalized connection status for an integration provider."""

    connected: bool
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass(frozen=True)
class AuthUrlPayload:
    """Payload for OAuth authorization URL responses."""

    auth_url: str
    state: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


class IntegrationProvider(Protocol):
    """Contract for integration providers used by the registry layer."""

    key: str
    display_name: str

    def get_auth_url(self, user_id: str) -> AuthUrlPayload:
        ...

    def get_connection_status(self, user_id: str) -> ConnectionStatus:
        ...
