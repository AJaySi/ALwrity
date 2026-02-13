from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from pathlib import Path
from services.database import WORKSPACE_DIR, get_user_db_path

router = APIRouter(prefix="/api/assets", tags=["Assets Serving"])

@router.get("/{user_id}/avatars/{filename}")
async def serve_avatar(user_id: str, filename: str):
    """
    Serve avatar images directly.
    Public endpoint relying on unguessable filenames.
    """
    # Sanitize user_id (simple check to prevent directory traversal)
    safe_user_id = "".join(c for c in user_id if c.isalnum() or c in ('-', '_'))
    if safe_user_id != user_id:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    # Sanitize filename
    safe_filename = os.path.basename(filename)
    
    # Construct path
    # workspace/workspace_{user_id}/assets/avatars/{filename}
    file_path = Path(WORKSPACE_DIR) / f"workspace_{safe_user_id}" / "assets" / "avatars" / safe_filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Asset not found")
        
    return FileResponse(file_path)

@router.get("/{user_id}/voice_samples/{filename}")
async def serve_voice_sample(user_id: str, filename: str):
    """
    Serve voice sample audio files directly.
    """
    # Sanitize user_id
    safe_user_id = "".join(c for c in user_id if c.isalnum() or c in ('-', '_'))
    if safe_user_id != user_id:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    # Sanitize filename
    safe_filename = os.path.basename(filename)
    
    # Construct path
    # workspace/workspace_{user_id}/assets/voice_samples/{filename}
    file_path = Path(WORKSPACE_DIR) / f"workspace_{safe_user_id}" / "assets" / "voice_samples" / safe_filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Asset not found")
        
    return FileResponse(file_path)
