"""
Facebook Persona Scheduler
Handles scheduled generation of Facebook personas after onboarding.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from loguru import logger

from services.database import get_db_session
from services.persona_data_service import PersonaDataService
from services.persona.facebook.facebook_persona_service import FacebookPersonaService
from services.onboarding.database_service import OnboardingDatabaseService
from models.scheduler_models import SchedulerEventLog


async def generate_facebook_persona_task(user_id: str):
    """
    Async task function to generate Facebook persona for a user.
    
    This function is called by the scheduler 20 minutes after onboarding completion.
    
    Args:
        user_id: User ID (Clerk string)
    """
    db = None
    try:
        logger.info(f"Scheduled Facebook persona generation started for user {user_id}")
        
        db = get_db_session()
        if not db:
            logger.error(f"Failed to get database session for Facebook persona generation (user: {user_id})")
            return
        
        # Get persona data service
        persona_data_service = PersonaDataService(db_session=db)
        onboarding_service = OnboardingDatabaseService(db=db)
        
        # Get core persona (required for Facebook persona)
        persona_data = persona_data_service.get_user_persona_data(user_id)
        if not persona_data or not persona_data.get('core_persona'):
            logger.warning(f"No core persona found for user {user_id}, cannot generate Facebook persona")
            return
        
        core_persona = persona_data.get('core_persona', {})
        
        # Get onboarding data for context
        website_analysis = onboarding_service.get_website_analysis(user_id, db)
        research_prefs = onboarding_service.get_research_preferences(user_id, db)
        
        onboarding_data = {
            "website_url": website_analysis.get('website_url', '') if website_analysis else '',
            "writing_style": website_analysis.get('writing_style', {}) if website_analysis else {},
            "content_characteristics": website_analysis.get('content_characteristics', {}) if website_analysis else {},
            "target_audience": website_analysis.get('target_audience', '') if website_analysis else '',
            "research_preferences": research_prefs or {}
        }
        
        # Check if persona already exists to avoid unnecessary API calls
        platform_personas = persona_data.get('platform_personas', {}) if persona_data else {}
        if platform_personas.get('facebook'):
            logger.info(f"Facebook persona already exists for user {user_id}, skipping generation")
            return
        
        start_time = datetime.utcnow()
        # Generate Facebook persona
        facebook_service = FacebookPersonaService()
        try:
            generated_persona = facebook_service.generate_facebook_persona(
                core_persona, 
                onboarding_data
            )
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            if generated_persona and "error" not in generated_persona:
                # Save to database
                success = persona_data_service.save_platform_persona(user_id, 'facebook', generated_persona)
                if success:
                    logger.info(f"✅ Scheduled Facebook persona generation completed for user {user_id}")
                    
                    # Log success to scheduler event log for dashboard
                    try:
                        event_log = SchedulerEventLog(
                            event_type='job_completed',
                            event_date=start_time,
                            job_id=f"facebook_persona_{user_id}",
                            job_type='one_time',
                            user_id=user_id,
                            event_data={
                                'job_function': 'generate_facebook_persona_task',
                                'execution_time_seconds': execution_time,
                                'status': 'success'
                            }
                        )
                        db.add(event_log)
                        db.commit()
                    except Exception as log_error:
                        logger.warning(f"Failed to log Facebook persona generation success to scheduler event log: {log_error}")
                        if db:
                            db.rollback()
                else:
                    error_msg = f"Failed to save Facebook persona for user {user_id}"
                    logger.warning(f"⚠️ {error_msg}")
                    
                    # Log failure to scheduler event log
                    try:
                        event_log = SchedulerEventLog(
                            event_type='job_failed',
                            event_date=start_time,
                            job_id=f"facebook_persona_{user_id}",
                            job_type='one_time',
                            user_id=user_id,
                            error_message=error_msg,
                            event_data={
                                'job_function': 'generate_facebook_persona_task',
                                'execution_time_seconds': execution_time,
                                'status': 'failed',
                                'failure_reason': 'save_failed',
                                'expensive_api_call': True
                            }
                        )
                        db.add(event_log)
                        db.commit()
                    except Exception as log_error:
                        logger.warning(f"Failed to log Facebook persona save failure to scheduler event log: {log_error}")
                        if db:
                            db.rollback()
            else:
                error_msg = f"Scheduled Facebook persona generation failed for user {user_id}: {generated_persona}"
                logger.error(f"❌ {error_msg}")
                
                # Log failure to scheduler event log for dashboard visibility
                try:
                    event_log = SchedulerEventLog(
                        event_type='job_failed',
                        event_date=start_time,
                        job_id=f"facebook_persona_{user_id}",  # Match scheduled job ID format
                        job_type='one_time',
                        user_id=user_id,
                        error_message=error_msg,
                        event_data={
                            'job_function': 'generate_facebook_persona_task',
                            'execution_time_seconds': execution_time,
                            'status': 'failed',
                            'failure_reason': 'generation_returned_error',
                            'expensive_api_call': True
                        }
                    )
                    db.add(event_log)
                    db.commit()
                except Exception as log_error:
                    logger.warning(f"Failed to log Facebook persona generation failure to scheduler event log: {log_error}")
                    if db:
                        db.rollback()
        except Exception as gen_error:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = f"Exception during scheduled Facebook persona generation for user {user_id}: {str(gen_error)}. Expensive API call may have been made."
            logger.error(f"❌ {error_msg}")
            
            # Log exception to scheduler event log for dashboard visibility
            try:
                event_log = SchedulerEventLog(
                    event_type='job_failed',
                    event_date=start_time,
                    job_id=f"facebook_persona_{user_id}",  # Match scheduled job ID format
                    job_type='one_time',
                    user_id=user_id,
                    error_message=error_msg,
                    event_data={
                        'job_function': 'generate_facebook_persona_task',
                        'execution_time_seconds': execution_time,
                        'status': 'failed',
                        'failure_reason': 'exception',
                        'exception_type': type(gen_error).__name__,
                        'exception_message': str(gen_error),
                        'expensive_api_call': True
                    }
                )
                db.add(event_log)
                db.commit()
            except Exception as log_error:
                logger.warning(f"Failed to log Facebook persona generation exception to scheduler event log: {log_error}")
                if db:
                    db.rollback()
            
    except Exception as e:
        logger.error(f"Error in scheduled Facebook persona generation for user {user_id}: {e}")
    finally:
        if db:
            try:
                db.close()
            except Exception as e:
                logger.error(f"Error closing database session: {e}")


def schedule_facebook_persona_generation(user_id: str, delay_minutes: int = 20) -> str:
    """
    Schedule Facebook persona generation for a user after a delay.
    
    Args:
        user_id: User ID (Clerk string)
        delay_minutes: Delay in minutes before generating persona (default: 20)
        
    Returns:
        Job ID
    """
    try:
        from services.scheduler import get_scheduler
        
        scheduler = get_scheduler()
        
        # Calculate run date (current time + delay) - ensure UTC timezone-aware
        run_date = datetime.now(timezone.utc) + timedelta(minutes=delay_minutes)
        
        # Generate consistent job ID (without timestamp) for proper restoration
        # This allows restoration to find and restore the job with original scheduled time
        # Note: Clerk user_id already includes "user_" prefix, so we don't add it again
        job_id = f"facebook_persona_{user_id}"
        
        # Schedule the task
        scheduled_job_id = scheduler.schedule_one_time_task(
            func=generate_facebook_persona_task,
            run_date=run_date,
            job_id=job_id,
            kwargs={"user_id": user_id},
            replace_existing=True
        )
        
        logger.info(
            f"Scheduled Facebook persona generation for user {user_id} "
            f"at {run_date} (job_id: {scheduled_job_id})"
        )
        
        return scheduled_job_id
        
    except Exception as e:
        logger.error(f"Failed to schedule Facebook persona generation for user {user_id}: {e}")
        raise

