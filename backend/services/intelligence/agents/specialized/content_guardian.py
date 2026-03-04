"""
Content Guardian Agent implementation.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger
from .base import SIFBaseAgent, TXTAI_AVAILABLE, Agent
from services.intelligence.agents.core_agent_framework import TaskProposal
from services.intelligence.txtai_service import TxtaiIntelligenceService

class ContentGuardianAgent(SIFBaseAgent):
    """Agent for monitoring brand consistency and quality."""
    
    def __init__(self, intelligence_service: TxtaiIntelligenceService, user_id: str, **kwargs):
        # Pass kwargs to superclass to handle 'task' and other framework arguments
        super().__init__(intelligence_service, user_id, agent_type="content_guardian", **kwargs)

    async def _create_txtai_agent(self):
        """Create a specialized txtai Agent for content review."""
        if not TXTAI_AVAILABLE or Agent is None:
            return None
        
        try:
            _llm_for_agent = getattr(self.llm, "llm", self.llm)
            return Agent(
                tools=[
                    {
                        "name": "brand_voice_checker",
                        "description": "Checks content against brand voice guidelines",
                        "target": self._check_brand_voice
                    }
                ],
                llm=_llm_for_agent,
                max_iterations=3
            )
        except Exception as e:
            logger.error(f"Failed to create txtai agent for ContentGuardian: {e}")
            raise e
        
    def _check_brand_voice(self, content: str) -> Dict[str, Any]:
        """Tool to check brand voice consistency."""
        # This would use semantic search to compare against brand guidelines
        return {
            "consistent": True,
            "score": 0.95,
            "notes": "Content aligns with professional/authoritative tone."
        }

    async def propose_daily_tasks(self, context: Dict[str, Any]) -> List[TaskProposal]:
        """Propose quality assurance tasks."""
        proposals = []
        
        # 1. Content Freshness Audit
        proposals.append(TaskProposal(
            title="Audit Old Content",
            description="Review top performing posts from >6 months ago for updates.",
            pillar_id="create",
            priority="low",
            estimated_time=30,
            source_agent="ContentGuardianAgent",
            reasoning="Maintains content relevance and authority.",
            action_type="navigate",
            action_url="/content-planning-dashboard"
        ))
        
        return proposals
