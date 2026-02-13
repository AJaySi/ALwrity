
import os
import sys
import sqlite3

user_id = "user_33Gz1FPI86VDXhRY8QN4ragRFGN"
base_path = os.getcwd()
safe_user_id = "".join(c for c in user_id if c.isalnum() or c in ('-', '_'))
user_workspace = os.path.join(base_path, "workspace", f"workspace_{safe_user_id}")
db_path = os.path.join(user_workspace, "db", f"alwrity_{safe_user_id}.db")

print(f"Reading from: {db_path}")

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("\n--- API Usage Logs ---")
cursor.execute("SELECT * FROM api_usage_logs")
rows = cursor.fetchall()
for row in rows:
    print(dict(row))

print("\n--- Subscription Plans ---")
try:
    cursor.execute("SELECT * FROM subscription_plans")
    rows = cursor.fetchall()
    for row in rows:
        print(dict(row))
except Exception as e:
    print(f"Error reading subscription_plans: {e}")

print("\n--- Usage Summaries ---")
try:
    cursor.execute("SELECT * FROM usage_summaries")
    rows = cursor.fetchall()
    for row in rows:
        print(dict(row))
except Exception as e:
    print(f"Error reading usage_summaries: {e}")

conn.close()
