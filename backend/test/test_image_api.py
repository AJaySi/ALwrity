#!/usr/bin/env python3
"""
Test script for LinkedIn Image Generation API endpoints
"""

import asyncio
import aiohttp
import json

async def test_image_generation_api():
    """Test the LinkedIn image generation API endpoints"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing LinkedIn Image Generation API...")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base_url}/api/linkedin/image-generation-health") as response:
            if response.status == 200:
                health_data = await response.json()
                print(f"✅ Health Check: {health_data['status']}")
                print(f"   Services: {health_data['services']}")
                print(f"   Test Prompts: {health_data['test_prompts_generated']}")
            else:
                print(f"❌ Health Check Failed: {response.status}")
                return
    
    # Test 2: Generate Image Prompts
    print("\n2️⃣ Testing Image Prompt Generation...")
    prompt_data = {
        "content_type": "post",
        "topic": "AI in Marketing",
        "industry": "Technology",
        "content": "This is a test LinkedIn post about AI in marketing. It demonstrates the image generation capabilities."
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{base_url}/api/linkedin/generate-image-prompts",
            json=prompt_data
        ) as response:
            if response.status == 200:
                prompts = await response.json()
                print(f"✅ Generated {len(prompts)} image prompts:")
                for i, prompt in enumerate(prompts, 1):
                    print(f"   {i}. {prompt['style']}: {prompt['description']}")
                
                # Test 3: Generate Image from First Prompt
                print("\n3️⃣ Testing Image Generation...")
                image_data = {
                    "prompt": prompts[0]['prompt'],
                    "content_context": {
                        "topic": prompt_data["topic"],
                        "industry": prompt_data["industry"],
                        "content_type": prompt_data["content_type"],
                        "content": prompt_data["content"],
                        "style": prompts[0]['style']
                    },
                    "aspect_ratio": "1:1"
                }
                
                async with session.post(
                    f"{base_url}/api/linkedin/generate-image",
                    json=image_data
                ) as img_response:
                    if img_response.status == 200:
                        result = await img_response.json()
                        if result.get('success'):
                            print(f"✅ Image Generated Successfully!")
                            print(f"   Image ID: {result.get('image_id')}")
                            print(f"   Style: {result.get('style')}")
                            print(f"   Aspect Ratio: {result.get('aspect_ratio')}")
                        else:
                            print(f"❌ Image Generation Failed: {result.get('error')}")
                    else:
                        print(f"❌ Image Generation Request Failed: {img_response.status}")
                        error_text = await img_response.text()
                        print(f"   Error: {error_text}")
            else:
                print(f"❌ Prompt Generation Failed: {response.status}")
                error_text = await response.text()
                print(f"   Error: {error_text}")

if __name__ == "__main__":
    print("🚀 Starting LinkedIn Image Generation API Tests...")
    try:
        asyncio.run(test_image_generation_api())
        print("\n🎉 All tests completed!")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
