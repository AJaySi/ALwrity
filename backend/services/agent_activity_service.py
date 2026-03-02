from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from models.agent_activity_models import AgentAlert, AgentApprovalRequest, AgentEvent, AgentRun


@dataclass
class AgentEventPayload:
    """Shared schema for agent activity event payloads."""

    phase: Optional[str] = None
    step: Optional[str] = None
    tool_name: Optional[str] = None
    progress_percent: Optional[float] = None
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None
    decision_reason: Optional[str] = None
    evidence_refs: List[str] = field(default_factory=list)
    safe_debug: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


def build_agent_event_payload(
    *,
    phase: Optional[str] = None,
    step: Optional[str] = None,
    tool_name: Optional[str] = None,
    progress_percent: Optional[float] = None,
    input_summary: Optional[str] = None,
    output_summary: Optional[str] = None,
    decision_reason: Optional[str] = None,
    evidence_refs: Optional[List[str]] = None,
    safe_debug: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return asdict(
        AgentEventPayload(
            phase=phase,
            step=step,
            tool_name=tool_name,
            progress_percent=progress_percent,
            input_summary=input_summary,
            output_summary=output_summary,
            decision_reason=decision_reason,
            evidence_refs=list(evidence_refs or []),
            safe_debug=bool(safe_debug),
            metadata=dict(metadata or {}),
        )
    )


def _normalize_event_payload(payload: Optional[Union[Dict[str, Any], AgentEventPayload]]) -> Dict[str, Any]:
    if payload is None:
        return build_agent_event_payload()
    if isinstance(payload, AgentEventPayload):
        return asdict(payload)
    if not isinstance(payload, dict):
        return build_agent_event_payload(output_summary=str(payload)[:2000], safe_debug=False)

    return build_agent_event_payload(
        phase=payload.get("phase"),
        step=payload.get("step"),
        tool_name=payload.get("tool_name"),
        progress_percent=payload.get("progress_percent"),
        input_summary=payload.get("input_summary"),
        output_summary=payload.get("output_summary"),
        decision_reason=payload.get("decision_reason"),
        evidence_refs=payload.get("evidence_refs") if isinstance(payload.get("evidence_refs"), list) else [],
        safe_debug=bool(payload.get("safe_debug", True)),
        metadata=payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {},
    )


class AgentActivityService:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id

    def start_run(self, agent_type: str, prompt: Optional[str] = None, mlflow_run_id: Optional[str] = None) -> AgentRun:
        run = AgentRun(
            user_id=self.user_id,
            agent_type=agent_type,
            prompt=prompt,
            status="running",
            mlflow_run_id=mlflow_run_id,
            started_at=datetime.utcnow(),
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def finish_run(
        self,
        run_id: int,
        success: bool,
        result_summary: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        run = self.db.query(AgentRun).filter(AgentRun.id == run_id, AgentRun.user_id == self.user_id).first()
        if not run:
            return
        run.status = "completed" if success else "failed"
        run.success = bool(success)
        run.result_summary = result_summary
        run.error_message = error_message
        run.finished_at = datetime.utcnow()
        self.db.add(run)
        self.db.commit()

    def log_event(
        self,
        event_type: str,
        severity: str = "info",
        message: Optional[str] = None,
        payload: Optional[Union[Dict[str, Any], AgentEventPayload]] = None,
        run_id: Optional[int] = None,
        agent_type: Optional[str] = None,
    ) -> AgentEvent:
        normalized_payload = _normalize_event_payload(payload)
        evt = AgentEvent(
            run_id=run_id,
            user_id=self.user_id,
            agent_type=agent_type,
            event_type=event_type,
            severity=severity,
            message=message,
            payload=normalized_payload,
            created_at=datetime.utcnow(),
        )
        self.db.add(evt)
        self.db.commit()
        self.db.refresh(evt)
        return evt

    def create_alert(
        self,
        alert_type: str,
        title: str,
        message: str,
        severity: str = "info",
        payload: Optional[Dict[str, Any]] = None,
        cta_path: Optional[str] = None,
        dedupe_key: Optional[str] = None,
    ) -> Optional[AgentAlert]:
        if dedupe_key:
            existing = (
                self.db.query(AgentAlert)
                .filter(
                    AgentAlert.user_id == self.user_id,
                    AgentAlert.dedupe_key == dedupe_key,
                    AgentAlert.read_at.is_(None),
                )
                .first()
            )
            if existing:
                return None

        alert = AgentAlert(
            user_id=self.user_id,
            source="agents",
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            cta_path=cta_path,
            payload=payload,
            dedupe_key=dedupe_key,
            created_at=datetime.utcnow(),
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def list_alerts(self, unread_only: bool = True, limit: int = 50) -> List[AgentAlert]:
        q = self.db.query(AgentAlert).filter(AgentAlert.user_id == self.user_id)
        if unread_only:
            q = q.filter(AgentAlert.read_at.is_(None))
        return q.order_by(AgentAlert.created_at.desc()).limit(limit).all()

    def mark_alert_read(self, alert_id: int) -> bool:
        alert = self.db.query(AgentAlert).filter(AgentAlert.id == alert_id, AgentAlert.user_id == self.user_id).first()
        if not alert:
            return False
        alert.read_at = datetime.utcnow()
        self.db.add(alert)
        self.db.commit()
        return True

    def list_runs(self, limit: int = 30) -> List[AgentRun]:
        return (
            self.db.query(AgentRun)
            .filter(AgentRun.user_id == self.user_id)
            .order_by(AgentRun.started_at.desc())
            .limit(limit)
            .all()
        )

    def list_events(self, run_id: Optional[int] = None, limit: int = 200) -> List[AgentEvent]:
        q = self.db.query(AgentEvent).filter(AgentEvent.user_id == self.user_id)
        if run_id is not None:
            q = q.filter(AgentEvent.run_id == run_id)
        return q.order_by(AgentEvent.created_at.desc()).limit(limit).all()

    def create_approval_request(
        self,
        action_id: str,
        action_type: str,
        risk_level: float,
        payload: Optional[Dict[str, Any]] = None,
        agent_type: Optional[str] = None,
        target_resource: Optional[str] = None,
        run_id: Optional[int] = None,
        expires_at: Optional[datetime] = None,
    ) -> AgentApprovalRequest:
        req = AgentApprovalRequest(
            user_id=self.user_id,
            run_id=run_id,
            agent_type=agent_type,
            action_id=action_id,
            action_type=action_type,
            target_resource=target_resource,
            risk_level=float(risk_level or 0.5),
            payload=payload,
            status="pending",
            expires_at=expires_at,
            created_at=datetime.utcnow(),
        )
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req

    def list_approval_requests(self, status: Optional[str] = "pending", limit: int = 50) -> List[AgentApprovalRequest]:
        q = self.db.query(AgentApprovalRequest).filter(AgentApprovalRequest.user_id == self.user_id)
        if status:
            q = q.filter(AgentApprovalRequest.status == status)
        return q.order_by(AgentApprovalRequest.created_at.desc()).limit(limit).all()

    def decide_approval_request(self, approval_id: int, decision: str, user_comments: str = "") -> Optional[AgentApprovalRequest]:
        req = (
            self.db.query(AgentApprovalRequest)
            .filter(AgentApprovalRequest.id == approval_id, AgentApprovalRequest.user_id == self.user_id)
            .first()
        )
        if not req:
            return None
        decision_value = str(decision or "").lower().strip()
        if decision_value not in {"approved", "rejected"}:
            decision_value = "rejected"
        req.status = "approved" if decision_value == "approved" else "rejected"
        req.decision = decision_value
        req.user_comments = (user_comments or "")[:4000]
        req.decided_at = datetime.utcnow()
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req
