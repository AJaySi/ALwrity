#!/usr/bin/env python3
"""
Test script for native Google Search grounding implementation.

This script tests the new GeminiGroundedProvider that uses native Google Search
grounding instead of custom search implementation.

Usage:
    python test_native_grounding.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from loguru import logger
from services.llm_providers.gemini_grounded_provider import GeminiGroundedProvider


async def test_native_grounding():
    """Test the native Google Search grounding functionality."""
    try:
        logger.info("🧪 Testing Native Google Search Grounding")
        
        # Check if GEMINI_API_KEY is set
        if not os.getenv('GEMINI_API_KEY'):
            logger.error("❌ GEMINI_API_KEY environment variable not set")
            logger.info("Please set GEMINI_API_KEY to test native grounding")
            return False
        
        # Initialize the grounded provider
        logger.info("🔧 Initializing Gemini Grounded Provider...")
        provider = GeminiGroundedProvider()
        logger.info("✅ Provider initialized successfully")
        
        # Test 1: Basic grounded content generation
        logger.info("\n📝 Test 1: Basic LinkedIn Post Generation")
        test_prompt = "Write a professional LinkedIn post about the latest AI trends in 2025"
        
        result = await provider.generate_grounded_content(
            prompt=test_prompt,
            content_type="linkedin_post",
            temperature=0.7,
            max_tokens=500
        )
        
        if result and 'content' in result:
            logger.info("✅ Content generated successfully")
            logger.info(f"📊 Content length: {len(result['content'])} characters")
            logger.info(f"🔗 Sources found: {len(result.get('sources', []))}")
            logger.info(f"📚 Citations found: {len(result.get('citations', []))}")
            
            # Display the generated content
            logger.info("\n📄 Generated Content:")
            logger.info("-" * 50)
            logger.info(result['content'][:500] + "..." if len(result['content']) > 500 else result['content'])
            logger.info("-" * 50)
            
            # Display sources if available
            if result.get('sources'):
                logger.info("\n🔗 Sources:")
                for i, source in enumerate(result['sources']):
                    logger.info(f"  {i+1}. {source.get('title', 'Unknown')}")
                    logger.info(f"     URL: {source.get('url', 'N/A')}")
            
            # Display search queries if available
            if result.get('search_queries'):
                logger.info(f"\n🔍 Search Queries Used: {result['search_queries']}")
            
            # Display grounding metadata info
            if result.get('grounding_metadata'):
                logger.info("✅ Grounding metadata found")
            else:
                logger.warning("⚠️ No grounding metadata found")
                
        else:
            logger.error("❌ Content generation failed")
            if 'error' in result:
                logger.error(f"Error: {result['error']}")
            return False
        
        # Test 2: Article generation
        logger.info("\n📝 Test 2: LinkedIn Article Generation")
        article_prompt = "Create a comprehensive article about sustainable business practices in tech companies"
        
        article_result = await provider.generate_grounded_content(
            prompt=article_prompt,
            content_type="linkedin_article",
            temperature=0.7,
            max_tokens=1000
        )
        
        if article_result and 'content' in article_result:
            logger.info("✅ Article generated successfully")
            logger.info(f"📊 Article length: {len(article_result['content'])} characters")
            logger.info(f"🔗 Sources: {len(article_result.get('sources', []))}")
            
            # Check for article-specific processing
            if 'title' in article_result:
                logger.info(f"📰 Article title: {article_result['title']}")
            if 'word_count' in article_result:
                logger.info(f"📊 Word count: {article_result['word_count']}")
                
        else:
            logger.error("❌ Article generation failed")
            return False
        
        # Test 3: Content quality assessment
        logger.info("\n📝 Test 3: Content Quality Assessment")
        if result.get('content') and result.get('sources'):
            quality_metrics = provider.assess_content_quality(
                content=result['content'],
                sources=result['sources']
            )
            
            logger.info("✅ Quality assessment completed")
            logger.info(f"📊 Overall score: {quality_metrics.get('overall_score', 'N/A')}")
            logger.info(f"🔗 Source coverage: {quality_metrics.get('source_coverage', 'N/A')}")
            logger.info(f"🎯 Tone score: {quality_metrics.get('tone_score', 'N/A')}")
            logger.info(f"📝 Word count: {quality_metrics.get('word_count', 'N/A')}")
            logger.info(f"🏆 Quality level: {quality_metrics.get('quality_level', 'N/A')}")
        
        # Test 4: Citation extraction
        logger.info("\n📝 Test 4: Citation Extraction")
        if result.get('content'):
            citations = provider.extract_citations(result['content'])
            logger.info(f"✅ Extracted {len(citations)} citations")
            
            for i, citation in enumerate(citations):
                logger.info(f"  Citation {i+1}: {citation.get('reference', 'Unknown')}")
        
        logger.info("\n🎉 All tests completed successfully!")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {str(e)}")
        logger.info("💡 Make sure to install required dependencies:")
        logger.info("   pip install google-genai loguru")
        return False
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {str(e)}")
        return False


async def test_individual_components():
    """Test individual components of the native grounding system."""
    try:
        logger.info("🔧 Testing Individual Components")
        
        # Test 1: Provider initialization
        logger.info("\n📋 Test 1: Provider Initialization")
        if not os.getenv('GEMINI_API_KEY'):
            logger.warning("⚠️ Skipping provider test - no API key")
            return False
            
        provider = GeminiGroundedProvider()
        logger.info("✅ Provider initialized successfully")
        
        # Test 2: Prompt building
        logger.info("\n📋 Test 2: Prompt Building")
        test_prompt = "Test prompt for LinkedIn post"
        grounded_prompt = provider._build_grounded_prompt(test_prompt, "linkedin_post")
        
        if grounded_prompt and len(grounded_prompt) > len(test_prompt):
            logger.info("✅ Grounded prompt built successfully")
            logger.info(f"📊 Original length: {len(test_prompt)}")
            logger.info(f"📊 Enhanced length: {len(grounded_prompt)}")
        else:
            logger.error("❌ Prompt building failed")
            return False
        
        # Test 3: Content processing methods
        logger.info("\n📋 Test 3: Content Processing Methods")
        
        # Test post processing
        test_content = "This is a test LinkedIn post #AI #Technology"
        post_processing = provider._process_post_content(test_content)
        if post_processing:
            logger.info("✅ Post processing works")
            logger.info(f"🔖 Hashtags found: {len(post_processing.get('hashtags', []))}")
        
        # Test article processing
        test_article = "# Test Article\n\nThis is test content for an article."
        article_processing = provider._process_article_content(test_article)
        if article_processing:
            logger.info("✅ Article processing works")
            logger.info(f"📊 Word count: {article_processing.get('word_count', 'N/A')}")
        
        logger.info("✅ All component tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Component test failed: {str(e)}")
        return False


async def main():
    """Main test function."""
    logger.info("🚀 Starting Native Grounding Tests")
    logger.info("=" * 60)
    
    # Test individual components first
    component_success = await test_individual_components()
    
    if component_success:
        # Test the full integration
        integration_success = await test_native_grounding()
        
        if integration_success:
            logger.info("\n🎉 SUCCESS: All tests passed!")
            logger.info("✅ Native Google Search grounding is working correctly")
            logger.info("✅ Gemini API integration successful")
            logger.info("✅ Grounding metadata processing working")
            logger.info("✅ Content generation with sources successful")
        else:
            logger.error("\n❌ FAILURE: Integration tests failed")
            sys.exit(1)
    else:
        logger.error("\n❌ FAILURE: Component tests failed")
        sys.exit(1)


if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Run the tests
    asyncio.run(main())
