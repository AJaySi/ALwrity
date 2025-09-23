#!/usr/bin/env python3
"""
Debug Step 4 data issues - check what data is available from database.
"""

import asyncio
import time
from loguru import logger
import sys
import os

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

async def test_step4_data_sources():
    """Test what data Step 4 is actually receiving."""
    try:
        logger.info("🧪 Testing Step 4 data sources")
        
        # Test 1: Onboarding Data Service
        logger.info("📋 Test 1: Onboarding Data Service")
        try:
            from services.onboarding_data_service import OnboardingDataService
            onboarding_service = OnboardingDataService()
            
            # Test with user_id = 1
            onboarding_data = onboarding_service.get_personalized_ai_inputs(1)
            
            logger.info(f"📊 Onboarding data keys: {list(onboarding_data.keys()) if onboarding_data else 'None'}")
            
            if onboarding_data:
                # Check for posting preferences
                posting_prefs = onboarding_data.get("posting_preferences")
                posting_days = onboarding_data.get("posting_days")
                optimal_times = onboarding_data.get("optimal_times")
                
                logger.info(f"📅 Posting preferences: {posting_prefs}")
                logger.info(f"📅 Posting days: {posting_days}")
                logger.info(f"📅 Optimal times: {optimal_times}")
                
                # Check website analysis
                website_analysis = onboarding_data.get("website_analysis", {})
                logger.info(f"🌐 Website analysis keys: {list(website_analysis.keys())}")
                
                # Check competitor analysis
                competitor_analysis = onboarding_data.get("competitor_analysis", {})
                logger.info(f"🏢 Competitor analysis keys: {list(competitor_analysis.keys())}")
                
                # Check keyword analysis
                keyword_analysis = onboarding_data.get("keyword_analysis", {})
                logger.info(f"🔍 Keyword analysis keys: {list(keyword_analysis.keys())}")
                
            else:
                logger.error("❌ No onboarding data returned")
                
        except Exception as e:
            logger.error(f"❌ Onboarding service error: {str(e)}")
        
        # Test 2: Comprehensive User Data Processor
        logger.info("\n📋 Test 2: Comprehensive User Data Processor")
        try:
            from services.calendar_generation_datasource_framework.data_processing.comprehensive_user_data import ComprehensiveUserDataProcessor
            
            processor = ComprehensiveUserDataProcessor()
            comprehensive_data = await processor.get_comprehensive_user_data(1, 1)
            
            logger.info(f"📊 Comprehensive data keys: {list(comprehensive_data.keys()) if comprehensive_data else 'None'}")
            
            if comprehensive_data:
                # Check onboarding data
                onboarding_data = comprehensive_data.get("onboarding_data", {})
                logger.info(f"👤 Onboarding data keys: {list(onboarding_data.keys())}")
                
                # Check for posting preferences (Step 4 requirement)
                posting_prefs = onboarding_data.get("posting_preferences")
                posting_days = onboarding_data.get("posting_days")
                optimal_times = onboarding_data.get("optimal_times")
                
                logger.info(f"📅 Posting preferences: {posting_prefs}")
                logger.info(f"📅 Posting days: {posting_days}")
                logger.info(f"📅 Optimal times: {optimal_times}")
                
                # Check strategy data
                strategy_data = comprehensive_data.get("strategy_data", {})
                logger.info(f"🎯 Strategy data keys: {list(strategy_data.keys())}")
                
                # Check gap analysis
                gap_analysis = comprehensive_data.get("gap_analysis", {})
                logger.info(f"📊 Gap analysis keys: {list(gap_analysis.keys())}")
                
            else:
                logger.error("❌ No comprehensive data returned")
                
        except Exception as e:
            logger.error(f"❌ Comprehensive data processor error: {str(e)}")
        
        # Test 3: Database Connection
        logger.info("\n📋 Test 3: Database Connection")
        try:
            from services.database import get_db_session
            from models.onboarding import OnboardingSession, WebsiteAnalysis
            
            session = get_db_session()
            
            # Check for onboarding sessions
            onboarding_sessions = session.query(OnboardingSession).all()
            logger.info(f"📊 Found {len(onboarding_sessions)} onboarding sessions")
            
            if onboarding_sessions:
                for i, session_data in enumerate(onboarding_sessions):
                    logger.info(f"   Session {i+1}: user_id={session_data.user_id}, created={session_data.created_at}")
                    
                    # Check for website analysis
                    website_analyses = session.query(WebsiteAnalysis).filter(
                        WebsiteAnalysis.session_id == session_data.id
                    ).all()
                    logger.info(f"   Website analyses: {len(website_analyses)}")
                    
            else:
                logger.warning("⚠️ No onboarding sessions found in database")
                
        except Exception as e:
            logger.error(f"❌ Database connection error: {str(e)}")
        
        # Test 4: Step 4 Direct Test
        logger.info("\n📋 Test 4: Step 4 Direct Test")
        try:
            from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase2.step4_implementation import CalendarFrameworkStep
            
            step4 = CalendarFrameworkStep()
            
            # Create mock context
            context = {
                "user_id": 1,
                "strategy_id": 1,
                "calendar_type": "monthly",
                "industry": "technology",
                "business_size": "sme"
            }
            
            # Try to execute Step 4
            logger.info("🔄 Executing Step 4...")
            result = await step4.execute(context)
            
            logger.info(f"✅ Step 4 executed successfully")
            logger.info(f"📊 Result keys: {list(result.keys()) if result else 'None'}")
            
        except Exception as e:
            logger.error(f"❌ Step 4 execution error: {str(e)}")
            import traceback
            logger.error(f"📋 Traceback: {traceback.format_exc()}")
        
        logger.info("\n🎯 Step 4 Data Debug Complete")
        
    except Exception as e:
        logger.error(f"❌ Error in data debug test: {str(e)}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    
    # Run the test
    asyncio.run(test_step4_data_sources())
