"""
Database service for ALwrity backend.
Handles database connections and sessions.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
from typing import Optional, List

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
from models.content_asset_models import Base as ContentAssetBase
# Product Marketing models use SubscriptionBase, but import to ensure models are registered
from models.product_marketing_models import Campaign, CampaignProposal, CampaignAsset
# Product Asset models (Product Marketing Suite - product assets, not campaigns)
from models.product_asset_models import ProductAsset, ProductStyleTemplate, EcommerceExport
# Podcast Maker models use SubscriptionBase, but import to ensure models are registered
from models.podcast_models import PodcastProject
# Research models use SubscriptionBase
from models.research_models import ResearchProject
# Video Studio models
from models.video_models import VideoGenerationTask
# Bing Analytics models
from models.bing_analytics_models import Base as BingAnalyticsBase

# Monitoring Task Models (Share EnhancedStrategyBase but need explicit import to register)
# Import these to ensure their tables are created by EnhancedStrategyBase.metadata.create_all
import models.oauth_token_monitoring_models
import models.website_analysis_monitoring_models
import models.platform_insights_monitoring_models
import models.agent_activity_models
import models.daily_workflow_models

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
    # Some older workspaces might have 'alwrity.db' instead of 'alwrity_{user_id}.db'
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
    # This runs once per process per user when the engine is created
    try:
        # We need to import the function here or rely on it being available in the module scope
        # Since this function is called at runtime, init_user_database should be available
        init_user_database(user_id)
    except Exception as e:
        logger.error(f"Failed to auto-initialize database for user {user_id}: {e}")
        # We don't raise here to allow the engine to be returned, 
        # but the application might fail later if tables are missing.
    
    return engine

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
        BingAnalyticsBase.metadata.create_all(bind=engine)
        
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

def init_database():
    """
    Initialize global database tables (for backward compatibility/startup checks).
    Uses default engine.
    """
    if not default_engine:
        logger.warning("Global database initialization skipped: default_engine is disabled (Multi-tenant mode)")
        return

    try:
        # Create all tables for all models using default engine
        OnboardingBase.metadata.create_all(bind=default_engine)
        SEOAnalysisBase.metadata.create_all(bind=default_engine)
        ContentPlanningBase.metadata.create_all(bind=default_engine)
        EnhancedStrategyBase.metadata.create_all(bind=default_engine)
        MonitoringBase.metadata.create_all(bind=default_engine)
        APIMonitoringBase.metadata.create_all(bind=default_engine)
        PersonaBase.metadata.create_all(bind=default_engine)
        SubscriptionBase.metadata.create_all(bind=default_engine)
        UserBusinessInfoBase.metadata.create_all(bind=default_engine)
        ContentAssetBase.metadata.create_all(bind=default_engine)
        logger.info("Global database initialized successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error initializing global database: {str(e)}")


# Import here to avoid circular dependency at module level if possible, 
# but get_db needs it. 
# We assume auth_middleware is available.
from middleware.auth_middleware import get_current_user
from fastapi import Depends

# Legacy support for single-tenant code
# TODO: Refactor all consumers to use get_db or get_session_for_user
default_db_path = None # os.path.join(ROOT_DIR, 'alwrity.db')
DATABASE_URL = None # f"sqlite:///{default_db_path}"
default_engine = None # create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
engine = None # default_engine
SessionLocal = None # sessionmaker(autocommit=False, autoflush=False, bind=default_engine)

def get_db(current_user: dict = Depends(get_current_user)):
    """
    Database dependency for FastAPI endpoints.
    Context-aware: connects to the authenticated user's database.
    """
    user_id = current_user.get('id') or current_user.get('clerk_user_id')
    if not user_id:
        # Fallback or error? For now log error
        logger.error("No user ID found in context for DB connection")
        # Could raise exception, but let's try to be safe
        raise Exception("User ID required for database access")
        
    engine = get_engine_for_user(user_id)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper for scripts/legacy that explicitly know the user_id
def get_session_for_user(user_id: str) -> Optional[Session]:
    """
    Get a new database session for a specific user.
    The session is not scoped, so the caller is responsible for closing it.
    """
    engine = get_engine_for_user(user_id)
    if not engine:
        return None
        
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def get_db_session(user_id: Optional[str] = None) -> Optional[Session]:
    """
    DEPRECATED: Use get_session_for_user(user_id) instead.
    Legacy wrapper to prevent ImportErrors during refactoring.
    """
    from utils.logger_utils import get_service_logger
    logger = get_service_logger("database")
    # logger.warning("Using deprecated get_db_session. Please update to get_session_for_user(user_id).")
    
    if user_id:
        return get_session_for_user(user_id)
        
    # If no user_id, we can't give a valid session in multi-tenant mode
    return None


def close_database():
    """
    Close database connections.
    """
    try:
        for engine in _user_engines.values():
            engine.dispose()
        _user_engines.clear()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {str(e)}")
 
