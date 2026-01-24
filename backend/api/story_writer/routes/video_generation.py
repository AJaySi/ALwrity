from pathlib import Path
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from loguru import logger
from pydantic import BaseModel

from middleware.auth_middleware import get_current_user, get_current_user_with_query_token
from models.story_models import (
    StoryVideoGenerationRequest,
    StoryVideoGenerationResponse,
    StoryVideoResult,
    StoryScene,
    StoryGenerationRequest,
)
from services.story_writer.video_generation_service import StoryVideoGenerationService
from services.story_writer.image_generation_service import StoryImageGenerationService
from services.story_writer.audio_generation_service import StoryAudioGenerationService
from services.story_writer.story_service import StoryWriterService

from ..task_manager import task_manager
from ..utils.auth import require_authenticated_user
from ..utils.hd_video import (
    generate_hd_video_payload,
    generate_hd_video_scene_payload,
)
from ..utils.media_utils import resolve_media_file


router = APIRouter()
video_service = StoryVideoGenerationService()
image_service = StoryImageGenerationService()
audio_service = StoryAudioGenerationService()
story_service = StoryWriterService()


class HDVideoRequest(BaseModel):
    prompt: str
    provider: str = "huggingface"
    model: str | None = None
    num_frames: int | None = None
    guidance_scale: float | None = None
    num_inference_steps: int | None = None
    negative_prompt: str | None = None
    seed: int | None = None


class HDVideoSceneRequest(BaseModel):
    scene_number: int
    scene_data: Dict[str, Any]
    story_context: Dict[str, Any]
    all_scenes: List[Dict[str, Any]]
    provider: str = "huggingface"
    model: str | None = None
    num_frames: int | None = None
    guidance_scale: float | None = None
    num_inference_steps: int | None = None
    negative_prompt: str | None = None
    seed: int | None = None


@router.post("/generate-video", response_model=StoryVideoGenerationResponse)
async def generate_story_video(
    request: StoryVideoGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> StoryVideoGenerationResponse:
    """Generate a video from story scenes, images, and audio."""
    try:
        user_id = require_authenticated_user(current_user)

        if not request.scenes or len(request.scenes) == 0:
            raise HTTPException(status_code=400, detail="At least one scene is required")

        if len(request.scenes) != len(request.image_urls) or len(request.scenes) != len(request.audio_urls):
            raise HTTPException(
                status_code=400,
                detail="Number of scenes, image URLs, and audio URLs must match",
            )

        logger.info(f"[StoryWriter] Generating video for {len(request.scenes)} scenes for user {user_id}")

        scenes_data = [scene.dict() if isinstance(scene, StoryScene) else scene for scene in request.scenes]
        video_paths: List[Optional[str]] = []  # Animated videos (preferred)
        image_paths: List[Optional[str]] = []  # Static images (fallback)
        audio_paths: List[str] = []
        valid_scenes: List[Dict[str, Any]] = []

        # Resolve video/audio directories
        base_dir = Path(__file__).parent.parent.parent.parent
        ai_video_dir = (base_dir / "story_videos" / "AI_Videos").resolve()

        video_urls = request.video_urls or [None] * len(request.scenes)
        ai_audio_urls = request.ai_audio_urls or [None] * len(request.scenes)

        for idx, (scene, image_url, audio_url) in enumerate(zip(scenes_data, request.image_urls, request.audio_urls)):
            # Prefer animated video if available
            video_url = video_urls[idx] if idx < len(video_urls) else None
            video_path = None
            image_path = None

            if video_url:
                # Extract filename from animated video URL (e.g., /api/story/videos/ai/filename.mp4)
                video_filename = video_url.split("/")[-1].split("?")[0]
                video_path = ai_video_dir / video_filename
                if video_path.exists():
                    logger.info(f"[StoryWriter] Using animated video for scene {scene.get('scene_number', idx+1)}: {video_filename}")
                    video_paths.append(str(video_path))
                    image_paths.append(None)
                else:
                    logger.warning(f"[StoryWriter] Animated video not found: {video_path}, falling back to image")
                    video_paths.append(None)
                    video_path = None

            # Fall back to image if no animated video
            if not video_path:
                image_filename = image_url.split("/")[-1].split("?")[0]
                image_path = image_service.output_dir / image_filename
                if image_path.exists():
                    video_paths.append(None)
                    image_paths.append(str(image_path))
                else:
                    logger.warning(f"[StoryWriter] Image not found: {image_path} (from URL: {image_url})")
                    continue

            # Prefer AI audio if available, otherwise use free audio
            ai_audio_url = ai_audio_urls[idx] if idx < len(ai_audio_urls) else None
            audio_filename = None
            audio_path = None

            if ai_audio_url:
                audio_filename = ai_audio_url.split("/")[-1].split("?")[0]
                audio_path = audio_service.output_dir / audio_filename
                if audio_path.exists():
                    logger.info(f"[StoryWriter] Using AI audio for scene {scene.get('scene_number', idx+1)}: {audio_filename}")
                else:
                    logger.warning(f"[StoryWriter] AI audio not found: {audio_path}, falling back to free audio")
                    audio_path = None

            # Fall back to free audio if no AI audio
            if not audio_path:
                audio_filename = audio_url.split("/")[-1].split("?")[0]
                audio_path = audio_service.output_dir / audio_filename
                if not audio_path.exists():
                    logger.warning(f"[StoryWriter] Audio not found: {audio_path} (from URL: {audio_url})")
                    continue

            audio_paths.append(str(audio_path))
            valid_scenes.append(scene)

        if len(valid_scenes) == 0 or len(audio_paths) == 0:
            raise HTTPException(status_code=400, detail="No valid video/image or audio files were found")
        if len(valid_scenes) != len(audio_paths):
            raise HTTPException(
                status_code=400,
                detail="Number of valid scenes and audio files must match",
            )

        video_result = video_service.generate_story_video(
            scenes=valid_scenes,
            image_paths=image_paths,  # Can contain None for scenes with animated videos
            video_paths=video_paths,  # Can contain None for scenes with static images
            audio_paths=audio_paths,
            user_id=user_id,
            story_title=request.story_title or "Story",
            fps=request.fps or 24,
            transition_duration=request.transition_duration or 0.5,
        )

        video_model = StoryVideoResult(
            video_filename=video_result.get("video_filename", ""),
            video_url=video_result.get("video_url", ""),
            duration=video_result.get("duration", 0.0),
            fps=video_result.get("fps", 24),
            file_size=video_result.get("file_size", 0),
            num_scenes=video_result.get("num_scenes", 0),
            error=video_result.get("error"),
        )

        return StoryVideoGenerationResponse(video=video_model, success=True)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to generate video: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/generate-video-async", response_model=Dict[str, Any])
async def generate_story_video_async(
    request: StoryVideoGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Generate a video asynchronously with progress updates via task manager.
    Frontend can poll /api/story/task/{task_id}/status to show progress messages.
    """
    try:
        user_id = require_authenticated_user(current_user)

        if not request.scenes or len(request.scenes) == 0:
            raise HTTPException(status_code=400, detail="At least one scene is required")
        if len(request.scenes) != len(request.image_urls) or len(request.scenes) != len(request.audio_urls):
            raise HTTPException(
                status_code=400,
                detail="Number of scenes, image URLs, and audio URLs must match",
            )

        task_id = task_manager.create_task("story_video_generation")
        background_tasks.add_task(
            _execute_video_generation_task,
            task_id=task_id,
            request=request,
            user_id=user_id,
        )
        return {"task_id": task_id, "status": "pending", "message": "Video generation started"}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to start async video generation: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


def _execute_video_generation_task(task_id: str, request: StoryVideoGenerationRequest, user_id: str):
    """Background task to generate story video with progress mapped to task manager."""
    try:
        task_manager.update_task_status(task_id, "processing", progress=2.0, message="Initializing video generation...")

        scenes_data = [scene.dict() if isinstance(scene, StoryScene) else scene for scene in request.scenes]
        image_paths: List[str] = []
        audio_paths: List[str] = []
        valid_scenes: List[Dict[str, Any]] = []

        for scene, image_url, audio_url in zip(scenes_data, request.image_urls, request.audio_urls):
            image_filename = image_url.split("/")[-1].split("?")[0]
            audio_filename = audio_url.split("/")[-1].split("?")[0]
            image_path = image_service.output_dir / image_filename
            audio_path = audio_service.output_dir / audio_filename
            if not image_path.exists():
                logger.warning(f"[StoryWriter] Image not found: {image_path} (from URL: {image_url})")
                continue
            if not audio_path.exists():
                logger.warning(f"[StoryWriter] Audio not found: {audio_path} (from URL: {audio_url})")
                continue
            image_paths.append(str(image_path))
            audio_paths.append(str(audio_path))
            valid_scenes.append(scene)

        if not image_paths or not audio_paths or len(image_paths) != len(audio_paths):
            raise RuntimeError("No valid or mismatched image/audio assets for video generation.")

        def progress_callback(sub_progress: float, msg: str):
            overall = 5.0 + max(0.0, min(100.0, sub_progress)) * 0.9
            task_manager.update_task_status(task_id, "processing", progress=overall, message=msg)

        result = video_service.generate_story_video(
            scenes=valid_scenes,
            image_paths=image_paths,
            audio_paths=audio_paths,
            user_id=user_id,
            story_title=request.story_title or "Story",
            fps=request.fps or 24,
            transition_duration=request.transition_duration or 0.5,
            progress_callback=progress_callback,
        )

        task_manager.update_task_status(
            task_id,
            "completed",
            progress=100.0,
            message="Video generation complete!",
            result={"video": result, "success": True},
        )
    except Exception as exc:
        logger.error(f"[StoryWriter] Async video generation failed: {exc}", exc_info=True)
        task_manager.update_task_status(task_id, "failed", error=str(exc), message=f"Video generation failed: {exc}")


@router.post("/hd-video")
async def generate_hd_video(
    request: HDVideoRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        user_id = require_authenticated_user(current_user)
        return generate_hd_video_payload(request, user_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to generate HD video: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/hd-video-scene")
async def generate_hd_video_scene(
    request: HDVideoSceneRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        user_id = require_authenticated_user(current_user)
        return generate_hd_video_scene_payload(request, user_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to generate HD video for scene: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/generate-complete-video", response_model=Dict[str, Any])
async def generate_complete_story_video(
    request: StoryGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Generate a complete story video workflow asynchronously."""
    try:
        user_id = require_authenticated_user(current_user)
        logger.info(f"[StoryWriter] Starting complete video generation for user {user_id}")

        task_id = task_manager.create_task("complete_video_generation")
        background_tasks.add_task(
            execute_complete_video_generation,
            task_id=task_id,
            request_data=request.dict(),
            user_id=user_id,
        )

        return {
            "task_id": task_id,
            "status": "pending",
            "message": "Complete video generation started",
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to start complete video generation: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


def execute_complete_video_generation(
    task_id: str,
    request_data: Dict[str, Any],
    user_id: str,
):
    """
    Execute complete video generation workflow synchronously.
    Runs in a background task and performs blocking operations.
    """
    try:
        task_manager.update_task_status(task_id, "processing", progress=5.0, message="Starting complete video generation...")

        task_manager.update_task_status(task_id, "processing", progress=10.0, message="Generating story premise...")
        premise = story_service.generate_premise(
            persona=request_data["persona"],
            story_setting=request_data["story_setting"],
            character_input=request_data["character_input"],
            plot_elements=request_data["plot_elements"],
            writing_style=request_data["writing_style"],
            story_tone=request_data["story_tone"],
            narrative_pov=request_data["narrative_pov"],
            audience_age_group=request_data["audience_age_group"],
            content_rating=request_data["content_rating"],
            ending_preference=request_data["ending_preference"],
            user_id=user_id,
        )

        task_manager.update_task_status(task_id, "processing", progress=20.0, message="Generating structured outline with scenes...")
        outline_scenes = story_service.generate_outline(
            premise=premise,
            persona=request_data["persona"],
            story_setting=request_data["story_setting"],
            character_input=request_data["character_input"],
            plot_elements=request_data["plot_elements"],
            writing_style=request_data["writing_style"],
            story_tone=request_data["story_tone"],
            narrative_pov=request_data["narrative_pov"],
            audience_age_group=request_data["audience_age_group"],
            content_rating=request_data["content_rating"],
            ending_preference=request_data["ending_preference"],
            user_id=user_id,
            use_structured_output=True,
        )

        if not isinstance(outline_scenes, list):
            raise RuntimeError("Failed to generate structured outline")

        task_manager.update_task_status(task_id, "processing", progress=30.0, message="Generating images for scenes...")

        def image_progress_callback(sub_progress: float, message: str):
            overall_progress = 30.0 + (sub_progress * 0.2)
            task_manager.update_task_status(task_id, "processing", progress=overall_progress, message=message)

        image_results = image_service.generate_scene_images(
            scenes=outline_scenes,
            user_id=user_id,
            provider=request_data.get("image_provider"),
            width=request_data.get("image_width", 1024),
            height=request_data.get("image_height", 1024),
            model=request_data.get("image_model"),
            progress_callback=image_progress_callback,
        )

        task_manager.update_task_status(task_id, "processing", progress=50.0, message="Generating audio narration for scenes...")

        def audio_progress_callback(sub_progress: float, message: str):
            overall_progress = 50.0 + (sub_progress * 0.2)
            task_manager.update_task_status(task_id, "processing", progress=overall_progress, message=message)

        audio_results = audio_service.generate_scene_audio_list(
            scenes=outline_scenes,
            user_id=user_id,
            provider=request_data.get("audio_provider", "gtts"),
            lang=request_data.get("audio_lang", "en"),
            slow=request_data.get("audio_slow", False),
            rate=request_data.get("audio_rate", 150),
            progress_callback=audio_progress_callback,
        )

        task_manager.update_task_status(task_id, "processing", progress=70.0, message="Preparing video assets...")
        image_paths: List[str] = []
        audio_paths: List[str] = []
        valid_scenes: List[Dict[str, Any]] = []

        for scene in outline_scenes:
            scene_number = scene.get("scene_number", 0)
            image_result = next((img for img in image_results if img.get("scene_number") == scene_number), None)
            audio_result = next((aud for aud in audio_results if aud.get("scene_number") == scene_number), None)

            if image_result and audio_result and not image_result.get("error") and not audio_result.get("error"):
                image_path = image_result.get("image_path")
                audio_path = audio_result.get("audio_path")
                if image_path and audio_path:
                    image_paths.append(image_path)
                    audio_paths.append(audio_path)
                    valid_scenes.append(scene)

        if len(image_paths) == 0 or len(audio_paths) == 0:
            raise RuntimeError(
                f"No valid images or audio files were generated. Images: {len(image_paths)}, Audio: {len(audio_paths)}"
            )
        if len(image_paths) != len(audio_paths):
            raise RuntimeError(
                f"Mismatch between image and audio counts. Images: {len(image_paths)}, Audio: {len(audio_paths)}"
            )

        task_manager.update_task_status(task_id, "processing", progress=75.0, message="Composing video from scenes...")

        def video_progress_callback(sub_progress: float, message: str):
            overall_progress = 75.0 + (sub_progress * 0.2)
            task_manager.update_task_status(task_id, "processing", progress=overall_progress, message=message)

        video_result = video_service.generate_story_video(
            scenes=valid_scenes,
            image_paths=image_paths,
            audio_paths=audio_paths,
            user_id=user_id,
            story_title=request_data.get("story_setting", "Story")[:50],
            fps=request_data.get("video_fps", 24),
            transition_duration=request_data.get("video_transition_duration", 0.5),
            progress_callback=video_progress_callback,
        )

        result = {
            "premise": premise,
            "outline_scenes": outline_scenes,
            "images": image_results,
            "audio_files": audio_results,
            "video": video_result,
            "success": True,
        }

        task_manager.update_task_status(
            task_id,
            "completed",
            progress=100.0,
            message="Complete video generation finished!",
            result=result,
        )

        logger.info(f"[StoryWriter] Complete video generation task {task_id} completed successfully")

    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"[StoryWriter] Complete video generation task {task_id} failed: {error_msg}", exc_info=True)
        task_manager.update_task_status(
            task_id,
            "failed",
            error=error_msg,
            message=f"Complete video generation failed: {error_msg}",
        )


@router.get("/videos/{video_filename}")
async def serve_story_video(
    video_filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Serve a generated story video file."""
    try:
        require_authenticated_user(current_user)
        video_path = resolve_media_file(video_service.output_dir, video_filename)
        return FileResponse(path=str(video_path), media_type="video/mp4", filename=video_filename)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to serve video: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/videos/ai/{video_filename}")
async def serve_ai_story_video(
    video_filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Serve a generated AI scene animation video."""
    try:
        require_authenticated_user(current_user)

        base_dir = Path(__file__).parent.parent.parent.parent
        ai_video_dir = (base_dir / "story_videos" / "AI_Videos").resolve()
        video_service_ai = StoryVideoGenerationService(output_dir=str(ai_video_dir))
        video_path = resolve_media_file(video_service_ai.output_dir, video_filename)

        return FileResponse(
            path=str(video_path),
            media_type="video/mp4",
            filename=video_filename
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to serve AI video: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


