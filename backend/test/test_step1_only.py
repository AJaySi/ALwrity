#!/usr/bin/env python3
"""
Simple Test Script for Step 1 Only

This script tests only Step 1 to verify imports are working correctly.
"""

import asyncio
import sys
import os
from typing import Dict, Any
from loguru import logger

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Add the services directory to the path
services_dir = os.path.join(backend_dir, "services")
if services_dir not in sys.path:
    sys.path.insert(0, services_dir)

async def test_step1_only():
    """Test only Step 1 to verify imports work."""
    
    try:
        logger.info("🚀 Starting test of Step 1 only")
        
        # Test data
        test_context = {
            "user_id": 1,
            "strategy_id": 1,
            "calendar_duration": 7,
            "posting_preferences": {
                "posting_frequency": "daily",
                "preferred_days": ["monday", "wednesday", "friday"],
                "preferred_times": ["09:00", "12:00", "15:00"],
                "content_per_day": 2
            }
        }
        
        # Test Step 1: Content Strategy Analysis
        logger.info("📋 Testing Step 1: Content Strategy Analysis")
        try:
            from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase1.phase1_steps import ContentStrategyAnalysisStep
            from services.calendar_generation_datasource_framework.data_processing.strategy_data import StrategyDataProcessor
            
            logger.info("✅ Imports successful")
            
            # Create strategy processor with mock data for testing
            strategy_processor = StrategyDataProcessor()
            
            # Mock strategy data
            mock_strategy_data = {
                "strategy_id": 1,
                "strategy_name": "Test Strategy",
                "industry": "technology",
                "target_audience": {
                    "primary": "Tech professionals",
                    "secondary": "Business leaders",
                    "demographics": {"age_range": "25-45", "location": "Global"}
                },
                "content_pillars": [
                    "AI and Machine Learning",
                    "Digital Transformation",
                    "Innovation and Technology Trends",
                    "Business Strategy and Growth"
                ],
                "business_objectives": [
                    "Increase brand awareness by 40%",
                    "Generate 500 qualified leads per month",
                    "Establish thought leadership"
                ],
                "target_metrics": {"awareness": "website_traffic", "leads": "lead_generation"},
                "quality_indicators": {"data_completeness": 0.8, "strategic_alignment": 0.9}
            }
            
            # Mock the get_strategy_data method for testing
            async def mock_get_strategy_data(strategy_id):
                return mock_strategy_data
            
            strategy_processor.get_strategy_data = mock_get_strategy_data
            
            # Mock the validate_data method
            async def mock_validate_data(data):
                return {
                    "quality_score": 0.85,
                    "missing_fields": [],
                    "recommendations": []
                }
            
            strategy_processor.validate_data = mock_validate_data
            
            step1 = ContentStrategyAnalysisStep()
            step1.strategy_processor = strategy_processor
            
            result1 = await step1.execute(test_context)
            logger.info(f"✅ Step 1 completed: {result1.get('status')}")
            logger.info(f"   Quality Score: {result1.get('quality_score')}")
            
        except Exception as e:
            logger.error(f"❌ Step 1 failed: {str(e)}")
            return False
        
        logger.info("🎉 Step 1 test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    
    # Run the test
    success = asyncio.run(test_step1_only())
    
    if success:
        logger.info("✅ Test completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Test failed!")
        sys.exit(1)
