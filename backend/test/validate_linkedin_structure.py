"""
Simple validation script for LinkedIn content generation structure.
This script validates the code structure without requiring external dependencies.
"""

import os
import sys
import ast
import traceback
from pathlib import Path

def validate_file_syntax(file_path: str) -> bool:
    """Validate Python file syntax."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        ast.parse(content)
        print(f"✅ {file_path}: Syntax valid")
        return True
    except SyntaxError as e:
        print(f"❌ {file_path}: Syntax error - {e}")
        return False
    except Exception as e:
        print(f"❌ {file_path}: Error - {e}")
        return False

def validate_import_structure(file_path: str) -> bool:
    """Validate import structure without actually importing."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        print(f"✅ {file_path}: Found {len(imports)} imports")
        return True
    except Exception as e:
        print(f"❌ {file_path}: Import validation error - {e}")
        return False

def check_class_structure(file_path: str, expected_classes: list) -> bool:
    """Check if expected classes are defined."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        found_classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                found_classes.append(node.name)
        
        missing_classes = set(expected_classes) - set(found_classes)
        if missing_classes:
            print(f"⚠️ {file_path}: Missing classes: {missing_classes}")
        else:
            print(f"✅ {file_path}: All expected classes found")
        
        print(f"   Found classes: {found_classes}")
        return len(missing_classes) == 0
    except Exception as e:
        print(f"❌ {file_path}: Class validation error - {e}")
        return False

def check_function_structure(file_path: str, expected_functions: list) -> bool:
    """Check if expected functions are defined."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        found_functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                found_functions.append(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                found_functions.append(node.name)
        
        missing_functions = set(expected_functions) - set(found_functions)
        if missing_functions:
            print(f"⚠️ {file_path}: Missing functions: {missing_functions}")
        else:
            print(f"✅ {file_path}: All expected functions found")
        
        return len(missing_functions) == 0
    except Exception as e:
        print(f"❌ {file_path}: Function validation error - {e}")
        return False

def validate_linkedin_models():
    """Validate LinkedIn models file."""
    print("\n🔍 Validating LinkedIn Models")
    print("-" * 40)
    
    file_path = "models/linkedin_models.py"
    if not os.path.exists(file_path):
        print(f"❌ {file_path}: File does not exist")
        return False
    
    # Check syntax
    syntax_ok = validate_file_syntax(file_path)
    
    # Check imports
    imports_ok = validate_import_structure(file_path)
    
    # Check expected classes
    expected_classes = [
        "LinkedInPostRequest", "LinkedInArticleRequest", "LinkedInCarouselRequest",
        "LinkedInVideoScriptRequest", "LinkedInCommentResponseRequest",
        "LinkedInPostResponse", "LinkedInArticleResponse", "LinkedInCarouselResponse",
        "LinkedInVideoScriptResponse", "LinkedInCommentResponseResult",
        "PostContent", "ArticleContent", "CarouselContent", "VideoScript"
    ]
    classes_ok = check_class_structure(file_path, expected_classes)
    
    return syntax_ok and imports_ok and classes_ok

def validate_linkedin_service():
    """Validate LinkedIn service file."""
    print("\n🔍 Validating LinkedIn Service")
    print("-" * 40)
    
    file_path = "services/linkedin_service.py"
    if not os.path.exists(file_path):
        print(f"❌ {file_path}: File does not exist")
        return False
    
    # Check syntax
    syntax_ok = validate_file_syntax(file_path)
    
    # Check imports
    imports_ok = validate_import_structure(file_path)
    
    # Check expected classes
    expected_classes = ["LinkedInContentService"]
    classes_ok = check_class_structure(file_path, expected_classes)
    
    # Check expected methods
    expected_functions = [
        "generate_post", "generate_article", "generate_carousel",
        "generate_video_script", "generate_comment_response"
    ]
    functions_ok = check_function_structure(file_path, expected_functions)
    
    return syntax_ok and imports_ok and classes_ok and functions_ok

def validate_linkedin_router():
    """Validate LinkedIn router file."""
    print("\n🔍 Validating LinkedIn Router")
    print("-" * 40)
    
    file_path = "routers/linkedin.py"
    if not os.path.exists(file_path):
        print(f"❌ {file_path}: File does not exist")
        return False
    
    # Check syntax
    syntax_ok = validate_file_syntax(file_path)
    
    # Check imports
    imports_ok = validate_import_structure(file_path)
    
    # Check expected functions (endpoints)
    expected_functions = [
        "health_check", "generate_post", "generate_article", 
        "generate_carousel", "generate_video_script", "generate_comment_response",
        "get_content_types", "get_usage_stats"
    ]
    functions_ok = check_function_structure(file_path, expected_functions)
    
    return syntax_ok and imports_ok and functions_ok

def check_file_exists(file_path: str) -> bool:
    """Check if file exists."""
    exists = os.path.exists(file_path)
    status = "✅" if exists else "❌"
    print(f"{status} {file_path}: {'Exists' if exists else 'Missing'}")
    return exists

def validate_file_structure():
    """Validate the overall file structure."""
    print("\n🔍 Validating File Structure")
    print("-" * 40)
    
    required_files = [
        "models/linkedin_models.py",
        "services/linkedin_service.py", 
        "routers/linkedin.py",
        "test_linkedin_endpoints.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if not check_file_exists(file_path):
            all_exist = False
    
    return all_exist

def main():
    """Run all validations."""
    print("🚀 LinkedIn Content Generation Structure Validation")
    print("=" * 60)
    
    results = {}
    
    # Validate file structure
    results["file_structure"] = validate_file_structure()
    
    # Validate individual components
    results["models"] = validate_linkedin_models()
    results["service"] = validate_linkedin_service() 
    results["router"] = validate_linkedin_router()
    
    # Summary
    print("\n📊 Validation Results")
    print("=" * 40)
    
    passed = sum(results.values())
    total = len(results)
    
    for component, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{component}: {status}")
    
    print(f"\nOverall: {passed}/{total} validations passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All structure validations passed!")
        print("The LinkedIn content generation migration is structurally complete.")
        print("\nNext steps:")
        print("1. Install required dependencies (fastapi, pydantic, etc.)")
        print("2. Configure API keys (GEMINI_API_KEY)")
        print("3. Start the FastAPI server")
        print("4. Test the endpoints")
    else:
        print(f"\n⚠️ {total - passed} validation(s) failed. Please review the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)