#!/usr/bin/env python3
"""
Debug script for Step 8 (Daily Content Planning) to isolate data type issues.
"""

import asyncio
import logging
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase3.step8_daily_content_planning.daily_schedule_generator import DailyScheduleGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

async def debug_step8():
    """Debug Step 8 with controlled test data."""
    
    logger.info("🔍 Starting Step 8 Debug Session")
    
    # Create test data with known types
    test_weekly_themes = [
        {
            "title": "Week 1 Theme: AI Implementation",
            "description": "Focus on AI tools and implementation",
            "primary_pillar": "AI and Machine Learning",
            "content_angles": ["AI tools", "Implementation guide", "Best practices"],
            "target_platforms": ["LinkedIn", "Blog", "Twitter"],
            "strategic_alignment": "High alignment with business goals",
            "gap_addressal": "Addresses AI implementation gap",
            "priority": "high",
            "estimated_impact": "High",
            "ai_confidence": 0.9,
            "week_number": 1
        },
        {
            "title": "Week 2 Theme: Digital Transformation",
            "description": "Digital transformation strategies",
            "primary_pillar": "Digital Transformation", 
            "content_angles": ["Strategy", "Case studies", "ROI"],
            "target_platforms": ["LinkedIn", "Blog", "YouTube"],
            "strategic_alignment": "Medium alignment with business goals",
            "gap_addressal": "Addresses transformation gap",
            "priority": "medium",
            "estimated_impact": "Medium",
            "ai_confidence": 0.8,
            "week_number": 2
        }
    ]
    
    test_platform_strategies = {
        "LinkedIn": {
            "content_type": "professional",
            "posting_frequency": "daily",
            "engagement_strategy": "thought_leadership"
        },
        "Blog": {
            "content_type": "educational",
            "posting_frequency": "weekly",
            "engagement_strategy": "seo_optimized"
        },
        "Twitter": {
            "content_type": "conversational",
            "posting_frequency": "daily",
            "engagement_strategy": "community_building"
        }
    }
    
    test_content_pillars = [
        {
            "name": "AI and Machine Learning",
            "weight": 0.4,
            "description": "AI tools and implementation"
        },
        {
            "name": "Digital Transformation", 
            "weight": 0.3,
            "description": "Digital strategy and transformation"
        },
        {
            "name": "Business Strategy",
            "weight": 0.3,
            "description": "Strategic business insights"
        }
    ]
    
    test_calendar_framework = {
        "type": "monthly",
        "total_weeks": 4,
        "posting_frequency": "daily",
        "posting_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "industry": "technology",
        "business_size": "sme"
    }
    
    test_posting_preferences = {
        "preferred_times": ["09:00", "12:00", "15:00"],
        "posting_frequency": "daily",
        "content_count_per_day": 2
    }
    
    test_business_goals = [
        "Increase brand awareness by 40%",
        "Generate 500 qualified leads per month", 
        "Establish thought leadership"
    ]
    
    test_target_audience = {
        "primary": "Tech professionals",
        "secondary": "Business leaders",
        "demographics": {
            "age_range": "25-45",
            "location": "Global"
        }
    }
    
    # Test data type validation
    logger.info("🔍 Validating test data types:")
    logger.info(f"  weekly_themes: {type(test_weekly_themes)} (length: {len(test_weekly_themes)})")
    logger.info(f"  platform_strategies: {type(test_platform_strategies)}")
    logger.info(f"  content_pillars: {type(test_content_pillars)}")
    logger.info(f"  calendar_framework: {type(test_calendar_framework)}")
    logger.info(f"  posting_preferences: {type(test_posting_preferences)}")
    logger.info(f"  business_goals: {type(test_business_goals)}")
    logger.info(f"  target_audience: {type(test_target_audience)}")
    
    # Validate weekly themes structure
    for i, theme in enumerate(test_weekly_themes):
        logger.info(f"  Theme {i+1}: {type(theme)} - keys: {list(theme.keys())}")
        if not isinstance(theme, dict):
            logger.error(f"❌ Theme {i+1} is not a dictionary: {type(theme)}")
            return
    
    try:
        # Initialize the daily schedule generator
        generator = DailyScheduleGenerator()
        logger.info("✅ DailyScheduleGenerator initialized successfully")
        
        # Test the generate_daily_schedules method
        logger.info("🚀 Testing generate_daily_schedules method...")
        
        daily_schedules = await generator.generate_daily_schedules(
            weekly_themes=test_weekly_themes,
            platform_strategies=test_platform_strategies,
            business_goals=test_business_goals,
            target_audience=test_target_audience,
            posting_preferences=test_posting_preferences,
            calendar_duration=28  # 4 weeks * 7 days
        )
        
        logger.info(f"✅ Successfully generated {len(daily_schedules)} daily schedules")
        
        # Log first few schedules for inspection
        for i, schedule in enumerate(daily_schedules[:3]):
            logger.info(f"  Schedule {i+1}: {type(schedule)} - keys: {list(schedule.keys())}")
            
    except Exception as e:
        logger.error(f"❌ Error in Step 8 debug: {str(e)}")
        logger.error(f"📋 Error type: {type(e)}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return
    
    logger.info("🎉 Step 8 debug completed successfully!")

if __name__ == "__main__":
    asyncio.run(debug_step8())
