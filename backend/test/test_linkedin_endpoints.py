"""
Test script for LinkedIn content generation endpoints.

This script tests the LinkedIn content generation functionality
to ensure proper integration and validation.
"""

import asyncio
import json
import time
from typing import Dict, Any
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.linkedin_models import (
    LinkedInPostRequest, LinkedInArticleRequest, LinkedInCarouselRequest,
    LinkedInVideoScriptRequest, LinkedInCommentResponseRequest
)
from services.linkedin_service import linkedin_service
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<level>{level}</level> | {message}")


async def test_post_generation():
    """Test LinkedIn post generation."""
    logger.info("🧪 Testing LinkedIn Post Generation")
    
    try:
        request = LinkedInPostRequest(
            topic="Artificial Intelligence in Healthcare",
            industry="Healthcare",
            post_type="thought_leadership",
            tone="professional",
            target_audience="Healthcare executives and AI professionals",
            key_points=["AI diagnostics", "Patient outcomes", "Cost reduction", "Implementation challenges"],
            include_hashtags=True,
            include_call_to_action=True,
            research_enabled=True,
            search_engine="metaphor",
            max_length=2000
        )
        
        start_time = time.time()
        response = await linkedin_service.generate_post(request)
        duration = time.time() - start_time
        
        logger.info(f"✅ Post generation completed in {duration:.2f} seconds")
        logger.info(f"Success: {response.success}")
        
        if response.success and response.data:
            logger.info(f"Content length: {response.data.character_count} characters")
            logger.info(f"Hashtags generated: {len(response.data.hashtags)}")
            logger.info(f"Call-to-action: {response.data.call_to_action is not None}")
            logger.info(f"Research sources: {len(response.research_sources)}")
            
            # Preview content (first 200 chars)
            content_preview = response.data.content[:200] + "..." if len(response.data.content) > 200 else response.data.content
            logger.info(f"Content preview: {content_preview}")
        else:
            logger.error(f"Post generation failed: {response.error}")
            
        return response.success
        
    except Exception as e:
        logger.error(f"❌ Error testing post generation: {str(e)}")
        return False


async def test_article_generation():
    """Test LinkedIn article generation."""
    logger.info("🧪 Testing LinkedIn Article Generation")
    
    try:
        request = LinkedInArticleRequest(
            topic="Digital Transformation in Manufacturing",
            industry="Manufacturing",
            tone="professional",
            target_audience="Manufacturing leaders and technology professionals",
            key_sections=["Current challenges", "Technology solutions", "Implementation strategies", "Future outlook"],
            include_images=True,
            seo_optimization=True,
            research_enabled=True,
            search_engine="metaphor",
            word_count=1500
        )
        
        start_time = time.time()
        response = await linkedin_service.generate_article(request)
        duration = time.time() - start_time
        
        logger.info(f"✅ Article generation completed in {duration:.2f} seconds")
        logger.info(f"Success: {response.success}")
        
        if response.success and response.data:
            logger.info(f"Word count: {response.data.word_count}")
            logger.info(f"Sections: {len(response.data.sections)}")
            logger.info(f"Reading time: {response.data.reading_time} minutes")
            logger.info(f"Image suggestions: {len(response.data.image_suggestions)}")
            logger.info(f"SEO metadata: {response.data.seo_metadata is not None}")
            logger.info(f"Research sources: {len(response.research_sources)}")
            
            # Preview title
            logger.info(f"Article title: {response.data.title}")
        else:
            logger.error(f"Article generation failed: {response.error}")
            
        return response.success
        
    except Exception as e:
        logger.error(f"❌ Error testing article generation: {str(e)}")
        return False


async def test_carousel_generation():
    """Test LinkedIn carousel generation."""
    logger.info("🧪 Testing LinkedIn Carousel Generation")
    
    try:
        request = LinkedInCarouselRequest(
            topic="5 Ways to Improve Team Productivity",
            industry="Business Management",
            slide_count=8,
            tone="professional",
            target_audience="Team leaders and managers",
            key_takeaways=["Clear communication", "Goal setting", "Tool optimization", "Regular feedback", "Work-life balance"],
            include_cover_slide=True,
            include_cta_slide=True,
            visual_style="modern"
        )
        
        start_time = time.time()
        response = await linkedin_service.generate_carousel(request)
        duration = time.time() - start_time
        
        logger.info(f"✅ Carousel generation completed in {duration:.2f} seconds")
        logger.info(f"Success: {response.success}")
        
        if response.success and response.data:
            logger.info(f"Slide count: {len(response.data.slides)}")
            logger.info(f"Carousel title: {response.data.title}")
            logger.info(f"Design guidelines: {bool(response.data.design_guidelines)}")
            
            # Preview first slide
            if response.data.slides:
                first_slide = response.data.slides[0]
                logger.info(f"First slide title: {first_slide.title}")
        else:
            logger.error(f"Carousel generation failed: {response.error}")
            
        return response.success
        
    except Exception as e:
        logger.error(f"❌ Error testing carousel generation: {str(e)}")
        return False


async def test_video_script_generation():
    """Test LinkedIn video script generation."""
    logger.info("🧪 Testing LinkedIn Video Script Generation")
    
    try:
        request = LinkedInVideoScriptRequest(
            topic="Quick tips for remote team management",
            industry="Human Resources",
            video_length=90,
            tone="conversational",
            target_audience="Remote team managers",
            key_messages=["Communication tools", "Regular check-ins", "Team building", "Performance tracking"],
            include_hook=True,
            include_captions=True
        )
        
        start_time = time.time()
        response = await linkedin_service.generate_video_script(request)
        duration = time.time() - start_time
        
        logger.info(f"✅ Video script generation completed in {duration:.2f} seconds")
        logger.info(f"Success: {response.success}")
        
        if response.success and response.data:
            logger.info(f"Hook: {bool(response.data.hook)}")
            logger.info(f"Main content scenes: {len(response.data.main_content)}")
            logger.info(f"Conclusion: {bool(response.data.conclusion)}")
            logger.info(f"Thumbnail suggestions: {len(response.data.thumbnail_suggestions)}")
            logger.info(f"Captions: {bool(response.data.captions)}")
            
            # Preview hook
            if response.data.hook:
                hook_preview = response.data.hook[:100] + "..." if len(response.data.hook) > 100 else response.data.hook
                logger.info(f"Hook preview: {hook_preview}")
        else:
            logger.error(f"Video script generation failed: {response.error}")
            
        return response.success
        
    except Exception as e:
        logger.error(f"❌ Error testing video script generation: {str(e)}")
        return False


async def test_comment_response_generation():
    """Test LinkedIn comment response generation."""
    logger.info("🧪 Testing LinkedIn Comment Response Generation")
    
    try:
        request = LinkedInCommentResponseRequest(
            original_post="Just published an article about AI transformation in healthcare. The potential for improving patient outcomes while reducing costs is incredible. Healthcare leaders need to start preparing for this shift now.",
            comment="Great insights! How do you see this affecting smaller healthcare providers who might not have the resources for large AI implementations?",
            response_type="value_add",
            tone="professional",
            include_question=True,
            brand_voice="Expert but approachable, data-driven and helpful"
        )
        
        start_time = time.time()
        response = await linkedin_service.generate_comment_response(request)
        duration = time.time() - start_time
        
        logger.info(f"✅ Comment response generation completed in {duration:.2f} seconds")
        logger.info(f"Success: {response.success}")
        
        if response.success and response.response:
            logger.info(f"Primary response length: {len(response.response)} characters")
            logger.info(f"Alternative responses: {len(response.alternative_responses)}")
            logger.info(f"Tone analysis: {bool(response.tone_analysis)}")
            
            # Preview response
            response_preview = response.response[:150] + "..." if len(response.response) > 150 else response.response
            logger.info(f"Response preview: {response_preview}")
            
            if response.tone_analysis:
                logger.info(f"Detected sentiment: {response.tone_analysis.get('sentiment', 'unknown')}")
        else:
            logger.error(f"Comment response generation failed: {response.error}")
            
        return response.success
        
    except Exception as e:
        logger.error(f"❌ Error testing comment response generation: {str(e)}")
        return False


async def test_error_handling():
    """Test error handling with invalid requests."""
    logger.info("🧪 Testing Error Handling")
    
    try:
        # Test with empty topic
        request = LinkedInPostRequest(
            topic="",  # Empty topic should trigger validation error
            industry="Technology",
        )
        
        response = await linkedin_service.generate_post(request)
        
        # Should still handle gracefully
        if not response.success:
            logger.info("✅ Error handling working correctly for invalid input")
            return True
        else:
            logger.warning("⚠️ Expected error handling but got successful response")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in error handling test: {str(e)}")
        return False


async def run_all_tests():
    """Run all LinkedIn content generation tests."""
    logger.info("🚀 Starting LinkedIn Content Generation Tests")
    logger.info("=" * 60)
    
    test_results = {}
    
    # Run individual tests
    test_results["post_generation"] = await test_post_generation()
    logger.info("-" * 40)
    
    test_results["article_generation"] = await test_article_generation()
    logger.info("-" * 40)
    
    test_results["carousel_generation"] = await test_carousel_generation()
    logger.info("-" * 40)
    
    test_results["video_script_generation"] = await test_video_script_generation()
    logger.info("-" * 40)
    
    test_results["comment_response_generation"] = await test_comment_response_generation()
    logger.info("-" * 40)
    
    test_results["error_handling"] = await test_error_handling()
    logger.info("-" * 40)
    
    # Summary
    logger.info("📊 Test Results Summary")
    logger.info("=" * 60)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        logger.info("🎉 All tests passed! LinkedIn content generation is working correctly.")
    else:
        logger.warning(f"⚠️ {total - passed} test(s) failed. Please check the implementation.")
    
    return passed == total


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(run_all_tests())
    
    if success:
        logger.info("\n✅ LinkedIn content generation migration completed successfully!")
        logger.info("The FastAPI endpoints are ready for use.")
    else:
        logger.error("\n❌ Some tests failed. Please review the implementation.")
        
    # Print API endpoint information
    logger.info("\n📡 Available LinkedIn Content Generation Endpoints:")
    logger.info("- POST /api/linkedin/generate-post")
    logger.info("- POST /api/linkedin/generate-article") 
    logger.info("- POST /api/linkedin/generate-carousel")
    logger.info("- POST /api/linkedin/generate-video-script")
    logger.info("- POST /api/linkedin/generate-comment-response")
    logger.info("- GET /api/linkedin/health")
    logger.info("- GET /api/linkedin/content-types")
    logger.info("- GET /api/linkedin/usage-stats")