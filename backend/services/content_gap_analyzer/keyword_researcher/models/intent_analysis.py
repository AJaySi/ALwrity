"""
Intent Analysis Models

Pydantic models for search intent analysis and user journey mapping.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class IntentType(str, Enum):
    """Enumeration for search intent types."""
    INFORMATIONAL = "informational"
    TRANSACTIONAL = "transactional"
    NAVIGATIONAL = "navigational"
    COMMERCIAL = "commercial"
    LOCAL = "local"


class IntentSubtype(str, Enum):
    """Enumeration for intent subtypes."""
    # Informational subtypes
    EDUCATIONAL = "educational"
    DEFINITIONAL = "definition"
    TUTORIAL = "tutorial"
    COMPARISON = "comparison"
    HOW_TO = "how_to"
    NEWS = "news"
    
    # Transactional subtypes
    PURCHASE = "purchase"
    COST_INQUIRY = "cost_inquiry"
    PRICING = "pricing"
    BUY_NOW = "buy_now"
    QUOTE_REQUEST = "quote_request"
    
    # Navigational subtypes
    BRAND_SEARCH = "brand_search"
    WEBSITE_VISIT = "website_visit"
    LOGIN = "login"
    CONTACT = "contact"
    
    # Commercial subtypes
    REVIEW = "review"
    BEST_OF = "best_of"
    COMPARISON_SHOPPING = "comparison_shopping"
    ALTERNATIVE = "alternative"
    DEALS = "deals"


class UserJourneyStage(str, Enum):
    """Enumeration for user journey stages."""
    AWARENESS = "awareness"
    CONSIDERATION = "consideration"
    DECISION = "decision"
    PURCHASE = "purchase"
    RETENTION = "retention"


class IntentKeyword(BaseModel):
    """Model for keyword with intent classification."""
    
    keyword: str = Field(..., description="The keyword analyzed")
    intent_type: IntentType = Field(..., description="Primary intent type")
    intent_subtype: Optional[IntentSubtype] = Field(
        default=None, 
        description="Specific intent subtype"
    )
    confidence_score: float = Field(..., description="Confidence in classification (0-100)")
    user_journey_stage: UserJourneyStage = Field(..., description="User journey stage")
    content_suggestions: List[str] = Field(..., description="Recommended content types")
    conversion_potential: float = Field(..., description="Conversion potential score (0-100)")


class IntentPattern(BaseModel):
    """Model for intent patterns in keyword groups."""
    
    pattern_name: str = Field(..., description="Name of the pattern")
    intent_distribution: Dict[IntentType, float] = Field(..., description="Distribution of intents")
    dominant_intent: IntentType = Field(..., description="Most common intent")
    keyword_examples: List[str] = Field(..., description="Example keywords for this pattern")
    content_strategy: List[str] = Field(..., description="Content strategy recommendations")


class UserJourneyMapping(BaseModel):
    """Model for user journey mapping across keywords."""
    
    journey_stage: UserJourneyStage = Field(..., description="User journey stage")
    keywords: List[IntentKeyword] = Field(..., description="Keywords in this stage")
    content_priorities: List[str] = Field(..., description="Content creation priorities")
    kpi_focus: List[str] = Field(..., description="Key performance indicators to focus on")
    recommended_channels: List[str] = Field(..., description="Recommended marketing channels")


class ContentFormatRecommendation(BaseModel):
    """Model for content format recommendations based on intent."""
    
    intent_type: IntentType = Field(..., description="Target intent type")
    recommended_formats: List[str] = Field(..., description="Recommended content formats")
    optimal_length: str = Field(..., description="Optimal content length")
    key_elements: List[str] = Field(..., description="Key elements to include")
    call_to_action: str = Field(..., description="Recommended call to action")


class ConversionOptimization(BaseModel):
    """Model for conversion optimization suggestions."""
    
    keyword: str = Field(..., description="Target keyword")
    intent_type: IntentType = Field(..., description="Search intent")
    optimization_suggestions: List[str] = Field(..., description="Optimization recommendations")
    conversion_elements: List[str] = Field(..., description="Elements to improve conversion")
    expected_lift: float = Field(..., description="Expected conversion lift percentage")


class IntentAnalysisRequest(BaseModel):
    """Request model for intent analysis."""
    
    keywords: List[str] = Field(..., description="Keywords to analyze")
    industry: Optional[str] = Field(default=None, description="Industry context")
    include_journey_mapping: bool = Field(
        default=True, 
        description="Whether to include user journey mapping"
    )
    include_conversion_optimization: bool = Field(
        default=True, 
        description="Whether to include conversion optimization"
    )


class IntentAnalysisResponse(BaseModel):
    """Complete intent analysis response."""
    
    request_id: str = Field(..., description="Unique request identifier")
    analysis_timestamp: datetime = Field(..., description="When analysis was performed")
    keywords_by_intent: Dict[IntentType, List[IntentKeyword]] = Field(..., description="Keywords grouped by intent")
    intent_patterns: List[IntentPattern] = Field(..., description="Identified intent patterns")
    user_journey_mapping: Optional[List[UserJourneyMapping]] = Field(
        default=None, 
        description="User journey mapping"
    )
    content_format_recommendations: List[ContentFormatRecommendation] = Field(..., description="Content format recommendations")
    conversion_optimization: Optional[List[ConversionOptimization]] = Field(
        default=None, 
        description="Conversion optimization suggestions"
    )
    dominant_intent: IntentType = Field(..., description="Overall dominant intent")
    content_strategy_recommendations: List[str] = Field(..., description="Strategic content recommendations")
