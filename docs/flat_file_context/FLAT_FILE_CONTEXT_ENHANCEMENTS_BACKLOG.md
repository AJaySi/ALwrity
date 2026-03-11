# Flat File Context Enhancements Backlog

This document tracks next-phase implementation items for the flat-file context framework.

## 1) TTL/Refresh Hints + Freshness Policy
### Objective
Prevent stale agent decisions by adding explicit freshness semantics.

### Proposed additions
- Add `m.ttl_s` (seconds) and `m.stale_after` (timestamp) to context envelope.
- Add `m.refresh_recommended` boolean.
- Define per-context defaults (Step 2 likely long TTL, but still bounded).

### Acceptance criteria
- Reader utility can classify context as `fresh|stale|expired`.
- Fallback to DB/SIF triggered automatically when stale policy requires.

---

## 2) Optional `.json.gz` Companion for Large Payloads
### Objective
Reduce disk footprint and IO for large context payloads.

### Proposed additions
- Write primary `.json` always.
- If payload exceeds threshold (e.g., >256 KB), write `.json.gz` companion.
- Add pointer metadata (`m.gz=true`, `m.gz_path`).

### Acceptance criteria
- Reader transparently supports JSON + GZIP variants.
- No regression for small payloads.

---

## 3) Section Checksums for Drift Detection
### Objective
Detect inconsistencies between flat-file context and database state.

### Proposed additions
- Add checksums per section (`d.brand`, `d.seo`, `d.audience`, etc.) under `m.chk`.
- Persist DB-row reference (`m.db_ref`) with latest row id/timestamp.
- Add `verify_drift()` utility.

### Acceptance criteria
- Drift check can flag `in_sync|partial_drift|out_of_sync`.
- On drift, reader suggests refresh + fallback path.

---

## 4) Extend Pattern to Step 3 and Step 4
### Objective
Standardize agent context retrieval across onboarding steps.

### Proposed additions
- `step3_research_context.json`
- `step4_persona_context.json`
- Shared envelope with step-specific `d/s` contracts.

### Acceptance criteria
- Same fallback chain works for step-specific readers.
- SIF agents can consume common interface across Step 2/3/4.

---

## Suggested implementation order
1. TTL/freshness
2. Checksums/drift detection
3. Step 3/4 expansion
4. Optional gzip optimization
