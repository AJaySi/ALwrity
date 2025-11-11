#!/usr/bin/env python3
"""
Script to run the cumulative stats migration.
This creates the scheduler_cumulative_stats table.
"""

import sqlite3
import os
import sys

# Get the database path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
db_path = os.path.join(backend_dir, 'alwrity.db')
migration_path = os.path.join(backend_dir, 'database', 'migrations', 'create_scheduler_cumulative_stats.sql')

if not os.path.exists(db_path):
    print(f"❌ Database not found at {db_path}")
    sys.exit(1)

if not os.path.exists(migration_path):
    print(f"❌ Migration file not found at {migration_path}")
    sys.exit(1)

try:
    conn = sqlite3.connect(db_path)
    with open(migration_path, 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    print("✅ Migration executed successfully")
    conn.close()
except Exception as e:
    print(f"❌ Error running migration: {e}")
    sys.exit(1)

