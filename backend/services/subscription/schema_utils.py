from typing import Set
from sqlalchemy.orm import Session
from sqlalchemy import text
from loguru import logger


_checked_subscription_plan_columns: bool = False
_checked_usage_summaries_columns: bool = False


def ensure_subscription_plan_columns(db: Session) -> None:
    """Ensure required columns exist on subscription_plans for runtime safety.

    This is a defensive guard for environments where migrations have not yet
    been applied. If columns are missing (e.g., exa_calls_limit), we add them
    with a safe default so ORM queries do not fail.
    """
    global _checked_subscription_plan_columns
    if _checked_subscription_plan_columns:
        return

    try:
        # Discover existing columns using PRAGMA
        result = db.execute(text("PRAGMA table_info(subscription_plans)"))
        cols: Set[str] = {row[1] for row in result}
        
        logger.debug(f"Schema check: Found {len(cols)} columns in subscription_plans table")

        # Columns we may reference in models but might be missing in older DBs
        required_columns = {
            "exa_calls_limit": "INTEGER DEFAULT 0",
            "video_calls_limit": "INTEGER DEFAULT 0",
            "image_edit_calls_limit": "INTEGER DEFAULT 0",
            "audio_calls_limit": "INTEGER DEFAULT 0",
        }

        for col_name, ddl in required_columns.items():
            if col_name not in cols:
                logger.info(f"Adding missing column {col_name} to subscription_plans table")
                try:
                    db.execute(text(f"ALTER TABLE subscription_plans ADD COLUMN {col_name} {ddl}"))
                    db.commit()
                    logger.info(f"Successfully added column {col_name}")
                except Exception as alter_err:
                    logger.error(f"Failed to add column {col_name}: {alter_err}")
                    db.rollback()
                    # Don't set flag on error - allow retry
                    raise
            else:
                logger.debug(f"Column {col_name} already exists")
        
        # Only set flag if we successfully completed the check
        _checked_subscription_plan_columns = True
    except Exception as e:
        logger.error(f"Error ensuring subscription_plan columns: {e}", exc_info=True)
        db.rollback()
        # Don't set the flag if there was an error, so we retry next time
        _checked_subscription_plan_columns = False
        raise


def ensure_usage_summaries_columns(db: Session) -> None:
    """Ensure required columns exist on usage_summaries for runtime safety.

    This is a defensive guard for environments where migrations have not yet
    been applied. If columns are missing (e.g., exa_calls, exa_cost), we add them
    with a safe default so ORM queries do not fail.
    """
    global _checked_usage_summaries_columns
    if _checked_usage_summaries_columns:
        return

    try:
        # Discover existing columns using PRAGMA
        result = db.execute(text("PRAGMA table_info(usage_summaries)"))
        cols: Set[str] = {row[1] for row in result}
        
        logger.debug(f"Schema check: Found {len(cols)} columns in usage_summaries table")

        # Columns we may reference in models but might be missing in older DBs
        required_columns = {
            "exa_calls": "INTEGER DEFAULT 0",
            "exa_cost": "REAL DEFAULT 0.0",
            "video_calls": "INTEGER DEFAULT 0",
            "video_cost": "REAL DEFAULT 0.0",
            "image_edit_calls": "INTEGER DEFAULT 0",
            "image_edit_cost": "REAL DEFAULT 0.0",
            "audio_calls": "INTEGER DEFAULT 0",
            "audio_cost": "REAL DEFAULT 0.0",
        }

        for col_name, ddl in required_columns.items():
            if col_name not in cols:
                logger.info(f"Adding missing column {col_name} to usage_summaries table")
                try:
                    db.execute(text(f"ALTER TABLE usage_summaries ADD COLUMN {col_name} {ddl}"))
                    db.commit()
                    logger.info(f"Successfully added column {col_name}")
                except Exception as alter_err:
                    logger.error(f"Failed to add column {col_name}: {alter_err}")
                    db.rollback()
                    # Don't set flag on error - allow retry
                    raise
            else:
                logger.debug(f"Column {col_name} already exists")
        
        # Only set flag if we successfully completed the check
        _checked_usage_summaries_columns = True
    except Exception as e:
        logger.error(f"Error ensuring usage_summaries columns: {e}", exc_info=True)
        db.rollback()
        # Don't set the flag if there was an error, so we retry next time
        _checked_usage_summaries_columns = False
        raise


def ensure_all_schema_columns(db: Session) -> None:
    """Ensure all required columns exist in subscription-related tables."""
    ensure_subscription_plan_columns(db)
    ensure_usage_summaries_columns(db)


