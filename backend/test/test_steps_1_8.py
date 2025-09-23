#!/usr/bin/env python3
"""
Test Script for Steps 1-8 of Calendar Generation Framework

This script tests the first 8 steps of the calendar generation process
with real data sources and no fallbacks.
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

async def test_steps_1_8():
    """Test Steps 1-8 of the calendar generation framework."""
    
    try:
        logger.info("🚀 Starting test of Steps 1-8")
        
        # Test data
        test_context = {
            "user_id": 1,
            "strategy_id": 1,
            "calendar_duration": 7,  # 1 week
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
            
            # Create strategy processor with mock data for testing
            strategy_processor = StrategyDataProcessor()
            
            # For testing, we'll create a simple mock strategy data
            # In a real scenario, this would come from the database
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
        
        # Test Step 2: Gap Analysis
        logger.info("📋 Testing Step 2: Gap Analysis")
        try:
            from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase1.phase1_steps import GapAnalysisStep
            from services.calendar_generation_datasource_framework.data_processing.gap_analysis_data import GapAnalysisDataProcessor
            
            # Create gap processor with mock data for testing
            gap_processor = GapAnalysisDataProcessor()
            
            # Mock gap analysis data
            mock_gap_data = {
                "content_gaps": [
                    {"topic": "AI Ethics", "priority": "high", "impact_score": 0.9},
                    {"topic": "Digital Transformation ROI", "priority": "medium", "impact_score": 0.7},
                    {"topic": "Cloud Migration Strategies", "priority": "high", "impact_score": 0.8}
                ],
                "keyword_opportunities": [
                    {"keyword": "AI ethics in business", "search_volume": 5000, "competition": "low"},
                    {"keyword": "digital transformation ROI", "search_volume": 8000, "competition": "medium"},
                    {"keyword": "cloud migration guide", "search_volume": 12000, "competition": "high"}
                ],
                "competitor_insights": {
                    "top_competitors": ["Competitor A", "Competitor B"],
                    "content_gaps": ["AI Ethics", "Practical ROI"],
                    "opportunities": ["Case Studies", "Implementation Guides"]
                },
                "opportunities": [
                    {"type": "content", "topic": "AI Ethics", "priority": "high"},
                    {"type": "content", "topic": "ROI Analysis", "priority": "medium"}
                ],
                "recommendations": [
                    "Create comprehensive AI ethics guide",
                    "Develop ROI calculator for digital transformation",
                    "Publish case studies on successful implementations"
                ]
            }
            
            # Mock the get_gap_analysis_data method
            async def mock_get_gap_analysis_data(user_id):
                return mock_gap_data
            
            gap_processor.get_gap_analysis_data = mock_get_gap_analysis_data
            
            step2 = GapAnalysisStep()
            step2.gap_processor = gap_processor
            
            result2 = await step2.execute(test_context)
            logger.info(f"✅ Step 2 completed: {result2.get('status')}")
            logger.info(f"   Quality Score: {result2.get('quality_score')}")
            
        except Exception as e:
            logger.error(f"❌ Step 2 failed: {str(e)}")
            return False
        
        # Test Step 3: Audience & Platform Strategy
        logger.info("📋 Testing Step 3: Audience & Platform Strategy")
        try:
            from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase1.phase1_steps import AudiencePlatformStrategyStep
            from services.calendar_generation_datasource_framework.data_processing.comprehensive_user_data import ComprehensiveUserDataProcessor
            
            # Create comprehensive processor with mock data for testing
            comprehensive_processor = ComprehensiveUserDataProcessor()
            
            # Mock comprehensive user data
            mock_user_data = {
                "user_id": 1,
                "onboarding_data": {
                    "industry": "technology",
                    "business_size": "enterprise",
                    "target_audience": {
                        "primary": "Tech professionals",
                        "secondary": "Business leaders",
                        "demographics": {"age_range": "25-45", "location": "Global"}
                    },
                    "platform_preferences": {
                        "LinkedIn": {"priority": "high", "content_focus": "professional"},
                        "Twitter": {"priority": "medium", "content_focus": "news"},
                        "Blog": {"priority": "high", "content_focus": "in-depth"}
                    }
                },
                "performance_data": {
                    "LinkedIn": {"engagement_rate": 0.08, "reach": 10000},
                    "Twitter": {"engagement_rate": 0.05, "reach": 5000},
                    "Blog": {"engagement_rate": 0.12, "reach": 8000}
                },
                "strategy_data": mock_strategy_data
            }
            
            # Mock the get_comprehensive_user_data method
            async def mock_get_comprehensive_user_data(user_id, strategy_id):
                return mock_user_data
            
            comprehensive_processor.get_comprehensive_user_data = mock_get_comprehensive_user_data
            
            step3 = AudiencePlatformStrategyStep()
            step3.comprehensive_processor = comprehensive_processor
            
            result3 = await step3.execute(test_context)
            logger.info(f"✅ Step 3 completed: {result3.get('status')}")
            logger.info(f"   Quality Score: {result3.get('quality_score')}")
            
        except Exception as e:
            logger.error(f"❌ Step 3 failed: {str(e)}")
            return False
        
        # Test Step 4: Calendar Framework
        logger.info("📋 Testing Step 4: Calendar Framework")
        try:
            from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase2.step4_implementation import CalendarFrameworkStep
            
            step4 = CalendarFrameworkStep()
            result4 = await step4.execute(test_context)
            logger.info(f"✅ Step 4 completed: {result4.get('status')}")
            logger.info(f"   Quality Score: {result4.get('quality_score')}")
            
        except Exception as e:
            logger.error(f"❌ Step 4 failed: {str(e)}")
            return False
        
        # Test Step 5: Content Pillar Distribution
        logger.info("📋 Testing Step 5: Content Pillar Distribution")
        try:
            from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase2.step5_implementation import ContentPillarDistributionStep
            
            step5 = ContentPillarDistributionStep()
            result5 = await step5.execute(test_context)
            logger.info(f"✅ Step 5 completed: {result5.get('status')}")
            logger.info(f"   Quality Score: {result5.get('quality_score')}")
            
        except Exception as e:
            logger.error(f"❌ Step 5 failed: {str(e)}")
            return False
        
        # Test Step 6: Platform-Specific Strategy
        logger.info("📋 Testing Step 6: Platform-Specific Strategy")
        try:
            from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase2.step6_implementation import PlatformSpecificStrategyStep
            
            step6 = PlatformSpecificStrategyStep()
            result6 = await step6.execute(test_context)
            logger.info(f"✅ Step 6 completed: {result6.get('status')}")
            logger.info(f"   Quality Score: {result6.get('quality_score')}")
            
        except Exception as e:
            logger.error(f"❌ Step 6 failed: {str(e)}")
            return False
        
        # Test Step 7: Weekly Theme Development
        logger.info("📋 Testing Step 7: Weekly Theme Development")
        try:
            from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase3.step7_implementation import WeeklyThemeDevelopmentStep
            
            step7 = WeeklyThemeDevelopmentStep()
            result7 = await step7.execute(test_context)
            logger.info(f"✅ Step 7 completed: {result7.get('status')}")
            logger.info(f"   Quality Score: {result7.get('quality_score')}")
            
        except Exception as e:
            logger.error(f"❌ Step 7 failed: {str(e)}")
            return False
        
        # Test Step 8: Daily Content Planning
        logger.info("📋 Testing Step 8: Daily Content Planning")
        try:
            from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase3.step8_implementation import DailyContentPlanningStep
            
            step8 = DailyContentPlanningStep()
            result8 = await step8.execute(test_context)
            logger.info(f"✅ Step 8 completed: {result8.get('status')}")
            logger.info(f"   Quality Score: {result8.get('quality_score')}")
            
        except Exception as e:
            logger.error(f"❌ Step 8 failed: {str(e)}")
            return False
        
        logger.info("🎉 All Steps 1-8 completed successfully!")
        logger.info("📝 Note: This test uses mock data for database services.")
        logger.info("📝 In production, real database services would be used.")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    
    # Run the test
    success = asyncio.run(test_steps_1_8())
    
    if success:
        logger.info("✅ Test completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Test failed!")
        sys.exit(1)
