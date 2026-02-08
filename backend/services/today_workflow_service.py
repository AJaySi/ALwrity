import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from models.daily_workflow_models import DailyWorkflowPlan, DailyWorkflowTask
from models.agent_activity_models import AgentAlert
from services.agent_activity_service import AgentActivityService
from services.llm_providers.main_text_generation import llm_text_gen


PILLAR_IDS = ["plan", "generate", "publish", "analyze", "engage", "remarket"]


def _today_date_str() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _coerce_priority(value: Any) -> str:
    v = str(value or "medium").lower().strip()
    return v if v in {"high", "medium", "low"} else "medium"


def _coerce_status(value: Any) -> str:
    v = str(value or "pending").lower().strip()
    if v in {"pending", "in_progress", "completed", "skipped", "dismissed"}:
        return "skipped" if v == "dismissed" else v
    return "pending"


def _fallback_tasks(date: str) -> List[Dict[str, Any]]:
    return [
        {
            "pillarId": "plan",
            "title": "Review today’s plan",
            "description": "Confirm priorities and adjust the content calendar for today.",
            "priority": "high",
            "estimatedTime": 15,
            "actionType": "navigate",
            "actionUrl": "/content-planning-dashboard",
            "enabled": True,
        },
        {
            "pillarId": "generate",
            "title": "Generate one core content asset",
            "description": "Create a draft aligned with your current strategy and voice.",
            "priority": "high",
            "estimatedTime": 45,
            "actionType": "navigate",
            "actionUrl": "/blog-writer",
            "enabled": True,
        },
        {
            "pillarId": "publish",
            "title": "Publish or schedule today’s content",
            "description": "Publish or schedule content across the selected channel(s).",
            "priority": "medium",
            "estimatedTime": 20,
            "actionType": "navigate",
            "actionUrl": "/content-planning-dashboard",
            "enabled": True,
        },
        {
            "pillarId": "analyze",
            "title": "Check semantic health and performance",
            "description": "Review semantic health metrics and key performance indicators.",
            "priority": "medium",
            "estimatedTime": 15,
            "actionType": "navigate",
            "actionUrl": "/seo-dashboard",
            "enabled": True,
        },
        {
            "pillarId": "engage",
            "title": "Engage on one channel",
            "description": "Respond to comments and share one post to keep momentum.",
            "priority": "medium",
            "estimatedTime": 15,
            "actionType": "navigate",
            "actionUrl": "/linkedin-writer",
            "enabled": True,
        },
        {
            "pillarId": "remarket",
            "title": "Repurpose and remarket content",
            "description": "Create one repurposed snippet and distribute it to increase reach.",
            "priority": "low",
            "estimatedTime": 20,
            "actionType": "navigate",
            "actionUrl": "/facebook-writer",
            "enabled": True,
        },
    ]


def build_grounding_context(db: Session, user_id: str, date: str) -> Dict[str, Any]:
    unread_agent_alerts = (
        db.query(AgentAlert)
        .filter(AgentAlert.user_id == user_id, AgentAlert.read_at.is_(None))
        .order_by(AgentAlert.created_at.desc())
        .limit(10)
        .all()
    )
    return {
        "date": date,
        "user_id": user_id,
        "pillars": PILLAR_IDS,
        "recent_agent_alerts": [
            {"type": a.alert_type, "severity": a.severity, "title": a.title, "message": a.message}
            for a in unread_agent_alerts
        ],
    }


def generate_agent_enhanced_plan(db: Session, user_id: str, date: str) -> Dict[str, Any]:
    activity = AgentActivityService(db, user_id)
    grounding = build_grounding_context(db, user_id, date)

    schema = {
        "type": "object",
        "properties": {
            "date": {"type": "string"},
            "tasks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "pillarId": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "priority": {"type": "string"},
                        "estimatedTime": {"type": "number"},
                        "actionType": {"type": "string"},
                        "actionUrl": {"type": "string"},
                        "enabled": {"type": "boolean"},
                        "dependencies": {"type": "array", "items": {"type": "string"}},
                        "metadata": {"type": "object"},
                    },
                },
            },
        },
    }

    prompt = (
        "Generate a Today workflow plan for ALwrity with exactly 6 lifecycle pillars: "
        "plan, generate, publish, analyze, engage, remarket.\n\n"
        "Rules:\n"
        "- Produce JSON only that matches the schema.\n"
        "- Include 1-3 tasks per pillar.\n"
        "- Each task must have pillarId in {plan, generate, publish, analyze, engage, remarket}.\n"
        "- Prefer actionable tasks that can be completed today.\n"
        "- Use these common actionUrl routes when relevant: "
        "/content-planning-dashboard, /blog-writer, /linkedin-writer, /facebook-writer, /seo-dashboard, /scheduler-dashboard.\n"
        "- Keep descriptions concise.\n\n"
        f"Grounding context:\n{json.dumps(grounding, indent=2)}\n"
    )

    run = activity.start_run(agent_type="TodayWorkflowGenerator", prompt=prompt[:4000])
    activity.log_event(
        event_type="plan",
        severity="info",
        message="Building grounded daily workflow plan",
        payload={"grounding": grounding},
        run_id=run.id,
        agent_type="TodayWorkflowGenerator",
    )

    try:
        raw = llm_text_gen(prompt=prompt, json_struct=schema, user_id=user_id)
        if isinstance(raw, dict):
            result = raw
        else:
            try:
                result = json.loads(raw)
            except Exception:
                result = {"date": date, "tasks": _fallback_tasks(date)}
    except Exception as e:
        activity.log_event(
            event_type="warning",
            severity="warning",
            message=str(e)[:2000],
            payload={"fallback": True},
            run_id=run.id,
            agent_type="TodayWorkflowGenerator",
        )
        result = {"date": date, "tasks": _fallback_tasks(date)}

    tasks = result.get("tasks") if isinstance(result, dict) else None
    if not isinstance(tasks, list) or not tasks:
        result = {"date": date, "tasks": _fallback_tasks(date)}

    activity.log_event(
        event_type="final_summary",
        severity="info",
        message="Daily workflow plan generated",
        payload={"date": date, "task_count": len(result.get("tasks", []))},
        run_id=run.id,
        agent_type="TodayWorkflowGenerator",
    )
    activity.finish_run(run.id, success=True, result_summary=json.dumps({"date": date, "tasks": result.get("tasks", [])})[:4000])
    return result


def get_or_create_daily_workflow_plan(db: Session, user_id: str, date: Optional[str] = None) -> tuple[DailyWorkflowPlan, bool]:
    date_str = date or _today_date_str()
    existing = (
        db.query(DailyWorkflowPlan)
        .filter(DailyWorkflowPlan.user_id == user_id, DailyWorkflowPlan.date == date_str)
        .first()
    )
    if existing:
        return existing, False

    plan_data = generate_agent_enhanced_plan(db, user_id, date_str)
    tasks = plan_data.get("tasks", [])

    plan = DailyWorkflowPlan(
        user_id=user_id,
        date=date_str,
        source="agent",
        plan_json=plan_data,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)

    for t in tasks:
        pillar_id = str(t.get("pillarId") or "").lower().strip()
        if pillar_id not in PILLAR_IDS:
            continue
        task = DailyWorkflowTask(
            plan_id=plan.id,
            user_id=user_id,
            pillar_id=pillar_id,
            title=str(t.get("title") or "Task").strip()[:255],
            description=str(t.get("description") or "").strip(),
            status=_coerce_status(t.get("status")),
            priority=_coerce_priority(t.get("priority")),
            estimated_time=int(t.get("estimatedTime") or 15),
            action_type=str(t.get("actionType") or "navigate").strip()[:20],
            action_url=str(t.get("actionUrl") or "").strip() or None,
            enabled=bool(t.get("enabled", True)),
            dependencies=t.get("dependencies") if isinstance(t.get("dependencies"), list) else None,
            metadata_json=t.get("metadata") if isinstance(t.get("metadata"), dict) else None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(task)
    db.commit()
    db.refresh(plan)
    return plan, True


def update_task_status(
    db: Session,
    user_id: str,
    task_id: int,
    status: str,
    completion_notes: Optional[str] = None,
) -> Optional[DailyWorkflowTask]:
    task = db.query(DailyWorkflowTask).filter(DailyWorkflowTask.id == task_id, DailyWorkflowTask.user_id == user_id).first()
    if not task:
        return None
    task.status = _coerce_status(status)
    task.decided_at = datetime.utcnow()
    if completion_notes is not None:
        task.completion_notes = completion_notes[:4000]
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
