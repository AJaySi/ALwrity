"""
Keyword Analysis Models

Pydantic models for keyword analysis requests and responses.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class KeywordAnalysisRequest(BaseModel):
    """Request model for keyword analysis."""
    
    industry: str = Field(..., description="Industry category for analysis")
    url: str = Field(..., description="Target website URL")
    target_keywords: Optional[List[str]] = Field(
        default=None, 
        description="Optional list of target keywords to focus on"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class KeywordTrend(BaseModel):
    """Model for individual keyword trend data."""
    
    search_volume: int = Field(..., description="Estimated monthly search volume")
    difficulty: float = Field(..., description="Keyword difficulty score (0-100)")
    trend: str = Field(..., description="Trend direction (rising, stable, declining)")
    competition: str = Field(..., description="Competition level (low, medium, high)")
    intent: str = Field(..., description="Primary search intent")
    cpc: float = Field(..., description="Cost per click estimate")
    seasonal_factor: float = Field(..., description="Seasonal trend multiplier")


class TrendAnalysisSummary(BaseModel):
    """Summary statistics for trend analysis."""
    
    total_keywords: int = Field(..., description="Total keywords analyzed")
    high_volume_keywords: int = Field(..., description="Count of high-volume keywords")
    low_competition_keywords: int = Field(..., description="Count of low-competition keywords")
    trending_keywords: int = Field(..., description="Count of trending keywords")
    opportunity_score: float = Field(..., description="Overall opportunity score (0-100)")


class TrendRecommendation(BaseModel):
    """Individual trend-based recommendation."""
    
    keyword: str = Field(..., description="Target keyword")
    recommendation: str = Field(..., description="Specific recommendation")
    priority: str = Field(..., description="Priority level (high, medium, low)")
    estimated_impact: str = Field(..., description="Expected impact description")


class TrendAnalysisResponse(BaseModel):
    """Complete trend analysis response."""
    
    trends: Dict[str, KeywordTrend] = Field(..., description="Keyword trend data")
    summary: TrendAnalysisSummary = Field(..., description="Trend analysis summary")
    recommendations: List[TrendRecommendation] = Field(..., description="Trend-based recommendations")


class KeywordAnalysisResponse(BaseModel):
    """Complete keyword analysis response."""
    
    trend_analysis: TrendAnalysisResponse = Field(..., description="Trend analysis results")
    intent_analysis: Dict[str, Any] = Field(..., description="Search intent analysis results")
    opportunities: List[Dict[str, Any]] = Field(..., description="Keyword opportunities")
    insights: List[str] = Field(..., description="Strategic insights")
    analysis_timestamp: str = Field(..., description="When analysis was performed")
    industry: str = Field(..., description="Industry analyzed")
    target_url: str = Field(..., description="Target URL analyzed")
