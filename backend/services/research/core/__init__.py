"""
Research Engine Core Module

This is the standalone AI Research Engine that can be imported by
Blog Writer, Podcast Maker, YouTube Creator, and other ALwrity tools.

Design Goals:
- Tool-agnostic: Any content tool can import and use this
- AI-driven parameter optimization: Users don't need to understand Exa/Tavily internals
- Provider priority: Exa → Tavily → Google (fallback)
- Personalization-aware: Accepts context from calling tools
- Advanced by default: Prioritizes quality over speed

Usage:
    from services.research.core import ResearchEngine, ResearchContext

    engine = ResearchEngine()
    result = await engine.research(ResearchContext(
        query="AI trends in healthcare 2025",
        content_type=ContentType.BLOG,
        persona_context={"industry": "Healthcare", "audience": "Medical professionals"}
    ))

Author: ALwrity Team
Version: 2.0
Last Updated: December 2025
"""

from .research_context import (
    ResearchContext,
    ResearchPersonalizationContext,
    ContentType,
    ResearchGoal,
    ResearchDepth,
    ProviderPreference,
)
from .parameter_optimizer import ParameterOptimizer
from .research_engine import ResearchEngine

__all__ = [
    # Context schemas
    "ResearchContext",
    "ResearchPersonalizationContext",
    "ContentType",
    "ResearchGoal",
    "ResearchDepth",
    "ProviderPreference",
    # Core classes
    "ParameterOptimizer",
    "ResearchEngine",
]
