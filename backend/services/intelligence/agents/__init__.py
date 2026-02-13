"""
ALwrity Autonomous Marketing Agents Module

This module provides autonomous marketing agents built on txtai's native agent framework. 
The agents work together to monitor market conditions, analyze competitor activities,
and execute coordinated marketing strategies without human intervention.
"""

# Core agent framework
from .core_agent_framework import (
    BaseALwrityAgent,
    AgentAction,
    AgentPerformance,
    StrategyOrchestratorAgent
)

# Market signal detection
from .market_signal_detector import (
    MarketSignal,
    MarketSignalDetector
)

# Performance monitoring
from .performance_monitor import (
    PerformanceMonitor,
    performance_monitor,
    PerformanceMetric,
    AgentPerformanceMetrics
)

# Specialized agents
from .specialized_agents import (
    ContentGuardianAgent,
    LinkGraphAgent,
    StrategyArchitectAgent,
    ContentStrategyAgent,
    CompetitorResponseAgent,
    SEOOptimizationAgent,
    SocialAmplificationAgent
)

from .trend_surfer_agent import TrendSurferAgent

# Agent Orchestrator
from .agent_orchestrator import (
    ALwrityAgentOrchestrator,
    orchestration_service
)

__all__ = [
    'BaseALwrityAgent',
    'AgentAction',
    'AgentPerformance',
    'StrategyOrchestratorAgent',
    'MarketSignal',
    'MarketSignalDetector',
    'MarketTrendAnalyzer',
    'PerformanceMonitor',
    'performance_monitor',
    'PerformanceMetric',
    'AgentPerformanceMetrics',
    'ContentGuardianAgent',
    'LinkGraphAgent',
    'StrategyArchitectAgent',
    'ContentStrategyAgent',
    'CompetitorResponseAgent',
    'SEOOptimizationAgent',
    'SocialAmplificationAgent',
    'TrendSurferAgent',
    'ALwrityAgentOrchestrator',
    'orchestration_service'
]
