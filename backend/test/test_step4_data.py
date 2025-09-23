#!/usr/bin/env python3
"""
Test script for Step 4 data
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_step4_data():
    """Test Step 4 data processing."""
    
    print("🧪 Testing Step 4: Calendar Framework & Timeline Data")
    
    try:
        # Test comprehensive user data
        from services.calendar_generation_datasource_framework.data_processing.comprehensive_user_data import ComprehensiveUserDataProcessor
        
        processor = ComprehensiveUserDataProcessor()
        data = await processor.get_comprehensive_user_data(1, 1)
        
        print("✅ Comprehensive user data retrieved successfully")
        print(f"📊 Data keys: {list(data.keys())}")
        
        onboarding_data = data.get('onboarding_data', {})
        print(f"📋 Onboarding data keys: {list(onboarding_data.keys())}")
        
        posting_preferences = onboarding_data.get('posting_preferences')
        posting_days = onboarding_data.get('posting_days')
        optimal_times = onboarding_data.get('optimal_times')
        
        print(f"📅 Posting preferences: {posting_preferences}")
        print(f"📅 Posting days: {posting_days}")
        print(f"⏰ Optimal times: {optimal_times}")
        
        if posting_preferences and posting_days:
            print("✅ Step 4 data requirements met!")
        else:
            print("❌ Step 4 data requirements NOT met!")
            
    except Exception as e:
        print(f"❌ Error testing Step 4 data: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_step4_data())
