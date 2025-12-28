"""
Authentication API Endpoints
Handles user login, registration, and token management.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, EmailStr, Field

from database import get_db
from database.models import User
from middleware.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_active_user,
    require_admin,
    Token,
    UserResponse
)
from middleware.rate_limit import limiter
from utils.errors import UserFriendlyError


router = APIRouter(prefix="/api/auth", tags=["authentication"])


# Request/Response Models
class LoginRequest(BaseModel):
    """Login request model."""
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    """User registration request model."""
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=255)
    role: str = Field(default="user", pattern="^(admin|user|readonly)$")


class ChangePasswordRequest(BaseModel):
    """Password change request model."""
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)


class UpdateUserRequest(BaseModel):
    """User update request model."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=255)
    role: Optional[str] = Field(None, pattern="^(admin|user|readonly)$")
    is_active: Optional[bool] = None


# Authentication Endpoints
@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    User login endpoint.

    Returns JWT access token on successful authentication.
    """
    try:
        # Find user by username
        result = await db.execute(
            select(User).where(User.username == login_data.username)
        )
        user = result.scalar_one_or_none()

        # Verify user exists and password is correct
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        # Update last login timestamp
        user.last_login = datetime.utcnow()
        await db.commit()

        # Create access token
        access_token = create_access_token(
            data={
                "sub": user.username,
                "user_id": user.id,
                "role": user.role
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 86400  # 24 hours
        }

    except HTTPException:
        raise
    except Exception as e:
        UserFriendlyError.handle_error(e, context="logging in", status_code=500)


@router.post("/login/form", response_model=Token)
@limiter.limit("10/minute")
async def login_form(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2 compatible login endpoint (form data).

    This endpoint accepts form-encoded data for OAuth2 compatibility.
    """
    try:
        # Find user by username
        result = await db.execute(
            select(User).where(User.username == form_data.username)
        )
        user = result.scalar_one_or_none()

        # Verify credentials
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        # Update last login
        user.last_login = datetime.utcnow()
        await db.commit()

        # Create token
        access_token = create_access_token(
            data={
                "sub": user.username,
                "user_id": user.id,
                "role": user.role
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 86400
        }

    except HTTPException:
        raise
    except Exception as e:
        UserFriendlyError.handle_error(e, context="logging in", status_code=500)


@router.post("/register", response_model=UserResponse)
@limiter.limit("5/hour")
async def register(
    request: Request,
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)  # Only admins can create users
):
    """
    Register a new user.

    Requires admin authentication. Only admins can create new users.
    """
    try:
        # Check if username already exists
        result = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Check if email already exists (if provided)
        if user_data.email:
            result = await db.execute(
                select(User).where(User.email == user_data.email)
            )
            existing_email = result.scalar_one_or_none()

            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

        # Create new user
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hash_password(user_data.password),
            role=user_data.role,
            is_active=True
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user

    except HTTPException:
        raise
    except Exception as e:
        UserFriendlyError.handle_error(e, context="registering user", status_code=500)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
@limiter.limit("10/minute")
async def update_current_user(
    request: Request,
    update_data: UpdateUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update current user's information.

    Users can only update their own email and full_name.
    Role and is_active changes require admin privileges.
    """
    try:
        # Check if trying to modify role or is_active (requires admin)
        if (update_data.role is not None or update_data.is_active is not None) and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can modify role or account status"
            )

        # Update fields
        if update_data.email is not None:
            # Check if email is already taken
            result = await db.execute(
                select(User).where(User.email == update_data.email, User.id != current_user.id)
            )
            existing = result.scalar_one_or_none()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            current_user.email = update_data.email

        if update_data.full_name is not None:
            current_user.full_name = update_data.full_name

        if update_data.role is not None and current_user.role == "admin":
            current_user.role = update_data.role

        if update_data.is_active is not None and current_user.role == "admin":
            current_user.is_active = update_data.is_active

        await db.commit()
        await db.refresh(current_user)

        return current_user

    except HTTPException:
        raise
    except Exception as e:
        UserFriendlyError.handle_error(e, context="updating user", status_code=500)


@router.post("/change-password")
@limiter.limit("5/hour")
async def change_password(
    request: Request,
    password_data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Change current user's password.
    """
    try:
        # Verify current password
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )

        # Update password
        current_user.hashed_password = hash_password(password_data.new_password)
        await db.commit()

        return {
            "success": True,
            "message": "Password changed successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        UserFriendlyError.handle_error(e, context="changing password", status_code=500)


# Admin-only user management endpoints
@router.get("/users", response_model=list[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    List all users (admin only).
    """
    try:
        result = await db.execute(select(User).order_by(User.created_at.desc()))
        users = result.scalars().all()
        return users

    except Exception as e:
        UserFriendlyError.handle_error(e, context="listing users", status_code=500)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get user by ID (admin only).
    """
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        UserFriendlyError.handle_error(e, context="retrieving user", status_code=500)


@router.put("/users/{user_id}", response_model=UserResponse)
@limiter.limit("10/minute")
async def update_user(
    request: Request,
    user_id: int,
    update_data: UpdateUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update user by ID (admin only).
    """
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Update fields
        if update_data.email is not None:
            result = await db.execute(
                select(User).where(User.email == update_data.email, User.id != user_id)
            )
            existing = result.scalar_one_or_none()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            user.email = update_data.email

        if update_data.full_name is not None:
            user.full_name = update_data.full_name

        if update_data.role is not None:
            user.role = update_data.role

        if update_data.is_active is not None:
            user.is_active = update_data.is_active

        await db.commit()
        await db.refresh(user)

        return user

    except HTTPException:
        raise
    except Exception as e:
        UserFriendlyError.handle_error(e, context="updating user", status_code=500)


@router.delete("/users/{user_id}")
@limiter.limit("5/hour")
async def delete_user(
    request: Request,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete user by ID (admin only).

    Note: Cannot delete your own account.
    """
    try:
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        await db.delete(user)
        await db.commit()

        return {
            "success": True,
            "message": f"User '{user.username}' deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        UserFriendlyError.handle_error(e, context="deleting user", status_code=500)


@router.get("/stats")
async def get_auth_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get authentication statistics (admin only).
    """
    try:
        # Count total users
        total_users_result = await db.execute(select(func.count(User.id)))
        total_users = total_users_result.scalar()

        # Count active users
        active_users_result = await db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        active_users = active_users_result.scalar()

        # Count by role
        admin_count_result = await db.execute(
            select(func.count(User.id)).where(User.role == "admin")
        )
        admin_count = admin_count_result.scalar()

        user_count_result = await db.execute(
            select(func.count(User.id)).where(User.role == "user")
        )
        user_count = user_count_result.scalar()

        readonly_count_result = await db.execute(
            select(func.count(User.id)).where(User.role == "readonly")
        )
        readonly_count = readonly_count_result.scalar()

        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "by_role": {
                "admin": admin_count,
                "user": user_count,
                "readonly": readonly_count
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        UserFriendlyError.handle_error(e, context="retrieving auth statistics", status_code=500)
