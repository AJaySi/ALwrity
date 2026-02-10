import asyncio
import sys
import types
import importlib.util
from datetime import datetime
from pathlib import Path


BACKEND = Path(__file__).resolve().parents[1]


def _load_module(module_name: str, file_path: Path):
    parts = module_name.split('.')
    for i in range(1, len(parts)):
        pkg_name = '.'.join(parts[:i])
        if pkg_name not in sys.modules:
            pkg = types.ModuleType(pkg_name)
            pkg.__path__ = [str(file_path.parents[len(parts)-i-1])]
            sys.modules[pkg_name] = pkg

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


SCHED_MOD = _load_module("services.scheduler.core.scheduler", BACKEND / "services" / "scheduler" / "core" / "scheduler.py")


class _Registry:
    def get_task_loader(self, _task_type):
        return lambda db: [types.SimpleNamespace(id=1), types.SimpleNamespace(id=2)]

    def get_registered_types(self):
        return ["dummy"]


class _DB:
    pass


def test_task_lease_acquire_release_and_expiry():
    scheduler = SCHED_MOD.TaskScheduler()
    key = "dummy_1"

    assert scheduler._acquire_task_lease(key) is True
    assert scheduler._is_task_leased(key) is True

    # cannot re-acquire while leased
    assert scheduler._acquire_task_lease(key) is False

    scheduler._release_task_lease(key)
    assert scheduler._is_task_leased(key) is False


def test_timeout_cleanup_logic_present():
    content = (BACKEND / "services" / "scheduler" / "core" / "scheduler.py").read_text()
    assert "done, pending = await asyncio.wait(execution_tasks, timeout=300)" in content
    assert "pending_task.cancel()" in content
    assert "await asyncio.gather(*pending, return_exceptions=True)" in content


def test_redispatch_prevention_logic_present():
    content = (BACKEND / "services" / "scheduler" / "core" / "scheduler.py").read_text()
    assert "if self._is_task_leased(task_key):" in content
    assert "if not self._acquire_task_lease(task_key):" in content


def test_task_execution_releases_lease_present():
    content = (BACKEND / "services" / "scheduler" / "core" / "task_execution_handler.py").read_text()
    assert "scheduler._release_task_lease(task_id)" in content


async def _slow_execute_task_async(scheduler, task_type, task, summary):
    task_key = f"{task_type}_{getattr(task, 'id', id(task))}"
    scheduler.active_executions[task_key] = asyncio.current_task()
    try:
        await asyncio.sleep(10)
    finally:
        scheduler.active_executions.pop(task_key, None)
        scheduler._release_task_lease(task_key)


def test_pending_tasks_cancelled_and_no_lease_leak(monkeypatch):
    scheduler = SCHED_MOD.TaskScheduler()
    scheduler.registry = _Registry()
    scheduler.max_concurrent_executions = 10
    scheduler.active_executions = {}

    monkeypatch.setattr(SCHED_MOD, "execute_task_async", _slow_execute_task_async)

    original_wait = SCHED_MOD.asyncio.wait

    async def _short_wait(tasks, timeout=300):
        return await original_wait(tasks, timeout=0.01)

    monkeypatch.setattr(SCHED_MOD.asyncio, "wait", _short_wait)

    async def _run():
        result = await scheduler._process_task_type("dummy", _DB(), cycle_summary={})
        assert result is not None

    asyncio.run(_run())

    # after cancellation + gather cleanup, no active executions and no leases should remain
    assert scheduler.active_executions == {}
    assert scheduler._task_leases == {}
