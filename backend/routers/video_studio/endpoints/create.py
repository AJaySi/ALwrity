"""
Create video endpoints: text-to-video and image-to-video generation.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import uuid

from services.database import get_db
from models.content_asset_models import AssetSource, AssetType
from services.video_studio import VideoStudioService
from services.content_asset_service import ContentAssetService
from middleware.auth_middleware import get_current_user
from utils.auth_utils import require_authenticated_user
from utils.logger_utils import get_service_logger
from api.story_writer.task_manager import task_manager
from ..tasks.video_generation import execute_video_generation_task

logger = get_service_logger("video_studio.endpoints.create")

router = APIRouter()


@router.post("/generate")
async def generate_video(
    background_tasks: BackgroundTasks,
    prompt: str = Form(..., description="Text description for video generation"),
    negative_prompt: Optional[str] = Form(None, description="What to avoid in the video"),
    duration: int = Form(5, description="Video duration in seconds", ge=1, le=10),
    resolution: str = Form("720p", description="Video resolution"),
    aspect_ratio: str = Form("16:9", description="Video aspect ratio"),
    motion_preset: str = Form("medium", description="Motion intensity"),
    provider: str = Form("wavespeed", description="AI provider to use"),
    model: str = Form("hunyuan-video-1.5", description="Specific AI model to use"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Generate video from text description using AI models.

    Supports multiple providers and models for optimal quality and cost.
    """
    try:
        user_id = require_authenticated_user(current_user)

        # Initialize services
        video_service = VideoStudioService()
        asset_service = ContentAssetService(db)

        logger.info(f"[VideoStudio] Text-to-video request: user={user_id}, model={model}, duration={duration}s")

        # Generate video
        result = await video_service.generate_text_to_video(
            prompt=prompt,
            negative_prompt=negative_prompt,
            duration=duration,
            resolution=resolution,
            aspect_ratio=aspect_ratio,
            motion_preset=motion_preset,
            provider=provider,
            model=model,
            user_id=user_id,
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Video generation failed: {result.get('error', 'Unknown error')}"
            )

        # Store in asset library if successful
        video_url = result.get("video_url")
        if video_url:
            asset_metadata = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "duration": duration,
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
                "motion_preset": motion_preset,
                "provider": provider,
                "model": model,
                "generation_type": "text-to-video",
            }

            asset_service.create_asset(
                user_id=user_id,
                filename=f"video_{uuid.uuid4().hex[:8]}.mp4",
                file_url=video_url,
                asset_type=AssetType.VIDEO,
                source_module=AssetSource.VIDEO_STUDIO,
                asset_metadata=asset_metadata,
                cost=result.get("cost", 0),
                tags=["video_studio", "text-to-video", "ai-generated"]
            )

        logger.info(f"[VideoStudio] Video generated successfully: user={user_id}, url={video_url}")

        return {
            "success": True,
            "video_url": video_url,
            "cost": result.get("cost", 0),
            "estimated_duration": result.get("estimated_duration", duration),
            "model_used": model,
            "provider": provider,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VideoStudio] Text-to-video error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")


@router.post("/transform")
async def transform_to_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Image file to transform"),
    prompt: Optional[str] = Form(None, description="Optional text prompt to guide transformation"),
    duration: int = Form(5, description="Video duration in seconds", ge=1, le=10),
    resolution: str = Form("720p", description="Video resolution"),
    aspect_ratio: str = Form("16:9", description="Video aspect ratio"),
    motion_preset: str = Form("medium", description="Motion intensity"),
    provider: str = Form("wavespeed", description="AI provider to use"),
    model: str = Form("alibaba/wan-2.5", description="Specific AI model to use"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Transform image to video using AI models.

    Supports various motion presets and durations for dynamic video creation.
    """
    try:
        user_id = require_authenticated_user(current_user)

        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Initialize services
        video_service = VideoStudioService()
        asset_service = ContentAssetService(db)

        logger.info(f"[VideoStudio] Image-to-video request: user={user_id}, model={model}, duration={duration}s")

        # Read image file
        image_data = await file.read()

        # Generate video
        result = await video_service.generate_image_to_video(
            image_data=image_data,
            prompt=prompt,
            duration=duration,
            resolution=resolution,
            aspect_ratio=aspect_ratio,
            motion_preset=motion_preset,
            provider=provider,
            model=model,
            user_id=user_id,
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Video transformation failed: {result.get('error', 'Unknown error')}"
            )

        # Store in asset library if successful
        video_url = result.get("video_url")
        if video_url:
            asset_metadata = {
                "original_image": file.filename,
                "prompt": prompt,
                "duration": duration,
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
                "motion_preset": motion_preset,
                "provider": provider,
                "model": model,
                "generation_type": "image-to-video",
            }

            asset_service.create_asset(
                user_id=user_id,
                filename=f"video_{uuid.uuid4().hex[:8]}.mp4",
                file_url=video_url,
                asset_type=AssetType.VIDEO,
                source_module=AssetSource.VIDEO_STUDIO,
                asset_metadata=asset_metadata,
                cost=result.get("cost", 0),
                tags=["video_studio", "image-to-video", "ai-generated"]
            )

        logger.info(f"[VideoStudio] Video transformation successful: user={user_id}, url={video_url}")

        return {
            "success": True,
            "video_url": video_url,
            "cost": result.get("cost", 0),
            "estimated_duration": result.get("estimated_duration", duration),
            "model_used": model,
            "provider": provider,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VideoStudio] Image-to-video error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Video transformation failed: {str(e)}")


@router.post("/generate-async")
async def generate_video_async(
    background_tasks: BackgroundTasks,
    prompt: Optional[str] = Form(None, description="Text description for video generation"),
    image: Optional[UploadFile] = File(None, description="Image file for image-to-video"),
    operation_type: str = Form("text-to-video", description="Operation type: text-to-video or image-to-video"),
    negative_prompt: Optional[str] = Form(None, description="What to avoid in the video"),
    duration: int = Form(5, description="Video duration in seconds", ge=1, le=10),
    resolution: str = Form("720p", description="Video resolution"),
    aspect_ratio: str = Form("16:9", description="Video aspect ratio"),
    motion_preset: str = Form("medium", description="Motion intensity"),
    provider: str = Form("wavespeed", description="AI provider to use"),
    model: str = Form("alibaba/wan-2.5", description="Specific AI model to use"),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Generate video asynchronously with polling support.
    
    Returns task_id for polling. Frontend can poll /api/video-studio/task/{task_id}/status
    to get progress updates and final result.
    """
    try:
        user_id = require_authenticated_user(current_user)
        
        # Validate operation type
        if operation_type not in ["text-to-video", "image-to-video"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid operation_type: {operation_type}. Must be 'text-to-video' or 'image-to-video'"
            )
        
        # Validate inputs based on operation type
        if operation_type == "text-to-video" and not prompt:
            raise HTTPException(
                status_code=400,
                detail="prompt is required for text-to-video generation"
            )
        
        if operation_type == "image-to-video" and not image:
            raise HTTPException(
                status_code=400,
                detail="image file is required for image-to-video generation"
            )
        
        # Read image data if provided
        image_data = None
        if image:
            image_data = await image.read()
            if len(image_data) == 0:
                raise HTTPException(status_code=400, detail="Image file is empty")
        
        # Create task
        task_id = task_manager.create_task("video_generation")
        
        # Prepare kwargs
        kwargs = {
            "duration": duration,
            "resolution": resolution,
            "model": model,
        }
        if negative_prompt:
            kwargs["negative_prompt"] = negative_prompt
        if aspect_ratio:
            kwargs["aspect_ratio"] = aspect_ratio
        if motion_preset:
            kwargs["motion_preset"] = motion_preset
        
        # Start background task
        background_tasks.add_task(
            execute_video_generation_task,
            task_id=task_id,
            operation_type=operation_type,
            user_id=user_id,
            prompt=prompt,
            image_data=image_data,
            provider=provider,
            **kwargs
        )
        
        logger.info(f"[VideoStudio] Started async video generation: task_id={task_id}, operation={operation_type}, user={user_id}")
        
        return {
            "task_id": task_id,
            "status": "pending",
            "message": f"Video generation started. This may take several minutes. Poll /api/video-studio/task/{task_id}/status for updates."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VideoStudio] Failed to start async video generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start video generation: {str(e)}")
