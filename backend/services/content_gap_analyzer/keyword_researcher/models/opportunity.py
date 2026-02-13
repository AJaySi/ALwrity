"""
Opportunity Models

Pydantic models for keyword opportunity identification and scoring.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class OpportunityType(str, Enum):
    """Enumeration for opportunity types."""
    CONTENT_GAP = "content_gap"
    TRENDING = "trending"
    LONG_TAIL = "long_tail"
    LOW_COMPETITION = "low_competition"
    HIGH_VOLUME = "high_volume"
    SEASONAL = "seasonal"
    COMPETITIVE_ADVANTAGE = "competitive_advantage"


class PriorityLevel(str, Enum):
    """Enumeration for priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CompetitionLevel(str, Enum):
    """Enumeration for competition levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class OpportunityScore(BaseModel):
    """Model for opportunity scoring components."""
    
    overall_score: float = Field(..., description="Overall opportunity score (0-100)")
    volume_score: float = Field(..., description="Search volume score (0-100)")
    competition_score: float = Field(..., description="Competition score (0-100)")
    trend_score: float = Field(..., description="Trend score (0-100)")
    relevance_score: float = Field(..., description="Relevance score (0-100)")
    difficulty_score: float = Field(..., description="Difficulty score (0-100)")
    confidence_level: float = Field(..., description="Confidence in scoring (0-100)")


class ContentOpportunity(BaseModel):
    """Model for content opportunity details."""
    
    keyword: str = Field(..., description="Target keyword")
    opportunity_type: OpportunityType = Field(..., description="Type of opportunity")
    search_volume: int = Field(..., description="Estimated monthly search volume")
    competition_level: CompetitionLevel = Field(..., description="Competition level")
    difficulty_score: float = Field(..., description="Keyword difficulty (0-100)")
    estimated_traffic: str = Field(..., description="Estimated monthly traffic potential")
    opportunity_score: OpportunityScore = Field(..., description="Detailed opportunity scoring")
    content_suggestions: List[str] = Field(..., description="Content creation suggestions")
    priority: PriorityLevel = Field(..., description="Implementation priority")
    implementation_time: str = Field(..., description="Estimated implementation time")
    required_resources: List[str] = Field(..., description="Resources needed for implementation")
    success_probability: float = Field(..., description="Probability of success (0-100)")


class CompetitiveAdvantage(BaseModel):
    """Model for competitive advantage opportunities."""
    
    keyword: str = Field(..., description="Target keyword")
    advantage_type: str = Field(..., description="Type of competitive advantage")
    current_ranking: Optional[int] = Field(default=None, description="Current ranking if any")
    gap_analysis: str = Field(..., description="Analysis of competitive gap")
    unique_angle: str = Field(..., description="Unique angle for content")
    differentiation_factors: List[str] = Field(..., description="Factors that differentiate")
    market_positioning: str = Field(..., description="Recommended market positioning")


class LongTailOpportunity(BaseModel):
    """Model for long-tail keyword opportunities."""
    
    keyword: str = Field(..., description="Long-tail keyword")
    base_keyword: str = Field(..., description="Base keyword it derives from")
    search_volume: int = Field(..., description="Monthly search volume")
    conversion_potential: float = Field(..., description="Conversion potential (0-100)")
    user_intent: str = Field(..., description="Specific user intent")
    content_format: str = Field(..., description="Recommended content format")
    targeting_strategy: str = Field(..., description="How to target this keyword")


class ContentGapOpportunity(BaseModel):
    """Model for content gap opportunities."""
    
    keyword: str = Field(..., description="Keyword with content gap")
    gap_type: str = Field(..., description="Type of content gap")
    missing_content_types: List[str] = Field(..., description="Content types that are missing")
    competitor_coverage: Dict[str, List[str]] = Field(..., description="What competitors are covering")
    opportunity_size: str = Field(..., description="Size of the opportunity")
    content_recommendations: List[str] = Field(..., description="Specific content recommendations")


class OpportunityAnalysisRequest(BaseModel):
    """Request model for opportunity analysis."""
    
    trend_analysis: Dict[str, Any] = Field(..., description="Trend analysis data")
    intent_analysis: Dict[str, Any] = Field(..., description="Intent analysis data")
    min_opportunity_score: Optional[float] = Field(
        default=50.0, 
        description="Minimum opportunity score threshold"
    )
    max_difficulty: Optional[float] = Field(
        default=70.0, 
        description="Maximum difficulty score threshold"
    )
    include_long_tail: bool = Field(default=True, description="Include long-tail opportunities")
    include_content_gaps: bool = Field(default=True, description="Include content gap analysis")


class OpportunityAnalysisResponse(BaseModel):
    """Complete opportunity analysis response."""
    
    request_id: str = Field(..., description="Unique request identifier")
    analysis_timestamp: datetime = Field(..., description="When analysis was performed")
    opportunities: List[ContentOpportunity] = Field(..., description="Identified opportunities")
    high_priority_opportunities: List[ContentOpportunity] = Field(..., description="High-priority opportunities")
    competitive_advantages: Optional[List[CompetitiveAdvantage]] = Field(
        default=None, 
        description="Competitive advantage opportunities"
    )
    long_tail_opportunities: Optional[List[LongTailOpportunity]] = Field(
        default=None, 
        description="Long-tail keyword opportunities"
    )
    content_gaps: Optional[List[ContentGapOpportunity]] = Field(
        default=None, 
        description="Content gap opportunities"
    )
    summary_metrics: Dict[str, Any] = Field(..., description="Summary metrics and statistics")
    implementation_roadmap: List[str] = Field(..., description="Recommended implementation roadmap")
