# Quick Testing Reference

## One-Line Test Execution

### Run Everything
```bash
cd C:\Ziggie\control-center\backend && python run_auth_tests.py
```

### Run Local Tests Only (No Server Needed)
```bash
cd C:\Ziggie\control-center\backend && python test_bearer_authentication.py
```

### Run HTTP Tests Only (Requires Server)
```bash
cd C:\Ziggie\control-center\backend && python test_http_bearer.py
```

## Manual Testing with Curl

### 1. Login and Save Token
```bash
# PowerShell
$TOKEN = ((curl -s -X POST http://127.0.0.1:54112/api/auth/login `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"username":"admin","password":"admin123"}') | ConvertFrom-Json).access_token

echo "Token: $TOKEN"
```

```bash
# Bash/Git Bash
TOKEN=$(curl -s -X POST http://127.0.0.1:54112/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

echo "Token: $TOKEN"
```

### 2. Test Protected Endpoint
```bash
# PowerShell
curl -X GET http://127.0.0.1:54112/api/auth/me `
  -Headers @{"Authorization"="Bearer $TOKEN"}
```

```bash
# Bash/Git Bash
curl -X GET http://127.0.0.1:54112/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Test with Verbose Output
```bash
curl -v -X GET http://127.0.0.1:54112/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Check Server Health
```bash
curl http://127.0.0.1:54112/health
```

### 5. List All Users (Admin Only)
```bash
curl -X GET http://127.0.0.1:54112/api/auth/users \
  -H "Authorization: Bearer $TOKEN"
```

## Test Results Interpretation

### Expected Success Output from test_bearer_authentication.py
```
============================================================
HTTP BEARER TOKEN AUTHENTICATION TEST SUITE
============================================================

✓ Password hashing - PASS: Password verification successful
✓ Token creation and decoding - PASS: All claims verified
✓ User creation in database - PASS: User ID: 1
✓ Bearer token validation - PASS: User authenticated successfully
✓ Bearer header parsing - PASS: Header format validation tested
✓ JWT secret configuration - PASS: Custom secret configured
✓ JWT algorithm - PASS

✅ ALL TESTS PASSED!
```

### Expected Success Output from test_http_bearer.py
```
============================================================
HTTP BEARER TOKEN INTEGRATION TEST SUITE
============================================================

✓ Server availability - PASS: Server responding at http://127.0.0.1:54112
✓ Login - PASS: Login successful
✓ No authentication rejection - PASS: Server correctly rejected unauthenticated request
✓ Bearer token authentication - PASS: Successfully authenticated with Bearer token
✓ Invalid token rejection - PASS: Server correctly rejected invalid token
✓ Malformed header handling - PASS: Various header formats tested
✓ Token expiration info - PASS: Token expires at <timestamp>
✓ Protected endpoint access - PASS: Successfully accessed protected endpoint

✅ ALL TESTS PASSED!
```

## Troubleshooting Quick Fixes

### If: "Cannot reach server"
**Fix:** Start the server in another terminal
```bash
cd C:\Ziggie\control-center\backend
python main.py
```

### If: "Invalid authentication token"
**Fix:** Verify JWT_SECRET configuration
```python
python -c "from config import settings; print(settings.JWT_SECRET)"
```

### If: "User not found"
**Fix:** Check if database is initialized
```python
python test_bearer_authentication.py
# Check "User creation in database" test
```

### If: "Token has expired"
**Fix:** Generate a fresh token (old token expired after 24 hours)
```bash
# Get new token
TOKEN=$(curl -s -X POST http://127.0.0.1:54112/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')
```

### If: "Incorrect username or password"
**Fix:** Verify admin credentials (default: admin/admin123)
```python
# Check config
python -c "
from config import settings
print(f'Username: {settings.DEFAULT_ADMIN_USERNAME}')
print(f'Password: {settings.DEFAULT_ADMIN_PASSWORD}')
"
```

## Debug Commands

### Decode Token Payload
```python
python -c "
import base64, json
token = 'YOUR_TOKEN_HERE'
parts = token.split('.')
payload = base64.urlsafe_b64decode(parts[1] + '==')
print(json.dumps(json.loads(payload), indent=2))
"
```

### Check Database State
```python
python -c "
import asyncio
from database.db import init_db, AsyncSessionLocal
from database.models import User
from sqlalchemy import select

async def check():
    await init_db()
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        for user in result.scalars():
            print(f'{user.username} (ID: {user.id}, Active: {user.is_active})')

asyncio.run(check())
"
```

### Check JWT Configuration
```python
python -c "
from config import settings
print(f'JWT_SECRET: {settings.JWT_SECRET[:20]}...')
print(f'JWT_ALGORITHM: {settings.JWT_ALGORITHM}')
print(f'JWT_EXPIRATION_HOURS: {settings.JWT_EXPIRATION_HOURS}')
"
```

### Test Token Creation Locally
```python
python -c "
from middleware.auth import create_access_token, decode_access_token

# Create token
token = create_access_token({'sub': 'admin', 'user_id': 1, 'role': 'admin'})
print(f'Token: {token[:50]}...')

# Decode token
decoded = decode_access_token(token)
print(f'Decoded: {decoded}')
"
```

## File Locations

| Test File | Purpose |
|-----------|---------|
| test_bearer_authentication.py | Local component testing |
| test_http_bearer.py | HTTP endpoint testing |
| run_auth_tests.py | Test orchestration |
| middleware/auth_debug.py | Debug utilities |
| AUTHENTICATION_DEBUG_GUIDE.md | Detailed debugging |
| AUTH_TEST_SUMMARY.md | Complete reference |
| QUICK_TEST_REFERENCE.md | This file |

## Server Startup

```bash
cd C:\Ziggie\control-center\backend
python main.py
```

Server runs on: `http://127.0.0.1:54112`

## Common Endpoints

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| /health | GET | No | Health check |
| /api/auth/login | POST | No | Get access token |
| /api/auth/me | GET | Yes | Get current user |
| /api/auth/users | GET | Yes (Admin) | List all users |
| /api/auth/change-password | POST | Yes | Change password |

## Status Codes Reference

| Code | Meaning | Auth Issue |
|------|---------|-----------|
| 200 | Success | Token valid |
| 401 | Unauthorized | Token invalid/expired/missing |
| 403 | Forbidden | User inactive or insufficient role |
| 404 | Not found | User doesn't exist |

## Next Steps

1. **Run Tests**: `python run_auth_tests.py`
2. **Check Output**: Review passed/failed tests
3. **Debug if Needed**: Use AUTHENTICATION_DEBUG_GUIDE.md
4. **Verify Manually**: Use curl commands above
5. **Document**: Note any issues found and fixed

## Quick Links

- Debugging Guide: `AUTHENTICATION_DEBUG_GUIDE.md`
- Full Summary: `AUTH_TEST_SUMMARY.md`
- Debug Utilities: `middleware/auth_debug.py`
- Auth Logic: `middleware/auth.py`
- Auth Endpoints: `api/auth.py`
