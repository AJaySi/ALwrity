"""Save generated images to the unified asset library."""

import base64
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .deps import _require_user_id
from middleware.auth_middleware import get_current_user
from services.database import get_db
from utils.logger_utils import get_service_logger
from utils.storage_paths import get_repo_root, sanitize_user_id

logger = get_service_logger("api.image_studio")
router = APIRouter(tags=["image-studio"])


class SaveToLibraryRequest(BaseModel):
    image_base64: str = Field(..., description="Base64-encoded image (or data URL)")
    prompt: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    cost: Optional[float] = None
    operation: str = Field("image-generation", description="Operation type for labelling")
    output_format: str = Field("png", description="Output image format")


@router.post("/save-to-library")
async def save_to_library(
    req: SaveToLibraryRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save a generated image to the asset library.

    Decodes base64 image data, saves to workspace disk storage,
    and creates a record in the ContentAsset database table.
    """
    user_id = _require_user_id(current_user, "save-to-library")

    # Decode base64 payload
    try:
        b64data = req.image_base64
        if "base64," in b64data:
            b64data = b64data.split("base64,")[1]
        image_bytes = base64.b64decode(b64data)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image data")

    # Generate file path under workspace
    safe_user = sanitize_user_id(user_id)
    repo_root = get_repo_root()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"generated_{timestamp}.{req.output_format or 'png'}"

    assets_dir = repo_root / "workspace" / f"workspace_{safe_user}" / "assets" / "images"
    assets_dir.mkdir(parents=True, exist_ok=True)

    file_path = assets_dir / filename
    file_path.write_bytes(image_bytes)

    # Build serving URL (assets_serving.py serves /{user_id}/avatars/{filename})
    file_url = f"/api/assets/{safe_user}/avatars/{filename}"

    # Save to unified asset library via existing utility
    from utils.asset_tracker import save_asset_to_library

    asset_id = save_asset_to_library(
        db=db,
        user_id=user_id,
        asset_type="image",
        source_module="image_studio",
        filename=filename,
        file_url=file_url,
        file_path=str(file_path),
        file_size=len(image_bytes),
        mime_type=f"image/{req.output_format or 'png'}",
        title=f"Generated Image - {timestamp}",
        prompt=req.prompt,
        provider=req.provider,
        model=req.model,
        cost=req.cost,
    )

    if not asset_id:
        raise HTTPException(status_code=500, detail="Failed to save to asset library")

    logger.info(f"[Save to Library] ✅ Image saved: asset_id={asset_id}, user={user_id}")

    return {
        "success": True,
        "asset_id": asset_id,
        "file_url": file_url,
        "filename": filename,
        "file_size": len(image_bytes),
    }
