# Flat File Context Security, Isolation, and Size Controls

## Objective
Provide minimal but practical security for agent flat-file context with strong end-user isolation and bounded document growth.

## Isolation model
- Per-user namespace: `workspace/workspace_<safe_user_id>/agent_context/`
- Sanitized user IDs only (`[a-zA-Z0-9_-]`) to prevent path traversal.
- Reader-side user check: loaded document `user_id` must match requesting user context.

## Minimal security controls implemented
1. **Atomic writes**
   - Context files are written via temporary file + `os.replace`.
   - Prevents partial/corrupt files under concurrent writes.
2. **File permissions**
   - Context files are best-effort set to `0600`.
3. **Sensitive key redaction**
   - Recursive redaction for key patterns like `api_key`, `token`, `secret`, `password`, `authorization`, `cookie`.
4. **Manifest index**
   - `context_manifest.json` gives agents a controlled map of available docs and relationships.

## Size and context-window controls
- Byte budget for raw document payloads (`DEFAULT_MAX_BYTES`).
- If oversize, low-priority/heavy sections are trimmed first (`raw_*`, large snapshots, heavy arrays).
- Trim metadata is preserved under `meta.trim` for traceability.
- Agent policy remains summary-first (`agent_summary` before `data`).

## Internal document linking
- Each context file includes `document_context.related_documents`.
- Manifest includes per-document `related_documents` links.
- This enables agents to:
  1. read one document,
  2. discover related context files,
  3. fetch only relevant next documents.

## Recommended next steps
- Add optional file-level signatures/HMAC for tamper evidence.
- Add checksum per section to detect DB drift.
- Add staleness policy (`ttl_s`, `stale_after`) and auto-refresh triggers.
