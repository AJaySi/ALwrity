import asyncio
from services.llm_providers.gemini_provider import gemini_structured_json_response

async def test_simple_schema():
    """Test with a very simple schema to see if structured output works at all"""
    
    # Very simple schema
    simple_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        }
    }
    
    simple_prompt = "Generate a person with a name and age."
    
    print("Testing simple schema...")
    print(f"Schema: {simple_schema}")
    print(f"Prompt: {simple_prompt}")
    print("\n" + "="*50 + "\n")
    
    try:
        result = gemini_structured_json_response(
            prompt=simple_prompt,
            schema=simple_schema,
            temperature=0.3,
            max_tokens=100
        )
        
        print("Result:")
        print(result)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_schema())
