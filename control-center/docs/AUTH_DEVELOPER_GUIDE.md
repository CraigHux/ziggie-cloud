# Authentication Developer Guide
## Ziggie Control Center

**Version:** 1.0.0
**Last Updated:** 2025-11-10
**Target Audience:** Backend Developers, Frontend Developers, DevOps Engineers

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [JWT Token Flow](#jwt-token-flow)
3. [Backend Implementation](#backend-implementation)
4. [Frontend Implementation](#frontend-implementation)
5. [Integration Examples](#integration-examples)
6. [API Endpoints](#api-endpoints)
7. [Security Architecture](#security-architecture)
8. [Error Handling](#error-handling)
9. [Testing Guide](#testing-guide)
10. [Deployment Considerations](#deployment-considerations)

---

## Architecture Overview

### System Components

The Ziggie Control Center authentication system consists of:

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  LoginPage Component                                 │   │
│  │  ├─ AuthContext (Global State)                       │   │
│  │  ├─ useAuth Hook (Custom Hook)                       │   │
│  │  └─ Protected Routes (Route Guards)                  │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                ┌──────────┴───────────┐
                │ HTTP/HTTPS Requests │
                │ JWT Authorization   │
                └──────────┬───────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                  Backend (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  API Routes (/api/auth/*)                            │   │
│  │  ├─ login                                            │   │
│  │  ├─ register                                         │   │
│  │  ├─ me (get current user)                            │   │
│  │  ├─ users (admin only)                               │   │
│  │  └─ change-password                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Middleware Layer (middleware/auth.py)               │   │
│  │  ├─ Password Hashing (bcrypt)                        │   │
│  │  ├─ JWT Token Creation                               │   │
│  │  ├─ Token Validation                                 │   │
│  │  └─ Authentication Dependencies                      │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Database Layer (SQLAlchemy)                         │   │
│  │  ├─ User Model                                       │   │
│  │  ├─ Password Hashing                                 │   │
│  │  └─ User Queries                                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Backend** | FastAPI | ^0.100 | REST API framework |
| **Auth** | JWT (PyJWT) | ^2.8 | Token-based authentication |
| **Hashing** | bcrypt | ^4.0 | Password hashing |
| **Database ORM** | SQLAlchemy | ^2.0 | Database queries |
| **Frontend** | React | ^18.0 | UI framework |
| **HTTP Client** | Axios | ^1.4 | HTTP requests |
| **Routing** | React Router | ^6.0 | Client-side routing |
| **UI Library** | Material-UI | ^5.0 | Component library |

---

## JWT Token Flow

### Complete Authentication Flow

#### 1. Login Request

**User Action:** User submits login form with credentials

```
Frontend Request:
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Backend Processing:**
```python
# 1. Look up user by username
user = db.query(User).filter(User.username == "admin").first()

# 2. Verify password using bcrypt
if not bcrypt.checkpw(password.encode(), user.hashed_password.encode()):
    raise HTTPException(401, "Incorrect credentials")

# 3. Update last login timestamp
user.last_login = datetime.utcnow()
db.commit()

# 4. Generate JWT token with user claims
access_token = create_access_token({
    "sub": user.username,
    "user_id": user.id,
    "role": user.role
})

# 5. Return token to frontend
return {
    "access_token": access_token,
    "token_type": "bearer",
    "expires_in": 86400  # 24 hours in seconds
}
```

#### 2. Token Storage

**Frontend Action:** Store token for subsequent requests

```javascript
// Store token in localStorage
localStorage.setItem('access_token', response.access_token);

// Store user info
localStorage.setItem('user', JSON.stringify(userData));

// Update React Context
setUser(userData);
```

#### 3. Authenticated Requests

**For subsequent API calls:**

```javascript
// Axios interceptor automatically adds Authorization header
const response = await axios.get('/api/agents', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});
```

**Backend Validation:**

```python
# Middleware extracts and validates token
token = extract_token_from_header(request)
payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

# Verify user still exists and is active
user = db.query(User).filter(User.id == payload['user_id']).first()
if not user or not user.is_active:
    raise HTTPException(401, "User not found or inactive")

# Inject user into endpoint
return user
```

#### 4. Token Expiration

**After 24 hours:**
- Token becomes invalid
- User receives 401 Unauthorized
- Frontend automatically redirects to login
- User must log in again

### JWT Token Structure

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjEsInJvbGUiOiJhZG1pbiIsImV4cCI6MTczMDM5Mzc4MCwiaWF0IjoxNzMwMzA3MzgwLCJ0eXBlIjoiYWNjZXNzIn0.
abc123xyz...
```

**Header (Base64):**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload (Base64):**
```json
{
  "sub": "admin",              // username (subject claim)
  "user_id": 1,               // user database ID
  "role": "admin",            // user role
  "exp": 1730393780,         // expiration timestamp
  "iat": 1730307380,         // issued-at timestamp
  "type": "access"           // token type
}
```

**Signature (HMAC-SHA256):**
```
HMACSHA256(
  Base64URL(header) + "." + Base64URL(payload),
  JWT_SECRET
)
```

---

## Backend Implementation

### Configuration (config.py)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # JWT Configuration
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Database
    DATABASE_URL: str = "sqlite:///./control_center.db"

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ]

    class Config:
        env_file = ".env"

settings = Settings()
```

### User Model (database/models.py)

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user")  # admin, user, readonly
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
```

### Authentication Middleware (middleware/auth.py)

```python
from datetime import datetime, timedelta
import jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class AuthUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password with bcrypt."""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()

        expire = datetime.utcnow() + (
            expires_delta or timedelta(hours=24)
        )

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

    @staticmethod
    def decode_access_token(token: str) -> dict:
        """Decode and validate JWT token."""
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
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

# Security dependencies
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    token = credentials.credentials
    payload = AuthUtils.decode_access_token(token)

    user = await db.query(User).filter(
        User.id == payload.get("user_id")
    ).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
```

### Authentication Endpoints (api/auth.py)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/auth", tags=["authentication"])

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return JWT token."""
    # Query user
    result = await db.execute(
        select(User).where(User.username == login_data.username)
    )
    user = result.scalar_one_or_none()

    # Verify password
    if not user or not verify_password(
        login_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
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

    # Generate token
    access_token = create_access_token({
        "sub": user.username,
        "user_id": user.id,
        "role": user.role
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 86400
    }

@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current authenticated user information."""
    return current_user
```

---

## Frontend Implementation

### Authentication Context (src/contexts/AuthContext.jsx)

```javascript
import React, { createContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:54112/api/auth';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize from localStorage
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user');

    if (token && storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (err) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (username, password) => {
    setError(null);
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/login`, {
        username,
        password,
      });

      const { access_token } = response.data;
      localStorage.setItem('access_token', access_token);

      // Fetch user data
      const userResponse = await axios.get(`${API_URL}/me`, {
        headers: { Authorization: `Bearer ${access_token}` }
      });

      localStorage.setItem('user', JSON.stringify(userResponse.data));
      setUser(userResponse.data);

      return { success: true };
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Login failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      error,
      login,
      logout,
      isAuthenticated: !!user,
      token: localStorage.getItem('access_token'),
    }}>
      {children}
    </AuthContext.Provider>
  );
};
```

### useAuth Hook (src/hooks/useAuth.js)

```javascript
import { useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';

export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
};
```

### Protected Routes (src/components/Auth/ProtectedRoute.jsx)

```javascript
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

export const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};
```

### Axios Interceptor (src/hooks/useAPI.js)

```javascript
import axios from 'axios';
import { useAuth } from './useAuth';

export const useAPI = () => {
  const { token, logout } = useAuth();

  const instance = axios.create({
    baseURL: 'http://127.0.0.1:54112'
  });

  // Add token to requests
  instance.interceptors.request.use(config => {
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  // Handle errors
  instance.interceptors.response.use(
    response => response,
    error => {
      if (error.response?.status === 401 ||
          error.response?.status === 403) {
        logout();
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  return instance;
};
```

---

## Integration Examples

### Example 1: Protecting an Endpoint

**Backend (FastAPI):**

```python
from fastapi import APIRouter, Depends
from middleware.auth import get_current_user, require_admin
from database.models import User

router = APIRouter(prefix="/api/agents", tags=["agents"])

@router.get("/")
async def list_agents(
    current_user: User = Depends(get_current_user)
):
    """Get all agents (requires authentication)."""
    # Only authenticated users can access
    return {"agents": []}

@router.post("/")
async def create_agent(
    agent_data: dict,
    current_user: User = Depends(require_admin)
):
    """Create agent (requires admin role)."""
    # Only admins can create agents
    return {"created": True}
```

### Example 2: Frontend Login Flow

**React Component:**

```javascript
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';

const LoginForm = () => {
  const { login, loading, error } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    const result = await login(username, password);

    if (result.success) {
      navigate('/dashboard');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* form fields */}
    </form>
  );
};
```

### Example 3: Making Authenticated API Calls

**Frontend (React):**

```javascript
import { useAuth } from '../hooks/useAuth';
import axios from 'axios';

const Dashboard = () => {
  const { token } = useAuth();

  const fetchAgents = async () => {
    try {
      const response = await axios.get(
        'http://127.0.0.1:54112/api/agents',
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      console.log('Agents:', response.data);
    } catch (error) {
      if (error.response?.status === 401) {
        // Token expired or invalid
        // User should login again
      }
    }
  };

  return (
    <button onClick={fetchAgents}>
      Fetch Agents
    </button>
  );
};
```

---

## API Endpoints

### Authentication Endpoints

#### POST /api/auth/login
Login with credentials and receive JWT token.

**Request:**
```bash
POST /api/auth/login HTTP/1.1
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Incorrect username or password"
}
```

#### GET /api/auth/me
Get current authenticated user information.

**Request:**
```bash
GET /api/auth/me HTTP/1.1
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "full_name": "Administrator",
  "role": "admin",
  "is_active": true,
  "created_at": "2025-11-10T10:00:00",
  "last_login": "2025-11-10T15:30:00"
}
```

#### POST /api/auth/change-password
Change current user's password.

**Request:**
```bash
POST /api/auth/change-password HTTP/1.1
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "current_password": "admin123",
  "new_password": "newsecure456"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

#### POST /api/auth/register
Create new user (admin only).

**Request:**
```bash
POST /api/auth/register HTTP/1.1
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure123",
  "email": "john@example.com",
  "full_name": "John Doe",
  "role": "user"
}
```

**Response (200 OK):**
```json
{
  "id": 2,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "role": "user",
  "is_active": true,
  "created_at": "2025-11-10T16:00:00",
  "last_login": null
}
```

#### GET /api/auth/users
List all users (admin only).

**Request:**
```bash
GET /api/auth/users HTTP/1.1
Authorization: Bearer {admin_token}
```

**Response:**
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Administrator",
    "role": "admin",
    "is_active": true,
    "created_at": "2025-11-10T10:00:00",
    "last_login": "2025-11-10T15:30:00"
  },
  {
    "id": 2,
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "role": "user",
    "is_active": true,
    "created_at": "2025-11-10T16:00:00",
    "last_login": null
  }
]
```

#### PUT /api/auth/users/{user_id}
Update user by ID (admin only).

**Request:**
```bash
PUT /api/auth/users/2 HTTP/1.1
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "role": "readonly",
  "is_active": false
}
```

#### DELETE /api/auth/users/{user_id}
Delete user (admin only).

**Request:**
```bash
DELETE /api/auth/users/2 HTTP/1.1
Authorization: Bearer {admin_token}
```

#### GET /api/auth/stats
Get authentication statistics (admin only).

**Request:**
```bash
GET /api/auth/stats HTTP/1.1
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "total_users": 5,
  "active_users": 4,
  "inactive_users": 1,
  "by_role": {
    "admin": 1,
    "user": 3,
    "readonly": 1
  },
  "timestamp": "2025-11-10T16:00:00"
}
```

---

## Security Architecture

### Password Security

**Bcrypt Hashing:**
```python
# Configuration
BCRYPT_ROUNDS = 12  # Work factor (higher = slower but more secure)

# Hashing
salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

# Verification
is_valid = bcrypt.checkpw(
    plain_password.encode('utf-8'),
    hashed_password.encode('utf-8')
)
```

**Benefits:**
- Bcrypt includes salt in the hash
- Work factor makes brute force attacks computationally expensive
- Automatically handles encoding

### JWT Security

**Token Configuration:**
- **Algorithm:** HS256 (HMAC-SHA256)
- **Secret:** Change in production (minimum 32 characters)
- **Expiration:** 24 hours
- **Claims:** sub (username), user_id, role, exp, iat, type

**Best Practices:**
1. Use strong JWT_SECRET (generate with `secrets.token_urlsafe(32)`)
2. Rotate JWT_SECRET periodically
3. Never log JWT tokens (contains user data)
4. Validate token expiration
5. Implement token refresh mechanism for production

### CORS Configuration

```python
# config.py
CORS_ORIGINS = [
    "http://localhost:3001",      # Local development
    "http://127.0.0.1:3001",      # Localhost alternative
    # "https://yourdomain.com",   # Production domain
]

# app.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting

**Configuration:**
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, ...):
    pass
```

**Applied Limits:**
- Login: 10 requests per minute
- Registration: 5 requests per hour
- Password change: 5 requests per hour

---

## Error Handling

### HTTP Status Codes

| Status | Meaning | Example |
|--------|---------|---------|
| **200** | OK | Successful login, user info retrieved |
| **400** | Bad Request | Invalid input, username exists |
| **401** | Unauthorized | Invalid credentials, token expired |
| **403** | Forbidden | Insufficient permissions, inactive user |
| **404** | Not Found | User not found by ID |
| **500** | Server Error | Database error, server crash |

### Error Response Format

```json
{
  "detail": "Incorrect username or password"
}
```

### Common Error Handling

```python
from fastapi import HTTPException, status

# Invalid credentials
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"},
)

# Insufficient permissions
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Access denied. Required role: admin"
)

# User not found
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found"
)
```

### Frontend Error Handling

```javascript
try {
  const response = await axios.post('/api/auth/login', data);
  setUser(response.data);
} catch (error) {
  const errorMessage = error.response?.data?.detail || 'Unknown error';

  if (error.response?.status === 401) {
    // Handle authentication error
  } else if (error.response?.status === 403) {
    // Handle authorization error
  } else {
    // Handle other errors
  }
}
```

---

## Testing Guide

### Unit Tests (Backend)

```python
import pytest
from fastapi.testclient import TestClient
from app import app
from middleware.auth import hash_password

client = TestClient(app)

def test_login_success():
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_password():
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_protected_endpoint_without_token():
    response = client.get("/api/agents")
    assert response.status_code == 401

def test_protected_endpoint_with_token():
    # First login
    login_response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_response.json()["access_token"]

    # Then access protected endpoint
    response = client.get(
        "/api/agents",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

def test_password_hashing():
    plain = "mypassword123"
    hashed = hash_password(plain)

    # Should not contain plain text
    assert plain not in hashed

    # Should be hashable twice without matching
    hashed2 = hash_password(plain)
    assert hashed != hashed2  # Different salts
```

### Integration Tests (Frontend)

```javascript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import LoginPage from './LoginPage';

test('successful login redirects to dashboard', async () => {
  render(<LoginPage />);

  const usernameInput = screen.getByLabelText(/username/i);
  const passwordInput = screen.getByLabelText(/password/i);
  const submitButton = screen.getByRole('button', { name: /sign in/i });

  fireEvent.change(usernameInput, { target: { value: 'admin' } });
  fireEvent.change(passwordInput, { target: { value: 'admin123' } });
  fireEvent.click(submitButton);

  await waitFor(() => {
    expect(window.location.pathname).toBe('/');
  });
});

test('failed login shows error message', async () => {
  render(<LoginPage />);

  fireEvent.change(screen.getByLabelText(/username/i), {
    target: { value: 'admin' }
  });
  fireEvent.change(screen.getByLabelText(/password/i), {
    target: { value: 'wrongpassword' }
  });
  fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

  await waitFor(() => {
    expect(screen.getByText(/incorrect/i)).toBeInTheDocument();
  });
});
```

### Manual Testing

**Test Case 1: Login Flow**
1. Navigate to http://localhost:3001/login
2. Enter username: admin
3. Enter password: admin123
4. Click "Sign In"
5. Verify redirected to dashboard
6. Check token in localStorage

**Test Case 2: Protected Routes**
1. Logout from dashboard
2. Try to access /dashboard directly
3. Verify redirected to login
4. Login again
5. Verify can access dashboard

**Test Case 3: Token Expiration**
1. Login successfully
2. Wait 24+ hours (or manually edit localStorage)
3. Try to make an API request
4. Verify get 401 error
5. Verify auto-logout and redirect to login

---

## Deployment Considerations

### Environment Configuration

**Production (.env):**
```env
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET=your-production-secret-key

JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

DATABASE_URL=postgresql://user:pass@localhost:5432/ziggie

CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### Security Checklist

- [ ] Change default admin password immediately
- [ ] Generate strong JWT_SECRET
- [ ] Use HTTPS in production
- [ ] Configure CORS for specific domains
- [ ] Set up database backups
- [ ] Enable HTTPS-only cookies
- [ ] Implement refresh token mechanism
- [ ] Set up audit logging
- [ ] Configure rate limiting
- [ ] Enable CSRF protection
- [ ] Use httpOnly cookies for tokens
- [ ] Implement multi-factor authentication (future)

### Database Setup

**PostgreSQL (Production):**
```bash
# Create database
psql -c "CREATE DATABASE ziggie;"

# Run migrations
alembic upgrade head

# Seed admin user
python -c "from scripts import seed_admin; seed_admin()"
```

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - JWT_SECRET=your-secret
      - DATABASE_URL=postgresql://user:password@db:5432/ziggie
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=ziggie
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## Troubleshooting

### Token Validation Fails in Production

**Problem:** Token works in development but not in production

**Solutions:**
1. Ensure JWT_SECRET is same in all servers
2. Verify clock synchronization (token expiration based on server time)
3. Check token format in Authorization header
4. Validate Base64 encoding of token

### CORS Errors

**Problem:** Frontend can't reach backend authentication

**Solutions:**
1. Verify CORS_ORIGINS includes frontend domain
2. Check HTTP vs HTTPS
3. Verify port numbers match
4. Check browser console for actual error

### Password Hashing Fails

**Problem:** bcrypt validation fails for stored passwords

**Solutions:**
1. Ensure password is properly encoded (UTF-8)
2. Verify bcrypt is installed: `pip install bcrypt`
3. Check hash format (should be valid bcrypt hash)
4. Verify salt is included in stored hash

---

## Document Information

**File:** `AUTH_DEVELOPER_GUIDE.md`
**Location:** `C:\Ziggie\control-center\docs\`
**Version:** 1.0.0
**Last Updated:** 2025-11-10
**Status:** Published
**Maintainer:** L2 Documentation Agent

---

**For Support:** Contact your system administrator or review related documentation files.
