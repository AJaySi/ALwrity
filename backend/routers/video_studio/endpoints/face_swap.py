"""
Face Swap endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import uuid

from ...database import get_db
from ...models.content_asset_models import AssetSource, AssetType
from ...services.video_studio import VideoStudioService
from ...services.video_studio.face_swap_service import FaceSwapService
from ...services.asset_service import ContentAssetService
from ...utils.auth import get_current_user, require_authenticated_user
from ...utils.logger_utils import get_service_logger

logger = get_service_logger("video_studio.endpoints.face_swap")

router = APIRouter()


@router.post("/face-swap")
async def swap_face(
    background_tasks: BackgroundTasks,
    image_file: UploadFile = File(..., description="Reference image for character swap"),
    video_file: UploadFile = File(..., description="Source video for face swap"),
    model: str = Form("mocha", description="AI model to use: 'mocha' or 'video-face-swap'"),
    prompt: Optional[str] = Form(None, description="Optional prompt to guide the swap (MoCha only)"),
    resolution: str = Form("480p", description="Output resolution for MoCha (480p or 720p)"),
    seed: Optional[int] = Form(None, description="Random seed for reproducibility (MoCha only, -1 for random)"),
    target_gender: str = Form("all", description="Filter which faces to swap (video-face-swap only: all, female, male)"),
    target_index: int = Form(0, description="Select which face to swap (video-face-swap only: 0 = largest)"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Perform face/character swap using MoCha or Video Face Swap.
    
    Supports two models:
    1. MoCha (wavespeed-ai/wan-2.1/mocha) - Character replacement with motion preservation
       - Resolution: 480p ($0.04/s) or 720p ($0.08/s)
       - Max length: 120 seconds
       - Features: Prompt guidance, seed control
       
    2. Video Face Swap (wavespeed-ai/video-face-swap) - Simple face swap with multi-face support
       - Pricing: $0.01/s
       - Max length: 10 minutes (600 seconds)
       - Features: Gender filter, face index selection
    
    Requirements:
    - Image: Clear reference image (JPG/PNG, avoid WEBP)
    - Video: Source video (max 120s for MoCha, max 600s for video-face-swap)
    - Minimum charge: 5 seconds for both models
    """
    try:
        user_id = require_authenticated_user(current_user)

        # Validate file types
        if not image_file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Image file must be an image")
        
        if not video_file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="Video file must be a video")

        # Validate resolution
        if resolution not in ("480p", "720p"):
            raise HTTPException(
                status_code=400,
                detail="Resolution must be '480p' or '720p'"
            )

        # Initialize services
        face_swap_service = FaceSwapService()
        asset_service = ContentAssetService(db)

        logger.info(
            f"[FaceSwap] Face swap request: user={user_id}, "
            f"resolution={resolution}"
        )

        # Read files
        image_data = await image_file.read()
        video_data = await video_file.read()

        # Validate file sizes
        if len(image_data) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="Image file must be less than 10MB")
        
        if len(video_data) > 500 * 1024 * 1024:  # 500MB
            raise HTTPException(status_code=400, detail="Video file must be less than 500MB")

        # Perform face swap
        result = await face_swap_service.swap_face(
            image_data=image_data,
            video_data=video_data,
            model=model,
            prompt=prompt,
            resolution=resolution,
            seed=seed,
            target_gender=target_gender,
            target_index=target_index,
            user_id=user_id,
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Face swap failed: {result.get('error', 'Unknown error')}"
            )

        # Store in asset library
        video_url = result.get("video_url")
        if video_url:
            model_name = "wavespeed-ai/wan-2.1/mocha" if model == "mocha" else "wavespeed-ai/video-face-swap"
            
            asset_metadata = {
                "image_file": image_file.filename,
                "video_file": video_file.filename,
                "model": model,
                "operation_type": "face_swap",
            }
            
            if model == "mocha":
                asset_metadata.update({
                    "prompt": prompt,
                    "resolution": resolution,
                    "seed": seed,
                })
            else:  # video-face-swap
                asset_metadata.update({
                    "target_gender": target_gender,
                    "target_index": target_index,
                })

            asset_service.create_asset(
                user_id=user_id,
                filename=f"face_swap_{uuid.uuid4().hex[:8]}.mp4",
                file_url=video_url,
                asset_type=AssetType.VIDEO,
                source_module=AssetSource.VIDEO_STUDIO,
                asset_metadata=asset_metadata,
                cost=result.get("cost", 0),
                tags=["video_studio", "face_swap", "ai-generated"],
            )

        logger.info(f"[FaceSwap] Face swap successful: user={user_id}, url={video_url}")

        return {
            "success": True,
            "video_url": video_url,
            "cost": result.get("cost", 0),
            "model": model,
            "resolution": result.get("resolution"),
            "metadata": result.get("metadata", {}),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[FaceSwap] Face swap error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Face swap failed: {str(e)}")


@router.post("/face-swap/estimate-cost")
async def estimate_face_swap_cost(
    model: str = Form("mocha", description="AI model to use: 'mocha' or 'video-face-swap'"),
    resolution: str = Form("480p", description="Output resolution for MoCha (480p or 720p)"),
    estimated_duration: float = Form(10.0, description="Estimated video duration in seconds", ge=5.0),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Estimate cost for face swap operation.
    
    Returns estimated cost based on model, resolution (for MoCha), and duration.
    """
    try:
        require_authenticated_user(current_user)
        
        # Validate model
        if model not in ("mocha", "video-face-swap"):
            raise HTTPException(
                status_code=400,
                detail="Model must be 'mocha' or 'video-face-swap'"
            )
        
        # Validate resolution (only for MoCha)
        if model == "mocha":
            if resolution not in ("480p", "720p"):
                raise HTTPException(
                    status_code=400,
                    detail="Resolution must be '480p' or '720p' for MoCha"
                )
            max_duration = 120.0
        else:
            max_duration = 600.0  # 10 minutes for video-face-swap
        
        if estimated_duration > max_duration:
            raise HTTPException(
                status_code=400,
                detail=f"Estimated duration must be <= {max_duration} seconds for {model}"
            )
        
        face_swap_service = FaceSwapService()
        estimated_cost = face_swap_service.calculate_cost(model, resolution if model == "mocha" else None, estimated_duration)
        
        # Pricing info
        if model == "mocha":
            cost_per_second = 0.04 if resolution == "480p" else 0.08
            return {
                "estimated_cost": estimated_cost,
                "model": model,
                "resolution": resolution,
                "estimated_duration": estimated_duration,
                "cost_per_second": cost_per_second,
                "pricing_model": "per_second",
                "min_duration": 5.0,
                "max_duration": 120.0,
                "min_charge": cost_per_second * 5.0,
            }
        else:  # video-face-swap
            return {
                "estimated_cost": estimated_cost,
                "model": model,
                "estimated_duration": estimated_duration,
                "cost_per_second": 0.01,
                "pricing_model": "per_second",
                "min_duration": 5.0,
                "max_duration": 600.0,
                "min_charge": 0.05,  # $0.01 * 5 seconds
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[FaceSwap] Failed to estimate cost: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to estimate cost: {str(e)}")
