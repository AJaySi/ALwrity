"""
WordPress OAuth2 Service
Handles WordPress.com OAuth2 authentication flow for simplified user connection.
"""

import os
import secrets
import sqlite3
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger
import json
import base64

class WordPressOAuthService:
    """Manages WordPress.com OAuth2 authentication flow."""
    
    def __init__(self, db_path: str = "alwrity.db"):
        self.db_path = db_path
        # WordPress.com OAuth2 credentials
        self.client_id = os.getenv('WORDPRESS_CLIENT_ID', '')
        self.client_secret = os.getenv('WORDPRESS_CLIENT_SECRET', '')
        self.redirect_uri = os.getenv('WORDPRESS_REDIRECT_URI', 'https://alwrity-ai.vercel.app/wp/callback')
        self.base_url = "https://public-api.wordpress.com"

        # Validate configuration
        if not self.client_id or not self.client_secret or self.client_id == 'your_wordpress_com_client_id_here':
            logger.error("WordPress OAuth client credentials not configured. Please set WORDPRESS_CLIENT_ID and WORDPRESS_CLIENT_SECRET environment variables with valid WordPress.com application credentials.")
            logger.error("To get credentials: 1. Go to https://developer.wordpress.com/apps/ 2. Create a new application 3. Set redirect URI to: https://your-domain.com/wp/callback")

        self._init_db()
    
    def _init_db(self):
        """Initialize database tables for OAuth tokens."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS wordpress_oauth_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS wordpress_oauth_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    state TEXT NOT NULL UNIQUE,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP DEFAULT (datetime('now', '+10 minutes'))
                )
            ''')
            conn.commit()
        logger.info("WordPress OAuth database initialized.")
    
    def generate_authorization_url(self, user_id: str, scope: str = "global") -> Dict[str, Any]:
        """Generate WordPress OAuth2 authorization URL."""
        try:
            # Check if credentials are properly configured
            if not self.client_id or not self.client_secret or self.client_id == 'your_wordpress_com_client_id_here':
                logger.error("WordPress OAuth client credentials not configured")
                return None

            # Generate secure state parameter
            state = secrets.token_urlsafe(32)

            # Store state in database for validation
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO wordpress_oauth_states (state, user_id)
                    VALUES (?, ?)
                ''', (state, user_id))
                conn.commit()

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
            
            # Validate state parameter
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id FROM wordpress_oauth_states 
                    WHERE state = ? AND expires_at > datetime('now')
                ''', (state,))
                result = cursor.fetchone()
                
                if not result:
                    logger.error(f"Invalid or expired state parameter: {state}")
                    return None
                
                user_id = result[0]
                logger.info(f"WordPress OAuth: State validated for user {user_id}")
                
                # Clean up used state
                cursor.execute('DELETE FROM wordpress_oauth_states WHERE state = ?', (state,))
                conn.commit()
            
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
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO wordpress_oauth_tokens 
                    (user_id, access_token, token_type, expires_at, scope, blog_id, blog_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, access_token, 'bearer', expires_at, scope, blog_id, blog_url))
                conn.commit()
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
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, access_token, token_type, expires_at, scope, blog_id, blog_url, created_at
                    FROM wordpress_oauth_tokens
                    WHERE user_id = ? AND is_active = TRUE AND expires_at > datetime('now')
                    ORDER BY created_at DESC
                ''', (user_id,))
                
                tokens = []
                for row in cursor.fetchall():
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
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE wordpress_oauth_tokens 
                    SET is_active = FALSE, updated_at = datetime('now')
                    WHERE user_id = ? AND id = ?
                ''', (user_id, token_id))
                conn.commit()
                
                if cursor.rowcount > 0:
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
