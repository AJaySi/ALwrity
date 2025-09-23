"""
Test script for Blog Content SEO Analyzer

This script tests the core functionality of the SEO analyzer
without requiring the full application setup.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.blog_writer.seo.blog_content_seo_analyzer import BlogContentSEOAnalyzer


async def test_seo_analyzer():
    """Test the SEO analyzer with sample data"""
    
    # Sample blog content
    sample_content = """
# The Ultimate Guide to AI-Powered Blog Writing

## Introduction

In today's digital landscape, content creation has become more important than ever. With the rise of artificial intelligence, we're seeing revolutionary changes in how we approach blog writing and content marketing.

## What is AI-Powered Blog Writing?

AI-powered blog writing refers to the use of artificial intelligence tools and technologies to assist in the creation, optimization, and management of blog content. This includes everything from research and outline generation to content creation and SEO optimization.

## Key Benefits of AI Blog Writing

### 1. Increased Efficiency
AI tools can significantly reduce the time required to create high-quality blog content. What used to take hours can now be completed in minutes.

### 2. Improved SEO Performance
AI-powered tools can analyze search trends, identify optimal keywords, and ensure content is optimized for search engines.

### 3. Enhanced Content Quality
With AI assistance, writers can focus on strategy and creativity while AI handles the technical aspects of content creation.

## Best Practices for AI Blog Writing

1. **Start with Research**: Use AI tools to gather comprehensive information about your topic
2. **Create Detailed Outlines**: Leverage AI to structure your content effectively
3. **Optimize for SEO**: Use AI analysis to ensure your content ranks well
4. **Review and Refine**: Always review AI-generated content before publishing

## Conclusion

AI-powered blog writing is transforming the content creation landscape. By leveraging these tools effectively, content creators can produce higher quality content more efficiently than ever before.

The future of content creation is here, and it's powered by artificial intelligence.
"""

    # Sample research data
    sample_research_data = {
        "keyword_analysis": {
            "primary": ["AI blog writing", "artificial intelligence content", "AI content creation"],
            "long_tail": ["AI-powered blog writing tools", "artificial intelligence content marketing", "AI blog writing software"],
            "semantic": ["content automation", "AI writing assistant", "automated content creation", "AI content optimization"],
            "all_keywords": ["AI blog writing", "artificial intelligence content", "AI content creation", "AI-powered blog writing tools", "artificial intelligence content marketing", "AI blog writing software", "content automation", "AI writing assistant", "automated content creation", "AI content optimization"],
            "search_intent": "informational"
        },
        "competitor_analysis": {
            "top_competitors": ["HubSpot", "Content Marketing Institute", "Copyblogger"],
            "content_gaps": ["AI-specific use cases", "ROI measurement", "implementation strategies"]
        },
        "content_angles": [
            "Beginner's guide to AI blog writing",
            "ROI of AI content creation tools",
            "AI vs human content creation comparison"
        ]
    }

    print("🚀 Starting SEO Analysis Test")
    print("=" * 50)
    
    try:
        # Initialize the analyzer
        analyzer = BlogContentSEOAnalyzer()
        print("✅ SEO Analyzer initialized successfully")
        
        # Run the analysis
        print("\n📊 Running SEO analysis...")
        results = await analyzer.analyze_blog_content(sample_content, sample_research_data)
        
        # Display results
        print("\n📈 Analysis Results:")
        print("=" * 30)
        
        if 'error' in results:
            print(f"❌ Analysis failed: {results['error']}")
            return
        
        print(f"🎯 Overall Score: {results.get('overall_score', 0)}/100")
        print(f"📊 Overall Grade: {results.get('analysis_summary', {}).get('overall_grade', 'N/A')}")
        print(f"📝 Status: {results.get('analysis_summary', {}).get('status', 'N/A')}")
        
        print("\n📋 Category Scores:")
        category_scores = results.get('category_scores', {})
        for category, score in category_scores.items():
            print(f"  • {category.capitalize()}: {score}/100")
        
        print("\n💡 Key Strengths:")
        strengths = results.get('analysis_summary', {}).get('key_strengths', [])
        for strength in strengths:
            print(f"  ✅ {strength}")
        
        print("\n⚠️ Areas for Improvement:")
        weaknesses = results.get('analysis_summary', {}).get('key_weaknesses', [])
        for weakness in weaknesses:
            print(f"  🔧 {weakness}")
        
        print("\n📝 Actionable Recommendations:")
        recommendations = results.get('actionable_recommendations', [])
        for i, rec in enumerate(recommendations[:5], 1):  # Show first 5 recommendations
            print(f"  {i}. [{rec.get('category', 'N/A')}] {rec.get('recommendation', 'N/A')}")
        
        print("\n🎉 SEO Analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_seo_analyzer())
