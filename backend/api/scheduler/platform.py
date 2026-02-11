"""Platform Monitoring Router for Scheduler API"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from loguru import logger

# Import models and utilities
from .models.platform_insights import PlatformInsightsStatusResponse
from .models.website_analysis import WebsiteAnalysisStatusResponse
from .utils import extract_user_id_from_current_user
from .validators import validate_user_access

# Import existing services and models
from services.database import get_db
from middleware.auth_middleware import get_current_user
from models.platform_insights_monitoring_models import PlatformInsightsTask
from models.website_analysis_monitoring_models import WebsiteAnalysisTask

router = APIRouter(prefix="/api/scheduler", tags=["scheduler-platform"])


@router.get("/platform-insights/status/{user_id}", response_model=PlatformInsightsStatusResponse)
async def get_platform_insights_status(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get platform insights task status for a user.

    Returns:
        - GSC insights tasks (Google Search Console)
        - Bing insights tasks
        - Task details including execution status, schedules, and history
        - Read-only task status (no implicit task creation)
    """
    try:
        # Verify user access - users can only see their own platform insights
        validated_user_id = validate_user_access(user_id, current_user, require_ownership=True)

        logger.debug(f"[Platform Insights Status] Getting status for user: {validated_user_id}")

        # Get all insights tasks for user
        tasks = db.query(PlatformInsightsTask).filter(
            PlatformInsightsTask.user_id == validated_user_id
        ).order_by(PlatformInsightsTask.platform, PlatformInsightsTask.created_at).all()

        # P2.B operational semantics: this GET endpoint is strictly read-only.
        # Missing connected-platform tasks are handled via explicit POST reconcile endpoint.

        # Group tasks by platform
        gsc_tasks = [t for t in tasks if t.platform == 'gsc']
        bing_tasks = [t for t in tasks if t.platform == 'bing']

        logger.debug(
            f"[Platform Insights Status] Found {len(tasks)} total tasks: "
            f"{len(gsc_tasks)} GSC, {len(bing_tasks)} Bing"
        )

        # Format tasks for response
        def format_task(task: PlatformInsightsTask) -> Dict[str, Any]:
            return {
                'id': task.id,
                'platform': task.platform,
                'site_url': task.site_url,
                'status': task.status,
                'last_check': task.last_check.isoformat() if task.last_check else None,
                'last_success': task.last_success.isoformat() if task.last_success else None,
                'last_failure': task.last_failure.isoformat() if task.last_failure else None,
                'failure_reason': task.failure_reason,
                'next_check': task.next_check.isoformat() if task.next_check else None,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'updated_at': task.updated_at.isoformat() if task.updated_at else None,
                'metadata': task.metadata or {}
            }

        formatted_gsc_tasks = [format_task(t) for t in gsc_tasks]
        formatted_bing_tasks = [format_task(t) for t in bing_tasks]

        # Calculate summary statistics
        total_tasks = len(tasks)
        active_tasks = len([t for t in tasks if t.status == 'active'])
        paused_tasks = len([t for t in tasks if t.status == 'paused'])
        failed_tasks = len([t for t in tasks if t.status == 'failed'])

        return PlatformInsightsStatusResponse(
            tasks=formatted_gsc_tasks + formatted_bing_tasks,
            total_tasks=total_tasks,
            active_tasks=active_tasks,
            paused_tasks=paused_tasks,
            failed_tasks=failed_tasks,
            last_updated=datetime.utcnow()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Platform Insights Status] Error getting status for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get platform insights status: {str(e)}")


@router.post("/platform-insights/reconcile/{user_id}")
async def reconcile_platform_insights_status(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Explicitly reconcile missing platform insights tasks for connected platforms."""
    try:
        validated_user_id = validate_user_access(user_id, current_user, require_ownership=True)

        from services.oauth_token_monitoring_service import get_connected_platforms
        from services.platform_insights_monitoring_service import create_platform_insights_task

        connected_platforms = get_connected_platforms(validated_user_id)
        insights_platforms = {'gsc', 'bing'}
        connected_insights = [p for p in connected_platforms if p in insights_platforms]

        existing_tasks = db.query(PlatformInsightsTask).filter(
            PlatformInsightsTask.user_id == validated_user_id,
            PlatformInsightsTask.platform.in_(connected_insights)
        ).all()
        existing_platforms = {task.platform for task in existing_tasks}
        missing_platforms = [p for p in connected_insights if p not in existing_platforms]

        created_platforms: List[str] = []
        skipped_platforms: List[str] = []
        failures: List[Dict[str, str]] = []

        for platform in missing_platforms:
            # Re-check inside the loop for best-effort race safety before calling creator
            exists_now = db.query(PlatformInsightsTask).filter(
                PlatformInsightsTask.user_id == validated_user_id,
                PlatformInsightsTask.platform == platform
            ).first()
            if exists_now:
                skipped_platforms.append(platform)
                continue

            result = create_platform_insights_task(
                user_id=validated_user_id,
                platform=platform,
                site_url=None,
                db=db,
            )

            if result.get('success'):
                if result.get('existing'):
                    skipped_platforms.append(platform)
                else:
                    created_platforms.append(platform)
            else:
                failures.append({'platform': platform, 'error': result.get('error', 'unknown_error')})

        logger.info(
            f"[Platform Insights Reconcile] user={validated_user_id} "
            f"created={created_platforms} skipped={skipped_platforms} failures={len(failures)}"
        )

        return {
            'success': len(failures) == 0,
            'user_id': validated_user_id,
            'connected_insights_platforms': connected_insights,
            'created_platforms': created_platforms,
            'skipped_platforms': skipped_platforms,
            'failures': failures,
            'auditable': True,
            'reconciled_at': datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Platform Insights Reconcile] Error reconciling user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to reconcile platform insights tasks: {str(e)}")


@router.get("/website-analysis/status/{user_id}", response_model=WebsiteAnalysisStatusResponse)
async def get_website_analysis_status(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get website analysis task status for a user.

    Returns:
        - User website analysis tasks
        - Competitor website analysis tasks
        - Task details including execution status, schedules, and history
    """
    try:
        # Verify user access - users can only see their own website analysis
        validated_user_id = validate_user_access(user_id, current_user, require_ownership=True)

        logger.debug(f"[Website Analysis Status] Getting status for user: {validated_user_id}")

        # Get all website analysis tasks for user
        tasks = db.query(WebsiteAnalysisTask).filter(
            WebsiteAnalysisTask.user_id == validated_user_id
        ).order_by(WebsiteAnalysisTask.task_type, WebsiteAnalysisTask.created_at).all()

        # Separate user website and competitor tasks
        user_website_tasks = [t for t in tasks if t.task_type == 'user_website']
        competitor_tasks = [t for t in tasks if t.task_type == 'competitor']

        logger.debug(
            f"[Website Analysis Status] Found {len(tasks)} tasks for user {validated_user_id}: "
            f"{len(user_website_tasks)} user website, {len(competitor_tasks)} competitors"
        )

        # Format tasks for response
        def format_task(task: WebsiteAnalysisTask) -> Dict[str, Any]:
            return {
                'id': task.id,
                'website_url': task.website_url,
                'task_type': task.task_type,
                'competitor_id': task.competitor_id,
                'status': task.status,
                'last_check': task.last_check.isoformat() if task.last_check else None,
                'last_success': task.last_success.isoformat() if task.last_success else None,
                'last_failure': task.last_failure.isoformat() if task.last_failure else None,
                'failure_reason': task.failure_reason,
                'next_check': task.next_check.isoformat() if task.next_check else None,
                'frequency_days': task.frequency_days,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'updated_at': task.updated_at.isoformat() if task.updated_at else None,
                'metadata': task.metadata or {}
            }

        formatted_user_website_tasks = [format_task(t) for t in user_website_tasks]
        formatted_competitor_tasks = [format_task(t) for t in competitor_tasks]

        # Calculate summary statistics
        total_tasks = len(tasks)
        active_tasks = len([t for t in tasks if t.status == 'active'])
        paused_tasks = len([t for t in tasks if t.status == 'paused'])
        failed_tasks = len([t for t in tasks if t.status == 'failed'])

        return WebsiteAnalysisStatusResponse(
            tasks=formatted_user_website_tasks + formatted_competitor_tasks,
            total_tasks=total_tasks,
            active_tasks=active_tasks,
            paused_tasks=paused_tasks,
            failed_tasks=failed_tasks,
            last_updated=datetime.utcnow()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Website Analysis Status] Error getting status for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get website analysis status: {str(e)}")


@router.get("/platform-monitoring/summary/{user_id}")
async def get_platform_monitoring_summary(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a comprehensive summary of all platform monitoring for a user.

    This provides an overview of both platform insights and website analysis tasks,
    useful for dashboard widgets and monitoring alerts.

    Args:
        user_id: User ID

    Returns:
        Combined summary of platform insights and website analysis monitoring
    """
    try:
        # Verify user access
        validated_user_id = validate_user_access(user_id, current_user, require_ownership=True)

        # Get platform insights summary
        insights_tasks = db.query(PlatformInsightsTask).filter(
            PlatformInsightsTask.user_id == validated_user_id
        ).all()

        # Get website analysis summary
        website_tasks = db.query(WebsiteAnalysisTask).filter(
            WebsiteAnalysisTask.user_id == validated_user_id
        ).all()

        # Calculate insights statistics
        insights_stats = {
            'total': len(insights_tasks),
            'active': len([t for t in insights_tasks if t.status == 'active']),
            'failed': len([t for t in insights_tasks if t.status == 'failed']),
            'platforms': list(set(t.platform for t in insights_tasks))
        }

        # Calculate website analysis statistics
        website_stats = {
            'total': len(website_tasks),
            'active': len([t for t in website_tasks if t.status == 'active']),
            'failed': len([t for t in website_tasks if t.status == 'failed']),
            'user_websites': len([t for t in website_tasks if t.task_type == 'user_website']),
            'competitors': len([t for t in website_tasks if t.task_type == 'competitor'])
        }

        # Overall health score (percentage of active tasks)
        total_tasks = insights_stats['total'] + website_stats['total']
        active_tasks = insights_stats['active'] + website_stats['active']

        health_score = (active_tasks / total_tasks * 100) if total_tasks > 0 else 100

        # Recent activity (last 24 hours)
        from datetime import datetime, timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)

        recent_insights = len([t for t in insights_tasks if t.last_check and t.last_check > yesterday])
        recent_website = len([t for t in website_tasks if t.last_check and t.last_check > yesterday])

        return {
            'user_id': validated_user_id,
            'platform_insights': insights_stats,
            'website_analysis': website_stats,
            'overall': {
                'total_tasks': total_tasks,
                'active_tasks': active_tasks,
                'failed_tasks': insights_stats['failed'] + website_stats['failed'],
                'health_score': round(health_score, 1),
                'recent_activity_24h': recent_insights + recent_website
            },
            'last_updated': datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Platform Monitoring Summary] Error getting summary for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get platform monitoring summary: {str(e)}")


@router.get("/platform-monitoring/health/{user_id}")
async def get_platform_monitoring_health(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get platform monitoring health status for a user.

    This endpoint provides a quick health check for monitoring systems,
    useful for status indicators and health monitoring.

    Args:
        user_id: User ID

    Returns:
        Health status of platform monitoring systems
    """
    try:
        # Verify user access
        validated_user_id = validate_user_access(user_id, current_user, require_ownership=True)

        # Quick health checks
        insights_count = db.query(PlatformInsightsTask).filter(
            PlatformInsightsTask.user_id == validated_user_id
        ).count()

        website_count = db.query(WebsiteAnalysisTask).filter(
            WebsiteAnalysisTask.user_id == validated_user_id
        ).count()

        # Check for any recent failures
        from datetime import datetime, timedelta
        last_hour = datetime.utcnow() - timedelta(hours=1)

        recent_insights_failures = db.query(PlatformInsightsTask).filter(
            PlatformInsightsTask.user_id == validated_user_id,
            PlatformInsightsTask.last_failure.isnot(None),
            PlatformInsightsTask.last_failure > last_hour
        ).count()

        recent_website_failures = db.query(WebsiteAnalysisTask).filter(
            WebsiteAnalysisTask.user_id == validated_user_id,
            WebsiteAnalysisTask.last_failure.isnot(None),
            WebsiteAnalysisTask.last_failure > last_hour
        ).count()

        # Determine overall health
        total_tasks = insights_count + website_count
        recent_failures = recent_insights_failures + recent_website_failures

        if total_tasks == 0:
            health_status = 'not_configured'
            health_message = 'No monitoring tasks configured'
        elif recent_failures > 0:
            health_status = 'degraded'
            health_message = f'{recent_failures} recent failures in the last hour'
        elif total_tasks > 0:
            health_status = 'healthy'
            health_message = f'All {total_tasks} monitoring tasks operational'
        else:
            health_status = 'unknown'
            health_message = 'Unable to determine health status'

        return {
            'user_id': validated_user_id,
            'health_status': health_status,
            'health_message': health_message,
            'monitoring_stats': {
                'platform_insights_tasks': insights_count,
                'website_analysis_tasks': website_count,
                'total_tasks': total_tasks,
                'recent_failures': recent_failures
            },
            'last_checked': datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Platform Monitoring Health] Error checking health for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get platform monitoring health: {str(e)}")