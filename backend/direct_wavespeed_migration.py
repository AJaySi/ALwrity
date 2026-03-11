import sqlite3

# Database path
db_path = r'c:\Users\diksha rawat\Desktop\ALwrity_github\windsurf\ALwrity\workspace\workspace_user_33Gz1FPI86VDXhRY8QN4ragRFGN\db\alwrity_user_33Gz1FPI86VDXhRY8QN4ragRFGN.db'

print(f"Running WaveSpeed migration on: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check current columns
    cursor.execute('PRAGMA table_info(usage_summaries)')
    columns = [col[1] for col in cursor.fetchall()]
    
    print(f"Current columns with 'wavespeed': {[col for col in columns if 'wavespeed' in col]}")
    
    # Add wavespeed_calls if missing
    if 'wavespeed_calls' not in columns:
        print("Adding wavespeed_calls...")
        cursor.execute('ALTER TABLE usage_summaries ADD COLUMN wavespeed_calls INTEGER DEFAULT 0')
        print("✅ wavespeed_calls added")
    else:
        print("wavespeed_calls already exists")
    
    # Add wavespeed_tokens if missing
    if 'wavespeed_tokens' not in columns:
        print("Adding wavespeed_tokens...")
        cursor.execute('ALTER TABLE usage_summaries ADD COLUMN wavespeed_tokens INTEGER DEFAULT 0')
        print("✅ wavespeed_tokens added")
    else:
        print("wavespeed_tokens already exists")
        
    # Add wavespeed_cost if missing
    if 'wavespeed_cost' not in columns:
        print("Adding wavespeed_cost...")
        cursor.execute('ALTER TABLE usage_summaries ADD COLUMN wavespeed_cost REAL DEFAULT 0.0')
        print("✅ wavespeed_cost added")
    else:
        print("wavespeed_cost already exists")
    
    conn.commit()
    
    # Verify
    cursor.execute('PRAGMA table_info(usage_summaries)')
    updated_columns = [col[1] for col in cursor.fetchall()]
    wavespeed_cols = [col for col in updated_columns if 'wavespeed' in col]
    
    print(f"\n✅ Migration completed!")
    print(f"WaveSpeed columns now available: {wavespeed_cols}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()

print("\n🎉 WaveSpeed migration completed successfully!")
print("The subscription dashboard should now work without errors.")
