"""
User Job Store Utilities
Utilities for managing per-user job stores based on website root.
"""

from typing import Optional
from urllib.parse import urlparse
from loguru import logger
from sqlalchemy.orm import Session as SQLSession

from services.database import get_session_for_user
from models.onboarding import OnboardingSession, WebsiteAnalysis


def extract_domain_root(url: str) -> str:
    """
    Extract domain root from a website URL for use as job store identifier.
    
    Examples:
        https://www.example.com -> example
        https://blog.example.com -> example
        https://example.co.uk -> example
        http://subdomain.example.com/path -> example
    
    Args:
        url: Website URL
        
    Returns:
        Domain root (e.g., 'example') or 'default' if extraction fails
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.netloc or parsed.path.split('/')[0]
        
        # Remove www. prefix if present
        if hostname.startswith('www.'):
            hostname = hostname[4:]
        
        # Split by dots and get the root domain
        # For example.com -> example, for example.co.uk -> example
        parts = hostname.split('.')
        if len(parts) >= 2:
            # Handle common TLDs that might be part of domain (e.g., co.uk)
            if len(parts) >= 3 and parts[-2] in ['co', 'com', 'net', 'org']:
                root = parts[-3]
            else:
                root = parts[-2]
        else:
            root = parts[0] if parts else 'default'
        
        # Clean and validate root
        root = root.lower().strip()
        # Remove invalid characters for job store name
        root = ''.join(c for c in root if c.isalnum() or c in ['-', '_'])
        
        if not root or len(root) < 2:
            return 'default'
        
        return root
        
    except Exception as e:
        logger.warning(f"Failed to extract domain root from URL '{url}': {e}")
        return 'default'


def get_user_job_store_name(user_id: str, db: SQLSession = None) -> str:
    """
    Get job store name for a user based on their website root from onboarding.
    
    Args:
        user_id: User ID (Clerk string)
        db: Optional database session (will create if not provided)
        
    Returns:
        Job store name (e.g., 'example' or 'default')
    """
    db_session = db
    close_db = False
    
    try:
        if not db_session:
            db_session = get_session_for_user(user_id)
            close_db = True
        
        if not db_session:
            logger.warning(f"Could not get database session for user {user_id}, using default job store")
            return 'default'
        
        # Get user's website URL from onboarding
        # Query directly since user_id is a string (Clerk ID)
        onboarding_session = db_session.query(OnboardingSession).filter(
            OnboardingSession.user_id == user_id
        ).order_by(OnboardingSession.updated_at.desc()).first()
        
        if not onboarding_session:
            logger.debug(
                f"[Job Store] No onboarding session found for user {user_id}, using default job store. "
                f"This is normal if user hasn't completed onboarding."
            )
            return 'default'
        
        # Get the latest website analysis for this session
        website_analysis = db_session.query(WebsiteAnalysis).filter(
            WebsiteAnalysis.session_id == onboarding_session.id
        ).order_by(WebsiteAnalysis.updated_at.desc()).first()
        
        if not website_analysis or not website_analysis.website_url:
            logger.debug(
                f"[Job Store] No website URL found for user {user_id} (session_id: {onboarding_session.id}), "
                f"using default job store. This is normal if website analysis wasn't completed."
            )
            return 'default'
        
        website_url = website_analysis.website_url
        domain_root = extract_domain_root(website_url)
        
        logger.debug(f"Job store for user {user_id}: {domain_root} (from {website_url})")
        return domain_root
        
    except Exception as e:
        logger.error(f"Error getting job store name for user {user_id}: {e}")
        return 'default'
    finally:
        if close_db and db_session:
            try:
                db_session.close()
            except Exception:
                pass

