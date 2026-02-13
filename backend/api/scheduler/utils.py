"""Shared utility functions for Scheduler API"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger


def format_job_for_response(job_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a job dictionary for API response.

    Args:
        job_dict: Raw job dictionary from scheduler

    Returns:
        Formatted job dictionary for API response
    """
    try:
        # Extract job information
        job_id = job_dict.get('id', '')
        job_info = job_dict.get('job', {})

        formatted = {
            'id': job_id,
            'name': job_info.get('name', ''),
            'func': job_info.get('func', ''),
            'args': job_info.get('args', []),
            'kwargs': job_info.get('kwargs', {}),
            'trigger': job_dict.get('trigger', ''),
            'trigger_type': job_dict.get('trigger', '').split('.')[0] if '.' in str(job_dict.get('trigger', '')) else job_dict.get('trigger', ''),
            'next_run_time': job_dict.get('next_run_time'),
            'is_paused': job_dict.get('paused', False),
            'is_database_task': job_dict.get('is_database_task', False),
            'task_type': job_dict.get('task_type'),
            'user_id': job_dict.get('user_id'),
            'created_at': job_dict.get('created_at'),
            'updated_at': job_dict.get('updated_at')
        }

        return formatted

    except Exception as e:
        logger.error(f"[Utils] Error formatting job for response: {e}", exc_info=True)
        return {
            'id': job_dict.get('id', 'unknown'),
            'name': 'Error formatting job',
            'func': '',
            'args': [],
            'kwargs': {},
            'trigger': '',
            'trigger_type': '',
            'next_run_time': None,
            'is_paused': False,
            'is_database_task': False,
            'task_type': None,
            'user_id': None,
            'created_at': None,
            'updated_at': None
        }


def calculate_event_log_cleanup_cutoff(days: int) -> datetime:
    """
    Calculate the cutoff timestamp for event log cleanup.

    Args:
        days: Number of days to keep logs

    Returns:
        Datetime representing the cutoff (events older than this should be deleted)
    """
    return datetime.utcnow() - timedelta(days=days)


def validate_task_intervention_eligibility(
    task_status: str,
    failure_count: int,
    last_attempt: Optional[datetime],
    max_retries: int = 3,
    retry_delay_minutes: int = 60
) -> Dict[str, Any]:
    """
    Validate whether a task is eligible for manual intervention/retry.

    Args:
        task_status: Current task status
        failure_count: Number of consecutive failures
        last_attempt: Timestamp of last attempt
        max_retries: Maximum allowed retries
        retry_delay_minutes: Minimum delay between retries

    Returns:
        Dictionary with eligibility status and reason
    """
    try:
        # Check if task is in a failed state that allows intervention
        if task_status not in ['failed', 'error', 'timeout']:
            return {
                'eligible': False,
                'reason': f'Task status "{task_status}" does not allow intervention'
            }

        # Check retry limit
        if failure_count >= max_retries:
            return {
                'eligible': False,
                'reason': f'Task has exceeded maximum retries ({max_retries})'
            }

        # Check retry delay
        if last_attempt:
            time_since_last_attempt = datetime.utcnow() - last_attempt
            min_delay = timedelta(minutes=retry_delay_minutes)

            if time_since_last_attempt < min_delay:
                remaining_delay = min_delay - time_since_last_attempt
                return {
                    'eligible': False,
                    'reason': f'Task must wait {remaining_delay.seconds // 60} more minutes before retry',
                    'retry_available_at': last_attempt + min_delay
                }

        return {
            'eligible': True,
            'reason': 'Task is eligible for intervention'
        }

    except Exception as e:
        logger.error(f"[Utils] Error validating task intervention eligibility: {e}", exc_info=True)
        return {
            'eligible': False,
            'reason': f'Error validating eligibility: {str(e)}'
        }


def extract_user_id_from_current_user(current_user: Dict[str, Any]) -> Optional[str]:
    """
    Extract user ID from current user dictionary with fallbacks.

    Args:
        current_user: Current user dictionary from auth middleware

    Returns:
        User ID string or None if not found
    """
    return (
        current_user.get('sub') or
        current_user.get('user_id') or
        current_user.get('id') or
        current_user.get('clerk_user_id')
    )


def sanitize_task_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize task metadata by removing sensitive information.

    Args:
        metadata: Raw task metadata

    Returns:
        Sanitized metadata dictionary
    """
    try:
        # Create a copy to avoid modifying the original
        sanitized = metadata.copy()

        # Remove sensitive keys
        sensitive_keys = [
            'api_key', 'token', 'password', 'secret', 'key',
            'access_token', 'refresh_token', 'auth_token'
        ]

        for key in sensitive_keys:
            if key in sanitized:
                sanitized[key] = '***REDACTED***'

        # Recursively sanitize nested dictionaries
        for key, value in sanitized.items():
            if isinstance(value, dict):
                sanitized[key] = sanitize_task_metadata(value)

        return sanitized

    except Exception as e:
        logger.error(f"[Utils] Error sanitizing task metadata: {e}", exc_info=True)
        return {'error': 'Failed to sanitize metadata'}