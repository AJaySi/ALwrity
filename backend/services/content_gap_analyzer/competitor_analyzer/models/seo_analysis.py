"""
SEO Analysis Models for Competitor Analyzer Service

This module contains Pydantic models for SEO gap analysis,
SEO comparisons, and SEO recommendation models.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from .shared import PriorityLevel, ImpactLevel, Recommendation


class SEOGapType(str, Enum):
    """SEO gap type enumeration."""
    KEYWORD_GAP = "keyword_gap"
    TECHNICAL_SEO_GAP = "technical_seo_gap"
    CONTENT_SEO_GAP = "content_seo_gap"
    BACKLINK_GAP = "backlink_gap"
    LOCAL_SEO_GAP = "local_seo_gap"
    MOBILE_SEO_GAP = "mobile_seo_gap"
    SPEED_GAP = "speed_gap"
    STRUCTURED_DATA_GAP = "structured_data_gap"


class KeywordDifficulty(str, Enum):
    """Keyword difficulty enumeration."""
    VERY_EASY = "very_easy"
    EASY = "easy"
    MODERATE = "moderate"
    DIFFICULT = "difficult"
    VERY_DIFFICULT = "very_difficult"


class SearchIntent(str, Enum):
    """Search intent enumeration."""
    INFORMATIONAL = "informational"
    COMMERCIAL = "commercial"
    TRANSACTIONAL = "transactional"
    NAVIGATIONAL = "navigational"


class SEOMetric(BaseModel):
    """Model for individual SEO metrics."""
    
    metric_name: str = Field(..., description="Name of SEO metric")
    value: float = Field(..., description="Metric value")
    unit: Optional[str] = Field(default=None, description="Unit of measurement")
    benchmark: Optional[float] = Field(default=None, description="Industry benchmark")
    status: str = Field(..., description="Status (good/fair/poor)")
    improvement_potential: float = Field(..., description="Improvement potential", ge=0.0, le=10.0)
    last_updated: datetime = Field(..., description="When metric was last updated")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class KeywordGap(BaseModel):
    """Model for keyword gap analysis."""
    
    keyword: str = Field(..., description="Keyword with gap")
    search_volume: int = Field(..., description="Monthly search volume", ge=0)
    keyword_difficulty: KeywordDifficulty = Field(..., description="Keyword difficulty")
    search_intent: SearchIntent = Field(..., description="Search intent")
    competitor_rankings: Dict[str, int] = Field(..., description="Competitor rankings")
    your_ranking: Optional[int] = Field(default=None, description="Your ranking", ge=0)
    gap_opportunity: float = Field(..., description="Gap opportunity score", ge=0.0, le=10.0)
    estimated_traffic_potential: int = Field(default=0, description="Estimated traffic potential", ge=0)
    content_difficulty: float = Field(..., description="Content creation difficulty", ge=0.0, le=10.0)
    competition_level: str = Field(..., description="Competition level")
    trend_direction: str = Field(..., description="Search trend direction")
    seasonal_pattern: Optional[str] = Field(default=None, description="Seasonal pattern")
    related_keywords: List[str] = Field(default_factory=list, description="Related keywords")
    content_suggestions: List[str] = Field(..., description="Content suggestions")
    priority: PriorityLevel = Field(..., description="Priority level")
    identified_at: datetime = Field(default_factory=datetime.utcnow, description="When gap was identified")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TechnicalSEOGap(BaseModel):
    """Model for technical SEO gap analysis."""
    
    gap_type: SEOGapType = Field(..., description="Type of technical SEO gap")
    issue_description: str = Field(..., description="Description of technical issue")
    severity: PriorityLevel = Field(..., description="Severity of issue")
    impact_level: ImpactLevel = Field(..., description="Impact on SEO performance")
    current_status: str = Field(..., description="Current status")
    ideal_status: str = Field(..., description="Ideal status")
    competitor_performance: Dict[str, str] = Field(..., description="Competitor performance")
    fix_complexity: PriorityLevel = Field(..., description="Complexity of fix")
    estimated_fix_time: str = Field(..., description="Estimated time to fix")
    technical_requirements: List[str] = Field(..., description="Technical requirements")
    tools_needed: List[str] = Field(..., description="Tools needed for fix")
    expected_improvement: str = Field(..., description="Expected improvement")
    implementation_steps: List[str] = Field(..., description="Implementation steps")
    monitoring_metrics: List[str] = Field(..., description="Metrics to monitor")
    identified_at: datetime = Field(default_factory=datetime.utcnow, description="When gap was identified")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BacklinkGap(BaseModel):
    """Model for backlink gap analysis."""
    
    competitor_url: str = Field(..., description="Competitor URL")
    backlink_source: str = Field(..., description="Source of backlink")
    domain_authority: int = Field(..., description="Domain authority of source", ge=0, le=100)
    page_authority: int = Field(..., description="Page authority of source", ge=0, le=100)
    relevance_score: float = Field(..., description="Relevance score", ge=0.0, le=10.0)
    traffic_potential: int = Field(default=0, description="Traffic potential", ge=0)
    acquisition_difficulty: PriorityLevel = Field(..., description="Difficulty of acquisition")
    estimated_cost: Optional[float] = Field(default=None, description="Estimated cost", ge=0)
    outreach_strategy: str = Field(..., description="Outreach strategy")
    content_angle: str = Field(..., description="Content angle for acquisition")
    success_probability: float = Field(..., description="Success probability", ge=0.0, le=1.0)
    time_to_acquire: str = Field(..., description="Time to acquire")
    competitor_coverage: List[str] = Field(..., description="Which competitors have this backlink")
    identified_at: datetime = Field(default_factory=datetime.utcnow, description="When gap was identified")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SEOComparison(BaseModel):
    """Model for SEO comparison between competitors."""
    
    comparison_date: datetime = Field(..., description="When comparison was made")
    compared_urls: List[str] = Field(..., description="URLs compared")
    seo_metrics: List[SEOMetric] = Field(..., description="SEO metrics compared")
    ranking_comparison: Dict[str, Dict[str, int]] = Field(..., description="Ranking comparison by keyword")
    technical_seo_comparison: Dict[str, List[str]] = Field(..., description="Technical SEO comparison")
    backlink_comparison: Dict[str, Dict[str, Any]] = Field(..., description="Backlink comparison")
    content_seo_comparison: Dict[str, Dict[str, Any]] = Field(..., description="Content SEO comparison")
    overall_seo_scores: Dict[str, float] = Field(..., description="Overall SEO scores")
    strengths_by_competitor: Dict[str, List[str]] = Field(..., description="Strengths by competitor")
    weaknesses_by_competitor: Dict[str, List[str]] = Field(..., description="Weaknesses by competitor")
    opportunities: List[str] = Field(..., description="SEO opportunities identified")
    threats: List[str] = Field(..., description="SEO threats identified")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SEOGap(BaseModel):
    """Model for comprehensive SEO gap analysis."""
    
    gap_type: SEOGapType = Field(..., description="Type of SEO gap")
    description: str = Field(..., description="Description of the SEO gap")
    impact_level: ImpactLevel = Field(..., description="Impact on SEO performance")
    opportunity_level: PriorityLevel = Field(..., description="Opportunity level")
    current_performance: Dict[str, float] = Field(..., description="Current performance metrics")
    competitor_performance: Dict[str, float] = Field(..., description="Competitor performance metrics")
    improvement_potential: float = Field(..., description="Improvement potential score", ge=0.0, le=10.0)
    implementation_complexity: PriorityLevel = Field(..., description="Implementation complexity")
    estimated_time_to_impact: str = Field(..., description="Estimated time to see impact")
    resource_requirements: List[str] = Field(..., description="Resource requirements")
    success_metrics: List[str] = Field(..., description="Success metrics to track")
    recommendations: List[Recommendation] = Field(..., description="Specific recommendations")
    related_gaps: List[str] = Field(..., description="Related SEO gaps")
    priority_score: float = Field(..., description="Priority score", ge=0.0, le=10.0)
    confidence_level: float = Field(..., description="Confidence in gap analysis", ge=0.0, le=1.0)
    identified_at: datetime = Field(default_factory=datetime.utcnow, description="When gap was identified")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SEORecommendation(BaseModel):
    """Model for SEO-specific recommendations."""
    
    recommendation_type: SEOGapType = Field(..., description="Type of SEO recommendation")
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed recommendation description")
    priority: PriorityLevel = Field(..., description="Recommendation priority")
    expected_impact: ImpactLevel = Field(..., description="Expected impact")
    implementation_steps: List[str] = Field(..., description="Implementation steps")
    tools_needed: List[str] = Field(..., description="Tools needed")
    timeline: str = Field(..., description="Implementation timeline")
    budget_estimate: Optional[float] = Field(default=None, description="Budget estimate", ge=0)
    team_requirements: List[str] = Field(..., description="Team requirements")
    success_criteria: List[str] = Field(..., description="Success criteria")
    risk_factors: List[str] = Field(..., description="Risk factors")
    monitoring_plan: str = Field(..., description="Monitoring plan")
    related_recommendations: List[str] = Field(..., description="Related recommendations")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When recommendation was created")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SEOAnalysis(BaseModel):
    """Model for comprehensive SEO analysis."""
    
    industry: str = Field(..., description="Industry analyzed")
    competitor_urls: List[str] = Field(..., description="Competitors analyzed")
    analysis_date: datetime = Field(..., description="When analysis was performed")
    total_gaps_identified: int = Field(..., description="Total SEO gaps identified", ge=0)
    gaps_by_type: Dict[SEOGapType, int] = Field(..., description="Gaps categorized by type")
    keyword_gaps: List[KeywordGap] = Field(..., description="Keyword-specific gaps")
    technical_seo_gaps: List[TechnicalSEOGap] = Field(..., description="Technical SEO gaps")
    backlink_gaps: List[BacklinkGap] = Field(..., description="Backlink gaps")
    seo_comparisons: List[SEOComparison] = Field(..., description="SEO comparisons")
    overall_seo_scores: Dict[str, float] = Field(..., description="Overall SEO scores")
    high_priority_gaps: List[SEOGap] = Field(..., description="High priority gaps")
    recommendations: List[SEORecommendation] = Field(..., description="SEO recommendations")
    implementation_roadmap: List[str] = Field(..., description="Implementation roadmap")
    expected_impact_timeline: str = Field(..., description="Expected impact timeline")
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in analysis")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SEOTrend(BaseModel):
    """Model for SEO trend tracking."""
    
    metric_name: str = Field(..., description="SEO metric being tracked")
    competitor_url: str = Field(..., description="Competitor URL")
    historical_values: List[float] = Field(..., description="Historical values")
    trend_direction: str = Field(..., description="Trend direction")
    trend_percentage: float = Field(..., description="Trend percentage change")
    time_period: str = Field(..., description="Time period for trend")
    significance: str = Field(..., description="Significance of trend")
    forecast_values: Optional[List[float]] = Field(default=None, description="Forecasted values")
    confidence_interval: Optional[float] = Field(default=None, description="Confidence interval")
    influencing_factors: List[str] = Field(..., description="Factors influencing trend")
    seasonal_patterns: Optional[str] = Field(default=None, description="Seasonal patterns")
    recorded_at: datetime = Field(default_factory=datetime.utcnow, description="When trend was recorded")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SEOAlert(BaseModel):
    """Model for SEO alerts and notifications."""
    
    alert_type: SEOGapType = Field(..., description="Type of SEO alert")
    severity: PriorityLevel = Field(..., description="Alert severity")
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Alert description")
    trigger_condition: str = Field(..., description="Condition that triggered alert")
    affected_urls: List[str] = Field(..., description="Affected URLs")
    impact_assessment: str = Field(..., description="Impact assessment")
    recommended_actions: List[str] = Field(..., description="Recommended actions")
    urgency: PriorityLevel = Field(..., description="Alert urgency")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When alert was created")
    acknowledged: bool = Field(default=False, description="Whether alert has been acknowledged")
    resolved_at: Optional[datetime] = Field(default=None, description="When alert was resolved")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
