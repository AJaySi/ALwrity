# Agent Flat-File Context System Review

## Scope
This review documents the **current implementation** of ALwrity's onboarding flat-file context system and compares it to the proposed **Direct-to-File Virtual Shell (VFS)** model.

---

## 1) Present Implementation (What Exists Today)

### 1.1 Storage model
- Context is stored per user under:
  - `backend/workspace/workspace_<safe_user_id>/agent_context/`
- Files are JSON documents, one per onboarding domain:
  - `step2_website_analysis.json`
  - `step3_research_preferences.json`
  - `step4_persona_data.json`
  - `step5_integrations.json`
  - `context_manifest.json`

### 1.2 Writer and reader
- `AgentFlatContextStore` is the core component that:
  - sanitizes user IDs for path safety,
  - writes documents atomically (`tempfile` + `os.replace`),
  - sets restrictive file permissions (`0600` best effort),
  - generates structured `agent_summary` objects,
  - updates a manifest index of available documents.
- Data is loaded by direct file reads from the same class (`load_stepX_context_document`).

### 1.3 Read-path fallback chain
`SIFIntegrationService` uses a strict fallback sequence for onboarding context retrieval:
1. **flat file** (`AgentFlatContextStore`)
2. **database** (`WebsiteAnalysis`, `ResearchPreferences`, `PersonaData`, etc.)
3. **SIF semantic index** (`TxtaiIntelligenceService.search`)

Step 5 uses `flat_file -> sif_semantic`.

### 1.4 Producer flow (onboarding persistence)
`StepManagementService` persists canonical snapshots to flat context when onboarding steps are saved:
- Step 2 website analysis
- Step 3 research preferences (and later competitor-enriched refresh)
- Step 4 persona data
- Step 5 integrations

### 1.5 Context optimization currently implemented
- Sensitive-key redaction in nested payloads (`api_key`, `token`, `secret`, etc.).
- Size budgeting with trimming (`DEFAULT_MAX_BYTES = 300_000`) and trim metadata.
- Generated summaries include:
  - quick facts,
  - retrieval hints (high-signal terms and suggested agent queries),
  - domain-specific focus blocks.
- Document context includes audience, retrieval contract, journey stage, related documents, and context-window guidance.

---

## 2) Comparison vs Proposed Direct-to-File VFS

## Strong alignment
The current system already matches the proposal in important ways:
- **Direct-to-file persistence** instead of DB-backed retrieval for fast reads.
- **Manifest/index concept** (`context_manifest.json`) that can act like a precomputed path map.
- **Agent-first retrieval semantics** (summary-first contract and fallback policy).
- **Operational safety controls** (atomic writes, redaction, path sanitization).

## Gaps vs full virtual shell abstraction
The following pieces are not fully implemented as described in your proposed architecture:
- No explicit **virtual shell provider** (`IFileSystem`) exposing `ls/cat/grep/find` commands.
- No always-live, process-level **in-memory `Map<virtualPath, absolutePath>`** for path lookups.
- No native glob/query command layer for agent shell UX.
- Not currently **read-only enforced at API surface** (writes are intentionally allowed by onboarding services to refresh context).

---

## 3) Practical Recommendation: Incremental VFS Evolution

1. **Introduce a read-only VFS facade for agents**
   - Keep `AgentFlatContextStore` as the write path for trusted onboarding services.
   - Add `AgentContextVFS` read adapter exposing:
     - `ls(path)` from manifest,
     - `cat(path)` mapped to underlying JSON,
     - `find(glob)` on virtual keys,
     - `grep(query)` with path prefilter + stream scan.

2. **Promote manifest to a first-class path map**
   - Build and cache an in-memory map on service startup or first access.
   - Refresh map when manifest `updated_at` changes.

3. **Add explicit write policy boundaries**
   - Agent-facing interface: hard read-only (`EROFS`).
   - Internal system service interface: allow writes for onboarding synchronization.

4. **Metadata strategy for grep ranking**
   - Prioritize in order:
     1) `agent_summary.quick_facts`
     2) `agent_summary.retrieval_hints.high_signal_terms`
     3) `document_context.context_type` and `journey.stage`
     4) full `data` body

---

## 4) Response to the Metadata Header Question

> "Does your current `.txt` optimization include specific metadata headers (like YAML frontmatter) that the grep tool should prioritize?"

For this implementation, context is currently persisted as structured JSON (not `.txt` with YAML frontmatter). Equivalent high-value metadata already exists and should be prioritized for search/ranking:
- `context_type`
- `updated_at`
- `agent_summary.quick_facts`
- `agent_summary.retrieval_hints.high_signal_terms`
- `document_context.journey.stage`
- `document_context.related_documents`

If you later move to `.txt` transport files, mirror these as frontmatter fields to preserve retrieval quality.

---

## 5) Bottom line
Your current onboarding flat-file context implementation is already a strong "shim" architecture and close to the proposed model. The biggest missing piece is a dedicated virtual-shell read interface (`ls/cat/grep/find`) backed by a persistent path-map cache and a clear read-only contract for agent execution contexts.

---

## 6) Implemented Follow-up (VFS Adapter + Workspace Guide)

The following enhancements are now implemented:

1. **Auto-generated workspace map**
   - The system now generates `workspace_<user>/README.md` whenever `context_manifest.json` is updated.
   - The README includes:
     - available context files,
     - key signal hints from `agent_summary.retrieval_hints.high_signal_terms`,
     - journey-stage hints,
     - virtual path mappings and retrieval strategy guidance.

2. **Read-only VFS facade**
   - Added `AgentContextVFS` with:
     - `list_context()` (`ls` equivalent),
     - `search_context()` (`grep` equivalent; prioritizes `high_signal_terms` and `quick_facts`),
     - `read_context_file()` (`cat` equivalent; large-file summary mode + subkey drilldown),
     - explicit write rejection (`EROFS`).

3. **Virtual path support**
   - `/env/summary` maps to `AgentFlatContextStore.generate_total_summary()`.
   - `/steps/website`, `/steps/research`, `/steps/persona`, `/steps/integrations` map to step documents.

4. **System-prompt helper**
   - Added `build_filesystem_header(user_id)` to inject a compact file availability + priority hint block into agent startup prompts.

5. **Merged context helper in SIF integration**
   - `SIFIntegrationService.get_merged_flat_context()` now provides a unified view across all available flat files while preserving existing per-step retrieval methods.

6. **Basic file-level security hardening**
   - Workspace and context directories are now explicitly forced to `0700`.
   - Context and workspace files are written with strict `0600`.
   - Added path sandboxing to ensure requested paths cannot escape user workspace roots.
   - Restricted context-file loading to an allowlist of known onboarding context documents.
   - Added deterministic per-user secret derivation from `.env` (`FILE_ENCRYPTION_SALT` + `safe_user_id`) with non-sensitive fingerprints for audit/debug and future encryption-at-rest rollout.

7. **Tool-logic enhancement (coarse-to-fine search)**
   - `search_context` now performs a two-pass retrieval:
     1) high-relevance summary match pass (`high_signal_terms`, `quick_facts`),
     2) parallelized stream scan pass over sandboxed allowlisted files for supporting details.
   - Results include relevance labels, snippets, and line numbers for body matches.
   - Large-result behavior now reports truncation guidance (show top 10 and suggest narrower keywords).
   - `inspect_file` now provides token-saving behavior: full return for small files, or `agent_summary` + top-level keys for larger files, with key-level zoom-in support.

8. **Retrieval robustness roadmap (next hardening phase)**
   - **Query normalization:** Add synonym expansion and typo-tolerant matching (e.g., `tone` ≈ `brand voice`) before coarse/fine passes.
   - **Confidence scoring:** Return confidence tiers that blend source freshness (`updated_at`), summary-match strength, and match density.
   - **Field-aware boosting:** Weight matches by field priority (`high_signal_terms` > `quick_facts` > `data`) and document recency.
   - **Deduplicated evidence:** Collapse repeated hits from the same file/key into one clustered result with a single best snippet and hit count.
   - **Fallback query reformulation:** If zero hits, automatically retry with narrow/expanded variants and return attempted queries.
   - **Answerability contract:** Add a lightweight `can_answer` signal in search responses so orchestrators can decide whether to ask follow-up questions or fetch more context.
   - **Evaluation harness:** Track retrieval metrics over golden queries (`precision@k`, `MRR`, zero-hit rate, stale-hit rate) in CI to prevent relevance regressions.

9. **Collaborative VFS namespace (shared memory mode)**
   - Added optional `project_id` support to `AgentContextVFS` with isolated root: `workspace/project_<project_id>/`.
   - Introduced `scratchpad/` for collaborative writes while keeping onboarding `agent_context` read-first.
   - Added `write_shared_note(...)` with advisory locking (`flock`) and strict filename/path validation.
   - Added append-only `activity_log.jsonl` via `append_activity_log(...)` for watchdog/event-driven coordination.
   - Maintains owner-only permissions (`0700` scratchpad dir, `0600` files) and audit trails for shared writes.

10. **Testing readiness upgrades**
   - Added automated tests for:
     - query reformulation + `can_answer` behavior in `search_context`,
     - large-file progressive disclosure behavior in `inspect_file`,
     - collaborative write path (`write_shared_note`) and append-only activity logging.
   - Test module: `backend/tests/test_agent_context_vfs.py`.
   - These tests provide a baseline regression harness for VFS retrieval quality and shared-memory safety.
