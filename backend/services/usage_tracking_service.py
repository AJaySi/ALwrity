"""
Usage Tracking Service
Comprehensive tracking of API usage, costs, and subscription limits.
"""

import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from loguru import logger
import json

from models.subscription_models import (
    APIUsageLog, UsageSummary, APIProvider, UsageAlert, 
    UserSubscription, UsageStatus
)
from services.pricing_service import PricingService

class UsageTrackingService:
    """Service for tracking API usage and managing subscription limits."""
    
    def __init__(self, db: Session):
        self.db = db
        self.pricing_service = PricingService(db)
    
    async def track_api_usage(self, user_id: str, provider: APIProvider, 
                            endpoint: str, method: str, model_used: str = None,
                            tokens_input: int = 0, tokens_output: int = 0,
                            response_time: float = 0.0, status_code: int = 200,
                            request_size: int = None, response_size: int = None,
                            user_agent: str = None, ip_address: str = None,
                            error_message: str = None, retry_count: int = 0,
                            **kwargs) -> Dict[str, Any]:
        """Track an API usage event and update billing information."""
        
        try:
            # Calculate costs
            cost_data = self.pricing_service.calculate_api_cost(
                provider=provider,
                model_name=model_used or f"{provider.value}-default",
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                request_count=1,
                **kwargs
            )
            
            # Create usage log entry
            billing_period = datetime.now().strftime("%Y-%m")
            usage_log = APIUsageLog(
                user_id=user_id,
                provider=provider,
                endpoint=endpoint,
                method=method,
                model_used=model_used,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                tokens_total=(tokens_input or 0) + (tokens_output or 0),
                cost_input=cost_data['cost_input'],
                cost_output=cost_data['cost_output'],
                cost_total=cost_data['cost_total'],
                response_time=response_time,
                status_code=status_code,
                request_size=request_size,
                response_size=response_size,
                user_agent=user_agent,
                ip_address=ip_address,
                error_message=error_message,
                retry_count=retry_count,
                billing_period=billing_period
            )
            
            self.db.add(usage_log)
            
            # Update usage summary
            await self._update_usage_summary(
                user_id=user_id,
                provider=provider,
                tokens_used=(tokens_input or 0) + (tokens_output or 0),
                cost=cost_data['cost_total'],
                billing_period=billing_period,
                response_time=response_time,
                is_error=status_code >= 400
            )
            
            # Check for usage alerts
            await self._check_usage_alerts(user_id, provider, billing_period)
            
            self.db.commit()
            
            logger.info(f"Tracked API usage: {user_id} -> {provider.value} -> ${cost_data['cost_total']:.6f}")
            
            return {
                'usage_logged': True,
                'cost': cost_data['cost_total'],
                'tokens_used': (tokens_input or 0) + (tokens_output or 0),
                'billing_period': billing_period
            }
            
        except Exception as e:
            logger.error(f"Error tracking API usage: {str(e)}")
            self.db.rollback()
            return {
                'usage_logged': False,
                'error': str(e)
            }
    
    async def _update_usage_summary(self, user_id: str, provider: APIProvider,
                                  tokens_used: int, cost: float, billing_period: str,
                                  response_time: float, is_error: bool):
        """Update the usage summary for a user."""
        
        # Get or create usage summary
        summary = self.db.query(UsageSummary).filter(
            UsageSummary.user_id == user_id,
            UsageSummary.billing_period == billing_period
        ).first()
        
        if not summary:
            summary = UsageSummary(
                user_id=user_id,
                billing_period=billing_period
            )
            self.db.add(summary)
        
        # Update provider-specific counters
        provider_name = provider.value
        current_calls = getattr(summary, f"{provider_name}_calls", 0)
        setattr(summary, f"{provider_name}_calls", current_calls + 1)
        
        # Update token usage for LLM providers
        if provider in [APIProvider.GEMINI, APIProvider.OPENAI, APIProvider.ANTHROPIC, APIProvider.MISTRAL]:
            current_tokens = getattr(summary, f"{provider_name}_tokens", 0)
            setattr(summary, f"{provider_name}_tokens", current_tokens + tokens_used)
        
        # Update cost
        current_cost = getattr(summary, f"{provider_name}_cost", 0.0)
        setattr(summary, f"{provider_name}_cost", current_cost + cost)
        
        # Update totals
        summary.total_calls += 1
        summary.total_tokens += tokens_used
        summary.total_cost += cost
        
        # Update performance metrics
        if summary.total_calls > 0:
            # Update average response time
            total_response_time = summary.avg_response_time * (summary.total_calls - 1) + response_time
            summary.avg_response_time = total_response_time / summary.total_calls
            
            # Update error rate
            if is_error:
                error_count = int(summary.error_rate * (summary.total_calls - 1) / 100) + 1
                summary.error_rate = (error_count / summary.total_calls) * 100
            else:
                error_count = int(summary.error_rate * (summary.total_calls - 1) / 100)
                summary.error_rate = (error_count / summary.total_calls) * 100
        
        # Update usage status based on limits
        await self._update_usage_status(summary)
        
        summary.updated_at = datetime.utcnow()
    
    async def _update_usage_status(self, summary: UsageSummary):
        """Update usage status based on subscription limits."""
        
        limits = self.pricing_service.get_user_limits(summary.user_id)
        if not limits:
            return
        
        # Check various limits and determine status
        max_usage_percentage = 0.0
        
        # Check cost limit
        cost_limit = limits['limits'].get('monthly_cost', 0)
        if cost_limit > 0:
            cost_usage_pct = (summary.total_cost / cost_limit) * 100
            max_usage_percentage = max(max_usage_percentage, cost_usage_pct)
        
        # Check call limits for each provider
        for provider in APIProvider:
            provider_name = provider.value
            current_calls = getattr(summary, f"{provider_name}_calls", 0)
            call_limit = limits['limits'].get(f"{provider_name}_calls", 0)
            
            if call_limit > 0:
                call_usage_pct = (current_calls / call_limit) * 100
                max_usage_percentage = max(max_usage_percentage, call_usage_pct)
        
        # Update status based on highest usage percentage
        if max_usage_percentage >= 100:
            summary.usage_status = UsageStatus.LIMIT_REACHED
        elif max_usage_percentage >= 80:
            summary.usage_status = UsageStatus.WARNING
        else:
            summary.usage_status = UsageStatus.ACTIVE
    
    async def _check_usage_alerts(self, user_id: str, provider: APIProvider, billing_period: str):
        """Check if usage alerts should be sent."""
        
        # Get current usage
        summary = self.db.query(UsageSummary).filter(
            UsageSummary.user_id == user_id,
            UsageSummary.billing_period == billing_period
        ).first()
        
        if not summary:
            return
        
        # Get user limits
        limits = self.pricing_service.get_user_limits(user_id)
        if not limits:
            return
        
        # Check for alert thresholds (80%, 90%, 100%)
        thresholds = [80, 90, 100]
        
        for threshold in thresholds:
            # Check if alert already sent for this threshold
            existing_alert = self.db.query(UsageAlert).filter(
                UsageAlert.user_id == user_id,
                UsageAlert.billing_period == billing_period,
                UsageAlert.threshold_percentage == threshold,
                UsageAlert.provider == provider,
                UsageAlert.is_sent == True
            ).first()
            
            if existing_alert:
                continue
            
            # Check if threshold is reached
            provider_name = provider.value
            current_calls = getattr(summary, f"{provider_name}_calls", 0)
            call_limit = limits['limits'].get(f"{provider_name}_calls", 0)
            
            if call_limit > 0:
                usage_percentage = (current_calls / call_limit) * 100
                
                if usage_percentage >= threshold:
                    await self._create_usage_alert(
                        user_id=user_id,
                        provider=provider,
                        threshold=threshold,
                        current_usage=current_calls,
                        limit=call_limit,
                        billing_period=billing_period
                    )
    
    async def _create_usage_alert(self, user_id: str, provider: APIProvider,
                                threshold: int, current_usage: int, limit: int,
                                billing_period: str):
        """Create a usage alert."""
        
        # Determine alert type and severity
        if threshold >= 100:
            alert_type = "limit_reached"
            severity = "error"
            title = f"API Limit Reached - {provider.value.title()}"
            message = f"You have reached your {provider.value} API limit of {limit:,} calls for this billing period."
        elif threshold >= 90:
            alert_type = "usage_warning"
            severity = "warning"
            title = f"API Usage Warning - {provider.value.title()}"
            message = f"You have used {current_usage:,} of {limit:,} {provider.value} API calls ({threshold}% of your limit)."
        else:
            alert_type = "usage_warning"
            severity = "info"
            title = f"API Usage Notice - {provider.value.title()}"
            message = f"You have used {current_usage:,} of {limit:,} {provider.value} API calls ({threshold}% of your limit)."
        
        alert = UsageAlert(
            user_id=user_id,
            alert_type=alert_type,
            threshold_percentage=threshold,
            provider=provider,
            title=title,
            message=message,
            severity=severity,
            billing_period=billing_period
        )
        
        self.db.add(alert)
        logger.info(f"Created usage alert for {user_id}: {title}")
    
    def get_user_usage_stats(self, user_id: str, billing_period: str = None) -> Dict[str, Any]:
        """Get comprehensive usage statistics for a user."""
        
        if not billing_period:
            billing_period = datetime.now().strftime("%Y-%m")
        
        # Get usage summary
        summary = self.db.query(UsageSummary).filter(
            UsageSummary.user_id == user_id,
            UsageSummary.billing_period == billing_period
        ).first()
        
        # Get user limits
        limits = self.pricing_service.get_user_limits(user_id)
        
        # Get recent alerts
        alerts = self.db.query(UsageAlert).filter(
            UsageAlert.user_id == user_id,
            UsageAlert.billing_period == billing_period,
            UsageAlert.is_read == False
        ).order_by(UsageAlert.created_at.desc()).limit(10).all()
        
        if not summary:
            # No usage this period - return complete structure with zeros
            provider_breakdown = {}
            usage_percentages = {}
            
            # Initialize provider breakdown with zeros
            for provider in APIProvider:
                provider_name = provider.value
                provider_breakdown[provider_name] = {
                    'calls': 0,
                    'tokens': 0,
                    'cost': 0.0
                }
                usage_percentages[f"{provider_name}_calls"] = 0
            
            usage_percentages['cost'] = 0
            
            return {
                'billing_period': billing_period,
                'usage_status': 'active',
                'total_calls': 0,
                'total_tokens': 0,
                'total_cost': 0.0,
                'avg_response_time': 0.0,
                'error_rate': 0.0,
                'last_updated': datetime.now().isoformat(),
                'limits': limits,
                'provider_breakdown': provider_breakdown,
                'alerts': [],
                'usage_percentages': usage_percentages
            }
        
        # Calculate usage percentages
        usage_percentages = {}
        if limits:
            for provider in APIProvider:
                provider_name = provider.value
                current_calls = getattr(summary, f"{provider_name}_calls", 0) or 0
                call_limit = limits['limits'].get(f"{provider_name}_calls", 0) or 0
                
                if call_limit > 0:
                    usage_percentages[f"{provider_name}_calls"] = (current_calls / call_limit) * 100
                else:
                    usage_percentages[f"{provider_name}_calls"] = 0
            
            # Cost usage percentage
            cost_limit = limits['limits'].get('monthly_cost', 0) or 0
            total_cost = summary.total_cost or 0
            if cost_limit > 0:
                usage_percentages['cost'] = (total_cost / cost_limit) * 100
            else:
                usage_percentages['cost'] = 0
        
        # Provider breakdown
        provider_breakdown = {}
        for provider in APIProvider:
            provider_name = provider.value
            provider_breakdown[provider_name] = {
                'calls': getattr(summary, f"{provider_name}_calls", 0) or 0,
                'tokens': getattr(summary, f"{provider_name}_tokens", 0) or 0,
                'cost': getattr(summary, f"{provider_name}_cost", 0.0) or 0.0
            }
        
        return {
            'billing_period': billing_period,
            'usage_status': summary.usage_status.value if hasattr(summary.usage_status, 'value') else str(summary.usage_status),
            'total_calls': summary.total_calls or 0,
            'total_tokens': summary.total_tokens or 0,
            'total_cost': summary.total_cost or 0.0,
            'avg_response_time': summary.avg_response_time or 0.0,
            'error_rate': summary.error_rate or 0.0,
            'limits': limits,
            'provider_breakdown': provider_breakdown,
            'alerts': [
                {
                    'id': alert.id,
                    'type': alert.alert_type,
                    'title': alert.title,
                    'message': alert.message,
                    'severity': alert.severity,
                    'created_at': alert.created_at.isoformat()
                }
                for alert in alerts
            ],
            'usage_percentages': usage_percentages,
            'last_updated': summary.updated_at.isoformat()
        }
    
    def get_usage_trends(self, user_id: str, months: int = 6) -> Dict[str, Any]:
        """Get usage trends over time."""
        
        # Calculate billing periods
        end_date = datetime.now()
        periods = []
        for i in range(months):
            period_date = end_date - timedelta(days=30 * i)
            periods.append(period_date.strftime("%Y-%m"))
        
        periods.reverse()  # Oldest first
        
        # Get usage summaries for these periods
        summaries = self.db.query(UsageSummary).filter(
            UsageSummary.user_id == user_id,
            UsageSummary.billing_period.in_(periods)
        ).order_by(UsageSummary.billing_period).all()
        
        # Create trends data
        trends = {
            'periods': periods,
            'total_calls': [],
            'total_cost': [],
            'total_tokens': [],
            'provider_trends': {}
        }
        
        summary_dict = {s.billing_period: s for s in summaries}
        
        for period in periods:
            summary = summary_dict.get(period)
            
            if summary:
                trends['total_calls'].append(summary.total_calls or 0)
                trends['total_cost'].append(summary.total_cost or 0.0)
                trends['total_tokens'].append(summary.total_tokens or 0)
                
                # Provider-specific trends
                for provider in APIProvider:
                    provider_name = provider.value
                    if provider_name not in trends['provider_trends']:
                        trends['provider_trends'][provider_name] = {
                            'calls': [],
                            'cost': [],
                            'tokens': []
                        }
                    
                    trends['provider_trends'][provider_name]['calls'].append(
                        getattr(summary, f"{provider_name}_calls", 0) or 0
                    )
                    trends['provider_trends'][provider_name]['cost'].append(
                        getattr(summary, f"{provider_name}_cost", 0.0) or 0.0
                    )
                    trends['provider_trends'][provider_name]['tokens'].append(
                        getattr(summary, f"{provider_name}_tokens", 0) or 0
                    )
            else:
                # No data for this period
                trends['total_calls'].append(0)
                trends['total_cost'].append(0.0)
                trends['total_tokens'].append(0)
                
                for provider in APIProvider:
                    provider_name = provider.value
                    if provider_name not in trends['provider_trends']:
                        trends['provider_trends'][provider_name] = {
                            'calls': [],
                            'cost': [],
                            'tokens': []
                        }
                    
                    trends['provider_trends'][provider_name]['calls'].append(0)
                    trends['provider_trends'][provider_name]['cost'].append(0.0)
                    trends['provider_trends'][provider_name]['tokens'].append(0)
        
        return trends
    
    async def enforce_usage_limits(self, user_id: str, provider: APIProvider,
                                 tokens_requested: int = 0) -> Tuple[bool, str, Dict[str, Any]]:
        """Enforce usage limits before making an API call."""
        
        return self.pricing_service.check_usage_limits(
            user_id=user_id,
            provider=provider,
            tokens_requested=tokens_requested
        )