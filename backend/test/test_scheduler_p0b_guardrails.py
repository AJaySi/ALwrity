import asyncio
import importlib.util
import sys
import types
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest



def _load_scheduler_module(module_name: str, file_path: Path):
    """Load modules directly from file without executing top-level package __init__ files."""
    parts = module_name.split('.')
    for i in range(1, len(parts)):
        pkg_name = '.'.join(parts[:i])
        if pkg_name not in sys.modules:
            pkg = types.ModuleType(pkg_name)
            pkg.__path__ = [str(file_path.parent)]
            sys.modules[pkg_name] = pkg

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


BACKEND = Path(__file__).resolve().parents[1]
MONITORING_MOD = _load_scheduler_module("api.scheduler.monitoring", BACKEND / "api" / "scheduler" / "monitoring.py")
DASHBOARD_MODEL_MOD = _load_scheduler_module("api.scheduler.models.dashboard", BACKEND / "api" / "scheduler" / "models" / "dashboard.py")


CORE_CHECK_MOD = _load_scheduler_module("services.scheduler.core.check_cycle_handler", BACKEND / "services" / "scheduler" / "core" / "check_cycle_handler.py")
check_cycle_handler = CORE_CHECK_MOD

class FakeChainQuery:
    def __init__(self, rows=None):
        self._rows = rows or []

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def offset(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def join(self, *args, **kwargs):
        return self

    def count(self):
        return len(self._rows)

    def all(self):
        return list(self._rows)

    def first(self):
        return self._rows[0] if self._rows else None

    def scalar(self):
        return len(self._rows)


class FakeDB:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.added = []
        self.closed = False
        self.queried_after_close = False

    def query(self, *args, **kwargs):
        if self.closed:
            self.queried_after_close = True
            raise RuntimeError("query on closed session")
        return FakeChainQuery(self.rows)

    def add(self, obj):
        self.added.append(obj)

    def flush(self):
        if self.added and getattr(self.added[-1], "id", None) is None:
            self.added[-1].id = len(self.added)

    def commit(self):
        return None

    def rollback(self):
        return None

    def close(self):
        self.closed = True




def test_dashboard_contract_model_shape():
    payload = DASHBOARD_MODEL_MOD.SchedulerDashboardResponse(
        stats={
            "total_checks": 1,
            "tasks_found": 1,
            "tasks_executed": 1,
            "tasks_failed": 0,
            "tasks_skipped": 0,
            "last_check": datetime.utcnow(),
            "last_update": datetime.utcnow(),
            "active_executions": 0,
            "running": True,
            "check_interval_minutes": 15,
            "min_check_interval_minutes": 15,
            "max_check_interval_minutes": 60,
            "intelligent_scheduling": True,
            "active_strategies_count": 1,
            "last_interval_adjustment": None,
            "registered_types": ["monitoring_task"],
            "cumulative_total_check_cycles": 1,
            "cumulative_tasks_found": 1,
            "cumulative_tasks_executed": 1,
            "cumulative_tasks_failed": 0
        },
        jobs=[],
        job_count=0,
        recurring_jobs=1,
        one_time_jobs=0,
        registered_task_types=["monitoring_task"],
        user_isolation={"enabled": True, "current_user_id": "user_1"}
    ).model_dump()

    for key in ["stats", "jobs", "job_count", "recurring_jobs", "one_time_jobs", "registered_task_types", "user_isolation"]:
        assert key in payload

@pytest.mark.asyncio
async def test_execution_logs_contract(monkeypatch):
    monkeypatch.setattr(MONITORING_MOD, "aggregate_execution_logs", lambda **kwargs: {
        "logs": [{
            "id": 1,
            "task_id": 1,
            "user_id": "user_1",
            "execution_date": datetime.utcnow().isoformat(),
            "status": "success",
            "error_message": None,
            "execution_time_ms": 10,
            "result_data": {},
            "created_at": datetime.utcnow().isoformat(),
            "task": {
                "id": 1,
                "task_title": "Test",
                "component_name": "Scheduler",
                "metric": "m",
                "frequency": "Daily",
            },
        }],
        "total_count": 1,
        "limit": 50,
        "offset": 0,
        "has_more": False,
        "is_scheduler_logs": False,
    })

    response = await MONITORING_MOD.get_execution_logs(
        limit=50,
        offset=0,
        status=None,
        current_user={"sub": "user_1"},
        db=FakeDB(),
    )
    payload = response.model_dump()
    for key in ["logs", "total_count", "limit", "offset", "has_more"]:
        assert key in payload


@pytest.mark.asyncio
async def test_event_history_contract(monkeypatch):
    monkeypatch.setattr(MONITORING_MOD, "aggregate_event_history", lambda **kwargs: {
        "events": [{
            "id": 1,
            "event_type": "check_cycle",
            "event_date": datetime.utcnow().isoformat(),
            "check_cycle_number": 1,
            "check_interval_minutes": 15,
            "previous_interval_minutes": None,
            "new_interval_minutes": None,
            "tasks_found": 0,
            "tasks_executed": 0,
            "tasks_failed": 0,
            "tasks_by_type": {},
            "check_duration_seconds": 0.1,
            "active_strategies_count": 0,
            "active_executions": 0,
            "job_id": None,
            "job_type": None,
            "user_id": "user_1",
            "event_data": {},
            "error_message": None,
            "created_at": datetime.utcnow().isoformat(),
        }],
        "total_count": 1,
        "limit": 50,
        "offset": 0,
        "has_more": False,
        "date_filter": {"days": 7, "cutoff_date": datetime.utcnow().isoformat(), "showing_events_since": datetime.utcnow().isoformat()},
    })

    response = await MONITORING_MOD.get_event_history(
        limit=50,
        offset=0,
        event_type="check_cycle",
        days=7,
        current_user={"sub": "user_1"},
        db=FakeDB(),
    )
    payload = response.model_dump()
    for key in ["events", "total_count", "limit", "offset", "has_more"]:
        assert key in payload


@pytest.mark.asyncio
async def test_platform_insights_logs_contract(monkeypatch):
    log = SimpleNamespace(
        id=1,
        task_id=10,
        execution_date=datetime.utcnow(),
        status="success",
        result_data={},
        error_message=None,
        execution_time_ms=123,
        data_source="api",
        created_at=datetime.utcnow(),
    )
    db = FakeDB(rows=[log])
    monkeypatch.setattr(MONITORING_MOD, "validate_user_access", lambda *args, **kwargs: "user_1")

    response = await MONITORING_MOD.get_platform_insights_logs(
        user_id="user_1",
        limit=10,
        offset=0,
        task_id=10,
        current_user={"sub": "user_1"},
        db=db,
    )

    assert response["success"] is True
    assert "logs" in response
    assert "total_count" in response


@pytest.mark.asyncio
async def test_smoke_check_cycle_persists_event_log(monkeypatch):
    fake_db = FakeDB()

    class FakeRegistry:
        def get_registered_types(self):
            return []

    scheduler = SimpleNamespace(
        stats={
            "total_checks": 0,
            "last_check": None,
            "active_strategies_count": 0,
            "tasks_skipped": 0,
            "last_update": None,
        },
        current_check_interval_minutes=15,
        active_executions={},
        max_concurrent_executions=10,
        registry=FakeRegistry(),
        _process_task_type=lambda *args, **kwargs: asyncio.sleep(0),
        exception_handler=SimpleNamespace(handle_exception=lambda *args, **kwargs: None),
    )

    monkeypatch.setattr(check_cycle_handler, "get_db_session", lambda: fake_db)

    async def _noop_adjust(*args, **kwargs):
        return None

    monkeypatch.setattr(check_cycle_handler, "adjust_check_interval_if_needed", _noop_adjust)

    class _CumStats:
        total_check_cycles = 0
        cumulative_tasks_found = 0
        cumulative_tasks_executed = 0
        cumulative_tasks_failed = 0
        cumulative_tasks_skipped = 0
        last_check_cycle_id = None
        last_updated = None
        updated_at = None

    monkeypatch.setattr(check_cycle_handler.SchedulerCumulativeStats, "get_or_create", lambda db: _CumStats())

    await check_cycle_handler.check_and_execute_due_tasks(scheduler)
    assert any(getattr(e, "event_type", None) == "check_cycle" for e in fake_db.added)




def test_startup_db_session_lifecycle_fix_present():
    scheduler_source = Path(__file__).resolve().parents[1] / "services" / "scheduler" / "core" / "scheduler.py"
    content = scheduler_source.read_text()
    assert "db_counts = get_db_session()" in content
    assert "if db_counts:" in content
    assert "db_counts.close()" in content
