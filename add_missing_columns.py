#!/usr/bin/env python3
"""
Migration script to add missing columns to usage_summaries table.
Run this once to fix the database schema.

Usage:
    python add_missing_columns.py
"""

import sqlite3
from pathlib import Path

def get_db_path():
    """Find the database path."""
    possible_paths = [
        Path(__file__).parent / "backend" / "alwrity.db",
        Path(__file__).parent.parent / "backend" / "alwrity.db",
        Path("C:/Users/diksha rawat/Desktop/ALwrity_github/windsurf/ALwrity/backend/alwrity.db"),
    ]
    
    for db_path in possible_paths:
        if db_path.exists():
            print(f"Using database: {db_path}")
            return db_path
    
    backend_dir = Path(__file__).parent / "backend"
    if backend_dir.exists():
        db_files = list(backend_dir.glob("*.db"))
        if db_files:
            print(f"Found database: {db_files[0]}")
            return db_files[0]
    
    raise FileNotFoundError(f"Database not found. Searched: {possible_paths}")

def create_usage_summaries_table(cursor):
    """Create the usage_summaries table if it doesn't exist."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id VARCHAR(100) NOT NULL,
            billing_period VARCHAR(20) NOT NULL,
            
            -- API Call Counts
            gemini_calls INTEGER DEFAULT 0,
            openai_calls INTEGER DEFAULT 0,
            anthropic_calls INTEGER DEFAULT 0,
            mistral_calls INTEGER DEFAULT 0,
            wavespeed_calls INTEGER DEFAULT 0,
            tavily_calls INTEGER DEFAULT 0,
            serper_calls INTEGER DEFAULT 0,
            metaphor_calls INTEGER DEFAULT 0,
            firecrawl_calls INTEGER DEFAULT 0,
            stability_calls INTEGER DEFAULT 0,
            exa_calls INTEGER DEFAULT 0,
            video_calls INTEGER DEFAULT 0,
            image_edit_calls INTEGER DEFAULT 0,
            audio_calls INTEGER DEFAULT 0,
            
            -- Token Usage
            gemini_tokens INTEGER DEFAULT 0,
            openai_tokens INTEGER DEFAULT 0,
            anthropic_tokens INTEGER DEFAULT 0,
            mistral_tokens INTEGER DEFAULT 0,
            wavespeed_tokens INTEGER DEFAULT 0,
            
            -- Cost Tracking
            gemini_cost REAL DEFAULT 0.0,
            openai_cost REAL DEFAULT 0.0,
            anthropic_cost REAL DEFAULT 0.0,
            mistral_cost REAL DEFAULT 0.0,
            wavespeed_cost REAL DEFAULT 0.0,
            tavily_cost REAL DEFAULT 0.0,
            serper_cost REAL DEFAULT 0.0,
            metaphor_cost REAL DEFAULT 0.0,
            firecrawl_cost REAL DEFAULT 0.0,
            stability_cost REAL DEFAULT 0.0,
            exa_cost REAL DEFAULT 0.0,
            video_cost REAL DEFAULT 0.0,
            image_edit_cost REAL DEFAULT 0.0,
            audio_cost REAL DEFAULT 0.0,
            
            -- Totals
            total_calls INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            total_cost REAL DEFAULT 0.0,
            
            -- Performance Metrics
            avg_response_time REAL DEFAULT 0.0,
            error_rate REAL DEFAULT 0.0,
            usage_status VARCHAR(20) DEFAULT 'active',
            warnings_sent INTEGER DEFAULT 0,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            UNIQUE(user_id, billing_period)
        )
    """)
    print("Created usage_summaries table")

def add_missing_columns():
    db_path = get_db_path()
    print(f"Using database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check what tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables in database: {tables}")
    
    # Check if usage_summaries exists
    if "usage_summaries" not in tables:
        print("usage_summaries table doesn't exist. Creating it...")
        create_usage_summaries_table(cursor)
        conn.commit()
        conn.close()
        print("Done! Table created successfully.")
        return
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(usage_summaries)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    print(f"Existing columns in usage_summaries: {len(existing_columns)}")
    
    # Columns to add (name, type, default)
    columns_to_add = [
        # Call counts
        ("wavespeed_calls", "INTEGER", "0"),
        ("tavily_calls", "INTEGER", "0"),
        ("serper_calls", "INTEGER", "0"),
        ("metaphor_calls", "INTEGER", "0"),
        ("firecrawl_calls", "INTEGER", "0"),
        ("stability_calls", "INTEGER", "0"),
        ("exa_calls", "INTEGER", "0"),
        ("video_calls", "INTEGER", "0"),
        ("image_edit_calls", "INTEGER", "0"),
        ("audio_calls", "INTEGER", "0"),
        # Token usage
        ("wavespeed_tokens", "INTEGER", "0"),
        # Cost tracking
        ("wavespeed_cost", "REAL", "0.0"),
        ("tavily_cost", "REAL", "0.0"),
        ("serper_cost", "REAL", "0.0"),
        ("metaphor_cost", "REAL", "0.0"),
        ("firecrawl_cost", "REAL", "0.0"),
        ("stability_cost", "REAL", "0.0"),
        ("exa_cost", "REAL", "0.0"),
        ("video_cost", "REAL", "0.0"),
        ("image_edit_cost", "REAL", "0.0"),
        ("audio_cost", "REAL", "0.0"),
    ]
    
    added = []
    skipped = []
    
    for col_name, col_type, default in columns_to_add:
        if col_name in existing_columns:
            skipped.append(col_name)
            continue
            
        try:
            sql = f"ALTER TABLE usage_summaries ADD COLUMN {col_name} {col_type} DEFAULT {default}"
            cursor.execute(sql)
            added.append(col_name)
            print(f"  Added: {col_name}")
        except sqlite3.Error as e:
            print(f"  Error adding {col_name}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\nSummary:")
    print(f"  Added: {len(added)} columns")
    print(f"  Skipped (already exist): {len(skipped)} columns")
    
    if added:
        print(f"\nColumns added: {', '.join(added)}")
    if skipped:
        print(f"Already existed: {', '.join(skipped)}")

if __name__ == "__main__":
    add_missing_columns()
