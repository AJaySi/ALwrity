"""
Content Strategy Routes
Main router that includes all content strategy endpoint modules.
"""

from fastapi import APIRouter

# Import endpoint modules
from .endpoints.strategy_crud import router as crud_router
from .endpoints.analytics_endpoints import router as analytics_router
from .endpoints.utility_endpoints import router as utility_router
from .endpoints.streaming_endpoints import router as streaming_router
from .endpoints.autofill_endpoints import router as autofill_router
from .endpoints.ai_generation_endpoints import router as ai_generation_router

# Create main router
# Using /enhanced-strategies prefix for backward compatibility with frontend
router = APIRouter(prefix="/enhanced-strategies", tags=["Content Strategy"])

# Include all endpoint routers
# CRUD endpoints directly under /enhanced-strategies (backward compatibility)
router.include_router(crud_router, prefix="")
# Analytics endpoints under /enhanced-strategies/strategies/{id}/...
router.include_router(analytics_router, prefix="/strategies")
# Utility endpoints directly under /enhanced-strategies
router.include_router(utility_router, prefix="")
# Streaming endpoints directly under /enhanced-strategies
router.include_router(streaming_router, prefix="")
# Autofill endpoints under /enhanced-strategies/strategies/{id}/...
router.include_router(autofill_router, prefix="/strategies")
# AI generation endpoints under /enhanced-strategies/ai-generation
router.include_router(ai_generation_router, prefix="/ai-generation") 