import sys
import types
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient


# Stub heavy modules before importing router under test.
fake_registry_module = types.ModuleType("services.integrations.registry")
fake_registry_module.get_provider = lambda _key: None
sys.modules["services.integrations.registry"] = fake_registry_module

fake_gsc_service_module = types.ModuleType("services.gsc_service")


class _FakeGSCService:
    def handle_oauth_callback(self, code, state):
        return {"success": True, "user_id": "user-123"}

    def get_site_list(self, user_id):
        return []

    def clear_incomplete_credentials(self, user_id):
        return True

    def get_search_analytics(self, *args, **kwargs):
        return {}

    def get_sitemaps(self, *args, **kwargs):
        return []

    def get_latest_cached_analytics(self, *args, **kwargs):
        return None


fake_gsc_service_module.GSCService = _FakeGSCService
sys.modules["services.gsc_service"] = fake_gsc_service_module

from routers import gsc_auth  # noqa: E402
from middleware.auth_middleware import get_current_user  # noqa: E402


class MockProvider:
    def __init__(self, *, connected=True, disconnect_success=True):
        self._connected = connected
        self._disconnect_success = disconnect_success

    def get_auth_url(self, user_id: str):
        return SimpleNamespace(
            auth_url="https://accounts.google.com/o/oauth2/auth?state=test-state-123",
            state="test-state-123",
        )

    def get_connection_status(self, user_id: str):
        return SimpleNamespace(connected=self._connected)

    def disconnect(self, user_id: str):
        return self._disconnect_success


def _build_client(monkeypatch, provider: MockProvider, gsc_service_mock: SimpleNamespace):
    app = FastAPI()
    app.include_router(gsc_auth.router)

    app.dependency_overrides[get_current_user] = lambda: {"id": "user-123"}

    monkeypatch.setattr(gsc_auth, "get_provider", lambda _key: provider)
    monkeypatch.setattr(gsc_auth, "gsc_service", gsc_service_mock)
    monkeypatch.setattr(
        gsc_auth,
        "get_trusted_origins_for_redirect",
        lambda *_args, **_kwargs: ["http://testserver"],
    )

    return TestClient(app)


def test_auth_url_generation(monkeypatch):
    provider = MockProvider()
    gsc_service_mock = SimpleNamespace()
    client = _build_client(monkeypatch, provider, gsc_service_mock)

    response = client.get("/gsc/auth/url")

    assert response.status_code == 200
    body = response.json()
    assert body["auth_url"].startswith("https://accounts.google.com")
    assert body["state"] == "test-state-123"
    assert "http://testserver" in body["trusted_origins"]


def test_callback_success(monkeypatch):
    provider = MockProvider()
    gsc_service_mock = SimpleNamespace(
        handle_oauth_callback=lambda code, state: {"success": True, "user_id": "user-123"}
    )
    client = _build_client(monkeypatch, provider, gsc_service_mock)

    response = client.get("/gsc/callback", params={"code": "abc", "state": "state"})

    assert response.status_code == 200
    assert "Connection Successful" in response.text
    assert "GSC_AUTH_SUCCESS" in response.text


def test_callback_failure(monkeypatch):
    provider = MockProvider()
    gsc_service_mock = SimpleNamespace(
        handle_oauth_callback=lambda code, state: {"success": False, "error": "invalid_state"}
    )
    client = _build_client(monkeypatch, provider, gsc_service_mock)

    response = client.get("/gsc/callback", params={"code": "abc", "state": "state"})

    assert response.status_code == 400
    assert "Connection Failed" in response.text
    assert "GSC_AUTH_ERROR" in response.text


def test_status_connected(monkeypatch):
    provider = MockProvider(connected=True)
    gsc_service_mock = SimpleNamespace(
        get_site_list=lambda _user_id: [{"siteUrl": "https://example.com/", "permissionLevel": "siteOwner"}]
    )
    client = _build_client(monkeypatch, provider, gsc_service_mock)

    response = client.get("/gsc/status")

    assert response.status_code == 200
    body = response.json()
    assert body["connected"] is True
    assert body["total_sites"] == 1
    assert body["sites"][0]["siteUrl"] == "https://example.com/"


def test_disconnect(monkeypatch):
    provider = MockProvider(disconnect_success=True)
    gsc_service_mock = SimpleNamespace()
    client = _build_client(monkeypatch, provider, gsc_service_mock)

    response = client.delete("/gsc/disconnect")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "Successfully disconnected" in body["message"]
