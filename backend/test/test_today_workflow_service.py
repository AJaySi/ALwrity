import sys
import types

import pytest

from services.intelligence.agents.core_agent_framework import TaskProposal


# Stub deep onboarding import chain before importing today_workflow_service.
module_names = [
    "api",
    "api.content_planning",
    "api.content_planning.services",
    "api.content_planning.services.content_strategy",
    "api.content_planning.services.content_strategy.onboarding",
    "api.content_planning.services.content_strategy.onboarding.data_integration",
]
for name in module_names:
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)


class _StubOnboardingDataIntegrationService:
    def get_integrated_data_sync(self, user_id, db):
        return {}


sys.modules[
    "api.content_planning.services.content_strategy.onboarding.data_integration"
].OnboardingDataIntegrationService = _StubOnboardingDataIntegrationService

from services import today_workflow_service as workflow


class _NoopActivityService:
    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id


class _NoopMemoryService:
    def __init__(self, user_id, db):
        self.user_id = user_id
        self.db = db


class _StaticAgent:
    def __init__(self, proposals):
        self._proposals = proposals

    async def propose_daily_tasks(self, _grounding):
        return self._proposals


class _FakeOrchestrationService:
    def __init__(self, orchestrator):
        self._orchestrator = orchestrator

    async def get_or_create_orchestrator(self, _user_id):
        return self._orchestrator


@pytest.mark.asyncio
async def test_generate_agent_enhanced_plan_includes_strategy_agent_proposals(monkeypatch):
    strategy_proposal = TaskProposal(
        title="Define weekly content themes",
        description="Create this week's strategic themes for planned posts.",
        pillar_id="plan",
        priority="high",
        estimated_time=20,
        source_agent="StrategyArchitectAgent",
        reasoning="Strategy-driven planning",
        action_type="navigate",
        action_url="/content-planning-dashboard",
    )

    orchestrator = type(
        "Orchestrator",
        (),
        {"agents": {"strategy": _StaticAgent([strategy_proposal])}},
    )()

    monkeypatch.setattr(workflow, "build_grounding_context", lambda db, user_id, date: {"date": date})
    monkeypatch.setattr(workflow, "AgentActivityService", _NoopActivityService)
    monkeypatch.setattr(workflow, "TaskMemoryService", _NoopMemoryService)
    monkeypatch.setattr(workflow, "orchestration_service", _FakeOrchestrationService(orchestrator))

    result = await workflow.generate_agent_enhanced_plan(db=object(), user_id="u1", date="2026-01-01")

    assert len(result["tasks"]) == 1
    assert result["tasks"][0]["pillarId"] == "plan"
    assert result["tasks"][0]["title"] == "Define weekly content themes"
    assert result["tasks"][0]["metadata"]["source_agent"] == "StrategyArchitectAgent"


@pytest.mark.asyncio
async def test_generate_agent_enhanced_plan_dedupes_plan_tasks_with_priority_and_tiebreak(monkeypatch):
    title = "Build next week content plan"

    content_medium = TaskProposal(
        title=title,
        description="Draft a medium-priority weekly plan.",
        pillar_id="plan",
        priority="medium",
        estimated_time=15,
        source_agent="ZetaAgent",
        reasoning="baseline",
    )
    strategy_high = TaskProposal(
        title=title,
        description="Draft a high-priority strategic plan.",
        pillar_id="plan",
        priority="high",
        estimated_time=20,
        source_agent="StrategyArchitectAgent",
        reasoning="urgent update",
    )
    competitor_high = TaskProposal(
        title=title,
        description="Alternative high-priority plan.",
        pillar_id="plan",
        priority="high",
        estimated_time=25,
        source_agent="BetaAgent",
        reasoning="same priority tie",
    )

    orchestrator = type(
        "Orchestrator",
        (),
        {
            "agents": {
                "content": _StaticAgent([content_medium]),
                "strategy": _StaticAgent([strategy_high]),
                "competitor": _StaticAgent([competitor_high]),
            }
        },
    )()

    monkeypatch.setattr(workflow, "build_grounding_context", lambda db, user_id, date: {"date": date})
    monkeypatch.setattr(workflow, "AgentActivityService", _NoopActivityService)
    monkeypatch.setattr(workflow, "TaskMemoryService", _NoopMemoryService)
    monkeypatch.setattr(workflow, "orchestration_service", _FakeOrchestrationService(orchestrator))

    result = await workflow.generate_agent_enhanced_plan(db=object(), user_id="u1", date="2026-01-01")

    assert len(result["tasks"]) == 1
    task = result["tasks"][0]
    assert task["title"] == title
    assert task["priority"] == "high"
    # Deterministic equal-priority tie-break keeps lexicographically earlier source agent.
    assert task["metadata"]["source_agent"] == "BetaAgent"
