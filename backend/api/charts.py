"""
Chart API — Shared chart generation endpoints for Blog Writer, Podcast Maker, etc.

Two modes:
  1. Explicit: POST /api/charts/generate  with { chart_type, chart_data, title }
  2. AI-driven: POST /api/charts/generate  with { text }  → LLM infers chart_type + data

Both return { preview_url, chart_id, chart_type?, chart_data?, title? }
"""

import uuid
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from loguru import logger

from middleware.auth_middleware import get_current_user, get_current_user_with_query_token
from api.story_writer.utils.auth import require_authenticated_user
from services.chart_service import get_chart_service, VALID_CHART_TYPES


router = APIRouter(prefix="/api/charts", tags=["Charts"])


class ChartGenerateRequest(BaseModel):
    """Request for chart generation.

    Provide either:
      - chart_type + chart_data (explicit mode), OR
      - text (AI inference mode — LLM determines chart_type + data)
    """
    chart_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Chart data dict (labels, values, before/after, etc.)"
    )
    chart_type: Optional[str] = Field(
        default=None,
        description=f"Chart type: {', '.join(VALID_CHART_TYPES)}"
    )
    title: str = Field(default="", description="Chart title")
    subtitle: Optional[str] = Field(default="", description="Optional subtitle")
    text: Optional[str] = Field(
        default=None,
        description="Text to infer chart from (AI mode). Mutually exclusive with chart_type+chart_data."
    )
    section_heading: Optional[str] = Field(
        default=None,
        description="Blog section heading for context (AI mode with research)"
    )
    section_key_points: Optional[list] = Field(
        default=None,
        description="Key points from the section (AI mode with research)"
    )


class ChartGenerateResponse(BaseModel):
    """Response for chart generation."""
    preview_url: str = ""
    chart_id: str = ""
    chart_type: Optional[str] = None
    chart_data: Optional[Dict[str, Any]] = None
    title: Optional[str] = None
    warnings: list = Field(default_factory=list, description="Pipeline warnings (e.g. Exa search failures)")


@router.post("/generate", response_model=ChartGenerateResponse)
async def generate_chart(
    request: ChartGenerateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Generate a chart PNG preview.

    Two modes:
      1. Explicit: Provide chart_type + chart_data
      2. AI-driven: Provide text, and the LLM infers chart_type + chart_data
    """
    user_id = require_authenticated_user(current_user)

    try:
        chart_svc = get_chart_service(user_id=user_id)

        if request.text and not request.chart_type:
            # AI inference mode
            logger.info(f"[Charts] AI inference mode for user {user_id}, text length={len(request.text)}")
            result = await chart_svc.generate_chart_from_text(
                text=request.text,
                user_id=user_id,
                section_heading=request.section_heading,
                section_key_points=request.section_key_points,
            )

            if not result.get("path"):
                raise HTTPException(status_code=500, detail="Chart generation failed")

            chart_id = result["chart_id"]
            filename = result.get("filename", f"chart_preview_{chart_id}.png")

            return ChartGenerateResponse(
                preview_url=f"/api/charts/preview/{chart_id}/{filename}",
                chart_id=chart_id,
                chart_type=result.get("chart_type"),
                chart_data=result.get("chart_data"),
                title=result.get("title"),
                warnings=result.get("warnings", []),
            )

        elif request.chart_type and request.chart_data:
            # Explicit mode
            chart_type = request.chart_type
            if chart_type not in VALID_CHART_TYPES:
                # Try normalizing aliases
                from services.chart_service import _normalize_chart_type
                chart_type = _normalize_chart_type(chart_type)
                if chart_type not in VALID_CHART_TYPES:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid chart_type. Must be one of: {VALID_CHART_TYPES}"
                    )

            logger.info(f"[Charts] Explicit mode: type={chart_type}, user={user_id}")

            chart_id = uuid.uuid4().hex[:8]
            result = chart_svc.generate_chart(
                chart_data=request.chart_data,
                chart_type=chart_type,
                title=request.title,
                subtitle=request.subtitle or "",
                chart_id=chart_id,
            )

            if not result.get("path"):
                raise HTTPException(status_code=500, detail="Chart generation failed — check chart_data format")

            filename = result.get("filename", f"chart_preview_{chart_id}.png")

            return ChartGenerateResponse(
                preview_url=f"/api/charts/preview/{chart_id}/{filename}",
                chart_id=chart_id,
                chart_type=chart_type,
                chart_data=request.chart_data,
                title=request.title,
            )

        else:
            raise HTTPException(
                status_code=400,
                detail="Provide either 'text' (AI mode) or 'chart_type' + 'chart_data' (explicit mode)"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Charts] Generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chart generation failed: {str(e)}")


@router.get("/preview/{chart_id}/{filename}")
async def serve_chart_preview(
    chart_id: str,
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user_with_query_token),
):
    """Serve chart preview PNG files. Auth via header or query token."""
    user_id = require_authenticated_user(current_user)

    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    chart_svc = get_chart_service(user_id=user_id)
    file_path = chart_svc.get_chart_preview_path(chart_id)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Chart preview not found")

    if not str(file_path.resolve()).startswith(str(chart_svc.output_dir.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")

    return FileResponse(
        path=str(file_path),
        media_type="image/png",
        filename=filename,
    )


@router.get("/health")
async def charts_health():
    """Health check for Charts service."""
    return {"status": "ok", "service": "charts"}