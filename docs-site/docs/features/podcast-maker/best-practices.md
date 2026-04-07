# Podcast Maker Best Practices

This guide is implementation-aware: every recommendation below is based on how the current Podcast Maker APIs actually behave in frontend and backend code.

## 1) Start with budget-safe defaults (preflight-first workflow)

Podcast Maker runs **preflight validation** before major steps (analysis, research, script generation, TTS preview, and full TTS render). Use that as your workflow guardrail:

1. Analyze idea first
2. Approve a small set of research queries
3. Generate script
4. Preview voice on short excerpts
5. Render full scene audio
6. Generate scene videos
7. Combine final assets

Why this matters:
- If credits/limits are insufficient, preflight fails fast before expensive operations.
- Video generation also runs server-side animation validation and returns subscription-friendly errors for insufficient credits.

## 2) Duration vs. scene-count tradeoffs (cost + reliability)

The stack defaults to a **45s scene target** and cost estimate logic effectively scales scene count as:

- `scene_count ≈ ceil(duration_minutes * 60 / scene_length_target_seconds)`

Practical recommendations:
- **5–8 min episodes**: target 5–8 scenes.
- **10–15 min episodes**: target 8–14 scenes.
- Increase `scene_length_target` when you need fewer API calls and faster completion.
- Keep script concise because per-scene TTS has a **10,000-character max** (long text gets truncated by frontend before render).

Rule of thumb:
- More scenes = better pacing granularity but more TTS/video calls.
- Fewer scenes = cheaper/faster pipeline, but each scene must carry more narrative weight.

## 3) Voice strategy: preview first, render second

Use a two-pass voice workflow:

### Pass A: Preview and lock voice profile
Use preview on short, representative lines (intro, data-heavy line, CTA) to validate:
- voice identity
- speed
- emotion
- pronunciation behavior (especially numbers/statistics)

### Pass B: Full scene render with tuned knobs
When rendering scene audio, adjust only the knobs that matter:
- `voice_id` (or `custom_voice_id` for cloned voice)
- `speed` (default 1.0 is usually safest for timing)
- `emotion` (scene-level emotion is supported)
- `english_normalization` (keep enabled for number-heavy scripts)
- audio format controls (`sample_rate`, `bitrate`, `channel`, `format`, `language_boost`) only when distribution requires them

Also note:
- The frontend injects pause markers and strips markdown before TTS for better natural rhythm.
- Use short lines (2–4 per scene is a good operational target from script generation guidance).

## 4) Research quality: when to use Exa config options

Use Exa config knobs intentionally, not by default.

### Search type
- `auto`: default for most projects.
- `keyword`: use when topic vocabulary is stable/specific.
- `neural`: use when you need semantic discovery across mixed phrasing.

### Domain filters
Use either include or exclude domains (not both).
- Prefer `exa_include_domains` for compliance/brand-safe sourcing.
- Use `exa_exclude_domains` to remove noisy/untrusted sources.

If both are sent, the backend/frontend sanitize behavior will prefer include-domain intent and drop the conflicting side.

### `max_sources`, category, and freshness
- Increase `max_sources` only when synthesis quality is poor at default depth.
- Use `date_range` (e.g. last month/quarter/year) for trend-sensitive topics.
- Turn on statistics-oriented options when the episode needs hard numbers.

### Query operations
- Always approve only the strongest queries before running research.
- Empty query sets are rejected server-side.

## 5) Avatar + image prompt strategy for visual consistency

Consistency is strongest when you anchor scene images to a persistent base avatar.

Recommended approach:
1. Create/upload a presenter avatar once per project.
2. Reuse that avatar as `base_avatar_url` for scene images.
3. Keep one shared style nucleus across prompts (lighting, environment, host look, framing).
4. Change only scene-specific context (topic, emotion, supporting visual motif).

Important implementation notes:
- If `base_avatar_url` is provided, image generation uses character-consistency flow; if the base avatar cannot be loaded, image generation fails (no silent fallback).
- Keep scene emotion aligned to visual lighting cues for continuity.
- For presenter generation, keep speakers realistic (supported range is 1–2).

## 6) Script and scene structure that survives production

Generate script with full context:
- analysis (audience/type/keywords)
- selected outline
- research payload
- bible/persona context

Then enforce editorial constraints before render:
- Remove filler and repeated lines.
- Ensure each scene has a single narrative job.
- Keep line lengths short enough for natural TTS breathing.
- Verify emotion tag is valid (`neutral`, `happy`, `excited`, `serious`, `curious`, `confident`) to avoid fallback normalization.

## 7) Project save/resume + asset-library workflows

Treat a podcast as a resumable production artifact.

### Save/resume
- Persist state to project APIs throughout the workflow (analysis, research, script, render jobs, knobs, final video URL).
- Use project list filtering/sorting to resume active work quickly.
- Handle duplicate-idea conflicts by reopening existing project IDs instead of cloning work.

### Asset library workflow
- Save generated and uploaded assets (audio/avatar/images) into the content asset library with project metadata.
- Use consistent tags (`podcast`, project id, scene id) so assets are searchable and reusable.
- Reuse previously approved host avatars and voice samples across episodes to reduce generation churn.

## 8) Video and dubbing execution strategy

### Video
- Only pass supported video resolution (`480p` or `720p`).
- Poll task status (video generation is asynchronous and can take up to ~10 minutes).
- Use mask image only when you need controlled motion region.
- Generate all scene videos before starting combine to avoid failed final assembly.

### Dubbing
- Use `quality=low` for fast/cheap exploration.
- Use `quality=high` + `use_voice_clone=true` when voice identity matters.
- Keep `speed` in 0.5–2.0 and voice clone accuracy in 0.1–1.0.
- For voice cloning, feed a clean 10–60s sample for best identity retention.

---

## Common failure modes and fixes

For broader platform issues, see the main [Troubleshooting Guide](../../guides/troubleshooting.md).

| Failure mode | Why it happens | Fix |
|---|---|---|
| Preflight blocked (analysis/research/script/TTS/video) | Insufficient credits or operation limits | Run lighter settings first: fewer scenes, lower duration, fewer research queries; then retry. |
| Research request rejected | No approved queries selected | Approve at least one non-empty query before running Exa research. |
| Research config mismatch | Include + exclude domains both supplied | Use only one domain filter type per run. |
| Scene audio cuts off | Scene text exceeded TTS max characters | Reduce scene length/lines; split long scene into two scenes. |
| Avatar-consistent image generation fails | `base_avatar_url` is broken/inaccessible | Re-upload avatar or switch to a valid project image URL; retry scene generation. |
| Video task fails quickly | Invalid media URL, unsupported resolution, missing assets | Verify audio/image URLs are valid and use only `480p`/`720p`. |
| Final combine video fails | One or more scene video files missing/invalid | Confirm every scene has a completed video task before combine. |
| Dubbing quality sounds robotic | Low quality mode or weak source audio | Switch to high quality and/or use voice cloning with a cleaner sample. |
| Voice clone results are unstable | Poor sample or extreme accuracy/speed settings | Use clean 10–60s sample; keep accuracy near default and speed near 1.0. |
| Save appears inconsistent across sessions | Save failed and only partial local fallback exists | Trigger explicit save after each major step and verify project reload from API. |
