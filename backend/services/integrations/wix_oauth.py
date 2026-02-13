"""
Wix OAuth2 Service
Handles Wix OAuth2 authentication flow and token storage.
"""

from contextlib import contextmanager
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy import text
import sqlite3
import os
from services.database import get_user_data_db_session


from services.database import get_user_db_path

class WixOAuthService:
    """Manages Wix OAuth2 authentication flow and token storage."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
    
    def _get_db_path(self, user_id: str) -> str:
        if self.db_path:
            return self.db_path
        return get_user_db_path(user_id)
    
    def _init_db(self, user_id: str):
        """Initialize database tables for OAuth tokens."""
        db_path = self._get_db_path(user_id)
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        with sqlite3.connect(db_path) as conn:
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
            # Ensure DB is initialized for this user
            self._init_db(user_id)
            db_path = self._get_db_path(user_id)
            
            expires_at = None
            if expires_in:
                expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO wix_oauth_tokens 
                    (user_id, access_token, refresh_token, token_type, expires_at, expires_in, scope, site_id, member_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, access_token, refresh_token, token_type, expires_at, expires_in, scope, site_id, member_id))
                conn.commit()
                logger.info(f"Wix OAuth: Token inserted into database for user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing Wix tokens for user {user_id}: {e}")
            return False
    
    def get_user_tokens(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active Wix tokens for a user."""
        try:
            # Ensure database tables exist to prevent 'no such table' errors
            self._init_db(user_id)
            
            db_path = self._get_db_path(user_id)
            if not os.path.exists(db_path):
                return []
                
            with sqlite3.connect(db_path) as conn:
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
            # Ensure database tables exist to prevent 'no such table' errors
            self._init_db(user_id)

            db_path = self._get_db_path(user_id)
            if not os.path.exists(db_path):
                return {
                    "has_tokens": False,
                    "has_active_tokens": False,
                    "has_expired_tokens": False,
                    "active_tokens": [],
                    "expired_tokens": [],
                    "total_tokens": 0,
                    "last_token_date": None
                }

            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Get all tokens (active and expired)
                cursor.execute('''
                    SELECT id, access_token, refresh_token, token_type, expires_at, expires_in, scope, site_id, member_id, created_at, is_active
                    FROM wix_oauth_tokens
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                ''', (user_id,))
                
                rows = cursor.fetchall()
                all_tokens = []
                active_tokens = []
                expired_tokens = []

                for row in rows:
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
                            dt = datetime.fromisoformat(expires_at_val) if isinstance(expires_at_val, str) else expires_at_val
                            not_expired = dt > datetime.utcnow()
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
            # Ensure DB initialized for this user
            self._init_db(user_id)
            db_path = self._get_db_path(user_id)

            expires_at = None
            if expires_in:
                expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                if refresh_token:
                    cursor.execute('''
                        UPDATE wix_oauth_tokens 
                        SET access_token = ?, refresh_token = ?, expires_at = ?, expires_in = ?, is_active = 1, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND refresh_token = ?
                    ''', (access_token, refresh_token, expires_at, expires_in, user_id, refresh_token))
                else:
                    # Update most recent token
                    cursor.execute('''
                        UPDATE wix_oauth_tokens 
                        SET access_token = ?, expires_at = ?, expires_in = ?, is_active = 1, updated_at = CURRENT_TIMESTAMP
                        WHERE id = (SELECT id FROM wix_oauth_tokens WHERE user_id = ? ORDER BY created_at DESC LIMIT 1)
                    ''', (access_token, expires_at, expires_in, user_id))
                conn.commit()
                logger.info(f"Wix OAuth: Tokens updated for user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating Wix tokens for user {user_id}: {e}")
            return False
    
    def revoke_token(self, user_id: str, token_id: int) -> bool:
        """Revoke a Wix OAuth token."""
        try:
            db_path = self._get_db_path(user_id)
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE wix_oauth_tokens 
                    SET is_active = FALSE, updated_at = datetime('now')
                    WHERE user_id = ? AND id = ?
                ''', (user_id, token_id))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Wix token {token_id} revoked for user {user_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error revoking Wix token: {e}")
            return False
