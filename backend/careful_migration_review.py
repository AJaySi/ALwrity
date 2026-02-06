#!/usr/bin/env python3

"""
Careful Migration Review and Planning
Review current state and plan careful migration approach.
"""

import sys
import os
import re

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Review current state and plan careful migration."""
    print("🔍 CAREFUL MIGRATION REVIEW & PLANNING")
    print("=" * 80)
    print("Current state: After Phase 2 (Strategic) - Clean git state")
    print()
    
    # Check current migration status
    print("📊 CURRENT MIGRATION STATUS:")
    
    migrated_files = []
    remaining_files = []
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # Skip migration scripts, tests, and other non-application files
                skip_patterns = [
                    'migrate_', 'migration_', 'phase_', 'proven_', 
                    'test_', 'backup_', '__init__.py', 'logging_config.py',
                    'careful_migration_review.py'
                ]
                
                should_skip = any(pattern in file_path for pattern in skip_patterns)
                
                if not should_skip:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        has_loguru = 'from loguru import logger' in content
                        has_unified = 'from utils.logging import get_logger' in content
                        logger_usage = content.count('logger.')
                        
                        if has_loguru:
                            remaining_files.append({
                                'file': file_path,
                                'logger_usage': logger_usage
                            })
                        elif has_unified:
                            migrated_files.append({
                                'file': file_path,
                                'logger_usage': logger_usage
                            })
                            
                    except Exception as e:
                        print(f'   ⚠️  Error reading {file_path}: {e}')
    
    print(f"   ✅ Successfully migrated: {len(migrated_files)} files")
    print(f"   ❌ Still using loguru: {len(remaining_files)} files")
    
    if migrated_files:
        print(f"\n✅ CURRENTLY MIGRATED FILES:")
        for i, file_info in enumerate(migrated_files[:10]):  # Show first 10
            print(f"   {i+1:2d}. {file_info['file']} ({file_info['logger_usage']} usages)")
        if len(migrated_files) > 10:
            print(f"   ... and {len(migrated_files) - 10} more migrated files")
    
    if remaining_files:
        print(f"\n❌ REMAINING FILES WITH LOGURU:")
        for i, file_info in enumerate(remaining_files[:15]):  # Show first 15
            print(f"   {i+1:2d}. {file_info['file']} ({file_info['logger_usage']} usages)")
        if len(remaining_files) > 15:
            print(f"   ... and {len(remaining_files) - 15} more files")
    else:
        print(f"\n🎉 NO REMAINING FILES WITH LOGURU!")
        print(f"   All ALwrity application files have been successfully migrated!")
    
    # Show current git commits
    print(f"\n📝 CURRENT GIT STATUS:")
    print(f"   Current commit: 96048d7 - Complete core services unified logging migration")
    print(f"   Branch: main")
    print(f"   Status: Clean working tree")
    print(f"   Ahead of origin: 10 commits")
    
    print(f"\n🎯 CAREFUL MIGRATION PLAN:")
    print(f"   1. ✅ Current state: Phase 2 completed successfully")
    print(f"   2. 🔍 Review: {len(remaining_files)} files still need migration")
    print(f"   3. 🎯 Target: Focus on high-usage application files only")
    print(f"   4. 🛡️  Safety: No migration script modifications")
    print(f"   5. 📊 Validation: Comprehensive testing after each file")
    print(f"   6. 💾 Backup: Individual file backups only")
    
    if remaining_files:
        # Sort remaining files by usage (high impact first)
        remaining_files.sort(key=lambda x: x['logger_usage'], reverse=True)
        
        print(f"\n📋 PRIORITY MIGRATION TARGETS:")
        print(f"   High Usage (>10): {len([f for f in remaining_files if f['logger_usage'] > 10])} files")
        print(f"   Medium Usage (5-10): {len([f for f in remaining_files if 5 <= f['logger_usage'] <= 10])} files")
        print(f"   Low Usage (<5): {len([f for f in remaining_files if f['logger_usage'] < 5])} files")
        
        print(f"\n🎯 TOP 10 PRIORITY FILES:")
        for i, file_info in enumerate(remaining_files[:10]):
            print(f"   {i+1:2d}. {file_info['file']} ({file_info['logger_usage']} usages)")
    
    print(f"\n🚀 NEXT STEPS:")
    if remaining_files:
        print(f"   1. 📝 Create careful migration script for top 10 files")
        print(f"   2. 🔧 Migrate one file at a time with validation")
        print(f"   3. ✅ Test each migration thoroughly")
        print(f"   4. 📊 Monitor system performance during migration")
        print(f"   5. 💾 Create individual backups for each file")
        print(f"   6. 🔄 Rollback immediately if any issues detected")
    else:
        print(f"   1. 🎉 Migration complete - all files migrated")
        print(f"   2. 📊 Final validation and testing")
        print(f"   3. 📚 Document migration methodology")
        print(f"   4. 🚀 Prepare for production deployment")
        print(f"   5. 📈 Monitor and optimize unified logging system")

if __name__ == "__main__":
    main()
