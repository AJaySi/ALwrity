"""
Scheduler Monitoring and Alerting System
Provides comprehensive monitoring, alerting, and health checks for the ALwrity scheduler
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from loguru import logger
from dataclasses import dataclass, field
from enum import Enum
import json

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertType(Enum):
    CONNECTION_EXHAUSTION = "connection_exhaustion"
    SCHEDULER_ERROR = "scheduler_error"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    DATABASE_ERROR = "database_error"
    TASK_FAILURE = "task_failure"
    HEALTH_CHECK_FAILED = "health_check_failed"

@dataclass
class Alert:
    """Scheduler alert data structure"""
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class HealthCheckResult:
    """Health check result"""
    healthy: bool
    checks: Dict[str, bool] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    alerts: List[Alert] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

class SchedulerMonitor:
    """
    Comprehensive scheduler monitoring and alerting system
    """
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.health_history: List[HealthCheckResult] = []
        self.max_alerts = 1000
        self.max_health_history = 100
        self.alert_handlers: List[Callable[[Alert], None]] = []
        self.monitoring_enabled = True
        self.last_health_check: Optional[datetime] = None
        
        # Performance thresholds
        self.thresholds = {
            "max_cycle_duration": 300,  # 5 minutes
            "max_failure_rate": 10,      # 10%
            "max_consecutive_failures": 3,
            "connection_pool_threshold": 80,  # 80% usage
        }
    
    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """Add custom alert handler"""
        self.alert_handlers.append(handler)
    
    def create_alert(self, alert_type: AlertType, severity: AlertSeverity, 
                    title: str, message: str, details: Dict[str, Any] = None) -> Alert:
        """Create and handle a new alert"""
        alert = Alert(
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            details=details or {}
        )
        
        self.alerts.append(alert)
        
        # Trim old alerts
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts:]
        
        # Call alert handlers
        if self.monitoring_enabled:
            for handler in self.alert_handlers:
                try:
                    handler(alert)
                except Exception as e:
                    logger.error(f"[SchedulerMonitor] Alert handler error: {e}")
        
        # Log alert
        log_level = {
            AlertSeverity.INFO: "info",
            AlertSeverity.WARNING: "warning", 
            AlertSeverity.ERROR: "error",
            AlertSeverity.CRITICAL: "critical"
        }.get(severity, "info")
        
        getattr(logger, log_level)(f"[SchedulerMonitor] {severity.value.upper()}: {title} - {message}")
        
        return alert
    
    def resolve_alert(self, alert_type: AlertType, title: str = None):
        """Resolve alerts by type and optionally title"""
        for alert in self.alerts:
            if alert.alert_type == alert_type and not alert.resolved:
                if title is None or alert.title == title:
                    alert.resolved = True
                    alert.resolved_at = datetime.now()
                    logger.info(f"[SchedulerMonitor] Resolved alert: {alert.title}")
    
    async def perform_health_check(self, scheduler_instance) -> HealthCheckResult:
        """Perform comprehensive health check"""
        if not self.monitoring_enabled:
            return HealthCheckResult(healthy=True)
        
        start_time = time.time()
        result = HealthCheckResult(healthy=True)
        
        try:
            # Check scheduler status
            result.checks["scheduler_running"] = await self._check_scheduler_status(scheduler_instance)
            
            # Check database connectivity
            result.checks["database_connectivity"] = await self._check_database_connectivity()
            
            # Check connection pool status
            result.checks["connection_pools"] = await self._check_connection_pools()
            
            # Check performance metrics
            result.checks["performance"] = await self._check_performance_metrics(scheduler_instance)
            
            # Check task execution
            result.checks["task_execution"] = await self._check_task_execution(scheduler_instance)
            
            # Overall health
            result.healthy = all(result.checks.values())
            
            # Get metrics
            result.metrics = await self._collect_metrics(scheduler_instance)
            
            # Generate alerts for failed checks
            if not result.healthy:
                await self._generate_health_alerts(result)
            
            self.last_health_check = datetime.now()
            
        except Exception as e:
            logger.error(f"[SchedulerMonitor] Health check failed: {e}")
            result.healthy = False
            result.checks["health_check_error"] = False
            
            self.create_alert(
                AlertType.HEALTH_CHECK_FAILED,
                AlertSeverity.ERROR,
                "Health Check Failed",
                f"Health check execution failed: {str(e)}",
                {"error": str(e), "duration": time.time() - start_time}
            )
        
        # Store in history
        self.health_history.append(result)
        if len(self.health_history) > self.max_health_history:
            self.health_history = self.health_history[-self.max_health_history:]
        
        duration = time.time() - start_time
        logger.info(f"[SchedulerMonitor] Health check completed in {duration:.2f}s - {'✅ Healthy' if result.healthy else '❌ Unhealthy'}")
        
        return result
    
    async def _check_scheduler_status(self, scheduler_instance) -> bool:
        """Check if scheduler is running properly"""
        try:
            if hasattr(scheduler_instance, 'status'):
                return scheduler_instance.status.value == "running"
            return True
        except Exception as e:
            logger.error(f"[SchedulerMonitor] Scheduler status check failed: {e}")
            return False
    
    async def _check_database_connectivity(self) -> bool:
        """Check database connectivity"""
        try:
            from services.database import get_db_session
            
            db = get_db_session()
            if not db:
                return False
            
            # Test basic query
            result = db.execute("SELECT 1").fetchone()
            db.close()
            
            return result is not None
        except Exception as e:
            logger.error(f"[SchedulerMonitor] Database connectivity check failed: {e}")
            return False
    
    async def _check_connection_pools(self) -> bool:
        """Check connection pool status"""
        try:
            from services.database import get_platform_engine, get_user_data_engine
            
            platform_engine = get_platform_engine()
            user_data_engine = get_user_data_engine()
            
            # Check pool status
            platform_pool = platform_engine.pool
            user_data_pool = user_data_engine.pool
            
            # Check if pools are over threshold
            platform_usage = (platform_pool.checkedout() / max(1, platform_pool.size())) * 100
            user_data_usage = (user_data_pool.checkedout() / max(1, user_data_pool.size())) * 100
            
            max_usage = max(platform_usage, user_data_usage)
            
            if max_usage > self.thresholds["connection_pool_threshold"]:
                self.create_alert(
                    AlertType.CONNECTION_EXHAUSTION,
                    AlertSeverity.WARNING,
                    "High Connection Pool Usage",
                    f"Connection pool usage at {max_usage:.1f}%",
                    {
                        "platform_usage": platform_usage,
                        "user_data_usage": user_data_usage,
                        "threshold": self.thresholds["connection_pool_threshold"]
                    }
                )
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"[SchedulerMonitor] Connection pool check failed: {e}")
            return False
    
    async def _check_performance_metrics(self, scheduler_instance) -> bool:
        """Check performance metrics"""
        try:
            if not hasattr(scheduler_instance, 'metrics'):
                return True
            
            metrics = scheduler_instance.metrics
            
            # Check cycle duration
            if metrics.last_cycle_duration > self.thresholds["max_cycle_duration"]:
                self.create_alert(
                    AlertType.PERFORMANCE_DEGRADATION,
                    AlertSeverity.WARNING,
                    "Slow Check Cycle",
                    f"Last cycle took {metrics.last_cycle_duration:.2f}s",
                    {
                        "duration": metrics.last_cycle_duration,
                        "threshold": self.thresholds["max_cycle_duration"]
                    }
                )
                return False
            
            # Check failure rate
            if metrics.total_cycles > 0:
                failure_rate = (metrics.failed_cycles / metrics.total_cycles) * 100
                if failure_rate > self.thresholds["max_failure_rate"]:
                    self.create_alert(
                        AlertType.PERFORMANCE_DEGRADATION,
                        AlertSeverity.ERROR,
                        "High Failure Rate",
                        f"Failure rate at {failure_rate:.1f}%",
                        {
                            "failure_rate": failure_rate,
                            "failed_cycles": metrics.failed_cycles,
                            "total_cycles": metrics.total_cycles,
                            "threshold": self.thresholds["max_failure_rate"]
                        }
                    )
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"[SchedulerMonitor] Performance check failed: {e}")
            return False
    
    async def _check_task_execution(self, scheduler_instance) -> bool:
        """Check task execution status"""
        try:
            # This would check if tasks are being executed properly
            # For now, return True as basic implementation
            return True
        except Exception as e:
            logger.error(f"[SchedulerMonitor] Task execution check failed: {e}")
            return False
    
    async def _collect_metrics(self, scheduler_instance) -> Dict[str, Any]:
        """Collect comprehensive metrics"""
        try:
            metrics = {}
            
            # Scheduler metrics
            if hasattr(scheduler_instance, 'get_status'):
                metrics["scheduler"] = scheduler_instance.get_status()
            
            # Database metrics
            try:
                from services.database import get_platform_engine, get_user_data_engine
                
                platform_engine = get_platform_engine()
                user_data_engine = get_user_data_engine()
                
                metrics["connection_pools"] = {
                    "platform": {
                        "size": platform_engine.pool.size(),
                        "checked_in": platform_engine.pool.checkedin(),
                        "checked_out": platform_engine.pool.checkedout(),
                        "overflow": platform_engine.pool.overflow(),
                        "invalid": platform_engine.pool.invalid()
                    },
                    "user_data": {
                        "size": user_data_engine.pool.size(),
                        "checked_in": user_data_engine.pool.checkedin(),
                        "checked_out": user_data_engine.pool.checkedout(),
                        "overflow": user_data_engine.pool.overflow(),
                        "invalid": user_data_engine.pool.invalid()
                    }
                }
            except Exception as e:
                logger.error(f"[SchedulerMonitor] Failed to collect database metrics: {e}")
            
            # System metrics
            metrics["system"] = {
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": (datetime.now() - scheduler_instance.start_time).total_seconds() if hasattr(scheduler_instance, 'start_time') and scheduler_instance.start_time else None
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"[SchedulerMonitor] Failed to collect metrics: {e}")
            return {}
    
    async def _generate_health_alerts(self, health_result: HealthCheckResult):
        """Generate alerts based on health check results"""
        for check_name, passed in health_result.checks.items():
            if not passed:
                self.create_alert(
                    AlertType.HEALTH_CHECK_FAILED,
                    AlertSeverity.WARNING,
                    f"Health Check Failed: {check_name}",
                    f"Health check '{check_name}' failed",
                    {
                        "check_name": check_name,
                        "health_result": health_result.__dict__
                    }
                )
    
    def get_active_alerts(self, severity: AlertSeverity = None) -> List[Alert]:
        """Get active (unresolved) alerts"""
        alerts = [alert for alert in self.alerts if not alert.resolved]
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        return alerts
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of all alerts"""
        active_alerts = self.get_active_alerts()
        
        return {
            "total_alerts": len(self.alerts),
            "active_alerts": len(active_alerts),
            "resolved_alerts": len(self.alerts) - len(active_alerts),
            "by_severity": {
                severity.value: len([a for a in active_alerts if a.severity == severity])
                for severity in AlertSeverity
            },
            "by_type": {
                alert_type.value: len([a for a in active_alerts if a.alert_type == alert_type])
                for alert_type in AlertType
            },
            "recent_alerts": [
                {
                    "type": alert.alert_type.value,
                    "severity": alert.severity.value,
                    "title": alert.title,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat()
                }
                for alert in sorted(active_alerts, key=lambda a: a.timestamp, reverse=True)[:10]
            ]
        }
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get summary of health check history"""
        if not self.health_history:
            return {"message": "No health checks performed yet"}
        
        recent_checks = self.health_history[-10:]  # Last 10 checks
        healthy_count = sum(1 for check in recent_checks if check.healthy)
        
        return {
            "total_checks": len(self.health_history),
            "recent_checks": len(recent_checks),
            "healthy_recent": healthy_count,
            "health_rate": (healthy_count / len(recent_checks)) * 100,
            "last_check": self.health_history[-1].timestamp.isoformat(),
            "last_healthy": self.health_history[-1].healthy,
            "checks_per_hour": self._calculate_checks_per_hour()
        }
    
    def _calculate_checks_per_hour(self) -> float:
        """Calculate health checks per hour"""
        if len(self.health_history) < 2:
            return 0.0
        
        time_span = self.health_history[-1].timestamp - self.health_history[0].timestamp
        hours = time_span.total_seconds() / 3600
        
        return len(self.health_history) / max(hours, 0.1)
    
    def enable_monitoring(self):
        """Enable monitoring"""
        self.monitoring_enabled = True
        logger.info("[SchedulerMonitor] Monitoring enabled")
    
    def disable_monitoring(self):
        """Disable monitoring"""
        self.monitoring_enabled = False
        logger.info("[SchedulerMonitor] Monitoring disabled")
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.clear()
        logger.info("[SchedulerMonitor] All alerts cleared")

# Global monitor instance
_scheduler_monitor: Optional[SchedulerMonitor] = None

def get_scheduler_monitor() -> SchedulerMonitor:
    """Get the global scheduler monitor instance"""
    global _scheduler_monitor
    if _scheduler_monitor is None:
        _scheduler_monitor = SchedulerMonitor()
    return _scheduler_monitor
