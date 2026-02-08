from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from middleware.auth_middleware import get_current_user
from services.database import get_db
from services.today_workflow_service import get_or_create_daily_workflow_plan, update_task_status
from models.daily_workflow_models import DailyWorkflowPlan, DailyWorkflowTask
import asyncio
from services.intelligence.txtai_service import TxtaiIntelligenceService


router = APIRouter(prefix="/api/today-workflow", tags=["Today Workflow"])

async def _index_tasks_to_sif(user_id: str, date: str, tasks: list[dict], label: str):
    svc = TxtaiIntelligenceService(user_id)
    items = []
    for t in tasks:
        task_id = t.get("id")
        pillar_id = t.get("pillarId")
        status = t.get("status")
        title = t.get("title")
        description = t.get("description")
        text = f"[{pillar_id}] {title}\n{description}\nstatus={status}"
        metadata = {
            "type": "daily_workflow_task",
            "date": date,
            "label": label,
            "pillar_id": pillar_id,
            "status": status,
            "implemented": status == "completed",
            "dismissed": status == "skipped",
            "task_id": task_id,
        }
        items.append((f"{label}_task:{user_id}:{date}:{task_id}", text, metadata))
    try:
        await svc.index_content(items)
    except Exception:
        return


@router.get("")
async def get_today_workflow(
    date: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    user_id = str(current_user.get("id"))
    plan, created = get_or_create_daily_workflow_plan(db, user_id, date=date)

    tasks = (
        db.query(DailyWorkflowTask)
        .filter(DailyWorkflowTask.plan_id == plan.id, DailyWorkflowTask.user_id == user_id)
        .order_by(DailyWorkflowTask.created_at.asc())
        .all()
    )

    response_tasks = []
    for t in tasks:
        response_tasks.append(
            {
                "id": str(t.id),
                "pillarId": t.pillar_id,
                "title": t.title,
                "description": t.description,
                "status": "skipped" if t.status == "dismissed" else t.status,
                "priority": t.priority,
                "estimatedTime": t.estimated_time,
                "dependencies": t.dependencies or [],
                "actionUrl": t.action_url,
                "actionType": t.action_type,
                "metadata": t.metadata_json or {},
                "enabled": bool(t.enabled),
            }
        )

    total = len(response_tasks)
    completed = len([t for t in response_tasks if t["status"] in ("completed", "skipped")])
    current_index = 0
    for i, task in enumerate(response_tasks):
        if task["status"] not in ("completed", "skipped"):
            current_index = i
            break
        current_index = i

    workflow_status = "not_started"
    if completed > 0 and completed < total:
        workflow_status = "in_progress"
    elif total > 0 and completed == total:
        workflow_status = "completed"

    total_estimated = int(sum(int(t.get("estimatedTime") or 0) for t in response_tasks))

    if created:
        asyncio.create_task(_index_tasks_to_sif(user_id, plan.date, response_tasks, label="today"))
        try:
            from datetime import date as date_type, timedelta

            y_str = (date_type.fromisoformat(plan.date) - timedelta(days=1)).isoformat()
            y_plan = (
                db.query(DailyWorkflowPlan)
                .filter(DailyWorkflowPlan.user_id == user_id, DailyWorkflowPlan.date == y_str)
                .first()
            )
            if y_plan:
                y_tasks = (
                    db.query(DailyWorkflowTask)
                    .filter(DailyWorkflowTask.plan_id == y_plan.id, DailyWorkflowTask.user_id == user_id)
                    .order_by(DailyWorkflowTask.created_at.asc())
                    .all()
                )
                y_response = []
                for t in y_tasks:
                    y_response.append(
                        {
                            "id": str(t.id),
                            "pillarId": t.pillar_id,
                            "title": t.title,
                            "description": t.description,
                            "status": "skipped" if t.status == "dismissed" else t.status,
                        }
                    )
                asyncio.create_task(_index_tasks_to_sif(user_id, y_str, y_response, label="yesterday"))
        except Exception:
            pass

    return {
        "success": True,
        "data": {
            "workflow": {
                "id": f"daily-{user_id}-{plan.date}",
                "date": plan.date,
                "userId": user_id,
                "tasks": response_tasks,
                "currentTaskIndex": current_index,
                "completedTasks": completed,
                "totalTasks": total,
                "workflowStatus": workflow_status,
                "totalEstimatedTime": total_estimated,
                "actualTimeSpent": 0,
            },
            "plan": {
                "id": plan.id,
                "date": plan.date,
                "source": plan.source,
                "created_at": plan.created_at.isoformat() if plan.created_at else None,
                "updated_at": plan.updated_at.isoformat() if plan.updated_at else None,
            },
        },
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
    }


@router.post("/tasks/{task_id}/status")
async def set_task_status(
    task_id: int,
    body: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    user_id = str(current_user.get("id"))
    status = body.get("status")
    if not status:
        raise HTTPException(status_code=400, detail="status is required")
    completion_notes = body.get("completion_notes")

    task = update_task_status(db, user_id, task_id, status=status, completion_notes=completion_notes)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    plan_for_date = db.query(DailyWorkflowPlan).filter(DailyWorkflowPlan.id == task.plan_id).first()
    plan_date = plan_for_date.date if plan_for_date and plan_for_date.date else ""
    task_payload = {
        "id": str(task.id),
        "pillarId": task.pillar_id,
        "title": task.title,
        "description": task.description,
        "status": "skipped" if task.status == "dismissed" else task.status,
    }
    asyncio.create_task(_index_tasks_to_sif(user_id, plan_date, [task_payload], label="today"))

    return {
        "success": True,
        "data": {
            "task": {
                "id": str(task.id),
                "pillarId": task.pillar_id,
                "status": "skipped" if task.status == "dismissed" else task.status,
                "decided_at": task.decided_at.isoformat() if task.decided_at else None,
            }
        },
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
    }
