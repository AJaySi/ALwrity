"""
Market Analysis Models for Competitor Analyzer Service

This module contains Pydantic models for market positioning,
market share analysis, and competitive landscape analysis.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from .shared import PriorityLevel, ImpactLevel, Recommendation, AIInsight


class MarketPosition(str, Enum):
    """Market position enumeration."""
    LEADER = "leader"
    CHALLENGER = "challenger"
    FOLLOWER = "follower"
    NICHE = "niche"
    EMERGING = "emerging"


class MarketShareType(str, Enum):
    """Market share type enumeration."""
    REVENUE = "revenue"
    CUSTOMER_BASE = "customer_base"
    TRAFFIC = "traffic"
    CONTENT_VOLUME = "content_volume"
    BRAND_AWARENESS = "brand_awareness"


class CompetitiveIntensity(str, Enum):
    """Competitive intensity enumeration."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class MarketSegment(BaseModel):
    """Model for market segment analysis."""
    
    segment_name: str = Field(..., description="Name of market segment")
    segment_size: float = Field(..., description="Size of segment (in millions)", ge=0)
    growth_rate: float = Field(..., description="Annual growth rate percentage", ge=-100.0, le=1000.0)
    competitor_count: int = Field(..., description="Number of competitors in segment", ge=0)
    market_leader: Optional[str] = Field(default=None, description="Market leader in segment")
    entry_barriers: List[str] = Field(default_factory=list, description="Entry barriers")
    key_success_factors: List[str] = Field(default_factory=list, description="Key success factors")
    trends: List[str] = Field(default_factory=list, description="Current trends in segment")
    opportunities: List[str] = Field(default_factory=list, description="Opportunities in segment")


class MarketShare(BaseModel):
    """Model for market share data."""
    
    competitor_url: str = Field(..., description="Competitor URL")
    competitor_name: str = Field(..., description="Competitor name")
    share_type: MarketShareType = Field(..., description="Type of market share")
    share_percentage: float = Field(..., description="Market share percentage", ge=0.0, le=100.0)
    share_value: Optional[float] = Field(default=None, description="Market share value", ge=0)
    change_from_previous_period: float = Field(default=0.0, description="Change from previous period")
    period: str = Field(..., description="Time period for share data")
    data_source: str = Field(..., description="Source of market share data")
    confidence_level: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in data")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Data last updated")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MarketPositioning(BaseModel):
    """Model for market positioning analysis."""
    
    market_leader: str = Field(..., description="Identified market leader")
    content_leader: str = Field(..., description="Identified content leader")
    quality_leader: str = Field(..., description="Identified quality leader")
    innovation_leader: str = Field(..., description="Identified innovation leader")
    market_gaps: List[str] = Field(..., description="Identified market gaps")
    opportunities: List[str] = Field(..., description="Market opportunities")
    competitive_advantages: List[str] = Field(..., description="Competitive advantages")
    strategic_recommendations: List[Recommendation] = Field(..., description="Strategic recommendations")
    positioning_map: Dict[str, List[str]] = Field(..., description="Positioning map data")
    market_maturity: str = Field(..., description="Market maturity level")
    growth_potential: ImpactLevel = Field(..., description="Growth potential")
    analysis_date: datetime = Field(default_factory=datetime.utcnow, description="Analysis date")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CompetitiveLandscape(BaseModel):
    """Model for competitive landscape analysis."""
    
    total_competitors: int = Field(..., description="Total number of competitors", ge=0)
    direct_competitors: int = Field(..., description="Number of direct competitors", ge=0)
    indirect_competitors: int = Field(..., description="Number of indirect competitors", ge=0)
    market_concentration: float = Field(..., description="Market concentration index", ge=0.0, le=1.0)
    competitive_intensity: CompetitiveIntensity = Field(..., description="Competitive intensity level")
    market_leaders: List[str] = Field(..., description="Market leaders")
    emerging_competitors: List[str] = Field(..., description="Emerging competitors")
    market_trends: List[str] = Field(..., description="Market trends")
    disruption_risks: List[str] = Field(..., description="Disruption risks")
    entry_barriers: List[str] = Field(..., description="Entry barriers")
    success_factors: List[str] = Field(..., description="Key success factors")
    analysis_date: datetime = Field(default_factory=datetime.utcnow, description="Analysis date")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MarketTrend(BaseModel):
    """Model for market trend analysis."""
    
    trend_name: str = Field(..., description="Name of trend")
    trend_description: str = Field(..., description="Description of trend")
    trend_direction: str = Field(..., description="Trend direction (growing/declining/stable)")
    impact_level: ImpactLevel = Field(..., description="Impact level on market")
    time_horizon: str = Field(..., description="Time horizon for trend")
    confidence_level: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in trend analysis")
    supporting_data: Dict[str, Any] = Field(default_factory=dict, description="Supporting data")
    implications: List[str] = Field(..., description="Implications of trend")
    opportunities: List[str] = Field(..., description="Opportunities from trend")
    threats: List[str] = Field(..., description="Threats from trend")
    identified_at: datetime = Field(default_factory=datetime.utcnow, description="When trend was identified")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MarketOpportunity(BaseModel):
    """Model for market opportunity analysis."""
    
    opportunity_name: str = Field(..., description="Name of opportunity")
    opportunity_type: str = Field(..., description="Type of opportunity")
    description: str = Field(..., description="Description of opportunity")
    market_size: float = Field(..., description="Potential market size", ge=0)
    growth_potential: float = Field(..., description="Growth potential percentage", ge=0.0)
    competition_level: CompetitiveIntensity = Field(..., description="Competition level")
    time_to_market: str = Field(..., description="Estimated time to market")
    required_investment: Optional[float] = Field(default=None, description="Required investment", ge=0)
    expected_roi: Optional[float] = Field(default=None, description="Expected ROI percentage", ge=-100.0, le=1000.0)
    risk_level: PriorityLevel = Field(..., description="Risk level")
    success_factors: List[str] = Field(..., description="Success factors")
    barriers: List[str] = Field(..., description="Barriers to entry")
    strategic_fit: ImpactLevel = Field(..., description="Strategic fit level")
    identified_at: datetime = Field(default_factory=datetime.utcnow, description="When opportunity was identified")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MarketAnalysis(BaseModel):
    """Model for comprehensive market analysis."""
    
    industry: str = Field(..., description="Industry analyzed")
    market_size: float = Field(..., description="Total market size", ge=0)
    growth_rate: float = Field(..., description="Market growth rate", ge=-100.0, le=1000.0)
    market_positioning: MarketPositioning = Field(..., description="Market positioning analysis")
    competitive_landscape: CompetitiveLandscape = Field(..., description="Competitive landscape")
    market_shares: List[MarketShare] = Field(..., description="Market share data")
    market_segments: List[MarketSegment] = Field(..., description="Market segments")
    market_trends: List[MarketTrend] = Field(..., description="Market trends")
    opportunities: List[MarketOpportunity] = Field(..., description="Market opportunities")
    insights: List[AIInsight] = Field(..., description="AI-generated insights")
    recommendations: List[Recommendation] = Field(..., description="Strategic recommendations")
    analysis_date: datetime = Field(default_factory=datetime.utcnow, description="Analysis date")
    data_period: str = Field(..., description="Time period of data analyzed")
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Overall confidence score")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MarketForecast(BaseModel):
    """Model for market forecasting."""
    
    forecast_type: str = Field(..., description="Type of forecast")
    time_horizon: str = Field(..., description="Forecast time horizon")
    methodology: str = Field(..., description="Forecast methodology")
    assumptions: List[str] = Field(..., description="Forecast assumptions")
    market_size_forecast: List[float] = Field(..., description="Market size forecast values")
    growth_rate_forecast: List[float] = Field(..., description="Growth rate forecast values")
    confidence_intervals: List[float] = Field(..., description="Confidence intervals")
    key_drivers: List[str] = Field(..., description="Key growth drivers")
    risk_factors: List[str] = Field(..., description="Risk factors")
    scenarios: Dict[str, Dict[str, Any]] = Field(..., description="Alternative scenarios")
    forecast_date: datetime = Field(default_factory=datetime.utcnow, description="Forecast date")
    next_update: datetime = Field(..., description="Next forecast update date")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MarketBenchmark(BaseModel):
    """Model for market benchmarking."""
    
    benchmark_name: str = Field(..., description="Name of benchmark")
    benchmark_type: str = Field(..., description="Type of benchmark")
    industry_average: float = Field(..., description="Industry average value")
    top_quartile: float = Field(..., description="Top quartile value")
    median: float = Field(..., description="Median value")
    bottom_quartile: float = Field(..., description="Bottom quartile value")
    your_value: float = Field(..., description="Your value")
    percentile_rank: float = Field(..., description="Your percentile rank", ge=0.0, le=100.0)
    performance_gap: float = Field(..., description="Gap to top quartile")
    improvement_potential: float = Field(..., description="Improvement potential percentage", ge=0.0)
    benchmark_date: datetime = Field(default_factory=datetime.utcnow, description="Benchmark date")
    data_source: str = Field(..., description="Data source for benchmark")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
