"""
OAuth Token Monitoring Service
Service for creating and managing OAuth token monitoring tasks.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from utils.logger_utils import get_service_logger
import os

# Use service logger for consistent logging (WARNING level visible in production)
logger = get_service_logger("oauth_token_monitoring")

from models.oauth_token_monitoring_models import OAuthTokenMonitoringTask
from services.gsc_service import GSCService
from services.integrations.bing_oauth import BingOAuthService
from services.integrations.wordpress_oauth import WordPressOAuthService

# Note: Wix tokens are stored in frontend sessionStorage, not backend database
# So we cannot check for Wix connections from the backend yet


def get_connected_platforms(user_id: str) -> List[str]:
    """
    Detect which platforms are connected for a user by checking token storage.
    
    Checks:
    - GSC: gsc_credentials table
    - Bing: bing_oauth_tokens table
    - WordPress: wordpress_oauth_tokens table
    - Wix: Not checked (tokens in frontend sessionStorage)
    
    Args:
        user_id: User ID (Clerk string)
        
    Returns:
        List of connected platform identifiers: ['gsc', 'bing', 'wordpress', 'wix']
    """
    connected = []
    
    logger.warning(f"[OAuth Monitoring] Checking connected platforms for user: {user_id}")
    
    try:
        # Check GSC - use absolute database path
        db_path = os.path.abspath("alwrity.db")
        logger.warning(f"[OAuth Monitoring] Checking GSC with db_path: {db_path}")
        gsc_service = GSCService(db_path=db_path)
        gsc_credentials = gsc_service.load_user_credentials(user_id)
        if gsc_credentials:
            connected.append('gsc')
            logger.warning(f"[OAuth Monitoring] ✅ GSC connected for user {user_id}")
        else:
            logger.warning(f"[OAuth Monitoring] ❌ GSC not connected for user {user_id} (no credentials found)")
    except Exception as e:
        logger.warning(f"[OAuth Monitoring] ⚠️ GSC check failed for user {user_id}: {e}", exc_info=True)
    
    try:
        # Check Bing - use absolute database path
        db_path = os.path.abspath("alwrity.db")
        logger.warning(f"[OAuth Monitoring] Checking Bing with db_path: {db_path}")
        bing_service = BingOAuthService(db_path=db_path)
        token_status = bing_service.get_user_token_status(user_id)
        has_tokens = token_status.get('has_active_tokens', False)
        logger.warning(f"[OAuth Monitoring] Bing token_status keys: {list(token_status.keys())}, has_active_tokens: {has_tokens}")
        if has_tokens:
            connected.append('bing')
            logger.warning(f"[OAuth Monitoring] ✅ Bing connected for user {user_id}")
        else:
            logger.warning(f"[OAuth Monitoring] ❌ Bing not connected for user {user_id} (no active tokens)")
    except Exception as e:
        logger.warning(f"[OAuth Monitoring] ⚠️ Bing check failed for user {user_id}: {e}", exc_info=True)
    
    try:
        # Check WordPress - use absolute database path
        db_path = os.path.abspath("alwrity.db")
        logger.warning(f"[OAuth Monitoring] Checking WordPress with db_path: {db_path}")
        wordpress_service = WordPressOAuthService(db_path=db_path)
        tokens = wordpress_service.get_user_tokens(user_id)
        logger.warning(f"[OAuth Monitoring] WordPress tokens found: {len(tokens) if tokens else 0}")
        if tokens and len(tokens) > 0:
            connected.append('wordpress')
            logger.warning(f"[OAuth Monitoring] ✅ WordPress connected for user {user_id} ({len(tokens)} token(s))")
        else:
            logger.warning(f"[OAuth Monitoring] ❌ WordPress not connected for user {user_id} (no tokens found)")
    except Exception as e:
        logger.warning(f"[OAuth Monitoring] ⚠️ WordPress check failed for user {user_id}: {e}", exc_info=True)
    
    # Wix: Not checked (tokens in frontend sessionStorage)
    # TODO: Once backend storage is implemented, check wix_tokens table
    
    logger.warning(f"[OAuth Monitoring] Connected platforms for user {user_id}: {connected}")
    return connected


def create_oauth_monitoring_tasks(
    user_id: str,
    db: Session,
    platforms: Optional[List[str]] = None
) -> List[OAuthTokenMonitoringTask]:
    """
    Create OAuth token monitoring tasks for a user.
    
    If platforms are not provided, automatically detects connected platforms.
    Creates one task per platform with next_check set to 7 days from now.
    
    Args:
        user_id: User ID (Clerk string)
        db: Database session
        platforms: Optional list of platforms to create tasks for.
                   If None, auto-detects connected platforms.
                   Valid values: 'gsc', 'bing', 'wordpress', 'wix'
        
    Returns:
        List of created OAuthTokenMonitoringTask instances
    """
    try:
        # Auto-detect platforms if not provided
        if platforms is None:
            platforms = get_connected_platforms(user_id)
            logger.warning(f"[OAuth Monitoring] Auto-detected {len(platforms)} connected platforms for user {user_id}: {platforms}")
        else:
            logger.warning(f"[OAuth Monitoring] Creating monitoring tasks for specified platforms: {platforms}")
        
        if not platforms:
            logger.warning(f"[OAuth Monitoring] No connected platforms found for user {user_id}. No monitoring tasks created.")
            return []
        
        created_tasks = []
        now = datetime.utcnow()
        next_check = now + timedelta(days=7)  # 7 days from now
        
        for platform in platforms:
            # Check if task already exists for this user/platform combination
            existing_task = db.query(OAuthTokenMonitoringTask).filter(
                OAuthTokenMonitoringTask.user_id == user_id,
                OAuthTokenMonitoringTask.platform == platform
            ).first()
            
            if existing_task:
                logger.warning(
                    f"[OAuth Monitoring] Monitoring task already exists for user {user_id}, platform {platform}. "
                    f"Skipping creation."
                )
                continue
            
            # Create new monitoring task
            task = OAuthTokenMonitoringTask(
                user_id=user_id,
                platform=platform,
                status='active',
                next_check=next_check,
                created_at=now,
                updated_at=now
            )
            
            db.add(task)
            created_tasks.append(task)
            logger.warning(
                f"[OAuth Monitoring] Created OAuth token monitoring task for user {user_id}, "
                f"platform {platform}, next_check: {next_check.isoformat()}"
            )
        
        db.commit()
        logger.warning(
            f"[OAuth Monitoring] Successfully created {len(created_tasks)} OAuth token monitoring tasks "
            f"for user {user_id}"
        )
        
        return created_tasks
        
    except Exception as e:
        logger.error(
            f"Error creating OAuth token monitoring tasks for user {user_id}: {e}",
            exc_info=True
        )
        db.rollback()
        return []

