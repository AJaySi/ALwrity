import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock

import pytest


class FakeQuery:
    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return None


class FakeDB:
    def __init__(self):
        self.added = []

    def query(self, *args, **kwargs):
        return FakeQuery()

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        return None

    def close(self):
        return None


class _TaskBase:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class FakeOnboardingFullWebsiteAnalysisTask(_TaskBase):
    user_id = "user_id"
    website_url = "website_url"


class FakeDeepCompetitorAnalysisTask(_TaskBase):
    user_id = "user_id"
    website_url = "website_url"


class FakeSIFIndexingTask(_TaskBase):
    user_id = "user_id"
    website_url = "website_url"


class FakeMarketTrendsTask(_TaskBase):
    user_id = "user_id"
    website_url = "website_url"


def _load_completion_module():
    module_name = "test_onboarding_completion_service_module"
    file_path = Path("/workspace/ALwrity/backend/api/onboarding_utils/onboarding_completion_service.py")

    onboarding_mod = ModuleType("api.content_planning.services.content_strategy.onboarding")
    onboarding_mod.OnboardingDataIntegrationService = lambda: SimpleNamespace(
        get_integrated_data_sync=lambda user_id, db: {
            "website_analysis": {"website_url": "https://acme.dev"},
            "research_preferences": {"competitors": []},
            "competitor_analysis": [
                {"competitor_url": "https://first-competitor.com/path"},
                {"competitor_domain": "second-competitor.com"},
                {"competitor_url": "https://first-competitor.com/another"},
            ],
        }
    )

    database_mod = ModuleType("services.database")
    db_for_tasks = FakeDB()
    database_mod.get_session_for_user = lambda user_id: FakeDB()
    database_mod.SessionLocal = lambda: db_for_tasks

    persona_mod = ModuleType("services.persona_analysis_service")
    persona_mod.PersonaAnalysisService = lambda: SimpleNamespace()

    research_sched_mod = ModuleType("services.research.research_persona_scheduler")
    research_sched_mod.schedule_research_persona_generation = lambda *a, **k: None

    facebook_sched_mod = ModuleType("services.persona.facebook.facebook_persona_scheduler")
    facebook_sched_mod.schedule_facebook_persona_generation = lambda *a, **k: None

    progress_mod = ModuleType("services.onboarding.progress_service")
    progress_mod.OnboardingProgressService = lambda: SimpleNamespace(complete_onboarding=lambda user_id: True)

    setup_mod = ModuleType("services.progressive_setup_service")
    setup_mod.ProgressiveSetupService = lambda db: SimpleNamespace(initialize_user_environment=lambda user_id: None)

    website_sched_mod = ModuleType("services.website_analysis_monitoring_service")
    website_sched_mod.schedule_website_analysis_task_creation = lambda *a, **k: None

    models_mod = ModuleType("models.website_analysis_monitoring_models")
    models_mod.OnboardingFullWebsiteAnalysisTask = FakeOnboardingFullWebsiteAnalysisTask
    models_mod.DeepCompetitorAnalysisTask = FakeDeepCompetitorAnalysisTask
    models_mod.SIFIndexingTask = FakeSIFIndexingTask
    models_mod.MarketTrendsTask = FakeMarketTrendsTask

    sys.modules["api.content_planning.services.content_strategy.onboarding"] = onboarding_mod
    sys.modules["services.database"] = database_mod
    sys.modules["services.persona_analysis_service"] = persona_mod
    sys.modules["services.research.research_persona_scheduler"] = research_sched_mod
    sys.modules["services.persona.facebook.facebook_persona_scheduler"] = facebook_sched_mod
    sys.modules["services.onboarding.progress_service"] = progress_mod
    sys.modules["services.progressive_setup_service"] = setup_mod
    sys.modules["services.website_analysis_monitoring_service"] = website_sched_mod
    sys.modules["models.website_analysis_monitoring_models"] = models_mod

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module, db_for_tasks


@pytest.mark.asyncio
async def test_complete_onboarding_uses_competitor_analysis_fallback_for_deep_task():
    module, db_for_tasks = _load_completion_module()

    service = module.OnboardingCompletionService()
    service._validate_required_steps_database = AsyncMock(return_value=[])
    service._validate_api_keys = AsyncMock(return_value=None)
    service._generate_persona_from_onboarding = AsyncMock(return_value=False)

    result = await service.complete_onboarding({"id": "user-123"})

    assert result["message"] == "Onboarding completed successfully"

    deep_tasks = [obj for obj in db_for_tasks.added if isinstance(obj, FakeDeepCompetitorAnalysisTask)]
    assert len(deep_tasks) == 1
    assert deep_tasks[0].payload["competitors"] == [
        "https://first-competitor.com",
        "second-competitor.com",
    ]
