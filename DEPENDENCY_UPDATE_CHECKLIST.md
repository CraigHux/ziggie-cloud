# Ziggie Dependency Update Checklist

> **Quick action guide for dependency updates**
> **Source**: DEPENDENCY_AUDIT_REPORT.md

---

## TODAY (P0 - Security Critical)

### Backend Security Updates

```bash
# Navigate to backend directory
cd C:\Ziggie\control-center\backend

# Backup current requirements
cp requirements.txt requirements.txt.backup

# Update requirements.txt with critical patches
cat >> requirements.txt << EOF
# AWS SDK (MISSING - CRITICAL)
boto3==1.35.84
botocore==1.35.84

# Security Updates (2025-12-28)
PyJWT==2.10.1        # Was 2.8.0 - Auth bypass fixes
requests==2.32.3     # Was 2.31.0 - SSRF patches
bcrypt==4.2.1        # Was 4.1.2 - Password hashing improvements
EOF

# Install updates
pip install --upgrade -r requirements.txt

# Test backend still works
python -m pytest tests/
```

### Frontend Security Updates

```bash
# Navigate to frontend directory
cd C:\Ziggie\control-center\frontend

# Update axios (SSRF vulnerability)
npm install axios@1.7.9

# Run audit and auto-fix safe issues
npm audit fix

# Test frontend still works
npm run test
```

### Verify Services

```bash
# Restart Docker services
docker compose -f C:\Ziggie\docker-compose.yml restart backend frontend

# Check health
curl http://localhost:54112/health
curl http://localhost:3001/
```

---

## THIS WEEK (P1 - High Priority)

### Pin Docker Image Versions

**File**: `C:\Ziggie\hostinger-vps\docker-compose.yml`

```bash
# Check current running versions
docker ps --format "table {{.Names}}\t{{.Image}}"

# For each service, update docker-compose.yml:
```

**Replace**:
```yaml
# BEFORE
ollama:
  image: ollama/ollama:latest

n8n:
  image: n8nio/n8n:latest

flowise:
  image: flowiseai/flowise:latest
```

**With** (example - check actual versions):
```yaml
# AFTER
ollama:
  image: ollama/ollama:0.1.32  # Pin to specific version

n8n:
  image: n8nio/n8n:1.65.3      # Pin to specific version

flowise:
  image: flowiseai/flowise:1.6.5  # Pin to specific version
```

### Update FastAPI Ecosystem

```bash
cd C:\Ziggie\control-center\backend

# Update requirements.txt
cat > requirements.txt.new << 'EOF'
fastapi==0.115.6        # Was 0.109.0
uvicorn[standard]==0.34.0  # Was 0.27.0
websockets==14.1        # Was 12.0
psutil==6.1.1           # Was 5.9.8
sqlalchemy==2.0.36      # Was 2.0.25
aiosqlite==0.20.0       # Was 0.19.0
pydantic==2.10.5        # Was 2.5.3 - CHECK BREAKING CHANGES
pydantic-settings==2.7.1  # Was 2.1.0
python-dotenv==1.0.1    # Was 1.0.0
requests==2.32.3        # Was 2.31.0 (security)
slowapi==0.1.9          # Current
PyJWT==2.10.1           # Was 2.8.0 (security)
bcrypt==4.2.1           # Was 4.1.2 (security)
python-multipart==0.0.20  # Was 0.0.6
email-validator==2.2.0  # Was 2.1.1
httpx==0.28.1           # Was 0.27.0
boto3==1.35.84          # NEW - AWS SDK
botocore==1.35.84       # NEW - boto3 core
watchdog==6.0.0         # NEW - coordinator dependency
EOF

# Review changes
diff requirements.txt requirements.txt.new

# Apply changes (after review)
mv requirements.txt.new requirements.txt

# Install
pip install --upgrade -r requirements.txt

# Test thoroughly
python -m pytest tests/ -v
```

### Run Security Scans

```bash
# Install scanning tools
pip install pip-audit safety

# Python security scan
cd C:\Ziggie\control-center\backend
pip-audit -r requirements.txt --format json --output audit.json

# Node.js security scan
cd C:\Ziggie\control-center\frontend
npm audit --json > npm-audit.json

# Review reports
cat audit.json
cat npm-audit.json
```

---

## THIS SPRINT (P2 - Medium Priority)

### Standardize MongoDB Versions

**Files to update**:
- `C:\Ziggie\docker-compose.yml`
- `C:\Ziggie\hostinger-vps\docker-compose.yml`
- `C:\Ziggie\ziggie-cloud-repo\docker-compose.yml`

**Change**:
```yaml
# Standardize on specific version
mongodb:
  image: mongo:7.0.14  # Was mongo:7 or mongo:7.0
```

### Create Missing requirements.txt Files

```bash
# For sim-studio
cat > C:\Ziggie\ziggie-cloud-repo\sim-studio\requirements.txt << 'EOF'
fastapi==0.115.6
uvicorn==0.34.0
httpx==0.28.1
pydantic==2.10.5
websockets==14.1
EOF

# For api
cat > C:\Ziggie\ziggie-cloud-repo\api\requirements.txt << 'EOF'
fastapi==0.115.6
uvicorn==0.34.0
httpx==0.28.1
pydantic==2.10.5
EOF

# Update Dockerfiles to use requirements.txt
```

**Update Dockerfile**:
```dockerfile
# BEFORE
RUN pip install --no-cache-dir fastapi uvicorn httpx pydantic

# AFTER
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

### Update Testing Dependencies

```bash
cd C:\Ziggie\control-center\backend\tests

# Update tests/requirements.txt
cat > requirements.txt.new << 'EOF'
# Testing frameworks
pytest==8.3.4           # Was 7.4.3
pytest-asyncio==0.24.0  # Was 0.21.1
pytest-cov==6.0.0       # Was 4.1.0
pytest-mock==3.14.0     # Was 3.12.0

# HTTP testing
httpx==0.28.1           # Was 0.27.0
requests-mock==1.11.0   # Current

# Web framework testing
fastapi==0.115.6        # Match main requirements
starlette==0.41.3       # Match fastapi

# WebSocket testing
websockets==14.1        # Match main requirements
python-socketio==5.11.0  # Current

# Mocking
unittest-mock==1.5.0    # Current
responses==0.24.1       # Current

# Database testing
pytest-postgresql==5.0.0  # Current

# Performance testing
locust==2.32.5          # Was 2.19.1

# Test data generation
faker==33.1.0           # Was 20.1.0
factory-boy==3.3.0      # Current

# Code coverage
coverage==7.3.2         # Current

# Linting & quality
pylint==3.3.3           # Was 3.0.3
flake8==7.1.1           # Was 6.1.0
black==24.12.0          # Was 23.12.1
mypy==1.14.0            # Was 1.7.1

# API client
python-multipart==0.0.20  # Match main requirements
EOF

# Apply changes
mv requirements.txt.new requirements.txt

# Install
pip install -r requirements.txt
```

### Generate Python Lockfile

```bash
cd C:\Ziggie\control-center\backend

# Option 1: Simple freeze
pip freeze > requirements.lock

# Option 2: Use pip-tools (better)
pip install pip-tools
pip-compile requirements.txt --output-file=requirements.lock

# Add to .gitignore if environment-specific
```

---

## AUTOMATION SETUP (P3 - Backlog)

### GitHub Actions Workflow

**File**: `.github/workflows/dependency-audit.yml`

```yaml
name: Dependency Audit

on:
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday
  pull_request:
    paths:
      - '**/requirements.txt'
      - '**/package.json'
      - '**/docker-compose.yml'
  workflow_dispatch:  # Manual trigger

jobs:
  audit-python:
    name: Python Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install pip-audit
        run: pip install pip-audit

      - name: Scan backend dependencies
        run: pip-audit -r control-center/backend/requirements.txt --format json --output audit-backend.json

      - name: Upload audit results
        uses: actions/upload-artifact@v4
        with:
          name: python-audit
          path: audit-backend.json

  audit-node:
    name: Node.js Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        working-directory: control-center/frontend
        run: npm ci

      - name: Run npm audit
        working-directory: control-center/frontend
        run: npm audit --json > npm-audit.json || true

      - name: Upload audit results
        uses: actions/upload-artifact@v4
        with:
          name: node-audit
          path: control-center/frontend/npm-audit.json

  audit-docker:
    name: Docker Image Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Scan Docker images with Trivy
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'config'
          scan-ref: '.'
          format: 'json'
          output: 'trivy-results.json'

      - name: Upload Trivy results
        uses: actions/upload-artifact@v4
        with:
          name: docker-scan
          path: trivy-results.json
```

### Dependabot Configuration

**File**: `.github/dependabot.yml`

```yaml
version: 2
updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/control-center/backend"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 10
    reviewers:
      - "your-username"
    labels:
      - "dependencies"
      - "python"

  # Node.js dependencies
  - package-ecosystem: "npm"
    directory: "/control-center/frontend"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 10
    reviewers:
      - "your-username"
    labels:
      - "dependencies"
      - "javascript"

  # Docker dependencies
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 5
    reviewers:
      - "your-username"
    labels:
      - "dependencies"
      - "docker"
```

---

## VERIFICATION COMMANDS

### After Updates - Verify Everything Works

```bash
# Python backend
cd C:\Ziggie\control-center\backend
python -c "import fastapi, uvicorn, sqlalchemy, boto3; print('✓ All imports work')"
python -m pytest tests/ -v

# Node.js frontend
cd C:\Ziggie\control-center\frontend
npm run lint
npm run test
npm run build  # Ensure build still works

# Docker services
docker compose -f C:\Ziggie\docker-compose.yml up -d
docker compose ps  # All should be "healthy"

# API health checks
curl http://localhost:54112/health  # Backend
curl http://localhost:3001/         # Frontend

# Check logs for errors
docker compose logs --tail=50 backend
docker compose logs --tail=50 frontend
```

### Check for New Vulnerabilities

```bash
# Python
pip-audit

# Node.js
npm audit

# Docker (requires trivy installed)
trivy image ziggie-backend:latest
trivy image ziggie-frontend:latest
```

---

## ROLLBACK PLAN

If updates break something:

```bash
# Python - rollback to backup
cd C:\Ziggie\control-center\backend
cp requirements.txt.backup requirements.txt
pip install -r requirements.txt

# Node.js - rollback via package-lock.json
cd C:\Ziggie\control-center\frontend
git checkout package-lock.json
npm ci  # Install exact versions from lockfile

# Docker - use previous image tags
docker compose down
git checkout docker-compose.yml
docker compose up -d
```

---

## NOTES

- **Always test in dev/staging before production**
- **Keep backup of working requirements files**
- **Check changelogs for breaking changes** (especially Pydantic 2.5 → 2.10)
- **Update one category at a time** (Python, then Node.js, then Docker)
- **Monitor logs after each update**

---

*Generated: 2025-12-28*
*Source: BMAD Verification Agent*
