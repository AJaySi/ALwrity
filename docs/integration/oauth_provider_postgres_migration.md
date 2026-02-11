# OAuth Provider PostgreSQL Migration (Read-Only + Dual-Write)

## Overview
This document captures the migration work to move OAuth provider token reads to PostgreSQL as the system of record, while **temporarily retaining SQLite writes** for rollback safety. The goals are to:

- Ensure monitoring and task restoration read from the PostgreSQL SSOT.
- Maintain existing runtime behavior during rollout (dual-write to SQLite).
- Enable Wix monitoring via backend token storage.

## What Changed

### 1) Provider Registry
A centralized provider registry now instantiates OAuth provider services (GSC, Bing, WordPress, Wix) to standardize token status checks and reduce direct SQLite access paths.

**Why**: Consistent provider access means monitoring and restoration can run through a single interface while the storage backend changes are isolated inside each provider.

### 2) Provider Services: PostgreSQL Reads + SQLite Dual-Write
Each provider service now:

- Creates PostgreSQL tables if needed.
- Reads token state from PostgreSQL.
- Continues writing to SQLite (dual-write) for rollback.

**Why**: This lets production use PostgreSQL for reads while retaining the legacy SQLite data path for quick fallback if needed.

### 3) Connected Platforms Detection
`get_connected_platforms` now reads connection status from PostgreSQL-backed provider services using each provider’s `get_user_token_status`.

**Why**: Connected-platform detection powers task restoration and monitoring. It must reflect the SSOT storage.

### 4) Wix Monitoring Enabled
`_check_wix_token` now checks backend storage (PostgreSQL) instead of frontend sessionStorage, enabling Wix monitoring tasks.

**Why**: Monitoring runs in backend tasks, so token checks must be server-side.

## Tables (PostgreSQL SSOT)

| Provider | Tokens Table | State Table |
| --- | --- | --- |
| GSC | `gsc_credentials` | `gsc_oauth_states` |
| Bing | `bing_oauth_tokens` | `bing_oauth_states` |
| WordPress | `wordpress_oauth_tokens` | `wordpress_oauth_states` |
| Wix | `wix_oauth_tokens` | N/A |

## Rollback / Dual-Write Notes

- All providers **still write to SQLite** after a PostgreSQL write.
- Reads now prefer PostgreSQL.
- If rollback is required, revert reads back to SQLite while preserving the dual-write path.

## Monitoring Behavior

- OAuth token monitoring now uses the provider registry.
- Wix monitoring is fully enabled using backend token storage.
- Failure states and alerts remain unchanged.

## Operational Requirements

Set environment variables:

```
PLATFORM_DATABASE_URL=postgresql://...
USER_DATA_DATABASE_URL=postgresql://...
```

## Validation Checklist

- Verify tables exist in PostgreSQL.
- Confirm provider token status calls read expected data.
- Confirm OAuth monitoring tasks run for GSC/Bing/WordPress/Wix.
