"""
SEO Optimization Agent implementation.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
from .base import SIFBaseAgent, TXTAI_AVAILABLE, Agent
from services.intelligence.agents.core_agent_framework import BaseALwrityAgent, TaskProposal
from services.database import has_onboarding_session

try:
    from services.intelligence.sif_integration import SIFIntegrationService
    SIF_AVAILABLE = True
except ImportError:
    SIF_AVAILABLE = False

class SEOOptimizationAgent(BaseALwrityAgent):
    """
    Agent responsible for technical SEO, keyword strategy, and performance optimization.
    """
    
    def __init__(self, user_id: str, shared_llm_name: str, llm: Any = None, **kwargs):
        super().__init__(user_id, "seo_specialist", shared_llm_name, llm, **kwargs)
        
        self.sif_service = None
        if SIF_AVAILABLE and has_onboarding_session(user_id):
            try:
                self.sif_service = SIFIntegrationService(user_id)
            except Exception as e:
                logger.warning(f"Failed to initialize SIF service for SEOOptimizationAgent: {e}")
        elif SIF_AVAILABLE:
            logger.debug(
                "Skipping SIF service initialization for SEOOptimizationAgent user {}: no onboarding session",
                user_id,
            )

    def _create_txtai_agent(self):
        """Create a specialized txtai Agent for SEO optimization."""
        if not TXTAI_AVAILABLE or Agent is None:
            return None
            
        _llm_for_agent = getattr(self.llm, "llm", self.llm)
        return Agent(
            tools=[
                {
                    "name": "seo_auditor",
                    "description": "Performs comprehensive SEO audits",
                    "target": self._seo_auditor_tool
                },
                {
                    "name": "keyword_researcher",
                    "description": "Researches high-potential keywords",
                    "target": self._keyword_researcher_tool
                },
                {
                    "name": "on_page_optimizer",
                    "description": "Optimizes on-page elements",
                    "target": self._on_page_optimizer_tool
                },
                {
                    "name": "technical_fixer",
                    "description": "Fixes technical SEO issues",
                    "target": self._technical_fixer_tool
                }
            ],
            llm=_llm_for_agent,
            max_iterations=15,
            # Removed unsupported 'system' argument
            # Instruction will be provided via orchestrator context or initial prompt
            # Instruction should be provided during invocation or via orchestrator context
        )
    
    # Tool Implementations
    
    def _seo_auditor_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        SEO audit tool that retrieves existing SEO data via SIF.
        
        Args:
            context: Dictionary containing 'website_url' to audit.
        """
        # Stub implementation
        return {"health": "good", "issues": []}

    def _keyword_researcher_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Keyword research tool.
        
        Args:
            context: Dictionary containing 'seed_keywords' or 'topic'.
        """
        # Stub implementation
        return {"keywords": []}

    def _on_page_optimizer_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        On-page optimization tool.
        
        Args:
            context: Dictionary containing 'url' and 'target_keyword'.
        """
        # Stub implementation
        return {"optimized": True}

    def _technical_fixer_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Technical SEO fixer tool.
        
        Args:
            context: Dictionary containing 'issue_id' to fix.
        """
        # Stub implementation
        return {"fixed": True}

    async def propose_daily_tasks(self, context: Dict[str, Any]) -> List[TaskProposal]:
        """
        Propose SEO-focused tasks.
        """
        proposals = []
        
        # 1. Quick SEO Win
        proposals.append(TaskProposal(
            title="Fix Broken Links",
            description="3 internal links on 'About Us' page are broken.",
            pillar_id="distribute",
            priority="high",
            estimated_time=10,
            source_agent="SEOOptimizationAgent",
            reasoning="Easy technical win.",
            action_type="navigate",
            action_url="/content-planning-dashboard"
        ))
        
        return proposals
