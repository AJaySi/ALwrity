# P2.A — Scheduler Data Model Consistency (User Identity Typing)

## Objective
Normalize scheduler execution log user identity handling for SaaS multi-tenant deployments while preserving backward compatibility.

## Problem
`task_execution_logs.user_id` is an integer (legacy), while scheduler API auth context uses string tenant identifiers.
This mismatch can cause incomplete tenant filtering and inconsistent dashboard visibility.

## Changes Implemented
1. **Canonical string identity added**
   - New column: `task_execution_logs.user_id_str VARCHAR(255)`.
   - New indexes:
     - `idx_task_execution_logs_user_id_str`
     - `idx_task_execution_logs_user_id_str_status_date`

2. **Compatibility reads enabled**
   - Execution-log reads now filter with:
     - `user_id_str = :user_id`
     - OR legacy fallback `CAST(user_id AS STRING) = :user_id`

3. **Compatibility writes enabled**
   - New log writes populate `user_id_str` whenever identity is known.
   - Legacy `user_id` integer is still populated when the source identity is numeric.

4. **Backfill migration added**
   - Existing rows with integer-only identity are backfilled:
     - `user_id_str = CAST(user_id AS VARCHAR)` for rows missing string identity.

5. **Validation report SQL added**
   - SQL report computes:
     - total rows,
     - rows with `user_id_str`,
     - legacy rows,
     - successfully backfilled legacy rows,
     - unresolved rows.

## Migration Plan
1. Apply migration `backend/database/migrations/007_task_execution_logs_user_id_str.sql`.
2. Run validation SQL `backend/scripts/task_execution_log_user_id_backfill_report.sql`.
3. Verify unresolved legacy rows are 0 or understood.

## Go/No-Go Criteria (P2.A)
### Go
- Tenant filtering works for mixed historical/new rows.
- Dashboard execution log API remains backward compatible.
- Backfill report shows no unexplained unresolved legacy rows.

### No-Go
- Tenant log visibility gaps persist for rows expected to be visible.
- API contract fields regress (`logs`, `total_count`, pagination keys, `task` object).
- Migration leaves orphaned/ambiguous rows without clear mitigation.

## Rollback Guidance
- Code rollback is safe because old integer field is untouched.
- DB rollback can ignore new column (non-breaking additive change), or remove it during maintenance.

## Future Cleanup (Post-transition)
- Move all writer paths to string-only user IDs.
- Remove legacy `user_id` integer reads after retention window.
- Optionally drop legacy integer column in a later major migration.
