from __future__ import annotations

import unittest
from typing import Optional

from services.integrations.base import (
    Account,
    AuthUrlPayload,
    ConnectionResult,
    ConnectionStatus,
    RefreshResult,
)
from services.integrations.enhanced_integration_provider import EnhancedIntegrationProvider


class _AlwaysSuccessProvider:
    key = "success"
    display_name = "Success"

    def get_auth_url(self, user_id: str, redirect_uri: Optional[str] = None) -> AuthUrlPayload:
        return AuthUrlPayload(auth_url="https://example.test/success", state=user_id, provider_id=self.key)

    def handle_callback(self, code: str, state: str) -> ConnectionResult:
        return ConnectionResult(success=True, user_id=state, provider_id=self.key, access_token=code)

    def get_connection_status(self, user_id: str) -> ConnectionStatus:
        return ConnectionStatus(connected=True, provider_id=self.key, user_id=user_id)

    def refresh_token(self, user_id: str) -> Optional[RefreshResult]:
        return RefreshResult(success=True, user_id=user_id, provider_id=self.key, access_token="ok")

    def disconnect(self, user_id: str) -> bool:
        return True

    def list_connected_accounts(self, user_id: str) -> list[Account]:
        return [Account(account_id="1", provider_id=self.key, display_name=user_id)]


class _AlwaysFailProvider:
    key = "failure"
    display_name = "Failure"

    def get_auth_url(self, user_id: str, redirect_uri: Optional[str] = None) -> AuthUrlPayload:
        raise RuntimeError("auth exploded")

    def handle_callback(self, code: str, state: str) -> ConnectionResult:
        raise RuntimeError("callback exploded")

    def get_connection_status(self, user_id: str) -> ConnectionStatus:
        raise RuntimeError("status exploded")

    def refresh_token(self, user_id: str) -> Optional[RefreshResult]:
        raise RuntimeError("refresh exploded")

    def disconnect(self, user_id: str) -> bool:
        raise RuntimeError("disconnect exploded")

    def list_connected_accounts(self, user_id: str) -> list[Account]:
        raise RuntimeError("accounts exploded")


class EnhancedProviderContractTests(unittest.TestCase):
    def test_success_path_passthrough(self) -> None:
        wrapped = EnhancedIntegrationProvider(_AlwaysSuccessProvider())
        wrapped.max_retries = 0

        self.assertEqual(wrapped.get_auth_url("u-1").provider_id, "success")
        self.assertTrue(wrapped.handle_callback("abc", "u-1").success)
        self.assertTrue(wrapped.get_connection_status("u-1").connected)
        self.assertTrue(wrapped.refresh_token("u-1").success)
        self.assertTrue(wrapped.disconnect("u-1"))
        self.assertEqual(len(wrapped.list_connected_accounts("u-1")), 1)

    def test_failure_path_returns_safe_fallbacks(self) -> None:
        wrapped = EnhancedIntegrationProvider(_AlwaysFailProvider())
        wrapped.max_retries = 0

        auth = wrapped.get_auth_url("u-2")
        self.assertEqual(auth.provider_id, "failure")
        self.assertEqual(auth.auth_url, "")

        callback = wrapped.handle_callback("code", "u-2")
        self.assertFalse(callback.success)
        self.assertEqual(callback.provider_id, "failure")
        self.assertEqual(callback.user_id, "u-2")

        status = wrapped.get_connection_status("u-2")
        self.assertFalse(status.connected)
        self.assertEqual(status.provider_id, "failure")
        self.assertEqual(status.user_id, "u-2")

        refresh = wrapped.refresh_token("u-2")
        self.assertIsNotNone(refresh)
        assert refresh is not None
        self.assertFalse(refresh.success)
        self.assertEqual(refresh.provider_id, "failure")

        self.assertFalse(wrapped.disconnect("u-2"))
        self.assertEqual(wrapped.list_connected_accounts("u-2"), [])


if __name__ == "__main__":
    unittest.main()
