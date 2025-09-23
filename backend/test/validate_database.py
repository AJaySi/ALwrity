#!/usr/bin/env python3
"""
Database validation script for billing system
"""
import sqlite3
from datetime import datetime

def validate_database():
    conn = sqlite3.connect('alwrity.db')
    cursor = conn.cursor()
    
    print('=== BILLING DATABASE VALIDATION ===')
    print(f'Validation timestamp: {datetime.now()}')
    print()
    
    # Check subscription-related tables
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND (
            name LIKE '%subscription%' OR 
            name LIKE '%usage%' OR 
            name LIKE '%billing%' OR
            name LIKE '%pricing%' OR
            name LIKE '%alert%'
        )
        ORDER BY name
    """)
    tables = cursor.fetchall()
    
    print('=== SUBSCRIPTION TABLES ===')
    for table in tables:
        table_name = table[0]
        print(f'\nTable: {table_name}')
        
        # Get table schema
        cursor.execute(f'PRAGMA table_info({table_name})')
        columns = cursor.fetchall()
        print('  Schema:')
        for col in columns:
            col_id, name, type_name, not_null, default, pk = col
            constraints = []
            if pk:
                constraints.append('PRIMARY KEY')
            if not_null:
                constraints.append('NOT NULL')
            if default:
                constraints.append(f'DEFAULT {default}')
            constraint_str = f' ({", ".join(constraints)})' if constraints else ''
            print(f'    {name}: {type_name}{constraint_str}')
        
        # Get row count
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        count = cursor.fetchone()[0]
        print(f'  Row count: {count}')
        
        # Sample data for non-empty tables
        if count > 0 and count <= 10:
            cursor.execute(f'SELECT * FROM {table_name} LIMIT 3')
            rows = cursor.fetchall()
            print('  Sample data:')
            for i, row in enumerate(rows):
                print(f'    Row {i+1}: {row}')
    
    # Check for user-specific data
    print('\n=== USER DATA VALIDATION ===')
    
    # Check if we have user-specific usage data
    cursor.execute("SELECT DISTINCT user_id FROM usage_summary LIMIT 5")
    users = cursor.fetchall()
    print(f'Users with usage data: {[u[0] for u in users]}')
    
    # Check user subscriptions
    cursor.execute("SELECT DISTINCT user_id FROM user_subscriptions LIMIT 5")
    user_subs = cursor.fetchall()
    print(f'Users with subscriptions: {[u[0] for u in user_subs]}')
    
    # Check API usage logs
    cursor.execute("SELECT COUNT(*) FROM api_usage_logs")
    api_logs_count = cursor.fetchone()[0]
    print(f'Total API usage logs: {api_logs_count}')
    
    if api_logs_count > 0:
        cursor.execute("SELECT DISTINCT user_id FROM api_usage_logs LIMIT 5")
        api_users = cursor.fetchall()
        print(f'Users with API usage logs: {[u[0] for u in api_users]}')
    
    conn.close()
    print('\n=== VALIDATION COMPLETE ===')

if __name__ == '__main__':
    validate_database()
