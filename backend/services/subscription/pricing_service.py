"""
Pricing Service for API Usage Tracking
Manages API pricing, cost calculation, and subscription limits.
"""

from typing import Dict, Any, Optional, List, Tuple, Union
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from loguru import logger

from models.subscription_models import (
    APIProviderPricing, SubscriptionPlan, UserSubscription, 
    UsageSummary, APIUsageLog, APIProvider, SubscriptionTier
)

class PricingService:
    """Service for managing API pricing and cost calculations."""
    
    # Class-level cache shared across all instances (critical for cache invalidation on subscription renewal)
    # key: f"{user_id}:{provider}", value: { 'result': (bool, str, dict), 'expires_at': datetime }
    _limits_cache: Dict[str, Dict[str, Any]] = {}
    
    def __init__(self, db: Session):
        self.db = db
        self._pricing_cache = {}
        self._plans_cache = {}
        # Cache for schema feature detection (ai_text_generation_calls_limit column)
        self._ai_text_gen_col_checked: bool = False
        self._ai_text_gen_col_available: bool = False

    # ------------------- Billing period helpers -------------------
    def _compute_next_period_end(self, start: datetime, cycle: str) -> datetime:
        """Compute the next period end given a start and billing cycle."""
        try:
            cycle_value = cycle.value if hasattr(cycle, 'value') else str(cycle)
        except Exception:
            cycle_value = str(cycle)
        if cycle_value == 'yearly':
            return start + timedelta(days=365)
        return start + timedelta(days=30)

    def _ensure_subscription_current(self, subscription) -> bool:
        """Auto-advance subscription period if expired and auto_renew is enabled."""
        if not subscription:
            return False
        now = datetime.utcnow()
        try:
            if subscription.current_period_end and subscription.current_period_end < now:
                if getattr(subscription, 'auto_renew', False):
                    subscription.current_period_start = now
                    subscription.current_period_end = self._compute_next_period_end(now, subscription.billing_cycle)
                    # Keep status active if model enum else string
                    try:
                        subscription.status = subscription.status.ACTIVE  # type: ignore[attr-defined]
                    except Exception:
                        setattr(subscription, 'status', 'active')
                    self.db.commit()
                else:
                    return False
        except Exception:
            self.db.rollback()
        return True

    def get_current_billing_period(self, user_id: str) -> Optional[str]:
        """Return current billing period key (YYYY-MM) after ensuring subscription is current."""
        subscription = self.db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.is_active == True
        ).first()
        # Ensure subscription is current (advance if auto_renew)
        self._ensure_subscription_current(subscription)
        # Continue to use YYYY-MM for summaries
        return datetime.now().strftime("%Y-%m")
    
    @classmethod
    def clear_user_cache(cls, user_id: str) -> int:
        """Clear all cached limit checks for a specific user. Returns number of entries cleared."""
        keys_to_remove = [key for key in cls._limits_cache.keys() if key.startswith(f"{user_id}:")]
        for key in keys_to_remove:
            del cls._limits_cache[key]
        logger.info(f"Cleared {len(keys_to_remove)} cache entries for user {user_id}")
        return len(keys_to_remove)
        
    def initialize_default_pricing(self):
        """Initialize default pricing for all API providers."""
        
        # Gemini API Pricing (Updated as of September 2025 - Official Google AI Pricing)
        # Source: https://ai.google.dev/gemini-api/docs/pricing
        gemini_pricing = [
            # Gemini 2.5 Pro - Standard Tier
            {
                "provider": APIProvider.GEMINI,
                "model_name": "gemini-2.5-pro",
                "cost_per_input_token": 0.00000125,   # $1.25 per 1M input tokens (prompts <= 200k tokens)
                "cost_per_output_token": 0.00001,     # $10.00 per 1M output tokens (prompts <= 200k tokens)
                "description": "Gemini 2.5 Pro - State-of-the-art multipurpose model for coding and complex reasoning"
            },
            {
                "provider": APIProvider.GEMINI,
                "model_name": "gemini-2.5-pro-large",
                "cost_per_input_token": 0.0000025,    # $2.50 per 1M input tokens (prompts > 200k tokens)
                "cost_per_output_token": 0.000015,    # $15.00 per 1M output tokens (prompts > 200k tokens)
                "description": "Gemini 2.5 Pro - Large context model for prompts > 200k tokens"
            },
            # Gemini 2.5 Flash - Standard Tier
            {
                "provider": APIProvider.GEMINI,
                "model_name": "gemini-2.5-flash",
                "cost_per_input_token": 0.0000003,    # $0.30 per 1M input tokens (text/image/video)
                "cost_per_output_token": 0.0000025,   # $2.50 per 1M output tokens
                "description": "Gemini 2.5 Flash - Hybrid reasoning model with 1M token context window"
            },
            {
                "provider": APIProvider.GEMINI,
                "model_name": "gemini-2.5-flash-audio",
                "cost_per_input_token": 0.000001,     # $1.00 per 1M input tokens (audio)
                "cost_per_output_token": 0.0000025,   # $2.50 per 1M output tokens
                "description": "Gemini 2.5 Flash - Audio input model"
            },
            # Gemini 2.5 Flash-Lite - Standard Tier
            {
                "provider": APIProvider.GEMINI,
                "model_name": "gemini-2.5-flash-lite",
                "cost_per_input_token": 0.0000001,    # $0.10 per 1M input tokens (text/image/video)
                "cost_per_output_token": 0.0000004,   # $0.40 per 1M output tokens
                "description": "Gemini 2.5 Flash-Lite - Smallest and most cost-effective model for at-scale usage"
            },
            {
                "provider": APIProvider.GEMINI,
                "model_name": "gemini-2.5-flash-lite-audio",
                "cost_per_input_token": 0.0000003,    # $0.30 per 1M input tokens (audio)
                "cost_per_output_token": 0.0000004,   # $0.40 per 1M output tokens
                "description": "Gemini 2.5 Flash-Lite - Audio input model"
            },
            # Gemini 1.5 Flash - Standard Tier
            {
                "provider": APIProvider.GEMINI,
                "model_name": "gemini-1.5-flash",
                "cost_per_input_token": 0.000000075,  # $0.075 per 1M input tokens (prompts <= 128k tokens)
                "cost_per_output_token": 0.0000003,   # $0.30 per 1M output tokens (prompts <= 128k tokens)
                "description": "Gemini 1.5 Flash - Fast multimodal model with 1M token context window"
            },
            {
                "provider": APIProvider.GEMINI,
                "model_name": "gemini-1.5-flash-large",
                "cost_per_input_token": 0.00000015,   # $0.15 per 1M input tokens (prompts > 128k tokens)
                "cost_per_output_token": 0.0000006,   # $0.60 per 1M output tokens (prompts > 128k tokens)
                "description": "Gemini 1.5 Flash - Large context model for prompts > 128k tokens"
            },
            # Gemini 1.5 Flash-8B - Standard Tier
            {
                "provider": APIProvider.GEMINI,
                "model_name": "gemini-1.5-flash-8b",
                "cost_per_input_token": 0.0000000375, # $0.0375 per 1M input tokens (prompts <= 128k tokens)
                "cost_per_output_token": 0.00000015,  # $0.15 per 1M output tokens (prompts <= 128k tokens)
                "description": "Gemini 1.5 Flash-8B - Smallest model for lower intelligence use cases"
            },
            {
                "provider": APIProvider.GEMINI,
                "model_name": "gemini-1.5-flash-8b-large",
                "cost_per_input_token": 0.000000075,  # $0.075 per 1M input tokens (prompts > 128k tokens)
                "cost_per_output_token": 0.0000003,   # $0.30 per 1M output tokens (prompts > 128k tokens)
                "description": "Gemini 1.5 Flash-8B - Large context model for prompts > 128k tokens"
            },
            # Gemini 1.5 Pro - Standard Tier
            {
                "provider": APIProvider.GEMINI,
                "model_name": "gemini-1.5-pro",
                "cost_per_input_token": 0.00000125,   # $1.25 per 1M input tokens (prompts <= 128k tokens)
                "cost_per_output_token": 0.000005,    # $5.00 per 1M output tokens (prompts <= 128k tokens)
                "description": "Gemini 1.5 Pro - Highest intelligence model with 2M token context window"
            },
            {
                "provider": APIProvider.GEMINI,
                "model_name": "gemini-1.5-pro-large",
                "cost_per_input_token": 0.0000025,    # $2.50 per 1M input tokens (prompts > 128k tokens)
                "cost_per_output_token": 0.00001,     # $10.00 per 1M output tokens (prompts > 128k tokens)
                "description": "Gemini 1.5 Pro - Large context model for prompts > 128k tokens"
            },
            # Gemini Embedding - Standard Tier
            {
                "provider": APIProvider.GEMINI,
                "model_name": "gemini-embedding",
                "cost_per_input_token": 0.00000015,   # $0.15 per 1M input tokens
                "cost_per_output_token": 0.0,         # No output tokens for embeddings
                "description": "Gemini Embedding - Newest embeddings model with higher rate limits"
            },
            # Grounding with Google Search - Standard Tier
            {
                "provider": APIProvider.GEMINI,
                "model_name": "gemini-grounding-search",
                "cost_per_request": 0.035,            # $35 per 1,000 requests (after free tier)
                "cost_per_input_token": 0.0,          # No additional token cost for grounding
                "cost_per_output_token": 0.0,         # No additional token cost for grounding
                "description": "Grounding with Google Search - 1,500 RPD free, then $35/1K requests"
            }
        ]
        
        # OpenAI Pricing (estimated, will be updated)
        openai_pricing = [
            {
                "provider": APIProvider.OPENAI,
                "model_name": "gpt-4o",
                "cost_per_input_token": 0.0000025,    # $2.50 per 1M input tokens
                "cost_per_output_token": 0.00001,     # $10.00 per 1M output tokens
                "description": "GPT-4o - Latest OpenAI model"
            },
            {
                "provider": APIProvider.OPENAI,
                "model_name": "gpt-4o-mini",
                "cost_per_input_token": 0.00000015,   # $0.15 per 1M input tokens
                "cost_per_output_token": 0.0000006,   # $0.60 per 1M output tokens
                "description": "GPT-4o Mini - Cost-effective model"
            }
        ]
        
        # Anthropic Pricing (estimated, will be updated)
        anthropic_pricing = [
            {
                "provider": APIProvider.ANTHROPIC,
                "model_name": "claude-3.5-sonnet",
                "cost_per_input_token": 0.000003,     # $3.00 per 1M input tokens
                "cost_per_output_token": 0.000015,    # $15.00 per 1M output tokens
                "description": "Claude 3.5 Sonnet - Anthropic's flagship model"
            }
        ]
        
        # Search API Pricing (estimated)
        search_pricing = [
            {
                "provider": APIProvider.TAVILY,
                "model_name": "tavily-search",
                "cost_per_request": 0.001,  # $0.001 per search
                "description": "Tavily AI Search API"
            },
            {
                "provider": APIProvider.SERPER,
                "model_name": "serper-search",
                "cost_per_request": 0.001,  # $0.001 per search
                "description": "Serper Google Search API"
            },
            {
                "provider": APIProvider.METAPHOR,
                "model_name": "metaphor-search",
                "cost_per_request": 0.003,  # $0.003 per search
                "description": "Metaphor/Exa AI Search API"
            },
            {
                "provider": APIProvider.FIRECRAWL,
                "model_name": "firecrawl-extract",
                "cost_per_page": 0.002,  # $0.002 per page crawled
                "description": "Firecrawl Web Extraction API"
            },
            {
                "provider": APIProvider.STABILITY,
                "model_name": "stable-diffusion",
                "cost_per_image": 0.04,  # $0.04 per image
                "description": "Stability AI Image Generation"
            }
        ]
        
        # Combine all pricing data
        all_pricing = gemini_pricing + openai_pricing + anthropic_pricing + search_pricing
        
        # Insert pricing data
        for pricing_data in all_pricing:
            existing = self.db.query(APIProviderPricing).filter(
                APIProviderPricing.provider == pricing_data["provider"],
                APIProviderPricing.model_name == pricing_data["model_name"]
            ).first()
            
            if not existing:
                pricing = APIProviderPricing(**pricing_data)
                self.db.add(pricing)
        
        self.db.commit()
        logger.debug("Default API pricing initialized")
    
    def initialize_default_plans(self):
        """Initialize default subscription plans."""
        
        plans = [
            {
                "name": "Free",
                "tier": SubscriptionTier.FREE,
                "price_monthly": 0.0,
                "price_yearly": 0.0,
                "gemini_calls_limit": 100,
                "openai_calls_limit": 0,
                "anthropic_calls_limit": 0,
                "mistral_calls_limit": 50,
                "tavily_calls_limit": 20,
                "serper_calls_limit": 20,
                "metaphor_calls_limit": 10,
                "firecrawl_calls_limit": 10,
                "stability_calls_limit": 5,
                "gemini_tokens_limit": 100000,
                "monthly_cost_limit": 0.0,
                "features": ["basic_content_generation", "limited_research"],
                "description": "Perfect for trying out ALwrity"
            },
            {
                "name": "Basic",
                "tier": SubscriptionTier.BASIC,
                "price_monthly": 29.0,
                "price_yearly": 290.0,
                "ai_text_generation_calls_limit": 10,  # Unified limit for all LLM providers
                "gemini_calls_limit": 1000,  # Legacy, kept for backwards compatibility (not used for enforcement)
                "openai_calls_limit": 500,
                "anthropic_calls_limit": 200,
                "mistral_calls_limit": 500,
                "tavily_calls_limit": 200,
                "serper_calls_limit": 200,
                "metaphor_calls_limit": 100,
                "firecrawl_calls_limit": 100,
                "stability_calls_limit": 5,
                "gemini_tokens_limit": 2000,
                "openai_tokens_limit": 2000,
                "anthropic_tokens_limit": 2000,
                "mistral_tokens_limit": 2000,
                "monthly_cost_limit": 50.0,
                "features": ["full_content_generation", "advanced_research", "basic_analytics"],
                "description": "Great for individuals and small teams"
            },
            {
                "name": "Pro",
                "tier": SubscriptionTier.PRO,
                "price_monthly": 79.0,
                "price_yearly": 790.0,
                "gemini_calls_limit": 5000,
                "openai_calls_limit": 2500,
                "anthropic_calls_limit": 1000,
                "mistral_calls_limit": 2500,
                "tavily_calls_limit": 1000,
                "serper_calls_limit": 1000,
                "metaphor_calls_limit": 500,
                "firecrawl_calls_limit": 500,
                "stability_calls_limit": 200,
                "gemini_tokens_limit": 5000000,
                "openai_tokens_limit": 2500000,
                "anthropic_tokens_limit": 1000000,
                "mistral_tokens_limit": 2500000,
                "monthly_cost_limit": 150.0,
                "features": ["unlimited_content_generation", "premium_research", "advanced_analytics", "priority_support"],
                "description": "Perfect for growing businesses"
            },
            {
                "name": "Enterprise",
                "tier": SubscriptionTier.ENTERPRISE,
                "price_monthly": 199.0,
                "price_yearly": 1990.0,
                "gemini_calls_limit": 0,  # Unlimited
                "openai_calls_limit": 0,
                "anthropic_calls_limit": 0,
                "mistral_calls_limit": 0,
                "tavily_calls_limit": 0,
                "serper_calls_limit": 0,
                "metaphor_calls_limit": 0,
                "firecrawl_calls_limit": 0,
                "stability_calls_limit": 0,
                "gemini_tokens_limit": 0,
                "openai_tokens_limit": 0,
                "anthropic_tokens_limit": 0,
                "mistral_tokens_limit": 0,
                "monthly_cost_limit": 500.0,
                "features": ["unlimited_everything", "white_label", "dedicated_support", "custom_integrations"],
                "description": "For large organizations with high-volume needs"
            }
        ]
        
        for plan_data in plans:
            existing = self.db.query(SubscriptionPlan).filter(
                SubscriptionPlan.name == plan_data["name"]
            ).first()
            
            if not existing:
                plan = SubscriptionPlan(**plan_data)
                self.db.add(plan)
        
        self.db.commit()
        logger.debug("Default subscription plans initialized")
    
    def calculate_api_cost(self, provider: APIProvider, model_name: str, 
                          tokens_input: int = 0, tokens_output: int = 0, 
                          request_count: int = 1, **kwargs) -> Dict[str, float]:
        """Calculate cost for an API call."""
        
        # Get pricing for the provider and model
        pricing = self.db.query(APIProviderPricing).filter(
            APIProviderPricing.provider == provider,
            APIProviderPricing.model_name == model_name,
            APIProviderPricing.is_active == True
        ).first()
        
        if not pricing:
            logger.warning(f"No pricing found for {provider.value}:{model_name}, using default estimates")
            # Use default estimates
            cost_input = tokens_input * 0.000001  # $1 per 1M tokens default
            cost_output = tokens_output * 0.000001
            cost_total = (cost_input + cost_output) * request_count
        else:
            # Calculate based on actual pricing
            cost_input = tokens_input * pricing.cost_per_input_token
            cost_output = tokens_output * pricing.cost_per_output_token
            cost_request = request_count * pricing.cost_per_request
            
            # Handle special cases for non-LLM APIs
            cost_search = kwargs.get('search_count', 0) * pricing.cost_per_search
            cost_image = kwargs.get('image_count', 0) * pricing.cost_per_image
            cost_page = kwargs.get('page_count', 0) * pricing.cost_per_page
            
            cost_total = cost_input + cost_output + cost_request + cost_search + cost_image + cost_page
        
        # Round to 6 decimal places for precision
        return {
            'cost_input': round(cost_input, 6),
            'cost_output': round(cost_output, 6),
            'cost_total': round(cost_total, 6)
        }
    
    def get_user_limits(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get usage limits for a user based on their subscription."""
        
        subscription = self.db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.is_active == True
        ).first()
        
        if not subscription:
            # Return free tier limits
            free_plan = self.db.query(SubscriptionPlan).filter(
                SubscriptionPlan.tier == SubscriptionTier.FREE
            ).first()
            if free_plan:
                return self._plan_to_limits_dict(free_plan)
            return None

        # Ensure current period before returning limits
        self._ensure_subscription_current(subscription)
        return self._plan_to_limits_dict(subscription.plan)
    
    def _ensure_ai_text_gen_column_detection(self) -> None:
        """Detect at runtime whether ai_text_generation_calls_limit column exists and cache the result."""
        if self._ai_text_gen_col_checked:
            return
        try:
            # Try to query the column - if it exists, this will work
            self.db.execute(text('SELECT ai_text_generation_calls_limit FROM subscription_plans LIMIT 0'))
            self._ai_text_gen_col_available = True
        except Exception:
            self._ai_text_gen_col_available = False
        finally:
            self._ai_text_gen_col_checked = True
    
    def _plan_to_limits_dict(self, plan: SubscriptionPlan) -> Dict[str, Any]:
        """Convert subscription plan to limits dictionary."""
        # Detect if unified AI text generation limit column exists
        self._ensure_ai_text_gen_column_detection()
        
        # Use unified AI text generation limit if column exists and is set
        ai_text_gen_limit = None
        if self._ai_text_gen_col_available:
            try:
                ai_text_gen_limit = getattr(plan, 'ai_text_generation_calls_limit', None)
                # If 0, treat as not set (unlimited for Enterprise or use fallback)
                if ai_text_gen_limit == 0:
                    ai_text_gen_limit = None
            except (AttributeError, Exception):
                # Column exists but access failed - use fallback
                ai_text_gen_limit = None
        
        return {
            'plan_name': plan.name,
            'tier': plan.tier.value,
            'limits': {
                # Unified AI text generation limit (applies to all LLM providers)
                # If not set, fall back to first non-zero legacy limit for backwards compatibility
                'ai_text_generation_calls': ai_text_gen_limit if ai_text_gen_limit is not None else (
                    plan.gemini_calls_limit if plan.gemini_calls_limit > 0 else
                    plan.openai_calls_limit if plan.openai_calls_limit > 0 else
                    plan.anthropic_calls_limit if plan.anthropic_calls_limit > 0 else
                    plan.mistral_calls_limit if plan.mistral_calls_limit > 0 else 0
                ),
                # Legacy per-provider limits (for backwards compatibility and analytics)
                'gemini_calls': plan.gemini_calls_limit,
                'openai_calls': plan.openai_calls_limit,
                'anthropic_calls': plan.anthropic_calls_limit,
                'mistral_calls': plan.mistral_calls_limit,
                # Other API limits
                'tavily_calls': plan.tavily_calls_limit,
                'serper_calls': plan.serper_calls_limit,
                'metaphor_calls': plan.metaphor_calls_limit,
                'firecrawl_calls': plan.firecrawl_calls_limit,
                'stability_calls': plan.stability_calls_limit,
                # Token limits
                'gemini_tokens': plan.gemini_tokens_limit,
                'openai_tokens': plan.openai_tokens_limit,
                'anthropic_tokens': plan.anthropic_tokens_limit,
                'mistral_tokens': plan.mistral_tokens_limit,
                'monthly_cost': plan.monthly_cost_limit
            },
            'features': plan.features or []
        }
    
    def check_usage_limits(self, user_id: str, provider: APIProvider, 
                          tokens_requested: int = 0, actual_provider_name: Optional[str] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """Check if user can make an API call within their limits.
        
        Args:
            user_id: User ID
            provider: APIProvider enum (may be MISTRAL for HuggingFace)
            tokens_requested: Estimated tokens for the request
            actual_provider_name: Optional actual provider name (e.g., "huggingface" when provider is MISTRAL)
        """
        try:
            # Use actual_provider_name if provided, otherwise use enum value
            # This fixes cases where HuggingFace maps to MISTRAL enum but should show as "huggingface" in errors
            display_provider_name = actual_provider_name or provider.value
            
            logger.debug(f"[Subscription Check] Starting limit check for user {user_id}, provider {display_provider_name}, tokens {tokens_requested}")
            
            # Short TTL cache to reduce DB reads under sustained traffic
            cache_key = f"{user_id}:{provider.value}"
            now = datetime.utcnow()
            cached = self._limits_cache.get(cache_key)
            if cached and cached.get('expires_at') and cached['expires_at'] > now:
                logger.debug(f"[Subscription Check] Using cached result for {user_id}:{provider.value}")
                return tuple(cached['result'])  # type: ignore

            # Get user subscription first to check expiration
            subscription = self.db.query(UserSubscription).filter(
                UserSubscription.user_id == user_id,
                UserSubscription.is_active == True
            ).first()
            
            if subscription:
                logger.debug(f"[Subscription Check] Found subscription for user {user_id}: plan_id={subscription.plan_id}, period_end={subscription.current_period_end}")
            else:
                logger.debug(f"[Subscription Check] No active subscription found for user {user_id}")
            
            # Check subscription expiration (STRICT: deny if expired)
            if subscription:
                if subscription.current_period_end < now:
                    logger.warning(f"[Subscription Check] Subscription expired for user {user_id}: period_end={subscription.current_period_end}, now={now}")
                    # Subscription expired - check if auto_renew is enabled
                    if not getattr(subscription, 'auto_renew', False):
                        # Expired and no auto-renew - deny access
                        logger.warning(f"[Subscription Check] Subscription expired for user {user_id}, auto_renew=False, denying access")
                        result = (False, "Subscription expired. Please renew your subscription to continue using the service.", {
                            'expired': True,
                            'period_end': subscription.current_period_end.isoformat()
                        })
                        self._limits_cache[cache_key] = {
                            'result': result,
                            'expires_at': now + timedelta(seconds=30)
                        }
                        return result
                    else:
                        # Try to auto-renew
                        if not self._ensure_subscription_current(subscription):
                            # Auto-renew failed - deny access
                            result = (False, "Subscription expired and auto-renewal failed. Please renew manually.", {
                                'expired': True,
                                'auto_renew_failed': True
                            })
                            self._limits_cache[cache_key] = {
                                'result': result,
                                'expires_at': now + timedelta(seconds=30)
                            }
                            return result

            # Get user limits with error handling (STRICT: fail on errors)
            try:
                limits = self.get_user_limits(user_id)
                if limits:
                    logger.debug(f"[Subscription Check] Retrieved limits for user {user_id}: plan={limits.get('plan_name')}, tier={limits.get('tier')}")
                else:
                    logger.debug(f"[Subscription Check] No limits found for user {user_id}, checking free tier")
            except Exception as e:
                logger.error(f"[Subscription Check] Error getting user limits for {user_id}: {e}", exc_info=True)
                # STRICT: Fail closed - deny request if we can't check limits
                return False, f"Failed to retrieve subscription limits: {str(e)}", {}
            
            if not limits:
                # No subscription found - check for free tier
                free_plan = self.db.query(SubscriptionPlan).filter(
                    SubscriptionPlan.tier == SubscriptionTier.FREE,
                    SubscriptionPlan.is_active == True
                ).first()
                if free_plan:
                    logger.info(f"[Subscription Check] Assigning free tier to user {user_id}")
                    limits = self._plan_to_limits_dict(free_plan)
                else:
                    # No subscription and no free tier - deny access
                    logger.warning(f"[Subscription Check] No subscription or free tier found for user {user_id}, denying access")
                    return False, "No subscription plan found. Please subscribe to a plan.", {}
            
            # Get current usage for this billing period with error handling
            try:
                current_period = self.get_current_billing_period(user_id) or datetime.now().strftime("%Y-%m")
                usage = self.db.query(UsageSummary).filter(
                    UsageSummary.user_id == user_id,
                    UsageSummary.billing_period == current_period
                ).first()
                
                if not usage:
                    # First usage this period, create summary
                    try:
                        usage = UsageSummary(
                            user_id=user_id,
                            billing_period=current_period
                        )
                        self.db.add(usage)
                        self.db.commit()
                    except Exception as create_error:
                        logger.error(f"Error creating usage summary: {create_error}")
                        self.db.rollback()
                        # STRICT: Fail closed on DB error
                        return False, f"Failed to create usage summary: {str(create_error)}", {}
            except Exception as e:
                logger.error(f"Error getting usage summary for {user_id}: {e}")
                self.db.rollback()
                # STRICT: Fail closed on DB error
                return False, f"Failed to retrieve usage summary: {str(e)}", {}
            
            # Check call limits with error handling
            # NOTE: call_limit = 0 means UNLIMITED (Enterprise plans)
            try:
                # Use display_provider_name for error messages, but provider.value for DB queries
                provider_name = provider.value  # For DB field names (e.g., "mistral_calls", "mistral_tokens")
                
                # For LLM text generation providers, check against unified total_calls limit
                llm_providers = ['gemini', 'openai', 'anthropic', 'mistral']
                is_llm_provider = provider_name in llm_providers
                
                if is_llm_provider:
                    # Use unified AI text generation limit (total_calls across all LLM providers)
                    ai_text_gen_limit = limits['limits'].get('ai_text_generation_calls', 0) or 0
                    
                    # If unified limit not set, fall back to provider-specific limit for backwards compatibility
                    if ai_text_gen_limit == 0:
                        ai_text_gen_limit = limits['limits'].get(f"{provider_name}_calls", 0) or 0
                    
                    # Calculate total LLM provider calls (sum of gemini + openai + anthropic + mistral)
                    current_total_llm_calls = (
                        (usage.gemini_calls or 0) +
                        (usage.openai_calls or 0) +
                        (usage.anthropic_calls or 0) +
                        (usage.mistral_calls or 0)
                    )
                    
                    # Only enforce limit if limit > 0 (0 means unlimited for Enterprise)
                    if ai_text_gen_limit > 0 and current_total_llm_calls >= ai_text_gen_limit:
                        logger.error(f"[Subscription Check] AI text generation call limit exceeded for user {user_id}: {current_total_llm_calls}/{ai_text_gen_limit} (provider: {display_provider_name})")
                        result = (False, f"AI text generation call limit reached. Used {current_total_llm_calls} of {ai_text_gen_limit} total AI text generation calls this billing period.", {
                            'current_calls': current_total_llm_calls,
                            'limit': ai_text_gen_limit,
                            'usage_percentage': (current_total_llm_calls / ai_text_gen_limit) * 100 if ai_text_gen_limit > 0 else 0,
                            'provider': display_provider_name,  # Use display name for consistency
                            'usage_info': {
                                'provider': display_provider_name,  # Use display name for user-facing info
                                'current_calls': current_total_llm_calls,
                                'limit': ai_text_gen_limit,
                                'type': 'ai_text_generation',
                                'breakdown': {
                                    'gemini': usage.gemini_calls or 0,
                                    'openai': usage.openai_calls or 0,
                                    'anthropic': usage.anthropic_calls or 0,
                                    'mistral': usage.mistral_calls or 0  # DB field name (not display name)
                                }
                            }
                        })
                        self._limits_cache[cache_key] = {
                            'result': result,
                            'expires_at': now + timedelta(seconds=30)
                        }
                        return result
                    else:
                        logger.debug(f"[Subscription Check] AI text generation limit check passed for user {user_id}: {current_total_llm_calls}/{ai_text_gen_limit if ai_text_gen_limit > 0 else 'unlimited'} (provider: {display_provider_name})")
                else:
                    # For non-LLM providers, check provider-specific limit
                    current_calls = getattr(usage, f"{provider_name}_calls", 0) or 0
                    call_limit = limits['limits'].get(f"{provider_name}_calls", 0) or 0
                    
                    # Only enforce limit if limit > 0 (0 means unlimited for Enterprise)
                    if call_limit > 0 and current_calls >= call_limit:
                        logger.error(f"[Subscription Check] Call limit exceeded for user {user_id}, provider {display_provider_name}: {current_calls}/{call_limit}")
                        result = (False, f"API call limit reached for {display_provider_name}. Used {current_calls} of {call_limit} calls this billing period.", {
                            'current_calls': current_calls,
                            'limit': call_limit,
                            'usage_percentage': 100.0,
                            'provider': display_provider_name  # Use display name for consistency
                        })
                        self._limits_cache[cache_key] = {
                            'result': result,
                            'expires_at': now + timedelta(seconds=30)
                        }
                        return result
                    else:
                        logger.debug(f"[Subscription Check] Call limit check passed for user {user_id}, provider {display_provider_name}: {current_calls}/{call_limit if call_limit > 0 else 'unlimited'}")
            except Exception as e:
                logger.error(f"Error checking call limits: {e}")
                # Continue to next check
            
            # Check token limits for LLM providers with error handling
            # NOTE: token_limit = 0 means UNLIMITED (Enterprise plans)
            try:
                if provider in [APIProvider.GEMINI, APIProvider.OPENAI, APIProvider.ANTHROPIC, APIProvider.MISTRAL]:
                    current_tokens = getattr(usage, f"{provider_name}_tokens", 0) or 0
                    token_limit = limits['limits'].get(f"{provider_name}_tokens", 0) or 0
                    
                    # Only enforce limit if limit > 0 (0 means unlimited for Enterprise)
                    if token_limit > 0 and (current_tokens + tokens_requested) > token_limit:
                        result = (False, f"Token limit would be exceeded for {display_provider_name}. Current: {current_tokens}, Requested: {tokens_requested}, Limit: {token_limit}", {
                            'current_tokens': current_tokens,
                            'requested_tokens': tokens_requested,
                            'limit': token_limit,
                            'usage_percentage': ((current_tokens + tokens_requested) / token_limit) * 100,
                            'provider': display_provider_name,  # Use display name in error details
                            'usage_info': {
                                'provider': display_provider_name,
                                'current_tokens': current_tokens,
                                'requested_tokens': tokens_requested,
                                'limit': token_limit,
                                'type': 'tokens'
                            }
                        })
                        self._limits_cache[cache_key] = {
                            'result': result,
                            'expires_at': now + timedelta(seconds=30)
                        }
                        return result
            except Exception as e:
                logger.error(f"Error checking token limits: {e}")
                # Continue to next check
            
            # Check cost limits with error handling
            # NOTE: cost_limit = 0 means UNLIMITED (Enterprise plans)
            try:
                cost_limit = limits['limits'].get('monthly_cost', 0) or 0
                # Only enforce limit if limit > 0 (0 means unlimited for Enterprise)
                if cost_limit > 0 and usage.total_cost >= cost_limit:
                    result = (False, f"Monthly cost limit reached. Current cost: ${usage.total_cost:.2f}, Limit: ${cost_limit:.2f}", {
                        'current_cost': usage.total_cost,
                        'limit': cost_limit,
                        'usage_percentage': 100.0
                    })
                    self._limits_cache[cache_key] = {
                        'result': result,
                        'expires_at': now + timedelta(seconds=30)
                    }
                    return result
            except Exception as e:
                logger.error(f"Error checking cost limits: {e}")
                # Continue to success case
            
            # Calculate usage percentages for warnings
            try:
                # Determine which call variables to use based on provider type
                if is_llm_provider:
                    # Use unified LLM call tracking
                    current_call_count = current_total_llm_calls
                    call_limit_value = ai_text_gen_limit
                else:
                    # Use provider-specific call tracking
                    current_call_count = current_calls
                    call_limit_value = call_limit
                
                call_usage_pct = (current_call_count / max(call_limit_value, 1)) * 100 if call_limit_value > 0 else 0
                cost_usage_pct = (usage.total_cost / max(cost_limit, 1)) * 100 if cost_limit > 0 else 0
                result = (True, "Within limits", {
                    'current_calls': current_call_count,
                    'call_limit': call_limit_value,
                    'call_usage_percentage': call_usage_pct,
                    'current_cost': usage.total_cost,
                    'cost_limit': cost_limit,
                    'cost_usage_percentage': cost_usage_pct
                })
                self._limits_cache[cache_key] = {
                    'result': result,
                    'expires_at': now + timedelta(seconds=30)
                }
                return result
            except Exception as e:
                logger.error(f"Error calculating usage percentages: {e}")
                # Return basic success
                return True, "Within limits", {}
        
        except Exception as e:
            logger.error(f"Unexpected error in check_usage_limits for {user_id}: {e}")
            # STRICT: Fail closed - deny requests if subscription system fails
            return False, f"Subscription check error: {str(e)}", {}
    
    def estimate_tokens(self, text: str, provider: APIProvider) -> int:
        """Estimate token count for text based on provider."""
        
        # Get pricing info for token estimation
        pricing = self.db.query(APIProviderPricing).filter(
            APIProviderPricing.provider == provider,
            APIProviderPricing.is_active == True
        ).first()
        
        if pricing and pricing.tokens_per_word:
            # Use provider-specific conversion
            word_count = len(text.split())
            return int(word_count * pricing.tokens_per_word)
        else:
            # Use default estimation (roughly 1.3 tokens per word for most models)
            word_count = len(text.split())
            return int(word_count * 1.3)
    
    def get_pricing_info(self, provider: APIProvider, model_name: str = None) -> Optional[Dict[str, Any]]:
        """Get pricing information for a provider/model."""
        
        query = self.db.query(APIProviderPricing).filter(
            APIProviderPricing.provider == provider,
            APIProviderPricing.is_active == True
        )
        
        if model_name:
            query = query.filter(APIProviderPricing.model_name == model_name)
        
        pricing = query.first()
        
        if not pricing:
            return None
        
    def check_comprehensive_limits(
        self, 
        user_id: str, 
        operations: List[Dict[str, Any]]
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Comprehensive pre-flight validation that checks ALL limits before making ANY API calls.
        
        This prevents wasteful API calls by validating that ALL subsequent operations will succeed
        before making the first external API call.
        
        Args:
            user_id: User ID
            operations: List of operations to validate, each with:
                - 'provider': APIProvider enum
                - 'tokens_requested': int (estimated tokens for LLM calls, 0 for non-LLM)
                - 'actual_provider_name': Optional[str] (e.g., "huggingface" when provider is MISTRAL)
                - 'operation_type': str (e.g., "google_grounding", "llm_call", "image_generation")
        
        Returns:
            (can_proceed, error_message, error_details)
            If can_proceed is False, error_message explains which limit would be exceeded
        """
        try:
            logger.info(f"[Pre-flight Check] 🔍 Starting comprehensive validation for user {user_id}")
            logger.info(f"[Pre-flight Check] 📋 Validating {len(operations)} operation(s) before making any API calls")
            
            # Get current usage and limits once
            current_period = self.get_current_billing_period(user_id) or datetime.now().strftime("%Y-%m")
            usage = self.db.query(UsageSummary).filter(
                UsageSummary.user_id == user_id,
                UsageSummary.billing_period == current_period
            ).first()
            
            if not usage:
                # First usage this period, create summary
                try:
                    usage = UsageSummary(
                        user_id=user_id,
                        billing_period=current_period
                    )
                    self.db.add(usage)
                    self.db.commit()
                except Exception as create_error:
                    logger.error(f"Error creating usage summary: {create_error}")
                    self.db.rollback()
                    return False, f"Failed to create usage summary: {str(create_error)}", {}
            
            # Get user limits
            limits_dict = self.get_user_limits(user_id)
            if not limits_dict:
                # No subscription found - check for free tier
                free_plan = self.db.query(SubscriptionPlan).filter(
                    SubscriptionPlan.tier == SubscriptionTier.FREE,
                    SubscriptionPlan.is_active == True
                ).first()
                if free_plan:
                    limits_dict = self._plan_to_limits_dict(free_plan)
                else:
                    return False, "No subscription plan found. Please subscribe to a plan.", {}
            
            limits = limits_dict.get('limits', {})
            
            # Track cumulative usage across all operations
            total_llm_calls = (
                (usage.gemini_calls or 0) +
                (usage.openai_calls or 0) +
                (usage.anthropic_calls or 0) +
                (usage.mistral_calls or 0)
            )
            total_llm_tokens = {}
            total_images = usage.stability_calls or 0
            
            # Log current usage summary
            logger.info(f"[Pre-flight Check] 📊 Current Usage Summary:")
            logger.info(f"   └─ Total LLM Calls: {total_llm_calls}")
            logger.info(f"   └─ Gemini Tokens: {usage.gemini_tokens or 0}, Mistral/HF Tokens: {usage.mistral_tokens or 0}")
            logger.info(f"   └─ Image Calls: {total_images}")
            
            # Validate each operation
            for op_idx, operation in enumerate(operations):
                provider = operation.get('provider')
                provider_name = provider.value if hasattr(provider, 'value') else str(provider)
                tokens_requested = operation.get('tokens_requested', 0)
                actual_provider_name = operation.get('actual_provider_name')
                operation_type = operation.get('operation_type', 'unknown')
                
                display_provider_name = actual_provider_name or provider_name
                
                logger.info(f"[Pre-flight Check] ✅ Operation {op_idx + 1}/{len(operations)}: {operation_type}")
                logger.info(f"   ├─ Provider: {display_provider_name} (enum: {provider_name})")
                logger.info(f"   └─ Estimated Tokens: {tokens_requested}")
                
                # Check if this is an LLM provider
                llm_providers = ['gemini', 'openai', 'anthropic', 'mistral']
                is_llm_provider = provider_name in llm_providers
                
                # Check unified AI text generation limit for LLM providers
                if is_llm_provider:
                    ai_text_gen_limit = limits.get('ai_text_generation_calls', 0) or 0
                    if ai_text_gen_limit == 0:
                        # Fallback to provider-specific limit
                        ai_text_gen_limit = limits.get(f"{provider_name}_calls", 0) or 0
                    
                    # Count this operation as an LLM call
                    projected_total_llm_calls = total_llm_calls + 1
                    
                    if ai_text_gen_limit > 0 and projected_total_llm_calls > ai_text_gen_limit:
                        error_info = {
                            'current_calls': total_llm_calls,
                            'limit': ai_text_gen_limit,
                            'provider': display_provider_name,
                            'operation_type': operation_type,
                            'operation_index': op_idx
                        }
                        return False, f"AI text generation call limit would be exceeded. Would use {projected_total_llm_calls} of {ai_text_gen_limit} total AI text generation calls.", {
                            'error_type': 'call_limit',
                            'usage_info': error_info
                        }
                    
                    # Check token limits for this provider
                    # Use cumulative projected tokens from previous operations, or current from DB if first operation
                    provider_tokens_key = f"{provider_name}_tokens"
                    if provider_tokens_key in total_llm_tokens:
                        # Use cumulative projected tokens from previous operations
                        current_provider_tokens = total_llm_tokens[provider_tokens_key]
                        logger.info(f"   └─ Using cumulative projected tokens: {current_provider_tokens}")
                    else:
                        # First operation for this provider - get current from database
                        current_provider_tokens = getattr(usage, provider_tokens_key, 0) or 0
                        total_llm_tokens[provider_tokens_key] = current_provider_tokens
                        logger.info(f"   └─ Current tokens from DB: {current_provider_tokens}")
                    
                    token_limit = limits.get(provider_tokens_key, 0) or 0
                    
                    if token_limit > 0 and tokens_requested > 0:
                        projected_tokens = current_provider_tokens + tokens_requested
                        logger.info(f"   └─ Token Check: {current_provider_tokens} (current) + {tokens_requested} (requested) = {projected_tokens} (total) / {token_limit} (limit)")
                        
                        if projected_tokens > token_limit:
                            usage_percentage = (projected_tokens / token_limit) * 100 if token_limit > 0 else 0
                            error_info = {
                                'current_tokens': current_provider_tokens,
                                'requested_tokens': tokens_requested,
                                'limit': token_limit,
                                'provider': display_provider_name,
                                'operation_type': operation_type,
                                'operation_index': op_idx
                            }
                            error_msg = (
                                f"Token limit exceeded for {display_provider_name} "
                                f"({operation_type}). "
                                f"Current: {current_provider_tokens}/{token_limit}, "
                                f"Requested: {tokens_requested}, "
                                f"Would exceed by: {projected_tokens - token_limit} tokens "
                                f"({usage_percentage:.1f}% of limit)"
                            )
                            logger.error(f"[Pre-flight Check] ❌ BLOCKED: {error_msg}")
                            return False, error_msg, {
                                'error_type': 'token_limit',
                                'usage_info': error_info
                            }
                        else:
                            logger.info(f"   └─ ✅ Token limit check passed: {projected_tokens} <= {token_limit}")
                    
                    # Update cumulative counts for next operation
                    total_llm_calls = projected_total_llm_calls
                    total_llm_tokens[provider_tokens_key] += tokens_requested
                    logger.info(f"   └─ Updated cumulative tokens for {display_provider_name}: {total_llm_tokens[provider_tokens_key]}")
                
                # Check image generation limits
                elif provider == APIProvider.STABILITY:
                    image_limit = limits.get('stability_calls', 0) or 0
                    projected_images = total_images + 1
                    
                    if image_limit > 0 and projected_images > image_limit:
                        error_info = {
                            'current_images': total_images,
                            'limit': image_limit,
                            'provider': 'stability',
                            'operation_type': operation_type,
                            'operation_index': op_idx
                        }
                        return False, f"Image generation limit would be exceeded. Would use {projected_images} of {image_limit} images this billing period.", {
                            'error_type': 'image_limit',
                            'usage_info': error_info
                        }
                    
                    total_images = projected_images
                
                # Check other provider-specific limits
                else:
                    provider_calls_key = f"{provider_name}_calls"
                    current_provider_calls = getattr(usage, provider_calls_key, 0) or 0
                    call_limit = limits.get(provider_calls_key, 0) or 0
                    
                    if call_limit > 0:
                        projected_calls = current_provider_calls + 1
                        if projected_calls > call_limit:
                            error_info = {
                                'current_calls': current_provider_calls,
                                'limit': call_limit,
                                'provider': display_provider_name,
                                'operation_type': operation_type,
                                'operation_index': op_idx
                            }
                            return False, f"API call limit would be exceeded for {display_provider_name}. Would use {projected_calls} of {call_limit} calls this billing period.", {
                                'error_type': 'call_limit',
                                'usage_info': error_info
                            }
            
            # All checks passed
            logger.info(f"[Pre-flight Check] ✅ All {len(operations)} operation(s) validated successfully")
            logger.info(f"[Pre-flight Check] ✅ User {user_id} is cleared to proceed with API calls")
            return True, None, None
            
        except Exception as e:
            logger.error(f"[Pre-flight Check] Error during comprehensive limit check: {e}", exc_info=True)
            return False, f"Failed to validate limits: {str(e)}", {}
    
    def get_pricing_for_provider_model(self, provider: APIProvider, model_name: str) -> Optional[Dict[str, Any]]:
        """Get pricing configuration for a specific provider and model."""
        pricing = self.db.query(APIProviderPricing).filter(
            APIProviderPricing.provider == provider,
            APIProviderPricing.model_name == model_name
        ).first()
        
        if not pricing:
            return None
        
        return {
            'provider': pricing.provider.value,
            'model_name': pricing.model_name,
            'cost_per_input_token': pricing.cost_per_input_token,
            'cost_per_output_token': pricing.cost_per_output_token,
            'cost_per_request': pricing.cost_per_request,
            'cost_per_search': pricing.cost_per_search,
            'cost_per_image': pricing.cost_per_image,
            'cost_per_page': pricing.cost_per_page,
            'description': pricing.description
        }
