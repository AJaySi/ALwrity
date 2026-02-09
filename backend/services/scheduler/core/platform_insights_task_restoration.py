"""
Platform Insights Task Restoration
Automatically creates missing platform insights tasks for users who have connected platforms
but don't have insights tasks created yet.
"""

from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from utils.logging import get_service_logger

from services.database import get_db_session
from models.platform_insights_monitoring_models import PlatformInsightsTask
from services.platform_insights_monitoring_service import create_platform_insights_task
from services.oauth_token_monitoring_service import get_connected_platforms
from models.oauth_token_monitoring_models import OAuthTokenMonitoringTask

logger = get_service_logger("platform_insights_task_restoration")


async def restore_platform_insights_tasks(scheduler):
    """
    Restore/create missing platform insights tasks for all users.
    
    This checks all users who have connected platforms (GSC/Bing) and ensures they have
    insights tasks created. Tasks are created for platforms that are:
    - Connected (detected via get_connected_platforms or OAuth tasks)
    - Missing insights tasks (no PlatformInsightsTask exists)
    
    Args:
        scheduler: TaskScheduler instance
    """
    try:
        logger.warning("[Platform Insights Restoration] Starting platform insights task restoration...")
        db = get_db_session()
        if not db:
            logger.warning("[Platform Insights Restoration] Could not get database session")
            return
        
        try:
            # Get all existing insights tasks to find unique user_ids
            existing_tasks = db.query(PlatformInsightsTask).all()
            user_ids_with_tasks = set(task.user_id for task in existing_tasks)
            
            # Get all OAuth tasks to find users with connected platforms
            oauth_tasks = db.query(OAuthTokenMonitoringTask).all()
            user_ids_with_oauth = set(task.user_id for task in oauth_tasks)
            
            # Platforms that support insights (GSC and Bing only)
            insights_platforms = ['gsc', 'bing']
            
            # Get users who have OAuth tasks for GSC or Bing
            users_to_check = set()
            for task in oauth_tasks:
                if task.platform in insights_platforms:
                    users_to_check.add(task.user_id)
            
            logger.warning(
                f"[Platform Insights Restoration] Found {len(existing_tasks)} existing insights tasks "
                f"for {len(user_ids_with_tasks)} users. Checking {len(users_to_check)} users "
                f"with GSC/Bing OAuth connections."
            )
            
            if not users_to_check:
                logger.warning("[Platform Insights Restoration] No users with GSC/Bing connections found")
                return
            
            total_created = 0
            restoration_summary = []
            
            for user_id in users_to_check:
                try:
                    # Get connected platforms for this user
                    connected_platforms = get_connected_platforms(user_id)
                    
                    # Filter to only GSC and Bing
                    insights_connected = [p for p in connected_platforms if p in insights_platforms]
                    
                    if not insights_connected:
                        logger.debug(
                            f"[Platform Insights Restoration] No GSC/Bing connections for user {user_id[:20]}..., skipping"
                        )
                        continue
                    
                    # Check which platforms are missing insights tasks
                    existing_platforms = {
                        task.platform 
                        for task in existing_tasks 
                        if task.user_id == user_id
                    }
                    
                    missing_platforms = [
                        platform 
                        for platform in insights_connected 
                        if platform not in existing_platforms
                    ]
                    
                    if missing_platforms:
                        # Create missing tasks for each platform
                        for platform in missing_platforms:
                            try:
                                # Don't fetch site_url here - it requires API calls
                                # The executor will fetch it when the task runs (weekly)
                                # This avoids API calls during restoration
                                result = create_platform_insights_task(
                                    user_id=user_id,
                                    platform=platform,
                                    site_url=None,  # Will be fetched by executor when task runs
                                    db=db
                                )
                                
                                if result.get('success'):
                                    total_created += 1
                                    restoration_summary.append(
                                        f"  ├─ User {user_id[:20]}...: {platform.upper()} task created"
                                    )
                                else:
                                    logger.debug(
                                        f"[Platform Insights Restoration] Failed to create {platform} task "
                                        f"for user {user_id}: {result.get('error')}"
                                    )
                            except Exception as e:
                                logger.debug(
                                    f"[Platform Insights Restoration] Error creating {platform} task "
                                    f"for user {user_id}: {e}"
                                )
                                continue
                    
                except Exception as e:
                    logger.debug(
                        f"[Platform Insights Restoration] Error processing user {user_id}: {e}"
                    )
                    continue
            
            # Log summary
            if total_created > 0:
                logger.warning(
                    f"[Platform Insights Restoration] ✅ Created {total_created} platform insights tasks:\n" +
                    "\n".join(restoration_summary)
                )
            else:
                logger.warning(
                    f"[Platform Insights Restoration] ✅ All users have required platform insights tasks. "
                    f"Checked {len(users_to_check)} users, found {len(existing_tasks)} existing tasks."
                )
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"[Platform Insights Restoration] Error during restoration: {e}", exc_info=True)

