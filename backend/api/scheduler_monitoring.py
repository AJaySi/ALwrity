"""
Scheduler Monitoring API Endpoints
Provides REST API for scheduler monitoring, management, and health checks
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger
import asyncio

from services.scheduler_monitor import get_scheduler_monitor, AlertSeverity, AlertType
from services.robust_scheduler import get_robust_scheduler, SchedulerStatus

router = APIRouter(prefix="/scheduler", tags=["scheduler"])

@router.get("/status")
async def get_scheduler_status():
    """Get comprehensive scheduler status"""
    try:
        scheduler = get_robust_scheduler()
        status = scheduler.get_status()
        
        return JSONResponse(content={
            "success": True,
            "data": status,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"[SchedulerAPI] Failed to get scheduler status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_scheduler_health():
    """Get scheduler health check results"""
    try:
        scheduler = get_robust_scheduler()
        monitor = get_scheduler_monitor()
        
        health_result = await monitor.perform_health_check(scheduler)
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "healthy": health_result.healthy,
                "checks": health_result.checks,
                "metrics": health_result.metrics,
                "timestamp": health_result.timestamp.isoformat()
            }
        })
    except Exception as e:
        logger.error(f"[SchedulerAPI] Failed to perform health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_scheduler_metrics():
    """Get detailed scheduler metrics"""
    try:
        scheduler = get_robust_scheduler()
        monitor = get_scheduler_monitor()
        
        # Get scheduler metrics
        scheduler_status = scheduler.get_status()
        
        # Get monitoring metrics
        monitor_metrics = await monitor._collect_metrics(scheduler)
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "scheduler": scheduler_status,
                "monitoring": monitor_metrics,
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"[SchedulerAPI] Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_alerts(severity: Optional[str] = None, active_only: bool = True):
    """Get scheduler alerts"""
    try:
        monitor = get_scheduler_monitor()
        
        # Parse severity
        alert_severity = None
        if severity:
            try:
                alert_severity = AlertSeverity(severity.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")
        
        # Get alerts
        if active_only:
            alerts = monitor.get_active_alerts(alert_severity)
        else:
            alerts = monitor.alerts
            if alert_severity:
                alerts = [a for a in alerts if a.severity == alert_severity]
        
        # Format alerts
        formatted_alerts = [
            {
                "id": id(alert),
                "type": alert.alert_type.value,
                "severity": alert.severity.value,
                "title": alert.title,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "resolved": alert.resolved,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                "details": alert.details
            }
            for alert in sorted(alerts, key=lambda a: a.timestamp, reverse=True)
        ]
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "alerts": formatted_alerts,
                "summary": monitor.get_alert_summary()
            }
        })
    except Exception as e:
        logger.error(f"[SchedulerAPI] Failed to get alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Resolve a specific alert"""
    try:
        monitor = get_scheduler_monitor()
        
        # Find alert by ID (simplified - in production, use proper alert IDs)
        for alert in monitor.alerts:
            if id(alert) == int(alert_id) and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                
                return JSONResponse(content={
                    "success": True,
                    "message": "Alert resolved successfully"
                })
        
        raise HTTPException(status_code=404, detail="Alert not found or already resolved")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid alert ID")
    except Exception as e:
        logger.error(f"[SchedulerAPI] Failed to resolve alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/resolve")
async def resolve_alerts_by_type(alert_type: str):
    """Resolve alerts by type"""
    try:
        monitor = get_scheduler_monitor()
        
        # Parse alert type
        try:
            alert_type_enum = AlertType(alert_type.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid alert type: {alert_type}")
        
        # Resolve alerts
        monitor.resolve_alert(alert_type_enum)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Resolved all {alert_type} alerts"
        })
    except Exception as e:
        logger.error(f"[SchedulerAPI] Failed to resolve alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health-summary")
async def get_health_summary():
    """Get health check summary"""
    try:
        monitor = get_scheduler_monitor()
        summary = monitor.get_health_summary()
        
        return JSONResponse(content={
            "success": True,
            "data": summary
        })
    except Exception as e:
        logger.error(f"[SchedulerAPI] Failed to get health summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start")
async def start_scheduler(background_tasks: BackgroundTasks):
    """Start the scheduler"""
    try:
        scheduler = get_robust_scheduler()
        
        if scheduler.status == SchedulerStatus.RUNNING:
            return JSONResponse(content={
                "success": True,
                "message": "Scheduler is already running"
            })
        
        # Start scheduler in background
        background_tasks.add_task(scheduler.start)
        
        return JSONResponse(content={
            "success": True,
            "message": "Scheduler start initiated"
        })
    except Exception as e:
        logger.error(f"[SchedulerAPI] Failed to start scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_scheduler(background_tasks: BackgroundTasks):
    """Stop the scheduler"""
    try:
        scheduler = get_robust_scheduler()
        
        if scheduler.status == SchedulerStatus.STOPPED:
            return JSONResponse(content={
                "success": True,
                "message": "Scheduler is already stopped"
            })
        
        # Stop scheduler in background
        background_tasks.add_task(scheduler.stop)
        
        return JSONResponse(content={
            "success": True,
            "message": "Scheduler stop initiated"
        })
    except Exception as e:
        logger.error(f"[SchedulerAPI] Failed to stop scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restart")
async def restart_scheduler(background_tasks: BackgroundTasks):
    """Restart the scheduler"""
    try:
        scheduler = get_robust_scheduler()
        
        # Stop and start in background
        async def restart():
            await scheduler.stop()
            await asyncio.sleep(2)  # Brief pause
            await scheduler.start()
        
        background_tasks.add_task(restart)
        
        return JSONResponse(content={
            "success": True,
            "message": "Scheduler restart initiated"
        })
    except Exception as e:
        logger.error(f"[SchedulerAPI] Failed to restart scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger-check-cycle")
async def trigger_check_cycle(background_tasks: BackgroundTasks):
    """Manually trigger a check cycle"""
    try:
        scheduler = get_robust_scheduler()
        
        if scheduler.status != SchedulerStatus.RUNNING:
            raise HTTPException(status_code=400, detail="Scheduler is not running")
        
        # Trigger check cycle in background
        background_tasks.add_task(scheduler._execute_check_cycle)
        
        return JSONResponse(content={
            "success": True,
            "message": "Check cycle triggered"
        })
    except Exception as e:
        logger.error(f"[SchedulerAPI] Failed to trigger check cycle: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/connection-pools")
async def get_connection_pool_status():
    """Get connection pool status"""
    try:
        from services.database import get_platform_engine, get_user_data_engine
        
        platform_engine = get_platform_engine()
        user_data_engine = get_user_data_engine()
        
        platform_pool = platform_engine.pool
        user_data_pool = user_data_engine.pool
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "platform": {
                    "size": platform_pool.size(),
                    "checked_in": platform_pool.checkedin(),
                    "checked_out": platform_pool.checkedout(),
                    "overflow": platform_pool.overflow(),
                    "invalid": platform_pool.invalid(),
                    "usage_percent": (platform_pool.checkedout() / max(1, platform_pool.size())) * 100
                },
                "user_data": {
                    "size": user_data_pool.size(),
                    "checked_in": user_data_pool.checkedin(),
                    "checked_out": user_data_pool.checkedout(),
                    "overflow": user_data_pool.overflow(),
                    "invalid": user_data_pool.invalid(),
                    "usage_percent": (user_data_pool.checkedout() / max(1, user_data_pool.size())) * 100
                },
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"[SchedulerAPI] Failed to get connection pool status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/monitoring/enable")
async def enable_monitoring():
    """Enable scheduler monitoring"""
    try:
        monitor = get_scheduler_monitor()
        monitor.enable_monitoring()
        
        return JSONResponse(content={
            "success": True,
            "message": "Monitoring enabled"
        })
    except Exception as e:
        logger.error(f"[SchedulerAPI] Failed to enable monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/monitoring/disable")
async def disable_monitoring():
    """Disable scheduler monitoring"""
    try:
        monitor = get_scheduler_monitor()
        monitor.disable_monitoring()
        
        return JSONResponse(content={
            "success": True,
            "message": "Monitoring disabled"
        })
    except Exception as e:
        logger.error(f"[SchedulerAPI] Failed to disable monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/clear")
async def clear_alerts():
    """Clear all alerts"""
    try:
        monitor = get_scheduler_monitor()
        monitor.clear_alerts()
        
        return JSONResponse(content={
            "success": True,
            "message": "All alerts cleared"
        })
    except Exception as e:
        logger.error(f"[SchedulerAPI] Failed to clear alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_dashboard_data():
    """Get comprehensive dashboard data"""
    try:
        scheduler = get_robust_scheduler()
        monitor = get_scheduler_monitor()
        
        # Get all data
        status = scheduler.get_status()
        health_result = await monitor.perform_health_check(scheduler)
        alerts = monitor.get_active_alerts()
        alert_summary = monitor.get_alert_summary()
        health_summary = monitor.get_health_summary()
        
        # Get connection pool status
        from services.database import get_platform_engine, get_user_data_engine
        platform_engine = get_platform_engine()
        user_data_engine = get_user_data_engine()
        
        connection_pools = {
            "platform": {
                "size": platform_engine.pool.size(),
                "checked_out": platform_engine.pool.checkedout(),
                "usage_percent": (platform_engine.pool.checkedout() / max(1, platform_engine.pool.size())) * 100
            },
            "user_data": {
                "size": user_data_engine.pool.size(),
                "checked_out": user_data_engine.pool.checkedout(),
                "usage_percent": (user_data_pool.checkedout() / max(1, user_data_pool.pool.size())) * 100
            }
        }
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "scheduler": status,
                "health": {
                    "healthy": health_result.healthy,
                    "checks": health_result.checks,
                    "summary": health_summary
                },
                "alerts": {
                    "active_count": len(alerts),
                    "summary": alert_summary,
                    "recent": [
                        {
                            "type": alert.alert_type.value,
                            "severity": alert.severity.value,
                            "title": alert.title,
                            "timestamp": alert.timestamp.isoformat()
                        }
                        for alert in sorted(alerts, key=lambda a: a.timestamp, reverse=True)[:5]
                    ]
                },
                "connection_pools": connection_pools,
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"[SchedulerAPI] Failed to get dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
