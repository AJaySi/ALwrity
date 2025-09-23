#!/usr/bin/env python3
"""
Simple test script to verify import issues are fixed.

This script tests that all the required services can be imported and initialized
without import errors.

Usage:
    python test_imports.py
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing Imports...")
    
    try:
        print("📦 Testing LinkedIn Models...")
        from models.linkedin_models import (
            LinkedInPostRequest, LinkedInPostResponse, PostContent, ResearchSource,
            LinkedInArticleRequest, LinkedInArticleResponse, ArticleContent,
            LinkedInCarouselRequest, LinkedInCarouselResponse, CarouselContent, CarouselSlide,
            LinkedInVideoScriptRequest, LinkedInVideoScriptResponse, VideoScript,
            LinkedInCommentResponseRequest, LinkedInCommentResponseResult,
            HashtagSuggestion, ImageSuggestion, Citation, ContentQualityMetrics,
            GroundingLevel
        )
        print("✅ LinkedIn Models imported successfully")
    except Exception as e:
        print(f"❌ LinkedIn Models import failed: {e}")
        return False
    
    try:
        print("📦 Testing Research Service...")
        from services.research import GoogleSearchService
        print("✅ Research Service imported successfully")
    except Exception as e:
        print(f"❌ Research Service import failed: {e}")
        return False
    
    try:
        print("📦 Testing Citation Service...")
        from services.citation import CitationManager
        print("✅ Citation Service imported successfully")
    except Exception as e:
        print(f"❌ Citation Service import failed: {e}")
        return False
    
    try:
        print("📦 Testing Quality Service...")
        from services.quality import ContentQualityAnalyzer
        print("✅ Quality Service imported successfully")
    except Exception as e:
        print(f"❌ Quality Service import failed: {e}")
        return False
    
    try:
        print("📦 Testing LLM Providers...")
        from services.llm_providers.gemini_provider import gemini_structured_json_response, gemini_text_response
        print("✅ LLM Providers imported successfully")
    except Exception as e:
        print(f"❌ LLM Providers import failed: {e}")
        return False
    
    try:
        print("📦 Testing Gemini Grounded Provider...")
        from services.llm_providers.gemini_grounded_provider import GeminiGroundedProvider
        print("✅ Gemini Grounded Provider imported successfully")
    except Exception as e:
        print(f"❌ Gemini Grounded Provider import failed: {e}")
        return False
    
    try:
        print("📦 Testing LinkedIn Service...")
        from services.linkedin_service import LinkedInService
        print("✅ LinkedIn Service imported successfully")
    except Exception as e:
        print(f"❌ LinkedIn Service import failed: {e}")
        return False
    
    print("\n🎉 All imports successful!")
    return True

def test_service_initialization():
    """Test that services can be initialized without errors."""
    print("\n🔧 Testing Service Initialization...")
    
    try:
        print("📦 Initializing LinkedIn Service...")
        from services.linkedin_service import LinkedInService
        service = LinkedInService()
        print("✅ LinkedIn Service initialized successfully")
        
        # Check which services are available
        print(f"   - Google Search: {'✅' if service.google_search else '❌'}")
        print(f"   - Gemini Grounded: {'✅' if service.gemini_grounded else '❌'}")
        print(f"   - Citation Manager: {'✅' if service.citation_manager else '❌'}")
        print(f"   - Quality Analyzer: {'✅' if service.quality_analyzer else '❌'}")
        print(f"   - Fallback Provider: {'✅' if service.fallback_provider else '❌'}")
        
        return True
    except Exception as e:
        print(f"❌ LinkedIn Service initialization failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Starting Import Tests")
    print("=" * 50)
    
    # Test imports
    import_success = test_imports()
    
    if import_success:
        # Test service initialization
        init_success = test_service_initialization()
        
        if init_success:
            print("\n🎉 SUCCESS: All tests passed!")
            print("✅ Import issues have been resolved")
            print("✅ Services can be initialized")
            print("✅ Ready for testing native grounding")
        else:
            print("\n⚠️ PARTIAL SUCCESS: Imports work but initialization failed")
            print("💡 This may be due to missing dependencies or configuration")
    else:
        print("\n❌ FAILURE: Import tests failed")
        print("💡 There are still import issues to resolve")
        sys.exit(1)

if __name__ == "__main__":
    main()
