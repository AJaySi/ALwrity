"""
Research Project Handler

CRUD operations for research projects.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from loguru import logger
import uuid
from sqlalchemy import func

from services.database import get_db
from middleware.auth_middleware import get_current_user
from services.research_service import ResearchService
from models.research_models import ResearchProject
from ..models import (
    SaveResearchProjectRequest,
    SaveResearchProjectResponse,
    ResearchProjectResponse,
    ResearchProjectListResponse,
)

router = APIRouter()


@router.post("/projects/save", response_model=SaveResearchProjectResponse)
async def save_research_project(
    request: SaveResearchProjectRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Save a research project to database.
    
    This endpoint saves the complete research project state to the database,
    allowing users to resume research later. Similar to podcast projects.
    Uses database storage instead of file-based storage for production reliability.
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID")
        
        logger.info(f"[Research Projects] Saving project: {request.title[:50] if request.title else 'Untitled'}...")
        
        service = ResearchService(db)
        
        # Check if this is an update (project_id provided) or new project
        project_id = request.project_id if request.project_id else str(uuid.uuid4())
        existing_project = service.get_project(user_id, project_id)
        
        # Determine status based on completion
        status = "completed" if (request.intent_result or request.legacy_result) else "in_progress" if request.intent_analysis else "draft"
        
        # Generate title if not provided
        project_title = request.title or f"Research: {', '.join(request.keywords[:3])}"
        
        if existing_project:
            # Update existing project
            updated = service.update_project(
                user_id=user_id,
                project_id=project_id,
                title=project_title,
                keywords=request.keywords,
                industry=request.industry,
                target_audience=request.target_audience,
                research_mode=request.research_mode,
                config=request.config,
                intent_analysis=request.intent_analysis,
                confirmed_intent=request.confirmed_intent,
                intent_result=request.intent_result,
                legacy_result=request.legacy_result,
                current_step=request.current_step,
                status=status,
            )
            
            if updated:
                logger.info(f"✅ Research project updated in database: project_id={project_id}, db_id={updated.id}")
                return SaveResearchProjectResponse(
                    success=True,
                    asset_id=updated.id,
                    project_id=project_id,
                    message=f"Research project updated successfully"
                )
            else:
                return SaveResearchProjectResponse(
                    success=False,
                    message="Failed to update research project"
                )
        else:
            # Create new project
            project = service.create_project(
                user_id=user_id,
                project_id=project_id,
                keywords=request.keywords,
                industry=request.industry,
                target_audience=request.target_audience,
                research_mode=request.research_mode,
                title=project_title,
                config=request.config,
                intent_analysis=request.intent_analysis,
                confirmed_intent=request.confirmed_intent,
                intent_result=request.intent_result,
                legacy_result=request.legacy_result,
                current_step=request.current_step,
                status=status,
            )
            
            logger.info(f"✅ Research project saved to database: project_id={project_id}, db_id={project.id}")
            return SaveResearchProjectResponse(
                success=True,
                asset_id=project.id,
                project_id=project_id,
                message=f"Research project saved successfully"
            )
            
    except Exception as e:
        logger.error(f"[Research Projects] Save failed: {e}")
        import traceback
        traceback.print_exc()
        return SaveResearchProjectResponse(
            success=False,
            message=f"Error saving research project: {str(e)}"
        )


@router.get("/projects/{project_id}", response_model=ResearchProjectResponse)
async def get_research_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get a research project by ID."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID")
        
        service = ResearchService(db)
        project = service.get_project(user_id, project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return ResearchProjectResponse.model_validate(project)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Research Projects] Get failed: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching project: {str(e)}")


@router.get("/projects", response_model=ResearchProjectListResponse)
async def list_research_projects(
    status: Optional[str] = Query(None, description="Filter by status"),
    is_favorite: Optional[bool] = Query(None, description="Filter by favorite"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """List user's research projects."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID")
        
        service = ResearchService(db)
        projects = service.list_projects(
            user_id=user_id,
            status=status,
            is_favorite=is_favorite,
            limit=limit,
            offset=offset,
        )
        
        # Get total count
        total_query = db.query(func.count(ResearchProject.id)).filter(ResearchProject.user_id == user_id)
        if status:
            total_query = total_query.filter(ResearchProject.status == status)
        if is_favorite is not None:
            total_query = total_query.filter(ResearchProject.is_favorite == is_favorite)
        total = total_query.scalar()
        
        return ResearchProjectListResponse(
            projects=[ResearchProjectResponse.model_validate(p) for p in projects],
            total=total,
            limit=limit,
            offset=offset,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Research Projects] List failed: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing projects: {str(e)}")


@router.put("/projects/{project_id}", response_model=ResearchProjectResponse)
async def update_research_project(
    project_id: str,
    updates: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Update a research project (e.g., toggle favorite, update title)."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID")
        
        service = ResearchService(db)
        updated = service.update_project(
            user_id=user_id,
            project_id=project_id,
            **updates
        )
        
        if not updated:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return ResearchProjectResponse.model_validate(updated)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Research Projects] Update failed: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating project: {str(e)}")


@router.delete("/projects/{project_id}", status_code=204)
async def delete_research_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Delete a research project."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID")
        
        service = ResearchService(db)
        deleted = service.delete_project(user_id, project_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Research Projects] Delete failed: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting project: {str(e)}")
