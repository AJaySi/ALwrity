# Persona Data Table Migration Guide

## Overview
This guide explains how to create the `persona_data` table for storing Step 4 (Persona Generation) data from the onboarding flow.

## Background
The `persona_data` table was missing from the database schema, causing Step 4 onboarding data to only be saved to JSON files instead of the database. This migration adds the required table with proper user isolation.

## Migration Methods

### Method 1: Automatic Migration (Recommended)
The easiest way is to restart your backend server. The table will be created automatically when the application starts.

```bash
# Stop the backend if running (Ctrl+C)
# Then restart it:
python backend/start_alwrity_backend.py --dev
```

**How it works:**
- The `init_database()` function in `backend/services/database.py` (line 69) calls `OnboardingBase.metadata.create_all(bind=engine)`
- This automatically creates all missing tables defined in the `OnboardingBase` models
- Since we added the `PersonaData` model, it will be created on startup

### Method 2: Manual Migration Script
If you prefer to run the migration manually without restarting the backend:

```bash
# From the project root directory:
python backend/scripts/create_persona_data_table.py
```

**What this script does:**
1. Checks if the `persona_data` table already exists
2. Creates the table if it doesn't exist
3. Verifies the table was created successfully
4. Shows the table structure (columns and types)
5. Lists all onboarding-related tables and their status

### Method 3: SQL Migration (Production/Manual)
For production environments or manual database management:

```bash
# Connect to your PostgreSQL database and run:
psql -U your_username -d your_database -f backend/database/migrations/add_persona_data_table.sql
```

**Or using psql command:**
```sql
-- Connect to your database
\c your_database

-- Run the migration
\i backend/database/migrations/add_persona_data_table.sql

-- Verify the table was created
\dt persona_data
\d persona_data
```

## Table Structure

The `persona_data` table includes:

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `session_id` | INTEGER | Foreign key to `onboarding_sessions.id` |
| `core_persona` | JSONB | Core persona data (demographics, psychographics, etc.) |
| `platform_personas` | JSONB | Platform-specific personas (LinkedIn, Twitter, etc.) |
| `quality_metrics` | JSONB | Quality assessment metrics |
| `selected_platforms` | JSONB | Array of selected platforms |
| `created_at` | TIMESTAMP | When the record was created |
| `updated_at` | TIMESTAMP | When the record was last updated |

**Indexes:**
- `idx_persona_data_session_id` - For efficient session lookups
- `idx_persona_data_created_at` - For time-based queries

**Constraints:**
- Foreign key to `onboarding_sessions.id` with `ON DELETE CASCADE`

## Verification

After running the migration, verify it was successful:

### Using Python:
```python
from services.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()

if 'persona_data' in tables:
    print("✅ persona_data table exists")
    columns = inspector.get_columns('persona_data')
    for col in columns:
        print(f"   - {col['name']}: {col['type']}")
else:
    print("❌ persona_data table not found")
```

### Using SQL:
```sql
-- Check if table exists
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_name = 'persona_data'
);

-- Show table structure
\d persona_data
```

### Using the Backend Logs:
After restarting the backend, look for this log message:
```
Database initialized successfully with all models including subscription system and business info
```

Then, when a user completes Step 4, you should see:
```
✅ DATABASE: Persona data saved to database for user user_xxxxx
```

## Expected Behavior After Migration

Once the table is created and the backend is running with the updated code:

1. **Step 4 Completion:**
   - Persona data (corePersona, platformPersonas, qualityMetrics, selectedPlatforms) is saved to the database
   - Database logs confirm: `✅ DATABASE: Persona data saved to database for user {user_id}`

2. **User Isolation:**
   - Each user's persona data is stored separately using their `user_id`
   - Data is linked to the user's onboarding session

3. **Data Persistence:**
   - Persona data is no longer lost when JSON files are deleted
   - Data survives backend restarts
   - Data is accessible across different sessions

## Troubleshooting

### Table Already Exists Error
If you see "table already exists" errors:
- This is normal! It means the table was already created
- The migration scripts use `CREATE TABLE IF NOT EXISTS` to handle this
- No action needed

### Permission Denied
If you get permission errors:
```
ERROR: permission denied for schema public
```
**Solution:** Ensure your database user has CREATE TABLE permissions:
```sql
GRANT CREATE ON SCHEMA public TO your_database_user;
```

### Foreign Key Constraint Fails
If the `onboarding_sessions` table doesn't exist:
1. Run the full database initialization first:
   ```python
   from services.database import init_database
   init_database()
   ```
2. Then create the `persona_data` table

### Missing Database Connection
If you see "database connection" errors:
1. Check your `DATABASE_URL` environment variable
2. Ensure PostgreSQL/SQLite is running
3. Verify database credentials

## Rollback (If Needed)

To remove the `persona_data` table:

```sql
DROP TABLE IF EXISTS persona_data CASCADE;
```

**Warning:** This will delete all persona data. Use with caution!

## Related Files

- **Model:** `backend/models/onboarding.py` - `PersonaData` class (lines 149-183)
- **Service:** `backend/services/onboarding_database_service.py` - `save_persona_data()` method (lines 298-338)
- **Migration:** `backend/database/migrations/add_persona_data_table.sql`
- **Script:** `backend/scripts/create_persona_data_table.py`
- **Database Init:** `backend/services/database.py` - `init_database()` function (line 63-80)

## Summary

**Recommended approach for local development:**
```bash
# Just restart the backend - the table will be created automatically!
python backend/start_alwrity_backend.py --dev
```

**For production deployment:**
- The table will be created automatically on first deployment
- Or run the SQL migration manually before deployment
- No downtime required - the migration is additive only

## Questions?

If you encounter issues:
1. Check the backend logs for detailed error messages
2. Verify all onboarding tables exist using the verification script
3. Ensure your database user has proper permissions
4. Check that the `PersonaData` model is imported correctly in `backend/services/onboarding_database_service.py`

