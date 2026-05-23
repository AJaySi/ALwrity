# Podcast Maker API Reference

This reference summarizes key endpoint groups exposed by the Podcast API domain.

## Endpoint Map

```mermaid
flowchart TD
    A[/api/podcast]
    A --> P[projects.py]
    A --> AN[analysis.py]
    A --> R[research.py]
    A --> S[script.py]
    A --> AU[audio.py]
    A --> V[video.py]
    A --> I[images.py]
    A --> AV[avatar.py]
    A --> D[dubbing.py]

    P --> P1[Create project]
    P --> P2[List project history]
    AN --> AN1[Run episode analysis]
    R --> R1[Generate/select queries]
    S --> S1[Create/update script]
    AU --> AU1[Render audio]
    V --> V1[Render video]
    I --> I1[Generate supporting images]
    AV --> AV1[Configure presenter avatar]
    D --> D1[Voice dubbing / localization]
```

## Endpoint Families

- **Project endpoints**: lifecycle operations for episode containers and history.
- **Analysis endpoints**: diagnostic scoring and recommendation extraction.
- **Research & script endpoints**: query planning, source grounding, and script management.
- **Media endpoints**: audio/video render, image generation, avatar personalization, and dubbing.
