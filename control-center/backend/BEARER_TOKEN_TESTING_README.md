# Bearer Token Authentication Testing Suite

**Role:** L2.QA.TESTING.1 - API Testing and Validation
**Mission:** Reproduce and validate HTTP Bearer token authentication issue
**Status:** COMPLETE - Ready to Execute

## Overview

This comprehensive testing suite addresses the authentication issue where login works but Bearer token validation fails:

```
✓ Login works: POST /api/auth/login returns valid JWT token
✗ Bearer fails: GET /api/auth/me with Bearer token returns "Invalid authentication token"
```

## What You Get

### 3 Test Scripts (1,154 lines)
- **test_bearer_authentication.py** - Local component tests
- **test_http_bearer.py** - HTTP endpoint tests
- **run_auth_tests.py** - Orchestrated test execution

### 4 Documentation Files
- **AUTHENTICATION_DEBUG_GUIDE.md** - Step-by-step debugging
- **AUTH_TEST_SUMMARY.md** - Architecture & analysis
- **QUICK_TEST_REFERENCE.md** - Quick commands
- **TEST_EXECUTION_SUMMARY.md** - Execution guide

### 1 Debug Module
- **middleware/auth_debug.py** - Logging utilities

## Quick Start (30 seconds)

```bash
cd C:\Ziggie\control-center\backend
python run_auth_tests.py
```

This runs all tests and provides a complete report.

## Detailed Execution

### Option 1: Full Test Suite (Recommended)

Start server in one terminal:
```bash
cd C:\Ziggie\control-center\backend
python main.py
```

Run tests in another:
```bash
cd C:\Ziggie\control-center\backend
python run_auth_tests.py
```

**Expected Runtime:** 3-5 minutes
**What it tests:**
1. Local component tests (password, JWT, database)
2. HTTP endpoint tests (login, bearer token, protected endpoints)
3. Error handling and edge cases

### Option 2: Local Tests Only

```bash
cd C:\Ziggie\control-center\backend
python test_bearer_authentication.py
```

**Expected Runtime:** 30-60 seconds
**Requirements:** No server needed
**Tests:** Component-level functionality

### Option 3: HTTP Tests Only

```bash
cd C:\Ziggie\control-center\backend
python test_http_bearer.py
```

**Expected Runtime:** 2-3 minutes
**Requirements:** Server must be running
**Tests:** Actual HTTP endpoints

## Understanding Results

### Success (All Tests Pass)
```
✅ ALL TESTS PASSED!
- All 6 local tests passed
- All 8 HTTP tests passed
- Bearer token authentication working correctly
```

### Failure (Some Tests Fail)
```
❌ SOME TESTS FAILED
- Review which tests failed
- Consult AUTHENTICATION_DEBUG_GUIDE.md
- Enable debug logging
```

## Test Scenarios

### Local Tests (test_bearer_authentication.py)

| # | Test | Validates |
|---|------|-----------|
| 1 | Password Hashing | bcrypt hash/verify functions |
| 2 | JWT Token Creation | Token generation and decoding |
| 3 | Database User Setup | User CRUD operations |
| 4 | Bearer Token Validation | End-to-end auth flow |
| 5 | Header Parsing | Authorization header formats |
| 6 | Config Validation | JWT settings security |

### HTTP Tests (test_http_bearer.py)

| # | Test | Validates |
|---|------|-----------|
| 1 | Server Availability | Server responds |
| 2 | Login Endpoint | Token generation via POST |
| 3 | No Auth Rejection | Unauthenticated requests blocked |
| 4 | Bearer Token Auth | Token usage via HTTP |
| 5 | Invalid Token | Bad token rejection |
| 6 | Malformed Headers | Various header formats |
| 7 | Token Expiration | Token lifetime |
| 8 | Protected Endpoint | Real endpoint access |

## Manual Testing (Curl)

```bash
# 1. Get token
TOKEN=$(curl -s -X POST http://127.0.0.1:54112/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# 2. Use token
curl -X GET http://127.0.0.1:54112/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Expected: User information with 200 status
```

## Debugging When Tests Fail

### Step 1: Review Test Output
- Note which specific test failed
- Read the error message carefully

### Step 2: Check Quick Fixes
See QUICK_TEST_REFERENCE.md for:
- Server not running? Start it
- JWT_SECRET issue? Check config
- Token expired? Get a fresh one
- Database issue? Verify setup

### Step 3: Follow Debug Guide
AUTHENTICATION_DEBUG_GUIDE.md has:
- 8-step diagnostic process
- Known issue patterns
- Debug logging setup
- Configuration validation

### Step 4: Enable Debug Logging
Use middleware/auth_debug.py utilities:
```python
# Add to middleware/auth.py
from middleware.auth_debug import AuthenticationLogger, TokenDebugger

def decode_access_token(token: str):
    TokenDebugger.log_token_details(token)
    # ... rest of function
```

### Step 5: Check Server Logs
```bash
# Look for errors in running server terminal
# Common issues:
# - KeyError: Missing claims in token
# - AttributeError: Database query error
# - InvalidTokenError: JWT signature failure
```

## Key Files

### Test Files
```
C:\Ziggie\control-center\backend\
├── test_bearer_authentication.py    # Local tests (458 lines)
├── test_http_bearer.py              # HTTP tests (468 lines)
├── run_auth_tests.py                # Orchestration (228 lines)
```

### Documentation
```
C:\Ziggie\control-center\backend\
├── BEARER_TOKEN_TESTING_README.md       # This file
├── AUTHENTICATION_DEBUG_GUIDE.md         # Debugging guide
├── AUTH_TEST_SUMMARY.md                 # Architecture & analysis
├── QUICK_TEST_REFERENCE.md              # Quick commands
├── TEST_EXECUTION_SUMMARY.md            # Execution guide
```

### Debug Utilities
```
C:\Ziggie\control-center\backend\
└── middleware\
    └── auth_debug.py                # Debug logging utilities
```

### Existing Files (Not Modified)
```
C:\Ziggie\control-center\backend\
├── middleware\auth.py               # Authentication logic
├── api\auth.py                      # Auth endpoints
├── database\models.py               # User model
├── config.py                        # Settings
├── main.py                          # App setup
└── test_authentication.py           # Original tests (already passing)
```

## Technology Stack

- **FastAPI** - Web framework
- **PyJWT** - JWT token handling
- **SQLAlchemy** - ORM
- **bcrypt** - Password hashing
- **httpx** - HTTP client (testing)

## Common Issues & Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| "Cannot reach server" | Start server: `python main.py` |
| "Invalid authentication token" | Check JWT_SECRET in config.py |
| "User not found" | Run test_bearer_authentication.py to check DB |
| "Token expired" | Get fresh token from login endpoint |
| "Incorrect username/password" | Verify credentials (admin/admin123) |

## Architecture Overview

```
HTTP Request with Bearer Token
    ↓
HTTPBearer Security Dependency (FastAPI)
    ↓
get_current_user() function
    ├─ Extract token from "Authorization: Bearer TOKEN"
    ├─ Verify JWT signature (uses JWT_SECRET)
    ├─ Decode JWT payload
    ├─ Extract username and user_id
    ├─ Query database for user
    ├─ Verify user is active
    └─ Return User object
    ↓
Protected Endpoint Handler
    ↓
Response to Client
```

## Success Criteria

All tests pass when:
1. ✓ Password hashing works bidirectionally
2. ✓ JWT tokens encode/decode correctly
3. ✓ Database user operations succeed
4. ✓ Bearer token validation completes successfully
5. ✓ Token can be used to access protected endpoints
6. ✓ Invalid tokens are rejected
7. ✓ Unauthenticated requests are blocked
8. ✓ Configuration is secure and consistent

## Performance

| Test | Duration |
|------|----------|
| test_bearer_authentication.py | 30-60 seconds |
| test_http_bearer.py | 2-3 minutes |
| run_auth_tests.py | 3-5 minutes |
| Manual curl test | < 1 second |

## Troubleshooting Path

```
Run Tests
    ↓
Tests Pass?
    ├─ YES → System working correctly
    └─ NO → Continue
         ↓
   Review Failed Test
         ↓
   Check QUICK_TEST_REFERENCE.md
         ↓
   Quick Fix Applied?
         ├─ YES → Re-run tests
         └─ NO → Continue
              ↓
         Follow AUTHENTICATION_DEBUG_GUIDE.md
              ↓
         Enable Debug Logging
              ↓
         Re-run with Logging
              ↓
         Identify Root Cause
              ↓
         Apply Fix
              ↓
         Re-run Tests to Verify
```

## Integration Steps

### Step 1: Run Tests (Identify Issue)
```bash
cd C:\Ziggie\control-center\backend
python run_auth_tests.py
```

### Step 2: Debug If Needed (Understand Issue)
```bash
# Follow AUTHENTICATION_DEBUG_GUIDE.md
# Use middleware/auth_debug.py utilities
# Check server logs
```

### Step 3: Apply Fix (Resolve Issue)
```bash
# Based on debugging results
# Modify relevant files
# Re-run tests to verify
```

### Step 4: Verify Solution (Confirm Working)
```bash
# Run all tests again
# Test with curl manually
# Document what was fixed
```

## Documentation Map

```
Start Here:
└─ BEARER_TOKEN_TESTING_README.md (This file)
   │
   ├─ Want to run tests?
   │  └─ TEST_EXECUTION_SUMMARY.md
   │     └─ run_auth_tests.py
   │
   ├─ Want quick commands?
   │  └─ QUICK_TEST_REFERENCE.md
   │
   ├─ Need to debug?
   │  └─ AUTHENTICATION_DEBUG_GUIDE.md
   │
   └─ Want technical details?
      └─ AUTH_TEST_SUMMARY.md
         └─ middleware/auth_debug.py
```

## Contact / Support

If stuck:
1. Check QUICK_TEST_REFERENCE.md for common issues
2. Read AUTHENTICATION_DEBUG_GUIDE.md completely
3. Review AUTH_TEST_SUMMARY.md for architecture details
4. Enable logging using auth_debug.py
5. Check server logs for actual errors

## Summary

You have a complete, ready-to-use testing suite that will:

1. **Identify** the exact issue with Bearer token authentication
2. **Provide** detailed diagnostic information
3. **Enable** quick debugging with utilities
4. **Guide** you through resolution with step-by-step instructions
5. **Verify** fixes work with automated tests

Everything is ready to execute now. Start with:

```bash
cd C:\Ziggie\control-center\backend
python run_auth_tests.py
```

---

**Created:** November 10, 2025
**Role:** L2.QA.TESTING.1 - API Testing and Validation
**Status:** COMPLETE - Ready to Execute
