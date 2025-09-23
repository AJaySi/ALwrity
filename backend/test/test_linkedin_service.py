#!/usr/bin/env python3
"""
Test script for LinkedIn service functionality.

This script tests that the LinkedIn service can be initialized and
basic functionality works without errors.

Usage:
    python test_linkedin_service.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from loguru import logger
from models.linkedin_models import LinkedInPostRequest, GroundingLevel
from services.linkedin_service import LinkedInService


async def test_linkedin_service():
    """Test the LinkedIn service functionality."""
    try:
        logger.info("🧪 Testing LinkedIn Service Functionality")
        
        # Initialize the service
        logger.info("📦 Initializing LinkedIn Service...")
        service = LinkedInService()
        logger.info("✅ LinkedIn Service initialized successfully")
        
        # Create a test request
        test_request = LinkedInPostRequest(
            topic="AI in Marketing",
            industry="Technology",
            tone="professional",
            max_length=500,
            target_audience="Marketing professionals",
            key_points=["AI automation", "Personalization", "ROI improvement"],
            research_enabled=True,
            search_engine="google",
            grounding_level=GroundingLevel.BASIC,
            include_citations=True
        )
        
        logger.info("📝 Testing LinkedIn Post Generation...")
        
        # Test post generation
        response = await service.generate_linkedin_post(test_request)
        
        if response.success:
            logger.info("✅ LinkedIn post generation successful")
            logger.info(f"📊 Content length: {len(response.data.content)} characters")
            logger.info(f"🔗 Sources: {len(response.research_sources)}")
            logger.info(f"📚 Citations: {len(response.data.citations)}")
            logger.info(f"🏆 Quality score: {response.data.quality_metrics.overall_score if response.data.quality_metrics else 'N/A'}")
            
            # Display a snippet of the generated content
            content_preview = response.data.content[:200] + "..." if len(response.data.content) > 200 else response.data.content
            logger.info(f"📄 Content preview: {content_preview}")
            
        else:
            logger.error(f"❌ LinkedIn post generation failed: {response.error}")
            return False
        
        logger.info("🎉 LinkedIn service test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ LinkedIn service test failed: {str(e)}")
        return False


async def main():
    """Main test function."""
    logger.info("🚀 Starting LinkedIn Service Test")
    logger.info("=" * 50)
    
    success = await test_linkedin_service()
    
    if success:
        logger.info("\n🎉 SUCCESS: LinkedIn service is working correctly!")
        logger.info("✅ Service initialization successful")
        logger.info("✅ Post generation working")
        logger.info("✅ Ready for production use")
    else:
        logger.error("\n❌ FAILURE: LinkedIn service test failed")
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
