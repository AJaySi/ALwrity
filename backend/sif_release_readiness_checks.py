import asyncio
import unittest
import sys
from pathlib import Path
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.intelligence.monitoring.semantic_dashboard import RealTimeSemanticMonitor, SemanticHealthMetric
from services.today_workflow_service import _ensure_pillar_coverage, PILLAR_IDS
from services.intelligence.sif_agents import ContentGuardianAgent as SifGuardian
from services.intelligence.agents.specialized_agents import ContentGuardianAgent as SpecializedGuardian


class _FakeIntelligence:
    def __init__(self, results=None):
        self._results = results or []

    async def search(self, query: str, limit: int = 10):
        return self._results


class _FakeCompetitorIndex:
    async def search(self, query: str, limit: int = 5):
        return [
            {"id": "comp-1", "score": 0.82},
            {"id": "comp-2", "score": 0.65},
        ]


class SIFReleaseReadinessTests(unittest.IsolatedAsyncioTestCase):
    def test_single_strategy_architect_init_block(self):
        source = Path("backend/services/intelligence/agents/agent_orchestrator.py").read_text()
        self.assertEqual(source.count('if enabled_by_key.get("strategy_architect", True):'), 1)

    async def test_semantic_health_returns_canonical_metric(self):
        monitor = RealTimeSemanticMonitor.__new__(RealTimeSemanticMonitor)
        monitor.user_id = "u1"
        metric_list = [
            SemanticHealthMetric("semantic_diversity", 0.8, 0.6, "healthy", "t", "d", []),
            SemanticHealthMetric("authority_score", 0.3, 0.4, "critical", "t", "d", ["Improve authority"]),
        ]
        async def _fake_metrics():
            return metric_list
        monitor._check_semantic_health = _fake_metrics

        result = await RealTimeSemanticMonitor.check_semantic_health(monitor)
        self.assertIsInstance(result, SemanticHealthMetric)
        self.assertEqual(result.metric_name, "semantic_health")
        self.assertEqual(result.status, "critical")

    async def test_verify_originality_uses_real_scores_sif_guardian(self):
        agent = SifGuardian.__new__(SifGuardian)
        agent.ORIGINALITY_THRESHOLD = 0.75
        agent.intelligence = _FakeIntelligence()
        agent._log_agent_operation = lambda *args, **kwargs: None

        result = await SifGuardian.verify_originality(agent, "This is sufficiently long text for originality analysis.", _FakeCompetitorIndex())
        self.assertIn("originality_score", result)
        self.assertLess(result["originality_score"], 1.0)
        self.assertIn("warning", result)
        self.assertEqual(result["method"], "competitor_index_search")

    async def test_verify_originality_uses_real_scores_specialized_guardian(self):
        agent = SpecializedGuardian.__new__(SpecializedGuardian)
        agent.ORIGINALITY_THRESHOLD = 0.75
        agent.intelligence = _FakeIntelligence()
        agent._log_agent_operation = lambda *args, **kwargs: None

        result = await SpecializedGuardian.verify_originality(agent, "This is sufficiently long text for originality analysis.", _FakeCompetitorIndex())
        self.assertIn("originality_score", result)
        self.assertLess(result["originality_score"], 1.0)
        self.assertIn("warning", result)
        self.assertEqual(result["method"], "competitor_index_search")

    def test_pillar_coverage_guardrail_backfills_missing(self):
        tasks = [{"pillarId": "plan", "title": "Plan", "description": "d", "priority": "high", "estimatedTime": 10, "actionType": "navigate", "enabled": True}]
        grounding = {"workflow_config": {"enforce_pillar_coverage": True}}

        with patch("services.today_workflow_service._build_single_task_for_missing_pillar", return_value=None):
            covered = _ensure_pillar_coverage(tasks, "u1", "2026-01-01", grounding)

        pillars = {t["pillarId"] for t in covered}
        self.assertEqual(pillars, set(PILLAR_IDS))


if __name__ == "__main__":
    unittest.main()
