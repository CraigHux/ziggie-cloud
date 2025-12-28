# GitHub Secrets Configuration Guide
**Repository**: CraigHux/ziggie-cloud
**Author**: DAEDALUS (Pipeline Architect)
**Created**: 2025-12-28

---

## Overview

This document lists all GitHub Secrets required for CI/CD workflows in the Ziggie Command Center repository.

**Location**: Repository → Settings → Secrets and variables → Actions

---

## Required Secrets (CRITICAL)

### Database Passwords

```bash
# PostgreSQL
POSTGRES_PASSWORD="<generate-secure-password>"
# Used by: postgres container, ziggie-api, sim-studio, n8n

# MongoDB
MONGO_PASSWORD="<generate-secure-password>"
# Used by: mongodb container, mcp-gateway, sim-studio

# Redis
REDIS_PASSWORD="<generate-secure-password>"
# Used by: redis container, all services for caching
```

**Generation**:
```bash
# Generate secure passwords (32 characters)
openssl rand -base64 32
```

### Application Secrets

```bash
# API Secret Key (JWT signing)
API_SECRET_KEY="<generate-secure-key>"
# Used by: ziggie-api for JWT token signing

# n8n Encryption Key
N8N_ENCRYPTION_KEY="<generate-32-char-key>"
# Used by: n8n for encrypting credentials in database

# n8n Admin Password
N8N_PASSWORD="<create-strong-password>"
# Used by: n8n web UI authentication

# Flowise Admin Password
FLOWISE_PASSWORD="<create-strong-password>"
# Used by: flowise web UI authentication

# Grafana Admin Password
GRAFANA_PASSWORD="<create-strong-password>"
# Used by: grafana web UI authentication

# Open WebUI Secret Key
WEBUI_SECRET_KEY="<generate-secure-key>"
# Used by: open-webui session management
```

---

## External API Keys

### AI/LLM Services

```bash
# OpenAI API Key
OPENAI_API_KEY="sk-..."
# Used by: n8n workflows, flowise, AI features
# Get from: https://platform.openai.com/api-keys

# Anthropic API Key
ANTHROPIC_API_KEY="sk-ant-..."
# Used by: n8n workflows, flowise, AI features
# Get from: https://console.anthropic.com/settings/keys
```

### AWS Services

```bash
# AWS Access Key
AWS_ACCESS_KEY_ID="AKIA..."
# Used by: S3 operations, Secrets Manager, Lambda

# AWS Secret Key
AWS_SECRET_ACCESS_KEY="..."
# Used by: AWS authentication
# Get from: AWS IAM Console → Users → Security credentials
```

### GitHub Integration

```bash
# GitHub Personal Access Token
GITHUB_TOKEN="ghp_..."
# Used by: API access, repository operations, n8n
# Scopes required: repo, workflow, read:org
# Get from: GitHub Settings → Developer settings → Personal access tokens

# GitHub Runner Token (auto-generated)
GITHUB_RUNNER_TOKEN="..."
# Used by: Self-hosted runner registration
# Get from: Repository Settings → Actions → Runners → New runner

# GitHub OAuth (for n8n)
GITHUB_CLIENT_ID="..."
GITHUB_CLIENT_SECRET="..."
# Get from: GitHub Settings → Developer settings → OAuth Apps
```

---

## Optional Secrets

### Notifications

```bash
# Slack Webhook URL
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
# Used by: Deployment notifications, health alerts
# Get from: Slack App → Incoming Webhooks
```

---

## Environment Variables (Not Secrets)

These are configuration values, not sensitive:

```bash
# Domain
VPS_DOMAIN="ziggie.cloud"

# Deployment Directory
DEPLOYMENT_DIR="/opt/ziggie"

# AWS Region
AWS_REGION="eu-north-1"
```

---

## Setup Instructions

### 1. Generate All Secrets

```bash
#!/bin/bash
# generate-secrets.sh

echo "Generating secure secrets for Ziggie..."

# Database passwords
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32)"
echo "MONGO_PASSWORD=$(openssl rand -base64 32)"
echo "REDIS_PASSWORD=$(openssl rand -base64 32)"

# Application secrets
echo "API_SECRET_KEY=$(openssl rand -base64 32)"
echo "N8N_ENCRYPTION_KEY=$(openssl rand -base64 24 | head -c 32)"
echo "N8N_PASSWORD=$(openssl rand -base64 16)"
echo "FLOWISE_PASSWORD=$(openssl rand -base64 16)"
echo "GRAFANA_PASSWORD=$(openssl rand -base64 16)"
echo "WEBUI_SECRET_KEY=$(openssl rand -base64 32)"

echo ""
echo "⚠️  SAVE THESE SECRETS SECURELY!"
echo "Do NOT commit them to the repository"
```

Run this script:
```bash
chmod +x generate-secrets.sh
./generate-secrets.sh > secrets.txt

# Review and save securely
cat secrets.txt

# Delete after copying to GitHub
shred -u secrets.txt
```

### 2. Add Secrets to GitHub

**Via Web UI**:
1. Go to https://github.com/CraigHux/ziggie-cloud/settings/secrets/actions
2. Click "New repository secret"
3. Enter name and value
4. Click "Add secret"
5. Repeat for all secrets

**Via GitHub CLI**:
```bash
# Set secrets from file
gh secret set POSTGRES_PASSWORD < postgres_password.txt
gh secret set MONGO_PASSWORD < mongo_password.txt
gh secret set REDIS_PASSWORD < redis_password.txt

# Set secret from stdin
echo "sk-..." | gh secret set OPENAI_API_KEY

# Set secret interactively
gh secret set API_SECRET_KEY
# (paste value when prompted)
```

### 3. Verify Secrets

```bash
# List all secrets (values are hidden)
gh secret list

# Expected output:
# POSTGRES_PASSWORD      Updated 2025-12-28
# MONGO_PASSWORD         Updated 2025-12-28
# REDIS_PASSWORD         Updated 2025-12-28
# ...
```

### 4. Test in Workflow

Create a test workflow to verify secrets are accessible:

```yaml
# .github/workflows/test-secrets.yml
name: Test Secrets
on: workflow_dispatch

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Test secrets existence
        run: |
          # Test if secrets are set (don't print values!)
          if [ -z "${{ secrets.POSTGRES_PASSWORD }}" ]; then
            echo "::error::POSTGRES_PASSWORD not set"
            exit 1
          fi
          echo "✅ All required secrets are set"
```

---

## Secrets Usage Matrix

| Secret | Used By | Required For |
|--------|---------|--------------|
| `POSTGRES_PASSWORD` | postgres, ziggie-api, n8n, sim-studio | Database access |
| `MONGO_PASSWORD` | mongodb, mcp-gateway, sim-studio | Document storage |
| `REDIS_PASSWORD` | redis, all services | Caching, sessions |
| `API_SECRET_KEY` | ziggie-api | JWT token signing |
| `N8N_PASSWORD` | n8n | Web UI login |
| `N8N_ENCRYPTION_KEY` | n8n | Credential encryption |
| `FLOWISE_PASSWORD` | flowise | Web UI login |
| `GRAFANA_PASSWORD` | grafana | Dashboard access |
| `WEBUI_SECRET_KEY` | open-webui | Session management |
| `OPENAI_API_KEY` | n8n, flowise, workflows | AI features |
| `ANTHROPIC_API_KEY` | n8n, flowise, workflows | Claude API |
| `AWS_ACCESS_KEY_ID` | mcp-gateway, workflows | AWS services |
| `AWS_SECRET_ACCESS_KEY` | mcp-gateway, workflows | AWS authentication |
| `GITHUB_TOKEN` | workflows, n8n | Repository access |
| `GITHUB_RUNNER_TOKEN` | github-runner | Runner registration |
| `SLACK_WEBHOOK_URL` | workflows | Notifications |

---

## Security Best Practices

### 1. Never Commit Secrets

**Add to `.gitignore`**:
```gitignore
# Secrets
.env
.env.local
.env.*.local
secrets.txt
*_password.txt
*_secret.txt
*.pem
*.key
```

### 2. Rotate Secrets Regularly

**Rotation Schedule**:
- Critical secrets (DB passwords): Every 90 days
- API keys: Every 180 days or on compromise
- GitHub tokens: Every 365 days or on compromise

**Rotation Process**:
```bash
# 1. Generate new secret
NEW_SECRET=$(openssl rand -base64 32)

# 2. Update in GitHub
echo "$NEW_SECRET" | gh secret set POSTGRES_PASSWORD

# 3. Update on VPS
ssh root@82.25.112.73
cd /opt/ziggie
nano .env  # Update POSTGRES_PASSWORD

# 4. Restart affected services
docker compose restart postgres ziggie-api n8n sim-studio

# 5. Verify
docker compose logs -f ziggie-api
```

### 3. Limit Secret Access

**GitHub Secret Scopes**:
- Repository secrets: Only this repository
- Organization secrets: All repositories (use sparingly)
- Environment secrets: Specific environment only

**Recommendation**: Use repository secrets for Ziggie-specific values.

### 4. Monitor Secret Usage

```bash
# Check when secrets were last updated
gh secret list

# Audit workflow runs for secret access
gh run list --limit 20

# Review workflow logs for secret leaks
gh run view <run-id> --log
```

### 5. Emergency Secret Revocation

If a secret is compromised:

```bash
# 1. Immediately delete from GitHub
gh secret delete COMPROMISED_SECRET

# 2. Generate new secret
NEW_SECRET=$(openssl rand -base64 32)

# 3. Update in GitHub
echo "$NEW_SECRET" | gh secret set COMPROMISED_SECRET

# 4. Update on VPS
ssh root@82.25.112.73
# Update .env file

# 5. Restart services
docker compose restart

# 6. Revoke old credentials
# For API keys: Revoke in provider console
# For database: Change password
```

---

## Troubleshooting

### Secret Not Available in Workflow

**Symptom**: Workflow fails with "secret not found"

**Diagnosis**:
```bash
# Check if secret exists
gh secret list | grep SECRET_NAME

# Check workflow syntax
# Correct:   ${{ secrets.SECRET_NAME }}
# Incorrect: ${{ env.SECRET_NAME }}
```

**Solution**:
```bash
# Add secret if missing
gh secret set SECRET_NAME
```

### Secret Value Incorrect

**Symptom**: Service fails to authenticate

**Diagnosis**:
```bash
# Check when secret was last updated
gh secret list

# Check service logs
ssh root@82.25.112.73
docker compose logs ziggie-api | grep -i auth
```

**Solution**:
```bash
# Re-set secret
gh secret set POSTGRES_PASSWORD

# Update on VPS
ssh root@82.25.112.73
nano /opt/ziggie/.env
docker compose restart
```

### Secret Leaked in Logs

**Symptom**: Secret visible in workflow logs

**Example**:
```yaml
# ❌ NEVER DO THIS
- run: echo "Password is ${{ secrets.POSTGRES_PASSWORD }}"

# ✅ DO THIS INSTEAD
- run: echo "Password is set"
```

**If Leaked**:
1. Delete workflow run immediately
2. Rotate secret (see Emergency Secret Revocation)
3. Review all workflows for similar issues
4. Update workflows to use secret masking

---

## Secret Validation Checklist

Before deployment, verify:

- [ ] All 18 required secrets are set in GitHub
- [ ] Secrets match values in VPS `.env` file
- [ ] No secrets committed to repository
- [ ] `.gitignore` includes secret file patterns
- [ ] Secrets are at least 16 characters
- [ ] Database passwords are unique (not reused)
- [ ] API keys are valid and not expired
- [ ] GitHub token has required scopes
- [ ] Slack webhook URL is correct (if using)
- [ ] Test workflow passes with secrets

---

## Quick Reference

### Add Secret
```bash
gh secret set SECRET_NAME
# (paste value when prompted)
```

### List Secrets
```bash
gh secret list
```

### Delete Secret
```bash
gh secret delete SECRET_NAME
```

### Update Secret
```bash
echo "new-value" | gh secret set SECRET_NAME
```

### Test Secret in Workflow
```yaml
- name: Test secret
  env:
    SECRET_VAR: ${{ secrets.SECRET_NAME }}
  run: |
    if [ -z "$SECRET_VAR" ]; then
      echo "::error::Secret not set"
      exit 1
    fi
    echo "✅ Secret is set"
```

---

**Document Version**: 1.0
**Last Updated**: 2025-12-28
**Security Classification**: INTERNAL USE ONLY
**Contact**: DAEDALUS (Pipeline Architect)
