"""
Podcast Maker API Router

API endpoints for podcast project persistence and management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from services.database import get_db
from middleware.auth_middleware import get_current_user, get_current_user_with_query_token
from services.podcast_service import PodcastService
from models.podcast_models import PodcastProject
from services.wavespeed.infinitetalk import animate_scene_with_voiceover
from services.story_writer.video_generation_service import StoryVideoGenerationService
from services.llm_providers.main_image_generation import generate_image
from services.llm_providers.main_video_generation import track_video_usage
from services.subscription import PricingService
from services.subscription.preflight_validator import validate_scene_animation_operation
from api.story_writer.task_manager import task_manager
from api.story_writer.utils.auth import require_authenticated_user
# Podcast-specific media loading functions (no dependency on story_writer)
from services.llm_providers.main_text_generation import llm_text_gen
from services.story_writer.audio_generation_service import StoryAudioGenerationService
from utils.asset_tracker import save_asset_to_library
from models.story_models import StoryAudioResult
from loguru import logger
from services.blog_writer.research.exa_provider import ExaResearchProvider
from types import SimpleNamespace
import tempfile
import os
import uuid

router = APIRouter(prefix="/api/podcast", tags=["Podcast Maker"])
AI_VIDEO_SUBDIR = Path("AI_Videos")
# Initialize audio service with podcast_audio directory
# router.py is at: backend/api/podcast/router.py
# parents[0] = backend/api/podcast/
# parents[1] = backend/api/
# parents[2] = backend/
BASE_DIR = Path(__file__).resolve().parents[2]  # backend/
PODCAST_AUDIO_DIR = (BASE_DIR / "podcast_audio").resolve()
PODCAST_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
PODCAST_IMAGES_DIR = (BASE_DIR / "podcast_images").resolve()
PODCAST_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
audio_service = StoryAudioGenerationService(output_dir=str(PODCAST_AUDIO_DIR))


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
    exa_suggested_config: Optional[Dict[str, Any]] = None


class PodcastScriptRequest(BaseModel):
    """Request model for podcast script generation."""
    idea: str = Field(..., description="Podcast idea or topic")
    duration_minutes: int = Field(default=10, description="Target duration in minutes")
    speakers: int = Field(default=1, description="Number of speakers")
    research: Optional[Dict[str, Any]] = Field(None, description="Optional research payload to ground the script")


class PodcastSceneLine(BaseModel):
    speaker: str
    text: str
    emphasis: Optional[bool] = False


class PodcastScene(BaseModel):
    id: str
    title: str
    duration: int
    lines: list[PodcastSceneLine]
    approved: bool = False
    emotion: Optional[str] = None
    imageUrl: Optional[str] = None  # Generated image URL for video generation


class PodcastExaConfig(BaseModel):
    """Exa config for podcast research."""
    exa_search_type: Optional[str] = Field(default="auto", description="auto | keyword | neural")
    exa_category: Optional[str] = None
    exa_include_domains: List[str] = []
    exa_exclude_domains: List[str] = []
    max_sources: int = 8
    include_statistics: Optional[bool] = False
    date_range: Optional[str] = Field(default=None, description="last_month | last_3_months | last_year | all_time")

    @model_validator(mode="after")
    def validate_domains(self):
        if self.exa_include_domains and self.exa_exclude_domains:
            # Exa API does not allow both include and exclude domains together with contents
            # Prefer include_domains and drop exclude_domains
            self.exa_exclude_domains = []
        return self


class PodcastExaResearchRequest(BaseModel):
    """Request for podcast research using Exa directly (no blog writer)."""
    topic: str
    queries: List[str]
    exa_config: Optional[PodcastExaConfig] = None


class PodcastExaSource(BaseModel):
    title: str = ""
    url: str = ""
    excerpt: str = ""
    published_at: Optional[str] = None
    highlights: Optional[List[str]] = None
    summary: Optional[str] = None
    source_type: Optional[str] = None
    index: Optional[int] = None


class PodcastExaResearchResponse(BaseModel):
    sources: List[PodcastExaSource]
    search_queries: List[str] = []
    cost: Optional[Dict[str, Any]] = None
    search_type: Optional[str] = None
    provider: str = "exa"
    content: Optional[str] = None


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
    english_normalization: Optional[bool] = False  # Better number reading for statistics


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
- exa_suggested_config: suggested Exa search options to power research (keep conservative defaults to control cost), with:
  - exa_search_type: "auto" | "neural" | "keyword" (prefer "auto" unless clearly news-heavy)
  - exa_category: one of ["research paper","news","company","github","tweet","personal site","pdf","financial report","linkedin profile"]
  - exa_include_domains: up to 3 reputable domains to prioritize (optional)
  - exa_exclude_domains: up to 3 domains to avoid (optional)
  - max_sources: 6-10
  - include_statistics: boolean (true if topic needs fresh stats)
  - date_range: one of ["last_month","last_3_months","last_year","all_time"] (pick recent if time-sensitive)

Requirements:
- Keep language factual, actionable, and suited for spoken audio.
- Avoid narrative fiction tone; focus on insights, hooks, objections, and takeaways.
- Prefer 2024-2025 context when relevant.
"""

    try:
        raw = llm_text_gen(prompt=prompt, user_id=user_id, json_struct=None)
    except HTTPException:
        # Re-raise HTTPExceptions (e.g., 429 subscription limit) - preserve error details
        raise
    except Exception as exc:
        logger.error(f"[Podcast Analyze] Analysis failed for user {user_id}: {exc}")
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

    exa_suggested_config = data.get("exa_suggested_config") or None

    return PodcastAnalyzeResponse(
        audience=audience,
        content_type=content_type,
        top_keywords=top_keywords,
        suggested_outlines=suggested_outlines,
        title_suggestions=title_suggestions,
        exa_suggested_config=exa_suggested_config,
    )


@router.post("/research/exa", response_model=PodcastExaResearchResponse)
async def podcast_research_exa(
    request: PodcastExaResearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Run podcast research directly via Exa (no blog writer pipeline).
    """
    user_id = require_authenticated_user(current_user)

    queries = [q.strip() for q in request.queries if q and q.strip()]
    if not queries:
        raise HTTPException(status_code=400, detail="At least one query is required for research.")

    exa_cfg = request.exa_config or PodcastExaConfig()
    cfg = SimpleNamespace(
        exa_search_type=exa_cfg.exa_search_type or "auto",
        exa_category=exa_cfg.exa_category,
        exa_include_domains=exa_cfg.exa_include_domains or [],
        exa_exclude_domains=exa_cfg.exa_exclude_domains or [],
        max_sources=exa_cfg.max_sources or 8,
        source_types=[],
    )

    provider = ExaResearchProvider()
    prompt = request.topic

    try:
        result = await provider.search(
            prompt=prompt,
            topic=request.topic,
            industry="",
            target_audience="",
            config=cfg,
            user_id=user_id,
        )
    except Exception as exc:
        logger.error(f"[Podcast Exa Research] Failed for user {user_id}: {exc}")
        raise HTTPException(status_code=500, detail=f"Exa research failed: {exc}")

    # Track usage if available
    try:
        cost_total = 0.0
        if isinstance(result, dict):
            cost_total = result.get("cost", {}).get("total", 0.005) if result.get("cost") else 0.005
        provider.track_exa_usage(user_id, cost_total)
    except Exception as track_err:
        logger.warning(f"[Podcast Exa Research] Failed to track usage: {track_err}")

    sources_payload = []
    if isinstance(result, dict):
        for src in result.get("sources", []) or []:
            try:
                sources_payload.append(PodcastExaSource(**src))
            except Exception:
                sources_payload.append(PodcastExaSource(**{
                    "title": src.get("title", ""),
                    "url": src.get("url", ""),
                    "excerpt": src.get("excerpt", ""),
                    "published_at": src.get("published_at"),
                    "highlights": src.get("highlights"),
                    "summary": src.get("summary"),
                    "source_type": src.get("source_type"),
                    "index": src.get("index"),
                }))

    return PodcastExaResearchResponse(
        sources=sources_payload,
        search_queries=result.get("search_queries", queries) if isinstance(result, dict) else queries,
        cost=result.get("cost") if isinstance(result, dict) else None,
        search_type=result.get("search_type") if isinstance(result, dict) else None,
        provider=result.get("provider", "exa") if isinstance(result, dict) else "exa",
        content=result.get("content") if isinstance(result, dict) else None,
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

    # Build comprehensive research context for higher-quality scripts
    research_context = ""
    if request.research:
        try:
            key_insights = request.research.get("keyword_analysis", {}).get("key_insights") or []
            fact_cards = request.research.get("factCards", []) or []
            mapped_angles = request.research.get("mappedAngles", []) or []
            sources = request.research.get("sources", []) or []

            top_facts = [f.get("quote", "") for f in fact_cards[:5] if f.get("quote")]
            angles_summary = [
                f"{a.get('title', '')}: {a.get('why', '')}" for a in mapped_angles[:3] if a.get("title") or a.get("why")
            ]
            top_sources = [s.get("url") for s in sources[:3] if s.get("url")]

            research_parts = []
            if key_insights:
                research_parts.append(f"Key Insights: {', '.join(key_insights[:5])}")
            if top_facts:
                research_parts.append(f"Key Facts: {', '.join(top_facts)}")
            if angles_summary:
                research_parts.append(f"Research Angles: {' | '.join(angles_summary)}")
            if top_sources:
                research_parts.append(f"Top Sources: {', '.join(top_sources)}")

            research_context = "\n".join(research_parts)
        except Exception as exc:
            logger.warning(f"Failed to parse research context: {exc}")
            research_context = ""

    prompt = f"""You are an expert podcast script planner. Create natural, conversational podcast scenes.

Podcast Idea: "{request.idea}"
Duration: ~{request.duration_minutes} minutes
Speakers: {request.speakers} (Host + optional Guest)

{f"RESEARCH CONTEXT:\n{research_context}\n" if research_context else ""}

Return JSON with:
- scenes: array of scenes. Each scene has:
  - id: string
  - title: short scene title (<= 60 chars)
  - duration: duration in seconds (evenly split across total duration)
  - emotion: string (one of: "neutral", "happy", "excited", "serious", "curious", "confident")
  - lines: array of {{"speaker": "...", "text": "...", "emphasis": boolean}}
    * Write natural, conversational dialogue
    * Each line can be a sentence or a few sentences that flow together
    * Use plain text only - no markdown formatting (no asterisks, underscores, etc.)
    * Mark "emphasis": true for key statistics or important points

Guidelines:
- Write for spoken delivery: conversational, natural, with contractions
- Use research insights naturally - weave statistics into dialogue, don't just list them
- Vary emotion per scene based on content
- Ensure scenes match target duration: aim for ~2.5 words per second of audio
- Keep it engaging and informative, like a real podcast conversation
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

    valid_emotions = {"neutral", "happy", "excited", "serious", "curious", "confident"}

    # Normalize scenes
    scenes: list[PodcastScene] = []
    for idx, scene in enumerate(scenes_data):
        title = scene.get("title") or f"Scene {idx + 1}"
        duration = int(scene.get("duration") or max(30, (request.duration_minutes * 60) // max(1, len(scenes_data))))
        emotion = scene.get("emotion") or "neutral"
        if emotion not in valid_emotions:
            emotion = "neutral"
        lines_raw = scene.get("lines") or []
        lines: list[PodcastSceneLine] = []
        for line in lines_raw:
            speaker = line.get("speaker") or ("Host" if len(lines) % request.speakers == 0 else "Guest")
            text = line.get("text") or ""
            emphasis = line.get("emphasis", False)
            if text:
                lines.append(PodcastSceneLine(speaker=speaker, text=text, emphasis=emphasis))
        scenes.append(
            PodcastScene(
                id=scene.get("id") or f"scene-{idx + 1}",
                title=title,
                duration=duration,
                lines=lines,
                approved=False,
                emotion=emotion,
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
            speed=request.speed or 1.0,  # Normal speed (was 0.9, but too slow - causing duration issues)
            volume=request.volume or 1.0,
            pitch=request.pitch or 0.0,  # Normal pitch (0.0 = neutral)
            emotion=request.emotion or "neutral",
            english_normalization=request.english_normalization or False,
        )
        
        # Override URL to use podcast endpoint instead of story endpoint
        if result.get("audio_url") and "/api/story/audio/" in result.get("audio_url", ""):
            audio_filename = result.get("audio_filename", "")
            result["audio_url"] = f"/api/podcast/audio/{audio_filename}"
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


class PodcastCombineAudioRequest(BaseModel):
    """Request model for combining podcast audio files."""
    project_id: str
    scene_ids: List[str] = Field(..., description="List of scene IDs to combine")
    scene_audio_urls: List[str] = Field(..., description="List of audio URLs for each scene")


class PodcastCombineAudioResponse(BaseModel):
    """Response model for combined podcast audio."""
    combined_audio_url: str
    combined_audio_filename: str
    total_duration: float
    file_size: int
    scene_count: int


@router.post("/combine-audio", response_model=PodcastCombineAudioResponse)
async def combine_podcast_audio(
    request: PodcastCombineAudioRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Combine multiple scene audio files into a single podcast audio file.
    """
    user_id = require_authenticated_user(current_user)
    
    if not request.scene_ids or not request.scene_audio_urls:
        raise HTTPException(status_code=400, detail="Scene IDs and audio URLs are required")
    
    if len(request.scene_ids) != len(request.scene_audio_urls):
        raise HTTPException(status_code=400, detail="Scene IDs and audio URLs count must match")
    
    try:
        # Import moviepy for audio concatenation
        try:
            from moviepy import AudioFileClip, concatenate_audioclips
        except ImportError:
            logger.error("[Podcast] MoviePy not available for audio combination")
            raise HTTPException(
                status_code=500,
                detail="Audio combination requires MoviePy. Please install: pip install moviepy"
            )
        
        # Create temporary directory for audio processing
        temp_dir = Path(tempfile.gettempdir()) / f"podcast_combine_{uuid.uuid4().hex[:8]}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        audio_clips = []
        total_duration = 0.0
        
        try:
            # Log incoming request for debugging
            logger.info(f"[Podcast] Combining audio: {len(request.scene_audio_urls)} URLs received")
            for idx, url in enumerate(request.scene_audio_urls):
                logger.info(f"[Podcast] URL {idx+1}: {url}")
            
            # Download and load each audio file from podcast_audio directory
            for idx, audio_url in enumerate(request.scene_audio_urls):
                try:
                    # Normalize audio URL - handle both absolute and relative paths
                    if audio_url.startswith("http"):
                        # External URL - would need to download
                        logger.error(f"[Podcast] External URLs not supported: {audio_url}")
                        raise HTTPException(
                            status_code=400,
                            detail=f"External URLs not supported. Please use local file paths."
                        )
                    
                    # Handle relative paths - only /api/podcast/audio/... URLs are supported
                    audio_path = None
                    if audio_url.startswith("/api/"):
                        # Extract filename from URL
                        from urllib.parse import urlparse
                        parsed = urlparse(audio_url)
                        path = parsed.path if parsed.scheme else audio_url
                        
                        # Handle both /api/podcast/audio/ and /api/story/audio/ URLs (for backward compatibility)
                        if "/api/podcast/audio/" in path:
                            filename = path.split("/api/podcast/audio/", 1)[1].split("?", 1)[0].strip()
                        elif "/api/story/audio/" in path:
                            # Convert story audio URLs to podcast audio (they're in the same directory now)
                            filename = path.split("/api/story/audio/", 1)[1].split("?", 1)[0].strip()
                            logger.info(f"[Podcast] Converting story audio URL to podcast: {audio_url} -> {filename}")
                        else:
                            logger.error(f"[Podcast] Unsupported audio URL format: {audio_url}. Expected /api/podcast/audio/ or /api/story/audio/ URLs.")
                            continue
                        
                        if not filename:
                            logger.error(f"[Podcast] Could not extract filename from URL: {audio_url}")
                            continue
                        
                        # Podcast audio files are stored in podcast_audio directory
                        audio_path = (PODCAST_AUDIO_DIR / filename).resolve()
                        
                        # Security check: ensure path is within PODCAST_AUDIO_DIR
                        if not str(audio_path).startswith(str(PODCAST_AUDIO_DIR)):
                            logger.error(f"[Podcast] Attempted path traversal when resolving audio: {audio_url}")
                            continue
                    else:
                        logger.warning(f"[Podcast] Non-API URL format, treating as direct path: {audio_url}")
                        audio_path = Path(audio_url)
                    
                    if not audio_path or not audio_path.exists():
                        logger.error(f"[Podcast] Audio file not found: {audio_path} (from URL: {audio_url})")
                        continue
                    
                    # Load audio clip
                    audio_clip = AudioFileClip(str(audio_path))
                    audio_clips.append(audio_clip)
                    total_duration += audio_clip.duration
                    logger.info(f"[Podcast] Loaded audio {idx+1}/{len(request.scene_audio_urls)}: {audio_path.name} ({audio_clip.duration:.2f}s)")
                    
                except HTTPException:
                    raise
                except Exception as e:
                    logger.error(f"[Podcast] Failed to load audio {idx+1}: {e}", exc_info=True)
                    # Continue with other audio files
                    continue
            
            if not audio_clips:
                raise HTTPException(status_code=400, detail="No valid audio files found to combine")
            
            # Concatenate all audio clips
            logger.info(f"[Podcast] Combining {len(audio_clips)} audio clips (total duration: {total_duration:.2f}s)")
            combined_audio = concatenate_audioclips(audio_clips)
            
            # Generate output filename
            output_filename = f"podcast_combined_{request.project_id}_{uuid.uuid4().hex[:8]}.mp3"
            output_path = PODCAST_AUDIO_DIR / output_filename
            
            # Write combined audio file
            combined_audio.write_audiofile(
                str(output_path),
                codec="mp3",
                bitrate="192k",
                logger=None,  # Suppress moviepy logging
            )
            
            # Close audio clips to free resources
            for clip in audio_clips:
                clip.close()
            combined_audio.close()
            
            file_size = output_path.stat().st_size
            audio_url = f"/api/podcast/audio/{output_filename}"
            
            logger.info(f"[Podcast] Combined audio saved: {output_path} ({file_size} bytes)")
            
            # Save to asset library
            try:
                save_asset_to_library(
                    db=db,
                    user_id=user_id,
                    asset_type="audio",
                    source_module="podcast_maker",
                    filename=output_filename,
                    file_url=audio_url,
                    file_path=str(output_path),
                    file_size=file_size,
                    mime_type="audio/mpeg",
                    title=f"Combined Podcast - {request.project_id}",
                    description=f"Combined podcast audio from {len(request.scene_ids)} scenes",
                    tags=["podcast", "audio", "combined", request.project_id],
                    asset_metadata={
                        "project_id": request.project_id,
                        "scene_ids": request.scene_ids,
                        "scene_count": len(request.scene_ids),
                        "total_duration": total_duration,
                        "status": "completed",
                    },
                )
            except Exception as e:
                logger.warning(f"[Podcast] Failed to save combined audio asset: {e}")
            
            return PodcastCombineAudioResponse(
                combined_audio_url=audio_url,
                combined_audio_filename=output_filename,
                total_duration=total_duration,
                file_size=file_size,
                scene_count=len(request.scene_ids),
            )
            
        finally:
            # Cleanup temporary directory
            try:
                import shutil
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"[Podcast] Failed to cleanup temp directory: {e}")
                
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[Podcast] Audio combination failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Audio combination failed: {exc}")


@router.get("/task/{task_id}/status")
async def podcast_task_status(task_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Expose task status under podcast namespace (reuses shared task manager)."""
    require_authenticated_user(current_user)
    return task_manager.get_task_status(task_id)


class PodcastImageRequest(BaseModel):
    """Request for generating an image for a podcast scene."""
    scene_id: str
    scene_title: str
    scene_content: Optional[str] = None  # Optional: scene lines text for context
    idea: Optional[str] = None  # Optional: podcast idea for context
    width: int = 1024
    height: int = 1024


class PodcastImageResponse(BaseModel):
    """Response for podcast scene image generation."""
    scene_id: str
    scene_title: str
    image_filename: str
    image_url: str
    width: int
    height: int
    provider: str
    model: Optional[str] = None
    cost: float


@router.post("/image", response_model=PodcastImageResponse)
async def generate_podcast_scene_image(
    request: PodcastImageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate an AI image for a podcast scene.
    Creates a professional, podcast-appropriate image based on scene title and content.
    """
    user_id = require_authenticated_user(current_user)

    if not request.scene_title:
        raise HTTPException(status_code=400, detail="Scene title is required")

    try:
        # Build image prompt from scene context
        prompt_parts = [
            "Professional podcast studio setting, modern and clean",
            f"Scene topic: {request.scene_title}",
        ]
        
        if request.scene_content:
            # Extract key themes from scene content (first 200 chars)
            content_preview = request.scene_content[:200].replace("\n", " ")
            prompt_parts.append(f"Content context: {content_preview}")
        
        if request.idea:
            prompt_parts.append(f"Podcast theme: {request.idea[:100]}")
        
        prompt_parts.extend([
            "Professional lighting, podcast microphone visible",
            "Modern podcast studio aesthetic, clean background",
            "High quality, professional photography style",
            "Suitable for video generation with talking avatar"
        ])
        
        image_prompt = ", ".join(prompt_parts)

        logger.info(f"[Podcast] Generating image for scene {request.scene_id}: {request.scene_title}")

        # Generate image using main_image_generation service
        image_options = {
            "provider": None,  # Auto-select provider
            "width": request.width,
            "height": request.height,
        }
        
        result = generate_image(
            prompt=image_prompt,
            options=image_options,
            user_id=user_id
        )

        # Save image to podcast images directory
        base_dir = Path(__file__).parent.parent.parent.parent
        podcast_images_dir = base_dir / "podcast_images"
        podcast_images_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        clean_title = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in request.scene_title[:30])
        unique_id = str(uuid.uuid4())[:8]
        image_filename = f"scene_{request.scene_id}_{clean_title}_{unique_id}.png"
        image_path = podcast_images_dir / image_filename

        # Save image
        with open(image_path, "wb") as f:
            f.write(result.image_bytes)

        logger.info(f"[Podcast] Saved image to: {image_path}")

        # Create image URL (served via API endpoint)
        image_url = f"/api/podcast/images/{image_filename}"

        # Save to asset library
        try:
            save_asset_to_library(
                db=db,
                user_id=user_id,
                asset_type="image",
                source_module="podcast_maker",
                filename=image_filename,
                file_url=image_url,
                file_path=str(image_path),
                file_size=len(result.image_bytes),
                mime_type="image/png",
                title=f"{request.scene_title} - Podcast Scene",
                description=f"Podcast scene image: {request.scene_title}",
                prompt=image_prompt,
                tags=["podcast", "scene", request.scene_id],
                provider=result.provider,
                model=result.model,
                asset_metadata={
                    "scene_id": request.scene_id,
                    "scene_title": request.scene_title,
                    "status": "completed",
                },
            )
        except Exception as e:
            logger.warning(f"[Podcast] Failed to save image asset: {e}")

        # Estimate cost (rough estimate: ~$0.04 per image for most providers)
        cost = 0.04

        return PodcastImageResponse(
            scene_id=request.scene_id,
            scene_title=request.scene_title,
            image_filename=image_filename,
            image_url=image_url,
            width=result.width,
            height=result.height,
            provider=result.provider,
            model=result.model,
            cost=cost,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[Podcast] Image generation failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(exc)}")


@router.get("/audio/{filename}")
async def serve_podcast_audio(
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user_with_query_token),
):
    """Serve generated podcast scene audio files.
    
    Supports authentication via Authorization header or token query parameter.
    Query parameter is useful for HTML elements like <audio> that cannot send custom headers.
    """
    from fastapi.responses import FileResponse
    
    require_authenticated_user(current_user)
    
    # Security check: ensure filename doesn't contain path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    audio_path = (PODCAST_AUDIO_DIR / filename).resolve()
    
    # Security check: ensure path is within PODCAST_AUDIO_DIR
    if not str(audio_path).startswith(str(PODCAST_AUDIO_DIR)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(audio_path, media_type="audio/mpeg")


@router.get("/images/{filename}")
async def serve_podcast_image(
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user_with_query_token),
):
    """Serve generated podcast scene images.
    
    Supports authentication via Authorization header or token query parameter.
    Query parameter is useful for HTML elements like <img> that cannot send custom headers.
    """
    from fastapi.responses import FileResponse
    
    require_authenticated_user(current_user)
    
    base_dir = Path(__file__).parent.parent.parent.parent
    image_path = base_dir / "podcast_images" / filename
    
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(image_path, media_type="image/png")

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
    avatar_image_url: Optional[str] = Field(None, description="URL to scene image (required for video generation)")
    resolution: str = Field("720p", description="Video resolution (480p or 720p)")
    prompt: Optional[str] = Field(None, description="Optional animation prompt override")


class PodcastVideoGenerationResponse(BaseModel):
    """Response model for podcast video generation."""
    task_id: str
    status: str
    message: str


def _load_podcast_audio_bytes(audio_url: str) -> bytes:
    """Load podcast audio bytes from URL. Only handles /api/podcast/audio/ URLs."""
    from urllib.parse import urlparse
    
    if not audio_url:
        raise HTTPException(status_code=400, detail="Audio URL is required")
    
    try:
        parsed = urlparse(audio_url)
        path = parsed.path if parsed.scheme else audio_url
        
        # Only handle /api/podcast/audio/ URLs
        prefix = "/api/podcast/audio/"
        if prefix not in path:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported audio URL format: {audio_url}. Only /api/podcast/audio/ URLs are supported."
            )
        
        filename = path.split(prefix, 1)[1].split("?", 1)[0].strip()
        if not filename:
            raise HTTPException(status_code=400, detail=f"Could not extract filename from URL: {audio_url}")
        
        # Podcast audio files are stored in podcast_audio directory
        audio_path = (PODCAST_AUDIO_DIR / filename).resolve()
        
        # Security check: ensure path is within PODCAST_AUDIO_DIR
        if not str(audio_path).startswith(str(PODCAST_AUDIO_DIR)):
            logger.error(f"[Podcast] Attempted path traversal when resolving audio: {audio_url}")
            raise HTTPException(status_code=403, detail="Invalid audio path")
        
        if not audio_path.exists():
            logger.warning(f"[Podcast] Audio file not found: {audio_path}")
            raise HTTPException(status_code=404, detail=f"Audio file not found: {filename}")
        
        return audio_path.read_bytes()
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[Podcast] Failed to load audio: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to load audio: {str(exc)}")


def _load_podcast_image_bytes(image_url: str) -> bytes:
    """Load podcast image bytes from URL. Only handles /api/podcast/images/ URLs."""
    from urllib.parse import urlparse
    
    if not image_url:
        raise HTTPException(status_code=400, detail="Image URL is required")
    
    try:
        parsed = urlparse(image_url)
        path = parsed.path if parsed.scheme else image_url
        
        # Only handle /api/podcast/images/ URLs
        prefix = "/api/podcast/images/"
        if prefix not in path:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported image URL format: {image_url}. Only /api/podcast/images/ URLs are supported."
            )
        
        filename = path.split(prefix, 1)[1].split("?", 1)[0].strip()
        if not filename:
            raise HTTPException(status_code=400, detail=f"Could not extract filename from URL: {image_url}")
        
        # Podcast images are stored in podcast_images directory
        image_path = (PODCAST_IMAGES_DIR / filename).resolve()
        
        # Security check: ensure path is within PODCAST_IMAGES_DIR
        if not str(image_path).startswith(str(PODCAST_IMAGES_DIR)):
            logger.error(f"[Podcast] Attempted path traversal when resolving image: {image_url}")
            raise HTTPException(status_code=403, detail="Invalid image path")
        
        if not image_path.exists():
            logger.warning(f"[Podcast] Image file not found: {image_path}")
            raise HTTPException(status_code=404, detail=f"Image file not found: {filename}")
        
        return image_path.read_bytes()
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[Podcast] Failed to load image: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to load image: {str(exc)}")


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
    audio_bytes = _load_podcast_audio_bytes(request.audio_url)

    # Load image bytes (scene image is required for video generation)
    if request.avatar_image_url:
        image_bytes = _load_podcast_image_bytes(request.avatar_image_url)
    else:
        # Scene-specific image should be generated before video generation
        raise HTTPException(
            status_code=400,
            detail="Scene image is required for video generation. Please generate images for scenes first.",
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
    avatar_image_url: Optional[str] = Field(None, description="URL to scene image (required for video generation)")
    resolution: str = Field("720p", description="Video resolution (480p or 720p)")
    prompt: Optional[str] = Field(None, description="Optional animation prompt override")


class PodcastVideoGenerationResponse(BaseModel):
    """Response model for podcast video generation."""
    task_id: str
    status: str
    message: str


def _load_podcast_audio_bytes(audio_url: str) -> bytes:
    """Load podcast audio bytes from URL. Only handles /api/podcast/audio/ URLs."""
    from urllib.parse import urlparse
    
    if not audio_url:
        raise HTTPException(status_code=400, detail="Audio URL is required")
    
    try:
        parsed = urlparse(audio_url)
        path = parsed.path if parsed.scheme else audio_url
        
        # Only handle /api/podcast/audio/ URLs
        prefix = "/api/podcast/audio/"
        if prefix not in path:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported audio URL format: {audio_url}. Only /api/podcast/audio/ URLs are supported."
            )
        
        filename = path.split(prefix, 1)[1].split("?", 1)[0].strip()
        if not filename:
            raise HTTPException(status_code=400, detail=f"Could not extract filename from URL: {audio_url}")
        
        # Podcast audio files are stored in podcast_audio directory
        audio_path = (PODCAST_AUDIO_DIR / filename).resolve()
        
        # Security check: ensure path is within PODCAST_AUDIO_DIR
        if not str(audio_path).startswith(str(PODCAST_AUDIO_DIR)):
            logger.error(f"[Podcast] Attempted path traversal when resolving audio: {audio_url}")
            raise HTTPException(status_code=403, detail="Invalid audio path")
        
        if not audio_path.exists():
            logger.warning(f"[Podcast] Audio file not found: {audio_path}")
            raise HTTPException(status_code=404, detail=f"Audio file not found: {filename}")
        
        return audio_path.read_bytes()
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[Podcast] Failed to load audio: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to load audio: {str(exc)}")


def _load_podcast_image_bytes(image_url: str) -> bytes:
    """Load podcast image bytes from URL. Only handles /api/podcast/images/ URLs."""
    from urllib.parse import urlparse
    
    if not image_url:
        raise HTTPException(status_code=400, detail="Image URL is required")
    
    try:
        parsed = urlparse(image_url)
        path = parsed.path if parsed.scheme else image_url
        
        # Only handle /api/podcast/images/ URLs
        prefix = "/api/podcast/images/"
        if prefix not in path:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported image URL format: {image_url}. Only /api/podcast/images/ URLs are supported."
            )
        
        filename = path.split(prefix, 1)[1].split("?", 1)[0].strip()
        if not filename:
            raise HTTPException(status_code=400, detail=f"Could not extract filename from URL: {image_url}")
        
        # Podcast images are stored in podcast_images directory
        image_path = (PODCAST_IMAGES_DIR / filename).resolve()
        
        # Security check: ensure path is within PODCAST_IMAGES_DIR
        if not str(image_path).startswith(str(PODCAST_IMAGES_DIR)):
            logger.error(f"[Podcast] Attempted path traversal when resolving image: {image_url}")
            raise HTTPException(status_code=403, detail="Invalid image path")
        
        if not image_path.exists():
            logger.warning(f"[Podcast] Image file not found: {image_path}")
            raise HTTPException(status_code=404, detail=f"Image file not found: {filename}")
        
        return image_path.read_bytes()
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[Podcast] Failed to load image: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to load image: {str(exc)}")


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
    audio_bytes = _load_podcast_audio_bytes(request.audio_url)

    # Load image bytes (scene image is required for video generation)
    if request.avatar_image_url:
        image_bytes = _load_podcast_image_bytes(request.avatar_image_url)
    else:
        # Scene-specific image should be generated before video generation
        raise HTTPException(
            status_code=400,
            detail="Scene image is required for video generation. Please generate images for scenes first.",
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

