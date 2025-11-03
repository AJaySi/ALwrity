from typing import Set
from sqlalchemy.orm import Session


_checked_subscription_plan_columns: bool = False


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
        # Discover existing columns
        result = db.execute("PRAGMA table_info(subscription_plans)")
        cols: Set[str] = {row[1] for row in result}

        # Columns we may reference in models but might be missing in older DBs
        required_columns = {
            "exa_calls_limit": "INTEGER DEFAULT 0",
        }

        for col_name, ddl in required_columns.items():
            if col_name not in cols:
                db.execute(f"ALTER TABLE subscription_plans ADD COLUMN {col_name} {ddl}")
        db.commit()
    except Exception:
        # Do not block app if pragma/alter fails; let normal errors surface
        db.rollback()
    finally:
        _checked_subscription_plan_columns = True


