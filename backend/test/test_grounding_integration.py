"""
Test script for LinkedIn grounding integration.

This script tests the integration of the new grounding services:
- GoogleSearchService
- GeminiGroundedProvider  
- CitationManager
- ContentQualityAnalyzer
- Enhanced LinkedInService
"""

import asyncio
import os
from datetime import datetime
from loguru import logger

# Set up environment variables for testing
os.environ.setdefault('GOOGLE_SEARCH_API_KEY', 'test_key')
os.environ.setdefault('GOOGLE_SEARCH_ENGINE_ID', 'test_engine_id')
os.environ.setdefault('GEMINI_API_KEY', 'test_gemini_key')

from services.linkedin_service import LinkedInService
from models.linkedin_models import (
    LinkedInPostRequest, LinkedInArticleRequest, LinkedInCarouselRequest,
    LinkedInVideoScriptRequest, LinkedInCommentResponseRequest,
    GroundingLevel, SearchEngine, LinkedInTone, LinkedInPostType
)


async def test_grounding_integration():
    """Test the complete grounding integration."""
    logger.info("Starting LinkedIn grounding integration test")
    
    try:
        # Initialize the enhanced LinkedIn service
        linkedin_service = LinkedInService()
        logger.info("LinkedIn service initialized successfully")
        
        # Test 1: Basic post generation with grounding disabled
        logger.info("\n=== Test 1: Basic Post Generation (No Grounding) ===")
        basic_request = LinkedInPostRequest(
            topic="AI in Marketing",
            industry="Marketing",
            post_type=LinkedInPostType.PROFESSIONAL,
            tone=LinkedInTone.PROFESSIONAL,
            research_enabled=False,
            grounding_level=GroundingLevel.NONE,
            include_citations=False
        )
        
        basic_response = await linkedin_service.generate_linkedin_post(basic_request)
        logger.info(f"Basic post generation: {'SUCCESS' if basic_response.success else 'FAILED'}")
        if basic_response.success:
            logger.info(f"Content length: {basic_response.data.character_count}")
            logger.info(f"Grounding enabled: {basic_response.data.grounding_enabled}")
        
        # Test 2: Enhanced post generation with grounding enabled
        logger.info("\n=== Test 2: Enhanced Post Generation (With Grounding) ===")
        enhanced_request = LinkedInPostRequest(
            topic="Digital Transformation in Healthcare",
            industry="Healthcare",
            post_type=LinkedInPostType.THOUGHT_LEADERSHIP,
            tone=LinkedInTone.AUTHORITATIVE,
            research_enabled=True,
            search_engine=SearchEngine.GOOGLE,
            grounding_level=GroundingLevel.ENHANCED,
            include_citations=True,
            max_length=2000
        )
        
        enhanced_response = await linkedin_service.generate_linkedin_post(enhanced_request)
        logger.info(f"Enhanced post generation: {'SUCCESS' if enhanced_response.success else 'FAILED'}")
        if enhanced_response.success:
            logger.info(f"Content length: {enhanced_response.data.character_count}")
            logger.info(f"Grounding enabled: {enhanced_response.data.grounding_enabled}")
            logger.info(f"Research sources: {len(enhanced_response.research_sources)}")
            logger.info(f"Citations: {len(enhanced_response.data.citations)}")
            if enhanced_response.data.quality_metrics:
                logger.info(f"Quality score: {enhanced_response.data.quality_metrics.overall_score:.2f}")
            if enhanced_response.grounding_status:
                logger.info(f"Grounding status: {enhanced_response.grounding_status['status']}")
        
        # Test 3: Article generation with grounding
        logger.info("\n=== Test 3: Article Generation (With Grounding) ===")
        article_request = LinkedInArticleRequest(
            topic="Future of Remote Work",
            industry="Technology",
            tone=LinkedInTone.EDUCATIONAL,
            research_enabled=True,
            search_engine=SearchEngine.GOOGLE,
            grounding_level=GroundingLevel.ENHANCED,
            include_citations=True,
            word_count=1500
        )
        
        article_response = await linkedin_service.generate_linkedin_article(article_request)
        logger.info(f"Article generation: {'SUCCESS' if article_response.success else 'FAILED'}")
        if article_response.success:
            logger.info(f"Word count: {article_response.data.word_count}")
            logger.info(f"Grounding enabled: {article_response.data.grounding_enabled}")
            logger.info(f"Research sources: {len(article_response.research_sources)}")
            logger.info(f"Citations: {len(article_response.data.citations)}")
        
        # Test 4: Carousel generation with grounding
        logger.info("\n=== Test 4: Carousel Generation (With Grounding) ===")
        carousel_request = LinkedInCarouselRequest(
            topic="Cybersecurity Best Practices",
            industry="Technology",
            tone=LinkedInTone.EDUCATIONAL,
            research_enabled=True,
            search_engine=SearchEngine.GOOGLE,
            grounding_level=GroundingLevel.ENHANCED,
            include_citations=True,
            number_of_slides=5
        )
        
        carousel_response = await linkedin_service.generate_linkedin_carousel(carousel_request)
        logger.info(f"Carousel generation: {'SUCCESS' if carousel_response.success else 'FAILED'}")
        if carousel_response.success:
            logger.info(f"Number of slides: {len(carousel_response.data.slides)}")
            logger.info(f"Grounding enabled: {carousel_response.data.grounding_enabled}")
            logger.info(f"Research sources: {len(carousel_response.research_sources)}")
        
        # Test 5: Video script generation with grounding
        logger.info("\n=== Test 5: Video Script Generation (With Grounding) ===")
        video_request = LinkedInVideoScriptRequest(
            topic="AI Ethics in Business",
            industry="Technology",
            tone=LinkedInTone.EDUCATIONAL,
            research_enabled=True,
            search_engine=SearchEngine.GOOGLE,
            grounding_level=GroundingLevel.ENHANCED,
            include_citations=True,
            video_duration=90
        )
        
        video_response = await linkedin_service.generate_linkedin_video_script(video_request)
        logger.info(f"Video script generation: {'SUCCESS' if video_response.success else 'FAILED'}")
        if video_response.success:
            logger.info(f"Grounding enabled: {video_response.data.grounding_enabled}")
            logger.info(f"Research sources: {len(video_response.research_sources)}")
            logger.info(f"Citations: {len(video_response.data.citations)}")
        
        # Test 6: Comment response generation
        logger.info("\n=== Test 6: Comment Response Generation ===")
        comment_request = LinkedInCommentResponseRequest(
            original_comment="Great insights on AI implementation!",
            post_context="Post about AI transformation in healthcare",
            industry="Healthcare",
            tone=LinkedInTone.FRIENDLY,
            response_length="medium",
            include_questions=True,
            research_enabled=False,
            grounding_level=GroundingLevel.BASIC
        )
        
        comment_response = await linkedin_service.generate_linkedin_comment_response(comment_request)
        logger.info(f"Comment response generation: {'SUCCESS' if comment_response.success else 'FAILED'}")
        if comment_response.success:
            logger.info(f"Response length: {len(comment_response.response) if comment_response.response else 0}")
            logger.info(f"Grounding enabled: {comment_response.grounding_status['status'] if comment_response.grounding_status else 'N/A'}")
        
        logger.info("\n=== Integration Test Summary ===")
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Integration test failed: {str(e)}")
        raise


async def test_individual_services():
    """Test individual service components."""
    logger.info("\n=== Testing Individual Service Components ===")
    
    try:
        # Test Google Search Service
        from services.research import GoogleSearchService
        google_search = GoogleSearchService()
        logger.info("GoogleSearchService initialized successfully")
        
        # Test Citation Manager
        from services.citation import CitationManager
        citation_manager = CitationManager()
        logger.info("CitationManager initialized successfully")
        
        # Test Content Quality Analyzer
        from services.quality import ContentQualityAnalyzer
        quality_analyzer = ContentQualityAnalyzer()
        logger.info("ContentQualityAnalyzer initialized successfully")
        
        # Test Gemini Grounded Provider
        from services.llm_providers.gemini_grounded_provider import GeminiGroundedProvider
        gemini_grounded = GeminiGroundedProvider()
        logger.info("GeminiGroundedProvider initialized successfully")
        
        logger.info("All individual services initialized successfully!")
        
    except Exception as e:
        logger.error(f"Service component test failed: {str(e)}")
        raise


async def main():
    """Main test function."""
    logger.info("Starting LinkedIn Grounding Integration Tests")
    logger.info(f"Test timestamp: {datetime.now().isoformat()}")
    
    try:
        # Test individual services first
        await test_individual_services()
        
        # Test complete integration
        await test_grounding_integration()
        
        logger.info("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test suite failed: {str(e)}")
        logger.error("Please check the error details above and ensure all services are properly configured.")
        return 1
    
    return 0


if __name__ == "__main__":
    # Run the tests
    exit_code = asyncio.run(main())
    exit(exit_code)
