"""
Log Wrapping Service
Intelligently wraps API usage logs when they exceed limits (count or time-based).
Aggregates old logs into cumulative records while preserving historical data.

Features:
- Count-based retention: Keeps 4,000 most recent detailed logs
- Time-based retention: Aggregates logs older than 90 days
- Automatic aggregation: Triggered on log queries
- Context preservation: Maintains costs, tokens, counts, success rates
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from loguru import logger

from models.subscription_models import APIUsageLog, APIProvider


class LogWrappingService:
    """Service for wrapping and aggregating API usage logs."""
    
    MAX_LOGS_PER_USER = 5000
    AGGREGATION_THRESHOLD_DAYS = 30  # Aggregate logs older than 30 days
    RETENTION_DAYS = 90  # Time-based retention: aggregate logs older than 90 days
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_and_wrap_logs(self, user_id: str) -> Dict[str, Any]:
        """
        Check if user has exceeded log limit (count or time-based) and wrap if necessary.
        
        Checks both:
        1. Count-based: If user has more than MAX_LOGS_PER_USER logs
        2. Time-based: If user has logs older than RETENTION_DAYS
        
        Returns:
            Dict with wrapping status and statistics
        """
        try:
            # Count total logs for user
            total_count = self.db.query(func.count(APIUsageLog.id)).filter(
                APIUsageLog.user_id == user_id
            ).scalar() or 0
            
            # Check for logs older than retention period
            retention_cutoff = datetime.utcnow() - timedelta(days=self.RETENTION_DAYS)
            old_logs_count = self.db.query(func.count(APIUsageLog.id)).filter(
                APIUsageLog.user_id == user_id,
                APIUsageLog.timestamp < retention_cutoff,
                APIUsageLog.endpoint != '[AGGREGATED]'  # Don't re-aggregate already aggregated logs
            ).scalar() or 0
            
            # Determine if wrapping is needed
            count_based_trigger = total_count > self.MAX_LOGS_PER_USER
            time_based_trigger = old_logs_count > 0
            
            if not count_based_trigger and not time_based_trigger:
                return {
                    'wrapped': False,
                    'total_logs': total_count,
                    'old_logs': old_logs_count,
                    'max_logs': self.MAX_LOGS_PER_USER,
                    'retention_days': self.RETENTION_DAYS,
                    'message': f'Log count ({total_count}) and age are within limits'
                }
            
            # Determine trigger reason
            trigger_reasons = []
            if count_based_trigger:
                trigger_reasons.append(f'count limit ({total_count} > {self.MAX_LOGS_PER_USER})')
            if time_based_trigger:
                trigger_reasons.append(f'time-based retention ({old_logs_count} logs older than {self.RETENTION_DAYS} days)')
            
            logger.info(
                f"[LogWrapping] User {user_id} needs log wrapping. "
                f"Total: {total_count}, Old logs: {old_logs_count}. "
                f"Triggers: {', '.join(trigger_reasons)}"
            )
            
            wrap_result = self._wrap_old_logs(user_id, total_count, time_based=time_based_trigger)
            
            return {
                'wrapped': True,
                'total_logs_before': total_count,
                'total_logs_after': wrap_result['logs_remaining'],
                'aggregated_logs': wrap_result['aggregated_count'],
                'aggregated_periods': wrap_result['periods'],
                'trigger_reasons': trigger_reasons,
                'old_logs_aggregated': wrap_result.get('old_logs_aggregated', 0),
                'message': f'Wrapped {wrap_result["aggregated_count"]} logs into {len(wrap_result["periods"])} aggregated records'
            }
            
        except Exception as e:
            logger.error(f"[LogWrapping] Error checking/wrapping logs for user {user_id}: {e}", exc_info=True)
            return {
                'wrapped': False,
                'error': str(e),
                'message': f'Error wrapping logs: {str(e)}'
            }
    
    def _wrap_old_logs(self, user_id: str, total_count: int, time_based: bool = False) -> Dict[str, Any]:
        """
        Aggregate old logs into cumulative records.
        
        Strategy:
        1. Keep most recent 4000 logs (detailed) - count-based
        2. Aggregate logs older than RETENTION_DAYS - time-based
        3. Aggregate oldest logs beyond 4000 limit - count-based
        4. Create aggregated records grouped by provider and billing period
        5. Delete individual logs that were aggregated
        
        Args:
            user_id: User ID
            total_count: Total number of logs for user
            time_based: If True, prioritize time-based retention over count-based
        """
        try:
            # Calculate retention cutoff date
            retention_cutoff = datetime.utcnow() - timedelta(days=self.RETENTION_DAYS)
            aggregation_cutoff = datetime.utcnow() - timedelta(days=self.AGGREGATION_THRESHOLD_DAYS)
            
            # Determine which logs to aggregate
            logs_to_keep = 4000
            logs_to_aggregate_count = max(0, total_count - logs_to_keep)
            
            if time_based:
                # Time-based: Aggregate all logs older than retention period
                # (excluding already aggregated logs)
                logs_to_process = self.db.query(APIUsageLog).filter(
                    APIUsageLog.user_id == user_id,
                    APIUsageLog.timestamp < retention_cutoff,
                    APIUsageLog.endpoint != '[AGGREGATED]'  # Don't re-aggregate
                ).order_by(APIUsageLog.timestamp.asc()).all()
                
                logger.info(
                    f"[LogWrapping] Time-based aggregation: Found {len(logs_to_process)} logs "
                    f"older than {self.RETENTION_DAYS} days"
                )
            else:
                # Count-based: Aggregate oldest logs beyond the keep limit
                logs_to_process = self.db.query(APIUsageLog).filter(
                    APIUsageLog.user_id == user_id,
                    APIUsageLog.endpoint != '[AGGREGATED]'  # Don't re-aggregate
                ).order_by(APIUsageLog.timestamp.asc()).limit(logs_to_aggregate_count).all()
                
                logger.info(
                    f"[LogWrapping] Count-based aggregation: Processing {len(logs_to_process)} "
                    f"oldest logs beyond {logs_to_keep} limit"
                )
            
            # Also check for time-based logs even if count-based is primary
            # This ensures we don't keep very old logs just because they're within the count limit
            if not time_based and logs_to_aggregate_count > 0:
                # Get logs that are both old AND beyond count limit
                old_logs_beyond_limit = self.db.query(APIUsageLog).filter(
                    APIUsageLog.user_id == user_id,
                    APIUsageLog.timestamp < retention_cutoff,
                    APIUsageLog.endpoint != '[AGGREGATED]'
                ).order_by(APIUsageLog.timestamp.asc()).all()
                
                # Merge with count-based logs, prioritizing old logs
                existing_ids = {log.id for log in logs_to_process}
                for old_log in old_logs_beyond_limit:
                    if old_log.id not in existing_ids:
                        logs_to_process.append(old_log)
                
                logger.info(
                    f"[LogWrapping] Combined aggregation: {len(logs_to_process)} logs to process "
                    f"({logs_to_aggregate_count} count-based + {len(old_logs_beyond_limit)} time-based)"
                )
            
            if not logs_to_process:
                return {
                    'aggregated_count': 0,
                    'logs_remaining': total_count,
                    'periods': []
                }
            
            # Group logs by provider and billing period for aggregation
            aggregated_data: Dict[str, Dict[str, Any]] = {}
            
            for log in logs_to_process:
                # Use provider value as key (e.g., "mistral" for huggingface)
                provider_key = log.provider.value
                # Special handling: if provider is MISTRAL but we want to show as huggingface
                if provider_key == "mistral":
                    # Check if this is actually huggingface by looking at model or endpoint
                    # For now, we'll use "mistral" as the key but store actual provider name
                    provider_display = "huggingface" if "huggingface" in (log.model_used or "").lower() else "mistral"
                else:
                    provider_display = provider_key
                
                period_key = f"{provider_display}_{log.billing_period}"
                
                if period_key not in aggregated_data:
                    aggregated_data[period_key] = {
                        'provider': log.provider,
                        'billing_period': log.billing_period,
                        'count': 0,
                        'total_tokens_input': 0,
                        'total_tokens_output': 0,
                        'total_tokens': 0,
                        'total_cost_input': 0.0,
                        'total_cost_output': 0.0,
                        'total_cost': 0.0,
                        'total_response_time': 0.0,
                        'success_count': 0,
                        'failed_count': 0,
                        'oldest_timestamp': log.timestamp,
                        'newest_timestamp': log.timestamp,
                        'log_ids': []
                    }
                
                agg = aggregated_data[period_key]
                agg['count'] += 1
                agg['total_tokens_input'] += log.tokens_input or 0
                agg['total_tokens_output'] += log.tokens_output or 0
                agg['total_tokens'] += log.tokens_total or 0
                agg['total_cost_input'] += float(log.cost_input or 0.0)
                agg['total_cost_output'] += float(log.cost_output or 0.0)
                agg['total_cost'] += float(log.cost_total or 0.0)
                agg['total_response_time'] += float(log.response_time or 0.0)
                
                if 200 <= log.status_code < 300:
                    agg['success_count'] += 1
                else:
                    agg['failed_count'] += 1
                
                if log.timestamp:
                    if log.timestamp < agg['oldest_timestamp']:
                        agg['oldest_timestamp'] = log.timestamp
                    if log.timestamp > agg['newest_timestamp']:
                        agg['newest_timestamp'] = log.timestamp
                
                agg['log_ids'].append(log.id)
            
            # Create aggregated log entries
            aggregated_count = 0
            periods_created = []
            
            for period_key, agg_data in aggregated_data.items():
                # Calculate averages
                count = agg_data['count']
                avg_response_time = agg_data['total_response_time'] / count if count > 0 else 0.0
                
                # Create aggregated log entry
                aggregated_log = APIUsageLog(
                    user_id=user_id,
                    provider=agg_data['provider'],
                    endpoint='[AGGREGATED]',
                    method='AGGREGATED',
                    model_used=f"[{count} calls aggregated]",
                    tokens_input=agg_data['total_tokens_input'],
                    tokens_output=agg_data['total_tokens_output'],
                    tokens_total=agg_data['total_tokens'],
                    cost_input=agg_data['total_cost_input'],
                    cost_output=agg_data['total_cost_output'],
                    cost_total=agg_data['total_cost'],
                    response_time=avg_response_time,
                    status_code=200 if agg_data['success_count'] > agg_data['failed_count'] else 500,
                    error_message=f"Aggregated {count} calls: {agg_data['success_count']} success, {agg_data['failed_count']} failed",
                    retry_count=0,
                    timestamp=agg_data['oldest_timestamp'],  # Use oldest timestamp
                    billing_period=agg_data['billing_period']
                )
                
                self.db.add(aggregated_log)
                periods_created.append({
                    'provider': agg_data['provider'].value,
                    'billing_period': agg_data['billing_period'],
                    'count': count,
                    'period_start': agg_data['oldest_timestamp'].isoformat() if agg_data['oldest_timestamp'] else None,
                    'period_end': agg_data['newest_timestamp'].isoformat() if agg_data['newest_timestamp'] else None
                })
                
                aggregated_count += count
            
            # Delete individual logs that were aggregated
            log_ids_to_delete = []
            for agg_data in aggregated_data.values():
                log_ids_to_delete.extend(agg_data['log_ids'])
            
            if log_ids_to_delete:
                self.db.query(APIUsageLog).filter(
                    APIUsageLog.id.in_(log_ids_to_delete)
                ).delete(synchronize_session=False)
            
            self.db.commit()
            
            # Get remaining log count
            remaining_count = self.db.query(func.count(APIUsageLog.id)).filter(
                APIUsageLog.user_id == user_id
            ).scalar() or 0
            
            logger.info(
                f"[LogWrapping] Wrapped {aggregated_count} logs into {len(periods_created)} aggregated records. "
                f"Remaining logs: {remaining_count}"
            )
            
            # Count how many old logs were aggregated (for reporting)
            # Count logs that were aggregated based on time (not just count)
            old_logs_aggregated = 0
            for log in logs_to_process:
                if log.timestamp and log.timestamp < retention_cutoff:
                    old_logs_aggregated += 1
            
            return {
                'aggregated_count': aggregated_count,
                'logs_remaining': remaining_count,
                'periods': periods_created,
                'old_logs_aggregated': old_logs_aggregated
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"[LogWrapping] Error wrapping logs: {e}", exc_info=True)
            raise

