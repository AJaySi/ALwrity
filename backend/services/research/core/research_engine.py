"""
Research Engine - Core Orchestrator

The main entry point for AI research across all ALwrity tools.
This engine wraps existing providers (Exa, Tavily, Google) and provides
a unified interface for any content generation tool.

Usage:
    from services.research.core import ResearchEngine, ResearchContext, ContentType

    engine = ResearchEngine()
    result = await engine.research(ResearchContext(
        query="AI trends in healthcare 2025",
        content_type=ContentType.PODCAST,
        personalization=ResearchPersonalizationContext(
            industry="Healthcare",
            target_audience="Medical professionals"
        )
    ))

Author: ALwrity Team
Version: 2.0
"""

import os
import time
from typing import Dict, Any, Optional, Callable
from loguru import logger

from .research_context import (
    ResearchContext,
    ResearchResult,
    ResearchDepth,
    ContentType,
    ResearchPersonalizationContext,
)
from .parameter_optimizer import ParameterOptimizer

# Reuse existing blog writer models and services
from models.blog_models import (
    BlogResearchRequest,
    BlogResearchResponse,
    ResearchConfig,
    ResearchProvider,
    ResearchMode,
    PersonaInfo,
    ResearchSource,
)

# Research persona for personalization
from models.research_persona_models import ResearchPersona


class ResearchEngine:
    """
    AI Research Engine - Standalone module for content research.
    
    This engine:
    1. Accepts a ResearchContext from any tool
    2. Uses AI to optimize parameters for Exa/Tavily
    3. Integrates research persona for personalization
    4. Executes research using existing providers
    5. Returns standardized ResearchResult
    
    Can be imported by Blog Writer, Podcast Maker, YouTube Creator, etc.
    """
    
    def __init__(self, db_session=None):
        """Initialize the Research Engine."""
        self.optimizer = ParameterOptimizer()
        self._providers_initialized = False
        self._exa_provider = None
        self._tavily_provider = None
        self._google_provider = None
        self._db_session = db_session
        
        # Check provider availability
        self.exa_available = bool(os.getenv("EXA_API_KEY"))
        self.tavily_available = bool(os.getenv("TAVILY_API_KEY"))
        
        logger.info(f"ResearchEngine initialized: exa={self.exa_available}, tavily={self.tavily_available}")
    
    def _get_research_persona(self, user_id: str, generate_if_missing: bool = True) -> Optional[ResearchPersona]:
        """
        Fetch research persona for user, generating if missing.
        
        Phase 2: Since onboarding is mandatory and always completes before accessing
        any tool, we can safely generate research persona on first use. This ensures
        hyper-personalization without requiring "General" fallbacks.
        
        Args:
            user_id: User ID (Clerk string)
            generate_if_missing: If True, generate persona if not cached (default: True)
            
        Returns:
            ResearchPersona if successful, None only if user has no core persona
        """
        if not user_id:
            return None
        
        try:
            from services.research.research_persona_service import ResearchPersonaService
            
            db = self._db_session
            if not db:
                from services.database import get_db_session
                db = get_db_session()
            
            persona_service = ResearchPersonaService(db_session=db)
            
            if generate_if_missing:
                # Phase 2: Use get_or_generate() to create persona on first visit
                # This triggers LLM call if not cached, but onboarding guarantees
                # core persona exists, so generation will succeed
                logger.info(f"🔄 Getting/generating research persona for user {user_id}...")
                persona = persona_service.get_or_generate(user_id, force_refresh=False)
                
                if persona:
                    logger.info(f"✅ Research persona ready for user {user_id}: industry={persona.default_industry}")
                else:
                    logger.warning(f"⚠️ Could not get/generate research persona for user {user_id} - using core persona fallback")
            else:
                # Fast path: only return cached (for config endpoints)
                persona = persona_service.get_cached_only(user_id)
                if persona:
                    logger.debug(f"Research persona loaded from cache for user {user_id}")
            
            return persona
            
        except Exception as e:
            logger.warning(f"Failed to load research persona for user {user_id}: {e}")
            return None
    
    def _enrich_context_with_persona(
        self, 
        context: ResearchContext, 
        persona: ResearchPersona
    ) -> ResearchContext:
        """
        Enrich the research context with persona data.
        
        Only applies persona defaults if the context doesn't already have values.
        User-provided values always take precedence.
        """
        # Create personalization context if not exists
        if not context.personalization:
            context.personalization = ResearchPersonalizationContext()
        
        # Apply persona defaults only if not already set
        if not context.personalization.industry or context.personalization.industry == "General":
            if persona.default_industry:
                context.personalization.industry = persona.default_industry
                logger.debug(f"Applied persona industry: {persona.default_industry}")
        
        if not context.personalization.target_audience or context.personalization.target_audience == "General":
            if persona.default_target_audience:
                context.personalization.target_audience = persona.default_target_audience
                logger.debug(f"Applied persona target_audience: {persona.default_target_audience}")
        
        # Apply suggested Exa domains if not already set
        if not context.include_domains and persona.suggested_exa_domains:
            context.include_domains = persona.suggested_exa_domains[:6]  # Limit to 6 domains
            logger.debug(f"Applied persona domains: {context.include_domains}")
        
        # Apply suggested Exa category if not already set
        if not context.exa_category and persona.suggested_exa_category:
            context.exa_category = persona.suggested_exa_category
            logger.debug(f"Applied persona exa_category: {persona.suggested_exa_category}")
        
        return context
    
    async def research(
        self,
        context: ResearchContext,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> ResearchResult:
        """
        Execute research based on the given context.
        
        Args:
            context: Research context with query, goals, and personalization
            progress_callback: Optional callback for progress updates
            
        Returns:
            ResearchResult with sources, analysis, and content
        """
        start_time = time.time()
        
        try:
            # Progress update
            self._progress(progress_callback, "🔍 Analyzing research query...")
            
            # Enrich context with research persona (Phase 2: generate if missing)
            user_id = context.get_user_id()
            if user_id:
                self._progress(progress_callback, "👤 Loading personalized research profile...")
                persona = self._get_research_persona(user_id, generate_if_missing=True)
                if persona:
                    self._progress(progress_callback, "✨ Applying hyper-personalized settings...")
                    context = self._enrich_context_with_persona(context, persona)
                else:
                    logger.warning(f"No research persona available for user {user_id} - proceeding with provided context")
            
            # Optimize parameters based on enriched context
            provider, config = self.optimizer.optimize(context)
            
            self._progress(progress_callback, f"🤖 Selected {provider.value.upper()} for research")
            
            # Build the request using existing blog models
            request = self._build_request(context, config)
            user_id = context.get_user_id() or ""
            
            # Execute research using appropriate provider
            self._progress(progress_callback, f"🌐 Connecting to {provider.value} search...")
            
            if provider == ResearchProvider.EXA:
                response = await self._execute_exa_research(request, config, user_id, progress_callback)
            elif provider == ResearchProvider.TAVILY:
                response = await self._execute_tavily_research(request, config, user_id, progress_callback)
            else:
                response = await self._execute_google_research(request, config, user_id, progress_callback)
            
            # Transform response to ResearchResult
            self._progress(progress_callback, "📊 Processing results...")
            
            result = self._transform_response(response, provider, context)
            
            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"Research completed in {duration_ms:.0f}ms: {len(result.sources)} sources")
            
            self._progress(progress_callback, f"✅ Research complete: {len(result.sources)} sources found")
            
            return result
            
        except Exception as e:
            logger.error(f"Research failed: {e}")
            return ResearchResult(
                success=False,
                error_message=str(e),
                error_code="RESEARCH_FAILED",
                retry_suggested=True,
                original_query=context.query
            )
    
    def _progress(self, callback: Optional[Callable[[str], None]], message: str):
        """Send progress update if callback provided."""
        if callback:
            callback(message)
        logger.info(f"[Research] {message}")
    
    def _build_request(self, context: ResearchContext, config: ResearchConfig) -> BlogResearchRequest:
        """Build BlogResearchRequest from ResearchContext."""
        
        # Extract keywords from query
        keywords = context.keywords if context.keywords else [context.query]
        
        # Build persona info from personalization
        persona = None
        if context.personalization:
            persona = PersonaInfo(
                persona_id=context.personalization.persona_id,
                tone=context.personalization.tone,
                audience=context.personalization.target_audience,
                industry=context.personalization.industry,
            )
        
        return BlogResearchRequest(
            keywords=keywords,
            topic=context.query,
            industry=context.get_industry(),
            target_audience=context.get_audience(),
            tone=context.personalization.tone if context.personalization else None,
            word_count_target=context.personalization.word_count_target if context.personalization else 1500,
            persona=persona,
            research_mode=config.mode,
            config=config,
        )
    
    async def _execute_exa_research(
        self,
        request: BlogResearchRequest,
        config: ResearchConfig,
        user_id: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> BlogResearchResponse:
        """Execute research using Exa provider."""
        from services.blog_writer.research.exa_provider import ExaResearchProvider
        from services.blog_writer.research.research_strategies import get_strategy_for_mode
        
        self._progress(progress_callback, "🔍 Executing Exa neural search...")
        
        # Get strategy for building prompt
        strategy = get_strategy_for_mode(config.mode)
        topic = request.topic or ", ".join(request.keywords)
        industry = request.industry or "General"
        target_audience = request.target_audience or "General"
        
        research_prompt = strategy.build_research_prompt(topic, industry, target_audience, config)
        
        # Execute Exa search
        try:
            exa_provider = ExaResearchProvider()
            raw_result = await exa_provider.search(
                research_prompt, topic, industry, target_audience, config, user_id
            )
            
            # Track usage
            cost = raw_result.get('cost', {}).get('total', 0.005) if isinstance(raw_result.get('cost'), dict) else 0.005
            exa_provider.track_exa_usage(user_id, cost)
            
            self._progress(progress_callback, f"📝 Found {len(raw_result.get('sources', []))} sources")
            
            # Run common analysis
            return await self._run_analysis(request, raw_result, config, user_id, progress_callback)
            
        except RuntimeError as e:
            if "EXA_API_KEY not configured" in str(e):
                logger.warning("Exa not configured, falling back to Tavily")
                self._progress(progress_callback, "⚠️ Exa unavailable, trying Tavily...")
                config.provider = ResearchProvider.TAVILY
                return await self._execute_tavily_research(request, config, user_id, progress_callback)
            raise
    
    async def _execute_tavily_research(
        self,
        request: BlogResearchRequest,
        config: ResearchConfig,
        user_id: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> BlogResearchResponse:
        """Execute research using Tavily provider."""
        from services.blog_writer.research.tavily_provider import TavilyResearchProvider
        from services.blog_writer.research.research_strategies import get_strategy_for_mode
        
        self._progress(progress_callback, "🔍 Executing Tavily AI search...")
        
        # Get strategy for building prompt
        strategy = get_strategy_for_mode(config.mode)
        topic = request.topic or ", ".join(request.keywords)
        industry = request.industry or "General"
        target_audience = request.target_audience or "General"
        
        research_prompt = strategy.build_research_prompt(topic, industry, target_audience, config)
        
        # Execute Tavily search
        try:
            tavily_provider = TavilyResearchProvider()
            raw_result = await tavily_provider.search(
                research_prompt, topic, industry, target_audience, config, user_id
            )
            
            # Track usage
            cost = raw_result.get('cost', {}).get('total', 0.001) if isinstance(raw_result.get('cost'), dict) else 0.001
            search_depth = config.tavily_search_depth or "basic"
            tavily_provider.track_tavily_usage(user_id, cost, search_depth)
            
            self._progress(progress_callback, f"📝 Found {len(raw_result.get('sources', []))} sources")
            
            # Run common analysis
            return await self._run_analysis(request, raw_result, config, user_id, progress_callback)
            
        except RuntimeError as e:
            if "TAVILY_API_KEY not configured" in str(e):
                logger.warning("Tavily not configured, falling back to Google")
                self._progress(progress_callback, "⚠️ Tavily unavailable, using Google Search...")
                config.provider = ResearchProvider.GOOGLE
                return await self._execute_google_research(request, config, user_id, progress_callback)
            raise
    
    async def _execute_google_research(
        self,
        request: BlogResearchRequest,
        config: ResearchConfig,
        user_id: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> BlogResearchResponse:
        """Execute research using Google/Gemini grounding."""
        from services.blog_writer.research.google_provider import GoogleResearchProvider
        from services.blog_writer.research.research_strategies import get_strategy_for_mode
        
        self._progress(progress_callback, "🔍 Executing Google Search grounding...")
        
        # Get strategy for building prompt
        strategy = get_strategy_for_mode(config.mode)
        topic = request.topic or ", ".join(request.keywords)
        industry = request.industry or "General"
        target_audience = request.target_audience or "General"
        
        research_prompt = strategy.build_research_prompt(topic, industry, target_audience, config)
        
        # Execute Google search
        google_provider = GoogleResearchProvider()
        raw_result = await google_provider.search(
            research_prompt, topic, industry, target_audience, config, user_id
        )
        
        self._progress(progress_callback, "📝 Processing grounded results...")
        
        # Run common analysis
        return await self._run_analysis(request, raw_result, config, user_id, progress_callback, is_google=True)
    
    async def _run_analysis(
        self,
        request: BlogResearchRequest,
        raw_result: Dict[str, Any],
        config: ResearchConfig,
        user_id: str,
        progress_callback: Optional[Callable[[str], None]] = None,
        is_google: bool = False
    ) -> BlogResearchResponse:
        """Run common analysis on raw results."""
        from services.blog_writer.research.keyword_analyzer import KeywordAnalyzer
        from services.blog_writer.research.competitor_analyzer import CompetitorAnalyzer
        from services.blog_writer.research.content_angle_generator import ContentAngleGenerator
        from services.blog_writer.research.data_filter import ResearchDataFilter
        
        self._progress(progress_callback, "🔍 Analyzing keywords and content angles...")
        
        # Extract content for analysis
        if is_google:
            content = raw_result.get("content", "")
            sources = self._extract_sources_from_grounding(raw_result)
            search_queries = raw_result.get("search_queries", []) or []
            grounding_metadata = self._extract_grounding_metadata(raw_result)
        else:
            content = raw_result.get('content', '')
            sources = [ResearchSource(**s) if isinstance(s, dict) else s for s in raw_result.get('sources', [])]
            search_queries = raw_result.get('search_queries', [])
            grounding_metadata = None
        
        topic = request.topic or ", ".join(request.keywords)
        industry = request.industry or "General"
        
        # Run analyzers
        keyword_analyzer = KeywordAnalyzer()
        competitor_analyzer = CompetitorAnalyzer()
        content_angle_generator = ContentAngleGenerator()
        data_filter = ResearchDataFilter()
        
        keyword_analysis = keyword_analyzer.analyze(content, request.keywords, user_id=user_id)
        competitor_analysis = competitor_analyzer.analyze(content, user_id=user_id)
        suggested_angles = content_angle_generator.generate(content, topic, industry, user_id=user_id)
        
        # Build response
        response = BlogResearchResponse(
            success=True,
            sources=sources,
            keyword_analysis=keyword_analysis,
            competitor_analysis=competitor_analysis,
            suggested_angles=suggested_angles,
            search_widget="",
            search_queries=search_queries,
            grounding_metadata=grounding_metadata,
            original_keywords=request.keywords,
        )
        
        # Filter and clean research data
        self._progress(progress_callback, "✨ Filtering and optimizing results...")
        filtered_response = data_filter.filter_research_data(response)
        
        return filtered_response
    
    def _extract_sources_from_grounding(self, gemini_result: Dict[str, Any]) -> list:
        """Extract sources from Gemini grounding metadata."""
        from models.blog_models import ResearchSource
        
        sources = []
        if not gemini_result or not isinstance(gemini_result, dict):
            return sources
        
        raw_sources = gemini_result.get("sources", []) or []
        
        for src in raw_sources:
            source = ResearchSource(
                title=src.get("title", "Untitled"),
                url=src.get("url", ""),
                excerpt=src.get("content", "")[:500] if src.get("content") else f"Source from {src.get('title', 'web')}",
                credibility_score=float(src.get("credibility_score", 0.8)),
                published_at=str(src.get("publication_date", "2024-01-01")),
                index=src.get("index"),
                source_type=src.get("type", "web")
            )
            sources.append(source)
        
        return sources
    
    def _extract_grounding_metadata(self, gemini_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract grounding metadata from Gemini result."""
        if not gemini_result or not isinstance(gemini_result, dict):
            return None
        
        return gemini_result.get("grounding_metadata")
    
    def _transform_response(
        self,
        response: BlogResearchResponse,
        provider: ResearchProvider,
        context: ResearchContext
    ) -> ResearchResult:
        """Transform BlogResearchResponse to ResearchResult."""
        
        # Convert sources to dicts
        sources = []
        for s in response.sources:
            if hasattr(s, 'dict'):
                sources.append(s.dict())
            elif isinstance(s, dict):
                sources.append(s)
            else:
                sources.append({
                    'title': getattr(s, 'title', ''),
                    'url': getattr(s, 'url', ''),
                    'excerpt': getattr(s, 'excerpt', ''),
                })
        
        # Extract grounding metadata
        grounding = None
        if response.grounding_metadata:
            if hasattr(response.grounding_metadata, 'dict'):
                grounding = response.grounding_metadata.dict()
            else:
                grounding = response.grounding_metadata
        
        return ResearchResult(
            success=response.success,
            sources=sources,
            keyword_analysis=response.keyword_analysis,
            competitor_analysis=response.competitor_analysis,
            suggested_angles=response.suggested_angles,
            provider_used=provider.value,
            search_queries=response.search_queries,
            grounding_metadata=grounding,
            original_query=context.query,
            error_message=response.error_message,
            error_code=response.error_code if hasattr(response, 'error_code') else None,
            retry_suggested=response.retry_suggested if hasattr(response, 'retry_suggested') else False,
        )
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of available providers."""
        return {
            "exa": {
                "available": self.exa_available,
                "priority": 1,
                "description": "Neural search for semantic understanding"
            },
            "tavily": {
                "available": self.tavily_available,
                "priority": 2,
                "description": "AI-powered web search"
            },
            "google": {
                "available": True,  # Always available via Gemini
                "priority": 3,
                "description": "Google Search grounding"
            }
        }

