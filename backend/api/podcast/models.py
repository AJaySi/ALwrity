"""
Podcast API Models

All Pydantic request/response models for podcast endpoints.
"""

from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Dict, Any
from datetime import datetime


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
    final_video_url: Optional[str] = None
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
    sample_rate: Optional[int] = None
    bitrate: Optional[int] = None
    channel: Optional[str] = None
    format: Optional[str] = None
    language_boost: Optional[str] = None
    enable_sync_mode: Optional[bool] = True


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
    avatar_url: Optional[str] = Field(None, description="Optional presenter avatar URL")


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
    final_video_url: Optional[str] = None


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


class PodcastImageRequest(BaseModel):
    """Request for generating an image for a podcast scene."""
    scene_id: str
    scene_title: str
    scene_content: Optional[str] = None  # Optional: scene lines text for context
    idea: Optional[str] = None  # Optional: podcast idea for context
    base_avatar_url: Optional[str] = None  # Base avatar image URL for scene variations
    width: int = 1024
    height: int = 1024
    custom_prompt: Optional[str] = None  # Custom prompt from user (overrides auto-generated prompt)
    style: Optional[str] = None  # "Auto", "Fiction", or "Realistic"
    rendering_speed: Optional[str] = None  # "Default", "Turbo", or "Quality"
    aspect_ratio: Optional[str] = None  # "1:1", "16:9", "9:16", "4:3", "3:4"


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


class PodcastVideoGenerationRequest(BaseModel):
    """Request model for podcast video generation."""
    project_id: str = Field(..., description="Podcast project ID")
    scene_id: str = Field(..., description="Scene ID")
    scene_title: str = Field(..., description="Scene title")
    audio_url: str = Field(..., description="URL to the generated audio file")
    avatar_image_url: Optional[str] = Field(None, description="URL to scene image (required for video generation)")
    resolution: str = Field("720p", description="Video resolution (480p or 720p)")
    prompt: Optional[str] = Field(None, description="Optional animation prompt override")
    seed: Optional[int] = Field(-1, description="Random seed; -1 for random")
    mask_image_url: Optional[str] = Field(None, description="Optional mask image URL to specify animated region")


class PodcastVideoGenerationResponse(BaseModel):
    """Response model for podcast video generation."""
    task_id: str
    status: str
    message: str


class PodcastCombineVideosRequest(BaseModel):
    """Request to combine scene videos into final podcast"""
    project_id: str = Field(..., description="Project ID")
    scene_video_urls: list[str] = Field(..., description="List of scene video URLs in order")
    podcast_title: str = Field(default="Podcast", description="Title for the final podcast video")


class PodcastCombineVideosResponse(BaseModel):
    """Response from combine videos endpoint"""
    task_id: str
    status: str
    message: str

