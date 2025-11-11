"""
Website Analysis Task Loader
Functions to load due website analysis tasks from database.
"""

from datetime import datetime
from typing import List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models.website_analysis_monitoring_models import WebsiteAnalysisTask


def load_due_website_analysis_tasks(
    db: Session,
    user_id: Optional[Union[str, int]] = None
) -> List[WebsiteAnalysisTask]:
    """
    Load all website analysis tasks that are due for execution.
    
    Criteria:
    - status == 'active' (only check active tasks)
    - next_check <= now (or is None for first execution)
    - Optional: user_id filter for specific user (for user isolation)
    
    User isolation is enforced through filtering by user_id when provided.
    If no user_id is provided, loads tasks for all users (for system-wide monitoring).
    
    Args:
        db: Database session
        user_id: Optional user ID (Clerk string) to filter tasks (if None, loads all users' tasks)
        
    Returns:
        List of due WebsiteAnalysisTask instances
    """
    now = datetime.utcnow()
    
    # Build query for due tasks
    query = db.query(WebsiteAnalysisTask).filter(
        and_(
            WebsiteAnalysisTask.status == 'active',
            or_(
                WebsiteAnalysisTask.next_check <= now,
                WebsiteAnalysisTask.next_check.is_(None)
            )
        )
    )
    
    # Apply user filter if provided (for user isolation)
    if user_id is not None:
        query = query.filter(WebsiteAnalysisTask.user_id == str(user_id))
    
    return query.all()

