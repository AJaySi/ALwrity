"""
Competitor Response Agent implementation.
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

class CompetitorResponseAgent(BaseALwrityAgent):
    """
    Agent responsible for monitoring competitors and generating counter-strategies.
    """
    
    def __init__(self, user_id: str, shared_llm_name: str, llm: Any = None, **kwargs):
        super().__init__(user_id, "competitor_analyst", shared_llm_name, llm, **kwargs)
        
        self.sif_service = None
        if SIF_AVAILABLE and has_onboarding_session(user_id):
            try:
                self.sif_service = SIFIntegrationService(user_id)
            except Exception as e:
                logger.warning(f"Failed to initialize SIF service for CompetitorResponseAgent: {e}")
        elif SIF_AVAILABLE:
            logger.debug(
                "Skipping SIF service initialization for CompetitorResponseAgent user {}: no onboarding session",
                user_id,
            )

    def _create_txtai_agent(self):
        """Create a specialized txtai Agent for competitor analysis."""
        if not TXTAI_AVAILABLE or Agent is None:
            return None
            
        _llm_for_agent = getattr(self.llm, "llm", self.llm)
        return Agent(
            tools=[
                {
                    "name": "competitor_monitor",
                    "description": "Monitors competitor content and changes",
                    "target": self._competitor_monitor_tool
                },
                {
                    "name": "threat_analyzer",
                    "description": "Analyzes competitive threats",
                    "target": self._threat_analyzer_tool
                }
            ],
            llm=_llm_for_agent,
            max_iterations=5,
            # Removed unsupported 'system' argument
            # Instruction will be provided via orchestrator context or initial prompt
            # Instruction should be provided during invocation or via orchestrator context
        )
    
    # Tool Implementations
    
    def _competitor_monitor_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Competitor monitoring tool that retrieves data via SIF.
        
        Args:
            context: Dictionary containing 'competitor_url' (optional) to filter monitoring targets.
        """
        # Stub implementation
        return {"status": "monitored", "changes": []}
    
    def _threat_analyzer_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Threat analysis tool using SIF data.
        
        Args:
            context: Dictionary containing analysis parameters like 'focus_area' or 'timeframe'.
        """
        # Stub implementation
        return {"threat_assessment": "Low", "level": "low"}

    async def propose_daily_tasks(self, context: Dict[str, Any]) -> List[TaskProposal]:
        """
        Propose tasks based on competitive intel.
        """
        proposals = []
        
        # 1. Competitor Gap Fill
        proposals.append(TaskProposal(
            title="Cover 'AI Agent Frameworks'",
            description="Competitor X just published a guide on this. Create a better version.",
            pillar_id="create",
            priority="high",
            estimated_time=60,
            source_agent="CompetitorResponseAgent",
            reasoning="High-value topic gaining traction.",
            action_type="navigate",
            action_url="/content-planning-dashboard"
        ))
        
        return proposals
