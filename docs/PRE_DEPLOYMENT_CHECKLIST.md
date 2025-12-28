# Pre-Deployment Validation Checklist
**Repository**: CraigHux/ziggie-cloud
**Author**: DAEDALUS (Pipeline Architect)
**Created**: 2025-12-28

---

## Overview

Complete this checklist before EVERY deployment to production. This ensures 100% compliance with quality gates and Know Thyself principles.

**Mandatory Completion**: All items must be checked before pushing to main branch.

---

## Checklist

### 1. Code Quality (Stage 1 Equivalent)

#### Python Code
- [ ] Run `flake8 control-center/backend` - 0 critical errors (E9, F63, F7, F82)
- [ ] Run `black --check control-center/backend` - all files formatted
- [ ] Run `pylint control-center/backend` - score > 8.0/10
- [ ] Run `bandit -r control-center/backend` - no high/critical issues

#### JavaScript Code
- [ ] Run `npm run lint` in `control-center/frontend` - 0 errors
- [ ] Run `npm run build` - build succeeds
- [ ] Check bundle size - no significant increase (>10%)

#### Security
- [ ] No API keys in code files
- [ ] No hardcoded passwords
- [ ] No secrets committed to repository
- [ ] `.env.example` updated with new variables (if any)
- [ ] Secrets properly configured in GitHub (if new ones needed)

#### Configuration
- [ ] `docker-compose.yml` syntax valid: `docker compose config --quiet`
- [ ] All YAML files valid: `yamllint -d relaxed **/*.yml`
- [ ] No `latest` tags in Dockerfiles (pinned versions)
- [ ] Healthcheck present in all service Dockerfiles

---

### 2. Testing (Stage 2 - CRITICAL)

#### Zero Tolerance - test.skip()
- [ ] **CRITICAL**: Scan for Python skips: `grep -r "@pytest.mark.skip" control-center/backend`
- [ ] **CRITICAL**: Scan for JavaScript skips: `grep -r "test.skip\|it.skip\|describe.skip" control-center/frontend`
- [ ] **RESULT**: ZERO violations found (if found, STOP and fix)

#### Python Tests
- [ ] Run `pytest control-center/backend/tests/ -v`
- [ ] All tests PASS (100% pass rate)
- [ ] Coverage > 70%: `pytest --cov=control-center/backend --cov-report=term`
- [ ] No flaky tests (run tests 3 times, all pass)

#### JavaScript Tests
- [ ] Run `npm test` in `control-center/frontend`
- [ ] All tests PASS (100% pass rate)
- [ ] Coverage > 70%: `npm run test:coverage`

#### Integration Tests
- [ ] API endpoints return expected responses
- [ ] Database connections work
- [ ] External service integrations tested (if applicable)

---

### 3. Build (Stage 3 Equivalent)

#### Docker Images
- [ ] Build ziggie-api: `docker build -t ziggie-api:test control-center/backend`
- [ ] Build mcp-gateway: `docker build -t mcp-gateway:test mcp-gateway`
- [ ] Build sim-studio: `docker build -t sim-studio:test sim-studio`
- [ ] All builds succeed without errors
- [ ] Images start successfully: `docker run --rm <image>:test --help`

#### Docker Compose
- [ ] Run full stack locally: `docker compose up -d`
- [ ] All services start: `docker compose ps`
- [ ] Health checks pass: `docker compose ps` (all "healthy")
- [ ] No error logs: `docker compose logs | grep -i error`

---

### 4. Pre-Deployment (Stage 4 Preparation)

#### Environment
- [ ] VPS accessible: `ssh root@82.25.112.73 "echo 'OK'"`
- [ ] Disk space > 10GB: `ssh root@82.25.112.73 "df -h /opt/ziggie"`
- [ ] Self-hosted runner online: `gh api repos/CraigHux/ziggie-cloud/actions/runners`
- [ ] GitHub Actions quota available (not near limit)

#### Secrets
- [ ] All required secrets set in GitHub: `gh secret list`
- [ ] Secrets match VPS `.env` file (spot check 3 random secrets)
- [ ] No expired API keys (OpenAI, Anthropic, AWS, GitHub)

#### Database
- [ ] Database migrations ready (if any): `alembic check` or equivalent
- [ ] Migration scripts tested locally
- [ ] Backup plan defined (automated backup will run, but confirm)

#### Rollback Plan
- [ ] Know which commit to rollback to: `git log --oneline -5`
- [ ] Rollback procedure reviewed (see ROLLBACK_PLAYBOOK.md)
- [ ] Emergency contact reachable (if business-critical deployment)

---

### 5. Documentation

#### Code Changes
- [ ] Code changes documented in commit messages
- [ ] Breaking changes listed in commit message
- [ ] API changes documented (if any)

#### Deployment Notes
- [ ] Known issues documented
- [ ] Configuration changes noted
- [ ] New environment variables documented

---

### 6. Final Verification

#### Local Testing
- [ ] Manual smoke test performed locally
- [ ] Critical user flows tested
- [ ] No console errors in browser (for frontend changes)
- [ ] No unhandled exceptions in logs (for backend changes)

#### Git
- [ ] On correct branch: `git branch --show-current` → `main`
- [ ] All changes committed: `git status` → "nothing to commit"
- [ ] Pushed to remote: `git push --dry-run` → "Everything up-to-date"

#### Team Communication
- [ ] Team notified of deployment (if during business hours)
- [ ] Known risks communicated
- [ ] Post-deployment monitoring plan confirmed

---

## Deployment Command

Once ALL items above are checked, deploy:

```bash
# Standard deployment (automatic on push to main)
git push origin main

# Monitor deployment
gh run watch

# Or manual trigger
gh workflow run ci-cd-enhanced.yml
```

---

## Post-Deployment Verification (Within 5 Minutes)

After deployment completes, verify:

### 1. Workflow Success
- [ ] GitHub Actions workflow completed: `gh run list --limit 1`
- [ ] All 5 stages passed (Lint, Test, Build, Deploy, Verify)
- [ ] No errors in workflow logs: `gh run view <run-id> --log`

### 2. Service Health
```bash
# All should return {"status":"healthy"}
curl https://ziggie.cloud/api/health
curl https://ziggie.cloud/mcp/health
curl https://ziggie.cloud/sim/health
```

- [ ] Ziggie API healthy
- [ ] MCP Gateway healthy
- [ ] Sim Studio healthy

### 3. Database Connectivity
```bash
ssh root@82.25.112.73 << 'EOF'
  docker exec ziggie-postgres pg_isready -U ziggie
  docker exec ziggie-redis redis-cli ping
  docker exec ziggie-mongodb mongosh --quiet --eval "db.runCommand('ping').ok"
EOF
```

- [ ] PostgreSQL connected
- [ ] Redis connected
- [ ] MongoDB connected

### 4. Container Status
```bash
ssh root@82.25.112.73 "docker ps --format 'table {{.Names}}\t{{.Status}}'"
```

- [ ] All ziggie-* containers "Up" and "healthy"
- [ ] No containers in "Restarting" state

### 5. Smoke Tests
- [ ] Critical API endpoints respond correctly
- [ ] Frontend loads without errors
- [ ] User authentication works
- [ ] Database queries return expected results

---

## Rollback Triggers

If ANY of the following occur within 10 minutes of deployment, initiate rollback:

- [ ] Health check fails
- [ ] Container crashes repeatedly (>3 restarts in 5 minutes)
- [ ] Database connection errors
- [ ] 5XX errors in production logs
- [ ] Critical feature broken
- [ ] Performance degradation >50%

**Rollback Command**:
```bash
gh workflow run rollback.yml \
  -f rollback_type=previous_commit \
  -f reason="<specific reason>"
```

---

## Checklist Templates

### Quick Checklist (Minimal Changes)

For small, low-risk changes:

```
□ No test.skip() violations
□ All tests pass locally
□ Docker build succeeds
□ Secrets validated
□ Rollback plan ready
```

### Full Checklist (Major Changes)

For significant changes, database migrations, or infrastructure updates:

```
Use complete checklist above (all 6 sections)
```

---

## Automated Pre-Deployment Check Script

Run this script before pushing:

```bash
#!/bin/bash
# pre-deploy-check.sh

set -e

echo "=========================================="
echo "Pre-Deployment Validation"
echo "=========================================="

# Stage 1: Code Quality
echo "Stage 1: Code Quality"
flake8 control-center/backend --count --select=E9,F63,F7,F82 --show-source --statistics
black --check control-center/backend
cd control-center/frontend && npm run lint && cd ../..

# Stage 2: Test.skip() Detection (CRITICAL)
echo "Stage 2: CRITICAL - test.skip() Detection"
PYTHON_SKIPS=$(grep -r "@pytest.mark.skip\|@unittest.skip\|pytest.skip" control-center/backend --include="test_*.py" || true)
JS_SKIPS=$(grep -r "test.skip\|it.skip\|describe.skip" control-center/frontend --include="*.test.js" --include="*.spec.js" || true)

if [ -n "$PYTHON_SKIPS" ] || [ -n "$JS_SKIPS" ]; then
  echo "❌ FAILED: test.skip() violations detected"
  echo "$PYTHON_SKIPS"
  echo "$JS_SKIPS"
  exit 1
fi
echo "✅ No test.skip() violations"

# Stage 3: Tests
echo "Stage 3: Running Tests"
pytest control-center/backend/tests/ -v
cd control-center/frontend && npm test && cd ../..

# Stage 4: Docker Build
echo "Stage 4: Docker Build Test"
docker compose build

# Stage 5: Final Checks
echo "Stage 5: Final Checks"
git status
docker compose config --quiet

echo "=========================================="
echo "✅ Pre-Deployment Validation PASSED"
echo "Ready to deploy: git push origin main"
echo "=========================================="
```

Make executable and run:
```bash
chmod +x pre-deploy-check.sh
./pre-deploy-check.sh
```

---

## Common Failures and Solutions

### Test.skip() Detected

**Error**: `test.skip() violations detected`

**Solution**:
1. Find violations: `grep -r "test.skip" .`
2. Remove skip decorators
3. Implement features to make tests pass
4. Re-run tests: `pytest -v`

### Build Failed

**Error**: `Docker build failed`

**Solution**:
1. Check Dockerfile syntax
2. Verify base image available
3. Check for missing dependencies
4. Test build locally: `docker build -t test .`

### Health Check Failed

**Error**: `Service not responding to health checks`

**Solution**:
1. Check service logs: `docker compose logs <service>`
2. Verify health endpoint exists
3. Test locally: `curl http://localhost:8000/health`
4. Check environment variables

---

## Deployment Frequency Guidelines

| Change Type | Deployment Window | Risk Level |
|-------------|------------------|------------|
| Bug fix (minor) | Anytime | Low |
| Feature (non-breaking) | Business hours | Medium |
| Feature (breaking) | Off-hours | High |
| Database migration | Planned maintenance | Critical |
| Infrastructure change | Planned maintenance | Critical |

**Recommended**: Deploy during business hours for immediate rollback support if needed.

---

## Post-Deployment Monitoring

Monitor for 30 minutes after deployment:

```bash
# Watch logs for errors
ssh root@82.25.112.73 "docker compose logs -f | grep -i error"

# Monitor health checks
watch -n 10 'curl -s https://ziggie.cloud/api/health | jq .'

# Check container restarts
ssh root@82.25.112.73 "docker stats --no-stream"
```

---

**Checklist Version**: 1.0
**Last Updated**: 2025-12-28
**Mandatory**: YES - Required for all deployments
**Owner**: DAEDALUS (Pipeline Architect)
