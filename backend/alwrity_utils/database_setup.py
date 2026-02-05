"""
Database Setup Module
Handles database initialization and table creation.
"""

from typing import List, Tuple
import sys
from pathlib import Path
from utils.logger_utils import get_service_logger

# Use service logger for consistent logging
logger = get_service_logger("database_setup")


class DatabaseSetup:
    """Manages database setup for ALwrity backend."""
    
    def __init__(self, production_mode: bool = False):
        self.production_mode = production_mode
    
    def setup_essential_tables(self) -> bool:
        """Set up essential database tables."""
        import os
        verbose = os.getenv("ALWRITY_VERBOSE", "false").lower() == "true"
        
        if verbose:
            print("📊 Setting up essential database tables...")
        
        try:
            from services.database import init_database, engine
            
            # Initialize database connection
            init_database()
            if verbose:
                print("   ✅ Database connection initialized")
            
            # Create essential tables
            self._create_monitoring_tables()
            self._create_subscription_tables()
            self._create_persona_tables()
            self._create_onboarding_tables()
            
            if verbose:
                print("✅ Essential database tables created")
            return True
            
        except Exception as e:
            if verbose:
                print(f"⚠️  Warning: Database setup failed: {e}")
                if self.production_mode:
                    print("   Continuing in production mode...")
                else:
                    print("   This may affect functionality")
            return True  # Don't fail startup for database issues
    
    def _create_monitoring_tables(self) -> bool:
        """Create API monitoring tables."""
        import os
        verbose = os.getenv("ALWRITY_VERBOSE", "false").lower() == "true"
        
        try:
            from models.api_monitoring import Base as MonitoringBase
            MonitoringBase.metadata.create_all(bind=engine)
            if verbose:
                print("   ✅ Monitoring tables created")
            return True
        except Exception as e:
            if verbose:
                print(f"   ⚠️  Monitoring tables failed: {e}")
            return True  # Non-critical
    
    def _create_subscription_tables(self) -> bool:
        """Create subscription and billing tables."""
        import os
        verbose = os.getenv("ALWRITY_VERBOSE", "false").lower() == "true"
        
        try:
            from models.subscription_models import Base as SubscriptionBase
            SubscriptionBase.metadata.create_all(bind=engine)
            if verbose:
                print("   ✅ Subscription tables created")
            return True
        except Exception as e:
            if verbose:
                print(f"   ⚠️  Subscription tables failed: {e}")
            return True  # Non-critical
    
    def _create_persona_tables(self) -> bool:
        """Create persona analysis tables."""
        import os
        verbose = os.getenv("ALWRITY_VERBOSE", "false").lower() == "true"
        
        try:
            from models.persona_models import Base as PersonaBase
            PersonaBase.metadata.create_all(bind=engine)
            if verbose:
                print("   ✅ Persona tables created")
            return True
        except Exception as e:
            if verbose:
                print(f"   ⚠️  Persona tables failed: {e}")
            return True  # Non-critical
    
    def _create_onboarding_tables(self) -> bool:
        """Create onboarding tables."""
        import os
        verbose = os.getenv("ALWRITY_VERBOSE", "false").lower() == "true"
        
        try:
            from models.onboarding import Base as OnboardingBase
            OnboardingBase.metadata.create_all(bind=engine)
            if verbose:
                print("   ✅ Onboarding tables created")
            return True
        except Exception as e:
            if verbose:
                print(f"   ⚠️  Onboarding tables failed: {e}")
            return True  # Non-critical
    
    def verify_tables(self) -> bool:
        """Verify that essential tables exist."""
        import os
        verbose = os.getenv("ALWRITY_VERBOSE", "false").lower() == "true"
        
        if self.production_mode:
            if verbose:
                print("⚠️  Skipping table verification in production mode")
            return True
        
        if verbose:
            print("🔍 Verifying database tables...")
        
        try:
            from services.database import engine
            from sqlalchemy import inspect
            
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            essential_tables = [
                'api_monitoring_logs',
                'subscription_plans',
                'user_subscriptions',
                'onboarding_sessions',
                'persona_data'
            ]
            
            existing_tables = [table for table in essential_tables if table in tables]
            if verbose:
                print(f"   ✅ Found tables: {existing_tables}")
            
            if len(existing_tables) < len(essential_tables):
                missing = [table for table in essential_tables if table not in existing_tables]
                if verbose:
                    print(f"   ⚠️  Missing tables: {missing}")
            
            return True
            
        except Exception as e:
            print(f"   ⚠️  Table verification failed: {e}")
            return True  # Non-critical
    
    def setup_advanced_tables(self) -> bool:
        """Set up advanced tables (non-critical)."""
        if self.production_mode:
            print("⚠️  Skipping advanced table setup in production mode")
            return True
        
        print("🔧 Setting up advanced database features...")
        
        try:
            # Set up monitoring tables
            self._setup_monitoring_tables()
            
            # Set up billing tables  
            self._setup_billing_tables()
            
            logger.debug("✅ Advanced database features configured")
            return True
            
        except Exception as e:
            logger.warning(f"Advanced table setup failed: {e}")
            return True  # Non-critical
    
    def _setup_monitoring_tables(self) -> bool:
        """Set up API monitoring tables."""
        try:
            sys.path.append(str(Path(__file__).parent.parent))
            from scripts.create_monitoring_tables import create_monitoring_tables
            
            if create_monitoring_tables():
                print("   ✅ API monitoring tables created")
                return True
            else:
                print("   ⚠️  API monitoring setup failed")
                return True  # Non-critical
                
        except Exception as e:
            print(f"   ⚠️  Monitoring setup failed: {e}")
            return True  # Non-critical
    
    def _setup_billing_tables(self) -> bool:
        """Set up billing and subscription tables."""
        try:
            sys.path.append(str(Path(__file__).parent.parent))
            from scripts.create_billing_tables import create_billing_tables, check_existing_tables
            from services.database import engine
            
            # Check if tables already exist
            if check_existing_tables(engine):
                logger.debug("✅ Billing tables already exist")
                return True
            
            if create_billing_tables():
                logger.debug("✅ Billing tables created")
                return True
            else:
                logger.warning("Billing setup failed")
                return True  # Non-critical
                
        except Exception as e:
            logger.warning(f"Billing setup failed: {e}")
            return True  # Non-critical
