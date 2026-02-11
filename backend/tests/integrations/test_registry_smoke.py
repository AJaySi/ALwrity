from __future__ import annotations

import sys
import types
import unittest
from datetime import datetime
from typing import Optional

# Stub heavy provider modules before importing registry.
for module_name, class_name in (
    ("services.gsc_service", "GSCService"),
    ("services.integrations.bing_oauth", "BingOAuthService"),
    ("services.integrations.wordpress_oauth", "WordPressOAuthService"),
    ("services.integrations.wix_oauth", "WixOAuthService"),
    ("services.wix_service", "WixService"),
):
    module = types.ModuleType(module_name)
    setattr(module, class_name, type(class_name, (), {}))
    sys.modules[module_name] = module

from services.integrations.base import (
    Account,
    AuthUrlPayload,
    ConnectionResult,
    ConnectionStatus,
    RefreshResult,
)
from services.integrations import registry


class _FakeProvider:
    def __init__(self, key: str):
        self._key = key

    @property
    def key(self) -> str:
        return self._key

    @property
    def display_name(self) -> str:
        return self._key.upper()

    def get_auth_url(self, user_id: str, redirect_uri: Optional[str] = None) -> AuthUrlPayload:
        return AuthUrlPayload(auth_url=f"https://example.test/{self._key}", state=user_id, provider_id=self._key)

    def handle_callback(self, code: str, state: str) -> ConnectionResult:
        return ConnectionResult(success=True, user_id=state, provider_id=self._key, access_token=code)

    def get_connection_status(self, user_id: str) -> ConnectionStatus:
        return ConnectionStatus(connected=True, provider_id=self._key, user_id=user_id)

    def refresh_token(self, user_id: str) -> Optional[RefreshResult]:
        return RefreshResult(
            success=True,
            user_id=user_id,
            provider_id=self._key,
            access_token="token",
            expires_at=datetime(2030, 1, 1),
        )

    def disconnect(self, user_id: str) -> bool:
        return True

    def list_connected_accounts(self, user_id: str) -> list[Account]:
        return [Account(account_id=f"{self._key}:{user_id}", provider_id=self._key, display_name=user_id)]


class RegistrySmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self._providers_backup = dict(registry._INTEGRATION_PROVIDERS)
        self._factories_backup = dict(registry._INTEGRATION_PROVIDER_FACTORIES)
        registry._INTEGRATION_PROVIDERS.clear()
        registry._INTEGRATION_PROVIDER_FACTORIES.clear()
        for key in ("gsc", "bing", "wordpress", "wix"):
            registry.register_provider_factory(key, lambda key=key: _FakeProvider(key))

    def tearDown(self) -> None:
        registry._INTEGRATION_PROVIDERS.clear()
        registry._INTEGRATION_PROVIDER_FACTORIES.clear()
        registry._INTEGRATION_PROVIDERS.update(self._providers_backup)
        registry._INTEGRATION_PROVIDER_FACTORIES.update(self._factories_backup)

    def test_get_provider_smoke_for_supported_keys(self) -> None:
        for key in ("gsc", "bing", "wordpress", "wix"):
            with self.subTest(key=key):
                provider = registry.get_provider(key)
                self.assertIsNotNone(provider)
                assert provider is not None

                auth = provider.get_auth_url("user-1")
                self.assertEqual(auth.provider_id, key)
                self.assertEqual(auth.state, "user-1")

                callback = provider.handle_callback("code-123", "user-1")
                self.assertTrue(callback.success)
                self.assertEqual(callback.provider_id, key)

                status = provider.get_connection_status("user-1")
                self.assertTrue(status.connected)
                self.assertEqual(status.provider_id, key)
                self.assertEqual(status.user_id, "user-1")

                refreshed = provider.refresh_token("user-1")
                self.assertIsNotNone(refreshed)
                assert refreshed is not None
                self.assertTrue(refreshed.success)
                self.assertEqual(refreshed.provider_id, key)

                self.assertTrue(provider.disconnect("user-1"))
                accounts = provider.list_connected_accounts("user-1")
                self.assertEqual(len(accounts), 1)
                self.assertEqual(accounts[0].provider_id, key)

    def test_get_provider_unknown(self) -> None:
        self.assertIsNone(registry.get_provider("nope"))


if __name__ == "__main__":
    unittest.main()
