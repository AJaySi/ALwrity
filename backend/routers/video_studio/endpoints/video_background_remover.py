"""
Video Background Remover endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import uuid

from ...database import get_db
from ...models.content_asset_models import AssetSource, AssetType
from ...services.video_studio.video_background_remover_service import VideoBackgroundRemoverService
from ...services.asset_service import ContentAssetService
from ...utils.auth import get_current_user, require_authenticated_user
from utils.logger_utils import get_service_logger

logger = get_service_logger("video_studio.endpoints.video_background_remover")

router = APIRouter()


@router.post("/video-background-remover")
async def remove_background(
    background_tasks: BackgroundTasks,
    video_file: UploadFile = File(..., description="Source video for background removal"),
    background_image_file: Optional[UploadFile] = File(None, description="Optional background image for replacement"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Remove or replace video background using WaveSpeed Video Background Remover.
    
    Features:
    - Clean matting and edge-aware blending
    - Natural compositing for realistic results
    - Optional background image replacement
    - Supports videos up to 10 minutes
    
    Args:
        video_file: Source video file
        background_image_file: Optional replacement background image
    """
    try:
        user_id = require_authenticated_user(current_user)
        
        if not video_file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Initialize services
        background_remover_service = VideoBackgroundRemoverService()
        asset_service = ContentAssetService(db)
        
        logger.info(f"[VideoBackgroundRemover] Background removal request: user={user_id}, has_background={background_image_file is not None}")
        
        # Read video file
        video_data = await video_file.read()
        
        # Read background image if provided
        background_image_data = None
        if background_image_file:
            if not background_image_file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="Background file must be an image")
            background_image_data = await background_image_file.read()
        
        # Remove/replace background
        result = await background_remover_service.remove_background(
            video_data=video_data,
            background_image_data=background_image_data,
            user_id=user_id,
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Background removal failed: {result.get('error', 'Unknown error')}"
            )
        
        # Store processed video in asset library
        video_url = result.get("video_url")
        if video_url:
            asset_metadata = {
                "original_file": video_file.filename,
                "has_background_replacement": result.get("has_background_replacement", False),
                "background_file": background_image_file.filename if background_image_file else None,
                "generation_type": "background_removal",
            }
            
            asset_service.create_asset(
                user_id=user_id,
                filename=f"bg_removed_{uuid.uuid4().hex[:8]}.mp4",
                file_url=video_url,
                asset_type=AssetType.VIDEO,
                source_module=AssetSource.VIDEO_STUDIO,
                asset_metadata=asset_metadata,
                cost=result.get("cost", 0),
                tags=["video_studio", "background_removal", "ai-processed"]
            )
        
        logger.info(f"[VideoBackgroundRemover] Background removal successful: user={user_id}, url={video_url}")
        
        return {
            "success": True,
            "video_url": video_url,
            "cost": result.get("cost", 0),
            "has_background_replacement": result.get("has_background_replacement", False),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VideoBackgroundRemover] Background removal error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Background removal failed: {str(e)}")


@router.post("/video-background-remover/estimate-cost")
async def estimate_background_removal_cost(
    estimated_duration: float = Form(10.0, description="Estimated video duration in seconds", ge=5.0),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Estimate cost for video background removal operation.
    
    Returns estimated cost based on duration.
    """
    try:
        require_authenticated_user(current_user)
        
        background_remover_service = VideoBackgroundRemoverService()
        estimated_cost = background_remover_service.calculate_cost(estimated_duration)
        
        return {
            "estimated_cost": estimated_cost,
            "estimated_duration": estimated_duration,
            "cost_per_second": 0.01,
            "pricing_model": "per_second",
            "min_duration": 0.0,
            "max_duration": 600.0,  # 10 minutes max
            "min_charge": 0.05,  # Minimum $0.05 for ≤5 seconds
            "max_charge": 6.00,  # Maximum $6.00 for 600 seconds
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VideoBackgroundRemover] Failed to estimate cost: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to estimate cost: {str(e)}")
