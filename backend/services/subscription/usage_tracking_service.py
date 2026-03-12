"""
Usage Tracking Service
Comprehensive tracking of API usage, costs, and subscription limits.
"""

# Ensure Optional is available in global scope for dynamic imports
from typing import Optional

import asyncio
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
from loguru import logger
import json

from models.subscription_models import (
    APIUsageLog, UsageSummary, APIProvider, UsageAlert, 
    UserSubscription, UsageStatus
)
from .pricing_service import PricingService
from .provider_detection import detect_actual_provider
from .usage_tracking_helpers import (
    build_billing_periods,
    build_default_usage_percentages,
    build_empty_usage_response,
    build_provider_breakdown,
    build_usage_trends_response,
    calculate_final_total_cost,
    maybe_persist_reconciled_costs,
    query_usage_summaries,
    reset_usage_summary_counters,
    self_heal_summaries_from_logs,
)

class UsageTrackingService:
    """Service for tracking API usage and managing subscription limits."""
    
    def __init__(self, db: Session):
        self.db = db
        self.pricing_service = PricingService(db)
        # TTL cache (30s) for enforcement results to cut DB chatter
        # key: f"{user_id}:{provider}", value: { 'result': (bool,str,dict), 'expires_at': datetime }
        self._enforce_cache: Dict[str, Dict[str, Any]] = {}

    def _get_authoritative_billing_period_keys(self, user_id: str, billing_period: Optional[str] = None) -> Dict[str, Any]:
        """Return authoritative billing period lookup keys anchored to subscription period boundaries."""
        subscription = self.db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id
        ).first()

        # If caller explicitly requested a billing period, keep it authoritative for that read.
        if billing_period:
            return {
                "billing_period": billing_period,
                "lookup_periods": [billing_period],
                "period_start": subscription.current_period_start if subscription else None,
                "period_end": subscription.current_period_end if subscription else None,
            }

        if subscription and subscription.current_period_start and subscription.current_period_end:
            start_key = subscription.current_period_start.strftime("%Y-%m")
            end_key = subscription.current_period_end.strftime("%Y-%m")
            lookup_periods = [start_key] if start_key == end_key else [start_key, end_key]
            return {
                "billing_period": start_key,
                "lookup_periods": lookup_periods,
                "period_start": subscription.current_period_start,
                "period_end": subscription.current_period_end,
            }

        resolved_period = self.pricing_service.get_current_billing_period(user_id) or datetime.now().strftime("%Y-%m")
        return {
            "billing_period": resolved_period,
            "lookup_periods": [resolved_period],
            "period_start": None,
            "period_end": None,
        }
    
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
            # Use specific model names instead of generic defaults
            default_models = {
                APIProvider.GEMINI: "gemini-2.5-flash",  # Use Flash as default (cost-effective)
                APIProvider.OPENAI: "gpt-4o-mini",       # Use Mini as default (cost-effective)
                APIProvider.ANTHROPIC: "claude-3.5-sonnet",  # Use Sonnet as default
                APIProvider.MISTRAL: "openai/gpt-oss-120b:groq",  # HuggingFace default model
                APIProvider.WAVESPEED: "openai/gpt-oss-120b"  # WaveSpeed default model
            }
            
            # For HuggingFace (stored as MISTRAL), use the actual model name or default
            if provider == APIProvider.MISTRAL:
                # HuggingFace models - try to match the actual model name from model_used
                if model_used:
                    model_name = model_used
                else:
                    model_name = default_models.get(APIProvider.MISTRAL, "openai/gpt-oss-120b:groq")
            else:
                model_name = model_used or default_models.get(provider, f"{provider.value}-default")
            
            cost_data = self.pricing_service.calculate_api_cost(
                provider=provider,
                model_name=model_name,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                request_count=1,
                **kwargs
            )
            
            # Create usage log entry
            period_keys = self._get_authoritative_billing_period_keys(user_id)
            billing_period = period_keys["billing_period"]
            
            # Detect actual provider name (WaveSpeed, Google, HuggingFace, etc.)
            actual_provider_name = detect_actual_provider(
                provider_enum=provider,
                model_name=model_used,
                endpoint=endpoint
            )
            
            usage_log = APIUsageLog(
                user_id=user_id,
                provider=provider,
                endpoint=endpoint,
                method=method,
                model_used=model_used,
                actual_provider_name=actual_provider_name,  # Track actual provider
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
        period_keys = self._get_authoritative_billing_period_keys(user_id, billing_period)
        summary = self.db.query(UsageSummary).filter(
            UsageSummary.user_id == user_id,
            UsageSummary.billing_period.in_(period_keys["lookup_periods"])
        ).first()
        
        if not summary:
            summary = UsageSummary(
                user_id=user_id,
                billing_period=period_keys["billing_period"]
            )
            self.db.add(summary)
        
        # Update provider-specific counters
        provider_name = provider.value
        current_calls = getattr(summary, f"{provider_name}_calls", 0)
        setattr(summary, f"{provider_name}_calls", current_calls + 1)
        
        # Update token usage for LLM providers
        if provider in [APIProvider.GEMINI, APIProvider.OPENAI, APIProvider.ANTHROPIC, APIProvider.MISTRAL, APIProvider.WAVESPEED]:
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
        period_keys = self._get_authoritative_billing_period_keys(user_id, billing_period)
        summary = self.db.query(UsageSummary).filter(
            UsageSummary.user_id == user_id,
            UsageSummary.billing_period.in_(period_keys["lookup_periods"])
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

        if not user_id:
            logger.error("get_user_usage_stats called without user_id")
            raise ValueError("user_id is required")
        
        requested_billing_period = billing_period
        period_keys = self._get_authoritative_billing_period_keys(user_id, requested_billing_period)
        billing_period = period_keys["billing_period"]
        
        # Get usage summary
        summary = self.db.query(UsageSummary).filter(
            UsageSummary.user_id == user_id,
            UsageSummary.billing_period.in_(period_keys["lookup_periods"])
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
            # If no summary exists for current period, we should initialize it
            # This handles the "start of month" case where a user logs in but hasn't made calls yet
            if not requested_billing_period:
                logger.info(f"Initializing empty UsageSummary for user {user_id} in period {billing_period}")
                summary = UsageSummary(
                    user_id=user_id,
                    billing_period=billing_period,
                    usage_status=UsageStatus.ACTIVE,
                    total_calls=0,
                    total_tokens=0,
                    total_cost=0.0
                )
                try:
                    self.db.add(summary)
                    self.db.commit()
                    self.db.refresh(summary)
                except Exception as e:
                    logger.error(f"Failed to initialize summary: {e}")
                    self.db.rollback()
                    # Fallback to zero-struct return if DB write fails
                    pass
            
            if not summary: # Still no summary after attempt
                return build_empty_usage_response(
                    billing_period=billing_period,
                    limits=limits,
                    providers=APIProvider,
                )
        
        # Provider breakdown - calculate costs first, then use for percentages
        # Only include Gemini and HuggingFace (HuggingFace is stored under MISTRAL enum)
        provider_breakdown, resolved_costs, core_counts = build_provider_breakdown(
            db=self.db,
            user_id=user_id,
            billing_period=billing_period,
            summary=summary,
        )

        summary_total_cost = summary.total_cost or 0.0
        calculated_total_cost, final_total_cost = calculate_final_total_cost(
            summary_total_cost=summary_total_cost,
            resolved_costs=resolved_costs,
        )

        maybe_persist_reconciled_costs(
            db=self.db,
            summary=summary,
            summary_total_cost=summary_total_cost,
            calculated_total_cost=calculated_total_cost,
            final_total_cost=final_total_cost,
            resolved_costs=resolved_costs,
        )
        
        # Calculate usage percentages - only for Gemini and HuggingFace
        # Use the calculated costs for accurate percentages
        usage_percentages = build_default_usage_percentages(APIProvider)
        if limits:
            # Gemini
            gemini_call_limit = limits['limits'].get("gemini_calls", 0) or 0
            if gemini_call_limit > 0:
                usage_percentages['gemini_calls'] = (core_counts['gemini_calls'] / gemini_call_limit) * 100
            
            # HuggingFace (stored as mistral in database)
            mistral_call_limit = limits['limits'].get("mistral_calls", 0) or 0
            if mistral_call_limit > 0:
                usage_percentages['mistral_calls'] = (core_counts['mistral_calls'] / mistral_call_limit) * 100
            
            # Cost usage percentage - use final_total_cost (calculated from logs if needed)
            cost_limit = limits['limits'].get('monthly_cost', 0) or 0
            if cost_limit > 0:
                usage_percentages['cost'] = (final_total_cost / cost_limit) * 100
        
        return {
            'billing_period': billing_period,
            'usage_status': summary.usage_status.value if hasattr(summary.usage_status, 'value') else str(summary.usage_status),
            'total_calls': summary.total_calls or 0,
            'total_tokens': summary.total_tokens or 0,
            'total_cost': final_total_cost,
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
        """Get usage trends over time with self-healing from logs."""
        periods = build_billing_periods(months)
        summary_dict = query_usage_summaries(self.db, user_id, periods)
        self_heal_summaries_from_logs(self.db, user_id, periods, summary_dict)
        return build_usage_trends_response(periods, summary_dict)
    
    async def enforce_usage_limits(self, user_id: str, provider: APIProvider,
                                 tokens_requested: int = 0) -> Tuple[bool, str, Dict[str, Any]]:
        """Enforce usage limits before making an API call."""
        # Check short-lived cache first (30s)
        cache_key = f"{user_id}:{provider.value}"
        now = datetime.utcnow()
        cached = self._enforce_cache.get(cache_key)
        if cached and cached.get('expires_at') and cached['expires_at'] > now:
            return tuple(cached['result'])  # type: ignore

        result = self.pricing_service.check_usage_limits(
            user_id=user_id,
            provider=provider,
            tokens_requested=tokens_requested
        )
        self._enforce_cache[cache_key] = {
            'result': result,
            'expires_at': now + timedelta(seconds=30)
        }
        return result
    
    async def reset_current_billing_period(self, user_id: str) -> Dict[str, Any]:
        """Reset usage status and counters for the current billing period (after plan renewal/change)."""
        try:
            period_keys = self._get_authoritative_billing_period_keys(user_id)
            billing_period = period_keys["billing_period"]
            summary = self.db.query(UsageSummary).filter(
                UsageSummary.user_id == user_id,
                UsageSummary.billing_period.in_(period_keys["lookup_periods"])
            ).first()

            if not summary:
                return {"reset": False, "reason": "no_summary"}

            reset_usage_summary_counters(summary)
            self.db.commit()

            logger.info(f"Reset usage counters for user {user_id} in billing period {billing_period} after renewal")
            return {"reset": True, "counters_reset": True}
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error resetting usage status: {e}")
            return {"reset": False, "error": str(e)}
