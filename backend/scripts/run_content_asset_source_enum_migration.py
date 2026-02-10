#!/usr/bin/env python3
"""Run migration to add missing content asset source module enum values."""

from pathlib import Path

from sqlalchemy import text

from services.database import SessionLocal


def run_migration() -> None:
    backend_dir = Path(__file__).resolve().parent.parent
    migration_file = backend_dir / "database" / "migrations" / "add_content_asset_source_modules.sql"

    if not migration_file.exists():
        raise FileNotFoundError(f"Migration file not found: {migration_file}")

    sql = migration_file.read_text(encoding="utf-8")

    db = SessionLocal()
    try:
        db.execute(text(sql))
        db.commit()
        print("✅ Content asset source enum migration completed")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
