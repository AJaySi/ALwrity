from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.agent_activity_models import AgentAlert, AgentApprovalRequest, AgentEvent, AgentRun


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
        payload: Optional[Dict[str, Any]] = None,
        run_id: Optional[int] = None,
        agent_type: Optional[str] = None,
    ) -> AgentEvent:
        evt = AgentEvent(
            run_id=run_id,
            user_id=self.user_id,
            agent_type=agent_type,
            event_type=event_type,
            severity=severity,
            message=message,
            payload=payload,
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

    def get_huddle_feed(
        self,
        since: Optional[str] = None,
        cursor: Optional[str] = None,
        runs_limit: int = 20,
        events_limit: int = 50,
        alerts_limit: int = 20,
        approvals_limit: int = 20,
    ) -> Dict[str, Any]:
        now = datetime.utcnow()
        since_dt = self._parse_datetime(since)
        cursor_dt = self._parse_datetime(cursor)

        statuses = self._get_active_statuses()
        runs = self._list_runs_for_feed(limit=runs_limit, since_dt=since_dt, cursor_dt=cursor_dt)
        events = self._list_events_for_feed(limit=events_limit, since_dt=since_dt, cursor_dt=cursor_dt)
        alerts = self._list_alerts_for_feed(limit=alerts_limit, since_dt=since_dt, cursor_dt=cursor_dt)
        approvals = self._list_approvals_for_feed(limit=approvals_limit, since_dt=since_dt, cursor_dt=cursor_dt)

        cursors = {
            "runs": self._next_cursor(runs, "started_at"),
            "events": self._next_cursor(events, "created_at"),
            "alerts": self._next_cursor(alerts, "created_at"),
            "approvals": self._next_cursor(approvals, "created_at"),
            "feed": now.isoformat(),
        }

        return {
            "statuses": statuses,
            "runs": [self._serialize_run(run) for run in runs],
            "events": [self._serialize_event(evt) for evt in events],
            "alerts": [self._serialize_alert(alert) for alert in alerts],
            "approvals": [self._serialize_approval(req) for req in approvals],
            "unread_alerts": self._count_unread_alerts(),
            "pending_approvals": self._count_pending_approvals(),
            "cursors": cursors,
            "server_timestamp": now.isoformat(),
        }

    @staticmethod
    def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        text = str(value).strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(text)
            if parsed.tzinfo is not None:
                return parsed.replace(tzinfo=None)
            return parsed
        except ValueError:
            return None

    def _get_active_statuses(self) -> List[Dict[str, Any]]:
        subquery = (
            self.db.query(
                AgentRun.agent_type.label("agent_type"),
                func.max(AgentRun.started_at).label("max_started_at"),
            )
            .filter(AgentRun.user_id == self.user_id)
            .group_by(AgentRun.agent_type)
            .subquery()
        )

        rows = (
            self.db.query(AgentRun)
            .join(
                subquery,
                (AgentRun.agent_type == subquery.c.agent_type)
                & (AgentRun.started_at == subquery.c.max_started_at),
            )
            .filter(AgentRun.user_id == self.user_id)
            .all()
        )
        return [
            {
                "agent_type": row.agent_type,
                "status": row.status,
                "success": row.success,
                "run_id": row.id,
                "updated_at": (row.finished_at or row.started_at).isoformat() if (row.finished_at or row.started_at) else None,
            }
            for row in rows
        ]

    def _list_runs_for_feed(self, limit: int, since_dt: Optional[datetime], cursor_dt: Optional[datetime]) -> List[AgentRun]:
        q = self.db.query(AgentRun).filter(AgentRun.user_id == self.user_id)
        if since_dt:
            q = q.filter(AgentRun.started_at >= since_dt)
        if cursor_dt:
            q = q.filter(AgentRun.started_at < cursor_dt)
        return q.order_by(AgentRun.started_at.desc()).limit(limit).all()

    def _list_events_for_feed(self, limit: int, since_dt: Optional[datetime], cursor_dt: Optional[datetime]) -> List[AgentEvent]:
        q = self.db.query(AgentEvent).filter(AgentEvent.user_id == self.user_id)
        if since_dt:
            q = q.filter(AgentEvent.created_at >= since_dt)
        if cursor_dt:
            q = q.filter(AgentEvent.created_at < cursor_dt)
        return q.order_by(AgentEvent.created_at.desc()).limit(limit).all()

    def _list_alerts_for_feed(self, limit: int, since_dt: Optional[datetime], cursor_dt: Optional[datetime]) -> List[AgentAlert]:
        q = self.db.query(AgentAlert).filter(AgentAlert.user_id == self.user_id, AgentAlert.read_at.is_(None))
        if since_dt:
            q = q.filter(AgentAlert.created_at >= since_dt)
        if cursor_dt:
            q = q.filter(AgentAlert.created_at < cursor_dt)
        return q.order_by(AgentAlert.created_at.desc()).limit(limit).all()

    def _list_approvals_for_feed(
        self,
        limit: int,
        since_dt: Optional[datetime],
        cursor_dt: Optional[datetime],
    ) -> List[AgentApprovalRequest]:
        q = self.db.query(AgentApprovalRequest).filter(
            AgentApprovalRequest.user_id == self.user_id,
            AgentApprovalRequest.status == "pending",
        )
        if since_dt:
            q = q.filter(AgentApprovalRequest.created_at >= since_dt)
        if cursor_dt:
            q = q.filter(AgentApprovalRequest.created_at < cursor_dt)
        return q.order_by(AgentApprovalRequest.created_at.desc()).limit(limit).all()


    def _count_unread_alerts(self) -> int:
        return self.db.query(AgentAlert).filter(
            AgentAlert.user_id == self.user_id,
            AgentAlert.read_at.is_(None),
        ).count()

    def _count_pending_approvals(self) -> int:
        return self.db.query(AgentApprovalRequest).filter(
            AgentApprovalRequest.user_id == self.user_id,
            AgentApprovalRequest.status == "pending",
        ).count()

    @staticmethod
    def _next_cursor(items: List[Any], time_attr: str) -> Optional[str]:
        if not items:
            return None
        ts = getattr(items[-1], time_attr, None)
        return ts.isoformat() if ts else None

    @staticmethod
    def _serialize_run(run: AgentRun) -> Dict[str, Any]:
        return {
            "id": run.id,
            "user_id": run.user_id,
            "agent_type": run.agent_type,
            "status": run.status,
            "success": run.success,
            "error_message": run.error_message,
            "result_summary": run.result_summary,
            "mlflow_run_id": run.mlflow_run_id,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "finished_at": run.finished_at.isoformat() if run.finished_at else None,
        }

    @staticmethod
    def _serialize_event(evt: AgentEvent) -> Dict[str, Any]:
        return {
            "id": evt.id,
            "run_id": evt.run_id,
            "agent_type": evt.agent_type,
            "event_type": evt.event_type,
            "severity": evt.severity,
            "message": evt.message,
            "payload": evt.payload,
            "created_at": evt.created_at.isoformat() if evt.created_at else None,
        }

    @staticmethod
    def _serialize_alert(alert: AgentAlert) -> Dict[str, Any]:
        return {
            "id": alert.id,
            "source": alert.source,
            "type": alert.alert_type,
            "severity": alert.severity,
            "title": alert.title,
            "message": alert.message,
            "cta_path": alert.cta_path,
            "payload": alert.payload,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
            "read_at": alert.read_at.isoformat() if alert.read_at else None,
        }

    @staticmethod
    def _serialize_approval(req: AgentApprovalRequest) -> Dict[str, Any]:
        return {
            "id": req.id,
            "status": req.status,
            "decision": req.decision,
            "action_id": req.action_id,
            "action_type": req.action_type,
            "agent_type": req.agent_type,
            "target_resource": req.target_resource,
            "risk_level": req.risk_level,
            "payload": req.payload,
            "created_at": req.created_at.isoformat() if req.created_at else None,
            "decided_at": req.decided_at.isoformat() if req.decided_at else None,
        }
