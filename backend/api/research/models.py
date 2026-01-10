"""
Research API Models

All Pydantic request/response models for research endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# Research Execution Models
# ============================================================================

class ResearchRequest(BaseModel):
    """API request for research."""
    query: str = Field(..., description="Main research query or topic")
    keywords: List[str] = Field(default_factory=list, description="Additional keywords")
    
    # Research configuration
    goal: Optional[str] = Field(default="factual", description="Research goal: factual, trending, competitive, etc.")
    depth: Optional[str] = Field(default="standard", description="Research depth: quick, standard, comprehensive, expert")
    provider: Optional[str] = Field(default="auto", description="Provider preference: auto, exa, tavily, google")
    
    # Personalization
    content_type: Optional[str] = Field(default="general", description="Content type: blog, podcast, video, etc.")
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    tone: Optional[str] = None
    
    # Constraints
    max_sources: int = Field(default=10, ge=1, le=25)
    recency: Optional[str] = None  # day, week, month, year
    
    # Domain filtering
    include_domains: List[str] = Field(default_factory=list)
    exclude_domains: List[str] = Field(default_factory=list)
    
    # Advanced mode
    advanced_mode: bool = False
    
    # Raw provider parameters (only if advanced_mode=True)
    exa_category: Optional[str] = None
    exa_search_type: Optional[str] = None
    tavily_topic: Optional[str] = None
    tavily_search_depth: Optional[str] = None
    tavily_include_answer: bool = False
    tavily_time_range: Optional[str] = None


class ResearchResponse(BaseModel):
    """API response for research."""
    success: bool
    task_id: Optional[str] = None  # For async requests
    
    # Results (if synchronous)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    keyword_analysis: Dict[str, Any] = Field(default_factory=dict)
    competitor_analysis: Dict[str, Any] = Field(default_factory=dict)
    suggested_angles: List[str] = Field(default_factory=list)
    
    # Metadata
    provider_used: Optional[str] = None
    search_queries: List[str] = Field(default_factory=list)
    
    # Error handling
    error_message: Optional[str] = None
    error_code: Optional[str] = None


class ProviderStatusResponse(BaseModel):
    """Response for provider status check."""
    exa: Dict[str, Any]
    tavily: Dict[str, Any]
    google: Dict[str, Any]


# ============================================================================
# Intent-Driven Research Models
# ============================================================================

class AnalyzeIntentRequest(BaseModel):
    """Request to analyze user research intent."""
    user_input: str = Field(..., description="User's keywords, question, or goal")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    use_persona: bool = Field(True, description="Use research persona for context")
    use_competitor_data: bool = Field(True, description="Use competitor data for context")
    # User-provided intent settings (optional - if provided, use these instead of inferring)
    user_provided_purpose: Optional[str] = Field(None, description="User-selected purpose (learn, create_content, etc.)")
    user_provided_content_output: Optional[str] = Field(None, description="User-selected content output (blog, podcast, etc.)")
    user_provided_depth: Optional[str] = Field(None, description="User-selected depth (overview, detailed, expert)")


class AnalyzeIntentResponse(BaseModel):
    """Response from intent analysis with optimized provider parameters."""
    success: bool
    intent: Dict[str, Any]
    analysis_summary: str
    suggested_queries: List[Dict[str, Any]]
    suggested_keywords: List[str]
    suggested_angles: List[str]
    quick_options: List[Dict[str, Any]]
    confidence_reason: Optional[str] = None
    great_example: Optional[str] = None
    error_message: Optional[str] = None
    
    # Unified: Optimized provider parameters based on intent
    optimized_config: Optional[Dict[str, Any]] = None  # Provider settings auto-configured from intent
    recommended_provider: Optional[str] = None  # Best provider for this intent (exa, tavily, google)
    
    # Google Trends configuration (if trends in deliverables)
    trends_config: Optional[Dict[str, Any]] = None  # Trends keywords and settings with justifications


class IntentDrivenResearchRequest(BaseModel):
    """Request for intent-driven research."""
    # Intent from previous analyze step, or minimal input for auto-inference
    user_input: str = Field(..., description="User's original input")
    
    # Optional: Confirmed intent from UI (if user modified the inferred intent)
    confirmed_intent: Optional[Dict[str, Any]] = None
    
    # Optional: Specific queries to run (if user selected from suggested)
    selected_queries: Optional[List[Dict[str, Any]]] = None
    
    # Research configuration
    max_sources: int = Field(default=10, ge=1, le=25)
    include_domains: List[str] = Field(default_factory=list)
    exclude_domains: List[str] = Field(default_factory=list)
    
    # Google Trends configuration (from intent analysis)
    trends_config: Optional[Dict[str, Any]] = None  # Trends keywords and settings
    
    # Skip intent inference (for re-runs with same intent)
    skip_inference: bool = False


class IntentDrivenResearchResponse(BaseModel):
    """Response from intent-driven research."""
    success: bool
    
    # Direct answers
    primary_answer: str = ""
    secondary_answers: Dict[str, Optional[str]] = Field(default_factory=dict)
    focus_areas_coverage: Dict[str, Optional[str]] = Field(default_factory=dict)
    also_answering_coverage: Dict[str, Optional[str]] = Field(default_factory=dict)
    
    # Deliverables
    statistics: List[Dict[str, Any]] = Field(default_factory=list)
    expert_quotes: List[Dict[str, Any]] = Field(default_factory=list)
    case_studies: List[Dict[str, Any]] = Field(default_factory=list)
    trends: List[Dict[str, Any]] = Field(default_factory=list)
    comparisons: List[Dict[str, Any]] = Field(default_factory=list)
    best_practices: List[str] = Field(default_factory=list)
    step_by_step: List[str] = Field(default_factory=list)
    pros_cons: Optional[Dict[str, Any]] = None
    definitions: Dict[str, str] = Field(default_factory=dict)
    examples: List[str] = Field(default_factory=list)
    predictions: List[str] = Field(default_factory=list)
    
    # Content-ready outputs
    executive_summary: str = ""
    key_takeaways: List[str] = Field(default_factory=list)
    suggested_outline: List[str] = Field(default_factory=list)
    
    # Sources and metadata
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = 0.8
    gaps_identified: List[str] = Field(default_factory=list)
    follow_up_queries: List[str] = Field(default_factory=list)
    intent: Optional[Dict[str, Any]] = None
    google_trends_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


# ============================================================================
# Research Project Models
# ============================================================================

class SaveResearchProjectRequest(BaseModel):
    """Request to save a research project to database."""
    project_id: Optional[str] = Field(None, description="Project ID for updates (optional, auto-generated if not provided)")
    title: Optional[str] = Field(None, description="Project title")
    keywords: List[str] = Field(..., description="Research keywords")
    industry: str = Field(..., description="Industry")
    target_audience: str = Field(..., description="Target audience")
    research_mode: str = Field(..., description="Research mode (comprehensive, targeted, basic)")
    config: Dict[str, Any] = Field(..., description="Research configuration")
    intent_analysis: Optional[Dict[str, Any]] = Field(None, description="Intent analysis result")
    confirmed_intent: Optional[Dict[str, Any]] = Field(None, description="Confirmed research intent")
    intent_result: Optional[Dict[str, Any]] = Field(None, description="Intent-driven research result")
    legacy_result: Optional[Dict[str, Any]] = Field(None, description="Legacy research result")
    current_step: int = Field(1, description="Current wizard step")
    description: Optional[str] = Field(None, description="Project description")


class SaveResearchProjectResponse(BaseModel):
    """Response after saving research project."""
    success: bool
    asset_id: Optional[int] = None  # Database ID (for backward compatibility)
    project_id: Optional[str] = None  # Project UUID (for lookups)
    message: str


class ResearchProjectResponse(BaseModel):
    """Response model for research project."""
    id: int
    project_id: str
    user_id: str
    title: Optional[str] = None
    keywords: List[str]
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    research_mode: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    intent_analysis: Optional[Dict[str, Any]] = None
    confirmed_intent: Optional[Dict[str, Any]] = None
    intent_result: Optional[Dict[str, Any]] = None
    legacy_result: Optional[Dict[str, Any]] = None
    trends_config: Optional[Dict[str, Any]] = None
    current_step: int = 1
    status: str = "draft"
    is_favorite: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ResearchProjectListResponse(BaseModel):
    """Response model for listing research projects."""
    projects: List[ResearchProjectResponse]
    total: int
    limit: int
    offset: int
