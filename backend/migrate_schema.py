#!/usr/bin/env python
"""Migration script to add missing columns to daily_workflow_plans table."""
import sqlite3
import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = ROOT_DIR / "workspace"

def migrate_database(db_path):
    """Add missing columns to daily_workflow_plans table."""
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(daily_workflow_plans)")
        existing_cols = {row[1] for row in cursor.fetchall()}
        
        columns_to_add = {
            'generation_mode': "VARCHAR(30) NOT NULL DEFAULT 'llm_generation'",
            'committee_agent_count': "INTEGER NOT NULL DEFAULT 0",
            'fallback_used': "BOOLEAN NOT NULL DEFAULT 0"
        }
        
        for col_name, col_def in columns_to_add.items():
            if col_name not in existing_cols:
                alter_sql = f"ALTER TABLE daily_workflow_plans ADD COLUMN {col_name} {col_def}"
                print(f"Adding column: {col_name}")
                cursor.execute(alter_sql)
                print(f"  ✓ Added {col_name}")
            else:
                print(f"  - Column {col_name} already exists")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        return True
    
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def find_and_migrate_databases():
    """Find all databases and apply migrations."""
    workspace_dir = WORKSPACE_DIR
    
    if not workspace_dir.exists():
        print(f"Workspace directory not found: {workspace_dir}")
        return
    
    # Find all .db files
    db_files = list(workspace_dir.glob('**/db/*.db'))
    
    if not db_files:
        print("No databases found to migrate")
        return
    
    print(f"Found {len(db_files)} database(s) to migrate:\n")
    
    for db_path in db_files:
        print(f"Migrating: {db_path.name}")
        migrate_database(str(db_path))
        print()

if __name__ == '__main__':
    find_and_migrate_databases()
