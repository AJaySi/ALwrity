"""
FastAPI wrapper for the B-Roll Composer pipeline.
POST /compose  →  triggers scene assembly, returns video download URL.
"""

from __future__ import annotations
import os
import uuid
import json
import asyncio
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from broll_composer import (
    Insight, SceneAssets, dispatch_scene, compose_video,
    make_bar_chart, make_line_trend, make_bullet_overlay,
)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="B-Roll Composer API",
    description="Programmatic video composition: Background + Chart + Avatar Circle",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WORK_DIR = Path("/tmp/broll_jobs")
WORK_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class InsightPayload(BaseModel):
    key_insight: str = Field(..., example="AI tools reduced content cycles by 40% in 2025.")
    supporting_stat: str = Field(..., example="HubSpot 2026 report cites a 12% lift in CTR.")
    visual_cue: str = Field(
        ...,
        example="bar_chart_comparison",
        description="bar_chart_comparison | line_trend | bullet_points | full_avatar",
    )
    audio_tone: str = Field(..., example="authoritative_and_surprising")
    duration: float = Field(default=10.0, ge=3.0, le=60.0)
    chart_data: dict = Field(default_factory=dict)
    bullet_lines: Optional[List[str]] = None


class ComposeRequest(BaseModel):
    insights: List[InsightPayload]
    fps: int = Field(default=24, ge=12, le=60)
    fade_dur: float = Field(default=0.5, ge=0.0, le=2.0,
                            description="Crossfade duration in seconds between scenes")


class JobStatus(BaseModel):
    job_id: str
    status: str        # queued | processing | done | error
    output_url: Optional[str] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# In-memory job store (replace with Redis in production)
# ---------------------------------------------------------------------------

_jobs: dict[str, JobStatus] = {}


# ---------------------------------------------------------------------------
# Background task: composition worker
# ---------------------------------------------------------------------------

async def _compose_worker(
    job_id: str,
    request: ComposeRequest,
    bg_path: str,
    avatar_path: Optional[str],
):
    job = _jobs[job_id]
    job.status = "processing"

    try:
        loop = asyncio.get_running_loop()
        out_path = str(WORK_DIR / f"{job_id}.mp4")

        def _sync_compose():
            scenes = []
            for i, payload in enumerate(request.insights):
                insight = Insight(
                    key_insight=payload.key_insight,
                    supporting_stat=payload.supporting_stat,
                    visual_cue=payload.visual_cue,
                    audio_tone=payload.audio_tone,
                    chart_data=payload.chart_data,
                    duration=payload.duration,
                )
                assets = SceneAssets(
                    background_img=bg_path,
                    avatar_video=avatar_path,
                )
                scene = dispatch_scene(insight, assets, payload.bullet_lines)
                scenes.append(scene)

            compose_video(scenes, output_path=out_path, fps=request.fps,
                          fade_dur=request.fade_dur)
            return out_path

        await loop.run_in_executor(None, _sync_compose)
        job.status = "done"
        job.output_url = f"/download/{job_id}"

    except Exception as exc:
        job.status = "error"
        job.error = str(exc)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/compose", response_model=JobStatus, status_code=202)
async def start_compose(
    background_tasks: BackgroundTasks,
    payload: str = Form(..., description="JSON string matching ComposeRequest schema"),
    background: UploadFile = File(..., description="Background image (JPEG/PNG)"),
    avatar: Optional[UploadFile] = File(None, description="Avatar video (MP4) — optional"),
):
    """
    Kick off a video composition job.
    - **payload**: JSON body (ComposeRequest)
    - **background**: background image file
    - **avatar**: optional avatar video file
    Returns a job_id — poll GET /status/{job_id} for progress.
    """
    try:
        request = ComposeRequest(**json.loads(payload))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid payload: {e}")

    job_id = uuid.uuid4().hex

    # Save uploads
    job_dir = WORK_DIR / job_id
    job_dir.mkdir(exist_ok=True)

    bg_path = str(job_dir / background.filename)
    with open(bg_path, "wb") as f:
        f.write(await background.read())

    avatar_path = None
    if avatar:
        avatar_path = str(job_dir / avatar.filename)
        with open(avatar_path, "wb") as f:
            f.write(await avatar.read())

    # Register job
    job = JobStatus(job_id=job_id, status="queued")
    _jobs[job_id] = job

    # Launch background worker
    background_tasks.add_task(
        _compose_worker, job_id, request, bg_path, avatar_path
    )

    return job


@app.get("/status/{job_id}", response_model=JobStatus)
async def get_status(job_id: str):
    """Poll composition job status."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/download/{job_id}")
async def download_video(job_id: str):
    """Download the finished video."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "done":
        raise HTTPException(status_code=409, detail=f"Job status: {job.status}")

    out_path = WORK_DIR / f"{job_id}.mp4"
    if not out_path.exists():
        raise HTTPException(status_code=404, detail="Output file missing")

    return FileResponse(
        path=str(out_path),
        media_type="video/mp4",
        filename=f"broll_{job_id}.mp4",
    )


@app.post("/preview/chart")
async def preview_chart(
    chart_data: dict,
    title: str = "",
    chart_type: str = "bar_chart_comparison",
):
    """Generate and return a chart PNG for preview (no video assembly)."""
    out = str(WORK_DIR / f"preview_{uuid.uuid4().hex}.png")
    if chart_type == "bar_chart_comparison":
        make_bar_chart(chart_data, out, title)
    else:
        make_line_trend(chart_data, out, title)
    return FileResponse(path=out, media_type="image/png")


@app.get("/health")
async def health():
    return {"status": "ok"}
