"""
Research Service - Core research functionality for AI Blog Writer.

Handles Google Search grounding, caching, and research orchestration.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from models.blog_models import (
    BlogResearchRequest,
    BlogResearchResponse,
    ResearchSource,
    GroundingMetadata,
    GroundingChunk,
    GroundingSupport,
    Citation,
)
from services.blog_writer.logger_config import blog_writer_logger, log_function_call
from fastapi import HTTPException

from .keyword_analyzer import KeywordAnalyzer
from .competitor_analyzer import CompetitorAnalyzer
from .content_angle_generator import ContentAngleGenerator
from .data_filter import ResearchDataFilter


class ResearchService:
    """Service for conducting comprehensive research using Google Search grounding."""
    
    def __init__(self):
        self.keyword_analyzer = KeywordAnalyzer()
        self.competitor_analyzer = CompetitorAnalyzer()
        self.content_angle_generator = ContentAngleGenerator()
        self.data_filter = ResearchDataFilter()
    
    @log_function_call("research_operation")
    async def research(self, request: BlogResearchRequest, user_id: str) -> BlogResearchResponse:
        """
        Stage 1: Research & Strategy (AI Orchestration)
        Uses ONLY Gemini's native Google Search grounding - ONE API call for everything.
        Follows LinkedIn service pattern for efficiency and cost optimization.
        Includes intelligent caching for exact keyword matches.
        """
        try:
            from services.llm_providers.gemini_grounded_provider import GeminiGroundedProvider
            from services.cache.research_cache import research_cache
            
            topic = request.topic or ", ".join(request.keywords)
            industry = request.industry or (request.persona.industry if request.persona and request.persona.industry else "General")
            target_audience = getattr(request.persona, 'target_audience', 'General') if request.persona else 'General'
            
            # Log research parameters
            blog_writer_logger.log_operation_start(
                "research",
                topic=topic,
                industry=industry,
                target_audience=target_audience,
                keywords=request.keywords,
                keyword_count=len(request.keywords)
            )
            
            # Check cache first for exact keyword match
            cached_result = research_cache.get_cached_result(
                keywords=request.keywords,
                industry=industry,
                target_audience=target_audience
            )
            
            if cached_result:
                logger.info(f"Returning cached research result for keywords: {request.keywords}")
                blog_writer_logger.log_operation_end("research", 0, success=True, cache_hit=True)
                return BlogResearchResponse(**cached_result)
            
            # User ID validation (validation logic is now in Google Grounding provider)
            if not user_id:
                raise ValueError("user_id is required for research operation. Please provide Clerk user ID.")
            
            # Cache miss - proceed with API call
            logger.info(f"Cache miss - making API call for keywords: {request.keywords}")
            blog_writer_logger.log_operation_start("gemini_api_call", api_name="gemini_grounded", operation="research")
            gemini = GeminiGroundedProvider()

            # Single comprehensive research prompt - Gemini handles Google Search automatically
            research_prompt = f"""
            Research the topic "{topic}" in the {industry} industry for {target_audience} audience. Provide a comprehensive analysis including:

            1. Current trends and insights (2024-2025)
            2. Key statistics and data points with sources
            3. Industry expert opinions and quotes
            4. Recent developments and news
            5. Market analysis and forecasts
            6. Best practices and case studies
            7. Keyword analysis: primary, secondary, and long-tail opportunities
            8. Competitor analysis: top players and content gaps
            9. Content angle suggestions: 5 compelling angles for blog posts

            Focus on factual, up-to-date information from credible sources.
            Include specific data points, percentages, and recent developments.
            Structure your response with clear sections for each analysis area.
            """
            
            # Single Gemini call with native Google Search grounding - no fallbacks
            # Validation is handled inside generate_grounded_content when validate_subsequent_operations=True
            import time
            api_start_time = time.time()
            gemini_result = await gemini.generate_grounded_content(
                prompt=research_prompt,
                content_type="research",
                max_tokens=2000,
                user_id=user_id,
                validate_subsequent_operations=True  # Validates Google Grounding + 3 LLM calls
            )
            api_duration_ms = (time.time() - api_start_time) * 1000
            
            # Log API call performance
            blog_writer_logger.log_api_call(
                "gemini_grounded",
                "generate_grounded_content",
                api_duration_ms,
                token_usage=gemini_result.get("token_usage", {}),
                content_length=len(gemini_result.get("content", ""))
            )
            
            # Extract sources from grounding metadata
            sources = self._extract_sources_from_grounding(gemini_result)
            
            # Extract grounding metadata for detailed UI display
            grounding_metadata = self._extract_grounding_metadata(gemini_result)
            
            # Extract search widget and queries for UI display
            search_widget = gemini_result.get("search_widget", "") or ""
            search_queries = gemini_result.get("search_queries", []) or []
            
            # Parse the comprehensive response for different analysis components
            content = gemini_result.get("content", "")
            keyword_analysis = self.keyword_analyzer.analyze(content, request.keywords, user_id=user_id)
            competitor_analysis = self.competitor_analyzer.analyze(content, user_id=user_id)
            suggested_angles = self.content_angle_generator.generate(content, topic, industry, user_id=user_id)
            
            logger.info(f"Research completed successfully with {len(sources)} sources and {len(search_queries)} search queries")
            
            # Log analysis results
            blog_writer_logger.log_performance(
                "research_analysis",
                len(content),
                "characters",
                sources_count=len(sources),
                search_queries_count=len(search_queries),
                keyword_analysis_keys=len(keyword_analysis),
                suggested_angles_count=len(suggested_angles)
            )

            # Create the response
            response = BlogResearchResponse(
                success=True,
                sources=sources,
                keyword_analysis=keyword_analysis,
                competitor_analysis=competitor_analysis,
                suggested_angles=suggested_angles,
                # Add search widget and queries for UI display
                search_widget=search_widget if 'search_widget' in locals() else "",
                search_queries=search_queries if 'search_queries' in locals() else [],
                # Add grounding metadata for detailed UI display
                grounding_metadata=grounding_metadata,
            )
            
            # Filter and clean research data for optimal AI processing
            filtered_response = self.data_filter.filter_research_data(response)
            logger.info("Research data filtering completed successfully")
            
            # Cache the successful result for future exact keyword matches (both caches)
            persistent_research_cache.cache_result(
                keywords=request.keywords,
                industry=industry,
                target_audience=target_audience,
                result=filtered_response.dict()
            )
            
            # Also cache in memory for faster access
            research_cache.cache_result(
                keywords=request.keywords,
                industry=industry,
                target_audience=target_audience,
                result=filtered_response.dict()
            )
            
            return filtered_response
            
        except HTTPException:
            # Re-raise HTTPException (subscription errors) - let task manager handle it
            raise
        except Exception as e:
            error_message = str(e)
            logger.error(f"Research failed: {error_message}")
            
            # Log error with full context
            blog_writer_logger.log_error(
                e,
                "research",
                context={
                    "topic": topic,
                    "keywords": request.keywords,
                    "industry": industry,
                    "target_audience": target_audience
                }
            )
            
            # Import custom exceptions for better error handling
            from services.blog_writer.exceptions import (
                ResearchFailedException, 
                APIRateLimitException, 
                APITimeoutException,
                ValidationException
            )
            
            # Determine if this is a retryable error
            retry_suggested = True
            user_message = "Research failed. Please try again with different keywords or check your internet connection."
            
            if isinstance(e, APIRateLimitException):
                retry_suggested = True
                user_message = f"Rate limit exceeded. Please wait {e.context.get('retry_after', 60)} seconds before trying again."
            elif isinstance(e, APITimeoutException):
                retry_suggested = True
                user_message = "Research request timed out. Please try again with a shorter query or check your internet connection."
            elif isinstance(e, ValidationException):
                retry_suggested = False
                user_message = "Invalid research request. Please check your input parameters and try again."
            elif "401" in error_message or "403" in error_message:
                retry_suggested = False
                user_message = "Authentication failed. Please check your API credentials."
            elif "400" in error_message:
                retry_suggested = False
                user_message = "Invalid request. Please check your input parameters."
            
            # Return a graceful failure response with enhanced error information
            return BlogResearchResponse(
                success=False,
                sources=[],
                keyword_analysis={},
                competitor_analysis={},
                suggested_angles=[],
                search_widget="",
                search_queries=[],
                error_message=user_message,
                retry_suggested=retry_suggested,
                error_code=getattr(e, 'error_code', 'RESEARCH_FAILED'),
                actionable_steps=getattr(e, 'actionable_steps', [
                    "Try with different keywords",
                    "Check your internet connection",
                    "Wait a few minutes and try again",
                    "Contact support if the issue persists"
                ])
            )
    
    @log_function_call("research_with_progress")
    async def research_with_progress(self, request: BlogResearchRequest, task_id: str, user_id: str) -> BlogResearchResponse:
        """
        Research method with progress updates for real-time feedback.
        """
        try:
            from services.llm_providers.gemini_grounded_provider import GeminiGroundedProvider
            from services.cache.research_cache import research_cache
            from services.cache.persistent_research_cache import persistent_research_cache
            from api.blog_writer.task_manager import task_manager
            
            topic = request.topic or ", ".join(request.keywords)
            industry = request.industry or (request.persona.industry if request.persona and request.persona.industry else "General")
            target_audience = getattr(request.persona, 'target_audience', 'General') if request.persona else 'General'
            
            # Check cache first for exact keyword match (try both caches)
            await task_manager.update_progress(task_id, "🔍 Checking cache for existing research...")
            
            # Try persistent cache first (survives restarts)
            cached_result = persistent_research_cache.get_cached_result(
                keywords=request.keywords,
                industry=industry,
                target_audience=target_audience
            )
            
            # Fallback to in-memory cache
            if not cached_result:
                cached_result = research_cache.get_cached_result(
                    keywords=request.keywords,
                    industry=industry,
                    target_audience=target_audience
                )
            
            if cached_result:
                await task_manager.update_progress(task_id, "✅ Found cached research results! Returning instantly...")
                logger.info(f"Returning cached research result for keywords: {request.keywords}")
                return BlogResearchResponse(**cached_result)
            
            # User ID validation (validation logic is now in Google Grounding provider)
            if not user_id:
                await task_manager.update_progress(task_id, "❌ Error: User ID is required for research operation")
                raise ValueError("user_id is required for research operation. Please provide Clerk user ID.")
            
            # Cache miss - proceed with API call
            await task_manager.update_progress(task_id, "🌐 Cache miss - connecting to Google Search grounding...")
            logger.info(f"Cache miss - making API call for keywords: {request.keywords}")
            gemini = GeminiGroundedProvider()

            # Single comprehensive research prompt - Gemini handles Google Search automatically
            research_prompt = f"""
            Research the topic "{topic}" in the {industry} industry for {target_audience} audience. Provide a comprehensive analysis including:

            1. Current trends and insights (2024-2025)
            2. Key statistics and data points with sources
            3. Industry expert opinions and quotes
            4. Recent developments and news
            5. Market analysis and forecasts
            6. Best practices and case studies
            7. Keyword analysis: primary, secondary, and long-tail opportunities
            8. Competitor analysis: top players and content gaps
            9. Content angle suggestions: 5 compelling angles for blog posts

            Focus on factual, up-to-date information from credible sources.
            Include specific data points, percentages, and recent developments.
            Structure your response with clear sections for each analysis area.
            """
            
            await task_manager.update_progress(task_id, "🤖 Making AI request to Gemini with Google Search grounding...")
            # Single Gemini call with native Google Search grounding - no fallbacks
            # Validation is handled inside generate_grounded_content when validate_subsequent_operations=True
            try:
                gemini_result = await gemini.generate_grounded_content(
                    prompt=research_prompt,
                    content_type="research",
                    max_tokens=2000,
                    user_id=user_id,
                    validate_subsequent_operations=True  # Validates Google Grounding + 3 LLM calls
                )
            except HTTPException as http_error:
                # Re-raise HTTPException so it can be properly handled by task manager
                logger.error(f"Subscription limit exceeded for research: {http_error.detail}")
                await task_manager.update_progress(task_id, f"❌ Subscription limit exceeded: {http_error.detail.get('message', str(http_error.detail)) if isinstance(http_error.detail, dict) else str(http_error.detail)}")
                raise  # Re-raise HTTPException to preserve status code and error details
            
            await task_manager.update_progress(task_id, "📊 Processing research results and extracting insights...")
            # Extract sources from grounding metadata
            sources = self._extract_sources_from_grounding(gemini_result)
            
            # Extract grounding metadata for detailed UI display
            grounding_metadata = self._extract_grounding_metadata(gemini_result)
            
            # Extract search widget and queries for UI display
            search_widget = gemini_result.get("search_widget", "") or ""
            search_queries = gemini_result.get("search_queries", []) or []
            
            await task_manager.update_progress(task_id, "🔍 Analyzing keywords and content angles...")
            # Parse the comprehensive response for different analysis components
            content = gemini_result.get("content", "")
            keyword_analysis = self.keyword_analyzer.analyze(content, request.keywords, user_id=user_id)
            competitor_analysis = self.competitor_analyzer.analyze(content, user_id=user_id)
            suggested_angles = self.content_angle_generator.generate(content, topic, industry, user_id=user_id)
            
            await task_manager.update_progress(task_id, "💾 Caching results for future use...")
            logger.info(f"Research completed successfully with {len(sources)} sources and {len(search_queries)} search queries")

            # Create the response
            response = BlogResearchResponse(
                success=True,
                sources=sources,
                keyword_analysis=keyword_analysis,
                competitor_analysis=competitor_analysis,
                suggested_angles=suggested_angles,
                # Add search widget and queries for UI display
                search_widget=search_widget if 'search_widget' in locals() else "",
                search_queries=search_queries if 'search_queries' in locals() else [],
                # Add grounding metadata for detailed UI display
                grounding_metadata=grounding_metadata,
                # Preserve original user keywords for caching
                original_keywords=request.keywords,
            )
            
            # Filter and clean research data for optimal AI processing
            await task_manager.update_progress(task_id, "🔍 Filtering and cleaning research data...")
            filtered_response = self.data_filter.filter_research_data(response)
            logger.info("Research data filtering completed successfully")
            
            # Cache the successful result for future exact keyword matches (both caches)
            persistent_research_cache.cache_result(
                keywords=request.keywords,
                industry=industry,
                target_audience=target_audience,
                result=filtered_response.dict()
            )
            
            # Also cache in memory for faster access
            research_cache.cache_result(
                keywords=request.keywords,
                industry=industry,
                target_audience=target_audience,
                result=filtered_response.dict()
            )
            
            return filtered_response
            
        except HTTPException:
            # Re-raise HTTPException (subscription errors) - let task manager handle it
            raise
        except Exception as e:
            error_message = str(e)
            logger.error(f"Research failed: {error_message}")
            
            # Log error with full context
            blog_writer_logger.log_error(
                e,
                "research",
                context={
                    "topic": topic,
                    "keywords": request.keywords,
                    "industry": industry,
                    "target_audience": target_audience
                }
            )
            
            # Import custom exceptions for better error handling
            from services.blog_writer.exceptions import (
                ResearchFailedException, 
                APIRateLimitException, 
                APITimeoutException,
                ValidationException
            )
            
            # Determine if this is a retryable error
            retry_suggested = True
            user_message = "Research failed. Please try again with different keywords or check your internet connection."
            
            if isinstance(e, APIRateLimitException):
                retry_suggested = True
                user_message = f"Rate limit exceeded. Please wait {e.context.get('retry_after', 60)} seconds before trying again."
            elif isinstance(e, APITimeoutException):
                retry_suggested = True
                user_message = "Research request timed out. Please try again with a shorter query or check your internet connection."
            elif isinstance(e, ValidationException):
                retry_suggested = False
                user_message = "Invalid research request. Please check your input parameters and try again."
            elif "401" in error_message or "403" in error_message:
                retry_suggested = False
                user_message = "Authentication failed. Please check your API credentials."
            elif "400" in error_message:
                retry_suggested = False
                user_message = "Invalid request. Please check your input parameters."
            
            # Return a graceful failure response with enhanced error information
            return BlogResearchResponse(
                success=False,
                sources=[],
                keyword_analysis={},
                competitor_analysis={},
                suggested_angles=[],
                search_widget="",
                search_queries=[],
                error_message=user_message,
                retry_suggested=retry_suggested,
                error_code=getattr(e, 'error_code', 'RESEARCH_FAILED'),
                actionable_steps=getattr(e, 'actionable_steps', [
                    "Try with different keywords",
                    "Check your internet connection",
                    "Wait a few minutes and try again",
                    "Contact support if the issue persists"
                ])
            )

    def _extract_sources_from_grounding(self, gemini_result: Dict[str, Any]) -> List[ResearchSource]:
        """Extract sources from Gemini grounding metadata."""
        sources = []
        
        # The Gemini grounded provider already extracts sources and puts them in the 'sources' field
        raw_sources = gemini_result.get("sources", [])
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

    def _extract_grounding_metadata(self, gemini_result: Dict[str, Any]) -> GroundingMetadata:
        """Extract detailed grounding metadata from Gemini result."""
        grounding_chunks = []
        grounding_supports = []
        citations = []
        
        # Extract grounding chunks from the raw grounding metadata
        raw_grounding = gemini_result.get("grounding_metadata", {})
        
        # Handle case where grounding_metadata might be a GroundingMetadata object
        if hasattr(raw_grounding, 'grounding_chunks'):
            raw_chunks = raw_grounding.grounding_chunks
        else:
            raw_chunks = raw_grounding.get("grounding_chunks", [])
        
        for chunk in raw_chunks:
            if "web" in chunk:
                web_data = chunk["web"]
                grounding_chunk = GroundingChunk(
                    title=web_data.get("title", "Untitled"),
                    url=web_data.get("uri", ""),
                    confidence_score=None  # Will be set from supports
                )
                grounding_chunks.append(grounding_chunk)
        
        # Extract grounding supports with confidence scores
        if hasattr(raw_grounding, 'grounding_supports'):
            raw_supports = raw_grounding.grounding_supports
        else:
            raw_supports = raw_grounding.get("grounding_supports", [])
        for support in raw_supports:
            # Handle both dictionary and GroundingSupport object formats
            if hasattr(support, 'confidence_scores'):
                confidence_scores = support.confidence_scores
                chunk_indices = support.grounding_chunk_indices
                segment_text = getattr(support, 'segment_text', '')
                start_index = getattr(support, 'start_index', None)
                end_index = getattr(support, 'end_index', None)
            else:
                confidence_scores = support.get("confidence_scores", [])
                chunk_indices = support.get("grounding_chunk_indices", [])
                segment = support.get("segment", {})
                segment_text = segment.get("text", "")
                start_index = segment.get("start_index")
                end_index = segment.get("end_index")
            
            grounding_support = GroundingSupport(
                confidence_scores=confidence_scores,
                grounding_chunk_indices=chunk_indices,
                segment_text=segment_text,
                start_index=start_index,
                end_index=end_index
            )
            grounding_supports.append(grounding_support)
            
            # Update confidence scores for chunks
            if confidence_scores and chunk_indices:
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
                for idx in chunk_indices:
                    if idx < len(grounding_chunks):
                        grounding_chunks[idx].confidence_score = avg_confidence
        
        # Extract citations from the raw result
        raw_citations = gemini_result.get("citations", [])
        for citation in raw_citations:
            citation_obj = Citation(
                citation_type=citation.get("type", "inline"),
                start_index=citation.get("start_index", 0),
                end_index=citation.get("end_index", 0),
                text=citation.get("text", ""),
                source_indices=citation.get("source_indices", []),
                reference=citation.get("reference", "")
            )
            citations.append(citation_obj)
        
        # Extract search entry point and web search queries
        if hasattr(raw_grounding, 'search_entry_point'):
            search_entry_point = getattr(raw_grounding.search_entry_point, 'rendered_content', '') if raw_grounding.search_entry_point else ''
        else:
            search_entry_point = raw_grounding.get("search_entry_point", {}).get("rendered_content", "")
        
        if hasattr(raw_grounding, 'web_search_queries'):
            web_search_queries = raw_grounding.web_search_queries
        else:
            web_search_queries = raw_grounding.get("web_search_queries", [])
        
        return GroundingMetadata(
            grounding_chunks=grounding_chunks,
            grounding_supports=grounding_supports,
            citations=citations,
            search_entry_point=search_entry_point,
            web_search_queries=web_search_queries
        )
