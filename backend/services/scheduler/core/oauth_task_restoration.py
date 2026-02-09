"""
OAuth Token Monitoring Task Restoration
Automatically creates missing OAuth monitoring tasks for users who have connected platforms
but don't have monitoring tasks created yet.
"""

from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from utils.logging import get_service_logger

from services.database import get_platform_db_session
from models.oauth_token_monitoring_models import OAuthTokenMonitoringTask
from services.oauth_token_monitoring_service import get_connected_platforms, create_oauth_monitoring_tasks

# Use service logger for consistent logging (WARNING level visible in production)
logger = get_service_logger("oauth_task_restoration")


async def restore_oauth_monitoring_tasks(scheduler):
    """
    Restore/create missing OAuth token monitoring tasks for all users.
    
    This checks all users who have connected platforms and ensures they have
    monitoring tasks created. Tasks are created for platforms that are:
    - Connected (detected via get_connected_platforms)
    - Missing monitoring tasks (no OAuthTokenMonitoringTask exists)
    
    Args:
        scheduler: TaskScheduler instance
    """
    try:
        logger.warning("[OAuth Task Restoration] Starting OAuth monitoring task restoration...")
        db = get_platform_db_session()
        if not db:
            logger.warning("[OAuth Task Restoration] Could not get platform database session")
            return
        
        try:
            # Get all existing OAuth tasks to find unique user_ids
            existing_tasks = db.query(OAuthTokenMonitoringTask).all()
            user_ids_with_tasks = set(task.user_id for task in existing_tasks)
            
            # Log existing tasks breakdown by platform
            existing_by_platform = {}
            for task in existing_tasks:
                existing_by_platform[task.platform] = existing_by_platform.get(task.platform, 0) + 1
            
            platform_summary = ", ".join([f"{p}: {c}" for p, c in sorted(existing_by_platform.items())])
            logger.warning(
                f"[OAuth Task Restoration] Found {len(existing_tasks)} existing OAuth tasks "
                f"for {len(user_ids_with_tasks)} users. Platforms: {platform_summary}"
            )
            
            # Check users who already have at least one OAuth task
            users_to_check = list(user_ids_with_tasks)
            
            # Also query all users from onboarding who completed step 5 (integrations)
            # to catch users who connected platforms but tasks weren't created
            # Use the same pattern as OnboardingProgressService.get_onboarding_status()
            # Completion is tracked by: current_step >= 6 OR progress >= 100.0
            # This matches the logic used in home page redirect and persona generation checks
            try:
                from services.onboarding.progress_service import get_onboarding_progress_service
                from models.onboarding import OnboardingSession
                from sqlalchemy import or_
                
                # Get onboarding progress service (same as used throughout the app)
                progress_service = get_onboarding_progress_service()
                
                # Query all sessions and filter using the same completion logic as the service
                # This matches the pattern in OnboardingProgressService.get_onboarding_status():
                # is_completed = (session.current_step >= 6) or (session.progress >= 100.0)
                completed_sessions = db.query(OnboardingSession).filter(
                    or_(
                        OnboardingSession.current_step >= 6,
                        OnboardingSession.progress >= 100.0
                    )
                ).all()
                
                # Validate using the service method for consistency
                onboarding_user_ids = set()
                for session in completed_sessions:
                    # Use the same service method as the rest of the app
                    status = progress_service.get_onboarding_status(session.user_id)
                    if status.get('is_completed', False):
                        onboarding_user_ids.add(session.user_id)
                all_user_ids = users_to_check.copy()
                
                # Add users from onboarding who might not have tasks yet
                for user_id in onboarding_user_ids:
                    if user_id not in all_user_ids:
                        all_user_ids.append(user_id)
                
                users_to_check = all_user_ids
                logger.warning(
                    f"[OAuth Task Restoration] Checking {len(users_to_check)} users "
                    f"({len(user_ids_with_tasks)} with existing tasks, "
                    f"{len(onboarding_user_ids)} from onboarding sessions, "
                    f"{len(onboarding_user_ids) - len(user_ids_with_tasks)} new users to check)"
                )
            except Exception as e:
                logger.warning(f"[OAuth Task Restoration] Could not query onboarding users: {e}")
                # Fallback to users with existing tasks only
            
            total_created = 0
            restoration_summary = []  # Collect summary for single log
            
            for user_id in users_to_check:
                try:
                    # Get connected platforms for this user (silent - no logging)
                    connected_platforms = get_connected_platforms(user_id)
                    
                    if not connected_platforms:
                        logger.debug(
                            f"[OAuth Task Restoration] No connected platforms for user {user_id[:20]}..., skipping"
                        )
                        continue
                    
                    # Check which platforms are missing tasks
                    existing_platforms = {
                        task.platform 
                        for task in existing_tasks 
                        if task.user_id == user_id
                    }
                    
                    missing_platforms = [
                        platform 
                        for platform in connected_platforms 
                        if platform not in existing_platforms
                    ]
                    
                    if missing_platforms:
                        # Create missing tasks
                        created = create_oauth_monitoring_tasks(
                            user_id=user_id,
                            db=db,
                            platforms=missing_platforms
                        )
                        
                        total_created += len(created)
                        # Collect summary info instead of logging immediately
                        platforms_str = ", ".join([p.upper() for p in missing_platforms])
                        restoration_summary.append(
                            f"  ├─ User {user_id[:20]}...: {len(created)} tasks ({platforms_str})"
                        )
                        
                except Exception as e:
                    logger.warning(
                        f"[OAuth Task Restoration] Error checking/creating tasks for user {user_id}: {e}",
                        exc_info=True
                    )
                    continue
            
            # Final summary log with platform breakdown
            final_existing_tasks = db.query(OAuthTokenMonitoringTask).all()
            final_by_platform = {}
            for task in final_existing_tasks:
                final_by_platform[task.platform] = final_by_platform.get(task.platform, 0) + 1
            
            final_platform_summary = ", ".join([f"{p}: {c}" for p, c in sorted(final_by_platform.items())])
            
            # Single formatted summary log (similar to scheduler startup)
            if total_created > 0:
                summary_lines = "\n".join(restoration_summary[:5])  # Show first 5 users
                if len(restoration_summary) > 5:
                    summary_lines += f"\n  └─ ... and {len(restoration_summary) - 5} more users"
                
                logger.warning(
                    f"[OAuth Task Restoration] ✅ OAuth Monitoring Tasks Restored\n"
                    f"   ├─ Tasks Created: {total_created}\n"
                    f"   ├─ Users Processed: {len(users_to_check)}\n"
                    f"   ├─ Platform Breakdown: {final_platform_summary}\n"
                    + summary_lines
                )
            else:
                logger.warning(
                    f"[OAuth Task Restoration] ✅ All users have required OAuth monitoring tasks. "
                    f"Checked {len(users_to_check)} users. Platform breakdown: {final_platform_summary}"
                )
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(
            f"[OAuth Task Restoration] Error restoring OAuth monitoring tasks: {e}",
            exc_info=True
        )

