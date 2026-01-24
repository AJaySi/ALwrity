"""
Video transformation endpoints.
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
from utils.logger_utils import get_service_logger

logger = get_service_logger("video_studio.endpoints.transform")

router = APIRouter()


@router.post("/transform")
async def transform_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Video file to transform"),
    transform_type: str = Form(..., description="Type of transformation: format, aspect, speed, resolution, compress"),
    # Format conversion parameters
    output_format: Optional[str] = Form(None, description="Output format for format conversion (mp4, mov, webm, gif)"),
    codec: Optional[str] = Form(None, description="Video codec (libx264, libvpx-vp9, etc.)"),
    quality: Optional[str] = Form(None, description="Quality preset (high, medium, low)"),
    audio_codec: Optional[str] = Form(None, description="Audio codec (aac, mp3, opus, etc.)"),
    # Aspect ratio parameters
    target_aspect: Optional[str] = Form(None, description="Target aspect ratio (16:9, 9:16, 1:1, 4:5, 21:9)"),
    crop_mode: Optional[str] = Form("center", description="Crop mode for aspect conversion (center, letterbox)"),
    # Speed parameters
    speed_factor: Optional[float] = Form(None, description="Speed multiplier (0.25, 0.5, 1.0, 1.5, 2.0, 4.0)"),
    # Resolution parameters
    target_resolution: Optional[str] = Form(None, description="Target resolution (480p, 720p, 1080p, 1440p, 4k)"),
    maintain_aspect: bool = Form(True, description="Whether to maintain aspect ratio when scaling"),
    # Compression parameters
    target_size_mb: Optional[float] = Form(None, description="Target file size in MB for compression"),
    compress_quality: Optional[str] = Form(None, description="Quality preset for compression (high, medium, low)"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Transform video using FFmpeg/MoviePy (format, aspect, speed, resolution, compression).

    Supports:
    - Format conversion (MP4, MOV, WebM, GIF)
    - Aspect ratio conversion (16:9, 9:16, 1:1, 4:5, 21:9)
    - Speed adjustment (0.25x - 4x)
    - Resolution scaling (480p - 4K)
    - Compression (file size optimization)
    """
    try:
        user_id = require_authenticated_user(current_user)

        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")

        # Initialize services
        video_service = VideoStudioService()
        asset_service = ContentAssetService(db)

        logger.info(
            f"[VideoStudio] Video transformation request: "
            f"user={user_id}, type={transform_type}"
        )

        # Read video file
        video_data = await file.read()

        # Validate transform type
        valid_transform_types = ["format", "aspect", "speed", "resolution", "compress"]
        if transform_type not in valid_transform_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid transform_type. Must be one of: {', '.join(valid_transform_types)}"
            )

        # Transform video
        result = await video_service.transform_video(
            video_data=video_data,
            transform_type=transform_type,
            user_id=user_id,
            output_format=output_format,
            codec=codec,
            quality=quality,
            audio_codec=audio_codec,
            target_aspect=target_aspect,
            crop_mode=crop_mode,
            speed_factor=speed_factor,
            target_resolution=target_resolution,
            maintain_aspect=maintain_aspect,
            target_size_mb=target_size_mb,
            compress_quality=compress_quality,
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Video transformation failed: {result.get('error', 'Unknown error')}"
            )

        # Store transformed version in asset library
        video_url = result.get("video_url")
        if video_url:
            asset_metadata = {
                "original_file": file.filename,
                "transform_type": transform_type,
                "output_format": output_format,
                "target_aspect": target_aspect,
                "speed_factor": speed_factor,
                "target_resolution": target_resolution,
                "generation_type": "transformation",
            }

            asset_service.create_asset(
                user_id=user_id,
                filename=f"transformed_{uuid.uuid4().hex[:8]}.mp4",
                file_url=video_url,
                asset_type=AssetType.VIDEO,
                source_module=AssetSource.VIDEO_STUDIO,
                asset_metadata=asset_metadata,
                cost=result.get("cost", 0),
                tags=["video_studio", "transform", transform_type]
            )

        logger.info(f"[VideoStudio] Video transformation successful: user={user_id}, url={video_url}")

        return {
            "success": True,
            "video_url": video_url,
            "cost": result.get("cost", 0),
            "transform_type": transform_type,
            "metadata": result.get("metadata", {}),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VideoStudio] Video transformation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Video transformation failed: {str(e)}")
