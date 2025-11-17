"""
Story Writer API Router

Main router for story generation operations including premise, outline,
content generation, and full story creation.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Any, Dict, Union, List, Optional
from loguru import logger
from middleware.auth_middleware import get_current_user

from models.story_models import (
    StoryGenerationRequest,
    StorySetupGenerationRequest,
    StorySetupGenerationResponse,
    StorySetupOption,
    StoryStartRequest,
    StoryPremiseResponse,
    StoryOutlineResponse,
    StoryScene,
    StoryContentResponse,
    StoryFullGenerationResponse,
    StoryContinueRequest,
    StoryContinueResponse,
    StoryImageGenerationRequest,
    StoryImageGenerationResponse,
    StoryImageResult,
    StoryAudioGenerationRequest,
    StoryAudioGenerationResponse,
    StoryAudioResult,
    StoryVideoGenerationRequest,
    StoryVideoGenerationResponse,
    StoryVideoResult,
    TaskStatus,
)
from services.story_writer.story_service import StoryWriterService
from .task_manager import task_manager
from .cache_manager import cache_manager
from uuid import uuid4
from pydantic import BaseModel
from pathlib import Path

from .utils.auth import require_authenticated_user
from .utils.media_utils import resolve_media_file
from .utils.hd_video import (
    generate_hd_video_payload,
    generate_hd_video_scene_payload,
)


router = APIRouter(prefix="/api/story", tags=["Story Writer"])

service = StoryWriterService()


@router.get("/health")
async def health() -> Dict[str, Any]:
    """Health check endpoint."""
    return {"status": "ok", "service": "story_writer"}


# ---------------------------
# Story Setup Generation Endpoints
# ---------------------------

@router.post("/generate-setup", response_model=StorySetupGenerationResponse)
async def generate_story_setup(
    request: StorySetupGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> StorySetupGenerationResponse:
    """Generate 3 story setup options from a user's story idea."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID in authentication token")
        
        if not request.story_idea or not request.story_idea.strip():
            raise HTTPException(status_code=400, detail="Story idea is required")
        
        logger.info(f"[StoryWriter] Generating story setup options for user {user_id}")
        
        options = service.generate_story_setup_options(
            story_idea=request.story_idea,
            user_id=user_id
        )
        
        # Convert dict options to StorySetupOption models
        setup_options = [StorySetupOption(**option) for option in options]
        
        return StorySetupGenerationResponse(options=setup_options, success=True)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[StoryWriter] Failed to generate story setup options: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# Premise Generation Endpoints
# ---------------------------

@router.post("/generate-premise", response_model=StoryPremiseResponse)
async def generate_premise(
    request: StoryGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> StoryPremiseResponse:
    """Generate a story premise."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID in authentication token")
        
        logger.info(f"[StoryWriter] Generating premise for user {user_id}")
        
        premise = service.generate_premise(
            persona=request.persona,
            story_setting=request.story_setting,
            character_input=request.character_input,
            plot_elements=request.plot_elements,
            writing_style=request.writing_style,
            story_tone=request.story_tone,
            narrative_pov=request.narrative_pov,
            audience_age_group=request.audience_age_group,
            content_rating=request.content_rating,
            ending_preference=request.ending_preference,
            user_id=user_id
        )
        
        return StoryPremiseResponse(premise=premise, success=True)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[StoryWriter] Failed to generate premise: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# Outline Generation Endpoints
# ---------------------------

@router.post("/generate-outline", response_model=StoryOutlineResponse)
async def generate_outline(
    request: StoryStartRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    use_structured: bool = True
) -> StoryOutlineResponse:
    """Generate a story outline from a premise."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID in authentication token")
        
        if not request.premise or not request.premise.strip():
            raise HTTPException(status_code=400, detail="Premise is required")
        
        logger.info(f"[StoryWriter] Generating outline for user {user_id} (structured={use_structured})")
        logger.info(f"[StoryWriter] Outline generation parameters: audience_age_group={request.audience_age_group}, writing_style={request.writing_style}, story_tone={request.story_tone}")
        
        outline = service.generate_outline(
            premise=request.premise,
            persona=request.persona,
            story_setting=request.story_setting,
            character_input=request.character_input,
            plot_elements=request.plot_elements,
            writing_style=request.writing_style,
            story_tone=request.story_tone,
            narrative_pov=request.narrative_pov,
            audience_age_group=request.audience_age_group,
            content_rating=request.content_rating,
            ending_preference=request.ending_preference,
            user_id=user_id,
            use_structured_output=use_structured
        )
        
        # Check if outline is structured (list of scenes) or plain text
        is_structured = isinstance(outline, list)
        
        if is_structured:
            # Convert dict scenes to StoryScene models
            scenes = [StoryScene(**scene) if isinstance(scene, dict) else scene for scene in outline]
            return StoryOutlineResponse(outline=scenes, success=True, is_structured=True)
        else:
            # Plain text outline
            return StoryOutlineResponse(outline=str(outline), success=True, is_structured=False)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[StoryWriter] Failed to generate outline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# Story Content Generation Endpoints
# ---------------------------

@router.post("/generate-start", response_model=StoryContentResponse)
async def generate_story_start(
    request: StoryStartRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> StoryContentResponse:
    """Generate the starting section of a story."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID in authentication token")
        
        if not request.premise or not request.premise.strip():
            raise HTTPException(status_code=400, detail="Premise is required")
        if not request.outline or (isinstance(request.outline, str) and not request.outline.strip()):
            raise HTTPException(status_code=400, detail="Outline is required")
        
        logger.info(f"[StoryWriter] Generating story start for user {user_id}")
        
        # Handle outline - could be string or list (structured scenes)
        outline_data = request.outline
        # Convert StoryScene models to dicts if needed
        if isinstance(outline_data, list) and len(outline_data) > 0:
            if isinstance(outline_data[0], StoryScene):
                outline_data = [scene.dict() for scene in outline_data]
        
        story_length = getattr(request, 'story_length', 'Medium')
        story_start = service.generate_story_start(
            premise=request.premise,
            outline=outline_data,
            persona=request.persona,
            story_setting=request.story_setting,
            character_input=request.character_input,
            plot_elements=request.plot_elements,
            writing_style=request.writing_style,
            story_tone=request.story_tone,
            narrative_pov=request.narrative_pov,
            audience_age_group=request.audience_age_group,
            content_rating=request.content_rating,
            ending_preference=request.ending_preference,
            story_length=story_length,
            user_id=user_id
        )
        
        # Check if this is a short story - if so, mark as complete immediately
        story_length_lower = story_length.lower()
        is_short_story = "short" in story_length_lower or "1000" in story_length_lower
        
        # For short stories, check word count to verify completeness
        is_complete = False
        if is_short_story:
            word_count = len(story_start.split()) if story_start else 0
            # Short story should be ~1000 words (900-1100 acceptable range)
            if word_count >= 900:
                is_complete = True
                logger.info(f"[StoryWriter] Short story generated with {word_count} words. Marking as complete.")
            else:
                logger.warning(f"[StoryWriter] Short story generated with only {word_count} words. May need continuation.")
        
        # Format outline for response (convert list to string if needed)
        outline_response = outline_data
        if isinstance(outline_data, list):
            # Format structured outline as readable text
            outline_response = "\n".join([
                f"Scene {scene.get('scene_number', i+1) if isinstance(scene, dict) else getattr(scene, 'scene_number', i+1)}: "
                f"{scene.get('title', 'Untitled') if isinstance(scene, dict) else getattr(scene, 'title', 'Untitled')}\n"
                f"  {scene.get('description', '') if isinstance(scene, dict) else getattr(scene, 'description', '')}"
                for i, scene in enumerate(outline_data)
            ])
        
        return StoryContentResponse(
            story=story_start,
            premise=request.premise,
            outline=str(outline_response),
            is_complete=is_complete,  # True for short stories that are complete, False for medium/long
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[StoryWriter] Failed to generate story start: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/continue", response_model=StoryContinueResponse)
async def continue_story(
    request: StoryContinueRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> StoryContinueResponse:
    """Continue writing a story."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID in authentication token")
        
        if not request.story_text or not request.story_text.strip():
            raise HTTPException(status_code=400, detail="Story text is required")
        
        logger.info(f"[StoryWriter] Continuing story for user {user_id}")
        
        # Handle outline - could be string or list (structured scenes)
        outline_data = request.outline
        # Convert StoryScene models to dicts if needed
        if isinstance(outline_data, list) and len(outline_data) > 0:
            if isinstance(outline_data[0], StoryScene):
                outline_data = [scene.dict() for scene in outline_data]
        
        # Check word count before continuing
        story_length = getattr(request, 'story_length', 'Medium')
        story_length_lower = story_length.lower()
        is_short_story = "short" in story_length_lower or "1000" in story_length_lower
        
        # Block continuation for short stories - they should be complete in one call
        if is_short_story:
            logger.warning(f"[StoryWriter] Attempted to continue a short story. Short stories should be complete in one call.")
            raise HTTPException(
                status_code=400,
                detail="Short stories are generated in a single call and should be complete. If the story is incomplete, please regenerate it from the beginning."
            )
        
        current_word_count = len(request.story_text.split()) if request.story_text else 0
        
        # Determine target word count based on story length (with 5% buffer)
        # Medium: <5000 words (target ~4500, buffer ~4725)
        # Long: around 10000 words (target ~10000, buffer ~10500)
        if "long" in story_length_lower or "10000" in story_length_lower:
            target_total_words = 10000
            buffer_target = int(10000 * 1.05)  # 10500 words maximum
        else:
            # Medium story: <5000 words
            target_total_words = 4500  # Target for medium stories
            buffer_target = int(4500 * 1.05)  # ~4725 words maximum
        
        # If target is already reached or exceeded, return completion immediately
        if current_word_count >= buffer_target:
            logger.info(f"[StoryWriter] Word count ({current_word_count}) already at or past buffer target ({buffer_target}) for {story_length} story. Story is complete.")
            return StoryContinueResponse(
                continuation="IAMDONE",
                is_complete=True,
                success=True
            )
        
        # Also check if we're very close to target (within 50 words)
        if current_word_count >= target_total_words and (current_word_count - target_total_words) < 50:
            logger.info(f"[StoryWriter] Word count ({current_word_count}) is very close to target ({target_total_words}). Story is complete.")
            return StoryContinueResponse(
                continuation="IAMDONE",
                is_complete=True,
                success=True
            )
        
        continuation = service.continue_story(
            premise=request.premise,
            outline=outline_data,
            story_text=request.story_text,
            persona=request.persona,
            story_setting=request.story_setting,
            character_input=request.character_input,
            plot_elements=request.plot_elements,
            writing_style=request.writing_style,
            story_tone=request.story_tone,
            narrative_pov=request.narrative_pov,
            audience_age_group=request.audience_age_group,
            content_rating=request.content_rating,
            ending_preference=request.ending_preference,
            story_length=story_length,
            user_id=user_id
        )
        
        # Check if continuation is IAMDONE or if word count now exceeds target
        is_complete = 'IAMDONE' in continuation.upper()
        
        # Also check word count after continuation
        if not is_complete and continuation:
            # Estimate new word count
            new_story_text = request.story_text + '\n\n' + continuation
            new_word_count = len(new_story_text.split())
            
            # Calculate buffer target
            buffer_target = int(target_total_words * 1.05)
            
            # If new word count exceeds buffer target, mark as complete
            if new_word_count >= buffer_target:
                logger.info(f"[StoryWriter] Word count ({new_word_count}) now exceeds buffer target ({buffer_target}). Story is complete.")
                # Append IAMDONE if not already present
                if 'IAMDONE' not in continuation.upper():
                    continuation = continuation.rstrip() + '\n\nIAMDONE'
                is_complete = True
            # Also check if we're at or very close to target
            elif new_word_count >= target_total_words and (new_word_count - target_total_words) < 100:
                logger.info(f"[StoryWriter] Word count ({new_word_count}) is at or very close to target ({target_total_words}). Story is complete.")
                if 'IAMDONE' not in continuation.upper():
                    continuation = continuation.rstrip() + '\n\nIAMDONE'
                is_complete = True
        
        return StoryContinueResponse(
            continuation=continuation,
            is_complete=is_complete,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[StoryWriter] Failed to continue story: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# Full Story Generation Endpoints (Async)
# ---------------------------

@router.post("/generate-full", response_model=Dict[str, Any])
async def generate_full_story(
    request: StoryGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    max_iterations: int = 10
) -> Dict[str, Any]:
    """Generate a complete story asynchronously."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID in authentication token")
        
        # Check cache first
        cache_key = cache_manager.get_cache_key(request.dict())
        cached_result = cache_manager.get_cached_result(cache_key)
        if cached_result:
            logger.info(f"[StoryWriter] Returning cached result for user {user_id}")
            task_id = task_manager.create_task("story_generation")
            task_manager.update_task_status(
                task_id,
                "completed",
                progress=100.0,
                result=cached_result,
                message="Returned cached result"
            )
            return {"task_id": task_id, "cached": True}
        
        # Create task
        task_id = task_manager.create_task("story_generation")
        
        # Prepare request data
        request_data = request.dict()
        request_data["max_iterations"] = max_iterations
        
        # Execute task in background
        background_tasks.add_task(
            task_manager.execute_story_generation_task,
            task_id=task_id,
            request_data=request_data,
            user_id=user_id
        )
        
        logger.info(f"[StoryWriter] Created task {task_id} for full story generation (user {user_id})")
        
        return {
            "task_id": task_id,
            "status": "pending",
            "message": "Story generation started. Use /task/{task_id}/status to check progress."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[StoryWriter] Failed to start story generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# Task Management Endpoints
# ---------------------------

@router.get("/task/{task_id}/status", response_model=TaskStatus)
async def get_task_status(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> TaskStatus:
    """Get the status of a story generation task."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        task_status = task_manager.get_task_status(task_id)
        
        if not task_status:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        return TaskStatus(**task_status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[StoryWriter] Failed to get task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{task_id}/result")
async def get_task_result(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get the result of a completed story generation task."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        task_status = task_manager.get_task_status(task_id)
        
        if not task_status:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        if task_status["status"] != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Task {task_id} is not completed. Status: {task_status['status']}"
            )
        
        result = task_status.get("result")
        if not result:
            raise HTTPException(status_code=404, detail=f"No result found for task {task_id}")
        
        # Some tasks return a full-story payload compatible with StoryFullGenerationResponse,
        # others (e.g., video-only) return a dict like {"video": {...}, "success": True}.
        # To avoid model conflicts, return a generic payload and include task_id.
        # Frontend callers can branch on keys present (e.g., "video").
        if isinstance(result, dict):
            # Ensure success flag present without duplicating
            payload = {**result}
            payload.setdefault("success", True)
            payload["task_id"] = task_id
            return payload

        # Fallback: wrap non-dict results
        return {"result": result, "success": True, "task_id": task_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[StoryWriter] Failed to get task result: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class HDVideoRequest(BaseModel):
    prompt: str
    provider: str = "huggingface"
    model: str | None = None
    num_frames: int | None = None
    guidance_scale: float | None = None
    num_inference_steps: int | None = None
    negative_prompt: str | None = None
    seed: int | None = None

@router.post("/hd-video")
async def generate_hd_video(
    request: HDVideoRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate an HD AI animation using provider text-to-video (Hugging Face for now).
    Saves the returned bytes as a video file and returns the secured URL.
    """
    try:
        user_id = require_authenticated_user(current_user)
        return generate_hd_video_payload(request, user_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[StoryWriter] Failed to generate HD video: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class HDVideoSceneRequest(BaseModel):
    scene_number: int
    scene_data: Dict[str, Any]
    story_context: Dict[str, Any]
    all_scenes: List[Dict[str, Any]]
    scene_image_url: Optional[str] = None
    provider: str = "huggingface"
    model: str | None = None
    num_frames: int | None = None
    guidance_scale: float | None = None
    num_inference_steps: int | None = None
    negative_prompt: str | None = None
    seed: int | None = None


@router.post("/hd-video-scene")
async def generate_hd_video_scene(
    request: HDVideoSceneRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate HD AI video for a single scene with AI-enhanced prompt.
    Uses prompt enhancer to create HunyuanVideo-optimized prompt from story context.
    """
    try:
        user_id = require_authenticated_user(current_user)
        return generate_hd_video_scene_payload(request, user_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[StoryWriter] Failed to generate HD video for scene: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# Image Generation Endpoints
# ---------------------------

@router.post("/generate-images", response_model=StoryImageGenerationResponse)
async def generate_scene_images(
    request: StoryImageGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> StoryImageGenerationResponse:
    """Generate images for story scenes."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID in authentication token")
        
        if not request.scenes or len(request.scenes) == 0:
            raise HTTPException(status_code=400, detail="At least one scene is required")
        
        logger.info(f"[StoryWriter] Generating images for {len(request.scenes)} scenes for user {user_id}")
        
        # Import image generation service
        from services.story_writer.image_generation_service import StoryImageGenerationService
        
        image_service = StoryImageGenerationService()
        
        # Convert StoryScene models to dicts
        scenes_data = [scene.dict() if isinstance(scene, StoryScene) else scene for scene in request.scenes]
        
        # Generate images for all scenes
        image_results = image_service.generate_scene_images(
            scenes=scenes_data,
            user_id=user_id,
            provider=request.provider,
            width=request.width or 1024,
            height=request.height or 1024,
            model=request.model
        )
        
        # Convert results to StoryImageResult models
        image_models = [
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
                error=result.get("error")
            )
            for result in image_results
        ]
        
        return StoryImageGenerationResponse(
            images=image_models,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[StoryWriter] Failed to generate images: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images/{image_filename}")
async def serve_scene_image(
    image_filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Serve a generated story scene image."""
    try:
        require_authenticated_user(current_user)

        from services.story_writer.image_generation_service import StoryImageGenerationService
        from fastapi.responses import FileResponse

        image_service = StoryImageGenerationService()
        image_path = resolve_media_file(image_service.output_dir, image_filename)

        return FileResponse(
            path=str(image_path),
            media_type="image/png",
            filename=image_filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[StoryWriter] Failed to serve image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# Audio Generation Endpoints
# ---------------------------

@router.post("/generate-audio", response_model=StoryAudioGenerationResponse)
async def generate_scene_audio(
    request: StoryAudioGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> StoryAudioGenerationResponse:
    """Generate audio narration for story scenes."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID in authentication token")
        
        if not request.scenes or len(request.scenes) == 0:
            raise HTTPException(status_code=400, detail="At least one scene is required")
        
        logger.info(f"[StoryWriter] Generating audio for {len(request.scenes)} scenes for user {user_id}")
        
        # Import audio generation service
        from services.story_writer.audio_generation_service import StoryAudioGenerationService
        
        audio_service = StoryAudioGenerationService()
        
        # Convert StoryScene models to dicts
        scenes_data = [scene.dict() if isinstance(scene, StoryScene) else scene for scene in request.scenes]
        
        # Generate audio for all scenes
        audio_results = audio_service.generate_scene_audio_list(
            scenes=scenes_data,
            user_id=user_id,
            provider=request.provider or "gtts",
            lang=request.lang or "en",
            slow=request.slow or False,
            rate=request.rate or 150
        )
        
        # Convert results to StoryAudioResult models
        # Ensure all required fields are strings, not None
        audio_models = []
        for result in audio_results:
            # Handle None values by converting to empty strings for required fields
            audio_url = result.get("audio_url") or ""
            audio_filename = result.get("audio_filename") or ""
            
            audio_models.append(
            StoryAudioResult(
                scene_number=result.get("scene_number", 0),
                scene_title=result.get("scene_title", "Untitled"),
                    audio_filename=audio_filename,
                    audio_url=audio_url,
                provider=result.get("provider", "unknown"),
                file_size=result.get("file_size", 0),
                error=result.get("error")
            )
            )
        
        return StoryAudioGenerationResponse(
            audio_files=audio_models,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[StoryWriter] Failed to generate audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audio/{audio_filename}")
async def serve_scene_audio(
    audio_filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Serve a generated story scene audio file."""
    try:
        require_authenticated_user(current_user)

        from services.story_writer.audio_generation_service import StoryAudioGenerationService
        from fastapi.responses import FileResponse

        audio_service = StoryAudioGenerationService()
        audio_path = resolve_media_file(audio_service.output_dir, audio_filename)

        return FileResponse(
            path=str(audio_path),
            media_type="audio/mpeg",
            filename=audio_filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[StoryWriter] Failed to serve audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# Video Generation Endpoints
# ---------------------------

@router.post("/generate-video", response_model=StoryVideoGenerationResponse)
async def generate_story_video(
    request: StoryVideoGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> StoryVideoGenerationResponse:
    """Generate a video from story scenes, images, and audio."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID in authentication token")
        
        if not request.scenes or len(request.scenes) == 0:
            raise HTTPException(status_code=400, detail="At least one scene is required")
        
        if len(request.scenes) != len(request.image_urls) or len(request.scenes) != len(request.audio_urls):
            raise HTTPException(status_code=400, detail="Number of scenes, image URLs, and audio URLs must match")
        
        logger.info(f"[StoryWriter] Generating video for {len(request.scenes)} scenes for user {user_id}")
        
        # Import video generation service and image/audio services
        from services.story_writer.video_generation_service import StoryVideoGenerationService
        from services.story_writer.image_generation_service import StoryImageGenerationService
        from services.story_writer.audio_generation_service import StoryAudioGenerationService
        from pathlib import Path
        
        video_service = StoryVideoGenerationService()
        image_service = StoryImageGenerationService()
        audio_service = StoryAudioGenerationService()
        
        # Convert StoryScene models to dicts
        scenes_data = [scene.dict() if isinstance(scene, StoryScene) else scene for scene in request.scenes]
        
        # Extract image and audio filenames from URLs
        image_paths = []
        audio_paths = []
        valid_scenes = []
        
        for idx, (scene, image_url, audio_url) in enumerate(zip(scenes_data, request.image_urls, request.audio_urls)):
            # Extract filename from URL (e.g., "/api/story/images/scene_1_image.png" -> "scene_1_image.png")
            # Handle both full URLs and relative paths
            image_filename = image_url.split('/')[-1] if '/' in image_url else image_url
            audio_filename = audio_url.split('/')[-1] if '/' in audio_url else audio_url
            
            # Remove query parameters if present
            image_filename = image_filename.split('?')[0]
            audio_filename = audio_filename.split('?')[0]
            
            # Construct full paths
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
        
        if len(image_paths) == 0 or len(audio_paths) == 0:
            raise HTTPException(status_code=400, detail="No valid image or audio files were found")
        
        if len(image_paths) != len(audio_paths):
            raise HTTPException(status_code=400, detail="Number of valid images and audio files must match")
        
        # Use only valid scenes that have both image and audio
        scenes_data = valid_scenes
        
        # Generate video
        video_result = video_service.generate_story_video(
            scenes=scenes_data,
            image_paths=image_paths,
            audio_paths=audio_paths,
            user_id=user_id,
            story_title=request.story_title or "Story",
            fps=request.fps or 24,
            transition_duration=request.transition_duration or 0.5
        )
        
        # Convert result to StoryVideoResult model
        video_model = StoryVideoResult(
            video_filename=video_result.get("video_filename", ""),
            video_url=video_result.get("video_url", ""),
            duration=video_result.get("duration", 0.0),
            fps=video_result.get("fps", 24),
            file_size=video_result.get("file_size", 0),
            num_scenes=video_result.get("num_scenes", 0),
            error=video_result.get("error")
        )
        
        return StoryVideoGenerationResponse(
            video=video_model,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[StoryWriter] Failed to generate video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-video-async", response_model=Dict[str, Any])
async def generate_story_video_async(
    request: StoryVideoGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate a video asynchronously with progress updates via task manager.
    Frontend can poll /api/story/task/{task_id}/status to show progress messages.
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID in authentication token")
        if not request.scenes or len(request.scenes) == 0:
            raise HTTPException(status_code=400, detail="At least one scene is required")
        if len(request.scenes) != len(request.image_urls) or len(request.scenes) != len(request.audio_urls):
            raise HTTPException(status_code=400, detail="Number of scenes, image URLs, and audio URLs must match")

        task_id = task_manager.create_task("story_video_generation")
        background_tasks.add_task(
            _execute_video_generation_task,
            task_id=task_id,
            request=request,
            user_id=user_id
        )
        return {"task_id": task_id, "status": "pending", "message": "Video generation started"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[StoryWriter] Failed to start async video generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _execute_video_generation_task(task_id: str, request: StoryVideoGenerationRequest, user_id: str):
    """Background task to generate story video with progress mapped to task manager."""
    from services.story_writer.video_generation_service import StoryVideoGenerationService
    from services.story_writer.image_generation_service import StoryImageGenerationService
    from services.story_writer.audio_generation_service import StoryAudioGenerationService
    try:
        task_manager.update_task_status(task_id, "processing", progress=2.0, message="Initializing video generation...")
        video_service = StoryVideoGenerationService()
        image_service = StoryImageGenerationService()
        audio_service = StoryAudioGenerationService()

        # Prepare assets
        scenes_data = [scene.dict() if isinstance(scene, StoryScene) else scene for scene in request.scenes]
        image_paths, audio_paths, valid_scenes = [], [], []
        for idx, (scene, image_url, audio_url) in enumerate(zip(scenes_data, request.image_urls, request.audio_urls)):
            image_filename = (image_url.split('/')[-1] if '/' in image_url else image_url).split('?')[0]
            audio_filename = (audio_url.split('/')[-1] if '/' in audio_url else audio_url).split('?')[0]
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

        # Map service progress (0-100) to task progress (5-95)
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
            progress_callback=progress_callback
        )

        task_manager.update_task_status(
            task_id,
            "completed",
            progress=100.0,
            message="Video generation complete!",
            result={"video": result, "success": True}
        )
    except Exception as e:
        logger.error(f"[StoryWriter] Async video generation failed: {e}", exc_info=True)
        task_manager.update_task_status(task_id, "failed", error=str(e), message=f"Video generation failed: {e}")

@router.post("/generate-complete-video", response_model=Dict[str, Any])
async def generate_complete_story_video(
    request: StoryGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Generate a complete story video (outline → images → audio → video) asynchronously."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID in authentication token")
        
        logger.info(f"[StoryWriter] Starting complete video generation for user {user_id}")
        
        # Create task
        task_id = task_manager.create_task("complete_video_generation")
        
        # Start background task
        background_tasks.add_task(
            execute_complete_video_generation,
            task_id=task_id,
            request_data=request.dict(),
            user_id=user_id
        )
        
        return {
            "task_id": task_id,
            "status": "pending",
            "message": "Complete video generation started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[StoryWriter] Failed to start complete video generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def execute_complete_video_generation(
    task_id: str,
    request_data: Dict[str, Any],
    user_id: str
):
    """
    Execute complete video generation workflow synchronously.
    
    This function runs in a background task and performs blocking operations.
    It's not async because it calls synchronous methods from the services.
    """
    from services.story_writer.story_service import StoryWriterService
    from services.story_writer.image_generation_service import StoryImageGenerationService
    from services.story_writer.audio_generation_service import StoryAudioGenerationService
    from services.story_writer.video_generation_service import StoryVideoGenerationService
    
    service = StoryWriterService()
    image_service = StoryImageGenerationService()
    audio_service = StoryAudioGenerationService()
    video_service = StoryVideoGenerationService()
    
    try:
        task_manager.update_task_status(task_id, "processing", progress=5.0, message="Starting complete video generation...")
        
        # Step 1: Generate premise
        task_manager.update_task_status(task_id, "processing", progress=10.0, message="Generating story premise...")
        premise = service.generate_premise(
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
            user_id=user_id
        )
        
        # Step 2: Generate structured outline
        task_manager.update_task_status(task_id, "processing", progress=20.0, message="Generating structured outline with scenes...")
        outline_scenes = service.generate_outline(
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
            use_structured_output=True
        )
        
        if not isinstance(outline_scenes, list):
            raise RuntimeError("Failed to generate structured outline")
        
        # Step 3: Generate images for all scenes
        # Progress range: 30-50% (20% total for image generation)
        task_manager.update_task_status(task_id, "processing", progress=30.0, message="Generating images for scenes...")
        
        def image_progress_callback(sub_progress: float, message: str):
            """Map sub-progress (0-100) to overall progress (30-50%)."""
            overall_progress = 30.0 + (sub_progress * 0.2)
            task_manager.update_task_status(task_id, "processing", progress=overall_progress, message=message)
        
        # Get image generation settings from request (with defaults)
        image_provider = request_data.get("image_provider")
        image_width = request_data.get("image_width", 1024)
        image_height = request_data.get("image_height", 1024)
        image_model = request_data.get("image_model")
        
        image_results = image_service.generate_scene_images(
            scenes=outline_scenes,
            user_id=user_id,
            provider=image_provider,
            width=image_width,
            height=image_height,
            model=image_model,
            progress_callback=image_progress_callback
        )
        
        # Step 4: Generate audio for all scenes
        # Progress range: 50-70% (20% total for audio generation)
        task_manager.update_task_status(task_id, "processing", progress=50.0, message="Generating audio narration for scenes...")
        
        def audio_progress_callback(sub_progress: float, message: str):
            """Map sub-progress (0-100) to overall progress (50-70%)."""
            overall_progress = 50.0 + (sub_progress * 0.2)
            task_manager.update_task_status(task_id, "processing", progress=overall_progress, message=message)
        
        # Get audio generation settings from request (with defaults)
        audio_provider = request_data.get("audio_provider", "gtts")
        audio_lang = request_data.get("audio_lang", "en")
        audio_slow = request_data.get("audio_slow", False)
        audio_rate = request_data.get("audio_rate", 150)
        
        audio_results = audio_service.generate_scene_audio_list(
            scenes=outline_scenes,
            user_id=user_id,
            provider=audio_provider,
            lang=audio_lang,
            slow=audio_slow,
            rate=audio_rate,
            progress_callback=audio_progress_callback
        )
        
        # Step 5: Prepare image and audio paths
        task_manager.update_task_status(task_id, "processing", progress=70.0, message="Preparing video assets...")
        image_paths = []
        audio_paths = []
        valid_scenes = []
        
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
            raise RuntimeError(f"No valid images or audio files were generated. Images: {len(image_paths)}, Audio: {len(audio_paths)}")
        
        if len(image_paths) != len(audio_paths):
            raise RuntimeError(f"Mismatch between image and audio counts. Images: {len(image_paths)}, Audio: {len(audio_paths)}")
        
        # Step 6: Generate video
        # Progress range: 75-95% (20% total for video generation)
        task_manager.update_task_status(task_id, "processing", progress=75.0, message="Composing video from scenes...")
        
        def video_progress_callback(sub_progress: float, message: str):
            """Map sub-progress (0-100) to overall progress (75-95%)."""
            overall_progress = 75.0 + (sub_progress * 0.2)
            task_manager.update_task_status(task_id, "processing", progress=overall_progress, message=message)
        
        # Get video generation settings from request (with defaults)
        video_fps = request_data.get("video_fps", 24)
        video_transition_duration = request_data.get("video_transition_duration", 0.5)
        story_title = request_data.get("story_setting", "Story")[:50]
        
        video_result = video_service.generate_story_video(
            scenes=valid_scenes,
            image_paths=image_paths,
            audio_paths=audio_paths,
            user_id=user_id,
            story_title=story_title,
            fps=video_fps,
            transition_duration=video_transition_duration,
            progress_callback=video_progress_callback
        )
        
        # Prepare result
        result = {
            "premise": premise,
            "outline_scenes": outline_scenes,
            "images": image_results,
            "audio_files": audio_results,
            "video": video_result,
            "success": True
        }
        
        task_manager.update_task_status(
            task_id,
            "completed",
            progress=100.0,
            message="Complete video generation finished!",
            result=result
        )
        
        logger.info(f"[StoryWriter] Complete video generation task {task_id} completed successfully")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[StoryWriter] Complete video generation task {task_id} failed: {error_msg}", exc_info=True)
        task_manager.update_task_status(
            task_id,
            "failed",
            error=error_msg,
            message=f"Complete video generation failed: {error_msg}"
        )


@router.get("/videos/{video_filename}")
async def serve_story_video(
    video_filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Serve a generated story video file."""
    try:
        require_authenticated_user(current_user)

        from services.story_writer.video_generation_service import StoryVideoGenerationService
        from fastapi.responses import FileResponse

        video_service = StoryVideoGenerationService()
        video_path = resolve_media_file(video_service.output_dir, video_filename)

        return FileResponse(
            path=str(video_path),
            media_type="video/mp4",
            filename=video_filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[StoryWriter] Failed to serve video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# Cache Management Endpoints
# ---------------------------

@router.get("/cache/stats")
async def get_cache_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get cache statistics."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        stats = cache_manager.get_cache_stats()
        return {"success": True, "stats": stats}
        
    except Exception as e:
        logger.error(f"[StoryWriter] Failed to get cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear")
async def clear_cache(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Clear the story generation cache."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        result = cache_manager.clear_cache()
        return {"success": True, **result}
        
    except Exception as e:
        logger.error(f"[StoryWriter] Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))
