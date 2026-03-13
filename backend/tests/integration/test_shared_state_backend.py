from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.enhanced_strategy_models import Base
from services.shared_state_backend import SharedStateBackend
from models.content_strategy_state_models import (
    StrategyGenerationTaskState,
    StreamingCacheState,
)


def _build_sessions(tmp_path):
    db_path = tmp_path / "shared_state_test.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine)
    return factory(), factory()


def test_task_state_is_shared_across_workers(tmp_path):
    worker_a, worker_b = _build_sessions(tmp_path)
    backend_a = SharedStateBackend(worker_a)
    backend_b = SharedStateBackend(worker_b)

    user_id = "user_alpha"
    task_id = "task-123"
    status_payload = {"task_id": task_id, "status": "started", "progress": 5}

    backend_a.set_task_status(user_id, task_id, status_payload)
    read_from_worker_b = backend_b.get_task_status(user_id, task_id)

    assert read_from_worker_b is not None
    assert read_from_worker_b["status"] == "started"
    assert read_from_worker_b["progress"] == 5


def test_latest_strategy_is_shared_across_workers(tmp_path):
    worker_a, worker_b = _build_sessions(tmp_path)
    backend_a = SharedStateBackend(worker_a)
    backend_b = SharedStateBackend(worker_b)

    backend_a.set_latest_strategy(
        user_id="tenant-1",
        strategy_payload={"user_id": "tenant-1", "strategy": {"pillar": "SEO"}, "task_id": "t1"},
    )

    latest = backend_b.get_latest_strategy("tenant-1")
    assert latest is not None
    assert latest["strategy"]["pillar"] == "SEO"


def test_streaming_cache_ttl_expiry_returns_not_found(tmp_path):
    worker_a, worker_b = _build_sessions(tmp_path)
    backend_a = SharedStateBackend(worker_a)
    backend_b = SharedStateBackend(worker_b)

    backend_a.set_streaming_cache("tenant-2", "strategic_intelligence", {"value": 42}, ttl_seconds=1)

    cache_row = worker_a.query(StreamingCacheState).filter_by(user_id="tenant-2", cache_key="strategic_intelligence").first()
    cache_row.expires_at = datetime.utcnow() - timedelta(seconds=1)
    worker_a.commit()

    assert backend_b.get_streaming_cache("tenant-2", "strategic_intelligence") is None


def test_expired_task_returns_none_for_not_found_handling(tmp_path):
    worker_a, worker_b = _build_sessions(tmp_path)
    backend_a = SharedStateBackend(worker_a)
    backend_b = SharedStateBackend(worker_b)

    backend_a.set_task_status("tenant-3", "task-expired", {"status": "completed"})
    task_row = worker_a.query(StrategyGenerationTaskState).filter_by(user_id="tenant-3", task_id="task-expired").first()
    task_row.expires_at = datetime.utcnow() - timedelta(seconds=1)
    worker_a.commit()

    assert backend_b.get_task_status("tenant-3", "task-expired") is None
