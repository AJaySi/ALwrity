"""
Database service for ALwrity backend.
Handles database connections and sessions with connection pooling.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
from typing import Optional, Dict, Any
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
from models.persona_models import Base as PersonaBase
from models.subscription_models import Base as SubscriptionBase
from models.user_business_info import Base as UserBusinessInfoBase
from models.content_asset_models import Base as ContentAssetBase
from models.product_asset_models import Base as ProductAssetBase
# Additional monitoring models (use EnhancedStrategyBase)
from models.oauth_token_monitoring_models import OAuthTokenMonitoringTask
from models.website_analysis_monitoring_models import WebsiteAnalysisTask
from models.platform_insights_monitoring_models import PlatformInsightsTask

# SSOT Core Models - Platform Database
from models.users import Base as UsersBase
from models.user_subscriptions import Base as UserSubscriptionsBase
from models.subscription_plans import Base as SubscriptionPlansBase
from models.platform_usage_logs import Base as PlatformUsageLogsBase

# SSOT Core Models - User Data Database
from models.user_profiles import Base as UserProfilesBase
from models.user_projects import Base as UserProjectsBase
from models.user_content_assets import Base as UserContentAssetsBase
from models.user_personas import Base as UserPersonasBase

# Database configuration - PostgreSQL only (Clean Architecture)
# Legacy DATABASE_URL removed - no longer supported

# Create engine with safer pooling defaults for PostgreSQL (Connection Exhaustion Fix)
engine_kwargs = {
    "echo": False,                 # Set to True for SQL debugging
    "pool_pre_ping": True,        # Detect stale connections
    "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "3600")),  # Recycle connections per .env setting
    "pool_size": int(os.getenv("DB_POOL_SIZE", "20")),      # Production-optimized pool size
    "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "30")), # Production-optimized overflow
    "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
}

# Backward compatibility: SessionLocal function for existing code
def SessionLocal():
    """
    Backward compatible SessionLocal function.
    Returns user data database session for PostgreSQL-only architecture.
    Uses global session maker to prevent duplicate session maker creation.
    """
    UserDataSessionLocal = get_user_data_session_maker()
    return UserDataSessionLocal()

# Backward compatibility: engine for existing scripts and tests
def engine():
    """
    Backward compatible engine function.
    Returns user data database engine for PostgreSQL-only architecture.
    Uses global engine to prevent duplicate engine creation.
    """
    return get_user_data_engine()

# Global engine instances for connection pooling
_platform_engine = None
_user_data_engine = None

# Global session makers for consistent session creation
_platform_session_maker = None
_user_data_session_maker = None

def get_platform_engine():
    """Get or create platform database engine with connection pooling"""
    global _platform_engine
    if _platform_engine is None:
        platform_db_url = os.getenv("PLATFORM_DATABASE_URL")
        if not platform_db_url:
            raise ValueError("PLATFORM_DATABASE_URL not set")
        _platform_engine = create_engine(platform_db_url, **engine_kwargs)
        logger.info(f"Platform engine created with pool_size={engine_kwargs['pool_size']}")
    return _platform_engine

def get_user_data_engine():
    """Get or create user data database engine with connection pooling"""
    global _user_data_engine
    if _user_data_engine is None:
        user_data_db_url = os.getenv("USER_DATA_DATABASE_URL")
        if not user_data_db_url:
            raise ValueError("USER_DATA_DATABASE_URL not set")
        _user_data_engine = create_engine(user_data_db_url, **engine_kwargs)
        logger.info(f"User data engine created with pool_size={engine_kwargs['pool_size']}")
    return _user_data_engine

def get_platform_session_maker():
    """Get or create platform database session maker"""
    global _platform_session_maker
    if _platform_session_maker is None:
        platform_engine = get_platform_engine()
        _platform_session_maker = sessionmaker(autocommit=False, autoflush=False, bind=platform_engine)
    return _platform_session_maker

def get_user_data_session_maker():
    """Get or create user data database session maker"""
    global _user_data_session_maker
    if _user_data_session_maker is None:
        user_data_engine = get_user_data_engine()
        _user_data_session_maker = sessionmaker(autocommit=False, autoflush=False, bind=user_data_engine)
    return _user_data_session_maker

def get_platform_db_session() -> Optional[Session]:
    """
    Get a platform database session for system-level tables.
    PostgreSQL-only implementation with connection pooling.
    
    Returns:
        Platform database session or None if connection fails
    """
    try:
        PlatformSessionLocal = get_platform_session_maker()
        db = PlatformSessionLocal()
        logger.debug("Platform database session created")
        return db
            
    except Exception as e:
        logger.error(f"Error creating platform database session: {str(e)}")
        return None

def get_user_data_db_session() -> Optional[Session]:
    """
    Get a user data database session for user-specific tables.
    PostgreSQL-only implementation with connection pooling.
    
    Returns:
        User data database session or None if connection fails
    """
    try:
        UserDataSessionLocal = get_user_data_session_maker()
        db = UserDataSessionLocal()
        logger.debug("User data database session created")
        return db
            
    except Exception as e:
        logger.error(f"Error creating user data database session: {str(e)}")
        return None

def get_db_session() -> Optional[Session]:
    """
    Get a database session using dual database architecture.
    PostgreSQL-only implementation.
    
    Returns:
        Database session or None if connection fails
    """
    try:
        # Require dual database environment variables
        platform_db_url = os.getenv("PLATFORM_DATABASE_URL")
        user_data_db_url = os.getenv("USER_DATA_DATABASE_URL")
        
        if not platform_db_url or not user_data_db_url:
            raise ValueError(
                """
 POSTGRESQL REQUIRED - Clean Architecture
                
ALwrity requires PostgreSQL environment variables to be set:
- PLATFORM_DATABASE_URL=postgresql://user:pass@host:port/database_name
- USER_DATA_DATABASE_URL=postgresql://user:pass@host:port/database_name

This is intentional - we no longer support SQLite or single database setups.
"""
            )
        
        # Use dual database architecture - return user data session for backward compatibility
        user_data_db = get_user_data_db_session()
        
        logger.info("Using dual PostgreSQL database architecture")
        return user_data_db
            
    except SQLAlchemyError as e:
        logger.error(f"Error creating database session: {str(e)}")
        return None

def init_database():
    """
    Initialize the database using dual database architecture.
    PostgreSQL-only implementation with connection pooling.
    """
    try:
        # Require dual database environment variables
        platform_db_url = os.getenv("PLATFORM_DATABASE_URL")
        user_data_db_url = os.getenv("USER_DATA_DATABASE_URL")
        
        if not platform_db_url or not user_data_db_url:
            raise ValueError(
                """
 POSTGRESQL REQUIRED - Clean Architecture
                
ALwrity requires PostgreSQL environment variables to be set:
- PLATFORM_DATABASE_URL=postgresql://user:pass@host:port/database_name
- USER_DATA_DATABASE_URL=postgresql://user:pass@host:port/database_name

This is intentional - we no longer support SQLite or single database setups.
"""
            )
        
        # Use global engines to prevent duplicate engine creation
        platform_engine = get_platform_engine()
        user_data_engine = get_user_data_engine()
        
        logger.info(f"Database engines created with pool settings: size={engine_kwargs['pool_size']}, "
                   f"max_overflow={engine_kwargs['max_overflow']}, recycle={engine_kwargs['pool_recycle']}s")
        
        # Create tables on appropriate databases using single connection per database
        # Platform database tables
        logger.info("Creating platform database tables...")
        try:
            # Legacy platform tables
            OnboardingBase.metadata.create_all(bind=platform_engine, checkfirst=True)
            SEOAnalysisBase.metadata.create_all(bind=platform_engine, checkfirst=True)
            SubscriptionBase.metadata.create_all(bind=platform_engine, checkfirst=True)
            UserBusinessInfoBase.metadata.create_all(bind=platform_engine, checkfirst=True)
            ContentAssetBase.metadata.create_all(bind=platform_engine, checkfirst=True)
            ProductAssetBase.metadata.create_all(bind=platform_engine, checkfirst=True)
            
            # SSOT Core Platform Tables
            UsersBase.metadata.create_all(bind=platform_engine, checkfirst=True)
            UserSubscriptionsBase.metadata.create_all(bind=platform_engine, checkfirst=True)
            SubscriptionPlansBase.metadata.create_all(bind=platform_engine, checkfirst=True)
            PlatformUsageLogsBase.metadata.create_all(bind=platform_engine, checkfirst=True)
            
            # Create monitoring tables on platform database (system-level monitoring)
            OAuthTokenMonitoringTask.__table__.create(bind=platform_engine, checkfirst=True)
            WebsiteAnalysisTask.__table__.create(bind=platform_engine, checkfirst=True)
            PlatformInsightsTask.__table__.create(bind=platform_engine, checkfirst=True)
            
            logger.info("✅ All platform database tables created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create platform database tables: {e}")
        
        # User data database tables
        logger.info("Creating user data database tables...")
        try:
            # Legacy user data tables
            ContentPlanningBase.metadata.create_all(bind=user_data_engine, checkfirst=True)
            EnhancedStrategyBase.metadata.create_all(bind=user_data_engine, checkfirst=True)
            MonitoringBase.metadata.create_all(bind=user_data_engine, checkfirst=True)
            PersonaBase.metadata.create_all(bind=user_data_engine, checkfirst=True)
            
            # SSOT Core User Data Tables (Multi-tenant with RLS)
            UserProfilesBase.metadata.create_all(bind=user_data_engine, checkfirst=True)
            UserProjectsBase.metadata.create_all(bind=user_data_engine, checkfirst=True)
            UserContentAssetsBase.metadata.create_all(bind=user_data_engine, checkfirst=True)
            UserPersonasBase.metadata.create_all(bind=user_data_engine, checkfirst=True)
            
            logger.info("✅ All user data database tables created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create user data database tables: {e}")
        
        logger.info("Dual PostgreSQL database initialized successfully with all models")
            
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def close_database():
    """
    Close database connections using dual database architecture.
    PostgreSQL-only implementation.
    """
    try:
        # Require dual database environment variables
        platform_db_url = os.getenv("PLATFORM_DATABASE_URL")
        user_data_db_url = os.getenv("USER_DATA_DATABASE_URL")
        
        if not platform_db_url or not user_data_db_url:
            raise ValueError(
                """
 POSTGRESQL REQUIRED - Clean Architecture
                
ALwrity requires PostgreSQL environment variables to be set:
- PLATFORM_DATABASE_URL=postgresql://user:pass@host:port/database_name
- USER_DATA_DATABASE_URL=postgresql://user:pass@host:port/database_name

This is intentional - we no longer support SQLite or single database setups.
"""
            )
        
        # Use global engines to prevent duplicate engine creation
        platform_engine = get_platform_engine()
        user_data_engine = get_user_data_engine()
        
        platform_engine.dispose()
        user_data_engine.dispose()
        
        # Reset global engine instances and session makers
        global _platform_engine, _user_data_engine, _platform_session_maker, _user_data_session_maker
        _platform_engine = None
        _user_data_engine = None
        _platform_session_maker = None
        _user_data_session_maker = None
        
        logger.info("Dual PostgreSQL database connections closed")
            
    except Exception as e:
        logger.error(f"Error closing database connections: {str(e)}")

def get_db():
    """
    Database dependency for FastAPI endpoints using dual database architecture.
    PostgreSQL-only implementation.
    """
    # Require dual database environment variables
    platform_db_url = os.getenv("PLATFORM_DATABASE_URL")
    user_data_db_url = os.getenv("USER_DATA_DATABASE_URL")
    
    if not platform_db_url or not user_data_db_url:
        raise ValueError(
            """
 POSTGRESQL REQUIRED - Clean Architecture
            
ALwrity requires PostgreSQL environment variables to be set:
- PLATFORM_DATABASE_URL=postgresql://user:pass@host:port/database_name
- USER_DATA_DATABASE_URL=postgresql://user:pass@host:port/database_name

This is intentional - we no longer support SQLite or single database setups.
"""
        )
    
    # Use global session maker to prevent duplicate session maker creation
    UserDataSessionLocal = get_user_data_session_maker()
    
    db = UserDataSessionLocal()
    
    try:
        yield db
    finally:
        db.close()

# ===== SSOT CORE DATABASE FUNCTIONS =====
# These functions implement the missing core functionality documented in the SSOT

def get_platform_db() -> Session:
    """
    Get platform database session for user management, subscriptions, analytics.
    SSOT-compliant function for platform database access.
    
    Returns:
        Platform database session for system-level operations
    """
    return get_platform_db_session()

def get_user_data_db() -> Session:
    """
    Get user data database session for multi-tenant content.
    SSOT-compliant function for user data database access.
    
    Returns:
        User data database session for tenant-specific operations
    """
    return get_user_data_db_session()

def set_user_context(user_id: str, db_session: Session):
    """
    Set PostgreSQL RLS user context for tenant isolation.
    Implements Row-Level Security context management.
    
    Args:
        user_id: User ID for tenant isolation
        db_session: Database session to set context on
    """
    try:
        # Set PostgreSQL session variable for RLS policies
        db_session.execute(text("SET app.current_user_id = :user_id"), {"user_id": user_id})
        logger.info(f"✅ RLS user context set for user_id: {user_id}")
    except Exception as e:
        logger.error(f"❌ Failed to set RLS user context: {e}")
        raise

def test_connections() -> Dict[str, bool]:
    """
    Test connectivity to both databases.
    SSOT-compliant database connection testing.
    
    Returns:
        Dictionary with connection status for each database
    """
    results = {}
    
    try:
        # Test platform database
        platform_session = get_platform_db_session()
        platform_session.execute(text("SELECT 1"))
        results["platform"] = True
        platform_session.close()
        logger.info("✅ Platform database connection: SUCCESS")
    except Exception as e:
        results["platform"] = False
        logger.error(f"❌ Platform database connection: FAILED - {e}")
    
    try:
        # Test user data database
        user_data_session = get_user_data_db_session()
        user_data_session.execute(text("SELECT 1"))
        results["user_data"] = True
        user_data_session.close()
        logger.info("✅ User data database connection: SUCCESS")
    except Exception as e:
        results["user_data"] = False
        logger.error(f"❌ User data database connection: FAILED - {e}")
    
    return results

def get_database_info() -> Dict[str, Any]:
    """
    Get database connection and configuration information.
    SSOT-compliant database information retrieval.
    
    Returns:
        Dictionary with database configuration and status information
    """
    info = {
        "architecture": "dual_postgresql",
        "platform_database": {
            "url_configured": bool(os.getenv("PLATFORM_DATABASE_URL")),
            "engine_created": _platform_engine is not None,
            "pool_size": engine_kwargs["pool_size"] if _platform_engine else None,
            "max_overflow": engine_kwargs["max_overflow"] if _platform_engine else None,
        },
        "user_data_database": {
            "url_configured": bool(os.getenv("USER_DATA_DATABASE_URL")),
            "engine_created": _user_data_engine is not None,
            "pool_size": engine_kwargs["pool_size"] if _user_data_engine else None,
            "max_overflow": engine_kwargs["max_overflow"] if _user_data_engine else None,
        },
        "configuration": {
            "pool_size": engine_kwargs["pool_size"],
            "max_overflow": engine_kwargs["max_overflow"],
            "pool_timeout": engine_kwargs["pool_timeout"],
            "pool_recycle": engine_kwargs["pool_recycle"],
            "pool_pre_ping": engine_kwargs["pool_pre_ping"],
        }
    }
    
    # Add connection status
    connections = test_connections()
    info["platform_database"]["connection_status"] = connections.get("platform", False)
    info["user_data_database"]["connection_status"] = connections.get("user_data", False)
    
    return info

def setup_row_level_security():
    """
    Setup RLS policies on all user data tables.
    Implements Row-Level Security for multi-tenant architecture.
    """
    try:
        user_data_engine = get_user_data_engine()
        
        # Enable RLS on user data tables
        rls_tables = [
            "user_profiles",
            "user_projects", 
            "user_content_assets",
            "user_personas"
        ]
        
        for table_name in rls_tables:
            try:
                # Use connection with proper session for DDL operations
                with user_data_engine.connect() as conn:
                    # Enable RLS on table
                    conn.execute(text(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY"))
                    
                    # Create RLS policy for public role (simpler approach)
                    policy_sql = f"""
                    CREATE POLICY {table_name}_user_isolation ON {table_name}
                        FOR ALL
                        USING (user_id::text = current_setting('app.current_user_id'));
                    """
                    conn.execute(text(policy_sql))
                    conn.commit()
                
                logger.info(f"✅ RLS enabled and policy created for {table_name}")
            except Exception as e:
                logger.warning(f"⚠️ Could not setup RLS for {table_name}: {e}")
        
        logger.info("✅ Row-Level Security setup completed")
        
    except Exception as e:
        logger.error(f"❌ Failed to setup Row-Level Security: {e}")
        raise

def init_databases():
    """
    Initialize both databases with proper schema creation.
    SSOT-compliant dual database initialization.
    """
    try:
        logger.info("🚀 Initializing dual PostgreSQL databases...")
        
        # Test connections first
        connections = test_connections()
        if not all(connections.values()):
            raise ValueError("Cannot initialize databases - connection tests failed")
        
        # Use existing init_database function
        init_database()
        
        # Setup Row-Level Security
        setup_row_level_security()
        
        logger.info("✅ Dual databases initialized successfully with RLS")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize databases: {e}")
        raise

def close_databases():
    """
    Properly close all database connections and cleanup.
    SSOT-compliant database connection cleanup.
    """
    try:
        logger.info("🛑 Closing all database connections...")
        
        # Use existing close_database function
        close_database()
        
        logger.info("✅ All database connections closed successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to close databases: {e}")
        raise