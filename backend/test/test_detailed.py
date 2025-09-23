import requests
import json

# Test the research endpoint with more detailed output
url = "http://localhost:8000/api/blog/research"
payload = {
    "keywords": ["AI content generation", "blog writing"],
    "topic": "ALwrity content generation",
    "industry": "Technology",
    "target_audience": "content creators"
}

try:
    print("Sending request to research endpoint...")
    response = requests.post(url, json=payload, timeout=60)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n=== FULL RESPONSE ===")
        print(json.dumps(data, indent=2))
        
        # Check if we got the expected fields
        expected_fields = ['success', 'sources', 'keyword_analysis', 'competitor_analysis', 'suggested_angles', 'search_widget', 'search_queries']
        print(f"\n=== FIELD ANALYSIS ===")
        for field in expected_fields:
            value = data.get(field)
            if field == 'sources':
                print(f"{field}: {len(value) if value else 0} items")
            elif field == 'search_queries':
                print(f"{field}: {len(value) if value else 0} items")
            elif field == 'search_widget':
                print(f"{field}: {'Present' if value else 'Missing'}")
            else:
                print(f"{field}: {type(value).__name__} - {str(value)[:100]}...")
                
    else:
        print(f"Error Response: {response.text}")
        
except Exception as e:
    print(f"Request failed: {e}")
    import traceback
    traceback.print_exc()
