-- Migration: Add user_id column to task_execution_logs for user isolation
-- Date: 2025-01-XX
-- Purpose: Enable user isolation tracking in scheduler task execution logs

-- Add user_id column (nullable for backward compatibility with existing records)
ALTER TABLE task_execution_logs 
ADD COLUMN user_id INTEGER NULL;

-- Create index for efficient user filtering and queries
CREATE INDEX IF NOT EXISTS idx_task_execution_logs_user_id 
ON task_execution_logs(user_id);

-- Create composite index for common query patterns (user_id + status + execution_date)
CREATE INDEX IF NOT EXISTS idx_task_execution_logs_user_status_date 
ON task_execution_logs(user_id, status, execution_date);

-- Note: Backfilling existing records would require joining with monitoring_tasks 
-- and enhanced_content_strategies tables. This can be done in a separate migration
-- or during a maintenance window. For now, existing records will have user_id = NULL.

