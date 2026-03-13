import os
import sys

sys.path.insert(0, os.path.abspath("backend"))

import spacy
spacy.load = lambda _name: object()
from fastapi import FastAPI
from fastapi.testclient import TestClient

from services.database import get_db
from middleware.auth_middleware import get_current_user, get_current_user_with_query_token

from api.content_planning.api.content_strategy.endpoints import (
    utility_endpoints,
    analytics_endpoints,
    autofill_endpoints,
    streaming_endpoints,
    ai_generation_endpoints,
)


class FakeDBSession:
    pass


class FakeEnhancedStrategyDBService:
    def __init__(self, db):
        assert db is not None, "DB session should be non-null in multi-tenant mode"

    async def get_enhanced_strategies_with_analytics(self, strategy_id):
        return [{"id": strategy_id, "name": "S1"}]


class FakeEnhancedStrategyService:
    def __init__(self, db_service):
        self.db_service = db_service

    async def _get_onboarding_data(self, user_id):
        return {"user_id": user_id, "company": "Acme"}

    async def get_enhanced_strategies(self, user_id, strategy_id, db):
        assert db is not None, "DB session should be non-null in multi-tenant mode"
        return {"strategies": [{"id": strategy_id or 1}], "total_count": 1}


class FakeAutoFillRefreshService:
    def __init__(self, db):
        assert db is not None, "DB session should be non-null in multi-tenant mode"

    async def build_fresh_payload_with_transparency(self, user_id, use_ai=True, ai_only=False, yield_callback=None):
        return {"fields": {"k": "v"}, "meta": {"user_id": user_id}}


def _override_current_user():
    return {"id": "user_test_123"}


def _override_db():
    yield FakeDBSession()


def build_app():
    app = FastAPI()
    app.include_router(utility_endpoints.router, prefix="/utility")
    app.include_router(analytics_endpoints.router, prefix="/analytics")
    app.include_router(autofill_endpoints.router, prefix="/autofill")
    app.include_router(streaming_endpoints.router, prefix="/streaming")
    app.include_router(ai_generation_endpoints.router, prefix="/ai")

    app.dependency_overrides[get_current_user] = _override_current_user
    app.dependency_overrides[get_current_user_with_query_token] = _override_current_user
    app.dependency_overrides[get_db] = _override_db
    return app


def test_utility_endpoint_uses_shared_db_dependency(monkeypatch):
    app = build_app()
    monkeypatch.setattr(utility_endpoints, "EnhancedStrategyDBService", FakeEnhancedStrategyDBService)
    monkeypatch.setattr(utility_endpoints, "EnhancedStrategyService", FakeEnhancedStrategyService)

    client = TestClient(app)
    resp = client.get("/utility/onboarding-data")

    assert resp.status_code == 200
    assert resp.json().get("status") == "success"


def test_analytics_endpoint_uses_shared_db_dependency(monkeypatch):
    app = build_app()
    monkeypatch.setattr(analytics_endpoints, "EnhancedStrategyDBService", FakeEnhancedStrategyDBService)

    client = TestClient(app)
    resp = client.get("/analytics/1/analytics")

    assert resp.status_code == 200
    assert resp.json().get("status") == "success"


def test_autofill_endpoint_uses_shared_db_dependency(monkeypatch):
    app = build_app()

    class FakeDBServiceWithSave(FakeEnhancedStrategyDBService):
        async def save_autofill_insights(self, strategy_id, user_id, payload):
            class Record:
                pass

            record = Record()
            record.id = 1
            record.strategy_id = strategy_id
            record.user_id = user_id
            record.created_at = None

            return record

    monkeypatch.setattr(autofill_endpoints, "EnhancedStrategyDBService", FakeDBServiceWithSave)

    client = TestClient(app)
    resp = client.post(
        "/autofill/1/autofill/accept",
        json={"user_id": "user_test_123", "accepted_fields": {"field": "value"}},
    )

    assert resp.status_code == 200
    assert resp.json().get("status") == "success"


def test_streaming_endpoint_uses_shared_db_dependency(monkeypatch):
    app = build_app()
    monkeypatch.setattr(streaming_endpoints, "EnhancedStrategyDBService", FakeEnhancedStrategyDBService)
    monkeypatch.setattr(streaming_endpoints, "EnhancedStrategyService", FakeEnhancedStrategyService)

    client = TestClient(app)
    resp = client.get("/streaming/stream/strategies")

    assert resp.status_code == 200
    assert '"status": "success"' in resp.text


def test_ai_generation_endpoint_uses_shared_db_dependency(monkeypatch):
    app = build_app()
    monkeypatch.setattr(ai_generation_endpoints, "EnhancedStrategyDBService", FakeEnhancedStrategyDBService)
    monkeypatch.setattr(ai_generation_endpoints, "EnhancedStrategyService", FakeEnhancedStrategyService)

    client = TestClient(app)
    resp = client.get("/ai/strategy-generation-status", params={"user_id": 1})

    assert resp.status_code == 200
    assert resp.json().get("status") == "success"
