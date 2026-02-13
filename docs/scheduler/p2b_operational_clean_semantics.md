# P2.B — Operational Clean Semantics (Week 6)

## Goals
- Make scheduler GET/status endpoints read-only and idempotent.
- Move reconcile/create behavior to explicit POST workflows.
- Define operational runbook and alert thresholds for on-call.

## Changes Delivered
1. **Read-only GET status path**
   - `GET /api/scheduler/platform-insights/status/{user_id}` no longer creates tasks.
   - `GET /api/scheduler/dashboard` no longer persists cumulative-stat corrections.

2. **Explicit reconcile endpoints**
   - `POST /api/scheduler/platform-insights/reconcile/{user_id}`
     - Creates missing connected-platform insight tasks.
     - Returns auditable details: created/skipped/failures and timestamp.
   - `POST /api/scheduler/dashboard/cumulative-stats/reconcile`
     - Rebuilds cumulative stats from event history.
     - Persists to `scheduler_cumulative_stats` when model/table is available.

3. **Race-safety hardening**
   - Added unique `(user_id, platform)` constraint/index on `platform_insights_tasks`.
   - Reconcile endpoint uses pre-create existence recheck and returns skipped records.

## Runbook
### A) Platform insights task gap detected
1. Confirm with GET status:
   - `GET /api/scheduler/platform-insights/status/{user_id}`
2. Run reconcile:
   - `POST /api/scheduler/platform-insights/reconcile/{user_id}`
3. Verify:
   - `created_platforms` expected; `failures` empty.
4. If failures exist:
   - inspect OAuth connectivity and DB errors.
   - rerun reconcile once issue fixed.

### B) Cumulative dashboard stats drift
1. Verify dashboard drift symptoms (mismatch vs event history).
2. Run explicit reconcile:
   - `POST /api/scheduler/dashboard/cumulative-stats/reconcile`
3. Confirm returned `stats` match expected event aggregates.

## Alerting Thresholds (initial)
- **Reconcile failure rate**: warning if `failures > 0` on manual/automated reconcile run.
- **Duplicate platform task attempts**: warning if `skipped_platforms` repeatedly non-empty for same user within 1h (indicates repeated reconcile callers).
- **Dashboard stat drift**: warning if cumulative totals differ from event-derived totals by > 1 check cycle for 10+ minutes.
- **Platform task coverage**: warning if connected platform count > active platform insight task count for > 30 minutes.

## Go / No-Go
### Go
- GET endpoints are read-only/idempotent.
- Reconcile flows are explicit and return auditable metadata.
- Unique constraint blocks duplicate platform tasks under races.

### No-Go
- Any GET endpoint mutates DB state.
- Concurrent reconcile still creates duplicates.
- Missing runbook or undefined on-call thresholds.
