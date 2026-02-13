"""
Migration Helpers for Unified Logging System

Utilities to support gradual migration from direct loguru imports to unified logging system.
"""

import os
from typing import Dict, Any, Optional
from loguru import logger


def migrate_logger_import(old_logger_instance, service_name: str):
    """
    Helper to migrate existing logger instances to unified system.
    
    This function helps transition from direct loguru usage to unified logging
    while maintaining existing functionality.
    
    Args:
        old_logger_instance: Existing logger instance from direct loguru import
        service_name: Name of the service for unified logging
        
    Returns:
        Migrated logger instance or original if migration not enabled
    """
    migration_status = get_migration_status()
    
    if not migration_status["migration_enabled"]:
        return old_logger_instance
    
    try:
        from .core.unified_logger import get_logger
        unified_logger = get_logger(service_name)
        
        log_migration_progress(
            service_name, 
            "migrated_instance", 
            f"Successfully migrated {service_name} to unified logging system"
        )
        
        return unified_logger
        
    except Exception as e:
        log_migration_progress(
            service_name,
            "migration_failed",
            f"Failed to migrate {service_name}: {e}"
        )
        return old_logger_instance


def get_migration_status() -> Dict[str, Any]:
    """
    Get current migration status across all modules.
    
    Returns:
        Dictionary with migration configuration
    """
    return {
        "migration_enabled": os.getenv("LOGGING_MIGRATION_ENABLED", "false").lower() == "true",
        "migration_mode": os.getenv("LOGGING_MIGRATION_MODE", "gradual"),
        "migration_target": os.getenv("LOGGING_MIGRATION_TARGET", ""),
    }


def log_migration_progress(module: str, status: str, details: str = None):
    """
    Log migration progress for monitoring.
    
    Args:
        module: Name of the module being migrated
        status: Current migration status
        details: Additional details about the migration
    """
    logger.info(f"🔄 Migration [{module}]: {status} - {details}")


def validate_migration(module: str) -> bool:
    """
    Validate that migration worked correctly for a specific module.
    
    Args:
        module: Name of the module to validate
        
    Returns:
        True if migration successful, False otherwise
    """
    try:
        from .core.unified_logger import get_logger
        test_logger = get_logger(f"{module}_validation")
        test_logger.info(f"Testing unified logging for {module}")
        
        # Test basic functionality
        test_logger.debug("Debug test")
        test_logger.info("Info test")
        test_logger.warning("Warning test")
        test_logger.error("Error test")
        
        log_migration_progress(module, "validation_success", "All logging levels working correctly")
        return True
        
    except Exception as e:
        log_migration_progress(module, "validation_failed", f"Validation failed: {e}")
        return False


def rollback_to_loguru(module: str):
    """
    Emergency rollback to direct loguru imports if unified system fails.
    
    Args:
        module: Name of the module to rollback
    """
    log_migration_progress(module, "rollback_initiated", f"Rolling back {module} to direct loguru")
    
    # Set environment variable to disable unified logging
    os.environ["LOGGING_MIGRATION_ENABLED"] = "false"
    
    log_migration_progress(module, "rollback_complete", f"Successfully rolled back {module} to direct loguru")


def get_migration_target_list() -> list:
    """
    Get list of target modules for migration from environment variable.
    
    Returns:
        List of module names to migrate
    """
    migration_target = os.getenv("LOGGING_MIGRATION_TARGET", "")
    if migration_target:
        return [module.strip() for module in migration_target.split(",") if module.strip()]
    return []


def is_migration_enabled() -> bool:
    """
    Check if migration is currently enabled.
    
    Returns:
        True if migration is enabled, False otherwise
    """
    return get_migration_status()["migration_enabled"]


def get_migration_mode() -> str:
    """
    Get current migration mode.
    
    Returns:
        Migration mode ('gradual', 'full', or 'disabled')
    """
    return get_migration_status()["migration_mode"]
