"""
Research API Router

Main router that imports and registers all handler modules.
Refactored for maintainability and extensibility.

Author: ALwrity Team
Version: 3.0
"""

from fastapi import APIRouter

# Import all handler routers
from .handlers import providers, research, intent, projects

# Create main router
router = APIRouter(prefix="/api/research", tags=["Research Engine"])

# Include all handler routers
router.include_router(providers.router)
router.include_router(research.router)
router.include_router(intent.router)
router.include_router(projects.router)
