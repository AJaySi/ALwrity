"""
WordPress OAuth2 Service
Handles WordPress.com OAuth2 authentication flow for simplified user connection.
"""

import os
import secrets
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger
<<<<<<< HEAD
from sqlalchemy.orm import Session

from services.database import get_platform_db_session
from models.oauth_token_models import WordPressOAuthToken, WordPressOauthState
=======
import json
import base64
from services.oauth_redirects import get_redirect_uri
>>>>>>> origin/codex/add-oauth-endpoints-and-validations

class WordPressOAuthService:
    """Manages WordPress.com OAuth2 authentication flow."""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session
        # WordPress.com OAuth2 credentials
        self.client_id = os.getenv('WORDPRESS_CLIENT_ID', '')
        self.client_secret = os.getenv('WORDPRESS_CLIENT_SECRET', '')
        # Enforce redirect URI from env so the callback origin matches deployment.
        try:
            self.redirect_uri = get_redirect_uri("WordPress", "WORDPRESS_REDIRECT_URI")
        except ValueError as exc:
            logger.error(f"WordPress OAuth redirect URI configuration error: {exc}")
            self.redirect_uri = None
        self.base_url = "https://public-api.wordpress.com"

        # Validate configuration
        if not self.client_id or not self.client_secret or self.client_id == 'your_wordpress_com_client_id_here':
            logger.error("WordPress OAuth client credentials not configured. Please set WORDPRESS_CLIENT_ID and WORDPRESS_CLIENT_SECRET environment variables with valid WordPress.com application credentials.")
            logger.error("To get credentials: 1. Go to https://developer.wordpress.com/apps/ 2. Create a new application 3. Set redirect URI to: https://your-domain.com/wp/callback")


    def _get_db_session(self) -> Optional[Session]:
        return self.db_session or get_platform_db_session()

    def _cleanup_session(self, db: Optional[Session]) -> None:
        if db is not None and self.db_session is None:
            db.close()
    
    def generate_authorization_url(self, user_id: str, scope: str = "global") -> Dict[str, Any]:
        """Generate WordPress OAuth2 authorization URL."""
        try:
            # Check if credentials are properly configured
            if (
                not self.client_id
                or not self.client_secret
                or self.client_id == 'your_wordpress_com_client_id_here'
                or not self.redirect_uri
            ):
                logger.error("WordPress OAuth client credentials not configured")
                return None

            # Generate secure state parameter
            state = secrets.token_urlsafe(32)

            # Store state in database for validation
            db = self._get_db_session()
            if not db:
                raise ValueError("Database session unavailable for WordPress OAuth state storage")
            try:
                db.add(WordPressOauthState(
                    state=state,
                    user_id=user_id,
                    expires_at=datetime.utcnow() + timedelta(minutes=10),
                ))
                db.commit()
            except Exception:
                db.rollback()
                raise
            finally:
                self._cleanup_session(db)

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
            db = self._get_db_session()
            if not db:
                logger.error("WordPress OAuth: Database session unavailable")
                return None
            try:
                state_record = (
                    db.query(WordPressOauthState)
                    .filter(WordPressOauthState.state == state)
                    .first()
                )
                
                if not state_record or (state_record.expires_at and state_record.expires_at <= datetime.utcnow()):
                    logger.error(f"Invalid or expired state parameter: {state}")
                    if state_record:
                        db.delete(state_record)
                        db.commit()
                    return None
                
                user_id = state_record.user_id
                logger.info(f"WordPress OAuth: State validated for user {user_id}")
                
                # Clean up used state
                db.delete(state_record)
                db.commit()
            except Exception:
                db.rollback()
                raise
            finally:
                self._cleanup_session(db)
            
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
            
            db = self._get_db_session()
            if not db:
                logger.error("WordPress OAuth: Database session unavailable for token storage")
                return None
            try:
                db.add(WordPressOAuthToken(
                    user_id=user_id,
                    access_token=access_token,
                    token_type='bearer',
                    expires_at=expires_at,
                    scope=scope,
                    blog_id=blog_id,
                    blog_url=blog_url,
                ))
                db.commit()
                logger.info(f"WordPress OAuth: Token inserted into database for user {user_id}")
            except Exception:
                db.rollback()
                raise
            finally:
                self._cleanup_session(db)
            
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
        db = self._get_db_session()
        if not db:
            logger.error("Error getting WordPress tokens: database session unavailable")
            return []
        try:
            now = datetime.utcnow()
            records = (
                db.query(WordPressOAuthToken)
                .filter(
                    WordPressOAuthToken.user_id == user_id,
                    WordPressOAuthToken.is_active.is_(True),
                    WordPressOAuthToken.expires_at > now,
                )
                .order_by(WordPressOAuthToken.created_at.desc())
                .all()
            )
            
            tokens = []
            for record in records:
                tokens.append({
                    "id": record.id,
                    "access_token": record.access_token,
                    "token_type": record.token_type,
                    "expires_at": record.expires_at,
                    "scope": record.scope,
                    "blog_id": record.blog_id,
                    "blog_url": record.blog_url,
                    "created_at": record.created_at,
                })
            
            return tokens
                
        except Exception as e:
            logger.error(f"Error getting WordPress tokens for user {user_id}: {e}")
            return []
        finally:
            self._cleanup_session(db)
    
    def get_user_token_status(self, user_id: str) -> Dict[str, Any]:
        """Get detailed token status for a user including expired tokens."""
        db = self._get_db_session()
        if not db:
            logger.error("Error getting WordPress token status: database session unavailable")
            return {
                "has_tokens": False,
                "has_active_tokens": False,
                "has_expired_tokens": False,
                "active_tokens": [],
                "expired_tokens": [],
                "total_tokens": 0,
                "last_token_date": None,
                "error": "Database session unavailable",
            }
        try:
            records = (
                db.query(WordPressOAuthToken)
                .filter(WordPressOAuthToken.user_id == user_id)
                .order_by(WordPressOAuthToken.created_at.desc())
                .all()
            )
            
            all_tokens = []
            active_tokens = []
            expired_tokens = []
            now = datetime.utcnow()
            
            for record in records:
                token_data = {
                    "id": record.id,
                    "access_token": record.access_token,
                    "refresh_token": record.refresh_token,
                    "token_type": record.token_type,
                    "expires_at": record.expires_at,
                    "scope": record.scope,
                    "blog_id": record.blog_id,
                    "blog_url": record.blog_url,
                    "created_at": record.created_at,
                    "is_active": bool(record.is_active),
                }
                all_tokens.append(token_data)
                
                is_active_flag = bool(record.is_active)
                not_expired = True
                if record.expires_at:
                    not_expired = record.expires_at > now
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
        finally:
            self._cleanup_session(db)
    
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
        db = self._get_db_session()
        if not db:
            logger.error("Error revoking WordPress token: database session unavailable")
            return False
        try:
            updated = db.query(WordPressOAuthToken).filter(
                WordPressOAuthToken.user_id == user_id,
                WordPressOAuthToken.id == token_id,
            ).update(
                {"is_active": False, "updated_at": datetime.utcnow()}
            )
            db.commit()
            
            if updated > 0:
                logger.info(f"WordPress token {token_id} revoked for user {user_id}")
                return True
            return False
                
        except Exception as e:
            db.rollback()
            logger.error(f"Error revoking WordPress token: {e}")
            return False
        finally:
            self._cleanup_session(db)
    
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
