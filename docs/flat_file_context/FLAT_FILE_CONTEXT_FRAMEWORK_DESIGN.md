# Flat File Context Framework Design (Agent-Optimized)

## Purpose
Design a **compact, machine-first flat-file framework** for ALwrity AI agents.

This framework is optimized for:
- deterministic structure,
- minimal token footprint,
- fast parsing,
- high-signal retrieval,
- robust fallback behavior.

## Core Principles
1. **Agent-first, not human-first**
   - Keys are short and stable.
   - Avoid verbose prose in payloads.
   - Include only fields needed for reasoning and tool actions.

2. **Compact + predictable schema**
   - Fixed top-level keys in strict order.
   - Canonical value types (no shape drift).
   - Avoid polymorphic fields when possible.

3. **Dual-layer context**
   - `d` (full normalized data for deep reasoning).
   - `s` (summary/high-signal fast path for most agent reads).

4. **Fallback-safe design**
   - Every context doc includes source + freshness metadata.
   - If missing/stale, consumers fall back to DB then SIF semantic.

5. **Multi-tenant isolation**
   - Per-user file under `workspace/workspace_<safe_user_id>/agent_context/`.

---

## Canonical Context Envelope (compact)
```json
{
  "v": "1.0",
  "t": "onboarding.step2.website_analysis",
  "u": "<user_id>",
  "ts": "<iso8601>",
  "src": "onboarding_step2",
  "d": {},
  "s": {},
  "m": {
    "db": 0,
    "sb": 0,
    "q": []
  }
}
```

### Field map
- `v`: schema version
- `t`: context type
- `u`: user id
- `ts`: updated timestamp
- `src`: source writer
- `d`: canonical normalized data
- `s`: high-signal summary for quick agent use
- `m`: meta (`db`=data bytes, `sb`=summary bytes, `q`=query hints)

---

## Agent Readability Best Practices
- Prefer enums/controlled vocab over free text.
- Use compact keys and arrays for repetitive entities.
- Truncate long textual blobs unless explicitly required.
- Keep “quick facts” flattened.
- Separate operational metadata from semantic content.
- Include retrieval hints (`q`) for consistent query drafting.

---

## Write Pipeline Pattern
1. Normalize incoming source payload.
2. Derive compact summary (`s`) from normalized data.
3. Compute lightweight metadata (`m`).
4. Atomic write JSON file.
5. Emit writer version + timestamp.

## Read Pipeline Pattern
1. Attempt flat-file load.
2. Validate minimum envelope fields (`v,t,u,ts,d`).
3. Prefer `s` for quick tasks; use `d` for deeper reasoning.
4. If invalid/missing/stale: fallback DB -> SIF semantic.

---

## Scope Expansion Pattern
Apply same envelope for:
- Step 2: website analysis
- Step 3: research preferences + competitor snapshots
- Step 4: persona profile + platform personas

Only `t`, `d`, and `s` payload contracts should vary.

---

## Governance
- Schema changes require version bump (`v`).
- Backward compatibility policy: readers support N and N-1.
- Drift checks should compare canonical hash/checksum vs DB latest row.


## Document Context + End-User Journey Metadata
Each context file should carry explicit machine-oriented document metadata so agents understand *what this file is* before reading full payloads.

Suggested `document_context` fields:
- `audience`: `ai_agents`
- `purpose`: `fast_context_retrieval`
- `context_type`: step-scoped type identifier
- `journey`: stage/action/agent expectation
- `retrieval_contract`: preferred source + fallback order
- `context_window_guidance`: byte budget and summary-first policy

This block is intentionally compact and deterministic to reduce wasted token usage for agent planning.

## Context Window and Length Policy
- Keep combined `data + summary` under a defined byte budget where practical.
- Enforce summary-first reads in agent consumers.
- Truncate long textual fields in summaries; keep full text only in `data` when needed.
- Flag oversize docs in metadata so readers can skip low-priority sections.
- Prefer short, stable keys in machine envelopes and avoid natural-language verbosity.


## Implemented baseline controls
- Atomic file writes to avoid partial documents.
- Best-effort restricted file permissions (`0600`).
- Recursive sensitive-key redaction for payload snapshots.
- Payload size budget enforcement with deterministic trimming metadata.
- Internal document linking via `related_documents` and manifest index.


Security and isolation details: `docs/flat_file_context/FLAT_FILE_CONTEXT_SECURITY_AND_ISOLATION.md`


Step docs: `docs/flat_file_context/STEP2_FLAT_FILE_CONTEXT_DESIGN.md`, `docs/flat_file_context/STEP3_FLAT_FILE_CONTEXT_DESIGN.md`, `docs/flat_file_context/STEP4_FLAT_FILE_CONTEXT_DESIGN.md`, `docs/flat_file_context/STEP5_FLAT_FILE_CONTEXT_DESIGN.md`
