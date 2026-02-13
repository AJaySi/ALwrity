"""
Database service for ALwrity backend.
Handles database connections and sessions with connection pooling.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables to ensure they're available
load_dotenv()

# Import models
from models.onboarding import Base as OnboardingBase
from models.seo_analysis import Base as SEOAnalysisBase
from models.content_planning import Base as ContentPlanningBase
from models.enhanced_strategy_models import Base as EnhancedStrategyBase
# Monitoring models now use the same base as enhanced strategy models
from models.monitoring_models import Base as MonitoringBase
from models.api_monitoring import Base as APIMonitoringBase
from models.persona_models import Base as PersonaBase
from models.subscription_models import Base as SubscriptionBase
from models.user_business_info import Base as UserBusinessInfoBase
from models.user_website import Base as UserWebsiteBase
from models.content_asset_models import Base as ContentAssetBase

# Product Marketing models use SubscriptionBase, but import to ensure models are registered
from models.product_marketing_models import Campaign, CampaignProposal, CampaignAsset
# Product Asset models (Product Marketing Suite - product assets, not campaigns)
from models.product_asset_models import ProductAsset, ProductStyleTemplate, EcommerceExport
from models.product_asset_models import Base as ProductAssetBase

# Podcast Maker models use SubscriptionBase, but import to ensure models are registered
from models.podcast_models import PodcastProject
# Research models use SubscriptionBase
from models.research_models import ResearchProject
# Video Studio models
from models.video_models import VideoGenerationTask
# Bing Analytics models
from models.bing_analytics_models import Base as BingAnalyticsBase

# Monitoring Task Models (Share EnhancedStrategyBase but need explicit import to register)
import models.oauth_token_monitoring_models
import models.website_analysis_monitoring_models
import models.platform_insights_monitoring_models
import models.agent_activity_models
import models.daily_workflow_models

# PR-354 New Models
from models.oauth_token_monitoring_models import OAuthTokenMonitoringTask
from models.website_analysis_monitoring_models import WebsiteAnalysisTask
from models.platform_insights_monitoring_models import PlatformInsightsTask
from models.oauth_token_models import BingOAuthToken, WordPressOAuthToken, WixOAuthToken
from models.oauth_token_models import Base as OAuthTokenBase
from models.users import Base as UsersBase
from models.user_subscriptions import Base as UserSubscriptionsBase
from models.subscription_plans import Base as SubscriptionPlansBase
from models.platform_usage_logs import Base as PlatformUsageLogsBase
from models.user_profiles import Base as UserProfilesBase
from models.user_projects import Base as UserProjectsBase
from models.user_content_assets import Base as UserContentAssetsBase
from models.user_personas import Base as UserPersonasBase


# Database configuration
# Get project root (3 levels up from services/database.py: services -> backend -> root)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORKSPACE_DIR = os.path.join(ROOT_DIR, 'workspace')

# Engine cache for multi-tenant support
_user_engines = {}

def get_user_db_path(user_id: str) -> str:
    """Get the database path for a specific user."""
    # Sanitize user_id to be safe for filesystem
    safe_user_id = "".join(c for c in user_id if c.isalnum() or c in ('-', '_'))
    user_workspace = os.path.join(WORKSPACE_DIR, f"workspace_{safe_user_id}")
    
    # Check for legacy naming convention first (to support existing data)
    legacy_db_path = os.path.join(user_workspace, 'db', 'alwrity.db')
    specific_db_path = os.path.join(user_workspace, 'db', f'alwrity_{safe_user_id}.db')
    
    # If the specific one exists, use it (preferred)
    if os.path.exists(specific_db_path):
        return specific_db_path
        
    # If legacy exists and specific doesn't, use legacy
    if os.path.exists(legacy_db_path):
        return legacy_db_path
        
    # Default to specific for new databases
    return specific_db_path

def get_all_user_ids() -> List[str]:
    """
    Discover all user IDs by scanning workspace directories.
    Returns a list of user_ids (e.g., 'user_2p...', 'user_123').
    """
    user_ids = []
    if not os.path.exists(WORKSPACE_DIR):
        return []
    
    try:
        for item in os.listdir(WORKSPACE_DIR):
            if item.startswith("workspace_") and os.path.isdir(os.path.join(WORKSPACE_DIR, item)):
                # Extract user_id from workspace_{user_id}
                user_id = item[len("workspace_"):]
                if user_id:
                    user_ids.append(user_id)
    except Exception as e:
        logger.error(f"Error discovering user workspaces: {e}")
        
    return user_ids

def get_engine_for_user(user_id: str):
    """Get or create a SQLAlchemy engine for a specific user."""
    if user_id in _user_engines:
        return _user_engines[user_id]
    
    db_path = get_user_db_path(user_id)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    database_url = f"sqlite:///{db_path}"
    
    engine_kwargs = {
        "echo": False,
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": int(os.getenv("DB_POOL_SIZE", "20")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "40")),
        "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
        "connect_args": {"check_same_thread": False}
    }
    
    engine = create_engine(database_url, **engine_kwargs)
    _user_engines[user_id] = engine

    # Ensure tables are initialized for this user
    try:
        init_user_database(user_id)
    except Exception as e:
        logger.error(f"Failed to auto-initialize database for user {user_id}: {e}")
    
    return engine

def get_session_for_user(user_id: str):
    """Get a new database session for a specific user."""
    engine = get_engine_for_user(user_id)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def init_user_database(user_id: str):
    """Initialize database tables for a specific user."""
    engine = get_engine_for_user(user_id)
    try:
        # Create all tables for all models
        OnboardingBase.metadata.create_all(bind=engine)
        SEOAnalysisBase.metadata.create_all(bind=engine)
        ContentPlanningBase.metadata.create_all(bind=engine)
        EnhancedStrategyBase.metadata.create_all(bind=engine)
        MonitoringBase.metadata.create_all(bind=engine)
        APIMonitoringBase.metadata.create_all(bind=engine)
        PersonaBase.metadata.create_all(bind=engine)
        SubscriptionBase.metadata.create_all(bind=engine)
        UserBusinessInfoBase.metadata.create_all(bind=engine)
        ContentAssetBase.metadata.create_all(bind=engine)
        
        # New models from PR-354 (added to SQLite for compatibility)
        ProductAssetBase.metadata.create_all(bind=engine)
        UsersBase.metadata.create_all(bind=engine)
        UserSubscriptionsBase.metadata.create_all(bind=engine)
        SubscriptionPlansBase.metadata.create_all(bind=engine)
        PlatformUsageLogsBase.metadata.create_all(bind=engine)
        OAuthTokenBase.metadata.create_all(bind=engine)
        UserProfilesBase.metadata.create_all(bind=engine)
        UserProjectsBase.metadata.create_all(bind=engine)
        UserContentAssetsBase.metadata.create_all(bind=engine)
        UserPersonasBase.metadata.create_all(bind=engine)
        
        # Create monitoring tables explicitly if needed
        OAuthTokenMonitoringTask.__table__.create(bind=engine, checkfirst=True)
        WebsiteAnalysisTask.__table__.create(bind=engine, checkfirst=True)
        PlatformInsightsTask.__table__.create(bind=engine, checkfirst=True)
        
        # Initialize default data for new databases
        try:
            # Import here to avoid circular dependencies
            from services.subscription.pricing_service import PricingService
            
            # Create a session for data initialization
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionLocal()
            try:
                pricing_service = PricingService(db)
                pricing_service.initialize_default_pricing()
                pricing_service.initialize_default_plans()
                db.commit()
                logger.info(f"Default pricing and plans initialized for user {user_id}")
            except Exception as data_error:
                logger.error(f"Error initializing default data for user {user_id}: {data_error}")
                db.rollback()
            finally:
                db.close()
        except Exception as import_error:
            logger.warning(f"Could not initialize pricing data (PricingService import failed): {import_error}")

        logger.info(f"Database initialized successfully for user {user_id}")
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database for user {user_id}: {str(e)}")
        raise
