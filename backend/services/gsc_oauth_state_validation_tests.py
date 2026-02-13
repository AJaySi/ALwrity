from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from services.gsc_service import GSCService


class DummyCredentials:
    token = "token"
    refresh_token = "refresh"
    token_uri = "https://oauth2.googleapis.com/token"
    client_id = "client-id"
    client_secret = "client-secret"
    scopes = ["https://www.googleapis.com/auth/webmasters.readonly"]


class DummyFlow:
    def __init__(self):
        self.credentials = DummyCredentials()

    def fetch_token(self, code):
        return None


@pytest.fixture
def gsc_service(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)

    def fake_db_session():
        return Session()

    monkeypatch.setattr("services.gsc_service.get_user_data_db_session", fake_db_session)
    monkeypatch.setattr(GSCService, "_init_gsc_tables", lambda self: None)

    service = GSCService()

    with service._db_session() as db:
        db.execute(
            text(
                """
                CREATE TABLE gsc_oauth_states (
                    state TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
                """
            )
        )

    monkeypatch.setattr(
        "services.gsc_service.Flow.from_client_secrets_file",
        lambda *args, **kwargs: DummyFlow(),
    )

    saved_users = []

    def fake_save_user_credentials(user_id, credentials):
        saved_users.append(user_id)
        return True

    monkeypatch.setattr(service, "save_user_credentials", fake_save_user_credentials)

    return service, saved_users


def insert_state(service, state, user_id, expires_at):
    with service._db_session() as db:
        db.execute(
            text(
                """
                INSERT INTO gsc_oauth_states (state, user_id, expires_at)
                VALUES (:state, :user_id, :expires_at)
                """
            ),
            {"state": state, "user_id": user_id, "expires_at": expires_at},
        )


def count_state(service, state):
    with service._db_session() as db:
        result = db.execute(
            text("SELECT COUNT(*) FROM gsc_oauth_states WHERE state = :state"),
            {"state": state},
        ).fetchone()
    return result[0]


def test_callback_rejects_missing_state(gsc_service):
    service, _ = gsc_service

    result = service.handle_oauth_callback("code", "")

    assert result["success"] is False
    assert result["error"] == "Invalid OAuth state: missing state parameter"


def test_callback_rejects_unknown_state(gsc_service):
    service, saved_users = gsc_service

    result = service.handle_oauth_callback("code", "unknown-state")

    assert result["success"] is False
    assert result["error"] == "Invalid OAuth state: state not found"
    assert saved_users == []


def test_callback_rejects_reused_state(gsc_service):
    service, saved_users = gsc_service
    valid_until = datetime.utcnow() + timedelta(minutes=10)
    insert_state(service, "single-use-state", "user-1", valid_until)

    first_result = service.handle_oauth_callback("code", "single-use-state")
    second_result = service.handle_oauth_callback("code", "single-use-state")

    assert first_result == {"success": True, "user_id": "user-1"}
    assert second_result["success"] is False
    assert second_result["error"] == "Invalid OAuth state: state not found"
    assert saved_users == ["user-1"]


def test_callback_rejects_expired_state(gsc_service):
    service, saved_users = gsc_service
    expired_at = datetime.utcnow() - timedelta(minutes=1)
    insert_state(service, "expired-state", "user-1", expired_at)

    result = service.handle_oauth_callback("code", "expired-state")

    assert result["success"] is False
    assert result["error"] == "Invalid OAuth state: state expired"
    assert saved_users == []


def test_callback_rejects_cross_user_state_mismatch(gsc_service):
    service, saved_users = gsc_service
    valid_until = datetime.utcnow() + timedelta(minutes=10)
    insert_state(service, "state-user-1", "user-1", valid_until)
    insert_state(service, "state-user-2", "user-2", valid_until)

    result = service.handle_oauth_callback("code", "state-user-3")

    assert result["success"] is False
    assert result["error"] == "Invalid OAuth state: state not found"
    assert count_state(service, "state-user-1") == 1
    assert count_state(service, "state-user-2") == 1
    assert saved_users == []
