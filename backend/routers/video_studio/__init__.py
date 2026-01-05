"""
Video Studio Router

Provides AI video generation capabilities including:
- Text-to-video generation
- Image-to-video transformation
- Avatar/face generation
- Video enhancement and editing

Uses WaveSpeed AI models for high-quality video generation.
"""

from fastapi import APIRouter

from .endpoints import create, avatar, enhance, extend, transform, models, serve, tasks, prompt, social, face_swap, video_translate, video_background_remover, add_audio_to_video, edit

# Create main router
router = APIRouter(
    prefix="/video-studio",
    tags=["video-studio"],
    responses={404: {"description": "Not found"}},
)

# Include all endpoint routers
router.include_router(create.router)
router.include_router(avatar.router)
router.include_router(enhance.router)
router.include_router(extend.router)
router.include_router(transform.router)
router.include_router(social.router)
router.include_router(face_swap.router)
router.include_router(video_translate.router)
router.include_router(video_background_remover.router)
router.include_router(add_audio_to_video.router)
router.include_router(edit.router)
router.include_router(models.router)
router.include_router(serve.router)
router.include_router(tasks.router)
router.include_router(prompt.router)