#!/usr/bin/env python3
"""Add expires_at column to gsc_oauth_states table."""

from services.database import SessionLocal
from sqlalchemy import text

def add_expires_at_column():
    """Add expires_at column to gsc_oauth_states table."""
    db = SessionLocal()
    try:
        # Check if column exists
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'gsc_oauth_states' 
            AND column_name = 'expires_at'
        """)).fetchone()
        
        if not result:
            print('Adding expires_at column to gsc_oauth_states...')
            db.execute(text("""
                ALTER TABLE gsc_oauth_states
                ADD COLUMN expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '20 minutes')
            """))
            db.commit()
            print('✅ expires_at column added successfully')
        else:
            print('✅ expires_at column already exists')
            
    except Exception as e:
        print(f'Error: {e}')
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_expires_at_column()
