#!/usr/bin/env python3
"""
Test script for the hallucination detector service.

This script tests the hallucination detector functionality
without requiring the full FastAPI server to be running.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.hallucination_detector import HallucinationDetector

async def test_hallucination_detector():
    """Test the hallucination detector with sample text."""
    
    print("🧪 Testing Hallucination Detector")
    print("=" * 50)
    
    # Initialize detector
    detector = HallucinationDetector()
    
    # Test text with various types of claims
    test_text = """
    The Eiffel Tower is located in Paris, France. It was built in 1889 and stands 330 meters tall.
    The tower was designed by Gustave Eiffel and is one of the most visited monuments in the world.
    Our company increased sales by 25% last quarter and launched three new products.
    The weather today is sunny with a temperature of 22 degrees Celsius.
    """
    
    print(f"📝 Test Text:\n{test_text.strip()}\n")
    
    try:
        # Test claim extraction
        print("🔍 Testing claim extraction...")
        claims = await detector._extract_claims(test_text)
        print(f"✅ Extracted {len(claims)} claims:")
        for i, claim in enumerate(claims, 1):
            print(f"   {i}. {claim}")
        print()
        
        # Test full hallucination detection
        print("🔍 Testing full hallucination detection...")
        result = await detector.detect_hallucinations(test_text)
        
        print(f"✅ Analysis completed:")
        print(f"   Overall Confidence: {result.overall_confidence:.2f}")
        print(f"   Total Claims: {result.total_claims}")
        print(f"   Supported: {result.supported_claims}")
        print(f"   Refuted: {result.refuted_claims}")
        print(f"   Insufficient: {result.insufficient_claims}")
        print()
        
        # Display individual claims
        print("📊 Individual Claim Analysis:")
        for i, claim in enumerate(result.claims, 1):
            print(f"\n   Claim {i}: {claim.text}")
            print(f"   Assessment: {claim.assessment}")
            print(f"   Confidence: {claim.confidence:.2f}")
            print(f"   Supporting Sources: {len(claim.supporting_sources)}")
            print(f"   Refuting Sources: {len(claim.refuting_sources)}")
            
            if claim.supporting_sources:
                print("   Supporting Sources:")
                for j, source in enumerate(claim.supporting_sources[:2], 1):  # Show first 2
                    print(f"     {j}. {source.get('title', 'Untitled')} (Score: {source.get('score', 0):.2f})")
            
            if claim.refuting_sources:
                print("   Refuting Sources:")
                for j, source in enumerate(claim.refuting_sources[:2], 1):  # Show first 2
                    print(f"     {j}. {source.get('title', 'Untitled')} (Score: {source.get('score', 0):.2f})")
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_health_check():
    """Test the health check functionality."""
    
    print("\n🏥 Testing Health Check")
    print("=" * 30)
    
    detector = HallucinationDetector()
    
    # Check API availability
    exa_available = bool(detector.exa_api_key)
    openai_available = bool(detector.openai_api_key)
    
    print(f"Exa.ai API Available: {'✅' if exa_available else '❌'}")
    print(f"OpenAI API Available: {'✅' if openai_available else '❌'}")
    
    if not exa_available:
        print("⚠️  Exa.ai API key not found. Set EXA_API_KEY environment variable.")
    
    if not openai_available:
        print("⚠️  OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
    
    if exa_available and openai_available:
        print("✅ All APIs are available for full functionality.")
    elif openai_available:
        print("⚠️  Limited functionality available (claim extraction only).")
    else:
        print("❌ No APIs available. Only fallback functionality will work.")

def main():
    """Main test function."""
    
    print("🚀 Hallucination Detector Test Suite")
    print("=" * 50)
    
    # Check environment variables
    print("🔧 Environment Check:")
    exa_key = os.getenv('EXA_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    print(f"EXA_API_KEY: {'✅ Set' if exa_key else '❌ Not set'}")
    print(f"OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Not set'}")
    print()
    
    # Run tests
    asyncio.run(test_health_check())
    asyncio.run(test_hallucination_detector())

if __name__ == "__main__":
    main()
