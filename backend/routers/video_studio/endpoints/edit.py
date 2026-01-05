"""
Edit Studio API endpoints.

Phase 1: Basic FFmpeg operations (Trim/Cut, Speed Control, Stabilization)
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.middleware.auth import get_current_user, require_authenticated_user
from backend.database.database import get_db
from backend.services.video_studio.edit_service import EditService

router = APIRouter()


@router.post("/edit/trim")
async def trim_video(
    file: UploadFile = File(..., description="Video file to trim"),
    start_time: float = Form(0.0, description="Start time in seconds"),
    end_time: Optional[float] = Form(None, description="End time in seconds (optional)"),
    max_duration: Optional[float] = Form(None, description="Maximum duration in seconds (trims if video is longer)"),
    trim_mode: str = Form("beginning", description="How to trim if max_duration is set: beginning, middle, end"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Trim video to specified duration or time range.
    
    Supports:
    - Trim by start/end time
    - Trim to maximum duration
    - Trim modes: beginning, middle, end
    """
    try:
        user_id = require_authenticated_user(current_user)
        
        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Validate trim_mode
        valid_modes = ["beginning", "middle", "end"]
        if trim_mode not in valid_modes:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid trim_mode. Must be one of: {', '.join(valid_modes)}"
            )
        
        # Initialize service
        edit_service = EditService()
        
        # Read video file
        video_data = await file.read()
        
        # Trim video
        result = await edit_service.trim_video(
            video_data=video_data,
            start_time=start_time,
            end_time=end_time,
            max_duration=max_duration,
            trim_mode=trim_mode,
            user_id=user_id,
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Video trimming failed: {str(e)}"
        )


@router.post("/edit/speed")
async def adjust_video_speed(
    file: UploadFile = File(..., description="Video file to adjust speed"),
    speed_factor: float = Form(..., description="Speed multiplier (0.25, 0.5, 1.0, 1.5, 2.0, 4.0)"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Adjust video playback speed.
    
    Supports:
    - Slow motion: 0.25x, 0.5x
    - Normal: 1.0x
    - Fast forward: 1.5x, 2.0x, 4.0x
    """
    try:
        user_id = require_authenticated_user(current_user)
        
        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Validate speed factor
        if speed_factor <= 0 or speed_factor > 4.0:
            raise HTTPException(
                status_code=400,
                detail="Speed factor must be between 0.25 and 4.0"
            )
        
        # Initialize service
        edit_service = EditService()
        
        # Read video file
        video_data = await file.read()
        
        # Adjust speed
        result = await edit_service.adjust_speed(
            video_data=video_data,
            speed_factor=speed_factor,
            user_id=user_id,
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Video speed adjustment failed: {str(e)}"
        )


@router.post("/edit/stabilize")
async def stabilize_video(
    file: UploadFile = File(..., description="Video file to stabilize"),
    smoothing: int = Form(10, description="Smoothing window size (1-100, default: 10)"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Stabilize shaky video using FFmpeg's vidstab filters.
    
    Uses two-pass stabilization:
    1. Detect camera shake (vidstabdetect)
    2. Apply stabilization (vidstabtransform)
    
    Note: Requires FFmpeg with vidstab filters enabled.
    """
    try:
        user_id = require_authenticated_user(current_user)
        
        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Validate smoothing
        if smoothing < 1 or smoothing > 100:
            raise HTTPException(
                status_code=400,
                detail="Smoothing must be between 1 and 100"
            )
        
        # Initialize service
        edit_service = EditService()
        
        # Read video file
        video_data = await file.read()
        
        # Stabilize video
        result = await edit_service.stabilize_video(
            video_data=video_data,
            smoothing=smoothing,
            user_id=user_id,
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Video stabilization failed: {str(e)}"
        )


@router.post("/edit/estimate-cost")
async def estimate_edit_cost(
    edit_type: str = Form(..., description="Type of edit: trim, speed, stabilize, text, volume, normalize, denoise"),
    duration: float = Form(10.0, description="Estimated video duration in seconds"),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Estimate cost for video editing operation.
    
    Note: FFmpeg-based operations are free.
    AI-based operations will have costs (Phase 3).
    """
    try:
        require_authenticated_user(current_user)
        
        edit_service = EditService()
        estimated_cost = edit_service.calculate_cost(edit_type, duration)
        
        return {
            "estimated_cost": estimated_cost,
            "edit_type": edit_type,
            "estimated_duration": duration,
            "pricing_model": "free",  # FFmpeg operations are free
            "note": "FFmpeg-based editing operations are free. AI-based operations may have costs.",
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cost estimation failed: {str(e)}"
        )


# ==================== Phase 2: Text & Audio Endpoints ====================

@router.post("/edit/text")
async def add_text_overlay(
    file: UploadFile = File(..., description="Video file to add text overlay"),
    text: str = Form(..., description="Text to overlay on video"),
    position: str = Form("center", description="Text position: top, center, bottom, top-left, top-right, bottom-left, bottom-right"),
    font_size: int = Form(48, description="Font size in pixels"),
    font_color: str = Form("white", description="Font color (e.g., white, #FFFFFF)"),
    background_color: str = Form("black@0.5", description="Background color with opacity (e.g., black@0.5)"),
    start_time: float = Form(0.0, description="When to start showing text (seconds)"),
    end_time: Optional[float] = Form(None, description="When to stop showing text (None = end of video)"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Add text overlay to video using FFmpeg drawtext filter.
    
    Supports:
    - Multiple positions (center, top, bottom, corners)
    - Custom font size and colors
    - Background box with opacity
    - Time-limited display (show text only during specific time range)
    """
    try:
        user_id = require_authenticated_user(current_user)
        
        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        valid_positions = ["top", "center", "bottom", "top-left", "top-right", "bottom-left", "bottom-right"]
        if position not in valid_positions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid position. Must be one of: {', '.join(valid_positions)}"
            )
        
        edit_service = EditService()
        video_data = await file.read()
        
        result = await edit_service.add_text_overlay(
            video_data=video_data,
            text=text,
            position=position,
            font_size=font_size,
            font_color=font_color,
            background_color=background_color,
            start_time=start_time,
            end_time=end_time,
            user_id=user_id,
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Text overlay failed: {str(e)}"
        )


@router.post("/edit/volume")
async def adjust_volume(
    file: UploadFile = File(..., description="Video file to adjust volume"),
    volume_factor: float = Form(..., description="Volume multiplier (0.0 = mute, 1.0 = original, 2.0 = double)"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Adjust video audio volume.
    
    Supports:
    - Mute (0.0)
    - Reduce volume (0.0 - 1.0)
    - Original (1.0)
    - Increase volume (1.0 - 3.0+)
    """
    try:
        user_id = require_authenticated_user(current_user)
        
        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        if volume_factor < 0:
            raise HTTPException(status_code=400, detail="Volume factor must be non-negative")
        
        if volume_factor > 5.0:
            raise HTTPException(status_code=400, detail="Volume factor cannot exceed 5.0 to prevent distortion")
        
        edit_service = EditService()
        video_data = await file.read()
        
        result = await edit_service.adjust_volume(
            video_data=video_data,
            volume_factor=volume_factor,
            user_id=user_id,
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Volume adjustment failed: {str(e)}"
        )


@router.post("/edit/normalize")
async def normalize_audio(
    file: UploadFile = File(..., description="Video file to normalize audio"),
    target_level: float = Form(-14.0, description="Target integrated loudness in LUFS (default: -14 for streaming)"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Normalize audio levels using EBU R128 standard (loudnorm filter).
    
    Common target levels:
    - -14 LUFS: YouTube, Spotify, general streaming
    - -16 LUFS: Podcast standard
    - -23 LUFS: Broadcast TV (EBU R128)
    - -24 LUFS: US Broadcast (ATSC A/85)
    """
    try:
        user_id = require_authenticated_user(current_user)
        
        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        if target_level > 0 or target_level < -50:
            raise HTTPException(
                status_code=400,
                detail="Target level must be between -50 and 0 LUFS"
            )
        
        edit_service = EditService()
        video_data = await file.read()
        
        result = await edit_service.normalize_audio(
            video_data=video_data,
            target_level=target_level,
            user_id=user_id,
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Audio normalization failed: {str(e)}"
        )


@router.post("/edit/denoise")
async def reduce_noise(
    file: UploadFile = File(..., description="Video file to reduce audio noise"),
    strength: float = Form(0.5, description="Noise reduction strength (0.0 - 1.0)"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Reduce audio noise using FFmpeg's noise reduction filters.
    
    Supports:
    - Light noise reduction (0.0 - 0.3): Subtle cleanup
    - Moderate reduction (0.3 - 0.6): Good for background noise
    - Strong reduction (0.6 - 1.0): Heavy noise, may affect audio quality
    """
    try:
        user_id = require_authenticated_user(current_user)
        
        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        if strength < 0 or strength > 1:
            raise HTTPException(
                status_code=400,
                detail="Strength must be between 0.0 and 1.0"
            )
        
        edit_service = EditService()
        video_data = await file.read()
        
        result = await edit_service.reduce_noise(
            video_data=video_data,
            noise_reduction_strength=strength,
            user_id=user_id,
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Noise reduction failed: {str(e)}"
        )
