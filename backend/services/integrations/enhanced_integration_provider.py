"""
Enhanced Integration Provider with Error Handling & Resilience
Provides enhanced error handling, circuit breaker, and retry logic for OAuth integrations.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from loguru import logger

from .base import (
    IntegrationProvider,
    ConnectionStatus,
    AuthUrlPayload,
    ConnectionResult,
    RefreshResult,
    Account,
)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    expected_exception: type = Exception
    success_threshold: int = 3


class CircuitBreaker:
    """Circuit breaker implementation for OAuth operations."""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        
    def __call__(self, func: Callable) -> Callable:
        """Decorator for circuit breaker functionality."""
        def wrapper(*args, **kwargs):
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise Exception(f"Circuit breaker is OPEN for {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.config.expected_exception as e:
                self._on_failure()
                raise e
                
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        if self.last_failure_time is None:
            return False
        return time.time() - self.last_failure_time >= self.config.recovery_timeout
    
    def _on_success(self):
        """Handle successful operation."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logger.info("Circuit breaker reset to CLOSED")
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker OPENED after {self.failure_count} failures")


class EnhancedIntegrationProvider:
    """Enhanced integration provider with error handling and resilience."""
    
    def __init__(self, provider: IntegrationProvider):
        self.provider = provider
        self.logger = logger.bind(provider=provider.key)
        
        # Circuit breaker configuration
        self.circuit_breaker = CircuitBreaker(
            config=CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60,
                expected_exception=Exception
            )
        )
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 1.0
        self.backoff_factor = 2.0
    
    @property
    def key(self) -> str:
        return self.provider.key
    
    @property
    def display_name(self) -> str:
        return self.provider.display_name
    
    def get_auth_url(self, user_id: str, redirect_uri: Optional[str] = None) -> AuthUrlPayload:
        """Get auth URL with enhanced error handling."""
        return self._execute_with_resilience(
            operation="get_auth_url",
            func=self.provider.get_auth_url,
            user_id=user_id,
            redirect_uri=redirect_uri,
        )

    def handle_callback(self, code: str, state: str) -> ConnectionResult:
        """Handle OAuth callback with enhanced error handling."""
        return self._execute_with_resilience(
            operation="handle_callback",
            func=self.provider.handle_callback,
            code=code,
            state=state,
        )

    def get_connection_status(self, user_id: str) -> ConnectionStatus:
        """Get connection status with enhanced error handling."""
        return self._execute_with_resilience(
            operation="get_connection_status",
            func=self.provider.get_connection_status,
            user_id=user_id,
        )

    def refresh_token(self, user_id: str) -> Optional[RefreshResult]:
        """Refresh token with enhanced error handling."""
        return self._execute_with_resilience(
            operation="refresh_token",
            func=self.provider.refresh_token,
            user_id=user_id,
        )

    def disconnect(self, user_id: str) -> bool:
        """Disconnect provider with enhanced error handling."""
        return self._execute_with_resilience(
            operation="disconnect",
            func=self.provider.disconnect,
            user_id=user_id,
        )

    def list_connected_accounts(self, user_id: str) -> list[Account]:
        """List connected accounts with enhanced error handling."""
        return self._execute_with_resilience(
            operation="list_connected_accounts",
            func=self.provider.list_connected_accounts,
            user_id=user_id,
        )

    def _execute_with_resilience(
        self, 
        operation: str, 
        func: Callable, 
        **kwargs
    ) -> Any:
        """Execute operation with circuit breaker and retry logic."""
        
        # Apply circuit breaker
        protected_func = self.circuit_breaker(func)
        
        # Execute with retries
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                self.logger.debug(f"Executing {operation} for {kwargs.get('user_id', 'unknown')}, attempt {attempt + 1}")
                
                result = protected_func(**kwargs)
                
                # Log success on final attempt
                if attempt > 0:
                    self.logger.info(f"Operation {operation} succeeded after {attempt + 1} attempts")
                
                return result
                
            except Exception as e:
                last_exception = e
                self.logger.warning(
                    f"Operation {operation} failed on attempt {attempt + 1}: {e}"
                )
                
                # Don't retry on last attempt
                if attempt < self.max_retries:
                    delay = self.retry_delay * (self.backoff_factor ** attempt)
                    self.logger.debug(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
        
        # All retries failed
        self.logger.error(
            f"Operation {operation} failed after {self.max_retries + 1} attempts: {last_exception}"
        )
        
        # Return appropriate error response based on operation
        if operation == "get_connection_status":
            return ConnectionStatus(
                connected=False,
                provider_id=self.provider.key,
                user_id=kwargs.get("user_id", "unknown"),
                error=f"Service unavailable after retries: {str(last_exception)}",
                details={
                    "circuit_breaker": self.circuit_breaker.state.value,
                    "attempts": self.max_retries + 1,
                    "last_error": str(last_exception)
                }
            )
        elif operation == "get_auth_url":
            return AuthUrlPayload(
                auth_url="",
                state="",
                provider_id=self.provider.key,
                details={"error": f"Service unavailable: {str(last_exception)}"}
            )
        elif operation == "handle_callback":
            return ConnectionResult(
                success=False,
                user_id=kwargs.get("state", "unknown"),
                provider_id=self.provider.key,
                error=f"Service unavailable after retries: {str(last_exception)}",
            )
        elif operation == "refresh_token":
            return RefreshResult(
                success=False,
                user_id=kwargs.get("user_id", "unknown"),
                provider_id=self.provider.key,
                error=f"Service unavailable after retries: {str(last_exception)}",
            )
        elif operation == "disconnect":
            return False
        elif operation == "list_connected_accounts":
            return []
        else:
            raise last_exception
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the integration provider."""
        return {
            "provider": self.provider.key,
            "display_name": self.provider.display_name,
            "circuit_breaker_state": self.circuit_breaker.state.value,
            "failure_count": self.circuit_breaker.failure_count,
            "success_count": self.circuit_breaker.success_count,
            "last_failure_time": self.circuit_breaker.last_failure_time,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay
        }


def create_enhanced_provider(provider: IntegrationProvider) -> EnhancedIntegrationProvider:
    """Factory function to create enhanced provider."""
    return EnhancedIntegrationProvider(provider)
