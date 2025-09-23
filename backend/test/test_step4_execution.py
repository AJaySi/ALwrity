#!/usr/bin/env python3
"""
Test script for Step 4 execution
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_step4_execution():
    """Test Step 4 execution directly."""
    
    print("🧪 Testing Step 4: Calendar Framework & Timeline Execution")
    
    try:
        # Import Step 4
        from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase2.step4_implementation import CalendarFrameworkStep
        
        # Create test context
        context = {
            "user_id": 1,
            "strategy_id": 1,
            "calendar_type": "monthly",
            "industry": "technology",
            "business_size": "sme",
            "step_results": {},
            "quality_scores": {}
        }
        
        # Create Step 4 instance
        step4 = CalendarFrameworkStep()
        print("✅ Step 4 instance created successfully")
        
        # Test Step 4 execution
        print("🔄 Executing Step 4...")
        result = await step4.run(context)
        
        if result:
            print("✅ Step 4 executed successfully!")
            print(f"Status: {result.get('status')}")
            print(f"Quality Score: {result.get('quality_score')}")
            print(f"Execution Time: {result.get('execution_time')}")
            
            if result.get('status') == 'error':
                print(f"❌ Step 4 Error: {result.get('error_message')}")
            else:
                print("📊 Step 4 Results:")
                print(f"  - Calendar Structure: {result.get('calendar_structure', {}).get('type')}")
                print(f"  - Timeline Config: {result.get('timeline_config', {}).get('total_weeks')} weeks")
                print(f"  - Duration Control: {result.get('duration_control', {}).get('validation_passed')}")
        else:
            print("❌ Step 4 returned None")
            
    except Exception as e:
        print(f"❌ Error testing Step 4 execution: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_step4_execution())
