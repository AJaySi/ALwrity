# LLM Providers Module

This module provides functions for interacting with multiple LLM providers, specifically Google's Gemini API and Hugging Face Inference Providers. It follows official API documentation and implements best practices for reliable AI interactions.

## Supported Providers

- **Google Gemini**: High-quality text generation with structured JSON output
- **Hugging Face**: Multiple models via Inference Providers with unified interface

## Quick Start

```python
from services.llm_providers.main_text_generation import llm_text_gen

# Generate text (auto-detects available provider)
response = llm_text_gen("Write a blog post about AI trends")
print(response)
```

## Configuration

Set your preferred provider using the `GPT_PROVIDER` environment variable:

```bash
# Use Google Gemini (default)
export GPT_PROVIDER=gemini

# Use Hugging Face
export GPT_PROVIDER=hf_response_api
```

Configure API keys:

```bash
# For Google Gemini
export GEMINI_API_KEY=your_gemini_api_key_here

# For Hugging Face
export HF_TOKEN=your_huggingface_token_here
```

## Key Features

- **Structured JSON Response Generation**: Generate structured outputs with schema validation
- **Text Response Generation**: Simple text generation with retry logic
- **Comprehensive Error Handling**: Robust error handling and logging
- **Automatic API Key Management**: Secure API key handling
- **Support for Multiple Models**: gemini-2.5-flash and gemini-2.5-pro

## Best Practices

### 1. Use Structured Output for Complex Responses
```python
# ✅ Good: Use structured output for multi-field responses
schema = {
    "type": "object",
    "properties": {
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"}
                }
            }
        }
    }
}
result = gemini_structured_json_response(prompt, schema, temperature=0.2, max_tokens=8192)
```

### 2. Keep Schemas Simple and Flat
```python
# ✅ Good: Simple, flat schema
schema = {
    "type": "object",
    "properties": {
        "monitoringTasks": {
            "type": "array",
            "items": {"type": "object", "properties": {...}}
        }
    }
}

# ❌ Avoid: Complex nested schemas with many required fields
schema = {
    "type": "object",
    "required": ["field1", "field2", "field3"],
    "properties": {
        "field1": {"type": "object", "required": [...], "properties": {...}},
        "field2": {"type": "array", "items": {"type": "object", "required": [...], "properties": {...}}}
    }
}
```

### 3. Set Appropriate Token Limits
```python
# ✅ Good: Use 8192 tokens for complex outputs
result = gemini_structured_json_response(prompt, schema, max_tokens=8192)

# ✅ Good: Use 2048 tokens for simple text responses
result = gemini_text_response(prompt, max_tokens=2048)
```

### 4. Use Low Temperature for Structured Output
```python
# ✅ Good: Low temperature for consistent structured output
result = gemini_structured_json_response(prompt, schema, temperature=0.1, max_tokens=8192)

# ✅ Good: Higher temperature for creative text
result = gemini_text_response(prompt, temperature=0.8, max_tokens=2048)
```

### 5. Implement Proper Error Handling
```python
# ✅ Good: Handle errors in calling functions
try:
    response = gemini_structured_json_response(prompt, schema)
    if isinstance(response, dict) and "error" in response:
        raise Exception(f"Gemini error: {response.get('error')}")
    # Process successful response
except Exception as e:
    logger.error(f"AI service error: {e}")
    # Handle error appropriately
```

### 6. Avoid Fallback to Text Parsing
```python
# ✅ Good: Use structured output only, no fallback
response = gemini_structured_json_response(prompt, schema)
if "error" in response:
    raise Exception(f"Gemini error: {response.get('error')}")

# ❌ Avoid: Fallback to text parsing for structured responses
# This can lead to inconsistent results and parsing errors
```

## Usage Examples

### Structured JSON Response
```python
from services.llm_providers.gemini_provider import gemini_structured_json_response

# Define schema
monitoring_schema = {
    "type": "object",
    "properties": {
        "monitoringTasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "component": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "assignee": {"type": "string"},
                    "frequency": {"type": "string"},
                    "metric": {"type": "string"},
                    "measurementMethod": {"type": "string"},
                    "successCriteria": {"type": "string"},
                    "alertThreshold": {"type": "string"},
                    "actionableInsights": {"type": "string"}
                }
            }
        }
    }
}

# Generate structured response
prompt = "Generate a monitoring plan for content strategy..."
result = gemini_structured_json_response(
    prompt=prompt,
    schema=monitoring_schema,
    temperature=0.1,
    max_tokens=8192
)

# Handle response
if isinstance(result, dict) and "error" in result:
    raise Exception(f"Gemini error: {result.get('error')}")

# Process successful response
monitoring_tasks = result.get("monitoringTasks", [])
```

### Text Response
```python
from services.llm_providers.gemini_provider import gemini_text_response

# Generate text response
prompt = "Write a blog post about AI in content marketing..."
result = gemini_text_response(
    prompt=prompt,
    temperature=0.8,
    max_tokens=2048
)

# Process response
if result:
    print(f"Generated text: {result}")
else:
    print("No response generated")
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Response.parsed is None
**Symptoms**: `response.parsed` returns `None` even with successful HTTP 200
**Causes**: 
- Schema too complex for the model
- Token limit too low
- Temperature too high for structured output

**Solutions**:
- Simplify schema structure
- Increase `max_tokens` to 8192
- Lower temperature to 0.1-0.3
- Test with smaller outputs first

#### 2. JSON Parsing Fails
**Symptoms**: `JSONDecodeError` or "Unterminated string" errors
**Causes**:
- Response truncated due to token limits
- Schema doesn't match expected output
- Model generates malformed JSON

**Solutions**:
- Reduce output size requested
- Verify schema matches expected structure
- Use structured output instead of text parsing
- Increase token limits

#### 3. Truncation Issues
**Symptoms**: Response cuts off mid-sentence or mid-array
**Causes**:
- Output too large for single response
- Token limits exceeded

**Solutions**:
- Reduce number of items requested
- Increase `max_tokens` to 8192
- Break large requests into smaller chunks
- Use `gemini-2.5-pro` for larger outputs

#### 4. Rate Limiting
**Symptoms**: `RetryError` or connection timeouts
**Causes**:
- Too many requests in short time
- Network connectivity issues

**Solutions**:
- Exponential backoff already implemented
- Check network connectivity
- Reduce request frequency
- Verify API key validity

### Debug Logging

The module includes comprehensive debug logging. Enable debug mode to see:

```python
import logging
logging.getLogger('services.llm_providers.gemini_provider').setLevel(logging.DEBUG)
```

Key log messages to monitor:
- `Gemini structured call | prompt_len=X | schema_kind=Y | temp=Z`
- `Gemini response | type=X | has_text=Y | has_parsed=Z`
- `Using response.parsed for structured output`
- `Falling back to response.text parsing`

## API Reference

### gemini_structured_json_response()

Generate structured JSON response using Google's Gemini Pro model.

**Parameters**:
- `prompt` (str): Input prompt for the AI model
- `schema` (dict): JSON schema defining expected output structure
- `temperature` (float): Controls randomness (0.0-1.0). Use 0.1-0.3 for structured output
- `top_p` (float): Nucleus sampling parameter (0.0-1.0)
- `top_k` (int): Top-k sampling parameter
- `max_tokens` (int): Maximum tokens in response. Use 8192 for complex outputs
- `system_prompt` (str, optional): System instruction for the model

**Returns**:
- `dict`: Parsed JSON response matching the provided schema

**Raises**:
- `Exception`: If API key is missing or API call fails

### gemini_text_response()

Generate text response using Google's Gemini Pro model.

**Parameters**:
- `prompt` (str): Input prompt for the AI model
- `temperature` (float): Controls randomness (0.0-1.0). Higher = more creative
- `top_p` (float): Nucleus sampling parameter (0.0-1.0)
- `n` (int): Number of responses to generate
- `max_tokens` (int): Maximum tokens in response
- `system_prompt` (str, optional): System instruction for the model

**Returns**:
- `str`: Generated text response

**Raises**:
- `Exception`: If API key is missing or API call fails

## Dependencies

- `google.generativeai` (genai): Official Gemini API client
- `tenacity`: Retry logic with exponential backoff
- `logging`: Debug and error logging
- `json`: Fallback JSON parsing
- `re`: Text extraction utilities

## Version History

- **v2.0** (January 2025): Enhanced structured output support, improved error handling, comprehensive documentation
- **v1.0**: Initial implementation with basic text and structured response support

## Contributing

When contributing to this module:

1. Follow the established patterns for error handling
2. Add comprehensive logging for debugging
3. Test with both simple and complex schemas
4. Update documentation for any new features
5. Ensure backward compatibility

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review debug logs for specific error messages
3. Test with simplified schemas to isolate issues
4. Verify API key configuration and network connectivity
