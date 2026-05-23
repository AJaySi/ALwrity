# Podcast Maker Implementation Overview

Podcast Maker orchestrates a multi-stage content pipeline: project configuration, research grounding, script composition, media rendering, and publish-state tracking.

## Architecture & Data Flow

```mermaid
flowchart LR
    UI[Podcast Maker UI]
    API[Podcast API Router]
    PROJ[Project Service]
    RESEARCH[Research Handler]
    SCRIPT[Script Handler]
    RENDER[Audio/Video Render Handlers]
    STORE[(Podcast Tables)]
    JOBS[(Render Queue)]

    UI --> API
    API --> PROJ
    API --> RESEARCH
    API --> SCRIPT
    API --> RENDER

    PROJ --> STORE
    RESEARCH --> STORE
    SCRIPT --> STORE
    RENDER --> JOBS
    RENDER --> STORE

    JOBS --> UI
    STORE --> UI
```

## Component Responsibilities

- **UI layer**: captures project metadata, persona settings, and script/editor actions.
- **API router**: central endpoint registration and request dispatch.
- **Research and script handlers**: generate, validate, and persist episode knowledge and narration assets.
- **Render handlers**: combine narration, visuals, and scene timing into draft/final media outputs.
- **Storage + queue**: maintain immutable version history and asynchronous job state.
