#!/usr/bin/env python3
"""
Migration script to add missing wavespeed columns to usage_summaries table
"""

import sqlite3
import sys
import os
from pathlib import Path

def get_db_path():
    """Find the database file"""
    # Look for common database locations
    possible_paths = [
        "backend/database.db",
        "backend/data/database.db", 
        "database.db",
        "data/database.db"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # If not found, check if there's a .db file in backend directory
    backend_dir = Path("backend")
    if backend_dir.exists():
        for db_file in backend_dir.glob("*.db"):
            return str(db_file)
    
    return None

def migrate_usage_summaries():
    """Add missing wavespeed columns to usage_summaries table"""
    
    db_path = get_db_path()
    if not db_path:
        print("❌ Database file not found!")
        print("Looked in:")
        for path in ["backend/database.db", "backend/data/database.db", "database.db", "data/database.db"]:
            print(f"  - {path}")
        return False
    
    print(f"📁 Using database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='usage_summaries'
        """)
        
        if not cursor.fetchone():
            print("❌ Table 'usage_summaries' does not exist!")
            return False
        
        # Get current columns
        cursor.execute("PRAGMA table_info(usage_summaries)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Current columns: {columns}")
        
        # Columns to add
        columns_to_add = [
            ("wavespeed_calls", "INTEGER DEFAULT 0"),
            ("tavily_calls", "INTEGER DEFAULT 0"), 
            ("serper_calls", "INTEGER DEFAULT 0"),
            ("metaphor_calls", "INTEGER DEFAULT 0"),
            ("firecrawl_calls", "INTEGER DEFAULT 0"),
            ("stability_calls", "INTEGER DEFAULT 0"),
            ("exa_calls", "INTEGER DEFAULT 0"),
            ("video_calls", "INTEGER DEFAULT 0"),
            ("image_edit_calls", "INTEGER DEFAULT 0"),
            ("audio_calls", "INTEGER DEFAULT 0"),
            ("wavespeed_tokens", "INTEGER DEFAULT 0"),
            ("wavespeed_cost", "FLOAT DEFAULT 0.0"),
            ("tavily_cost", "FLOAT DEFAULT 0.0"),
            ("serper_cost", "FLOAT DEFAULT 0.0"),
            ("metaphor_cost", "FLOAT DEFAULT 0.0"),
            ("firecrawl_cost", "FLOAT DEFAULT 0.0"),
            ("stability_cost", "FLOAT DEFAULT 0.0"),
            ("exa_cost", "FLOAT DEFAULT 0.0"),
            ("video_cost", "FLOAT DEFAULT 0.0"),
            ("image_edit_cost", "FLOAT DEFAULT 0.0"),
            ("audio_cost", "FLOAT DEFAULT 0.0")
        ]
        
        # Add missing columns
        added_columns = []
        for column_name, column_def in columns_to_add:
            if column_name not in columns:
                print(f"➕ Adding column: {column_name}")
                cursor.execute(f"ALTER TABLE usage_summaries ADD COLUMN {column_name} {column_def}")
                added_columns.append(column_name)
            else:
                print(f"✅ Column already exists: {column_name}")
        
        if added_columns:
            conn.commit()
            print(f"🎉 Successfully added {len(added_columns)} columns:")
            for col in added_columns:
                print(f"   - {col}")
        else:
            print("✅ All columns already exist!")
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(usage_summaries)")
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Updated columns: {new_columns}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting usage_summaries migration...")
    
    if migrate_usage_summaries():
        print("✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("❌ Migration failed!")
        sys.exit(1)
