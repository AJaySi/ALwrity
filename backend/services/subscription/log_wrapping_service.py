"""
Log Wrapping Service
Intelligently wraps API usage logs when they exceed 5000 records.
Aggregates old logs into cumulative records while preserving historical data.
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
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_and_wrap_logs(self, user_id: str) -> Dict[str, Any]:
        """
        Check if user has exceeded log limit and wrap if necessary.
        
        Returns:
            Dict with wrapping status and statistics
        """
        try:
            # Count total logs for user
            total_count = self.db.query(func.count(APIUsageLog.id)).filter(
                APIUsageLog.user_id == user_id
            ).scalar() or 0
            
            if total_count <= self.MAX_LOGS_PER_USER:
                return {
                    'wrapped': False,
                    'total_logs': total_count,
                    'max_logs': self.MAX_LOGS_PER_USER,
                    'message': f'Log count ({total_count}) is within limit ({self.MAX_LOGS_PER_USER})'
                }
            
            # Need to wrap logs - aggregate old logs
            logger.info(f"[LogWrapping] User {user_id} has {total_count} logs, exceeding limit of {self.MAX_LOGS_PER_USER}. Starting wrap...")
            
            wrap_result = self._wrap_old_logs(user_id, total_count)
            
            return {
                'wrapped': True,
                'total_logs_before': total_count,
                'total_logs_after': wrap_result['logs_remaining'],
                'aggregated_logs': wrap_result['aggregated_count'],
                'aggregated_periods': wrap_result['periods'],
                'message': f'Wrapped {wrap_result["aggregated_count"]} logs into {len(wrap_result["periods"])} aggregated records'
            }
            
        except Exception as e:
            logger.error(f"[LogWrapping] Error checking/wrapping logs for user {user_id}: {e}", exc_info=True)
            return {
                'wrapped': False,
                'error': str(e),
                'message': f'Error wrapping logs: {str(e)}'
            }
    
    def _wrap_old_logs(self, user_id: str, total_count: int) -> Dict[str, Any]:
        """
        Aggregate old logs into cumulative records.
        
        Strategy:
        1. Keep most recent 4000 logs (detailed)
        2. Aggregate logs older than 30 days or oldest logs beyond 4000
        3. Create aggregated records grouped by provider and billing period
        4. Delete individual logs that were aggregated
        """
        try:
            # Calculate how many logs to keep (4000 detailed, rest aggregated)
            logs_to_keep = 4000
            logs_to_aggregate = total_count - logs_to_keep
            
            # Get cutoff date (30 days ago)
            cutoff_date = datetime.utcnow() - timedelta(days=self.AGGREGATION_THRESHOLD_DAYS)
            
            # Get logs to aggregate: oldest logs beyond the keep limit
            # Order by timestamp ascending to get oldest first
            # We'll keep the most recent logs_to_keep logs, aggregate the rest
            logs_to_process = self.db.query(APIUsageLog).filter(
                APIUsageLog.user_id == user_id
            ).order_by(APIUsageLog.timestamp.asc()).limit(logs_to_aggregate).all()
            
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
            
            return {
                'aggregated_count': aggregated_count,
                'logs_remaining': remaining_count,
                'periods': periods_created
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"[LogWrapping] Error wrapping logs: {e}", exc_info=True)
            raise

