"""
GSC Insights Task Executor
Handles execution of GSC insights fetch tasks for connected platforms.
"""

import logging
import os
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session
import sqlite3

from ..core.executor_interface import TaskExecutor, TaskExecutionResult
from ..core.exception_handler import TaskExecutionError, DatabaseError, SchedulerExceptionHandler
from models.platform_insights_monitoring_models import (
    PlatformInsightsTask,
    PlatformInsightsExecutionLog,
    PlatformInsightDeltaEvent,
)
from services.gsc_service import GSCService
from utils.logger_utils import get_service_logger

logger = get_service_logger("gsc_insights_executor")


class GSCInsightsExecutor(TaskExecutor):
    """
    Executor for GSC insights fetch tasks.
    
    Handles:
    - Fetching GSC insights data weekly
    - On first run: Loads existing cached data
    - On subsequent runs: Fetches fresh data from GSC API
    - Logging results and updating task status
    """
    
    def __init__(self):
        self.logger = logger
        self.exception_handler = SchedulerExceptionHandler()
        self.gsc_service = GSCService()
    
    async def execute_task(self, task: PlatformInsightsTask, db: Session) -> TaskExecutionResult:
        """
        Execute a GSC insights fetch task.
        
        Args:
            task: PlatformInsightsTask instance
            db: Database session
            
        Returns:
            TaskExecutionResult
        """
        start_time = time.time()
        user_id = task.user_id
        site_url = task.site_url
        
        try:
            self.logger.info(
                f"Executing GSC insights fetch: task_id={task.id} | "
                f"user_id={user_id} | site_url={site_url}"
            )
            
            # Create execution log
            execution_log = PlatformInsightsExecutionLog(
                task_id=task.id,
                execution_date=datetime.utcnow(),
                status='running'
            )
            db.add(execution_log)
            db.flush()
            
            # Fetch insights
            result = await self._fetch_insights(task, db)
            
            # Update execution log
            execution_time_ms = int((time.time() - start_time) * 1000)
            execution_log.status = 'success' if result.success else 'failed'
            execution_log.result_data = result.result_data
            execution_log.error_message = result.error_message
            execution_log.execution_time_ms = execution_time_ms
            execution_log.data_source = result.result_data.get('data_source') if result.success else None
            
            # Update task based on result
            task.last_check = datetime.utcnow()
            
            if result.success:
                task.last_success = datetime.utcnow()
                task.status = 'active'
                task.failure_reason = None
                # Reset failure tracking on success
                task.consecutive_failures = 0
                task.failure_pattern = None
                # Schedule next check (7 days from now)
                task.next_check = self.calculate_next_execution(
                    task=task,
                    frequency='Weekly',
                    last_execution=task.last_check
                )
            else:
                # Analyze failure pattern
                from services.scheduler.core.failure_detection_service import FailureDetectionService
                failure_detection = FailureDetectionService(db)
                pattern = failure_detection.analyze_task_failures(
                    task.id, "gsc_insights", task.user_id
                )
                
                task.last_failure = datetime.utcnow()
                task.failure_reason = result.error_message
                
                if pattern and pattern.should_cool_off:
                    # Mark task for human intervention
                    task.status = "needs_intervention"
                    task.consecutive_failures = pattern.consecutive_failures
                    task.failure_pattern = {
                        "consecutive_failures": pattern.consecutive_failures,
                        "recent_failures": pattern.recent_failures,
                        "failure_reason": pattern.failure_reason.value,
                        "error_patterns": pattern.error_patterns,
                        "cool_off_until": (datetime.utcnow() + timedelta(days=7)).isoformat()
                    }
                    # Clear next_check - task won't run automatically
                    task.next_check = None
                    
                    self.logger.warning(
                        f"Task {task.id} marked for human intervention: "
                        f"{pattern.consecutive_failures} consecutive failures, "
                        f"reason: {pattern.failure_reason.value}"
                    )
                else:
                    # Normal failure handling
                    task.status = 'failed'
                    task.consecutive_failures = (task.consecutive_failures or 0) + 1
                    # Schedule retry in 1 day
                    task.next_check = datetime.utcnow() + timedelta(days=1)
            
            task.updated_at = datetime.utcnow()
            db.commit()
            
            return result
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Set database session for exception handler
            self.exception_handler.db = db
            
            error_result = self.exception_handler.handle_task_execution_error(
                task=task,
                error=e,
                execution_time_ms=execution_time_ms,
                context="GSC insights fetch"
            )
            
            # Analyze failure pattern
            from services.scheduler.core.failure_detection_service import FailureDetectionService
            failure_detection = FailureDetectionService(db)
            pattern = failure_detection.analyze_task_failures(
                task.id, "gsc_insights", task.user_id
            )
            
            # Update task
            task.last_check = datetime.utcnow()
            task.last_failure = datetime.utcnow()
            task.failure_reason = str(e)
            
            if pattern and pattern.should_cool_off:
                # Mark task for human intervention
                task.status = "needs_intervention"
                task.consecutive_failures = pattern.consecutive_failures
                task.failure_pattern = {
                    "consecutive_failures": pattern.consecutive_failures,
                    "recent_failures": pattern.recent_failures,
                    "failure_reason": pattern.failure_reason.value,
                    "error_patterns": pattern.error_patterns,
                    "cool_off_until": (datetime.utcnow() + timedelta(days=7)).isoformat()
                }
                task.next_check = None
            else:
                task.status = 'failed'
                task.consecutive_failures = (task.consecutive_failures or 0) + 1
                task.next_check = datetime.utcnow() + timedelta(days=1)
            
            task.updated_at = datetime.utcnow()
            db.commit()
            
            return error_result
    
    async def _fetch_insights(self, task: PlatformInsightsTask, db: Session) -> TaskExecutionResult:
        """
        Fetch GSC insights data.
        
        On first run (no last_success), loads cached data.
        On subsequent runs, fetches fresh data from API.
        """
        user_id = task.user_id
        site_url = task.site_url
        
        try:
            # Check if this is first run (no previous success)
            is_first_run = task.last_success is None
            
            if is_first_run:
                # First run: Try to load from cache
                self.logger.info(f"First run for GSC insights task {task.id} - loading cached data")
                cached_data = self._load_cached_data(user_id, site_url)
                
                if cached_data:
                    self.logger.info(f"Loaded cached GSC data for user {user_id}")
                    return TaskExecutionResult(
                        success=True,
                        result_data={
                            'data_source': 'cached',
                            'insights': cached_data,
                            'message': 'Loaded from cached data (first run)'
                        }
                    )
                else:
                    # No cached data - try to fetch from API
                    self.logger.info(f"No cached data found, fetching from GSC API")
                    return await self._fetch_fresh_data(task, db, user_id, site_url)
            else:
                # Subsequent run: Always fetch fresh data
                self.logger.info(f"Subsequent run for GSC insights task {task.id} - fetching fresh data")
                return await self._fetch_fresh_data(task, db, user_id, site_url)
                
        except Exception as e:
            self.logger.error(f"Error fetching GSC insights for user {user_id}: {e}", exc_info=True)
            return TaskExecutionResult(
                success=False,
                error_message=f"Failed to fetch GSC insights: {str(e)}",
                result_data={'error': str(e)}
            )
    
    def _load_cached_data(self, user_id: str, site_url: Optional[str]) -> Optional[Dict[str, Any]]:
        """Load most recent cached GSC data from database."""
        try:
            db_path = self.gsc_service.db_path
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Find most recent cached data
                if site_url:
                    cursor.execute('''
                        SELECT data_json, created_at
                        FROM gsc_data_cache
                        WHERE user_id = ? AND site_url = ? AND data_type = 'analytics'
                        ORDER BY created_at DESC
                        LIMIT 1
                    ''', (user_id, site_url))
                else:
                    cursor.execute('''
                        SELECT data_json, created_at
                        FROM gsc_data_cache
                        WHERE user_id = ? AND data_type = 'analytics'
                        ORDER BY created_at DESC
                        LIMIT 1
                    ''', (user_id,))
                
                result = cursor.fetchone()
                
                if result:
                    data_json, created_at = result
                    insights_data = json.loads(data_json) if isinstance(data_json, str) else data_json
                    
                    self.logger.info(
                        f"Found cached GSC data from {created_at} for user {user_id}"
                    )
                    
                    return insights_data
                
                return None
                
        except Exception as e:
            self.logger.warning(f"Error loading cached GSC data: {e}")
            return None
    
    async def _fetch_fresh_data(self, task: PlatformInsightsTask, db: Session, user_id: str, site_url: Optional[str]) -> TaskExecutionResult:
        """Fetch fresh GSC insights from API and persist comparable-window delta events."""
        try:
            if not site_url:
                sites = self.gsc_service.get_site_list(user_id)
                if not sites:
                    return TaskExecutionResult(
                        success=False,
                        error_message="No GSC sites found for user",
                        result_data={'error': 'No sites found'}
                    )
                site_url = sites[0]['siteUrl']

            window_days = 30
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=window_days)
            prior_end_dt = start_dt - timedelta(days=1)
            prior_start_dt = prior_end_dt - timedelta(days=window_days)

            end_date = end_dt.strftime('%Y-%m-%d')
            start_date = start_dt.strftime('%Y-%m-%d')
            prior_end_date = prior_end_dt.strftime('%Y-%m-%d')
            prior_start_date = prior_start_dt.strftime('%Y-%m-%d')

            current_analytics = self.gsc_service.get_search_analytics(
                user_id=user_id,
                site_url=site_url,
                start_date=start_date,
                end_date=end_date
            )
            if 'error' in current_analytics:
                return TaskExecutionResult(
                    success=False,
                    error_message=current_analytics.get('error', 'Unknown error'),
                    result_data=current_analytics
                )

            prior_analytics = self.gsc_service.get_search_analytics(
                user_id=user_id,
                site_url=site_url,
                start_date=prior_start_date,
                end_date=prior_end_date
            )
            if 'error' in prior_analytics:
                self.logger.warning(
                    f"Prior comparable window unavailable for user={user_id}, site={site_url}: "
                    f"{prior_analytics.get('error')}"
                )
                prior_analytics = {'query_data': {'rows': []}, 'page_data': {'rows': []}}

            delta_events = self._compute_delta_events(
                current_analytics=current_analytics,
                prior_analytics=prior_analytics,
                current_window=(start_date, end_date),
                prior_window=(prior_start_date, prior_end_date),
            )
            persisted_events = self._persist_delta_events(
                db=db,
                task=task,
                user_id=user_id,
                site_url=site_url,
                delta_events=delta_events,
                current_window=(start_date, end_date),
                prior_window=(prior_start_date, prior_end_date),
            )

            insights_data = {
                'site_url': site_url,
                'date_range': {
                    'start': start_date,
                    'end': end_date
                },
                'prior_date_range': {
                    'start': prior_start_date,
                    'end': prior_end_date
                },
                'overall_metrics': current_analytics.get('overall_metrics', {}),
                'query_data': current_analytics.get('query_data', {}),
                'page_data': current_analytics.get('page_data', {}),
                'delta_events_generated': len(delta_events),
                'delta_events_persisted': persisted_events,
                'fetched_at': datetime.utcnow().isoformat()
            }

            self.logger.info(
                f"Successfully fetched GSC insights and persisted {persisted_events} delta events "
                f"for user {user_id}, site {site_url}"
            )

            return TaskExecutionResult(
                success=True,
                result_data={
                    'data_source': 'api',
                    'insights': insights_data,
                    'message': 'Fetched fresh data from GSC API and persisted delta events'
                }
            )

        except Exception as e:
            self.logger.error(f"Error fetching fresh GSC data: {e}", exc_info=True)
            return TaskExecutionResult(
                success=False,
                error_message=f"API fetch failed: {str(e)}",
                result_data={'error': str(e)}
            )

    def _extract_dimension_map(self, analytics_data: Dict[str, Any], entity_type: str) -> Dict[str, Dict[str, float]]:
        """Build normalized metric map keyed by query/page."""
        container_key = 'page_data' if entity_type == 'page' else 'query_data'
        rows = analytics_data.get(container_key, {}).get('rows', []) if isinstance(analytics_data, dict) else []

        mapped: Dict[str, Dict[str, float]] = {}
        for row in rows:
            keys = row.get('keys', [])
            if not keys:
                continue
            entity_key = str(keys[0]).strip()
            if not entity_key:
                continue

            clicks = float(row.get('clicks', 0) or 0)
            impressions = float(row.get('impressions', 0) or 0)
            ctr = float(row.get('ctr', 0) or 0) * 100.0
            position = float(row.get('position', 0) or 0)

            mapped[entity_key] = {
                'clicks': clicks,
                'impressions': impressions,
                'ctr': ctr,
                'position': position,
            }

        return mapped

    def _compute_delta_events(
        self,
        current_analytics: Dict[str, Any],
        prior_analytics: Dict[str, Any],
        current_window: Tuple[str, str],
        prior_window: Tuple[str, str],
    ) -> List[Dict[str, Any]]:
        """Generate labeled decline/rise/opportunity events from comparable windows."""
        thresholds = {
            'clicks_pct_change': 20.0,
            'impressions_pct_change': 25.0,
            'ctr_abs_pp_change': 1.5,
            'position_abs_change': 2.0,
            'opportunity_min_impressions': 100.0,
            'opportunity_max_ctr': 2.0,
            'opportunity_min_position': 3.0,
            'opportunity_max_position': 20.0,
        }

        events: List[Dict[str, Any]] = []
        for entity_type in ('page', 'query'):
            current_map = self._extract_dimension_map(current_analytics, entity_type)
            prior_map = self._extract_dimension_map(prior_analytics, entity_type)
            all_keys = set(current_map.keys()) | set(prior_map.keys())

            for entity_key in all_keys:
                curr = current_map.get(entity_key, {'clicks': 0.0, 'impressions': 0.0, 'ctr': 0.0, 'position': 0.0})
                prev = prior_map.get(entity_key, {'clicks': 0.0, 'impressions': 0.0, 'ctr': 0.0, 'position': 0.0})

                delta_clicks = curr['clicks'] - prev['clicks']
                delta_impressions = curr['impressions'] - prev['impressions']
                delta_ctr = curr['ctr'] - prev['ctr']
                delta_position = curr['position'] - prev['position']

                clicks_pct = ((delta_clicks / prev['clicks']) * 100.0) if prev['clicks'] > 0 else None
                impressions_pct = ((delta_impressions / prev['impressions']) * 100.0) if prev['impressions'] > 0 else None

                trigger_type = None
                reasons: List[str] = []

                if clicks_pct is not None and clicks_pct <= -thresholds['clicks_pct_change']:
                    trigger_type = 'decline'
                    reasons.append('clicks_drop')
                if impressions_pct is not None and impressions_pct <= -thresholds['impressions_pct_change']:
                    trigger_type = trigger_type or 'decline'
                    reasons.append('impressions_drop')
                if delta_ctr <= -thresholds['ctr_abs_pp_change']:
                    trigger_type = trigger_type or 'decline'
                    reasons.append('ctr_drop')
                if delta_position >= thresholds['position_abs_change']:
                    trigger_type = trigger_type or 'decline'
                    reasons.append('position_drop')

                if trigger_type is None:
                    if clicks_pct is not None and clicks_pct >= thresholds['clicks_pct_change']:
                        trigger_type = 'rise'
                        reasons.append('clicks_rise')
                    if impressions_pct is not None and impressions_pct >= thresholds['impressions_pct_change']:
                        trigger_type = trigger_type or 'rise'
                        reasons.append('impressions_rise')
                    if delta_ctr >= thresholds['ctr_abs_pp_change']:
                        trigger_type = trigger_type or 'rise'
                        reasons.append('ctr_rise')
                    if delta_position <= -thresholds['position_abs_change']:
                        trigger_type = trigger_type or 'rise'
                        reasons.append('position_rise')

                if trigger_type is None:
                    is_opportunity = (
                        curr['impressions'] >= thresholds['opportunity_min_impressions']
                        and curr['ctr'] <= thresholds['opportunity_max_ctr']
                        and thresholds['opportunity_min_position'] <= curr['position'] <= thresholds['opportunity_max_position']
                    )
                    if is_opportunity:
                        trigger_type = 'opportunity'
                        reasons.append('high_impressions_low_ctr')

                if not trigger_type:
                    continue

                severity = 'low'
                if trigger_type == 'decline':
                    severity = 'high' if len(reasons) >= 2 else 'medium'
                elif trigger_type == 'opportunity':
                    severity = 'medium'

                events.append({
                    'event_type': trigger_type,
                    'entity_type': entity_type,
                    'entity_key': entity_key,
                    'severity': severity,
                    'reasons': reasons,
                    'metrics': {
                        'current': curr,
                        'prior': prev,
                        'delta': {
                            'clicks': delta_clicks,
                            'impressions': delta_impressions,
                            'ctr': delta_ctr,
                            'position': delta_position,
                            'clicks_pct': clicks_pct,
                            'impressions_pct': impressions_pct,
                        },
                    },
                    'thresholds': thresholds,
                    'current_window': {'start': current_window[0], 'end': current_window[1]},
                    'prior_window': {'start': prior_window[0], 'end': prior_window[1]},
                })

        return events

    def _persist_delta_events(
        self,
        db: Session,
        task: PlatformInsightsTask,
        user_id: str,
        site_url: str,
        delta_events: List[Dict[str, Any]],
        current_window: Tuple[str, str],
        prior_window: Tuple[str, str],
    ) -> int:
        """Persist generated delta events for downstream dashboard/content-strategy features."""
        # Remove previously stored events for the same window to keep retrieval deterministic
        db.query(PlatformInsightDeltaEvent).filter(
            PlatformInsightDeltaEvent.user_id == user_id,
            PlatformInsightDeltaEvent.platform == 'gsc',
            PlatformInsightDeltaEvent.site_url == site_url,
            PlatformInsightDeltaEvent.current_start_date == current_window[0],
            PlatformInsightDeltaEvent.current_end_date == current_window[1],
        ).delete(synchronize_session=False)

        for event in delta_events:
            db.add(PlatformInsightDeltaEvent(
                user_id=user_id,
                platform='gsc',
                site_url=site_url,
                task_id=task.id,
                event_type=event['event_type'],
                entity_type=event['entity_type'],
                entity_key=event['entity_key'],
                current_start_date=current_window[0],
                current_end_date=current_window[1],
                prior_start_date=prior_window[0],
                prior_end_date=prior_window[1],
                details=event,
                severity=event.get('severity'),
            ))

        db.flush()
        return len(delta_events)

    def calculate_next_execution(
        self,
        task: PlatformInsightsTask,
        frequency: str,
        last_execution: Optional[datetime] = None
    ) -> datetime:
        """
        Calculate next execution time based on frequency.
        
        For platform insights, frequency is always 'Weekly' (7 days).
        """
        if last_execution is None:
            last_execution = datetime.utcnow()
        
        if frequency == 'Weekly':
            return last_execution + timedelta(days=7)
        elif frequency == 'Daily':
            return last_execution + timedelta(days=1)
        else:
            # Default to weekly
            return last_execution + timedelta(days=7)

