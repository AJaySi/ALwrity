"""
Competitor Analyzer Models Package

This package contains Pydantic models for competitor analyzer services,
including competitor analysis, market analysis, content gaps, and SEO analysis.
"""

# Import all models from submodules
from .shared import (
    AnalysisStatus,
    PriorityLevel,
    ImpactLevel,
    OpportunityLevel,
    BaseAnalysisRequest,
    BaseAnalysisResponse,
    ValidationError,
    APIResponse,
    HealthCheckResponse,
    PaginationInfo,
    PaginatedResponse,
    AnalysisSummary,
    AIInsight,
    Recommendation,
    ContentSuggestion,
    Metric,
)

from .competitor_models import (
    CompetitorSize,
    CompetitorType,
    ContentType,
    PublishingFrequency,
    EngagementMetrics,
    SEOMetrics,
    ContentAnalysis,
    CompetitorProfile,
    CompetitorMetrics,
    CompetitorAnalysis,
    CompetitorComparison,
    CompetitorInsight,
    CompetitorTrend,
    CompetitorAlert,
)

from .market_analysis import (
    MarketPosition,
    MarketShareType,
    CompetitiveIntensity,
    MarketSegment,
    MarketShare,
    MarketPositioning,
    CompetitiveLandscape,
    MarketTrend,
    MarketOpportunity,
    MarketAnalysis,
    MarketForecast,
    MarketBenchmark,
)

from .content_gap_models import (
    GapType,
    ContentFormat,
    ContentGap,
    TopicGap,
    FormatGap,
    QualityGap,
    FrequencyGap,
    ContentGapAnalysis,
    ContentOpportunity,
    GapRecommendation,
    ContentGapTrend,
)

from .seo_analysis import (
    SEOGapType,
    KeywordDifficulty,
    SearchIntent,
    SEOMetric,
    KeywordGap,
    TechnicalSEOGap,
    BacklinkGap,
    SEOComparison,
    SEOGap,
    SEORecommendation,
    SEOAnalysis,
    SEOTrend,
    SEOAlert,
)

# Export all models for easy import
__all__ = [
    # Shared Models
    "AnalysisStatus",
    "PriorityLevel",
    "ImpactLevel",
    "OpportunityLevel",
    "BaseAnalysisRequest",
    "BaseAnalysisResponse",
    "ValidationError",
    "APIResponse",
    "HealthCheckResponse",
    "PaginationInfo",
    "PaginatedResponse",
    "AnalysisSummary",
    "AIInsight",
    "Recommendation",
    "ContentSuggestion",
    "Metric",
    
    # Competitor Models
    "CompetitorSize",
    "CompetitorType",
    "ContentType",
    "PublishingFrequency",
    "EngagementMetrics",
    "SEOMetrics",
    "ContentAnalysis",
    "CompetitorProfile",
    "CompetitorMetrics",
    "CompetitorAnalysis",
    "CompetitorComparison",
    "CompetitorInsight",
    "CompetitorTrend",
    "CompetitorAlert",
    
    # Market Analysis Models
    "MarketPosition",
    "MarketShareType",
    "CompetitiveIntensity",
    "MarketSegment",
    "MarketShare",
    "MarketPositioning",
    "CompetitiveLandscape",
    "MarketTrend",
    "MarketOpportunity",
    "MarketAnalysis",
    "MarketForecast",
    "MarketBenchmark",
    
    # Content Gap Models
    "GapType",
    "ContentFormat",
    "ContentGap",
    "TopicGap",
    "FormatGap",
    "QualityGap",
    "FrequencyGap",
    "ContentGapAnalysis",
    "ContentOpportunity",
    "GapRecommendation",
    "ContentGapTrend",
    
    # SEO Analysis Models
    "SEOGapType",
    "KeywordDifficulty",
    "SearchIntent",
    "SEOMetric",
    "KeywordGap",
    "TechnicalSEOGap",
    "BacklinkGap",
    "SEOComparison",
    "SEOGap",
    "SEORecommendation",
    "SEOAnalysis",
    "SEOTrend",
    "SEOAlert",
]

# Version information
__version__ = "1.0.0"
__description__ = "Pydantic models for competitor analyzer service"
