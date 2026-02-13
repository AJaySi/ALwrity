"""
Logger Configuration Module - Consolidated into Unified Logging System
Handles clean logging setup for end users using the unified logging system.
"""

import os
import logging
from loguru import logger

# Use unified logger for consistent logging
unified_logger = logger.bind(service="logging_config")


def setup_clean_logging():
    """Set up clean logging for end users using unified system."""
    verbose_mode = os.getenv("ALWRITY_VERBOSE", "false").lower() == "true"
    
    # Always remove all existing handlers first to prevent conflicts
    try:
        unified_logger.remove()  # Remove default handler (no parameters needed)
    except Exception as e:
        # If remove fails, continue anyway
        if verbose_mode:
            print(f"⚠️  Warning: Could not remove logger handlers: {e}")
    
    if not verbose_mode:
        # Suppress verbose logging for end users - be more aggressive
        logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)
        logging.getLogger('sqlalchemy.pool').setLevel(logging.CRITICAL)
        logging.getLogger('sqlalchemy.dialects').setLevel(logging.CRITICAL)
        logging.getLogger('sqlalchemy.orm').setLevel(logging.CRITICAL)
        logging.getLogger('sqlalchemy').setLevel(logging.CRITICAL)
        logging.getLogger('sqlalchemy.engine.Engine').setLevel(logging.CRITICAL)
        
        # Suppress service initialization logs (but allow scheduler logs)
        logging.getLogger('services').setLevel(logging.WARNING)
        
        # Ensure scheduler logs are visible
        logging.getLogger('task_scheduler').setLevel(logging.INFO)
        logging.getLogger('services.scheduler').setLevel(logging.INFO)
        logging.getLogger('services.scheduler.core').setLevel(logging.INFO)
        
        logging.getLogger('api').setLevel(logging.WARNING)
        logging.getLogger('models').setLevel(logging.WARNING)
        
        # Suppress specific noisy loggers
        noisy_loggers = [
            'linkedin_persona_service',
            'facebook_persona_service', 
            'core_persona_service',
            'persona_analysis_service',
            'ai_service_manager',
            'ai_engine_service',
            'website_analyzer',
            'competitor_analyzer',
            'keyword_researcher',
            'content_gap_analyzer',
            'onboarding_data_service',
            'comprehensive_user_data',
            'strategy_data',
            'gap_analysis_data'          
           
        ]
        
        for noisy_logger in noisy_loggers:
            try:
                logging.getLogger(noisy_logger).setLevel(logging.WARNING)
            except:
                pass  # Logger might not exist yet
    
    return verbose_mode


def get_uvicorn_log_level():
    """Get appropriate log level for uvicorn based on verbosity."""
    verbose_mode = os.getenv("ALWRITY_VERBOSE", "false").lower() == "true"
    return "debug" if verbose_mode else "info"
