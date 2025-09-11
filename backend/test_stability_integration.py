#!/usr/bin/env python3
"""Test script for Stability AI integration."""

import asyncio
import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv()

# Test imports
def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from models.stability_models import (
            StableImageUltraRequest, StableImageCoreRequest, StableSD3Request,
            OutputFormat, AspectRatio, StylePreset
        )
        print("✅ Stability models imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import stability models: {e}")
        return False
    
    try:
        from services.stability_service import StabilityAIService, get_stability_service
        print("✅ Stability service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import stability service: {e}")
        return False
    
    try:
        from routers.stability import router as stability_router
        from routers.stability_advanced import router as stability_advanced_router
        from routers.stability_admin import router as stability_admin_router
        print("✅ Stability routers imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import stability routers: {e}")
        return False
    
    try:
        from middleware.stability_middleware import (
            RateLimitMiddleware, MonitoringMiddleware, CachingMiddleware
        )
        print("✅ Stability middleware imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import stability middleware: {e}")
        return False
    
    try:
        from utils.stability_utils import (
            ImageValidator, AudioValidator, PromptOptimizer
        )
        print("✅ Stability utilities imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import stability utilities: {e}")
        return False
    
    try:
        from config.stability_config import (
            get_stability_config, MODEL_PRICING, IMAGE_LIMITS
        )
        print("✅ Stability config imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import stability config: {e}")
        return False
    
    return True


def test_configuration():
    """Test configuration setup."""
    print("\n🔧 Testing configuration...")
    
    try:
        from config.stability_config import get_stability_config
        
        # Test with environment variable
        if os.getenv("STABILITY_API_KEY"):
            config = get_stability_config()
            print("✅ Configuration loaded from environment")
            print(f"   - API Key: {'Set' if config.api_key else 'Not set'}")
            print(f"   - Base URL: {config.base_url}")
            print(f"   - Timeout: {config.timeout}s")
            return True
        else:
            print("⚠️  STABILITY_API_KEY not set in environment")
            print("   - This is expected if you haven't configured it yet")
            return True
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_models():
    """Test Pydantic model validation."""
    print("\n📋 Testing Pydantic models...")
    
    try:
        from models.stability_models import (
            StableImageUltraRequest, StableImageCoreRequest,
            OutpaintRequest, InpaintRequest
        )
        
        # Test valid model creation
        ultra_request = StableImageUltraRequest(
            prompt="A beautiful landscape",
            aspect_ratio="16:9",
            seed=42
        )
        print("✅ StableImageUltraRequest validation passed")
        
        # Test outpaint request
        outpaint_request = OutpaintRequest(
            left=100,
            right=200,
            output_format="webp"
        )
        print("✅ OutpaintRequest validation passed")
        
        # Test invalid model (should raise validation error)
        try:
            invalid_request = StableImageUltraRequest(
                prompt="",  # Empty prompt should fail
                seed=5000000000  # Invalid seed
            )
            print("❌ Model validation failed - invalid data was accepted")
            return False
        except Exception:
            print("✅ Model validation correctly rejected invalid data")
        
        return True
        
    except Exception as e:
        print(f"❌ Model testing failed: {e}")
        return False


async def test_service_creation():
    """Test service creation and basic functionality."""
    print("\n🔌 Testing service creation...")
    
    try:
        from services.stability_service import StabilityAIService
        
        # Test service creation without API key (should fail)
        try:
            service = StabilityAIService()
            print("❌ Service creation should have failed without API key")
            return False
        except ValueError:
            print("✅ Service correctly requires API key")
        
        # Test service creation with API key
        service = StabilityAIService(api_key="test_key")
        print("✅ Service created successfully with API key")
        
        # Test helper methods
        headers = service._get_headers()
        assert "Authorization" in headers
        print("✅ Service helper methods work correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Service creation test failed: {e}")
        return False


def test_router_creation():
    """Test router creation and endpoint registration."""
    print("\n🛣️  Testing router creation...")
    
    try:
        from fastapi import FastAPI
        from routers.stability import router as stability_router
        from routers.stability_advanced import router as stability_advanced_router
        from routers.stability_admin import router as stability_admin_router
        
        # Create test app
        app = FastAPI()
        
        # Include routers
        app.include_router(stability_router)
        app.include_router(stability_advanced_router)
        app.include_router(stability_admin_router)
        
        print("✅ Routers included successfully")
        
        # Check that routes are registered
        route_count = len(app.routes)
        print(f"✅ {route_count} routes registered")
        
        # List some key routes
        stability_routes = [
            route for route in app.routes 
            if hasattr(route, 'path') and '/api/stability' in route.path
        ]
        print(f"✅ {len(stability_routes)} Stability AI routes found")
        
        return True
        
    except Exception as e:
        print(f"❌ Router creation test failed: {e}")
        return False


def test_middleware():
    """Test middleware functionality."""
    print("\n🛡️  Testing middleware...")
    
    try:
        from middleware.stability_middleware import (
            RateLimitMiddleware, MonitoringMiddleware, CachingMiddleware
        )
        
        # Test middleware creation
        rate_limiter = RateLimitMiddleware()
        monitoring = MonitoringMiddleware()
        caching = CachingMiddleware()
        
        print("✅ Middleware instances created successfully")
        
        # Test basic functionality
        stats = monitoring.get_stats()
        assert isinstance(stats, dict)
        print("✅ Monitoring middleware functional")
        
        cache_stats = caching.get_cache_stats()
        assert isinstance(cache_stats, dict)
        print("✅ Caching middleware functional")
        
        return True
        
    except Exception as e:
        print(f"❌ Middleware test failed: {e}")
        return False


async def run_all_tests():
    """Run all tests."""
    print("🧪 Running Stability AI Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Model Validation Test", test_models),
        ("Service Creation Test", test_service_creation),
        ("Router Creation Test", test_router_creation),
        ("Middleware Test", test_middleware)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 30)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Stability AI integration is ready.")
        print("\n📚 Documentation available at:")
        print("   - Integration Guide: backend/docs/STABILITY_AI_INTEGRATION.md")
        print("   - API Docs: http://localhost:8000/docs (when server is running)")
        print("\n🚀 To start using:")
        print("   1. Set your STABILITY_API_KEY in .env file")
        print("   2. Run: python app.py")
        print("   3. Visit: http://localhost:8000/docs")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please address the issues above.")
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)