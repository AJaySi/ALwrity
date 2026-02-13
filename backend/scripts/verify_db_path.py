
import os
import sys
import sqlite3

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database import get_user_db_path

user_id = "user_33Gz1FPI86VDXhRY8QN4ragRFGN"
base_path = os.getcwd()
safe_user_id = "".join(c for c in user_id if c.isalnum() or c in ('-', '_'))
user_workspace = os.path.join(base_path, "workspace", f"workspace_{safe_user_id}")

path1 = os.path.join(user_workspace, "db", "alwrity.db")
path2 = os.path.join(user_workspace, "db", f"alwrity_{safe_user_id}.db")

print(f"Checking paths for user {user_id}:")
print(f"Legacy: {path1}")
print(f"Specific: {path2}")

def check_db(path):
    if not os.path.exists(path):
        print(f"  [MISSING] {path}")
        return
    
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM api_usage_logs")
        count = cursor.fetchone()[0]
        print(f"  [EXISTS] {path} - Rows in api_usage_logs: {count}")
        conn.close()
    except Exception as e:
        print(f"  [EXISTS] {path} - Error reading: {e}")

check_db(path1)
check_db(path2)

print("-" * 30)
resolved = get_user_db_path(user_id)
print(f"Application resolves to: {resolved}")
