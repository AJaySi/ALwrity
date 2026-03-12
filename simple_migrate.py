import sqlite3
import os

# Find database
db_paths = ["backend/database.db", "backend/data/database.db", "database.db", "data/database.db"]
db_path = None

for path in db_paths:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    print("Database not found!")
    exit(1)

print(f"Using database: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usage_summaries'")
    if not cursor.fetchone():
        print("Table usage_summaries not found!")
        exit(1)
    
    # Get columns
    cursor.execute("PRAGMA table_info(usage_summaries)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Columns: {columns}")
    
    # Check for wavespeed_calls
    if "wavespeed_calls" in columns:
        print("✅ wavespeed_calls column exists")
    else:
        print("❌ wavespeed_calls column missing")
        
        # Add the column
        print("Adding wavespeed_calls column...")
        cursor.execute("ALTER TABLE usage_summaries ADD COLUMN wavespeed_calls INTEGER DEFAULT 0")
        conn.commit()
        print("✅ wavespeed_calls column added")
    
    conn.close()
    print("Migration completed!")
    
except Exception as e:
    print(f"Error: {e}")
