"""
Podcast Video Handlers

Video generation and serving endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pathlib import Path
from urllib.parse import quote
import re
import json
from concurrent.futures import ThreadPoolExecutor

from services.database import get_session_for_user
from middleware.auth_middleware import get_current_user, get_current_user_with_query_token
from api.story_writer.utils.auth import require_authenticated_user
from services.wavespeed.infinitetalk import animate_scene_with_voiceover
from services.podcast.video_combination_service import PodcastVideoCombinationService
from services.llm_providers.main_video_generation import track_video_usage
from services.subscription import PricingService
from services.subscription.preflight_validator import validate_scene_animation_operation
from api.story_writer.task_manager import task_manager
from loguru import logger
from ..constants import AI_VIDEO_SUBDIR, PODCAST_VIDEOS_DIR
from ..utils import load_podcast_audio_bytes, load_podcast_image_bytes
from services.podcast_service import PodcastService
from ..models import (
    PodcastVideoGenerationRequest,
    PodcastVideoGenerationResponse,
    PodcastCombineVideosRequest,
    PodcastCombineVideosResponse,
)

router = APIRouter()

# Thread pool executor for CPU-intensive video operations
# This prevents blocking the FastAPI event loop
_video_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="podcast_video")


def _extract_error_message(exc: Exception) -> str:
    """
    Extract user-friendly error message from exception.
    Handles HTTPException with nested error details from WaveSpeed API.
    """
    if isinstance(exc, HTTPException):
        detail = exc.detail
        # If detail is a dict (from WaveSpeed client)
        if isinstance(detail, dict):
            # Try to extract message from nested response JSON
            response_str = detail.get("response", "")
            if response_str:
                try:
                    response_json = json.loads(response_str)
                    if isinstance(response_json, dict) and "message" in response_json:
                        return response_json["message"]
                except (json.JSONDecodeError, TypeError):
                    pass
            # Fall back to error field
            if "error" in detail:
                return detail["error"]
        # If detail is a string
        elif isinstance(detail, str):
            return detail
    
    # For other exceptions, use string representation
    error_str = str(exc)
    
    # Try to extract meaningful message from HTTPException string format
    # Format: "502: {'error': '...', 'response': '{"message":"..."}'}"
    if "Insufficient credits" in error_str or "insufficient credits" in error_str.lower():
        return "Insufficient WaveSpeed credits. Please top up your account."
    
    # Try to extract JSON message from string
    try:
        # Look for JSON-like structures in the error string
        json_match = re.search(r'"message"\s*:\s*"([^"]+)"', error_str)
        if json_match:
            return json_match.group(1)
    except Exception:
        pass
    
    return error_str


def _execute_podcast_video_task(
    task_id: str,
    request: PodcastVideoGenerationRequest,
    user_id: str,
    image_bytes: bytes,
    audio_bytes: bytes,
    auth_token: Optional[str] = None,
    mask_image_bytes: Optional[bytes] = None,
):
    """Background task to generate InfiniteTalk video for podcast scene."""
    try:
        task_manager.update_task_status(
            task_id, "processing", progress=5.0, message="Submitting to WaveSpeed InfiniteTalk..."
        )

        # Extract scene number from scene_id
        scene_number_match = re.search(r'\d+', request.scene_id)
        scene_number = int(scene_number_match.group()) if scene_number_match else 0

        # Fetch project context (Bible & Analysis) from DB if not provided in request
        from services.database import get_session_for_user
        from services.podcast_service import PodcastService
        
        project_bible = request.bible
        project_analysis = None
        
        try:
            # Create a dedicated session for this background task
            db = get_session_for_user(user_id)
            try:
                podcast_service = PodcastService(db)
                # Fetch project directly from DB to get latest analysis/bible
                project = podcast_service.get_project(user_id, request.project_id)
                if project:
                    # Use project bible if request didn't provide one
                    if not project_bible and project.bible:
                        project_bible = project.bible
                    
                    # Get analysis for better context
                    if project.analysis:
                        project_analysis = project.analysis
                        logger.info(f"[Podcast] Loaded analysis for video context: {list(project_analysis.keys())}")
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"[Podcast] Failed to fetch project context for video generation: {e}")

        # Prepare scene data for animation
        scene_data = {
            "scene_number": scene_number,
            "title": request.scene_title,
            "scene_id": request.scene_id,
        }
        story_context = {
            "project_id": request.project_id,
            "type": "podcast",
            "bible": project_bible,
            "analysis": project_analysis,
        }

        animation_result = animate_scene_with_voiceover(
            image_bytes=image_bytes,
            audio_bytes=audio_bytes,
            scene_data=scene_data,
            story_context=story_context,
            user_id=user_id,
            resolution=request.resolution or "720p",
            prompt_override=request.prompt,
            mask_image_bytes=mask_image_bytes,
            seed=request.seed if request.seed is not None else -1,
            image_mime="image/png",
            audio_mime="audio/mpeg",
        )

        task_manager.update_task_status(
            task_id, "processing", progress=80.0, message="Saving video file..."
        )

        # Use podcast-specific video directory
        ai_video_dir = PODCAST_VIDEOS_DIR / AI_VIDEO_SUBDIR
        ai_video_dir.mkdir(parents=True, exist_ok=True)
        video_service = PodcastVideoCombinationService(output_dir=str(PODCAST_VIDEOS_DIR / "Final_Videos"))

        save_result = video_service.save_scene_video(
            video_bytes=animation_result["video_bytes"],
            scene_number=scene_number,
            user_id=user_id,
        )
        video_filename = save_result["video_filename"]
        video_url = f"/api/podcast/videos/{video_filename}"
        if auth_token:
            video_url = f"{video_url}?token={quote(auth_token)}"

        logger.info(
            f"[Podcast] Video saved: filename={video_filename}, url={video_url}, scene={request.scene_id}"
        )

        usage_info = track_video_usage(
            user_id=user_id,
            provider=animation_result["provider"],
            model_name=animation_result["model_name"],
            prompt=animation_result["prompt"],
            video_bytes=animation_result["video_bytes"],
            cost_override=animation_result["cost"],
        )

        result_data = {
            "video_url": video_url,
            "video_filename": video_filename,
            "cost": animation_result["cost"],
            "duration": animation_result["duration"],
            "provider": animation_result["provider"],
            "model": animation_result["model_name"],
        }

        logger.info(
            f"[Podcast] Updating task status to completed: task_id={task_id}, result={result_data}"
        )

        task_manager.update_task_status(
            task_id,
            "completed",
            progress=100.0,
            message="Video generation complete!",
            result=result_data,
        )

        # Verify the task status was updated correctly
        updated_status = task_manager.get_task_status(task_id)
        logger.info(
            f"[Podcast] Task status after update: task_id={task_id}, status={updated_status.get('status') if updated_status else 'None'}, has_result={bool(updated_status.get('result') if updated_status else False)}, video_url={updated_status.get('result', {}).get('video_url') if updated_status else 'N/A'}"
        )

        logger.info(
            f"[Podcast] Video generation completed for project {request.project_id}, scene {request.scene_id}"
        )

    except Exception as exc:
        # Use logger.exception to avoid KeyError when exception message contains curly braces
        logger.exception(f"[Podcast] Video generation failed for project {request.project_id}, scene {request.scene_id}")
        
        # Extract user-friendly error message from exception
        error_msg = _extract_error_message(exc)
        
        task_manager.update_task_status(
            task_id, "failed", error=error_msg, message=f"Video generation failed: {error_msg}"
        )


@router.post("/render/video", response_model=PodcastVideoGenerationResponse)
async def generate_podcast_video(
    request: Request,
    body: PodcastVideoGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Generate video for a podcast scene using WaveSpeed InfiniteTalk (avatar image + audio).
    Returns task_id for polling since InfiniteTalk can take up to 10 minutes.
    """
    # Debug logging to identify "Depends object has no attribute get" error source
    logger.info(f"[Podcast] generate_podcast_video called. current_user type: {type(current_user)}")
    
    # Check if current_user is a Depends object (FastAPI injection failure)
    if hasattr(current_user, "dependency"):
        logger.error(f"[Podcast] CRITICAL: current_user is a Depends object! Dependency injection failed.")
        # Attempt to manually resolve or fail gracefully
        auth_header = None
        try:
            if hasattr(request, 'headers') and hasattr(request.headers, 'get'):
                 auth_header = request.headers.get("Authorization")
        except:
            pass
            
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "").strip()
            # Manually verify token if dependency injection failed
            from middleware.auth_middleware import clerk_auth
            current_user = await clerk_auth.verify_token(token)
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication failed (manual recovery)")
        else:
             raise HTTPException(status_code=401, detail="Authentication failed (injection error)")

    user_id = require_authenticated_user(current_user)

    logger.info(
        f"[Podcast] Starting video generation for project {body.project_id}, scene {body.scene_id}"
    )

    # Load audio bytes
    audio_bytes = load_podcast_audio_bytes(body.audio_url)

    # Validate resolution
    if body.resolution not in {"480p", "720p"}:
        raise HTTPException(status_code=400, detail="Resolution must be '480p' or '720p'.")

    # Load image bytes (scene image is required for video generation)
    if body.avatar_image_url:
        image_bytes = load_podcast_image_bytes(body.avatar_image_url)
    else:
        # Scene-specific image should be generated before video generation
        raise HTTPException(
            status_code=400,
            detail="Scene image is required for video generation. Please generate images for scenes first.",
        )

    mask_image_bytes = None
    if body.mask_image_url:
        try:
            mask_image_bytes = load_podcast_image_bytes(body.mask_image_url)
        except Exception as e:
            logger.error(f"[Podcast] Failed to load mask image: {e}")
            raise HTTPException(
                status_code=400,
                detail="Failed to load mask image for video generation.",
            )

    # Validate subscription limits
    db = get_session_for_user(user_id)
    if not db:
        raise HTTPException(status_code=500, detail="Database session unavailable for user.")
    try:
        pricing_service = PricingService(db)
        validate_scene_animation_operation(pricing_service=pricing_service, user_id=user_id)
    finally:
        db.close()

    # Extract token for authenticated URL building
    auth_token = None
    try:
        if hasattr(request, 'headers') and hasattr(request.headers, 'get'):
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                auth_token = auth_header.replace("Bearer ", "").strip()
    except Exception as e:
        logger.warning(f"[Podcast] Failed to extract auth token from headers: {e}")

    # Create async task
    task_id = task_manager.create_task("podcast_video_generation")
    background_tasks.add_task(
        _execute_podcast_video_task,
        task_id=task_id,
        request=body,
        user_id=user_id,
        image_bytes=image_bytes,
        audio_bytes=audio_bytes,
        auth_token=auth_token,
        mask_image_bytes=mask_image_bytes,
    )

    return PodcastVideoGenerationResponse(
        task_id=task_id,
        status="pending",
        message="Video generation started. This may take up to 10 minutes.",
    )


@router.get("/videos/{filename}")
async def serve_podcast_video(
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user_with_query_token),
):
    """Serve generated podcast scene video files.
    
    Supports authentication via Authorization header or token query parameter.
    Query parameter is useful for HTML elements like <video> that cannot send custom headers.
    """
    require_authenticated_user(current_user)
    
    # Security check: ensure filename doesn't contain path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Look for video in podcast_videos directory (including AI_Videos subdirectory)
    video_path = None
    possible_paths = [
        PODCAST_VIDEOS_DIR / filename,
        PODCAST_VIDEOS_DIR / AI_VIDEO_SUBDIR / filename,
    ]
    
    for path in possible_paths:
        resolved_path = path.resolve()
        # Security check: ensure path is within PODCAST_VIDEOS_DIR
        if str(resolved_path).startswith(str(PODCAST_VIDEOS_DIR)) and resolved_path.exists():
            video_path = resolved_path
            break
    
    if not video_path:
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(video_path, media_type="video/mp4")


@router.get("/videos")
async def list_podcast_videos(
    project_id: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    List existing video files for the current user, optionally filtered by project.
    Returns videos mapped to scene numbers for easy matching.
    """
    try:
        user_id = require_authenticated_user(current_user)
        
        logger.info(f"[Podcast] Listing videos for user_id={user_id}, project_id={project_id}")
        
        # Look in podcast_videos/AI_Videos directory
        ai_video_dir = PODCAST_VIDEOS_DIR / AI_VIDEO_SUBDIR
        ai_video_dir.mkdir(parents=True, exist_ok=True)
        
        videos = []
        if ai_video_dir.exists():
            # Pattern: scene_{scene_number}_{user_id}_{timestamp}.mp4
            # Extract user_id from current user (same logic as save_scene_video)
            clean_user_id = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in user_id[:16])
            
            logger.info(f"[Podcast] Looking for videos with clean_user_id={clean_user_id} in {ai_video_dir}")
            
            # Map scene_number -> (most recent video info)
            scene_video_map: Dict[int, Dict[str, Any]] = {}
            
            all_files = list(ai_video_dir.glob("*.mp4"))
            logger.info(f"[Podcast] Found {len(all_files)} MP4 files in directory")
            
            for video_file in all_files:
                filename = video_file.name
                # Match pattern: scene_{number}_{user_id}_{hash}.mp4
                # Use greedy match for user_id and match hash as "anything except underscore before .mp4"
                match = re.match(r"scene_(\d+)_(.+)_([^_]+)\.mp4", filename)
                if match:
                    scene_number = int(match.group(1))
                    file_user_id = match.group(2)
                    hash_part = match.group(3)
                    # Only include videos for this user
                    if file_user_id == clean_user_id:
                        video_url = f"/api/podcast/videos/{filename}"
                        file_mtime = video_file.stat().st_mtime
                        
                        # Keep the most recent video for each scene
                        if scene_number not in scene_video_map or file_mtime > scene_video_map[scene_number]["mtime"]:
                            scene_video_map[scene_number] = {
                                "scene_number": scene_number,
                                "filename": filename,
                                "video_url": video_url,
                                "file_size": video_file.stat().st_size,
                                "mtime": file_mtime,
                            }
            
            # Convert map to list and sort by scene number
            videos = list(scene_video_map.values())
            videos.sort(key=lambda v: v["scene_number"])
            
            logger.info(f"[Podcast] Returning {len(videos)} videos for user: {[v['scene_number'] for v in videos]}")
        else:
            logger.warning(f"[Podcast] Video directory does not exist: {ai_video_dir}")
        
        return {"videos": videos}
    
    except Exception as e:
        logger.exception(f"[Podcast] Error listing videos")
        return {"videos": []}


@router.post("/render/combine-videos", response_model=PodcastCombineVideosResponse)
async def combine_podcast_videos(
    request_obj: Request,
    request: PodcastCombineVideosRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Combine all scene videos into a single final podcast video.
    Returns task_id for polling.
    """
    user_id = require_authenticated_user(current_user)
    
    logger.info(f"[Podcast] Combining {len(request.scene_video_urls)} scene videos for project {request.project_id}")
    
    if not request.scene_video_urls:
        raise HTTPException(status_code=400, detail="No scene videos provided")
    
    # Create async task
    task_id = task_manager.create_task("podcast_combine_videos")
    
    # Extract token for authenticated URL building
    auth_token = None
    auth_header = request_obj.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        auth_token = auth_header.replace("Bearer ", "").strip()
    
    # Run video combination in thread pool executor to prevent blocking event loop
    # Submit directly to executor - this runs in a background thread and doesn't block
    # The executor handles the thread pool management automatically
    def handle_task_completion(future):
        """Callback to handle task completion and log errors."""
        try:
            future.result()  # This will raise if there was an exception
        except Exception as e:
            logger.error(f"[Podcast] Error in video combination task: {e}", exc_info=True)
    
    # Submit to executor - returns immediately, task runs in background thread
    future = _video_executor.submit(
        _execute_combine_videos_task,
        task_id,
        request.project_id,
        request.scene_video_urls,
        request.podcast_title,
        user_id,
        auth_token,
    )
    # Add callback to log errors without blocking
    future.add_done_callback(handle_task_completion)
    
    return PodcastCombineVideosResponse(
        task_id=task_id,
        status="pending",
        message="Video combination started. This may take a few minutes.",
    )


def _execute_combine_videos_task(
    task_id: str,
    project_id: str,
    scene_video_urls: list[str],
    podcast_title: str,
    user_id: str,
    auth_token: Optional[str] = None,
):
    """Background task to combine scene videos into final podcast."""
    try:
        task_manager.update_task_status(
            task_id, "processing", progress=10.0, message="Preparing scene videos..."
        )
        
        # Convert scene video URLs to local file paths
        scene_video_paths = []
        for video_url in scene_video_urls:
            # Extract filename from URL (e.g., /api/podcast/videos/scene_1_user_xxx.mp4)
            filename = video_url.split("/")[-1].split("?")[0]  # Remove query params
            video_path = PODCAST_VIDEOS_DIR / AI_VIDEO_SUBDIR / filename
            
            if not video_path.exists():
                logger.warning(f"[Podcast] Scene video not found: {video_path}")
                continue
                
            scene_video_paths.append(str(video_path))
        
        if not scene_video_paths:
            raise ValueError("No valid scene videos found to combine")
        
        logger.info(f"[Podcast] Found {len(scene_video_paths)} scene videos to combine")
        
        task_manager.update_task_status(
            task_id, "processing", progress=30.0, message="Combining videos..."
        )
        
        # Use dedicated PodcastVideoCombinationService
        final_videos_dir = PODCAST_VIDEOS_DIR / "Final_Videos"
        final_videos_dir.mkdir(parents=True, exist_ok=True)
        
        video_service = PodcastVideoCombinationService(output_dir=str(final_videos_dir))
        
        # Progress callback for task updates
        def progress_callback(progress: float, message: str):
            task_manager.update_task_status(
                task_id, "processing", progress=progress, message=message
            )
        
        task_manager.update_task_status(
            task_id, "processing", progress=50.0, message="Combining videos..."
        )
        
        # Combine videos using dedicated podcast service
        result = video_service.combine_videos(
            video_paths=scene_video_paths,
            podcast_title=podcast_title,
            fps=30,
            progress_callback=progress_callback,
        )
        
        video_filename = Path(result["video_path"]).name
        video_url = f"/api/podcast/final-videos/{video_filename}"
        if auth_token:
            video_url = f"{video_url}?token={quote(auth_token)}"
        
        logger.info(f"[Podcast] Final video combined: {video_filename}")
        
        result_data = {
            "video_url": video_url,
            "video_filename": video_filename,
            "duration": result.get("duration", 0),
            "file_size": result.get("file_size", 0),
        }
        
        task_manager.update_task_status(
            task_id,
            "completed",
            progress=100.0,
            message="Podcast video ready!",
            result=result_data,
        )
        
        # Save final video URL to project for persistence across reloads
        # Do this quickly and synchronously - database operations are fast
        try:
            from services.database import SessionLocal
            db = SessionLocal()
            try:
                service = PodcastService(db)
                service.update_project(user_id, project_id, final_video_url=video_url)
                db.commit()
                logger.info(f"[Podcast] Saved final video URL to project {project_id}: {video_url}")
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"[Podcast] Failed to save final video URL to project: {e}")
            # Don't fail the task if project update fails - video is still available via task result
        
        logger.info(f"[Podcast] Task {task_id} marked as completed successfully")
        
    except Exception as e:
        logger.exception(f"[Podcast] Failed to combine videos: {e}")
        error_msg = _extract_error_message(e)
        task_manager.update_task_status(
            task_id,
            "failed",
            progress=0.0,
            message=f"Video combination failed: {error_msg}",
            error=str(error_msg),
        )
        logger.error(f"[Podcast] Task {task_id} marked as failed: {error_msg}")


@router.get("/final-videos/{filename}")
async def serve_final_podcast_video(
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user_with_query_token),
):
    """Serve the final combined podcast video with authentication."""
    user_id = require_authenticated_user(current_user)
    
    final_videos_dir = PODCAST_VIDEOS_DIR / "Final_Videos"
    video_path = final_videos_dir / filename
    
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Basic security: ensure filename doesn't contain path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        filename=filename,
    )
