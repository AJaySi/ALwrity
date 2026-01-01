# AI Podcast Backend Reference

Curated overview of the backend surfaces that the AI Podcast Maker
should call. Covers service clients, research providers, subscription
controls, and FastAPI routes relevant to analysis, research, scripting,
and rendering.

---

## WaveSpeed & Audio Infrastructure

- `backend/services/wavespeed/client.py`
  - `WaveSpeedClient.submit_image_to_video(model_path, payload)` –
    submit WAN 2.5 / InfiniteTalk jobs and receive prediction IDs.
  - `WaveSpeedClient.get_prediction_result(prediction_id)` /
    `poll_until_complete(...)` – shared polling helpers for render jobs.
  - `WaveSpeedClient.generate_image(...)` – synchronous Ideogram V3 /
    Qwen image bytes (mirrors Image Studio usage).
  - `WaveSpeedClient.generate_speech(...)` – Minimax Speech 02 HD via
    WaveSpeed; accepts `voice_id`, `speed`, `sample_rate`, etc. Returns
    raw audio bytes (sync) or prediction IDs (async).
  - `WaveSpeedClient.optimize_prompt(...)` – prompt optimizer that can
    improve image/video prompts before rendering.

- `backend/services/wavespeed/infinitetalk.py`
  - `animate_scene_with_voiceover(...)` – wraps InfiniteTalk (image +
    narration to talking video). Enforces payload limits, pulls the
    final MP4, and reports cost/duration metadata.

- `backend/services/llm_providers/main_audio_generation.py`
  - `generate_audio(...)` – subscription-aware TTS orchestration built
    on `WaveSpeedClient.generate_speech`. Applies PricingService checks,
    records UsageSummary/APIUsageLog entries, and returns provider/model
    metadata for frontends.

---

## Research Providers & Adapters

- `backend/services/blog_writer/research/research_service.py`
  - Central orchestrator for grounded research. Supports Google Search
    grounding (Gemini) and Exa neural search via configurable provider.
  - Calls `validate_research_operations` / `validate_exa_research_operations`
    before touching external APIs and logs usage through PricingService.
  - Returns fact cards (`ResearchSource`, `GroundingMetadata`) already
    normalized for downstream mapping.

- `backend/services/blog_writer/research/exa_provider.py`
  - `ExaResearchProvider.search(...)` – Executes Exa queries, converts
    results into `ResearchSource` objects, estimates cost, and tracks it.
  - Provides helpers for excerpt extraction, aggregation, and usage
    tracking (`track_exa_usage`).

- `backend/services/llm_providers/gemini_grounded_provider.py`
  - Implements Gemini + Google Grounding calls with support for cached
    metadata, chunk/support parsing, and debugging hooks used by Story
    Writer and LinkedIn flows.

- `backend/api/research_config.py`
  - Exposes feature flags such as `exa_available`, suggested categories,
  - and other metadata needed by the frontend to decide provider options.

---

## Subscription & Pre-flight Validation

- `backend/services/subscription/preflight_validator.py`
  - `validate_research_operations(pricing_service, user_id, gpt_provider)`
    – Blocks research runs if Gemini/HF token budgets would be exceeded
    (covers Google Grounding + analyzer passes).
  - `validate_exa_research_operations(...)` – Same for Exa workflows;
    validates Exa call count plus follow-up LLM usage.
  - `validate_image_generation_operations(...)`,
    `validate_image_upscale_operations(...)`,
    `validate_image_editing_operations(...)` – templates for validating
    other expensive steps (useful for render queue and avatar creation).

- `backend/services/subscription/pricing_service.py`
  - Provides `check_usage_limits`, `check_comprehensive_limits`, and
    plan metadata (limits per provider) used across validators.

Frontends must call these validators (via thin API wrappers) before
initiating script generation, research, or rendering to surface tier
errors without wasting API calls.

---

## REST Routes to Reuse

### Story Writer (`backend/api/story_writer/router.py`)

- `POST /api/story/generate-setup` – Generate initial story setups from
  an idea (`story_setup.py::generate_story_setup`).
- `POST /api/story/generate-outline` – Structured outline generation via
  Gemini with persona/settings context.
- `POST /api/story/generate-images` – Batch scene image creation backed
  by WaveSpeed (WAN 2.5 / Ideogram). Returns per-scene URLs + metadata.
- `POST /api/story/generate-ai-audio` – Minimax Speech 02 HD render for
  a single scene with knob controls (voice, speed, pitch, emotion).
- `POST /api/story/optimize-prompt` – WaveSpeed prompt optimization API
  for cleaning up image/video prompts before rendering.
- `POST /api/story/generate-audio` – Legacy multi-scene TTS (gTTS) if a
  lower-cost fallback is needed.
- `GET /api/story/images/{filename}` & `/audio/{filename}` – Authenticated
  asset delivery for generated media.

These endpoints already enforce auth, asset tracking, and subscription
limits; the podcast UI should simply adopt their payloads.

### Blog Writer (`backend/api/blog_writer/router.py`)

- `POST /api/blog/research` (inside router earlier in file) – Executes
  grounded research via Google or Exa depending on `provider`.
- `POST /api/blog/flow-analysis/basic|advanced` – Example of long-running
  job orchestration with task IDs (pattern for script/performance analysis).
- `POST /api/blog/seo/analyze` & `/seo/metadata` – Illustrate how to pass
  authenticated user IDs into PricingService checks, useful for podcast
  metadata generation.
- Cache endpoints (`GET/DELETE /api/blog/cache/*`) – Provide research
  cache stats/clear operations that podcast flows can reuse.

### Image Studio (`backend/api/images.py`)

- `POST /api/images/generate` – Subscription-aware image creation with
  asset tracking (pattern for cost estimates + upload paths).
- `GET /api/images/image-studio/images/{file}` – Serves generated images;
  demonstrates query-token auth used by `<img>` tags.

Reuse these routes for avatar defaults or background art inside the
podcast builder instead of writing bespoke services.

---

## Key Data Flow Hooks

- Research job polling: `backend/api/story_writer/routes/story_tasks.py`
  plus `task_manager.py` define consistent job IDs and status payloads.
- Media job polling: `StoryImageGenerationService` and `StoryAudioGenerationService`
  already drop artifacts into disk/CDN with tracked filenames; the
  podcast render queue can subscribe to those patterns.
- Persona assets: onboarding routes in `backend/api/onboarding_endpoints.py`
  expose upload endpoints for voice/avatars; pass resulting asset IDs to
  the podcast APIs instead of raw files.

Use this reference to swap out the mock podcast helpers with production
APIs while staying inside existing authentication, subscription, and
asset storage conventions.

