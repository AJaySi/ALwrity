#!/usr/bin/env python3
"""
Check if WaveSpeed migration is needed for user database
"""

import sqlite3
import os

# Database path from error logs
db_path = r'c:\Users\diksha rawat\Desktop\ALwrity_github\windsurf\ALwrity\workspace\workspace_user_33Gz1FPI86VDXhRY8QN4ragRFGN\db\alwrity_user_33Gz1FPI86VDXhRY8QN4ragRFGN.db'

print(f"Checking database: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if usage_summaries table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usage_summaries'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ usage_summaries table found")
            
            # Check current columns
            cursor.execute('PRAGMA table_info(usage_summaries)')
            columns = [col[1] for col in cursor.fetchall()]
            
            wavespeed_cols = [col for col in columns if 'wavespeed' in col]
            print(f"Current WaveSpeed columns: {wavespeed_cols}")
            
            if not wavespeed_cols:
                print("\n❌ WaveSpeed columns are MISSING!")
                print("\nTo fix this, run these SQL commands:")
                print(f"sqlite3 \"{db_path}\"")
                print("ALTER TABLE usage_summaries ADD COLUMN wavespeed_calls INTEGER DEFAULT 0;")
                print("ALTER TABLE usage_summaries ADD COLUMN wavespeed_tokens INTEGER DEFAULT 0;")
                print("ALTER TABLE usage_summaries ADD COLUMN wavespeed_cost REAL DEFAULT 0.0;")
                print(".quit")
            else:
                print("✅ WaveSpeed columns already exist!")
        else:
            print("❌ usage_summaries table not found")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
else:
    print("❌ Database file not found")
