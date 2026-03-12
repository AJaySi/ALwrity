"""
Quick fix for missing wavespeed columns in usage_summaries table
Run this script to fix the database schema issue
"""

import sqlite3
import os

def fix_database():
    # Find database file
    db_path = None
    for path in ["backend/database.db", "database.db"]:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ Database not found!")
        print("Please make sure you're running this from the project root directory")
        return
    
    print(f"📁 Using database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usage_summaries'")
        if not cursor.fetchone():
            print("❌ Table 'usage_summaries' not found!")
            return
        
        # Get current columns
        cursor.execute("PRAGMA table_info(usage_summaries)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Columns that need to be added
        missing_columns = []
        required_columns = [
            'wavespeed_calls', 'tavily_calls', 'serper_calls', 'metaphor_calls',
            'firecrawl_calls', 'stability_calls', 'exa_calls', 'video_calls',
            'image_edit_calls', 'audio_calls', 'wavespeed_tokens', 'wavespeed_cost',
            'tavily_cost', 'serper_cost', 'metaphor_cost', 'firecrawl_cost',
            'stability_cost', 'exa_cost', 'video_cost', 'image_edit_cost', 'audio_cost'
        ]
        
        for col in required_columns:
            if col not in columns:
                missing_columns.append(col)
        
        if missing_columns:
            print(f"➕ Adding {len(missing_columns)} missing columns...")
            for col in missing_columns:
                if col.endswith('_calls') or col.endswith('_tokens'):
                    cursor.execute(f"ALTER TABLE usage_summaries ADD COLUMN {col} INTEGER DEFAULT 0")
                else:  # cost columns
                    cursor.execute(f"ALTER TABLE usage_summaries ADD COLUMN {col} FLOAT DEFAULT 0.0")
                print(f"   ✅ Added {col}")
            
            conn.commit()
            print("🎉 Database schema updated successfully!")
        else:
            print("✅ All columns already exist!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔧 Fixing database schema for usage_summaries...")
    fix_database()
    print("✅ Done!")
