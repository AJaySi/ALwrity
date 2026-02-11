"""
OAuth Provider Migration Script
Migrates existing provider-specific OAuth tokens to unified storage
and updates provider implementations to use the unified framework.
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any, List
from loguru import logger

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from services.integrations.unified_token_service import unified_token_service
from services.database import get_user_data_db_session


def create_unified_engine():
    """Create database engine for unified token storage."""
    database_url = os.getenv('USER_DATA_DATABASE_URL')
    if not database_url:
        raise ValueError("USER_DATA_DATABASE_URL environment variable not set")
    
    return create_engine(database_url)


def get_legacy_session():
    """Create database session for legacy token storage."""
    database_url = os.getenv('PLATFORM_DATABASE_URL')
    if not database_url:
        raise ValueError("PLATFORM_DATABASE_URL environment variable not set")
    
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    return Session()


def migrate_bing_tokens():
    """Migrate Bing OAuth tokens to unified storage."""
    logger.info("Starting Bing OAuth token migration...")
    
    legacy_session = get_legacy_session()
    
    try:
        # Get all Bing tokens
        result = legacy_session.execute(text("""
            SELECT user_id, access_token, refresh_token, token_type, 
                   expires_at, scope, site_url, created_at, updated_at, is_active
            FROM bing_oauth_tokens
            WHERE is_active = TRUE
        """))
        
        bing_tokens = result.fetchall()
        logger.info(f"Found {len(bing_tokens)} Bing tokens to migrate")
        
        migrated_count = 0
        for token in bing_tokens:
            try:
                # Extract account info from site_url if available
                account_info = {}
                if token['site_url']:
                    account_info['site_url'] = token['site_url']
                
                # Store in unified format
                unified_token_service.store_token(
                    provider_id='bing',
                    user_id=token['user_id'],
                    access_token=token['access_token'],
                    refresh_token=token['refresh_token'],
                    expires_at=token['expires_at'],
                    scope=token['scope'],
                    account_info=account_info,
                    metadata={
                        'legacy_site_url': token['site_url'],
                        'migrated_at': datetime.utcnow().isoformat(),
                        'migration_source': 'bing_oauth_tokens'
                    }
                )
                migrated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to migrate Bing token for user {token['user_id']}: {e}")
        
        logger.info(f"Successfully migrated {migrated_count} Bing tokens")
        
    except Exception as e:
        logger.error(f"Bing token migration failed: {e}")
        raise
    finally:
        legacy_session.close()


def migrate_gsc_tokens():
    """Migrate GSC OAuth tokens to unified storage."""
    logger.info("Starting GSC OAuth token migration...")
    
    legacy_session = get_legacy_session()
    
    try:
        # Get all GSC credentials
        result = legacy_session.execute(text("""
            SELECT user_id, token, refresh_token, expires_at, 
                   created_at, updated_at, is_active
            FROM gsc_credentials
            WHERE is_active = TRUE
        """))
        
        gsc_tokens = result.fetchall()
        logger.info(f"Found {len(gsc_tokens)} GSC tokens to migrate")
        
        migrated_count = 0
        for token in gsc_tokens:
            try:
                # Store in unified format
                unified_token_service.store_token(
                    provider_id='gsc',
                    user_id=token['user_id'],
                    access_token=token['token'],
                    refresh_token=token['refresh_token'],
                    expires_at=token['expires_at'],
                    account_info={'provider': 'google'},
                    metadata={
                        'migrated_at': datetime.utcnow().isoformat(),
                        'migration_source': 'gsc_credentials'
                    }
                )
                migrated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to migrate GSC token for user {token['user_id']}: {e}")
        
        logger.info(f"Successfully migrated {migrated_count} GSC tokens")
        
    except Exception as e:
        logger.error(f"GSC token migration failed: {e}")
        raise
    finally:
        legacy_session.close()


def migrate_wordpress_tokens():
    """Migrate WordPress OAuth tokens to unified storage."""
    logger.info("Starting WordPress OAuth token migration...")
    
    legacy_session = get_legacy_session()
    
    try:
        # Get all WordPress tokens
        result = legacy_session.execute(text("""
            SELECT user_id, access_token, refresh_token, token_type, 
                   expires_at, scope, blog_id, blog_url, 
                   created_at, updated_at, is_active
            FROM wordpress_oauth_tokens
            WHERE is_active = TRUE
        """))
        
        wp_tokens = result.fetchall()
        logger.info(f"Found {len(wp_tokens)} WordPress tokens to migrate")
        
        migrated_count = 0
        for token in wp_tokens:
            try:
                # Extract account info
                account_info = {}
                if token['blog_id']:
                    account_info['blog_id'] = token['blog_id']
                if token['blog_url']:
                    account_info['blog_url'] = token['blog_url']
                
                # Store in unified format
                unified_token_service.store_token(
                    provider_id='wordpress',
                    user_id=token['user_id'],
                    access_token=token['access_token'],
                    refresh_token=token['refresh_token'],
                    expires_at=token['expires_at'],
                    scope=token['scope'],
                    account_info=account_info,
                    metadata={
                        'legacy_blog_id': token['blog_id'],
                        'legacy_blog_url': token['blog_url'],
                        'migrated_at': datetime.utcnow().isoformat(),
                        'migration_source': 'wordpress_oauth_tokens'
                    }
                )
                migrated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to migrate WordPress token for user {token['user_id']}: {e}")
        
        logger.info(f"Successfully migrated {migrated_count} WordPress tokens")
        
    except Exception as e:
        logger.error(f"WordPress token migration failed: {e}")
        raise
    finally:
        legacy_session.close()


def migrate_wix_tokens():
    """Migrate Wix OAuth tokens to unified storage."""
    logger.info("Starting Wix OAuth token migration...")
    
    legacy_session = get_legacy_session()
    
    try:
        # Get all Wix tokens
        result = legacy_session.execute(text("""
            SELECT user_id, access_token, refresh_token, token_type, 
                   expires_in, site_id, member_id, created_at, 
                   updated_at, is_active
            FROM wix_oauth_tokens
            WHERE is_active = TRUE
        """))
        
        wix_tokens = result.fetchall()
        logger.info(f"Found {len(wix_tokens)} Wix tokens to migrate")
        
        migrated_count = 0
        for token in wix_tokens:
            try:
                # Calculate expiration time
                expires_at = None
                if token['expires_in']:
                    expires_at = datetime.utcnow() + timedelta(seconds=token['expires_in'])
                
                # Extract account info
                account_info = {}
                if token['site_id']:
                    account_info['site_id'] = token['site_id']
                if token['member_id']:
                    account_info['member_id'] = token['member_id']
                
                # Store in unified format
                unified_token_service.store_token(
                    provider_id='wix',
                    user_id=token['user_id'],
                    access_token=token['access_token'],
                    refresh_token=token['refresh_token'],
                    expires_at=expires_at,
                    account_info=account_info,
                    metadata={
                        'legacy_site_id': token['site_id'],
                        'legacy_member_id': token['member_id'],
                        'legacy_expires_in': token['expires_in'],
                        'migrated_at': datetime.utcnow().isoformat(),
                        'migration_source': 'wix_oauth_tokens'
                    }
                )
                migrated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to migrate Wix token for user {token['user_id']}: {e}")
        
        logger.info(f"Successfully migrated {migrated_count} Wix tokens")
        
    except Exception as e:
        logger.error(f"Wix token migration failed: {e}")
        raise
    finally:
        legacy_session.close()


def validate_migration():
    """Validate that migration was successful."""
    logger.info("Validating OAuth token migration...")
    
    try:
        # Get statistics from unified storage
        stats = unified_token_service.get_token_statistics()
        
        logger.info("Migration validation results:")
        logger.info(f"  Total tokens: {stats['total_tokens']}")
        logger.info(f"  Provider counts: {stats['provider_counts']}")
        
        # Verify expected providers are present
        expected_providers = ['bing', 'gsc', 'wordpress', 'wix']
        for provider in expected_providers:
            count = stats['provider_counts'].get(provider, 0)
            logger.info(f"  {provider}: {count} tokens")
        
        logger.info("Migration validation completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Migration validation failed: {e}")
        return False


def cleanup_legacy_tables():
    """
    Clean up legacy token tables after successful migration.
    
    WARNING: This function should only be called after manual verification
    that the migration was successful and the unified system is working properly.
    """
    logger.warning("Cleaning up legacy OAuth token tables...")
    
    legacy_session = get_legacy_session()
    
    try:
        # Deactivate legacy tokens (keep for rollback safety)
        tables_to_deactivate = [
            'bing_oauth_tokens',
            'gsc_credentials', 
            'wordpress_oauth_tokens',
            'wix_oauth_tokens'
        ]
        
        for table in tables_to_deactivate:
            try:
                legacy_session.execute(text(f"""
                    UPDATE {table} 
                    SET is_active = FALSE, updated_at = :updated_at
                    WHERE is_active = TRUE
                """), {"updated_at": datetime.utcnow()})
                
                logger.info(f"Deactivated tokens in {table}")
                
            except Exception as e:
                logger.error(f"Failed to deactivate tokens in {table}: {e}")
        
        legacy_session.commit()
        logger.warning("Legacy token tables deactivated (not dropped - can be reactivated if needed)")
        
    except Exception as e:
        logger.error(f"Legacy table cleanup failed: {e}")
        raise
    finally:
        legacy_session.close()


def run_full_migration():
    """Run the complete OAuth token migration process."""
    logger.info("Starting OAuth token unification migration...")
    
    try:
        # Check environment
        if not os.getenv('USER_DATA_DATABASE_URL'):
            raise ValueError("USER_DATA_DATABASE_URL not configured")
        
        if not os.getenv('PLATFORM_DATABASE_URL'):
            raise ValueError("PLATFORM_DATABASE_URL not configured")
        
        # Migrate each provider
        migrate_bing_tokens()
        migrate_gsc_tokens()
        migrate_wordpress_tokens()
        migrate_wix_tokens()
        
        # Validate migration
        if validate_migration():
            logger.info("OAuth token migration completed successfully!")
            
            # Ask for confirmation before cleanup
            response = input("Migration validation successful. Clean up legacy tables? (y/N): ")
            if response.lower() == 'y':
                cleanup_legacy_tables()
                logger.info("Legacy table cleanup completed")
            else:
                logger.info("Legacy tables preserved for manual cleanup")
        else:
            logger.error("Migration validation failed!")
            return False
            
    except Exception as e:
        logger.error(f"OAuth token migration failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("OAuth Token Unification Migration Script")
    print("=====================================")
    print("This script migrates OAuth tokens from provider-specific tables")
    print("to the unified token storage system.")
    print()
    print("Prerequisites:")
    print("- USER_DATA_DATABASE_URL environment variable set")
    print("- PLATFORM_DATABASE_URL environment variable set")
    print("- Both databases accessible")
    print()
    
    response = input("Proceed with migration? (y/N): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        sys.exit(0)
    
    success = run_full_migration()
    if success:
        print("Migration completed successfully!")
        sys.exit(0)
    else:
        print("Migration failed. Check logs for details.")
        sys.exit(1)
