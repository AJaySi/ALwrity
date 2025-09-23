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

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./alwrity.db')

# Create engine with safer pooling defaults and SQLite-friendly settings
engine_kwargs = {
    "echo": False,                 # Set to True for SQL debugging
    "pool_pre_ping": True,        # Detect stale connections
    "pool_recycle": 300,          # Recycle connections to avoid timeouts
    "pool_size": int(os.getenv("DB_POOL_SIZE", "20")),
    "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "40")),
    "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
}

# SQLite needs special handling for multithreaded FastAPI
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    **engine_kwargs,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session() -> Optional[Session]:
    """
    Get a database session.
    
    Returns:
        Database session or None if connection fails
    """
    try:
        db = SessionLocal()
        return db
    except SQLAlchemyError as e:
        logger.error(f"Error creating database session: {str(e)}")
        return None

def init_database():
    """
    Initialize the database by creating all tables.
    """
    try:
        # Create all tables for all models
        OnboardingBase.metadata.create_all(bind=engine)
        SEOAnalysisBase.metadata.create_all(bind=engine)
        ContentPlanningBase.metadata.create_all(bind=engine)
        EnhancedStrategyBase.metadata.create_all(bind=engine)
        MonitoringBase.metadata.create_all(bind=engine)
        PersonaBase.metadata.create_all(bind=engine)
        SubscriptionBase.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully with all models including subscription system")
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def close_database():
    """
    Close database connections.
    """
    try:
        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {str(e)}")

# Database dependency for FastAPI
def get_db():
    """
    Database dependency for FastAPI endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 