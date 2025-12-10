"""
Podcast Maker API Router

API endpoints for podcast project persistence and management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from services.database import get_db
from middleware.auth_middleware import get_current_user
from services.podcast_service import PodcastService
from models.podcast_models import PodcastProject
from services.wavespeed.infinitetalk import animate_scene_with_voiceover
from services.story_writer.video_generation_service import StoryVideoGenerationService
from services.llm_providers.main_video_generation import track_video_usage
from services.subscription import PricingService
from services.subscription.preflight_validator import validate_scene_animation_operation
from api.story_writer.task_manager import task_manager
from api.story_writer.utils.auth import require_authenticated_user
from api.story_writer.utils.media_utils import load_story_image_bytes, load_story_audio_bytes
from services.llm_providers.main_text_generation import llm_text_gen
from services.story_writer.audio_generation_service import StoryAudioGenerationService
from utils.asset_tracker import save_asset_to_library
from models.story_models import StoryAudioResult
from loguru import logger

router = APIRouter(prefix="/api/podcast", tags=["Podcast Maker"])
AI_VIDEO_SUBDIR = Path("AI_Videos")
audio_service = StoryAudioGenerationService()


class PodcastProjectResponse(BaseModel):
    """Response model for podcast project."""
    id: int
    project_id: str
    user_id: str
    idea: str
    duration: int
    speakers: int
    budget_cap: float
    analysis: Optional[Dict[str, Any]] = None
    queries: Optional[List[Dict[str, Any]]] = None
    selected_queries: Optional[List[str]] = None
    research: Optional[Dict[str, Any]] = None
    raw_research: Optional[Dict[str, Any]] = None
    estimate: Optional[Dict[str, Any]] = None
    script_data: Optional[Dict[str, Any]] = None
    render_jobs: Optional[List[Dict[str, Any]]] = None
    knobs: Optional[Dict[str, Any]] = None
    research_provider: Optional[str] = None
    show_script_editor: bool = False
    show_render_queue: bool = False
    current_step: Optional[str] = None
    status: str = "draft"
    is_favorite: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PodcastAnalyzeRequest(BaseModel):
    """Request model for podcast idea analysis."""
    idea: str = Field(..., description="Podcast topic or idea")
    duration: int = Field(default=10, description="Target duration in minutes")
    speakers: int = Field(default=1, description="Number of speakers")


class PodcastAnalyzeResponse(BaseModel):
    """Response model for podcast idea analysis."""
    audience: str
    content_type: str
    top_keywords: list[str]
    suggested_outlines: list[Dict[str, Any]]
    title_suggestions: list[str]


class PodcastScriptRequest(BaseModel):
    """Request model for podcast script generation."""
    idea: str = Field(..., description="Podcast idea or topic")
    duration_minutes: int = Field(default=10, description="Target duration in minutes")
    speakers: int = Field(default=1, description="Number of speakers")
    research: Optional[Dict[str, Any]] = Field(None, description="Optional research payload to ground the script")


class PodcastSceneLine(BaseModel):
    speaker: str
    text: str


class PodcastScene(BaseModel):
    id: str
    title: str
    duration: int
    lines: list[PodcastSceneLine]
    approved: bool = False


class PodcastScriptResponse(BaseModel):
    scenes: list[PodcastScene]


class PodcastAudioRequest(BaseModel):
    """Generate TTS for a podcast scene."""
    scene_id: str
    scene_title: str
    text: str
    voice_id: Optional[str] = "Wise_Woman"
    speed: Optional[float] = 1.0
    volume: Optional[float] = 1.0
    pitch: Optional[float] = 0.0
    emotion: Optional[str] = "neutral"


class PodcastAudioResponse(BaseModel):
    scene_id: str
    scene_title: str
    audio_filename: str
    audio_url: str
    provider: str
    model: str
    voice_id: str
    text_length: int
    file_size: int
    cost: float


class PodcastProjectListResponse(BaseModel):
    """Response model for project list."""
    projects: List[PodcastProjectResponse]
    total: int
    limit: int
    offset: int


class CreateProjectRequest(BaseModel):
    """Request model for creating a project."""
    project_id: str = Field(..., description="Unique project ID")
    idea: str = Field(..., description="Episode idea or URL")
    duration: int = Field(..., description="Duration in minutes")
    speakers: int = Field(default=1, description="Number of speakers")
    budget_cap: float = Field(default=50.0, description="Budget cap in USD")


class UpdateProjectRequest(BaseModel):
    """Request model for updating project state."""
    analysis: Optional[Dict[str, Any]] = None
    queries: Optional[List[Dict[str, Any]]] = None
    selected_queries: Optional[List[str]] = None
    research: Optional[Dict[str, Any]] = None
    raw_research: Optional[Dict[str, Any]] = None
    estimate: Optional[Dict[str, Any]] = None
    script_data: Optional[Dict[str, Any]] = None
    render_jobs: Optional[List[Dict[str, Any]]] = None
    knobs: Optional[Dict[str, Any]] = None
    research_provider: Optional[str] = None
    show_script_editor: Optional[bool] = None
    show_render_queue: Optional[bool] = None
    current_step: Optional[str] = None
    status: Optional[str] = None


@router.post("/projects", response_model=PodcastProjectResponse, status_code=201)
async def create_project(
    request: CreateProjectRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Create a new podcast project."""
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        service = PodcastService(db)
        
        # Check if project_id already exists for this user
        existing = service.get_project(user_id, request.project_id)
        if existing:
            raise HTTPException(status_code=400, detail="Project ID already exists")
        
        project = service.create_project(
            user_id=user_id,
            project_id=request.project_id,
            idea=request.idea,
            duration=request.duration,
            speakers=request.speakers,
            budget_cap=request.budget_cap,
        )
        
        return PodcastProjectResponse.model_validate(project)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating project: {str(e)}")


@router.post("/analyze", response_model=PodcastAnalyzeResponse)
async def analyze_podcast_idea(
    request: PodcastAnalyzeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Analyze a podcast idea and return podcast-oriented outlines, keywords, and titles.
    This uses the shared LLM provider but with a podcast-specific prompt (not story format).
    """
    user_id = require_authenticated_user(current_user)

    prompt = f"""
You are an expert podcast producer. Given a podcast idea, craft concise podcast-ready assets
that sound like episode plans (not fiction stories).

Podcast Idea: "{request.idea}"
Duration: ~{request.duration} minutes
Speakers: {request.speakers} (host + optional guest)

Return JSON with:
- audience: short target audience description
- content_type: podcast style/format
- top_keywords: 5 podcast-relevant keywords/phrases
- suggested_outlines: 2 items, each with title (<=60 chars) and 4-6 short segments (bullet-friendly, factual)
- title_suggestions: 3 concise episode titles (no cliffhanger storytelling)

Requirements:
- Keep language factual, actionable, and suited for spoken audio.
- Avoid narrative fiction tone; focus on insights, hooks, objections, and takeaways.
- Prefer 2024-2025 context when relevant.
"""

    try:
        raw = llm_text_gen(prompt=prompt, user_id=user_id, json_struct=None)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")

    # Normalize response (accept dict or JSON string)
    import json

    if isinstance(raw, str):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="LLM returned non-JSON output")
    elif isinstance(raw, dict):
        data = raw
    else:
        raise HTTPException(status_code=500, detail="Unexpected LLM response format")

    audience = data.get("audience") or "Growth-focused professionals"
    content_type = data.get("content_type") or "Interview + insights"
    top_keywords = data.get("top_keywords") or []
    suggested_outlines = data.get("suggested_outlines") or []
    title_suggestions = data.get("title_suggestions") or []

    return PodcastAnalyzeResponse(
        audience=audience,
        content_type=content_type,
        top_keywords=top_keywords,
        suggested_outlines=suggested_outlines,
        title_suggestions=title_suggestions,
    )


@router.post("/script", response_model=PodcastScriptResponse)
async def generate_podcast_script(
    request: PodcastScriptRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Generate a podcast script outline (scenes + lines) using podcast-oriented prompting.
    """
    user_id = require_authenticated_user(current_user)

    research_snippet = ""
    if request.research:
        try:
            key_insights = request.research.get("keyword_analysis", {}).get("key_insights") or []
            sources = request.research.get("sources", []) or []
            top_sources = [s.get("url") for s in sources[:3] if s.get("url")]
            research_snippet = f"Key insights: {key_insights}. Top sources: {top_sources}"
        except Exception:
            research_snippet = ""

    prompt = f"""
You are an expert podcast script planner. Create concise, podcast-ready scenes (not narrative fiction).

Podcast Idea: "{request.idea}"
Duration: ~{request.duration_minutes} minutes
Speakers: {request.speakers} (Host + optional Guest)
Research (if any): {research_snippet}

Return JSON with:
- scenes: array of scenes. Each scene has:
  - id: string
  - title: short scene title (<= 60 chars)
  - duration: duration in seconds (aim for evenly split across total duration)
  - lines: array of {{"speaker": "...", "text": "..."}}, 3-6 lines per scene, succinct and spoken-friendly.

Requirements:
- Keep language conversational, factual, and action-oriented (no cliffhangers or fictional storytelling).
- Include hooks, objections, counters, and takeaways where relevant.
- Cite no URLs in the lines; keep them clean for narration.
- Ensure total duration aligns with ~{request.duration_minutes} minutes across all scenes.
"""

    try:
        raw = llm_text_gen(prompt=prompt, user_id=user_id, json_struct=None)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Script generation failed: {exc}")

    import json

    if isinstance(raw, str):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="LLM returned non-JSON output")
    elif isinstance(raw, dict):
        data = raw
    else:
        raise HTTPException(status_code=500, detail="Unexpected LLM response format")

    scenes_data = data.get("scenes") or []
    if not isinstance(scenes_data, list):
        raise HTTPException(status_code=500, detail="LLM response missing scenes array")

    # Normalize scenes
    scenes: list[PodcastScene] = []
    for idx, scene in enumerate(scenes_data):
        title = scene.get("title") or f"Scene {idx + 1}"
        duration = int(scene.get("duration") or max(30, (request.duration_minutes * 60) // max(1, len(scenes_data))))
        lines_raw = scene.get("lines") or []
        lines: list[PodcastSceneLine] = []
        for line in lines_raw:
            speaker = line.get("speaker") or ("Host" if len(lines) % request.speakers == 0 else "Guest")
            text = line.get("text") or ""
            if text:
                lines.append(PodcastSceneLine(speaker=speaker, text=text))
        scenes.append(
            PodcastScene(
                id=scene.get("id") or f"scene-{idx + 1}",
                title=title,
                duration=duration,
                lines=lines,
                approved=False,
            )
        )

    return PodcastScriptResponse(scenes=scenes)


@router.post("/audio", response_model=PodcastAudioResponse)
async def generate_podcast_audio(
    request: PodcastAudioRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate AI audio for a podcast scene using shared audio service.
    """
    user_id = require_authenticated_user(current_user)

    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    try:
        result: StoryAudioResult = audio_service.generate_ai_audio(
            scene_number=0,
            scene_title=request.scene_title,
            text=request.text.strip(),
            user_id=user_id,
            voice_id=request.voice_id or "Wise_Woman",
            speed=request.speed or 1.0,
            volume=request.volume or 1.0,
            pitch=request.pitch or 0.0,
            emotion=request.emotion or "neutral",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {exc}")

    # Save to asset library (podcast module)
    try:
        if result.get("audio_url"):
            save_asset_to_library(
                db=db,
                user_id=user_id,
                asset_type="audio",
                source_module="podcast_maker",
                filename=result.get("audio_filename", ""),
                file_url=result.get("audio_url", ""),
                file_path=result.get("audio_path"),
                file_size=result.get("file_size"),
                mime_type="audio/mpeg",
                title=f"{request.scene_title} - Podcast",
                description="Podcast scene narration",
                tags=["podcast", "audio", request.scene_id],
                provider=result.get("provider"),
                model=result.get("model"),
                cost=result.get("cost"),
                asset_metadata={
                    "scene_id": request.scene_id,
                    "scene_title": request.scene_title,
                    "status": "completed",
                },
            )
    except Exception as e:
        logger.warning(f"[Podcast] Failed to save audio asset: {e}")

    return PodcastAudioResponse(
        scene_id=request.scene_id,
        scene_title=request.scene_title,
        audio_filename=result.get("audio_filename", ""),
        audio_url=result.get("audio_url", ""),
        provider=result.get("provider", "wavespeed"),
        model=result.get("model", "minimax/speech-02-hd"),
        voice_id=result.get("voice_id", request.voice_id or "Wise_Woman"),
        text_length=result.get("text_length", len(request.text)),
        file_size=result.get("file_size", 0),
        cost=result.get("cost", 0.0),
    )


@router.get("/task/{task_id}/status")
async def podcast_task_status(task_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Expose task status under podcast namespace (reuses shared task manager)."""
    require_authenticated_user(current_user)
    return task_manager.get_task_status(task_id)

@router.get("/projects/{project_id}", response_model=PodcastProjectResponse)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get a podcast project by ID."""
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        service = PodcastService(db)
        project = service.get_project(user_id, project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return PodcastProjectResponse.model_validate(project)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching project: {str(e)}")


@router.put("/projects/{project_id}", response_model=PodcastProjectResponse)
async def update_project(
    project_id: str,
    request: UpdateProjectRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Update a podcast project state."""
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        service = PodcastService(db)
        
        # Convert request to dict, excluding None values
        updates = request.model_dump(exclude_unset=True)
        
        project = service.update_project(user_id, project_id, **updates)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return PodcastProjectResponse.model_validate(project)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating project: {str(e)}")


@router.get("/projects", response_model=PodcastProjectListResponse)
async def list_projects(
    status: Optional[str] = Query(None, description="Filter by status"),
    favorites_only: bool = Query(False, description="Only favorites"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    order_by: str = Query("updated_at", description="Order by: updated_at or created_at"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """List user's podcast projects."""
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        if order_by not in ["updated_at", "created_at"]:
            raise HTTPException(status_code=400, detail="order_by must be 'updated_at' or 'created_at'")
        
        service = PodcastService(db)
        projects, total = service.list_projects(
            user_id=user_id,
            status=status,
            favorites_only=favorites_only,
            limit=limit,
            offset=offset,
            order_by=order_by,
        )
        
        return PodcastProjectListResponse(
            projects=[PodcastProjectResponse.model_validate(p) for p in projects],
            total=total,
            limit=limit,
            offset=offset,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing projects: {str(e)}")


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Delete a podcast project."""
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        service = PodcastService(db)
        deleted = service.delete_project(user_id, project_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting project: {str(e)}")


@router.post("/projects/{project_id}/favorite", response_model=PodcastProjectResponse)
async def toggle_favorite(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Toggle favorite status of a project."""
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        service = PodcastService(db)
        project = service.toggle_favorite(user_id, project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return PodcastProjectResponse.model_validate(project)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling favorite: {str(e)}")


class PodcastVideoGenerationRequest(BaseModel):
    """Request model for podcast video generation."""
    project_id: str = Field(..., description="Podcast project ID")
    scene_id: str = Field(..., description="Scene ID")
    scene_title: str = Field(..., description="Scene title")
    audio_url: str = Field(..., description="URL to the generated audio file")
    avatar_image_url: Optional[str] = Field(None, description="URL to avatar image (optional)")
    resolution: str = Field("720p", description="Video resolution (480p or 720p)")
    prompt: Optional[str] = Field(None, description="Optional animation prompt override")


class PodcastVideoGenerationResponse(BaseModel):
    """Response model for podcast video generation."""
    task_id: str
    status: str
    message: str


def _load_audio_bytes_from_url(audio_url: str) -> bytes:
    """Load audio bytes from URL."""
    import requests
    
    # Try to resolve as story audio first
    audio_bytes = load_story_audio_bytes(audio_url)
    if audio_bytes:
        return audio_bytes
    
    # Fallback: try direct HTTP request
    try:
        response = requests.get(audio_url, timeout=30)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        logger.warning(f"Failed to load audio from URL {audio_url}: {e}")
    
    raise HTTPException(status_code=404, detail=f"Audio file not found: {audio_url}")


def _load_image_bytes_from_url(image_url: str) -> bytes:
    """Load image bytes from URL."""
    import requests
    
    # Try to resolve as story image first
    image_bytes = load_story_image_bytes(image_url)
    if image_bytes:
        return image_bytes
    
    # Fallback: try direct HTTP request
    try:
        response = requests.get(image_url, timeout=30)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        logger.warning(f"Failed to load image from URL {image_url}: {e}")
    
    raise HTTPException(status_code=404, detail=f"Image file not found: {image_url}")


def _execute_podcast_video_task(
    task_id: str,
    request: PodcastVideoGenerationRequest,
    user_id: str,
    image_bytes: bytes,
    audio_bytes: bytes,
    auth_token: Optional[str] = None,
):
    """Background task to generate InfiniteTalk video for podcast scene."""
    try:
        task_manager.update_task_status(
            task_id, "processing", progress=5.0, message="Submitting to WaveSpeed InfiniteTalk..."
        )

        # Extract scene number from scene_id
        scene_number_match = re.search(r'\d+', request.scene_id)
        scene_number = int(scene_number_match.group()) if scene_number_match else 0

        # Prepare scene data for animation
        scene_data = {
            "scene_number": scene_number,
            "title": request.scene_title,
            "scene_id": request.scene_id,
        }
        story_context = {
            "project_id": request.project_id,
            "type": "podcast",
        }

        animation_result = animate_scene_with_voiceover(
            image_bytes=image_bytes,
            audio_bytes=audio_bytes,
            scene_data=scene_data,
            story_context=story_context,
            user_id=user_id,
            resolution=request.resolution or "720p",
            prompt_override=request.prompt,
            image_mime="image/png",
            audio_mime="audio/mpeg",
        )

        task_manager.update_task_status(
            task_id, "processing", progress=80.0, message="Saving video file..."
        )

        base_dir = Path(__file__).parent.parent.parent.parent
        ai_video_dir = base_dir / "story_videos" / AI_VIDEO_SUBDIR
        ai_video_dir.mkdir(parents=True, exist_ok=True)
        video_service = StoryVideoGenerationService(output_dir=str(ai_video_dir))

        save_result = video_service.save_scene_video(
            video_bytes=animation_result["video_bytes"],
            scene_number=scene_number,
            user_id=user_id,
        )
        video_filename = save_result["video_filename"]
        video_url = f"/api/story/videos/ai/{video_filename}"
        if auth_token:
            video_url = f"{video_url}?token={quote(auth_token)}"

        usage_info = track_video_usage(
            user_id=user_id,
            provider=animation_result["provider"],
            model_name=animation_result["model_name"],
            prompt=animation_result["prompt"],
            video_bytes=animation_result["video_bytes"],
            cost_override=animation_result["cost"],
        )

        task_manager.update_task_status(
            task_id,
            "completed",
            progress=100.0,
            message="Video generation complete!",
            result={
                "video_url": video_url,
                "video_filename": video_filename,
                "cost": animation_result["cost"],
                "duration": animation_result["duration"],
                "provider": animation_result["provider"],
                "model": animation_result["model_name"],
            },
        )

        logger.info(
            f"[Podcast] Video generation completed for project {request.project_id}, scene {request.scene_id}"
        )

    except Exception as exc:
        logger.error(f"[Podcast] Video generation failed: {exc}", exc_info=True)
        task_manager.update_task_status(
            task_id, "failed", error=str(exc), message=f"Video generation failed: {exc}"
        )


@router.post("/render/video", response_model=PodcastVideoGenerationResponse)
async def generate_podcast_video(
    request_obj: Request,
    request: PodcastVideoGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Generate video for a podcast scene using WaveSpeed InfiniteTalk (avatar image + audio).
    Returns task_id for polling since InfiniteTalk can take up to 10 minutes.
    """
    user_id = require_authenticated_user(current_user)

    logger.info(
        f"[Podcast] Starting video generation for project {request.project_id}, scene {request.scene_id}"
    )

    # Load audio bytes
    audio_bytes = _load_audio_bytes_from_url(request.audio_url)

    # Load image bytes (use avatar if provided, otherwise generate default)
    if request.avatar_image_url:
        image_bytes = _load_image_bytes_from_url(request.avatar_image_url)
    else:
        # Generate a default avatar image or use a placeholder
        # For now, raise an error if no avatar is provided
        raise HTTPException(
            status_code=400,
            detail="Avatar image is required for video generation. Please upload an avatar image.",
        )

    # Validate subscription limits
    db = next(get_db())
    try:
        pricing_service = PricingService(db)
        validate_scene_animation_operation(pricing_service=pricing_service, user_id=user_id)
    finally:
        db.close()

    # Extract token for authenticated URL building
    auth_token = None
    auth_header = request_obj.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        auth_token = auth_header.replace("Bearer ", "").strip()

    # Create async task
    task_id = task_manager.create_task("podcast_video_generation")
    background_tasks.add_task(
        _execute_podcast_video_task,
        task_id=task_id,
        request=request,
        user_id=user_id,
        image_bytes=image_bytes,
        audio_bytes=audio_bytes,
        auth_token=auth_token,
    )

    return PodcastVideoGenerationResponse(
        task_id=task_id,
        status="pending",
        message="Video generation started. This may take up to 10 minutes.",
    )


class PodcastVideoGenerationRequest(BaseModel):
    """Request model for podcast video generation."""
    project_id: str = Field(..., description="Podcast project ID")
    scene_id: str = Field(..., description="Scene ID")
    scene_title: str = Field(..., description="Scene title")
    audio_url: str = Field(..., description="URL to the generated audio file")
    avatar_image_url: Optional[str] = Field(None, description="URL to avatar image (optional)")
    resolution: str = Field("720p", description="Video resolution (480p or 720p)")
    prompt: Optional[str] = Field(None, description="Optional animation prompt override")


class PodcastVideoGenerationResponse(BaseModel):
    """Response model for podcast video generation."""
    task_id: str
    status: str
    message: str


def _load_audio_bytes_from_url(audio_url: str) -> bytes:
    """Load audio bytes from URL."""
    import requests
    
    # Try to resolve as story audio first
    audio_bytes = load_story_audio_bytes(audio_url)
    if audio_bytes:
        return audio_bytes
    
    # Fallback: try direct HTTP request
    try:
        response = requests.get(audio_url, timeout=30)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        logger.warning(f"Failed to load audio from URL {audio_url}: {e}")
    
    raise HTTPException(status_code=404, detail=f"Audio file not found: {audio_url}")


def _load_image_bytes_from_url(image_url: str) -> bytes:
    """Load image bytes from URL."""
    import requests
    
    # Try to resolve as story image first
    image_bytes = load_story_image_bytes(image_url)
    if image_bytes:
        return image_bytes
    
    # Fallback: try direct HTTP request
    try:
        response = requests.get(image_url, timeout=30)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        logger.warning(f"Failed to load image from URL {image_url}: {e}")
    
    raise HTTPException(status_code=404, detail=f"Image file not found: {image_url}")


def _execute_podcast_video_task(
    task_id: str,
    request: PodcastVideoGenerationRequest,
    user_id: str,
    image_bytes: bytes,
    audio_bytes: bytes,
    auth_token: Optional[str] = None,
):
    """Background task to generate InfiniteTalk video for podcast scene."""
    try:
        task_manager.update_task_status(
            task_id, "processing", progress=5.0, message="Submitting to WaveSpeed InfiniteTalk..."
        )

        # Extract scene number from scene_id
        scene_number_match = re.search(r'\d+', request.scene_id)
        scene_number = int(scene_number_match.group()) if scene_number_match else 0

        # Prepare scene data for animation
        scene_data = {
            "scene_number": scene_number,
            "title": request.scene_title,
            "scene_id": request.scene_id,
        }
        story_context = {
            "project_id": request.project_id,
            "type": "podcast",
        }

        animation_result = animate_scene_with_voiceover(
            image_bytes=image_bytes,
            audio_bytes=audio_bytes,
            scene_data=scene_data,
            story_context=story_context,
            user_id=user_id,
            resolution=request.resolution or "720p",
            prompt_override=request.prompt,
            image_mime="image/png",
            audio_mime="audio/mpeg",
        )

        task_manager.update_task_status(
            task_id, "processing", progress=80.0, message="Saving video file..."
        )

        base_dir = Path(__file__).parent.parent.parent.parent
        ai_video_dir = base_dir / "story_videos" / AI_VIDEO_SUBDIR
        ai_video_dir.mkdir(parents=True, exist_ok=True)
        video_service = StoryVideoGenerationService(output_dir=str(ai_video_dir))

        save_result = video_service.save_scene_video(
            video_bytes=animation_result["video_bytes"],
            scene_number=scene_number,
            user_id=user_id,
        )
        video_filename = save_result["video_filename"]
        video_url = f"/api/story/videos/ai/{video_filename}"
        if auth_token:
            video_url = f"{video_url}?token={quote(auth_token)}"

        usage_info = track_video_usage(
            user_id=user_id,
            provider=animation_result["provider"],
            model_name=animation_result["model_name"],
            prompt=animation_result["prompt"],
            video_bytes=animation_result["video_bytes"],
            cost_override=animation_result["cost"],
        )

        task_manager.update_task_status(
            task_id,
            "completed",
            progress=100.0,
            message="Video generation complete!",
            result={
                "video_url": video_url,
                "video_filename": video_filename,
                "cost": animation_result["cost"],
                "duration": animation_result["duration"],
                "provider": animation_result["provider"],
                "model": animation_result["model_name"],
            },
        )

        logger.info(
            f"[Podcast] Video generation completed for project {request.project_id}, scene {request.scene_id}"
        )

    except Exception as exc:
        logger.error(f"[Podcast] Video generation failed: {exc}", exc_info=True)
        task_manager.update_task_status(
            task_id, "failed", error=str(exc), message=f"Video generation failed: {exc}"
        )


@router.post("/render/video", response_model=PodcastVideoGenerationResponse)
async def generate_podcast_video(
    request_obj: Request,
    request: PodcastVideoGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Generate video for a podcast scene using WaveSpeed InfiniteTalk (avatar image + audio).
    Returns task_id for polling since InfiniteTalk can take up to 10 minutes.
    """
    user_id = require_authenticated_user(current_user)

    logger.info(
        f"[Podcast] Starting video generation for project {request.project_id}, scene {request.scene_id}"
    )

    # Load audio bytes
    audio_bytes = _load_audio_bytes_from_url(request.audio_url)

    # Load image bytes (use avatar if provided, otherwise generate default)
    if request.avatar_image_url:
        image_bytes = _load_image_bytes_from_url(request.avatar_image_url)
    else:
        # Generate a default avatar image or use a placeholder
        # For now, raise an error if no avatar is provided
        raise HTTPException(
            status_code=400,
            detail="Avatar image is required for video generation. Please upload an avatar image.",
        )

    # Validate subscription limits
    db = next(get_db())
    try:
        pricing_service = PricingService(db)
        validate_scene_animation_operation(pricing_service=pricing_service, user_id=user_id)
    finally:
        db.close()

    # Extract token for authenticated URL building
    auth_token = None
    auth_header = request_obj.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        auth_token = auth_header.replace("Bearer ", "").strip()

    # Create async task
    task_id = task_manager.create_task("podcast_video_generation")
    background_tasks.add_task(
        _execute_podcast_video_task,
        task_id=task_id,
        request=request,
        user_id=user_id,
        image_bytes=image_bytes,
        audio_bytes=audio_bytes,
        auth_token=auth_token,
    )

    return PodcastVideoGenerationResponse(
        task_id=task_id,
        status="pending",
        message="Video generation started. This may take up to 10 minutes.",
    )

