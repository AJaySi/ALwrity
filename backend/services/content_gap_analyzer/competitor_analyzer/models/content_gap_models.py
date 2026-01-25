"""
Content Gap Models for Competitor Analyzer Service

This module contains Pydantic models for content gap analysis,
gap identification, and content opportunity models.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from .shared import PriorityLevel, ImpactLevel, OpportunityLevel, Recommendation, ContentSuggestion


class GapType(str, Enum):
    """Content gap type enumeration."""
    TOPIC_GAP = "topic_gap"
    FORMAT_GAP = "format_gap"
    QUALITY_GAP = "quality_gap"
    FREQUENCY_GAP = "frequency_gap"
    AUDIENCE_GAP = "audience_gap"
    KEYWORD_GAP = "keyword_gap"
    INTENT_GAP = "intent_gap"
    TIMELINESS_GAP = "timeliness_gap"


class ContentFormat(str, Enum):
    """Content format enumeration."""
    BLOG_POST = "blog_post"
    ARTICLE = "article"
    CASE_STUDY = "case_study"
    WHITEPAPER = "whitepaper"
    EBOOK = "ebook"
    VIDEO = "video"
    PODCAST = "podcast"
    WEBINAR = "webinar"
    INFOGRAPHIC = "infographic"
    CHECKLIST = "checklist"
    TEMPLATE = "template"
    TOOL = "tool"
    CALCULATOR = "calculator"
    QUIZ = "quiz"
    SURVEY = "survey"
    RESEARCH_REPORT = "research_report"


class ContentGap(BaseModel):
    """Model for content gap identification."""
    
    gap_type: GapType = Field(..., description="Type of content gap")
    description: str = Field(..., description="Description of the gap")
    opportunity_level: OpportunityLevel = Field(..., description="Opportunity level")
    estimated_impact: ImpactLevel = Field(..., description="Estimated impact")
    content_suggestions: List[ContentSuggestion] = Field(..., description="Content suggestions to fill gap")
    priority: PriorityLevel = Field(..., description="Priority level")
    implementation_time: str = Field(..., description="Estimated implementation time")
    resources_required: List[str] = Field(default_factory=list, description="Resources required")
    success_metrics: List[str] = Field(default_factory=list, description="Success metrics")
    competitor_coverage: Dict[str, bool] = Field(..., description="Which competitors cover this gap")
    search_volume: Optional[int] = Field(default=None, description="Search volume for gap topic", ge=0)
    difficulty_score: Optional[float] = Field(default=None, description="Difficulty score", ge=0.0, le=10.0)
    identified_at: datetime = Field(default_factory=datetime.utcnow, description="When gap was identified")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TopicGap(BaseModel):
    """Model for topic-specific content gaps."""
    
    topic_name: str = Field(..., description="Topic with content gap")
    topic_category: str = Field(..., description="Category of the topic")
    gap_description: str = Field(..., description="Description of topic gap")
    competitor_coverage: List[str] = Field(..., description="Competitors covering this topic")
    coverage_depth: Dict[str, str] = Field(..., description="Depth of coverage by competitor")
    opportunity_score: float = Field(..., description="Opportunity score", ge=0.0, le=10.0)
    search_trend: str = Field(..., description="Search trend direction")
    seasonal_relevance: str = Field(..., description="Seasonal relevance")
    related_keywords: List[str] = Field(default_factory=list, description="Related keywords")
    content_angles: List[str] = Field(..., description="Potential content angles")
    expert_quotes: List[str] = Field(default_factory=list, description="Potential expert quotes to include")
    data_sources: List[str] = Field(default_factory=list, description="Data sources for content")
    identified_at: datetime = Field(default_factory=datetime.utcnow, description="When topic gap was identified")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FormatGap(BaseModel):
    """Model for format-specific content gaps."""
    
    target_format: ContentFormat = Field(..., description="Content format with gap")
    current_coverage: Dict[str, bool] = Field(..., description="Which competitors use this format")
    format_effectiveness: Dict[str, float] = Field(..., description="Effectiveness scores by competitor")
    audience_preference: float = Field(..., description="Audience preference score", ge=0.0, le=10.0)
    production_complexity: PriorityLevel = Field(..., description="Production complexity")
    resource_requirements: List[str] = Field(..., description="Resource requirements")
    estimated_engagement: float = Field(..., description="Estimated engagement score", ge=0.0, le=10.0)
    distribution_channels: List[str] = Field(..., description="Distribution channels")
    repurposing_potential: List[ContentFormat] = Field(..., description="Potential for repurposing")
    competitive_advantage: str = Field(..., description="Competitive advantage of this format")
    implementation_timeline: str = Field(..., description="Implementation timeline")
    identified_at: datetime = Field(default_factory=datetime.utcnow, description="When format gap was identified")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class QualityGap(BaseModel):
    """Model for quality-specific content gaps."""
    
    quality_dimension: str = Field(..., description="Quality dimension with gap")
    current_quality_scores: Dict[str, float] = Field(..., description="Current quality scores by competitor")
    industry_benchmark: float = Field(..., description="Industry benchmark score", ge=0.0, le=10.0)
    improvement_opportunity: float = Field(..., description="Improvement opportunity score", ge=0.0, le=10.0)
    improvement_areas: List[str] = Field(..., description="Areas for improvement")
    best_practices: List[str] = Field(..., description="Best practices to implement")
    measurement_criteria: List[str] = Field(..., description="Criteria to measure improvement")
    resource_investment: str = Field(..., description="Resource investment required")
    expected_roi: str = Field(..., description="Expected ROI from improvement")
    implementation_phases: List[str] = Field(..., description="Implementation phases")
    quality_tools: List[str] = Field(..., description="Tools to improve quality")
    identified_at: datetime = Field(default_factory=datetime.utcnow, description="When quality gap was identified")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FrequencyGap(BaseModel):
    """Model for frequency-specific content gaps."""
    
    content_category: str = Field(..., description="Content category with frequency gap")
    current_frequencies: Dict[str, str] = Field(..., description="Current publishing frequencies")
    optimal_frequency: str = Field(..., description="Optimal publishing frequency")
    audience_expectations: str = Field(..., description="Audience expectations")
    resource_constraints: List[str] = Field(..., description="Resource constraints")
    content_calendar_impact: str = Field(..., description="Impact on content calendar")
    automation_opportunities: List[str] = Field(..., description="Automation opportunities")
    quality_vs_quantity_balance: str = Field(..., description="Quality vs quantity considerations")
    seasonal_adjustments: Dict[str, str] = Field(..., description="Seasonal frequency adjustments")
    competitive_frequency_analysis: Dict[str, float] = Field(..., description="Competitive frequency analysis")
    implementation_strategy: str = Field(..., description="Implementation strategy")
    identified_at: datetime = Field(default_factory=datetime.utcnow, description="When frequency gap was identified")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ContentGapAnalysis(BaseModel):
    """Model for comprehensive content gap analysis."""
    
    industry: str = Field(..., description="Industry analyzed")
    competitor_urls: List[str] = Field(..., description="Competitors analyzed")
    total_gaps_identified: int = Field(..., description="Total gaps identified", ge=0)
    gaps_by_type: Dict[GapType, int] = Field(..., description="Gaps categorized by type")
    high_priority_gaps: List[ContentGap] = Field(..., description="High priority gaps")
    topic_gaps: List[TopicGap] = Field(..., description="Topic-specific gaps")
    format_gaps: List[FormatGap] = Field(..., description="Format-specific gaps")
    quality_gaps: List[QualityGap] = Field(..., description="Quality-specific gaps")
    frequency_gaps: List[FrequencyGap] = Field(..., description="Frequency-specific gaps")
    gap_summary: Dict[str, Any] = Field(..., description="Summary statistics of gaps")
    recommendations: List[Recommendation] = Field(..., description="Recommendations to address gaps")
    implementation_roadmap: List[str] = Field(..., description="Implementation roadmap")
    expected_impact: str = Field(..., description="Expected impact of addressing gaps")
    analysis_date: datetime = Field(default_factory=datetime.utcnow, description="Analysis date")
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in analysis")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ContentOpportunity(BaseModel):
    """Model for content opportunities derived from gap analysis."""
    
    opportunity_name: str = Field(..., description="Name of content opportunity")
    opportunity_type: GapType = Field(..., description="Type of opportunity")
    description: str = Field(..., description="Description of opportunity")
    target_audience: List[str] = Field(..., description="Target audience segments")
    content_formats: List[ContentFormat] = Field(..., description="Recommended content formats")
    estimated_traffic: int = Field(default=0, description="Estimated traffic potential", ge=0)
    conversion_potential: float = Field(..., description="Conversion potential score", ge=0.0, le=10.0)
    competitive_advantage: str = Field(..., description="Competitive advantage")
    time_to_create: str = Field(..., description="Time to create content")
    resource_requirements: List[str] = Field(..., description="Resource requirements")
    success_metrics: List[str] = Field(..., description="Success metrics")
    related_gaps: List[str] = Field(..., description="Related content gaps")
    priority_score: float = Field(..., description="Priority score", ge=0.0, le=10.0)
    identified_at: datetime = Field(default_factory=datetime.utcnow, description="When opportunity was identified")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GapRecommendation(BaseModel):
    """Model for specific recommendations to address content gaps."""
    
    gap_id: str = Field(..., description="ID of the gap being addressed")
    recommendation_type: str = Field(..., description="Type of recommendation")
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed recommendation description")
    implementation_steps: List[str] = Field(..., description="Implementation steps")
    expected_outcomes: List[str] = Field(..., description="Expected outcomes")
    timeline: str = Field(..., description="Implementation timeline")
    budget_estimate: Optional[float] = Field(default=None, description="Budget estimate", ge=0)
    team_requirements: List[str] = Field(..., description="Team requirements")
    tools_needed: List[str] = Field(..., description="Tools needed")
    success_criteria: List[str] = Field(..., description="Success criteria")
    risk_factors: List[str] = Field(..., description="Risk factors")
    mitigation_strategies: List[str] = Field(..., description="Mitigation strategies")
    priority: PriorityLevel = Field(..., description="Recommendation priority")
    impact_level: ImpactLevel = Field(..., description="Expected impact level")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When recommendation was created")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ContentGapTrend(BaseModel):
    """Model for tracking content gap trends over time."""
    
    gap_type: GapType = Field(..., description="Type of gap being tracked")
    gap_count: int = Field(..., description="Number of gaps of this type", ge=0)
    average_opportunity_score: float = Field(..., description="Average opportunity score", ge=0.0, le=10.0)
    trend_direction: str = Field(..., description="Trend direction")
    period: str = Field(..., description="Time period")
    addressed_gaps: int = Field(default=0, description="Number of gaps addressed", ge=0)
    new_gaps: int = Field(default=0, description="Number of new gaps", ge=0)
    competitor_changes: Dict[str, str] = Field(..., description="Changes in competitor coverage")
    market_changes: List[str] = Field(..., description="Market changes affecting gaps")
    trend_significance: str = Field(..., description="Significance of trend")
    forecast_trend: str = Field(..., description="Forecasted trend")
    recorded_at: datetime = Field(default_factory=datetime.utcnow, description="When trend was recorded")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
