#!/usr/bin/env python3
"""
Script to fix import paths in step files
"""

import os
import re

def fix_imports_in_file(file_path):
    """Fix import paths in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix the base_step import path
        # Change from ..base_step to ...base_step for subdirectories
        if '/step9_content_recommendations/' in file_path or '/step10_performance_optimization/' in file_path or '/step11_strategy_alignment_validation/' in file_path or '/step12_final_calendar_assembly/' in file_path:
            content = re.sub(r'from \.\.base_step import', 'from ...base_step import', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Fixed imports in {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Main function to fix all import paths."""
    base_path = "services/calendar_generation_datasource_framework/prompt_chaining/steps"
    
    # Files that need fixing
    files_to_fix = [
        f"{base_path}/phase3/step9_content_recommendations/step9_main.py",
        f"{base_path}/phase4/step10_performance_optimization/step10_main.py",
        f"{base_path}/phase4/step11_strategy_alignment_validation/step11_main.py",
        f"{base_path}/phase4/step12_final_calendar_assembly/step12_main.py",
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            fix_imports_in_file(file_path)
        else:
            print(f"⚠️ File not found: {file_path}")

if __name__ == "__main__":
    main()
