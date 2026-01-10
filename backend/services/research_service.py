"""
Research Service

Service layer for managing research project persistence.
Similar to PodcastService, but for research projects.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from models.research_models import ResearchProject


class ResearchService:
    """Service for managing research projects."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_project(
        self,
        user_id: str,
        project_id: str,
        keywords: List[str],
        industry: Optional[str] = None,
        target_audience: Optional[str] = None,
        research_mode: Optional[str] = "comprehensive",
        **kwargs
    ) -> ResearchProject:
        """Create a new research project."""
        # Extract current_step and status from kwargs to avoid conflicts
        current_step = kwargs.pop("current_step", 1)
        status = kwargs.pop("status", "draft")
        
        project = ResearchProject(
            project_id=project_id,
            user_id=user_id,
            keywords=keywords,
            industry=industry,
            target_audience=target_audience,
            research_mode=research_mode,
            status=status,
            current_step=current_step,
            **kwargs
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def get_project(self, user_id: str, project_id: str) -> Optional[ResearchProject]:
        """Get a project by ID, ensuring user ownership."""
        return self.db.query(ResearchProject).filter(
            and_(
                ResearchProject.project_id == project_id,
                ResearchProject.user_id == user_id
            )
        ).first()
    
    def update_project(
        self,
        user_id: str,
        project_id: str,
        **updates
    ) -> Optional[ResearchProject]:
        """Update a project's state."""
        project = self.get_project(user_id, project_id)
        if not project:
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        project.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def list_projects(
        self,
        user_id: str,
        status: Optional[str] = None,
        is_favorite: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ResearchProject]:
        """List projects for a user."""
        query = self.db.query(ResearchProject).filter(
            ResearchProject.user_id == user_id
        )
        
        if status:
            query = query.filter(ResearchProject.status == status)
        
        if is_favorite is not None:
            query = query.filter(ResearchProject.is_favorite == is_favorite)
        
        return query.order_by(desc(ResearchProject.updated_at)).offset(offset).limit(limit).all()
    
    def delete_project(self, user_id: str, project_id: str) -> bool:
        """Delete a project."""
        project = self.get_project(user_id, project_id)
        if not project:
            return False
        
        self.db.delete(project)
        self.db.commit()
        return True
