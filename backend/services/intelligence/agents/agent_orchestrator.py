"""
ALwrity Agent Orchestration System
Main orchestration system that coordinates all autonomous marketing agents
Built on txtai's native agent framework
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# txtai imports for native agent framework
try:
    from txtai import Agent, LLM
    TXTAI_AVAILABLE = Agent.__module__ != "txtai.agent.placeholder"
except ImportError:
    TXTAI_AVAILABLE = False
    logging.warning("txtai not available, using fallback implementation")

from utils.logger_utils import get_service_logger
from services.intelligence.agents.core_agent_framework import (
    BaseALwrityAgent, AgentAction, AgentPerformance, StrategyOrchestratorAgent
)
from services.intelligence.agents.specialized_agents import (
    ContentStrategyAgent, CompetitorResponseAgent, SEOOptimizationAgent, SocialAmplificationAgent
)
from services.intelligence.agents.trend_surfer_agent import TrendSurferAgent
from services.intelligence.agents.market_signal_detector import (
    MarketSignal, MarketSignalDetector
)
from services.intelligence.agents.safety_framework import (
    SafetyConstraintManager, RollbackManager, UserApprovalSystem, get_safety_framework
)
from services.intelligence.agents.performance_monitor import (
    PerformanceMetric, AgentStatus, AgentPerformanceMonitor, performance_service
)

logger = get_service_logger(__name__)

@dataclass
class AgentTeamConfiguration:
    """Configuration for the complete agent team"""
    user_id: str
    shared_llm: str = "Qwen/Qwen3-4B-Instruct-2507"
    max_iterations: int = 15
    enable_safety: bool = True
    enable_performance_monitoring: bool = True
    enable_market_signals: bool = True
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()

class ALwrityAgentOrchestrator:
    """Main orchestrator for ALwrity autonomous marketing agents"""
    
    def __init__(self, config: AgentTeamConfiguration):
        self.config = config
        self.user_id = config.user_id
        self.agents: Dict[str, BaseALwrityAgent] = {}
        self.orchestrator_agent: Optional[Agent] = None
        self.market_detector: Optional[MarketSignalDetector] = None
        self.performance_monitor: Optional[AgentPerformanceMonitor] = None
        self.safety_framework: Optional[Dict[str, Any]] = None
        
        # Initialize components
        self._initialize_components()
        
        logger.info(f"Initialized ALwrityAgentOrchestrator for user: {self.user_id}")
    
    def _initialize_components(self):
        """Initialize all agent system components"""
        try:
            # Initialize shared LLM
            if TXTAI_AVAILABLE:
                self.llm = LLM(self.config.shared_llm)
            else:
                self.llm = None
            
            # Initialize market signal detector
            if self.config.enable_market_signals:
                self.market_detector = MarketSignalDetector(self.user_id)
            
            # Initialize performance monitoring
            if self.config.enable_performance_monitoring:
                self.performance_monitor = AgentPerformanceMonitor(self.user_id)
            
            # Initialize safety framework
            if self.config.enable_safety:
                self.safety_framework = get_safety_framework(self.user_id)
            
            # Create specialized agents
            self._create_specialized_agents()
            
            # Create master orchestrator agent
            self._create_orchestrator_agent()
            
        except Exception as e:
            logger.error(f"Error initializing components for user {self.user_id}: {e}")
            raise e
    
    def _create_specialized_agents(self):
        """Create specialized marketing agents"""
        try:
            enabled_by_key = {}
            db = None
            try:
                from services.database import get_session_for_user
                from models.agent_activity_models import AgentProfile

                db = get_session_for_user(self.user_id)
                if db:
                    profiles = db.query(AgentProfile).filter(AgentProfile.user_id == self.user_id).all()
                    enabled_by_key = {p.agent_key: bool(p.enabled) for p in profiles if p and p.agent_key and p.enabled is not None}
            except Exception:
                enabled_by_key = {}
            finally:
                try:
                    if db:
                        db.close()
                except Exception:
                    pass

            # Content Strategy Agent
            if enabled_by_key.get("content_strategist", True):
                self.content_agent = ContentStrategyAgent(self.user_id, self.config.shared_llm, llm=self.llm)
                self.agents['content'] = self.content_agent
            
            # Competitor Response Agent
            if enabled_by_key.get("competitor_analyst", True):
                self.competitor_agent = CompetitorResponseAgent(self.user_id, self.config.shared_llm, llm=self.llm)
                self.agents['competitor'] = self.competitor_agent
            
            # SEO Optimization Agent
            if enabled_by_key.get("seo_specialist", True):
                self.seo_agent = SEOOptimizationAgent(self.user_id, self.config.shared_llm, llm=self.llm)
                self.agents['seo'] = self.seo_agent
            
            # Social Amplification Agent
            if enabled_by_key.get("social_media_manager", True):
                self.social_agent = SocialAmplificationAgent(self.user_id, self.config.shared_llm, llm=self.llm)
                self.agents['social'] = self.social_agent

            # Trend Surfer Agent
            if enabled_by_key.get("trend_surfer", True):
                # TrendSurferAgent needs TxtaiIntelligenceService, which we might need to get from SIF or initialize
                # For now, we assume SIF integration is handled elsewhere or we pass a mock/stub if needed
                # But wait, TrendSurferAgent constructor is (intelligence_service, user_id)
                # We need to get the intelligence service here.
                # Since AgentOrchestrator doesn't hold TxtaiIntelligenceService directly (SIFIntegrationService does),
                # this is tricky. 
                # However, SIFIntegrationService initializes AgentOrchestrator.
                # Let's import TxtaiIntelligenceService and initialize it here for the agent
                from services.intelligence.txtai_service import TxtaiIntelligenceService
                intel_service = TxtaiIntelligenceService(self.user_id)
                self.trend_surfer_agent = TrendSurferAgent(intel_service, self.user_id)
                self.agents['trend'] = self.trend_surfer_agent
            
            logger.info(f"Created {len(self.agents)} specialized agents for user {self.user_id}")
            
        except Exception as e:
            logger.error(f"Error creating specialized agents for user {self.user_id}: {e}")
            raise e
    
    # Specialized agent creation methods have been moved to specialized_agents.py

    
    def _create_orchestrator_agent(self):
        """Create master orchestrator agent using txtai native framework"""
        try:
            self.orchestrator_agent = StrategyOrchestratorAgent(
                user_id=self.user_id,
                market_detector=self.market_detector,
                performance_monitor=self.performance_monitor,
                llm=self.llm
            )
            
            # Set sub-agents
            self.orchestrator_agent.set_sub_agents(self.agents)
            
            logger.info(f"Created StrategyOrchestratorAgent for user {self.user_id}")
            
        except Exception as e:
            logger.error(f"Error creating orchestrator agent: {e}")
            # Fallback to simple agent if class instantiation fails
            self.orchestrator_agent = Agent(llm=self.llm)
    
    async def execute_marketing_strategy(self, market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute coordinated marketing strategy using agent team"""
        try:
            logger.info(f"Executing marketing strategy for user {self.user_id}")
            
            # Prepare comprehensive context
            context = await self._prepare_orchestrator_context(market_context)
            
            # Execute orchestrator with full team
            # The StrategyOrchestratorAgent will autonomously delegate tasks to sub-agents
            instruction = (
                "Analyze current market conditions and coordinate our marketing team to respond effectively.\n\n"
                "Please:\n"
                "1. Analyze the market situation.\n"
                "2. DELEGATE tasks to specific agents using the 'task_delegator' tool.\n"
                "3. Synthesize their results into a unified strategy.\n"
                "4. Provide specific action recommendations.\n\n"
                "Return a comprehensive strategy with specific actions, priorities, and expected outcomes."
            )
            orchestrator_prompt = self.orchestrator_agent.build_task_prompt(instruction=instruction, task_context=context)
            result = await self.orchestrator_agent.run(orchestrator_prompt)
            
            # Record performance metrics for the orchestration itself
            if self.config.enable_performance_monitoring:
                # We assume the agent's internal tracking handles per-action metrics
                pass
            
            logger.info(f"Marketing strategy execution completed for user {self.user_id}")
            
            return {
                "success": True,
                "strategy": result,
                "timestamp": datetime.utcnow().isoformat(),
                # In a real system, we might parse the result to extract structured data
            }
            
        except Exception as e:
            logger.error(f"Agent team execution failed for user {self.user_id}: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def process_market_signals(self) -> List[MarketSignal]:
        """Process market signals and generate agent responses"""
        try:
            if not self.market_detector:
                return []
            
            # Detect market signals
            signals = await self.market_detector.detect_market_signals()
            
            logger.info(f"Processed {len(signals)} market signals for user {self.user_id}")
            
            return signals
            
        except Exception as e:
            logger.error(f"Error processing market signals for user {self.user_id}: {e}")
            return []
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        try:
            agent_statuses = {}
            
            for agent_type, agent in self.agents.items():
                if hasattr(agent, 'get_current_status'):
                    status = await agent.get_current_status()
                    agent_statuses[agent_type] = status
            
            # Get performance metrics if available
            performance_summary = {}
            if self.performance_monitor:
                all_performance = self.performance_monitor.get_all_agents_performance()
                performance_summary = {perf['agent_id']: perf for perf in all_performance}
            
            return {
                "user_id": self.user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "agent_statuses": agent_statuses,
                "performance_summary": performance_summary,
                "market_signals_active": self.config.enable_market_signals,
                "safety_enabled": self.config.enable_safety,
                "performance_monitoring_enabled": self.config.enable_performance_monitoring
            }
            
        except Exception as e:
            logger.error(f"Error getting agent status for user {self.user_id}: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # Tool implementations for txtai agents have been moved to StrategyOrchestratorAgent class

    
    # Specialized agent tools have been moved to specialized_agents.py

    
    # Helper methods
    
    async def _prepare_orchestrator_context(self, market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare comprehensive context for orchestrator"""
        context = {
            "user_id": self.user_id,
            "market_conditions": market_context,
            "timestamp": datetime.utcnow().isoformat(),
            "available_agents": list(self.agents.keys()),
            "agent_capabilities": self._get_agent_capabilities(),
            "system_status": await self.get_agent_status()
        }
        
        return context
    
    def _get_agent_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of each agent type"""
        return {
            "content": ["Content analysis", "Gap detection", "Optimization", "Performance tracking"],
            "competitor": ["Competitor monitoring", "Threat analysis", "Response generation", "Strategy execution"],
            "seo": ["SEO auditing", "Issue prioritization", "Auto-fixing", "Strategy generation"],
            "social": ["Social monitoring", "Content adaptation", "Engagement optimization", "Distribution management"],
            "trend": ["Trend detection", "Opportunity analysis", "Content angle generation"]
        }

# Service class for agent orchestration
class AgentOrchestrationService:
    """Service class for managing agent orchestration"""
    
    def __init__(self):
        self.orchestrators: Dict[str, ALwrityAgentOrchestrator] = {}
        self.execution_history: List[Dict[str, Any]] = []
        
        logger.info("Initialized AgentOrchestrationService")
    
    async def get_or_create_orchestrator(self, user_id: str) -> ALwrityAgentOrchestrator:
        """Get or create an orchestrator for a user"""
        if user_id not in self.orchestrators:
            config = AgentTeamConfiguration(user_id=user_id)
            self.orchestrators[user_id] = ALwrityAgentOrchestrator(config)
            logger.info(f"Created new orchestrator for user: {user_id}")
        
        return self.orchestrators[user_id]
    
    async def execute_marketing_strategy(self, user_id: str, market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute marketing strategy for a user"""
        try:
            orchestrator = await self.get_or_create_orchestrator(user_id)
            result = await orchestrator.execute_marketing_strategy(market_context)
            
            # Record in history
            execution_record = {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "market_context": market_context,
                "result": result,
                "success": result.get("success", False)
            }
            self.execution_history.append(execution_record)
            
            # Keep only recent history (last 1000)
            if len(self.execution_history) > 1000:
                self.execution_history = self.execution_history[-1000:]
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing marketing strategy for user {user_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_agent_status(self, user_id: str) -> Dict[str, Any]:
        """Get agent status for a user"""
        try:
            orchestrator = await self.get_or_create_orchestrator(user_id)
            return await orchestrator.get_agent_status()
            
        except Exception as e:
            logger.error(f"Error getting agent status for user {user_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def process_market_signals(self, user_id: str) -> List[MarketSignal]:
        """Process market signals for a user"""
        try:
            orchestrator = await self.get_or_create_orchestrator(user_id)
            return await orchestrator.process_market_signals()
            
        except Exception as e:
            logger.error(f"Error processing market signals for user {user_id}: {e}")
            return []
    
    def get_execution_history(self, user_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get execution history"""
        if user_id:
            return [record for record in self.execution_history if record["user_id"] == user_id][-limit:]
        else:
            return self.execution_history[-limit:]
    
    def get_global_performance_stats(self) -> Dict[str, Any]:
        """Get global performance statistics"""
        if not self.execution_history:
            return {}
        
        total_executions = len(self.execution_history)
        successful_executions = len([r for r in self.execution_history if r.get("success", False)])
        
        unique_users = len(set(r["user_id"] for r in self.execution_history))
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0.0,
            "unique_users": unique_users,
            "timestamp": datetime.utcnow().isoformat()
        }

# Global service instance
orchestration_service = AgentOrchestrationService()

# Convenience functions for external use
async def execute_marketing_strategy(user_id: str, market_context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute marketing strategy for a user"""
    return await orchestration_service.execute_marketing_strategy(user_id, market_context)

async def get_agent_system_status(user_id: str) -> Dict[str, Any]:
    """Get agent system status for a user"""
    return await orchestration_service.get_agent_status(user_id)

async def process_market_signals_for_user(user_id: str) -> List[MarketSignal]:
    """Process market signals for a user"""
    return await orchestration_service.process_market_signals(user_id)
