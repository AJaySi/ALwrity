"""
WordPress OAuth2 Service
Handles WordPress.com OAuth2 authentication flow for simplified user connection.
"""

import os
import secrets
from contextlib import contextmanager
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger
import json
from sqlalchemy import text
from services.database import get_user_data_db_session

from services.database import get_user_db_path

class WordPressOAuthService:
    """Manages WordPress.com OAuth2 authentication flow."""
    
    def __init__(self, db_path: str = None):
        # db_path is deprecated in favor of dynamic user_id based paths
        self.db_path = db_path
        # WordPress.com OAuth2 credentials
        self.client_id = os.getenv('WORDPRESS_CLIENT_ID', '')
        self.client_secret = os.getenv('WORDPRESS_CLIENT_SECRET', '')
        
        # Determine redirect URI dynamically
        default_redirect = 'https://alwrity-ai.vercel.app/wp/callback'
        frontend_url = os.getenv('FRONTEND_URL')
        
        if frontend_url:
            self.redirect_uri = f"{frontend_url.rstrip('/')}/wp/callback"
        else:
            self.redirect_uri = os.getenv('WORDPRESS_REDIRECT_URI', default_redirect)
            
        self.base_url = "https://public-api.wordpress.com"

        # Validate configuration
        if not self.client_id or not self.client_secret or self.client_id == 'your_wordpress_com_client_id_here':
            logger.error("WordPress OAuth client credentials not configured. Please set WORDPRESS_CLIENT_ID and WORDPRESS_CLIENT_SECRET environment variables with valid WordPress.com application credentials.")
            logger.error("To get credentials: 1. Go to https://developer.wordpress.com/apps/ 2. Create a new application 3. Set redirect URI to: https://your-domain.com/wp/callback")

    def _get_db_path(self, user_id: str) -> str:
        return get_user_db_path(user_id)
    
    def _init_db(self, user_id: str):
        """Initialize database tables for OAuth tokens."""
<<<<<<< HEAD
        db_path = self._get_db_path(user_id)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
=======
        with self._db_session() as db:
            db.execute(text('''
>>>>>>> pr-354
                CREATE TABLE IF NOT EXISTS wordpress_oauth_tokens (
                    id BIGSERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    access_token TEXT NOT NULL,
                    refresh_token TEXT,
                    token_type TEXT DEFAULT 'bearer',
                    expires_at TIMESTAMP,
                    scope TEXT,
                    blog_id TEXT,
                    blog_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            '''))
            db.execute(text('''
                CREATE TABLE IF NOT EXISTS wordpress_oauth_states (
                    id BIGSERIAL PRIMARY KEY,
                    state TEXT NOT NULL UNIQUE,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '10 minutes')
                )
<<<<<<< HEAD
            ''')
            conn.commit()
=======
            '''))
        logger.info("WordPress OAuth database initialized.")
>>>>>>> pr-354
    
    def generate_authorization_url(self, user_id: str, scope: str = "global") -> Dict[str, Any]:
        """Generate WordPress OAuth2 authorization URL."""
        try:
            # Check if credentials are properly configured
            if not self.client_id or not self.client_secret or self.client_id == 'your_wordpress_com_client_id_here':
                logger.error("WordPress OAuth client credentials not configured")
                return None

            # Generate secure state parameter with user_id for routing
            random_token = secrets.token_urlsafe(32)
            state = f"{user_id}:{random_token}"

            # Store state in database for validation
<<<<<<< HEAD
            self._init_db(user_id)
            db_path = self._get_db_path(user_id)
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO wordpress_oauth_states (state, user_id)
                    VALUES (?, ?)
                ''', (state, user_id))
                conn.commit()
=======
            with self._db_session() as db:
                db.execute(
                    text('''
                        INSERT INTO wordpress_oauth_states (state, user_id)
                        VALUES (:state, :user_id)
                    '''),
                    {"state": state, "user_id": user_id}
                )
>>>>>>> pr-354

            # Build authorization URL
            # For WordPress.com, use "global" scope for full access to enable posting
            params = [
                f"client_id={self.client_id}",
                f"redirect_uri={self.redirect_uri}",
                "response_type=code",
                f"state={state}",
                f"scope={scope}"  # WordPress.com requires "global" scope for full access
            ]

            auth_url = f"{self.base_url}/oauth2/authorize?{'&'.join(params)}"

            logger.info(f"Generated WordPress OAuth URL for user {user_id}")
            logger.info(f"WordPress OAuth redirect URI: {self.redirect_uri}")
            return {
                "auth_url": auth_url,
                "state": state
            }

        except Exception as e:
            logger.error(f"Error generating WordPress OAuth URL: {e}")
            return None
    
    def handle_oauth_callback(self, code: str, state: str) -> Optional[Dict[str, Any]]:
        """Handle OAuth callback and exchange code for access token."""
        try:
            logger.info(f"WordPress OAuth callback started - code: {code[:20]}..., state: {state[:20]}...")
            
            # Extract user_id from state
            if ':' not in state:
                logger.error(f"Invalid WordPress state format: {state}")
                return None
                
            user_id = state.split(':')[0]
            db_path = self._get_db_path(user_id)
            
            if not os.path.exists(db_path):
                logger.error(f"User database not found for user {user_id}")
                return None

            # Validate state parameter
<<<<<<< HEAD
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id FROM wordpress_oauth_states 
                    WHERE state = ? AND expires_at > datetime('now')
                ''', (state,))
                result = cursor.fetchone()
                
                if not result:
                    logger.error(f"Invalid or expired state parameter: {state}")
                    return None
                
=======
            with self._db_session() as db:
                result = db.execute(
                    text('''
                        SELECT user_id, expires_at FROM wordpress_oauth_states
                        WHERE state = :state
                    '''),
                    {"state": state}
                ).fetchone()

                if not result:
                    logger.error(f"Invalid or expired state parameter: {state}")
                    return None

                user_id, expires_at = result
                if expires_at and expires_at <= datetime.utcnow():
                    logger.error(f"Expired state parameter: {state}")
                    db.execute(
                        text('DELETE FROM wordpress_oauth_states WHERE state = :state'),
                        {"state": state}
                    )
                    return None

                logger.info(f"WordPress OAuth: State validated for user {user_id}")

>>>>>>> pr-354
                # Clean up used state
                db.execute(
                    text('DELETE FROM wordpress_oauth_states WHERE state = :state'),
                    {"state": state}
                )
            
            # Exchange authorization code for access token
            token_data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': self.redirect_uri,
                'code': code,
                'grant_type': 'authorization_code'
            }
            
            logger.info(f"WordPress OAuth: Exchanging code for token...")
            response = requests.post(
                f"{self.base_url}/oauth2/token",
                data=token_data,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
                return None
            
            token_info = response.json()
            logger.info(f"WordPress OAuth: Token received - blog_id: {token_info.get('blog_id')}, blog_url: {token_info.get('blog_url')}")
            
            # Store token information
            access_token = token_info.get('access_token')
            blog_id = token_info.get('blog_id')
            blog_url = token_info.get('blog_url')
            scope = token_info.get('scope', '')
            
            # Calculate expiration (WordPress tokens typically expire in 2 weeks)
            expires_at = datetime.now() + timedelta(days=14)
            
<<<<<<< HEAD
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO wordpress_oauth_tokens 
                    (user_id, access_token, token_type, expires_at, scope, blog_id, blog_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, access_token, 'bearer', expires_at, scope, blog_id, blog_url))
                conn.commit()
=======
            with self._db_session() as db:
                db.execute(
                    text('''
                        INSERT INTO wordpress_oauth_tokens
                        (user_id, access_token, token_type, expires_at, scope, blog_id, blog_url)
                        VALUES (:user_id, :access_token, :token_type, :expires_at, :scope, :blog_id, :blog_url)
                    '''),
                    {
                        "user_id": user_id,
                        "access_token": access_token,
                        "token_type": "bearer",
                        "expires_at": expires_at,
                        "scope": scope,
                        "blog_id": blog_id,
                        "blog_url": blog_url
                    }
                )
>>>>>>> pr-354
                logger.info(f"WordPress OAuth: Token inserted into database for user {user_id}")
            
            logger.info(f"WordPress OAuth token stored successfully for user {user_id}, blog: {blog_url}")
            return {
                "success": True,
                "access_token": access_token,
                "blog_id": blog_id,
                "blog_url": blog_url,
                "scope": scope,
                "expires_at": expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error handling WordPress OAuth callback: {e}")
            return None
    
    def get_user_tokens(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active WordPress tokens for a user."""
        try:
<<<<<<< HEAD
            # Ensure database tables exist to prevent 'no such table' errors
            self._init_db(user_id)
            
            db_path = self._get_db_path(user_id)
            if not os.path.exists(db_path):
                return []
                
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, access_token, token_type, expires_at, scope, blog_id, blog_url, created_at
                    FROM wordpress_oauth_tokens
                    WHERE user_id = ? AND is_active = TRUE AND expires_at > datetime('now')
                    ORDER BY created_at DESC
                ''', (user_id,))
                
=======
            with self._db_session() as db:
                rows = db.execute(
                    text('''
                        SELECT id, access_token, token_type, expires_at, scope, blog_id, blog_url, created_at
                        FROM wordpress_oauth_tokens
                        WHERE user_id = :user_id AND is_active = TRUE AND expires_at > CURRENT_TIMESTAMP
                        ORDER BY created_at DESC
                    '''),
                    {"user_id": user_id}
                ).fetchall()

>>>>>>> pr-354
                tokens = []
                for row in rows:
                    tokens.append({
                        "id": row[0],
                        "access_token": row[1],
                        "token_type": row[2],
                        "expires_at": row[3],
                        "scope": row[4],
                        "blog_id": row[5],
                        "blog_url": row[6],
                        "created_at": row[7]
                    })
                
                return tokens
                
        except Exception as e:
            logger.error(f"Error getting WordPress tokens for user {user_id}: {e}")
            return []
    
    def get_user_token_status(self, user_id: str) -> Dict[str, Any]:
        """Get detailed token status for a user including expired tokens."""
        try:
<<<<<<< HEAD
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
                    SELECT id, access_token, refresh_token, token_type, expires_at, scope, blog_id, blog_url, created_at, is_active
                    FROM wordpress_oauth_tokens
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                ''', (user_id,))
                
=======
            with self._db_session() as db:
                rows = db.execute(
                    text('''
                        SELECT id, access_token, refresh_token, token_type, expires_at, scope, blog_id, blog_url, created_at, is_active
                        FROM wordpress_oauth_tokens
                        WHERE user_id = :user_id
                        ORDER BY created_at DESC
                    '''),
                    {"user_id": user_id}
                ).fetchall()

>>>>>>> pr-354
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
                        "scope": row[5],
                        "blog_id": row[6],
                        "blog_url": row[7],
                        "created_at": row[8],
                        "is_active": bool(row[9])
                    }
                    all_tokens.append(token_data)
                    
                    # Determine expiry using robust parsing and is_active flag
                    is_active_flag = bool(row[9])
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
            logger.error(f"Error getting WordPress token status for user {user_id}: {e}")
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
    
    def test_token(self, access_token: str) -> bool:
        """Test if a WordPress access token is valid."""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(
                f"{self.base_url}/rest/v1/me/",
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error testing WordPress token: {e}")
            return False
    
    def revoke_token(self, user_id: str, token_id: int) -> bool:
        """Revoke a WordPress OAuth token."""
        try:
<<<<<<< HEAD
            db_path = self._get_db_path(user_id)
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE wordpress_oauth_tokens 
                    SET is_active = FALSE, updated_at = datetime('now')
                    WHERE user_id = ? AND id = ?
                ''', (user_id, token_id))
                conn.commit()
                
                if cursor.rowcount > 0:
=======
            with self._db_session() as db:
                result = db.execute(
                    text('''
                        UPDATE wordpress_oauth_tokens
                        SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = :user_id AND id = :token_id
                    '''),
                    {"user_id": user_id, "token_id": token_id}
                )

                if result.rowcount > 0:
>>>>>>> pr-354
                    logger.info(f"WordPress token {token_id} revoked for user {user_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error revoking WordPress token: {e}")
            return False
    
    def get_connection_status(self, user_id: str) -> Dict[str, Any]:
        """Get WordPress connection status for a user."""
        try:
            tokens = self.get_user_tokens(user_id)
            
            if not tokens:
                return {
                    "connected": False,
                    "sites": [],
                    "total_sites": 0
                }
            
            # Test each token and get site information
            active_sites = []
            for token in tokens:
                if self.test_token(token["access_token"]):
                    active_sites.append({
                        "id": token["id"],
                        "blog_id": token["blog_id"],
                        "blog_url": token["blog_url"],
                        "scope": token["scope"],
                        "created_at": token["created_at"]
                    })
            
            return {
                "connected": len(active_sites) > 0,
                "sites": active_sites,
                "total_sites": len(active_sites)
            }
            
        except Exception as e:
            logger.error(f"Error getting WordPress connection status: {e}")
            return {
                "connected": False,
                "sites": [],
                "total_sites": 0
            }
