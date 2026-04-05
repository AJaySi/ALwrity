"""
Production Optimizer Module
Handles production-specific optimizations and configurations.
"""

import os
import sys
from typing import List, Dict, Any


class ProductionOptimizer:
    """Optimizes ALwrity backend for production deployment."""
    
    def __init__(self):
        self.production_optimizations = {
            'disable_spacy_download': False,  # Allow spaCy verification (required for persona generation)
            'disable_nltk_download': False,   # Allow NLTK verification (required for persona generation)
            'skip_linguistic_setup': False,   # Always verify linguistic models are available
            'minimal_database_setup': True,
            'skip_file_creation': True
        }
    
    def apply_production_optimizations(self) -> bool:
        """Apply production-specific optimizations."""
        print("🚀 Applying production optimizations...")
        
        # Set production environment variables
        self._set_production_env_vars()
        
        # Disable heavy operations
        self._disable_heavy_operations()
        
        # Optimize logging
        self._optimize_logging()
        
        print("✅ Production optimizations applied")
        return True
    
    def _set_production_env_vars(self) -> None:
        """Set production-specific environment variables."""
        production_vars = {
            # Note: PORT is NOT set here - it's provided by the deployment platform (e.g., Render)
            # Don't override PORT as it must come from the environment
            # Note: HOST is not set here - it's auto-detected by start_backend()
            # Based on deployment environment (cloud vs local)
            'RELOAD': 'false',
            'LOG_LEVEL': 'INFO',
            'DEBUG': 'false',
            'PYTHONUNBUFFERED': '1',  # Ensure logs are flushed immediately
            'PYTHONDONTWRITEBYTECODE': '1'  # Don't create .pyc files
        }
        
        for key, value in production_vars.items():
            os.environ.setdefault(key, value)
            print(f"   ✅ {key}={value}")
    
    def _disable_heavy_operations(self) -> None:
        """Configure operations for production startup."""
        print("   ⚡ Configuring operations for production...")
        
        # Note: spaCy and NLTK verification are allowed in production
        # Models should be pre-installed during build phase (via render.yaml or similar)
        # The setup will verify models exist without re-downloading
        
        print("   ✅ Production operations configured")
    
    def _optimize_logging(self) -> None:
        """Optimize logging for production."""
        print("   📝 Optimizing logging for production...")
        
        # Set appropriate log level
        os.environ.setdefault('LOG_LEVEL', 'INFO')
        
        # Disable debug logging
        os.environ.setdefault('DEBUG', 'false')
        
        print("   ✅ Logging optimized")
    
    def skip_linguistic_setup(self) -> bool:
        """Skip linguistic analysis setup in production."""
        if os.getenv('SKIP_LINGUISTIC_SETUP', 'false').lower() == 'true':
            print("⚠️  Skipping linguistic analysis setup (production mode)")
            return True
        return False
    
    def skip_spacy_setup(self) -> bool:
        """Skip spaCy model setup in production."""
        if os.getenv('DISABLE_SPACY_DOWNLOAD', 'false').lower() == 'true':
            print("⚠️  Skipping spaCy model setup (production mode)")
            return True
        return False
    
    def skip_nltk_setup(self) -> bool:
        """Skip NLTK data setup in production."""
        if os.getenv('DISABLE_NLTK_DOWNLOAD', 'false').lower() == 'true':
            print("⚠️  Skipping NLTK data setup (production mode)")
            return True
        return False
    
    def get_production_config(self) -> Dict[str, Any]:
        """Get production configuration settings."""
        return {
            'host': os.getenv('HOST', '0.0.0.0'),
            'port': int(os.getenv('PORT', '8000')),
            'reload': False,  # Never reload in production
            'log_level': os.getenv('LOG_LEVEL', 'info'),
            'access_log': True,
            'workers': 1,  # Single worker for Render
            'timeout_keep_alive': 30,
            'timeout_graceful_shutdown': 30
        }
    
    def validate_production_environment(self) -> bool:
        """Validate that the environment is ready for production."""
        print("🔍 Validating production environment...")
        
        # Check critical environment variables
        required_vars = ['HOST', 'PORT', 'LOG_LEVEL']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing environment variables: {missing_vars}")
            return False
        
        # Check that reload is disabled
        if os.getenv('RELOAD', 'false').lower() == 'true':
            print("⚠️  Warning: RELOAD is enabled in production")
        
        print("✅ Production environment validated")
        return True
