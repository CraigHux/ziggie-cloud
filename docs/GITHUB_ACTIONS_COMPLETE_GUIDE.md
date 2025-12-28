# GitHub Actions Complete CI/CD Guide
**Author**: DAEDALUS (Pipeline Architect - Elite Technical Team)
**Created**: 2025-12-28
**Repository**: Ziggie Command Center

---

## Executive Summary

Complete GitHub Actions CI/CD pipeline for Ziggie with:
- **5-Stage Quality Gates**: Lint → Test → Build → Deploy → Verify
- **ZERO TOLERANCE**: Automated test.skip() detection (Know Thyself Principle #2)
- **Self-Hosted Runner**: Deployed on Hostinger VPS (82.25.112.73)
- **Rollback Capability**: Emergency rollback within 60 seconds
- **Health Monitoring**: Every 5 minutes with auto-recovery

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Workflows](#workflows)
3. [Required Secrets](#required-secrets)
4. [Self-Hosted Runner Setup](#self-hosted-runner-setup)
5. [Deployment Process](#deployment-process)
6. [Rollback Procedures](#rollback-procedures)
7. [Quality Gates](#quality-gates)
8. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Repository                        │
│                   (CraigHux/ziggie-cloud)                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    Push to main branch
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              GitHub Actions - 5 Stage Pipeline               │
├─────────────────────────────────────────────────────────────┤
│  Stage 1: LINT & SECURITY                                   │
│    ├─ Python: flake8, black, pylint, bandit               │
│    ├─ JavaScript: eslint                                   │
│    ├─ YAML validation                                      │
│    ├─ Docker Compose syntax check                          │
│    └─ Secret detection (CRITICAL)                          │
├─────────────────────────────────────────────────────────────┤
│  Stage 2: TEST (ZERO test.skip() TOLERANCE)                │
│    ├─ Scan for test.skip() violations (FAIL BUILD IF FOUND)│
│    ├─ Python: pytest with coverage                         │
│    ├─ JavaScript: jest with coverage                       │
│    └─ Upload test results & coverage reports               │
├─────────────────────────────────────────────────────────────┤
│  Stage 3: BUILD                                             │
│    ├─ Multi-architecture Docker builds                     │
│    ├─ ziggie-api (Python/FastAPI)                         │
│    ├─ mcp-gateway (Node.js)                               │
│    ├─ sim-studio (Python/FastAPI+WebSockets)              │
│    └─ Image testing & artifact upload                      │
├─────────────────────────────────────────────────────────────┤
│  Stage 4: DEPLOY (Production only)                         │
│    ├─ Pre-deployment backup                                │
│    ├─ Download built images                                │
│    ├─ Sync code to /opt/ziggie                            │
│    ├─ Rolling update (stop → remove → start → verify)     │
│    └─ Cleanup old backups (keep last 10)                  │
├─────────────────────────────────────────────────────────────┤
│  Stage 5: VERIFY                                            │
│    ├─ HTTP health checks (with retries)                   │
│    ├─ Database connectivity (PostgreSQL, MongoDB, Redis)   │
│    ├─ Container status verification                        │
│    └─ Generate deployment summary                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            Self-Hosted Runner (ziggie-vps-runner)          │
│                 Hostinger VPS: 82.25.112.73                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Stack                      │
│  /opt/ziggie - 18 Services (API, MCP, DBs, Monitoring)     │
└─────────────────────────────────────────────────────────────┘
```

---

## Workflows

### 1. Enhanced CI/CD Pipeline (`ci-cd-enhanced.yml`)

**Trigger**: Push to main, PR to main, manual dispatch
**Purpose**: Complete 5-stage pipeline with ZERO test.skip() tolerance

**Key Features**:
- Automated test.skip() detection (fails build if found)
- Multi-service Docker builds with artifact caching
- Rolling deployment with health checks
- Automatic rollback on failure
- Comprehensive reporting

**Usage**:
```bash
# Automatic (push to main)
git push origin main

# Manual dispatch
gh workflow run ci-cd-enhanced.yml

# With custom services
gh workflow run ci-cd-enhanced.yml \
  -f services="ziggie-api,mcp-gateway"
```

### 2. Main Deployment Workflow (`deploy.yml`)

**Trigger**: Push to main (existing workflow)
**Purpose**: Fast deployment for code changes

**Key Features**:
- Validation → Test → Backup → Deploy → Verify
- Preserves .env files
- Cleanup old backups automatically
- Slack notifications

### 3. Rollback Workflow (`rollback.yml`)

**Trigger**: Manual dispatch only
**Purpose**: Emergency rollback to previous state

**Options**:
1. **previous_commit**: Rollback to last commit (fast)
2. **specific_commit**: Rollback to specific SHA
3. **container_restart**: Restart containers only (no code change)
4. **full_restore**: Full restore including database (manual DB restore required)

**Usage**:
```bash
# Rollback to previous commit
gh workflow run rollback.yml \
  -f rollback_type=previous_commit \
  -f reason="Deployment issue - API not responding"

# Rollback to specific commit
gh workflow run rollback.yml \
  -f rollback_type=specific_commit \
  -f target_commit=abc1234 \
  -f reason="Revert breaking changes"
```

### 4. Health Check Workflow (`health-check.yml`)

**Trigger**: Scheduled (every 5 minutes), manual dispatch
**Purpose**: Continuous monitoring with auto-recovery

**Checks**:
- Container status (running/unhealthy)
- HTTP health endpoints
- Database connectivity
- Disk space (alert at 80%, critical at 90%)
- Memory usage (alert at 85%, critical at 95%)

**Auto-Recovery**:
- Automatically restarts unhealthy services
- Sends Slack alerts on failures
- Verifies recovery after restart

### 5. PR Validation Workflow (`pr-check.yml`)

**Trigger**: Pull request to main
**Purpose**: Pre-merge validation

**Checks**:
- Secret detection
- YAML validation
- Docker Compose syntax
- Security scan (Trivy)
- Dockerfile best practices
- Test builds
- Deployment dry run

---

## Required Secrets

Configure these in GitHub repository settings → Secrets and variables → Actions:

### Essential Secrets

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `POSTGRES_PASSWORD` | PostgreSQL database password | `secure_pg_pass_123` |
| `MONGO_PASSWORD` | MongoDB root password | `secure_mongo_pass_123` |
| `REDIS_PASSWORD` | Redis password | `secure_redis_pass_123` |
| `N8N_PASSWORD` | n8n admin password | `secure_n8n_pass_123` |
| `N8N_ENCRYPTION_KEY` | n8n encryption key | `random_32_char_string` |
| `FLOWISE_PASSWORD` | Flowise admin password | `secure_flowise_pass_123` |
| `GRAFANA_PASSWORD` | Grafana admin password | `secure_grafana_pass_123` |
| `API_SECRET_KEY` | API JWT secret | `random_secret_key_for_jwt` |

### External API Keys

| Secret Name | Description | Required For |
|-------------|-------------|--------------|
| `OPENAI_API_KEY` | OpenAI API key | AI features, n8n |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | AI features, n8n |
| `AWS_ACCESS_KEY_ID` | AWS access key | S3, Secrets Manager |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | S3, Secrets Manager |
| `GITHUB_TOKEN` | GitHub PAT | API access, n8n |
| `GITHUB_RUNNER_TOKEN` | Self-hosted runner token | GitHub Actions runner |

### Optional Secrets

| Secret Name | Description | Required For |
|-------------|-------------|--------------|
| `SLACK_WEBHOOK_URL` | Slack webhook for notifications | Deployment alerts |
| `GITHUB_CLIENT_ID` | GitHub OAuth client ID | n8n GitHub integration |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth secret | n8n GitHub integration |

### Environment Variables

| Variable Name | Description | Default |
|---------------|-------------|---------|
| `VPS_DOMAIN` | Domain name | `ziggie.cloud` |
| `DEPLOYMENT_DIR` | Deployment directory | `/opt/ziggie` |

---

## Self-Hosted Runner Setup

### Current Runner Status

```json
{
  "id": 3,
  "name": "ziggie-vps-runner",
  "os": "Linux",
  "status": "online",
  "busy": false,
  "labels": ["self-hosted", "Linux", "X64", "ziggie"]
}
```

### Setup Instructions

#### 1. Register Runner on GitHub

```bash
# On GitHub: Settings → Actions → Runners → New self-hosted runner
# Follow GitHub's instructions to download and configure

# Download runner
cd /opt
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.330.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.330.0/actions-runner-linux-x64-2.330.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.330.0.tar.gz

# Configure runner
./config.sh --url https://github.com/CraigHux/ziggie-cloud \
  --token <RUNNER_TOKEN> \
  --name ziggie-vps-runner \
  --labels self-hosted,Linux,ziggie \
  --work _work
```

#### 2. Install Runner as Service

```bash
# Install service
sudo ./svc.sh install

# Start service
sudo ./svc.sh start

# Check status
sudo ./svc.sh status
```

#### 3. Verify Runner

```bash
# Check runner is online
gh api repos/CraigHux/ziggie-cloud/actions/runners

# Test workflow
gh workflow run health-check.yml
```

### Runner Maintenance

```bash
# View logs
sudo journalctl -u actions.runner.* -f

# Restart runner
sudo ./svc.sh stop
sudo ./svc.sh start

# Update runner (when new version available)
sudo ./svc.sh stop
./config.sh remove --token <TOKEN>
# Download new version
./config.sh --url https://github.com/CraigHux/ziggie-cloud --token <NEW_TOKEN>
sudo ./svc.sh install
sudo ./svc.sh start
```

### Docker Access (CRITICAL)

Runner must have Docker socket access:

```bash
# Add runner user to docker group
sudo usermod -aG docker <runner-user>

# Verify
docker ps
```

---

## Deployment Process

### Standard Deployment (Automatic)

```bash
# 1. Commit and push to main
git add .
git commit -m "feat: add new feature"
git push origin main

# 2. GitHub Actions automatically triggers
# 3. Monitor in GitHub Actions UI or CLI
gh run watch

# 4. Check deployment status
curl https://ziggie.cloud/api/health
```

### Manual Deployment

```bash
# Deploy all services
gh workflow run ci-cd-enhanced.yml

# Deploy specific services
gh workflow run ci-cd-enhanced.yml \
  -f services="ziggie-api,mcp-gateway"
```

### Deployment Timeline

| Stage | Duration | Actions |
|-------|----------|---------|
| Stage 1: Lint | ~30-60s | Code quality, security scan |
| Stage 2: Test | ~60-120s | Run all tests, check test.skip() |
| Stage 3: Build | ~120-180s | Build 3 Docker images |
| Stage 4: Deploy | ~30-60s | Rolling update, backup |
| Stage 5: Verify | ~30-60s | Health checks, database tests |
| **Total** | **~4-8 minutes** | Full pipeline |

### Pre-Deployment Checklist

- [ ] All tests passing locally
- [ ] No `test.skip()` or `@pytest.mark.skip` in code
- [ ] No secrets in code files
- [ ] Docker Compose validated: `docker compose config --quiet`
- [ ] Database migrations ready (if any)
- [ ] Backup plan confirmed

---

## Rollback Procedures

### Emergency Rollback (< 60 seconds)

**Scenario**: Deployment succeeded but services are failing

```bash
# Option 1: Container restart only (fastest)
gh workflow run rollback.yml \
  -f rollback_type=container_restart \
  -f reason="Service crash after deployment"

# Option 2: Rollback code to previous commit
gh workflow run rollback.yml \
  -f rollback_type=previous_commit \
  -f reason="API breaking changes"
```

### Selective Rollback

Rollback specific services:

```bash
gh workflow run rollback.yml \
  -f rollback_type=previous_commit \
  -f services="ziggie-api" \
  -f reason="API regression detected"
```

### Rollback to Specific Commit

```bash
# Find commit SHA
git log --oneline -10

# Rollback to specific commit
gh workflow run rollback.yml \
  -f rollback_type=specific_commit \
  -f target_commit=abc1234 \
  -f reason="Revert to stable version before X feature"
```

### Manual Rollback (Fallback)

If GitHub Actions unavailable:

```bash
# SSH to VPS
ssh root@82.25.112.73

# Navigate to deployment directory
cd /opt/ziggie

# Check recent backups
ls -lh backups/

# Restore from backup
cp backups/20251228_120000/docker-compose.yml .

# Restart services
docker compose down
docker compose up -d

# Verify
docker ps
curl http://localhost:8000/health
```

---

## Quality Gates

### Stage 1: Lint & Security

**Exit Criteria**:
- ✅ Python linting: 0 critical errors (E9, F63, F7, F82)
- ✅ JavaScript linting: 0 errors
- ✅ No secrets detected in code
- ✅ YAML files valid
- ✅ Docker Compose syntax valid

**Failure Actions**:
- Block deployment
- Generate security report
- Notify team via Slack

### Stage 2: Test (ZERO TOLERANCE)

**Exit Criteria**:
- ✅ **ZERO test.skip() violations** (Python & JavaScript)
- ✅ All tests pass
- ✅ Coverage threshold met (70%)
- ✅ No failing tests

**test.skip() Detection Patterns**:

**Python**:
```python
# ❌ VIOLATIONS (will fail build)
@pytest.mark.skip
@pytest.mark.skip(reason="not implemented")
@unittest.skip("broken")
pytest.skip("conditional skip")
self.skipTest("reason")
```

**JavaScript**:
```javascript
// ❌ VIOLATIONS (will fail build)
test.skip('feature', () => {})
it.skip('test', () => {})
describe.skip('suite', () => {})
xit('old skip syntax', () => {})
xdescribe('old skip syntax', () => {})
```

**Enforcement**:
```bash
# Pipeline will fail with:
🛑 BUILD FAILED: test.skip() VIOLATIONS
Know Thyself Principle #2: NO TEST SKIPPED
Tolerance: ZERO
Consequence: Sprint FAILURE
```

### Stage 3: Build

**Exit Criteria**:
- ✅ All Docker images build successfully
- ✅ Images pass smoke tests
- ✅ Image size within reasonable limits
- ✅ No build errors

### Stage 4: Deploy

**Exit Criteria**:
- ✅ Backup created successfully
- ✅ Code synced to deployment directory
- ✅ All services restarted
- ✅ Containers in "running" state

### Stage 5: Verify

**Exit Criteria**:
- ✅ HTTP health checks pass (all services)
- ✅ Database connectivity verified
- ✅ No container crashes
- ✅ Response times < 500ms

**Verification Matrix**:

| Service | Health Endpoint | Database | Expected Response |
|---------|----------------|----------|-------------------|
| ziggie-api | `http://<IP>:8000/health` | PostgreSQL | `{"status":"healthy"}` |
| mcp-gateway | `http://<IP>:8080/health` | MongoDB, Redis | `{"status":"healthy"}` |
| sim-studio | `http://<IP>:8001/health` | PostgreSQL, MongoDB | `{"status":"healthy"}` |

---

## Troubleshooting

### Common Issues

#### 1. "test.skip() violation detected"

**Symptom**: Build fails at Stage 2 with test skip violations

**Solution**:
```bash
# Find violations
grep -r "test\.skip\|@pytest\.mark\.skip" control-center/backend
grep -r "test\.skip\|it\.skip" control-center/frontend

# Fix: Remove skip and implement feature
# DO NOT just comment out tests
```

#### 2. "Secret detected in code"

**Symptom**: Build fails at Stage 1 with secret detection

**Solution**:
```bash
# Find secret
grep -r "sk-" .

# Fix options:
# 1. Remove secret from code
# 2. Move to .env file (ensure .env is in .gitignore)
# 3. Use GitHub Secrets for CI/CD
# 4. Use AWS Secrets Manager for production

# Rotate exposed secret immediately
```

#### 3. Health check failed

**Symptom**: Stage 5 fails with "health check failed after 10 attempts"

**Diagnosis**:
```bash
# SSH to VPS
ssh root@82.25.112.73

# Check container logs
docker logs ziggie-api --tail=100
docker logs ziggie-mcp-gateway --tail=100

# Check container status
docker ps -a

# Test health endpoint manually
API_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ziggie-api)
curl -v http://$API_IP:8000/health
```

**Common Causes**:
- Service crashed during startup
- Database connection failed
- Port conflict
- Missing environment variable

#### 4. Self-hosted runner offline

**Symptom**: Workflow queued but not starting

**Diagnosis**:
```bash
# Check runner status
gh api repos/CraigHux/ziggie-cloud/actions/runners

# SSH to VPS and check service
ssh root@82.25.112.73
sudo systemctl status actions.runner.*
sudo journalctl -u actions.runner.* -n 50
```

**Solution**:
```bash
# Restart runner service
sudo systemctl restart actions.runner.*

# If still failing, re-register
cd /opt/actions-runner
sudo ./svc.sh stop
./config.sh remove --token <OLD_TOKEN>
./config.sh --url https://github.com/CraigHux/ziggie-cloud --token <NEW_TOKEN>
sudo ./svc.sh install
sudo ./svc.sh start
```

#### 5. Deployment succeeded but service not accessible

**Symptom**: Deployment passes but can't reach service via domain

**Diagnosis**:
```bash
# Check nginx is running
docker ps | grep nginx

# Check nginx logs
docker logs ziggie-nginx

# Test internal connectivity
API_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ziggie-api)
curl http://$API_IP:8000/health  # Should work

# Test external (via nginx)
curl https://ziggie.cloud/api/health  # Might fail
```

**Common Causes**:
- Nginx configuration not reloaded
- SSL certificate expired
- Firewall blocking port 443
- DNS not pointing to VPS

**Solution**:
```bash
# Reload nginx
docker exec ziggie-nginx nginx -s reload

# Check SSL certificate
docker exec ziggie-nginx ls -lh /etc/letsencrypt/live/ziggie.cloud/

# Renew if expired
docker compose restart certbot
```

---

## Performance Optimization

### Build Caching

Docker images are cached between builds. To force rebuild:

```bash
gh workflow run ci-cd-enhanced.yml \
  -f services="ziggie-api" \
  --ref main

# Then manually trigger rebuild on VPS
ssh root@82.25.112.73
cd /opt/ziggie
docker compose build --no-cache ziggie-api
docker compose up -d ziggie-api
```

### Parallel Execution

Workflows use job parallelization:
- Stage 1 (Lint): Single job
- Stage 2 (Test): Parallel (Python + JavaScript)
- Stage 3 (Build): Parallel matrix (3 services)
- Stage 4 (Deploy): Sequential (safety)
- Stage 5 (Verify): Parallel (3 services + 3 DBs)

### Artifact Retention

| Artifact | Retention | Size | Purpose |
|----------|-----------|------|---------|
| Docker images | 7 days | ~500MB | Deployment artifacts |
| Test results | 30 days | ~5MB | Coverage tracking |
| Security reports | 30 days | ~1MB | Compliance |

---

## Monitoring & Alerts

### GitHub Actions Monitoring

```bash
# List recent runs
gh run list --limit 10

# Watch current run
gh run watch

# View run details
gh run view <run-id>

# Download logs
gh run download <run-id>
```

### Slack Notifications

Configure `SLACK_WEBHOOK_URL` secret for:
- Deployment success/failure
- Health check failures
- Rollback completions
- Security violations

**Webhook Format**:
```
https://hooks.slack.com/services/[REDACTED]
```

### Metrics Dashboard

View in GitHub Actions UI:
- Success rate (last 30 days)
- Average deployment time
- Build failure trends
- Most common failure reasons

---

## Best Practices

### 1. Always Test Locally First

```bash
# Run linters
cd control-center/backend
flake8 .
black --check .

cd ../frontend
npm run lint

# Run tests
cd control-center/backend
pytest tests/ -v

cd ../frontend
npm test

# Test Docker build
docker compose build ziggie-api
```

### 2. Never Skip Tests

**❌ NEVER DO THIS**:
```python
@pytest.mark.skip(reason="will implement later")
def test_feature():
    pass
```

**✅ DO THIS INSTEAD**:
```python
def test_feature():
    # Implement the feature to make test pass
    result = feature()
    assert result == expected
```

### 3. Use Feature Flags for Incomplete Features

Instead of skipping tests, use feature flags:

```python
# .env
FEATURE_NEW_API=false

# Code
if settings.FEATURE_NEW_API:
    # New implementation
else:
    # Old implementation (tests pass)
```

### 4. Monitor Runner Disk Space

```bash
# SSH to VPS
ssh root@82.25.112.73

# Check disk usage
df -h /opt/ziggie

# Clean Docker (if low)
docker system prune -af --volumes
```

### 5. Rotate Secrets Regularly

Every 90 days:
- Rotate database passwords
- Regenerate API keys
- Update GitHub runner token
- Renew SSL certificates

---

## Emergency Procedures

### Complete System Failure

If all automated workflows fail:

```bash
# 1. SSH to VPS
ssh root@82.25.112.73

# 2. Check Docker
docker ps -a
docker compose logs --tail=100

# 3. Restart all services
cd /opt/ziggie
docker compose down
docker compose up -d

# 4. Monitor startup
docker compose logs -f

# 5. Verify health
curl http://localhost:8000/health
curl http://localhost:8080/health
```

### Runner Completely Offline

If runner won't start:

```bash
# 1. Check GitHub runner status
gh api repos/CraigHux/ziggie-cloud/actions/runners

# 2. SSH to VPS
ssh root@82.25.112.73

# 3. Remove runner
cd /opt/actions-runner
sudo ./svc.sh stop
sudo ./svc.sh uninstall
rm -rf _work

# 4. Re-register from scratch
# Go to GitHub: Settings → Actions → Runners → New self-hosted runner
# Follow on-screen instructions

# 5. Verify
gh api repos/CraigHux/ziggie-cloud/actions/runners
```

### Rollback Failed

If automatic rollback fails:

```bash
# Manual rollback steps
ssh root@82.25.112.73
cd /opt/ziggie

# Find last good backup
ls -lht backups/ | head -5

# Restore backup
BACKUP_DIR="backups/<timestamp>"
cp $BACKUP_DIR/docker-compose.yml .

# Rebuild from last good commit
git fetch origin
git reset --hard <last-good-commit-sha>

# Rebuild and restart
docker compose build
docker compose up -d

# Verify
docker ps
curl http://localhost:8000/health
```

---

## Security Considerations

### 1. Secret Management

**Never commit**:
- API keys
- Database passwords
- SSH private keys
- JWT secrets

**Use instead**:
- GitHub Secrets (CI/CD)
- AWS Secrets Manager (production)
- Environment variables (.env file, not in repo)

### 2. Runner Security

Self-hosted runner has access to:
- Docker socket (can run arbitrary containers)
- /opt/ziggie directory (deployment files)
- GitHub repository (can clone code)

**Protections**:
- Runner runs as non-root user
- Docker commands via sudo only
- No sensitive data in runner logs
- Regular security updates

### 3. Network Security

Services communicate via internal Docker network:
- Public: Nginx (80, 443)
- Internal: All other services (not exposed)

### 4. Audit Logging

All deployments logged:
- GitHub Actions run logs (retained 90 days)
- Docker container logs
- Nginx access logs
- System audit logs (auditd)

---

## Appendix: File Locations

### GitHub Actions Workflows

```
C:\Ziggie\.github\workflows\
├── ci-cd-enhanced.yml       # 5-stage pipeline (THIS FILE)
├── deploy.yml                # Existing deployment workflow
├── rollback.yml              # Emergency rollback
├── health-check.yml          # Scheduled monitoring
└── pr-check.yml              # Pull request validation
```

### VPS Deployment Files

```
/opt/ziggie/
├── docker-compose.yml        # Main stack definition
├── .env                      # Secrets (not in repo)
├── backups/                  # Automated backups
│   ├── 20251228_120000/      # Timestamp-based
│   └── ...
├── nginx/                    # Reverse proxy config
├── mcp-gateway/              # MCP Gateway source
├── control-center/           # Control Center source
└── sim-studio/               # Sim Studio source
```

### Self-Hosted Runner

```
/opt/actions-runner/
├── config.sh                 # Runner configuration
├── run.sh                    # Manual runner start
├── svc.sh                    # Service management
├── _work/                    # Workspace (ephemeral)
└── _diag/                    # Diagnostic logs
```

---

## Quick Reference Commands

```bash
# ========== DEPLOYMENT ==========
# Trigger deployment
gh workflow run ci-cd-enhanced.yml

# Monitor deployment
gh run watch

# View deployment status
gh run list --limit 5

# ========== ROLLBACK ==========
# Emergency rollback
gh workflow run rollback.yml \
  -f rollback_type=previous_commit \
  -f reason="Emergency"

# ========== HEALTH CHECK ==========
# Manual health check
gh workflow run health-check.yml

# ========== VPS MANAGEMENT ==========
# SSH to VPS
ssh root@82.25.112.73

# Check services
docker ps

# View logs
docker compose logs -f ziggie-api

# Restart service
docker compose restart ziggie-api

# ========== RUNNER MANAGEMENT ==========
# Check runner status
gh api repos/CraigHux/ziggie-cloud/actions/runners

# Restart runner (on VPS)
sudo systemctl restart actions.runner.*

# View runner logs (on VPS)
sudo journalctl -u actions.runner.* -f
```

---

**Document Version**: 1.0
**Last Updated**: 2025-12-28
**Author**: DAEDALUS (Pipeline Architect)
**Status**: Production Ready
