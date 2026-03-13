# Backend Startup Readiness Behavior

This document describes the startup/readiness checks now performed by the backend in both `backend/main.py` and `backend/app.py`.

## What startup validates

At startup, the backend now runs a dedicated health routine before scheduler startup:

1. **Workspace root check**
   - Verifies the workspace root directory exists.
   - Verifies it is writable using an actual write/delete probe.

2. **Database open/create check**
   - **Single-tenant mode** (`default_engine` enabled): validates global DB initialization and a `SELECT 1` connectivity query.
   - **Multi-tenant mode** (`default_engine` disabled): resolves at least one tenant DB path and validates DB session creation/query using:
     - the first discovered tenant workspace (preferred), or
     - a synthetic startup tenant (`startup_synthetic`) when no tenant exists yet.

3. **Schema compatibility check**
   - Confirms presence of required tables/columns for baseline migration compatibility:
     - `onboarding_sessions`: `id`, `user_id`, `updated_at`
     - `daily_workflow_plans`: `id`, `user_id`, `generation_mode`, `fallback_used`

## Warning vs failure conditions

### Multi-tenant mode

- **Warning**
  - No existing tenant workspace at startup. A synthetic tenant path/session check is used.
- **Failure**
  - Workspace root missing or not writable.
  - Tenant DB path resolution fails.
  - Tenant DB session/query fails.
  - Required schema tables/columns missing.

### Single-tenant mode

- **Failure**
  - Global DB initialization/connectivity fails.
  - Workspace root missing or not writable.

## Fail-fast behavior

Failures are always logged at **error** level.

Startup fail-fast is controlled by:

- `ALWRITY_FAIL_FAST_STARTUP=true|false` (explicit override), or
- if unset, defaults to **true in production** (`APP_ENV` or `ENV` is `production`/`prod`), and **false otherwise**.

When fail-fast is active and startup checks fail, startup raises and the process exits instead of running in degraded mode.

## Readiness endpoint

`GET /health/readiness`

- Requires authenticated context.
- Returns:
  - latest startup check report, and
  - auth-context tenant readiness validation (user DB path resolution + session/query check).

This helps operators distinguish:

- platform startup health, vs
- per-tenant readiness under real auth context.
