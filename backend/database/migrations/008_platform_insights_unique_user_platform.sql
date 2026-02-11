-- Migration: enforce unique platform insights task per user/platform for reconcile race safety
-- Date: 2026-02-10

-- Remove duplicate rows while keeping the oldest task per (user_id, platform).
DELETE FROM platform_insights_tasks t
USING platform_insights_tasks d
WHERE t.user_id = d.user_id
  AND t.platform = d.platform
  AND t.id > d.id;

-- Enforce uniqueness to prevent duplicates under concurrent reconcile calls.
CREATE UNIQUE INDEX IF NOT EXISTS idx_platform_insights_user_platform
ON platform_insights_tasks(user_id, platform);
