"""
Content Recommendation Models

Pydantic models for content recommendations and topic clustering.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ContentType(str, Enum):
    """Enumeration for content types."""
    BLOG_POST = "blog_post"
    ARTICLE = "article"
    GUIDE = "guide"
    TUTORIAL = "tutorial"
    LANDING_PAGE = "landing_page"
    PRODUCT_PAGE = "product_page"
    CATEGORY_PAGE = "category_page"
    FAQ = "faq"
    CASE_STUDY = "case_study"
    INFOGRAPHIC = "infographic"
    VIDEO = "video"
    PODCAST = "podcast"
    WEBINAR = "webinar"
    WHITEPAPER = "whitepaper"
    EBOOK = "ebook"


class ContentFormat(str, Enum):
    """Enumeration for content formats."""
    LONG_FORM = "long_form"
    SHORT_FORM = "short_form"
    LISTICLE = "listicle"
    HOW_TO = "how_to"
    COMPARISON = "comparison"
    REVIEW = "review"
    INTERVIEW = "interview"
    ROUNDUP = "roundup"
    NEWS = "news"
    OPINION = "opinion"


class TopicCluster(BaseModel):
    """Model for topic clustering."""
    
    cluster_name: str = Field(..., description="Name of the topic cluster")
    pillar_keyword: str = Field(..., description="Pillar/primary keyword for the cluster")
    cluster_keywords: List[str] = Field(..., description="Keywords in this cluster")
    content_pieces: List[str] = Field(..., description="Recommended content pieces")
    internal_linking_strategy: str = Field(..., description="Internal linking strategy")
    cluster_authority_score: float = Field(..., description="Authority score for this cluster")
    estimated_traffic_potential: str = Field(..., description="Estimated traffic potential")


class ContentRecommendation(BaseModel):
    """Model for individual content recommendations."""
    
    keyword: str = Field(..., description="Target keyword")
    content_type: ContentType = Field(..., description="Recommended content type")
    content_format: ContentFormat = Field(..., description="Recommended content format")
    title_suggestion: str = Field(..., description="Suggested title")
    content_outline: List[str] = Field(..., description="Content outline/key sections")
    target_word_count: int = Field(..., description="Target word count")
    priority_score: float = Field(..., description="Priority score (0-100)")
    estimated_traffic: str = Field(..., description="Estimated traffic potential")
    conversion_potential: float = Field(..., description="Conversion potential (0-100)")
    creation_difficulty: str = Field(..., description="Difficulty to create (easy, medium, hard)")
    time_to_create: str = Field(..., description="Estimated time to create")
    content_angle: str = Field(..., description="Unique angle for the content")
    call_to_action: str = Field(..., description="Recommended call to action")


class ContentGap(BaseModel):
    """Model for content gap analysis."""
    
    gap_type: str = Field(..., description="Type of content gap")
    missing_keywords: List[str] = Field(..., description="Keywords with missing content")
    competitor_coverage: Dict[str, List[str]] = Field(..., description="What competitors cover")
    opportunity_size: str = Field(..., description="Size of the opportunity")
    recommended_content: List[ContentRecommendation] = Field(..., description="Recommended content to fill gaps")


class ContentSeries(BaseModel):
    """Model for content series recommendations."""
    
    series_name: str = Field(..., description="Name of the content series")
    series_description: str = Field(..., description="Description of the series")
    total_pieces: int = Field(..., description="Total number of content pieces")
    content_pieces: List[ContentRecommendation] = Field(..., description="Individual content pieces")
    publication_schedule: str = Field(..., description="Recommended publication schedule")
    cross_promotion_strategy: str = Field(..., description="How to cross-promote the series")
    expected_results: str = Field(..., description="Expected results from the series")


class ContentPerformancePrediction(BaseModel):
    """Model for content performance predictions."""
    
    keyword: str = Field(..., description="Target keyword")
    predicted_ranking: int = Field(..., description="Predicted search ranking")
    predicted_traffic: int = Field(..., description="Predicted monthly traffic")
    predicted_conversions: float = Field(..., description="Predicted monthly conversions")
    confidence_level: float = Field(..., description="Confidence in predictions (0-100)")
    time_to_rank: str = Field(..., description="Estimated time to achieve ranking")
    success_factors: List[str] = Field(..., description="Factors for success")
    potential_risks: List[str] = Field(..., description="Potential risks to success")


class ContentRecommendationRequest(BaseModel):
    """Request model for content recommendations."""
    
    ai_insights: Dict[str, Any] = Field(..., description="AI analysis insights")
    target_keywords: Optional[List[str]] = Field(
        default=None, 
        description="Specific keywords to target"
    )
    content_types: Optional[List[ContentType]] = Field(
        default=None, 
        description="Preferred content types"
    )
    max_recommendations: int = Field(
        default=10, 
        description="Maximum number of recommendations"
    )
    include_topic_clusters: bool = Field(
        default=True, 
        description="Include topic clustering analysis"
    )
    include_performance_prediction: bool = Field(
        default=True, 
        description="Include performance predictions"
    )


class ContentRecommendationResponse(BaseModel):
    """Complete content recommendation response."""
    
    request_id: str = Field(..., description="Unique request identifier")
    analysis_timestamp: datetime = Field(..., description="When analysis was performed")
    recommendations: List[ContentRecommendation] = Field(..., description="Content recommendations")
    topic_clusters: Optional[List[TopicCluster]] = Field(
        default=None, 
        description="Topic cluster analysis"
    )
    content_gaps: Optional[List[ContentGap]] = Field(
        default=None, 
        description="Content gap analysis"
    )
    content_series: Optional[List[ContentSeries]] = Field(
        default=None, 
        description="Content series recommendations"
    )
    performance_predictions: Optional[List[ContentPerformancePrediction]] = Field(
        default=None, 
        description="Performance predictions"
    )
    implementation_roadmap: List[str] = Field(..., description="Implementation roadmap")
    success_metrics: List[str] = Field(..., description="Recommended success metrics to track")
