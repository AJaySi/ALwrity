"""
Unified OAuth Validator for Onboarding
Validates OAuth connections using unified token service while preserving existing functionality.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from services.integrations.unified_token_service import unified_token_service


class UnifiedOAuthValidator:
    """
    Validates OAuth connections using unified token service.
    
    This class provides a bridge between the existing onboarding system
    and the new unified OAuth framework, ensuring no breaking changes
    while adopting the unified token service.
    """
    
    def __init__(self):
        """Initialize the unified OAuth validator."""
        self.token_service = unified_token_service
        self.supported_providers = ['gsc', 'bing', 'wordpress', 'wix']
    
    def validate_step_5_completion(self, user_id: str) -> bool:
        """
        Validate Step 5 completion using unified token service.
        
        This method replaces the basic Step 5 validation with comprehensive
        OAuth connection checking using the unified token service.
        
        Args:
            user_id: User identifier
            
        Returns:
            bool: True if user has at least one valid OAuth connection
        """
        try:
            logger.info(f"[UnifiedOAuthValidator] Validating Step 5 for user {user_id}")
            
            # Get all tokens for user using unified service
            tokens = self.token_service.get_all_user_tokens(user_id)
            
            if not tokens:
                logger.warning(f"[UnifiedOAuthValidator] No OAuth tokens found for user {user_id}")
                return False
            
            # Check if any tokens are valid and not expired
            valid_tokens = []
            expiring_tokens = []
            
            for token in tokens:
                provider_id = token.provider_id
                
                # Check if token is expired
                is_expired = self.token_service.is_token_expired(provider_id, user_id)
                
                if not is_expired:
                    valid_tokens.append({
                        'provider': provider_id,
                        'display_name': self._get_provider_display_name(provider_id),
                        'connected_at': token.created_at,
                        'expires_at': token.expires_at
                    })
                    logger.info(f"[UnifiedOAuthValidator] Valid token found: {provider_id}")
                else:
                    expiring_tokens.append({
                        'provider': provider_id,
                        'display_name': self._get_provider_display_name(provider_id),
                        'expired_at': token.expires_at
                    })
                    logger.warning(f"[UnifiedOAuthValidator] Expired token found: {provider_id}")
            
            # Step 5 is complete if user has at least one valid token
            has_valid_connection = len(valid_tokens) > 0
            
            # Log detailed validation results
            logger.info(f"[UnifiedOAuthValidator] Step 5 validation results for user {user_id}:")
            logger.info(f"  - Valid connections: {len(valid_tokens)}")
            logger.info(f"  - Expired connections: {len(expiring_tokens)}")
            logger.info(f"  - Step 5 complete: {has_valid_connection}")
            
            if valid_tokens:
                logger.info(f"[UnifiedOAuthValidator] Valid providers: {[token['provider'] for token in valid_tokens]}")
            
            if expiring_tokens:
                logger.warning(f"[UnifiedOAuthValidator] Expired providers: {[token['provider'] for token in expiring_tokens]}")
            
            return has_valid_connection
            
        except Exception as e:
            logger.error(f"[UnifiedOAuthValidator] Error validating Step 5 for user {user_id}: {e}")
            # Return conservative result to avoid blocking users
            return False
    
    def get_connection_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive summary of all OAuth connections.
        
        This method provides detailed connection information for onboarding
        and monitoring purposes using the unified token service.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict[str, Any]: Comprehensive connection summary
        """
        try:
            logger.info(f"[UnifiedOAuthValidator] Getting connection summary for user {user_id}")
            
            # Get all tokens using unified service
            tokens = self.token_service.get_all_user_tokens(user_id)
            
            summary = {
                'total_platforms': len(tokens),
                'connected_platforms': 0,
                'expiring_platforms': 0,
                'platforms': [],
                'expiring_soon': [],
                'validation_time': datetime.utcnow().isoformat(),
                'supported_providers': self.supported_providers
            }
            
            # Process each token
            for token in tokens:
                provider_id = token.provider_id
                is_expired = self.token_service.is_token_expired(provider_id, user_id)
                
                platform_info = {
                    'provider': provider_id,
                    'display_name': self._get_provider_display_name(provider_id),
                    'connected_at': token.created_at.isoformat() if token.created_at else None,
                    'expires_at': token.expires_at.isoformat() if token.expires_at else None,
                    'is_active': token.is_active,
                    'scope': token.scope,
                    'account_info': self._get_account_info(token)
                }
                
                if not is_expired:
                    summary['connected_platforms'] += 1
                    summary['platforms'].append(platform_info)
                    logger.info(f"[UnifiedOAuthValidator] Active connection: {provider_id}")
                else:
                    summary['expiring_platforms'] += 1
                    platform_info['status'] = 'expired'
                    summary['platforms'].append(platform_info)
                    logger.warning(f"[UnifiedOAuthValidator] Expired connection: {provider_id}")
                
                # Check if token is expiring soon (within 7 days)
                if token.expires_at:
                    days_until_expiry = (token.expires_at - datetime.utcnow()).days
                    if 0 <= days_until_expiry <= 7:
                        expiring_soon_info = {
                            'provider': provider_id,
                            'display_name': self._get_provider_display_name(provider_id),
                            'expires_at': token.expires_at.isoformat(),
                            'days_until_expiry': days_until_expiry
                        }
                        summary['expiring_soon'].append(expiring_soon_info)
                        logger.warning(f"[UnifiedOAuthValidator] Token expiring soon: {provider_id} in {days_until_expiry} days")
            
            # Add statistics from unified service
            stats = self.token_service.get_token_statistics()
            summary['token_statistics'] = stats
            
            logger.info(f"[UnifiedOAuthValidator] Connection summary for user {user_id}:")
            logger.info(f"  - Total platforms: {summary['total_platforms']}")
            logger.info(f"  - Connected platforms: {summary['connected_platforms']}")
            logger.info(f"  - Expiring platforms: {summary['expiring_platforms']}")
            logger.info(f"  - Expiring soon: {len(summary['expiring_soon'])}")
            
            return summary
            
        except Exception as e:
            logger.error(f"[UnifiedOAuthValidator] Error getting connection summary for user {user_id}: {e}")
            # Return safe fallback summary
            return {
                'total_platforms': 0,
                'connected_platforms': 0,
                'expiring_platforms': 0,
                'platforms': [],
                'expiring_soon': [],
                'validation_time': datetime.utcnow().isoformat(),
                'error': str(e),
                'supported_providers': self.supported_providers
            }
    
    def validate_provider_connection(self, user_id: str, provider_id: str) -> Dict[str, Any]:
        """
        Validate connection for a specific provider.
        
        Args:
            user_id: User identifier
            provider_id: Provider identifier
            
        Returns:
            Dict[str, Any]: Provider-specific validation result
        """
        try:
            if provider_id not in self.supported_providers:
                return {
                    'valid': False,
                    'error': f'Provider {provider_id} is not supported',
                    'supported_providers': self.supported_providers
                }
            
            # Get token for specific provider
            token = self.token_service.get_token(provider_id, user_id)
            
            if not token:
                return {
                    'valid': False,
                    'error': f'No token found for {provider_id}',
                    'provider': provider_id,
                    'display_name': self._get_provider_display_name(provider_id)
                }
            
            # Check if token is expired
            is_expired = self.token_service.is_token_expired(provider_id, user_id)
            
            return {
                'valid': not is_expired,
                'provider': provider_id,
                'display_name': self._get_provider_display_name(provider_id),
                'connected_at': token.created_at.isoformat() if token.created_at else None,
                'expires_at': token.expires_at.isoformat() if token.expires_at else None,
                'is_expired': is_expired,
                'is_active': token.is_active,
                'scope': token.scope,
                'account_info': self._get_account_info(token)
            }
            
        except Exception as e:
            logger.error(f"[UnifiedOAuthValidator] Error validating {provider_id} for user {user_id}: {e}")
            return {
                'valid': False,
                'error': str(e),
                'provider': provider_id,
                'display_name': self._get_provider_display_name(provider_id)
            }
    
    def get_provider_health_status(self, user_id: str) -> Dict[str, Any]:
        """
        Get health status for all providers.
        
        This method provides comprehensive health information for monitoring
        and analytics purposes.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict[str, Any]: Health status for all providers
        """
        try:
            logger.info(f"[UnifiedOAuthValidator] Getting provider health status for user {user_id}")
            
            health_status = {}
            
            # Get statistics from unified service
            stats = self.token_service.get_token_statistics()
            
            for provider_id in self.supported_providers:
                provider_validation = self.validate_provider_connection(user_id, provider_id)
                
                # Calculate health score
                health_score = 100
                if not provider_validation['valid']:
                    health_score = 0
                elif provider_validation.get('is_expired'):
                    health_score = 25
                elif provider_validation.get('expires_at'):
                    # Calculate days until expiry
                    expires_at = datetime.fromisoformat(provider_validation['expires_at'].replace('Z', '+00:00'))
                    days_until_expiry = (expires_at - datetime.utcnow()).days
                    
                    if days_until_expiry <= 1:
                        health_score = 50
                    elif days_until_expiry <= 7:
                        health_score = 75
                
                health_status[provider_id] = {
                    'display_name': self._get_provider_display_name(provider_id),
                    'health_score': health_score,
                    'status': self._get_health_status_from_score(health_score),
                    'validation': provider_validation,
                    'last_checked': datetime.utcnow().isoformat()
                }
            
            # Add overall statistics
            health_status['overall'] = {
                'total_providers': len(self.supported_providers),
                'healthy_providers': len([p for p in health_status.values() if p['health_score'] >= 75]),
                'warning_providers': len([p for p in health_status.values() if 25 <= p['health_score'] < 75]),
                'critical_providers': len([p for p in health_status.values() if p['health_score'] < 25]),
                'average_health_score': sum(p['health_score'] for p in health_status.values()) / len(health_status),
                'token_statistics': stats
            }
            
            logger.info(f"[UnifiedOAuthValidator] Provider health status for user {user_id}:")
            logger.info(f"  - Healthy providers: {health_status['overall']['healthy_providers']}")
            logger.info(f"  - Warning providers: {health_status['overall']['warning_providers']}")
            logger.info(f"  - Critical providers: {health_status['overall']['critical_providers']}")
            logger.info(f"  - Average health score: {health_status['overall']['average_health_score']:.1f}")
            
            return health_status
            
        except Exception as e:
            logger.error(f"[UnifiedOAuthValidator] Error getting provider health status for user {user_id}: {e}")
            return {
                'error': str(e),
                'overall': {
                    'total_providers': len(self.supported_providers),
                    'healthy_providers': 0,
                    'warning_providers': 0,
                    'critical_providers': len(self.supported_providers),
                    'average_health_score': 0
                }
            }
    
    def _get_provider_display_name(self, provider_id: str) -> str:
        """Get display name for provider."""
        display_names = {
            'gsc': 'Google Search Console',
            'bing': 'Bing Webmaster Tools',
            'wordpress': 'WordPress.com',
            'wix': 'Wix'
        }
        return display_names.get(provider_id, provider_id.title())
    
    def _get_account_info(self, token) -> Dict[str, Any]:
        """Extract account information from token."""
        account_info = {}
        
        if token.account_email:
            account_info['email'] = token.account_email
        if token.account_name:
            account_info['name'] = token.account_name
        if token.account_id:
            account_info['account_id'] = token.account_id
        
        # Parse metadata for additional account info
        if token.metadata_json:
            try:
                import json
                metadata = json.loads(token.metadata_json)
                account_info.update(metadata.get('account_info', {}))
            except (json.JSONDecodeError, Exception):
                logger.warning(f"[UnifiedOAuthValidator] Invalid JSON in metadata for token {token.provider_id}")
        
        return account_info
    
    def _get_health_status_from_score(self, score: int) -> str:
        """Get health status string from health score."""
        if score >= 75:
            return 'healthy'
        elif score >= 25:
            return 'warning'
        else:
            return 'critical'
    
    def _fallback_validation(self, user_id: str) -> bool:
        """
        Fallback validation removed for security and maintainability.
        
        The unified OAuth validator provides comprehensive validation
        without the complexity and potential security issues of fallback mechanisms.
        """
        logger.warning(f"[UnifiedOAuthValidator] Fallback validation disabled for user {user_id}")
        logger.warning(f"[UnifiedOAuthValidator] Use unified token service for consistent validation")
        
        # Return conservative result - this maintains existing behavior
        # while encouraging adoption of unified patterns
        return False
