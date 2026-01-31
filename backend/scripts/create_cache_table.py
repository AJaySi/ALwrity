"""
Database migration script to create comprehensive user data cache table.
Run this script to add the cache table to your database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _raise_postgresql_required():
    """Raise error if PostgreSQL not configured."""
    raise ValueError(
        """
 POSTGRESQL REQUIRED - Clean Architecture
        
    ALwrity requires PostgreSQL environment variables to be set:
    - DATABASE_URL=postgresql://user:pass@host:port/database_name
    - PLATFORM_DATABASE_URL=postgresql://user:pass@host:port/database_name
    - USER_DATA_DATABASE_URL=postgresql://user:pass@host:port/database_name

    This is intentional - we no longer support SQLite or single database setups.
    """
    )

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from loguru import logger
import os


def _raise_postgresql_required():
    """Raise error if PostgreSQL not configured."""
    raise ValueError(
        """
 POSTGRESQL REQUIRED - Clean Architecture
        
    ALwrity requires PostgreSQL environment variables to be set:
    - DATABASE_URL=postgresql://user:pass@host:port/database_name
    - PLATFORM_DATABASE_URL=postgresql://user:pass@host:port/database_name
    - USER_DATA_DATABASE_URL=postgresql://user:pass@host:port/database_name

    This is intentional - we no longer support SQLite or single database setups.
    """
    )

def create_cache_table():
    """Create the comprehensive user data cache table."""
    try:
        # Get database URL from environment or use default
        database_url = os.getenv('DATABASE_URL') or _raise_postgresql_required()
        
        # Create engine
        engine = create_engine(database_url)
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # SQL to create the cache table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS comprehensive_user_data_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            strategy_id INTEGER,
            data_hash VARCHAR(64) NOT NULL,
            comprehensive_data JSON NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL,
            last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
            access_count INTEGER DEFAULT 0
        );
        """
        
        # Create indexes
        create_indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_user_strategy ON comprehensive_user_data_cache(user_id, strategy_id);",
            "CREATE INDEX IF NOT EXISTS idx_expires_at ON comprehensive_user_data_cache(expires_at);",
            "CREATE INDEX IF NOT EXISTS idx_data_hash ON comprehensive_user_data_cache(data_hash);"
        ]
        
        # Execute table creation
        logger.info("Creating comprehensive_user_data_cache table...")
        db.execute(text(create_table_sql))
        
        # Execute index creation
        logger.info("Creating indexes...")
        for index_sql in create_indexes_sql:
            db.execute(text(index_sql))
        
        # Commit changes
        db.commit()
        
        # Verify table creation
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='comprehensive_user_data_cache';"))
        table_exists = result.fetchone()
        
        if table_exists:
            logger.info("✅ Comprehensive user data cache table created successfully!")
            
            # Show table structure
            result = db.execute(text("PRAGMA table_info(comprehensive_user_data_cache);"))
            columns = result.fetchall()
            
            logger.info("Table structure:")
            for column in columns:
                logger.info(f"  - {column[1]} ({column[2]})")
                
        else:
            logger.error("❌ Failed to create comprehensive_user_data_cache table")
            return False
            
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating cache table: {str(e)}")
        if 'db' in locals():
            db.close()
        return False

def drop_cache_table():
    """Drop the comprehensive user data cache table (for testing)."""
    try:
        # Get database URL from environment or use default
        database_url = os.getenv('DATABASE_URL') or _raise_postgresql_required()
        
        # Create engine
        engine = create_engine(database_url)
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Drop table
        logger.info("Dropping comprehensive_user_data_cache table...")
        db.execute(text("DROP TABLE IF EXISTS comprehensive_user_data_cache;"))
        db.commit()
        
        logger.info("✅ Comprehensive user data cache table dropped successfully!")
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error dropping cache table: {str(e)}")
        if 'db' in locals():
            db.close()
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage comprehensive user data cache table")
    parser.add_argument("--action", choices=["create", "drop"], default="create", 
                       help="Action to perform (create or drop table)")
    
    args = parser.parse_args()
    
    if args.action == "create":
        success = create_cache_table()
        if success:
            logger.info("🎉 Cache table setup completed successfully!")
        else:
            logger.error("💥 Cache table setup failed!")
            sys.exit(1)
    elif args.action == "drop":
        success = drop_cache_table()
        if success:
            logger.info("🗑️ Cache table dropped successfully!")
        else:
            logger.error("💥 Failed to drop cache table!")
            sys.exit(1)
