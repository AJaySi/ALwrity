"""
Google Trends Data Models

Pydantic models for Google Trends API responses.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class GoogleTrendsData(BaseModel):
    """Structured Google Trends data."""
    interest_over_time: List[Dict[str, Any]] = Field(default_factory=list, description="Time series interest data")
    interest_by_region: List[Dict[str, Any]] = Field(default_factory=list, description="Geographic interest data")
    related_topics: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Related topics: {top: [...], rising: [...]}"
    )
    related_queries: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Related queries: {top: [...], rising: [...]}"
    )
    trending_searches: Optional[List[str]] = Field(None, description="Current trending searches")
    timeframe: str = Field(..., description="Timeframe used (e.g., 'today 12-m')")
    geo: str = Field(..., description="Geographic region (e.g., 'US', 'GB')")
    keywords: List[str] = Field(..., description="Keywords analyzed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When data was fetched")


class TrendsConfig(BaseModel):
    """Google Trends configuration with AI-driven justifications."""
    enabled: bool = Field(True, description="Whether trends analysis is enabled")
    keywords: List[str] = Field(..., description="AI-optimized keywords for trends analysis")
    keywords_justification: str = Field(..., description="Why these keywords were chosen")
    timeframe: str = Field(default="today 12-m", description="Timeframe: 'today 1-y', 'today 12-m', 'all', etc.")
    timeframe_justification: str = Field(..., description="Why this timeframe was chosen")
    geo: str = Field(default="US", description="Country code (e.g., 'US', 'GB', 'IN')")
    geo_justification: str = Field(..., description="Why this geographic region was chosen")
    expected_insights: List[str] = Field(
        default_factory=list,
        description="What insights trends will uncover for content generation"
    )


class TrendsAnalysisResponse(BaseModel):
    """Response from trends analysis endpoint."""
    success: bool
    data: Optional[GoogleTrendsData] = None
    error_message: Optional[str] = None
    cached: bool = Field(False, description="Whether data was served from cache")
