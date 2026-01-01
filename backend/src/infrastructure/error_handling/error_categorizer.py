from typing import Tuple
from ..error_handling.retry import RetryableError, PermanentError


class ErrorCategorizer:
    """Categorize errors into retryable vs permanent"""
    
    @staticmethod
    def categorize(error: Exception) -> Tuple[bool, str]:
        """
        Categorize error.
        
        Returns:
            Tuple of (is_retryable, error_category)
        """
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # Network-related errors are usually retryable
        if any(keyword in error_type.lower() for keyword in ['connection', 'timeout', 'network']):
            return True, "network_error"
        
        if any(keyword in error_message for keyword in ['connection', 'timeout', 'network', 'temporary']):
            return True, "network_error"
        
        # Rate limiting is retryable
        if any(keyword in error_message for keyword in ['rate limit', 'too many requests', '429']):
            return True, "rate_limit"
        
        # Authentication errors are usually permanent (unless token expired)
        if any(keyword in error_type.lower() for keyword in ['auth', 'unauthorized', 'forbidden']):
            if 'expired' in error_message or 'token' in error_message:
                return True, "auth_token_expired"
            return False, "authentication_error"
        
        # Validation errors are permanent
        if any(keyword in error_type.lower() for keyword in ['validation', 'value', 'invalid']):
            return False, "validation_error"
        
        # File format errors are permanent
        if any(keyword in error_message for keyword in ['format', 'invalid file', 'unsupported']):
            return False, "file_format_error"
        
        # Default: assume retryable for unknown errors
        return True, "unknown_error"
    
    @staticmethod
    def should_retry(error: Exception) -> bool:
        """Determine if error should be retried"""
        is_retryable, _ = ErrorCategorizer.categorize(error)
        return is_retryable
    
    @staticmethod
    def raise_appropriate_error(error: Exception) -> None:
        """Raise appropriate error type based on categorization"""
        is_retryable, category = ErrorCategorizer.categorize(error)
        
        if is_retryable:
            raise RetryableError(f"[{category}] {str(error)}") from error
        else:
            raise PermanentError(f"[{category}] {str(error)}") from error

