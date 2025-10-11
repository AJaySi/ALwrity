# Ollama Integration Test Suite

This directory contains comprehensive tests for the Ollama integration in ALwrity. The test suite validates local AI model functionality, performance, and integration with ALwrity services.

## Quick Start

### 1. Prerequisites

- Ollama installed and running (`ollama serve`)
- At least one model downloaded (`ollama pull qwen3:0.6b`)
- ALwrity backend environment configured

### 2. Quick Test (30 seconds)

```bash
cd "E:\E Stuff\Projects\ALwrity"
python backend\test\simple_ollama_test.py
```

### 3. Full Test Suite (5 minutes)

```bash
python backend\test\run_ollama_tests_fixed.py
```

## Test Files Overview

| File                                         | Purpose              | Duration | When to Use                |
| -------------------------------------------- | -------------------- | -------- | -------------------------- |
| `simple_ollama_test.py`                      | Basic connectivity   | 30s      | Initial setup verification |
| `quick_ollama_test.py`                       | Core functionality   | 2-3 min  | Development quick checks   |
| `run_ollama_tests_fixed.py`                  | Complete suite       | 5 min    | Pre-commit validation      |
| `test_ollama_comprehensive.py`               | Detailed integration | 3-4 min  | Deep testing               |
| `test_api_key_manager_ollama_integration.py` | API key manager      | 1 min    | Configuration testing      |
| `test_smart_model_selector_functionality.py` | Model selection      | 1-2 min  | Model routing testing      |

## Expected Results

### ✅ All Tests Passing

```
📊 Overall Result: 5/5 tests passed
🎉 All tests passed! Ollama integration is working perfectly.
```

### ⚠️ Partial Success

```
📊 Overall Result: 3/5 tests passed
⚠️ Most tests passed. Some minor issues detected.
```

### ❌ Tests Failing

```
📊 Overall Result: 1/5 tests passed
❌ Multiple tests failed. Check your Ollama setup.
```

## Common Issues & Solutions

### Issue: "Ollama not available"

**Solution**: Start Ollama service

```bash
ollama serve
```

### Issue: "No models found"

**Solution**: Download a model

```bash
ollama pull qwen3:0.6b
ollama list  # Verify installation
```

### Issue: "No module named 'services'"

**Solution**: Run from correct directory

```bash
cd "E:\E Stuff\Projects\ALwrity"  # Project root
python backend\test\<test_file>.py
```

### Issue: "Import errors"

**Solution**: Check Python environment

```bash
# Ensure you're in the backend directory context
cd backend
python test\<test_file>.py
```

## Test Coverage

The test suite validates:

- ✅ **Service Connectivity**: Ollama API availability and response
- ✅ **Model Management**: Model listing, selection, and validation
- ✅ **Text Generation**: Basic and structured text generation
- ✅ **Smart Selection**: Task-based automatic model selection
- ✅ **API Integration**: ALwrity service integration points
- ✅ **Error Handling**: Graceful failure and retry scenarios
- ✅ **Performance**: Response time and efficiency metrics

## Performance Benchmarks

### Response Times (qwen3:0.6b model)

- **Simple queries**: 5-15 seconds
- **Analysis tasks**: 15-30 seconds
- **Complex reasoning**: 30-60 seconds
- **Long-form content**: 60-120 seconds

### Model Recommendations

```bash
# Lightweight (development)
ollama pull qwen3:0.6b

# Balanced (production)
ollama pull llama3.2:3b

# High quality (when resources allow)
ollama pull llama3.1:8b
```

## Troubleshooting

### 1. Check Ollama Status

```bash
# Is Ollama running?
curl http://localhost:11434/api/tags

# List available models
ollama list

# Test a model directly
ollama run qwen3:0.6b "Hello"
```

### 2. Check ALwrity Configuration

```bash
# Verify environment variables
cat backend/.env | grep OLLAMA

# Should show:
# OLLAMA_ENDPOINT=http://localhost:11434
# PREFER_LOCAL_AI=true
```

### 3. Check Python Environment

```bash
# Verify working directory
pwd
# Should be in ALwrity project root

# Check Python path includes backend
python -c "import sys; print('\n'.join(sys.path))"
```

### 4. Manual Integration Test

```python
# Test basic integration manually
cd backend
python -c "
from services.llm_providers.main_text_generation import llm_analysis_gen
result = llm_analysis_gen('What is 2+2?')
print(f'Result: {result[:100]}...')
"
```

## Development Workflow

### 1. Before Starting Development

```bash
python backend\test\simple_ollama_test.py
```

### 2. During Development

```bash
python backend\test\quick_ollama_test.py
```

### 3. Before Committing

```bash
python backend\test\run_ollama_tests_fixed.py
```

### 4. For Deep Debugging

```bash
python backend\test\test_ollama_comprehensive.py
```

## Adding New Tests

1. **Follow naming convention**: `test_ollama_<component>.py`
2. **Include proper imports**: Add backend to Python path
3. **Test isolation**: Each test should be independent
4. **Error handling**: Test both success and failure scenarios
5. **Documentation**: Clear test purpose and expected behavior

## Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Test Ollama Integration
  run: |
    ollama serve &
    ollama pull qwen3:0.6b
    python backend/test/run_ollama_tests_fixed.py
```

## Support

### Documentation

- **Full Guide**: `docs/OLLAMA_INTEGRATION_GUIDE.md`
- **Testing Details**: `docs/OLLAMA_TESTING_GUIDE.md`

### Common Commands

```bash
# Quick status check
python backend\test\simple_ollama_test.py

# Full validation
python backend\test\run_ollama_tests_fixed.py

# Component-specific testing
python backend\test\test_smart_model_selector_functionality.py

# Performance benchmarking
python backend\test\test_ollama_comprehensive.py
```

---

_For detailed testing documentation, see [OLLAMA_TESTING_GUIDE.md](../docs/OLLAMA_TESTING_GUIDE.md)_
