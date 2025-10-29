# Hugging Face Integration for AI Blog Writer

## Overview

The AI Blog Writer now supports both Google Gemini and Hugging Face as LLM providers, with a clean environment variable-based configuration system. This integration uses the [Hugging Face Responses API](https://huggingface.co/docs/inference-providers/guides/responses-api) which provides a unified interface for model interactions.

## Supported Providers

### 1. Google Gemini (Default)
- **Provider ID**: `google`
- **Environment Variable**: `GEMINI_API_KEY`
- **Models**: `gemini-2.0-flash-001`
- **Features**: Text generation, structured JSON output

### 2. Hugging Face
- **Provider ID**: `huggingface`
- **Environment Variable**: `HF_TOKEN`
- **Models**: Multiple models via Inference Providers
- **Features**: Text generation, structured JSON output, multi-model support

## Configuration

### Environment Variables

Set the `GPT_PROVIDER` environment variable to choose your preferred provider:

```bash
# Use Google Gemini (default)
export GPT_PROVIDER=gemini
# or
export GPT_PROVIDER=google

# Use Hugging Face
export GPT_PROVIDER=hf_response_api
# or
export GPT_PROVIDER=huggingface
# or
export GPT_PROVIDER=hf
```

### API Keys

Configure the appropriate API key for your chosen provider:

```bash
# For Google Gemini
export GEMINI_API_KEY=your_gemini_api_key_here

# For Hugging Face
export HF_TOKEN=your_huggingface_token_here
```

## Usage

### Basic Text Generation

```python
from services.llm_providers.main_text_generation import llm_text_gen

# Generate text (uses configured provider)
response = llm_text_gen("Write a blog post about AI trends")
print(response)
```

### Structured JSON Generation

```python
from services.llm_providers.main_text_generation import llm_text_gen

# Define JSON schema
schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "heading": {"type": "string"},
                    "content": {"type": "string"}
                }
            }
        }
    }
}

# Generate structured response
response = llm_text_gen(
    "Create a blog outline about machine learning",
    json_struct=schema
)
print(response)
```

### Direct Provider Usage

```python
# Google Gemini
from services.llm_providers.gemini_provider import gemini_text_response

response = gemini_text_response(
    prompt="Write about AI",
    temperature=0.7,
    max_tokens=1000
)

# Hugging Face
from services.llm_providers.huggingface_provider import huggingface_text_response

response = huggingface_text_response(
    prompt="Write about AI",
    model="openai/gpt-oss-120b:groq",
    temperature=0.7,
    max_tokens=1000
)
```

## Available Hugging Face Models

The Hugging Face provider supports multiple models via Inference Providers:

- `openai/gpt-oss-120b:groq` (default)
- `moonshotai/Kimi-K2-Instruct-0905:groq`
- `Qwen/Qwen2.5-VL-7B-Instruct`
- `meta-llama/Llama-3.1-8B-Instruct:groq`
- `microsoft/Phi-3-medium-4k-instruct:groq`
- `mistralai/Mistral-7B-Instruct-v0.3:groq`

## Provider Selection Logic

1. **Environment Variable**: If `GPT_PROVIDER` is set, use the specified provider
2. **Auto-detection**: If no environment variable, check available API keys:
   - Prefer Google Gemini if `GEMINI_API_KEY` is available
   - Fall back to Hugging Face if `HF_TOKEN` is available
3. **Fallback**: If the specified provider fails, automatically try the other provider

## Error Handling

The system includes comprehensive error handling:

- **Missing API Keys**: Clear error messages with setup instructions
- **Provider Failures**: Automatic fallback to the other provider
- **Invalid Models**: Validation with helpful error messages
- **Network Issues**: Retry logic with exponential backoff

## Migration from Previous Version

### Removed Providers
The following providers have been removed to simplify the system:
- OpenAI
- Anthropic
- DeepSeek

### Updated Imports
```python
# Old imports (no longer work)
from services.llm_providers.openai_provider import openai_chatgpt
from services.llm_providers.anthropic_provider import anthropic_text_response
from services.llm_providers.deepseek_provider import deepseek_text_response

# New imports
from services.llm_providers.gemini_provider import gemini_text_response, gemini_structured_json_response
from services.llm_providers.huggingface_provider import huggingface_text_response, huggingface_structured_json_response
```

## Testing

Run the integration tests to verify everything works:

```bash
cd backend
python -c "
import sys
sys.path.insert(0, '.')
from services.llm_providers.main_text_generation import check_gpt_provider
print('Google provider supported:', check_gpt_provider('google'))
print('Hugging Face provider supported:', check_gpt_provider('huggingface'))
print('OpenAI provider supported:', check_gpt_provider('openai'))
"
```

## Performance Considerations

### Google Gemini
- Fast response times
- High-quality outputs
- Good for structured content

### Hugging Face
- Multiple model options
- Cost-effective for high-volume usage
- Good for experimentation with different models

## Troubleshooting

### Common Issues

1. **"No LLM API keys configured"**
   - Ensure either `GEMINI_API_KEY` or `HF_TOKEN` is set
   - Check that the API key is valid

2. **"Unknown LLM provider"**
   - Use only `google` or `huggingface` as provider values
   - Check the `GPT_PROVIDER` environment variable

3. **"HF_TOKEN appears to be invalid"**
   - Ensure your Hugging Face token starts with `hf_`
   - Get a new token from [Hugging Face Settings](https://huggingface.co/settings/tokens)

4. **"OpenAI library not available"**
   - Install the OpenAI library: `pip install openai`
   - This is required for Hugging Face Responses API

### Debug Mode

Enable debug logging to see provider selection:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- Support for additional Hugging Face models
- Model-specific parameter optimization
- Advanced caching strategies
- Performance monitoring and metrics
- A/B testing between providers

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the [Hugging Face Responses API documentation](https://huggingface.co/docs/inference-providers/guides/responses-api)
3. Check the Google Gemini API documentation for Gemini-specific issues
