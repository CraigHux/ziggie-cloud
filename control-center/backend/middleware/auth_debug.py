"""
Authentication Debugging Middleware
Provides detailed logging and debugging capabilities for authentication flow.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

auth_logger = logging.getLogger("auth_debug")


class AuthenticationLogger:
    """Centralized authentication debugging logger."""

    @staticmethod
    def log_login_attempt(username: str, source_ip: str):
        """Log login attempt."""
        auth_logger.info(f"Login attempt - username: {username}, ip: {source_ip}")

    @staticmethod
    def log_login_success(username: str, user_id: int):
        """Log successful login."""
        auth_logger.info(f"Login successful - username: {username}, user_id: {user_id}")

    @staticmethod
    def log_login_failure(username: str, reason: str):
        """Log failed login."""
        auth_logger.warning(f"Login failed - username: {username}, reason: {reason}")

    @staticmethod
    def log_token_creation(username: str, user_id: int, token_preview: str):
        """Log token creation."""
        auth_logger.debug(f"Token created - username: {username}, user_id: {user_id}, token: {token_preview}...")

    @staticmethod
    def log_token_validation_attempt(token_preview: str):
        """Log token validation attempt."""
        auth_logger.debug(f"Validating token: {token_preview}...")

    @staticmethod
    def log_token_validation_success(username: str, user_id: int):
        """Log successful token validation."""
        auth_logger.info(f"Token validated successfully - username: {username}, user_id: {user_id}")

    @staticmethod
    def log_token_validation_failure(reason: str, token_preview: str = None):
        """Log token validation failure."""
        if token_preview:
            auth_logger.warning(f"Token validation failed - reason: {reason}, token: {token_preview}...")
        else:
            auth_logger.warning(f"Token validation failed - reason: {reason}")

    @staticmethod
    def log_bearer_header_parse(header_value: str, parsed_token: Optional[str]):
        """Log Bearer header parsing."""
        if parsed_token:
            auth_logger.debug(f"Bearer header parsed successfully: {parsed_token[:30]}...")
        else:
            auth_logger.warning(f"Failed to parse Bearer header: {header_value[:50]}...")

    @staticmethod
    def log_database_lookup(username: str, user_id: int, found: bool):
        """Log database user lookup."""
        status = "found" if found else "not found"
        auth_logger.debug(f"Database lookup - username: {username}, user_id: {user_id}, status: {status}")

    @staticmethod
    def log_user_inactive(username: str):
        """Log access by inactive user."""
        auth_logger.warning(f"Access attempt by inactive user: {username}")

    @staticmethod
    def log_config_validation(key: str, value: str, status: str):
        """Log configuration validation."""
        auth_logger.info(f"Config validation - {key}: {value[:30]}..., status: {status}")


class TokenDebugger:
    """Token debugging utilities."""

    @staticmethod
    def decode_token_payload(token: str) -> Optional[Dict[str, Any]]:
        """
        Decode JWT payload without verification for debugging.
        WARNING: This is for debugging only! Always verify tokens before trusting claims.
        """
        try:
            import base64
            import json

            parts = token.split(".")
            if len(parts) != 3:
                auth_logger.error(f"Invalid token format: expected 3 parts, got {len(parts)}")
                return None

            payload_str = parts[1]
            # Add padding if needed
            padding = 4 - (len(payload_str) % 4)
            if padding != 4:
                payload_str += "=" * padding

            payload_bytes = base64.urlsafe_b64decode(payload_str)
            payload = json.loads(payload_bytes)

            auth_logger.debug(f"Token payload decoded: {payload}")
            return payload

        except Exception as e:
            auth_logger.error(f"Error decoding token payload: {str(e)}")
            return None

    @staticmethod
    def log_token_details(token: str):
        """Log detailed token information."""
        parts = token.split(".")

        auth_logger.debug(f"Token Structure:")
        auth_logger.debug(f"  Parts: {len(parts)}")
        auth_logger.debug(f"  Header length: {len(parts[0])}")
        auth_logger.debug(f"  Payload length: {len(parts[1])}")
        auth_logger.debug(f"  Signature length: {len(parts[2]) if len(parts) > 2 else 0}")

        payload = TokenDebugger.decode_token_payload(token)
        if payload:
            auth_logger.debug(f"Token Claims:")
            for key, value in payload.items():
                if key == "exp":
                    from datetime import datetime
                    exp_time = datetime.utcfromtimestamp(value)
                    auth_logger.debug(f"  {key}: {exp_time} (timestamp: {value})")
                else:
                    auth_logger.debug(f"  {key}: {value}")


class AuthFlowTracer:
    """Trace authentication flow for debugging."""

    def __init__(self, trace_id: str = None):
        self.trace_id = trace_id or f"trace_{datetime.now().isoformat()}"
        self.events = []

    def add_event(self, event_name: str, details: Dict[str, Any] = None):
        """Add event to trace."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event": event_name,
            "details": details or {}
        }
        self.events.append(event)
        auth_logger.debug(f"[{self.trace_id}] {event_name}: {details}")

    def log_trace(self):
        """Log complete trace."""
        trace_log = {
            "trace_id": self.trace_id,
            "events": self.events
        }
        auth_logger.info(f"Authentication Trace: {json.dumps(trace_log, indent=2)}")

    def get_trace(self) -> Dict[str, Any]:
        """Get trace data."""
        return {
            "trace_id": self.trace_id,
            "events": self.events
        }


# Suggested debugging middleware integration for main.py
AUTHENTICATION_DEBUG_MIDDLEWARE = """
# Add this to main.py after creating the FastAPI app:

from middleware.auth_debug import AuthenticationLogger

# This creates a middleware that logs all authentication attempts
@app.middleware("http")
async def auth_debug_middleware(request: Request, call_next):
    # Log authentication headers
    auth_header = request.headers.get("Authorization", "")
    if auth_header:
        # Don't log the full token for security
        token_preview = auth_header[:30] + "..." if len(auth_header) > 30 else auth_header
        AuthenticationLogger.log_bearer_header_parse(auth_header, token_preview if auth_header.startswith("Bearer ") else None)

    response = await call_next(request)

    # Log response status for auth endpoints
    if "/api/auth/" in request.url.path:
        auth_logger.info(f"Auth endpoint response: {request.method} {request.url.path} -> {response.status_code}")

    return response
"""


# Patch for middleware/auth.py to add debugging
AUTH_PATCH_SUGGESTION = """
# Add these imports to middleware/auth.py:
from middleware.auth_debug import AuthenticationLogger, TokenDebugger, AuthFlowTracer

# Modify decode_access_token function to add debugging:
def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        # Debug: Log token details
        TokenDebugger.log_token_details(token)

        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        AuthenticationLogger.log_token_validation_success(
            payload.get("sub", "unknown"),
            payload.get("user_id", "unknown")
        )

        return payload
    except jwt.ExpiredSignatureError:
        AuthenticationLogger.log_token_validation_failure("Token expired", token[:30])
        raise HTTPException(...)
    except jwt.InvalidTokenError:
        AuthenticationLogger.log_token_validation_failure("Invalid token", token[:30])
        raise HTTPException(...)

# Modify get_current_user function to add debugging:
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    trace = AuthFlowTracer()

    try:
        token = credentials.credentials
        trace.add_event("token_received", {"token_preview": token[:30]})

        # Decode token
        payload = decode_access_token(token)
        trace.add_event("token_decoded", {"claims": list(payload.keys())})

        # Extract user information
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")

        trace.add_event("claims_extracted", {"username": username, "user_id": user_id})

        if username is None or user_id is None:
            trace.add_event("missing_claims", {"username": username, "user_id": user_id})
            trace.log_trace()
            raise HTTPException(...)

        # Fetch user from database
        result = await db.execute(
            select(User).where(User.id == user_id, User.username == username)
        )
        user = result.scalar_one_or_none()

        trace.add_event("database_lookup", {"found": user is not None})

        if user is None:
            trace.add_event("user_not_found", {"user_id": user_id, "username": username})
            trace.log_trace()
            AuthenticationLogger.log_database_lookup(username, user_id, False)
            raise HTTPException(...)

        trace.add_event("user_found", {"username": user.username})

        # Check active status
        if not user.is_active:
            trace.add_event("user_inactive")
            trace.log_trace()
            AuthenticationLogger.log_user_inactive(username)
            raise HTTPException(...)

        trace.add_event("authentication_success")
        trace.log_trace()
        AuthenticationLogger.log_token_validation_success(username, user_id)

        return user

    except HTTPException:
        trace.log_trace()
        raise
    except Exception as e:
        trace.add_event("unexpected_error", {"error": str(e)})
        trace.log_trace()
        raise
"""

if __name__ == "__main__":
    # Print debugging setup instructions
    print("Authentication Debugging Module")
    print("=" * 60)
    print("\nTo enable detailed authentication logging:")
    print("\n1. Add to middleware/auth.py:")
    print(AUTH_PATCH_SUGGESTION)
    print("\n2. Add to main.py:")
    print(AUTHENTICATION_DEBUG_MIDDLEWARE)
    print("\n3. Configure logging in main.py startup:")
    print("   from middleware.auth_debug import auth_logger")
