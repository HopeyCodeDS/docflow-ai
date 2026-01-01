import time
import random
from typing import Callable, TypeVar, Optional
from functools import wraps

T = TypeVar('T')


class RetryableError(Exception):
    """Error that can be retried"""
    pass


class PermanentError(Exception):
    """Error that should not be retried"""
    pass


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Add random jitter to delay
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            delay = initial_delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except PermanentError as e:
                    # Don't retry permanent errors
                    raise
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        # Calculate delay with exponential backoff
                        if jitter:
                            # Add random jitter (0 to 25% of delay)
                            jitter_amount = delay * 0.25 * random.random()
                            actual_delay = delay + jitter_amount
                        else:
                            actual_delay = delay
                        
                        actual_delay = min(actual_delay, max_delay)
                        
                        time.sleep(actual_delay)
                        delay *= exponential_base
                    else:
                        # Max retries reached
                        raise RetryableError(f"Max retries ({max_retries}) exceeded") from last_exception
            
            # Should never reach here, but just in case
            raise last_exception
        
        return wrapper
    return decorator

