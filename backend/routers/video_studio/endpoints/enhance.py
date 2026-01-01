"""
Video enhancement endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import uuid

from ...database import get_db
from ...models.content_asset_models import AssetSource, AssetType
from ...services.video_studio import VideoStudioService
from ...services.asset_service import ContentAssetService
from ...utils.auth import get_current_user, require_authenticated_user
from ...utils.logger_utils import get_service_logger

logger = get_service_logger("video_studio.endpoints.enhance")

router = APIRouter()


@router.post("/enhance")
async def enhance_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Video file to enhance"),
    enhancement_type: str = Form(..., description="Type of enhancement: upscale, stabilize, colorize, etc"),
    target_resolution: Optional[str] = Form(None, description="Target resolution for upscale"),
    provider: str = Form("wavespeed", description="AI provider to use"),
    model: str = Form("wavespeed/flashvsr", description="Specific AI model to use"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Enhance existing video using AI models.

    Supports upscaling, stabilization, colorization, and other enhancements.
    """
    try:
        user_id = require_authenticated_user(current_user)

        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")

        # Initialize services
        video_service = VideoStudioService()
        asset_service = ContentAssetService(db)

        logger.info(f"[VideoStudio] Video enhancement request: user={user_id}, type={enhancement_type}, model={model}")

        # Read video file
        video_data = await file.read()

        # Enhance video
        result = await video_service.enhance_video(
            video_data=video_data,
            enhancement_type=enhancement_type,
            target_resolution=target_resolution,
            provider=provider,
            model=model,
            user_id=user_id,
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Video enhancement failed: {result.get('error', 'Unknown error')}"
            )

        # Store enhanced version in asset library
        video_url = result.get("video_url")
        if video_url:
            asset_metadata = {
                "original_file": file.filename,
                "enhancement_type": enhancement_type,
                "target_resolution": target_resolution,
                "provider": provider,
                "model": model,
                "generation_type": "enhancement",
            }

            asset_service.create_asset(
                user_id=user_id,
                filename=f"enhanced_{uuid.uuid4().hex[:8]}.mp4",
                file_url=video_url,
                asset_type=AssetType.VIDEO,
                source_module=AssetSource.VIDEO_STUDIO,
                asset_metadata=asset_metadata,
                cost=result.get("cost", 0),
                tags=["video_studio", "enhancement", "ai-enhanced"]
            )

        logger.info(f"[VideoStudio] Video enhancement successful: user={user_id}, url={video_url}")

        return {
            "success": True,
            "video_url": video_url,
            "cost": result.get("cost", 0),
            "enhancement_type": enhancement_type,
            "model_used": model,
            "provider": provider,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VideoStudio] Video enhancement error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Video enhancement failed: {str(e)}")


@router.post("/enhance/estimate-cost")
async def estimate_enhance_cost(
    target_resolution: str = Form("1080p", description="Target resolution (720p, 1080p, 2k, 4k)"),
    estimated_duration: float = Form(10.0, description="Estimated video duration in seconds", ge=5.0),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Estimate cost for video enhancement operation.
    
    Returns estimated cost based on target resolution and duration.
    """
    try:
        require_authenticated_user(current_user)
        
        # Validate resolution
        if target_resolution not in ("720p", "1080p", "2k", "4k"):
            raise HTTPException(
                status_code=400,
                detail="Target resolution must be '720p', '1080p', '2k', or '4k'"
            )
        
        # FlashVSR pricing: $0.06-$0.16 per 5 seconds based on resolution
        pricing = {
            "720p": 0.06 / 5,   # $0.012 per second
            "1080p": 0.09 / 5,  # $0.018 per second
            "2k": 0.12 / 5,     # $0.024 per second
            "4k": 0.16 / 5,     # $0.032 per second
        }
        
        cost_per_second = pricing.get(target_resolution.lower(), pricing["1080p"])
        estimated_cost = max(5.0, estimated_duration) * cost_per_second  # Minimum 5 seconds
        
        return {
            "estimated_cost": estimated_cost,
            "target_resolution": target_resolution,
            "estimated_duration": estimated_duration,
            "cost_per_second": cost_per_second,
            "pricing_model": "per_second",
            "min_duration": 5.0,
            "max_duration": 600.0,  # 10 minutes max
            "min_charge": cost_per_second * 5.0,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VideoStudio] Failed to estimate cost: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to estimate cost: {str(e)}")