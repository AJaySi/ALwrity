"""Test script for Facebook Writer API endpoints."""

import requests
import json
from typing import Dict, Any

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/api/facebook-writer/health")
        print(f"Health Check: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_get_tools():
    """Test getting available tools."""
    try:
        response = requests.get(f"{BASE_URL}/api/facebook-writer/tools")
        print(f"Get Tools: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Available tools: {data['total_count']}")
            for tool in data['tools'][:3]:  # Show first 3 tools
                print(f"  - {tool['name']}: {tool['description']}")
        return response.status_code == 200
    except Exception as e:
        print(f"Get tools failed: {e}")
        return False

def test_generate_post():
    """Test Facebook post generation."""
    payload = {
        "business_type": "Fitness coach",
        "target_audience": "Fitness enthusiasts aged 25-35",
        "post_goal": "Increase engagement",
        "post_tone": "Inspirational",
        "include": "Success story, workout tips",
        "avoid": "Generic advice",
        "media_type": "Image",
        "advanced_options": {
            "use_hook": True,
            "use_story": True,
            "use_cta": True,
            "use_question": True,
            "use_emoji": True,
            "use_hashtags": True
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/facebook-writer/post/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Generate Post: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"Post generated successfully!")
                print(f"Content preview: {data['content'][:100]}...")
                if data.get('analytics'):
                    print(f"Expected reach: {data['analytics']['expected_reach']}")
            else:
                print(f"Generation failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"Request failed: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Generate post failed: {e}")
        return False

def test_generate_story():
    """Test Facebook story generation."""
    payload = {
        "business_type": "Fashion brand",
        "target_audience": "Fashion enthusiasts aged 18-30",
        "story_type": "Product showcase",
        "story_tone": "Fun",
        "include": "Behind the scenes",
        "avoid": "Too much text",
        "visual_options": {
            "background_type": "Gradient",
            "text_overlay": True,
            "stickers": True,
            "interactive_elements": True
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/facebook-writer/story/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Generate Story: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"Story generated successfully!")
                print(f"Content preview: {data['content'][:100]}...")
                if data.get('visual_suggestions'):
                    print(f"Visual suggestions: {len(data['visual_suggestions'])} items")
            else:
                print(f"Generation failed: {data.get('error', 'Unknown error')}")
        return response.status_code == 200
    except Exception as e:
        print(f"Generate story failed: {e}")
        return False

def test_generate_ad_copy():
    """Test Facebook ad copy generation."""
    payload = {
        "business_type": "E-commerce store",
        "product_service": "Wireless headphones",
        "ad_objective": "Conversions",
        "ad_format": "Single image",
        "target_audience": "Tech enthusiasts and music lovers",
        "targeting_options": {
            "age_group": "25-34",
            "interests": "Technology, Music, Audio equipment",
            "location": "United States"
        },
        "unique_selling_proposition": "Premium sound quality at affordable prices",
        "offer_details": "20% off for first-time buyers",
        "budget_range": "Medium"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/facebook-writer/ad-copy/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Generate Ad Copy: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"Ad copy generated successfully!")
                if data.get('primary_ad_copy'):
                    print(f"Headline: {data['primary_ad_copy'].get('headline', 'N/A')}")
                if data.get('performance_predictions'):
                    print(f"Estimated reach: {data['performance_predictions']['estimated_reach']}")
            else:
                print(f"Generation failed: {data.get('error', 'Unknown error')}")
        return response.status_code == 200
    except Exception as e:
        print(f"Generate ad copy failed: {e}")
        return False

def test_analyze_engagement():
    """Test engagement analysis."""
    payload = {
        "content": "🚀 Ready to transform your fitness journey? Our new 30-day challenge is here! Join thousands who've already seen amazing results. What's your biggest fitness goal? 💪 #FitnessMotivation #Challenge #Transformation",
        "content_type": "Post",
        "analysis_type": "Performance prediction",
        "business_type": "Fitness coach",
        "target_audience": "Fitness enthusiasts"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/facebook-writer/engagement/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Analyze Engagement: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"Analysis completed successfully!")
                print(f"Content score: {data.get('content_score', 'N/A')}/100")
                if data.get('engagement_metrics'):
                    print(f"Predicted engagement: {data['engagement_metrics']['predicted_engagement_rate']}")
            else:
                print(f"Analysis failed: {data.get('error', 'Unknown error')}")
        return response.status_code == 200
    except Exception as e:
        print(f"Analyze engagement failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Facebook Writer API Endpoints")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Get Tools", test_get_tools),
        ("Generate Post", test_generate_post),
        ("Generate Story", test_generate_story),
        ("Generate Ad Copy", test_generate_ad_copy),
        ("Analyze Engagement", test_analyze_engagement)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}")
        except Exception as e:
            print(f"❌ FAIL - {e}")
            results.append((test_name, False))
    
    print(f"\n📊 Test Results Summary")
    print("=" * 50)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Facebook Writer API is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the server logs for details.")

if __name__ == "__main__":
    main()