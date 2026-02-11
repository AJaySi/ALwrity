# Scheduler SaaS Rollout — Stage Gates and Minimal CI/CD Matrix

This document codifies the **exact Go/No-Go gates** and a **minimal must-pass CI/CD matrix** for scheduler rollout.

---


## Current Completion State

Implementation status and handoff checklist are tracked in:
- `docs/scheduler/integration_handoff_status.md`

Related implementation/runbook docs:
- `docs/scheduler/p2a_data_model_consistency.md`
- `docs/scheduler/p2b_operational_clean_semantics.md`

---

## Stage Gates (Exact Go/No-Go)

## Gate 1 (end Week 2) — P0 Complete
### Go
- P0 scope complete and merged.
- No scheduler API contract regressions for dashboard-critical endpoints.
- No tenant leakage observed in scheduler reads.

### No-Go
- Any response contract break in scheduler dashboard/log endpoints.
- Any cross-tenant data exposure.

### Required checks
- Contract and guardrail tests pass (see Matrix A/C/F).
- Tenant access control tests pass (see Matrix B).

---

## Gate 2 (end Week 4) — HA Canary Stable
### Go
- Two-replica canary runs with **exactly one leader**.
- No duplicate dispatch in timeout/lease stress scenarios.
- Failover observed and stable without split-brain.

### No-Go
- Split-brain leadership.
- Duplicate dispatch under canary or timeout stress.

### Required checks
- Leadership tests pass (Matrix D).
- Execution lifecycle timeout/lease tests pass (Matrix C + D).

---

## Gate 3 (end Week 6) — Multi-tenant + Ops Readiness
### Go
- User-ID typing consistency complete across mixed historical/new records.
- GET endpoints are read-only, mutation only via explicit reconcile POST/worker paths.
- Runbooks + alert thresholds published and acknowledged by on-call.

### No-Go
- Mixed user-ID rows not queryable by tenant.
- Any GET endpoint mutates DB state.
- Missing operational docs/alert wiring.

### Required checks
- Data model compatibility tests pass (Matrix E).
- Operational semantics tests pass (Matrix C/F).
- Docs reviewed/approved (runbooks + thresholds).

---

## Minimal CI/CD Test Matrix (Must-pass)

## A) API Contract (Must-pass)
Validate response keys/types and frontend compatibility fields (`total_count`, `limit`, `offset`, `has_more`, etc.).

**Command**
```bash
PYTHONPATH=backend pytest -q backend/test/test_scheduler_p0b_guardrails.py
```

---

## B) Tenant Isolation (Must-pass)
User A cannot access User B resources; cross-tenant checks return 403 where required.

**Command**
```bash
PYTHONPATH=backend pytest -q backend/test/test_scheduler_tenant_isolation_matrix.py
```

---

## C) Scheduler Core Behavior (Must-pass)
- Check cycle persists event log and cumulative pipeline behavior is healthy.
- Startup path avoids closed-session regressions.
- Timeout lifecycle handling does not leak pending tasks.

**Commands**
```bash
PYTHONPATH=backend pytest -q backend/test/test_scheduler_p0b_guardrails.py
PYTHONPATH=backend pytest -q backend/test/test_scheduler_p1b_execution_lifecycle.py
```

---

## D) HA Leadership (Must-pass from Week 3+)
- Two scheduler instances elect one leader.
- Failover is safe; no duplicate execution.

**Command**
```bash
PYTHONPATH=backend pytest -q backend/test/test_scheduler_p1a_leadership.py
```

---

## E) Data Migration/Typing (Must-pass from Week 5+)
- Old + new typed user-id rows query correctly.
- No execution-log visibility loss in mixed datasets.

**Commands**
```bash
PYTHONPATH=backend pytest -q backend/test/test_scheduler_p2a_data_model_consistency.py
# Post-migration validation SQL:
# backend/scripts/task_execution_log_user_id_backfill_report.sql
```

---

## F) Frontend Integration Smoke (Must-pass)
Scheduler dashboard critical sections render from backend payloads:
- stats cards
- jobs tree
- execution logs
- event history filters

**Backend payload smoke (CI-safe)**
```bash
PYTHONPATH=backend pytest -q backend/test/test_scheduler_p0b_guardrails.py
PYTHONPATH=backend pytest -q backend/test/test_scheduler_p2b_operational_semantics.py
```

If a dedicated browser E2E environment exists, add a dashboard smoke Playwright job that asserts no shape/parse runtime errors.

---

## Suggested pipeline order
1. **Fast gate**: A + B
2. **Core gate**: C
3. **Stage-aware gate**: D (Week 3+), E (Week 5+)
4. **Release gate**: F + docs approval
