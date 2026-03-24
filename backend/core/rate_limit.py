"""
Ooumph Rate Limiting Configuration
Protect API endpoints from abuse and DDoS attacks
"""
from fastapi import Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)


def get_identifier(request: Request) -> str:
    """
    Get unique identifier for rate limiting.
    Uses user ID if authenticated, otherwise IP address.
    """
    # Try to get user from token
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # For authenticated users, rate limit by user
            # This requires token validation - for now use IP
            pass
    except Exception:
        pass

    # Fall back to IP address
    return get_remote_address(request)


# Create rate limiter instance
limiter = Limiter(
    key_func=get_identifier,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
    storage_uri=settings.REDIS_URL if settings.RATE_LIMIT_ENABLED else "memory://",
    enabled=settings.RATE_LIMIT_ENABLED
)


async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom handler for rate limit exceeded errors.
    Returns a user-friendly error message.
    """
    logger.warning(
        f"Rate limit exceeded for {request.client.host}",
        extra={"path": request.url.path, "method": request.method}
    )

    raise HTTPException(
        status_code=429,
        detail={
            "error": "Rate limit exceeded",
            "message": f"Too many requests. Maximum {settings.RATE_LIMIT_PER_MINUTE} requests per minute allowed.",
            "retry_after": 60  # Suggest retry after 1 minute
        }
    )


# Rate limit decorators for common endpoints
def rate_limit_auth():
    """Stricter rate limiting for auth endpoints"""
    return limiter.limit("5/minute")


def rate_limit_api():
    """Standard rate limiting for API endpoints"""
    return limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")


def rate_limit_upload():
    """Very strict rate limiting for file uploads"""
    return limiter.limit("10/minute")
