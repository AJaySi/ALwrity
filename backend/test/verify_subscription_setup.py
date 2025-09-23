"""
Simple verification script for subscription system setup.
Checks that all files are created and properly structured.
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and report status."""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - NOT FOUND")
        return False

def check_file_content(file_path, search_terms, description):
    """Check if file contains expected content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        missing_terms = []
        for term in search_terms:
            if term not in content:
                missing_terms.append(term)
        
        if not missing_terms:
            print(f"✅ {description}: All expected content found")
            return True
        else:
            print(f"❌ {description}: Missing content - {missing_terms}")
            return False
    except Exception as e:
        print(f"❌ {description}: Error reading file - {e}")
        return False

def main():
    """Main verification function."""
    
    print("🔍 ALwrity Subscription System Setup Verification")
    print("=" * 60)
    
    backend_dir = Path(__file__).parent
    
    # Files to check
    files_to_check = [
        (backend_dir / "models" / "subscription_models.py", "Subscription Models"),
        (backend_dir / "services" / "pricing_service.py", "Pricing Service"),
        (backend_dir / "services" / "usage_tracking_service.py", "Usage Tracking Service"),
        (backend_dir / "services" / "subscription_exception_handler.py", "Exception Handler"),
        (backend_dir / "api" / "subscription_api.py", "Subscription API"),
        (backend_dir / "scripts" / "create_subscription_tables.py", "Migration Script"),
        (backend_dir / "test_subscription_system.py", "Test Script"),
        (backend_dir / "SUBSCRIPTION_SYSTEM_README.md", "Documentation")
    ]
    
    # Check file existence
    print("\n📁 Checking File Existence:")
    print("-" * 30)
    files_exist = 0
    for file_path, description in files_to_check:
        if check_file_exists(file_path, description):
            files_exist += 1
    
    # Check content of key files
    print("\n📝 Checking File Content:")
    print("-" * 30)
    
    content_checks = [
        (
            backend_dir / "models" / "subscription_models.py",
            ["SubscriptionPlan", "APIUsageLog", "UsageSummary", "APIProvider"],
            "Subscription Models Content"
        ),
        (
            backend_dir / "services" / "pricing_service.py",
            ["calculate_api_cost", "check_usage_limits", "APIProvider.GEMINI"],
            "Pricing Service Content"
        ),
        (
            backend_dir / "services" / "usage_tracking_service.py",
            ["track_api_usage", "get_user_usage_stats", "enforce_usage_limits"],
            "Usage Tracking Content"
        ),
        (
            backend_dir / "api" / "subscription_api.py",
            ["get_user_usage", "get_subscription_plans", "get_dashboard_data"],
            "API Endpoints Content"
        )
    ]
    
    content_valid = 0
    for file_path, search_terms, description in content_checks:
        if os.path.exists(file_path):
            if check_file_content(file_path, search_terms, description):
                content_valid += 1
        else:
            print(f"❌ {description}: File not found")
    
    # Check middleware integration
    print("\n🔧 Checking Middleware Integration:")
    print("-" * 30)
    
    middleware_file = backend_dir / "middleware" / "monitoring_middleware.py"
    middleware_terms = [
        "UsageTrackingService",
        "detect_api_provider",
        "track_api_usage",
        "check_usage_limits_middleware"
    ]
    
    middleware_ok = check_file_content(
        middleware_file,
        middleware_terms,
        "Middleware Integration"
    )
    
    # Check app.py integration
    print("\n🚀 Checking FastAPI Integration:")
    print("-" * 30)
    
    app_file = backend_dir / "app.py"
    app_terms = [
        "from api.subscription_api import router as subscription_router",
        "app.include_router(subscription_router)"
    ]
    
    app_ok = check_file_content(
        app_file,
        app_terms,
        "FastAPI App Integration"
    )
    
    # Check database service integration
    print("\n💾 Checking Database Integration:")
    print("-" * 30)
    
    db_file = backend_dir / "services" / "database.py"
    db_terms = [
        "from models.subscription_models import Base as SubscriptionBase",
        "SubscriptionBase.metadata.create_all(bind=engine)"
    ]
    
    db_ok = check_file_content(
        db_file,
        db_terms,
        "Database Service Integration"
    )
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    total_files = len(files_to_check)
    total_content = len(content_checks)
    
    print(f"Files Created: {files_exist}/{total_files}")
    print(f"Content Valid: {content_valid}/{total_content}")
    print(f"Middleware Integration: {'✅' if middleware_ok else '❌'}")
    print(f"FastAPI Integration: {'✅' if app_ok else '❌'}")
    print(f"Database Integration: {'✅' if db_ok else '❌'}")
    
    # Overall status
    all_checks = [
        files_exist == total_files,
        content_valid == total_content,
        middleware_ok,
        app_ok,
        db_ok
    ]
    
    if all(all_checks):
        print("\n🎉 ALL CHECKS PASSED!")
        print("✅ Subscription system setup is complete and ready to use.")
        
        print("\n" + "=" * 60)
        print("🚀 NEXT STEPS:")
        print("=" * 60)
        print("1. Install dependencies (if not already done):")
        print("   pip install sqlalchemy loguru fastapi")
        print("\n2. Run the migration script:")
        print("   python scripts/create_subscription_tables.py")
        print("\n3. Test the system:")
        print("   python test_subscription_system.py")
        print("\n4. Start the server:")
        print("   python start_alwrity_backend.py")
        print("\n5. Test API endpoints:")
        print("   GET http://localhost:8000/api/subscription/plans")
        print("   GET http://localhost:8000/api/subscription/pricing")
        
    else:
        print("\n❌ SOME CHECKS FAILED!")
        print("Please review the errors above and fix any issues.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)