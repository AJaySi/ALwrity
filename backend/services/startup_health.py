import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger
from sqlalchemy import inspect, text

from services.database import (
    WORKSPACE_DIR,
    get_all_user_ids,
    get_engine_for_user,
    get_session_for_user,
    get_user_db_path,
    init_database,
    default_engine,
)

_REQUIRED_SCHEMA: Dict[str, List[str]] = {
    "onboarding_sessions": ["id", "user_id", "updated_at"],
    "daily_workflow_plans": ["id", "user_id", "generation_mode", "fallback_used"],
}

_STARTUP_STATUS: Dict[str, Any] = {
    "status": "unknown",
    "mode": "multi_tenant" if default_engine is None else "single_tenant",
    "checks": [],
    "errors": [],
    "warnings": [],
    "checked_at": None,
}


def _env_true(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def should_fail_fast() -> bool:
    if os.getenv("ALWRITY_FAIL_FAST_STARTUP") is not None:
        return _env_true("ALWRITY_FAIL_FAST_STARTUP", default=False)
    app_env = os.getenv("APP_ENV", os.getenv("ENV", "")).strip().lower()
    return app_env in {"prod", "production"}


def _record_check(checks: List[Dict[str, Any]], name: str, ok: bool, detail: str) -> None:
    checks.append({"name": name, "ok": ok, "detail": detail})


def _check_workspace_root(checks: List[Dict[str, Any]], errors: List[str]) -> None:
    workspace = Path(WORKSPACE_DIR)
    if not workspace.exists():
        errors.append(f"Workspace root does not exist: {workspace}")
        _record_check(checks, "workspace_root_exists", False, str(workspace))
        return

    _record_check(checks, "workspace_root_exists", True, str(workspace))

    if not os.access(workspace, os.W_OK):
        errors.append(f"Workspace root is not writable: {workspace}")
        _record_check(checks, "workspace_root_writable", False, str(workspace))
        return

    probe_file = workspace / ".startup_health_write_probe"
    try:
        probe_file.write_text("ok", encoding="utf-8")
        probe_file.unlink(missing_ok=True)
        _record_check(checks, "workspace_root_writable", True, "write probe passed")
    except Exception as exc:
        errors.append(f"Workspace root write probe failed: {exc}")
        _record_check(checks, "workspace_root_writable", False, f"write probe failed: {exc}")


def _check_schema_for_user(user_id: str, checks: List[Dict[str, Any]], errors: List[str]) -> None:
    engine = get_engine_for_user(user_id)
    inspector = inspect(engine)

    for table, columns in _REQUIRED_SCHEMA.items():
        if not inspector.has_table(table):
            errors.append(f"Missing required table '{table}' in tenant DB for user '{user_id}'")
            _record_check(checks, f"schema_{table}", False, f"table missing for {user_id}")
            continue

        existing_columns = {col["name"] for col in inspector.get_columns(table)}
        missing_columns = [col for col in columns if col not in existing_columns]
        if missing_columns:
            errors.append(
                f"Missing required columns in '{table}' for user '{user_id}': {', '.join(missing_columns)}"
            )
            _record_check(
                checks,
                f"schema_{table}",
                False,
                f"missing columns for {user_id}: {', '.join(missing_columns)}",
            )
        else:
            _record_check(checks, f"schema_{table}", True, f"schema ok for {user_id}")


def _check_db_access(checks: List[Dict[str, Any]], errors: List[str], warnings: List[str]) -> Optional[str]:
    if default_engine is not None:
        try:
            init_database()
            with default_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            _record_check(checks, "single_tenant_db_connectivity", True, "SELECT 1 succeeded")
            return "single_tenant"
        except Exception as exc:
            errors.append(f"Single-tenant database check failed: {exc}")
            _record_check(checks, "single_tenant_db_connectivity", False, str(exc))
            return None

    user_ids = get_all_user_ids()
    candidate_user = user_ids[0] if user_ids else "startup_synthetic"

    try:
        db_path = get_user_db_path(candidate_user)
        _record_check(checks, "tenant_db_path_resolution", True, f"{candidate_user} -> {db_path}")
    except Exception as exc:
        errors.append(f"Tenant DB path resolution failed: {exc}")
        _record_check(checks, "tenant_db_path_resolution", False, str(exc))
        return None

    try:
        session = get_session_for_user(candidate_user)
        if not session:
            raise RuntimeError("session creation returned None")
        session.execute(text("SELECT 1"))
        _record_check(checks, "tenant_session_create", True, f"session opened for {candidate_user}")
        session.close()
    except Exception as exc:
        errors.append(f"Tenant DB open/create check failed for '{candidate_user}': {exc}")
        _record_check(checks, "tenant_session_create", False, str(exc))
        return None

    if not user_ids:
        warnings.append(
            "No existing tenant workspace found during startup; synthetic tenant DB path was used for readiness validation."
        )

    _check_schema_for_user(candidate_user, checks, errors)
    return candidate_user


def run_startup_health_routine() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    _check_workspace_root(checks, errors)
    if not errors:
        _check_db_access(checks, errors, warnings)

    status = "healthy" if not errors else "failed"
    report = {
        "status": status,
        "mode": "multi_tenant" if default_engine is None else "single_tenant",
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }

    _STARTUP_STATUS.update(report)

    if errors:
        for message in errors:
            logger.error(f"Startup readiness check failed: {message}")
    for warning in warnings:
        logger.warning(f"Startup readiness warning: {warning}")

    if errors and should_fail_fast():
        raise RuntimeError("Startup readiness checks failed")

    return report


def get_startup_status() -> Dict[str, Any]:
    return dict(_STARTUP_STATUS)


def readiness_under_auth_context(current_user: Dict[str, Any]) -> Dict[str, Any]:
    user_id = (current_user or {}).get("id") or (current_user or {}).get("clerk_user_id")
    if not user_id:
        return {
            "ready": False,
            "reason": "missing_user_context",
            "detail": "No authenticated user id was provided in auth context.",
        }

    try:
        db_path = get_user_db_path(user_id)
        session = get_session_for_user(user_id)
        if not session:
            raise RuntimeError("Session creation returned None")
        session.execute(text("SELECT 1"))
        session.close()
        return {
            "ready": True,
            "user_id": user_id,
            "tenant_db_path": db_path,
            "db_session": "ok",
        }
    except Exception as exc:
        logger.error(f"Readiness auth-context DB check failed for user '{user_id}': {exc}")
        return {
            "ready": False,
            "user_id": user_id,
            "tenant_db_path": get_user_db_path(user_id),
            "db_session": "failed",
            "reason": str(exc),
        }
