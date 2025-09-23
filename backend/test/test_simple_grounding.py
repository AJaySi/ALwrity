#!/usr/bin/env python3
"""
Simple test script to verify basic grounding functionality.

This script tests the core components without triggering API overload.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from loguru import logger
from services.llm_providers.gemini_grounded_provider import GeminiGroundedProvider

async def test_basic_functionality():
    """Test basic grounding functionality."""
    try:
        logger.info("🧪 Testing Basic Grounding Functionality")
        
        # Initialize provider
        provider = GeminiGroundedProvider()
        logger.info("✅ Provider initialized successfully")
        
        # Test prompt building
        prompt = "Write a short LinkedIn post about AI trends"
        grounded_prompt = provider._build_grounded_prompt(prompt, "linkedin_post")
        logger.info(f"✅ Grounded prompt built: {len(grounded_prompt)} characters")
        
        # Test content processing
        test_content = "AI is transforming industries #AI #Technology"
        processed = provider._process_post_content(test_content)
        logger.info(f"✅ Content processed: {len(processed.get('hashtags', []))} hashtags found")
        
        logger.info("🎉 Basic functionality test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Basic functionality test failed: {str(e)}")
        return False

async def main():
    """Main test function."""
    logger.info("🚀 Starting Simple Grounding Test")
    logger.info("=" * 50)
    
    success = await test_basic_functionality()
    
    if success:
        logger.info("\n🎉 SUCCESS: Basic grounding functionality is working!")
        logger.info("✅ Provider initialization successful")
        logger.info("✅ Prompt building working")
        logger.info("✅ Content processing working")
        logger.info("✅ Ready for API integration")
    else:
        logger.error("\n❌ FAILURE: Basic functionality test failed")
        sys.exit(1)

if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Run the test
    asyncio.run(main())
