# Ollama Integration Guide for ALwrity

## Overview

ALwrity now supports **Ollama** for running open-source AI models locally, providing users with free, private, and cost-effective AI capabilities. This integration enables ALwrity to leverage models like Llama, Gemma, DeepSeek, and others directly on the user's machine.

## Key Benefits

### 1. **Cost Savings**

- Zero API costs for AI model usage
- No per-token or per-request charges
- Eliminates ongoing cloud AI expenses

### 2. **Data Privacy**

- All AI processing happens locally
- No data sent to external servers
- Complete control over sensitive content

### 3. **Performance Optimization**

- Smart model selection based on task requirements
- Smaller models for analysis tasks (faster)
- Larger models for complex reasoning (better quality)

### 4. **Offline Capability**

- Works without internet connection (after initial setup)
- No dependency on cloud service availability
- Reduced latency for local processing

## Architecture

### Smart Model Selection System

ALwrity uses an intelligent model selection system that matches the right model to each task:

#### Task Categories:

1. **Analysis Tasks** (`analysis`, `seo_analysis`, `content_classification`)

   - **Models**: `llama3.2:3b`, `gemma2:2b`
   - **Focus**: Speed and efficiency
   - **Use Cases**: SEO analysis, data processing, content classification

2. **Reasoning Tasks** (`reasoning`, `blog_writing`, `social_media`)

   - **Models**: `llama3.1:8b`, `qwen2.5:7b`
   - **Focus**: Balanced performance and quality
   - **Use Cases**: Blog writing, general content creation, social media posts

3. **Complex Tasks** (`complex`, `research`, `strategy`)

   - **Models**: `llama3.1:70b`, `qwen2.5:14b`
   - **Focus**: Advanced reasoning and comprehensive knowledge
   - **Use Cases**: Research, strategic planning, complex analysis

4. **Coding Tasks** (`coding`)

   - **Models**: `deepseek-coder:6.7b`, `codellama`
   - **Focus**: Code understanding and generation
   - **Use Cases**: API documentation, technical writing, code examples

5. **Creative Tasks** (`creative`, `marketing`)
   - **Models**: `gemma2:9b`, `llama3.1:8b`
   - **Focus**: Language fluency and creativity
   - **Use Cases**: Marketing copy, creative writing, brand content

### Provider Priority System

When multiple providers are available, ALwrity uses this priority order:

1. **Google Gemini** (if API key available) - High quality, good free tier
2. **Ollama** (if running locally) - Free, private, local processing
3. **OpenAI** (if API key available) - High quality, paid
4. **Anthropic** (if API key available) - High quality, paid
5. **DeepSeek** (if API key available) - Good quality, affordable

Users can override this by setting `PREFER_LOCAL_AI=true` to prioritize Ollama.

## Installation & Setup

### 1. Install Ollama

Visit [https://ollama.ai/](https://ollama.ai/) and install Ollama for your operating system.

### 2. Download Recommended Models

For optimal ALwrity performance, download these models:

```bash
# Essential models (recommended minimum)
ollama pull llama3.2:3b      # Fast analysis tasks
ollama pull llama3.1:8b      # General reasoning

# Additional models for better performance
ollama pull deepseek-coder:6.7b  # Coding tasks
ollama pull gemma2:9b            # Creative tasks
ollama pull llama3.1:70b         # Complex tasks (requires >32GB RAM)
```

### 3. Configure ALwrity

Add these settings to your `.env` file:

```env
# Ollama Configuration
OLLAMA_ENDPOINT=http://localhost:11434
PREFER_LOCAL_AI=true
MAX_COST_TIER=free
PERFORMANCE_PRIORITY=balanced
RESOURCE_LIMIT=medium
```

### 4. Verify Installation

ALwrity will automatically detect when Ollama is running and include it in available providers.

## Configuration Options

### Environment Variables

| Variable               | Default                  | Description                                       |
| ---------------------- | ------------------------ | ------------------------------------------------- |
| `OLLAMA_ENDPOINT`      | `http://localhost:11434` | Ollama API endpoint                               |
| `PREFER_LOCAL_AI`      | `true`                   | Prioritize local models over cloud                |
| `MAX_COST_TIER`        | `free`                   | Maximum cost tier (`free` or `paid`)              |
| `PERFORMANCE_PRIORITY` | `balanced`               | Priority (`speed`, `quality`, `cost`, `balanced`) |
| `RESOURCE_LIMIT`       | `medium`                 | Resource limit (`low`, `medium`, `high`)          |

### Resource Requirements by Model

| Model                 | RAM Required | Resource Level | Speed      | Quality    |
| --------------------- | ------------ | -------------- | ---------- | ---------- |
| `llama3.2:3b`         | 4GB          | Low            | ⭐⭐⭐⭐⭐ | ⭐⭐⭐     |
| `llama3.1:8b`         | 8GB          | Medium         | ⭐⭐⭐⭐   | ⭐⭐⭐⭐   |
| `gemma2:9b`           | 12GB         | Medium         | ⭐⭐⭐     | ⭐⭐⭐⭐   |
| `deepseek-coder:6.7b` | 8GB          | Medium         | ⭐⭐⭐     | ⭐⭐⭐⭐⭐ |
| `llama3.1:70b`        | 40GB         | High           | ⭐⭐       | ⭐⭐⭐⭐⭐ |

## Usage Examples

### Basic Usage (Automatic Model Selection)

```python
from backend.services.llm_providers.main_text_generation import llm_text_gen

# ALwrity automatically selects the best available model
result = llm_text_gen("Write a blog post about AI trends")
```

### Task-Specific Functions

```python
from backend.services.llm_providers.main_text_generation import (
    llm_analysis_gen,
    llm_creative_gen,
    llm_coding_gen,
    llm_complex_gen,
    llm_cost_optimized_gen
)

# Fast analysis (uses small, efficient models)
seo_analysis = llm_analysis_gen("Analyze the SEO of this webpage")

# Creative content (uses models optimized for creativity)
marketing_copy = llm_creative_gen("Create a product launch campaign")

# Coding tasks (uses code-specialized models)
api_docs = llm_coding_gen("Generate API documentation for this endpoint")

# Complex research (uses large, capable models)
research = llm_complex_gen("Conduct comprehensive market analysis")

# Cost-optimized (prioritizes free/local models)
content = llm_cost_optimized_gen("Write a social media post")
```

### Manual Model Selection

```python
# Specify task type and priority
result = llm_text_gen(
    prompt="Analyze this data",
    task_type="analysis",
    priority="speed"  # Options: "speed", "quality", "cost", "balanced"
)
```

## Model Management

### Checking Available Models

```python
from backend.services.llm_providers.ollama_provider import get_available_models

models = get_available_models()
print(f"Available models: {models}")
```

### Model Recommendations

```python
from backend.services.llm_providers.ollama_provider import suggest_models_for_download

suggestions = suggest_models_for_download()
for task, command in suggestions.items():
    print(f"{task}: {command}")
```

## Performance Optimization

### System Requirements

| Use Case         | Minimum RAM | Recommended RAM | Models                                 |
| ---------------- | ----------- | --------------- | -------------------------------------- |
| **Basic**        | 8GB         | 16GB            | `llama3.2:3b`, `llama3.1:8b`           |
| **Professional** | 16GB        | 32GB            | Add `gemma2:9b`, `deepseek-coder:6.7b` |
| **Enterprise**   | 32GB        | 64GB+           | Add `llama3.1:70b`, `qwen2.5:14b`      |

### Optimization Tips

1. **Start Small**: Begin with `llama3.2:3b` and `llama3.1:8b`
2. **Monitor Resources**: Check RAM usage when running larger models
3. **Task Matching**: Use analysis functions for simple tasks, complex functions for research
4. **Batch Processing**: Group similar tasks together for efficiency
5. **Model Preloading**: Keep frequently used models loaded in Ollama

## Troubleshooting

### Common Issues

#### 1. Ollama Not Detected

```
Error: Ollama is not available. Please ensure Ollama is installed and running.
```

**Solution**:

- Verify Ollama is installed: `ollama --version`
- Start Ollama service: `ollama serve`
- Check endpoint: `curl http://localhost:11434/api/tags`

#### 2. Model Not Available

```
Error: Requested model llama3.1:8b not available, auto-selecting
```

**Solution**:

- Download the model: `ollama pull llama3.1:8b`
- Check available models: `ollama list`

#### 3. Out of Memory

```
Error: Failed to load model (insufficient memory)
```

**Solution**:

- Use smaller models: `llama3.2:3b` instead of `llama3.1:70b`
- Set `RESOURCE_LIMIT=low` in environment
- Close other applications to free RAM

#### 4. Slow Performance

**Solution**:

- Use analysis functions for simple tasks
- Set `PERFORMANCE_PRIORITY=speed`
- Use smaller models for non-critical tasks
- Ensure sufficient RAM available

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Check model selection process
result = llm_text_gen("test", task_type="analysis")
```

## Migration Guide

### From Cloud-Only to Hybrid

1. **Install Ollama** and basic models
2. **Set `PREFER_LOCAL_AI=true`** in environment
3. **Keep existing API keys** for fallback
4. **Monitor performance** and adjust model selection

### Gradual Adoption

1. **Week 1**: Install and test with analysis tasks
2. **Week 2**: Add reasoning tasks with medium models
3. **Week 3**: Download specialized models for coding/creative tasks
4. **Week 4**: Evaluate cost savings and performance gains

## Future Enhancements

### Planned Features

1. **Fine-tuning Support**: Custom models trained on user data
2. **Model Ensemble**: Combining multiple models for better results
3. **Automatic Model Management**: Download models based on usage patterns
4. **Performance Analytics**: Track model performance and costs
5. **GPU Acceleration**: Support for CUDA/Metal acceleration

### Ollama + Unsloth Integration

Future versions will integrate with Unsloth for:

- **Custom Model Training**: Train models on user's content and data
- **Domain Specialization**: Create marketing-specific AI models
- **Performance Optimization**: Fine-tuned models for specific ALwrity tasks

## Support

### Community Resources

- **Ollama Documentation**: [https://ollama.ai/docs](https://ollama.ai/docs)
- **Model Library**: [https://ollama.ai/library](https://ollama.ai/library)
- **ALwrity Issues**: [GitHub Issues](https://github.com/Ratna-Babu/ALwrity/issues)

### Getting Help

1. **Check this guide** for common solutions
2. **Enable debug logging** to identify issues
3. **Test with simple models** first
4. **Report issues** with detailed error messages and system specs

---

_Last updated: October 10, 2025_
