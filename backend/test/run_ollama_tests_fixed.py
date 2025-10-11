#!/usr/bin/env python3
"""
Fixed Ollama Test Runner for ALwrity

This script runs Ollama tests with proper import paths.
"""

import sys
import os
from pathlib import Path

def setup_paths():
    """Setup proper Python paths for imports."""
    # Get directories
    test_dir = Path(__file__).parent
    backend_dir = test_dir.parent
    project_root = backend_dir.parent
    
    # Add to Python path
    sys.path.insert(0, str(backend_dir))
    sys.path.insert(0, str(project_root))
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    print(f"Working directory: {os.getcwd()}")
    print(f"Python paths added: {backend_dir}, {project_root}")
    
    return test_dir, backend_dir, project_root

def check_ollama_basic():
    """Basic Ollama availability check."""
    print("🔍 Checking Ollama availability...")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama running with {len(models)} models")
            for model in models:
                print(f"   • {model['name']}")
            return True
        else:
            print("❌ Ollama not responding")
            return False
    except Exception as e:
        print(f"❌ Ollama check failed: {e}")
        return False

def test_api_key_manager():
    """Test API key manager integration."""
    print("\n🧪 Testing API Key Manager...")
    
    try:
        from services.api_key_manager import APIKeyManager
        
        api_manager = APIKeyManager()
        api_manager.load_api_keys()
        
        # Check Ollama detection
        if hasattr(api_manager, 'check_ollama_availability'):
            if api_manager.check_ollama_availability():
                print("✅ API key manager detects Ollama")
                return True
            else:
                print("❌ API key manager doesn't detect Ollama")
                return False
        else:
            print("⚠️  API key manager missing Ollama check method")
            return False
            
    except Exception as e:
        print(f"❌ API key manager test failed: {e}")
        return False

def test_model_selector():
    """Test smart model selector."""
    print("\n🧪 Testing Smart Model Selector...")
    
    try:
        from services.llm_providers.smart_model_selector import get_model_selector, TaskType
        
        selector = get_model_selector()
        available_providers = ["ollama"]
        
        provider, model = selector.select_model_for_task(TaskType.ANALYSIS, available_providers)
        
        if provider == "ollama":
            print(f"✅ Model selector works: {provider}:{model}")
            return True
        else:
            print(f"❌ Model selector chose wrong provider: {provider}")
            return False
            
    except Exception as e:
        print(f"❌ Model selector test failed: {e}")
        return False

def test_ollama_provider():
    """Test Ollama provider directly."""
    print("\n🧪 Testing Ollama Provider...")
    
    try:
        from services.llm_providers.ollama_provider import ollama_text_response, check_ollama_availability
        
        if not check_ollama_availability():
            print("❌ Ollama not available for provider test")
            return False
        
        # Test text generation using the function directly
        response = ollama_text_response(
            prompt="What is 2+2? Answer in one word.",
            model="qwen3:0.6b"
        )
        
        if response and len(response.strip()) > 0:
            print(f"✅ Ollama provider works: {response.strip()[:30]}...")
            return True
        else:
            print("❌ Ollama provider returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Ollama provider test failed: {e}")
        return False

def test_main_generation():
    """Test main text generation service."""
    print("\n🧪 Testing Main Text Generation...")
    
    try:
        # Set environment for local AI preference
        os.environ['PREFER_LOCAL_AI'] = 'true'
        os.environ['OLLAMA_ENDPOINT'] = 'http://localhost:11434'
        
        from services.llm_providers.main_text_generation import llm_analysis_gen
        
        response = llm_analysis_gen("What is the weather like? Answer briefly.")
        
        if response and len(response.strip()) > 0:
            print(f"✅ Main generation works: {response.strip()[:50]}...")
            return True
        else:
            print("❌ Main generation returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Main generation test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests in sequence."""
    print("=" * 60)
    print("        OLLAMA INTEGRATION TEST RUNNER")
    print("=" * 60)
    
    # Setup paths
    test_dir, backend_dir, project_root = setup_paths()
    
    # Set environment
    os.environ['PREFER_LOCAL_AI'] = 'true'
    os.environ['OLLAMA_ENDPOINT'] = 'http://localhost:11434'
    
    tests = [
        ("Ollama Basic", check_ollama_basic),
        ("API Key Manager", test_api_key_manager),
        ("Model Selector", test_model_selector),
        ("Ollama Provider", test_ollama_provider),
        ("Main Generation", test_main_generation),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("                    TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ollama integration is working perfectly.")
    elif passed >= total * 0.8:
        print("✅ Most tests passed. Minor issues may exist.")
    else:
        print("❌ Multiple tests failed. Check your Ollama setup.")
        print("\n🔧 Troubleshooting:")
        print("   • Ensure Ollama is running: ollama serve")
        print("   • Download a model: ollama pull qwen3:0.6b")
        print("   • Check models: ollama list")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)