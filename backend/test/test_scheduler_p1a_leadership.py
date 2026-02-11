import importlib.util
import sys
import types
from pathlib import Path


def _load_module(module_name: str, file_path: Path):
    parts = module_name.split('.')
    for i in range(1, len(parts)):
        pkg_name = '.'.join(parts[:i])
        if pkg_name not in sys.modules:
            pkg = types.ModuleType(pkg_name)
            # Package path should be the real package directory
            pkg_path = file_path.parents[len(parts) - i - 1] if len(parts) - i - 1 >= 0 else file_path.parent
            pkg.__path__ = [str(pkg_path)]
            sys.modules[pkg_name] = pkg

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


BACKEND = Path(__file__).resolve().parents[1]
SCHEDULER_MOD = _load_module(
    "services.scheduler.core.scheduler",
    BACKEND / "services" / "scheduler" / "core" / "scheduler.py"
)


class _ScalarResult:
    def __init__(self, value):
        self._value = value

    def scalar(self):
        return self._value


class _FakeSession:
    def __init__(self, lock_ok=True):
        self.lock_ok = lock_ok
        self.closed = False
        self.calls = []

    def execute(self, *_args, **_kwargs):
        self.calls.append((_args, _kwargs))
        return _ScalarResult(self.lock_ok)

    def commit(self):
        return None

    def rollback(self):
        return None

    def close(self):
        self.closed = True


class _FakeAps:
    def __init__(self):
        self.jobs = {}

    def get_job(self, job_id):
        return self.jobs.get(job_id)

    def add_job(self, func, trigger=None, id=None, **kwargs):
        self.jobs[id] = {"func": func, "trigger": trigger, "kwargs": kwargs}

    def remove_job(self, job_id):
        self.jobs.pop(job_id, None)


def test_leadership_lock_acquire_and_release(monkeypatch):
    scheduler = SCHEDULER_MOD.TaskScheduler(check_interval_minutes=15)
    fake_session = _FakeSession(lock_ok=True)

    monkeypatch.setattr(SCHEDULER_MOD, "get_db_session", lambda: fake_session)

    acquired = scheduler._acquire_leadership()
    assert acquired is True
    assert scheduler._is_leader is True
    assert scheduler._execution_enabled is True

    scheduler._release_leadership()
    assert fake_session.closed is True
    assert scheduler._is_leader is False
    assert scheduler._execution_enabled is False


def test_check_due_tasks_job_only_exists_for_leader():
    scheduler = SCHEDULER_MOD.TaskScheduler(check_interval_minutes=15)
    scheduler.scheduler = _FakeAps()

    scheduler._is_leader = False
    scheduler._execution_enabled = False
    scheduler._sync_check_due_tasks_job()
    assert "check_due_tasks" not in scheduler.scheduler.jobs

    scheduler._is_leader = True
    scheduler._execution_enabled = True
    scheduler._sync_check_due_tasks_job()
    assert "check_due_tasks" in scheduler.scheduler.jobs

    scheduler._is_leader = False
    scheduler._execution_enabled = False
    scheduler._sync_check_due_tasks_job()
    assert "check_due_tasks" not in scheduler.scheduler.jobs


def test_p1a_leadership_status_wiring_present():
    api_file = BACKEND / "api" / "scheduler" / "__init__.py"
    content = api_file.read_text()

    assert "scheduler_runtime" in content
    assert "scheduler_leadership" in content

    scheduler_file = BACKEND / "services" / "scheduler" / "core" / "scheduler.py"
    sched_content = scheduler_file.read_text()
    assert "leadership_monitor" in sched_content
    assert "_leadership_tick" in sched_content
    assert "_sync_check_due_tasks_job" in sched_content
