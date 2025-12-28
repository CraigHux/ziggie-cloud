"""
Debug middleware for authentication troubleshooting.
Add this to main.py to log all authentication attempts.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auth_debug")


class AuthDebugMiddleware(BaseHTTPMiddleware):
    """Middleware to debug authentication issues."""

    async def dispatch(self, request: Request, call_next):
        # Only log for protected endpoints
        if request.url.path.startswith("/api/auth/") and request.url.path != "/api/auth/login":
            logger.info("=" * 80)
            logger.info(f"AUTH DEBUG - {datetime.now().isoformat()}")
            logger.info(f"Path: {request.url.path}")
            logger.info(f"Method: {request.method}")

            # Log Authorization header
            auth_header = request.headers.get("Authorization")
            if auth_header:
                if auth_header.startswith("Bearer "):
                    token = auth_header[7:]
                    logger.info(f"Authorization Header: Bearer <token>")
                    logger.info(f"Token (first 20 chars): {token[:20]}...")
                    logger.info(f"Token length: {len(token)} chars")

                    # Check for common mistakes
                    if token.startswith("Bearer "):
                        logger.warning("⚠️  DOUBLE 'Bearer' PREFIX DETECTED!")
                        logger.warning("Token appears to already contain 'Bearer '")
                    if " " in token:
                        logger.warning("⚠️  SPACE DETECTED IN TOKEN!")
                        logger.warning("Token may contain whitespace")
                else:
                    logger.warning(f"⚠️  INCORRECT AUTH SCHEME: {auth_header[:20]}...")
                    logger.warning("Expected format: 'Bearer <token>'")
            else:
                logger.warning("⚠️  NO AUTHORIZATION HEADER FOUND")

            # Log all headers (sanitized)
            logger.info("All Headers:")
            for key, value in request.headers.items():
                if key.lower() == "authorization":
                    logger.info(f"  {key}: Bearer <redacted>")
                else:
                    logger.info(f"  {key}: {value}")

        # Process request
        response = await call_next(request)

        # Log response status for auth endpoints
        if request.url.path.startswith("/api/auth/") and request.url.path != "/api/auth/login":
            logger.info(f"Response Status: {response.status_code}")
            if response.status_code == 403:
                logger.error("❌ 403 FORBIDDEN - Check Authorization header format")
            elif response.status_code == 401:
                logger.error("❌ 401 UNAUTHORIZED - Token invalid or expired")
            elif response.status_code == 200:
                logger.info("✅ Authentication successful")
            logger.info("=" * 80)

        return response


# To enable this middleware, add to main.py:
# from middleware.auth_debug_middleware import AuthDebugMiddleware
# app.add_middleware(AuthDebugMiddleware)
