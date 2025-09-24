"""
LinkedIn Content Generation Service for ALwrity

This service generates various types of LinkedIn content with enhanced grounding capabilities.
Integrated with Google Search, Gemini Grounded Provider, and quality analysis.
"""

import asyncio
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger

from models.linkedin_models import (
    LinkedInPostRequest, LinkedInPostResponse, PostContent, ResearchSource,
    LinkedInArticleRequest, LinkedInArticleResponse, ArticleContent,
    LinkedInCarouselRequest, LinkedInCarouselResponse, CarouselContent, CarouselSlide,
    LinkedInVideoScriptRequest, LinkedInVideoScriptResponse, VideoScript,
    LinkedInCommentResponseRequest, LinkedInCommentResponseResult,
    HashtagSuggestion, ImageSuggestion, Citation, ContentQualityMetrics,
    GroundingLevel
)
from services.research import GoogleSearchService
from services.llm_providers.gemini_grounded_provider import GeminiGroundedProvider
from services.citation import CitationManager
from services.quality import ContentQualityAnalyzer


class LinkedInService:
    """
    Enhanced LinkedIn content generation service with grounding capabilities.
    
    This service integrates real research, grounded content generation,
    citation management, and quality analysis for enterprise-grade content.
    """
    
    def __init__(self):
        """Initialize the LinkedIn service with all required components."""
        # Google Search Service not used - removed to avoid false warnings
        self.google_search = None
            
        try:
            self.gemini_grounded = GeminiGroundedProvider()
            logger.info("✅ Gemini Grounded Provider initialized")
        except Exception as e:
            logger.warning(f"⚠️ Gemini Grounded Provider not available: {e}")
            self.gemini_grounded = None
            
        try:
            self.citation_manager = CitationManager()
            logger.info("✅ Citation Manager initialized")
        except Exception as e:
            logger.warning(f"⚠️ Citation Manager not available: {e}")
            self.citation_manager = None
            
        try:
            self.quality_analyzer = ContentQualityAnalyzer()
            logger.info("✅ Content Quality Analyzer initialized")
        except Exception as e:
            logger.warning(f"⚠️ Content Quality Analyzer not available: {e}")
            self.quality_analyzer = None
        
        # Initialize fallback provider for non-grounded content
        try:
            from services.llm_providers.gemini_provider import gemini_structured_json_response, gemini_text_response
            self.fallback_provider = {
                'generate_structured_json': gemini_structured_json_response,
                'generate_text': gemini_text_response
            }
            logger.info("✅ Fallback Gemini provider initialized")
        except ImportError as e:
            logger.warning(f"⚠️ Fallback Gemini provider not available: {e}")
            self.fallback_provider = None
    
    async def generate_linkedin_post(self, request: LinkedInPostRequest) -> LinkedInPostResponse:
        """
        Generate a LinkedIn post with enhanced grounding capabilities.
        
        Args:
            request: LinkedIn post generation request with grounding options
            
        Returns:
            LinkedInPostResponse with grounded content and quality metrics
        """
        try:
            start_time = datetime.now()
            logger.info(f"Starting LinkedIn post generation for topic: {request.topic}")
        
            # Debug: Log the request object and search_engine value
            logger.info(f"Request object: {request}")
            logger.info(f"Request search_engine: '{request.search_engine}' (type: {type(request.search_engine)})")
        
            # Step 1: Conduct research if enabled
            from services.linkedin.research_handler import ResearchHandler
            research_handler = ResearchHandler(self)
            research_sources, research_time = await research_handler.conduct_research(
                request, request.research_enabled, request.search_engine, 10
            )
            
            # Step 2: Generate content based on grounding level
            grounding_enabled = research_handler.determine_grounding_enabled(request, research_sources)
            
            # Use ContentGenerator for content generation
            from services.linkedin.content_generator import ContentGenerator
            content_generator = ContentGenerator(
                self.citation_manager, 
                self.quality_analyzer, 
                self.gemini_grounded, 
                self.fallback_provider
            )
            
            if grounding_enabled:
                content_result = await content_generator.generate_grounded_post_content(
                    request=request,
                    research_sources=research_sources
                )
            else:
                logger.error("Grounding not enabled, Error generating LinkedIn post")
                raise Exception("Grounding not enabled, Error generating LinkedIn post")
            
            # Step 3-5: Use content generator for processing and response building
            return await content_generator.generate_post(
                request=request,
                research_sources=research_sources,
                research_time=research_time,
                content_result=content_result,
                grounding_enabled=grounding_enabled
            )
            
        except Exception as e:
            logger.error(f"Error generating LinkedIn post: {str(e)}")
            return LinkedInPostResponse(
                success=False,
                error=f"Failed to generate LinkedIn post: {str(e)}"
            )
    
    async def generate_linkedin_article(self, request: LinkedInArticleRequest) -> LinkedInArticleResponse:
        """
        Generate a LinkedIn article with enhanced grounding capabilities.
        
        Args:
            request: LinkedIn article generation request with grounding options
            
        Returns:
            LinkedInArticleResponse with grounded content and quality metrics
        """
        try:
            start_time = datetime.now()
            logger.info(f"Starting LinkedIn article generation for topic: {request.topic}")
        
            # Step 1: Conduct research if enabled
            from services.linkedin.research_handler import ResearchHandler
            research_handler = ResearchHandler(self)
            research_sources, research_time = await research_handler.conduct_research(
                request, request.research_enabled, request.search_engine, 15
            )
            
            # Step 2: Generate content based on grounding level
            grounding_enabled = research_handler.determine_grounding_enabled(request, research_sources)
            
            # Use ContentGenerator for content generation
            from services.linkedin.content_generator import ContentGenerator
            content_generator = ContentGenerator(
                self.citation_manager, 
                self.quality_analyzer, 
                self.gemini_grounded, 
                self.fallback_provider
            )
            
            if grounding_enabled:
                content_result = await content_generator.generate_grounded_article_content(
                    request=request,
                    research_sources=research_sources
                )
            else:
                logger.error("Grounding not enabled - cannot generate LinkedIn article without AI provider")
                raise Exception("Grounding not enabled - cannot generate LinkedIn article without AI provider")
            
            # Step 3-5: Use content generator for processing and response building
            return await content_generator.generate_article(
                request=request,
                research_sources=research_sources,
                research_time=research_time,
                content_result=content_result,
                grounding_enabled=grounding_enabled
            )
            
        except Exception as e:
            logger.error(f"Error generating LinkedIn article: {str(e)}")
            return LinkedInArticleResponse(
                success=False,
                error=f"Failed to generate LinkedIn article: {str(e)}"
            )
    
    async def generate_linkedin_carousel(self, request: LinkedInCarouselRequest) -> LinkedInCarouselResponse:
        """
        Generate a LinkedIn carousel with enhanced grounding capabilities.
        
        Args:
            request: LinkedIn carousel generation request with grounding options
            
        Returns:
            LinkedInCarouselResponse with grounded content and quality metrics
        """
        try:
            start_time = datetime.now()
            logger.info(f"Starting LinkedIn carousel generation for topic: {request.topic}")
        
            # Step 1: Conduct research if enabled
            from services.linkedin.research_handler import ResearchHandler
            research_handler = ResearchHandler(self)
            research_sources, research_time = await research_handler.conduct_research(
                request, request.research_enabled, request.search_engine, 12
            )
            
            # Step 2: Generate content based on grounding level
            grounding_enabled = research_handler.determine_grounding_enabled(request, research_sources)
            
            # Use ContentGenerator for content generation
            from services.linkedin.content_generator import ContentGenerator
            content_generator = ContentGenerator(
                self.citation_manager, 
                self.quality_analyzer, 
                self.gemini_grounded, 
                self.fallback_provider
            )
            
            if grounding_enabled:
                content_result = await content_generator.generate_grounded_carousel_content(
                    request=request,
                    research_sources=research_sources
                )
            else:
                logger.error("Grounding not enabled - cannot generate LinkedIn carousel without AI provider")
                raise Exception("Grounding not enabled - cannot generate LinkedIn carousel without AI provider")
            
            # Step 3-5: Use content generator for processing and response building
            
            result = await content_generator.generate_carousel(
                request=request,
                research_sources=research_sources,
                research_time=research_time,
                content_result=content_result,
                grounding_enabled=grounding_enabled
            )
            
            if result['success']:
                # Convert to LinkedInCarouselResponse
                from models.linkedin_models import CarouselSlide, CarouselContent
                slides = []
                for slide_data in result['data']['slides']:
                    slides.append(CarouselSlide(
                        slide_number=slide_data['slide_number'],
                        title=slide_data['title'],
                        content=slide_data['content'],
                        visual_elements=slide_data['visual_elements'],
                        design_notes=slide_data.get('design_notes')
                    ))
                
                carousel_content = CarouselContent(
                    title=result['data']['title'],
                    slides=slides,
                    cover_slide=result['data'].get('cover_slide'),
                    cta_slide=result['data'].get('cta_slide'),
                    design_guidelines=result['data'].get('design_guidelines', {})
                )
                
                return LinkedInCarouselResponse(
                    success=True,
                    data=carousel_content,
                    research_sources=result['research_sources'],
                    generation_metadata=result['generation_metadata'],
                    grounding_status=result['grounding_status']
                )
            else:
                return LinkedInCarouselResponse(
                    success=False,
                    error=result['error']
                )
                
        except Exception as e:
            logger.error(f"Error generating LinkedIn carousel: {str(e)}")
            return LinkedInCarouselResponse(
                success=False,
                error=f"Failed to generate LinkedIn carousel: {str(e)}"
            )
    
    async def generate_linkedin_video_script(self, request: LinkedInVideoScriptRequest) -> LinkedInVideoScriptResponse:
        """
        Generate a LinkedIn video script with enhanced grounding capabilities.
        
        Args:
            request: LinkedIn video script generation request with grounding options
            
        Returns:
            LinkedInVideoScriptResponse with grounded content and quality metrics
        """
        try:
            start_time = datetime.now()
            logger.info(f"Starting LinkedIn video script generation for topic: {request.topic}")
        
            # Step 1: Conduct research if enabled
            from services.linkedin.research_handler import ResearchHandler
            research_handler = ResearchHandler(self)
            research_sources, research_time = await research_handler.conduct_research(
                request, request.research_enabled, request.search_engine, 8
            )
            
            # Step 2: Generate content based on grounding level
            grounding_enabled = research_handler.determine_grounding_enabled(request, research_sources)
            
            # Use ContentGenerator for content generation
            from services.linkedin.content_generator import ContentGenerator
            content_generator = ContentGenerator(
                self.citation_manager, 
                self.quality_analyzer, 
                self.gemini_grounded, 
                self.fallback_provider
            )
            
            if grounding_enabled:
                content_result = await content_generator.generate_grounded_video_script_content(
                    request=request,
                    research_sources=research_sources
                )
            else:
                logger.error("Grounding not enabled - cannot generate LinkedIn video script without AI provider")
                raise Exception("Grounding not enabled - cannot generate LinkedIn video script without AI provider")
            
            # Step 3-5: Use content generator for processing and response building
            
            result = await content_generator.generate_video_script(
                request=request,
                research_sources=research_sources,
                research_time=research_time,
                content_result=content_result,
                grounding_enabled=grounding_enabled
            )
            
            if result['success']:
                # Convert to LinkedInVideoScriptResponse
                from models.linkedin_models import VideoScript
                video_script = VideoScript(
                    hook=result['data']['hook'],
                    main_content=result['data']['main_content'],
                    conclusion=result['data']['conclusion'],
                    captions=result['data'].get('captions'),
                    thumbnail_suggestions=result['data'].get('thumbnail_suggestions', []),
                    video_description=result['data'].get('video_description', '')
                )
                
                return LinkedInVideoScriptResponse(
                    success=True,
                    data=video_script,
                    research_sources=result['research_sources'],
                    generation_metadata=result['generation_metadata'],
                    grounding_status=result['grounding_status']
                )
            else:
                return LinkedInVideoScriptResponse(
                    success=False,
                    error=result['error']
                )
                
        except Exception as e:
            logger.error(f"Error generating LinkedIn video script: {str(e)}")
            return LinkedInVideoScriptResponse(
                success=False,
                error=f"Failed to generate LinkedIn video script: {str(e)}"
            )
    
    async def generate_linkedin_comment_response(self, request: LinkedInCommentResponseRequest) -> LinkedInCommentResponseResult:
        """
        Generate a LinkedIn comment response with optional grounding capabilities.
        
        Args:
            request: LinkedIn comment response generation request
            
        Returns:
            LinkedInCommentResponseResult with response and optional grounding info
        """
        try:
            start_time = datetime.now()
            logger.info(f"Starting LinkedIn comment response generation")
        
            # Step 1: Conduct research if enabled
            from services.linkedin.research_handler import ResearchHandler
            research_handler = ResearchHandler(self)
            research_sources, research_time = await research_handler.conduct_research(
                request, request.research_enabled, request.search_engine, 5
            )
            
            # Step 2: Generate response based on grounding level
            grounding_enabled = research_handler.determine_grounding_enabled(request, research_sources)
            
            # Use ContentGenerator for content generation
            from services.linkedin.content_generator import ContentGenerator
            content_generator = ContentGenerator(
                self.citation_manager, 
                self.quality_analyzer, 
                self.gemini_grounded, 
                self.fallback_provider
            )
            
            if grounding_enabled:
                response_result = await content_generator.generate_grounded_comment_response(
                    request=request,
                    research_sources=research_sources
                )
            else:
                logger.error("Grounding not enabled - cannot generate LinkedIn comment response without AI provider")
                raise Exception("Grounding not enabled - cannot generate LinkedIn comment response without AI provider")
            
            # Step 3-5: Use content generator for processing and response building
            
            result = await content_generator.generate_comment_response(
                request=request,
                research_sources=research_sources,
                research_time=research_time,
                content_result=response_result,
                grounding_enabled=grounding_enabled
            )
            
            if result['success']:
                # Convert to LinkedInCommentResponseResult
                from models.linkedin_models import CommentResponse
                comment_response = CommentResponse(
                    response=result['response'],
                    alternative_responses=result.get('alternative_responses', []),
                    tone_analysis=result.get('tone_analysis')
                )
                
                return LinkedInCommentResponseResult(
                    success=True,
                    data=comment_response,
                    research_sources=result['research_sources'],
                    generation_metadata=result['generation_metadata'],
                    grounding_status=result['grounding_status']
                )
            else:
                return LinkedInCommentResponseResult(
                    success=False,
                    error=result['error']
                )
                
        except Exception as e:
            logger.error(f"Error generating LinkedIn comment response: {str(e)}")
            return LinkedInCommentResponseResult(
                success=False,
                error=f"Failed to generate LinkedIn comment response: {str(e)}"
            )
    
    async def _conduct_research(self, topic: str, industry: str, search_engine: str, max_results: int = 10) -> List[ResearchSource]:
        """
        Use native Google Search grounding instead of custom search.
        The Gemini API handles search automatically when the google_search tool is enabled.
        
        Args:
            topic: Research topic
            industry: Target industry
            search_engine: Search engine to use (google uses native grounding)
            max_results: Maximum number of results to return
            
        Returns:
            List of research sources (empty for google - sources come from grounding metadata)
        """
        try:
            # Debug: Log the search engine value received
            logger.info(f"Received search engine: '{search_engine}' (type: {type(search_engine)})")
            
            # Handle both enum value 'google' and enum name 'GOOGLE'
            if search_engine.lower() == "google":
                # No need for manual search - Gemini handles it automatically with native grounding
                logger.info("Using native Google Search grounding via Gemini API - no manual search needed")
                return []  # Return empty list - sources will come from grounding metadata
            else:
                # Fallback to basic research for other search engines
                logger.error(f"Search engine {search_engine} not fully implemented, using fallback")
                raise Exception(f"Search engine {search_engine} not fully implemented, using fallback")
                
        except Exception as e:
            logger.error(f"Error conducting research: {str(e)}")
            # Fallback to basic research
            raise Exception(f"Error conducting research: {str(e)}")
