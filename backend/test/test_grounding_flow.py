#!/usr/bin/env python3
"""
Test script to debug the grounding data flow
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.linkedin_service import LinkedInService
from models.linkedin_models import LinkedInPostRequest, GroundingLevel

async def test_grounding_flow():
    """Test the grounding data flow"""
    try:
        print("🔍 Testing grounding data flow...")
        
        # Initialize the service
        service = LinkedInService()
        print("✅ LinkedInService initialized")
        
        # Create a test request
        request = LinkedInPostRequest(
            topic="AI in healthcare transformation",
            industry="Healthcare",
            grounding_level=GroundingLevel.ENHANCED,
            include_citations=True,
            research_enabled=True,
            search_engine="google",
            max_length=2000
        )
        print("✅ Test request created")
        
        # Generate post
        print("🚀 Generating LinkedIn post...")
        response = await service.generate_linkedin_post(request)
        
        if response.success:
            print("✅ Post generated successfully!")
            print(f"📊 Research sources count: {len(response.research_sources) if response.research_sources else 0}")
            print(f"📝 Citations count: {len(response.data.citations) if response.data.citations else 0}")
            print(f"🔗 Source list: {response.data.source_list[:200] if response.data.source_list else 'None'}")
            
            if response.research_sources:
                print(f"📚 First research source: {response.research_sources[0]}")
                print(f"📚 Research source types: {[type(s) for s in response.research_sources[:3]]}")
            
            if response.data.citations:
                print(f"📝 First citation: {response.data.citations[0]}")
        else:
            print(f"❌ Post generation failed: {response.error}")
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_grounding_flow())
