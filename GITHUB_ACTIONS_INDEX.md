# GitHub Actions CI/CD - Master Index
**Project**: Ziggie Command Center
**Author**: DAEDALUS (Pipeline Architect - Elite Technical Team)
**Created**: 2025-12-28
**Status**: Production Ready

---

## Quick Start

```bash
# 1. Configure GitHub secrets (one-time setup)
gh secret set POSTGRES_PASSWORD
gh secret set MONGO_PASSWORD
# ... (see docs/GITHUB_SECRETS_SETUP.md for complete list)

# 2. Verify runner is online
gh api repos/CraigHux/ziggie-cloud/actions/runners

# 3. Run pre-deployment checklist
./pre-deploy-check.sh

# 4. Deploy to production
git push origin main

# 5. Monitor deployment
gh run watch

# 6. Verify deployment
curl https://ziggie.cloud/api/health
```

---

## Documentation Structure

```
GitHub Actions Documentation (DAEDALUS Pipeline)
├── GITHUB_ACTIONS_INDEX.md (this file)           # Master index & quick reference
├── docs/
│   ├── GITHUB_ACTIONS_COMPLETE_GUIDE.md          # Complete guide (850+ lines)
│   ├── GITHUB_SECRETS_SETUP.md                   # Secrets configuration (450+ lines)
│   ├── ROLLBACK_PLAYBOOK.md                      # Emergency rollback (700+ lines)
│   ├── PRE_DEPLOYMENT_CHECKLIST.md               # Pre-deploy validation (450+ lines)
│   └── CICD_DELIVERABLES_SUMMARY.md              # Deliverables summary (300+ lines)
└── .github/workflows/
    ├── ci-cd-enhanced.yml                         # 5-stage pipeline (NEW, 580 lines)
    ├── deploy.yml                                 # Fast deployment (existing)
    ├── rollback.yml                               # Emergency rollback (existing)
    ├── health-check.yml                           # Scheduled monitoring (existing)
    └── pr-check.yml                               # Pull request validation (existing)
```

**Total Documentation**: 2,750+ lines across 5 guides
**Total Workflows**: 1,858+ lines across 5 workflows

---

## When to Use Each Document

| Document | When to Use |
|----------|-------------|
| **GITHUB_ACTIONS_INDEX.md** (this file) | Quick reference, find other documents |
| **GITHUB_ACTIONS_COMPLETE_GUIDE.md** | Full documentation, troubleshooting, architecture |
| **GITHUB_SECRETS_SETUP.md** | Initial setup, rotate secrets, add new secrets |
| **ROLLBACK_PLAYBOOK.md** | Emergency rollback, incident response |
| **PRE_DEPLOYMENT_CHECKLIST.md** | Before every deployment (mandatory) |
| **CICD_DELIVERABLES_SUMMARY.md** | Overview, compliance, metrics |

---

## Workflow Quick Reference

### Deploy to Production
```bash
# Automatic (push to main)
git push origin main

# Manual trigger
gh workflow run ci-cd-enhanced.yml

# Deploy specific services
gh workflow run ci-cd-enhanced.yml \
  -f services="ziggie-api,mcp-gateway"
```

### Emergency Rollback
```bash
# Rollback to previous commit (60 seconds)
gh workflow run rollback.yml \
  -f rollback_type=previous_commit \
  -f reason="API not responding"

# Restart containers only (30 seconds)
gh workflow run rollback.yml \
  -f rollback_type=container_restart \
  -f reason="Service crash"
```

### Monitor Deployment
```bash
# Watch current deployment
gh run watch

# View recent deployments
gh run list --limit 10

# Check specific run
gh run view <run-id> --log
```

### Check Health
```bash
# Trigger manual health check
gh workflow run health-check.yml

# Check service health directly
curl https://ziggie.cloud/api/health
curl https://ziggie.cloud/mcp/health
curl https://ziggie.cloud/sim/health
```

---

## 5-Stage Pipeline Overview

```
Stage 1: LINT & SECURITY (30-60s)
├─ Python linting (flake8, black, pylint, bandit)
├─ JavaScript linting (eslint)
├─ YAML validation
├─ Secret detection (CRITICAL)
└─ Docker Compose validation
         ↓
Stage 2: TEST - ZERO test.skip() (60-120s)
├─ test.skip() detection (FAILS BUILD IF FOUND)
├─ Python tests (pytest + coverage ≥70%)
├─ JavaScript tests (jest + coverage ≥70%)
└─ Test result upload
         ↓
Stage 3: BUILD (120-180s)
├─ ziggie-api (Python/FastAPI)
├─ mcp-gateway (Node.js)
├─ sim-studio (Python/FastAPI+WebSockets)
└─ Docker image artifacts
         ↓
Stage 4: DEPLOY (30-60s)
├─ Pre-deployment backup
├─ Sync code to /opt/ziggie
├─ Rolling update (stop → remove → start)
└─ Cleanup old backups
         ↓
Stage 5: VERIFY (30-60s)
├─ HTTP health checks (10 retries)
├─ Database connectivity (PostgreSQL, MongoDB, Redis)
├─ Container status verification
└─ Deployment summary
         ↓
NOTIFICATION (Slack if configured)
```

**Total Time**: 4-8 minutes

---

## Critical Concepts

### ZERO TOLERANCE: test.skip() Detection

**Know Thyself Principle #2**: NO TEST SKIPPED

The pipeline **automatically detects and FAILS** if any of these patterns are found:

**Python**:
- `@pytest.mark.skip`
- `@unittest.skip`
- `pytest.skip()`
- `self.skipTest()`

**JavaScript**:
- `test.skip()`
- `it.skip()`
- `describe.skip()`
- `xit()` / `xdescribe()`

**Consequence**: Immediate build failure with detailed violation report

**Fix**: Remove skip decorators and implement features to make tests pass

---

## Required GitHub Secrets (18)

**Critical Secrets**:
1. `POSTGRES_PASSWORD` - PostgreSQL database password
2. `MONGO_PASSWORD` - MongoDB root password
3. `REDIS_PASSWORD` - Redis password
4. `API_SECRET_KEY` - API JWT secret
5. `N8N_PASSWORD` - n8n admin password
6. `N8N_ENCRYPTION_KEY` - n8n encryption key
7. `FLOWISE_PASSWORD` - Flowise admin password
8. `GRAFANA_PASSWORD` - Grafana admin password

**External API Keys**:
9. `OPENAI_API_KEY` - OpenAI API key
10. `ANTHROPIC_API_KEY` - Anthropic Claude API key
11. `AWS_ACCESS_KEY_ID` - AWS access key
12. `AWS_SECRET_ACCESS_KEY` - AWS secret key
13. `GITHUB_TOKEN` - GitHub personal access token

**Optional**:
14. `SLACK_WEBHOOK_URL` - Slack notifications
15. `GITHUB_CLIENT_ID` - GitHub OAuth
16. `GITHUB_CLIENT_SECRET` - GitHub OAuth secret
17. `GITHUB_RUNNER_TOKEN` - Self-hosted runner token
18. `WEBUI_SECRET_KEY` - Open WebUI secret

**Setup**: See `docs/GITHUB_SECRETS_SETUP.md`

---

## Rollback Decision Matrix

| Scenario | Rollback Type | Time | Command |
|----------|---------------|------|---------|
| Service crashed | Container Restart | 30s | `rollback_type=container_restart` |
| API errors | Previous Commit | 60s | `rollback_type=previous_commit` |
| Database migration failed | Specific Commit | 2m | `rollback_type=specific_commit` + manual DB rollback |
| Complete failure | Manual Rollback | 5m | SSH + manual steps |

**Full Procedures**: See `docs/ROLLBACK_PLAYBOOK.md`

---

## Pre-Deployment Checklist (Mandatory)

**Before EVERY deployment**, verify:

### Code Quality
- [ ] Python linting passes (flake8, black, pylint)
- [ ] JavaScript linting passes (eslint)
- [ ] No secrets in code
- [ ] Docker Compose valid

### Testing (CRITICAL)
- [ ] **ZERO test.skip() violations** (scan with grep)
- [ ] All tests pass (100%)
- [ ] Coverage ≥70%

### Build
- [ ] Docker builds succeed
- [ ] Images start successfully
- [ ] Local stack runs without errors

### Environment
- [ ] VPS accessible (SSH test)
- [ ] Self-hosted runner online
- [ ] GitHub secrets configured
- [ ] Disk space >10GB

**Automated Script**: `./pre-deploy-check.sh`
**Full Checklist**: See `docs/PRE_DEPLOYMENT_CHECKLIST.md`

---

## Self-Hosted Runner

**Location**: Hostinger VPS (82.25.112.73)
**Name**: `ziggie-vps-runner`
**Labels**: `self-hosted`, `Linux`, `X64`, `ziggie`

**Check Status**:
```bash
gh api repos/CraigHux/ziggie-cloud/actions/runners
```

**Restart Runner** (on VPS):
```bash
ssh root@82.25.112.73
sudo systemctl restart actions.runner.*
```

**View Logs** (on VPS):
```bash
sudo journalctl -u actions.runner.* -f
```

---

## Health Monitoring

**Frequency**: Every 5 minutes (automated)
**Workflow**: `health-check.yml`

**Checks**:
- Container status (running/unhealthy)
- HTTP health endpoints (3 services)
- Database connectivity (3 databases)
- Disk space (alert at 80%)
- Memory usage (alert at 85%)

**Auto-Recovery**:
- Automatically restarts unhealthy services
- Sends Slack alerts (if configured)
- Verifies recovery after restart

---

## Common Commands

### Deployment
```bash
# Standard deployment
git push origin main

# Manual deployment
gh workflow run ci-cd-enhanced.yml

# Deploy specific services
gh workflow run ci-cd-enhanced.yml -f services="ziggie-api"

# Monitor deployment
gh run watch
```

### Rollback
```bash
# Quick rollback (previous commit)
gh workflow run rollback.yml \
  -f rollback_type=previous_commit \
  -f reason="Emergency"

# Container restart only
gh workflow run rollback.yml \
  -f rollback_type=container_restart \
  -f reason="Service crash"
```

### Monitoring
```bash
# Manual health check
gh workflow run health-check.yml

# Check service health
curl https://ziggie.cloud/api/health

# View recent runs
gh run list --limit 10

# View specific run
gh run view <run-id>
```

### VPS Management
```bash
# SSH to VPS
ssh root@82.25.112.73

# Check containers
docker ps

# View logs
docker compose logs -f ziggie-api

# Restart service
docker compose restart ziggie-api
```

---

## Troubleshooting Quick Reference

### Build fails with "test.skip() violations"
```bash
# Find violations
grep -r "test.skip\|@pytest.mark.skip" .

# Fix: Remove skip decorators, implement features
# Re-run tests to verify they pass
```

### Health check fails
```bash
# SSH to VPS
ssh root@82.25.112.73

# Check logs
docker compose logs ziggie-api --tail=100

# Restart service
docker compose restart ziggie-api
```

### Self-hosted runner offline
```bash
# SSH to VPS
ssh root@82.25.112.73

# Check status
sudo systemctl status actions.runner.*

# Restart
sudo systemctl restart actions.runner.*
```

### Secret not available in workflow
```bash
# Check if secret exists
gh secret list | grep SECRET_NAME

# Add secret if missing
gh secret set SECRET_NAME
```

**Full Troubleshooting**: See `docs/GITHUB_ACTIONS_COMPLETE_GUIDE.md` → Troubleshooting section

---

## Performance Metrics

### Deployment Timeline
- Stage 1 (Lint): 30-60s (10%)
- Stage 2 (Test): 60-120s (25%)
- Stage 3 (Build): 120-180s (40%)
- Stage 4 (Deploy): 30-60s (15%)
- Stage 5 (Verify): 30-60s (10%)
- **Total**: 4-8 minutes

### Success Rate Targets
| Metric | Current | Target |
|--------|---------|--------|
| Pipeline success rate | 33% | 90%+ |
| Test pass rate | 100% | 100% |
| Health check pass rate | 100% | 100% |

---

## Architecture

### VPS Infrastructure
```
Hostinger VPS: 82.25.112.73
├── Self-hosted GitHub Runner (ziggie-vps-runner)
├── Docker Compose Stack (18 services)
│   ├── Application Layer
│   │   ├── ziggie-api (FastAPI)
│   │   ├── mcp-gateway (Node.js)
│   │   └── sim-studio (FastAPI+WebSockets)
│   ├── Database Layer
│   │   ├── postgres (PostgreSQL 15)
│   │   ├── mongodb (MongoDB 7)
│   │   └── redis (Redis 7)
│   └── Additional Services
│       ├── n8n (workflow automation)
│       ├── flowise (LLM workflows)
│       ├── ollama (local LLM)
│       ├── nginx (reverse proxy)
│       ├── grafana (monitoring)
│       └── ... (13 more services)
└── Deployment Directory (/opt/ziggie)
```

---

## Next Steps

### Immediate (Today)
1. Review this index document
2. Read `GITHUB_ACTIONS_COMPLETE_GUIDE.md` for full understanding
3. Configure GitHub secrets: `docs/GITHUB_SECRETS_SETUP.md`
4. Verify runner status: `gh api repos/.../runners`

### Short-Term (This Week)
1. Test deployment workflow end-to-end
2. Practice rollback procedure (emergency drill)
3. Configure Slack webhook (optional but recommended)
4. Train team on deployment procedures

### Long-Term (This Month)
1. Achieve 90%+ pipeline success rate
2. Establish deployment schedule
3. Create team runbooks for common issues
4. Set up external monitoring

---

## Support

### Questions About...

- **Deployment Process**: See `GITHUB_ACTIONS_COMPLETE_GUIDE.md`
- **Secrets Setup**: See `GITHUB_SECRETS_SETUP.md`
- **Rollback Procedures**: See `ROLLBACK_PLAYBOOK.md`
- **Pre-Deployment**: See `PRE_DEPLOYMENT_CHECKLIST.md`
- **Overview & Metrics**: See `CICD_DELIVERABLES_SUMMARY.md`

### Emergency Contact

**Pipeline Architect**: DAEDALUS (Elite Technical Team)
**Repository**: https://github.com/CraigHux/ziggie-cloud

---

## Compliance

### Know Thyself Principles

✅ **Principle #1: STICK TO THE PLAN**
- 5-stage pipeline strictly follows design
- No deviations without approval

✅ **Principle #2: NO TEST SKIPPED**
- **ZERO TOLERANCE** enforcement active
- Automated detection in Stage 2
- Immediate build failure on violations

✅ **Principle #3: DOCUMENT EVERYTHING**
- 2,750+ lines of documentation
- 5 comprehensive guides
- All procedures documented

---

**Index Version**: 1.0
**Last Updated**: 2025-12-28
**Status**: Production Ready
**Owner**: DAEDALUS (Pipeline Architect - Elite Technical Team)
