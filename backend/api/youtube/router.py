"""
YouTube Creator Studio API Router

Handles video planning, scene building, and rendering endpoints.
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from loguru import logger
from sqlalchemy.orm import Session

from middleware.auth_middleware import get_current_user
from services.database import get_db
from services.youtube.planner import YouTubePlannerService
from services.youtube.scene_builder import YouTubeSceneBuilderService
from services.youtube.renderer import YouTubeVideoRendererService
from services.persona_data_service import PersonaDataService
from services.subscription import PricingService
from services.subscription.preflight_validator import validate_scene_animation_operation
from utils.logger_utils import get_service_logger
from utils.asset_tracker import save_asset_to_library
from .task_manager import task_manager

router = APIRouter(prefix="/youtube", tags=["youtube"])
logger = get_service_logger("api.youtube")

# Video output directory
base_dir = Path(__file__).parent.parent.parent.parent
YOUTUBE_VIDEO_DIR = base_dir / "youtube_videos"
YOUTUBE_VIDEO_DIR.mkdir(parents=True, exist_ok=True)


# Request/Response Models
class VideoPlanRequest(BaseModel):
    """Request model for video planning."""
    user_idea: str = Field(..., description="User's video idea or topic")
    duration_type: str = Field(
        ..., 
        pattern="^(shorts|medium|long)$",
        description="Video duration type: shorts (≤60s), medium (1-4min), long (4-10min)"
    )
    reference_image_description: Optional[str] = Field(
        None, 
        description="Optional description of reference image for visual inspiration"
    )
    source_content_id: Optional[str] = Field(
        None,
        description="Optional ID of source content (blog/story) to convert"
    )
    source_content_type: Optional[str] = Field(
        None,
        pattern="^(blog|story)$",
        description="Type of source content: blog or story"
    )


class VideoPlanResponse(BaseModel):
    """Response model for video plan."""
    success: bool
    plan: Optional[Dict[str, Any]] = None
    message: str


class SceneBuildRequest(BaseModel):
    """Request model for scene building."""
    video_plan: Dict[str, Any] = Field(..., description="Video plan from planning endpoint")
    custom_script: Optional[str] = Field(
        None,
        description="Optional custom script to use instead of generating from plan"
    )


class SceneBuildResponse(BaseModel):
    """Response model for scene building."""
    success: bool
    scenes: List[Dict[str, Any]] = []
    message: str


class SceneUpdateRequest(BaseModel):
    """Request model for updating a single scene."""
    scene_id: int = Field(..., description="Scene number to update")
    narration: Optional[str] = None
    visual_description: Optional[str] = None
    duration_estimate: Optional[float] = None
    enabled: Optional[bool] = None


class SceneUpdateResponse(BaseModel):
    """Response model for scene update."""
    success: bool
    scene: Optional[Dict[str, Any]] = None
    message: str


class VideoRenderRequest(BaseModel):
    """Request model for video rendering."""
    scenes: List[Dict[str, Any]] = Field(..., description="List of scenes to render")
    video_plan: Dict[str, Any] = Field(..., description="Original video plan")
    resolution: str = Field("720p", pattern="^(480p|720p|1080p)$", description="Video resolution")
    combine_scenes: bool = Field(True, description="Whether to combine scenes into single video")
    voice_id: str = Field("Wise_Woman", description="Voice ID for narration")


class VideoRenderResponse(BaseModel):
    """Response model for video rendering."""
    success: bool
    task_id: Optional[str] = None
    message: str


class CostEstimateRequest(BaseModel):
    """Request model for cost estimation."""
    scenes: List[Dict[str, Any]] = Field(..., description="List of scenes to estimate")
    resolution: str = Field("720p", pattern="^(480p|720p|1080p)$", description="Video resolution")


class CostEstimateResponse(BaseModel):
    """Response model for cost estimation."""
    success: bool
    estimate: Optional[Dict[str, Any]] = None
    message: str


# Helper function to get user ID
def require_authenticated_user(current_user: Dict[str, Any]) -> str:
    """Extract and validate user ID from current user."""
    user_id = current_user.get("id") if current_user else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return str(user_id)


@router.post("/plan", response_model=VideoPlanResponse)
async def create_video_plan(
    request: VideoPlanRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VideoPlanResponse:
    """
    Generate a comprehensive video plan from user input.
    
    This endpoint uses AI to create a detailed plan including:
    - Video summary and target audience
    - Content outline with timing
    - Hook strategy and CTA
    - Visual style recommendations
    - SEO keywords
    """
    try:
        user_id = require_authenticated_user(current_user)
        
        logger.info(
            f"[YouTubeAPI] Planning video: idea={request.user_idea[:50]}..., "
            f"duration={request.duration_type}, user={user_id}"
        )
        
        # Get persona data if available
        persona_data = None
        try:
            persona_service = PersonaDataService()
            persona_data = persona_service.get_user_persona_data(user_id)
        except Exception as e:
            logger.warning(f"[YouTubeAPI] Could not load persona data: {e}")
        
        # Generate plan (optimized: for shorts, combine plan + scenes in one call)
        planner = YouTubePlannerService()
        plan = planner.generate_video_plan(
            user_idea=request.user_idea,
            duration_type=request.duration_type,
            persona_data=persona_data,
            reference_image_description=request.reference_image_description,
            source_content_id=request.source_content_id,
            source_content_type=request.source_content_type,
            user_id=user_id,
            include_scenes=(request.duration_type == "shorts"),  # Optimize shorts
        )
        
        return VideoPlanResponse(
            success=True,
            plan=plan,
            message="Video plan generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[YouTubeAPI] Error creating plan: {e}", exc_info=True)
        return VideoPlanResponse(
            success=False,
            message=f"Failed to create video plan: {str(e)}"
        )


@router.post("/scenes", response_model=SceneBuildResponse)
async def build_scenes(
    request: SceneBuildRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> SceneBuildResponse:
    """
    Build structured scenes from a video plan.
    
    Converts the video plan into detailed scenes with:
    - Narration text for each scene
    - Visual descriptions and prompts
    - Timing estimates
    - Visual cues and emphasis tags
    """
    try:
        user_id = require_authenticated_user(current_user)
        
        logger.info(
            f"[YouTubeAPI] Building scenes: duration={request.video_plan.get('duration_type')}, "
            f"custom_script={bool(request.custom_script)}, user={user_id}"
        )
        
        # Build scenes
        scene_builder = YouTubeSceneBuilderService()
        scenes = scene_builder.build_scenes_from_plan(
            video_plan=request.video_plan,
            user_id=user_id,
            custom_script=request.custom_script,
        )
        
        return SceneBuildResponse(
            success=True,
            scenes=scenes,
            message=f"Built {len(scenes)} scenes successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[YouTubeAPI] Error building scenes: {e}", exc_info=True)
        return SceneBuildResponse(
            success=False,
            message=f"Failed to build scenes: {str(e)}"
        )


@router.post("/scenes/{scene_id}/update", response_model=SceneUpdateResponse)
async def update_scene(
    scene_id: int,
    request: SceneUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> SceneUpdateResponse:
    """
    Update a single scene's narration, visual description, or duration.
    
    This allows users to fine-tune individual scenes before rendering.
    """
    try:
        require_authenticated_user(current_user)
        
        logger.info(f"[YouTubeAPI] Updating scene {scene_id}")
        
        # In a full implementation, this would update a stored scene
        # For now, return the updated scene data
        updated_scene = {
            "scene_number": scene_id,
            "narration": request.narration,
            "visual_description": request.visual_description,
            "duration_estimate": request.duration_estimate,
            "enabled": request.enabled if request.enabled is not None else True,
        }
        
        return SceneUpdateResponse(
            success=True,
            scene=updated_scene,
            message="Scene updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[YouTubeAPI] Error updating scene: {e}", exc_info=True)
        return SceneUpdateResponse(
            success=False,
            message=f"Failed to update scene: {str(e)}"
        )


@router.post("/render", response_model=VideoRenderResponse)
async def start_video_render(
    request: VideoRenderRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VideoRenderResponse:
    """
    Start rendering a video from scenes asynchronously.
    
    This endpoint creates a background task that:
    1. Generates narration audio for each scene
    2. Renders each scene using WAN 2.5 text-to-video
    3. Combines scenes into final video (if requested)
    4. Saves to asset library
    
    Returns task_id for polling progress.
    """
    try:
        user_id = require_authenticated_user(current_user)
        
        # Validate subscription limits
        pricing_service = PricingService(db)
        validate_scene_animation_operation(
            pricing_service=pricing_service,
            user_id=user_id
        )
        
        # Filter enabled scenes
        enabled_scenes = [s for s in request.scenes if s.get("enabled", True)]
        if not enabled_scenes:
            return VideoRenderResponse(
                success=False,
                message="No enabled scenes to render"
            )
        
        # VALIDATION: Pre-validate scenes before creating task to prevent wasted API calls
        validation_errors = []
        for scene in enabled_scenes:
            scene_num = scene.get("scene_number", 0)
            visual_prompt = (scene.get("enhanced_visual_prompt") or scene.get("visual_prompt", "")).strip()
            
            if not visual_prompt:
                validation_errors.append(f"Scene {scene_num}: Missing visual prompt")
            elif len(visual_prompt) < 5:
                validation_errors.append(f"Scene {scene_num}: Visual prompt too short ({len(visual_prompt)} chars, minimum 5)")
            
            # Validate duration
            duration = scene.get("duration_estimate", 5)
            if duration < 1 or duration > 10:
                validation_errors.append(f"Scene {scene_num}: Invalid duration ({duration}s, must be 1-10 seconds)")
        
        if validation_errors:
            error_msg = "Validation failed: " + "; ".join(validation_errors)
            logger.warning(f"[YouTubeAPI] {error_msg}")
            return VideoRenderResponse(
                success=False,
                message=error_msg + ". Please fix these issues before rendering."
            )
        
        logger.info(
            f"[YouTubeAPI] Starting render: {len(enabled_scenes)} scenes, "
            f"resolution={request.resolution}, user={user_id}"
        )
        
        # Create async task
        task_id = task_manager.create_task("youtube_video_render")
        logger.info(
            f"[YouTubeAPI] Created task {task_id} for user {user_id}, "
            f"scenes={len(enabled_scenes)}, resolution={request.resolution}"
        )
        
        # Verify task was created
        initial_status = task_manager.get_task_status(task_id)
        if not initial_status:
            logger.error(f"[YouTubeAPI] Failed to create task {task_id} - task not found immediately after creation")
            return VideoRenderResponse(
                success=False,
                message="Failed to create render task. Please try again."
            )
        
        # Add background task
        try:
            background_tasks.add_task(
                _execute_video_render_task,
                task_id=task_id,
                scenes=enabled_scenes,
                video_plan=request.video_plan,
                user_id=user_id,
                resolution=request.resolution,
                combine_scenes=request.combine_scenes,
                voice_id=request.voice_id,
            )
            logger.info(f"[YouTubeAPI] Background task added for task {task_id}")
        except Exception as bg_error:
            logger.error(f"[YouTubeAPI] Failed to add background task for {task_id}: {bg_error}", exc_info=True)
            # Mark task as failed
            task_manager.update_task_status(
                task_id,
                "failed",
                error=str(bg_error),
                message="Failed to start background render task"
            )
            return VideoRenderResponse(
                success=False,
                message=f"Failed to start render task: {str(bg_error)}"
            )
        
        return VideoRenderResponse(
            success=True,
            task_id=task_id,
            message=f"Video rendering started. Processing {len(enabled_scenes)} scenes..."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[YouTubeAPI] Error starting render: {e}", exc_info=True)
        return VideoRenderResponse(
            success=False,
            message=f"Failed to start render: {str(e)}"
        )


@router.get("/render/{task_id}")
async def get_render_status(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get the status of a video rendering task.
    
    Returns current progress, status, and result when complete.
    """
    try:
        require_authenticated_user(current_user)
        
        logger.debug(f"[YouTubeAPI] Getting render status for task: {task_id}")
        task_status = task_manager.get_task_status(task_id)
        if not task_status:
            logger.warning(
                f"[YouTubeAPI] Task {task_id} not found. "
                f"Available tasks: {list(task_manager.task_storage.keys())[:5]}..."
            )
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Task not found",
                    "message": "The render task was not found. It may have expired, been cleaned up, or the server may have restarted.",
                    "task_id": task_id,
                    "user_action": "Please try rendering again."
                }
            )
        
        return task_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[YouTubeAPI] Error getting render status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get render status: {str(e)}"
        )


def _execute_video_render_task(
    task_id: str,
    scenes: List[Dict[str, Any]],
    video_plan: Dict[str, Any],
    user_id: str,
    resolution: str,
    combine_scenes: bool,
    voice_id: str,
):
    """Background task to render video with progress updates."""
    logger.info(
        f"[YouTubeRenderer] Background task started for task {task_id}, "
        f"scenes={len(scenes)}, user={user_id}"
    )
    
    # Verify task exists before starting
    task_status = task_manager.get_task_status(task_id)
    if not task_status:
        logger.error(
            f"[YouTubeRenderer] Task {task_id} not found when background task started. "
            f"This should not happen - task may have been cleaned up."
        )
        return
    
    try:
        task_manager.update_task_status(
            task_id, "processing", progress=5.0, message="Initializing render..."
        )
        logger.info(f"[YouTubeRenderer] Task {task_id} status updated to processing")
        
        renderer = YouTubeVideoRendererService()
        
        total_scenes = len(scenes)
        scene_results = []
        total_cost = 0.0
        
        # VALIDATION: Pre-validate all scenes before starting expensive API calls
        invalid_scenes = []
        for idx, scene in enumerate(scenes):
            scene_num = scene.get("scene_number", idx + 1)
            visual_prompt = (scene.get("enhanced_visual_prompt") or scene.get("visual_prompt", "")).strip()
            
            if not visual_prompt:
                invalid_scenes.append({
                    "scene_number": scene_num,
                    "reason": "Missing visual prompt",
                    "prompt_length": 0
                })
            elif len(visual_prompt) < 5:
                invalid_scenes.append({
                    "scene_number": scene_num,
                    "reason": f"Visual prompt too short ({len(visual_prompt)} chars, minimum 5)",
                    "prompt_length": len(visual_prompt)
                })
            
            # Validate duration
            duration = scene.get("duration_estimate", 5)
            if duration < 1 or duration > 10:
                invalid_scenes.append({
                    "scene_number": scene_num,
                    "reason": f"Invalid duration ({duration}s, must be 1-10 seconds)",
                    "prompt_length": len(visual_prompt) if visual_prompt else 0
                })
        
        if invalid_scenes:
            error_msg = f"Found {len(invalid_scenes)} invalid scene(s) before rendering: " + \
                       ", ".join([f"Scene {s['scene_number']} ({s['reason']})" for s in invalid_scenes])
            logger.error(f"[YouTubeRenderer] {error_msg}")
            task_manager.update_task_status(
                task_id,
                "failed",
                error=error_msg,
                message=f"Validation failed: {len(invalid_scenes)} scene(s) have invalid data. Please fix them before rendering."
            )
            return
        
        # Render each scene
        for idx, scene in enumerate(scenes):
            scene_num = scene.get("scene_number", idx + 1)
            progress = 5.0 + (idx / total_scenes) * 85.0
            
            task_manager.update_task_status(
                task_id,
                "processing",
                progress=progress,
                message=f"Rendering scene {scene_num}/{total_scenes}..."
            )
            
            try:
                scene_result = renderer.render_scene_video(
                    scene=scene,
                    video_plan=video_plan,
                    user_id=user_id,
                    resolution=resolution,
                    generate_audio_enabled=True,
                    voice_id=voice_id,
                )
                
                scene_results.append(scene_result)
                total_cost += scene_result["cost"]
                
                # Save to asset library
                try:
                    from services.database import get_db
                    db = next(get_db())
                    try:
                        save_asset_to_library(
                            db=db,
                            user_id=user_id,
                            asset_type="video",
                            source_module="youtube_creator",
                            filename=scene_result["video_filename"],
                            file_url=scene_result["video_url"],
                            file_path=scene_result["video_path"],
                            file_size=scene_result["file_size"],
                            mime_type="video/mp4",
                            title=f"YouTube Scene {scene_num}: {scene.get('title', 'Untitled')}",
                            description=f"Scene {scene_num} from YouTube video",
                            prompt=scene.get("visual_prompt", ""),
                            tags=["youtube_creator", "video", "scene", f"scene_{scene_num}", resolution],
                            provider="wavespeed",
                            model="alibaba/wan-2.5/text-to-video",
                            cost=scene_result["cost"],
                            asset_metadata={
                                "scene_number": scene_num,
                                "duration": scene_result["duration"],
                                "resolution": resolution,
                                "status": "completed"
                            }
                        )
                    finally:
                        db.close()
                except Exception as e:
                    logger.warning(f"[YouTubeRenderer] Failed to save scene to library: {e}")
                
            except Exception as scene_error:
                error_msg = str(scene_error)
                scene_error_type = "unknown"
                
                if isinstance(scene_error, HTTPException):
                    error_detail = scene_error.detail
                    if isinstance(error_detail, dict):
                        error_msg = error_detail.get("message", error_detail.get("error", str(error_detail)))
                        scene_error_type = error_detail.get("error", "http_error")
                    else:
                        error_msg = str(error_detail)
                    # Check if it's a timeout or critical error that should fail fast
                    if scene_error.status_code == 504:  # Timeout
                        scene_error_type = "timeout"
                    elif scene_error.status_code >= 500:  # Server errors
                        scene_error_type = "server_error"
                else:
                    # Check error type from exception
                    if "timeout" in str(scene_error).lower():
                        scene_error_type = "timeout"
                    elif "connection" in str(scene_error).lower():
                        scene_error_type = "connection_error"
                
                logger.error(
                    f"[YouTubeRenderer] Scene {scene_num} failed: {error_msg} (type: {scene_error_type})",
                    exc_info=True
                )
                
                # Track failed scene for user retry
                failed_scene_result = {
                    "scene_number": scene_num,
                    "status": "failed",
                    "error": error_msg,
                    "error_type": scene_error_type,
                    "scene_data": scene,
                }
                scene_results.append(failed_scene_result)
                
                # Update task status immediately to reflect failure
                successful_count = len([r for r in scene_results if r.get("status") != "failed"])
                failed_count = len([r for r in scene_results if r.get("status") == "failed"])
                
                # Fail fast for critical errors (timeouts, server errors) if it's the first scene
                # or if multiple consecutive failures occur
                should_fail_fast = (
                    scene_error_type in ["timeout", "server_error", "connection_error"] and
                    (failed_count == 1 or failed_count >= 3)  # Fail fast on first timeout or 3+ failures
                )
                
                if should_fail_fast:
                    logger.error(
                        f"[YouTubeRenderer] Failing fast due to {scene_error_type} error. "
                        f"Scene {scene_num} failed, total failures: {failed_count}"
                    )
                    # Mark task as failed immediately
                    task_manager.update_task_status(
                        task_id,
                        "failed",
                        error=f"Render failed fast: Scene {scene_num} failed with {scene_error_type}",
                        message=f"Video rendering stopped early due to {scene_error_type}. "
                               f"{successful_count} scene(s) completed, {failed_count} scene(s) failed. "
                               f"Failed scene: {error_msg}",
                    )
                    # Update result with current state
                    successful_scenes = [r for r in scene_results if r.get("status") != "failed"]
                    failed_scenes = [r for r in scene_results if r.get("status") == "failed"]
                    result = {
                        "scene_results": successful_scenes,
                        "failed_scenes": failed_scenes,
                        "total_cost": total_cost,
                        "final_video_url": successful_scenes[0]["video_url"] if successful_scenes else None,
                        "num_scenes": len(successful_scenes),
                        "num_failed": len(failed_scenes),
                        "resolution": resolution,
                        "partial_success": len(failed_scenes) > 0 and len(successful_scenes) > 0,
                        "fail_fast": True,
                        "fail_reason": f"Scene {scene_num} failed with {scene_error_type}",
                    }
                    task_manager.update_task_status(
                        task_id,
                        "failed",
                        error=f"Render failed fast: {scene_error_type}",
                        message=f"Rendering stopped early. {successful_count} completed, {failed_count} failed.",
                        result=result
                    )
                    return  # Exit immediately
                
                # For non-critical errors, update progress but continue
                task_manager.update_task_status(
                    task_id,
                    "processing",
                    progress=progress,
                    message=f"Scene {scene_num} failed, continuing with remaining scenes... "
                           f"({successful_count} successful, {failed_count} failed)"
                )
                # Continue with other scenes - let user retry failed ones
                continue
        
        # Separate successful and failed scenes
        successful_scenes = [r for r in scene_results if r.get("status") != "failed"]
        failed_scenes = [r for r in scene_results if r.get("status") == "failed"]
        
        if not successful_scenes:
            # All scenes failed - mark as failed immediately
            error_msg = f"All {len(failed_scenes)} scene(s) failed to render"
            logger.error(f"[YouTubeRenderer] {error_msg}")
            task_manager.update_task_status(
                task_id,
                "failed",
                error=error_msg,
                message=f"All scenes failed. First error: {failed_scenes[0].get('error', 'Unknown') if failed_scenes else 'Unknown'}",
                result={
                    "scene_results": [],
                    "failed_scenes": failed_scenes,
                    "total_cost": 0.0,
                    "final_video_url": None,
                    "num_scenes": 0,
                    "num_failed": len(failed_scenes),
                    "resolution": resolution,
                    "partial_success": False,
                }
            )
            return
        
        # Combine scenes if requested (only if we have successful scenes)
        final_video_url = None
        if combine_scenes and len(successful_scenes) > 1:
            task_manager.update_task_status(
                task_id, "processing", progress=90.0, message="Combining scenes..."
            )
            
            # Use renderer to combine
            combined_result = renderer.render_full_video(
                scenes=scenes,
                video_plan=video_plan,
                user_id=user_id,
                resolution=resolution,
                combine_scenes=True,
                voice_id=voice_id,
            )
            
            final_video_url = combined_result.get("final_video_url")
        
        # Final result (successful_scenes and failed_scenes already separated above)
        result = {
            "scene_results": successful_scenes,
            "failed_scenes": failed_scenes,
            "total_cost": total_cost,
            "final_video_url": final_video_url or (successful_scenes[0]["video_url"] if successful_scenes else None),
            "num_successful": len(successful_scenes),
            "num_failed": len(failed_scenes),
            "resolution": resolution,
            "partial_success": len(failed_scenes) > 0 and len(successful_scenes) > 0,
        }
        
        # Determine final status based on results
        if len(failed_scenes) == 0:
            # All scenes succeeded
            final_status = "completed"
            final_message = f"Video rendering complete! {len(successful_scenes)} scene(s) rendered successfully."
        elif len(successful_scenes) > 0:
            # Partial success
            final_status = "completed"  # Still mark as completed but with partial success flag
            final_message = f"Video rendering completed with {len(failed_scenes)} failure(s). " \
                          f"{len(successful_scenes)} scene(s) rendered successfully."
        else:
            # This shouldn't happen due to early return above, but handle it
            final_status = "failed"
            final_message = f"All scenes failed to render."
        
        task_manager.update_task_status(
            task_id,
            final_status,
            progress=100.0,
            message=final_message,
            result=result
        )
        
        logger.info(
            f"[YouTubeRenderer] ✅ Render task {task_id} completed: "
            f"{len(scene_results)} scenes, cost=${total_cost:.2f}"
        )
        
    except HTTPException as exc:
        error_msg = str(exc.detail) if isinstance(exc.detail, str) else exc.detail.get("error", "Render failed") if isinstance(exc.detail, dict) else "Render failed"
        logger.error(f"[YouTubeRenderer] Render task {task_id} failed: {error_msg}")
        task_manager.update_task_status(
            task_id,
            "failed",
            error=error_msg,
            message=f"Video rendering failed: {error_msg}",
        )
    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"[YouTubeRenderer] Render task {task_id} error: {error_msg}", exc_info=True)
        task_manager.update_task_status(
            task_id,
            "failed",
            error=error_msg,
            message=f"Video rendering error: {error_msg}",
        )


@router.post("/estimate-cost", response_model=CostEstimateResponse)
async def estimate_render_cost(
    request: CostEstimateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> CostEstimateResponse:
    """
    Estimate the cost of rendering a video before actually rendering it.
    
    This endpoint calculates the expected cost based on:
    - Number of enabled scenes
    - Duration of each scene
    - Selected resolution
    
    Returns a detailed cost breakdown.
    """
    try:
        require_authenticated_user(current_user)
        
        logger.info(
            f"[YouTubeAPI] Estimating cost: {len(request.scenes)} scenes, "
            f"resolution={request.resolution}"
        )
        
        renderer = YouTubeVideoRendererService()
        estimate = renderer.estimate_render_cost(
            scenes=request.scenes,
            resolution=request.resolution,
        )
        
        return CostEstimateResponse(
            success=True,
            estimate=estimate,
            message="Cost estimate calculated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[YouTubeAPI] Error estimating cost: {e}", exc_info=True)
        return CostEstimateResponse(
            success=False,
            message=f"Failed to estimate cost: {str(e)}"
        )


@router.get("/videos/{video_filename}")
async def serve_youtube_video(
    video_filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> FileResponse:
    """
    Serve YouTube video files.
    
    This endpoint serves video files generated by the YouTube Creator Studio.
    Videos are stored in the youtube_videos directory.
    """
    try:
        require_authenticated_user(current_user)
        
        # Security: prevent directory traversal
        if ".." in video_filename or "/" in video_filename or "\\" in video_filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        video_path = YOUTUBE_VIDEO_DIR / video_filename
        
        if not video_path.exists():
            raise HTTPException(status_code=404, detail="Video not found")
        
        if not video_path.is_file():
            raise HTTPException(status_code=400, detail="Invalid video path")
        
        logger.debug(f"[YouTubeAPI] Serving video: {video_filename}")
        
        return FileResponse(
            path=str(video_path),
            media_type="video/mp4",
            filename=video_filename,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[YouTubeAPI] Error serving video: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to serve video: {str(e)}"
        )

