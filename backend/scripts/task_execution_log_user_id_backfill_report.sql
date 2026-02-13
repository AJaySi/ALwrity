-- Validation report for task_execution_logs user identity transition.
-- Run after migration 007_task_execution_logs_user_id_str.sql.

SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE user_id_str IS NOT NULL) AS rows_with_user_id_str,
    COUNT(*) FILTER (WHERE user_id IS NOT NULL) AS rows_with_legacy_user_id,
    COUNT(*) FILTER (WHERE user_id IS NOT NULL AND user_id_str = CAST(user_id AS VARCHAR)) AS backfilled_from_legacy_int,
    COUNT(*) FILTER (WHERE user_id IS NOT NULL AND user_id_str IS NULL) AS unresolved_legacy_rows,
    COUNT(*) FILTER (WHERE user_id IS NULL AND user_id_str IS NULL) AS rows_without_any_identity
FROM task_execution_logs;
