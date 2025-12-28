# Authentication Guide
**Control Center Backend - Quick Start**

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy example file
cp .env.example .env

# Generate a secure JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env with the generated secret
# JWT_SECRET=<your_generated_secret>
```

### 3. Start the Server
```bash
python main.py
```

The default admin user is created automatically:
- **Username:** `admin`
- **Password:** `admin123`

**IMPORTANT:** Change the default password immediately!

---

## API Authentication

### Login
```bash
# Login to get JWT token
curl -X POST http://localhost:54112/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer",
#   "expires_in": 86400
# }
```

### Use Token in Requests
```bash
# Save token
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Make authenticated request
curl http://localhost:54112/api/agents \
  -H "Authorization: Bearer $TOKEN"
```

---

## Protecting Your Endpoints

### Require Authentication
```python
from fastapi import Depends
from middleware.auth import get_current_user
from database.models import User

@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_user)
):
    return {"message": f"Hello {current_user.username}"}
```

### Require Admin Role
```python
from middleware.auth import require_admin

@router.post("/admin-only")
async def admin_endpoint(
    current_user: User = Depends(require_admin)
):
    return {"message": "Admin access granted"}
```

### Require User Role (Admin or User)
```python
from middleware.auth import require_user

@router.put("/user-endpoint")
async def user_endpoint(
    current_user: User = Depends(require_user)
):
    return {"message": "User access granted"}
```

---

## Role-Based Access Control

Three user roles are available:

| Role | Permissions | Use Case |
|------|-------------|----------|
| **admin** | Full access, user management | System administrators |
| **user** | Read/write access to resources | Developers, operators |
| **readonly** | Read-only access | Monitoring, auditing |

### Using Role Dependencies

```python
from middleware.auth import require_admin, require_user, require_readonly

# Only admins
@router.delete("/resource/{id}")
async def delete_resource(user: User = Depends(require_admin)):
    pass

# Admins and users
@router.post("/resource")
async def create_resource(user: User = Depends(require_user)):
    pass

# All authenticated users
@router.get("/resource")
async def read_resource(user: User = Depends(require_readonly)):
    pass
```

---

## WebSocket Authentication

WebSocket connections require token in query parameters:

```javascript
// JavaScript example
const token = "your_jwt_token";
const ws = new WebSocket(`ws://localhost:54112/api/services/ws?token=${token}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Update:", data);
};
```

```python
# Python example
import asyncio
import websockets

async def connect():
    token = "your_jwt_token"
    uri = f"ws://localhost:54112/api/services/ws?token={token}"

    async with websockets.connect(uri) as ws:
        async for message in ws:
            print(f"Update: {message}")

asyncio.run(connect())
```

---

## User Management

### Create New User (Admin Only)
```bash
curl -X POST http://localhost:54112/api/auth/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure123",
    "email": "john@example.com",
    "full_name": "John Doe",
    "role": "user"
  }'
```

### List Users (Admin Only)
```bash
curl http://localhost:54112/api/auth/users \
  -H "Authorization: Bearer $TOKEN"
```

### Update User (Admin Only)
```bash
curl -X PUT http://localhost:54112/api/auth/users/2 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role": "readonly", "is_active": false}'
```

### Delete User (Admin Only)
```bash
curl -X DELETE http://localhost:54112/api/auth/users/2 \
  -H "Authorization: Bearer $TOKEN"
```

---

## Self-Service Endpoints

### Change Password
```bash
curl -X POST http://localhost:54112/api/auth/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "admin123",
    "new_password": "newsecure456"
  }'
```

### Update Profile
```bash
curl -X PUT http://localhost:54112/api/auth/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newemail@example.com",
    "full_name": "New Name"
  }'
```

### Get Current User Info
```bash
curl http://localhost:54112/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## Security Best Practices

### Production Deployment

1. **Generate Secure JWT Secret**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   Add to `.env`:
   ```
   JWT_SECRET=<generated_secret>
   ```

2. **Change Default Admin Password**
   Immediately after first login!

3. **Use HTTPS**
   Never use HTTP in production for authentication.

4. **Secure CORS**
   Configure specific allowed origins in `.env`:
   ```
   CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
   ```

5. **Environment Variables**
   Never commit `.env` file to version control.
   Use `.env.example` as template.

6. **Token Storage**
   - Frontend: Store in httpOnly cookies or secure storage
   - Mobile: Use secure keychain/keystore
   - Never store in localStorage for sensitive apps

7. **Rate Limiting**
   Already configured:
   - Login: 10/minute
   - Registration: 5/hour
   - Password change: 5/hour

---

## Troubleshooting

### Token Expired
**Error:** `Token has expired`
**Solution:** Login again to get a new token. Tokens expire after 24 hours.

### Invalid Token
**Error:** `Invalid authentication token`
**Solution:** Ensure token is properly formatted: `Bearer <token>`

### Forbidden Access
**Error:** `Access denied. Required role: admin`
**Solution:** User doesn't have required role. Update user role in database.

### WebSocket Rejected
**Error:** `Authentication required: No token provided`
**Solution:** Add token to query params: `ws://host/path?token=<token>`

---

## Testing

### Python Test Script
```python
import requests

BASE = "http://localhost:54112"

# Login
r = requests.post(f"{BASE}/api/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Test authenticated endpoint
agents = requests.get(f"{BASE}/api/agents", headers=headers)
print(f"Agents: {agents.json()['total']}")

# Create user
user = requests.post(f"{BASE}/api/auth/register", headers=headers, json={
    "username": "test",
    "password": "test123",
    "role": "user"
})
print(f"User created: {user.json()}")
```

### cURL Test Script
```bash
#!/bin/bash

BASE="http://localhost:54112"

# Login
RESPONSE=$(curl -s -X POST $BASE/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

TOKEN=$(echo $RESPONSE | jq -r '.access_token')

echo "Token: $TOKEN"

# Test endpoints
curl -s $BASE/api/agents \
  -H "Authorization: Bearer $TOKEN" | jq

curl -s $BASE/api/services \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## API Reference

### Authentication Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/login` | None | Login with credentials |
| POST | `/api/auth/login/form` | None | OAuth2 compatible login |
| GET | `/api/auth/me` | User | Get current user info |
| PUT | `/api/auth/me` | User | Update current user |
| POST | `/api/auth/change-password` | User | Change password |
| POST | `/api/auth/register` | Admin | Create new user |
| GET | `/api/auth/users` | Admin | List all users |
| GET | `/api/auth/users/{id}` | Admin | Get user by ID |
| PUT | `/api/auth/users/{id}` | Admin | Update user |
| DELETE | `/api/auth/users/{id}` | Admin | Delete user |
| GET | `/api/auth/stats` | Admin | Get auth statistics |

### Protected WebSocket Endpoints

| Endpoint | Description | Auth |
|----------|-------------|------|
| `/api/services/ws?token=<jwt>` | Real-time service status | Required |
| `/api/system/ws?token=<jwt>` | Real-time system stats | Required |

---

## Development Tips

### Disable Authentication (Development Only)

**DO NOT USE IN PRODUCTION**

If you need to disable auth for development:

```python
# In your endpoint, use optional auth
from middleware.auth import get_current_user_optional

@router.get("/dev-endpoint")
async def dev_endpoint(user = Depends(get_current_user_optional)):
    # user will be None if no token provided
    if user:
        return {"user": user.username}
    return {"message": "Anonymous access"}
```

### Debug Token Issues

```python
import jwt
from config import settings

# Decode token manually
token = "your_token_here"
decoded = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
print(decoded)
```

---

## Support

For issues or questions:
1. Check `AUTH_IMPLEMENTATION_REPORT.md` for detailed documentation
2. Review error messages in server logs
3. Enable DEBUG mode in config.py for detailed logging

---

**Last Updated:** 2025-11-10
**Version:** 1.0.0
