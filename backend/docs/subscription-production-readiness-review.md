# ALwrity Subscription System - Production Readiness Review

Date: 2026-02-11
Scope reviewed:
- `backend/api/subscription/routes/*`
- `backend/services/subscription/*`
- `backend/models/subscription_models.py`

## Executive Summary

The subscription foundation is strong (plan modeling, usage logs, cost tracking, renewal history), but there were security and operational gaps that would have blocked production readiness for real users. The most severe issue was missing authorization checks on several user-scoped endpoints.

### Overall readiness verdict

**Conditionally ready** after this patch for basic production rollout, with follow-up work required for strict billing correctness at scale.

---

## Critical Findings

### 1) IDOR/data exposure risk on user-scoped subscription endpoints (**FIXED in this patch**)

Previously, some endpoints accepted a `user_id` path parameter but did not authenticate/authorize the caller against that `user_id`, enabling potential cross-user access.

#### Endpoints hardened in this patch
- `GET /usage/{user_id}/trends`
- `GET /dashboard/{user_id}`
- `GET /alerts/{user_id}`
- `POST /alerts/{alert_id}/mark-read` (ownership now enforced by alert owner)

### What changed
- Added `current_user: Dict[str, Any] = Depends(get_current_user)` to these handlers.
- Enforced `verify_user_access(user_id, current_user)` for user-id-scoped reads.
- Enforced `verify_user_access(str(alert.user_id), current_user)` before marking an alert as read.

---

## High-Priority Follow-up Risks (Not changed in this patch)

### 2) Limit-check caching is in-memory and process-local

Both usage enforcement and pricing limit checks use short-lived in-memory caches. This improves performance, but in multi-worker/multi-instance deployments it can produce inconsistent enforcement windows.

**Recommendation:** move limit-check cache to shared storage (Redis) or reduce cache scope to only non-authoritative hints.

### 3) Billing period keyed only by `YYYY-MM`

Current billing period calculations rely on calendar month strings, not true per-user subscription cycle anchors. For users who subscribe mid-month, this can diverge from exact billing cycle boundaries.

**Recommendation:** derive period keys from `current_period_start/current_period_end` and store immutable period identifiers tied to subscription cycle.

### 4) Monetary values stored as `Float`

Cost and billing fields use floating-point columns (`Float`), which can accumulate rounding drift in high volume billing systems.

**Recommendation:** migrate billing-critical monetary fields to fixed precision decimal types (e.g., `Numeric(12,6)`), and ensure all arithmetic uses `Decimal`.

---

## Production Readiness Checklist

### Security
- [x] User-scoped endpoints enforce authentication + authorization.
- [x] Alert mutation endpoint verifies ownership.
- [ ] Add explicit admin-only policies for any cross-user operational endpoints (if needed).

### Billing integrity
- [x] Per-call usage logs and summary tables exist.
- [x] Subscription renewal history is recorded.
- [ ] Move monetary accounting to decimal-backed persistence.
- [ ] Align period accounting with true subscription cycle boundaries.

### Scale & reliability
- [x] Basic caching exists to reduce DB pressure.
- [ ] Use shared cache for distributed deployments.
- [ ] Add load/concurrency validation around limit enforcement race windows.

### Observability
- [x] Extensive logging exists around usage checks and tracking.
- [ ] Add dashboards/alerts for failed subscription checks and auto-renew failures.

---

## Rollout Recommendation

Proceed with controlled rollout after this patch, with a short follow-up hardening sprint focused on:
1. Shared/distributed cache strategy for limit enforcement.
2. Decimal-based billing precision.
3. Subscription-cycle-accurate period accounting.

