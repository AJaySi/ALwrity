"""
Wix OAuth2 Service
Handles Wix OAuth2 authentication flow and token storage.
"""

import sqlite3
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy import text

from services.database import get_user_data_engine


class WixOAuthService:
    """Manages Wix OAuth2 authentication flow and token storage."""
    
    def __init__(self, db_path: str = "alwrity.db"):
        self.db_path = db_path
        self._init_db()
        self._init_postgres_tables()
    
    def _init_db(self):
        """Initialize database tables for OAuth tokens."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS wix_oauth_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    access_token TEXT NOT NULL,
                    refresh_token TEXT,
                    token_type TEXT DEFAULT 'bearer',
                    expires_at TIMESTAMP,
                    expires_in INTEGER,
                    scope TEXT,
                    site_id TEXT,
                    member_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            conn.commit()
        logger.info("Wix OAuth database initialized.")

    def _init_postgres_tables(self):
        """Initialize PostgreSQL tables for OAuth tokens."""
        engine = get_user_data_engine()
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS wix_oauth_tokens (
                        id SERIAL PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        access_token TEXT NOT NULL,
                        refresh_token TEXT,
                        token_type TEXT DEFAULT 'bearer',
                        expires_at TIMESTAMP,
                        expires_in INTEGER,
                        scope TEXT,
                        site_id TEXT,
                        member_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                    """
                )
            )
        logger.info("Wix OAuth PostgreSQL tables initialized.")

    def _execute_postgres(self, query: str, params: Optional[Dict[str, Any]] = None):
        engine = get_user_data_engine()
        with engine.begin() as conn:
            return conn.execute(text(query), params or {})

    @staticmethod
    def _normalize_datetime(value: Any) -> Optional[datetime]:
        if not value:
            return None
        if isinstance(value, datetime):
            return value.replace(tzinfo=None)
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
            except Exception:
                return None
        return None
    
    def store_tokens(
        self,
        user_id: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_in: Optional[int] = None,
        token_type: str = 'bearer',
        scope: Optional[str] = None,
        site_id: Optional[str] = None,
        member_id: Optional[str] = None
    ) -> bool:
        """
        Store Wix OAuth tokens in the database.
        
        Args:
            user_id: User ID (Clerk string)
            access_token: Access token from Wix
            refresh_token: Optional refresh token
            expires_in: Optional expiration time in seconds
            token_type: Token type (default: 'bearer')
            scope: Optional OAuth scope
            site_id: Optional Wix site ID
            member_id: Optional Wix member ID
            
        Returns:
            True if tokens were stored successfully
        """
        try:
            expires_at = None
            if expires_in:
                expires_at = datetime.now() + timedelta(seconds=expires_in)

            # Persist tokens to PostgreSQL first, then SQLite for rollback.
            self._execute_postgres(
                """
                INSERT INTO wix_oauth_tokens
                (user_id, access_token, refresh_token, token_type, expires_at, expires_in, scope, site_id, member_id)
                VALUES (:user_id, :access_token, :refresh_token, :token_type, :expires_at, :expires_in, :scope, :site_id, :member_id)
                """,
                {
                    "user_id": user_id,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": token_type,
                    "expires_at": expires_at,
                    "expires_in": expires_in,
                    "scope": scope,
                    "site_id": site_id,
                    "member_id": member_id,
                },
            )

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''
                    INSERT INTO wix_oauth_tokens 
                    (user_id, access_token, refresh_token, token_type, expires_at, expires_in, scope, site_id, member_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (user_id, access_token, refresh_token, token_type, expires_at, expires_in, scope, site_id, member_id),
                )
                conn.commit()
                logger.info(f"Wix OAuth: Token inserted into database for user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing Wix tokens for user {user_id}: {e}")
            return False
    
    def get_user_tokens(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active Wix tokens for a user."""
        try:
            # Read from PostgreSQL SSOT (primary).
            result = self._execute_postgres(
                """
                SELECT id, access_token, refresh_token, token_type, expires_at, expires_in, scope, site_id, member_id, created_at
                FROM wix_oauth_tokens
                WHERE user_id = :user_id
                AND is_active = TRUE
                AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                ORDER BY created_at DESC
                """,
                {"user_id": user_id},
            )

            tokens = []
            for row in result.fetchall():
                tokens.append(
                    {
                        "id": row[0],
                        "access_token": row[1],
                        "refresh_token": row[2],
                        "token_type": row[3],
                        "expires_at": row[4],
                        "expires_in": row[5],
                        "scope": row[6],
                        "site_id": row[7],
                        "member_id": row[8],
                        "created_at": row[9],
                    }
                )

            return tokens
                
        except Exception as e:
            logger.error(f"Error getting Wix tokens for user {user_id}: {e}")
            return []
    
    def get_user_token_status(self, user_id: str) -> Dict[str, Any]:
        """Get detailed token status for a user including expired tokens."""
        try:
            # Read from PostgreSQL SSOT (primary).
            result = self._execute_postgres(
                """
                SELECT id, access_token, refresh_token, token_type, expires_at, expires_in, scope, site_id, member_id, created_at, is_active
                FROM wix_oauth_tokens
                WHERE user_id = :user_id
                ORDER BY created_at DESC
                """,
                {"user_id": user_id},
            )

            all_tokens = []
            active_tokens = []
            expired_tokens = []

            for row in result.fetchall():
                token_data = {
                    "id": row[0],
                    "access_token": row[1],
                    "refresh_token": row[2],
                    "token_type": row[3],
                    "expires_at": row[4],
                    "expires_in": row[5],
                    "scope": row[6],
                    "site_id": row[7],
                    "member_id": row[8],
                    "created_at": row[9],
                    "is_active": bool(row[10]),
                }
                all_tokens.append(token_data)

                is_active_flag = bool(row[10])
                expires_at_val = self._normalize_datetime(row[4])
                not_expired = expires_at_val > datetime.utcnow() if expires_at_val else True

                if is_active_flag and not_expired:
                    active_tokens.append(token_data)
                else:
                    expired_tokens.append(token_data)

            return {
                "has_tokens": len(all_tokens) > 0,
                "has_active_tokens": len(active_tokens) > 0,
                "has_expired_tokens": len(expired_tokens) > 0,
                "active_tokens": active_tokens,
                "expired_tokens": expired_tokens,
                "total_tokens": len(all_tokens),
                "last_token_date": all_tokens[0]["created_at"] if all_tokens else None,
            }
                
        except Exception as e:
            logger.error(f"Error getting Wix token status for user {user_id}: {e}")
            return {
                "has_tokens": False,
                "has_active_tokens": False,
                "has_expired_tokens": False,
                "active_tokens": [],
                "expired_tokens": [],
                "total_tokens": 0,
                "last_token_date": None,
                "error": str(e)
            }
    
    def update_tokens(
        self,
        user_id: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_in: Optional[int] = None
    ) -> bool:
        """Update tokens for a user (e.g., after refresh)."""
        try:
            expires_at = None
            if expires_in:
                expires_at = datetime.now() + timedelta(seconds=expires_in)

            if refresh_token:
                self._execute_postgres(
                    """
                    UPDATE wix_oauth_tokens
                    SET access_token = :access_token,
                        refresh_token = :refresh_token,
                        expires_at = :expires_at,
                        expires_in = :expires_in,
                        is_active = TRUE,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = :user_id AND refresh_token = :refresh_token
                    """,
                    {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "expires_at": expires_at,
                        "expires_in": expires_in,
                        "user_id": user_id,
                    },
                )
            else:
                self._execute_postgres(
                    """
                    UPDATE wix_oauth_tokens
                    SET access_token = :access_token,
                        expires_at = :expires_at,
                        expires_in = :expires_in,
                        is_active = TRUE,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = :user_id
                    AND id = (
                        SELECT id FROM wix_oauth_tokens
                        WHERE user_id = :user_id
                        ORDER BY created_at DESC
                        LIMIT 1
                    )
                    """,
                    {
                        "access_token": access_token,
                        "expires_at": expires_at,
                        "expires_in": expires_in,
                        "user_id": user_id,
                    },
                )

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if refresh_token:
                    cursor.execute(
                        '''
                        UPDATE wix_oauth_tokens 
                        SET access_token = ?, refresh_token = ?, expires_at = ?, expires_in = ?, 
                            is_active = TRUE, updated_at = datetime('now')
                        WHERE user_id = ? AND refresh_token = ?
                        ''',
                        (access_token, refresh_token, expires_at, expires_in, user_id, refresh_token),
                    )
                else:
                    cursor.execute(
                        '''
                        UPDATE wix_oauth_tokens 
                        SET access_token = ?, expires_at = ?, expires_in = ?, 
                            is_active = TRUE, updated_at = datetime('now')
                        WHERE user_id = ? AND id = (SELECT id FROM wix_oauth_tokens WHERE user_id = ? ORDER BY created_at DESC LIMIT 1)
                        ''',
                        (access_token, expires_at, expires_in, user_id, user_id),
                    )
                conn.commit()
                logger.info(f"Wix OAuth: Tokens updated for user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating Wix tokens for user {user_id}: {e}")
            return False
    
    def revoke_token(self, user_id: str, token_id: int) -> bool:
        """Revoke a Wix OAuth token."""
        try:
            result = self._execute_postgres(
                """
                UPDATE wix_oauth_tokens
                SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = :user_id AND id = :token_id
                """,
                {"user_id": user_id, "token_id": token_id},
            )

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''
                    UPDATE wix_oauth_tokens 
                    SET is_active = FALSE, updated_at = datetime('now')
                    WHERE user_id = ? AND id = ?
                    ''',
                    (user_id, token_id),
                )
                conn.commit()

            if (result.rowcount or 0) > 0:
                logger.info(f"Wix token {token_id} revoked for user {user_id}")
                return True
            return False
                
        except Exception as e:
            logger.error(f"Error revoking Wix token: {e}")
            return False
