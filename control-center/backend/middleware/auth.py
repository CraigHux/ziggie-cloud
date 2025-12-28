"""
JWT Authentication Middleware
Provides JWT token creation, verification, and authentication dependencies.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import bcrypt
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from config import settings
from database import get_db
from database.models import User


# Security scheme
# auto_error=False allows manual 401 handling (semantic correctness)
# 401 = authentication required/failed, 403 = authenticated but forbidden
security = HTTPBearer(auto_error=False)


# Pydantic models for request/response
class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours in seconds


class TokenData(BaseModel):
    """Token payload data model."""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


class UserResponse(BaseModel):
    """User response model (without password)."""
    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


# Password hashing utilities
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


# JWT token utilities
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary of claims to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)  # Default 24 hours

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify a JWT access token.

    Args:
        token: JWT token string

    Returns:
        Dictionary of decoded claims

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Authentication dependencies
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user.

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: If authentication fails (401) or forbidden (403)
    """
    # Handle missing Authorization header with 401 (not 403)
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # Decode token
    payload = decode_access_token(token)

    # Extract user information
    username: str = payload.get("sub")
    user_id: int = payload.get("user_id")

    if username is None or user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    result = await db.execute(
        select(User).where(User.id == user_id, User.username == username)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get the current active user.
    Alias for get_current_user for clarity.
    """
    return current_user


# Role-based access control dependencies
class RoleChecker:
    """Dependency class for role-based access control."""

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, user: User = Depends(get_current_user)) -> User:
        """
        Check if user has required role.

        Args:
            user: Current authenticated user

        Returns:
            User object if authorized

        Raises:
            HTTPException: If user doesn't have required role
        """
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(self.allowed_roles)}"
            )
        return user


# Specific role dependencies
require_admin = RoleChecker(["admin"])
require_user = RoleChecker(["admin", "user"])
require_readonly = RoleChecker(["admin", "user", "readonly"])


# WebSocket authentication
async def verify_websocket_token(token: str, db: AsyncSession) -> Optional[User]:
    """
    Verify WebSocket connection token.

    Args:
        token: JWT token from WebSocket query params
        db: Database session

    Returns:
        User object if valid, None if invalid
    """
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")

        if username is None or user_id is None:
            return None

        result = await db.execute(
            select(User).where(User.id == user_id, User.username == username)
        )
        user = result.scalar_one_or_none()

        if user and user.is_active:
            return user

        return None
    except Exception:
        return None


# Optional authentication (for public endpoints that want user context)
async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication dependency.
    Returns user if authenticated, None otherwise.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None

    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")

        if username is None or user_id is None:
            return None

        result = await db.execute(
            select(User).where(User.id == user_id, User.username == username)
        )
        user = result.scalar_one_or_none()

        if user and user.is_active:
            return user

        return None
    except Exception:
        return None

