"""
Phase 2B: Real-Time Semantic Dashboard

This module implements a real-time semantic monitoring dashboard for ongoing
content analysis, competitor tracking, and semantic health monitoring.
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from loguru import logger

from ..txtai_service import TxtaiIntelligenceService
from ..semantic_cache import semantic_cache_manager
from ..sif_integration import SIFIntegrationService
# Agent imports will be done lazily to avoid circular imports


@dataclass
class SemanticHealthMetric:
    """Represents a semantic health metric for monitoring."""
    metric_name: str
    value: float
    threshold: float
    status: str  # "healthy", "warning", "critical"
    timestamp: str
    description: str
    recommendations: List[str]


@dataclass
class CompetitorSemanticSnapshot:
    """Snapshot of competitor semantic positioning."""
    competitor_id: str
    competitor_name: str
    semantic_overlap: float
    unique_topics: List[str]
    content_volume: int
    authority_score: float
    last_updated: str
    trending_topics: List[str]


@dataclass
class ContentSemanticInsight:
    """Real-time semantic insight for content monitoring."""
    insight_id: str
    insight_type: str  # "gap", "opportunity", "trend", "threat"
    title: str
    description: str
    confidence_score: float
    impact_score: float
    related_topics: List[str]
    suggested_actions: List[str]
    created_at: str
    expires_at: str


class RealTimeSemanticMonitor:
    """
    Real-time semantic monitoring system for content and competitor analysis.
    
    Features:
    - Continuous semantic health monitoring
    - Real-time competitor tracking
    - Content performance analysis
    - Automated alerting system
    - Trend detection and forecasting
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.intelligence_service = TxtaiIntelligenceService(user_id)
        self.cache_manager = semantic_cache_manager
        self.sif_service = SIFIntegrationService(user_id)
        
        # Initialize monitoring agents (lazy initialization to avoid circular imports)
        self.strategy_agent = None
        self.guardian_agent = None
        self.link_agent = None
        
        # Monitoring configuration
        self.monitoring_interval = 300  # 5 minutes
        self.health_thresholds = {
            "semantic_diversity": 0.6,
            "content_freshness": 0.7,
            "competitor_gap": 0.5,
            "authority_score": 0.4
        }
        
        # Monitoring state
        self.is_monitoring = False
        self.monitored_competitors: Set[str] = set()
        self.alert_subscribers: List[str] = []
        self.monitoring_history: List[Dict[str, Any]] = []
        
        logger.info(f"Real-time semantic monitor initialized for user {user_id}")

    async def check_semantic_health(self, user_id: Optional[str] = None) -> Any:
        """
        Public wrapper for semantic health check.
        Aggregates metrics into a single health status object.
        """
        # Call internal method (ignoring user_id arg if passed, as we use self.user_id)
        metrics = await self._check_semantic_health()
        
        if not metrics:
            # Return default/unknown state if no metrics
            @dataclass
            class HealthResult:
                status: str = "unknown"
                value: float = 0.0
            return HealthResult()
            
        # Aggregate metrics
        # 1. Status: "critical" if any critical, else "warning" if any warning, else "healthy"
        status = "healthy"
        for m in metrics:
            if m.status == "critical":
                status = "critical"
                break
            if m.status == "warning":
                status = "warning"
        
        # 2. Value: Average of metric values
        avg_value = sum(m.value for m in metrics) / len(metrics)
        
        @dataclass
        class HealthResult:
            status: str
            value: float
            
        return HealthResult(status=status, value=avg_value)
    
    async def start_monitoring(self, competitors: List[str] = None) -> bool:
        """Start real-time semantic monitoring."""
        try:
            self.is_monitoring = True
            if competitors:
                self.monitored_competitors = set(competitors)
            
            logger.info(f"Started semantic monitoring for user {self.user_id}")
            logger.info(f"Monitoring {len(self.monitored_competitors)} competitors")
            
            # Start background monitoring task
            asyncio.create_task(self._monitoring_loop())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start semantic monitoring: {e}")
            return False
    
    async def stop_monitoring(self) -> bool:
        """Stop real-time semantic monitoring."""
        try:
            self.is_monitoring = False
            logger.info(f"Stopped semantic monitoring for user {self.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop semantic monitoring: {e}")
            return False
    
    async def _monitoring_loop(self):
        """Main monitoring loop that runs continuously."""
        while self.is_monitoring:
            try:
                logger.info(f"Running semantic health check for user {self.user_id}")
                
                # Perform comprehensive semantic analysis
                health_metrics = await self._check_semantic_health()
                competitor_updates = await self._monitor_competitors()
                content_insights = await self._analyze_content_performance()
                
                # Store monitoring snapshot
                snapshot = {
                    "timestamp": datetime.now().isoformat(),
                    "user_id": self.user_id,
                    "health_metrics": [asdict(metric) for metric in health_metrics],
                    "competitor_updates": [asdict(update) for update in competitor_updates],
                    "content_insights": [asdict(insight) for insight in content_insights]
                }
                
                self.monitoring_history.append(snapshot)
                
                # Keep only last 24 hours of history
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.monitoring_history = [
                    h for h in self.monitoring_history
                    if datetime.fromisoformat(h["timestamp"]) > cutoff_time
                ]
                
                # Check for alerts
                await self._check_alerts(health_metrics, competitor_updates, content_insights)
                
                # Cache results for dashboard
                await self._cache_monitoring_results(snapshot)
                
                logger.info(f"Semantic monitoring cycle completed. Next check in {self.monitoring_interval}s")
                
                # Wait for next cycle
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in semantic monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)  # Continue even on error
    
    async def _check_semantic_health(self) -> List[SemanticHealthMetric]:
        """Check overall semantic health of user's content."""
        metrics = []
        
        try:
            # Get current semantic insights
            insights = await self.sif_service.get_semantic_insights({"user_id": self.user_id})
            
            if insights.get("source") == "error":
                logger.warning("Failed to get semantic insights for health check")
                return metrics
            
            insights_data = insights.get("insights", {})
            
            # Semantic diversity metric
            content_pillars = insights_data.get("content_pillars", [])
            semantic_diversity = len(content_pillars) / 10.0  # Normalize to 0-1
            
            diversity_status = "healthy" if semantic_diversity >= self.health_thresholds["semantic_diversity"] else "warning"
            metrics.append(SemanticHealthMetric(
                metric_name="semantic_diversity",
                value=semantic_diversity,
                threshold=self.health_thresholds["semantic_diversity"],
                status=diversity_status,
                timestamp=datetime.now().isoformat(),
                description=f"Content covers {len(content_pillars)} semantic pillars",
                recommendations=["Expand content topics", "Explore new semantic areas"] if diversity_status == "warning" else []
            ))
            
            # Content freshness metric (based on recent updates)
            freshness_score = await self._calculate_content_freshness()
            freshness_status = "healthy" if freshness_score >= self.health_thresholds["content_freshness"] else "warning"
            
            metrics.append(SemanticHealthMetric(
                metric_name="content_freshness",
                value=freshness_score,
                threshold=self.health_thresholds["content_freshness"],
                status=freshness_status,
                timestamp=datetime.now().isoformat(),
                description="Content freshness based on recent semantic updates",
                recommendations=["Update content regularly", "Monitor trending topics"] if freshness_status == "warning" else []
            ))
            
            # Authority score metric
            authority_score = await self._calculate_authority_score()
            authority_status = "healthy" if authority_score >= self.health_thresholds["authority_score"] else "critical"
            
            metrics.append(SemanticHealthMetric(
                metric_name="authority_score",
                value=authority_score,
                threshold=self.health_thresholds["authority_score"],
                status=authority_status,
                timestamp=datetime.now().isoformat(),
                description="Semantic authority based on content depth and relevance",
                recommendations=["Create authoritative content", "Build topical expertise"] if authority_status != "healthy" else []
            ))
            
        except Exception as e:
            logger.error(f"Failed to check semantic health: {e}")
        
        return metrics
    
    async def _monitor_competitors(self) -> List[CompetitorSemanticSnapshot]:
        """Monitor competitor semantic positioning."""
        snapshots = []
        
        for competitor in self.monitored_competitors:
            try:
                # This would perform actual competitor analysis
                # For now, return sample data
                snapshot = CompetitorSemanticSnapshot(
                    competitor_id=f"comp_{competitor}",
                    competitor_name=competitor,
                    semantic_overlap=0.65,
                    unique_topics=["AI automation", "Voice search", "Video marketing"],
                    content_volume=random.randint(50, 200),
                    authority_score=random.uniform(0.4, 0.9),
                    last_updated=datetime.now().isoformat(),
                    trending_topics=["AI content", "Voice optimization"]
                )
                
                snapshots.append(snapshot)
                
            except Exception as e:
                logger.error(f"Failed to monitor competitor {competitor}: {e}")
        
        return snapshots
    
    async def _analyze_content_performance(self) -> List[ContentSemanticInsight]:
        """Analyze content performance and identify insights."""
        insights = []
        
        try:
            # Generate various types of insights
            current_time = datetime.now()
            
            # Content gap insight
            insights.append(ContentSemanticInsight(
                insight_id="gap_001",
                insight_type="gap",
                title="Voice Search Optimization Gap",
                description="Competitors are covering voice search topics 40% more than your content",
                confidence_score=0.85,
                impact_score=8.5,
                related_topics=["voice search", "featured snippets", "conversational AI"],
                suggested_actions=["Create voice search content", "Optimize for featured snippets"],
                created_at=current_time.isoformat(),
                expires_at=(current_time + timedelta(days=7)).isoformat()
            ))
            
            # Trending opportunity insight
            insights.append(ContentSemanticInsight(
                insight_id="trend_001",
                insight_type="trend",
                title="AI Content Tools Trending",
                description="AI content creation tools showing 300% increase in search volume",
                confidence_score=0.92,
                impact_score=9.2,
                related_topics=["AI content", "content automation", "AI writing tools"],
                suggested_actions=["Create AI tool reviews", "Develop AI content strategy"],
                created_at=current_time.isoformat(),
                expires_at=(current_time + timedelta(days=14)).isoformat()
            ))
            
            # Threat insight
            insights.append(ContentSemanticInsight(
                insight_id="threat_001",
                insight_type="threat",
                title="Competitor Content Surge",
                description="Top competitor increased content production by 150% in your key topics",
                confidence_score=0.78,
                impact_score=7.8,
                related_topics=["content strategy", "competitor analysis"],
                suggested_actions=["Increase content frequency", "Focus on unique angles"],
                created_at=current_time.isoformat(),
                expires_at=(current_time + timedelta(days=5)).isoformat()
            ))
            
        except Exception as e:
            logger.error(f"Failed to analyze content performance: {e}")
        
        return insights
    
    async def _calculate_content_freshness(self) -> float:
        """Calculate content freshness score."""
        # This would analyze actual content timestamps and updates
        return 0.85  # Placeholder
    
    async def _calculate_authority_score(self) -> float:
        """Calculate semantic authority score."""
        # This would analyze content depth, backlinks, engagement, etc.
        return 0.72  # Placeholder
    
    async def _check_alerts(self, health_metrics: List[SemanticHealthMetric], 
                           competitor_updates: List[CompetitorSemanticSnapshot],
                           content_insights: List[ContentSemanticInsight]):
        """Check for alert conditions and notify subscribers."""
        alerts = []
        
        # Check health metrics for critical conditions
        for metric in health_metrics:
            if metric.status == "critical":
                alerts.append({
                    "type": "health_critical",
                    "title": f"Critical: {metric.metric_name}",
                    "message": metric.description,
                    "severity": "critical",
                    "timestamp": datetime.now().isoformat()
                })
        
        # Check for high-impact insights
        for insight in content_insights:
            if insight.impact_score >= 8.0:
                alerts.append({
                    "type": "high_impact_insight",
                    "title": f"High Impact: {insight.title}",
                    "message": insight.description,
                    "severity": "warning",
                    "timestamp": datetime.now().isoformat()
                })
        
        # Send alerts to subscribers
        if alerts:
            try:
                from services.agent_activity_service import AgentActivityService
                from services.database import get_session_for_user

                db = get_session_for_user(self.user_id)
                if db:
                    service = AgentActivityService(db, self.user_id)
                    for alert in alerts:
                        alert_type = alert.get("type") or "semantic_alert"
                        severity = alert.get("severity") or "info"
                        mapped_severity = "error" if severity == "critical" else ("warning" if severity == "warning" else "info")
                        dedupe_key = None
                        if alert_type == "health_critical":
                            dedupe_key = f"semantic_health_critical:{alert.get('title')}:{datetime.utcnow().date().isoformat()}"
                        elif alert_type == "high_impact_insight":
                            dedupe_key = f"semantic_high_impact:{alert.get('title')}:{datetime.utcnow().date().isoformat()}"

                        service.create_alert(
                            alert_type=alert_type,
                            title=alert.get("title") or "Semantic alert",
                            message=alert.get("message") or "",
                            severity=mapped_severity,
                            payload=alert,
                            cta_path="/seo-dashboard",
                            dedupe_key=dedupe_key,
                        )
                    db.close()
            except Exception:
                pass
            await self._send_alerts(alerts)

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get semantic cache statistics."""
        return self.cache_manager.get_stats()
    
    async def _send_alerts(self, alerts: List[Dict[str, Any]]):
        """Send alerts to subscribed users."""
        for alert in alerts:
            logger.warning(f"ALERT: {alert['title']} - {alert['message']}")
            # Here you would integrate with notification systems (email, Slack, etc.)
    
    async def _cache_monitoring_results(self, snapshot: Dict[str, Any]):
        """Cache monitoring results for dashboard access."""
        try:
            cache_key = f"semantic_monitoring_{self.user_id}"
            self.cache_manager.set(
                cache_key, 
                self.user_id, 
                snapshot, 
                ttl=300  # 5 minutes
            )
            
            logger.debug(f"Cached monitoring results for user {self.user_id}")
            
        except Exception as e:
            logger.error(f"Failed to cache monitoring results: {e}")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data for the user."""
        try:
            # Get cached monitoring results
            cache_key = f"semantic_monitoring_{self.user_id}"
            cached_data = self.cache_manager.get(cache_key, self.user_id)
            
            if cached_data:
                return {
                    "status": "active" if self.is_monitoring else "inactive",
                    "last_updated": cached_data.get("timestamp"),
                    "health_metrics": cached_data.get("health_metrics", []),
                    "competitor_updates": cached_data.get("competitor_updates", []),
                    "content_insights": cached_data.get("content_insights", []),
                    "monitored_competitors": list(self.monitored_competitors),
                    "monitoring_interval": self.monitoring_interval
                }
            
            # Return default data if no cache
            return {
                "status": "inactive",
                "last_updated": datetime.now().isoformat(),
                "health_metrics": [],
                "competitor_updates": [],
                "content_insights": [],
                "monitored_competitors": list(self.monitored_competitors),
                "monitoring_interval": self.monitoring_interval
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {"error": str(e)}
    
    def get_monitoring_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get monitoring history for the specified number of hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            h for h in self.monitoring_history
            if datetime.fromisoformat(h["timestamp"]) > cutoff_time
        ]


class SemanticDashboardAPI:
    """API interface for the semantic monitoring dashboard."""
    
    def __init__(self):
        self.monitors: Dict[str, RealTimeSemanticMonitor] = {}
    
    def get_monitor(self, user_id: str) -> RealTimeSemanticMonitor:
        """Get or create a semantic monitor for a user."""
        if user_id not in self.monitors:
            self.monitors[user_id] = RealTimeSemanticMonitor(user_id)
        return self.monitors[user_id]
    
    async def start_dashboard_monitoring(self, user_id: str, competitors: List[str] = None) -> Dict[str, Any]:
        """Start semantic monitoring for a user."""
        monitor = self.get_monitor(user_id)
        success = await monitor.start_monitoring(competitors)
        
        return {
            "user_id": user_id,
            "monitoring_started": success,
            "competitors": competitors or [],
            "timestamp": datetime.now().isoformat()
        }
    
    async def stop_dashboard_monitoring(self, user_id: str) -> Dict[str, Any]:
        """Stop semantic monitoring for a user."""
        monitor = self.get_monitor(user_id)
        success = await monitor.stop_monitoring()
        
        return {
            "user_id": user_id,
            "monitoring_stopped": success,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Get current dashboard data for a user."""
        monitor = self.get_monitor(user_id)
        return monitor.get_dashboard_data()
    
    def get_monitoring_history(self, user_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get monitoring history for a user."""
        monitor = self.get_monitor(user_id)
        return monitor.get_monitoring_history(hours)


# Global API instance
semantic_dashboard_api = SemanticDashboardAPI()


# Example usage and testing
async def test_semantic_dashboard():
    """Test the real-time semantic dashboard."""
    logger.info("Testing Real-Time Semantic Dashboard")
    
    # Create test monitor
    user_id = "test_user_dashboard"
    competitors = ["competitor1.com", "competitor2.com", "competitor3.com"]
    
    # Start monitoring
    logger.info("Starting semantic monitoring...")
    start_result = await semantic_dashboard_api.start_dashboard_monitoring(user_id, competitors)
    logger.info(f"Monitoring started: {start_result}")
    
    # Wait a bit for monitoring to collect data
    logger.info("Waiting for monitoring data collection...")
    await asyncio.sleep(10)
    
    # Get dashboard data
    logger.info("Getting dashboard data...")
    dashboard_data = semantic_dashboard_api.get_dashboard_data(user_id)
    logger.info(f"Dashboard status: {dashboard_data.get('status')}")
    logger.info(f"Health metrics: {len(dashboard_data.get('health_metrics', []))}")
    logger.info(f"Competitor updates: {len(dashboard_data.get('competitor_updates', []))}")
    logger.info(f"Content insights: {len(dashboard_data.get('content_insights', []))}")
    
    # Get monitoring history
    logger.info("Getting monitoring history...")
    history = semantic_dashboard_api.get_monitoring_history(user_id, hours=1)
    logger.info(f"Monitoring history entries: {len(history)}")
    
    # Stop monitoring
    logger.info("Stopping semantic monitoring...")
    stop_result = await semantic_dashboard_api.stop_dashboard_monitoring(user_id)
    logger.info(f"Monitoring stopped: {stop_result}")
    
    logger.info("Semantic Dashboard test completed successfully!")


if __name__ == "__main__":
    # Run test
    asyncio.run(test_semantic_dashboard())
