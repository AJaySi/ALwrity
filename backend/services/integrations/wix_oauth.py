"""
Wix OAuth2 Service
Handles Wix OAuth2 authentication flow and token storage.
"""

import os
import sqlite3
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger

from services.database import get_user_db_path
from services.token_crypto_service import TokenCryptoService


class WixOAuthService:
    """Manages Wix OAuth2 authentication flow and token storage."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self.token_crypto = TokenCryptoService()

    def _get_db_path(self, user_id: str) -> str:
        if self.db_path:
            return self.db_path
        return get_user_db_path(user_id)

    def _init_db(self, user_id: str):
        """Initialize database tables for OAuth tokens."""
        db_path = self._get_db_path(user_id)
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
                    is_active BOOLEAN DEFAULT TRUE,
                    token_key_version TEXT,
                    token_key_reference TEXT
                )
            ''')
            for column_name, column_def in [
                ("token_key_version", "TEXT"),
                ("token_key_reference", "TEXT"),
            ]:
                try:
                    cursor.execute(f"ALTER TABLE wix_oauth_tokens ADD COLUMN {column_name} {column_def}")
                except sqlite3.OperationalError:
                    pass
            conn.commit()

    def store_tokens(self, user_id: str, access_token: str, refresh_token: Optional[str] = None,
                     expires_in: Optional[int] = None, token_type: str = 'bearer', scope: Optional[str] = None,
                     site_id: Optional[str] = None, member_id: Optional[str] = None) -> bool:
        try:
            self._init_db(user_id)
            db_path = self._get_db_path(user_id)
            expires_at = datetime.now() + timedelta(seconds=expires_in) if expires_in else None
            encrypted_access_token, encrypted_refresh_token = self.token_crypto.encrypt_pair(access_token, refresh_token)

            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO wix_oauth_tokens
                    (user_id, access_token, refresh_token, token_type, expires_at, expires_in, scope, site_id, member_id, token_key_version, token_key_reference)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    encrypted_access_token,
                    encrypted_refresh_token,
                    token_type,
                    expires_at,
                    expires_in,
                    scope,
                    site_id,
                    member_id,
                    self.token_crypto.key_version,
                    self.token_crypto.key_reference,
                ))
                conn.commit()
                logger.info(f"Wix OAuth: Encrypted token stored for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing Wix tokens for user {user_id}: {e}")
            return False

    def get_user_tokens(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active Wix token rows (encrypted values)."""
        try:
            self._init_db(user_id)
            db_path = self._get_db_path(user_id)
            if not os.path.exists(db_path):
                return []

            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, access_token, refresh_token, token_type, expires_at, expires_in, scope, site_id, member_id, created_at, token_key_version, token_key_reference
                    FROM wix_oauth_tokens
                    WHERE user_id = ? AND is_active = TRUE AND (expires_at IS NULL OR expires_at > datetime('now'))
                    ORDER BY created_at DESC
                ''', (user_id,))

                return [{
                    "id": row[0], "access_token": row[1], "refresh_token": row[2], "token_type": row[3],
                    "expires_at": row[4], "expires_in": row[5], "scope": row[6], "site_id": row[7],
                    "member_id": row[8], "created_at": row[9], "token_key_version": row[10],
                    "token_key_reference": row[11]
                } for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting Wix tokens for user {user_id}: {e}")
            return []

    def get_user_tokens_decrypted(self, user_id: str) -> List[Dict[str, Any]]:
        """Decrypt tokens for integration managers and token refresh routines."""
        decrypted = []
        for token in self.get_user_tokens(user_id):
            token_copy = dict(token)
            token_copy["access_token"] = self.token_crypto.decrypt_token(token_copy.get("access_token"))
            token_copy["refresh_token"] = self.token_crypto.decrypt_token(token_copy.get("refresh_token"))
            decrypted.append(token_copy)
        return decrypted

    def get_user_token_status(self, user_id: str) -> Dict[str, Any]:
        try:
            self._init_db(user_id)
            db_path = self._get_db_path(user_id)
            if not os.path.exists(db_path):
                return {"has_tokens": False, "has_active_tokens": False, "has_expired_tokens": False,
                        "active_tokens": [], "expired_tokens": [], "total_tokens": 0, "last_token_date": None}

            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, access_token, refresh_token, token_type, expires_at, expires_in, scope, site_id, member_id,
                           created_at, is_active, token_key_version, token_key_reference
                    FROM wix_oauth_tokens
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                ''', (user_id,))

                all_tokens, active_tokens, expired_tokens = [], [], []
                for row in cursor.fetchall():
                    token_data = {
                        "id": row[0], "access_token": row[1], "refresh_token": row[2], "token_type": row[3],
                        "expires_at": row[4], "expires_in": row[5], "scope": row[6], "site_id": row[7],
                        "member_id": row[8], "created_at": row[9], "is_active": bool(row[10]),
                        "token_key_version": row[11], "token_key_reference": row[12]
                    }
                    all_tokens.append(token_data)

                    is_active_flag = bool(row[10])
                    not_expired = False
                    try:
                        expires_at_val = row[4]
                        if expires_at_val:
                            try:
                                dt = datetime.fromisoformat(expires_at_val) if isinstance(expires_at_val, str) else expires_at_val
                                not_expired = dt > datetime.now()
                            except Exception:
                                cursor.execute("SELECT datetime('now') < ?", (expires_at_val,))
                                not_expired = cursor.fetchone()[0] == 1
                        else:
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
            return {"has_tokens": False, "has_active_tokens": False, "has_expired_tokens": False,
                    "active_tokens": [], "expired_tokens": [], "total_tokens": 0, "last_token_date": None, "error": str(e)}

    def update_tokens(self, user_id: str, access_token: str, refresh_token: Optional[str] = None,
                      expires_in: Optional[int] = None) -> bool:
        try:
            self._init_db(user_id)
            db_path = self._get_db_path(user_id)
            expires_at = datetime.now() + timedelta(seconds=expires_in) if expires_in else None
            encrypted_access_token = self.token_crypto.encrypt_token(access_token)
            encrypted_refresh_token = self.token_crypto.encrypt_token(refresh_token) if refresh_token else None

            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                if refresh_token:
                    cursor.execute('''
                        UPDATE wix_oauth_tokens
                        SET access_token = ?, refresh_token = ?, expires_at = ?, expires_in = ?,
                            is_active = TRUE, updated_at = datetime('now'), token_key_version = ?, token_key_reference = ?
                        WHERE user_id = ? AND (refresh_token = ? OR refresh_token = ?)
                    ''', (encrypted_access_token, encrypted_refresh_token, expires_at, expires_in,
                          self.token_crypto.key_version, self.token_crypto.key_reference,
                          user_id, encrypted_refresh_token, refresh_token))
                else:
                    cursor.execute('''
                        UPDATE wix_oauth_tokens
                        SET access_token = ?, expires_at = ?, expires_in = ?,
                            is_active = TRUE, updated_at = datetime('now'), token_key_version = ?, token_key_reference = ?
                        WHERE user_id = ? AND id = (SELECT id FROM wix_oauth_tokens WHERE user_id = ? ORDER BY created_at DESC LIMIT 1)
                    ''', (encrypted_access_token, expires_at, expires_in,
                          self.token_crypto.key_version, self.token_crypto.key_reference, user_id, user_id))
                conn.commit()
                logger.info(f"Wix OAuth: Encrypted tokens updated for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating Wix tokens for user {user_id}: {e}")
            return False

    def rotate_token_encryption(self, user_id: str, batch_size: int = 100) -> Dict[str, int]:
        """Re-encrypt existing token rows in batches for key rotation."""
        self._init_db(user_id)
        db_path = self._get_db_path(user_id)
        rotated, skipped, last_id = 0, 0, 0
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            while True:
                cursor.execute('''
                    SELECT id, access_token, refresh_token
                    FROM wix_oauth_tokens
                    WHERE user_id = ? AND id > ?
                    ORDER BY id ASC
                    LIMIT ?
                ''', (user_id, last_id, batch_size))
                rows = cursor.fetchall()
                if not rows:
                    break

                for row_id, enc_access, enc_refresh in rows:
                    last_id = row_id
                    try:
                        plain_access = self.token_crypto.decrypt_token(enc_access)
                        plain_refresh = self.token_crypto.decrypt_token(enc_refresh) if enc_refresh else None
                    except Exception:
                        skipped += 1
                        continue

                    new_access, new_refresh = self.token_crypto.encrypt_pair(plain_access, plain_refresh)
                    cursor.execute('''
                        UPDATE wix_oauth_tokens
                        SET access_token = ?, refresh_token = ?, token_key_version = ?, token_key_reference = ?, updated_at = datetime('now')
                        WHERE id = ?
                    ''', (new_access, new_refresh, self.token_crypto.key_version, self.token_crypto.key_reference, row_id))
                    rotated += 1
            conn.commit()

        logger.info(f"Wix OAuth: Encryption rotation complete for user {user_id}; rotated={rotated}, skipped={skipped}")
        return {"rotated": rotated, "skipped": skipped}

    def revoke_token(self, user_id: str, token_id: int) -> bool:
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
