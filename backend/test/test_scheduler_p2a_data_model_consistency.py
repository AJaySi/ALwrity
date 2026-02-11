from datetime import datetime
import importlib.util
import sys
import types
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import monitoring_models as MONITORING_MODELS
from models import enhanced_strategy_models as ENHANCED_MODELS


def _load_aggregations_module(module_name: str, file_path: Path):
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
AGG_MOD = _load_aggregations_module("api.scheduler.aggregations", BACKEND / "api" / "scheduler" / "aggregations.py")


def _build_session():
    engine = create_engine("sqlite:///:memory:")
    ENHANCED_MODELS.Base.metadata.create_all(
        engine,
        tables=[
            ENHANCED_MODELS.EnhancedContentStrategy.__table__,
            MONITORING_MODELS.MonitoringTask.__table__,
            MONITORING_MODELS.TaskExecutionLog.__table__,
        ],
    )
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def test_execution_logs_user_filter_supports_legacy_and_string_ids():
    db = _build_session()

    strategy = ENHANCED_MODELS.EnhancedContentStrategy(id=1, user_id=1, name="Strategy", industry="Marketing")
    db.add(strategy)
    db.flush()

    task = MONITORING_MODELS.MonitoringTask(
        id=10,
        strategy_id=strategy.id,
        component_name="SEO",
        task_title="Daily SEO Check",
        task_description="desc",
        assignee="ALwrity",
        frequency="Daily",
        metric="rank",
        measurement_method="m",
        success_criteria="ok",
        alert_threshold="x",
        status="active",
    )
    db.add(task)
    db.flush()

    db.add(MONITORING_MODELS.TaskExecutionLog(task_id=task.id, user_id=123, user_id_str=None, execution_date=datetime.utcnow(), status="success"))
    db.add(MONITORING_MODELS.TaskExecutionLog(task_id=task.id, user_id=None, user_id_str="user_abc", execution_date=datetime.utcnow(), status="success"))
    db.add(MONITORING_MODELS.TaskExecutionLog(task_id=task.id, user_id=None, user_id_str="user_other", execution_date=datetime.utcnow(), status="failed"))
    db.commit()

    legacy_result = AGG_MOD.aggregate_execution_logs(db=db, user_id="123", limit=10, offset=0)
    assert legacy_result["total_count"] == 1
    assert legacy_result["logs"][0]["user_id"] == "123"

    canonical_result = AGG_MOD.aggregate_execution_logs(db=db, user_id="user_abc", limit=10, offset=0)
    assert canonical_result["total_count"] == 1
    assert canonical_result["logs"][0]["user_id"] == "user_abc"


def test_execution_logs_user_id_prefers_canonical_string_in_payload():
    db = _build_session()

    strategy = ENHANCED_MODELS.EnhancedContentStrategy(id=2, user_id=2, name="Strategy 2", industry="Marketing")
    task = MONITORING_MODELS.MonitoringTask(
        id=20,
        strategy_id=2,
        component_name="Content",
        task_title="Weekly Content Check",
        task_description="desc",
        assignee="ALwrity",
        frequency="Weekly",
        metric="engagement",
        measurement_method="m",
        success_criteria="ok",
        alert_threshold="x",
        status="active",
    )
    db.add_all([strategy, task])
    db.flush()

    db.add(MONITORING_MODELS.TaskExecutionLog(task_id=task.id, user_id=456, user_id_str="user_clerk_456", execution_date=datetime.utcnow(), status="success"))
    db.commit()

    result = AGG_MOD.aggregate_execution_logs(db=db, limit=10, offset=0)
    assert result["total_count"] == 1
    assert result["logs"][0]["user_id"] == "user_clerk_456"
