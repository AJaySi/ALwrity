# Ollama Integration - Quick Reference Card

## 🚀 Essential Commands

```bash
# Start Ollama
ollama serve

# Download models
ollama pull qwen3:0.6b        # Lightweight (600MB)
ollama pull llama3.2:3b       # Balanced (2GB)
ollama pull llama3.1:8b       # High quality (4.7GB)

# Check status
ollama list
curl http://localhost:11434/api/tags

# Quick test
cd "E:\E Stuff\Projects\ALwrity"
python backend\test\simple_ollama_test.py

# Full validation
python backend\test\run_ollama_tests_fixed.py
```

## 📋 Test Files Cheat Sheet

| Command                                         | Duration | Purpose             |
| ----------------------------------------------- | -------- | ------------------- |
| `python backend\test\simple_ollama_test.py`     | 30s      | Basic connectivity  |
| `python backend\test\quick_ollama_test.py`      | 2-3 min  | Core functionality  |
| `python backend\test\run_ollama_tests_fixed.py` | 5 min    | Complete validation |

## 🔧 Common Issues

| Error                      | Solution                 |
| -------------------------- | ------------------------ |
| "Connection refused"       | `ollama serve`           |
| "No models found"          | `ollama pull qwen3:0.6b` |
| "No module named services" | Run from project root    |
| Slow performance           | Use smaller model        |

## 📊 Expected Results

### ✅ Success Output

```
📊 Overall Result: 5/5 tests passed
🎉 All tests passed! Ollama integration is working perfectly.
```

### ⚠️ Partial Success

```
📊 Overall Result: 3/5 tests passed
⚠️ Most tests passed. Some minor issues detected.
```

## 🎯 Performance Targets

- **Simple queries**: < 30 seconds
- **Analysis tasks**: < 60 seconds
- **Memory usage**: < 8GB
- **Error rate**: < 5%

## 📚 Documentation Links

- **Setup Guide**: `docs/OLLAMA_INTEGRATION_GUIDE.md`
- **Testing Guide**: `docs/OLLAMA_TESTING_GUIDE.md`
- **Test README**: `backend/test/README_OLLAMA_TESTS.md`
- **Summary**: `docs/OLLAMA_DOCUMENTATION_SUMMARY.md`

---

_Keep this reference handy for daily Ollama development!_
