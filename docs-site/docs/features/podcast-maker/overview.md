# Podcast Maker Overview

Podcast Maker helps you turn a topic idea into a polished episode draft with research, script generation, AI voice narration, and optional video scenes.

## What you do in the product

1. **Start with an idea** and episode settings (duration, speakers, style).
2. **Review AI analysis** suggestions (audience fit, outline ideas, titles, takeaways).
3. **Run research** from selected queries and use source-backed fact cards.
4. **Generate and edit a script** scene-by-scene.
5. **Generate voice audio** for each scene and combine clips into one episode file.
6. **Optionally create scene images and talking-head videos**.
7. **Save and revisit projects** from your episode/project list.

## What you see in the UI

- Suggested outlines, titles, and hooks after analysis.
- A query approval step before research runs.
- Fact cards and summarized research insights.
- Scene-based script editor with approval actions.
- Audio generation controls (voice, emotion, speed, format-related options).
- Video task progress and completed video listing.
- Project persistence (save/load/list/favorite/delete).

## Feature status matrix (based on current code)

| Capability | Status | Notes |
|---|---|---|
| Idea enhancement + analysis suggestions | **Implemented** | Frontend calls `/api/podcast/idea/enhance` and `/api/podcast/analyze`; backend handlers exist. |
| Research with Exa flow | **Implemented** | Frontend uses `/api/podcast/research/exa`; backend Exa research route is present. |
| Script generation + scene approval | **Implemented** | Frontend uses `/api/podcast/script` and `/api/podcast/script/approve`; backend handlers exist. |
| Scene audio generation + combine audio | **Implemented** | Frontend uses `/api/podcast/audio` and `/api/podcast/combine-audio`; backend handlers exist. |
| Scene image generation | **Implemented** | Frontend uses `/api/podcast/image`; backend image handler exists. |
| Scene video generation + status polling + combine videos | **Implemented** | Frontend uses `/api/podcast/render/video`, `/api/podcast/task/{id}/status`, `/api/podcast/render/combine-videos`; backend video routes are present. |
| Project CRUD + favorites | **Implemented** | Frontend calls `/api/podcast/projects*`; backend create/get/update/list/delete/favorite routes exist. |
| Avatar upload/generate/make-presentable | **Implemented** | Frontend calls `/api/podcast/avatar/*`; backend routes exist. |
| Audio dubbing + voice clone routes | **Partial** | Backend dubbing routes exist; not wired in `podcastApi.ts` yet. |
| Task cancellation from Podcast Maker UI | **Partial** | Frontend has `cancelTask()` placeholder using `/api/story/task/.../cancel`, not a dedicated podcast cancel API path. |
| Multi-provider research toggle in podcast service | **Planned/Not active in current frontend** | Podcast frontend currently targets Exa route directly instead of a user-facing provider switch in this API layer. |

## Advanced / developer notes

Most users can ignore this section.

- Podcast Maker uses preflight checks before expensive operations (analysis/script/audio/research) to surface plan/credit issues early.
- The frontend normalizes snake_case API responses into camelCase for UI components where needed.
- Long-running video operations are task-based and polled from the client.

## Engineering references

These are internal planning/reference docs retained as source material:

- `docs/Podcast_maker/AI_PODCAST_BACKEND_REFERENCE.md`
- `docs/Podcast_maker/AI_PODCAST_ENHANCEMENTS.md`
- `docs/Podcast_maker/PODCAST_API_CALL_ANALYSIS.md`
- `docs/Podcast_maker/PODCAST_PERSISTENCE_IMPLEMENTATION.md`
- `docs/Podcast_maker/PODCAST_PLAN_COMPLETION_STATUS.md`
