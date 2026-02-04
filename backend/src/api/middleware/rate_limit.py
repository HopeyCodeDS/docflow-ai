"""
Rate limiting middleware for protecting auth endpoints from brute force attacks.
"""
from fastapi import Request, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio


class RateLimiter:
    """
    In-memory rate limiter using sliding window algorithm.

    For production, consider using Redis-based rate limiting for
    distributed deployments.
    """

    def __init__(self, requests_per_minute: int = 5):
        self.requests_per_minute = requests_per_minute
        self.requests: dict[str, list[datetime]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check(self, key: str) -> None:
        """
        Check if the request should be rate limited.

        Args:
            key: Unique identifier for the client (e.g., IP address)

        Raises:
            HTTPException: 429 Too Many Requests if rate limit exceeded
        """
        async with self._lock:
            now = datetime.utcnow()
            minute_ago = now - timedelta(minutes=1)

            # Clean old requests outside the sliding window
            self.requests[key] = [t for t in self.requests[key] if t > minute_ago]

            if len(self.requests[key]) >= self.requests_per_minute:
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later."
                )

            self.requests[key].append(now)


# Global rate limiter instances
login_limiter = RateLimiter(requests_per_minute=5)
refresh_limiter = RateLimiter(requests_per_minute=10)


async def rate_limit_login(request: Request) -> None:
    """
    FastAPI dependency for rate limiting login attempts.
    Limits to 5 requests per minute per IP address.
    """
    client_ip = request.client.host if request.client else "unknown"
    await login_limiter.check(client_ip)


async def rate_limit_refresh(request: Request) -> None:
    """
    FastAPI dependency for rate limiting token refresh attempts.
    Limits to 10 requests per minute per IP address.
    """
    client_ip = request.client.host if request.client else "unknown"
    await refresh_limiter.check(client_ip)
