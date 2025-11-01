"""
Monitoring Data Service
Handles saving and retrieving monitoring data from database and cache.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from models.monitoring_models import (
    StrategyMonitoringPlan, MonitoringTask, TaskExecutionLog,
    StrategyPerformanceMetrics, StrategyActivationStatus
)
from models.enhanced_strategy_models import EnhancedContentStrategy

logger = logging.getLogger(__name__)

class MonitoringDataService:
    """Service for managing monitoring data in database and cache."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    async def save_monitoring_data(self, strategy_id: int, monitoring_plan: Dict[str, Any]) -> bool:
        """Save monitoring plan and tasks to database."""
        try:
            logger.info(f"Saving monitoring data for strategy {strategy_id}")
            logger.info(f"Monitoring plan received: {monitoring_plan}")
            
            # Save the complete monitoring plan
            monitoring_plan_record = StrategyMonitoringPlan(
                strategy_id=strategy_id,
                plan_data=monitoring_plan
            )
            self.db.add(monitoring_plan_record)
            
            # Save individual monitoring tasks
            monitoring_tasks = monitoring_plan.get('monitoringTasks', [])
            logger.info(f"Found {len(monitoring_tasks)} monitoring tasks to save")
            
            for i, task_data in enumerate(monitoring_tasks):
                logger.info(f"Saving task {i+1}: {task_data.get('title', 'Unknown')}")
                task = MonitoringTask(
                    strategy_id=strategy_id,
                    component_name=task_data.get('component', ''),
                    task_title=task_data.get('title', ''),
                    task_description=task_data.get('description', ''),
                    assignee=task_data.get('assignee', 'ALwrity'),
                    frequency=task_data.get('frequency', 'Monthly'),
                    metric=task_data.get('metric', ''),
                    measurement_method=task_data.get('measurementMethod', ''),
                    success_criteria=task_data.get('successCriteria', ''),
                    alert_threshold=task_data.get('alertThreshold', ''),
                    status='active'
                )
                
                # Initialize next_execution based on frequency
                from services.scheduler.utils.frequency_calculator import calculate_next_execution
                task.next_execution = calculate_next_execution(
                    frequency=task.frequency,
                    base_time=datetime.utcnow()
                )
                
                self.db.add(task)
            
            # Save activation status
            activation_status = StrategyActivationStatus(
                strategy_id=strategy_id,
                user_id=1,  # Default user ID
                activation_date=datetime.utcnow(),
                status='active'
            )
            self.db.add(activation_status)
            
            # Save initial performance metrics
            performance_metrics = StrategyPerformanceMetrics(
                strategy_id=strategy_id,
                user_id=1,  # Default user ID
                metric_date=datetime.utcnow(),
                data_source='monitoring_plan',
                confidence_score=85  # High confidence for monitoring plan data
            )
            self.db.add(performance_metrics)
            
            self.db.commit()
            logger.info(f"Successfully saved monitoring data for strategy {strategy_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving monitoring data for strategy {strategy_id}: {e}")
            self.db.rollback()
            return False
    
    async def get_monitoring_data(self, strategy_id: int) -> Optional[Dict[str, Any]]:
        """Get monitoring data from database."""
        try:
            logger.info(f"Retrieving monitoring data for strategy {strategy_id}")
            
            # Get the monitoring plan
            monitoring_plan = self.db.query(StrategyMonitoringPlan).filter(
                StrategyMonitoringPlan.strategy_id == strategy_id
            ).order_by(desc(StrategyMonitoringPlan.created_at)).first()
            
            if not monitoring_plan:
                logger.warning(f"No monitoring plan found for strategy {strategy_id}")
                return None
            
            # Get monitoring tasks
            tasks = self.db.query(MonitoringTask).filter(
                MonitoringTask.strategy_id == strategy_id
            ).all()
            
            # Get activation status
            activation_status = self.db.query(StrategyActivationStatus).filter(
                StrategyActivationStatus.strategy_id == strategy_id
            ).first()
            
            # Get performance metrics
            performance_metrics = self.db.query(StrategyPerformanceMetrics).filter(
                StrategyPerformanceMetrics.strategy_id == strategy_id
            ).order_by(desc(StrategyPerformanceMetrics.metric_date)).first()
            
            # Build comprehensive monitoring data
            monitoring_data = {
                'strategy_id': strategy_id,
                'monitoring_plan': monitoring_plan.plan_data,
                'monitoring_tasks': [
                    {
                        'id': task.id,
                        'component': task.component_name,
                        'title': task.task_title,
                        'description': task.task_description,
                        'assignee': task.assignee,
                        'frequency': task.frequency,
                        'metric': task.metric,
                        'measurementMethod': task.measurement_method,
                        'successCriteria': task.success_criteria,
                        'alertThreshold': task.alert_threshold,
                        'status': task.status,
                        'last_executed': task.last_executed.isoformat() if task.last_executed else None,
                        'next_execution': task.next_execution.isoformat() if task.next_execution else None
                    }
                    for task in tasks
                ],
                'activation_status': {
                    'activation_date': activation_status.activation_date.isoformat() if activation_status else None,
                    'status': activation_status.status if activation_status else 'unknown',
                    'performance_score': activation_status.performance_score if activation_status else None
                },
                'performance_metrics': {
                    'traffic_growth': performance_metrics.traffic_growth_percentage if performance_metrics else None,
                    'engagement_rate': performance_metrics.engagement_rate_percentage if performance_metrics else None,
                    'conversion_rate': performance_metrics.conversion_rate_percentage if performance_metrics else None,
                    'roi_ratio': performance_metrics.roi_ratio if performance_metrics else None,
                    'content_quality_score': performance_metrics.content_quality_score if performance_metrics else None,
                    'data_source': performance_metrics.data_source if performance_metrics else None,
                    'confidence_score': performance_metrics.confidence_score if performance_metrics else None
                },
                'created_at': monitoring_plan.created_at.isoformat(),
                'updated_at': monitoring_plan.updated_at.isoformat()
            }
            
            logger.info(f"Successfully retrieved monitoring data for strategy {strategy_id}")
            return monitoring_data
            
        except Exception as e:
            logger.error(f"Error retrieving monitoring data for strategy {strategy_id}: {e}")
            return None
    
    async def get_analytics_data(self, strategy_id: int) -> Dict[str, Any]:
        """Get analytics data from monitoring data (no external API calls)."""
        try:
            logger.info(f"Generating analytics data for strategy {strategy_id}")
            
            # Get monitoring data from database
            monitoring_data = await self.get_monitoring_data(strategy_id)
            
            if not monitoring_data:
                logger.warning(f"No monitoring data found for strategy {strategy_id}")
                return self._get_empty_analytics_data()
            
            # Extract analytics from monitoring data
            monitoring_plan = monitoring_data['monitoring_plan']
            tasks = monitoring_data['monitoring_tasks']
            performance_metrics = monitoring_data['performance_metrics']
            
            # Always use monitoring tasks from the plan for rich data, fallback to database tasks
            monitoring_tasks = []
            if monitoring_plan.get('monitoringTasks'):
                # Use rich data from monitoring plan
                monitoring_tasks = [
                    {
                        'id': i + 1,
                        'component': task.get('component', ''),
                        'title': task.get('title', ''),
                        'description': task.get('description', ''),
                        'assignee': task.get('assignee', 'ALwrity'),
                        'frequency': task.get('frequency', 'Monthly'),
                        'metric': task.get('metric', ''),
                        'measurementMethod': task.get('measurementMethod', ''),
                        'successCriteria': task.get('successCriteria', ''),
                        'alertThreshold': task.get('alertThreshold', ''),
                        'actionableInsights': task.get('actionableInsights', ''),
                        'status': 'active',
                        'last_executed': None,
                        'next_execution': None
                    }
                    for i, task in enumerate(monitoring_plan.get('monitoringTasks', []))
                ]
            elif tasks:
                # Fallback to database tasks if plan doesn't have them
                monitoring_tasks = [
                    {
                        'id': task.id,
                        'component': task.component_name,
                        'title': task.task_title,
                        'description': task.task_description,
                        'assignee': task.assignee,
                        'frequency': task.frequency,
                        'metric': task.metric,
                        'measurementMethod': task.measurement_method,
                        'successCriteria': task.success_criteria,
                        'alertThreshold': task.alert_threshold,
                        'actionableInsights': '',
                        'status': task.status,
                        'last_executed': task.last_executed.isoformat() if task.last_executed else None,
                        'next_execution': task.next_execution.isoformat() if task.next_execution else None
                    }
                    for task in tasks
                ]
            
            # Always use performance metrics from success metrics for rich data
            extracted_metrics = {}
            if monitoring_plan.get('successMetrics'):
                success_metrics = monitoring_plan['successMetrics']
                extracted_metrics = {
                    'traffic_growth': self._extract_percentage(success_metrics.get('trafficGrowth', {}).get('current', '0%')),
                    'engagement_rate': self._extract_percentage(success_metrics.get('engagementRate', {}).get('current', '0%')),
                    'conversion_rate': self._extract_percentage(success_metrics.get('conversionRate', {}).get('current', '0%')),
                    'roi_ratio': self._extract_ratio(success_metrics.get('roi', {}).get('current', '0:1')),
                    'content_quality_score': self._extract_percentage(success_metrics.get('contentQuality', {}).get('current', '0%')),
                    'data_source': 'monitoring_plan',
                    'confidence_score': 85
                }
            else:
                # Fallback to database metrics if plan doesn't have them
                extracted_metrics = {
                    'traffic_growth': performance_metrics.get('traffic_growth', 0),
                    'engagement_rate': performance_metrics.get('engagement_rate', 0),
                    'conversion_rate': performance_metrics.get('conversion_rate', 0),
                    'roi_ratio': performance_metrics.get('roi_ratio', 0),
                    'content_quality_score': performance_metrics.get('content_quality_score', 0),
                    'data_source': performance_metrics.get('data_source', 'database'),
                    'confidence_score': performance_metrics.get('confidence_score', 70)
                }
            
            # Build analytics data from monitoring plan
            analytics_data = {
                'performance_trends': {
                    'traffic_growth': extracted_metrics.get('traffic_growth', 0),
                    'engagement_rate': extracted_metrics.get('engagement_rate', 0),
                    'conversion_rate': extracted_metrics.get('conversion_rate', 0),
                    'roi_ratio': extracted_metrics.get('roi_ratio', 0),
                    'content_quality_score': extracted_metrics.get('content_quality_score', 0)
                },
                'content_evolution': {
                    'content_pillars': monitoring_plan.get('contentPillars', []),
                    'content_mix': monitoring_plan.get('contentMix', {}),
                    'publishing_frequency': monitoring_plan.get('publishingFrequency', ''),
                    'quality_metrics': monitoring_plan.get('qualityMetrics', [])
                },
                'engagement_patterns': {
                    'audience_segments': monitoring_plan.get('audienceSegments', []),
                    'engagement_metrics': monitoring_plan.get('engagementMetrics', {}),
                    'optimal_timing': monitoring_plan.get('optimalTiming', {}),
                    'platform_performance': monitoring_plan.get('platformPerformance', {})
                },
                'recommendations': monitoring_plan.get('recommendations', []),
                'insights': monitoring_plan.get('insights', []),
                'monitoring_data': monitoring_data,
                'monitoring_tasks': monitoring_tasks,
                'monitoring_plan': monitoring_plan,  # Include full monitoring plan for rich data
                'success_metrics': monitoring_plan.get('successMetrics', {}),  # Include success metrics
                'monitoring_schedule': monitoring_plan.get('monitoringSchedule', {}),  # Include monitoring schedule
                '_source': 'database_monitoring',
                'data_freshness': monitoring_data['updated_at'],
                'confidence_score': extracted_metrics.get('confidence_score', 85)
            }
            
            logger.info(f"Successfully generated analytics data for strategy {strategy_id}")
            return analytics_data
            
        except Exception as e:
            logger.error(f"Error generating analytics data for strategy {strategy_id}: {e}")
            return self._get_empty_analytics_data()
    
    def _get_empty_analytics_data(self) -> Dict[str, Any]:
        """Return empty analytics data structure."""
        return {
            'performance_trends': {},
            'content_evolution': {},
            'engagement_patterns': {},
            'recommendations': [],
            'insights': [],
            'monitoring_data': None,
            'monitoring_tasks': [],
            '_source': 'empty',
            'data_freshness': datetime.utcnow().isoformat(),
            'confidence_score': 0
        }
    
    def _extract_percentage(self, value: str) -> float:
        """Extract percentage value from string like '15%'."""
        try:
            if isinstance(value, str) and '%' in value:
                return float(value.replace('%', ''))
            elif isinstance(value, (int, float)):
                return float(value)
            else:
                return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def _extract_ratio(self, value: str) -> float:
        """Extract ratio value from string like '3:1'."""
        try:
            if isinstance(value, str) and ':' in value:
                parts = value.split(':')
                if len(parts) == 2:
                    return float(parts[0]) / float(parts[1])
            elif isinstance(value, (int, float)):
                return float(value)
            else:
                return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    async def update_performance_metrics(self, strategy_id: int, metrics: Dict[str, Any]) -> bool:
        """Update performance metrics for a strategy."""
        try:
            logger.info(f"Updating performance metrics for strategy {strategy_id}")
            
            performance_metrics = StrategyPerformanceMetrics(
                strategy_id=strategy_id,
                user_id=1,  # Default user ID
                metric_date=datetime.utcnow(),
                traffic_growth_percentage=metrics.get('traffic_growth'),
                engagement_rate_percentage=metrics.get('engagement_rate'),
                conversion_rate_percentage=metrics.get('conversion_rate'),
                roi_ratio=metrics.get('roi_ratio'),
                content_quality_score=metrics.get('content_quality_score'),
                data_source='manual_update',
                confidence_score=metrics.get('confidence_score', 70)
            )
            
            self.db.add(performance_metrics)
            self.db.commit()
            
            logger.info(f"Successfully updated performance metrics for strategy {strategy_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating performance metrics for strategy {strategy_id}: {e}")
            self.db.rollback()
            return False
    
    def get_user_execution_logs(
        self,
        user_id: int,
        limit: Optional[int] = 50,
        offset: Optional[int] = 0,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get execution logs for a specific user.
        
        Args:
            user_id: User ID to filter execution logs
            limit: Maximum number of logs to return
            offset: Number of logs to skip (for pagination)
            status_filter: Optional status filter ('success', 'failed', 'running', 'skipped')
            
        Returns:
            List of execution log dictionaries with task details
        """
        try:
            logger.info(f"Getting execution logs for user {user_id}")
            
            # Build query for execution logs filtered by user_id
            query = self.db.query(TaskExecutionLog).filter(
                TaskExecutionLog.user_id == user_id
            )
            
            # Apply status filter if provided
            if status_filter:
                query = query.filter(TaskExecutionLog.status == status_filter)
            
            # Order by execution date (most recent first)
            query = query.order_by(desc(TaskExecutionLog.execution_date))
            
            # Apply pagination
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            logs = query.all()
            
            # Convert to dictionaries with task details
            logs_data = []
            for log in logs:
                # Get task details if available
                task = self.db.query(MonitoringTask).filter(
                    MonitoringTask.id == log.task_id
                ).first()
                
                log_data = {
                    "id": log.id,
                    "task_id": log.task_id,
                    "user_id": log.user_id,
                    "execution_date": log.execution_date.isoformat() if log.execution_date else None,
                    "status": log.status,
                    "result_data": log.result_data,
                    "error_message": log.error_message,
                    "execution_time_ms": log.execution_time_ms,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                    "task": {
                        "title": task.task_title if task else None,
                        "description": task.task_description if task else None,
                        "assignee": task.assignee if task else None,
                        "frequency": task.frequency if task else None,
                        "strategy_id": task.strategy_id if task else None
                    } if task else None
                }
                logs_data.append(log_data)
            
            logger.info(f"Retrieved {len(logs_data)} execution logs for user {user_id}")
            return logs_data
            
        except Exception as e:
            logger.error(f"Error getting execution logs for user {user_id}: {e}")
            return []
