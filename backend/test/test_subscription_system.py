"""
Test Script for Subscription System
Tests the core functionality of the usage-based subscription system.
"""

import sys
import os
from pathlib import Path
import asyncio
import json

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import sessionmaker
from loguru import logger

from services.database import engine
from services.pricing_service import PricingService
from services.usage_tracking_service import UsageTrackingService
from models.subscription_models import APIProvider, SubscriptionTier

async def test_pricing_service():
    """Test the pricing service functionality."""
    
    logger.info("🧪 Testing Pricing Service...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        pricing_service = PricingService(db)
        
        # Test cost calculation
        cost_data = pricing_service.calculate_api_cost(
            provider=APIProvider.GEMINI,
            model_name="gemini-2.5-flash",
            tokens_input=1000,
            tokens_output=500,
            request_count=1
        )
        
        logger.info(f"✅ Cost calculation: {cost_data}")
        
        # Test user limits
        limits = pricing_service.get_user_limits("test_user")
        logger.info(f"✅ User limits: {limits}")
        
        # Test usage limit checking
        can_proceed, message, usage_info = pricing_service.check_usage_limits(
            user_id="test_user",
            provider=APIProvider.GEMINI,
            tokens_requested=100
        )
        
        logger.info(f"✅ Usage check: {can_proceed} - {message}")
        logger.info(f"   Usage info: {usage_info}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Pricing service test failed: {e}")
        return False
    finally:
        db.close()

async def test_usage_tracking():
    """Test the usage tracking service."""
    
    logger.info("🧪 Testing Usage Tracking Service...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        usage_service = UsageTrackingService(db)
        
        # Test tracking an API usage
        result = await usage_service.track_api_usage(
            user_id="test_user",
            provider=APIProvider.GEMINI,
            endpoint="/api/generate",
            method="POST",
            model_used="gemini-2.5-flash",
            tokens_input=500,
            tokens_output=300,
            response_time=1.5,
            status_code=200
        )
        
        logger.info(f"✅ Usage tracking result: {result}")
        
        # Test getting usage stats
        stats = usage_service.get_user_usage_stats("test_user")
        logger.info(f"✅ Usage stats: {json.dumps(stats, indent=2)}")
        
        # Test usage trends
        trends = usage_service.get_usage_trends("test_user", 3)
        logger.info(f"✅ Usage trends: {json.dumps(trends, indent=2)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Usage tracking test failed: {e}")
        return False
    finally:
        db.close()

async def test_limit_enforcement():
    """Test usage limit enforcement."""
    
    logger.info("🧪 Testing Limit Enforcement...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        usage_service = UsageTrackingService(db)
        
        # Test multiple API calls to approach limits
        for i in range(5):
            result = await usage_service.track_api_usage(
                user_id="test_user_limits",
                provider=APIProvider.GEMINI,
                endpoint="/api/generate",
                method="POST",
                model_used="gemini-2.5-flash",
                tokens_input=1000,
                tokens_output=800,
                response_time=2.0,
                status_code=200
            )
            logger.info(f"Call {i+1}: {result}")
        
        # Check if limits are being enforced
        can_proceed, message, usage_info = await usage_service.enforce_usage_limits(
            user_id="test_user_limits",
            provider=APIProvider.GEMINI,
            tokens_requested=5000
        )
        
        logger.info(f"✅ Limit enforcement: {can_proceed} - {message}")
        logger.info(f"   Usage info: {usage_info}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Limit enforcement test failed: {e}")
        return False
    finally:
        db.close()

def test_database_tables():
    """Test that all subscription tables exist."""
    
    logger.info("🧪 Testing Database Tables...")
    
    try:
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Check for subscription tables
            tables_query = text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND (
                    name LIKE '%subscription%' OR 
                    name LIKE '%usage%' OR 
                    name LIKE '%pricing%' OR
                    name LIKE '%billing%'
                )
                ORDER BY name
            """)
            
            result = conn.execute(tables_query)
            tables = result.fetchall()
            
            expected_tables = [
                'api_provider_pricing',
                'api_usage_logs', 
                'billing_history',
                'subscription_plans',
                'usage_alerts',
                'usage_summaries',
                'user_subscriptions'
            ]
            
            found_tables = [t[0] for t in tables]
            logger.info(f"Found tables: {found_tables}")
            
            missing_tables = [t for t in expected_tables if t not in found_tables]
            if missing_tables:
                logger.error(f"❌ Missing tables: {missing_tables}")
                return False
            
            # Check table data
            for table in ['subscription_plans', 'api_provider_pricing']:
                count_query = text(f"SELECT COUNT(*) FROM {table}")
                result = conn.execute(count_query)
                count = result.fetchone()[0]
                logger.info(f"✅ {table}: {count} records")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Database tables test failed: {e}")
        return False

async def run_comprehensive_test():
    """Run comprehensive test suite."""
    
    logger.info("🚀 Starting Subscription System Comprehensive Test")
    logger.info("="*60)
    
    test_results = {}
    
    # Test 1: Database Tables
    logger.info("\n1. Testing Database Tables...")
    test_results['database_tables'] = test_database_tables()
    
    # Test 2: Pricing Service
    logger.info("\n2. Testing Pricing Service...")
    test_results['pricing_service'] = await test_pricing_service()
    
    # Test 3: Usage Tracking
    logger.info("\n3. Testing Usage Tracking...")
    test_results['usage_tracking'] = await test_usage_tracking()
    
    # Test 4: Limit Enforcement
    logger.info("\n4. Testing Limit Enforcement...")
    test_results['limit_enforcement'] = await test_limit_enforcement()
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name.upper().replace('_', ' ')}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Subscription system is ready.")
        
        logger.info("\n" + "="*60)
        logger.info("NEXT STEPS:")
        logger.info("="*60)
        logger.info("1. Start the FastAPI server:")
        logger.info("   cd backend && python start_alwrity_backend.py")
        logger.info("\n2. Test the API endpoints:")
        logger.info("   GET http://localhost:8000/api/subscription/plans")
        logger.info("   GET http://localhost:8000/api/subscription/pricing")
        logger.info("   GET http://localhost:8000/api/subscription/usage/test_user")
        logger.info("\n3. Integrate with your frontend dashboard")
        logger.info("4. Set up user authentication/identification")
        logger.info("5. Configure payment processing (Stripe, etc.)")
        logger.info("="*60)
        
        return True
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    # Run the comprehensive test
    success = asyncio.run(run_comprehensive_test())
    
    if not success:
        sys.exit(1)
    
    logger.info("✅ Test completed successfully!")