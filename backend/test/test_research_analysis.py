import requests
import json
from datetime import datetime

# Test the research endpoint and capture full response
url = "http://localhost:8000/api/blog/research"
payload = {
    "keywords": ["AI content generation", "blog writing"],
    "topic": "ALwrity content generation",
    "industry": "Technology",
    "target_audience": "content creators"
}

try:
    print("Sending request to research endpoint...")
    response = requests.post(url, json=payload, timeout=120)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        # Create analysis file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_analysis_{timestamp}.json"
        
        # Save full response to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n=== RESEARCH RESPONSE ANALYSIS ===")
        print(f"✅ Full response saved to: {filename}")
        print(f"Success: {data.get('success')}")
        print(f"Sources Count: {len(data.get('sources', []))}")
        print(f"Search Queries Count: {len(data.get('search_queries', []))}")
        print(f"Has Search Widget: {bool(data.get('search_widget'))}")
        print(f"Suggested Angles Count: {len(data.get('suggested_angles', []))}")
        
        print(f"\n=== SOURCES ANALYSIS ===")
        sources = data.get('sources', [])
        for i, source in enumerate(sources[:5]):  # Show first 5
            print(f"Source {i+1}: {source.get('title', 'No title')}")
            print(f"  URL: {source.get('url', 'No URL')[:100]}...")
            print(f"  Type: {source.get('type', 'Unknown')}")
            print(f"  Credibility: {source.get('credibility_score', 'N/A')}")
        
        print(f"\n=== SEARCH QUERIES ANALYSIS ===")
        queries = data.get('search_queries', [])
        print(f"Total queries: {len(queries)}")
        for i, query in enumerate(queries[:10]):  # Show first 10
            print(f"{i+1:2d}. {query}")
        
        print(f"\n=== SEARCH WIDGET ANALYSIS ===")
        widget = data.get('search_widget', '')
        if widget:
            print(f"Widget HTML length: {len(widget)} characters")
            print(f"Contains Google branding: {'Google' in widget}")
            print(f"Contains search chips: {'chip' in widget}")
            print(f"Contains carousel: {'carousel' in widget}")
            print(f"First 200 chars: {widget[:200]}...")
        else:
            print("No search widget provided")
        
        print(f"\n=== KEYWORD ANALYSIS ===")
        kw_analysis = data.get('keyword_analysis', {})
        print(f"Primary keywords: {kw_analysis.get('primary', [])}")
        print(f"Secondary keywords: {kw_analysis.get('secondary', [])}")
        print(f"Long-tail keywords: {kw_analysis.get('long_tail', [])}")
        print(f"Search intent: {kw_analysis.get('search_intent', 'Unknown')}")
        print(f"Difficulty score: {kw_analysis.get('difficulty', 'N/A')}")
        
        print(f"\n=== SUGGESTED ANGLES ===")
        angles = data.get('suggested_angles', [])
        for i, angle in enumerate(angles):
            print(f"{i+1}. {angle}")
        
        print(f"\n=== UI REPRESENTATION RECOMMENDATIONS ===")
        print("Based on the response, here's what should be displayed in the Editor UI:")
        print(f"1. Research Sources Panel: {len(sources)} real web sources")
        print(f"2. Search Widget: Interactive Google search chips ({len(queries)} queries)")
        print(f"3. Keyword Analysis: Primary/Secondary/Long-tail breakdown")
        print(f"4. Content Angles: {len(angles)} suggested blog post angles")
        print(f"5. Search Queries: {len(queries)} research queries for reference")
        
        # Additional analysis for UI components
        print(f"\n=== UI COMPONENT BREAKDOWN ===")
        
        # Sources for UI
        print("SOURCES FOR UI:")
        for i, source in enumerate(sources[:3]):
            print(f"  - {source.get('title')} (Credibility: {source.get('credibility_score')})")
        
        # Search widget for UI
        print(f"\nSEARCH WIDGET FOR UI:")
        print(f"  - HTML length: {len(widget)} chars")
        print(f"  - Can be embedded directly in UI")
        print(f"  - Contains {len(queries)} search suggestions")
        
        # Keywords for UI
        print(f"\nKEYWORDS FOR UI:")
        print(f"  - Primary: {', '.join(kw_analysis.get('primary', []))}")
        print(f"  - Secondary: {', '.join(kw_analysis.get('secondary', []))}")
        print(f"  - Long-tail: {', '.join(kw_analysis.get('long_tail', []))}")
        
        # Angles for UI
        print(f"\nCONTENT ANGLES FOR UI:")
        for i, angle in enumerate(angles[:3]):
            print(f"  - {angle}")
            
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Request failed: {e}")
    import traceback
    traceback.print_exc()
