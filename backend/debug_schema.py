#!/usr/bin/env python
"""Debug script to check database schema."""
import os
import sys
sys.path.insert(0, '.')

# Set up logging
os.environ['ALWRITY_VERBOSE'] = 'true'

from models.enhanced_strategy_models import Base
from models.daily_workflow_models import DailyWorkflowPlan, DailyWorkflowTask, TaskHistory

# Check what tables are registered with EnhancedStrategyBase
print("Tables registered with EnhancedStrategyBase:")
for table_name in Base.metadata.tables:
    print(f"  - {table_name}")
    if 'daily' in table_name:
        table = Base.metadata.tables[table_name]
        print(f"    Columns: {[col.name for col in table.columns]}")

# Now create the tables
from services.database import get_engine_for_user

test_user_id = "debug_test_user_12345"
engine = get_engine_for_user(test_user_id)

print(f"\nCreating tables for test user: {test_user_id}")
Base.metadata.create_all(bind=engine)

print("\n✅ Tables created successfully!")

# Verify the tables exist
import sqlite3
from services.database import get_user_db_path

db_path = get_user_db_path(test_user_id)
print(f"\nDatabase path: {db_path}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables in database: {tables}")
    
    if 'daily_workflow_plans' in tables:
        cursor.execute("PRAGMA table_info(daily_workflow_plans)")
        columns = cursor.fetchall()
        col_names = [col[1] for col in columns]
        print(f"\nColumns in daily_workflow_plans:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
else:
    print(f"❌ Database not found at {db_path}")
