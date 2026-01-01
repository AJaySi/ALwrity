"""
Video extension endpoints.
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

logger = get_service_logger("video_studio.endpoints.extend")

router = APIRouter()


@router.post("/extend")
async def extend_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Video file to extend"),
    prompt: str = Form(..., description="Text prompt describing how to extend the video"),
    model: str = Form("wan-2.5", description="Model to use: 'wan-2.5', 'wan-2.2-spicy', or 'seedance-1.5-pro'"),
    audio: Optional[UploadFile] = File(None, description="Optional audio file to guide generation (WAN 2.5 only)"),
    negative_prompt: Optional[str] = Form(None, description="Negative prompt (WAN 2.5 only)"),
    resolution: str = Form("720p", description="Output resolution: 480p, 720p, or 1080p (1080p WAN 2.5 only)"),
    duration: int = Form(5, description="Duration of extended video in seconds (varies by model)"),
    enable_prompt_expansion: bool = Form(False, description="Enable prompt optimizer (WAN 2.5 only)"),
    generate_audio: bool = Form(True, description="Generate audio for extended video (Seedance 1.5 Pro only)"),
    camera_fixed: bool = Form(False, description="Fix camera position (Seedance 1.5 Pro only)"),
    seed: Optional[int] = Form(None, description="Random seed for reproducibility"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Extend video duration using WAN 2.5, WAN 2.2 Spicy, or Seedance 1.5 Pro video-extend.

    Takes a short video clip and extends it with motion/audio continuity.
    """
    try:
        user_id = require_authenticated_user(current_user)

        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")

        # Validate model-specific constraints
        if model in ("wan-2.2-spicy", "wavespeed-ai/wan-2.2-spicy/video-extend"):
            if duration not in [5, 8]:
                raise HTTPException(status_code=400, detail="WAN 2.2 Spicy only supports 5 or 8 second durations")
            if resolution not in ["480p", "720p"]:
                raise HTTPException(status_code=400, detail="WAN 2.2 Spicy only supports 480p or 720p resolution")
            if audio:
                raise HTTPException(status_code=400, detail="Audio is not supported for WAN 2.2 Spicy")
        elif model in ("seedance-1.5-pro", "bytedance/seedance-v1.5-pro/video-extend"):
            if duration < 4 or duration > 12:
                raise HTTPException(status_code=400, detail="Seedance 1.5 Pro only supports 4-12 second durations")
            if resolution not in ["480p", "720p"]:
                raise HTTPException(status_code=400, detail="Seedance 1.5 Pro only supports 480p or 720p resolution")
            if audio:
                raise HTTPException(status_code=400, detail="Audio upload is not supported for Seedance 1.5 Pro (use generate_audio instead)")
        else:
            # WAN 2.5 validation
            if duration < 3 or duration > 10:
                raise HTTPException(status_code=400, detail="WAN 2.5 duration must be between 3 and 10 seconds")
            if resolution not in ["480p", "720p", "1080p"]:
                raise HTTPException(status_code=400, detail="WAN 2.5 resolution must be 480p, 720p, or 1080p")

        # Initialize services
        video_service = VideoStudioService()
        asset_service = ContentAssetService(db)

        logger.info(f"[VideoStudio] Video extension request: user={user_id}, model={model}, duration={duration}s, resolution={resolution}")

        # Read video file
        video_data = await file.read()

        # Read audio file if provided (WAN 2.5 only)
        audio_data = None
        if audio:
            if model in ("wan-2.2-spicy", "wavespeed-ai/wan-2.2-spicy/video-extend", "seedance-1.5-pro", "bytedance/seedance-v1.5-pro/video-extend"):
                raise HTTPException(status_code=400, detail=f"Audio upload is not supported for {model} model")
            
            if not audio.content_type.startswith('audio/'):
                raise HTTPException(status_code=400, detail="Audio file must be an audio file")
            
            # Validate audio file size (max 15MB per documentation)
            audio_data = await audio.read()
            if len(audio_data) > 15 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Audio file must be less than 15MB")
            
            # Note: Audio duration validation (3-30s) would require parsing the audio file
            # This is handled by the API, but we could add it here if needed

        # Extend video
        result = await video_service.extend_video(
            video_data=video_data,
            prompt=prompt,
            model=model,
            audio_data=audio_data,
            negative_prompt=negative_prompt,
            resolution=resolution,
            duration=duration,
            enable_prompt_expansion=enable_prompt_expansion,
            generate_audio=generate_audio,
            camera_fixed=camera_fixed,
            seed=seed,
            user_id=user_id,
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Video extension failed: {result.get('error', 'Unknown error')}"
            )

        # Store extended version in asset library
        video_url = result.get("video_url")
        if video_url:
            asset_metadata = {
                "original_file": file.filename,
                "prompt": prompt,
                "duration": duration,
                "resolution": resolution,
                "generation_type": "extend",
                "model": result.get("model_used", "alibaba/wan-2.5/video-extend"),
            }

            asset_service.create_asset(
                user_id=user_id,
                filename=f"extended_{uuid.uuid4().hex[:8]}.mp4",
                file_url=video_url,
                asset_type=AssetType.VIDEO,
                source_module=AssetSource.VIDEO_STUDIO,
                asset_metadata=asset_metadata,
                cost=result.get("cost", 0),
                tags=["video_studio", "extend", "ai-extended"]
            )

        logger.info(f"[VideoStudio] Video extension successful: user={user_id}, url={video_url}")

        return {
            "success": True,
            "video_url": video_url,
            "cost": result.get("cost", 0),
            "duration": duration,
            "resolution": resolution,
            "model_used": result.get("model_used", "alibaba/wan-2.5/video-extend"),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VideoStudio] Video extension error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Video extension failed: {str(e)}")
