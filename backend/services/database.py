"""
Database service for ALwrity backend.
Handles database connections and sessions.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
from typing import Optional

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

# Database configuration - PostgreSQL only (Clean Architecture)
# Legacy DATABASE_URL removed - no longer supported

# Create engine with safer pooling defaults for PostgreSQL
engine_kwargs = {
    "echo": False,                 # Set to True for SQL debugging
    "pool_pre_ping": True,        # Detect stale connections
    "pool_recycle": 300,          # Recycle connections to avoid timeouts
    "pool_size": int(os.getenv("DB_POOL_SIZE", "20")),
    "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "40")),
    "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
}

# Backward compatibility: SessionLocal function for existing code
def SessionLocal():
    """
    Backward compatible SessionLocal function.
    Returns user data database session for PostgreSQL-only architecture.
    """
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
    
    # Create user data database engine and session
    user_data_engine = create_engine(user_data_db_url, **engine_kwargs)
    UserDataSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=user_data_engine)
    return UserDataSessionLocal()

# Backward compatibility: engine for existing scripts and tests
def engine():
    """
    Backward compatible engine function.
    Returns user data database engine for PostgreSQL-only architecture.
    """
    user_data_db_url = os.getenv("USER_DATA_DATABASE_URL")
    
    if not user_data_db_url:
        raise ValueError(
            """
 POSTGRESQL REQUIRED - Clean Architecture
            
ALwrity requires PostgreSQL environment variables to be set:
- USER_DATA_DATABASE_URL=postgresql://user:pass@host:port/database_name

This is intentional - we no longer support SQLite or single database setups.
"""
        )
    
    return create_engine(user_data_db_url, **engine_kwargs)

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
        
        # Use dual database architecture
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # Create user data database engine
        user_data_engine = create_engine(user_data_db_url, **engine_kwargs)
        UserDataSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=user_data_engine)
        
        db = UserDataSessionLocal()
        logger.info("Using dual PostgreSQL database architecture")
        return db
            
    except SQLAlchemyError as e:
        logger.error(f"Error creating database session: {str(e)}")
        return None

def init_database():
    """
    Initialize the database using dual database architecture.
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
        
        # Use dual database architecture
        from sqlalchemy import create_engine
        
        # Create platform database engine
        platform_engine = create_engine(platform_db_url, **engine_kwargs)
        
        # Create user data database engine
        user_data_engine = create_engine(user_data_db_url, **engine_kwargs)
        
        # Create tables on appropriate databases
        # Platform database tables
        OnboardingBase.metadata.create_all(bind=platform_engine)
        SEOAnalysisBase.metadata.create_all(bind=platform_engine)
        SubscriptionBase.metadata.create_all(bind=platform_engine)
        UserBusinessInfoBase.metadata.create_all(bind=platform_engine)
        
        # User data database tables
        ContentPlanningBase.metadata.create_all(bind=user_data_engine)
        EnhancedStrategyBase.metadata.create_all(bind=user_data_engine)
        MonitoringBase.metadata.create_all(bind=user_data_engine)
        PersonaBase.metadata.create_all(bind=user_data_engine)
        
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
        
        # Use dual database architecture
        from sqlalchemy import create_engine
        
        # Create and dispose both database engines
        platform_engine = create_engine(platform_db_url, **engine_kwargs)
        user_data_engine = create_engine(user_data_db_url, **engine_kwargs)
        
        platform_engine.dispose()
        user_data_engine.dispose()
        logger.info("Dual PostgreSQL database connections closed")
            
    except Exception as e:
        logger.error(f"Error closing database connections: {str(e)}")

# Database dependency for FastAPI
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
    
    # Use dual database architecture
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Create user data database engine
    user_data_engine = create_engine(user_data_db_url, **engine_kwargs)
    UserDataSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=user_data_engine)
    
    db = UserDataSessionLocal()
    
    try:
        yield db
    finally:
        db.close()