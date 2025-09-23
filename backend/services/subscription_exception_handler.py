"""
Comprehensive Exception Handling and Logging for Subscription System
Provides robust error handling, logging, and monitoring for the usage-based subscription system.
"""

import traceback
import json
from datetime import datetime
from typing import Dict, Any, Optional, Union, List
from enum import Enum
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.subscription_models import APIProvider, UsageAlert

class SubscriptionErrorType(Enum):
    USAGE_LIMIT_EXCEEDED = "usage_limit_exceeded"
    PRICING_ERROR = "pricing_error"
    TRACKING_ERROR = "tracking_error"
    DATABASE_ERROR = "database_error"
    API_PROVIDER_ERROR = "api_provider_error"
    AUTHENTICATION_ERROR = "authentication_error"
    BILLING_ERROR = "billing_error"
    CONFIGURATION_ERROR = "configuration_error"

class SubscriptionErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SubscriptionException(Exception):
    """Base exception for subscription system errors."""
    
    def __init__(
        self,
        message: str,
        error_type: SubscriptionErrorType,
        severity: SubscriptionErrorSeverity = SubscriptionErrorSeverity.MEDIUM,
        user_id: str = None,
        provider: APIProvider = None,
        context: Dict[str, Any] = None,
        original_error: Exception = None
    ):
        self.message = message
        self.error_type = error_type
        self.severity = severity
        self.user_id = user_id
        self.provider = provider
        self.context = context or {}
        self.original_error = original_error
        self.timestamp = datetime.utcnow()
        
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/storage."""
        return {
            "message": self.message,
            "error_type": self.error_type.value,
            "severity": self.severity.value,
            "user_id": self.user_id,
            "provider": self.provider.value if self.provider else None,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "original_error": str(self.original_error) if self.original_error else None,
            "traceback": traceback.format_exc() if self.original_error else None
        }

class UsageLimitExceededException(SubscriptionException):
    """Exception raised when usage limits are exceeded."""
    
    def __init__(
        self,
        message: str,
        user_id: str,
        provider: APIProvider,
        limit_type: str,
        current_usage: Union[int, float],
        limit_value: Union[int, float],
        context: Dict[str, Any] = None
    ):
        context = context or {}
        context.update({
            "limit_type": limit_type,
            "current_usage": current_usage,
            "limit_value": limit_value,
            "usage_percentage": (current_usage / max(limit_value, 1)) * 100
        })
        
        super().__init__(
            message=message,
            error_type=SubscriptionErrorType.USAGE_LIMIT_EXCEEDED,
            severity=SubscriptionErrorSeverity.HIGH,
            user_id=user_id,
            provider=provider,
            context=context
        )

class PricingException(SubscriptionException):
    """Exception raised for pricing calculation errors."""
    
    def __init__(
        self,
        message: str,
        provider: APIProvider = None,
        model_name: str = None,
        context: Dict[str, Any] = None,
        original_error: Exception = None
    ):
        context = context or {}
        if model_name:
            context["model_name"] = model_name
        
        super().__init__(
            message=message,
            error_type=SubscriptionErrorType.PRICING_ERROR,
            severity=SubscriptionErrorSeverity.MEDIUM,
            provider=provider,
            context=context,
            original_error=original_error
        )

class TrackingException(SubscriptionException):
    """Exception raised for usage tracking errors."""
    
    def __init__(
        self,
        message: str,
        user_id: str = None,
        provider: APIProvider = None,
        context: Dict[str, Any] = None,
        original_error: Exception = None
    ):
        super().__init__(
            message=message,
            error_type=SubscriptionErrorType.TRACKING_ERROR,
            severity=SubscriptionErrorSeverity.MEDIUM,
            user_id=user_id,
            provider=provider,
            context=context,
            original_error=original_error
        )

class SubscriptionExceptionHandler:
    """Comprehensive exception handler for the subscription system."""
    
    def __init__(self, db: Session = None):
        self.db = db
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup structured logging for subscription errors."""
        # Configure loguru for subscription-specific logging
        logger.add(
            "logs/subscription_errors.log",
            rotation="1 day",
            retention="30 days",
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
            filter=lambda record: "subscription" in record["name"].lower()
        )
        
        logger.add(
            "logs/usage_tracking.log",
            rotation="1 day",
            retention="90 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            filter=lambda record: "usage_tracking" in str(record["message"]).lower()
        )
    
    def handle_exception(
        self,
        error: Union[Exception, SubscriptionException],
        context: Dict[str, Any] = None,
        log_level: str = "error"
    ) -> Dict[str, Any]:
        """Handle and log subscription system exceptions."""
        
        context = context or {}
        
        # Convert regular exceptions to SubscriptionException
        if not isinstance(error, SubscriptionException):
            error = SubscriptionException(
                message=str(error),
                error_type=self._classify_error(error),
                severity=self._determine_severity(error),
                context=context,
                original_error=error
            )
        
        # Log the error
        error_data = error.to_dict()
        error_data.update(context)
        
        log_message = f"Subscription Error: {error.message}"
        
        if log_level == "critical":
            logger.critical(log_message, extra={"error_data": error_data})
        elif log_level == "error":
            logger.error(log_message, extra={"error_data": error_data})
        elif log_level == "warning":
            logger.warning(log_message, extra={"error_data": error_data})
        else:
            logger.info(log_message, extra={"error_data": error_data})
        
        # Store critical errors in database for alerting
        if error.severity in [SubscriptionErrorSeverity.HIGH, SubscriptionErrorSeverity.CRITICAL]:
            self._store_error_alert(error)
        
        # Return formatted error response
        return self._format_error_response(error)
    
    def _classify_error(self, error: Exception) -> SubscriptionErrorType:
        """Classify an exception into a subscription error type."""
        
        error_str = str(error).lower()
        error_type_name = type(error).__name__.lower()
        
        if "limit" in error_str or "exceeded" in error_str:
            return SubscriptionErrorType.USAGE_LIMIT_EXCEEDED
        elif "pricing" in error_str or "cost" in error_str:
            return SubscriptionErrorType.PRICING_ERROR
        elif "tracking" in error_str or "usage" in error_str:
            return SubscriptionErrorType.TRACKING_ERROR
        elif "database" in error_str or "sql" in error_type_name:
            return SubscriptionErrorType.DATABASE_ERROR
        elif "api" in error_str or "provider" in error_str:
            return SubscriptionErrorType.API_PROVIDER_ERROR
        elif "auth" in error_str or "permission" in error_str:
            return SubscriptionErrorType.AUTHENTICATION_ERROR
        elif "billing" in error_str or "payment" in error_str:
            return SubscriptionErrorType.BILLING_ERROR
        else:
            return SubscriptionErrorType.CONFIGURATION_ERROR
    
    def _determine_severity(self, error: Exception) -> SubscriptionErrorSeverity:
        """Determine the severity of an error."""
        
        error_str = str(error).lower()
        error_type = type(error)
        
        # Critical errors
        if isinstance(error, (SQLAlchemyError, ConnectionError)):
            return SubscriptionErrorSeverity.CRITICAL
        
        # High severity errors
        if "limit exceeded" in error_str or "unauthorized" in error_str:
            return SubscriptionErrorSeverity.HIGH
        
        # Medium severity errors
        if "pricing" in error_str or "tracking" in error_str:
            return SubscriptionErrorSeverity.MEDIUM
        
        # Default to low
        return SubscriptionErrorSeverity.LOW
    
    def _store_error_alert(self, error: SubscriptionException):
        """Store critical errors as alerts in the database."""
        
        if not self.db or not error.user_id:
            return
        
        try:
            alert = UsageAlert(
                user_id=error.user_id,
                alert_type="system_error",
                threshold_percentage=0,
                provider=error.provider,
                title=f"System Error: {error.error_type.value}",
                message=error.message,
                severity=error.severity.value,
                billing_period=datetime.now().strftime("%Y-%m")
            )
            
            self.db.add(alert)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to store error alert: {e}")
    
    def _format_error_response(self, error: SubscriptionException) -> Dict[str, Any]:
        """Format error for API response."""
        
        response = {
            "success": False,
            "error": {
                "type": error.error_type.value,
                "message": error.message,
                "severity": error.severity.value,
                "timestamp": error.timestamp.isoformat()
            }
        }
        
        # Add context for debugging (non-sensitive info only)
        if error.context:
            safe_context = {
                k: v for k, v in error.context.items()
                if k not in ["password", "token", "key", "secret"]
            }
            response["error"]["context"] = safe_context
        
        # Add user-friendly message based on error type
        user_messages = {
            SubscriptionErrorType.USAGE_LIMIT_EXCEEDED: 
                "You have reached your usage limit. Please upgrade your plan or wait for the next billing cycle.",
            SubscriptionErrorType.PRICING_ERROR:
                "There was an issue calculating the cost for this request. Please try again.",
            SubscriptionErrorType.TRACKING_ERROR:
                "Unable to track usage for this request. Please contact support if this persists.",
            SubscriptionErrorType.DATABASE_ERROR:
                "A database error occurred. Please try again later.",
            SubscriptionErrorType.API_PROVIDER_ERROR:
                "There was an issue with the API provider. Please try again.",
            SubscriptionErrorType.AUTHENTICATION_ERROR:
                "Authentication failed. Please check your credentials.",
            SubscriptionErrorType.BILLING_ERROR:
                "There was a billing-related error. Please contact support.",
            SubscriptionErrorType.CONFIGURATION_ERROR:
                "System configuration error. Please contact support."
        }
        
        response["error"]["user_message"] = user_messages.get(
            error.error_type, 
            "An unexpected error occurred. Please try again or contact support."
        )
        
        return response

# Utility functions for common error scenarios
def handle_usage_limit_error(
    user_id: str,
    provider: APIProvider,
    limit_type: str,
    current_usage: Union[int, float],
    limit_value: Union[int, float],
    db: Session = None
) -> Dict[str, Any]:
    """Handle usage limit exceeded errors."""
    
    handler = SubscriptionExceptionHandler(db)
    error = UsageLimitExceededException(
        message=f"Usage limit exceeded for {limit_type}",
        user_id=user_id,
        provider=provider,
        limit_type=limit_type,
        current_usage=current_usage,
        limit_value=limit_value
    )
    
    return handler.handle_exception(error, log_level="warning")

def handle_pricing_error(
    message: str,
    provider: APIProvider = None,
    model_name: str = None,
    original_error: Exception = None,
    db: Session = None
) -> Dict[str, Any]:
    """Handle pricing calculation errors."""
    
    handler = SubscriptionExceptionHandler(db)
    error = PricingException(
        message=message,
        provider=provider,
        model_name=model_name,
        original_error=original_error
    )
    
    return handler.handle_exception(error)

def handle_tracking_error(
    message: str,
    user_id: str = None,
    provider: APIProvider = None,
    original_error: Exception = None,
    db: Session = None
) -> Dict[str, Any]:
    """Handle usage tracking errors."""
    
    handler = SubscriptionExceptionHandler(db)
    error = TrackingException(
        message=message,
        user_id=user_id,
        provider=provider,
        original_error=original_error
    )
    
    return handler.handle_exception(error)

def log_usage_event(
    user_id: str,
    provider: APIProvider,
    action: str,
    details: Dict[str, Any] = None
):
    """Log usage events for monitoring and debugging."""
    
    details = details or {}
    log_data = {
        "user_id": user_id,
        "provider": provider.value,
        "action": action,
        "timestamp": datetime.utcnow().isoformat(),
        **details
    }
    
    logger.info(f"Usage Tracking: {action}", extra={"usage_data": log_data})

# Decorator for automatic exception handling
def handle_subscription_errors(db: Session = None):
    """Decorator to automatically handle subscription-related exceptions."""
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except SubscriptionException as e:
                handler = SubscriptionExceptionHandler(db)
                return handler.handle_exception(e)
            except Exception as e:
                handler = SubscriptionExceptionHandler(db)
                return handler.handle_exception(e)
        
        return wrapper
    return decorator