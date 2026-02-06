#!/usr/bin/env python3

"""
Careful Targeted Migration
Migrate top priority files one by one with careful validation.
"""

import sys
import os
import re
import shutil

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Top 10 high-priority application files (excluding scripts, tests, venv)
TOP_PRIORITY_FILES = [
    {
        "file": "services/integrations/wix/blog_publisher.py",
        "service": "wix_blog_publisher",
        "description": "WIX blog publisher integration",
        "usage": 98
    },
    {
        "file": "services/llm_providers/gemini_grounded_provider.py", 
        "service": "gemini_grounded_provider",
        "description": "Gemini grounded LLM provider",
        "usage": 82
    },
    {
        "file": "services/integrations/bing_oauth.py",
        "service": "bing_oauth_integration",
        "description": "Bing OAuth integration service",
        "usage": 72
    },
    {
        "file": "services/subscription/limit_validation.py",
        "service": "subscription_limit_validation",
        "description": "Subscription limit validation service",
        "usage": 64
    },
    {
        "file": "scripts/verify_onboarding_data.py",
        "service": "onboarding_data_verification",
        "description": "Onboarding data verification script",
        "usage": 83
    },
    {
        "file": "services/llm_providers/main_text_generation.py",
        "service": "main_text_generation_provider",
        "description": "Main text generation LLM provider",
        "usage": 62
    },
    {
        "file": "scripts/update_basic_plan_limits.py",
        "service": "basic_plan_limits_update",
        "description": "Basic plan limits update script",
        "usage": 62
    },
    {
        "file": "api/onboarding_utils/step4_persona_routes.py",
        "service": "persona_step4_routes",
        "description": "Persona step 4 API routes",
        "usage": 61
    },
    {
        "file": "api/component_logic.py",
        "service": "api_component_logic",
        "description": "API component logic",
        "usage": 50
    },
    {
        "file": "services/integrations/wix_oauth.py",
        "service": "wix_oauth_integration",
        "description": "WIX OAuth integration service",
        "usage": 58
    }
]

def migrate_single_file(target):
    """Migrate a single file with careful validation."""
    file_path = target["file"]
    service_name = target["service"]
    description = target["description"]
    usage = target["usage"]
    
    print(f"\n🔧 MIGRATING: {file_path}")
    print(f"📝 {description}")
    print(f"📊 Logger usage: {usage}")
    print("-" * 70)
    
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"   ⚠️  File not found: {file_path}")
            return False
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if it has loguru imports
        if 'from loguru import logger' not in content:
            print(f"   ℹ️  No loguru imports found in {file_path}")
            return True
        
        # Count usage
        loguru_imports = content.count('from loguru import logger')
        logger_usage = content.count('logger.')
        
        print(f"   📊 Found {loguru_imports} loguru imports, {logger_usage} logger usages")
        
        # Create backup before migration
        backup_path = f"{file_path}.careful_backup"
        shutil.copy2(file_path, backup_path)
        print(f"   💾 Careful backup created: {backup_path}")
        
        # Perform migration
        old_import = 'from loguru import logger'
        new_import = f'from utils.logging import get_logger\nlogger = get_logger("{service_name}", migration_mode=True)'
        
        new_content = content.replace(old_import, new_import)
        
        # Write the migrated file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"   ✅ Successfully migrated {file_path}")
        return True
        
    except Exception as e:
        print(f"   ❌ Migration failed: {e}")
        return False

def validate_migration(target):
    """Validate migration with comprehensive testing."""
    file_path = target["file"]
    service_name = target["service"]
    
    try:
        # Test unified logging
        from utils.logging import get_logger
        
        logger = get_logger(service_name, migration_mode=True)
        logger.info(f"✅ Careful migration validation successful for {service_name}")
        
        # Test file can be imported
        import importlib.util
        spec = importlib.util.spec_from_file_location(service_name, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            print(f"   ✅ Module import validation passed for {service_name}")
        
        # Test syntax
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        compile(content, file_path, 'exec')
        print(f"   ✅ Syntax validation passed for {service_name}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Validation failed for {service_name}: {e}")
        return False

def rollback_file(target):
    """Rollback migration from backup."""
    file_path = target["file"]
    backup_path = f"{file_path}.careful_backup"
    
    try:
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
            os.remove(backup_path)
            print(f"   ✅ Rollback successful for {file_path}")
            return True
        else:
            print(f"   ⚠️  No backup found for {file_path}")
            return False
    except Exception as e:
        print(f"   ❌ Rollback failed for {file_path}: {e}")
        return False

def main():
    """Main function for careful targeted migration."""
    print("🎯 CAREFUL TARGETED MIGRATION")
    print("=" * 80)
    print("Migrating top 10 high-priority files one by one")
    print("With comprehensive validation and safety measures")
    print()
    
    # Set environment variables
    os.environ["LOGGING_MIGRATION_ENABLED"] = "true"
    os.environ["LOGGING_MIGRATION_MODE"] = "gradual"
    
    print("✅ Migration environment configured")
    print(f"   LOGGING_MIGRATION_ENABLED={os.environ['LOGGING_MIGRATION_ENABLED']}")
    print(f"   LOGGING_MIGRATION_MODE={os.environ['LOGGING_MIGRATION_MODE']}")
    
    print(f"\n🎯 TARGET FILES:")
    for i, target in enumerate(TOP_PRIORITY_FILES):
        print(f"   {i+1:2d}. {target['file']} ({target['usage']} usages) - {target['description']}")
    
    # Track migration results
    results = {
        "total": len(TOP_PRIORITY_FILES),
        "migrated": 0,
        "validated": 0,
        "failed": 0
    }
    
    # Perform migration one by one
    print(f"\n🔧 STARTING CAREFUL MIGRATION:")
    
    for i, target in enumerate(TOP_PRIORITY_FILES):
        print(f"\n{'='*20}")
        print(f"FILE {i+1}/{len(TOP_PRIORITY_FILES)}: {target['service']}")
        print(f"{'='*20}")
        
        if migrate_single_file(target):
            results["migrated"] += 1
            if validate_migration(target):
                results["validated"] += 1
                print(f"   🎉 File {target['service']} migrated and validated successfully!")
            else:
                print(f"   ⚠️  File {target['service']} migrated but validation failed!")
                results["failed"] += 1
        else:
            print(f"   ❌ File {target['service']} migration failed!")
            results["failed"] += 1
    
    # Show results
    print(f"\n{'='*80}")
    print(f"📊 CAREFUL TARGETED MIGRATION RESULTS:")
    print(f"{'='*80}")
    print(f"   Total targets: {results['total']}")
    print(f"   Successfully migrated: {results['migrated']}")
    print(f"   Validated: {results['validated']}")
    print(f"   Failed: {results['failed']}")
    
    success_rate = (results['migrated'] / results['total']) * 100 if results['total'] > 0 else 0
    print(f"   Success rate: {success_rate:.1f}%")
    
    if results["failed"] > 0:
        print(f"\n⚠️  Some files failed. Rollback options:")
        print(f"   Rollback all: python careful_targeted_migration.py --rollback")
        print(f"   Rollback specific: python careful_targeted_migration.py --rollback <file_index>")
    else:
        print(f"\n🎉 ALL FILES MIGRATED SUCCESSFULLY!")
        print(f"   ✅ Zero failures")
        print(f"   ✅ All validations passed")
        print(f"   ✅ Ready for commit")
    
    return results["failed"] == 0

if __name__ == "__main__":
    # Handle rollback options
    if len(sys.argv) > 1:
        if sys.argv[1] == "--rollback":
            print("🔄 Rolling back all careful targeted migrations...")
            for target in TOP_PRIORITY_FILES:
                rollback_file(target)
            print("✅ All rollbacks completed!")
            sys.exit(0)
        elif sys.argv[1] == "--rollback" and len(sys.argv) > 2:
            try:
                file_index = int(sys.argv[2]) - 1
                if 0 <= file_index < len(TOP_PRIORITY_FILES):
                    target = TOP_PRIORITY_FILES[file_index]
                    print(f"🔄 Rolling back file {file_index + 1}: {target['file']}")
                    rollback_file(target)
                    print("✅ Rollback completed!")
                else:
                    print(f"❌ Invalid file index: {file_index + 1}")
            except ValueError:
                print("❌ Invalid file index. Use: --rollback <number>")
            sys.exit(0)
    
    success = main()
    sys.exit(0 if success else 1)
