-- Migration: Add canonical string user identity to task_execution_logs
-- Date: 2026-02-10
-- Purpose: SaaS multi-tenant compatibility during transition from integer user_id to string user IDs.

ALTER TABLE task_execution_logs
ADD COLUMN IF NOT EXISTS user_id_str VARCHAR(255) NULL;

CREATE INDEX IF NOT EXISTS idx_task_execution_logs_user_id_str
ON task_execution_logs(user_id_str);

CREATE INDEX IF NOT EXISTS idx_task_execution_logs_user_id_str_status_date
ON task_execution_logs(user_id_str, status, execution_date);

-- Legacy compatibility backfill:
-- If a row only has integer user_id, populate user_id_str with its text representation.
UPDATE task_execution_logs
SET user_id_str = CAST(user_id AS VARCHAR)
WHERE user_id_str IS NULL
  AND user_id IS NOT NULL;
