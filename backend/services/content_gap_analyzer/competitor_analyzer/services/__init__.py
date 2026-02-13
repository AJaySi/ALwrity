"""
Services Package for Competitor Analyzer Service

This package contains specialized services for different aspects of competitor analysis.
"""

# Import all specialized services
from .competitor_analysis_service import CompetitorAnalysisService
from .market_positioning_service import MarketPositioningService
from .content_gap_analysis_service import ContentGapAnalysisService
from .seo_analysis_service import SEOAnalysisService

# Export all services for easy import
__all__ = [
    "CompetitorAnalysisService",
    "MarketPositioningService", 
    "ContentGapAnalysisService",
    "SEOAnalysisService",
]

# Version information
__version__ = "1.0.0"
__description__ = "Specialized services for competitor analyzer"
