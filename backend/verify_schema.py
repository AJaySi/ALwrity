import sqlite3

db_path = r'c:\Users\diksha rawat\Desktop\ALwrity\workspace\workspace_alwrity\db\alwrity_alwrity.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'daily_%'")
tables = cursor.fetchall()
print(f"Daily tables: {tables}")

if tables:
    cursor.execute("PRAGMA table_info(daily_workflow_plans)")
    cols = cursor.fetchall()
    col_names = [c[1] for c in cols]
    print(f"\nColumns in daily_workflow_plans: {col_names}")
    
    required = ['generation_mode', 'committee_agent_count', 'fallback_used']
    for col in required:
        if col in col_names:
            print(f"  ✓ {col}")
        else:
            print(f"  ✗ {col}")
else:
    print("No daily tables found")

conn.close()
