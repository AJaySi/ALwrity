-- Migration: Update onboarding_sessions.user_id from INTEGER to STRING
-- This migration updates the user_id column to support Clerk user IDs (strings)

-- Step 1: Alter the user_id column type from INTEGER to VARCHAR(255)
ALTER TABLE onboarding_sessions 
ALTER COLUMN user_id TYPE VARCHAR(255);

-- Step 2: Create an index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_user_id ON onboarding_sessions(user_id);

-- Note: This migration assumes no existing data needs to be preserved
-- If you have existing data with integer user_ids, you may need to:
-- 1. Backup the data first
-- 2. Clear the table or convert the integers to strings
-- 3. Then apply this migration

