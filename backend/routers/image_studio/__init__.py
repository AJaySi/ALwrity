"""Image Studio API router package.

Composed from modular sub-routers. Same prefix and tags as the original monolithic file.
"""

from fastapi import APIRouter

from .health import router as health_router
from .upscale import router as upscale_router
from .control import router as control_router
from .social import router as social_router
from .edit import router as edit_router
from .face_swap import router as face_swap_router
from .create import router as create_router
from .transform import router as transform_router
from .compress import router as compress_router
from .convert import router as convert_router
from .save import router as save_router

router = APIRouter(prefix="/api/image-studio", tags=["image-studio"])

router.include_router(health_router)
router.include_router(upscale_router)
router.include_router(control_router)
router.include_router(social_router)
router.include_router(edit_router)
router.include_router(face_swap_router)
router.include_router(create_router)
router.include_router(transform_router)
router.include_router(compress_router)
router.include_router(convert_router)
router.include_router(save_router)

__all__ = ["router"]
