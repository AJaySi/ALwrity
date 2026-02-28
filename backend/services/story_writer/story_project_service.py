"""
Story Project Service

Service layer for managing Story Studio project persistence.
Modeled after PodcastService for a consistent project API.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from models.story_project_models import StoryProject


class StoryProjectService:
    """Service for managing Story Studio projects."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_project(
        self,
        user_id: str,
        project_id: str,
        title: Optional[str] = None,
        story_mode: Optional[str] = None,
        story_template: Optional[str] = None,
        **kwargs: Any,
    ) -> StoryProject:
        project = StoryProject(
            project_id=project_id,
            user_id=user_id,
            title=title,
            story_mode=story_mode,
            story_template=story_template,
            status="draft",
            current_phase="setup",
            **kwargs,
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_project(self, user_id: str, project_id: str) -> Optional[StoryProject]:
        return (
            self.db.query(StoryProject)
            .filter(
                and_(
                    StoryProject.project_id == project_id,
                    StoryProject.user_id == user_id,
                )
            )
            .first()
        )

    def update_project(
        self,
        user_id: str,
        project_id: str,
        **updates: Any,
    ) -> Optional[StoryProject]:
        project = self.get_project(user_id, project_id)
        if not project:
            return None

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
        favorites_only: bool = False,
        limit: int = 50,
        offset: int = 0,
        order_by: str = "updated_at",
    ) -> Tuple[List[StoryProject], int]:
        query = self.db.query(StoryProject).filter(StoryProject.user_id == user_id)

        if status:
            query = query.filter(StoryProject.status == status)

        if favorites_only:
            query = query.filter(StoryProject.is_favorite.is_(True))

        total = query.count()

        if order_by == "created_at":
            query = query.order_by(desc(StoryProject.created_at))
        else:
            query = query.order_by(desc(StoryProject.updated_at))

        projects = query.offset(offset).limit(limit).all()

        return projects, total

    def delete_project(self, user_id: str, project_id: str) -> bool:
        project = self.get_project(user_id, project_id)
        if not project:
            return False

        self.db.delete(project)
        self.db.commit()
        return True

    def toggle_favorite(self, user_id: str, project_id: str) -> Optional[StoryProject]:
        project = self.get_project(user_id, project_id)
        if not project:
            return None

        project.is_favorite = not project.is_favorite
        project.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(project)
        return project

    def update_status(
        self,
        user_id: str,
        project_id: str,
        status: str,
    ) -> Optional[StoryProject]:
        return self.update_project(user_id, project_id, status=status)

