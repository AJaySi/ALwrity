"""
OAuth Provider Registry

Central registry for OAuth provider services and token status checks.
"""

from dataclasses import dataclass
from typing import Callable, Dict, Optional, Any

from services.gsc_service import GSCService
from services.integrations.bing_oauth import BingOAuthService
from services.integrations.wordpress_oauth import WordPressOAuthService
from services.integrations.wix_oauth import WixOAuthService


@dataclass(frozen=True)
class ProviderConfig:
    """Configuration for a provider in the registry."""

    platform: str
    factory: Callable[[], Any]


class ProviderRegistry:
    """Registry for provider services."""

    def __init__(self):
        self._configs: Dict[str, ProviderConfig] = {
            "gsc": ProviderConfig(platform="gsc", factory=GSCService),
            "bing": ProviderConfig(platform="bing", factory=BingOAuthService),
            "wordpress": ProviderConfig(platform="wordpress", factory=WordPressOAuthService),
            "wix": ProviderConfig(platform="wix", factory=WixOAuthService),
        }
        self._instances: Dict[str, Any] = {}

    def get_provider(self, platform: str) -> Optional[ProviderConfig]:
        """Get the provider configuration for a platform."""
        return self._configs.get(platform)

    def get_service(self, platform: str) -> Optional[Any]:
        """Get (or create) a provider service instance."""
        if platform not in self._configs:
            return None
        if platform not in self._instances:
            self._instances[platform] = self._configs[platform].factory()
        return self._instances[platform]

    def get_registered_platforms(self) -> Dict[str, ProviderConfig]:
        """Return registered provider configurations."""
        return self._configs.copy()
