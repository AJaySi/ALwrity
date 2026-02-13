"""
Avatar generation endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import base64
import uuid

from ...database import get_db
from ...models.content_asset_models import AssetSource, AssetType
from ...services.video_studio import VideoStudioService
from ...services.video_studio.avatar_service import AvatarStudioService
from ...services.asset_service import ContentAssetService
from ...utils.auth import get_current_user, require_authenticated_user
from utils.logger_utils import get_service_logger
from api.story_writer.task_manager import task_manager
from ..tasks.avatar_generation import execute_avatar_generation_task

logger = get_service_logger("video_studio.endpoints.avatar")

router = APIRouter()


@router.post("/avatars")
async def generate_avatar_video(
    background_tasks: BackgroundTasks,
    avatar_file: UploadFile = File(..., description="Avatar/face image"),
    audio_file: Optional[UploadFile] = File(None, description="Audio file for lip sync"),
    video_file: Optional[UploadFile] = File(None, description="Source video for face swap"),
    text: Optional[str] = Form(None, description="Text to speak (alternative to audio)"),
    language: str = Form("en", description="Language for text-to-speech"),
    provider: str = Form("wavespeed", description="AI provider to use"),
    model: str = Form("wavespeed/mocha", description="Specific AI model to use"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Generate talking avatar video or perform face swap.

    Supports both text-to-speech and audio input for natural lip sync.
    """
    try:
        user_id = require_authenticated_user(current_user)

        # Validate inputs
        if not avatar_file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Avatar file must be an image")

        if not any([audio_file, video_file, text]):
            raise HTTPException(status_code=400, detail="Must provide audio file, video file, or text")

        # Initialize services
        video_service = VideoStudioService()
        asset_service = ContentAssetService(db)

        logger.info(f"[VideoStudio] Avatar generation request: user={user_id}, model={model}")

        # Read files
        avatar_data = await avatar_file.read()
        audio_data = await audio_file.read() if audio_file else None
        video_data = await video_file.read() if video_file else None

        # Generate avatar video
        result = await video_service.generate_avatar_video(
            avatar_data=avatar_data,
            audio_data=audio_data,
            video_data=video_data,
            text=text,
            language=language,
            provider=provider,
            model=model,
            user_id=user_id,
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Avatar generation failed: {result.get('error', 'Unknown error')}"
            )

        # Store in asset library if successful
        video_url = result.get("video_url")
        if video_url:
            asset_metadata = {
                "avatar_file": avatar_file.filename,
                "audio_file": audio_file.filename if audio_file else None,
                "video_file": video_file.filename if video_file else None,
                "text": text,
                "language": language,
                "provider": provider,
                "model": model,
                "generation_type": "avatar",
            }

            asset_service.create_asset(
                user_id=user_id,
                filename=f"avatar_{uuid.uuid4().hex[:8]}.mp4",
                file_url=video_url,
                asset_type=AssetType.VIDEO,
                source_module=AssetSource.VIDEO_STUDIO,
                asset_metadata=asset_metadata,
                cost=result.get("cost", 0),
                tags=["video_studio", "avatar", "ai-generated"]
            )

        logger.info(f"[VideoStudio] Avatar generation successful: user={user_id}, url={video_url}")

        return {
            "success": True,
            "video_url": video_url,
            "cost": result.get("cost", 0),
            "model_used": model,
            "provider": provider,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VideoStudio] Avatar generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Avatar generation failed: {str(e)}")


@router.post("/avatar/create-async")
async def create_avatar_async(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(..., description="Image file for avatar"),
    audio: UploadFile = File(..., description="Audio file for lip-sync"),
    resolution: str = Form("720p", description="Video resolution (480p or 720p)"),
    prompt: Optional[str] = Form(None, description="Optional prompt for expression/style"),
    mask_image: Optional[UploadFile] = File(None, description="Optional mask image (InfiniteTalk only)"),
    seed: Optional[int] = Form(None, description="Optional random seed"),
    model: str = Form("infinitetalk", description="Model to use: 'infinitetalk' or 'hunyuan-avatar'"),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Create talking avatar asynchronously with polling support.
    
    Upload a photo and audio to create a talking avatar with perfect lip-sync.
    Supports resolutions of 480p and 720p.
    - InfiniteTalk: up to 10 minutes long
    - Hunyuan Avatar: up to 2 minutes (120 seconds) long
    
    Returns task_id for polling. Frontend can poll /api/video-studio/task/{task_id}/status
    to get progress updates and final result.
    """
    try:
        user_id = require_authenticated_user(current_user)
        
        # Validate resolution
        if resolution not in ["480p", "720p"]:
            raise HTTPException(
                status_code=400,
                detail="Resolution must be '480p' or '720p'"
            )
        
        # Read image data
        image_data = await image.read()
        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="Image file is empty")
        
        # Read audio data
        audio_data = await audio.read()
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Audio file is empty")
        
        # Convert to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        # Add data URI prefix
        image_mime = image.content_type or "image/png"
        image_base64 = f"data:{image_mime};base64,{image_base64}"
        
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        audio_mime = audio.content_type or "audio/mpeg"
        audio_base64 = f"data:{audio_mime};base64,{audio_base64}"
        
        # Handle optional mask image
        mask_image_base64 = None
        if mask_image:
            mask_data = await mask_image.read()
            if len(mask_data) > 0:
                mask_base64 = base64.b64encode(mask_data).decode('utf-8')
                mask_mime = mask_image.content_type or "image/png"
                mask_image_base64 = f"data:{mask_mime};base64,{mask_base64}"
        
        # Create task
        task_id = task_manager.create_task("avatar_generation")
        
        # Validate model
        if model not in ["infinitetalk", "hunyuan-avatar"]:
            raise HTTPException(
                status_code=400,
                detail="Model must be 'infinitetalk' or 'hunyuan-avatar'"
            )
        
        # Start background task
        background_tasks.add_task(
            execute_avatar_generation_task,
            task_id=task_id,
            user_id=user_id,
            image_base64=image_base64,
            audio_base64=audio_base64,
            resolution=resolution,
            prompt=prompt,
            mask_image_base64=mask_image_base64,
            seed=seed,
            model=model,
        )
        
        logger.info(f"[AvatarStudio] Started async avatar generation: task_id={task_id}, user={user_id}")
        
        return {
            "task_id": task_id,
            "status": "pending",
            "message": f"Avatar generation started. This may take several minutes. Poll /api/video-studio/task/{task_id}/status for updates."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[AvatarStudio] Failed to start async avatar generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start avatar generation: {str(e)}")


@router.post("/avatar/estimate-cost")
async def estimate_avatar_cost(
    resolution: str = Form("720p", description="Video resolution (480p or 720p)"),
    estimated_duration: float = Form(10.0, description="Estimated video duration in seconds", ge=5.0, le=600.0),
    model: str = Form("infinitetalk", description="Model to use: 'infinitetalk' or 'hunyuan-avatar'"),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Estimate cost for talking avatar generation.
    
    Returns estimated cost based on resolution, duration, and model.
    """
    try:
        require_authenticated_user(current_user)
        
        # Validate resolution
        if resolution not in ["480p", "720p"]:
            raise HTTPException(
                status_code=400,
                detail="Resolution must be '480p' or '720p'"
            )
        
        # Validate model
        if model not in ["infinitetalk", "hunyuan-avatar"]:
            raise HTTPException(
                status_code=400,
                detail="Model must be 'infinitetalk' or 'hunyuan-avatar'"
            )
        
        # Validate duration for Hunyuan Avatar (max 120 seconds)
        if model == "hunyuan-avatar" and estimated_duration > 120:
            raise HTTPException(
                status_code=400,
                detail="Hunyuan Avatar supports maximum 120 seconds (2 minutes)"
            )
        
        avatar_service = AvatarStudioService()
        estimated_cost = avatar_service.calculate_cost_estimate(resolution, estimated_duration, model)
        
        # Return pricing info based on model
        if model == "hunyuan-avatar":
            cost_per_5_seconds = 0.15 if resolution == "480p" else 0.30
            return {
                "estimated_cost": estimated_cost,
                "resolution": resolution,
                "estimated_duration": estimated_duration,
                "model": model,
                "cost_per_5_seconds": cost_per_5_seconds,
                "pricing_model": "per_5_seconds",
                "max_duration": 120,
            }
        else:
            cost_per_second = 0.03 if resolution == "480p" else 0.06
            return {
                "estimated_cost": estimated_cost,
                "resolution": resolution,
                "estimated_duration": estimated_duration,
                "model": model,
                "cost_per_second": cost_per_second,
                "pricing_model": "per_second",
                "max_duration": 600,
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[AvatarStudio] Failed to estimate cost: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to estimate cost: {str(e)}")
