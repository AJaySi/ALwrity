"""
Keyword Researcher Models

This package contains all Pydantic models for the keyword researcher service.
Models are organized by functional domain for better maintainability.
"""

# Import all models from submodules
from .keyword_analysis import (
    KeywordAnalysisRequest,
    KeywordAnalysisResponse,
    KeywordTrend,
    TrendAnalysisSummary,
    TrendRecommendation,
    TrendAnalysisResponse,
)

from .trend_analysis import (
    TrendDirection,
    CompetitionLevel,
    SearchIntent,
    KeywordTrendData,
    SeasonalTrend,
    TrendMetrics,
    TrendForecast,
    TrendAnalysisRequest as TrendAnalysisRequestModel,
    TrendAnalysisResponse as TrendAnalysisResponseModel,
)

from .intent_analysis import (
    IntentType,
    IntentSubtype,
    UserJourneyStage,
    IntentKeyword,
    IntentPattern,
    UserJourneyMapping,
    ContentFormatRecommendation,
    ConversionOptimization,
    IntentAnalysisRequest,
    IntentAnalysisResponse,
)

from .opportunity import (
    OpportunityType,
    PriorityLevel,
    CompetitionLevel as OpportunityCompetitionLevel,
    OpportunityScore,
    ContentOpportunity,
    CompetitiveAdvantage,
    LongTailOpportunity,
    ContentGapOpportunity,
    OpportunityAnalysisRequest,
    OpportunityAnalysisResponse,
)

from .content_recommendation import (
    ContentType,
    ContentFormat,
    TopicCluster,
    ContentRecommendation,
    ContentGap,
    ContentSeries,
    ContentPerformancePrediction,
    ContentRecommendationRequest,
    ContentRecommendationResponse,
)

from .shared import (
    AnalysisStatus,
    PriorityLevel as SharedPriorityLevel,
    DifficultyLevel,
    SeasonalPattern,
    BaseAnalysisRequest,
    BaseAnalysisResponse,
    KeywordMetric,
    AIInsight,
    ContentSuggestion,
    HealthCheckResponse,
    AnalysisSummary,
    ValidationError,
    APIResponse,
    PaginationInfo,
    PaginatedResponse,
)

# Export all models for easy import
__all__ = [
    # Keyword Analysis Models
    "KeywordAnalysisRequest",
    "KeywordAnalysisResponse",
    "KeywordTrend",
    "TrendAnalysisSummary",
    "TrendRecommendation",
    "TrendAnalysisResponse",
    
    # Trend Analysis Models
    "TrendDirection",
    "CompetitionLevel",
    "SearchIntent",
    "KeywordTrendData",
    "SeasonalTrend",
    "TrendMetrics",
    "TrendForecast",
    "TrendAnalysisRequestModel",
    "TrendAnalysisResponseModel",
    
    # Intent Analysis Models
    "IntentType",
    "IntentSubtype",
    "UserJourneyStage",
    "IntentKeyword",
    "IntentPattern",
    "UserJourneyMapping",
    "ContentFormatRecommendation",
    "ConversionOptimization",
    "IntentAnalysisRequest",
    "IntentAnalysisResponse",
    
    # Opportunity Models
    "OpportunityType",
    "PriorityLevel",
    "OpportunityCompetitionLevel",
    "OpportunityScore",
    "ContentOpportunity",
    "CompetitiveAdvantage",
    "LongTailOpportunity",
    "ContentGapOpportunity",
    "OpportunityAnalysisRequest",
    "OpportunityAnalysisResponse",
    
    # Content Recommendation Models
    "ContentType",
    "ContentFormat",
    "TopicCluster",
    "ContentRecommendation",
    "ContentGap",
    "ContentSeries",
    "ContentPerformancePrediction",
    "ContentRecommendationRequest",
    "ContentRecommendationResponse",
    
    # Shared Models
    "AnalysisStatus",
    "SharedPriorityLevel",
    "DifficultyLevel",
    "SeasonalPattern",
    "BaseAnalysisRequest",
    "BaseAnalysisResponse",
    "KeywordMetric",
    "AIInsight",
    "ContentSuggestion",
    "HealthCheckResponse",
    "AnalysisSummary",
    "ValidationError",
    "APIResponse",
    "PaginationInfo",
    "PaginatedResponse",
]

# Version information
__version__ = "1.0.0"
__description__ = "Pydantic models for keyword researcher service"
