# Authentication Quick Reference Card

## Getting Started (3 Steps)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate secure JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Add to .env: JWT_SECRET=<output>

# 3. Start server (auto-creates admin user)
python main.py
```

**Default Login:** `admin` / `admin123` ⚠️ **CHANGE IMMEDIATELY**

---

## cURL Commands

### Login
```bash
curl -X POST http://localhost:54112/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Use Token
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl http://localhost:54112/api/agents -H "Authorization: Bearer $TOKEN"
```

### Create User (Admin)
```bash
curl -X POST http://localhost:54112/api/auth/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"pass123","role":"user"}'
```

### Change Password
```bash
curl -X POST http://localhost:54112/api/auth/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"current_password":"admin123","new_password":"newpass456"}'
```

---

## Python Code

### Protect Endpoint
```python
from fastapi import Depends
from middleware.auth import get_current_user, require_admin
from database.models import User

# Any authenticated user
@router.get("/resource")
async def get_resource(user: User = Depends(get_current_user)):
    return {"user": user.username}

# Admin only
@router.delete("/resource")
async def delete_resource(user: User = Depends(require_admin)):
    return {"deleted": True}
```

### Client Usage
```python
import requests

# Login
r = requests.post("http://localhost:54112/api/auth/login",
                  json={"username": "admin", "password": "admin123"})
token = r.json()["access_token"]

# Use token
headers = {"Authorization": f"Bearer {token}"}
agents = requests.get("http://localhost:54112/api/agents", headers=headers)
print(agents.json())
```

---

## JavaScript Code

### Login & Fetch
```javascript
const BASE = 'http://localhost:54112';

// Login
const loginRes = await fetch(`${BASE}/api/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'admin123' })
});
const { access_token } = await loginRes.json();

// Use token
const agentsRes = await fetch(`${BASE}/api/agents`, {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const agents = await agentsRes.json();
```

### WebSocket
```javascript
const token = "your_jwt_token";
const ws = new WebSocket(`ws://localhost:54112/api/services/ws?token=${token}`);

ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

---

## Roles

| Role | Permissions | Use Case |
|------|-------------|----------|
| `admin` | Full access + user mgmt | System admins |
| `user` | Read/write resources | Developers |
| `readonly` | Read-only access | Monitoring |

### Dependencies
```python
from middleware.auth import require_admin, require_user, require_readonly

# Admin only
@router.post("/admin", dependencies=[Depends(require_admin)])

# User or admin
@router.post("/create", dependencies=[Depends(require_user)])

# Anyone authenticated
@router.get("/read", dependencies=[Depends(require_readonly)])
```

---

## Endpoints

### Public (No Auth)
- `POST /api/auth/login`
- `POST /api/auth/login/form`
- `GET /` (root)
- `GET /health`

### User Endpoints
- `GET /api/auth/me`
- `PUT /api/auth/me`
- `POST /api/auth/change-password`

### Admin Endpoints
- `POST /api/auth/register`
- `GET /api/auth/users`
- `PUT /api/auth/users/{id}`
- `DELETE /api/auth/users/{id}`
- `GET /api/auth/stats`

### Protected Resources
- `/api/agents/*`
- `/api/services/*`
- `/api/system/*`
- `/api/knowledge/*`
- `/api/docker/*`

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | No/invalid token | Login to get token |
| 403 Forbidden | Insufficient role | Need admin/user role |
| Token expired | Token > 24hrs old | Re-login |
| WS rejected | No token in query | Add `?token=<jwt>` |

---

## Testing

```bash
# Run test suite
python test_authentication.py

# Expected output: ✅ ALL TESTS PASSED!
```

---

## Production Checklist

- [ ] Generate secure `JWT_SECRET` (32+ chars)
- [ ] Change admin password from `admin123`
- [ ] Use HTTPS (not HTTP)
- [ ] Set specific `CORS_ORIGINS`
- [ ] Never commit `.env` to git
- [ ] Enable SSL/TLS
- [ ] Configure firewall
- [ ] Set up monitoring

---

## Files Reference

| File | Purpose |
|------|---------|
| `middleware/auth.py` | JWT & auth logic |
| `api/auth.py` | Auth endpoints |
| `database/models.py` | User model |
| `config.py` | JWT settings |
| `.env` | Secrets (git ignored) |

---

## Help

📖 **Full Docs:** `AUTH_IMPLEMENTATION_REPORT.md`
🚀 **Quick Start:** `AUTHENTICATION_GUIDE.md`
🔒 **Security:** `SECURITY_SUMMARY.md`
🧪 **Testing:** `test_authentication.py`

**API Docs:** http://localhost:54112/docs

---

**Version:** 1.0.0 | **Updated:** 2025-11-10
