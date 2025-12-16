"""
Podcast Project Handlers

CRUD operations for podcast projects.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from services.database import get_db
from middleware.auth_middleware import get_current_user
from services.podcast_service import PodcastService
from ..models import (
    PodcastProjectResponse,
    CreateProjectRequest,
    UpdateProjectRequest,
    PodcastProjectListResponse,
)

router = APIRouter()


@router.post("/projects", response_model=PodcastProjectResponse, status_code=201)
async def create_project(
    request: CreateProjectRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Create a new podcast project."""
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        service = PodcastService(db)
        
        # Check if project_id already exists for this user
        existing = service.get_project(user_id, request.project_id)
        if existing:
            raise HTTPException(status_code=400, detail="Project ID already exists")
        
        project = service.create_project(
            user_id=user_id,
            project_id=request.project_id,
            idea=request.idea,
            duration=request.duration,
            speakers=request.speakers,
            budget_cap=request.budget_cap,
        )
        
        return PodcastProjectResponse.model_validate(project)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating project: {str(e)}")


@router.get("/projects/{project_id}", response_model=PodcastProjectResponse)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get a podcast project by ID."""
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        service = PodcastService(db)
        project = service.get_project(user_id, project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return PodcastProjectResponse.model_validate(project)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching project: {str(e)}")


@router.put("/projects/{project_id}", response_model=PodcastProjectResponse)
async def update_project(
    project_id: str,
    request: UpdateProjectRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Update a podcast project state."""
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        service = PodcastService(db)
        
        # Convert request to dict, excluding None values
        updates = request.model_dump(exclude_unset=True)
        
        project = service.update_project(user_id, project_id, **updates)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return PodcastProjectResponse.model_validate(project)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating project: {str(e)}")


@router.get("/projects", response_model=PodcastProjectListResponse)
async def list_projects(
    status: Optional[str] = Query(None, description="Filter by status"),
    favorites_only: bool = Query(False, description="Only favorites"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    order_by: str = Query("updated_at", description="Order by: updated_at or created_at"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """List user's podcast projects."""
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        if order_by not in ["updated_at", "created_at"]:
            raise HTTPException(status_code=400, detail="order_by must be 'updated_at' or 'created_at'")
        
        service = PodcastService(db)
        projects, total = service.list_projects(
            user_id=user_id,
            status=status,
            favorites_only=favorites_only,
            limit=limit,
            offset=offset,
            order_by=order_by,
        )
        
        return PodcastProjectListResponse(
            projects=[PodcastProjectResponse.model_validate(p) for p in projects],
            total=total,
            limit=limit,
            offset=offset,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing projects: {str(e)}")


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Delete a podcast project."""
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        service = PodcastService(db)
        deleted = service.delete_project(user_id, project_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting project: {str(e)}")


@router.post("/projects/{project_id}/favorite", response_model=PodcastProjectResponse)
async def toggle_favorite(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Toggle favorite status of a project."""
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        service = PodcastService(db)
        project = service.toggle_favorite(user_id, project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return PodcastProjectResponse.model_validate(project)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling favorite: {str(e)}")

