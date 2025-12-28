"""Rate limiting middleware using SlowAPI."""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Create limiter instance with IP-based rate limiting
limiter = Limiter(key_func=get_remote_address)

__all__ = ["limiter", "RateLimitExceeded", "_rate_limit_exceeded_handler"]
