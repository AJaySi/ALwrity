"""Image Studio API - Unified Facade Router

This module serves as the main entry point for all Image Studio operations.
It provides a unified API facade that routes requests to specialized feature routers.

Architecture:
- Generation Router: Image creation, templates, providers (6 endpoints)
- Editing Router: Edit, upscale, control operations (7 endpoints)
- Advanced Router: Face swap, social, transform features (10 endpoints)
- Utilities Router: Compression, format conversion, health (10 endpoints)

Total: 33 endpoints across 4 specialized routers
"""

import os
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

# Import configuration and feature routers
from .image_studio_modules.config import config
from .image_studio_modules.generation import router as generation_router
from .image_studio_modules.editing import router as editing_router
from .image_studio_modules.advanced import router as advanced_router
from .image_studio_modules.utilities import router as utilities_router

from utils.logger_utils import get_service_logger

logger = get_service_logger("api.image_studio.facade")

# Initialize main router
router = APIRouter(
    prefix="/api/image-studio",
    tags=["image-studio"],
    responses={
        404: {"description": "Endpoint not found"},
        500: {"description": "Internal server error"}
    }
)

# Include feature routers with conditional mounting based on config
if config.enable_generation:
    router.include_router(
        generation_router,
        prefix="",
        tags=["generation"]
    )
    logger.info("[Image Studio Facade] ✓ Generation router mounted")

if config.enable_editing:
    router.include_router(
        editing_router,
        prefix="",
        tags=["editing"]
    )
    logger.info("[Image Studio Facade] ✓ Editing router mounted")

if config.enable_advanced:
    router.include_router(
        advanced_router,
        prefix="",
        tags=["advanced"]
    )
    logger.info("[Image Studio Facade] ✓ Advanced router mounted")

if config.enable_utilities:
    router.include_router(
        utilities_router,
        prefix="",
        tags=["utilities"]
    )
    logger.info("[Image Studio Facade] ✓ Utilities router mounted")


@router.get("/status", summary="Get Image Studio Status")
async def get_status():
    """Get the operational status of Image Studio modules."""
    return {
        "service": "image_studio",
        "version": config.version,
        "status": "operational",
        "environment": config.environment,
        "modules": {
            "generation": {
                "enabled": config.enable_generation,
                "endpoints": 6,
                "description": "Image creation, templates, providers"
            },
            "editing": {
                "enabled": config.enable_editing,
                "endpoints": 7,
                "description": "Edit, upscale, control operations"
            },
            "advanced": {
                "enabled": config.enable_advanced,
                "endpoints": 10,
                "description": "Face swap, social, transform features"
            },
            "utilities": {
                "enabled": config.enable_utilities,
                "endpoints": 10,
                "description": "Compression, format conversion, health"
            }
        },
        "total_endpoints": config.total_enabled_endpoints,
        "architecture": "modular_routers",
        "refactoring_complete": True
    }


@router.get("/health", summary="Health Check")
async def health_check():
    """Comprehensive health check for Image Studio.

    Returns:
        Health status with module information
    """
    try:
        # Check if all expected routers are mounted
        mounted_routers = []
        total_routes = len(router.routes)

        # Count routes by tag
        routes_by_tag = {}
        for route in router.routes:
            if hasattr(route, 'tags') and route.tags:
                tag = route.tags[0]
                routes_by_tag[tag] = routes_by_tag.get(tag, 0) + 1

        # Validate route counts
        expected_counts = {
            "generation": 6,
            "editing": 7,
            "advanced": 10,
            "utilities": 10
        }

        health_status = "healthy"
        issues = []

        for tag, expected_count in expected_counts.items():
            actual_count = routes_by_tag.get(tag, 0)
            if actual_count != expected_count:
                health_status = "degraded"
                issues.append(f"{tag}: expected {expected_count}, got {actual_count}")

        return {
            "status": health_status,
            "service": "image_studio",
            "version": config.version,
            "environment": config.environment,
            "total_routes": total_routes,
            "routes_by_module": routes_by_tag,
            "feature_flags": config.feature_flags,
            "configuration": config.to_dict(),
            "issues": issues if issues else None,
            "architecture": "modular_routers",
            "refactoring_status": "phase_3_complete"
        }

    except Exception as e:
        logger.error(f"[Health Check] ❌ Error: {e}", exc_info=True)
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "image_studio",
                "error": str(e),
                "version": "2.0.0"
            }
        )


@router.get("/metrics", summary="Get Usage Metrics")
async def get_metrics():
    """Get basic usage metrics for Image Studio.

    Note: This is a placeholder for future metrics implementation.
    """
    return {
        "service": "image_studio",
        "metrics_available": False,
        "note": "Metrics collection to be implemented in future release",
        "version": "2.0.0"
    }


# Note: Exception handlers are configured at the main FastAPI app level
# Individual router exception handlers are not supported


logger.info("[Image Studio Facade] Initialized with modular router architecture")
logger.info(f"[Image Studio Facade] Total routes: {len(router.routes)}")
logger.info(f"[Image Studio Facade] Environment: {config.environment}")
logger.info(f"[Image Studio Facade] Enabled endpoints: {config.total_enabled_endpoints}")
logger.info(f"[Image Studio Facade] Feature flags: {config.feature_flags}")
