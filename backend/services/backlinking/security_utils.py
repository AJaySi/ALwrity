"""
Security utilities for the AI Backlinking service.

Provides input sanitization, security validation, and protection
against common web vulnerabilities.
"""

import re
import html
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urlparse, urljoin, quote
from loguru import logger

from .config import get_config
from .exceptions import ValidationError


class InputSanitizer:
    """
    Input sanitization utilities for user data validation and cleaning.
    """

    # Dangerous HTML tags that should be removed
    DANGEROUS_HTML_TAGS = [
        'script', 'iframe', 'object', 'embed', 'form', 'input', 'button',
        'link', 'meta', 'style', 'javascript', 'vbscript', 'onload', 'onerror',
        'onclick', 'onmouseover', 'onsubmit'
    ]

    # SQL injection patterns to detect
    SQL_INJECTION_PATTERNS = [
        r';\s*(select|insert|update|delete|drop|create|alter)\s',
        r'union\s+select',
        r'--\s*$',
        r'#\s*$',
        r'/\*.*\*/',
        r';\s*$',
    ]

    # XSS attack patterns
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
    ]

    @staticmethod
    def sanitize_text_input(text: str, max_length: int = 10000) -> str:
        """
        Sanitize text input by removing dangerous content.

        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized text
        """
        if not text:
            return ""

        # Convert to string if not already
        text = str(text)

        # Remove null bytes and control characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)

        # Escape HTML entities
        text = html.escape(text, quote=True)

        # Remove dangerous HTML tags
        for tag in InputSanitizer.DANGEROUS_HTML_TAGS:
            pattern = f'<{tag}[^>]*>.*?</{tag}>'
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
            # Also remove self-closing tags
            pattern = f'<{tag}[^>]*/?>'
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # Check for SQL injection patterns
        for pattern in InputSanitizer.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning("Potential SQL injection detected in input")
                raise ValidationError("text", text, "Invalid input detected")

        # Check for XSS patterns
        for pattern in InputSanitizer.XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning("Potential XSS attack detected in input")
                raise ValidationError("text", text, "Invalid input detected")

        # Trim whitespace and limit length
        text = text.strip()
        if len(text) > max_length:
            text = text[:max_length - 3] + "..."

        return text

    @staticmethod
    def sanitize_email(email: str) -> str:
        """
        Sanitize email address input.

        Args:
            email: Email address to sanitize

        Returns:
            Sanitized email address

        Raises:
            ValidationError: If email appears malicious
        """
        if not email:
            return ""

        email = str(email).strip().lower()

        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("email", email, "Invalid email format")

        # Check for suspicious patterns
        suspicious_patterns = [
            r'[<>]',  # HTML tags
            r'[\x00-\x1f\x7f-\x9f]',  # Control characters
            r'javascript:',  # JavaScript URLs
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, email):
                logger.warning(f"Potentially malicious email detected: {email}")
                raise ValidationError("email", email, "Invalid email format")

        return email

    @staticmethod
    def sanitize_url(url: str, allowed_domains: Optional[List[str]] = None) -> str:
        """
        Sanitize URL input and validate it.

        Args:
            url: URL to sanitize
            allowed_domains: List of allowed domains (optional)

        Returns:
            Sanitized URL

        Raises:
            ValidationError: If URL is invalid or not allowed
        """
        if not url:
            return ""

        url = str(url).strip()

        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        try:
            parsed = urlparse(url)

            # Validate URL structure
            if not parsed.netloc:
                raise ValidationError("url", url, "Invalid URL format")

            # Check domain against whitelist if provided
            if allowed_domains:
                domain = parsed.netloc.lower()
                if not any(domain.endswith(allowed_domain.lower()) for allowed_domain in allowed_domains):
                    raise ValidationError("url", url, "Domain not allowed")

            # Remove potentially dangerous characters
            clean_url = parsed.scheme + '://' + parsed.netloc + quote(parsed.path)
            if parsed.query:
                clean_url += '?' + quote(parsed.query, safe='=&')
            if parsed.fragment:
                clean_url += '#' + quote(parsed.fragment)

            return clean_url

        except Exception as e:
            raise ValidationError("url", url, f"Invalid URL: {str(e)}")

    @staticmethod
    def sanitize_keywords(keywords: List[str]) -> List[str]:
        """
        Sanitize a list of keywords.

        Args:
            keywords: List of keywords to sanitize

        Returns:
            List of sanitized keywords
        """
        if not keywords:
            return []

        sanitized = []
        for keyword in keywords:
            # Sanitize each keyword
            clean_keyword = InputSanitizer.sanitize_text_input(keyword, max_length=100)

            # Remove special characters that could be used for injection
            clean_keyword = re.sub(r'[;"\'\\<>]', '', clean_keyword)

            if clean_keyword and len(clean_keyword) >= 2:  # Minimum keyword length
                sanitized.append(clean_keyword)

        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in sanitized:
            lower_keyword = keyword.lower()
            if lower_keyword not in seen:
                seen.add(lower_keyword)
                unique_keywords.append(keyword)

        return unique_keywords[:50]  # Limit to 50 keywords max


class SecurityValidator:
    """
    Security validation utilities for API requests and data processing.
    """

    def __init__(self):
        self.config = get_config()

    def validate_request_rate(self, user_id: str, action: str, max_requests: int = 10) -> bool:
        """
        Validate request rate for rate limiting.

        Args:
            user_id: User identifier
            action: Action being performed
            max_requests: Maximum requests allowed

        Returns:
            True if request is allowed, False if rate limited
        """
        # This is a basic implementation - in production, use Redis or similar
        # For now, we'll just log and allow all requests
        logger.info(f"Rate limit check for user {user_id}, action: {action}")
        return True

    def validate_api_key(self, api_key: str) -> bool:
        """
        Validate API key format and security.

        Args:
            api_key: API key to validate

        Returns:
            True if valid, False otherwise
        """
        if not api_key or len(api_key) < 10:
            return False

        # Check for suspicious patterns
        suspicious_patterns = [
            r'[<>]',  # HTML tags
            r'[\x00-\x1f\x7f-\x9f]',  # Control characters
            r'javascript:',  # JavaScript
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, api_key):
                return False

        return True

    def sanitize_request_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize all data in a request payload.

        Args:
            data: Request data dictionary

        Returns:
            Sanitized data dictionary
        """
        sanitized = {}

        for key, value in data.items():
            if isinstance(value, str):
                if key.lower().endswith(('email', '_email')):
                    sanitized[key] = InputSanitizer.sanitize_email(value)
                elif key.lower().endswith(('url', '_url')):
                    sanitized[key] = InputSanitizer.sanitize_url(value)
                elif key.lower() in ['name', 'title', 'topic']:
                    sanitized[key] = InputSanitizer.sanitize_text_input(value, max_length=500)
                else:
                    sanitized[key] = InputSanitizer.sanitize_text_input(value)
            elif isinstance(value, list):
                if key.lower().endswith('keywords'):
                    sanitized[key] = InputSanitizer.sanitize_keywords(value)
                else:
                    # Sanitize list items if they are strings
                    sanitized[key] = [
                        InputSanitizer.sanitize_text_input(item) if isinstance(item, str) else item
                        for item in value
                    ]
            elif isinstance(value, dict):
                # Recursively sanitize nested dictionaries
                sanitized[key] = self.sanitize_request_data(value)
            else:
                # Keep non-string values as-is
                sanitized[key] = value

        return sanitized


class ContentSecurity:
    """
    Content security utilities for processing and validating content.
    """

    @staticmethod
    def validate_content_safety(content: str) -> Dict[str, Any]:
        """
        Validate content for safety and appropriateness.

        Args:
            content: Content to validate

        Returns:
            Validation results with safety score and issues
        """
        issues = []
        safety_score = 100

        # Check for inappropriate content patterns
        inappropriate_patterns = [
            r'\bspam\b',
            r'\bviagra\b',
            r'\bcasino\b',
            r'\bloan\b.*\bapproval\b',
            r'\bmake\s+money\s+fast\b',
        ]

        content_lower = content.lower()
        for pattern in inappropriate_patterns:
            if re.search(pattern, content_lower):
                issues.append(f"Potentially inappropriate content detected: {pattern}")
                safety_score -= 20

        # Check content length
        if len(content) < 10:
            issues.append("Content too short")
            safety_score -= 10

        if len(content) > 10000:
            issues.append("Content too long")
            safety_score = max(safety_score - 10, 0)

        # Check for excessive caps
        caps_ratio = sum(1 for c in content if c.isupper()) / len(content) if content else 0
        if caps_ratio > 0.3:
            issues.append("Excessive use of capital letters")
            safety_score -= 5

        return {
            "is_safe": safety_score >= 70,
            "safety_score": max(safety_score, 0),
            "issues": issues
        }

    @staticmethod
    def sanitize_generated_content(content: str) -> str:
        """
        Sanitize AI-generated content for safety.

        Args:
            content: Generated content to sanitize

        Returns:
            Sanitized content
        """
        if not content:
            return ""

        # Remove any remaining script tags or dangerous content
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'on\w+\s*=', '', content, flags=re.IGNORECASE)

        # Ensure proper encoding
        try:
            content = content.encode('utf-8').decode('utf-8')
        except UnicodeError:
            content = content.encode('utf-8', errors='ignore').decode('utf-8')

        return content.strip()


# Global instances for easy access
input_sanitizer = InputSanitizer()
security_validator = SecurityValidator()
content_security = ContentSecurity()


def sanitize_user_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to sanitize user input data.

    Args:
        data: User input data

    Returns:
        Sanitized data
    """
    return security_validator.sanitize_request_data(data)


def validate_content_for_email(content: str) -> bool:
    """
    Validate content safety for email sending.

    Args:
        content: Content to validate

    Returns:
        True if safe to send, False otherwise
    """
    validation = content_security.validate_content_safety(content)
    if not validation["is_safe"]:
        logger.warning(
            "Unsafe content detected for email",
            safety_score=validation["safety_score"],
            issues=validation["issues"]
        )
    return validation["is_safe"]