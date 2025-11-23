"""
Content Assets API Router
API endpoints for managing unified content assets across all modules.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from services.database import get_db
from middleware.auth_middleware import get_current_user
from services.content_asset_service import ContentAssetService
from models.content_asset_models import AssetType, AssetSource

router = APIRouter(prefix="/api/content-assets", tags=["Content Assets"])


class AssetResponse(BaseModel):
    """Response model for asset data."""
    id: int
    user_id: str
    asset_type: str
    source_module: str
    filename: str
    file_url: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    prompt: Optional[str] = None
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    provider: Optional[str] = None
    model: Optional[str] = None
    cost: float = 0.0
    generation_time: Optional[float] = None
    is_favorite: bool = False
    download_count: int = 0
    share_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AssetListResponse(BaseModel):
    """Response model for asset list."""
    assets: List[AssetResponse]
    total: int
    limit: int
    offset: int


@router.get("/", response_model=AssetListResponse)
async def get_assets(
    asset_type: Optional[str] = Query(None, description="Filter by asset type"),
    source_module: Optional[str] = Query(None, description="Filter by source module"),
    search: Optional[str] = Query(None, description="Search query"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    favorites_only: bool = Query(False, description="Only favorites"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get user's content assets with optional filtering."""
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        service = ContentAssetService(db)
        
        # Parse filters
        asset_type_enum = None
        if asset_type:
            try:
                asset_type_enum = AssetType(asset_type.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid asset type: {asset_type}")
        
        source_module_enum = None
        if source_module:
            try:
                source_module_enum = AssetSource(source_module.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid source module: {source_module}")
        
        tags_list = None
        if tags:
            tags_list = [tag.strip() for tag in tags.split(",")]
        
        assets, total = service.get_user_assets(
            user_id=user_id,
            asset_type=asset_type_enum,
            source_module=source_module_enum,
            search_query=search,
            tags=tags_list,
            favorites_only=favorites_only,
            limit=limit,
            offset=offset,
        )
        
        return AssetListResponse(
            assets=[AssetResponse.model_validate(asset) for asset in assets],
            total=total,
            limit=limit,
            offset=offset,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching assets: {str(e)}")


@router.post("/{asset_id}/favorite", response_model=Dict[str, Any])
async def toggle_favorite(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Toggle favorite status of an asset."""
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        service = ContentAssetService(db)
        is_favorite = service.toggle_favorite(asset_id, user_id)
        
        return {"asset_id": asset_id, "is_favorite": is_favorite}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling favorite: {str(e)}")


@router.delete("/{asset_id}", response_model=Dict[str, Any])
async def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Delete an asset."""
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        service = ContentAssetService(db)
        success = service.delete_asset(asset_id, user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        return {"asset_id": asset_id, "deleted": True}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting asset: {str(e)}")


@router.post("/{asset_id}/usage", response_model=Dict[str, Any])
async def track_usage(
    asset_id: int,
    action: str = Query(..., description="Action: download, share, or access"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Track asset usage (download, share, access)."""
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        if action not in ["download", "share", "access"]:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        service = ContentAssetService(db)
        service.update_asset_usage(asset_id, user_id, action)
        
        return {"asset_id": asset_id, "action": action, "tracked": True}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking usage: {str(e)}")


class AssetUpdateRequest(BaseModel):
    """Request model for updating asset metadata."""
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    update_data: AssetUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Update asset metadata."""
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        service = ContentAssetService(db)
        
        asset = service.update_asset(
            asset_id=asset_id,
            user_id=user_id,
            title=update_data.title,
            description=update_data.description,
            tags=update_data.tags,
        )
        
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        return AssetResponse.model_validate(asset)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating asset: {str(e)}")


@router.get("/statistics", response_model=Dict[str, Any])
async def get_statistics(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get asset statistics for the current user."""
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        service = ContentAssetService(db)
        stats = service.get_asset_statistics(user_id)
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")

