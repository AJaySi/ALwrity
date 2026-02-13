from fastapi import APIRouter
from .handlers import avatar

router = APIRouter(prefix="/api/video-studio", tags=["Video Studio"])

router.include_router(avatar.router)
