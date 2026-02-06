"""
Platform Insights Monitoring Service
Creates and manages platform insights (GSC/Bing) fetch tasks.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from models.platform_insights_monitoring_models import PlatformInsightsTask
from utils.logging import get_service_logger

logger = get_service_logger("platform_insights_monitoring")


def create_platform_insights_task(
    user_id: str,
    platform: str,  # 'gsc' or 'bing'
    site_url: Optional[str] = None,
    db: Session = None
) -> Dict[str, Any]:
    """
    Create a platform insights fetch task for a user.
    
    This should be called when user connects GSC or Bing in Step 5.
    
    Args:
        user_id: Clerk user ID (string)
        platform: Platform name ('gsc' or 'bing')
        site_url: Optional site URL (for GSC/Bing specific site)
        db: Database session
        
    Returns:
        Dictionary with success status and task details
    """
    try:
        logger.info(
            f"[Platform Insights] Creating {platform} insights task for user: {user_id}"
        )
        
        # Check if task already exists
        existing = db.query(PlatformInsightsTask).filter(
            PlatformInsightsTask.user_id == user_id,
            PlatformInsightsTask.platform == platform
        ).first()
        
        if existing:
            logger.info(
                f"[Platform Insights] Task already exists for user {user_id}, platform {platform}"
            )
            return {
                'success': True,
                'task_id': existing.id,
                'message': 'Task already exists',
                'existing': True
            }
        
        # Calculate next check (7 days from now, weekly schedule)
        next_check = datetime.utcnow() + timedelta(days=7)
        
        # Create new task
        task = PlatformInsightsTask(
            user_id=user_id,
            platform=platform,
            site_url=site_url,
            status='active',
            next_check=next_check,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        logger.info(
            f"[Platform Insights] Created {platform} insights task {task.id} for user {user_id}, "
            f"next_check: {next_check}"
        )
        
        return {
            'success': True,
            'task_id': task.id,
            'platform': platform,
            'next_check': next_check.isoformat(),
            'message': f'{platform.upper()} insights task created successfully'
        }
        
    except Exception as e:
        logger.error(
            f"Error creating {platform} insights task for user {user_id}: {e}",
            exc_info=True
        )
        db.rollback()
        return {
            'success': False,
            'error': str(e)
        }


def get_user_insights_tasks(
    user_id: str,
    platform: Optional[str] = None,
    db: Session = None
) -> List[PlatformInsightsTask]:
    """
    Get all platform insights tasks for a user.
    
    Args:
        user_id: Clerk user ID (string)
        platform: Optional platform filter ('gsc' or 'bing')
        db: Database session
        
    Returns:
        List of PlatformInsightsTask instances
    """
    try:
        query = db.query(PlatformInsightsTask).filter(
            PlatformInsightsTask.user_id == user_id
        )
        
        if platform:
            query = query.filter(PlatformInsightsTask.platform == platform)
        
        tasks = query.all()
        
        logger.debug(
            f"[Platform Insights] Found {len(tasks)} insights tasks for user {user_id}"
        )
        
        return tasks
        
    except Exception as e:
        logger.error(f"Error getting insights tasks for user {user_id}: {e}", exc_info=True)
        return []

