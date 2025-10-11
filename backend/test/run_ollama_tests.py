#!/usr/bin/env python3
"""
Ollama Test Runner for ALwrity

This script runs all Ollama-related tests in the correct order and provides
a comprehensive report of the integration status.

Usage:
    python run_ollama_tests.py [--quick] [--verbose] [--setup-only]
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path
import time

# Add backend to path - fix import paths
backend_dir = Path(__file__).parent.parent  # Go up to backend directory
test_dir = Path(__file__).parent  # test directory
project_root = backend_dir.parent  # Project root

# Add paths for imports
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(project_root))

# Set working directory to backend for proper relative imports
os.chdir(backend_dir)

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"{'':^60}")
    print(f"{title:^60}")
    print(f"{'':^60}")
    print(f"{'='*60}")

def print_section(title):
    """Print a section header."""
    print(f"\n{'-'*40} {title} {'-'*40}")

def check_prerequisites():
    """Check if all prerequisites are met."""
    print_section("Prerequisites Check")
    
    issues = []
    
    # Check if Ollama is installed
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Ollama is installed")
        else:
            issues.append("Ollama command failed")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        issues.append("Ollama is not installed or not in PATH")
    
    # Check if Ollama is running
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama service is running")
        else:
            issues.append("Ollama service is not responding")
    except Exception:
        issues.append("Ollama service is not running")
    
    # Check if models are available
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print(f"✅ Found {len(models)} Ollama models")
                for model in models[:3]:  # Show first 3 models
                    print(f"   • {model['name']}")
                if len(models) > 3:
                    print(f"   ... and {len(models) - 3} more")
            else:
                issues.append("No Ollama models found")
    except Exception:
        issues.append("Could not check available models")
    
    # Check Python dependencies
    try:
        import requests
        print("✅ requests library available")
    except ImportError:
        issues.append("requests library not available")
    
    try:
        import pytest
        print("✅ pytest available")
    except ImportError:
        print("⚠️  pytest not available (optional)")
    
    return issues

def run_setup_test():
    """Run the setup test."""
    print_section("Setup Test")
    
    try:
        # Check if setup script exists and try to import
        setup_script_path = backend_dir / "scripts" / "setup_ollama.py"
        if not setup_script_path.exists():
            print("⚠️  Setup script not found - skipping setup test")
            return True
        
        # Import and run setup verification
        from scripts.setup_ollama import check_ollama_installed, check_ollama_running, get_installed_models
        
        print("🔧 Running setup verification...")
        
        if not check_ollama_installed():
            return False
        
        if not check_ollama_running():
            return False
        
        models = get_installed_models()
        if models:
            print(f"✅ Setup verification passed - {len(models)} models available")
            return True
        else:
            print("⚠️  Setup verification: No models available")
            return False
            
    except Exception as e:
        print(f"❌ Setup verification failed: {e}")
        return False

def run_individual_tests(verbose=False):
    """Run individual test files."""
    print_section("Individual Component Tests")
    
    test_files = [
        ("API Key Manager", "test_api_key_manager_ollama_integration.py"),
        ("Smart Model Selector", "test_smart_model_selector_functionality.py"),
        ("Comprehensive Suite", "test_ollama_comprehensive.py")
    ]
    
    results = {}
    
    for test_name, test_file in test_files:
        print(f"\n🧪 Running {test_name} tests...")
        
        test_path = test_dir / test_file  # Use test_dir instead of backend_dir
        
        if not test_path.exists():
            print(f"❌ Test file not found: {test_file}")
            results[test_name] = False
            continue
        
        try:
            # Try running with pytest first
            try:
                if verbose:
                    result = subprocess.run([
                        sys.executable, "-m", "pytest", str(test_path), "-v"
                    ], capture_output=not verbose, text=True, timeout=300)
                else:
                    result = subprocess.run([
                        sys.executable, "-m", "pytest", str(test_path), "-q"
                    ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print(f"✅ {test_name} tests passed (pytest)")
                    results[test_name] = True
                else:
                    print(f"⚠️  {test_name} tests had issues (pytest)")
                    if verbose:
                        print(f"   Output: {result.stdout}")
                        print(f"   Errors: {result.stderr}")
                    
                    # Try running directly
                    print(f"   Trying direct execution...")
                    result = subprocess.run([
                        sys.executable, str(test_path)
                    ], capture_output=not verbose, text=True, timeout=300)
                    
                    results[test_name] = result.returncode == 0
                    
            except FileNotFoundError:
                # Pytest not available, run directly
                print(f"   Running {test_name} directly...")
                result = subprocess.run([
                    sys.executable, str(test_path)
                ], capture_output=not verbose, text=True, timeout=300)
                
                results[test_name] = result.returncode == 0
                
            if results[test_name]:
                print(f"✅ {test_name} tests completed successfully")
            else:
                print(f"❌ {test_name} tests failed")
                if verbose and hasattr(result, 'stdout'):
                    print(f"   Output: {result.stdout}")
                    print(f"   Errors: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_name} tests timed out")
            results[test_name] = False
        except Exception as e:
            print(f"❌ {test_name} tests error: {e}")
            results[test_name] = False
    
    return results

def run_integration_test():
    """Run integration test with actual ALwrity services."""
    print_section("Integration Test")
    
    try:
        # Test main text generation
        from services.llm_providers.main_text_generation import llm_text_gen, llm_analysis_gen
        
        print("🔄 Testing main text generation integration...")
        
        # Test basic generation
        response = llm_text_gen(
            prompt="Write a very short test message",
            task_type="analysis",
            priority="speed"
        )
        
        if response and len(response.strip()) > 0:
            print(f"✅ Basic generation works: {response[:50]}...")
        else:
            print("❌ Basic generation failed")
            return False
        
        # Test task-specific generation
        analysis_response = llm_analysis_gen("Analyze: Test data shows 25% improvement")
        
        if analysis_response and len(analysis_response.strip()) > 0:
            print(f"✅ Analysis generation works: {analysis_response[:50]}...")
        else:
            print("❌ Analysis generation failed")
            return False
        
        print("✅ Integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def run_performance_test():
    """Run basic performance test."""
    print_section("Performance Test")
    
    try:
        from services.llm_providers.main_text_generation import llm_analysis_gen
        
        print("⚡ Running performance test...")
        
        start_time = time.time()
        
        response = llm_analysis_gen(
            "What is the capital of France?",
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"   Response time: {response_time:.2f} seconds")
        print(f"   Response length: {len(response)} characters")
        print(f"   Sample response: {response[:80]}...")
        
        if response_time < 60:  # Should complete within 60 seconds
            print("✅ Performance test passed")
            return True
        else:
            print("⚠️  Performance test: Response time too slow")
            return False
            
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def generate_report(prerequisite_issues, setup_result, test_results, integration_result, performance_result):
    """Generate a comprehensive test report."""
    print_header("OLLAMA INTEGRATION TEST REPORT")
    
    # Prerequisites
    print("\n📋 Prerequisites:")
    if prerequisite_issues:
        for issue in prerequisite_issues:
            print(f"   ❌ {issue}")
    else:
        print("   ✅ All prerequisites met")
    
    # Setup
    print(f"\n🔧 Setup: {'✅ Passed' if setup_result else '❌ Failed'}")
    
    # Individual tests
    print(f"\n🧪 Component Tests:")
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    
    for test_name, result in test_results.items():
        status = "✅ Passed" if result else "❌ Failed"
        print(f"   {test_name}: {status}")
    
    print(f"   📊 Overall: {passed_tests}/{total_tests} tests passed")
    
    # Integration
    print(f"\n🔄 Integration: {'✅ Passed' if integration_result else '❌ Failed'}")
    
    # Performance
    print(f"\n⚡ Performance: {'✅ Passed' if performance_result else '❌ Failed'}")
    
    # Overall status
    all_passed = (
        len(prerequisite_issues) == 0 and
        setup_result and
        all(test_results.values()) and
        integration_result and
        performance_result
    )
    
    print(f"\n🏁 OVERALL STATUS: {'✅ ALL TESTS PASSED' if all_passed else '⚠️ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Congratulations! Ollama integration is working perfectly.")
        print("\n💡 Quick start:")
        print("   from services.llm_providers.main_text_generation import llm_analysis_gen")
        print("   result = llm_analysis_gen('Your prompt here')")
    else:
        print("\n🔧 Issues found. Please check the following:")
        if prerequisite_issues:
            print("   • Fix prerequisite issues")
        if not setup_result:
            print("   • Run setup: python scripts/setup_ollama.py")
        if not all(test_results.values()):
            print("   • Check failed component tests")
        if not integration_result:
            print("   • Check ALwrity service integration")
        if not performance_result:
            print("   • Check system resources and model availability")
    
    return all_passed

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run Ollama integration tests for ALwrity")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--setup-only", action="store_true", help="Run setup tests only")
    
    args = parser.parse_args()
    
    print_header("ALWRITY OLLAMA INTEGRATION TEST SUITE")
    
    # Check prerequisites
    prerequisite_issues = check_prerequisites()
    
    if prerequisite_issues and not args.setup_only:
        print("\n⚠️  Prerequisites not met. Please fix these issues first:")
        for issue in prerequisite_issues:
            print(f"   • {issue}")
        print("\n💡 Try running: python scripts/setup_ollama.py")
        return False
    
    # Run setup test
    setup_result = run_setup_test()
    
    if args.setup_only:
        return setup_result
    
    # Run individual tests
    test_results = {}
    if not args.quick:
        test_results = run_individual_tests(args.verbose)
    
    # Run integration test
    integration_result = run_integration_test()
    
    # Run performance test
    performance_result = False
    if not args.quick:
        performance_result = run_performance_test()
    
    # Generate report
    overall_success = generate_report(
        prerequisite_issues, setup_result, test_results, 
        integration_result, performance_result
    )
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)