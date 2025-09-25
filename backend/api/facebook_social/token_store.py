import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

class FacebookTokenStore:
    """
    Secure token storage for Facebook OAuth tokens.
    Uses SQLite with encryption for local development.
    """
    
    def __init__(self):
        self.db_path = os.getenv("FACEBOOK_TOKENS_DB", "facebook_tokens.db")
        self.encryption_key = self._get_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        self._init_database()
    
    def _get_encryption_key(self) -> bytes:
        """Get or generate encryption key for token storage."""
        key_str = os.getenv("TOKEN_STORE_SECRET")
        if key_str:
            # Use provided key (should be base64 encoded)
            return key_str.encode()
        else:
            # Generate a new key (for development only)
            logger.warning("TOKEN_STORE_SECRET not set, generating new key for development")
            return Fernet.generate_key()
    
    def _init_database(self):
        """Initialize the tokens database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS facebook_tokens (
                        clerk_user_id TEXT PRIMARY KEY,
                        user_access_token TEXT NOT NULL,
                        token_expires_at TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize token database: {str(e)}")
            raise
    
    def _encrypt_token(self, token: str) -> str:
        """Encrypt a token for storage."""
        return self.cipher.encrypt(token.encode()).decode()
    
    def _decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt a token from storage."""
        return self.cipher.decrypt(encrypted_token.encode()).decode()
    
    def store_user_token(self, clerk_user_id: str, user_access_token: str, expires_at: Optional[datetime] = None) -> bool:
        """Store a user's Facebook access token."""
        try:
            encrypted_token = self._encrypt_token(user_access_token)
            now = datetime.utcnow().isoformat()
            expires_str = expires_at.isoformat() if expires_at else None
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO facebook_tokens 
                    (clerk_user_id, user_access_token, token_expires_at, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (clerk_user_id, encrypted_token, expires_str, now, now))
                conn.commit()
            
            logger.info(f"Stored Facebook token for user {clerk_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store token for user {clerk_user_id}: {str(e)}")
            return False
    
    def get_user_token(self, clerk_user_id: str) -> Optional[str]:
        """Retrieve a user's Facebook access token."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT user_access_token, token_expires_at FROM facebook_tokens 
                    WHERE clerk_user_id = ?
                """, (clerk_user_id,))
                
                row = cursor.fetchone()
                if row:
                    encrypted_token, expires_str = row
                    
                    # Check if token is expired
                    if expires_str:
                        expires_at = datetime.fromisoformat(expires_str)
                        if expires_at < datetime.utcnow():
                            logger.info(f"Token expired for user {clerk_user_id}")
                            return None
                    
                    return self._decrypt_token(encrypted_token)
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve token for user {clerk_user_id}: {str(e)}")
            return None
    
    def delete_user_token(self, clerk_user_id: str) -> bool:
        """Delete a user's Facebook access token."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM facebook_tokens WHERE clerk_user_id = ?", (clerk_user_id,))
                conn.commit()
            
            logger.info(f"Deleted Facebook token for user {clerk_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete token for user {clerk_user_id}: {str(e)}")
            return False
    
    def is_token_valid(self, clerk_user_id: str) -> bool:
        """Check if user has a valid (non-expired) token."""
        token = self.get_user_token(clerk_user_id)
        return token is not None

# Global token store instance
token_store = FacebookTokenStore()
