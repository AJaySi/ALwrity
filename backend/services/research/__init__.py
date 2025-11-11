"""
Research Services Module for ALwrity

This module provides research and grounding capabilities for content generation,
replacing mock research with real-time industry information.

Available Services:
- GoogleSearchService: Real-time industry research using Google Custom Search API
- ExaService: Competitor discovery and analysis using Exa API
- Source ranking and credibility assessment
- Content extraction and insight generation

Author: ALwrity Team
Version: 1.0
Last Updated: January 2025
"""

from .google_search_service import GoogleSearchService
from .exa_service import ExaService
from .tavily_service import TavilyService

__all__ = [
    "GoogleSearchService",
    "ExaService",
    "TavilyService"
]
