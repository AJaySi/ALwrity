#!/usr/bin/env python3
"""
Test script to verify session management and duplicate prevention.
This script tests the session cleanup and duplicate prevention features.
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_session_management():
    """Test session management features."""
    try:
        from api.content_planning.services.calendar_generation_service import CalendarGenerationService
        
        print("🧪 Testing Session Management")
        print("=" * 50)
        
        # Initialize service
        service = CalendarGenerationService(None)  # No DB needed for this test
        
        # Test 1: Initialize first session
        print("\n📋 Test 1: Initialize first session")
        request_data_1 = {
            "user_id": 1,
            "strategy_id": 1,
            "calendar_type": "monthly",
            "industry": "technology",
            "business_size": "sme"
        }
        
        session_id_1 = f"test-session-{int(datetime.now().timestamp())}-1000"
        success_1 = service.initialize_orchestrator_session(session_id_1, request_data_1)
        print(f"✅ First session initialized: {success_1}")
        print(f"📊 Available sessions: {list(service.orchestrator_sessions.keys())}")
        
        # Test 2: Try to initialize second session for same user (should fail)
        print("\n📋 Test 2: Try to initialize second session for same user")
        session_id_2 = f"test-session-{int(datetime.now().timestamp())}-2000"
        success_2 = service.initialize_orchestrator_session(session_id_2, request_data_1)
        print(f"❌ Second session should fail: {success_2}")
        print(f"📊 Available sessions: {list(service.orchestrator_sessions.keys())}")
        
        # Test 3: Check active session for user
        print("\n📋 Test 3: Check active session for user")
        active_session = service._get_active_session_for_user(1)
        print(f"✅ Active session for user 1: {active_session}")
        
        # Test 4: Initialize session for different user (should succeed)
        print("\n📋 Test 4: Initialize session for different user")
        request_data_2 = {
            "user_id": 2,
            "strategy_id": 2,
            "calendar_type": "weekly",
            "industry": "finance",
            "business_size": "enterprise"
        }
        
        session_id_3 = f"test-session-{int(datetime.now().timestamp())}-3000"
        success_3 = service.initialize_orchestrator_session(session_id_3, request_data_2)
        print(f"✅ Third session for different user: {success_3}")
        print(f"📊 Available sessions: {list(service.orchestrator_sessions.keys())}")
        
        # Test 5: Test session cleanup
        print("\n📋 Test 5: Test session cleanup")
        print(f"📊 Sessions before cleanup: {len(service.orchestrator_sessions)}")
        service._cleanup_old_sessions(1)
        print(f"📊 Sessions after cleanup: {len(service.orchestrator_sessions)}")
        
        print("\n🎉 Session management tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_session_management()
