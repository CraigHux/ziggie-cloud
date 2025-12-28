# Ziggie CI/CD Pipeline - Complete Setup Guide

> **Last Updated**: 2025-12-28
> **Target**: Hostinger VPS with Docker + Self-Hosted GitHub Runner
> **Repository**: CraigHux/ziggie-cloud

---

## Table of Contents

1. [Overview](#overview)
2. [Self-Hosted Runner Setup](#self-hosted-runner-setup)
3. [GitHub Secrets Configuration](#github-secrets-configuration)
4. [Deployment Key Generation](#deployment-key-generation)
5. [Workflow Files Reference](#workflow-files-reference)
6. [Rollback Procedures](#rollback-procedures)
7. [Monitoring & Alerts](#monitoring--alerts)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GitHub Repository                                │
│                     (CraigHux/ziggie-cloud)                             │
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │  Push to main    │  │  Manual Dispatch │  │  PR to main      │       │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘       │
│           │                     │                     │                  │
│           ▼                     ▼                     ▼                  │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │                    GitHub Actions                             │       │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │       │
│  │  │ deploy.yml  │  │rollback.yml │  │ pr-check.yml        │   │       │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘   │       │
│  └──────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Hostinger VPS                                     │
│                    (ziggie-vps-runner)                                   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │                 Self-Hosted Runner                            │       │
│  │    (Docker container: myoung34/github-runner:latest)         │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                              │                                           │
│                              ▼                                           │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │                  Docker Services (18)                         │       │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐             │       │
│  │  │ ziggie-api  │ │ mcp-gateway │ │ sim-studio  │ ...         │       │
│  │  └─────────────┘ └─────────────┘ └─────────────┘             │       │
│  └──────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
```

### Workflow Summary

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `deploy.yml` | Push to main, Manual | Main deployment pipeline |
| `rollback.yml` | Manual | Emergency rollback |
| `health-check.yml` | Every 5 minutes | Service monitoring |
| `pr-check.yml` | Pull request | Pre-merge validation |

---

## Self-Hosted Runner Setup

### Option 1: Docker-Based Runner (Recommended)

The runner is already configured in the main `docker-compose.yml`:

```yaml
# Already in hostinger-vps/docker-compose.yml
github-runner:
  image: myoung34/github-runner:latest
  container_name: ziggie-github-runner
  restart: unless-stopped
  environment:
    - REPO_URL=${GITHUB_REPO_URL}
    - RUNNER_TOKEN=${GITHUB_RUNNER_TOKEN}
    - RUNNER_NAME=ziggie-vps-runner
    - RUNNER_WORKDIR=/tmp/github-runner
    - LABELS=self-hosted,linux,ziggie
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
    - github_runner_data:/tmp/github-runner
  networks:
    - ziggie-network
```

**Setup Steps:**

1. **Get Runner Registration Token**
   ```bash
   # Go to: https://github.com/CraigHux/ziggie-cloud/settings/actions/runners/new
   # Copy the token shown (starts with A...)
   ```

2. **Update .env file**
   ```bash
   GITHUB_REPO_URL=https://github.com/CraigHux/ziggie-cloud
   GITHUB_RUNNER_TOKEN=AXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

3. **Start the runner**
   ```bash
   cd /opt/ziggie
   docker compose up -d github-runner

   # Check it's registered
   docker logs ziggie-github-runner
   ```

4. **Verify in GitHub**
   - Go to: Settings > Actions > Runners
   - Should see: `ziggie-vps-runner` with status "Idle"

### Option 2: Native Installation (Alternative)

If you prefer a native installation:

```bash
# SSH into VPS
ssh ziggie@YOUR_VPS_IP

# Create runner directory
mkdir -p /opt/actions-runner && cd /opt/actions-runner

# Download latest runner
curl -o actions-runner-linux-x64.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.321.0/actions-runner-linux-x64-2.321.0.tar.gz

# Extract
tar xzf actions-runner-linux-x64.tar.gz

# Configure
./config.sh --url https://github.com/CraigHux/ziggie-cloud \
  --token YOUR_TOKEN \
  --name ziggie-vps-runner \
  --labels self-hosted,linux,ziggie \
  --work /tmp/github-runner

# Install as service
sudo ./svc.sh install
sudo ./svc.sh start

# Check status
sudo ./svc.sh status
```

### Runner Security Best Practices

1. **Dedicated User**
   ```bash
   # Create dedicated user for runner
   sudo useradd -m -s /bin/bash github-runner
   sudo usermod -aG docker github-runner
   ```

2. **Limited Permissions**
   ```bash
   # Only give access to deployment directory
   sudo chown -R github-runner:github-runner /opt/ziggie
   ```

3. **Network Isolation**
   - Runner should only access Docker socket and deployment directory
   - Firewall rules should be minimal

4. **Token Rotation**
   - Rotate runner token periodically
   - Remove and re-add runner if compromised

---

## GitHub Secrets Configuration

### Required Secrets

Navigate to: Repository > Settings > Secrets and variables > Actions

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `SLACK_WEBHOOK_URL` | Slack notifications | `https://hooks.slack.com/services/...` |
| `VPS_SSH_KEY` | SSH private key for VPS (if using SSH action) | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `VPS_HOST` | VPS IP address | `123.45.67.89` |
| `VPS_USER` | SSH username | `ziggie` |

### Environment Variables (Actions Variables)

Navigate to: Repository > Settings > Secrets and variables > Actions > Variables

| Variable Name | Description | Example |
|---------------|-------------|---------|
| `VPS_DOMAIN` | Production domain | `ziggie.yourdomain.com` |
| `DEPLOYMENT_DIR` | Deployment path | `/opt/ziggie` |

### Setting Up Secrets via CLI

```bash
# Install GitHub CLI
# https://cli.github.com/

# Authenticate
gh auth login

# Set secrets
gh secret set SLACK_WEBHOOK_URL --body "https://hooks.slack.com/services/..."
gh secret set VPS_SSH_KEY < ~/.ssh/ziggie_deploy_key

# Set variables
gh variable set VPS_DOMAIN --body "ziggie.yourdomain.com"
gh variable set DEPLOYMENT_DIR --body "/opt/ziggie"
```

---

## Deployment Key Generation

### SSH Key for Automated Deployment

```bash
# Generate ED25519 key (recommended over RSA)
ssh-keygen -t ed25519 -C "ziggie-deploy@github-actions" -f ~/.ssh/ziggie_deploy_key -N ""

# View public key
cat ~/.ssh/ziggie_deploy_key.pub

# Add to VPS authorized_keys
ssh ziggie@YOUR_VPS_IP "mkdir -p ~/.ssh && echo 'YOUR_PUBLIC_KEY' >> ~/.ssh/authorized_keys"

# Set correct permissions on VPS
ssh ziggie@YOUR_VPS_IP "chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"

# Add private key as GitHub secret
gh secret set VPS_SSH_KEY < ~/.ssh/ziggie_deploy_key
```

### Deploy Key for Repository Access

If you need the VPS to pull from the repository:

```bash
# On VPS
ssh-keygen -t ed25519 -C "ziggie-vps-deploy" -f ~/.ssh/github_deploy -N ""

# Add public key to repository
# Go to: Repository > Settings > Deploy keys > Add deploy key
cat ~/.ssh/github_deploy.pub

# Configure SSH on VPS
cat >> ~/.ssh/config << 'EOF'
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/github_deploy
  IdentitiesOnly yes
EOF

# Test connection
ssh -T git@github.com
```

---

## Workflow Files Reference

### deploy.yml - Main Deployment

**Triggers:**
- Push to `main` branch (excluding .md files)
- Manual workflow dispatch

**Jobs:**
1. **validate** - Check changes, disk space, compose config
2. **test** - Pre-deployment health checks
3. **backup** - Create backup of current state
4. **deploy** - Sync code, build, deploy services
5. **verify** - Health checks on deployed services
6. **cleanup** - Prune Docker resources
7. **notify** - Send Slack notification

**Manual Dispatch Options:**
- `services`: Comma-separated list or "all"
- `skip_tests`: Skip pre-deployment tests

### rollback.yml - Emergency Rollback

**Triggers:**
- Manual workflow dispatch only

**Options:**
- `rollback_type`:
  - `previous_commit` - Roll back one commit
  - `specific_commit` - Roll back to specific SHA
  - `container_restart` - Just restart containers
  - `full_restore` - Includes database restore (manual)
- `services`: Which services to rollback
- `reason`: Documented reason for rollback

### health-check.yml - Continuous Monitoring

**Triggers:**
- Every 5 minutes (cron)
- Manual dispatch

**Checks:**
- Container status (running/healthy)
- HTTP health endpoints
- Database connectivity
- Disk space usage
- Memory usage

**Actions:**
- Auto-restart unhealthy services
- Alert on failures via Slack

### pr-check.yml - PR Validation

**Triggers:**
- Pull request to `main`

**Checks:**
- Secret scanning
- YAML validation
- Docker Compose validation
- Dockerfile best practices
- Build testing
- Deployment dry run

---

## Rollback Procedures

### Quick Rollback via UI

1. Go to: Actions > Rollback Deployment
2. Click "Run workflow"
3. Select rollback type:
   - **previous_commit**: Safe, rolls back one commit
   - **container_restart**: Just restart, no code changes
4. Enter reason
5. Click "Run workflow"

### Emergency CLI Rollback

If GitHub Actions is unavailable:

```bash
# SSH into VPS
ssh ziggie@YOUR_VPS_IP

# Go to deployment directory
cd /opt/ziggie

# View recent commits
git log --oneline -10

# Checkout previous version
git checkout HEAD~1 -- .

# Rebuild and restart
docker compose build ziggie-api mcp-gateway sim-studio
docker compose up -d ziggie-api mcp-gateway sim-studio

# Verify
docker compose ps
curl -f http://localhost:8000/health
```

### Database Rollback

For database issues (manual process):

```bash
# List backups
ls -la /opt/ziggie/backups/

# Restore PostgreSQL
docker exec -i ziggie-postgres psql -U ziggie < /opt/ziggie/backups/YYYYMMDD_HHMMSS/postgres_dump.sql

# Or restore schema only
docker exec -i ziggie-postgres psql -U ziggie < /opt/ziggie/backups/YYYYMMDD_HHMMSS/postgres_schema.sql
```

---

## Monitoring & Alerts

### Slack Notifications

Configure the Slack webhook:

1. Go to: https://api.slack.com/apps
2. Create new app > From scratch
3. Add "Incoming Webhooks" feature
4. Create webhook for your channel
5. Copy webhook URL
6. Add as GitHub secret: `SLACK_WEBHOOK_URL`

**Notification Types:**
- Deployment success/failure
- Rollback initiated/completed
- Health check failures

### Status Badges

Add to your README.md:

```markdown
## CI/CD Status

[![Deploy](https://github.com/CraigHux/ziggie-cloud/actions/workflows/deploy.yml/badge.svg)](https://github.com/CraigHux/ziggie-cloud/actions/workflows/deploy.yml)
[![Health Check](https://github.com/CraigHux/ziggie-cloud/actions/workflows/health-check.yml/badge.svg)](https://github.com/CraigHux/ziggie-cloud/actions/workflows/health-check.yml)
[![PR Check](https://github.com/CraigHux/ziggie-cloud/actions/workflows/pr-check.yml/badge.svg)](https://github.com/CraigHux/ziggie-cloud/actions/workflows/pr-check.yml)
```

### Grafana Dashboard (Optional)

If using the monitoring stack, create a dashboard for:
- Deployment frequency
- Success/failure rate
- Average deployment time
- Service uptime

---

## Troubleshooting

### Runner Not Connecting

```bash
# Check runner logs
docker logs ziggie-github-runner

# Common issues:
# 1. Token expired - get new token from GitHub
# 2. Network issue - check firewall
# 3. Already registered - remove old runner first
```

### Deployment Failing

```bash
# Check workflow logs in GitHub Actions

# SSH and check manually
ssh ziggie@YOUR_VPS_IP
cd /opt/ziggie

# Check container status
docker compose ps

# Check specific service logs
docker logs ziggie-api --tail=50
docker logs ziggie-mcp-gateway --tail=50

# Check disk space
df -h
```

### Health Checks Failing

```bash
# Check if services are running
docker ps

# Check if ports are listening
ss -tlnp | grep -E '8000|8080|8001'

# Check Docker network
docker network inspect ziggie-network

# Manual health check
docker exec ziggie-api curl -f http://localhost:8000/health
```

### Rollback Not Working

```bash
# Manual recovery
cd /opt/ziggie

# Stop all services
docker compose down

# Clean up
docker system prune -f

# Pull fresh
git fetch origin
git checkout main
git reset --hard origin/main

# Restart
docker compose up -d
```

---

## Security Checklist

- [ ] Runner token rotated monthly
- [ ] SSH keys use ED25519, not RSA
- [ ] Deploy keys have minimal permissions (read-only if possible)
- [ ] Secrets never logged (use `::add-mask::`)
- [ ] `.env` file excluded from sync
- [ ] No hardcoded credentials in code
- [ ] Branch protection enabled on `main`
- [ ] Required status checks before merge
- [ ] Signed commits (optional but recommended)

---

## Quick Reference

### Common Commands

```bash
# Trigger manual deployment
gh workflow run deploy.yml

# Trigger rollback
gh workflow run rollback.yml -f rollback_type=previous_commit -f reason="Bug in latest"

# Check workflow status
gh run list --workflow=deploy.yml

# View workflow logs
gh run view --log

# Check runner status
gh api repos/CraigHux/ziggie-cloud/actions/runners
```

### Important Paths

| Path | Description |
|------|-------------|
| `/opt/ziggie` | Deployment directory on VPS |
| `/opt/ziggie/.env` | Environment variables (secrets) |
| `/opt/ziggie/backups` | Pre-deployment backups |
| `/tmp/github-runner` | Runner work directory |

---

**Document Status**: Complete
**Last Verified**: 2025-12-28
**Maintainer**: L1 CI/CD Research Agent
