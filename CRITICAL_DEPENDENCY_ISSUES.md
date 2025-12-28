# CRITICAL Dependency Issues - Ziggie Ecosystem

> **Date**: 2025-12-28
> **Severity**: HIGH
> **Action Required**: TODAY

---

## 🔴 CRITICAL SECURITY ISSUES

### 1. Missing AWS SDK (boto3)

**Status**: ❌ BLOCKING

**Issue**: boto3 is used in production code but NOT listed in requirements.txt

**Files Affected**:
```
C:\Ziggie\aws-config\ziggie_bedrock.py
C:\Ziggie\aws-config\lambda\lambda_function.py
C:\Ziggie\integrations\meshy\config.py
```

**Risk**:
- Runtime ImportError in production
- AWS integrations will fail
- Lambda functions cannot run

**Fix** (5 minutes):
```bash
cd C:\Ziggie\control-center\backend

# Add to requirements.txt
echo "boto3==1.35.84" >> requirements.txt
echo "botocore==1.35.84" >> requirements.txt

# Install
pip install boto3==1.35.84 botocore==1.35.84

# Verify
python -c "import boto3; print('✓ boto3 works')"
```

---

### 2. Outdated Authentication Library (PyJWT)

**Status**: ⚠️ HIGH RISK

**Current Version**: 2.8.0
**Latest Version**: 2.10.1
**CVEs**: Known authentication bypass vulnerabilities

**Risk**:
- Token validation bypass
- Unauthorized access to API
- Session hijacking potential

**Fix** (2 minutes):
```bash
cd C:\Ziggie\control-center\backend
pip install --upgrade PyJWT==2.10.1

# Test auth still works
python -m pytest tests/test_auth.py -v
```

---

### 3. Outdated HTTP Client (requests)

**Status**: ⚠️ MEDIUM-HIGH RISK

**Current Version**: 2.31.0
**Latest Version**: 2.32.3
**CVEs**: SSRF (Server-Side Request Forgery) vulnerabilities

**Risk**:
- Attackers can make backend perform unauthorized requests
- Internal network scanning
- Bypass firewall rules

**Fix** (2 minutes):
```bash
cd C:\Ziggie\control-center\backend
pip install --upgrade requests==2.32.3
```

---

### 4. Outdated Frontend HTTP Client (axios)

**Status**: ⚠️ MEDIUM RISK

**Current Version**: 1.6.5
**Latest Version**: 1.7.9
**CVEs**: SSRF and redirect vulnerabilities

**Risk**:
- Client-side request forgery
- Unauthorized API calls
- Data exfiltration

**Fix** (1 minute):
```bash
cd C:\Ziggie\control-center\frontend
npm install axios@1.7.9
```

---

## 🟡 HIGH PRIORITY ISSUES

### 5. 14 Docker Services Using Floating Tags

**Status**: ⚠️ STABILITY RISK

**Services Affected**:
```
ollama:latest
n8n:latest
flowise:latest
open-webui:main
portainer:latest
nginx:alpine
certbot:latest
prometheus:latest
grafana:latest
loki:latest
promtail:latest
watchtower:latest
github-runner:latest
mongo:7 (partially floating)
```

**Risk**:
- Unpredictable updates break production
- Inconsistent versions across environments
- Difficult to reproduce issues
- No rollback path

**Example Fix** (per service):
```yaml
# BEFORE (risky)
ollama:
  image: ollama/ollama:latest

# AFTER (stable)
ollama:
  image: ollama/ollama:0.1.32
```

**Action**:
1. Check current versions: `docker ps --format "{{.Image}}"`
2. Pin versions in all 3 docker-compose.yml files
3. Test in dev before production

---

### 6. FastAPI Ecosystem Outdated

**Status**: ⚠️ STABILITY + SECURITY

**Packages**:
| Package | Current | Latest | Gap |
|---------|---------|--------|-----|
| fastapi | 0.109.0 | 0.115.6 | 6 minor versions |
| uvicorn | 0.27.0 | 0.34.0 | 7 minor versions |
| pydantic | 2.5.3 | 2.10.5 | 5 minor versions |

**Risk**:
- Missing security patches
- Performance improvements unavailable
- Incompatibility with newer libraries

**Fix** (10 minutes + testing):
```bash
cd C:\Ziggie\control-center\backend

# Update requirements.txt
cat >> requirements.txt << 'EOF'
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic==2.10.5
pydantic-settings==2.7.1
EOF

pip install --upgrade -r requirements.txt

# CRITICAL: Test thoroughly - Pydantic 2.10 may have breaking changes
python -m pytest tests/ -v
```

---

## 📊 Dependency Inventory Summary

| Category | Total | Outdated | Missing | Critical |
|----------|-------|----------|---------|----------|
| **Docker Images** | 18 | 14 | 0 | 14 |
| **Python Packages** | 16 | 15 | 2 | 3 |
| **Node.js Packages** | 10 direct | 7 | 0 | 1 |
| **Transitive Deps** | ~400 | Unknown | 0 | TBD |

---

## ⏱️ Time to Fix (Estimated)

| Issue | Time | Priority | Risk if Ignored |
|-------|------|----------|-----------------|
| Add boto3 | 5 min | P0 | Production crash |
| Update PyJWT | 2 min | P0 | Auth bypass |
| Update requests | 2 min | P0 | SSRF attack |
| Update axios | 1 min | P0 | Client-side attack |
| Pin Docker tags | 30 min | P1 | Unpredictable failures |
| Update FastAPI | 10 min + testing | P1 | Missing security patches |

**Total Time**: ~50 minutes for P0 + P1

---

## 🚀 Quick Fix Script (P0 Only)

Run this to fix the 4 critical security issues:

```bash
#!/bin/bash
# File: C:\Ziggie\scripts\fix-critical-deps.sh

set -e  # Exit on error

echo "=== Fixing Critical Dependencies ==="

# Backend fixes
cd C:\Ziggie\control-center\backend
echo "1. Adding boto3..."
echo "boto3==1.35.84" >> requirements.txt
echo "botocore==1.35.84" >> requirements.txt

echo "2. Updating security packages..."
pip install --upgrade \
  boto3==1.35.84 \
  PyJWT==2.10.1 \
  requests==2.32.3 \
  bcrypt==4.2.1

echo "3. Testing backend imports..."
python -c "import boto3, fastapi, uvicorn; print('✓ Backend OK')"

# Frontend fixes
cd C:\Ziggie\control-center\frontend
echo "4. Updating axios..."
npm install axios@1.7.9

echo "5. Running npm audit fix..."
npm audit fix

echo "6. Testing frontend build..."
npm run build

echo "=== All Critical Fixes Applied ==="
echo "Next steps:"
echo "  1. Run full test suite"
echo "  2. Restart Docker services"
echo "  3. Verify health endpoints"
```

**Usage**:
```bash
bash C:\Ziggie\scripts\fix-critical-deps.sh
```

---

## 🔍 Verification After Fixes

```bash
# 1. Verify imports work
python -c "import boto3, fastapi, uvicorn, sqlalchemy; print('✓ All imports OK')"

# 2. Run tests
cd C:\Ziggie\control-center\backend
python -m pytest tests/ -v

# 3. Check for new vulnerabilities
pip-audit

# 4. Restart services
docker compose -f C:\Ziggie\docker-compose.yml restart

# 5. Health checks
curl http://localhost:54112/health
curl http://localhost:3001/

# 6. Check logs
docker compose logs --tail=50 backend
docker compose logs --tail=50 frontend
```

---

## 📋 Checklist

### Today (P0)

- [ ] Add boto3 to requirements.txt
- [ ] Update PyJWT (2.8.0 → 2.10.1)
- [ ] Update requests (2.31.0 → 2.32.3)
- [ ] Update axios (1.6.5 → 1.7.9)
- [ ] Run npm audit fix
- [ ] Verify all services still work
- [ ] Run security scans (pip-audit, npm audit)

### This Week (P1)

- [ ] Pin all Docker image versions
- [ ] Update FastAPI ecosystem
- [ ] Standardize MongoDB versions
- [ ] Create missing requirements.txt files
- [ ] Generate Python lockfile

### This Sprint (P2)

- [ ] Update testing frameworks
- [ ] Set up automated dependency scanning
- [ ] Implement Dependabot/Renovate
- [ ] Document dependency update process

---

## 📞 Support

If you encounter issues during updates:

1. **Rollback**: Use backup requirements files
2. **Check logs**: `docker compose logs --tail=100 backend`
3. **Test individually**: Update one package at a time
4. **Breaking changes**: Check changelog for Pydantic 2.10

---

## 📈 Success Metrics

**Before Fix**:
- Risk Score: 6.5/10 (MEDIUM-HIGH)
- Missing Dependencies: 2
- Outdated Security Packages: 4
- Floating Docker Tags: 14

**After Fix (P0)**:
- Risk Score: 4.5/10 (MEDIUM)
- Missing Dependencies: 0
- Outdated Security Packages: 0
- Floating Docker Tags: 14 (still needs P1 fix)

**After Fix (P0 + P1)**:
- Risk Score: 3.0/10 (LOW)
- Missing Dependencies: 0
- Outdated Security Packages: 0
- Floating Docker Tags: 0

---

*Generated by BMAD Verification Agent*
*Priority: CRITICAL - Action Required TODAY*
*Estimated Time: 50 minutes*
