"""Traffic-aware pre-dispatch control for scheduler tasks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from utils.logger_utils import get_service_logger

logger = get_service_logger("traffic_control")


@dataclass
class DispatchDecision:
    execute_now: bool
    defer_reason: Optional[str] = None
    prior_schedule: Optional[str] = None
    next_schedule: Optional[str] = None
    nci_evidence: Optional[Dict[str, Any]] = None


class SchedulerTrafficControl:
    """Evaluates whether publish-like tasks should execute immediately or be deferred."""

    def evaluate_pre_execution(self, task: Any, db: Session) -> DispatchDecision:
        nci = self._query_nci(task)
        if nci.get("action") == "defer":
            prior_schedule = self._task_schedule_iso(task)
            next_window = self._compute_next_low_density_window(task, nci)
            self._update_post_delivery_state(
                task=task,
                db=db,
                defer_reason=nci.get("reason", "nci_deferred"),
                prior_schedule=prior_schedule,
                next_schedule=next_window.isoformat() if next_window else None,
                nci_evidence=nci,
            )
            return DispatchDecision(
                execute_now=False,
                defer_reason=nci.get("reason", "nci_deferred"),
                prior_schedule=prior_schedule,
                next_schedule=next_window.isoformat() if next_window else None,
                nci_evidence=nci,
            )

        return DispatchDecision(execute_now=True, nci_evidence=nci)

    def _query_nci(self, task: Any) -> Dict[str, Any]:
        """Query NCI signal and branch decision. Default is pass-through unless payload asks defer."""
        payload = getattr(task, "payload", None) or {}
        nci = payload.get("nci") or {}
        should_defer = bool(nci.get("should_defer", False))
        return {
            "signal": nci.get("signal", "unknown"),
            "score": nci.get("score"),
            "action": "defer" if should_defer else "execute_now",
            "reason": nci.get("reason", "nci_green" if not should_defer else "nci_requested_deferral"),
            "observed_at": datetime.utcnow().isoformat(),
        }

    def _compute_next_low_density_window(self, task: Any, nci: Dict[str, Any]) -> datetime:
        """Compute next low-density publish window."""
        payload = getattr(task, "payload", None) or {}
        delay_minutes = int(payload.get("defer_minutes", 60) or 60)
        return datetime.utcnow() + timedelta(minutes=max(delay_minutes, 1))

    def _update_post_delivery_state(
        self,
        task: Any,
        db: Session,
        defer_reason: str,
        prior_schedule: Optional[str],
        next_schedule: Optional[str],
        nci_evidence: Dict[str, Any],
    ):
        """Persist deferral metadata and re-schedule task for normal queue processing."""
        payload = dict(getattr(task, "payload", None) or {})
        payload["defer_state"] = {
            "defer_reason": defer_reason,
            "prior_schedule": prior_schedule,
            "next_schedule": next_schedule,
            "nci_evidence": nci_evidence,
            "deferred_at": datetime.utcnow().isoformat(),
        }
        setattr(task, "payload", payload)

        if next_schedule and hasattr(task, "next_execution"):
            task.next_execution = datetime.fromisoformat(next_schedule)
        if hasattr(task, "status"):
            task.status = "active"

        db.add(task)
        db.commit()
        logger.info(
            "[Traffic Control] Deferred task %s | reason=%s | next=%s",
            getattr(task, "id", None),
            defer_reason,
            next_schedule,
        )

    def _task_schedule_iso(self, task: Any) -> Optional[str]:
        next_execution = getattr(task, "next_execution", None)
        return next_execution.isoformat() if next_execution else None
