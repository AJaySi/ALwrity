"""
Agent Performance Monitoring Framework for ALwrity Autonomous Marketing Agents
Tracks agent performance, efficiency, and provides optimization recommendations
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque

from utils.logger_utils import get_service_logger
from services.database import get_session_for_user

logger = get_service_logger(__name__)

class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"
    INITIALIZING = "initializing"

class PerformanceMetric(Enum):
    RESPONSE_TIME = "response_time"
    SUCCESS_RATE = "success_rate"
    TOKEN_USAGE = "token_usage"
    COST_PER_ACTION = "cost_per_action"
    RESOURCE_UTILIZATION = "resource_utilization"
    GOAL_COMPLETION_RATE = "goal_completion_rate"

@dataclass
class AgentPerformanceMetrics:
    agent_id: str
    timestamp: datetime
    metrics: Dict[str, float]
    context: Dict[str, Any]

class PerformanceMonitor:
    """
    Monitors and analyzes agent performance metrics
    """
    
    def __init__(self):
        self.metrics_buffer = deque(maxlen=1000)
        self.performance_history = defaultdict(list)
        self.alert_thresholds = {
            PerformanceMetric.SUCCESS_RATE: 0.8,  # Alert if success rate < 80%
            PerformanceMetric.RESPONSE_TIME: 30.0, # Alert if response time > 30s
            PerformanceMetric.GOAL_COMPLETION_RATE: 0.7 # Alert if completion < 70%
        }
    
    async def record_metric(self, 
                          agent_id: str, 
                          metric_type: PerformanceMetric, 
                          value: float,
                          context: Optional[Dict[str, Any]] = None):
        """Record a performance metric for an agent"""
        metric_entry = AgentPerformanceMetrics(
            agent_id=agent_id,
            timestamp=datetime.utcnow(),
            metrics={metric_type.value: value},
            context=context or {}
        )
        
        self.metrics_buffer.append(metric_entry)
        self.performance_history[agent_id].append(metric_entry)
        
        # Check thresholds
        await self._check_thresholds(agent_id, metric_type, value)
        
        # Persist if needed (batching implemented in production)
        # await self._persist_metric(metric_entry)
        
    async def get_agent_performance(self, agent_id: str, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get aggregated performance metrics for an agent"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
        relevant_metrics = [
            m for m in self.performance_history[agent_id] 
            if m.timestamp > cutoff_time
        ]
        
        if not relevant_metrics:
            return {}
            
        aggregated = defaultdict(list)
        for m in relevant_metrics:
            for k, v in m.metrics.items():
                aggregated[k].append(v)
                
        result = {
            "agent_id": agent_id,
            "period_minutes": time_window_minutes,
            "sample_size": len(relevant_metrics),
            "metrics": {
                k: sum(v) / len(v) for k, v in aggregated.items()
            }
        }
        
        return result
        
    async def _check_thresholds(self, agent_id: str, metric_type: PerformanceMetric, value: float):
        """Check if metric violates thresholds"""
        threshold = self.alert_thresholds.get(metric_type)
        if not threshold:
            return
            
        is_violation = False
        if metric_type in [PerformanceMetric.SUCCESS_RATE, PerformanceMetric.GOAL_COMPLETION_RATE]:
            if value < threshold:
                is_violation = True
        elif value > threshold:
            is_violation = True
            
        if is_violation:
            logger.warning(
                f"Performance alert for agent {agent_id}: "
                f"{metric_type.value} = {value} (Threshold: {threshold})"
            )
            # Trigger alert notification (impl via notification service)

# Singleton instance
performance_monitor = PerformanceMonitor()
AgentPerformanceMonitor = PerformanceMonitor
performance_service = performance_monitor
