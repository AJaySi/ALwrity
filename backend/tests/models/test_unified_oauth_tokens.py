from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[3]))

from backend.models.unified_oauth_tokens import UnifiedOAuthToken


def test_is_expired_returns_true_when_past_expiration():
    token = UnifiedOAuthToken(
        provider_id="gsc",
        user_id="user-1",
        access_token="access",
        expires_at=datetime.utcnow() - timedelta(minutes=1),
    )

    assert token.is_expired() is True


def test_is_expired_returns_false_without_expiration():
    token = UnifiedOAuthToken(
        provider_id="gsc",
        user_id="user-1",
        access_token="access",
    )

    assert token.is_expired() is False


def test_needs_refresh_true_within_buffer_and_refresh_token_present():
    token = UnifiedOAuthToken(
        provider_id="gsc",
        user_id="user-1",
        access_token="access",
        refresh_token="refresh",
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )

    assert token.needs_refresh(buffer_minutes=30) is True


def test_needs_refresh_false_without_refresh_token():
    token = UnifiedOAuthToken(
        provider_id="gsc",
        user_id="user-1",
        access_token="access",
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )

    assert token.needs_refresh(buffer_minutes=30) is False


def test_token_metadata_serialization_and_deserialization_round_trip():
    token = UnifiedOAuthToken(
        provider_id="gsc",
        user_id="user-1",
        access_token="access",
    )

    metadata = {"tenant": "acme", "permissions": ["read", "write"]}
    token.token_metadata = metadata

    assert token.metadata_json is not None
    assert token.token_metadata == metadata


def test_token_metadata_handles_invalid_json_gracefully():
    token = UnifiedOAuthToken(
        provider_id="gsc",
        user_id="user-1",
        access_token="access",
        metadata_json="{invalid-json}",
    )

    assert token.token_metadata == {}
