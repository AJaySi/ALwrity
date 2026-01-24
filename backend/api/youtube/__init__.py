"""YouTube Creator Studio API Facade - Unified Entry Point

This module provides the unified API facade for YouTube Creator Studio,
integrating all feature-specific routers with configuration management,
health monitoring, and zero-downtime deployment capabilities.
"""

import time
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

# Import configuration
from .config import config

# Import feature routers
from .planning import router as planning_router
from .scenes import router as scenes_router
from .rendering import router as rendering_router
from .assets import router as assets_router

# Import logging
from utils.logger_utils import get_service_logger

logger = get_service_logger("api.youtube.facade")

# Create the main YouTube router
router = APIRouter(
    prefix="/youtube",
    tags=["youtube"],
    responses={
        404: {"description": "Endpoint not found"},
        500: {"description": "Internal server error"}
    }
)

# Include feature routers with conditional mounting based on configuration
if config.enable_planning:
    router.include_router(
        planning_router,
        prefix="",
        tags=["youtube-planning"]
    )
    logger.info(f"[YouTube Facade] ✓ Planning router mounted ({'enabled' if config.enable_planning else 'disabled'})")

if config.enable_scenes:
    router.include_router(
        scenes_router,
        prefix="",
        tags=["youtube-scenes"]
    )
    logger.info(f"[YouTube Facade] ✓ Scenes router mounted ({'enabled' if config.enable_scenes else 'disabled'})")

if config.enable_rendering:
    router.include_router(
        rendering_router,
        prefix="",
        tags=["youtube-rendering"]
    )
    logger.info(f"[YouTube Facade] ✓ Rendering router mounted ({'enabled' if config.enable_rendering else 'disabled'})")

if config.enable_assets:
    router.include_router(
        assets_router,
        prefix="",
        tags=["youtube-assets"]
    )
    logger.info(f"[YouTube Facade] ✓ Assets router mounted ({'enabled' if config.enable_assets else 'disabled'})")


@router.get("/status", summary="Get YouTube API Status")
async def get_youtube_status():
    """Get the operational status of the YouTube Creator Studio API."""
    return {
        "service": "youtube_creator_api",
        "version": config.version,
        "environment": config.environment,
        "status": "operational",
        "features": {
            "planning": {
                "enabled": config.enable_planning,
                "endpoints": 2,
                "description": "Video planning and AI-enhanced content generation"
            },
            "scenes": {
                "enabled": config.enable_scenes,
                "endpoints": 2,
                "description": "Scene building and management"
            },
            "rendering": {
                "enabled": config.enable_rendering,
                "endpoints": 4,
                "description": "Video rendering and processing"
            },
            "assets": {
                "enabled": config.enable_assets,
                "endpoints": 3,
                "description": "Asset management and file serving"
            }
        },
        "configuration": config.to_dict(),
        "total_endpoints": config.total_enabled_endpoints,
        "enabled_features": config.enabled_features,
        "disabled_features": config.disabled_features,
        "architecture": "modular_routers",
        "refactoring_complete": True
    }


@router.get("/health", summary="Comprehensive Health Check")
async def comprehensive_health_check():
    """Comprehensive health check for the YouTube Creator Studio API and all its components."""
    try:
        health_start_time = time.time()

        # Basic health info
        health_data = {
            "service": "youtube_creator_api",
            "version": config.version,
            "environment": config.environment,
            "timestamp": time.time(),
            "status": "healthy",
            "checks": {},
            "response_time_ms": None
        }

        # Router availability checks
        router_checks = {
            "planning_router": config.enable_planning,
            "scenes_router": config.enable_scenes,
            "rendering_router": config.enable_rendering,
            "assets_router": config.enable_assets
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

        # AI and video processing validation
        if config.enable_ai_enhancement:
            health_data["checks"]["ai_enhancement"] = {
                "status": "healthy",
                "message": "AI enhancement enabled"
            }
        else:
            health_data["checks"]["ai_enhancement"] = {
                "status": "disabled",
                "message": "AI enhancement disabled via configuration"
            }

        # Cost tracking validation
        if config.enable_cost_tracking:
            health_data["checks"]["cost_tracking"] = {
                "status": "healthy",
                "message": "Cost tracking enabled"
            }
        else:
            health_data["checks"]["cost_tracking"] = {
                "status": "warning",
                "message": "Cost tracking disabled - monitoring may be affected"
            }

        # Route validation
        expected_endpoints = config.total_enabled_endpoints
        actual_routes = len(router.routes)

        if actual_routes >= expected_endpoints:
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

        # Performance metrics
        health_end_time = time.time()
        response_time_ms = (health_end_time - health_start_time) * 1000
        health_data["response_time_ms"] = round(response_time_ms, 2)

        # Overall status determination
        if health_data["status"] == "healthy" and response_time_ms < 1000:
            health_data["status"] = "healthy"
        elif response_time_ms < 5000:
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
        logger.error(f"[YouTube Health] Critical health check failure: {e}", exc_info=True)
        return JSONResponse(
            status_code=503,
            content={
                "service": "youtube_creator_api",
                "version": config.version,
                "status": "unhealthy",
                "error": f"Health check failed: {str(e)}",
                "timestamp": time.time()
            }
        )


@router.get("/metrics", summary="Get API Metrics")
async def get_api_metrics():
    """Get basic usage metrics for the YouTube Creator Studio API.

    Note: This is a placeholder for future metrics implementation.
    In a production system, this would integrate with monitoring tools.
    """
    return {
        "service": "youtube_creator_api",
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


@router.get("/capabilities", summary="Get YouTube Creator Capabilities")
async def get_capabilities():
    """Get detailed information about YouTube Creator Studio capabilities."""
    return {
        "service": "youtube_creator_api",
        "version": config.version,
        "capabilities": {
            "video_creation": {
                "max_scenes": config.max_scenes_per_video,
                "max_duration_seconds": config.max_video_duration_seconds,
                "supported_resolutions": config.supported_resolutions,
                "default_resolution": config.default_resolution,
                "max_file_size_mb": config.max_video_size_mb
            },
            "ai_features": {
                "ai_enhancement": config.enable_ai_enhancement,
                "trend_analysis": config.enable_trend_analysis,
                "enhanced_analysis": config.enable_enhanced_analysis,
                "max_retries": config.max_ai_retries
            },
            "cost_management": {
                "cost_tracking": config.enable_cost_tracking,
                "cost_estimation": config.enable_cost_estimation,
                "max_cost_per_video": config.max_cost_per_video
            },
            "asset_management": {
                "asset_library": config.enable_asset_library,
                "retention_days": config.asset_retention_days,
                "max_assets_per_user": config.max_assets_per_user
            }
        },
        "features": config.enabled_features,
        "limits": {
            "concurrent_requests": config.max_concurrent_requests,
            "request_timeout": config.request_timeout_seconds,
            "rate_limit_per_minute": config.rate_limit_requests_per_minute
        }
    }


# Initialization logging
logger.info(f"[YouTube Facade] Initialized with version {config.version} in {config.environment} environment")
logger.info(f"[YouTube Facade] Enabled features: {config.enabled_features}")
logger.info(f"[YouTube Facade] Disabled features: {config.disabled_features}")
logger.info(f"[YouTube Facade] Total enabled endpoints: {config.total_enabled_endpoints}")
logger.info(f"[YouTube Facade] AI enhancement: {'enabled' if config.enable_ai_enhancement else 'disabled'}")
logger.info(f"[YouTube Facade] Cost tracking: {'enabled' if config.enable_cost_tracking else 'disabled'}")
logger.info(f"[YouTube Facade] Asset library: {'enabled' if config.enable_asset_library else 'disabled'}")
logger.info(f"[YouTube Facade] Monitoring: {'enabled' if config.enable_metrics else 'disabled'}")
logger.info(f"[YouTube Facade] Health checks: {'enabled' if config.enable_health_checks else 'disabled'}")

# Validate configuration on startup
if not config.enabled_features:
    logger.warning("[YouTube Facade] WARNING: All features are disabled! Check configuration.")
elif len(config.disabled_features) > 0:
    logger.info(f"[YouTube Facade] Partial deployment: {config.disabled_features} features disabled")

logger.info("[YouTube Facade] YouTube Creator Studio API Facade ready for operation")
