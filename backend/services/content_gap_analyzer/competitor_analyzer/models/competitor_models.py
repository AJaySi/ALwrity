"""
Competitor Models for Competitor Analyzer Service

This module contains Pydantic models for competitor analysis,
profiles, metrics, and related data structures.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from enum import Enum

from .shared import PriorityLevel, ImpactLevel, Metric, ContentSuggestion


class CompetitorSize(str, Enum):
    """Competitor size enumeration."""
    STARTUP = "startup"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class CompetitorType(str, Enum):
    """Competitor type enumeration."""
    DIRECT = "direct"
    INDIRECT = "indirect"
    SUBSTITUTE = "substitute"
    POTENTIAL = "potential"


class ContentType(str, Enum):
    """Content type enumeration."""
    BLOG_POST = "blog_post"
    ARTICLE = "article"
    CASE_STUDY = "case_study"
    WHITEPAPER = "whitepaper"
    EBOOK = "ebook"
    VIDEO = "video"
    PODCAST = "podcast"
    WEBINAR = "webinar"
    INFOGRAPHIC = "infographic"
    PRESS_RELEASE = "press_release"


class PublishingFrequency(str, Enum):
    """Publishing frequency enumeration."""
    DAILY = "daily"
    WEEKLY = "weekly"
    BI_WEEKLY = "bi_weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    IRREGULAR = "irregular"


class EngagementMetrics(BaseModel):
    """Model for engagement metrics."""
    
    avg_time_on_page: int = Field(..., description="Average time on page in seconds", ge=0)
    bounce_rate: float = Field(..., description="Bounce rate percentage", ge=0.0, le=1.0)
    social_shares: int = Field(..., description="Number of social shares", ge=0)
    comments_count: int = Field(default=0, description="Number of comments", ge=0)
    page_views: int = Field(default=0, description="Page views", ge=0)
    unique_visitors: int = Field(default=0, description="Unique visitors", ge=0)
    conversion_rate: float = Field(default=0.0, description="Conversion rate", ge=0.0, le=1.0)


class SEOMetrics(BaseModel):
    """Model for SEO metrics."""
    
    domain_authority: int = Field(..., description="Domain authority score", ge=0, le=100)
    page_authority: int = Field(default=0, description="Page authority score", ge=0, le=100)
    page_speed: int = Field(..., description="Page speed score", ge=0, le=100)
    mobile_friendly: bool = Field(..., description="Mobile-friendly status")
    ssl_certificate: bool = Field(default=True, description="SSL certificate status")
    indexed_pages: int = Field(default=0, description="Number of indexed pages", ge=0)
    backlinks_count: int = Field(default=0, description="Number of backlinks", ge=0)
    organic_traffic: int = Field(default=0, description="Organic traffic estimate", ge=0)
    keyword_rankings: int = Field(default=0, description="Number of keyword rankings", ge=0)


class ContentAnalysis(BaseModel):
    """Model for content analysis results."""
    
    content_count: int = Field(..., description="Total number of content pieces", ge=0)
    avg_quality_score: float = Field(..., description="Average quality score", ge=0.0, le=10.0)
    top_keywords: List[str] = Field(..., description="Top performing keywords")
    content_types: List[ContentType] = Field(..., description="Types of content produced")
    publishing_frequency: PublishingFrequency = Field(..., description="Publishing frequency")
    avg_word_count: int = Field(default=1000, description="Average word count per piece", ge=0)
    content_depth_score: float = Field(default=5.0, description="Content depth score", ge=0.0, le=10.0)
    freshness_score: float = Field(default=5.0, description="Content freshness score", ge=0.0, le=10.0)
    topic_diversity: float = Field(default=5.0, description="Topic diversity score", ge=0.0, le=10.0)


class CompetitorProfile(BaseModel):
    """Model for competitor profile information."""
    
    url: HttpUrl = Field(..., description="Competitor website URL")
    name: str = Field(..., description="Competitor name")
    description: Optional[str] = Field(default=None, description="Competitor description")
    founded_year: Optional[int] = Field(default=None, description="Year founded", ge=1900)
    company_size: Optional[CompetitorSize] = Field(default=None, description="Company size")
    competitor_type: CompetitorType = Field(..., description="Type of competitor")
    industry_focus: List[str] = Field(default_factory=list, description="Industry focus areas")
    target_audience: List[str] = Field(default_factory=list, description="Target audience segments")
    unique_selling_proposition: Optional[str] = Field(default=None, description="Unique selling proposition")
    market_position: Optional[str] = Field(default=None, description="Market position")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Profile last updated")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CompetitorMetrics(BaseModel):
    """Model for comprehensive competitor metrics."""
    
    engagement_metrics: EngagementMetrics = Field(..., description="Engagement metrics")
    seo_metrics: SEOMetrics = Field(..., description="SEO metrics")
    content_analysis: ContentAnalysis = Field(..., description="Content analysis results")
    estimated_monthly_traffic: int = Field(default=0, description="Estimated monthly traffic", ge=0)
    estimated_revenue: Optional[float] = Field(default=None, description="Estimated annual revenue", ge=0)
    employee_count: Optional[int] = Field(default=None, description="Number of employees", ge=0)
    market_share_percentage: float = Field(default=0.0, description="Market share percentage", ge=0.0, le=100.0)
    growth_rate: Optional[float] = Field(default=None, description="Annual growth rate", ge=-100.0, le=1000.0)
    customer_satisfaction: Optional[float] = Field(default=None, description="Customer satisfaction score", ge=0.0, le=10.0)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CompetitorAnalysis(BaseModel):
    """Model for complete competitor analysis results."""
    
    profile: CompetitorProfile = Field(..., description="Competitor profile information")
    metrics: CompetitorMetrics = Field(..., description="Competitor metrics")
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Identified weaknesses")
    opportunities: List[str] = Field(default_factory=list, description="Identified opportunities")
    threats: List[str] = Field(default_factory=list, description="Identified threats")
    content_suggestions: List[ContentSuggestion] = Field(default_factory=list, description="Content suggestions")
    competitive_advantages: List[str] = Field(default_factory=list, description="Competitive advantages")
    analysis_date: datetime = Field(default_factory=datetime.utcnow, description="When analysis was performed")
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in analysis")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CompetitorComparison(BaseModel):
    """Model for comparing multiple competitors."""
    
    competitor_analyses: List[CompetitorAnalysis] = Field(..., description="List of competitor analyses")
    comparison_metrics: List[Metric] = Field(..., description="Comparison metrics")
    ranking_by_metric: Dict[str, List[str]] = Field(..., description="Ranking of competitors by metric")
    market_leaders: Dict[str, str] = Field(..., description="Market leaders by category")
    performance_gaps: List[str] = Field(default_factory=list, description="Performance gaps identified")
    benchmark_opportunities: List[str] = Field(default_factory=list, description="Benchmark opportunities")
    comparison_date: datetime = Field(default_factory=datetime.utcnow, description="When comparison was made")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CompetitorInsight(BaseModel):
    """Model for competitor-specific insights."""
    
    competitor_url: HttpUrl = Field(..., description="Competitor URL")
    insight_type: str = Field(..., description="Type of insight")
    insight: str = Field(..., description="The insight content")
    actionable: bool = Field(..., description="Whether insight is actionable")
    priority: PriorityLevel = Field(..., description="Priority level")
    estimated_impact: ImpactLevel = Field(..., description="Estimated impact")
    implementation_effort: str = Field(..., description="Implementation effort required")
    supporting_data: Dict[str, Any] = Field(default_factory=dict, description="Supporting data for insight")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When insight was generated")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CompetitorTrend(BaseModel):
    """Model for competitor trend analysis."""
    
    competitor_url: HttpUrl = Field(..., description="Competitor URL")
    metric_name: str = Field(..., description="Metric being tracked")
    historical_values: List[float] = Field(..., description="Historical values")
    trend_direction: str = Field(..., description="Trend direction (up/down/stable)")
    trend_percentage: float = Field(..., description="Trend percentage change")
    time_period: str = Field(..., description="Time period for trend analysis")
    significance: str = Field(..., description="Significance of trend")
    forecast_values: Optional[List[float]] = Field(default=None, description="Forecasted values")
    confidence_interval: Optional[float] = Field(default=None, description="Confidence interval for forecast")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Trend last updated")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CompetitorAlert(BaseModel):
    """Model for competitor alerts and notifications."""
    
    competitor_url: HttpUrl = Field(..., description="Competitor URL")
    alert_type: str = Field(..., description="Type of alert")
    severity: PriorityLevel = Field(..., description="Alert severity")
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Alert description")
    trigger_condition: str = Field(..., description="Condition that triggered alert")
    action_required: bool = Field(..., description="Whether action is required")
    suggested_actions: List[str] = Field(default_factory=list, description="Suggested actions")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When alert was created")
    acknowledged: bool = Field(default=False, description="Whether alert has been acknowledged")
    resolved_at: Optional[datetime] = Field(default=None, description="When alert was resolved")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
