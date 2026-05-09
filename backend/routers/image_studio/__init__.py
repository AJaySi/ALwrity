"""Image Studio API router package.

Composed from modular sub-routers. Same prefix and tags as the original monolithic file.
"""

from ..image_studio_router import router as legacy_router
from .health import router as health_router
from .upscale import router as upscale_router
from .control import router as control_router
from .social import router as social_router
from .edit import router as edit_router
from .face_swap import router as face_swap_router

legacy_router.include_router(health_router)
legacy_router.include_router(upscale_router)
legacy_router.include_router(control_router)
legacy_router.include_router(social_router)
legacy_router.include_router(edit_router)
legacy_router.include_router(face_swap_router)

router = legacy_router

__all__ = ["router"]
