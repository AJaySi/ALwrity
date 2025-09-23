import requests
import json

# Test the research endpoint
url = "http://localhost:8000/api/blog/research"
payload = {
    "keywords": ["AI content generation", "blog writing"],
    "topic": "ALwrity content generation",
    "industry": "Technology",
    "target_audience": "content creators"
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n=== RESEARCH RESPONSE ===")
        print(f"Success: {data.get('success')}")
        print(f"Sources Count: {len(data.get('sources', []))}")
        print(f"Search Queries Count: {len(data.get('search_queries', []))}")
        print(f"Has Search Widget: {bool(data.get('search_widget'))}")
        print(f"Suggested Angles Count: {len(data.get('suggested_angles', []))}")
        
        print("\n=== SOURCES ===")
        for i, source in enumerate(data.get('sources', [])[:3]):
            print(f"Source {i+1}: {source.get('title', 'No title')}")
            print(f"  URL: {source.get('url', 'No URL')}")
            print(f"  Type: {source.get('type', 'Unknown')}")
        
        print("\n=== SEARCH QUERIES (First 5) ===")
        for i, query in enumerate(data.get('search_queries', [])[:5]):
            print(f"{i+1}. {query}")
        
        print("\n=== SUGGESTED ANGLES ===")
        for i, angle in enumerate(data.get('suggested_angles', [])[:3]):
            print(f"{i+1}. {angle}")
        
        print("\n=== KEYWORD ANALYSIS ===")
        kw_analysis = data.get('keyword_analysis', {})
        print(f"Primary: {kw_analysis.get('primary', [])}")
        print(f"Secondary: {kw_analysis.get('secondary', [])}")
        print(f"Search Intent: {kw_analysis.get('search_intent', 'Unknown')}")
        
        print("\n=== SEARCH WIDGET (First 200 chars) ===")
        widget = data.get('search_widget', '')
        if widget:
            print(widget[:200] + "..." if len(widget) > 200 else widget)
        else:
            print("No search widget provided")
            
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Request failed: {e}")
