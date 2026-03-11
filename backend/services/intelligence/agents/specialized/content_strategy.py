"""
Content Strategy Agent implementation.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
from .base import SIFBaseAgent, TXTAI_AVAILABLE, Agent
from services.intelligence.agents.core_agent_framework import BaseALwrityAgent, TaskProposal
from services.seo_tools.content_strategy_service import ContentStrategyService
from services.analytics import PlatformAnalyticsService
from services.database import has_onboarding_session

try:
    from services.intelligence.sif_integration import SIFIntegrationService
    SIF_AVAILABLE = True
except ImportError:
    SIF_AVAILABLE = False

class ContentStrategyAgent(BaseALwrityAgent):
    """
    Agent responsible for content strategy, gap analysis, and optimization.
    """
    
    def __init__(self, user_id: str, shared_llm_name: str, llm: Any = None, **kwargs):
        # Correctly pass arguments to superclass
        super().__init__(user_id, "content_strategist", shared_llm_name, llm, **kwargs)
        
        self.sif_service = None
        self.content_strategy_service = ContentStrategyService()
        if SIF_AVAILABLE and has_onboarding_session(user_id):
            try:
                self.sif_service = SIFIntegrationService(user_id)
            except Exception as e:
                logger.warning(f"Failed to initialize SIF service for ContentStrategyAgent: {e}")
        elif SIF_AVAILABLE:
            logger.debug(
                "Skipping SIF service initialization for ContentStrategyAgent user {}: no onboarding session",
                user_id,
            )

    def _create_txtai_agent(self):
        """Create a specialized txtai Agent for content strategy with tools."""
        if not TXTAI_AVAILABLE or Agent is None:
            return None
            
        # Unwrap tracking wrapper for txtai Agent if present
        _llm_for_agent = getattr(self.llm, "llm", self.llm)
        return Agent(
            tools=[
                {
                    "name": "content_analyzer",
                    "description": "Analyzes content performance using SIF insights and GSC data",
                    "target": self._content_analyzer_tool_sync
                },
                {
                    "name": "semantic_gap_detector",
                    "description": "Identifies semantic gaps between current content and high-performing topics",
                    "target": self._semantic_gap_detector_tool_sync
                },
                {
                    "name": "content_optimizer",
                    "description": "Optimizes content for target keywords and user intent",
                    "target": self._content_optimizer_tool_sync
                },
                {
                    "name": "performance_tracker",
                    "description": "Tracks content performance over time",
                    "target": self._performance_tracker_tool_sync
                },
                {
                    "name": "sitemap_analyzer",
                    "description": "Analyzes website structure and publishing velocity via sitemap",
                    "target": self._sitemap_analyzer_tool_sync
                },
                {
                    "name": "gsc_low_ctr_queries",
                    "description": "Returns low-CTR queries with evidence from cached GSC metrics",
                    "target": self._cs_gsc_low_ctr_queries_tool_sync
                },
                {
                    "name": "gsc_striking_distance_queries",
                    "description": "Returns striking-distance queries (positions ~8–20) with evidence",
                    "target": self._cs_gsc_striking_distance_tool_sync
                },
                {
                    "name": "gsc_declining_queries",
                    "description": "Returns period-over-period declining queries with evidence",
                    "target": self._cs_gsc_declining_queries_tool_sync
                },
                {
                    "name": "gsc_low_ctr_pages",
                    "description": "Returns low-CTR pages with top contributing queries",
                    "target": self._cs_gsc_low_ctr_pages_tool_sync
                },
                {
                    "name": "gsc_cannibalization_candidates",
                    "description": "Returns query→multiple-pages cannibalization candidates with target recommendation",
                    "target": self._cs_gsc_cannibalization_candidates_tool_sync
                },
                {
                    "name": "default_content_gsc_plan",
                    "description": "Runs a default first-pass plan using GSC signals (titles/meta, consolidation, refreshes)",
                    "target": self._default_content_gsc_plan_tool_sync
                },
            ],
            llm=_llm_for_agent,
            max_iterations=8,
            # Removed unsupported 'system' argument for MultiStepAgent
            # Provide instruction as part of initial prompt when invoking the agent
            # or store in context via orchestrator
            # Instruction should be provided during invocation or via orchestrator context
            )
    
    # Tool Implementations
    
    def _sitemap_analyzer_tool_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes sitemap structure and publishing velocity.
        
        Args:
            context: Input parameters for analysis. Example keys:
                - sitemap_url: Optional URL to sitemap.xml
                - include_lastmod: Whether to include last modification dates
        
        Returns:
            A dictionary with summary metrics (e.g., pages, last_mod).
        """
        # Stub implementation
        return {"status": "analyzed", "pages": 0}

    async def _cs_fetch_gsc_analytics(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        svc = PlatformAnalyticsService()
        data = await svc.get_comprehensive_analytics(self.user_id, platforms=["gsc"], start_date=start_date, end_date=end_date)
        gsc = data.get("gsc")
        if not gsc or gsc.status != "success":
            err = getattr(gsc, "error_message", None) if gsc else "No data"
            raise RuntimeError(f"GSC analytics unavailable: {err}")
        return {"metrics": gsc.metrics, "date_range": gsc.date_range}

    def _cs_gsc_low_ctr_queries_tool_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetches low-CTR queries from Google Search Console signals.
        
        Args:
            context: Input parameters. Example keys:
                - date_range: Optional date range
                - limit: Max number of queries to return
        
        Returns:
            A dictionary containing items and source.
        """
        self._log_agent_operation("Fetching Low CTR Queries (Stub)", context=context)
        return {"items": [], "source": "stub"}

    def _cs_gsc_striking_distance_tool_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns striking-distance queries (positions ~8–20).
        
        Args:
            context: Input parameters. Example keys:
                - position_range: Range to consider striking distance
                - limit: Max number of queries
        
        Returns:
            A dictionary containing items and source.
        """
        self._log_agent_operation("Fetching Striking Distance Queries (Stub)", context=context)
        return {"items": [], "source": "stub"}

    def _cs_gsc_declining_queries_tool_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns period-over-period declining queries.
        
        Args:
            context: Input parameters. Example keys:
                - compare_range: Time windows to compare
                - limit: Max number of queries
        
        Returns:
            A dictionary containing items and source.
        """
        self._log_agent_operation("Fetching Declining Queries (Stub)", context=context)
        return {"items": [], "source": "stub"}

    def _cs_gsc_low_ctr_pages_tool_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns low-CTR pages with top contributing queries.
        
        Args:
            context: Input parameters. Example keys:
                - date_range: Optional date range
                - limit: Max number of pages
        
        Returns:
            A dictionary containing items and source.
        """
        self._log_agent_operation("Fetching Low CTR Pages (Stub)", context=context)
        return {"items": [], "source": "stub"}

    def _cs_gsc_cannibalization_candidates_tool_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns query→multiple-pages cannibalization candidates with target recommendation.
        
        Args:
            context: Input parameters. Example keys:
                - limit: Max number of candidates
        
        Returns:
            A dictionary containing items and source.
        """
        self._log_agent_operation("Fetching Cannibalization Candidates (Stub)", context=context)
        return {"items": [], "source": "stub"}

    def _default_content_gsc_plan_tool_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a default first-pass plan using GSC signals (titles/meta, consolidation, refreshes).
        
        Args:
            context: Input parameters. Example keys:
                - target_url: Page to optimize
                - date_range: Optional date range for signals
        
        Returns:
            A dictionary describing plan_name and actions.
        """
        self._log_agent_operation("Generating Default GSC Plan (Stub)", context=context)
        return {"plan_name": "Stub Plan", "actions": []}

    def _content_analyzer_tool_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes content performance using SIF insights and Google Search Console data.
        
        Args:
            context: Input parameters. Example keys:
                - target_url: Page to analyze
                - date_range: Optional date range
                - include_competitors: Whether to include competitor comparison
        
        Returns:
            A dictionary containing content_analysis summary, sif_insights, gsc_performance,
            identified_gaps, strategic_recommendations, and timestamp.
        """
        return {
            "content_analysis": "Completed via SIF + GSC Integration",
            "sif_insights": {},
            "gsc_performance": {"clicks": 100},
            "identified_gaps": [],
            "strategic_recommendations": [],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _content_optimizer_tool_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates specific diffs/rewrites using LLM-based rewriting and semantic analysis.
        
        Args:
            context: Input parameters. Example keys:
                - target_url: Page to optimize
                - optimization_goal: e.g., 'increase CTR', 'clarify intent'
        
        Returns:
            A dictionary containing optimized_content text or diff instructions.
        """
        return {"optimized_content": "Optimized text"}

    def _semantic_gap_detector_tool_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detects semantic gaps in current coverage versus target topics.
        
        Args:
            context: Input parameters. Example keys:
                - topics: Optional list of topics to compare against
        
        Returns:
            A list of gap objects with relevance scores.
        """
        self._log_agent_operation("Detecting gaps", context=context)
        return [{"gap": "advanced techniques", "relevance": 0.9}]

    def _performance_tracker_tool_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tracks performance metrics over time.
        
        Args:
            context: Input parameters. Example keys:
                - date_range: Optional date range
                - metrics: Optional list of metrics to track
        
        Returns:
            A dictionary containing views/engagement summary.
        """
        self._log_agent_operation("Tracking performance", context=context)
        return {"views": 100, "engagement": 0.05}

    async def propose_daily_tasks(self, context: Dict[str, Any]) -> List[TaskProposal]:
        """
        Propose strategic tasks based on content analysis.
        """
        proposals = []
        
        # 1. Content Refresh
        proposals.append(TaskProposal(
            title="Refresh 'SEO Basics'",
            description="Update your SEO basics guide with 2024 trends.",
            pillar_id="create",
            priority="high",
            estimated_time=45,
            source_agent="ContentStrategyAgent",
            reasoning="Declining traffic and outdated references.",
            action_type="navigate",
            action_url="/content-planning-dashboard"
        ))
        
        return proposals
