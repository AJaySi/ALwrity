import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from models.daily_workflow_models import DailyWorkflowPlan, DailyWorkflowTask
from models.agent_activity_models import AgentAlert
from services.agent_activity_service import AgentActivityService
from services.llm_providers.main_text_generation import llm_text_gen
from loguru import logger

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


def _is_coverage_guardrail_enabled(grounding: Dict[str, Any]) -> bool:
    workflow_config = grounding.get("workflow_config", {}) if isinstance(grounding, dict) else {}
    if not isinstance(workflow_config, dict):
        return True
    if workflow_config.get("disable_pillar_coverage_guardrail") is True:
        return False
    if workflow_config.get("enforce_pillar_coverage") is False:
        return False
    return True


def _sanitize_task(task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(task, dict):
        return None

    pillar_id = str(task.get("pillarId") or "").lower().strip()
    title = str(task.get("title") or "").strip()
    if pillar_id not in PILLAR_IDS or not title:
        return None

    sanitized = dict(task)
    sanitized["pillarId"] = pillar_id
    sanitized["title"] = title
    sanitized["description"] = str(task.get("description") or "").strip()
    sanitized["priority"] = _coerce_priority(task.get("priority"))
    sanitized["estimatedTime"] = max(5, int(task.get("estimatedTime") or 15))
    sanitized["actionType"] = str(task.get("actionType") or "navigate").strip() or "navigate"
    sanitized["actionUrl"] = str(task.get("actionUrl") or "").strip() or None
    sanitized["enabled"] = bool(task.get("enabled", True))
    return sanitized


def _build_single_task_for_missing_pillar(
    user_id: str,
    date: str,
    pillar_id: str,
    grounding: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    schema = {
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
            "metadata": {"type": "object"},
        },
        "required": ["pillarId", "title", "description", "priority", "estimatedTime", "actionType", "enabled"],
    }
    prompt = (
        "Generate exactly one actionable JSON task for today's workflow.\n"
        f"Date: {date}\n"
        f"Required pillarId: {pillar_id}\n"
        "Constraints:\n"
        "- Return a single JSON object only.\n"
        "- Keep title concise and practical.\n"
        "- Task must be completable today.\n"
        "- Use actionType='navigate' and a valid ALwrity route when possible.\n"
        f"User context: {json.dumps(grounding.get('onboarding_data', {}), indent=2)}\n"
    )
    try:
        raw = llm_text_gen(prompt=prompt, json_struct=schema, user_id=user_id)
        candidate = raw if isinstance(raw, dict) else json.loads(raw)
    except Exception as e:
        logger.warning(f"Failed to generate pillar backfill task for {pillar_id}: {e}")
        return None

    candidate = _sanitize_task(candidate)
    if candidate:
        candidate["pillarId"] = pillar_id
        metadata = candidate.get("metadata") if isinstance(candidate.get("metadata"), dict) else {}
        metadata["source"] = "llm_pillar_backfill"
        candidate["metadata"] = metadata
    return candidate


def _ensure_pillar_coverage(
    tasks: List[Dict[str, Any]],
    user_id: str,
    date: str,
    grounding: Dict[str, Any],
) -> List[Dict[str, Any]]:
    sanitized_tasks = [t for t in (_sanitize_task(task) for task in tasks) if t]
    if not _is_coverage_guardrail_enabled(grounding):
        return sanitized_tasks

    covered_pillars = {task["pillarId"] for task in sanitized_tasks}
    fallback_by_pillar = {
        task["pillarId"]: task for task in (_sanitize_task(t) for t in _fallback_tasks(date)) if task
    }

    for pillar_id in PILLAR_IDS:
        if pillar_id in covered_pillars:
            continue

        generated = _build_single_task_for_missing_pillar(user_id, date, pillar_id, grounding)
        if generated:
            sanitized_tasks.append(generated)
            covered_pillars.add(pillar_id)
            continue

        controlled_fallback = fallback_by_pillar.get(pillar_id)
        if controlled_fallback:
            metadata = controlled_fallback.get("metadata") if isinstance(controlled_fallback.get("metadata"), dict) else {}
            metadata["source"] = "controlled_fallback"
            controlled_fallback["metadata"] = metadata
            sanitized_tasks.append(controlled_fallback)
            covered_pillars.add(pillar_id)

    return sanitized_tasks


def build_grounding_context(db: Session, user_id: str, date: str) -> Dict[str, Any]:
    # 1. Fetch unread alerts
    unread_agent_alerts = (
        db.query(AgentAlert)
        .filter(AgentAlert.user_id == user_id, AgentAlert.read_at.is_(None))
        .order_by(AgentAlert.created_at.desc())
        .limit(10)
        .all()
    )

    # 2. Fetch comprehensive onboarding data (SIF)
    onboarding_context = {}
    try:
        from api.content_planning.services.content_strategy.onboarding.data_integration import OnboardingDataIntegrationService

        svc = OnboardingDataIntegrationService()
        integrated = svc.get_integrated_data_sync(user_id, db) or {}
        
        canonical = integrated.get("canonical_profile", {})
        website_analysis = integrated.get("website_analysis", {})
        
        onboarding_context = {
            "website_url": website_analysis.get("website_url"),
            "business_type": website_analysis.get("business_type"),
            "industry": canonical.get("industry") or website_analysis.get("industry"),
            "target_audience": canonical.get("target_audience") or website_analysis.get("target_audience"),
            "content_pillars": canonical.get("content_pillars", []),
            "competitors": [c.get("domain") for c in website_analysis.get("competitors", [])[:3]] if website_analysis.get("competitors") else []
        }
    except Exception as e:
        logger.warning(f"Failed to fetch onboarding data for workflow generation: {e}")

    return {
        "date": date,
        "user_id": user_id,
        "pillars": PILLAR_IDS,
        "onboarding_data": onboarding_context,
        "recent_agent_alerts": [
            {"type": a.alert_type, "severity": a.severity, "title": a.title, "message": a.message}
            for a in unread_agent_alerts
        ],
    }


import asyncio
from services.intelligence.agents.agent_orchestrator import AgentOrchestrationService
from services.task_memory_service import TaskMemoryService

# Initialize orchestration service (singleton)
orchestration_service = AgentOrchestrationService()

async def generate_agent_enhanced_plan(db: Session, user_id: str, date: str) -> Dict[str, Any]:
    activity = AgentActivityService(db, user_id)
    grounding = build_grounding_context(db, user_id, date)
    memory_service = TaskMemoryService(user_id, db)

    # 1. Get Orchestrator
    try:
        orchestrator = await orchestration_service.get_or_create_orchestrator(user_id)
    except Exception as e:
        logger.error(f"Failed to get orchestrator: {e}")
        return {"date": date, "tasks": _fallback_tasks(date)}

    # 2. Parallel "Committee" Proposal Gathering
    logger.info(f"Gathering daily task proposals from agent committee for user {user_id}")
    
    agent_tasks = []
    try:
        # Define agents to poll
        agents_to_poll = [
            orchestrator.agents.get('content'),      # ContentStrategyAgent
            orchestrator.agents.get('seo'),          # SEOOptimizationAgent
            orchestrator.agents.get('social'),       # SocialAmplificationAgent
            orchestrator.agents.get('competitor'),   # CompetitorResponseAgent
            # Add StrategyArchitect if available in orchestrator.agents
        ]
        
        # Filter out None agents (disabled/failed init)
        active_agents = [a for a in agents_to_poll if a]
        
        # Execute propose_daily_tasks in parallel
        results = await asyncio.gather(
            *[a.propose_daily_tasks(grounding) for a in active_agents],
            return_exceptions=True
        )
        
        # Collect successful proposals
        raw_proposals = []
        for res in results:
            if isinstance(res, list):
                raw_proposals.extend(res)
            elif isinstance(res, Exception):
                logger.warning(f"Agent proposal failed: {res}")

        # 3. Filter Redundant Proposals (Self-Learning)
        # Note: We need to ensure we don't filter out essential recurring tasks if they were completed long ago
        # But for now, we filter exact duplicates from recent history (last 7 days)
        # We can implement semantic filtering later
        
        # Simple deduplication based on title+pillar
        unique_map = {}
        for p in raw_proposals:
            key = f"{p.pillar_id}:{p.title}"
            if key not in unique_map:
                unique_map[key] = p
            elif p.priority == "high": # Overwrite with higher priority
                unique_map[key] = p
                
        agent_tasks = list(unique_map.values())
        
        # Phase 3: Check memory for rejections (Semantic Filter)
        # For now, we rely on exact match logic in memory service if implemented fully
        # agent_tasks = await memory_service.filter_redundant_proposals(agent_tasks)
                
    except Exception as e:
        logger.error(f"Committee proposal phase failed: {e}")
        # Continue to fallback or LLM generation if committee fails

    # 4. Final Selection
    # If we have agent tasks, use them. Otherwise fall back to LLM generation.
    if agent_tasks:
        logger.info(f"Generated {len(agent_tasks)} tasks via Agent Committee")
        
        # Convert TaskProposal objects to dicts for frontend
        final_tasks = []
        for prop in agent_tasks:
            final_tasks.append({
                "pillarId": prop.pillar_id,
                "title": prop.title,
                "description": prop.description,
                "priority": prop.priority,
                "estimatedTime": prop.estimated_time,
                "actionType": prop.action_type,
                "actionUrl": prop.action_url,
                "enabled": True,
                "metadata": {
                    "source_agent": prop.source_agent,
                    "reasoning": prop.reasoning,
                    "context_data": prop.context_data
                }
            })
            
        final_tasks = _ensure_pillar_coverage(final_tasks, user_id, date, grounding)
        return {
            "date": date,
            "tasks": final_tasks
        }

    # Fallback to original LLM generation if agents returned nothing
    logger.info("Agent committee returned no tasks, falling back to LLM generation")

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
        "Generate a personalized Today workflow plan for ALwrity with exactly 6 lifecycle pillars: "
        "plan, generate, publish, analyze, engage, remarket.\n\n"
        "User Context (Onboarding & Strategy):\n"
        f"{json.dumps(grounding.get('onboarding_data', {}), indent=2)}\n\n"
        "Rules:\n"
        "- Produce JSON only that matches the schema.\n"
        "- Include 1-3 tasks per pillar.\n"
        "- Each task must have pillarId in {plan, generate, publish, analyze, engage, remarket}.\n"
        "- Customize tasks based on the user's industry, business type, and content pillars found in User Context.\n"
        "- If competitors are listed, include a task to analyze one of them.\n"
        "- Prefer actionable tasks that can be completed today.\n"
        "- Use these common actionUrl routes when relevant: "
        "/content-planning-dashboard, /blog-writer, /linkedin-writer, /facebook-writer, /seo-dashboard, /scheduler-dashboard.\n"
        "- Keep descriptions concise.\n\n"
        f"Grounding context (Alerts):\n{json.dumps(grounding.get('recent_agent_alerts', []), indent=2)}\n"
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
        tasks = _fallback_tasks(date)
    result = {
        "date": date,
        "tasks": _ensure_pillar_coverage(tasks, user_id, date, grounding),
    }

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


async def get_or_create_daily_workflow_plan(db: Session, user_id: str, date: Optional[str] = None) -> tuple[DailyWorkflowPlan, bool]:
    date_str = date or _today_date_str()
    existing = (
        db.query(DailyWorkflowPlan)
        .filter(DailyWorkflowPlan.user_id == user_id, DailyWorkflowPlan.date == date_str)
        .first()
    )
    if existing:
        return existing, False

    plan_data = await generate_agent_enhanced_plan(db, user_id, date_str)
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
