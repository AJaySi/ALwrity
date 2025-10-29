#!/usr/bin/env python3
"""
Initialize Alpha Tester Subscription Tiers
Creates subscription plans for alpha testing with appropriate limits.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from models.subscription_models import (
    SubscriptionPlan, SubscriptionTier, APIProviderPricing, APIProvider
)
from services.database import get_db_session
from datetime import datetime
from loguru import logger

def create_alpha_subscription_tiers():
    """Create subscription tiers for alpha testers."""
    if os.getenv('ENABLE_ALPHA', 'false').lower() not in {'1','true','yes','on'}:
        logger.info("Alpha tier initialization is disabled (ENABLE_ALPHA is false)")
        return False
    
    db = get_db_session()
    if not db:
        logger.error("❌ Could not get database session")
        return False
    
    try:
        # Define alpha subscription tiers
        alpha_tiers = [
            {
                "name": "Free Alpha",
                "tier": SubscriptionTier.FREE,
                "price_monthly": 0.0,
                "price_yearly": 0.0,
                "description": "Free tier for alpha testing - Limited usage",
                "features": ["blog_writer", "basic_seo", "content_planning"],
                "limits": {
                    "gemini_calls_limit": 50,      # 50 calls per day
                    "gemini_tokens_limit": 10000,  # 10k tokens per day
                    "tavily_calls_limit": 20,      # 20 searches per day
                    "serper_calls_limit": 10,      # 10 SEO searches per day
                    "stability_calls_limit": 5,    # 5 images per day
                    "monthly_cost_limit": 5.0      # $5 monthly limit
                }
            },
            {
                "name": "Basic Alpha",
                "tier": SubscriptionTier.BASIC,
                "price_monthly": 29.0,
                "price_yearly": 290.0,
                "description": "Basic alpha tier - Moderate usage for testing",
                "features": ["blog_writer", "seo_analysis", "content_planning", "strategy_copilot"],
                "limits": {
                    "gemini_calls_limit": 200,     # 200 calls per day
                    "gemini_tokens_limit": 50000,  # 50k tokens per day
                    "tavily_calls_limit": 100,     # 100 searches per day
                    "serper_calls_limit": 50,      # 50 SEO searches per day
                    "stability_calls_limit": 25,   # 25 images per day
                    "monthly_cost_limit": 25.0     # $25 monthly limit
                }
            },
            {
                "name": "Pro Alpha",
                "tier": SubscriptionTier.PRO,
                "price_monthly": 99.0,
                "price_yearly": 990.0,
                "description": "Pro alpha tier - High usage for power users",
                "features": ["blog_writer", "seo_analysis", "content_planning", "strategy_copilot", "advanced_analytics"],
                "limits": {
                    "gemini_calls_limit": 500,     # 500 calls per day
                    "gemini_tokens_limit": 150000, # 150k tokens per day
                    "tavily_calls_limit": 300,     # 300 searches per day
                    "serper_calls_limit": 150,     # 150 SEO searches per day
                    "stability_calls_limit": 100,  # 100 images per day
                    "monthly_cost_limit": 100.0    # $100 monthly limit
                }
            },
            {
                "name": "Enterprise Alpha",
                "tier": SubscriptionTier.ENTERPRISE,
                "price_monthly": 299.0,
                "price_yearly": 2990.0,
                "description": "Enterprise alpha tier - Unlimited usage for enterprise testing",
                "features": ["blog_writer", "seo_analysis", "content_planning", "strategy_copilot", "advanced_analytics", "custom_integrations"],
                "limits": {
                    "gemini_calls_limit": 0,       # Unlimited calls
                    "gemini_tokens_limit": 0,      # Unlimited tokens
                    "tavily_calls_limit": 0,       # Unlimited searches
                    "serper_calls_limit": 0,       # Unlimited SEO searches
                    "stability_calls_limit": 0,    # Unlimited images
                    "monthly_cost_limit": 500.0    # $500 monthly limit
                }
            }
        ]
        
        # Create subscription plans
        for tier_data in alpha_tiers:
            # Check if plan already exists
            existing_plan = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.name == tier_data["name"]
            ).first()
            
            if existing_plan:
                logger.info(f"✅ Plan '{tier_data['name']}' already exists, updating...")
                # Update existing plan
                for key, value in tier_data["limits"].items():
                    setattr(existing_plan, key, value)
                existing_plan.description = tier_data["description"]
                existing_plan.features = tier_data["features"]
                existing_plan.updated_at = datetime.utcnow()
            else:
                logger.info(f"🆕 Creating new plan: {tier_data['name']}")
                # Create new plan
                plan = SubscriptionPlan(
                    name=tier_data["name"],
                    tier=tier_data["tier"],
                    price_monthly=tier_data["price_monthly"],
                    price_yearly=tier_data["price_yearly"],
                    description=tier_data["description"],
                    features=tier_data["features"],
                    **tier_data["limits"]
                )
                db.add(plan)
        
        db.commit()
        logger.info("✅ Alpha subscription tiers created/updated successfully!")
        
        # Create API provider pricing
        create_api_pricing(db)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating alpha subscription tiers: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def create_api_pricing(db: Session):
    """Create API provider pricing configuration."""
    
    try:
        # Gemini pricing (based on current Google AI pricing)
        gemini_pricing = [
            {
                "model_name": "gemini-2.0-flash-exp",
                "cost_per_input_token": 0.00000075,   # $0.75 per 1M tokens
                "cost_per_output_token": 0.000003,    # $3 per 1M tokens
                "description": "Gemini 2.0 Flash Experimental"
            },
            {
                "model_name": "gemini-1.5-flash",
                "cost_per_input_token": 0.00000075,   # $0.75 per 1M tokens
                "cost_per_output_token": 0.000003,    # $3 per 1M tokens
                "description": "Gemini 1.5 Flash"
            },
            {
                "model_name": "gemini-1.5-pro",
                "cost_per_input_token": 0.00000125,   # $1.25 per 1M tokens
                "cost_per_output_token": 0.000005,    # $5 per 1M tokens
                "description": "Gemini 1.5 Pro"
            }
        ]
        
        # Tavily pricing
        tavily_pricing = [
            {
                "model_name": "search",
                "cost_per_search": 0.001,  # $0.001 per search
                "description": "Tavily Search API"
            }
        ]
        
        # Serper pricing
        serper_pricing = [
            {
                "model_name": "search",
                "cost_per_search": 0.001,  # $0.001 per search
                "description": "Serper Google Search API"
            }
        ]
        
        # Stability AI pricing
        stability_pricing = [
            {
                "model_name": "stable-diffusion-xl",
                "cost_per_image": 0.01,  # $0.01 per image
                "description": "Stable Diffusion XL"
            }
        ]
        
        # Create pricing records
        pricing_configs = [
            (APIProvider.GEMINI, gemini_pricing),
            (APIProvider.TAVILY, tavily_pricing),
            (APIProvider.SERPER, serper_pricing),
            (APIProvider.STABILITY, stability_pricing)
        ]
        
        for provider, pricing_list in pricing_configs:
            for pricing_data in pricing_list:
                # Check if pricing already exists
                existing_pricing = db.query(APIProviderPricing).filter(
                    APIProviderPricing.provider == provider,
                    APIProviderPricing.model_name == pricing_data["model_name"]
                ).first()
                
                if existing_pricing:
                    logger.info(f"✅ Pricing for {provider.value}/{pricing_data['model_name']} already exists")
                else:
                    logger.info(f"🆕 Creating pricing for {provider.value}/{pricing_data['model_name']}")
                    pricing = APIProviderPricing(
                        provider=provider,
                        **pricing_data
                    )
                    db.add(pricing)
        
        db.commit()
        logger.info("✅ API provider pricing created successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error creating API pricing: {e}")
        db.rollback()

def assign_default_plan_to_users():
    """Assign Free Alpha plan to all existing users."""
    if os.getenv('ENABLE_ALPHA', 'false').lower() not in {'1','true','yes','on'}:
        logger.info("Alpha default plan assignment is disabled (ENABLE_ALPHA is false)")
        return False
    
    db = get_db_session()
    if not db:
        logger.error("❌ Could not get database session")
        return False
    
    try:
        # Get Free Alpha plan
        free_plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.name == "Free Alpha"
        ).first()
        
        if not free_plan:
            logger.error("❌ Free Alpha plan not found")
            return False
        
        # For now, we'll create a default user subscription
        # In a real system, you'd query actual users
        from models.subscription_models import UserSubscription, BillingCycle, UsageStatus
        from datetime import datetime, timedelta
        
        # Create default user subscription for testing
        default_user_id = "default_user"
        existing_subscription = db.query(UserSubscription).filter(
            UserSubscription.user_id == default_user_id
        ).first()
        
        if not existing_subscription:
            logger.info(f"🆕 Creating default subscription for {default_user_id}")
            subscription = UserSubscription(
                user_id=default_user_id,
                plan_id=free_plan.id,
                billing_cycle=BillingCycle.MONTHLY,
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=30),
                status=UsageStatus.ACTIVE,
                is_active=True,
                auto_renew=True
            )
            db.add(subscription)
            db.commit()
            logger.info(f"✅ Default subscription created for {default_user_id}")
        else:
            logger.info(f"✅ Default subscription already exists for {default_user_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error assigning default plan: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("🚀 Initializing Alpha Subscription Tiers...")
    
    success = create_alpha_subscription_tiers()
    if success:
        logger.info("✅ Subscription tiers created successfully!")
        
        # Assign default plan
        assign_success = assign_default_plan_to_users()
        if assign_success:
            logger.info("✅ Default plan assigned successfully!")
        else:
            logger.error("❌ Failed to assign default plan")
    else:
        logger.error("❌ Failed to create subscription tiers")
    
    logger.info("🎉 Alpha subscription system initialization complete!")
