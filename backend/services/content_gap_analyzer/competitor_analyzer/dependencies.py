"""
Dependencies Management for Competitor Analyzer Service

This module provides dependency injection and management for external services
including AI providers, databases, and other dependencies.
"""

from typing import Dict, Any, List, Optional, Union
from functools import lru_cache
import asyncio
from loguru import logger

from .config import get_config, get_ai_provider_config
from .constants import DEFAULT_AI_CONFIDENCE_SCORE, AI_RETRY_ATTEMPTS, AI_TIMEOUT_SECONDS


class AIProviderInterface:
    """Interface for AI providers."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.enabled = config.get('enabled', True)
        self.priority = config.get('priority', 1)
        self.max_tokens = config.get('max_tokens', 4000)
        self.timeout_seconds = config.get('timeout_seconds', AI_TIMEOUT_SECONDS)
        self.retry_attempts = config.get('retry_attempts', AI_RETRY_ATTEMPTS)
        self.confidence_threshold = config.get('confidence_threshold', DEFAULT_AI_CONFIDENCE_SCORE)
    
    async def generate_response(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], str]:
        """
        Generate AI response.
        
        Args:
            prompt: Input prompt
            schema: Optional response schema
            
        Returns:
            Union[Dict[str, Any], str]: AI response
        """
        raise NotImplementedError("Subclasses must implement generate_response method")
    
    async def health_check(self) -> bool:
        """
        Check if AI provider is healthy.
        
        Returns:
            bool: Health status
        """
        return True


class LLMTextGenProvider(AIProviderInterface):
    """Implementation for llm_text_gen provider."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("llm_text_gen", config)
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the llm_text_gen client."""
        try:
            # Import the existing llm_text_gen service
            from services.llm_providers.llm_text_gen import llm_text_gen
            self._client = llm_text_gen
            logger.info("✅ LLMTextGen provider initialized successfully")
        except ImportError as e:
            logger.error(f"❌ Failed to import llm_text_gen: {e}")
            self.enabled = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLMTextGen client: {e}")
            self.enabled = False
    
    async def generate_response(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], str]:
        """
        Generate response using llm_text_gen.
        
        Args:
            prompt: Input prompt
            schema: Optional response schema
            
        Returns:
            Union[Dict[str, Any], str]: AI response
        """
        if not self.enabled or not self._client:
            raise Exception(f"LLMTextGen provider is not available")
        
        try:
            # Use the existing llm_text_gen service
            if schema:
                # For structured responses, use the appropriate method
                response = await self._client.generate_structured_response(prompt, schema)
            else:
                # For text responses
                response = await self._client.generate_text(prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in LLMTextGen generate_response: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check LLMTextGen provider health."""
        try:
            if not self.enabled or not self._client:
                return False
            
            # Simple health check - try to generate a simple response
            test_prompt = "Hello, are you working?"
            response = await self._client.generate_text(test_prompt)
            return bool(response)
            
        except Exception as e:
            logger.error(f"LLMTextGen health check failed: {e}")
            return False


class GeminiProvider(AIProviderInterface):
    """Implementation for Gemini provider."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("gemini", config)
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Gemini client."""
        try:
            # Import the existing gemini provider
            from services.llm_providers.gemini_provider import gemini_structured_json_response
            self._client = gemini_structured_json_response
            logger.info("✅ Gemini provider initialized successfully")
        except ImportError as e:
            logger.error(f"❌ Failed to import gemini provider: {e}")
            self.enabled = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini client: {e}")
            self.enabled = False
    
    async def generate_response(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], str]:
        """
        Generate response using Gemini.
        
        Args:
            prompt: Input prompt
            schema: Optional response schema
            
        Returns:
            Union[Dict[str, Any], str]: AI response
        """
        if not self.enabled or not self._client:
            raise Exception(f"Gemini provider is not available")
        
        try:
            # Use the existing gemini provider
            if schema:
                response = self._client(prompt=prompt, schema=schema)
            else:
                # For non-structured responses, create a simple schema
                simple_schema = {
                    "type": "object",
                    "properties": {
                        "response": {"type": "string"}
                    }
                }
                response = self._client(prompt=prompt, schema=simple_schema)
                response = response.get('response', str(response))
            
            return response
            
        except Exception as e:
            logger.error(f"Error in Gemini generate_response: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check Gemini provider health."""
        try:
            if not self.enabled or not self._client:
                return False
            
            # Simple health check
            test_prompt = "Hello"
            test_schema = {
                "type": "object",
                "properties": {
                    "response": {"type": "string"}
                }
            }
            response = self._client(prompt=test_prompt, schema=test_schema)
            return bool(response)
            
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return False


class CompetitorAnalyzerDependencies:
    """
    Dependency manager for Competitor Analyzer Service.
    
    This class manages all external dependencies including AI providers,
    database connections, caching, and other services.
    """
    
    def __init__(self):
        self._ai_providers: Dict[str, AIProviderInterface] = {}
        self._database_connections: Dict[str, Any] = {}
        self._cache_clients: Dict[str, Any] = {}
        self._external_services: Dict[str, Any] = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize all dependencies."""
        try:
            logger.info("🔄 Initializing Competitor Analyzer dependencies...")
            
            # Initialize AI providers
            await self._initialize_ai_providers()
            
            # Initialize database connections
            await self._initialize_database_connections()
            
            # Initialize cache clients
            await self._initialize_cache_clients()
            
            # Initialize external services
            await self._initialize_external_services()
            
            self._initialized = True
            logger.info("✅ Competitor Analyzer dependencies initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize dependencies: {e}")
            raise
    
    async def _initialize_ai_providers(self):
        """Initialize AI providers."""
        try:
            config = get_config()
            
            for provider_config in config.ai_providers:
                if not provider_config.enabled:
                    continue
                
                provider_name = provider_config.name
                provider_dict = provider_config.dict()
                
                if provider_name == "llm_text_gen":
                    provider = LLMTextGenProvider(provider_dict)
                elif provider_name == "gemini":
                    provider = GeminiProvider(provider_dict)
                else:
                    logger.warning(f"Unknown AI provider: {provider_name}")
                    continue
                
                # Health check the provider
                if await provider.health_check():
                    self._ai_providers[provider_name] = provider
                    logger.info(f"✅ AI provider '{provider_name}' initialized and healthy")
                else:
                    logger.warning(f"⚠️ AI provider '{provider_name}' failed health check")
            
            if not self._ai_providers:
                raise Exception("No healthy AI providers available")
                
        except Exception as e:
            logger.error(f"Error initializing AI providers: {e}")
            raise
    
    async def _initialize_database_connections(self):
        """Initialize database connections."""
        try:
            config = get_config()
            
            if config.database_url:
                # Initialize database connection based on URL
                # This would be implemented based on your database setup
                logger.info("🔄 Database connection configured")
            else:
                logger.info("ℹ️ No database URL configured, using default settings")
                
        except Exception as e:
            logger.error(f"Error initializing database connections: {e}")
            # Don't raise - database is optional for basic functionality
    
    async def _initialize_cache_clients(self):
        """Initialize cache clients."""
        try:
            config = get_config()
            
            if config.analysis.enable_caching:
                # Initialize cache client (Redis, Memcached, etc.)
                logger.info("🔄 Cache client configured")
            else:
                logger.info("ℹ️ Caching is disabled")
                
        except Exception as e:
            logger.error(f"Error initializing cache clients: {e}")
            # Don't raise - caching is optional
    
    async def _initialize_external_services(self):
        """Initialize external services."""
        try:
            config = get_config()
            
            # Initialize website analyzer if enabled
            if config.enable_website_analyzer:
                try:
                    from ..website_analyzer import WebsiteAnalyzer
                    self._external_services['website_analyzer'] = WebsiteAnalyzer()
                    logger.info("✅ Website analyzer service initialized")
                except ImportError:
                    logger.warning("⚠️ Website analyzer service not available")
            
            # Initialize AI engine service if enabled
            if config.enable_ai_engine_service:
                try:
                    from ..ai_engine_service import AIEngineService
                    self._external_services['ai_engine_service'] = AIEngineService()
                    logger.info("✅ AI engine service initialized")
                except ImportError:
                    logger.warning("⚠️ AI engine service not available")
                
        except Exception as e:
            logger.error(f"Error initializing external services: {e}")
            # Don't raise - external services are optional
    
    def get_ai_provider(self, provider_name: Optional[str] = None) -> AIProviderInterface:
        """
        Get an AI provider instance.
        
        Args:
            provider_name: Specific provider name (optional)
            
        Returns:
            AIProviderInterface: AI provider instance
        """
        if not self._initialized:
            raise Exception("Dependencies not initialized")
        
        if provider_name:
            if provider_name in self._ai_providers:
                return self._ai_providers[provider_name]
            else:
                raise Exception(f"AI provider '{provider_name}' not available")
        
        # Return primary provider or first available
        config = get_config()
        primary_provider = config.primary_ai_provider
        
        if primary_provider in self._ai_providers:
            return self._ai_providers[primary_provider]
        
        # Fallback to first available provider
        if self._ai_providers:
            first_provider = next(iter(self._ai_providers.values()))
            logger.warning(f"Primary provider '{primary_provider}' not available, using '{first_provider.name}'")
            return first_provider
        
        raise Exception("No AI providers available")
    
    def get_available_ai_providers(self) -> List[str]:
        """
        Get list of available AI providers.
        
        Returns:
            List[str]: List of provider names
        """
        if not self._initialized:
            return []
        
        return list(self._ai_providers.keys())
    
    def get_database_connection(self, connection_name: str = "default"):
        """
        Get database connection.
        
        Args:
            connection_name: Name of the connection
            
        Returns:
            Any: Database connection
        """
        if not self._initialized:
            raise Exception("Dependencies not initialized")
        
        if connection_name in self._database_connections:
            return self._database_connections[connection_name]
        
        raise Exception(f"Database connection '{connection_name}' not available")
    
    def get_cache_client(self, cache_name: str = "default"):
        """
        Get cache client.
        
        Args:
            cache_name: Name of the cache
            
        Returns:
            Any: Cache client
        """
        if not self._initialized:
            raise Exception("Dependencies not initialized")
        
        if cache_name in self._cache_clients:
            return self._cache_clients[cache_name]
        
        raise Exception(f"Cache client '{cache_name}' not available")
    
    def get_external_service(self, service_name: str):
        """
        Get external service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Any: External service instance
        """
        if not self._initialized:
            raise Exception("Dependencies not initialized")
        
        if service_name in self._external_services:
            return self._external_services[service_name]
        
        raise Exception(f"External service '{service_name}' not available")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all dependencies.
        
        Returns:
            Dict[str, Any]: Health check results
        """
        if not self._initialized:
            return {
                "status": "unhealthy",
                "error": "Dependencies not initialized"
            }
        
        health_results = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",  # Would use actual timestamp
            "dependencies": {}
        }
        
        # Check AI providers
        ai_health = {}
        for name, provider in self._ai_providers.items():
            try:
                is_healthy = await provider.health_check()
                ai_health[name] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "enabled": provider.enabled,
                    "priority": provider.priority
                }
            except Exception as e:
                ai_health[name] = {
                    "status": "error",
                    "error": str(e)
                }
                health_results["status"] = "degraded"
        
        health_results["dependencies"]["ai_providers"] = ai_health
        
        # Check database connections
        db_health = {}
        for name in self._database_connections:
            try:
                # Would implement actual health check
                db_health[name] = {"status": "healthy"}
            except Exception as e:
                db_health[name] = {"status": "error", "error": str(e)}
                health_results["status"] = "degraded"
        
        health_results["dependencies"]["database"] = db_health
        
        # Check cache clients
        cache_health = {}
        for name in self._cache_clients:
            try:
                # Would implement actual health check
                cache_health[name] = {"status": "healthy"}
            except Exception as e:
                cache_health[name] = {"status": "error", "error": str(e)}
                health_results["status"] = "degraded"
        
        health_results["dependencies"]["cache"] = cache_health
        
        # Check external services
        external_health = {}
        for name, service in self._external_services.items():
            try:
                # Would implement actual health check
                external_health[name] = {"status": "healthy"}
            except Exception as e:
                external_health[name] = {"status": "error", "error": str(e)}
                health_results["status"] = "degraded"
        
        health_results["dependencies"]["external_services"] = external_health
        
        return health_results
    
    async def shutdown(self):
        """Shutdown all dependencies."""
        try:
            logger.info("🔄 Shutting down Competitor Analyzer dependencies...")
            
            # Close database connections
            for name, connection in self._database_connections.items():
                try:
                    # Would implement actual connection closing
                    logger.info(f"Closed database connection: {name}")
                except Exception as e:
                    logger.error(f"Error closing database connection {name}: {e}")
            
            # Close cache clients
            for name, client in self._cache_clients.items():
                try:
                    # Would implement actual client closing
                    logger.info(f"Closed cache client: {name}")
                except Exception as e:
                    logger.error(f"Error closing cache client {name}: {e}")
            
            # Reset state
            self._ai_providers.clear()
            self._database_connections.clear()
            self._cache_clients.clear()
            self._external_services.clear()
            self._initialized = False
            
            logger.info("✅ Competitor Analyzer dependencies shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during dependency shutdown: {e}")


# Global dependency manager instance
_dependency_manager: Optional[CompetitorAnalyzerDependencies] = None


@lru_cache()
def get_dependencies() -> CompetitorAnalyzerDependencies:
    """
    Get the global dependency manager instance.
    
    Returns:
        CompetitorAnalyzerDependencies: Dependency manager instance
    """
    global _dependency_manager
    
    if _dependency_manager is None:
        _dependency_manager = CompetitorAnalyzerDependencies()
    
    return _dependency_manager


async def initialize_dependencies():
    """Initialize the global dependency manager."""
    dependencies = get_dependencies()
    await dependencies.initialize()


async def shutdown_dependencies():
    """Shutdown the global dependency manager."""
    dependencies = get_dependencies()
    await dependencies.shutdown()


# Dependency injection decorator
def inject_ai_provider(provider_name: Optional[str] = None):
    """
    Decorator for injecting AI provider into functions.
    
    Args:
        provider_name: Specific provider name (optional)
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            dependencies = get_dependencies()
            ai_provider = dependencies.get_ai_provider(provider_name)
            return await func(ai_provider, *args, **kwargs)
        return wrapper
    return decorator


def inject_database(connection_name: str = "default"):
    """
    Decorator for injecting database connection into functions.
    
    Args:
        connection_name: Name of the connection
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            dependencies = get_dependencies()
            db_connection = dependencies.get_database_connection(connection_name)
            return func(db_connection, *args, **kwargs)
        return wrapper
    return decorator


def inject_cache(cache_name: str = "default"):
    """
    Decorator for injecting cache client into functions.
    
    Args:
        cache_name: Name of the cache
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            dependencies = get_dependencies()
            cache_client = dependencies.get_cache_client(cache_name)
            return func(cache_client, *args, **kwargs)
        return wrapper
    return decorator


def inject_external_service(service_name: str):
    """
    Decorator for injecting external service into functions.
    
    Args:
        service_name: Name of the service
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            dependencies = get_dependencies()
            service = dependencies.get_external_service(service_name)
            return func(service, *args, **kwargs)
        return wrapper
    return decorator
