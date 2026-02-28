from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from middleware.auth_middleware import get_current_user
from services.database import get_db
from services.story_writer.story_project_service import StoryProjectService
from ..models_projects import (
    CreateStoryProjectRequest,
    StoryProjectListResponse,
    StoryProjectResponse,
    UpdateStoryProjectRequest,
)


router = APIRouter()


@router.post("/projects", response_model=StoryProjectResponse, status_code=201)
async def create_story_project(
    request: CreateStoryProjectRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> StoryProjectResponse:
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")

        service = StoryProjectService(db)

        existing = service.get_project(user_id, request.project_id)
        if existing:
            raise HTTPException(status_code=400, detail="Project ID already exists")

        project = service.create_project(
            user_id=user_id,
            project_id=request.project_id,
            title=request.title,
            story_mode=request.story_mode,
            story_template=request.story_template,
            setup=request.setup,
        )

        return StoryProjectResponse.model_validate(project)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating story project: {str(e)}")


@router.get("/projects/{project_id}", response_model=StoryProjectResponse)
async def get_story_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> StoryProjectResponse:
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")

        service = StoryProjectService(db)
        project = service.get_project(user_id, project_id)

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        return StoryProjectResponse.model_validate(project)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching story project: {str(e)}")


@router.put("/projects/{project_id}", response_model=StoryProjectResponse)
async def update_story_project(
    project_id: str,
    request: UpdateStoryProjectRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> StoryProjectResponse:
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")

        service = StoryProjectService(db)

        updates = request.model_dump(exclude_unset=True)

        project = service.update_project(user_id, project_id, **updates)

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        return StoryProjectResponse.model_validate(project)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating story project: {str(e)}")


@router.get("/projects", response_model=StoryProjectListResponse)
async def list_story_projects(
    status: Optional[str] = Query(None, description="Filter by status"),
    favorites_only: bool = Query(False, description="Only favorites"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    order_by: str = Query("updated_at", description="Order by: updated_at or created_at"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> StoryProjectListResponse:
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")

        if order_by not in ["updated_at", "created_at"]:
            raise HTTPException(status_code=400, detail="order_by must be 'updated_at' or 'created_at'")

        service = StoryProjectService(db)
        projects, total = service.list_projects(
            user_id=user_id,
            status=status,
            favorites_only=favorites_only,
            limit=limit,
            offset=offset,
            order_by=order_by,
        )

        return StoryProjectListResponse(
            projects=[StoryProjectResponse.model_validate(p) for p in projects],
            total=total,
            limit=limit,
            offset=offset,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing story projects: {str(e)}")


@router.delete("/projects/{project_id}", status_code=204)
async def delete_story_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> None:
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")

        service = StoryProjectService(db)
        deleted = service.delete_project(user_id, project_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Project not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting story project: {str(e)}")


@router.post("/projects/{project_id}/favorite", response_model=StoryProjectResponse)
async def toggle_story_project_favorite(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> StoryProjectResponse:
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")

        service = StoryProjectService(db)
        project = service.toggle_favorite(user_id, project_id)

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        return StoryProjectResponse.model_validate(project)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling story project favorite: {str(e)}")

