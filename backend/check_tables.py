#!/usr/bin/env python
import sqlite3
import os

db_path = 'alwrity.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check daily workflow tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'daily_%'")
    daily_tables = [row[0] for row in cursor.fetchall()]
    print(f"Daily workflow tables: {daily_tables}")
    
    # Check the columns in daily_workflow_plans if it exists
    if 'daily_workflow_plans' in daily_tables:
        cursor.execute("PRAGMA table_info(daily_workflow_plans)")
        columns = cursor.fetchall()
        col_names = [col[1] for col in columns]
        print(f"Columns in daily_workflow_plans: {col_names}")
        
        # Check if generation_mode exists
        if 'generation_mode' in col_names:
            print("✅ generation_mode column exists")
        else:
            print("❌ generation_mode column missing")
    else:
        print("❌ daily_workflow_plans table doesn't exist")
    
    conn.close()
else:
    print(f"❌ Database file {db_path} not found")
