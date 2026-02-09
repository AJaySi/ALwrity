"""
Database Migration Script for Billing System
Creates all tables needed for billing, usage tracking, and subscription management.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from utils.logging import get_logger
import traceback

# Import models
from models.subscription_models import Base as SubscriptionBase
from services.database import engine
from services.subscription.pricing_service import PricingService

# Initialize logger
logger = get_logger("create_billing_tables", migration_mode=True)

def create_billing_tables():
    """Create all billing and subscription-related tables."""
    
    try:
        # Create engine using dual database architecture
        db_engine = engine()
        
        # Create all tables
        logger.debug("Creating billing and subscription system tables...")
        SubscriptionBase.metadata.create_all(bind=db_engine)
        logger.debug("✅ Billing and subscription tables created successfully")
        
        # Create session for data initialization
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
        db = SessionLocal()
        
        try:
            # Initialize pricing and plans
            pricing_service = PricingService(db)
            
            logger.debug("Initializing default API pricing...")
            pricing_service.initialize_default_pricing()
            logger.debug("✅ Default API pricing initialized")
            
            logger.debug("Initializing default subscription plans...")
            pricing_service.initialize_default_plans()
            logger.debug("✅ Default subscription plans initialized")
            
        except Exception as e:
            logger.error(f"Error initializing default data: {e}")
            logger.error(traceback.format_exc())
            db.rollback()
            raise
        finally:
            db.close()
            
        logger.info("✅ Billing system setup completed successfully!")
        
        # Display summary
        display_setup_summary(db_engine)
        
    except Exception as e:
        logger.error(f"❌ Error creating billing tables: {e}")
        logger.error(traceback.format_exc())
        raise

def display_setup_summary(engine):
    """Display a summary of the created tables and data."""
    
    try:
        # Handle both engine function and engine object
        if callable(engine):
            db_engine = engine()
        else:
            db_engine = engine
            
        with db_engine.connect() as conn:
            logger.info("\n" + "="*60)
            logger.info("BILLING SYSTEM SETUP SUMMARY")
            logger.info("="*60)
            
            # Check tables (PostgreSQL compatible)
            tables_query = text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND (
                    table_name LIKE '%subscription%' OR 
                    table_name LIKE '%usage%' OR
                    table_name LIKE '%pricing%' OR
                    table_name LIKE '%alert%'
                )
                ORDER BY table_name
            """)
            
            result = conn.execute(tables_query)
            tables = result.fetchall()
            
            logger.info(f"\n📊 Created Tables ({len(tables)}):")
            for table in tables:
                logger.debug(f"  • {table[0]}")
            
            # Check subscription plans
            try:
                plans_query = text("SELECT COUNT(*) FROM subscription_plans")
                result = conn.execute(plans_query)
                plan_count = result.fetchone()[0]
                logger.info(f"\n💳 Subscription Plans: {plan_count}")
                
                if plan_count > 0:
                    plans_detail_query = text("""
                        SELECT name, tier, price_monthly, price_yearly 
                        FROM subscription_plans 
                        ORDER BY price_monthly
                    """)
                    result = conn.execute(plans_detail_query)
                    plans = result.fetchall()
                    
                    for plan in plans:
                        name, tier, monthly, yearly = plan
                        logger.debug(f"  • {name} ({tier}): ${monthly}/month, ${yearly}/year")
            except Exception as e:
                logger.warning(f"Could not check subscription plans: {e}")
            
            # Check API pricing
            try:
                pricing_query = text("SELECT COUNT(*) FROM api_provider_pricing")
                result = conn.execute(pricing_query)
                pricing_count = result.fetchone()[0]
                logger.info(f"\n💰 API Pricing Entries: {pricing_count}")

                if pricing_count > 0:
                    pricing_detail_query = text("""
                        SELECT provider, model_name, cost_per_input_token, cost_per_output_token
                        FROM api_provider_pricing
                        WHERE cost_per_input_token > 0 OR cost_per_output_token > 0
                        ORDER BY provider, model_name
                        LIMIT 10
                    """)
                    result = conn.execute(pricing_detail_query)
                    pricing_entries = result.fetchall()

                    logger.info("\n  LLM Pricing (per token) - Top 10:")
                    for entry in pricing_entries:
                        provider, model, input_cost, output_cost = entry
                        logger.debug(f"    • {provider}/{model}: ${input_cost:.8f} in, ${output_cost:.8f} out")
            except Exception as e:
                logger.warning(f"Could not check API pricing: {e}")
            
            logger.info("\n" + "="*60)
            logger.info("NEXT STEPS:")
            logger.info("="*60)
            logger.info("1. Billing system is ready for use")
            logger.info("2. API endpoints are available at:")
            logger.info("   GET /api/subscription/plans")
            logger.info("   GET /api/subscription/usage/{user_id}")
            logger.info("   GET /api/subscription/dashboard/{user_id}")
            logger.info("   GET /api/subscription/pricing")
            logger.info("\n3. Frontend billing dashboard is integrated")
            logger.info("4. Usage tracking middleware is active")
            logger.info("5. Real-time cost monitoring is enabled")
            logger.info("="*60)
            
    except Exception as e:
        logger.error(f"Error displaying summary: {e}")

def check_existing_tables(engine):
    """Check if billing tables already exist."""
    
    try:
        # Handle both engine function and engine object
        if callable(engine):
            db_engine = engine()
        else:
            db_engine = engine
            
        with db_engine.connect() as conn:
            # Check for billing tables (PostgreSQL compatible)
            check_query = text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND (
                    table_name = 'subscription_plans' OR 
                    table_name = 'user_subscriptions' OR 
                    table_name = 'api_usage_logs' OR
                    table_name = 'usage_summaries' OR
                    table_name = 'api_provider_pricing' OR
                    table_name = 'usage_alerts'
                )
            """)
            
            result = conn.execute(check_query)
            existing_tables = result.fetchall()
            
            if existing_tables:
                logger.warning(f"Found existing billing tables: {[t[0] for t in existing_tables]}")
                logger.debug("Tables already exist. Skipping creation to preserve data.")
                return False
            
            return True
            
    except Exception as e:
        logger.error(f"Error checking existing tables: {e}")
        return True  # Proceed anyway

if __name__ == "__main__":
    logger.debug("🚀 Starting billing system database migration...")
    
    try:
        # Create engine to check existing tables using dual database architecture
        from services.database import engine
        db_engine = engine()
        
        # Check existing tables
        if not check_existing_tables(db_engine):
            logger.debug("✅ Billing tables already exist, skipping creation")
            sys.exit(0)
        
        # Create tables and initialize data
        create_billing_tables()
        
        logger.info("✅ Billing system migration completed successfully!")
        
    except KeyboardInterrupt:
        logger.warning("Migration cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        sys.exit(1)
