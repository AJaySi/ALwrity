#!/usr/bin/env python3
"""
API Key Manager Ollama Integration Test

This test verifies that the API key manager correctly detects and manages
Ollama availability and configuration.
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.api_key_manager import APIKeyManager

class TestAPIKeyManagerOllama:
    """Test API Key Manager Ollama integration."""
    
    def setup_method(self):
        """Set up test environment."""
        self.api_manager = APIKeyManager()
    
    def test_ollama_availability_check(self):
        """Test that the API key manager can check Ollama availability."""
        print("\n🔑 Testing Ollama availability check...")
        
        try:
            # Test the check_ollama_availability method
            is_available = self.api_manager.check_ollama_availability()
            
            print(f"   Ollama availability: {is_available}")
            
            # Should return a boolean
            assert isinstance(is_available, bool)
            
            if is_available:
                print("   ✅ Ollama is available and detected")
            else:
                print("   ⚠️  Ollama not available (this is OK if not installed)")
            
        except Exception as e:
            print(f"   ❌ Availability check failed: {e}")
            raise
    
    def test_api_key_loading_with_ollama(self):
        """Test API key loading includes Ollama endpoint."""
        print("\n🔑 Testing API key loading with Ollama...")
        
        try:
            # Load API keys (this method modifies self.api_keys in place)
            self.api_manager.load_api_keys()
            
            # Get the loaded API keys
            api_keys = self.api_manager.api_keys
            
            print(f"   Loaded API keys: {list(api_keys.keys())}")
            
            # Should be a dictionary
            assert isinstance(api_keys, dict)
            
            # If Ollama is available, should include ollama key
            if self.api_manager.check_ollama_availability():
                assert 'ollama' in api_keys
                assert api_keys['ollama'] == 'http://localhost:11434'
                print("   ✅ Ollama endpoint correctly included in API keys")
            else:
                print("   ⚠️  Ollama not available, skipping endpoint check")
            
        except Exception as e:
            print(f"   ❌ API key loading failed: {e}")
            raise

if __name__ == "__main__":
    # Run the tests directly
    test_instance = TestAPIKeyManagerOllama()
    
    print("=" * 60)
    print("         API KEY MANAGER OLLAMA TEST")
    print("=" * 60)
    
    try:
        test_instance.setup_method()
        test_instance.test_ollama_availability_check()
        test_instance.test_api_key_loading_with_ollama()
        
        print("\n✅ All API Key Manager tests passed!")
        
    except Exception as e:
        print(f"\n❌ API Key Manager tests failed: {e}")
        sys.exit(1)
