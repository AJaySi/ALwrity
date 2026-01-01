"""
Background task for async avatar generation.
"""

from typing import Optional
from api.story_writer.task_manager import task_manager
from services.video_studio.avatar_service import AvatarStudioService
from services.video_studio import VideoStudioService
from utils.asset_tracker import save_asset_to_library
from utils.logger_utils import get_service_logger
from ..utils import extract_error_message

logger = get_service_logger("video_studio.tasks.avatar")


async def execute_avatar_generation_task(
    task_id: str,
    user_id: str,
    image_base64: str,
    audio_base64: str,
    resolution: str = "720p",
    prompt: Optional[str] = None,
    mask_image_base64: Optional[str] = None,
    seed: Optional[int] = None,
    model: str = "infinitetalk",
):
    """Background task for async avatar generation with progress updates."""
    try:
        # Progress callback that updates task status
        def progress_callback(progress: float, message: str):
            task_manager.update_task_status(
                task_id,
                "processing",
                progress=progress,
                message=message
            )
        
        # Update initial status
        task_manager.update_task_status(
            task_id,
            "processing",
            progress=5.0,
            message="Initializing avatar generation..."
        )
        
        # Create avatar service
        avatar_service = AvatarStudioService()
        
        # Generate avatar video
        task_manager.update_task_status(
            task_id,
            "processing",
            progress=20.0,
            message=f"Submitting request to {model}..."
        )
        
        result = await avatar_service.create_talking_avatar(
            image_base64=image_base64,
            audio_base64=audio_base64,
            resolution=resolution,
            prompt=prompt,
            mask_image_base64=mask_image_base64,
            seed=seed,
            user_id=user_id,
            model=model,
            progress_callback=progress_callback,
        )
        
        task_manager.update_task_status(
            task_id,
            "processing",
            progress=90.0,
            message="Saving video file..."
        )
        
        # Save file
        video_service = VideoStudioService()
        save_result = video_service._save_video_file(
            video_bytes=result["video_bytes"],
            operation_type="talking-avatar",
            user_id=user_id,
        )
        
        # Save to asset library
        try:
            from services.database import get_db
            db = next(get_db())
            try:
                save_asset_to_library(
                    db=db,
                    user_id=user_id,
                    asset_type="video",
                    source_module="video_studio",
                    filename=save_result["filename"],
                    file_url=save_result["file_url"],
                    file_path=save_result["file_path"],
                    file_size=save_result["file_size"],
                    mime_type="video/mp4",
                    title="Video Studio: Talking Avatar",
                    description=f"Talking avatar video: {prompt[:100] if prompt else 'No prompt'}",
                    prompt=result.get("prompt", prompt or ""),
                    tags=["video_studio", "avatar", "talking_avatar"],
                    provider=result.get("provider", "wavespeed"),
                    model=result.get("model_name", "wavespeed-ai/infinitetalk"),
                    cost=result.get("cost", 0.0),
                    asset_metadata={
                        "resolution": result.get("resolution", resolution),
                        "duration": result.get("duration", 5.0),
                        "operation": "talking-avatar",
                        "width": result.get("width", 1280),
                        "height": result.get("height", 720),
                    }
                )
                logger.info(f"[AvatarStudio] Video saved to asset library")
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"[AvatarStudio] Failed to save to asset library: {e}")
        
        # Update task with final result
        task_manager.update_task_status(
            task_id,
            "completed",
            progress=100.0,
            message="Avatar generation complete!",
            result={
                "video_url": save_result["file_url"],
                "cost": result.get("cost", 0.0),
                "duration": result.get("duration", 5.0),
                "model": result.get("model_name", "wavespeed-ai/infinitetalk"),
                "provider": result.get("provider", "wavespeed"),
                "resolution": result.get("resolution", resolution),
                "width": result.get("width", 1280),
                "height": result.get("height", 720),
            }
        )
        
    except Exception as exc:
        error_message = extract_error_message(exc)
        logger.error(f"[AvatarStudio] Avatar generation failed: {error_message}", exc_info=True)
        task_manager.update_task_status(
            task_id,
            "failed",
            progress=0.0,
            message=f"Avatar generation failed: {error_message}",
            error=error_message
        )
