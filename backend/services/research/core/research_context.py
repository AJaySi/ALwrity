"""
Research Context Schema

Defines the unified input schema for the Research Engine.
Any tool (Blog Writer, Podcast Maker, YouTube Creator) can create a ResearchContext
and pass it to the Research Engine.

Author: ALwrity Team
Version: 2.0
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ContentType(str, Enum):
    """Type of content being created - affects research focus."""
    BLOG = "blog"
    PODCAST = "podcast"
    VIDEO = "video"
    SOCIAL = "social"
    EMAIL = "email"
    NEWSLETTER = "newsletter"
    WHITEPAPER = "whitepaper"
    GENERAL = "general"


class ResearchGoal(str, Enum):
    """Primary goal of the research - affects provider selection and depth."""
    FACTUAL = "factual"          # Stats, data, citations
    TRENDING = "trending"         # Current trends, news
    COMPETITIVE = "competitive"   # Competitor analysis
    EDUCATIONAL = "educational"   # How-to, explanations
    INSPIRATIONAL = "inspirational"  # Stories, quotes
    TECHNICAL = "technical"       # Deep technical content


class ResearchDepth(str, Enum):
    """Depth of research - maps to existing ResearchMode."""
    QUICK = "quick"              # Fast, surface-level (maps to BASIC)
    STANDARD = "standard"        # Balanced depth (maps to BASIC with more sources)
    COMPREHENSIVE = "comprehensive"  # Deep research (maps to COMPREHENSIVE)
    EXPERT = "expert"            # Maximum depth with expert sources


class ProviderPreference(str, Enum):
    """Provider preference - AUTO lets the engine decide."""
    AUTO = "auto"       # AI decides based on query (default)
    EXA = "exa"         # Force Exa neural search
    TAVILY = "tavily"   # Force Tavily AI search
    GOOGLE = "google"   # Force Google grounding
    HYBRID = "hybrid"   # Use multiple providers


class ResearchPersonalizationContext(BaseModel):
    """
    Context from the calling tool (Blog Writer, Podcast Maker, etc.)
    This personalizes the research without the Research Engine knowing
    the specific tool implementation.
    """
    # Who is creating the content
    creator_id: Optional[str] = None  # Clerk user ID
    
    # Content context
    content_type: ContentType = ContentType.GENERAL
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    tone: Optional[str] = None  # professional, casual, technical, etc.
    
    # Persona data (from onboarding)
    persona_id: Optional[str] = None
    brand_voice: Optional[str] = None
    competitor_urls: List[str] = Field(default_factory=list)
    
    # Content requirements
    word_count_target: Optional[int] = None
    include_statistics: bool = True
    include_expert_quotes: bool = True
    include_case_studies: bool = False
    include_visuals: bool = False
    
    # Platform-specific hints
    platform: Optional[str] = None  # medium, wordpress, youtube, spotify, etc.
    
    class Config:
        use_enum_values = True


class ResearchContext(BaseModel):
    """
    Main input schema for the Research Engine.
    
    This is what any tool passes to the Research Engine to get research results.
    The engine uses AI to optimize parameters based on this context.
    """
    # Primary research input
    query: str = Field(..., description="Main research query or topic")
    keywords: List[str] = Field(default_factory=list, description="Additional keywords")
    
    # Research configuration
    goal: ResearchGoal = ResearchGoal.FACTUAL
    depth: ResearchDepth = ResearchDepth.STANDARD
    provider_preference: ProviderPreference = ProviderPreference.AUTO
    
    # Personalization from calling tool
    personalization: Optional[ResearchPersonalizationContext] = None
    
    # Constraints
    max_sources: int = Field(default=10, ge=1, le=25)
    recency: Optional[str] = None  # "day", "week", "month", "year", None for all-time
    
    # Domain filtering
    include_domains: List[str] = Field(default_factory=list)
    exclude_domains: List[str] = Field(default_factory=list)
    
    # Advanced mode (exposes raw provider parameters)
    advanced_mode: bool = False
    
    # Raw provider parameters (only used if advanced_mode=True)
    # Exa-specific
    exa_category: Optional[str] = None
    exa_search_type: Optional[str] = None  # auto, keyword, neural
    
    # Tavily-specific
    tavily_topic: Optional[str] = None  # general, news, finance
    tavily_search_depth: Optional[str] = None  # basic, advanced
    tavily_include_answer: bool = False
    tavily_include_raw_content: bool = False
    tavily_time_range: Optional[str] = None
    tavily_country: Optional[str] = None
    
    class Config:
        use_enum_values = True
    
    def get_effective_query(self) -> str:
        """Build effective query combining query and keywords."""
        if self.keywords:
            return f"{self.query} {' '.join(self.keywords)}"
        return self.query
    
    def get_industry(self) -> str:
        """Get industry from personalization or default."""
        if self.personalization and self.personalization.industry:
            return self.personalization.industry
        return "General"
    
    def get_audience(self) -> str:
        """Get target audience from personalization or default."""
        if self.personalization and self.personalization.target_audience:
            return self.personalization.target_audience
        return "General"
    
    def get_user_id(self) -> Optional[str]:
        """Get user ID from personalization."""
        if self.personalization:
            return self.personalization.creator_id
        return None


class ResearchResult(BaseModel):
    """
    Output schema from the Research Engine.
    Standardized format that any tool can consume.
    """
    success: bool = True
    
    # Content
    summary: Optional[str] = None  # AI-generated summary of findings
    raw_content: Optional[str] = None  # Raw aggregated content for LLM processing
    
    # Sources
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Analysis (reuses existing blog writer analysis)
    keyword_analysis: Dict[str, Any] = Field(default_factory=dict)
    competitor_analysis: Dict[str, Any] = Field(default_factory=dict)
    suggested_angles: List[str] = Field(default_factory=list)
    
    # Metadata
    provider_used: str = "google"  # Which provider was actually used
    search_queries: List[str] = Field(default_factory=list)
    grounding_metadata: Optional[Dict[str, Any]] = None
    
    # Cost tracking
    estimated_cost: float = 0.0
    
    # Error handling
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    retry_suggested: bool = False
    
    # Original context for reference
    original_query: Optional[str] = None
    
    class Config:
        use_enum_values = True

