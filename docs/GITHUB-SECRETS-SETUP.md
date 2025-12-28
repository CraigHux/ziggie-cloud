# GitHub Secrets & Variables Configuration

> **Repository**: CraigHux/ziggie-cloud
> **Last Updated**: 2025-12-28

---

## Quick Setup Commands

```bash
# Install GitHub CLI first
# Windows: winget install GitHub.cli
# macOS: brew install gh
# Linux: see https://cli.github.com/

# Authenticate
gh auth login

# Navigate to repository
cd C:\Ziggie
```

---

## Required Secrets

### 1. SLACK_WEBHOOK_URL (Optional but Recommended)

**Purpose**: Send deployment notifications to Slack

**How to get it**:
1. Go to https://api.slack.com/apps
2. Create New App > From Scratch
3. Name: "Ziggie Deployments", Workspace: Your workspace
4. Features > Incoming Webhooks > Activate
5. Add New Webhook to Workspace
6. Select channel (e.g., #deployments)
7. Copy the Webhook URL

**Set via CLI**:
```bash
gh secret set SLACK_WEBHOOK_URL --body "https://hooks.slack.com/services/[REDACTED]"
```

---

### 2. VPS_SSH_KEY (If using SSH action alternative)

**Purpose**: SSH access for remote deployments

**Generate new key**:
```bash
# Generate ED25519 key (most secure)
ssh-keygen -t ed25519 -C "ziggie-deploy@github-actions" -f ./ziggie_deploy_key -N ""

# View the private key (this goes in GitHub)
cat ziggie_deploy_key

# View the public key (this goes on VPS)
cat ziggie_deploy_key.pub
```

**Add public key to VPS**:
```bash
ssh ziggie@YOUR_VPS_IP "echo 'PASTE_PUBLIC_KEY_HERE' >> ~/.ssh/authorized_keys"
```

**Set private key as secret**:
```bash
gh secret set VPS_SSH_KEY < ziggie_deploy_key
```

**Delete local keys after setup**:
```bash
rm ziggie_deploy_key ziggie_deploy_key.pub
```

---

### 3. VPS_HOST

**Purpose**: VPS IP address for SSH connections

```bash
gh secret set VPS_HOST --body "YOUR_VPS_IP_ADDRESS"
```

---

### 4. VPS_USER

**Purpose**: SSH username

```bash
gh secret set VPS_USER --body "ziggie"
```

---

## Environment Variables (Non-Secret)

These are visible in logs and can be set as repository variables.

### Set via CLI

```bash
# Production domain
gh variable set VPS_DOMAIN --body "ziggie.yourdomain.com"

# Deployment directory path
gh variable set DEPLOYMENT_DIR --body "/opt/ziggie"
```

### Set via GitHub UI

1. Go to: Repository > Settings > Secrets and variables > Actions
2. Click "Variables" tab
3. Click "New repository variable"
4. Add each variable

---

## Repository Secrets Reference Table

| Secret Name | Required | Description | Example Value |
|-------------|----------|-------------|---------------|
| `SLACK_WEBHOOK_URL` | Optional | Slack notification webhook | `https://hooks.slack.com/...` |
| `VPS_SSH_KEY` | Conditional* | SSH private key | `-----BEGIN OPENSSH...` |
| `VPS_HOST` | Conditional* | VPS IP address | `123.45.67.89` |
| `VPS_USER` | Conditional* | SSH username | `ziggie` |

*Required only if using SSH-based deployment instead of self-hosted runner

---

## Repository Variables Reference Table

| Variable Name | Required | Description | Example Value |
|---------------|----------|-------------|---------------|
| `VPS_DOMAIN` | Optional | Production domain name | `ziggie.example.com` |
| `DEPLOYMENT_DIR` | Optional | Path on VPS | `/opt/ziggie` |

---

## VPS .env File Secrets

These secrets live on the VPS at `/opt/ziggie/.env` and are NOT stored in GitHub:

| Variable | Description |
|----------|-------------|
| `POSTGRES_PASSWORD` | PostgreSQL password |
| `MONGO_PASSWORD` | MongoDB password |
| `REDIS_PASSWORD` | Redis password |
| `N8N_PASSWORD` | n8n admin password |
| `N8N_ENCRYPTION_KEY` | n8n encryption key |
| `FLOWISE_PASSWORD` | Flowise admin password |
| `GRAFANA_PASSWORD` | Grafana admin password |
| `API_SECRET_KEY` | Ziggie API secret |
| `WEBUI_SECRET_KEY` | Open WebUI secret |
| `AWS_ACCESS_KEY_ID` | AWS credentials |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials |
| `GITHUB_TOKEN` | GitHub PAT for API access |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |

---

## GitHub Runner Token Setup

The runner token is handled differently - it's set in the VPS `.env` file:

### Get Runner Token

1. Go to: https://github.com/CraigHux/ziggie-cloud/settings/actions/runners/new
2. Select "Linux" as the OS
3. Copy the token shown (starts with `A...`)
4. Token is valid for 1 hour

### Set on VPS

```bash
ssh ziggie@YOUR_VPS_IP

# Edit .env file
nano /opt/ziggie/.env

# Add/update these lines:
GITHUB_REPO_URL=https://github.com/CraigHux/ziggie-cloud
GITHUB_RUNNER_TOKEN=AXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Restart the runner
cd /opt/ziggie
docker compose restart github-runner
```

---

## Verification Commands

### Check Secrets are Set

```bash
# List all secrets (names only, not values)
gh secret list

# Expected output:
# SLACK_WEBHOOK_URL    Updated 2025-12-28
# VPS_SSH_KEY          Updated 2025-12-28
# VPS_HOST             Updated 2025-12-28
# VPS_USER             Updated 2025-12-28
```

### Check Variables are Set

```bash
# List all variables
gh variable list

# Expected output:
# VPS_DOMAIN       ziggie.example.com    Updated 2025-12-28
# DEPLOYMENT_DIR   /opt/ziggie           Updated 2025-12-28
```

### Test Runner Connection

```bash
# Check runner status via API
gh api repos/CraigHux/ziggie-cloud/actions/runners --jq '.runners[] | {name, status, busy}'

# Expected output:
# {
#   "name": "ziggie-vps-runner",
#   "status": "online",
#   "busy": false
# }
```

---

## Security Best Practices

1. **Never commit secrets to git**
   - Use `.env.example` as template
   - Add `.env` to `.gitignore`

2. **Rotate secrets regularly**
   - Runner token: Monthly
   - SSH keys: Quarterly
   - API keys: As needed

3. **Minimum permissions**
   - SSH keys: Only access deployment directory
   - GitHub tokens: Only required scopes

4. **Audit access**
   - Review who has access to secrets
   - Remove unused secrets

5. **Use environments for staging**
   ```bash
   # Create production environment with protection rules
   gh api repos/CraigHux/ziggie-cloud/environments/production -X PUT
   ```

---

## Troubleshooting

### "Secret not found" Error

```bash
# Verify secret exists
gh secret list | grep SECRET_NAME

# Re-set if needed
gh secret set SECRET_NAME --body "value"
```

### "Permission denied" for SSH

```bash
# Check key permissions on VPS
ssh ziggie@VPS_IP "ls -la ~/.ssh/"

# Should show:
# -rw------- authorized_keys
# drwx------ .ssh

# Fix if needed
ssh ziggie@VPS_IP "chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
```

### Runner Token Expired

```bash
# Tokens expire in 1 hour
# Get new token from GitHub UI
# Update on VPS and restart runner

ssh ziggie@VPS_IP "cd /opt/ziggie && docker compose restart github-runner"
```

---

## Complete Setup Script

Run this to set up all secrets at once:

```bash
#!/bin/bash
# save as: setup-github-secrets.sh

echo "Setting up GitHub secrets for Ziggie CI/CD..."

# Check gh is installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI not installed. Install from: https://cli.github.com/"
    exit 1
fi

# Check authentication
if ! gh auth status &> /dev/null; then
    echo "Please authenticate: gh auth login"
    exit 1
fi

# Prompt for values
read -p "Slack Webhook URL (or press Enter to skip): " SLACK_URL
read -p "VPS IP Address: " VPS_IP
read -p "VPS Username [ziggie]: " VPS_USER
VPS_USER=${VPS_USER:-ziggie}

# Set secrets
if [ -n "$SLACK_URL" ]; then
    gh secret set SLACK_WEBHOOK_URL --body "$SLACK_URL"
    echo "Set SLACK_WEBHOOK_URL"
fi

gh secret set VPS_HOST --body "$VPS_IP"
echo "Set VPS_HOST"

gh secret set VPS_USER --body "$VPS_USER"
echo "Set VPS_USER"

# Generate and set SSH key
if [ ! -f ziggie_deploy_key ]; then
    ssh-keygen -t ed25519 -C "ziggie-deploy" -f ziggie_deploy_key -N ""
fi

gh secret set VPS_SSH_KEY < ziggie_deploy_key
echo "Set VPS_SSH_KEY"

echo ""
echo "Add this public key to VPS:"
cat ziggie_deploy_key.pub
echo ""
echo "Run: ssh $VPS_USER@$VPS_IP \"echo 'PASTE_KEY' >> ~/.ssh/authorized_keys\""

# Set variables
gh variable set VPS_DOMAIN --body "ziggie.example.com"
gh variable set DEPLOYMENT_DIR --body "/opt/ziggie"

echo ""
echo "Setup complete! Verify with: gh secret list && gh variable list"
```

---

**Document Status**: Complete
**Created**: 2025-12-28
