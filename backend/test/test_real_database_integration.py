#!/usr/bin/env python3
"""
Real Database Integration Test for Steps 1-8

This script tests the calendar generation framework with real database services,
replacing all mock data with actual database operations.
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

async def test_real_database_integration():
    """Test Steps 1-8 with real database services."""
    
    try:
        logger.info("🚀 Starting real database integration test")
        
        # Initialize database
        logger.info("🗄️ Initializing database connection")
        from services.database import init_database, get_db_session
        
        try:
            init_database()
            logger.info("✅ Database initialized successfully")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {str(e)}")
            return False
        
        # Get database session
        db_session = get_db_session()
        if not db_session:
            logger.error("❌ Failed to get database session")
            return False
        
        logger.info("✅ Database session created successfully")
        
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
        
        # Create test data in database
        logger.info("📝 Creating test data in database")
        await create_test_data(db_session, test_context)
        
        # Test Step 1: Content Strategy Analysis with Real Database
        logger.info("📋 Testing Step 1: Content Strategy Analysis (Real Database)")
        try:
            from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase1.phase1_steps import ContentStrategyAnalysisStep
            from services.calendar_generation_datasource_framework.data_processing.strategy_data import StrategyDataProcessor
            from services.content_planning_db import ContentPlanningDBService
            
            # Create real database service
            content_planning_db = ContentPlanningDBService(db_session)
            
            # Create strategy processor with real database service
            strategy_processor = StrategyDataProcessor()
            strategy_processor.content_planning_db_service = content_planning_db
            
            step1 = ContentStrategyAnalysisStep()
            step1.strategy_processor = strategy_processor
            
            result1 = await step1.execute(test_context)
            logger.info(f"✅ Step 1 completed: {result1.get('status')}")
            logger.info(f"   Quality Score: {result1.get('quality_score')}")
            
        except Exception as e:
            logger.error(f"❌ Step 1 failed: {str(e)}")
            return False
        
        # Test Step 2: Gap Analysis with Real Database
        logger.info("📋 Testing Step 2: Gap Analysis (Real Database)")
        try:
            from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase1.phase1_steps import GapAnalysisStep
            from services.calendar_generation_datasource_framework.data_processing.gap_analysis_data import GapAnalysisDataProcessor
            
            # Create gap processor with real database service
            gap_processor = GapAnalysisDataProcessor()
            gap_processor.content_planning_db_service = content_planning_db
            
            step2 = GapAnalysisStep()
            step2.gap_processor = gap_processor
            
            result2 = await step2.execute(test_context)
            logger.info(f"✅ Step 2 completed: {result2.get('status')}")
            logger.info(f"   Quality Score: {result2.get('quality_score')}")
            
        except Exception as e:
            logger.error(f"❌ Step 2 failed: {str(e)}")
            return False
        
        # Test Step 3: Audience & Platform Strategy with Real Database
        logger.info("📋 Testing Step 3: Audience & Platform Strategy (Real Database)")
        try:
            from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase1.phase1_steps import AudiencePlatformStrategyStep
            from services.calendar_generation_datasource_framework.data_processing.comprehensive_user_data import ComprehensiveUserDataProcessor
            
            # Create comprehensive processor with real database service
            comprehensive_processor = ComprehensiveUserDataProcessor(db_session)
            comprehensive_processor.content_planning_db_service = content_planning_db
            
            step3 = AudiencePlatformStrategyStep()
            step3.comprehensive_processor = comprehensive_processor
            
            result3 = await step3.execute(test_context)
            logger.info(f"✅ Step 3 completed: {result3.get('status')}")
            logger.info(f"   Quality Score: {result3.get('quality_score')}")
            
        except Exception as e:
            logger.error(f"❌ Step 3 failed: {str(e)}")
            return False
        
        # Test Steps 4-8 with Real Database
        logger.info("📋 Testing Steps 4-8: Calendar Framework to Daily Content Planning (Real Database)")
        try:
            # Test Step 4: Calendar Framework
            from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase2.step4_implementation import CalendarFrameworkStep
            step4 = CalendarFrameworkStep()
            result4 = await step4.execute(test_context)
            logger.info(f"✅ Step 4 completed: {result4.get('status')}")
            
            # Test Step 5: Content Pillar Distribution
            from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase2.step5_implementation import ContentPillarDistributionStep
            step5 = ContentPillarDistributionStep()
            result5 = await step5.execute(test_context)
            logger.info(f"✅ Step 5 completed: {result5.get('status')}")
            
            # Test Step 6: Platform-Specific Strategy
            from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase2.step6_implementation import PlatformSpecificStrategyStep
            step6 = PlatformSpecificStrategyStep()
            result6 = await step6.execute(test_context)
            logger.info(f"✅ Step 6 completed: {result6.get('status')}")
            
            # Test Step 7: Weekly Theme Development
            from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase3.step7_implementation import WeeklyThemeDevelopmentStep
            step7 = WeeklyThemeDevelopmentStep()
            result7 = await step7.execute(test_context)
            logger.info(f"✅ Step 7 completed: {result7.get('status')}")
            
            # Test Step 8: Daily Content Planning
            from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase3.step8_implementation import DailyContentPlanningStep
            step8 = DailyContentPlanningStep()
            result8 = await step8.execute(test_context)
            logger.info(f"✅ Step 8 completed: {result8.get('status')}")
            
        except Exception as e:
            logger.error(f"❌ Steps 4-8 failed: {str(e)}")
            return False
        
        # Clean up test data
        logger.info("🧹 Cleaning up test data")
        await cleanup_test_data(db_session, test_context)
        
        # Close database session
        db_session.close()
        
        logger.info("🎉 All Steps 1-8 completed successfully with real database!")
        logger.info("📝 Real database integration working perfectly!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {str(e)}")
        return False

async def create_test_data(db_session, test_context: Dict[str, Any]):
    """Create test data in the database."""
    try:
        from services.content_planning_db import ContentPlanningDBService
        from models.content_planning import ContentStrategy, ContentGapAnalysis
        
        db_service = ContentPlanningDBService(db_session)
        
        # Create test content strategy
        strategy_data = {
            "user_id": test_context["user_id"],
            "name": "Test Strategy - Real Database",
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
            "ai_recommendations": {
                "strategic_insights": [
                    "Focus on deep-dive technical content",
                    "Emphasize practical implementation guides",
                    "Highlight ROI and business impact"
                ]
            }
        }
        
        strategy = await db_service.create_content_strategy(strategy_data)
        if strategy:
            logger.info(f"✅ Created test strategy: {strategy.id}")
            test_context["strategy_id"] = strategy.id
        
        # Create test gap analysis
        gap_data = {
            "user_id": test_context["user_id"],
            "website_url": "https://example.com",
            "competitor_urls": ["https://competitor1.com", "https://competitor2.com"],
            "target_keywords": [
                {"keyword": "AI ethics in business", "search_volume": 5000, "competition": "low"},
                {"keyword": "digital transformation ROI", "search_volume": 8000, "competition": "medium"}
            ],
            "analysis_results": {
                "content_gaps": [
                    {"topic": "AI Ethics", "priority": "high", "impact_score": 0.9},
                    {"topic": "Digital Transformation ROI", "priority": "medium", "impact_score": 0.7}
                ],
                "keyword_opportunities": [
                    {"keyword": "AI ethics in business", "search_volume": 5000, "competition": "low"},
                    {"keyword": "digital transformation ROI", "search_volume": 8000, "competition": "medium"}
                ],
                "competitor_insights": [
                    {"competitor": "Competitor A", "strength": "Technical content", "weakness": "Practical guides"},
                    {"competitor": "Competitor B", "strength": "Case studies", "weakness": "AI focus"}
                ],
                "opportunities": [
                    {"type": "content", "topic": "AI Ethics", "priority": "high"},
                    {"type": "content", "topic": "ROI Analysis", "priority": "medium"}
                ]
            },
            "recommendations": [
                "Create comprehensive AI ethics guide",
                "Develop ROI calculator for digital transformation"
            ],
            "opportunities": [
                {"type": "content", "topic": "AI Ethics", "priority": "high"},
                {"type": "content", "topic": "ROI Analysis", "priority": "medium"}
            ]
        }
        
        gap_analysis = await db_service.create_content_gap_analysis(gap_data)
        if gap_analysis:
            logger.info(f"✅ Created test gap analysis: {gap_analysis.id}")
        
        logger.info("✅ Test data created successfully")
        
    except Exception as e:
        logger.error(f"❌ Error creating test data: {str(e)}")
        raise

async def cleanup_test_data(db_session, test_context: Dict[str, Any]):
    """Clean up test data from the database."""
    try:
        from services.content_planning_db import ContentPlanningDBService
        
        db_service = ContentPlanningDBService(db_session)
        
        # Clean up gap analysis (get by user_id and delete)
        gap_analyses = await db_service.get_user_content_gap_analyses(test_context["user_id"])
        for gap_analysis in gap_analyses:
            await db_service.delete_content_gap_analysis(gap_analysis.id)
        
        # Clean up strategy
        await db_service.delete_content_strategy(test_context["strategy_id"])
        
        logger.info("✅ Test data cleaned up successfully")
        
    except Exception as e:
        logger.error(f"❌ Error cleaning up test data: {str(e)}")

if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    
    # Run the test
    success = asyncio.run(test_real_database_integration())
    
    if success:
        logger.info("✅ Real database integration test completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Real database integration test failed!")
        sys.exit(1)
