"""
SEO Dashboard Services Package

This package provides comprehensive SEO analytics and dashboard functionality,
leveraging existing OAuth connections from onboarding step 5 and competitive
analysis from step 3.

Services:
- SEODashboardService: Main orchestration service for dashboard data
- AnalyticsAggregator: Combines and normalizes data from multiple platforms
- CompetitiveAnalyzer: Leverages onboarding research data for competitive insights
"""

from .dashboard_service import SEODashboardService
from .analytics_aggregator import AnalyticsAggregator
from .competitive_analyzer import CompetitiveAnalyzer

__all__ = [
    "SEODashboardService",
    "AnalyticsAggregator", 
    "CompetitiveAnalyzer",
]