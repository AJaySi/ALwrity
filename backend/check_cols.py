import sqlite3
import os

db_path = r'workspace/workspace_user_33Gz1FPI86VDXhRY8QN4ragRFGN/db/alwrity_user_33Gz1FPI86VDXhRY8QN4ragRFGN.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(daily_workflow_plans)")
    cols = cursor.fetchall()
    col_names = [c[1] for c in cols]
    print("Columns:", col_names)
    conn.close()
else:
    print(f"Database not found at {db_path}")
