# Podcast Maker API Reference

Base prefix: `/api/podcast`

This page summarizes the Podcast Maker endpoints currently represented in frontend and backend code.

## Endpoints by workflow stage

### Analysis and idea shaping

- `POST /idea/enhance`
- `POST /analyze`
- `POST /regenerate-queries`

### Research

- `POST /research/exa`

### Scripting

- `POST /script`
- `POST /script/approve`

### Audio

- `POST /audio/upload`
- `POST /audio`
- `POST /combine-audio`
- `GET /audio/{filename}`

### Images

- `POST /image`
- `GET /images/{path}`

### Video

- `POST /render/video`
- `POST /render/combine-videos`
- `GET /videos`
- `GET /videos/{filename}`
- `GET /final-videos/{filename}`

### Avatars

- `POST /avatar/upload`
- `POST /avatar/make-presentable`
- `POST /avatar/generate`

### Projects

- `POST /projects`
- `GET /projects`
- `GET /projects/{project_id}`
- `PUT /projects/{project_id}`
- `DELETE /projects/{project_id}`
- `POST /projects/{project_id}/favorite`

### Dubbing (backend available)

- `POST /dub/audio`
- `GET /dub/{task_id}/result`
- `GET /dub/audio/{filename}`
- `POST /dub/estimate`
- `GET /dub/languages`
- `GET /dub/voices`
- `POST /dub/voices/clone`
- `GET /dub/voices/{task_id}/result`
- `GET /dub/voices/audio/{filename}`

## Implementation details

### Endpoint usage in frontend service

The current `podcastApi.ts` directly calls these podcast routes for analysis, research, script, audio, image, video, avatar, and project workflows.

Known gap:

- `cancelTask()` is a placeholder that posts to `/api/story/task/{taskId}/cancel` rather than a dedicated podcast route.

### Request/response model notes

At a high level:

- Script endpoints exchange `idea`, `duration_minutes`, `speakers`, and optional `research`/`analysis`/`bible` context.
- Audio endpoints exchange scene identifiers, text, and voice/rendering options.
- Video endpoints exchange scene identifiers plus `audio_url` and optional image/prompt context.
- Project endpoints exchange project-level state payloads suitable for restoring workflow progress.

## Engineering references

- `docs/Podcast_maker/AI_PODCAST_BACKEND_REFERENCE.md`
- `docs/Podcast_maker/PODCAST_PERSISTENCE_IMPLEMENTATION.md`
