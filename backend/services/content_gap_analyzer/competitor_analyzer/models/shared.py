"""
Shared Models for Competitor Analyzer Service

This module contains base models and shared entities used across
competitor analyzer services.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class AnalysisStatus(str, Enum):
    """Analysis status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PriorityLevel(str, Enum):
    """Priority level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ImpactLevel(str, Enum):
    """Impact level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class OpportunityLevel(str, Enum):
    """Opportunity level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BaseAnalysisRequest(BaseModel):
    """Base model for analysis requests."""
    
    industry: str = Field(..., description="Industry category for analysis")
    competitor_urls: List[str] = Field(..., description="List of competitor URLs to analyze")
    analysis_depth: str = Field(default="comprehensive", description="Depth of analysis")
    include_seo_analysis: bool = Field(default=True, description="Include SEO analysis")
    include_content_analysis: bool = Field(default=True, description="Include content analysis")
    include_market_analysis: bool = Field(default=True, description="Include market analysis")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BaseAnalysisResponse(BaseModel):
    """Base model for analysis responses."""
    
    request_id: str = Field(..., description="Unique request identifier")
    status: AnalysisStatus = Field(..., description="Analysis status")
    analysis_timestamp: datetime = Field(..., description="When analysis was performed")
    industry: str = Field(..., description="Industry analyzed")
    total_competitors: int = Field(..., description="Total number of competitors analyzed")
    processing_time_seconds: Optional[float] = Field(default=None, description="Time taken to process")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


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


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Health status")
    service: str = Field(..., description="Service name")
    timestamp: datetime = Field(..., description="Health check timestamp")
    tests_passed: Optional[int] = Field(default=None, description="Number of tests passed")
    total_tests: Optional[int] = Field(default=None, description="Total number of tests")
    error: Optional[str] = Field(default=None, description="Error message if unhealthy")
    
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


class AnalysisSummary(BaseModel):
    """Model for analysis summary statistics."""
    
    total_competitors: int = Field(..., description="Total competitors analyzed")
    successful_analyses: int = Field(..., description="Number of successful analyses")
    failed_analyses: int = Field(..., description="Number of failed analyses")
    avg_quality_score: float = Field(..., description="Average quality score across competitors")
    total_content_pieces: int = Field(..., description="Total content pieces analyzed")
    total_opportunities: int = Field(..., description="Total opportunities identified")
    avg_domain_authority: float = Field(..., description="Average domain authority")
    processing_time_seconds: float = Field(..., description="Total processing time")


class AIInsight(BaseModel):
    """Model for AI-generated insights."""
    
    insight_type: str = Field(..., description="Type of insight")
    insight: str = Field(..., description="The insight content")
    opportunity: str = Field(..., description="Opportunity identified")
    priority: PriorityLevel = Field(..., description="Priority level")
    estimated_impact: ImpactLevel = Field(..., description="Estimated impact")
    implementation_suggestion: str = Field(..., description="Implementation suggestion")
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in the insight")


class Recommendation(BaseModel):
    """Model for recommendations."""
    
    type: str = Field(..., description="Type of recommendation")
    recommendation: str = Field(..., description="The recommendation")
    priority: PriorityLevel = Field(..., description="Priority level")
    estimated_impact: ImpactLevel = Field(..., description="Estimated impact")
    implementation_time: str = Field(..., description="Estimated implementation time")
    resources_required: List[str] = Field(default_factory=list, description="Resources required")
    success_metrics: List[str] = Field(default_factory=list, description="Success metrics to track")


class ContentSuggestion(BaseModel):
    """Model for content suggestions."""
    
    content_type: str = Field(..., description="Type of content to create")
    title_suggestion: str = Field(..., description="Suggested title")
    description: str = Field(..., description="Content description")
    target_keywords: List[str] = Field(default_factory=list, description="Target keywords")
    estimated_word_count: int = Field(..., description="Estimated word count")
    priority: PriorityLevel = Field(..., description="Priority level")
    opportunity_level: OpportunityLevel = Field(..., description="Opportunity level")


class Metric(BaseModel):
    """Model for metrics and KPIs."""
    
    name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    unit: Optional[str] = Field(default=None, description="Unit of measurement")
    benchmark: Optional[float] = Field(default=None, description="Benchmark value")
    trend: Optional[str] = Field(default=None, description="Trend direction")
    last_updated: datetime = Field(..., description="When metric was last updated")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
