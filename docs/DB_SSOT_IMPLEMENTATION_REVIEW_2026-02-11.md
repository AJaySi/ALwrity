# Database SSOT Implementation Review (2026-02-11)

## Scope
This review validates the current backend implementation against the SSOT expectations for:

- PostgreSQL-only dual database architecture
- SSOT core database functions
- SSOT core schema tables
- RLS and multi-tenant patterns
- Connection pooling configuration

## Validation Summary

### ✅ Confirmed Implemented

1. **All 8 SSOT core functions exist in `backend/services/database.py`**
   - `get_platform_db()`
   - `get_user_data_db()`
   - `set_user_context()`
   - `test_connections()`
   - `get_database_info()`
   - `setup_row_level_security()`
   - `init_databases()`
   - `close_databases()`

2. **Core schema tables are present in model files**
   - `users`
   - `user_subscriptions`
   - `subscription_plans`
   - `platform_usage_logs`
   - `user_profiles`
   - `user_projects`
   - `user_content_assets`
   - `user_personas`

3. **PostgreSQL connection pool defaults match SSOT target values**
   - `DB_POOL_SIZE` default = `20`
   - `DB_MAX_OVERFLOW` default = `30`
   - `DB_POOL_RECYCLE` default = `3600`

4. **Dual-database initialization logic exists**
   - Platform and user-data engines/session makers are separate.
   - `init_database()` creates platform and user-data table groups.

### ⚠️ Gaps / Risks Found (Actual)

1. **Duplicate table definitions exist for subscription tables**
   - `subscription_plans` and `user_subscriptions` are defined in multiple model modules.
   - This increases risk of schema drift and migration conflicts.

2. **Multiple independent `declarative_base()` registries are used**
   - Core SSOT models (`users`, `user_subscriptions`, etc.) each define their own `Base`.
   - Cross-model relationships/foreign keys split across registries can cause brittle mapper behavior and DDL ordering issues over time.

3. **RLS policy setup is not idempotent for policy creation**
   - `setup_row_level_security()` uses plain `CREATE POLICY` without `IF NOT EXISTS` handling or drop/recreate strategy.
   - Re-running initialization can produce duplicate-policy errors (currently logged as warnings).

4. **`set_user_context()` session variable scope assumes strict call ordering**
   - RLS uses `current_setting('app.current_user_id')` and requires context to be set before protected queries.
   - Missing centralized dependency/middleware may lead to accidental RLS failures in endpoints that forget to set context.

## Conclusion

The previously reported “critical missing implementation” claims are **not accurate** for core SSOT functions and table presence. The implementation includes those components.

However, there are **real architecture-hardening issues** to address before confidently calling the system production-ready:

- Consolidate duplicate subscription model definitions.
- Move SSOT models to a consistent metadata strategy where appropriate.
- Make RLS setup idempotent and migration-safe.
- Enforce user-context setup systematically in request lifecycle.

## Recommended Next Actions

1. Canonicalize subscription schema in one module and deprecate duplicates.
2. Introduce migration-backed DDL (Alembic) for RLS/policy lifecycle.
3. Add tests for:
   - function existence/import stability
   - dual-engine connectivity checks
   - repeated `setup_row_level_security()` runs
4. Add a FastAPI dependency that sets user context once per request for user-data routes.
