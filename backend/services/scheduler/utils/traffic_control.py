"""Traffic-control utilities for publish task pre-flight decisions."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional


DEFAULT_DEFER_MINUTES = 180


def compute_recalibrated_deployment_window(
    now: Optional[datetime] = None,
    delay_minutes: int = DEFAULT_DEFER_MINUTES,
) -> Dict[str, str]:
    """Compute deployment window metadata for deferred publish tasks."""
    current = now or datetime.utcnow()
    next_window = current + timedelta(minutes=max(1, int(delay_minutes)))
    return {
        "recalibrated_at": current.isoformat(),
        "next_eligible_at": next_window.isoformat(),
        "delay_minutes": str(max(1, int(delay_minutes))),
    }


def apply_recalibrated_window_to_task(task: Any, window: Dict[str, str]) -> None:
    """Persist recalibrated window on known scheduler timing fields."""
    next_eligible = datetime.fromisoformat(window["next_eligible_at"])

    if hasattr(task, "next_execution"):
        task.next_execution = next_eligible
    if hasattr(task, "next_check"):
        task.next_check = next_eligible


def upsert_deferral_metadata(task: Any, metadata: Dict[str, Any]) -> bool:
    """Store deferral metadata idempotently.

    Returns True if metadata was newly written or updated, False if already present
    with the same deferral marker.
    """
    existing: Dict[str, Any] = {}
    if hasattr(task, "result_data") and isinstance(getattr(task, "result_data", None), dict):
        existing = dict(task.result_data or {})
        carrier = "result_data"
    elif hasattr(task, "metadata_json") and isinstance(getattr(task, "metadata_json", None), dict):
        existing = dict(task.metadata_json or {})
        carrier = "metadata_json"
    else:
        existing = dict(getattr(task, "metadata", {}) or {}) if hasattr(task, "metadata") else {}
        carrier = "metadata"

    deferrals = existing.get("deferrals") or []
    marker = metadata.get("deferral_marker")
    if marker and any(isinstance(d, dict) and d.get("deferral_marker") == marker for d in deferrals):
        return False

    deferrals.append(metadata)
    existing["deferrals"] = deferrals
    existing["last_deferral"] = metadata

    if carrier == "result_data":
        task.result_data = existing
    elif carrier == "metadata_json":
        task.metadata_json = existing
    else:
        setattr(task, "metadata", existing)
    return True
