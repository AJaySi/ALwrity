#!/usr/bin/env python3
"""
Test script to verify the calendar generation progress endpoint.
This script tests the progress endpoint to ensure it returns the correct data structure.
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_progress_endpoint():
    """Test the progress endpoint with a mock session."""
    try:
        from api.content_planning.services.calendar_generation_service import CalendarGenerationService
        
        print("🧪 Testing Progress Endpoint")
        print("=" * 50)
        
        # Initialize service
        service = CalendarGenerationService()
        
        # Create a test session
        session_id = f"test-session-{int(datetime.now().timestamp())}"
        test_request_data = {
            "user_id": 1,
            "strategy_id": 1,
            "calendar_type": "monthly",
            "industry": "technology",
            "business_size": "sme"
        }
        
        print(f"📋 Creating test session: {session_id}")
        
        # Initialize session
        success = service.initialize_orchestrator_session(session_id, test_request_data)
        if not success:
            print("❌ Failed to initialize session")
            return False
        
        print("✅ Session initialized successfully")
        
        # Test progress retrieval
        print(f"🔍 Testing progress retrieval for session: {session_id}")
        progress = service.get_orchestrator_progress(session_id)
        
        if not progress:
            print("❌ No progress data returned")
            return False
        
        print("✅ Progress data retrieved successfully")
        print(f"📊 Progress data structure:")
        print(json.dumps(progress, indent=2, default=str))
        
        # Verify required fields
        required_fields = [
            "status", "current_step", "step_progress", "overall_progress",
            "step_results", "quality_scores", "errors", "warnings"
        ]
        
        missing_fields = [field for field in required_fields if field not in progress]
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        print("✅ All required fields present")
        
        # Test data types
        if not isinstance(progress["current_step"], int):
            print("❌ current_step should be int")
            return False
        
        if not isinstance(progress["step_progress"], (int, float)):
            print("❌ step_progress should be numeric")
            return False
        
        if not isinstance(progress["overall_progress"], (int, float)):
            print("❌ overall_progress should be numeric")
            return False
        
        print("✅ All data types correct")
        
        # Test quality scores
        quality_scores = progress["quality_scores"]
        if not isinstance(quality_scores, dict):
            print("❌ quality_scores should be dict")
            return False
        
        print("✅ Quality scores structure correct")
        
        print("\n🎉 All tests passed! Progress endpoint is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_progress_endpoint()
    sys.exit(0 if success else 1)
