#!/usr/bin/env python3
"""
Test script for Step 2 specifically
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase2.step2_implementation import Step2Implementation

async def test_step2():
    """Test Step 2 implementation."""
    
    print("🧪 Testing Step 2: Gap Analysis & Opportunity Identification")
    
    # Create test context
    context = {
        "user_id": 1,
        "strategy_id": 1,
        "calendar_type": "monthly",
        "industry": "technology",
        "business_size": "sme",
        "user_data": {
            "onboarding_data": {
                "posting_preferences": {
                    "daily": 2,
                    "weekly": 10,
                    "monthly": 40
                },
                "posting_days": [
                    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
                ],
                "optimal_times": [
                    "09:00", "12:00", "15:00", "18:00", "20:00"
                ]
            },
            "strategy_data": {
                "industry": "technology",
                "target_audience": {
                    "primary": "Tech professionals",
                    "secondary": "Business leaders"
                },
                "business_objectives": [
                    "Increase brand awareness",
                    "Generate leads",
                    "Establish thought leadership"
                ]
            }
        },
        "step_results": {},
        "quality_scores": {}
    }
    
    try:
        # Create Step 2 instance
        step2 = Step2Implementation()
        
        print("✅ Step 2 instance created successfully")
        
        # Test Step 2 execution
        print("🔄 Executing Step 2...")
        result = await step2.run(context)
        
        if result:
            print("✅ Step 2 executed successfully!")
            print(f"Status: {result.get('status')}")
            print(f"Quality Score: {result.get('quality_score')}")
            print(f"Execution Time: {result.get('execution_time')}")
            
            if result.get('status') == 'error':
                print(f"❌ Step 2 Error: {result.get('error_message')}")
        else:
            print("❌ Step 2 returned None")
            
    except Exception as e:
        print(f"❌ Error testing Step 2: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_step2())
