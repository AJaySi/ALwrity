@echo off
echo Running WaveSpeed migration...
cd /d "c:\Users\diksha rawat\Desktop\ALwrity_github\windsurf\ALwrity\backend"
windsurf_venv\Scripts\python.exe -c "
import sqlite3
import os

db_path = r'c:\Users\diksha rawat\Desktop\ALwrity_github\windsurf\ALwrity\workspace\workspace_user_33Gz1FPI86VDXhRY8QN4ragRFGN\db\alwrity_user_33Gz1FPI86VDXhRY8QN4ragRFGN.db'

print('Migrating WaveSpeed columns...')
print('Database:', db_path)

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('PRAGMA table_info(usage_summaries)')
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'wavespeed_calls' not in columns:
            cursor.execute('ALTER TABLE usage_summaries ADD COLUMN wavespeed_calls INTEGER DEFAULT 0')
            print('Added wavespeed_calls')
        
        if 'wavespeed_tokens' not in columns:
            cursor.execute('ALTER TABLE usage_summaries ADD COLUMN wavespeed_tokens INTEGER DEFAULT 0')
            print('Added wavespeed_tokens')
            
        if 'wavespeed_cost' not in columns:
            cursor.execute('ALTER TABLE usage_summaries ADD COLUMN wavespeed_cost REAL DEFAULT 0.0')
            print('Added wavespeed_cost')
        
        conn.commit()
        print('Migration completed successfully!')
        
    except Exception as e:
        print('Error:', str(e))
        conn.rollback()
    finally:
        conn.close()
else:
    print('Database not found:', db_path)

pause
"
