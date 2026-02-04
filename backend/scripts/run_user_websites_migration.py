"""
Migration script to create the user_websites table.
"""
from pathlib import Path
import sqlite3
from loguru import logger


def run_migration():
    """Run the user websites table migration."""
    try:
        logger.info("🔄 Starting user websites table migration...")
        backend_dir = Path(__file__).resolve().parents[1]
        migration_file = backend_dir / "database" / "migrations" / "add_user_websites_table.sql"
        db_file = backend_dir / "alwrity.db"

        if not migration_file.exists():
            raise FileNotFoundError(f"Migration file not found: {migration_file}")

        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_websites'")
            if cursor.fetchone():
                logger.info("ℹ️ Table 'user_websites' already exists, skipping migration")
                return

            migration_sql = migration_file.read_text()
            cursor.executescript(migration_sql)
            conn.commit()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_websites'")
            if cursor.fetchone():
                logger.info("✅ Table 'user_websites' created successfully")
            else:
                logger.warning("⚠️ Migration completed but table not found")

    except Exception as exc:
        logger.error(f"❌ Migration failed: {exc}")
        raise


if __name__ == "__main__":
    run_migration()
