#!/usr/bin/env python3
"""
Test script for calendar generation API
"""

import asyncio
import aiohttp
import json

async def test_calendar_generation():
    """Test the calendar generation API."""
    
    url = "http://localhost:8000/api/content-planning/calendar-generation/start"
    
    payload = {
        "user_id": 1,
        "strategy_id": 1,
        "calendar_type": "monthly",
        "industry": "technology",
        "business_size": "sme"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Calendar generation started successfully!")
                    print(f"Session ID: {result.get('session_id')}")
                    
                    # Test progress endpoint
                    session_id = result.get('session_id')
                    if session_id:
                        print(f"\n🔄 Testing progress for session: {session_id}")
                        progress_url = f"http://localhost:8000/api/content-planning/calendar-generation/progress/{session_id}"
                        
                        async with session.get(progress_url) as progress_response:
                            if progress_response.status == 200:
                                progress_data = await progress_response.json()
                                print("✅ Progress endpoint working!")
                                print(f"Status: {progress_data.get('status')}")
                                print(f"Current Step: {progress_data.get('current_step')}")
                                print(f"Overall Progress: {progress_data.get('overall_progress')}%")
                                
                                # Check for Step 4 specifically
                                step_results = progress_data.get('step_results', {})
                                if 'step_04' in step_results:
                                    step4_result = step_results['step_04']
                                    print(f"\n📊 Step 4 Status: {step4_result.get('status')}")
                                    print(f"Step 4 Quality: {step4_result.get('quality_score')}")
                                    if step4_result.get('status') == 'error':
                                        print(f"Step 4 Error: {step4_result.get('error_message')}")
                                else:
                                    print("⚠️ Step 4 results not yet available")
                            else:
                                print(f"❌ Progress endpoint failed: {progress_response.status}")
                else:
                    print(f"❌ Calendar generation failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    
        except Exception as e:
            print(f"❌ Error testing calendar generation: {e}")

if __name__ == "__main__":
    asyncio.run(test_calendar_generation())
