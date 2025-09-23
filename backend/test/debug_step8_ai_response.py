#!/usr/bin/env python3
"""
Debug script to test AI response parsing in Step 8.
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

async def debug_ai_response_parsing():
    """Debug AI response parsing in Step 8."""
    
    logger.info("🔍 Starting AI Response Parsing Debug")
    
    # Create test data
    test_posting_day = {
        "day_number": 1,
        "date": "2025-09-01",
        "day_name": "monday",
        "posting_times": ["09:00", "12:00"],
        "content_count": 2,
        "week_number": 1
    }
    
    test_weekly_theme = {
        "title": "Week 1 Theme: AI Implementation",
        "description": "Focus on AI tools and implementation",
        "content_angles": ["AI tools", "Implementation guide", "Best practices"]
    }
    
    test_platform_strategies = {
        "LinkedIn": {"approach": "professional"},
        "Blog": {"approach": "educational"}
    }
    
    # Test different AI response formats
    test_responses = [
        # Format 1: List of recommendations (correct format)
        [
            {
                "type": "Content Creation Opportunity",
                "title": "AI Implementation Guide",
                "description": "A comprehensive guide to AI implementation"
            },
            {
                "type": "Content Creation Opportunity", 
                "title": "AI Tools Overview",
                "description": "Overview of AI tools for business"
            }
        ],
        
        # Format 2: Dictionary with recommendations key
        {
            "recommendations": [
                {
                    "type": "Content Creation Opportunity",
                    "title": "AI Implementation Guide",
                    "description": "A comprehensive guide to AI implementation"
                },
                {
                    "type": "Content Creation Opportunity",
                    "title": "AI Tools Overview", 
                    "description": "Overview of AI tools for business"
                }
            ]
        },
        
        # Format 3: Float (the problematic case)
        0.95,
        
        # Format 4: String
        "AI Implementation Guide",
        
        # Format 5: None
        None
    ]
    
    generator = DailyScheduleGenerator()
    
    for i, test_response in enumerate(test_responses):
        logger.info(f"🔍 Testing AI response format {i+1}: {type(test_response)} = {test_response}")
        
        try:
            content_pieces = generator._parse_content_response(
                ai_response=test_response,
                posting_day=test_posting_day,
                weekly_theme=test_weekly_theme,
                platform_strategies=test_platform_strategies
            )
            
            logger.info(f"✅ Format {i+1} parsed successfully: {len(content_pieces)} content pieces")
            for j, piece in enumerate(content_pieces):
                logger.info(f"  Piece {j+1}: {piece.get('title', 'No title')}")
                
        except Exception as e:
            logger.error(f"❌ Format {i+1} failed: {str(e)}")
            logger.error(f"📋 Error type: {type(e)}")
            import traceback
            logger.error(f"📋 Traceback: {traceback.format_exc()}")
    
    logger.info("🎉 AI Response Parsing Debug completed!")

if __name__ == "__main__":
    asyncio.run(debug_ai_response_parsing())
