"""
Trend Analysis Models

Pydantic models for keyword trend analysis and seasonal insights.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TrendDirection(str, Enum):
    """Enumeration for trend directions."""
    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"
    SEASONAL = "seasonal"


class CompetitionLevel(str, Enum):
    """Enumeration for competition levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class SearchIntent(str, Enum):
    """Enumeration for search intent types."""
    INFORMATIONAL = "informational"
    TRANSACTIONAL = "transactional"
    NAVIGATIONAL = "navigational"
    COMMERCIAL = "commercial"


class KeywordTrendData(BaseModel):
    """Detailed keyword trend information."""
    
    keyword: str = Field(..., description="The keyword being analyzed")
    search_volume: int = Field(..., description="Estimated monthly search volume")
    difficulty_score: float = Field(..., description="Keyword difficulty (0-100)")
    trend_direction: TrendDirection = Field(..., description="Trend direction")
    competition_level: CompetitionLevel = Field(..., description="Competition level")
    primary_intent: SearchIntent = Field(..., description="Primary search intent")
    cost_per_click: float = Field(..., description="Estimated CPC")
    seasonal_factor: float = Field(..., description="Seasonal trend multiplier")
    growth_rate: Optional[float] = Field(
        default=None, 
        description="Monthly growth rate percentage"
    )


class SeasonalTrend(BaseModel):
    """Seasonal trend information for keywords."""
    
    month: str = Field(..., description="Month name")
    search_volume_multiplier: float = Field(..., description="Volume multiplier vs baseline")
    trend_intensity: str = Field(..., description="Intensity of seasonal trend")
    recommended_content: List[str] = Field(..., description="Content recommendations for this period")


class TrendMetrics(BaseModel):
    """Aggregate trend metrics for analysis."""
    
    total_keywords_analyzed: int = Field(..., description="Total keywords in analysis")
    rising_trends_count: int = Field(..., description="Count of rising trends")
    declining_trends_count: int = Field(..., description="Count of declining trends")
    average_difficulty: float = Field(..., description="Average difficulty score")
    high_opportunity_keywords: int = Field(..., description="Count of high-opportunity keywords")
    seasonal_keywords: int = Field(..., description="Count of seasonal keywords")


class TrendForecast(BaseModel):
    """Forecast data for keyword trends."""
    
    forecast_period: str = Field(..., description="Forecast period (e.g., '3_months', '6_months')")
    predicted_volume_change: float = Field(..., description="Predicted volume change percentage")
    confidence_level: float = Field(..., description="Confidence in forecast (0-100)")
    key_factors: List[str] = Field(..., description="Factors influencing the forecast")


class TrendAnalysisRequest(BaseModel):
    """Request model for trend analysis."""
    
    industry: str = Field(..., description="Industry category")
    target_keywords: Optional[List[str]] = Field(
        default=None, 
        description="Specific keywords to analyze"
    )
    include_seasonal_analysis: bool = Field(
        default=True, 
        description="Whether to include seasonal analysis"
    )
    forecast_period: Optional[str] = Field(
        default="3_months", 
        description="Forecast period for trend prediction"
    )


class TrendAnalysisResponse(BaseModel):
    """Complete trend analysis response."""
    
    request_id: str = Field(..., description="Unique request identifier")
    analysis_timestamp: datetime = Field(..., description="When analysis was performed")
    keyword_trends: Dict[str, KeywordTrendData] = Field(..., description="Individual keyword trends")
    seasonal_trends: Optional[List[SeasonalTrend]] = Field(
        default=None, 
        description="Seasonal trend data"
    )
    metrics: TrendMetrics = Field(..., description="Aggregate trend metrics")
    forecast: Optional[TrendForecast] = Field(
        default=None, 
        description="Trend forecast data"
    )
    industry_insights: List[str] = Field(..., description="Industry-specific trend insights")
