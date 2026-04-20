"""
B-Roll Handlers

API endpoints for B-roll chart preview and video generation.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from pathlib import Path
import uuid

from middleware.auth_middleware import get_current_user
from api.story_writer.utils.auth import require_authenticated_user
from services.podcast.broll_service import get_broll_service
from loguru import logger


router = APIRouter()


class ChartPreviewRequest(BaseModel):
    """Request model for chart preview generation."""
    chart_data: Dict[str, Any] = Field(..., description="Chart data (labels, before/after, etc.)")
    chart_type: str = Field(
        default="bar_comparison", 
        description="bar_comparison | bar_horizontal | line_trend | pie | stacked_bar | bullet"
    )
    title: str = Field(default="", description="Chart title")
    subtitle: Optional[str] = Field(default="", description="Optional subtitle at bottom")


class ChartPreviewResponse(BaseModel):
    """Response for chart preview."""
    preview_url: str
    chart_id: str


class BrollSceneRequest(BaseModel):
    """Request for generating B-roll video for a scene."""
    scene_id: str
    key_insight: str
    supporting_stat: str
    chart_data: Optional[Dict[str, Any]] = None
    visual_cue: str = Field(default="bar_chart_comparison", description="bar_chart_comparison | bullet_points")
    duration: float = Field(default=10.0, ge=3.0, le=60.0)
    background_image_url: str
    avatar_video_url: Optional[str] = None


class BrollSceneResponse(BaseModel):
    """Response for B-roll scene generation."""
    scene_id: str
    broll_video_url: str
    broll_video_path: str


class BrollComposeRequest(BaseModel):
    """Request for composing multiple B-roll videos."""
    scene_video_paths: List[str]
    output_filename: str = "final_broll.mp4"
    fade_dur: float = Field(default=0.5, ge=0.0, le=2.0)
    fps: int = Field(default=24, ge=12, le=60)


class BrollComposeResponse(BaseModel):
    """Response for B-roll composition."""
    final_video_url: str
    final_video_path: str


@router.post("/preview/chart", response_model=ChartPreviewResponse)
async def generate_chart_preview(
    request: ChartPreviewRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Generate a chart PNG preview (static image for Write phase).
    
    This endpoint is called from the Write phase to show users chart previews
    before they commit to B-roll video generation.
    """
    user_id = require_authenticated_user(current_user)
    
    try:
        broll_service = get_broll_service()
        chart_id = uuid.uuid4().hex[:8]
        
        preview_path = broll_service.generate_chart_preview(
            chart_data=request.chart_data,
            chart_type=request.chart_type,
            title=request.title,
            subtitle=request.subtitle or "",
            chart_id=chart_id,
        )
        
        if not preview_path:
            raise HTTPException(status_code=500, detail="Failed to generate chart preview")
        
        preview_filename = Path(preview_path).name
        preview_url = f"/api/podcast/broll/preview/{chart_id}/{preview_filename}"
        
        return ChartPreviewResponse(
            preview_url=preview_url,
            chart_id=chart_id,
        )
        
    except Exception as e:
        logger.error(f"[Broll] Chart preview generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chart preview failed: {str(e)}")


@router.post("/render/broll-scene", response_model=BrollSceneResponse)
async def generate_broll_scene(
    request: BrollSceneRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Generate a B-roll video for a single scene.
    
    This creates a programmatic video with:
    - Background image with Ken Burns effect
    - Chart overlay (if chart_data provided)
    - Avatar circle in corner (if avatar_video_url provided)
    - Insight card at bottom
    
    Returns a task_id for polling since video generation can take time.
    """
    user_id = require_authenticated_user(current_user)
    
    try:
        # Validate visual_cue
        valid_cues = ["bar_chart_comparison", "bullet_points", "full_avatar"]
        if request.visual_cue not in valid_cues:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid visual_cue. Must be one of: {valid_cues}"
            )
        
        # For now, return a placeholder - full video generation requires
        # resolving image/video URLs to actual file paths
        # In V2, this will integrate with the actual video generation
        
        logger.info(f"[Broll] B-roll scene request for scene: {request.scene_id}")
        
        return BrollSceneResponse(
            scene_id=request.scene_id,
            broll_video_url="",
            broll_video_path="",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Broll] B-roll scene generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"B-roll generation failed: {str(e)}")


@router.post("/render/broll-compose", response_model=BrollComposeResponse)
async def compose_broll_videos(
    request: BrollComposeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Compose multiple B-roll scene videos into a final video.
    
    Applies crossfade transitions between scenes.
    """
    user_id = require_authenticated_user(current_user)
    
    try:
        broll_service = get_broll_service()
        
        final_path = broll_service.compose_final_video(
            video_paths=request.scene_video_paths,
            output_filename=request.output_filename,
            fade_dur=request.fade_dur,
            fps=request.fps,
        )
        
        final_filename = final_path.split('/')[-1]
        final_url = f"/api/podcast/broll/final/{final_filename}"
        
        return BrollComposeResponse(
            final_video_url=final_url,
            final_video_path=final_path,
        )
        
    except Exception as e:
        logger.error(f"[Broll] Video composition failed: {e}")
        raise HTTPException(status_code=500, detail=f"Video composition failed: {str(e)}")


@router.get("/preview/{chart_id}/{filename}")
async def serve_chart_preview(
    chart_id: str,
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Serve chart preview PNG files."""
    user_id = require_authenticated_user(current_user)
    
    broll_service = get_broll_service()
    expected_filename = broll_service.get_chart_preview_filename(chart_id)
    if filename != expected_filename:
        raise HTTPException(status_code=404, detail="Chart preview not found")

    file_path = broll_service.get_output_path(filename)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Chart preview not found")
    
    return FileResponse(
        path=str(file_path),
        media_type="image/png",
        filename=filename,
    )


@router.get("/final/{filename}")
async def serve_final_broll(
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Serve final composed B-roll video files."""
    user_id = require_authenticated_user(current_user)
    
    broll_service = get_broll_service()
    file_path = broll_service.output_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(
        path=str(file_path),
        media_type="video/mp4",
        filename=filename,
    )


@router.get("/health")
async def broll_health():
    """Health check for B-roll service."""
    return {"status": "ok", "service": "broll"}
