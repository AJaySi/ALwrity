"""
Add Audio to Video endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import uuid

from ...database import get_db
from ...models.content_asset_models import AssetSource, AssetType
from ...services.video_studio.add_audio_to_video_service import AddAudioToVideoService
from ...services.asset_service import ContentAssetService
from ...utils.auth import get_current_user, require_authenticated_user
from ...utils.logger_utils import get_service_logger

logger = get_service_logger("video_studio.endpoints.add_audio_to_video")

router = APIRouter()


@router.post("/add-audio-to-video")
async def add_audio_to_video(
    background_tasks: BackgroundTasks,
    video_file: UploadFile = File(..., description="Source video for audio addition"),
    model: str = Form("hunyuan-video-foley", description="AI model to use: 'hunyuan-video-foley' or 'think-sound'"),
    prompt: Optional[str] = Form(None, description="Optional text prompt describing desired sounds (Hunyuan Video Foley)"),
    seed: Optional[int] = Form(None, description="Random seed for reproducibility (-1 for random)"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Add audio to video using AI models.
    
    Supports:
    1. Hunyuan Video Foley - Generate realistic Foley and ambient audio from video
       - Optional text prompt to describe desired sounds
       - Seed control for reproducibility
    
    2. Think Sound - (To be added)
    
    Args:
        video_file: Source video file
        model: AI model to use
        prompt: Optional text prompt describing desired sounds
        seed: Random seed for reproducibility
    """
    try:
        user_id = require_authenticated_user(current_user)
        
        if not video_file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Initialize services
        add_audio_service = AddAudioToVideoService()
        asset_service = ContentAssetService(db)
        
        logger.info(f"[AddAudioToVideo] Audio addition request: user={user_id}, model={model}, has_prompt={prompt is not None}")
        
        # Read video file
        video_data = await video_file.read()
        
        # Add audio to video
        result = await add_audio_service.add_audio(
            video_data=video_data,
            model=model,
            prompt=prompt,
            seed=seed,
            user_id=user_id,
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Adding audio failed: {result.get('error', 'Unknown error')}"
            )
        
        # Store processed video in asset library
        video_url = result.get("video_url")
        if video_url:
            asset_metadata = {
                "original_file": video_file.filename,
                "model": result.get("model_used", model),
                "has_prompt": prompt is not None,
                "prompt": prompt,
                "generation_type": "add_audio",
            }
            
            asset_service.create_asset(
                user_id=user_id,
                filename=f"audio_added_{uuid.uuid4().hex[:8]}.mp4",
                file_url=video_url,
                asset_type=AssetType.VIDEO,
                source_module=AssetSource.VIDEO_STUDIO,
                asset_metadata=asset_metadata,
                cost=result.get("cost", 0),
                tags=["video_studio", "audio_addition", "ai-processed"]
            )
        
        logger.info(f"[AddAudioToVideo] Audio addition successful: user={user_id}, url={video_url}")
        
        return {
            "success": True,
            "video_url": video_url,
            "cost": result.get("cost", 0),
            "model_used": result.get("model_used", model),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[AddAudioToVideo] Audio addition error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Adding audio failed: {str(e)}")


@router.post("/add-audio-to-video/estimate-cost")
async def estimate_add_audio_cost(
    model: str = Form("hunyuan-video-foley", description="AI model to use"),
    estimated_duration: float = Form(10.0, description="Estimated video duration in seconds", ge=0.0),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Estimate cost for adding audio to video operation.
    
    Returns estimated cost based on model and duration.
    """
    try:
        require_authenticated_user(current_user)
        
        add_audio_service = AddAudioToVideoService()
        estimated_cost = add_audio_service.calculate_cost(model, estimated_duration)
        
        # Build response based on model pricing
        if model == "think-sound":
            return {
                "estimated_cost": estimated_cost,
                "model": model,
                "estimated_duration": estimated_duration,
                "pricing_model": "per_video",
                "flat_rate": 0.05,
            }
        else:
            # Hunyuan Video Foley (per-second pricing)
            return {
                "estimated_cost": estimated_cost,
                "model": model,
                "estimated_duration": estimated_duration,
                "cost_per_second": 0.02,  # Estimated pricing
                "pricing_model": "per_second",
                "min_duration": 5.0,
                "max_duration": 600.0,  # 10 minutes max
                "min_charge": 0.02 * 5.0,
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[AddAudioToVideo] Failed to estimate cost: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to estimate cost: {str(e)}")
