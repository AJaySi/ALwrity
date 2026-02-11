"""Regression tests to ensure Bing OAuth route responses never expose tokens."""

import importlib
import sys
from unittest.mock import Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient


TOKEN_SUBSTRINGS = ["access_token", "refresh_token", "accessToken", "refreshToken", "token-secret"]


def _build_test_client(mock_service: Mock) -> TestClient:
    """Build a FastAPI TestClient with a mocked Bing OAuth service."""
    sys.modules.pop("routers.bing_oauth", None)

    with patch("services.integrations.bing_oauth.BingOAuthService", return_value=mock_service):
        router_module = importlib.import_module("routers.bing_oauth")

    app = FastAPI()
    app.include_router(router_module.router)
    app.dependency_overrides[router_module.get_current_user] = lambda: {"id": "test-user"}
    return TestClient(app)


def test_bing_status_redacts_token_fields():
    """/bing/status should not include token fields even when service returns them."""
    mock_service = Mock()
    mock_service.get_connection_status.return_value = {
        "connected": True,
        "total_sites": 1,
        "sites": [
            {
                "id": 12,
                "connection_id": 12,
                "connected": True,
                "scope": "webmaster.manage",
                "created_at": "2026-01-01T00:00:00",
                "site_count": 1,
                "sites": [{"name": "Example", "url": "https://example.com"}],
                "access_token": "token-secret",
                "refresh_token": "token-secret",
            }
        ],
        "access_token": "token-secret",
        "refresh_token": "token-secret",
    }

    client = _build_test_client(mock_service)
    response = client.get("/bing/status")

    assert response.status_code == 200
    assert response.json()["connected"] is True
    for forbidden in TOKEN_SUBSTRINGS:
        assert forbidden not in response.text


def test_bing_callback_postmessage_redacts_token_fields():
    """/bing/callback HTML output must not include token field names or values."""
    mock_service = Mock()
    mock_service.handle_oauth_callback.return_value = {
        "success": True,
        "user_id": "test-user",
        "connection_id": 55,
        "connected": True,
        "site_count": 1,
        "sites": [{"name": "Example", "url": "https://example.com"}],
        "access_token": "token-secret",
        "refresh_token": "token-secret",
    }

    client = _build_test_client(mock_service)
    response = client.get("/bing/callback", params={"code": "abc123", "state": "state123"})

    assert response.status_code == 200
    html = response.text

    assert "BING_OAUTH_SUCCESS" in html
    assert "connectionId" in html
    assert "siteCount" in html
    for forbidden in TOKEN_SUBSTRINGS:
        assert forbidden not in html
