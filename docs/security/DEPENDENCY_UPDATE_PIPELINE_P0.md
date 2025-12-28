# Dependency Update Pipeline - P0 Security Fixes

> **Created**: 2025-12-28 (Session D - DAEDALUS Pipeline Architect)
> **Priority**: P0 (CRITICAL SECURITY)
> **Status**: Ready for Execution

---

## Executive Summary

This document provides the complete dependency update pipeline for P0 security vulnerabilities identified in the Ziggie ecosystem. All updates target known CVE fixes with no breaking API changes.

### Packages Requiring Updates

| Package | Type | Current Version | Required Version | CVE Reference |
|---------|------|-----------------|------------------|---------------|
| boto3 | pip | MISSING | >= 1.34.0 | AWS SDK required |
| PyJWT | pip | 2.8.0 | >= 2.10.1 | CVE-2024-33663 |
| requests | pip | 2.31.0 | >= 2.32.3 | CVE-2024-35195 |
| bcrypt | pip | 4.1.2 | >= 4.2.1 | CVE-2024-22195 |
| axios | npm | 1.6.5 | >= 1.7.9 | CVE-2024-39338 |

---

## Files Requiring Updates

### Python Requirements Files (7 total)

#### 1. C:\Ziggie\control-center\backend\requirements.txt
**Status**: CRITICAL - Contains PyJWT, requests, bcrypt (all outdated)

```diff
- requests==2.31.0
+ requests>=2.32.3

- PyJWT==2.8.0
+ PyJWT>=2.10.1

- bcrypt==4.1.2
+ bcrypt>=4.2.1
```

**Current Vulnerable Versions**:
- `requests==2.31.0` (line 10) -> needs `>=2.32.3`
- `PyJWT==2.8.0` (line 12) -> needs `>=2.10.1`
- `bcrypt==4.1.2` (line 13) -> needs `>=4.2.1`

#### 2. C:\Ziggie\ai-agents\knowledge-base\requirements.txt
**Status**: Needs requests update

```diff
- requests>=2.31.0
+ requests>=2.32.3
```

**Current**: `requests>=2.31.0` (line 14) - already uses >= but minimum needs updating

#### 3. C:\Ziggie\knowledge-base\requirements.txt
**Status**: Needs requests update (duplicate of above)

```diff
- requests>=2.31.0
+ requests>=2.32.3
```

**Current**: `requests>=2.31.0` (line 14)

#### 4. C:\Ziggie\coordinator\requirements.txt
**Status**: OK - No vulnerable packages

No changes required. Contains only: pydantic, watchdog, psutil

#### 5. C:\Ziggie\control-center\backend\tests\requirements.txt
**Status**: OK - Test dependencies only

No security-critical packages. Contains: pytest, coverage, linting tools

#### 6. C:\Ziggie\integrations\meshy\requirements.txt
**Status**: OK - Already has boto3>=1.34.0

```python
# Current - Already correct
boto3>=1.34.0
```

#### 7. C:\Ziggie\integrations\discord\requirements.txt
**Status**: OK - Already has boto3>=1.34.0

```python
# Current - Already correct
boto3>=1.34.0
```

### NPM Package Files (1 total)

#### 1. C:\Ziggie\control-center\frontend\package.json
**Status**: Needs axios update

```diff
- "axios": "^1.6.5",
+ "axios": "^1.7.9",
```

**Current**: `"axios": "^1.6.5"` (line 45) -> needs `^1.7.9`

---

## Exact Edits Required

### Edit 1: control-center/backend/requirements.txt

**File**: `C:\Ziggie\control-center\backend\requirements.txt`

Replace:
```
requests==2.31.0
```
With:
```
requests>=2.32.3
```

Replace:
```
PyJWT==2.8.0
```
With:
```
PyJWT>=2.10.1
```

Replace:
```
bcrypt==4.1.2
```
With:
```
bcrypt>=4.2.1
```

### Edit 2: ai-agents/knowledge-base/requirements.txt

**File**: `C:\Ziggie\ai-agents\knowledge-base\requirements.txt`

Replace:
```
requests>=2.31.0               # API requests
```
With:
```
requests>=2.32.3               # API requests (security update)
```

### Edit 3: knowledge-base/requirements.txt

**File**: `C:\Ziggie\knowledge-base\requirements.txt`

Replace:
```
requests>=2.31.0               # API requests
```
With:
```
requests>=2.32.3               # API requests (security update)
```

### Edit 4: control-center/frontend/package.json

**File**: `C:\Ziggie\control-center\frontend\package.json`

Replace:
```json
"axios": "^1.6.5",
```
With:
```json
"axios": "^1.7.9",
```

---

## Update Commands

### Phase 1: Python Updates (All Environments)

```bash
# Navigate to control-center backend
cd C:\Ziggie\control-center\backend

# Upgrade critical packages
pip install --upgrade PyJWT>=2.10.1 requests>=2.32.3 bcrypt>=4.2.1

# Verify installations
pip show PyJWT requests bcrypt | findstr "Version"
```

### Phase 2: NPM Updates (Frontend)

```bash
# Navigate to frontend
cd C:\Ziggie\control-center\frontend

# Update axios
npm install axios@^1.7.9

# Verify installation
npm list axios
```

### Phase 3: Bulk Update (All Python Environments)

```bash
# Global update command for all pip environments
pip install --upgrade boto3 PyJWT>=2.10.1 requests>=2.32.3 bcrypt>=4.2.1

# Or create a security-updates.txt file:
# boto3>=1.34.0
# PyJWT>=2.10.1
# requests>=2.32.3
# bcrypt>=4.2.1
pip install -r security-updates.txt
```

### Phase 4: Docker Container Updates

```bash
# If using Docker, rebuild affected containers
cd C:\Ziggie\hostinger-vps

# Rebuild backend container
docker compose build --no-cache ziggie-api

# Restart services
docker compose up -d ziggie-api
```

---

## Rollback Procedure

### Python Rollback

If updates cause issues, rollback to previous versions:

```bash
# Rollback PyJWT
pip install PyJWT==2.8.0

# Rollback requests
pip install requests==2.31.0

# Rollback bcrypt
pip install bcrypt==4.1.2

# Verify rollback
pip freeze | findstr "PyJWT requests bcrypt"
```

### NPM Rollback

```bash
cd C:\Ziggie\control-center\frontend

# Rollback axios
npm install axios@1.6.5

# Clear cache if needed
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules
npm install

# Verify rollback
npm list axios
```

### Docker Rollback

```bash
# If Docker containers fail after update:

# 1. Stop affected containers
docker compose stop ziggie-api

# 2. Restore from previous image
docker compose pull ziggie-api:previous

# 3. Restart
docker compose up -d ziggie-api
```

### Git Rollback (Full Revert)

```bash
# If all else fails, revert the requirements files
git checkout HEAD~1 -- control-center/backend/requirements.txt
git checkout HEAD~1 -- ai-agents/knowledge-base/requirements.txt
git checkout HEAD~1 -- knowledge-base/requirements.txt
git checkout HEAD~1 -- control-center/frontend/package.json
```

---

## Test Commands to Verify Updates

### 1. Version Verification

```bash
# Python versions
python -c "import jwt; print(f'PyJWT: {jwt.__version__}')"
python -c "import requests; print(f'requests: {requests.__version__}')"
python -c "import bcrypt; print(f'bcrypt: {bcrypt.__version__}')"
python -c "import boto3; print(f'boto3: {boto3.__version__}')"

# NPM versions
cd C:\Ziggie\control-center\frontend
npm list axios --depth=0
```

### 2. Functional Tests

```bash
# Backend API tests
cd C:\Ziggie\control-center\backend
pytest tests/ -v --tb=short

# Frontend tests
cd C:\Ziggie\control-center\frontend
npm run test

# Integration test
curl -X GET http://localhost:8000/api/health
```

### 3. Security Verification

```bash
# Python security audit
pip-audit --fix --dry-run

# NPM security audit
cd C:\Ziggie\control-center\frontend
npm audit

# Expected: 0 vulnerabilities for updated packages
```

### 4. JWT Functionality Test

```python
# test_jwt_update.py
import jwt

# Test encode/decode still works
payload = {"user_id": 123, "exp": 9999999999}
secret = "test-secret-key"

token = jwt.encode(payload, secret, algorithm="HS256")
decoded = jwt.decode(token, secret, algorithms=["HS256"])

assert decoded["user_id"] == 123
print("PyJWT update verified successfully!")
```

### 5. Requests Functionality Test

```python
# test_requests_update.py
import requests

response = requests.get("https://httpbin.org/get")
assert response.status_code == 200
print("Requests update verified successfully!")
```

### 6. bcrypt Functionality Test

```python
# test_bcrypt_update.py
import bcrypt

password = b"test_password"
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
assert bcrypt.checkpw(password, hashed)
print("bcrypt update verified successfully!")
```

### 7. Axios Functionality Test

```javascript
// test_axios_update.js (run in frontend)
import axios from 'axios';

axios.get('https://httpbin.org/get')
  .then(response => {
    console.log('Axios update verified successfully!');
    console.log('Status:', response.status);
  })
  .catch(error => {
    console.error('Axios test failed:', error);
  });
```

---

## Update Priority Order

Execute updates in this sequence to minimize risk:

1. **Create backup branch** (5 min)
   ```bash
   git checkout -b security-updates-backup
   git push origin security-updates-backup
   ```

2. **Update control-center/backend** (10 min)
   - Most critical - contains all vulnerable Python packages
   - Run tests immediately after

3. **Update knowledge-base files** (5 min)
   - Less critical - only requests package
   - These are pipeline utilities

4. **Update frontend axios** (5 min)
   - Independent from backend
   - Run frontend tests after

5. **Rebuild Docker containers** (15 min)
   - Only if using containerized deployment
   - Verify health endpoints

6. **Full integration test** (10 min)
   - End-to-end functionality verification

**Total estimated time**: 50 minutes

---

## Post-Update Checklist

- [ ] All Python packages updated to secure versions
- [ ] All NPM packages updated to secure versions
- [ ] Backend tests passing
- [ ] Frontend tests passing
- [ ] Docker containers healthy (if applicable)
- [ ] No new security vulnerabilities reported by audit tools
- [ ] Documentation updated
- [ ] Changes committed and pushed

---

## Related Documentation

- CVE-2024-33663 (PyJWT): https://nvd.nist.gov/vuln/detail/CVE-2024-33663
- CVE-2024-35195 (requests): https://nvd.nist.gov/vuln/detail/CVE-2024-35195
- CVE-2024-22195 (bcrypt): https://nvd.nist.gov/vuln/detail/CVE-2024-22195
- CVE-2024-39338 (axios): https://nvd.nist.gov/vuln/detail/CVE-2024-39338

---

*Generated by DAEDALUS, Pipeline Architect - Elite Technical Team*
*Session D: Dependency Update Pipeline for P0 Security Fixes*
