"""
Website Analysis Task Restoration
Automatically creates missing website analysis tasks for users who completed onboarding
but don't have monitoring tasks created yet.
"""

from typing import List
from sqlalchemy.orm import Session
from utils.logging import get_service_logger

from services.database import get_platform_db_session
from models.website_analysis_monitoring_models import WebsiteAnalysisTask
from services.website_analysis_monitoring_service import create_website_analysis_tasks
from models.onboarding import OnboardingSession
from sqlalchemy import or_

# Use service logger for consistent logging (WARNING level visible in production)
logger = get_service_logger("website_analysis_restoration")


async def restore_website_analysis_tasks(scheduler):
    """
    Restore/create missing website analysis tasks for all users.
    
    This checks all users who completed onboarding and ensures they have
    website analysis tasks created. Tasks are created for:
    - User's website (if analysis exists)
    - All competitors (from onboarding step 3)
    
    Args:
        scheduler: TaskScheduler instance
    """
    try:
        logger.warning("[Website Analysis Restoration] Starting website analysis task restoration...")
        db = get_platform_db_session()
        if not db:
            logger.warning("[Website Analysis Restoration] Could not get platform database session")
            return
        
        try:
            # Check if table exists (may not exist if migration hasn't run)
            try:
                existing_tasks = db.query(WebsiteAnalysisTask).all()
            except Exception as table_error:
                logger.error(
                    f"[Website Analysis Restoration] ⚠️ WebsiteAnalysisTask table may not exist: {table_error}. "
                    f"Please run database migration: create_website_analysis_monitoring_tables.sql"
                )
                return
            
            user_ids_with_tasks = set(task.user_id for task in existing_tasks)
            
            # Log existing tasks breakdown by type
            existing_by_type = {}
            for task in existing_tasks:
                existing_by_type[task.task_type] = existing_by_type.get(task.task_type, 0) + 1
            
            type_summary = ", ".join([f"{t}: {c}" for t, c in sorted(existing_by_type.items())])
            logger.warning(
                f"[Website Analysis Restoration] Found {len(existing_tasks)} existing website analysis tasks "
                f"for {len(user_ids_with_tasks)} users. Types: {type_summary}"
            )
            
            # Check users who already have at least one website analysis task
            users_to_check = list(user_ids_with_tasks)
            
            # Also query all users from onboarding who completed step 2 (website analysis)
            # to catch users who completed onboarding but tasks weren't created
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
                    f"[Website Analysis Restoration] Checking {len(users_to_check)} users "
                    f"({len(user_ids_with_tasks)} with existing tasks, "
                    f"{len(onboarding_user_ids)} from onboarding sessions, "
                    f"{len(onboarding_user_ids) - len(user_ids_with_tasks)} new users to check)"
                )
            except Exception as e:
                logger.warning(f"[Website Analysis Restoration] Could not query onboarding users: {e}")
                # Fallback to users with existing tasks only
                users_to_check = list(user_ids_with_tasks)
            
            total_created = 0
            users_processed = 0
            
            for user_id in users_to_check:
                try:
                    users_processed += 1
                    
                    # Check if user already has tasks
                    existing_user_tasks = [
                        task for task in existing_tasks 
                        if task.user_id == user_id
                    ]
                    
                    if existing_user_tasks:
                        logger.debug(
                            f"[Website Analysis Restoration] User {user_id} already has "
                            f"{len(existing_user_tasks)} website analysis tasks, skipping"
                        )
                        continue
                    
                    logger.warning(
                        f"[Website Analysis Restoration] ⚠️ User {user_id} completed onboarding "
                        f"but has no website analysis tasks. Creating tasks..."
                    )
                    
                    # Create missing tasks
                    result = create_website_analysis_tasks(user_id=user_id, db=db)
                    
                    if result.get('success'):
                        tasks_count = result.get('tasks_created', 0)
                        total_created += tasks_count
                        logger.warning(
                            f"[Website Analysis Restoration] ✅ Created {tasks_count} website analysis tasks "
                            f"for user {user_id}"
                        )
                    else:
                        error = result.get('error', 'Unknown error')
                        logger.warning(
                            f"[Website Analysis Restoration] ⚠️ Could not create tasks for user {user_id}: {error}"
                        )
                        
                except Exception as e:
                    logger.warning(
                        f"[Website Analysis Restoration] Error checking/creating tasks for user {user_id}: {e}",
                        exc_info=True
                    )
                    continue
            
            # Final summary log
            final_existing_tasks = db.query(WebsiteAnalysisTask).all()
            final_by_type = {}
            for task in final_existing_tasks:
                final_by_type[task.task_type] = final_by_type.get(task.task_type, 0) + 1
            
            final_type_summary = ", ".join([f"{t}: {c}" for t, c in sorted(final_by_type.items())])
            
            if total_created > 0:
                logger.warning(
                    f"[Website Analysis Restoration] ✅ Created {total_created} missing website analysis tasks. "
                    f"Processed {users_processed} users. Final type breakdown: {final_type_summary}"
                )
            else:
                logger.warning(
                    f"[Website Analysis Restoration] ✅ All users have required website analysis tasks. "
                    f"Checked {users_processed} users, found {len(existing_tasks)} existing tasks. "
                    f"Type breakdown: {final_type_summary}"
                )
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(
            f"[Website Analysis Restoration] Error restoring website analysis tasks: {e}",
            exc_info=True
        )

