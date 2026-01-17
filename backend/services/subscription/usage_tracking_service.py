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
from loguru import logger
import json

from models.subscription_models import (
    APIUsageLog, UsageSummary, APIProvider, UsageAlert, 
    UserSubscription, UsageStatus
)
from .pricing_service import PricingService
from .provider_detection import detect_actual_provider

class UsageTrackingService:
    """Service for tracking API usage and managing subscription limits."""
    
    def __init__(self, db: Session):
        self.db = db
        self.pricing_service = PricingService(db)
        # TTL cache (30s) for enforcement results to cut DB chatter
        # key: f"{user_id}:{provider}", value: { 'result': (bool,str,dict), 'expires_at': datetime }
        self._enforce_cache: Dict[str, Dict[str, Any]] = {}
    
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
                "gemini": "gemini-2.5-flash",  # Use Flash as default (cost-effective)
                "openai": "gpt-4o-mini",       # Use Mini as default (cost-effective)
                "anthropic": "claude-3.5-sonnet",  # Use Sonnet as default
                "mistral": "openai/gpt-oss-120b:groq"  # HuggingFace default model
            }
            
            # For HuggingFace (stored as MISTRAL), use the actual model name or default
            if provider == APIProvider.MISTRAL:
                # HuggingFace models - try to match the actual model name from model_used
                if model_used:
                    model_name = model_used
                else:
                    model_name = default_models.get("mistral", "openai/gpt-oss-120b:groq")
            else:
                model_name = model_used or default_models.get(provider.value, f"{provider.value}-default")
            
            cost_data = self.pricing_service.calculate_api_cost(
                provider=provider,
                model_name=model_name,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                request_count=1,
                **kwargs
            )
            
            # Create usage log entry
            billing_period = self.pricing_service.get_current_billing_period(user_id) or datetime.now().strftime("%Y-%m")
            
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
            billing_period = self.pricing_service.get_current_billing_period(user_id) or datetime.now().strftime("%Y-%m")
        
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
                'usage_percentages': {}
            }
        
        # Provider breakdown - calculate costs first, then use for percentages
        # Only include Gemini and HuggingFace (HuggingFace is stored under MISTRAL enum)
        provider_breakdown = {}
        
        # Gemini
        gemini_calls = getattr(summary, "gemini_calls", 0) or 0
        gemini_tokens = getattr(summary, "gemini_tokens", 0) or 0
        gemini_cost = getattr(summary, "gemini_cost", 0.0) or 0.0
        
        # If gemini cost is 0 but there are calls, calculate from usage logs
        if gemini_calls > 0 and gemini_cost == 0.0:
            gemini_logs = self.db.query(APIUsageLog).filter(
                APIUsageLog.user_id == user_id,
                APIUsageLog.provider == APIProvider.GEMINI,
                APIUsageLog.billing_period == billing_period
            ).all()
            if gemini_logs:
                gemini_cost = sum(float(log.cost_total or 0.0) for log in gemini_logs)
                logger.info(f"[UsageStats] Calculated gemini cost from {len(gemini_logs)} logs: ${gemini_cost:.6f}")
        
        provider_breakdown['gemini'] = {
            'calls': gemini_calls,
            'tokens': gemini_tokens,
            'cost': gemini_cost
        }
        
        # HuggingFace (stored as MISTRAL in database)
        mistral_calls = getattr(summary, "mistral_calls", 0) or 0
        mistral_tokens = getattr(summary, "mistral_tokens", 0) or 0
        mistral_cost = getattr(summary, "mistral_cost", 0.0) or 0.0
        
        # If mistral (HuggingFace) cost is 0 but there are calls, calculate from usage logs
        if mistral_calls > 0 and mistral_cost == 0.0:
            mistral_logs = self.db.query(APIUsageLog).filter(
                APIUsageLog.user_id == user_id,
                APIUsageLog.provider == APIProvider.MISTRAL,
                APIUsageLog.billing_period == billing_period
            ).all()
            if mistral_logs:
                mistral_cost = sum(float(log.cost_total or 0.0) for log in mistral_logs)
                logger.info(f"[UsageStats] Calculated mistral (HuggingFace) cost from {len(mistral_logs)} logs: ${mistral_cost:.6f}")
        
        provider_breakdown['huggingface'] = {
            'calls': mistral_calls,
            'tokens': mistral_tokens,
            'cost': mistral_cost
        }
        
        # Add other providers (Video, Audio, Image, Image Edit) for comprehensive breakdown
        # Video (WaveSpeed, HuggingFace, etc.)
        video_calls = getattr(summary, "video_calls", 0) or 0
        video_cost = getattr(summary, "video_cost", 0.0) or 0.0
        if video_calls > 0 and video_cost == 0.0:
            video_logs = self.db.query(APIUsageLog).filter(
                APIUsageLog.user_id == user_id,
                APIUsageLog.provider == APIProvider.VIDEO,
                APIUsageLog.billing_period == billing_period
            ).all()
            if video_logs:
                video_cost = sum(float(log.cost_total or 0.0) for log in video_logs)
        
        provider_breakdown['video'] = {
            'calls': video_calls,
            'tokens': 0,
            'cost': video_cost
        }
        
        # Audio (WaveSpeed, etc.)
        audio_calls = getattr(summary, "audio_calls", 0) or 0
        audio_cost = getattr(summary, "audio_cost", 0.0) or 0.0
        if audio_calls > 0 and audio_cost == 0.0:
            audio_logs = self.db.query(APIUsageLog).filter(
                APIUsageLog.user_id == user_id,
                APIUsageLog.provider == APIProvider.AUDIO,
                APIUsageLog.billing_period == billing_period
            ).all()
            if audio_logs:
                audio_cost = sum(float(log.cost_total or 0.0) for log in audio_logs)
        
        provider_breakdown['audio'] = {
            'calls': audio_calls,
            'tokens': 0,
            'cost': audio_cost
        }
        
        # Image Generation (Stability/WaveSpeed)
        stability_calls = getattr(summary, "stability_calls", 0) or 0
        stability_cost = getattr(summary, "stability_cost", 0.0) or 0.0
        if stability_calls > 0 and stability_cost == 0.0:
            stability_logs = self.db.query(APIUsageLog).filter(
                APIUsageLog.user_id == user_id,
                APIUsageLog.provider == APIProvider.STABILITY,
                APIUsageLog.billing_period == billing_period
            ).all()
            if stability_logs:
                stability_cost = sum(float(log.cost_total or 0.0) for log in stability_logs)
        
        provider_breakdown['image'] = {
            'calls': stability_calls,
            'tokens': 0,
            'cost': stability_cost
        }
        
        # Image Editing (WaveSpeed)
        image_edit_calls = getattr(summary, "image_edit_calls", 0) or 0
        image_edit_cost = getattr(summary, "image_edit_cost", 0.0) or 0.0
        if image_edit_calls > 0 and image_edit_cost == 0.0:
            image_edit_logs = self.db.query(APIUsageLog).filter(
                APIUsageLog.user_id == user_id,
                APIUsageLog.provider == APIProvider.IMAGE_EDIT,
                APIUsageLog.billing_period == billing_period
            ).all()
            if image_edit_logs:
                image_edit_cost = sum(float(log.cost_total or 0.0) for log in image_edit_logs)
        
        provider_breakdown['image_edit'] = {
            'calls': image_edit_calls,
            'tokens': 0,
            'cost': image_edit_cost
        }
        
        # Search APIs
        tavily_calls = getattr(summary, "tavily_calls", 0) or 0
        tavily_cost = getattr(summary, "tavily_cost", 0.0) or 0.0
        provider_breakdown['tavily'] = {
            'calls': tavily_calls,
            'tokens': 0,
            'cost': tavily_cost
        }
        
        serper_calls = getattr(summary, "serper_calls", 0) or 0
        serper_cost = getattr(summary, "serper_cost", 0.0) or 0.0
        provider_breakdown['serper'] = {
            'calls': serper_calls,
            'tokens': 0,
            'cost': serper_cost
        }
        
        exa_calls = getattr(summary, "exa_calls", 0) or 0
        exa_cost = getattr(summary, "exa_cost", 0.0) or 0.0
        provider_breakdown['exa'] = {
            'calls': exa_calls,
            'tokens': 0,
            'cost': exa_cost
        }
        
        # Calculate total cost from provider breakdown if summary total_cost is 0
        calculated_total_cost = (
            gemini_cost + mistral_cost + video_cost + audio_cost + 
            stability_cost + image_edit_cost + tavily_cost + serper_cost + exa_cost
        )
        summary_total_cost = summary.total_cost or 0.0
        # Use calculated cost if summary cost is 0, otherwise use summary cost (it's more accurate)
        final_total_cost = summary_total_cost if summary_total_cost > 0 else calculated_total_cost
        
        # If we calculated costs from logs, update the summary for future requests
        if calculated_total_cost > 0 and summary_total_cost == 0.0:
            logger.info(f"[UsageStats] Updating summary costs: total_cost={final_total_cost:.6f}, gemini_cost={gemini_cost:.6f}, mistral_cost={mistral_cost:.6f}, video_cost={video_cost:.6f}, audio_cost={audio_cost:.6f}, image_cost={stability_cost:.6f}")
            summary.total_cost = final_total_cost
            summary.gemini_cost = gemini_cost
            summary.mistral_cost = mistral_cost
            # Update other provider costs if they exist
            if hasattr(summary, 'video_cost'):
                summary.video_cost = video_cost
            if hasattr(summary, 'audio_cost'):
                summary.audio_cost = audio_cost
            if hasattr(summary, 'stability_cost'):
                summary.stability_cost = stability_cost
            if hasattr(summary, 'image_edit_cost'):
                summary.image_edit_cost = image_edit_cost
            try:
                self.db.commit()
            except Exception as e:
                logger.error(f"[UsageStats] Error updating summary costs: {e}")
                self.db.rollback()
        
        # Calculate usage percentages - only for Gemini and HuggingFace
        # Use the calculated costs for accurate percentages
        usage_percentages = {}
        if limits:
            # Gemini
            gemini_call_limit = limits['limits'].get("gemini_calls", 0) or 0
            if gemini_call_limit > 0:
                usage_percentages['gemini_calls'] = (gemini_calls / gemini_call_limit) * 100
            else:
                usage_percentages['gemini_calls'] = 0
            
            # HuggingFace (stored as mistral in database)
            mistral_call_limit = limits['limits'].get("mistral_calls", 0) or 0
            if mistral_call_limit > 0:
                usage_percentages['mistral_calls'] = (mistral_calls / mistral_call_limit) * 100
            else:
                usage_percentages['mistral_calls'] = 0
            
            # Cost usage percentage - use final_total_cost (calculated from logs if needed)
            cost_limit = limits['limits'].get('monthly_cost', 0) or 0
            if cost_limit > 0:
                usage_percentages['cost'] = (final_total_cost / cost_limit) * 100
            else:
                usage_percentages['cost'] = 0
        
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
            billing_period = datetime.now().strftime("%Y-%m")
            summary = self.db.query(UsageSummary).filter(
                UsageSummary.user_id == user_id,
                UsageSummary.billing_period == billing_period
            ).first()

            if not summary:
                # Nothing to reset
                return {"reset": False, "reason": "no_summary"}

            # CRITICAL: Reset ALL usage counters to 0 so user gets fresh limits with new/renewed plan
            # Clear LIMIT_REACHED status
            summary.usage_status = UsageStatus.ACTIVE
            
            # Reset all LLM provider call counters
            summary.gemini_calls = 0
            summary.openai_calls = 0
            summary.anthropic_calls = 0
            summary.mistral_calls = 0
            
            # Reset all LLM provider token counters
            summary.gemini_tokens = 0
            summary.openai_tokens = 0
            summary.anthropic_tokens = 0
            summary.mistral_tokens = 0
            
            # Reset search/research provider counters
            summary.tavily_calls = 0
            summary.serper_calls = 0
            summary.metaphor_calls = 0
            summary.firecrawl_calls = 0
            
            # Reset image generation counters
            summary.stability_calls = 0
            
            # Reset video generation counters
            summary.video_calls = 0
            
            # Reset image editing counters
            summary.image_edit_calls = 0
            
            # Reset cost counters
            summary.gemini_cost = 0.0
            summary.openai_cost = 0.0
            summary.anthropic_cost = 0.0
            summary.mistral_cost = 0.0
            summary.tavily_cost = 0.0
            summary.serper_cost = 0.0
            summary.metaphor_cost = 0.0
            summary.firecrawl_cost = 0.0
            summary.stability_cost = 0.0
            summary.exa_cost = 0.0
            summary.video_cost = 0.0
            summary.image_edit_cost = 0.0
            
            # Reset totals
            summary.total_calls = 0
            summary.total_tokens = 0
            summary.total_cost = 0.0
            
            summary.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Reset usage counters for user {user_id} in billing period {billing_period} after renewal")
            return {"reset": True, "counters_reset": True}
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error resetting usage status: {e}")
            return {"reset": False, "error": str(e)}
