# Backend Log RCA Tracker

## Purpose

This document is the working catalog for backend issues observed in runtime logs.

For each issue, capture:
- error signature
- observed symptoms
- likely root cause analysis
- confidence level
- files to inspect/edit
- fix strategy notes
- validation steps
- status

## Triage Rules

- Do not fix directly from logs alone unless root cause is confirmed.
- Prefer grouping repeated log lines under one issue.
- Track the first failing subsystem, then downstream effects.
- Separate configuration problems from code defects.
- Keep this document updated before and after each fix.

## Issue 1: Clerk token verification failures on authenticated endpoints

- **Status**: Open
- **Severity**: High
- **Subsystem**: Authentication / request pipeline
- **Error signatures**:
  - `Unverified token rejected (production).`
  - `AUTHENTICATION ERROR: Token verification failed for endpoint: GET /api/...`
- **Observed endpoints in logs**:
  - `/api/content-planning/monitoring/lightweight-stats`
  - `/api/content-planning/monitoring/health`
  - `/api/subscription/dashboard/...`
  - `/api/subscription/alerts/...`
  - `/api/subscription/status/...`
- **Observed behavior**:
  - Requests reach authenticated endpoints.
  - Clerk verification fails.
  - Fallback unverified decode path is attempted.
  - Production mode rejects the token.
- **Primary RCA hypothesis**:
  - The backend is receiving bearer tokens that do not successfully validate against the resolved Clerk JWKS/issuer configuration.
  - The middleware then falls back to unverified decode, but production mode explicitly rejects that path.
- **Secondary RCA hypotheses**:
  - Frontend token/audience/issuer mismatch.
  - Wrong Clerk environment variables loaded in backend.
  - Issuer-derived JWKS URL resolution is inconsistent with actual Clerk instance.
  - Requests may be sent before a valid session token is available.
- **Evidence in code**:
  - `backend/middleware/auth_middleware.py`
    - `ClerkAuthMiddleware.__init__`
    - `ClerkAuthMiddleware.verify_token`
    - `get_current_user`
  - Relevant logic:
    - derives JWKS URL from token issuer or cached publishable key instance
    - falls back to `jwt.decode(..., verify_signature=False)`
    - rejects unverified tokens when `ALLOW_UNVERIFIED_JWT_DEV` is false
- **Likely files to inspect/edit later**:
  - `backend/middleware/auth_middleware.py`
  - possibly frontend auth/session request layer if token attachment is inconsistent
- **Confidence**: Medium
- **Root-cause questions to answer**:
  - Are `CLERK_SECRET_KEY` and publishable key values from the same Clerk instance?
  - Is the token issuer exactly matching the intended Clerk environment?
  - Are failing requests sent with stale, dev, or cross-environment tokens?
  - Are these requests triggered before Clerk session hydration on the frontend?
- **Validation after fix**:
  - Authenticated endpoints return 200 with verified user context.
  - No `Unverified token rejected (production)` log spam for healthy requests.

## Issue 2: Hugging Face structured JSON generation failing with model not found

- **Status**: Open
- **Severity**: High
- **Subsystem**: LLM provider / workflow generation
- **Error signatures**:
  - `HF structured model not found: %s. Trying fallback model.`
  - `Hugging Face API call failed: Not Found`
  - `HF structured model not found (no response_format path): %s`
  - `Hugging Face structured JSON generation failed: NotFoundError: Not Found`
  - `[llm_text_gen] Provider huggingface failed: RetryError[...]`
- **Observed behavior**:
  - Structured JSON call tries primary model.
  - Fallback model sequence also fails.
  - Retry without `response_format` still fails with `NotFound`.
  - Upstream caller falls through to another provider or fallback path.
- **Primary RCA hypothesis**:
  - The configured Hugging Face model identifier is invalid, unavailable to the account/provider, or incompatible with the current OpenAI-compatible Hugging Face endpoint.
- **Secondary RCA hypotheses**:
  - Base URL/API key/provider configuration is wrong.
  - Fallback model list contains provider-specific model ids not available in the current account/region.
  - Structured generation path assumes chat completions support for models that only exist on a different inference route.
- **Evidence in code**:
  - `backend/services/llm_providers/huggingface_provider.py`
    - `_fallback_model_sequence`
    - `huggingface_structured_json_response`
  - The code retries:
    - with `response_format={"type": "json_object"}`
    - then again without `response_format`
  - Both paths still fail with `NotFoundError`, which points more strongly to model/base-url availability than schema formatting.
- **Likely files to inspect/edit later**:
  - `backend/services/llm_providers/huggingface_provider.py`
  - provider selection/orchestration file calling Hugging Face as primary for structured JSON
  - environment/config file for HF model names and API base URL
- **Confidence**: High
- **Root-cause questions to answer**:
  - Which exact model string is being passed as the primary model in the failing call?
  - What base URL and API key are being used for the OpenAI client?
  - Are the fallback model ids valid for the currently configured Hugging Face inference provider?
- **Validation after fix**:
  - A structured JSON test request succeeds with the intended model or a verified fallback.
  - No `NotFoundError` for the chosen model list.

## Issue 3: txtai indexing attempted before service initialization completes

- **Status**: Open
- **Severity**: Medium
- **Subsystem**: Semantic indexing / background tasks
- **Error signatures**:
  - `Cannot index content - service not initialized for user ...`
- **Observed behavior**:
  - Background indexing is triggered.
  - `TxtaiIntelligenceService.index_content` calls `_ensure_initialized()`.
  - `_ensure_initialized()` starts background initialization and returns immediately.
  - `index_content` then checks `_initialized`, sees false, and fails fast.
- **Primary RCA hypothesis**:
  - There is a race condition between lazy background initialization and immediate indexing/search calls.
  - `SIF_FAIL_FAST=true` (default) causes operations to raise RuntimeError instead of gracefully deferring.
- **Evidence in code**:
  - `backend/services/intelligence/txtai_service.py`:
    - Line 57: `self.fail_fast = str(os.getenv("SIF_FAIL_FAST", "true")).lower() in {"1", "true", "yes", "on"}`
    - Lines 234-235: `index_content` raises RuntimeError if `fail_fast` and not initialized
    - Lines 284-285: `search` raises RuntimeError if `fail_fast` and not initialized
    - Lines 319-320: `get_similarity` raises RuntimeError if `fail_fast` and not initialized
    - `_ensure_initialized` is intentionally non-blocking (starts background thread)
  - `backend/api/today_workflow.py`:
    - `_index_tasks_to_sif` triggers indexing in background after workflow actions
- **Likely files to inspect/edit later**:
  - `backend/services/intelligence/txtai_service.py`
  - `backend/api/today_workflow.py`
  - any other callers that assume initialization is synchronous
- **Confidence**: High
- **Potential downstream impact**:
  - workflow/task indexing silently fails
  - semantic search quality degrades
  - noisy logs obscure higher-priority failures
- **Root-cause questions to answer**:
  - Should `index_content` await `_ensure_initialized_async()` instead of using the non-blocking path?
  - Should callers tolerate deferred indexing instead of fail-fast behavior?
  - Is `SIF_FAIL_FAST=true` appropriate for background indexing operations?
  - Should `SIF_FAIL_FAST` default to `false` for background operations?
- **Validation after fix**:
  - First indexing call after startup succeeds or is gracefully deferred without error spam.

## Issue 4: Today workflow endpoint reload observed during active debugging

- **Status**: Observed
- **Severity**: Low
- **Subsystem**: Development reload / workflow API
- **Log signature**:
  - `StatReload detected changes in 'api\today_workflow.py'. Reloading...`
- **Observed behavior**:
  - Development server reloads due to file edits.
- **RCA**:
  - Expected dev-server behavior, not itself a product bug.
- **Files involved**:
  - `backend/api/today_workflow.py`
- **Confidence**: High
- **Action**:
  - No fix needed; keep separate from actual runtime defects.

## Cross-Issue Notes

- The auth failures and the workflow/indexing issues may be independent.
- The Hugging Face failure may trigger fallback task generation, which can still create workflows while hiding the upstream provider problem.
- txtai indexing failures appear to be a post-generation side effect, not the root cause of generation failure.
- **LiteLLM was investigated and dropped as a false herring** – no project-level SIF/txtai wiring to LiteLLM was found.
- The SIF agent local-model path is **separate** from txtai embeddings and may be the source of the "local model used to work" feedback.

## Candidate Investigation Order

1. Authentication verification mismatch
2. Hugging Face model/provider availability mismatch
3. txtai initialization race (with `SIF_FAIL_FAST` behavior)
4. SIF agent local-model defaults (Qwen 1.5B vs lighter alternatives)
5. Any downstream workflow symptoms after the above are stabilized

## Minimal Fix Paths (Pre-Implementation)

### For Issue 3 (txtai init race):
- **Option A**: Change `SIF_FAIL_FAST` default to `false` for background operations
  - Allows graceful deferral instead of RuntimeError
  - Minimal code change, no logic changes
- **Option B**: Use `_ensure_initialized_async()` in `index_content`/`search`/`get_similarity`
  - Awaits initialization before proceeding
  - More robust but requires async refactoring
- **Option C**: Add initialization state callbacks to callers
  - More complex, may not be necessary

### For Issue 5 (SIF agent local-model drift):
- **Option A**: Change default `model_name` in `SIFBaseAgent.__init__` to lighter model
  - Example: `Qwen/Qwen2.5-0.5B-Instruct` or `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
  - Single-line change, immediate effect
- **Option B**: Add env/config override for default agent local model
  - More flexible, requires config wiring
  - Allows runtime tuning without code changes
- **Option C**: Keep current default and rely on existing fallback chain
  - The fallback chain already tries lighter models if memory fails
  - May be sufficient if memory detection works correctly

## Current Evidence Sources

- Runtime logs from terminal `python` process `22056`
- `backend/middleware/auth_middleware.py`
- `backend/services/llm_providers/huggingface_provider.py`
- `backend/services/intelligence/txtai_service.py`
- `backend/api/today_workflow.py`
- `backend/services/today_workflow_service.py`

## Issue 5: SIF agent local-model drift (distinct from txtai embeddings)

- **Status**: Open
- **Severity**: Medium
- **Subsystem**: SIF agents / local LLM wrappers
- **Error signatures**:
  - (No direct log signature yet; this is a hypothesis from user feedback that "local model used to work")
- **Observed behavior**:
  - User reports that a local model used to work for SIF agents now seems heavier or less responsive.
  - The SIF agent path is **separate** from txtai embeddings.
- **Primary RCA hypothesis**:
  - The SIF agent local LLM wrapper path uses a 1.5B parameter model by default, which may be heavier than the previous local model.
  - This is distinct from txtai embeddings, which still use `sentence-transformers/all-MiniLM-L6-v2`.
- **Evidence in code**:
  - `backend/services/intelligence/sif_agents.py`:
    - Lines 47-51: `LOCAL_LLM_FALLBACKS = ["Qwen/Qwen2.5-1.5B-Instruct", "Qwen/Qwen2.5-0.5B-Instruct", "TinyLlama/TinyLlama-1.1B-Chat-v1.0"]`
    - Lines 53-139: `LocalLLMWrapper` tries models in order, with memory issue detection and automatic fallback to smaller models
    - Line 141: `SIFBaseAgent.__init__` default `model_name="Qwen/Qwen2.5-1.5B-Instruct"`
  - `backend/services/intelligence/txtai_service.py`:
    - Line 48: Still uses `sentence-transformers/all-MiniLM-L6-v2` for embeddings
- **Likely files to inspect/edit later**:
  - `backend/services/intelligence/sif_agents.py`
  - `backend/services/intelligence/agents/specialized/base.py`
  - any config/env that controls default agent local model
- **Confidence**: Medium
- **Root-cause questions to answer**:
  - What was the previous local model default for SIF agents?
  - Is `Qwen/Qwen2.5-1.5B-Instruct` actually too heavy for the user’s laptop?
  - Should the default be changed to `Qwen/Qwen2.5-0.5B-Instruct` or `TinyLlama/TinyLlama-1.1B-Chat-v1.0`?
  - Are there any env/config overrides that could make this configurable?
- **Validation after fix**:
  - SIF agents use a CPU-friendly local model (e.g., smaller Qwen variant or TinyLlama).
  - Agent generation completes without excessive CPU/memory pressure.

## Issue 6: Model initialization blocking and module unification

- **Status**: Open
- **Severity**: High
- **Subsystem**: Startup / model loading / module architecture
- **Error signatures**:
  - (No direct log signature; architectural issue)
- **Observed behavior**:
  - `start_alwrity_backend.py` pre-downloads `Qwen/Qwen2.5-3B-Instruct` **synchronously** before server starts (line 122).
  - `sif_agents.py` defaults to `Qwen/Qwen2.5-1.5B-Instruct` and uses lazy loading via `LocalLLMWrapper`.
  - `txtai_service.py` uses `sentence-transformers/all-MiniLM-L6-v2` for embeddings.
  - Three separate modules handle model loading, creating confusion.
  - User wants fail-fast semantics (catch bugs, avoid silent failures) AND proper fallback.
  - User wants non-blocking model downloads for SIF/agents.
- **Primary RCA hypothesis**:
  - Startup script blocks on model download, contradicting non-blocking requirement.
  - Model size mismatch: startup downloads 3B, agents default to 1.5B.
  - Fail-fast in `txtai_service.py` prevents fallback from working.
  - Module separation (`txtai_service.py`, `sif_agents.py`, `start_alwrity_backend.py`) creates confusion.
- **Evidence in code**:
  - `start_alwrity_backend.py`:
    - Line 122: `target_model = "Qwen/Qwen2.5-3B-Instruct"`
    - Lines 127-131: `snapshot_download()` is **blocking** call
    - Lines 117-120: Skips on Render/Railway but **not** on local dev
  - `sif_agents.py`:
    - Line 48: `LOCAL_LLM_FALLBACKS = ["Qwen/Qwen2.5-1.5B-Instruct", "Qwen/Qwen2.5-0.5B-Instruct", "TinyLlama/TinyLlama-1.1B-Chat-v1.0"]`
    - Line 141: Default `model_name="Qwen/Qwen2.5-1.5B-Instruct"`
    - Line 150: Uses `LocalLLMWrapper` for lazy loading
    - Lines 94-130: Has fallback logic with memory issue detection
  - `txtai_service.py`:
    - Line 57: `SIF_FAIL_FAST=true` (default) causes RuntimeError
    - Lines 234-235, 284-285, 319-320: Fail-fast prevents fallback
- **Likely files to inspect/edit later**:
  - `start_alwrity_backend.py` (remove blocking download)
  - `services/intelligence/sif_agents.py` (unify model defaults)
  - `services/intelligence/txtai_service.py` (fix fail-fast with fallback)
  - Create unified `services/intelligence/model_registry.py` or similar
- **Confidence**: High
- **Root-cause questions to answer**:
  - Should model download be truly non-blocking (background thread)?
  - Should fail-fast be conditional (e.g., only for critical paths, not background ops)?
  - Should module unification create a single `ModelRegistry` or `ModelManager`?
  - How to ensure JSON/response structure compatibility across fallback chain?
- **Validation after fix**:
  - Server starts without blocking on model download.
  - SIF agents use consistent model defaults.
  - Fail-fast catches bugs but allows fallback for non-critical ops.
  - Single module handles all model loading logic.

## Minimal Fix Paths (Pre-Implementation)

### For Issue 3 (txtai init race) - REVISED:
- **Option A**: Change `SIF_FAIL_FAST` to be **conditional** (not global)
  - Keep fail-fast for critical paths (user-initiated ops)
  - Allow graceful deferral for background ops (indexing, clustering)
  - Requires distinguishing operation types
- **Option B**: Use `_ensure_initialized_async()` for **blocking ops only**
  - Keep non-blocking for background ops
  - Awaits init for user-facing ops
  - More robust but requires async refactoring
- **Option C**: Add operation-type-aware fail-fast
  - Pass `critical=True/False` to operations
  - Fail-fast only when `critical=True`
  - Most aligned with user requirements

### For Issue 5 (SIF agent local-model drift) - REVISED:
- **Option A**: Change default to lighter model AND improve fallback chain
  - Default: `Qwen/Qwen2.5-0.5B-Instruct` (lighter)
  - Fallback: `0.5B → TinyLlama 1.1B`
  - Ensure JSON/response structure compatibility
- **Option B**: Add env/config override + keep fallback chain
  - `SIF_AGENT_MODEL` env var
  - Fallback chain remains as-is
  - More flexible
- **Option C**: Keep current default and rely on existing fallback chain
  - **RECOMMENDED**: Already has memory detection and fallback
  - Just need to ensure JSON compatibility

### For Issue 6 (Model blocking + module unification):
- **Option A**: Remove blocking download from startup script
  - Delete `bootstrap_local_llm_models()` call
  - Let `LocalLLMWrapper` handle lazy loading
  - Minimal change, immediate non-blocking
- **Option B**: Make download non-blocking (background thread)
  - Keep pre-download but in background
  - Server starts immediately
  - More complex
- **Option C**: Create unified `ModelRegistry` module
  - Single source of truth for model defaults
  - Centralized download/cache logic
  - Eliminates confusion between modules
  - **RECOMMENDED for long-term**

## Session Update Log

### 2026-03-10

- Created initial RCA tracker document.
- Seeded first three concrete issues from supplied logs.
- No fixes applied from this document yet.
- Added Issue 5: SIF agent local-model drift (LiteLLM dropped as false herring).
- Refined Issue 3 with `SIF_FAIL_FAST` behavior details.
- Added minimal fix paths for Issues 3 and 5.
- Added Issue 6: Model initialization blocking and module unification.
- Updated minimal fix paths based on user requirements (fail-fast + fallback, non-blocking, unification).
