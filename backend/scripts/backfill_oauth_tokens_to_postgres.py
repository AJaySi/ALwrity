"""
Backfill OAuth tokens from SQLite to PostgreSQL.
"""

import argparse
import sqlite3
from datetime import datetime
from typing import Any, Dict, Iterable, Tuple

from loguru import logger

from services.database import get_user_data_db_session
from models.oauth_token_models import BingOAuthToken, WordPressOAuthToken, WixOAuthToken


def _parse_datetime(value: Any) -> Any:
    if value is None or isinstance(value, datetime):
        return value
    for parser in (datetime.fromisoformat,):
        try:
            return parser(value)
        except Exception:
            continue
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
        try:
            return datetime.strptime(value, fmt)
        except Exception:
            continue
    return None


def _fetch_rows(conn: sqlite3.Connection, query: str) -> Iterable[Tuple[Any, ...]]:
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


def _row_exists(session, model, data: Dict[str, Any]) -> bool:
    query = session.query(model).filter(
        model.user_id == data["user_id"],
        model.access_token == data["access_token"],
    )
    refresh_token = data.get("refresh_token")
    if refresh_token:
        query = query.filter(model.refresh_token == refresh_token)
    created_at = data.get("created_at")
    if created_at:
        query = query.filter(model.created_at == created_at)
    return session.query(query.exists()).scalar()


def _backfill_tokens(
    session,
    sqlite_conn: sqlite3.Connection,
    table_name: str,
    model,
    columns: Tuple[str, ...],
) -> int:
    select_columns = ", ".join(columns)
    rows = _fetch_rows(sqlite_conn, f"SELECT {select_columns} FROM {table_name}")
    inserted = 0
    for row in rows:
        data = dict(zip(columns, row))
        data["expires_at"] = _parse_datetime(data.get("expires_at"))
        data["created_at"] = _parse_datetime(data.get("created_at"))
        data["updated_at"] = _parse_datetime(data.get("updated_at"))
        if _row_exists(session, model, data):
            continue
        session.add(model(**data))
        inserted += 1
    return inserted


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill OAuth tokens into PostgreSQL.")
    parser.add_argument(
        "--sqlite-path",
        default="alwrity.db",
        help="Path to the SQLite database file (default: alwrity.db).",
    )
    args = parser.parse_args()

    session = get_user_data_db_session()
    if session is None:
        logger.error("PostgreSQL session unavailable. Set USER_DATA_DATABASE_URL before running.")
        return

    sqlite_conn = sqlite3.connect(args.sqlite_path)
    try:
        inserts = {}
        inserts["bing"] = _backfill_tokens(
            session,
            sqlite_conn,
            "bing_oauth_tokens",
            BingOAuthToken,
            (
                "user_id",
                "access_token",
                "refresh_token",
                "token_type",
                "expires_at",
                "scope",
                "site_url",
                "created_at",
                "updated_at",
                "is_active",
            ),
        )
        inserts["wordpress"] = _backfill_tokens(
            session,
            sqlite_conn,
            "wordpress_oauth_tokens",
            WordPressOAuthToken,
            (
                "user_id",
                "access_token",
                "refresh_token",
                "token_type",
                "expires_at",
                "scope",
                "blog_id",
                "blog_url",
                "created_at",
                "updated_at",
                "is_active",
            ),
        )
        inserts["wix"] = _backfill_tokens(
            session,
            sqlite_conn,
            "wix_oauth_tokens",
            WixOAuthToken,
            (
                "user_id",
                "access_token",
                "refresh_token",
                "token_type",
                "expires_at",
                "expires_in",
                "scope",
                "site_id",
                "member_id",
                "created_at",
                "updated_at",
                "is_active",
            ),
        )
        session.commit()
        for provider, count in inserts.items():
            logger.info("Backfilled %s tokens into PostgreSQL for %s", count, provider)
    except Exception as e:
        session.rollback()
        logger.error(f"Backfill failed: {e}")
    finally:
        session.close()
        sqlite_conn.close()


if __name__ == "__main__":
    main()
