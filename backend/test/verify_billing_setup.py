"""
Comprehensive verification script for billing and subscription system setup.
Checks that all files are created, tables exist, and the system is properly integrated.
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

def check_database_tables():
    """Check if billing database tables exist."""
    print("\n🗄️  Checking Database Tables:")
    print("-" * 30)
    
    try:
        # Add backend to path
        backend_dir = Path(__file__).parent
        sys.path.insert(0, str(backend_dir))
        
        from services.database import get_db_session, DATABASE_URL
        from sqlalchemy import text
        
        session = get_db_session()
        if not session:
            print("❌ Could not get database session")
            return False
        
        # Check for billing tables
        tables_query = text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND (
                name LIKE '%subscription%' OR 
                name LIKE '%usage%' OR 
                name LIKE '%billing%' OR
                name LIKE '%pricing%' OR
                name LIKE '%alert%'
            )
            ORDER BY name
        """)
        
        result = session.execute(tables_query)
        tables = result.fetchall()
        
        expected_tables = [
            'api_provider_pricing',
            'api_usage_logs', 
            'subscription_plans',
            'usage_alerts',
            'usage_summaries',
            'user_subscriptions'
        ]
        
        found_tables = [t[0] for t in tables]
        print(f"Found tables: {found_tables}")
        
        missing_tables = [t for t in expected_tables if t not in found_tables]
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return False
        
        # Check table data
        for table in ['subscription_plans', 'api_provider_pricing']:
            count_query = text(f"SELECT COUNT(*) FROM {table}")
            result = session.execute(count_query)
            count = result.fetchone()[0]
            print(f"✅ {table}: {count} records")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def main():
    """Main verification function."""
    
    print("🔍 ALwrity Billing & Subscription System Setup Verification")
    print("=" * 70)
    
    backend_dir = Path(__file__).parent
    
    # Files to check
    files_to_check = [
        (backend_dir / "models" / "subscription_models.py", "Subscription Models"),
        (backend_dir / "services" / "pricing_service.py", "Pricing Service"),
        (backend_dir / "services" / "usage_tracking_service.py", "Usage Tracking Service"),
        (backend_dir / "services" / "subscription_exception_handler.py", "Exception Handler"),
        (backend_dir / "api" / "subscription_api.py", "Subscription API"),
        (backend_dir / "scripts" / "create_billing_tables.py", "Billing Migration Script"),
        (backend_dir / "scripts" / "create_subscription_tables.py", "Subscription Migration Script"),
        (backend_dir / "start_alwrity_backend.py", "Backend Startup Script"),
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
            ["SubscriptionPlan", "APIUsageLog", "UsageSummary", "APIProviderPricing"],
            "Subscription Models Content"
        ),
        (
            backend_dir / "services" / "pricing_service.py",
            ["calculate_api_cost", "check_usage_limits", "initialize_default_pricing"],
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
        ),
        (
            backend_dir / "start_alwrity_backend.py",
            ["setup_billing_tables", "verify_billing_tables"],
            "Backend Startup Integration"
        )
    ]
    
    content_valid = 0
    for file_path, search_terms, description in content_checks:
        if os.path.exists(file_path):
            if check_file_content(file_path, search_terms, description):
                content_valid += 1
        else:
            print(f"❌ {description}: File not found")
    
    # Check database tables
    database_ok = check_database_tables()
    
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
    print("\n" + "=" * 70)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 70)
    
    total_files = len(files_to_check)
    total_content = len(content_checks)
    
    print(f"Files Created: {files_exist}/{total_files}")
    print(f"Content Valid: {content_valid}/{total_content}")
    print(f"Database Tables: {'✅' if database_ok else '❌'}")
    print(f"Middleware Integration: {'✅' if middleware_ok else '❌'}")
    print(f"FastAPI Integration: {'✅' if app_ok else '❌'}")
    print(f"Database Integration: {'✅' if db_ok else '❌'}")
    
    # Overall status
    all_checks = [
        files_exist == total_files,
        content_valid == total_content,
        database_ok,
        middleware_ok,
        app_ok,
        db_ok
    ]
    
    if all(all_checks):
        print("\n🎉 ALL CHECKS PASSED!")
        print("✅ Billing and subscription system setup is complete and ready to use.")
        
        print("\n" + "=" * 70)
        print("🚀 NEXT STEPS:")
        print("=" * 70)
        print("1. Start the backend server:")
        print("   python start_alwrity_backend.py")
        print("\n2. Test the API endpoints:")
        print("   GET http://localhost:8000/api/subscription/plans")
        print("   GET http://localhost:8000/api/subscription/usage/demo")
        print("   GET http://localhost:8000/api/subscription/dashboard/demo")
        print("   GET http://localhost:8000/api/subscription/pricing")
        print("\n3. Access the frontend billing dashboard")
        print("4. Monitor usage through the API monitoring middleware")
        print("5. Set up user identification for production use")
        print("=" * 70)
        
    else:
        print("\n❌ SOME CHECKS FAILED!")
        print("Please review the errors above and fix any issues.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
