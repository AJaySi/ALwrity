"""
AI Parameter Optimizer for Research Engine

Uses AI to analyze the research query and context to select optimal
parameters for Exa and Tavily APIs. This abstracts the complexity
from non-technical users.

Key Decisions:
- Provider selection (Exa vs Tavily vs Google)
- Search type (neural vs keyword)
- Category/topic selection
- Depth and result limits
- Domain filtering

Author: ALwrity Team
Version: 2.0
"""

import os
import re
from typing import Dict, Any, Optional, Tuple
from loguru import logger

from .research_context import (
    ResearchContext,
    ResearchGoal,
    ResearchDepth,
    ProviderPreference,
    ContentType,
)
from models.blog_models import ResearchConfig, ResearchProvider, ResearchMode


class ParameterOptimizer:
    """
    AI-driven parameter optimization for research providers.
    
    Analyzes the research context and selects optimal parameters
    for Exa, Tavily, or Google without requiring user expertise.
    """
    
    # Query patterns for intelligent routing
    TRENDING_PATTERNS = [
        r'\b(latest|recent|new|2024|2025|current|trending|news)\b',
        r'\b(update|announcement|launch|release)\b',
    ]
    
    TECHNICAL_PATTERNS = [
        r'\b(api|sdk|framework|library|implementation|architecture)\b',
        r'\b(code|programming|developer|technical|engineering)\b',
    ]
    
    COMPETITIVE_PATTERNS = [
        r'\b(competitor|alternative|vs|versus|compare|comparison)\b',
        r'\b(market|industry|landscape|players)\b',
    ]
    
    FACTUAL_PATTERNS = [
        r'\b(statistics|data|research|study|report|survey)\b',
        r'\b(percent|percentage|number|figure|metric)\b',
    ]
    
    # Exa category mapping based on query analysis
    EXA_CATEGORY_MAP = {
        'research': 'research paper',
        'news': 'news',
        'company': 'company',
        'personal': 'personal site',
        'github': 'github',
        'linkedin': 'linkedin profile',
        'finance': 'financial report',
    }
    
    # Tavily topic mapping
    TAVILY_TOPIC_MAP = {
        ResearchGoal.TRENDING: 'news',
        ResearchGoal.FACTUAL: 'general',
        ResearchGoal.COMPETITIVE: 'general',
        ResearchGoal.TECHNICAL: 'general',
        ResearchGoal.EDUCATIONAL: 'general',
        ResearchGoal.INSPIRATIONAL: 'general',
    }
    
    def __init__(self):
        """Initialize the optimizer."""
        self.exa_available = bool(os.getenv("EXA_API_KEY"))
        self.tavily_available = bool(os.getenv("TAVILY_API_KEY"))
        logger.info(f"ParameterOptimizer initialized: exa={self.exa_available}, tavily={self.tavily_available}")
    
    def optimize(self, context: ResearchContext) -> Tuple[ResearchProvider, ResearchConfig]:
        """
        Analyze research context and return optimized provider and config.
        
        Args:
            context: The research context from the calling tool
            
        Returns:
            Tuple of (selected_provider, optimized_config)
        """
        # If advanced mode, use raw parameters
        if context.advanced_mode:
            return self._build_advanced_config(context)
        
        # Analyze query to determine optimal approach
        query_analysis = self._analyze_query(context.query)
        
        # Select provider based on analysis and preferences
        provider = self._select_provider(context, query_analysis)
        
        # Build optimized config for selected provider
        config = self._build_config(context, provider, query_analysis)
        
        logger.info(f"Optimized research: provider={provider.value}, mode={config.mode.value}")
        
        return provider, config
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze the query to understand intent and optimal approach.
        
        Returns dict with:
        - is_trending: Query is about recent/current events
        - is_technical: Query is technical in nature
        - is_competitive: Query is about competition/comparison
        - is_factual: Query needs data/statistics
        - suggested_category: Exa category if applicable
        - suggested_topic: Tavily topic
        """
        query_lower = query.lower()
        
        analysis = {
            'is_trending': self._matches_patterns(query_lower, self.TRENDING_PATTERNS),
            'is_technical': self._matches_patterns(query_lower, self.TECHNICAL_PATTERNS),
            'is_competitive': self._matches_patterns(query_lower, self.COMPETITIVE_PATTERNS),
            'is_factual': self._matches_patterns(query_lower, self.FACTUAL_PATTERNS),
            'suggested_category': None,
            'suggested_topic': 'general',
            'suggested_search_type': 'auto',
        }
        
        # Determine Exa category
        if 'research' in query_lower or 'study' in query_lower or 'paper' in query_lower:
            analysis['suggested_category'] = 'research paper'
        elif 'github' in query_lower or 'repository' in query_lower:
            analysis['suggested_category'] = 'github'
        elif 'linkedin' in query_lower or 'professional' in query_lower:
            analysis['suggested_category'] = 'linkedin profile'
        elif analysis['is_trending']:
            analysis['suggested_category'] = 'news'
        elif 'company' in query_lower or 'startup' in query_lower:
            analysis['suggested_category'] = 'company'
        
        # Determine Tavily topic
        if analysis['is_trending']:
            analysis['suggested_topic'] = 'news'
        elif 'finance' in query_lower or 'stock' in query_lower or 'investment' in query_lower:
            analysis['suggested_topic'] = 'finance'
        else:
            analysis['suggested_topic'] = 'general'
        
        # Determine search type
        if analysis['is_technical'] or analysis['is_factual']:
            analysis['suggested_search_type'] = 'neural'  # Better for semantic understanding
        elif analysis['is_trending']:
            analysis['suggested_search_type'] = 'keyword'  # Better for current events
        
        return analysis
    
    def _matches_patterns(self, text: str, patterns: list) -> bool:
        """Check if text matches any of the patterns."""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _select_provider(self, context: ResearchContext, analysis: Dict[str, Any]) -> ResearchProvider:
        """
        Select the optimal provider based on context and query analysis.
        
        Priority: Exa → Tavily → Google for ALL modes (including basic).
        This provides better semantic search results for content creators.
        
        Exa's neural search excels at understanding context and meaning,
        which is valuable for all research types, not just technical queries.
        """
        preference = context.provider_preference
        
        # If user explicitly requested a provider, respect that
        if preference == ProviderPreference.EXA:
            if self.exa_available:
                return ResearchProvider.EXA
            logger.warning("Exa requested but not available, falling back")
            
        if preference == ProviderPreference.TAVILY:
            if self.tavily_available:
                return ResearchProvider.TAVILY
            logger.warning("Tavily requested but not available, falling back")
            
        if preference == ProviderPreference.GOOGLE:
            return ResearchProvider.GOOGLE
        
        # AUTO mode: Always prefer Exa → Tavily → Google
        # Exa provides superior semantic search for all content types
        if self.exa_available:
            logger.info(f"Selected Exa (primary provider): query analysis shows " +
                       f"technical={analysis.get('is_technical', False)}, " +
                       f"trending={analysis.get('is_trending', False)}")
            return ResearchProvider.EXA
        
        # Tavily as secondary option - good for real-time and news
        if self.tavily_available:
            logger.info(f"Selected Tavily (secondary): Exa unavailable, " +
                       f"trending={analysis.get('is_trending', False)}")
            return ResearchProvider.TAVILY
        
        # Google grounding as fallback
        logger.info("Selected Google (fallback): Exa and Tavily unavailable")
        return ResearchProvider.GOOGLE
    
    def _build_config(
        self,
        context: ResearchContext,
        provider: ResearchProvider,
        analysis: Dict[str, Any]
    ) -> ResearchConfig:
        """Build optimized ResearchConfig for the selected provider."""
        
        # Map ResearchDepth to ResearchMode
        mode_map = {
            ResearchDepth.QUICK: ResearchMode.BASIC,
            ResearchDepth.STANDARD: ResearchMode.BASIC,
            ResearchDepth.COMPREHENSIVE: ResearchMode.COMPREHENSIVE,
            ResearchDepth.EXPERT: ResearchMode.COMPREHENSIVE,
        }
        mode = mode_map.get(context.depth, ResearchMode.BASIC)
        
        # Base config
        config = ResearchConfig(
            mode=mode,
            provider=provider,
            max_sources=context.max_sources,
            include_statistics=context.personalization.include_statistics if context.personalization else True,
            include_expert_quotes=context.personalization.include_expert_quotes if context.personalization else True,
            include_competitors=analysis['is_competitive'],
            include_trends=analysis['is_trending'],
        )
        
        # Provider-specific optimizations
        if provider == ResearchProvider.EXA:
            config = self._optimize_exa_config(config, context, analysis)
        elif provider == ResearchProvider.TAVILY:
            config = self._optimize_tavily_config(config, context, analysis)
        
        # Apply domain filters
        if context.include_domains:
            if provider == ResearchProvider.EXA:
                config.exa_include_domains = context.include_domains
            elif provider == ResearchProvider.TAVILY:
                config.tavily_include_domains = context.include_domains[:300]  # Tavily limit
        
        if context.exclude_domains:
            if provider == ResearchProvider.EXA:
                config.exa_exclude_domains = context.exclude_domains
            elif provider == ResearchProvider.TAVILY:
                config.tavily_exclude_domains = context.exclude_domains[:150]  # Tavily limit
        
        return config
    
    def _optimize_exa_config(
        self,
        config: ResearchConfig,
        context: ResearchContext,
        analysis: Dict[str, Any]
    ) -> ResearchConfig:
        """Add Exa-specific optimizations."""
        
        # Set category based on analysis
        if analysis['suggested_category']:
            config.exa_category = analysis['suggested_category']
        
        # Set search type
        config.exa_search_type = analysis.get('suggested_search_type', 'auto')
        
        # For comprehensive research, use neural search
        if context.depth in [ResearchDepth.COMPREHENSIVE, ResearchDepth.EXPERT]:
            config.exa_search_type = 'neural'
        
        return config
    
    def _optimize_tavily_config(
        self,
        config: ResearchConfig,
        context: ResearchContext,
        analysis: Dict[str, Any]
    ) -> ResearchConfig:
        """Add Tavily-specific optimizations."""
        
        # Set topic based on analysis
        config.tavily_topic = analysis.get('suggested_topic', 'general')
        
        # Set search depth based on research depth
        if context.depth in [ResearchDepth.COMPREHENSIVE, ResearchDepth.EXPERT]:
            config.tavily_search_depth = 'advanced'  # 2 credits, but better results
            config.tavily_chunks_per_source = 3
        else:
            config.tavily_search_depth = 'basic'  # 1 credit
        
        # Set time range based on recency
        if context.recency:
            recency_map = {
                'day': 'd',
                'week': 'w', 
                'month': 'm',
                'year': 'y',
            }
            config.tavily_time_range = recency_map.get(context.recency, context.recency)
        elif analysis['is_trending']:
            config.tavily_time_range = 'w'  # Last week for trending topics
        
        # Include answer for comprehensive research
        if context.depth in [ResearchDepth.COMPREHENSIVE, ResearchDepth.EXPERT]:
            config.tavily_include_answer = 'advanced'
        
        # Include raw content for expert depth
        if context.depth == ResearchDepth.EXPERT:
            config.tavily_include_raw_content = 'markdown'
        
        return config
    
    def _build_advanced_config(self, context: ResearchContext) -> Tuple[ResearchProvider, ResearchConfig]:
        """
        Build config from raw advanced parameters.
        Used when advanced_mode=True and user wants full control.
        """
        # Determine provider from explicit parameters
        provider = ResearchProvider.GOOGLE
        
        if context.exa_category or context.exa_search_type:
            provider = ResearchProvider.EXA if self.exa_available else ResearchProvider.GOOGLE
        elif context.tavily_topic or context.tavily_search_depth:
            provider = ResearchProvider.TAVILY if self.tavily_available else ResearchProvider.GOOGLE
        
        # Check preference override
        if context.provider_preference == ProviderPreference.EXA and self.exa_available:
            provider = ResearchProvider.EXA
        elif context.provider_preference == ProviderPreference.TAVILY and self.tavily_available:
            provider = ResearchProvider.TAVILY
        elif context.provider_preference == ProviderPreference.GOOGLE:
            provider = ResearchProvider.GOOGLE
        
        # Map depth to mode
        mode_map = {
            ResearchDepth.QUICK: ResearchMode.BASIC,
            ResearchDepth.STANDARD: ResearchMode.BASIC,
            ResearchDepth.COMPREHENSIVE: ResearchMode.COMPREHENSIVE,
            ResearchDepth.EXPERT: ResearchMode.COMPREHENSIVE,
        }
        mode = mode_map.get(context.depth, ResearchMode.BASIC)
        
        # Build config with raw parameters
        config = ResearchConfig(
            mode=mode,
            provider=provider,
            max_sources=context.max_sources,
            # Exa
            exa_category=context.exa_category,
            exa_search_type=context.exa_search_type,
            exa_include_domains=context.include_domains,
            exa_exclude_domains=context.exclude_domains,
            # Tavily
            tavily_topic=context.tavily_topic,
            tavily_search_depth=context.tavily_search_depth,
            tavily_include_domains=context.include_domains[:300] if context.include_domains else [],
            tavily_exclude_domains=context.exclude_domains[:150] if context.exclude_domains else [],
            tavily_include_answer=context.tavily_include_answer,
            tavily_include_raw_content=context.tavily_include_raw_content,
            tavily_time_range=context.tavily_time_range,
            tavily_country=context.tavily_country,
        )
        
        logger.info(f"Advanced config: provider={provider.value}, mode={mode.value}")
        
        return provider, config

