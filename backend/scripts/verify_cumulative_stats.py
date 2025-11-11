#!/usr/bin/env python3
"""Verify cumulative stats table exists and has data"""

import sqlite3
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
db_path = os.path.join(backend_dir, 'alwrity.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scheduler_cumulative_stats'")
result = cursor.fetchone()
print(f"Table exists: {result is not None}")

if result:
    cursor.execute("SELECT * FROM scheduler_cumulative_stats WHERE id=1")
    row = cursor.fetchone()
    if row:
        print(f"Row data: {row}")
    else:
        print("Table exists but no row with id=1")
else:
    print("Table does not exist")

conn.close()

