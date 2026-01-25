"""
Dependencies

Service dependency injection and provider management.
"""

from typing import Dict, Any, List, Optional, Protocol
from abc import ABC, abstractmethod
from loguru import logger

from .config import KeywordResearcherConfig, get_config
from .constants import DEFAULT_CONFIDENCE_SCORE


class AIProvider(Protocol):
    """Protocol for AI providers."""
    
    async def generate_response(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Any:
        """Generate response from AI provider."""
        ...

    async def health_check(self) -> bool:
        """Check if AI provider is healthy."""
        ...

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        ...


class DatabaseService(Protocol):
    """Protocol for database services."""
    
    async def save_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """Save analysis results."""
        ...

    async def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis by ID."""
        ...

    async def health_check(self) -> bool:
        """Check if database is healthy."""
        ...


class CacheService(Protocol):
    """Protocol for cache services."""
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        ...

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        ...

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        ...

    async def health_check(self) -> bool:
        """Check if cache is healthy."""
        ...


class KeywordResearcherDependencies:
    """Dependency injection container for keyword researcher service."""
    
    def __init__(self, config: Optional[KeywordResearcherConfig] = None):
        """
        Initialize dependencies.
        
        Args:
            config: Service configuration
        """
        self.config = config or get_config()
        self._ai_providers: Dict[str, AIProvider] = {}
        self._database_service: Optional[DatabaseService] = None
        self._cache_service: Optional[CacheService] = None
        
        # Initialize dependencies
        self._initialize_ai_providers()
    
    def _initialize_ai_providers(self):
        """Initialize AI providers based on configuration."""
        for provider_config in self.config.ai_providers:
            if provider_config.enabled:
                try:
                    provider = self._create_ai_provider(provider_config)
                    self._ai_providers[provider_config.provider_name] = provider
                    logger.info(f"Initialized AI provider: {provider_config.provider_name}")
                except Exception as e:
                    logger.error(f"Failed to initialize AI provider {provider_config.provider_name}: {e}")
    
    def _create_ai_provider(self, provider_config) -> AIProvider:
        """Create AI provider instance based on configuration."""
        provider_name = provider_config.provider_name
        
        if provider_name == "gemini":
            return GeminiProvider(provider_config)
        elif provider_name == "main_text_generation":
            return MainTextGenerationProvider(provider_config)
        else:
            raise ValueError(f"Unknown AI provider: {provider_name}")
    
    def get_ai_provider(self, provider_name: Optional[str] = None) -> AIProvider:
        """
        Get AI provider instance.
        
        Args:
            provider_name: Specific provider name, or None for primary provider
            
        Returns:
            AI provider instance
        """
        if provider_name:
            if provider_name not in self._ai_providers:
                raise ValueError(f"AI provider not found: {provider_name}")
            return self._ai_providers[provider_name]
        
        # Return first available provider
        if not self._ai_providers:
            raise ValueError("No AI providers available")
        
        return next(iter(self._ai_providers.values()))
    
    def get_available_ai_providers(self) -> List[str]:
        """
        Get list of available AI provider names.
        
        Returns:
            List of provider names
        """
        return list(self._ai_providers.keys())
    
    def set_database_service(self, service: DatabaseService):
        """
        Set database service dependency.
        
        Args:
            service: Database service instance
        """
        self._database_service = service
        logger.info("Database service dependency set")
    
    def get_database_service(self) -> Optional[DatabaseService]:
        """
        Get database service dependency.
        
        Returns:
            Database service instance or None
        """
        return self._database_service
    
    def set_cache_service(self, service: CacheService):
        """
        Set cache service dependency.
        
        Args:
            service: Cache service instance
        """
        self._cache_service = service
        logger.info("Cache service dependency set")
    
    def get_cache_service(self) -> Optional[CacheService]:
        """
        Get cache service dependency.
        
        Returns:
            Cache service instance or None
        """
        return self._cache_service
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all dependencies.
        
        Returns:
            Health check results
        """
        results = {
            'ai_providers': {},
            'database': 'not_configured',
            'cache': 'not_configured',
            'overall_status': 'healthy'
        }
        
        # Check AI providers
        for name, provider in self._ai_providers.items():
            try:
                is_healthy = await provider.health_check()
                results['ai_providers'][name] = 'healthy' if is_healthy else 'unhealthy'
            except Exception as e:
                logger.error(f"Health check failed for AI provider {name}: {e}")
                results['ai_providers'][name] = 'error'
        
        # Check database service
        if self._database_service:
            try:
                is_healthy = await self._database_service.health_check()
                results['database'] = 'healthy' if is_healthy else 'unhealthy'
            except Exception as e:
                logger.error(f"Health check failed for database service: {e}")
                results['database'] = 'error'
        
        # Check cache service
        if self._cache_service:
            try:
                is_healthy = await self._cache_service.health_check()
                results['cache'] = 'healthy' if is_healthy else 'unhealthy'
            except Exception as e:
                logger.error(f"Health check failed for cache service: {e}")
                results['cache'] = 'error'
        
        # Determine overall status
        unhealthy_services = []
        for service, status in results.items():
            if service != 'overall_status' and status in ['unhealthy', 'error']:
                unhealthy_services.append(service)
        
        if unhealthy_services:
            results['overall_status'] = 'degraded' if len(unhealthy_services) == 1 else 'unhealthy'
        
        return results


class GeminiProvider:
    """Gemini AI provider implementation."""
    
    def __init__(self, config):
        """Initialize Gemini provider."""
        self.config = config
        self.provider_name = "gemini"
    
    async def generate_response(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Any:
        """Generate response using Gemini."""
        try:
            from services.llm_providers.gemini_provider import gemini_structured_json_response
            
            response = gemini_structured_json_response(
                prompt=prompt,
                schema=schema or {}
            )
            
            return response
        except Exception as e:
            logger.error(f"Gemini provider error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check Gemini provider health."""
        try:
            # Simple test prompt
            test_response = await self.generate_response("Test prompt", {"type": "string"})
            return test_response is not None
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return False


class MainTextGenerationProvider:
    """Main text generation AI provider implementation."""
    
    def __init__(self, config):
        """Initialize main text generation provider."""
        self.config = config
        self.provider_name = "main_text_generation"
    
    async def generate_response(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Any:
        """Generate response using main text generation."""
        try:
            from services.llm_providers.main_text_generation import llm_text_gen
            
            response = await llm_text_gen(prompt)
            
            # If schema is provided, try to parse as JSON
            if schema and isinstance(response, str):
                import json
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    return response
            
            return response
        except Exception as e:
            logger.error(f"Main text generation provider error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check main text generation provider health."""
        try:
            test_response = await self.generate_response("Test prompt")
            return test_response is not None
        except Exception as e:
            logger.error(f"Main text generation health check failed: {e}")
            return False


class DefaultDatabaseService:
    """Default database service implementation."""
    
    def __init__(self, config):
        """Initialize database service."""
        self.config = config
    
    async def save_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """Save analysis results."""
        # TODO: Implement actual database operations
        analysis_id = f"analysis_{hash(str(analysis_data))}"
        logger.info(f"Saved analysis {analysis_id}")
        return analysis_id
    
    async def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis by ID."""
        # TODO: Implement actual database operations
        logger.info(f"Retrieved analysis {analysis_id}")
        return None
    
    async def health_check(self) -> bool:
        """Check database health."""
        # TODO: Implement actual health check
        return True


class DefaultCacheService:
    """Default cache service implementation."""
    
    def __init__(self, config):
        """Initialize cache service."""
        self.config = config
        self._cache: Dict[str, Any] = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return self._cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        self._cache[key] = value
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    async def health_check(self) -> bool:
        """Check cache health."""
        return True


class DependencyManager:
    """Global dependency manager singleton."""
    
    _instance: Optional['DependencyManager'] = None
    _dependencies: Optional[KeywordResearcherDependencies] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def initialize(cls, config: Optional[KeywordResearcherConfig] = None):
        """
        Initialize dependency manager.
        
        Args:
            config: Service configuration
        """
        cls._dependencies = KeywordResearcherDependencies(config)
        logger.info("Dependency manager initialized")
    
    @classmethod
    def get_dependencies(cls) -> KeywordResearcherDependencies:
        """
        Get dependencies instance.
        
        Returns:
            Dependencies instance
        """
        if cls._dependencies is None:
            cls.initialize()
        return cls._dependencies
    
    @classmethod
    def reset(cls):
        """Reset dependency manager (for testing)."""
        cls._instance = None
        cls._dependencies = None


def get_dependencies() -> KeywordResearcherDependencies:
    """
    Get dependency injection container.
    
    Returns:
        Dependencies instance
    """
    return DependencyManager.get_dependencies()


def initialize_dependencies(config: Optional[KeywordResearcherConfig] = None):
    """
    Initialize dependency injection container.
    
    Args:
        config: Service configuration
    """
    DependencyManager.initialize(config)


# Convenience functions for dependency access
def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    """Get AI provider dependency."""
    return get_dependencies().get_ai_provider(provider_name)


def get_database_service() -> Optional[DatabaseService]:
    """Get database service dependency."""
    return get_dependencies().get_database_service()


def get_cache_service() -> Optional[CacheService]:
    """Get cache service dependency."""
    return get_dependencies().get_cache_service()


async def check_dependencies_health() -> Dict[str, Any]:
    """Check health of all dependencies."""
    return await get_dependencies().health_check()
