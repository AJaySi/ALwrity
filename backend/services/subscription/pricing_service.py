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
            },
            {
                "provider": APIProvider.EXA,
                "model_name": "exa-search",
                "cost_per_request": 0.005,  # $0.005 per search (1-25 results)
                "description": "Exa Neural Search API"
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
                "exa_calls_limit": 100,
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
                "exa_calls_limit": 500,
                "gemini_tokens_limit": 20000,  # Increased from 5000 for better stability
                "openai_tokens_limit": 20000,  # Increased from 5000 for better stability
                "anthropic_tokens_limit": 20000,  # Increased from 5000 for better stability
                "mistral_tokens_limit": 20000,  # Increased from 5000 for better stability
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
                "exa_calls_limit": 2000,
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
                "exa_calls_limit": 0,  # Unlimited
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
        
        # CRITICAL: Expire all objects first to ensure fresh data after renewal
        self.db.expire_all()
        
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
        
        # CRITICAL: Refresh subscription to get latest plan_id, then refresh plan relationship
        self.db.refresh(subscription)
        
        # Re-query plan directly to ensure fresh data (bypass relationship cache)
        plan = self.db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == subscription.plan_id
        ).first()
        
        if not plan:
            logger.error(f"Plan not found for subscription plan_id={subscription.plan_id}")
            return None
        
        # Refresh plan to ensure fresh limits
        self.db.refresh(plan)
        
        return self._plan_to_limits_dict(plan)
    
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
        
        Delegates to LimitValidator for actual validation logic.
        
        Args:
            user_id: User ID
            provider: APIProvider enum (may be MISTRAL for HuggingFace)
            tokens_requested: Estimated tokens for the request
            actual_provider_name: Optional actual provider name (e.g., "huggingface" when provider is MISTRAL)
        
        Returns:
            (can_proceed, error_message, usage_info)
        """
        from .limit_validation import LimitValidator
        validator = LimitValidator(self)
        return validator.check_usage_limits(user_id, provider, tokens_requested, actual_provider_name)
    
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
        
        # Return pricing info as dict
        return {
            'provider': pricing.provider.value,
            'model_name': pricing.model_name,
            'cost_per_input_token': pricing.cost_per_input_token,
            'cost_per_output_token': pricing.cost_per_output_token,
            'cost_per_request': pricing.cost_per_request,
            'description': pricing.description
        }
    
    def check_comprehensive_limits(
        self, 
        user_id: str, 
        operations: List[Dict[str, Any]]
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Comprehensive pre-flight validation that checks ALL limits before making ANY API calls.
        
        Delegates to LimitValidator for actual validation logic.
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
        from .limit_validation import LimitValidator
        validator = LimitValidator(self)
        return validator.check_comprehensive_limits(user_id, operations)
    
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
