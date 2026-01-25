"""
API Package for Competitor Analyzer Service

This package contains the unified API facade for competitor analyzer services.
"""

# Import the main API facade
from .competitor_analyzer_api import CompetitorAnalyzerAPI, get_competitor_analyzer_api, shutdown_competitor_analyzer_api

# Export API components
__all__ = [
    "CompetitorAnalyzerAPI",
    "get_competitor_analyzer_api",
    "shutdown_competitor_analyzer_api",
]

# Version information
__version__ = "2.0.0"
__description__ = "Unified API facade for competitor analyzer services"
