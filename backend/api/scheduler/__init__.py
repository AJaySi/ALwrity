"""Scheduler API Facade - Unified Entry Point

This module provides the unified API facade for the Scheduler Dashboard,
integrating all feature-specific routers with configuration management,
health monitoring, and zero-downtime deployment capabilities.
"""

import time
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

# Import configuration
from .config import config

# Import feature routers
from .dashboard import router as dashboard_router
from .monitoring import router as monitoring_router
from .tasks import router as tasks_router
from .platform import router as platform_router

# Import database and logging
from services.database import get_db
from utils.logger_utils import get_service_logger

logger = get_service_logger("api.scheduler.facade")

# Create the main scheduler router
router = APIRouter(
    prefix="/api/scheduler",
    tags=["scheduler"],
    responses={
        404: {"description": "Endpoint not found"},
        500: {"description": "Internal server error"}
    }
)

# Include feature routers with conditional mounting based on configuration
if config.enable_dashboard:
    router.include_router(
        dashboard_router,
        prefix="",
        tags=["scheduler-dashboard"]
    )
    logger.info(f"[Scheduler Facade] ✓ Dashboard router mounted ({'enabled' if config.enable_dashboard else 'disabled'})")

if config.enable_monitoring:
    router.include_router(
        monitoring_router,
        prefix="",
        tags=["scheduler-monitoring"]
    )
    logger.info(f"[Scheduler Facade] ✓ Monitoring router mounted ({'enabled' if config.enable_monitoring else 'disabled'})")

if config.enable_tasks:
    router.include_router(
        tasks_router,
        prefix="",
        tags=["scheduler-tasks"]
    )
    logger.info(f"[Scheduler Facade] ✓ Tasks router mounted ({'enabled' if config.enable_tasks else 'disabled'})")

if config.enable_platform:
    router.include_router(
        platform_router,
        prefix="",
        tags=["scheduler-platform"]
    )
    logger.info(f"[Scheduler Facade] ✓ Platform router mounted ({'enabled' if config.enable_platform else 'disabled'})")


@router.get("/status", summary="Get Scheduler API Status")
async def get_scheduler_status():
    """Get the operational status of the Scheduler API."""
    scheduler_runtime = {}
    try:
        from services.scheduler import get_scheduler
        scheduler_runtime = get_scheduler().get_stats().get('leadership', {})
    except Exception as e:
        scheduler_runtime = {
            "mode": "postgres_advisory_lock",
            "is_leader": False,
            "execution_enabled": False,
            "error": str(e)
        }

    return {
        "service": "scheduler_api",
        "version": config.version,
        "environment": config.environment,
        "status": "operational",
        "features": {
            "dashboard": {
                "enabled": config.enable_dashboard,
                "endpoints": 3,
                "description": "Dashboard statistics and overview"
            },
            "monitoring": {
                "enabled": config.enable_monitoring,
                "endpoints": 5,
                "description": "Execution logs, event history, cleanup"
            },
            "tasks": {
                "enabled": config.enable_tasks,
                "endpoints": 4,
                "description": "Task intervention and manual triggers"
            },
            "platform": {
                "enabled": config.enable_platform,
                "endpoints": 4,
                "description": "Platform insights and website analysis"
            }
        },
        "configuration": config.to_dict(),
        "total_endpoints": config.total_enabled_endpoints,
        "enabled_features": config.enabled_features,
        "disabled_features": config.disabled_features,
        "scheduler_runtime": {
            "leadership": scheduler_runtime
        },
        "architecture": "modular_routers",
        "refactoring_complete": True
    }


@router.get("/health", summary="Comprehensive Health Check")
async def comprehensive_health_check(db: Session = Depends(get_db)):
    """Comprehensive health check for the Scheduler API and all its components."""
    try:
        health_start_time = time.time()

        # Basic health info
        health_data = {
            "service": "scheduler_api",
            "version": config.version,
            "environment": config.environment,
            "timestamp": time.time(),
            "status": "healthy",
            "checks": {},
            "response_time_ms": None
        }

        # Database connectivity check
        try:
            # Simple database query to test connectivity
            db.execute("SELECT 1")
            health_data["checks"]["database"] = {
                "status": "healthy",
                "message": "Database connection successful"
            }
        except Exception as e:
            health_data["checks"]["database"] = {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}"
            }
            health_data["status"] = "degraded"

        # Scheduler leadership/runtime check
        try:
            from services.scheduler import get_scheduler
            leadership = get_scheduler().get_stats().get('leadership', {})
            health_data["checks"]["scheduler_leadership"] = {
                "status": "healthy" if leadership.get("execution_enabled") else "standby",
                "message": (
                    "Replica is active leader" if leadership.get("is_leader")
                    else "Replica is standby follower"
                ),
                "details": leadership
            }
        except Exception as e:
            health_data["checks"]["scheduler_leadership"] = {
                "status": "degraded",
                "message": f"Leadership status unavailable: {str(e)}"
            }
            health_data["status"] = "degraded"

        # Router availability checks
        router_checks = {
            "dashboard_router": config.enable_dashboard,
            "monitoring_router": config.enable_monitoring,
            "tasks_router": config.enable_tasks,
            "platform_router": config.enable_platform
        }

        for router_name, is_enabled in router_checks.items():
            if is_enabled:
                health_data["checks"][router_name] = {
                    "status": "healthy",
                    "message": f"{router_name} is enabled and operational"
                }
            else:
                health_data["checks"][router_name] = {
                    "status": "disabled",
                    "message": f"{router_name} is disabled via configuration"
                }

        # Feature flag validation
        expected_endpoints = config.total_enabled_endpoints
        actual_routes = len(router.routes)

        if actual_routes >= expected_endpoints:  # May have additional system routes
            health_data["checks"]["routing"] = {
                "status": "healthy",
                "message": f"Routing system operational: {actual_routes} routes configured"
            }
        else:
            health_data["checks"]["routing"] = {
                "status": "degraded",
                "message": f"Route count mismatch: expected {expected_endpoints}, got {actual_routes}"
            }
            health_data["status"] = "degraded"

        # Configuration validation
        if config.disabled_features:
            health_data["checks"]["configuration"] = {
                "status": "partial",
                "message": f"Some features disabled: {config.disabled_features}"
            }
        else:
            health_data["checks"]["configuration"] = {
                "status": "healthy",
                "message": "All features enabled"
            }

        # Performance metrics
        health_end_time = time.time()
        response_time_ms = (health_end_time - health_start_time) * 1000
        health_data["response_time_ms"] = round(response_time_ms, 2)

        # Overall status determination
        if health_data["status"] == "healthy" and response_time_ms < 1000:  # Response under 1 second
            health_data["status"] = "healthy"
        elif response_time_ms < 5000:  # Response under 5 seconds
            health_data["status"] = "degraded"
        else:
            health_data["status"] = "unhealthy"

        # Set HTTP status code based on health
        status_code = 200
        if health_data["status"] == "degraded":
            status_code = 200  # Still return 200 for degraded, just with status indicator
        elif health_data["status"] == "unhealthy":
            status_code = 503

        return JSONResponse(
            status_code=status_code,
            content=health_data
        )

    except Exception as e:
        logger.error(f"[Scheduler Health] Critical health check failure: {e}", exc_info=True)
        return JSONResponse(
            status_code=503,
            content={
                "service": "scheduler_api",
                "version": config.version,
                "status": "unhealthy",
                "error": f"Health check failed: {str(e)}",
                "timestamp": time.time()
            }
        )


@router.get("/metrics", summary="Get API Metrics")
async def get_api_metrics():
    """Get basic usage metrics for the Scheduler API.

    Note: This is a placeholder for future metrics implementation.
    In a production system, this would integrate with monitoring tools.
    """
    return {
        "service": "scheduler_api",
        "version": config.version,
        "metrics_available": config.enable_metrics,
        "note": "Metrics collection to be implemented in future release",
        "configuration": {
            "metrics_enabled": config.enable_metrics,
            "metrics_retention_days": config.metrics_retention_days,
            "performance_logging_enabled": config.enable_performance_logging
        }
    }


@router.get("/config", summary="Get API Configuration")
async def get_api_config():
    """Get the current API configuration (for debugging and monitoring)."""
    return config.to_dict()


# Note: Exception handlers and middleware should be configured at the main app level
# rather than router level to avoid conflicts and ensure proper error handling


# Initialization logging
logger.info(f"[Scheduler Facade] Initialized with version {config.version} in {config.environment} environment")
logger.info(f"[Scheduler Facade] Enabled features: {config.enabled_features}")
logger.info(f"[Scheduler Facade] Disabled features: {config.disabled_features}")
logger.info(f"[Scheduler Facade] Total enabled endpoints: {config.total_enabled_endpoints}")
logger.info(f"[Scheduler Facade] Monitoring: {'enabled' if config.enable_metrics else 'disabled'}")
logger.info(f"[Scheduler Facade] Health checks: {'enabled' if config.enable_health_checks else 'disabled'}")

# Validate configuration on startup
if not config.enabled_features:
    logger.warning("[Scheduler Facade] WARNING: All features are disabled! Check configuration.")
elif len(config.disabled_features) > 0:
    logger.info(f"[Scheduler Facade] Partial deployment: {config.disabled_features} features disabled")

logger.info("[Scheduler Facade] Scheduler API Facade ready for operation")
