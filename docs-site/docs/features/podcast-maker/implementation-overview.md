# Podcast Maker Implementation Overview

This page keeps implementation details in one place for engineering and advanced troubleshooting.

## Architecture

Podcast Maker is split into:

- **Frontend orchestration service**: `frontend/src/services/podcastApi.ts`
  - Coordinates step flow (analysis → research → script → audio/video)
  - Runs preflight checks before expensive calls
  - Maps API payloads into UI-friendly objects
- **Backend podcast handlers**: `backend/api/podcast/handlers/*.py`
  - Route-level APIs for analysis, research, script, media, and projects
  - Authenticated operations with user-scoped media/project data

## Frontend orchestration responsibilities

Primary responsibilities in `podcastApi.ts`:

- Create project analysis payloads and map response into Podcast Analysis UI data.
- Build/validate research query payloads for Exa research route.
- Generate script scenes and normalize scene/line structure for editor state.
- Render per-scene audio and combine scenes into final audio.
- Trigger scene image and video generation workflows.
- Persist project state via project CRUD endpoints.

## Backend handler modules

- `analysis.py`: idea enhancement, analysis, regenerate-queries.
- `research.py`: Exa research endpoint.
- `script.py`: script generation and scene approval.
- `audio.py`: audio upload, generation, combine, serving audio files.
- `images.py`: scene image generation and image serving.
- `video.py`: scene video generation, video listing/serving, combine videos.
- `avatar.py`: avatar upload, avatar generation, avatar cleanup/presentability.
- `projects.py`: create, get, update, list, delete, favorite project records.
- `dubbing.py`: dubbing/voice clone lifecycle endpoints (currently backend-available).

## Data models (functional view)

At feature level, the flow revolves around:

- **Project metadata**: `project_id`, idea, duration, speakers, budget and status fields.
- **Analysis output**: audience, content type, keywords, outlines, title suggestions.
- **Research output**: source list, summarized insights, fact cards for script grounding.
- **Script output**: scenes with IDs, durations, emotions, and speaker lines.
- **Media output**: audio files, scene images, scene videos, combined episode artifacts.

## Operational notes

- Preflight checks are used to fail fast on plan/credit constraints.
- Some operations are synchronous (analysis/script/audio/image), while video is async task-based.
- Client-side task polling is used for long-running jobs.

## Engineering references

- `docs/Podcast_maker/AI_PODCAST_BACKEND_REFERENCE.md`
- `docs/Podcast_maker/PODCAST_API_CALL_ANALYSIS.md`
- `docs/Podcast_maker/PODCAST_PLAN_COMPLETION_STATUS.md`
