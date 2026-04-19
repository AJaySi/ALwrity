# Programmatic B-Roll Composer

A layered video composition pipeline that assembles AI-generated images, programmatic data charts, Pillow text overlays, and circular-masked avatar videos into a single output MP4. Driven by structured JSON from an LLM, exposed via a FastAPI server.

---

## Table of Contents

1. [Architecture overview](#1-architecture-overview)
2. [File structure](#2-file-structure)
3. [Installation](#3-installation)
4. [Core concepts](#4-core-concepts)
   - 4.1 [The Insight dataclass](#41-the-insight-dataclass)
   - 4.2 [The SceneAssets dataclass](#42-the-sceneassets-dataclass)
   - 4.3 [The layer stack](#43-the-layer-stack)
   - 4.4 [The JSON bridge](#44-the-json-bridge)
5. [Asset generators](#5-asset-generators)
   - 5.1 [Bar chart — make_bar_chart](#51-bar-chart--make_bar_chart)
   - 5.2 [Line trend — make_line_trend](#52-line-trend--make_line_trend)
   - 5.3 [Bullet overlay — make_bullet_overlay](#53-bullet-overlay--make_bullet_overlay)
   - 5.4 [Insight card — make_insight_card](#54-insight-card--make_insight_card)
6. [Video effects](#6-video-effects)
   - 6.1 [Circular avatar mask — apply_circle_mask](#61-circular-avatar-mask--apply_circle_mask)
   - 6.2 [Ken Burns zoom — ken_burns](#62-ken-burns-zoom--ken_burns)
7. [Scene builders](#7-scene-builders)
   - 7.1 [Data scene — build_data_scene](#71-data-scene--build_data_scene)
   - 7.2 [Bullet scene — build_bullet_scene](#72-bullet-scene--build_bullet_scene)
   - 7.3 [Full avatar scene — build_full_avatar_scene](#73-full-avatar-scene--build_full_avatar_scene)
8. [Scene dispatcher — dispatch_scene](#8-scene-dispatcher--dispatch_scene)
9. [Crossfade transitions](#9-crossfade-transitions)
   - 9.1 [How crossfade_concat works](#91-how-crossfade_concat-works)
   - 9.2 [The set_duration gotcha](#92-the-set_duration-gotcha)
10. [Master compositor — compose_video](#10-master-compositor--compose_video)
11. [FastAPI server](#11-fastapi-server)
    - 11.1 [Request models](#111-request-models)
    - 11.2 [Job lifecycle](#112-job-lifecycle)
    - 11.3 [API endpoints](#113-api-endpoints)
12. [Running the project](#12-running-the-project)
    - 12.1 [Smoke test (no media files needed)](#121-smoke-test-no-media-files-needed)
    - 12.2 [Full video composition](#122-full-video-composition)
    - 12.3 [API server](#123-api-server)
13. [Calling the API](#13-calling-the-api)
14. [Production notes](#14-production-notes)
15. [Extending the pipeline](#15-extending-the-pipeline)

---

## 1. Architecture overview

The pipeline follows a **Layered Composition** model. Rather than generating video in one pass, it assembles independent visual layers — each produced by the cheapest appropriate tool — into a single timeline using MoviePy as the compositor.

```
LLM JSON output
      │
      ▼
 dispatch_scene()          ← routes visual_cue → builder function
      │
      ├─ build_data_scene()
      │     ├─ ImageClip (background)    ← AI-generated image
      │     ├─ ImageClip (chart PNG)     ← Matplotlib, transparent bg
      │     ├─ ImageClip (insight card)  ← Pillow RGBA
      │     └─ VideoFileClip (avatar)    ← circular numpy mask
      │
      ├─ build_bullet_scene()
      │     ├─ ImageClip (background)
      │     ├─ ImageClip (bullet overlay) ← Pillow RGBA
      │     └─ VideoFileClip (avatar)
      │
      └─ build_full_avatar_scene()
            └─ VideoFileClip (full-screen)
                   │
                   ▼
            crossfade_concat()           ← dissolve between scenes
                   │
                   ▼
            write_videofile()            ← H.264 MP4 via ffmpeg
```

The key design decision: charts and text are **never** rendered by a generative model. Matplotlib produces pixel-perfect data graphics from real numbers; Pillow renders crisp, deterministic text. Only the background and the talking-head avatar come from AI generation, minimising both cost and hallucination risk.

---

## 2. File structure

```
.
├── broll_composer.py   # Core library — all composition logic
├── api_server.py       # FastAPI wrapper — HTTP interface to the pipeline
└── requirements.txt    # Python dependencies
```

`broll_composer.py` has no FastAPI dependency and can be imported and called directly from scripts, notebooks, or other web frameworks.

---

## 3. Installation

```bash
# System dependency — must be on PATH
apt-get install ffmpeg

# Python packages
pip install -r requirements.txt
```

**requirements.txt**

```
moviepy==1.0.3
Pillow>=10.0
matplotlib>=3.8
numpy>=1.26
fastapi>=0.111
uvicorn[standard]>=0.29
python-multipart>=0.0.9
```

MoviePy 1.0.3 is pinned because 2.x introduced breaking API changes to `CompositeVideoClip` and the effects interface. The rest can float within the specified lower bounds.

---

## 4. Core concepts

### 4.1 The Insight dataclass

Every scene is driven by a single `Insight` object. This is the contract between the LLM and the composition pipeline:

```python
@dataclass
class Insight:
    key_insight: str      # Headline text rendered on the insight card
    supporting_stat: str  # Sub-headline rendered below the headline
    visual_cue: str       # Selects which scene builder to use (see §8)
    audio_tone: str       # Passed through for downstream TTS / audio selection
    chart_data: dict      # Data payload consumed by chart generators (see §5)
    duration: float       # Scene length in seconds, default 10.0
```

The `audio_tone` field is not used by the video pipeline itself — it is metadata for whatever system generates or selects the voiceover audio track for the scene.

### 4.2 The SceneAssets dataclass

`SceneAssets` carries file paths to the media assets for a given scene:

```python
@dataclass
class SceneAssets:
    background_img: str           # Required — path to JPEG or PNG background
    chart_img: Optional[str]      # Populated by dispatch_scene after chart generation
    avatar_video: Optional[str]   # Optional — path to MP4 avatar clip
    bullet_img: Optional[str]     # Reserved for pre-rendered bullet overlays
```

`chart_img` starts as `None` and is written to by `dispatch_scene` after it generates the Matplotlib PNG, so the scene builders receive a fully-populated `SceneAssets` by the time they run.

### 4.3 The layer stack

Every scene is a `CompositeVideoClip` — a MoviePy object that renders multiple clips on a shared canvas by alpha-compositing them bottom-to-top. The layer order is consistent across all scene types:

| Z-order | Layer | Source | Notes |
|---------|-------|--------|-------|
| 0 (bottom) | Background | AI image + Ken Burns | Darkened to make overlays legible |
| 1 | Chart or bullet overlay | Matplotlib or Pillow PNG | Transparent background; fades in |
| 2 | Insight card | Pillow RGBA | Positioned at y=820 (near bottom) |
| 3 (top) | Avatar circle | MP4 + numpy mask | Bottom-right corner |

### 4.4 The JSON bridge

The LLM is prompted to return a structured JSON object — not prose — so the pipeline can consume it without parsing ambiguity:

```json
{
  "key_insight": "AI tools reduced content cycles by 40%",
  "supporting_stat": "HubSpot 2026 report — 12% lift in CTR",
  "visual_cue": "bar_chart_comparison",
  "audio_tone": "authoritative_and_surprising",
  "duration": 10.0,
  "chart_data": {
    "labels": ["Content Velocity", "CTR", "Engagement", "Cost/Lead"],
    "before": [30, 22, 18, 60],
    "after":  [72, 34, 41, 38]
  }
}
```

`pipeline_from_json()` is the single-call entry point that accepts this JSON string, constructs the dataclasses, runs `dispatch_scene`, and writes the output MP4.

---

## 5. Asset generators

These functions produce static image files (PNG with alpha transparency) that are loaded as `ImageClip` objects in the scene builders. They are completely independent of MoviePy and can be called and previewed without assembling any video.

### 5.1 Bar chart — `make_bar_chart`

```python
make_bar_chart(data: dict, out_path: str, title: str = "") -> str
```

Produces a side-by-side "before vs after" bar chart using Matplotlib. The critical detail is the renderer configuration and save parameters:

```python
matplotlib.use("Agg")          # Non-interactive backend — no display required
fig, ax = plt.subplots(figsize=(8, 4.5), facecolor="none")
ax.set_facecolor("none")       # Transparent axes background
fig.savefig(out_path, dpi=150, transparent=True, bbox_inches="tight")
```

Setting both `facecolor="none"` on the figure and `transparent=True` on `savefig` is necessary because they control different things: the figure background and the PNG alpha channel respectively. Without both, a white box appears behind the chart when it is composited over the video background.

**Expected `data` shape:**

```python
{
    "labels": ["Category A", "Category B"],  # X-axis labels
    "before": [30, 22],                       # Bar heights (left bars)
    "after":  [72, 34]                        # Bar heights (right bars)
}
```

### 5.2 Line trend — `make_line_trend`

```python
make_line_trend(data: dict, out_path: str, title: str = "") -> str
```

Produces a time-series line chart with a translucent fill under the curve (`alpha=0.12`). Suited for growth trends, adoption curves, and any metric tracked over sequential time periods.

**Expected `data` shape:**

```python
{
    "x": [2021, 2022, 2023, 2024, 2025],  # X-axis values (numeric or strings)
    "y": [10, 18, 30, 45, 72]             # Y-axis values
}
```

### 5.3 Bullet overlay — `make_bullet_overlay`

```python
make_bullet_overlay(lines: list[str], out_path: str,
                    width: int = 900, font_size: int = 32) -> str
```

Renders a list of bullet-point strings onto a semi-transparent dark rounded rectangle using Pillow. The image height is computed dynamically from the number of lines:

```python
img_h = padding * 2 + len(lines) * line_h + 12
```

The fill colour `(10, 10, 10, 185)` gives roughly 73% opacity — dark enough for text legibility over any background, light enough that the background remains visible. The bullet character (`•`) is prepended in Python rather than in the font, so no special Unicode font support is required.

Font loading tries the DejaVu Sans Bold path common on Debian/Ubuntu systems, falling back to Pillow's built-in bitmap font if the TTF is absent.

### 5.4 Insight card — `make_insight_card`

```python
make_insight_card(insight: str, stat: str, out_path: str,
                  width: int = 960, height: int = 200) -> str
```

Renders a two-line card: a large bold headline (`font_size=34`) and a smaller supporting stat line (`font_size=20`). A solid red rectangle (`#E63946`) is drawn as a left-edge accent bar — a visual device borrowed from print editorial design that gives the card a distinct identity when overlaid on varied backgrounds.

The card uses `fill=(10, 10, 10, 200)` — approximately 78% opacity — slightly more opaque than the bullet overlay because the headline text is denser.

---

## 6. Video effects

### 6.1 Circular avatar mask — `apply_circle_mask`

```python
apply_circle_mask(clip: VideoFileClip, diameter: int) -> VideoFileClip
```

Takes an MP4 avatar clip and returns it with a circular alpha mask applied, so only the circle region is visible when the clip is composited over other layers.

The mask is built using NumPy's `ogrid`, which creates coordinate arrays without materialising a full mesh:

```python
Y, X = np.ogrid[:h, :w]
cx, cy = w / 2, h / 2
mask_arr = ((X - cx)**2 + (Y - cy)**2 <= (min(w, h) / 2)**2).astype(float)
```

This produces a 2D float array (values 0.0 or 1.0) where all pixels within the inscribed circle are 1 (opaque) and all pixels outside are 0 (transparent). MoviePy requires mask arrays in this float format — it does not accept uint8 or boolean arrays directly.

The mask array is wrapped in an `ImageClip` with `ismask=True` and the duration is set to match the source clip before calling `clip.set_mask()`.

**Why not use imagemagick or a pre-made circular PNG?** The numpy approach has no subprocess dependency, works for any input resolution, and the mask is computed once and reused for every frame without disk I/O.

### 6.2 Ken Burns zoom — `ken_burns`

```python
ken_burns(clip: ImageClip, zoom_ratio: float = 0.08) -> ImageClip
```

Applies a slow continuous zoom-in to a static image clip, creating the illusion of camera movement. This prevents the background from looking visually "dead" during the scene.

The implementation uses `clip.fl()`, MoviePy's frame-level transform function, which receives both `get_frame` (a callable that returns the frame array at time `t`) and the current time `t`:

```python
def zoom_frame(get_frame, t):
    frame = get_frame(t)
    frac = 1 + zoom_ratio * (t / clip.duration)   # grows from 1.0 to 1+zoom_ratio
    h, w = frame.shape[:2]
    new_h, new_w = int(h / frac), int(w / frac)   # shrink crop window
    y1 = (h - new_h) // 2                          # center the crop
    x1 = (w - new_w) // 2
    cropped = frame[y1:y1 + new_h, x1:x1 + new_w]
    return np.array(Image.fromarray(cropped).resize((w, h), Image.LANCZOS))
```

At `t=0`, `frac=1.0` so the crop is the full frame. At `t=duration`, `frac=1+zoom_ratio` so the crop is slightly smaller, and upscaling it back to full resolution creates the zoom effect. `zoom_ratio=0.08` means an 8% zoom over the full duration — perceptible but not distracting.

`apply_to=["mask"]` passes the same transform to the mask channel if one is present, keeping the mask geometrically in sync with the image.

---

## 7. Scene builders

Scene builders assemble the layers for a given `visual_cue` type into a `CompositeVideoClip`. Each builder follows the same pattern: build layers bottom-to-top, append to a list, return `CompositeVideoClip(layers, size=bg.size).set_duration(d)`.

The explicit `.set_duration(d)` on the return value is mandatory — see [§9.2](#92-the-set_duration-gotcha) for why.

### 7.1 Data scene — `build_data_scene`

Used for `visual_cue` values `bar_chart_comparison` and `line_trend`. The most information-dense layout:

- **Background**: full-canvas `ImageClip`, Ken Burns zoom at 8%, brightness reduced by 40 units via `vfx.lum_contrast(0, -40)`.
- **Chart**: resized to 700px wide, centred horizontally, positioned 180px from the top. Fades in over 0.6s starting at `t=0.5` and fades out over 0.4s at the end.
- **Insight card**: centred horizontally at y=820 (approximately the lower fifth of a 1080p frame). Fades in over 0.5s.
- **Avatar**: circular-masked at 240px diameter, positioned 40px from the bottom-right corner (`bg.w - 280, bg.h - 280`).

### 7.2 Bullet scene — `build_bullet_scene`

Used for `visual_cue` value `bullet_points`. A simpler layout suited to lists of supporting facts:

- **Background**: Ken Burns at 5% zoom (slower than the data scene — more contemplative pacing), brightness reduced by 50 units.
- **Bullet overlay**: rendered by `make_bullet_overlay`, centred both horizontally and vertically, fades in over 0.7s.
- **Avatar**: circular-masked at 200px diameter (slightly smaller than in the data scene), positioned 40px from the bottom-right corner.

If `bullet_lines` is not provided by the caller, the builder falls back to using `insight.key_insight` and `insight.supporting_stat` as two bullet points.

### 7.3 Full avatar scene — `build_full_avatar_scene`

Used for `visual_cue` value `full_avatar`. The "Hook" scene — designed to open a piece with a direct-to-camera delivery that grabs attention before the data arrives. No overlays; the avatar fills the entire frame:

```python
avatar = VideoFileClip(assets.avatar_video).subclip(0, d)
return avatar.resize(height=1080).set_duration(d)
```

This is the only scene type that does not use a `CompositeVideoClip` — it returns a `VideoFileClip` directly. The explicit `.set_duration(d)` is still applied (see §9.2).

---

## 8. Scene dispatcher — `dispatch_scene`

```python
dispatch_scene(insight: Insight, assets: SceneAssets,
               bullet_lines: Optional[list[str]] = None) -> CompositeVideoClip
```

The dispatcher is the JSON bridge's execution layer. It reads `insight.visual_cue` and routes to the correct builder, generating any intermediate assets (charts) along the way:

```
visual_cue value          Action
─────────────────────────────────────────────────────
"full_avatar"           → build_full_avatar_scene()
"bar_chart_comparison"  → make_bar_chart() → build_data_scene()
"line_trend"            → make_line_trend() → build_data_scene()
"bullet_points"         → build_bullet_scene()
<anything else>         → build_data_scene() with no chart (fallback)
```

Chart PNGs are written to `/tmp/chart.png`. This is intentionally a fixed path — each call overwrites the previous chart, which is fine because `dispatch_scene` is called sequentially per scene. If scenes are ever parallelised, use a `job_id`-prefixed temp path instead.

---

## 9. Crossfade transitions

### 9.1 How `crossfade_concat` works

```python
def crossfade_concat(scenes: list, fade_dur: float = 0.5) -> CompositeVideoClip:
    faded = []
    for i, clip in enumerate(scenes):
        c = clip
        if i > 0:
            c = c.fx(vfx.crossfadein, fade_dur)
        faded.append(c)
    return concatenate_videoclips(faded, padding=-fade_dur, method="compose")
```

`vfx.crossfadein` makes a clip's opacity ramp from 0 to 1 over `fade_dur` seconds from its start point. This handles the incoming side of the dissolve.

`padding=-fade_dur` is the critical parameter. By default, `concatenate_videoclips` places each clip immediately after the previous one ends. A negative padding shifts each clip left by `fade_dur` seconds, so it starts while the previous clip is still playing. The overlap window is exactly `fade_dur` seconds, which matches the duration of the `crossfadein` effect — this is what produces a dissolve rather than a hard cut or a gap.

`method="compose"` tells MoviePy to use `CompositeVideoClip` internally for the overlapping portions rather than trying to blend frames at the pixel level, which is how the alpha ramp from `crossfadein` is correctly respected.

The default `fade_dur` of `0.5s` is appropriate for fast-paced content. Increase to `0.8–1.0s` for a more cinematic feel. The total output duration is `sum(scene.duration for scene in scenes) - (len(scenes) - 1) * fade_dur`.

### 9.2 The `set_duration` gotcha

`CompositeVideoClip` infers its total duration by scanning the durations of all constituent clips. When sub-clips have `set_start` offsets — such as the chart clip which starts at `t=0.5` and has a duration of `d - 1.5`, and the insight card which starts at `t=0.5` with a duration of `d - 1.0` — MoviePy computes the composite's duration as `max(clip.start + clip.duration for clip in layers)`.

In most cases this yields a value slightly larger than `d` due to floating-point arithmetic on the offset calculations, or occasionally slightly smaller if a sub-clip ends fractionally before the background. Either error causes `crossfade_concat`'s `padding=-fade_dur` overlap to be miscalculated, typically producing a black flash frame at each scene boundary.

The fix is to explicitly call `.set_duration(d)` on every scene builder's return value, overriding the inferred value with the authoritative duration from the `Insight`:

```python
return CompositeVideoClip(layers, size=bg.size).set_duration(d)
```

This must be applied to all three builders, including `build_full_avatar_scene`, because a `resize()` call on a `VideoFileClip` creates a new clip object whose duration is re-derived from the source — it does not inherit the `subclip(0, d)` duration reliably on all platforms.

---

## 10. Master compositor — `compose_video`

```python
def compose_video(scenes: list, output_path: str = "output.mp4",
                  fps: int = 24, fade_dur: float = 0.5) -> str
```

The final assembly step. Calls `crossfade_concat` to produce the dissolved timeline, then writes to an H.264 MP4 via MoviePy's `write_videofile`:

```python
final.write_videofile(
    output_path,
    fps=fps,
    codec="libx264",
    audio_codec="aac",
    threads=4,
    preset="fast",
    logger=None,
)
```

`preset="fast"` is a reasonable default for a production pipeline — it is significantly faster than `slow` or `medium` with only a marginal quality difference at typical web streaming bitrates. Change to `slow` for archive-quality output. `logger=None` suppresses the verbose ffmpeg progress output; remove it during debugging.

`threads=4` maps to ffmpeg's `-threads` flag. Increase if the host has more cores available. This affects the encoding step only — MoviePy's frame rendering is single-threaded.

---

## 11. FastAPI server

`api_server.py` wraps the composition pipeline behind an HTTP API, enabling it to be called from any frontend, automation script, or orchestration system.

### 11.1 Request models

**`InsightPayload`** — mirrors the `Insight` dataclass with Pydantic validation:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `key_insight` | str | required | Headline text |
| `supporting_stat` | str | required | Sub-headline text |
| `visual_cue` | str | required | Scene template selector |
| `audio_tone` | str | required | Downstream audio metadata |
| `duration` | float | 3.0–60.0 | Scene length in seconds |
| `chart_data` | dict | optional | Data payload for chart generators |
| `bullet_lines` | list[str] | optional | Explicit bullet text (overrides defaults) |

**`ComposeRequest`** — the top-level request body:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `insights` | list[InsightPayload] | required | Ordered list of scenes |
| `fps` | int | 24 | Output frame rate (12–60) |
| `fade_dur` | float | 0.5 | Crossfade duration in seconds (0.0–2.0) |

**`JobStatus`** — the response model for job tracking:

| Field | Values | Description |
|-------|--------|-------------|
| `job_id` | UUID hex string | Unique identifier for polling |
| `status` | `queued`, `processing`, `done`, `error` | Current state |
| `output_url` | `/download/{job_id}` or null | Available when `status == "done"` |
| `error` | string or null | Error message when `status == "error"` |

### 11.2 Job lifecycle

Video composition is CPU-intensive and typically takes 30–120 seconds for a multi-scene piece. The API uses FastAPI's `BackgroundTasks` to run composition asynchronously so the HTTP response is immediate:

```
POST /compose
    │
    ├─ Validates payload, saves uploaded files to /tmp/broll_jobs/{job_id}/
    ├─ Creates JobStatus(status="queued")
    ├─ Registers BackgroundTask → _compose_worker()
    └─ Returns 202 Accepted with job_id

_compose_worker() (background)
    │
    ├─ Sets status = "processing"
    ├─ Runs _sync_compose() in a thread pool (loop.run_in_executor)
    │     └─ Iterates insights → dispatch_scene() → compose_video()
    ├─ On success: status = "done", output_url = "/download/{job_id}"
    └─ On error:   status = "error", error = str(exc)

GET /status/{job_id}  ← poll until status == "done" or "error"

GET /download/{job_id}  ← returns MP4 file
```

`loop.run_in_executor(None, _sync_compose)` is important: MoviePy's frame rendering and ffmpeg's encoding are blocking operations. Running them directly in an `async` function would block the entire event loop. `run_in_executor` offloads the work to a thread pool, keeping the server responsive to other requests during composition.

The job store is currently a plain Python dict (`_jobs`). This is appropriate for a single-worker development server. Replace with Redis (using `aioredis` or `redis-py`) for multi-worker or multi-instance deployments.

### 11.3 API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/compose` | Start a composition job (multipart form) |
| `GET` | `/status/{job_id}` | Poll job status |
| `GET` | `/download/{job_id}` | Download finished MP4 |
| `POST` | `/preview/chart` | Generate and return a chart PNG (no video) |
| `GET` | `/health` | Liveness check |

Interactive documentation is available at `http://localhost:8000/docs` once the server is running (FastAPI's built-in Swagger UI).

---

## 12. Running the project

### 12.1 Smoke test (no media files needed)

The smoke test validates all asset generators — chart PNGs, bullet overlays, and insight cards — without requiring any background images or avatar videos:

```bash
python broll_composer.py
```

Expected output:

```
Chart saved → /tmp/demo_chart.png
Bullets saved → /tmp/demo_bullets.png
Insight card saved → /tmp/demo_card.png

Sample Insight JSON: { ... }

All asset generation tests passed.
To run full video composition, supply real background_img and avatar_video paths.
```

Inspect the PNG files in `/tmp/` to visually verify chart rendering before running the full pipeline.

### 12.2 Full video composition

```python
from broll_composer import pipeline_from_json

insight_json = """{
    "key_insight": "AI reduced production time by 40%",
    "supporting_stat": "HubSpot 2026: 12% CTR lift",
    "visual_cue": "bar_chart_comparison",
    "audio_tone": "authoritative_and_surprising",
    "duration": 10.0,
    "chart_data": {
        "labels": ["Content Velocity", "CTR", "Engagement", "Cost/Lead"],
        "before": [30, 22, 18, 60],
        "after":  [72, 34, 41, 38]
    }
}"""

output_path = pipeline_from_json(
    insight_json,
    background_img="path/to/background.jpg",
    avatar_video="path/to/avatar.mp4",    # optional
)
print(f"Video written to {output_path}")
```

### 12.3 API server

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

For development with auto-reload:

```bash
uvicorn api_server:app --reload
```

---

## 13. Calling the API

The `/compose` endpoint accepts `multipart/form-data` with three parts: `payload` (JSON string), `background` (image file), and optionally `avatar` (video file).

```bash
curl -X POST http://localhost:8000/compose \
  -F 'payload={
    "insights": [{
      "key_insight": "AI reduced production time by 40%",
      "supporting_stat": "HubSpot 2026: 12% CTR lift",
      "visual_cue": "bar_chart_comparison",
      "audio_tone": "authoritative_and_surprising",
      "duration": 10.0,
      "chart_data": {
        "labels": ["Velocity","CTR","Engagement","Cost/Lead"],
        "before": [30, 22, 18, 60],
        "after":  [72, 34, 41, 38]
      }
    }],
    "fps": 24,
    "fade_dur": 0.5
  }' \
  -F 'background=@./bg.jpg' \
  -F 'avatar=@./avatar.mp4'
```

This returns a `JobStatus` with a `job_id`. Poll for completion:

```bash
curl http://localhost:8000/status/{job_id}
# → {"job_id": "...", "status": "done", "output_url": "/download/..."}
```

Download the finished video:

```bash
curl -O http://localhost:8000/download/{job_id}
```

Preview a chart without video assembly:

```bash
curl -X POST "http://localhost:8000/preview/chart?title=My+Chart&chart_type=bar_chart_comparison" \
  -H "Content-Type: application/json" \
  -d '{"labels":["A","B"],"before":[30,22],"after":[72,34]}' \
  --output preview.png
```

---

## 14. Production notes

**Concurrency**: FastAPI's `BackgroundTasks` runs in the same process as the web server. Under concurrent load, multiple composition jobs will share the same thread pool, which can cause memory pressure (each MoviePy frame rendering buffers several seconds of uncompressed video). For production, move composition to a dedicated worker queue (Celery + Redis, or ARQ) and have the API server dispatch jobs to it rather than running them in-process.

**Temp file isolation**: Chart PNGs and insight card PNGs are written to fixed paths under `/tmp/`. This is safe for sequential processing but will cause race conditions if jobs are parallelised. Prefix all temp file paths with the `job_id` to isolate them:

```python
chart_path = f"/tmp/{job_id}_chart.png"
```

**Memory**: MoviePy loads entire video clips into memory for compositing. For scenes longer than ~30 seconds with a high-resolution avatar, memory use can reach several GB. If this is a concern, render scenes individually and use ffmpeg's `concat` demuxer to join them in a second pass rather than compositing them all in Python.

**ffmpeg version**: MoviePy 1.0.3 delegates encoding to ffmpeg. Versions prior to 4.x may not support all `preset` values or the `aac` codec without additional flags. The pipeline is tested against ffmpeg 5.x and 6.x.

**File cleanup**: Completed job files accumulate in `/tmp/broll_jobs/`. Add a cleanup background task or cron job that deletes job directories older than a configurable TTL (e.g. 1 hour).

---

## 15. Extending the pipeline

**Adding a new scene template**: add a builder function following the `build_*_scene` naming convention, then add a `visual_cue` string → function mapping in `dispatch_scene`. No other changes are needed.

**Adding a new chart type**: add a `make_*` function that writes a transparent PNG, then handle the new `visual_cue` in `dispatch_scene` by calling it before passing `assets` to a builder.

**Supporting multiple backgrounds per script**: `SceneAssets` currently takes a single `background_img`. To vary the background per scene, add a `background_img` field to `InsightPayload` in the API model and pass it through to `SceneAssets` in the compose worker.

**Audio**: the pipeline produces silent video. Attach a voiceover by loading it as a MoviePy `AudioFileClip`, setting its start time to align with each scene, and passing the composite audio to `final.set_audio()` before calling `write_videofile`.
