"""
Shared Models

Common models, enums, and base classes used across keyword researcher services.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class AnalysisStatus(str, Enum):
    """Enumeration for analysis status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PriorityLevel(str, Enum):
    """Enumeration for priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DifficultyLevel(str, Enum):
    """Enumeration for difficulty levels."""
    VERY_EASY = "very_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"


class SeasonalPattern(str, Enum):
    """Enumeration for seasonal patterns."""
    NONE = "none"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    HOLIDAY_BASED = "holiday_based"
    WEATHER_RELATED = "weather_related"


class BaseAnalysisRequest(BaseModel):
    """Base model for analysis requests."""
    
    industry: str = Field(..., description="Industry category")
    target_keywords: Optional[List[str]] = Field(
        default=None, 
        description="Target keywords for analysis"
    )
    analysis_depth: str = Field(
        default="standard", 
        description="Analysis depth (basic, standard, comprehensive)"
    )
    include_recommendations: bool = Field(
        default=True, 
        description="Whether to include recommendations"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BaseAnalysisResponse(BaseModel):
    """Base model for analysis responses."""
    
    request_id: str = Field(..., description="Unique request identifier")
    analysis_timestamp: datetime = Field(..., description="When analysis was performed")
    status: AnalysisStatus = Field(..., description="Analysis status")
    processing_time_seconds: Optional[float] = Field(
        default=None, 
        description="Time taken to process the request"
    )
    error_message: Optional[str] = Field(
        default=None, 
        description="Error message if analysis failed"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class KeywordMetric(BaseModel):
    """Model for keyword metrics."""
    
    keyword: str = Field(..., description="The keyword")
    search_volume: int = Field(..., description="Monthly search volume")
    difficulty: float = Field(..., description="Difficulty score (0-100)")
    competition: str = Field(..., description="Competition level")
    trend: str = Field(..., description="Trend direction")
    cpc: float = Field(..., description="Cost per click")
    seasonal_factor: float = Field(..., description="Seasonal factor")
    last_updated: datetime = Field(..., description="When data was last updated")


class AIInsight(BaseModel):
    """Model for AI-generated insights."""
    
    insight: str = Field(..., description="The insight text")
    category: str = Field(..., description="Category of the insight")
    confidence: float = Field(..., description="Confidence level (0-100)")
    priority: PriorityLevel = Field(..., description="Priority level")
    actionable: bool = Field(..., description="Whether the insight is actionable")
    estimated_impact: str = Field(..., description="Estimated impact description")
    implementation_effort: str = Field(..., description="Effort required to implement")


class ContentSuggestion(BaseModel):
    """Model for content suggestions."""
    
    content_type: str = Field(..., description="Type of content")
    title_idea: str = Field(..., description="Suggested title")
    description: str = Field(..., description="Content description")
    target_audience: str = Field(..., description="Target audience")
    key_points: List[str] = Field(..., description="Key points to cover")
    estimated_word_count: int = Field(..., description="Estimated word count")
    difficulty: DifficultyLevel = Field(..., description="Creation difficulty")
    time_to_create: str = Field(..., description="Estimated time to create")


class HealthCheckResponse(BaseModel):
    """Model for health check responses."""
    
    service_name: str = Field(..., description="Name of the service")
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    last_check: datetime = Field(..., description="When health check was performed")
    dependencies: Dict[str, str] = Field(..., description="Status of dependencies")
    metrics: Dict[str, Union[str, int, float]] = Field(..., description="Service metrics")


class AnalysisSummary(BaseModel):
    """Model for analysis summaries."""
    
    total_keywords: int = Field(..., description="Total keywords analyzed")
    successful_analyses: int = Field(..., description="Number of successful analyses")
    failed_analyses: int = Field(..., description="Number of failed analyses")
    average_processing_time: float = Field(..., description="Average processing time in seconds")
    insights_generated: int = Field(..., description="Number of insights generated")
    recommendations_made: int = Field(..., description="Number of recommendations made")
    overall_score: float = Field(..., description="Overall analysis score (0-100)")


class ValidationError(BaseModel):
    """Model for validation errors."""
    
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Error message")
    value: Any = Field(..., description="Value that failed validation")
    error_code: str = Field(..., description="Error code")


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(..., description="Response timestamp")
    request_id: str = Field(..., description="Request identifier")
    errors: Optional[List[ValidationError]] = Field(default=None, description="Validation errors")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PaginationInfo(BaseModel):
    """Model for pagination information."""
    
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there's a next page")
    has_previous: bool = Field(..., description="Whether there's a previous page")


class PaginatedResponse(BaseModel):
    """Model for paginated responses."""
    
    items: List[Dict[str, Any]] = Field(..., description="Items in the current page")
    pagination: PaginationInfo = Field(..., description="Pagination information")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
