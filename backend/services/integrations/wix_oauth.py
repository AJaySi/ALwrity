"""
Wix OAuth2 Service
Handles Wix OAuth2 authentication flow and token storage.
"""

import os
import sqlite3
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy import func

from ..database import get_user_data_db_session
from models.oauth_token_models import WixOAuthToken


class WixOAuthService:
    """Manages Wix OAuth2 authentication flow and token storage."""
    
    def __init__(self, db_path: str = "alwrity.db"):
        self.db_path = db_path
        self._init_db()
    
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

    def _get_postgres_session(self):
        try:
            session = get_user_data_db_session()
            if session is None:
                logger.warning("Wix OAuth: PostgreSQL session unavailable; skipping dual-write")
            return session
        except Exception as e:
            logger.warning(f"Wix OAuth: Unable to create PostgreSQL session: {e}")
            return None

    def _insert_postgres_token(self, **fields) -> None:
        session = self._get_postgres_session()
        if not session:
            return
        try:
            session.add(WixOAuthToken(**fields))
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Wix OAuth: Failed to insert token into PostgreSQL: {e}")
        finally:
            session.close()

    def _update_postgres_token(
        self,
        user_id: str,
        refresh_token: Optional[str] = None,
        **updates: Any,
    ) -> None:
        session = self._get_postgres_session()
        if not session:
            return
        try:
            query = session.query(WixOAuthToken).filter(WixOAuthToken.user_id == user_id)
            if refresh_token:
                query = query.filter(WixOAuthToken.refresh_token == refresh_token)
            token = query.order_by(WixOAuthToken.created_at.desc()).first()
            if not token:
                logger.warning("Wix OAuth: No matching PostgreSQL token found for update")
                return
            for key, value in updates.items():
                setattr(token, key, value)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Wix OAuth: Failed to update token in PostgreSQL: {e}")
        finally:
            session.close()

    def _log_token_count_comparison(self, user_id: str) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM wix_oauth_tokens WHERE user_id = ?",
                    (user_id,),
                )
                sqlite_count = cursor.fetchone()[0] or 0
        except Exception as e:
            logger.warning(f"Wix OAuth: Unable to read SQLite token count: {e}")
            return

        session = self._get_postgres_session()
        if not session:
            return
        try:
            postgres_count = (
                session.query(func.count(WixOAuthToken.id))
                .filter(WixOAuthToken.user_id == user_id)
                .scalar()
                or 0
            )
            if sqlite_count != postgres_count:
                logger.warning(
                    "Wix OAuth: Token count mismatch for user %s (sqlite=%s, postgres=%s)",
                    user_id,
                    sqlite_count,
                    postgres_count,
                )
            else:
                logger.info(
                    "Wix OAuth: Token count match for user %s (count=%s)",
                    user_id,
                    sqlite_count,
                )
        except Exception as e:
            logger.warning(f"Wix OAuth: Unable to compare token counts: {e}")
        finally:
            session.close()
    
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
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO wix_oauth_tokens 
                    (user_id, access_token, refresh_token, token_type, expires_at, expires_in, scope, site_id, member_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, access_token, refresh_token, token_type, expires_at, expires_in, scope, site_id, member_id))
                conn.commit()
                logger.info(f"Wix OAuth: Token inserted into database for user {user_id}")

            self._insert_postgres_token(
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                token_type=token_type,
                expires_at=expires_at,
                expires_in=expires_in,
                scope=scope,
                site_id=site_id,
                member_id=member_id,
            )
            self._log_token_count_comparison(user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing Wix tokens for user {user_id}: {e}")
            return False
    
    def get_user_tokens(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active Wix tokens for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, access_token, refresh_token, token_type, expires_at, expires_in, scope, site_id, member_id, created_at
                    FROM wix_oauth_tokens
                    WHERE user_id = ? AND is_active = TRUE AND (expires_at IS NULL OR expires_at > datetime('now'))
                    ORDER BY created_at DESC
                ''', (user_id,))
                
                tokens = []
                for row in cursor.fetchall():
                    tokens.append({
                        "id": row[0],
                        "access_token": row[1],
                        "refresh_token": row[2],
                        "token_type": row[3],
                        "expires_at": row[4],
                        "expires_in": row[5],
                        "scope": row[6],
                        "site_id": row[7],
                        "member_id": row[8],
                        "created_at": row[9]
                    })
                
                return tokens
                
        except Exception as e:
            logger.error(f"Error getting Wix tokens for user {user_id}: {e}")
            return []
    
    def get_user_token_status(self, user_id: str) -> Dict[str, Any]:
        """Get detailed token status for a user including expired tokens."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get all tokens (active and expired)
                cursor.execute('''
                    SELECT id, access_token, refresh_token, token_type, expires_at, expires_in, scope, site_id, member_id, created_at, is_active
                    FROM wix_oauth_tokens
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                ''', (user_id,))
                
                all_tokens = []
                active_tokens = []
                expired_tokens = []
                
                for row in cursor.fetchall():
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
                        "is_active": bool(row[10])
                    }
                    all_tokens.append(token_data)
                    
                    # Determine expiry using robust parsing and is_active flag
                    is_active_flag = bool(row[10])
                    not_expired = False
                    try:
                        expires_at_val = row[4]
                        if expires_at_val:
                            # First try Python parsing
                            try:
                                dt = datetime.fromisoformat(expires_at_val) if isinstance(expires_at_val, str) else expires_at_val
                                not_expired = dt > datetime.now()
                            except Exception:
                                # Fallback to SQLite comparison
                                cursor.execute("SELECT datetime('now') < ?", (expires_at_val,))
                                not_expired = cursor.fetchone()[0] == 1
                        else:
                            # No expiry stored => consider not expired
                            not_expired = True
                    except Exception:
                        not_expired = False

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
                    "last_token_date": all_tokens[0]["created_at"] if all_tokens else None
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
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if refresh_token:
                    cursor.execute('''
                        UPDATE wix_oauth_tokens 
                        SET access_token = ?, refresh_token = ?, expires_at = ?, expires_in = ?, 
                            is_active = TRUE, updated_at = datetime('now')
                        WHERE user_id = ? AND refresh_token = ?
                    ''', (access_token, refresh_token, expires_at, expires_in, user_id, refresh_token))
                else:
                    cursor.execute('''
                        UPDATE wix_oauth_tokens 
                        SET access_token = ?, expires_at = ?, expires_in = ?, 
                            is_active = TRUE, updated_at = datetime('now')
                        WHERE user_id = ? AND id = (SELECT id FROM wix_oauth_tokens WHERE user_id = ? ORDER BY created_at DESC LIMIT 1)
                    ''', (access_token, expires_at, expires_in, user_id, user_id))
                conn.commit()
                logger.info(f"Wix OAuth: Tokens updated for user {user_id}")

            self._update_postgres_token(
                user_id=user_id,
                refresh_token=refresh_token,
                access_token=access_token,
                expires_at=expires_at,
                expires_in=expires_in,
                is_active=True,
            )
            self._log_token_count_comparison(user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating Wix tokens for user {user_id}: {e}")
            return False
    
    def revoke_token(self, user_id: str, token_id: int) -> bool:
        """Revoke a Wix OAuth token."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT refresh_token FROM wix_oauth_tokens WHERE user_id = ? AND id = ?",
                    (user_id, token_id),
                )
                token_row = cursor.fetchone()
                cursor.execute('''
                    UPDATE wix_oauth_tokens 
                    SET is_active = FALSE, updated_at = datetime('now')
                    WHERE user_id = ? AND id = ?
                ''', (user_id, token_id))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Wix token {token_id} revoked for user {user_id}")
                    refresh_token = token_row[0] if token_row else None
                    self._update_postgres_token(
                        user_id=user_id,
                        refresh_token=refresh_token,
                        is_active=False,
                    )
                    self._log_token_count_comparison(user_id)
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error revoking Wix token: {e}")
            return False
