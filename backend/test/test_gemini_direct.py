import asyncio
from services.llm_providers.gemini_grounded_provider import GeminiGroundedProvider

async def test_gemini_direct():
    gemini = GeminiGroundedProvider()
    
    prompt = """
    Research the topic "AI content generation" in the Technology industry for content creators audience. Provide a comprehensive analysis including:

    1. Current trends and insights (2024-2025)
    2. Key statistics and data points with sources
    3. Industry expert opinions and quotes
    4. Recent developments and news
    5. Market analysis and forecasts
    6. Best practices and case studies
    7. Keyword analysis: primary, secondary, and long-tail opportunities
    8. Competitor analysis: top players and content gaps
    9. Content angle suggestions: 5 compelling angles for blog posts

    Focus on factual, up-to-date information from credible sources.
    Include specific data points, percentages, and recent developments.
    Structure your response with clear sections for each analysis area.
    """
    
    try:
        result = await gemini.generate_grounded_content(
            prompt=prompt,
            content_type="research",
            max_tokens=2000
        )
        
        print("=== GEMINI RESULT ===")
        print(f"Type: {type(result)}")
        print(f"Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict):
            print(f"Sources count: {len(result.get('sources', []))}")
            print(f"Search queries count: {len(result.get('search_queries', []))}")
            print(f"Has search widget: {bool(result.get('search_widget'))}")
            print(f"Content length: {len(result.get('content', ''))}")
            
            print("\n=== FIRST SOURCE ===")
            sources = result.get('sources', [])
            if sources:
                print(f"Source: {sources[0]}")
            
            print("\n=== SEARCH QUERIES (First 3) ===")
            queries = result.get('search_queries', [])
            for i, query in enumerate(queries[:3]):
                print(f"{i+1}. {query}")
        else:
            print(f"Result is not a dict: {result}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini_direct())
