#!/usr/bin/env python3
"""
Test Script for AI SEO Tools API

This script tests all the migrated SEO tools endpoints to ensure
they are working correctly after migration to FastAPI.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_endpoint(session, endpoint, method="GET", data=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "POST":
            async with session.post(url, json=data) as response:
                result = await response.json()
                return {
                    "endpoint": endpoint,
                    "status": response.status,
                    "success": response.status == 200,
                    "response": result
                }
        else:
            async with session.get(url) as response:
                result = await response.json()
                return {
                    "endpoint": endpoint,
                    "status": response.status,
                    "success": response.status == 200,
                    "response": result
                }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "status": 0,
            "success": False,
            "error": str(e)
        }

async def run_seo_tools_tests():
    """Run comprehensive tests for all SEO tools"""
    
    print("🚀 Starting AI SEO Tools API Tests")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Test health endpoint
        print("\n1. Testing Health Endpoints...")
        health_tests = [
            ("/api/seo/health", "GET", None),
            ("/api/seo/tools/status", "GET", None)
        ]
        
        for endpoint, method, data in health_tests:
            result = await test_endpoint(session, endpoint, method, data)
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"   {status} {endpoint} - Status: {result['status']}")
        
        # Test meta description generation
        print("\n2. Testing Meta Description Generation...")
        meta_desc_data = {
            "keywords": ["SEO", "content marketing", "digital strategy"],
            "tone": "Professional",
            "search_intent": "Informational Intent",
            "language": "English"
        }
        
        result = await test_endpoint(session, "/api/seo/meta-description", "POST", meta_desc_data)
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"   {status} Meta Description Generation - Status: {result['status']}")
        
        if result["success"]:
            data = result["response"].get("data", {})
            descriptions = data.get("meta_descriptions", [])
            print(f"   Generated {len(descriptions)} meta descriptions")
        
        # Test PageSpeed analysis
        print("\n3. Testing PageSpeed Analysis...")
        pagespeed_data = {
            "url": "https://example.com",
            "strategy": "DESKTOP",
            "categories": ["performance"]
        }
        
        result = await test_endpoint(session, "/api/seo/pagespeed-analysis", "POST", pagespeed_data)
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"   {status} PageSpeed Analysis - Status: {result['status']}")
        
        # Test sitemap analysis
        print("\n4. Testing Sitemap Analysis...")
        sitemap_data = {
            "sitemap_url": "https://www.google.com/sitemap.xml",
            "analyze_content_trends": False,
            "analyze_publishing_patterns": False
        }
        
        result = await test_endpoint(session, "/api/seo/sitemap-analysis", "POST", sitemap_data)
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"   {status} Sitemap Analysis - Status: {result['status']}")
        
        # Test OpenGraph generation
        print("\n5. Testing OpenGraph Generation...")
        og_data = {
            "url": "https://example.com",
            "title_hint": "Test Page",
            "description_hint": "Test description",
            "platform": "General"
        }
        
        result = await test_endpoint(session, "/api/seo/opengraph-tags", "POST", og_data)
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"   {status} OpenGraph Generation - Status: {result['status']}")
        
        # Test on-page SEO analysis
        print("\n6. Testing On-Page SEO Analysis...")
        onpage_data = {
            "url": "https://example.com",
            "target_keywords": ["test", "example"],
            "analyze_images": True,
            "analyze_content_quality": True
        }
        
        result = await test_endpoint(session, "/api/seo/on-page-analysis", "POST", onpage_data)
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"   {status} On-Page SEO Analysis - Status: {result['status']}")
        
        # Test technical SEO analysis
        print("\n7. Testing Technical SEO Analysis...")
        technical_data = {
            "url": "https://example.com",
            "crawl_depth": 2,
            "include_external_links": True,
            "analyze_performance": True
        }
        
        result = await test_endpoint(session, "/api/seo/technical-seo", "POST", technical_data)
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"   {status} Technical SEO Analysis - Status: {result['status']}")
        
        # Test workflow endpoints
        print("\n8. Testing Workflow Endpoints...")
        
        # Website audit workflow
        audit_data = {
            "website_url": "https://example.com",
            "workflow_type": "complete_audit",
            "target_keywords": ["test", "example"]
        }
        
        result = await test_endpoint(session, "/api/seo/workflow/website-audit", "POST", audit_data)
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"   {status} Website Audit Workflow - Status: {result['status']}")
        
        # Content analysis workflow
        content_data = {
            "website_url": "https://example.com",
            "workflow_type": "content_analysis",
            "target_keywords": ["content", "strategy"]
        }
        
        result = await test_endpoint(session, "/api/seo/workflow/content-analysis", "POST", content_data)
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"   {status} Content Analysis Workflow - Status: {result['status']}")
    
    print("\n" + "=" * 50)
    print("🎉 SEO Tools API Testing Completed!")
    print("\nNote: Some tests may show connection errors if the server is not running.")
    print("Start the server with: uvicorn app:app --reload --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    asyncio.run(run_seo_tools_tests())