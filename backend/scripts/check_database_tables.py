#!/usr/bin/env python3
"""
Script to check database tables and debug foreign key issues.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database import get_user_data_engine, get_platform_engine
from sqlalchemy import inspect
from loguru import logger

def check_database_tables():
    """Check what tables exist in both databases"""
    try:
        logger.info("Checking database tables...")
        
        # Check user data database
        logger.info("=== USER DATA DATABASE ===")
        user_engine = get_user_data_engine()
        user_inspector = inspect(user_engine)
        user_table_names = user_inspector.get_table_names()
        
        logger.info(f"Found {len(user_table_names)} user data tables:")
        for table_name in sorted(user_table_names):
            logger.info(f"  - {table_name}")
        
        # Check platform database
        logger.info("=== PLATFORM DATABASE ===")
        platform_engine = get_platform_engine()
        platform_inspector = inspect(platform_engine)
        platform_table_names = platform_inspector.get_table_names()
        
        logger.info(f"Found {len(platform_table_names)} platform tables:")
        for table_name in sorted(platform_table_names):
            logger.info(f"  - {table_name}")
            
        # Check if enhanced_content_strategies exists in user data database
        if 'enhanced_content_strategies' in user_table_names:
            logger.info("✅ enhanced_content_strategies table exists in user data database!")
            
            # Get columns for this table
            columns = user_inspector.get_columns('enhanced_content_strategies')
            logger.info(f"Columns in enhanced_content_strategies:")
            for column in columns:
                logger.info(f"  - {column['name']}: {column['type']}")
        else:
            logger.error("❌ enhanced_content_strategies table does not exist in user data database!")
            
        logger.info("✅ Dual database check completed successfully!")
            
    except Exception as e:
        logger.error(f"❌ Error checking database tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_database_tables()
