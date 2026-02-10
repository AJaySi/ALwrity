"""
Background task for async video generation.
"""

from typing import Optional, Dict, Any
from api.story_writer.task_manager import task_manager
from services.video_studio import VideoStudioService
from utils.asset_tracker import save_asset_to_library
from utils.logger_utils import get_service_logger
from ..utils import extract_error_message

logger = get_service_logger("video_studio.tasks")


def execute_video_generation_task(
    task_id: str,
    operation_type: str,
    user_id: str,
    prompt: Optional[str] = None,
    image_data: Optional[bytes] = None,
    image_base64: Optional[str] = None,
    provider: str = "wavespeed",
    **kwargs,
):
    """Background task for async video generation with progress updates."""
    try:
        from services.llm_providers.main_video_generation import ai_video_generate
        
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
            message="Initializing video generation..."
        )
        
        # Call unified video generation with progress callback
        result = ai_video_generate(
            prompt=prompt,
            image_data=image_data,
            image_base64=image_base64,
            operation_type=operation_type,
            provider=provider,
            user_id=user_id,
            progress_callback=progress_callback,
            **kwargs
        )
        
        # Save file
        video_service = VideoStudioService()
        save_result = video_service._save_video_file(
            video_bytes=result["video_bytes"],
            operation_type=operation_type,
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
                    source_module="main_video_generation",
                    filename=save_result["filename"],
                    file_url=save_result["file_url"],
                    file_path=save_result["file_path"],
                    file_size=save_result["file_size"],
                    mime_type="video/mp4",
                    title=f"Video Studio: {operation_type.replace('-', ' ').title()}",
                    description=f"Generated video: {prompt[:100] if prompt else 'No prompt'}",
                    prompt=result.get("prompt", prompt or ""),
                    tags=["video_studio", operation_type],
                    provider=result.get("provider", provider),
                    model=result.get("model_name", kwargs.get("model", "unknown")),
                    cost=result.get("cost", 0.0),
                    asset_metadata={
                        "resolution": result.get("resolution", kwargs.get("resolution", "720p")),
                        "duration": result.get("duration", float(kwargs.get("duration", 5))),
                        "operation": operation_type,
                        "width": result.get("width", 1280),
                        "height": result.get("height", 720),
                    }
                )
                logger.info(f"[VideoStudio] Video saved to asset library")
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"[VideoStudio] Failed to save to asset library: {e}")
        
        # Update task with final result
        task_manager.update_task_status(
            task_id,
            "completed",
            progress=100.0,
            message="Video generation complete!",
            result={
                "video_url": save_result["file_url"],
                "cost": result.get("cost", 0.0),
                "duration": result.get("duration", float(kwargs.get("duration", 5))),
                "model": result.get("model_name", kwargs.get("model", "unknown")),
                "provider": result.get("provider", provider),
                "resolution": result.get("resolution", kwargs.get("resolution", "720p")),
                "width": result.get("width", 1280),
                "height": result.get("height", 720),
            }
        )
        
    except Exception as exc:
        logger.exception(f"[VideoStudio] Video generation failed: {exc}")
        error_msg = extract_error_message(exc)
        task_manager.update_task_status(
            task_id,
            "failed",
            error=error_msg,
            message=f"Video generation failed: {error_msg}"
        )
