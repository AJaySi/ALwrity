from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from loguru import logger

from middleware.auth_middleware import get_current_user, get_current_user_with_query_token
from models.story_models import (
    StoryImageGenerationRequest,
    StoryImageGenerationResponse,
    StoryImageResult,
    RegenerateImageRequest,
    RegenerateImageResponse,
    StoryAudioGenerationRequest,
    StoryAudioGenerationResponse,
    StoryAudioResult,
    GenerateAIAudioRequest,
    GenerateAIAudioResponse,
    StoryScene,
)
from services.story_writer.image_generation_service import StoryImageGenerationService
from services.story_writer.audio_generation_service import StoryAudioGenerationService

from ..utils.auth import require_authenticated_user
from ..utils.media_utils import resolve_media_file


router = APIRouter()
image_service = StoryImageGenerationService()
audio_service = StoryAudioGenerationService()


@router.post("/generate-images", response_model=StoryImageGenerationResponse)
async def generate_scene_images(
    request: StoryImageGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> StoryImageGenerationResponse:
    """Generate images for story scenes."""
    try:
        user_id = require_authenticated_user(current_user)

        if not request.scenes or len(request.scenes) == 0:
            raise HTTPException(status_code=400, detail="At least one scene is required")

        logger.info(f"[StoryWriter] Generating images for {len(request.scenes)} scenes for user {user_id}")

        scenes_data = [scene.dict() if isinstance(scene, StoryScene) else scene for scene in request.scenes]
        image_results = image_service.generate_scene_images(
            scenes=scenes_data,
            user_id=user_id,
            provider=request.provider,
            width=request.width or 1024,
            height=request.height or 1024,
            model=request.model,
        )

        image_models: List[StoryImageResult] = [
            StoryImageResult(
                scene_number=result.get("scene_number", 0),
                scene_title=result.get("scene_title", "Untitled"),
                image_filename=result.get("image_filename", ""),
                image_url=result.get("image_url", ""),
                width=result.get("width", 1024),
                height=result.get("height", 1024),
                provider=result.get("provider", "unknown"),
                model=result.get("model"),
                seed=result.get("seed"),
                error=result.get("error"),
            )
            for result in image_results
        ]

        return StoryImageGenerationResponse(images=image_models, success=True)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to generate images: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/regenerate-images", response_model=RegenerateImageResponse)
async def regenerate_scene_image(
    request: RegenerateImageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> RegenerateImageResponse:
    """Regenerate a single scene image using a direct prompt (no AI prompt generation)."""
    try:
        user_id = require_authenticated_user(current_user)

        if not request.prompt or not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt is required")

        logger.info(
            f"[StoryWriter] Regenerating image for scene {request.scene_number} "
            f"({request.scene_title}) for user {user_id}"
        )

        result = image_service.regenerate_scene_image(
            scene_number=request.scene_number,
            scene_title=request.scene_title,
            prompt=request.prompt.strip(),
            user_id=user_id,
            provider=request.provider,
            width=request.width or 1024,
            height=request.height or 1024,
            model=request.model,
        )

        return RegenerateImageResponse(
            scene_number=result.get("scene_number", request.scene_number),
            scene_title=result.get("scene_title", request.scene_title),
            image_filename=result.get("image_filename", ""),
            image_url=result.get("image_url", ""),
            width=result.get("width", request.width or 1024),
            height=result.get("height", request.height or 1024),
            provider=result.get("provider", "unknown"),
            model=result.get("model"),
            seed=result.get("seed"),
            success=True,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to regenerate image: {exc}")
        return RegenerateImageResponse(
            scene_number=request.scene_number,
            scene_title=request.scene_title,
            image_filename="",
            image_url="",
            width=request.width or 1024,
            height=request.height or 1024,
            provider=request.provider or "unknown",
            success=False,
            error=str(exc),
        )


@router.get("/images/{image_filename}")
async def serve_scene_image(
    image_filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user_with_query_token),
):
    """Serve a generated story scene image.
    
    Supports authentication via Authorization header or token query parameter.
    Query parameter is useful for HTML elements like <img> that cannot send custom headers.
    """
    try:
        require_authenticated_user(current_user)
        image_path = resolve_media_file(image_service.output_dir, image_filename)
        return FileResponse(path=str(image_path), media_type="image/png", filename=image_filename)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to serve image: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/generate-audio", response_model=StoryAudioGenerationResponse)
async def generate_scene_audio(
    request: StoryAudioGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> StoryAudioGenerationResponse:
    """Generate audio narration for story scenes."""
    try:
        user_id = require_authenticated_user(current_user)

        if not request.scenes or len(request.scenes) == 0:
            raise HTTPException(status_code=400, detail="At least one scene is required")

        logger.info(f"[StoryWriter] Generating audio for {len(request.scenes)} scenes for user {user_id}")

        scenes_data = [scene.dict() if isinstance(scene, StoryScene) else scene for scene in request.scenes]
        audio_results = audio_service.generate_scene_audio_list(
            scenes=scenes_data,
            user_id=user_id,
            provider=request.provider or "gtts",
            lang=request.lang or "en",
            slow=request.slow or False,
            rate=request.rate or 150,
        )

        audio_models: List[StoryAudioResult] = []
        for result in audio_results:
            audio_models.append(
                StoryAudioResult(
                    scene_number=result.get("scene_number", 0),
                    scene_title=result.get("scene_title", "Untitled"),
                    audio_filename=result.get("audio_filename") or "",
                    audio_url=result.get("audio_url") or "",
                    provider=result.get("provider", "unknown"),
                    file_size=result.get("file_size", 0),
                    error=result.get("error"),
                )
            )

        return StoryAudioGenerationResponse(audio_files=audio_models, success=True)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to generate audio: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/generate-ai-audio", response_model=GenerateAIAudioResponse)
async def generate_ai_audio(
    request: GenerateAIAudioRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> GenerateAIAudioResponse:
    """Generate AI audio for a single scene using WaveSpeed Minimax Speech 02 HD."""
    try:
        user_id = require_authenticated_user(current_user)

        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text is required")

        logger.info(
            f"[StoryWriter] Generating AI audio for scene {request.scene_number} "
            f"({request.scene_title}) for user {user_id}"
        )

        result = audio_service.generate_ai_audio(
            scene_number=request.scene_number,
            scene_title=request.scene_title,
            text=request.text.strip(),
            user_id=user_id,
            voice_id=request.voice_id or "Wise_Woman",
            speed=request.speed or 1.0,
            volume=request.volume or 1.0,
            pitch=request.pitch or 0.0,
            emotion=request.emotion or "happy",
        )

        return GenerateAIAudioResponse(
            scene_number=result.get("scene_number", request.scene_number),
            scene_title=result.get("scene_title", request.scene_title),
            audio_filename=result.get("audio_filename", ""),
            audio_url=result.get("audio_url", ""),
            provider=result.get("provider", "wavespeed"),
            model=result.get("model", "minimax/speech-02-hd"),
            voice_id=result.get("voice_id", request.voice_id or "Wise_Woman"),
            text_length=result.get("text_length", len(request.text)),
            file_size=result.get("file_size", 0),
            cost=result.get("cost", 0.0),
            success=True,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to generate AI audio: {exc}")
        return GenerateAIAudioResponse(
            scene_number=request.scene_number,
            scene_title=request.scene_title,
            audio_filename="",
            audio_url="",
            provider="wavespeed",
            model="minimax/speech-02-hd",
            voice_id=request.voice_id or "Wise_Woman",
            text_length=len(request.text) if request.text else 0,
            file_size=0,
            cost=0.0,
            success=False,
            error=str(exc),
        )


@router.get("/audio/{audio_filename}")
async def serve_scene_audio(
    audio_filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Serve a generated story scene audio file."""
    try:
        require_authenticated_user(current_user)
        audio_path = resolve_media_file(audio_service.output_dir, audio_filename)
        return FileResponse(path=str(audio_path), media_type="audio/mpeg", filename=audio_filename)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to serve audio: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


