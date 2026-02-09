"""
Wix OAuth2 Service
Handles Wix OAuth2 authentication flow and token storage.
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import or_

from services.database import get_platform_db_session
from models.oauth_token_models import WixOAuthToken


class WixOAuthService:
    """Manages Wix OAuth2 authentication flow and token storage."""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session
    
    def _get_db_session(self) -> Optional[Session]:
        return self.db_session or get_platform_db_session()

    def _cleanup_session(self, db: Optional[Session]) -> None:
        if db is not None and self.db_session is None:
            db.close()
    
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
        db = self._get_db_session()
        if not db:
            logger.error("Error storing Wix tokens: database session unavailable")
            return False
        try:
            expires_at = None
            if expires_in:
                expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            db.add(WixOAuthToken(
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                token_type=token_type,
                expires_at=expires_at,
                expires_in=expires_in,
                scope=scope,
                site_id=site_id,
                member_id=member_id,
            ))
            db.commit()
            logger.info(f"Wix OAuth: Token inserted into database for user {user_id}")
            
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error storing Wix tokens for user {user_id}: {e}")
            return False
        finally:
            self._cleanup_session(db)
    
    def get_user_tokens(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active Wix tokens for a user."""
        db = self._get_db_session()
        if not db:
            logger.error("Error getting Wix tokens: database session unavailable")
            return []
        try:
            now = datetime.utcnow()
            records = (
                db.query(WixOAuthToken)
                .filter(
                    WixOAuthToken.user_id == user_id,
                    WixOAuthToken.is_active.is_(True),
                    or_(WixOAuthToken.expires_at.is_(None), WixOAuthToken.expires_at > now),
                )
                .order_by(WixOAuthToken.created_at.desc())
                .all()
            )
            
            tokens = []
            for record in records:
                tokens.append({
                    "id": record.id,
                    "access_token": record.access_token,
                    "refresh_token": record.refresh_token,
                    "token_type": record.token_type,
                    "expires_at": record.expires_at,
                    "expires_in": record.expires_in,
                    "scope": record.scope,
                    "site_id": record.site_id,
                    "member_id": record.member_id,
                    "created_at": record.created_at,
                })
            
            return tokens
                
        except Exception as e:
            logger.error(f"Error getting Wix tokens for user {user_id}: {e}")
            return []
        finally:
            self._cleanup_session(db)
    
    def get_user_token_status(self, user_id: str) -> Dict[str, Any]:
        """Get detailed token status for a user including expired tokens."""
        db = self._get_db_session()
        if not db:
            logger.error("Error getting Wix token status: database session unavailable")
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
                db.query(WixOAuthToken)
                .filter(WixOAuthToken.user_id == user_id)
                .order_by(WixOAuthToken.created_at.desc())
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
                    "expires_in": record.expires_in,
                    "scope": record.scope,
                    "site_id": record.site_id,
                    "member_id": record.member_id,
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
        finally:
            self._cleanup_session(db)
    
    def update_tokens(
        self,
        user_id: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_in: Optional[int] = None
    ) -> bool:
        """Update tokens for a user (e.g., after refresh)."""
        db = self._get_db_session()
        if not db:
            logger.error("Error updating Wix tokens: database session unavailable")
            return False
        try:
            expires_at = None
            if expires_in:
                expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            if refresh_token:
                db.query(WixOAuthToken).filter(
                    WixOAuthToken.user_id == user_id,
                    WixOAuthToken.refresh_token == refresh_token,
                ).update(
                    {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "expires_at": expires_at,
                        "expires_in": expires_in,
                        "is_active": True,
                        "updated_at": datetime.utcnow(),
                    }
                )
            else:
                latest_token = (
                    db.query(WixOAuthToken)
                    .filter(WixOAuthToken.user_id == user_id)
                    .order_by(WixOAuthToken.created_at.desc())
                    .first()
                )
                if latest_token:
                    latest_token.access_token = access_token
                    latest_token.expires_at = expires_at
                    latest_token.expires_in = expires_in
                    latest_token.is_active = True
                    latest_token.updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"Wix OAuth: Tokens updated for user {user_id}")
            
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating Wix tokens for user {user_id}: {e}")
            return False
        finally:
            self._cleanup_session(db)
    
    def revoke_token(self, user_id: str, token_id: int) -> bool:
        """Revoke a Wix OAuth token."""
        db = self._get_db_session()
        if not db:
            logger.error("Error revoking Wix token: database session unavailable")
            return False
        try:
            updated = db.query(WixOAuthToken).filter(
                WixOAuthToken.user_id == user_id,
                WixOAuthToken.id == token_id,
            ).update(
                {"is_active": False, "updated_at": datetime.utcnow()}
            )
            db.commit()
            
            if updated > 0:
                logger.info(f"Wix token {token_id} revoked for user {user_id}")
                return True
            return False
                
        except Exception as e:
            db.rollback()
            logger.error(f"Error revoking Wix token: {e}")
            return False
        finally:
            self._cleanup_session(db)
