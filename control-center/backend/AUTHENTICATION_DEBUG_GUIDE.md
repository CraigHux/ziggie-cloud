# HTTP Bearer Token Authentication - Debugging Guide

## Overview

This guide provides comprehensive troubleshooting steps for the Bearer token authentication issue where:
- **Login works**: `curl -X POST http://127.0.0.1:54112/api/auth/login -d '{"username":"admin","password":"admin123"}'` returns a valid token
- **Bearer token fails**: `curl -X GET http://127.0.0.1:54112/api/auth/me -H "Authorization: Bearer TOKEN"` returns "Invalid authentication token"

## Quick Diagnosis

Run the test suite to identify the issue:

```bash
# Test 1: Unit tests for authentication components
cd C:\Ziggie\control-center\backend
python test_bearer_authentication.py

# Test 2: HTTP integration tests (requires server running)
# In another terminal, ensure server is running:
python main.py

# In first terminal:
python test_http_bearer.py
```

## Known Issue Patterns

### Pattern 1: Token Validation Working But HTTP Request Fails

**Symptoms:**
- `test_bearer_authentication.py` passes all tests
- `test_http_bearer.py` fails on TEST 4 (GET /api/auth/me with Bearer token)

**Common Causes:**
1. **Middleware ordering issue** - Authentication middleware runs after another middleware that rejects the request
2. **CORS preflight issue** - OPTIONS request handling interferes with bearer token validation
3. **Header case sensitivity** - Some servers treat "Authorization" differently
4. **Token encoding issue** - Token generated correctly but not transmitted correctly over HTTP

**Debug Steps:**
```bash
# 1. Check if server is properly configured for CORS
grep -n "CORSMiddleware" C:\Ziggie\control-center\backend\main.py

# 2. Verify auth middleware is registered before CORS
# In main.py, check order of:
# - app.add_middleware() calls
# - app.include_router() calls

# 3. Test with curl verbose output
curl -v -X GET http://127.0.0.1:54112/api/auth/me \
  -H "Authorization: Bearer <YOUR_TOKEN>"

# 4. Check server logs for actual error messages
# Look for KeyError, AttributeError, or other exceptions
```

### Pattern 2: JWT Signature Verification Fails

**Symptoms:**
- JWT token decodes fine but fails signature verification
- Error: "Invalid authentication token"
- Token was created with different secret than verification

**Common Causes:**
1. **JWT_SECRET mismatch** - Login and token verification use different secrets
2. **Environment variable override** - .env file overrides config.py settings
3. **Multiple server instances** - Different processes have different secrets

**Debug Steps:**
```bash
# 1. Check JWT configuration
python -c "from config import settings; print(f'JWT_SECRET: {settings.JWT_SECRET}'); print(f'JWT_ALGORITHM: {settings.JWT_ALGORITHM}')"

# 2. Verify no .env file conflicts
ls -la C:\Ziggie\control-center\backend\.env*

# 3. Check environment variables
echo %JWT_SECRET%
echo %JWT_ALGORITHM%

# 4. Run token creation and verification test
python test_bearer_authentication.py
# Should pass TEST 2 (JWT Token Creation and Decoding)
```

### Pattern 3: User Not Found in Database

**Symptoms:**
- Token decodes successfully
- User lookup in database fails
- Error: "User not found"

**Common Causes:**
1. **Database session issue** - Transaction not committed properly during login
2. **User ID mismatch** - Token has wrong user_id
3. **Database corrupted** - User record deleted or corrupted

**Debug Steps:**
```bash
# 1. Check if admin user exists
python -c "
import asyncio
from database.db import init_db, AsyncSessionLocal
from database.models import User
from sqlalchemy import select

async def check():
    await init_db()
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        for user in users:
            print(f'User: {user.username}, ID: {user.id}, Active: {user.is_active}')

asyncio.run(check())
"

# 2. Trace token claims vs database
python -c "
import asyncio
from middleware.auth import decode_access_token, create_access_token

token = create_access_token({
    'sub': 'admin',
    'user_id': 1,
    'role': 'admin'
})
decoded = decode_access_token(token)
print(f'Token claims: {decoded}')
"
```

### Pattern 4: Bearer Header Not Parsed Correctly

**Symptoms:**
- Token validation logic works
- Bearer header format issues
- Different behavior with different header formats

**Common Causes:**
1. **Case sensitivity** - "authorization" vs "Authorization"
2. **Whitespace issues** - Extra spaces in header value
3. **Token extraction logic** - String parsing error in extracting token from "Bearer <TOKEN>"

**Debug Steps:**
```bash
# 1. Test different header formats
curl -X GET http://127.0.0.1:54112/api/auth/me \
  -H "Authorization: Bearer <TOKEN>"

curl -X GET http://127.0.0.1:54112/api/auth/me \
  -H "authorization: Bearer <TOKEN>"

curl -X GET http://127.0.0.1:54112/api/auth/me \
  -H "Authorization: bearer <TOKEN>"

# 2. Check token extraction in auth.py
grep -A 5 "credentials.credentials" C:\Ziggie\control-center\backend\middleware\auth.py

# 3. Run header parsing test
python test_bearer_authentication.py
# Check TEST 5 (Bearer Header Parsing)
```

## Step-by-Step Debugging

### Step 1: Verify JWT Configuration

```bash
cd C:\Ziggie\control-center\backend

# Check config
python -c "
from config import settings
print('=== JWT Configuration ===')
print(f'Secret: {settings.JWT_SECRET[:20]}...')
print(f'Algorithm: {settings.JWT_ALGORITHM}')
print(f'Expiration: {settings.JWT_EXPIRATION_HOURS} hours')
print(f'DEFAULT_ADMIN_USERNAME: {settings.DEFAULT_ADMIN_USERNAME}')
print(f'HOST: {settings.HOST}')
print(f'PORT: {settings.PORT}')
"
```

### Step 2: Run Local Authentication Tests

```bash
# This tests all components locally without HTTP
python test_bearer_authentication.py
```

**Expected output:**
```
✓ Password hashing - Password verification successful
✓ Token creation and decoding - All claims verified
✓ User creation in database - User ID: 1
✓ Bearer token validation - User authenticated successfully
✓ Bearer header parsing - Header format validation tested
✓ JWT secret configuration - Custom secret configured
✓ JWT algorithm - PASS

ALL TESTS PASSED!
```

### Step 3: Verify Server is Running

```bash
# Check if server responds
curl http://127.0.0.1:54112/health

# Should return:
# {"status":"healthy","database":"connected","caching":"enabled"}
```

### Step 4: Test Login Endpoint

```bash
# Get a fresh token
curl -X POST http://127.0.0.1:54112/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Response should be:
# {"access_token":"<JWT_TOKEN>","token_type":"bearer","expires_in":86400}

# Save token to variable
TOKEN=$(curl -s -X POST http://127.0.0.1:54112/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

echo "Token: $TOKEN"
```

### Step 5: Test Bearer Token

```bash
# Test with the token
curl -v -X GET http://127.0.0.1:54112/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Should return user information with status 200
# If fails with 401, continue to Step 6
```

### Step 6: Enable Debug Logging

Add debugging to `middleware/auth.py`:

```python
# Add at the top of decode_access_token function:
def decode_access_token(token: str) -> Dict[str, Any]:
    import sys
    print(f"DEBUG: decode_access_token called", file=sys.stderr)
    print(f"DEBUG: token preview: {token[:50]}...", file=sys.stderr)
    print(f"DEBUG: JWT_SECRET: {settings.JWT_SECRET[:20]}...", file=sys.stderr)
    print(f"DEBUG: JWT_ALGORITHM: {settings.JWT_ALGORITHM}", file=sys.stderr)

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        print(f"DEBUG: Token decoded successfully: {payload}", file=sys.stderr)
        return payload
    except jwt.ExpiredSignatureError as e:
        print(f"DEBUG: Token expired: {e}", file=sys.stderr)
        raise ...
    except jwt.InvalidTokenError as e:
        print(f"DEBUG: Invalid token: {e}", file=sys.stderr)
        raise ...
```

Then check server logs when making request.

### Step 7: Check Database State

```bash
python -c "
import asyncio
from database.db import init_db, AsyncSessionLocal
from database.models import User
from sqlalchemy import select

async def check_users():
    await init_db()
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        print('=== Users in Database ===')
        for user in users:
            print(f'ID: {user.id}')
            print(f'  Username: {user.username}')
            print(f'  Email: {user.email}')
            print(f'  Role: {user.role}')
            print(f'  Active: {user.is_active}')
            print(f'  Created: {user.created_at}')
            print(f'  Last Login: {user.last_login}')
            print()

asyncio.run(check_users())
"
```

### Step 8: Integration Testing

```bash
# Run full HTTP integration tests
python test_http_bearer.py
```

This will test:
1. Server availability
2. Login endpoint
3. Unauthenticated access (should be rejected)
4. Authenticated access with Bearer token
5. Invalid token handling
6. Malformed header handling
7. Token expiration information
8. Protected endpoint access

## Debugging Checklist

- [ ] JWT_SECRET is configured and consistent
- [ ] Database is initialized and contains admin user
- [ ] Admin user is marked as active (is_active=True)
- [ ] Token is created with correct claims (sub, user_id, role)
- [ ] Token signature is valid (verification uses same secret as creation)
- [ ] Bearer header is formatted correctly: "Bearer <TOKEN>"
- [ ] Authorization header is being passed to endpoint
- [ ] Middleware is registered in correct order in main.py
- [ ] Database session is committed properly during login
- [ ] User lookup query is correct (checking both id and username)
- [ ] Server logs show no exceptions during token validation
- [ ] Token is not expired

## Common Curl Commands for Testing

```bash
# Get a token
TOKEN=$(curl -s -X POST http://127.0.0.1:54112/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# Test GET /api/auth/me
curl -X GET http://127.0.0.1:54112/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Test GET /api/auth/me with verbose output
curl -v -X GET http://127.0.0.1:54112/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Test GET /api/auth/users (admin only)
curl -X GET http://127.0.0.1:54112/api/auth/users \
  -H "Authorization: Bearer $TOKEN"

# Test POST /api/auth/change-password
curl -X POST http://127.0.0.1:54112/api/auth/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"current_password":"admin123","new_password":"newpass123"}'

# Decode token payload (copy TOKEN from above and use this)
python -c "
import base64, json
token = '$TOKEN'
parts = token.split('.')
payload = base64.urlsafe_b64decode(parts[1] + '==')
print(json.dumps(json.loads(payload), indent=2))
"
```

## Additional Resources

### Files Modified or Created

1. **test_bearer_authentication.py** - Unit tests for JWT authentication
2. **test_http_bearer.py** - HTTP integration tests
3. **middleware/auth_debug.py** - Debug logging utilities
4. **AUTHENTICATION_DEBUG_GUIDE.md** - This file

### Related Source Files

- `middleware/auth.py` - Core authentication logic
- `api/auth.py` - Authentication endpoints
- `database/models.py` - User model
- `config.py` - Configuration including JWT settings
- `main.py` - Application setup and middleware registration

## Support

If issues persist after following this guide:

1. Collect server logs
2. Run all tests and save output
3. Check for any custom middleware that might interfere
4. Verify no environment variable overrides
5. Compare with a fresh installation
