import os
import sqlite3

from services.database import get_user_db_path

USER_ID = "user_33Gz1FPI86VDXhRY8QN4ragRFGN"
db_path = get_user_db_path(USER_ID)

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
