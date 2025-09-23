#!/usr/bin/env python3
"""
Step 8 Debug Script - Isolated Testing
=====================================

This script tests Step 8 (Daily Content Planning) in isolation with controlled inputs
to identify which specific parameter is causing the 'float' object has no attribute 'get' error.

The script will:
1. Set up Step 8 with fixed, known dictionary inputs
2. Test the daily content generation in isolation
3. Identify which specific parameter is coming through as a float
4. Help pinpoint whether the issue is in weekly_theme, posting_day, platform_strategies, or other data
"""

import asyncio
import sys
import os
import logging
from typing import Dict, List, Any

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import Step 8 components
from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase3.step8_daily_content_planning.step8_main import DailyContentPlanningStep
from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase3.step8_daily_content_planning.daily_schedule_generator import DailyScheduleGenerator

def create_controlled_test_data():
    """Create controlled test data with known types for Step 8 testing."""
    
    # 1. Weekly themes from Step 7 (should be list of dictionaries)
    weekly_themes = [
        {
            "title": "Week 1 Theme: AI Implementation Guide",
            "description": "Comprehensive guide on AI implementation for businesses",
            "primary_pillar": "AI and Machine Learning",
            "secondary_pillars": ["Digital Transformation", "Innovation"],
            "strategic_alignment": "high",
            "audience_alignment": "high",
            "week_number": 1,
            "content_count": 5,
            "priority": "high",
            "estimated_impact": "High",
            "ai_confidence": 0.9
        },
        {
            "title": "Week 2 Theme: Digital Transformation Strategies",
            "description": "Strategic approaches to digital transformation",
            "primary_pillar": "Digital Transformation",
            "secondary_pillars": ["Business Strategy", "Innovation"],
            "strategic_alignment": "high",
            "audience_alignment": "medium",
            "week_number": 2,
            "content_count": 4,
            "priority": "medium",
            "estimated_impact": "Medium",
            "ai_confidence": 0.8
        }
    ]
    
    # 2. Platform strategies from Step 6 (should be dictionary)
    platform_strategies = {
        "linkedin": {
            "content_types": ["articles", "posts", "videos"],
            "posting_times": ["09:00", "12:00", "15:00"],
            "content_adaptation": "professional tone, industry insights",
            "engagement_strategy": "thought leadership content"
        },
        "twitter": {
            "content_types": ["tweets", "threads", "images"],
            "posting_times": ["08:00", "11:00", "14:00", "17:00"],
            "content_adaptation": "concise, engaging, hashtag optimization",
            "engagement_strategy": "conversation starters"
        }
    }
    
    # 3. Content pillars from Step 5 (should be list)
    content_pillars = [
        "AI and Machine Learning",
        "Digital Transformation", 
        "Innovation and Technology Trends",
        "Business Strategy and Growth"
    ]
    
    # 4. Calendar framework from Step 4 (should be dictionary)
    calendar_framework = {
        "duration_weeks": 4,
        "content_frequency": "daily",
        "posting_schedule": {
            "monday": ["09:00", "12:00", "15:00"],
            "tuesday": ["09:00", "12:00", "15:00"],
            "wednesday": ["09:00", "12:00", "15:00"],
            "thursday": ["09:00", "12:00", "15:00"],
            "friday": ["09:00", "12:00", "15:00"]
        },
        "theme_structure": "weekly_themes",
        "content_mix": {
            "blog_posts": 0.4,
            "social_media": 0.3,
            "videos": 0.2,
            "infographics": 0.1
        }
    }
    
    # 5. Business goals from Step 1 (should be list)
    business_goals = [
        "Increase brand awareness by 40%",
        "Generate 500 qualified leads per month",
        "Establish thought leadership"
    ]
    
    # 6. Target audience from Step 1 (should be dictionary)
    target_audience = {
        "primary": "Tech professionals",
        "secondary": "Business leaders",
        "demographics": {
            "age_range": "25-45",
            "location": "Global",
            "interests": ["technology", "innovation", "business growth"]
        }
    }
    
    # 7. Keywords from Step 2 (should be list)
    keywords = [
        "AI implementation",
        "digital transformation",
        "machine learning",
        "business automation",
        "technology trends"
    ]
    
    return {
        "weekly_themes": weekly_themes,
        "platform_strategies": platform_strategies,
        "content_pillars": content_pillars,
        "calendar_framework": calendar_framework,
        "business_goals": business_goals,
        "target_audience": target_audience,
        "keywords": keywords
    }

def validate_data_types(data: Dict[str, Any], test_name: str):
    """Validate that all data has the expected types."""
    logger.info(f"🔍 Validating data types for {test_name}")
    
    expected_types = {
        "weekly_themes": list,
        "platform_strategies": dict,
        "content_pillars": list,
        "calendar_framework": dict,
        "business_goals": list,
        "target_audience": dict,
        "keywords": list
    }
    
    for key, expected_type in expected_types.items():
        if key in data:
            actual_type = type(data[key])
            if actual_type != expected_type:
                logger.error(f"❌ Type mismatch for {key}: expected {expected_type.__name__}, got {actual_type.__name__}")
                logger.error(f"   Value: {data[key]}")
                return False
            else:
                logger.info(f"✅ {key}: {actual_type.__name__} (correct)")
        else:
            logger.warning(f"⚠️  Missing key: {key}")
    
    return True

async def test_daily_schedule_generator_isolated():
    """Test the DailyScheduleGenerator in isolation with controlled inputs."""
    logger.info("🧪 Testing DailyScheduleGenerator in isolation")
    
    # Create controlled test data
    test_data = create_controlled_test_data()
    
    # Validate data types
    if not validate_data_types(test_data, "DailyScheduleGenerator"):
        logger.error("❌ Data type validation failed")
        return False
    
    try:
        # Create DailyScheduleGenerator instance
        generator = DailyScheduleGenerator()
        
        # Test the generate_daily_schedules method
        logger.info("📅 Testing generate_daily_schedules method")
        
        # Get posting preferences and calendar duration
        posting_preferences = {
            "preferred_times": ["09:00", "12:00", "15:00"],
            "posting_frequency": "daily"
        }
        calendar_duration = test_data["calendar_framework"]["duration_weeks"] * 7
        
        # Call the method with controlled inputs
        daily_schedules = await generator.generate_daily_schedules(
            test_data["weekly_themes"],
            test_data["platform_strategies"],
            test_data["content_pillars"],
            test_data["calendar_framework"],
            posting_preferences,
            calendar_duration
        )
        
        logger.info(f"✅ DailyScheduleGenerator test successful")
        logger.info(f"   Generated {len(daily_schedules)} daily schedules")
        
        # Validate the output
        if isinstance(daily_schedules, list):
            logger.info("✅ Output is a list (correct)")
            for i, schedule in enumerate(daily_schedules[:3]):  # Show first 3
                logger.info(f"   Schedule {i+1}: {type(schedule)} - {schedule.get('day_number', 'N/A')}")
        else:
            logger.error(f"❌ Output is not a list: {type(daily_schedules)}")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"❌ DailyScheduleGenerator test failed: {str(e)}")
        logger.error(f"   Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"   Traceback: {traceback.format_exc()}")
        return False

async def test_step8_execute_method():
    """Test Step 8's execute method with controlled inputs."""
    logger.info("🧪 Testing Step 8 execute method")
    
    # Create controlled test data
    test_data = create_controlled_test_data()
    
    # Validate data types
    if not validate_data_types(test_data, "Step 8 Execute"):
        logger.error("❌ Data type validation failed")
        return False
    
    try:
        # Create Step 8 instance
        step8 = DailyContentPlanningStep()
        
        # Create context with controlled data
        context = {
            "step_results": {
                "step_07": {
                    "result": {
                        "weekly_themes": test_data["weekly_themes"]
                    }
                },
                "step_06": {
                    "result": {
                        "platform_strategies": test_data["platform_strategies"]
                    }
                },
                "step_05": {
                    "result": {
                        "content_pillars": test_data["content_pillars"]
                    }
                },
                "step_04": {
                    "result": {
                        "calendar_framework": test_data["calendar_framework"]
                    }
                },
                "step_01": {
                    "result": {
                        "business_goals": test_data["business_goals"],
                        "target_audience": test_data["target_audience"]
                    }
                },
                "step_02": {
                    "result": {
                        "keywords": test_data["keywords"]
                    }
                }
            },
            "user_data": {
                "business_goals": test_data["business_goals"],
                "target_audience": test_data["target_audience"],
                "keywords": test_data["keywords"]
            }
        }
        
        # Test the execute method
        logger.info("📅 Testing Step 8 execute method")
        result = await step8.execute(context)
        
        logger.info(f"✅ Step 8 execute test successful")
        logger.info(f"   Result type: {type(result)}")
        logger.info(f"   Result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Step 8 execute test failed: {str(e)}")
        logger.error(f"   Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"   Traceback: {traceback.format_exc()}")
        return False

async def test_specific_methods_with_debugging():
    """Test specific methods with detailed debugging to identify the float issue."""
    logger.info("🔍 Testing specific methods with detailed debugging")
    
    # Create controlled test data
    test_data = create_controlled_test_data()
    
    try:
        # Create DailyScheduleGenerator instance
        generator = DailyScheduleGenerator()
        
        # Test _get_weekly_theme method specifically
        logger.info("🔍 Testing _get_weekly_theme method")
        for week_num in [1, 2]:
            theme = generator._get_weekly_theme(test_data["weekly_themes"], week_num)
            logger.info(f"   Week {week_num} theme type: {type(theme)}")
            logger.info(f"   Week {week_num} theme: {theme}")
            
            if not isinstance(theme, dict):
                logger.error(f"❌ Week {week_num} theme is not a dictionary!")
                return False
        
        # Test _generate_daily_content method with controlled inputs
        logger.info("🔍 Testing _generate_daily_content method")
        
        # Create a controlled posting_day
        posting_day = {
            "day_number": 1,
            "week_number": 1,
            "content_count": 3,
            "platforms": ["linkedin", "twitter"]
        }
        
        # Test with controlled weekly theme
        weekly_theme = test_data["weekly_themes"][0]  # First theme
        
        # Test the method
        content = await generator._generate_daily_content(
            posting_day,
            weekly_theme,
            test_data["platform_strategies"],
            test_data["content_pillars"],
            test_data["calendar_framework"]
        )
        
        logger.info(f"✅ _generate_daily_content test successful")
        logger.info(f"   Content type: {type(content)}")
        logger.info(f"   Content: {content}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Specific method test failed: {str(e)}")
        logger.error(f"   Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"   Traceback: {traceback.format_exc()}")
        return False

async def main():
    """Main debug function."""
    logger.info("🚀 Starting Step 8 Debug Script")
    logger.info("=" * 50)
    
    # Test 1: DailyScheduleGenerator in isolation
    logger.info("\n🧪 Test 1: DailyScheduleGenerator in isolation")
    success1 = await test_daily_schedule_generator_isolated()
    
    # Test 2: Step 8 execute method
    logger.info("\n🧪 Test 2: Step 8 execute method")
    success2 = await test_step8_execute_method()
    
    # Test 3: Specific methods with debugging
    logger.info("\n🧪 Test 3: Specific methods with debugging")
    success3 = await test_specific_methods_with_debugging()
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 Debug Results Summary")
    logger.info("=" * 50)
    logger.info(f"✅ Test 1 (DailyScheduleGenerator): {'PASSED' if success1 else 'FAILED'}")
    logger.info(f"✅ Test 2 (Step 8 Execute): {'PASSED' if success2 else 'FAILED'}")
    logger.info(f"✅ Test 3 (Specific Methods): {'PASSED' if success3 else 'FAILED'}")
    
    if success1 and success2 and success3:
        logger.info("🎉 All tests passed! Step 8 is working correctly with controlled inputs.")
        logger.info("💡 The issue might be in the data flow from previous steps.")
    else:
        logger.error("❌ Some tests failed. Check the logs above for specific issues.")
    
    logger.info("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
