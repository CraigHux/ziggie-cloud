# Discord Webhook Setup Guide for Ziggie Ecosystem

This guide covers the complete setup process for Discord notifications in the Ziggie ecosystem.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Creating a Discord Webhook](#creating-a-discord-webhook)
3. [Storing Webhook URL Securely](#storing-webhook-url-securely)
4. [Configuration Options](#configuration-options)
5. [Testing the Integration](#testing-the-integration)
6. [n8n Workflow Setup](#n8n-workflow-setup)
7. [Integration Points](#integration-points)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Discord server with admin or "Manage Webhooks" permissions
- AWS CLI configured (for Secrets Manager storage)
- Python 3.9+ with dependencies installed
- n8n instance running (for workflow integration)

### Required Python Packages

```bash
pip install aiohttp boto3
```

---

## Creating a Discord Webhook

### Step 1: Open Server Settings

1. Open Discord and navigate to your server
2. Click the server name at the top left
3. Select "Server Settings" from the dropdown

### Step 2: Navigate to Integrations

1. In the left sidebar, click "Integrations"
2. Click "Webhooks"
3. Click "New Webhook"

### Step 3: Configure the Webhook

1. **Name**: `Ziggie Bot` (or your preferred name)
2. **Avatar**: Upload a bot avatar (optional)
3. **Channel**: Select the channel for notifications
   - Recommended: Create dedicated channels:
     - `#ziggie-alerts` - For errors and critical notifications
     - `#ziggie-deployments` - For deployment updates
     - `#ziggie-assets` - For asset generation notifications
     - `#ziggie-costs` - For cost alerts

### Step 4: Copy the Webhook URL

1. Click "Copy Webhook URL"
2. **IMPORTANT**: Never share this URL publicly
3. The URL format: `https://discord.com/api/webhooks/{webhook_id}/{webhook_token}`

### Creating Multiple Webhooks (Recommended)

For better organization, create separate webhooks for different notification types:

| Webhook Name | Channel | Purpose |
|--------------|---------|---------|
| Ziggie Alerts | #ziggie-alerts | Errors, critical issues |
| Ziggie Deploy | #ziggie-deployments | Deployment notifications |
| Ziggie Assets | #ziggie-assets | Asset generation updates |
| Ziggie Costs | #ziggie-costs | Budget and cost alerts |
| Ziggie Backup | #ziggie-backups | Backup status notifications |

---

## Storing Webhook URL Securely

### Option 1: AWS Secrets Manager (Recommended for Production)

```bash
# Store the webhook URL
aws secretsmanager create-secret \
    --name "ziggie/discord-webhook-url" \
    --description "Discord webhook URL for Ziggie notifications" \
    --secret-string '{"webhook_url": "https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN"}' \
    --region eu-north-1

# For multiple webhooks, store as JSON
aws secretsmanager create-secret \
    --name "ziggie/discord-webhooks" \
    --description "Discord webhooks for Ziggie ecosystem" \
    --secret-string '{
        "alerts": "https://discord.com/api/webhooks/...",
        "deployments": "https://discord.com/api/webhooks/...",
        "assets": "https://discord.com/api/webhooks/...",
        "costs": "https://discord.com/api/webhooks/...",
        "backups": "https://discord.com/api/webhooks/..."
    }' \
    --region eu-north-1
```

### Option 2: Environment Variable (Development)

```bash
# Add to your .env file
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN

# For multiple webhooks
DISCORD_WEBHOOK_ALERTS=https://discord.com/api/webhooks/...
DISCORD_WEBHOOK_DEPLOY=https://discord.com/api/webhooks/...
DISCORD_WEBHOOK_ASSETS=https://discord.com/api/webhooks/...
DISCORD_WEBHOOK_COSTS=https://discord.com/api/webhooks/...
DISCORD_WEBHOOK_BACKUP=https://discord.com/api/webhooks/...
```

### Option 3: Docker Compose Secrets

```yaml
# docker-compose.yml
services:
  ziggie-api:
    secrets:
      - discord_webhook_url
    environment:
      - DISCORD_WEBHOOK_URL_FILE=/run/secrets/discord_webhook_url

secrets:
  discord_webhook_url:
    file: ./secrets/discord_webhook_url.txt
```

---

## Configuration Options

### Python Module Configuration

```python
from integrations.discord import DiscordWebhook

# Option 1: Direct URL (development only)
webhook = DiscordWebhook(webhook_url="https://discord.com/api/webhooks/...")

# Option 2: Environment variable
webhook = DiscordWebhook()  # Uses DISCORD_WEBHOOK_URL env var

# Option 3: AWS Secrets Manager (recommended)
webhook = DiscordWebhook(
    use_secrets_manager=True,
    secret_name="ziggie/discord-webhook-url",
    region="eu-north-1"
)
```

### Notification Colors

| Type | Color (Hex) | Usage |
|------|-------------|-------|
| SUCCESS | `#28A745` | Task completed, deployment success |
| ERROR | `#DC3545` | Errors, failures |
| WARNING | `#FFC107` | Warnings, approaching limits |
| INFO | `#17A2B8` | Informational updates |
| ASSET | `#9B59B6` | Asset generation |
| DEPLOY | `#3498DB` | Deployments |
| COST | `#E67E22` | Cost alerts |
| BACKUP | `#1ABC9C` | Backup notifications |

---

## Testing the Integration

### Quick Test with Python

```python
import asyncio
from integrations.discord import DiscordWebhook, NotificationType

async def test():
    webhook = DiscordWebhook()

    result = await webhook.send_notification(
        NotificationType.INFO,
        title="Test Notification",
        description="Discord integration is working!",
        fields=[
            {"name": "Environment", "value": "Development", "inline": True},
            {"name": "Source", "value": "Integration Test", "inline": True}
        ]
    )

    print(f"Notification sent: {result}")
    await webhook.close()

asyncio.run(test())
```

### Test with cURL

```bash
# Test webhook directly
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "username": "Ziggie Test",
    "embeds": [{
      "title": "Test Notification",
      "description": "This is a test message",
      "color": 1752220
    }]
  }' \
  "https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN"
```

### Test n8n Workflow

```bash
# Trigger the n8n webhook
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_N8N_AUTH_TOKEN" \
  -d '{
    "notification_type": "info",
    "title": "Test from n8n",
    "description": "Testing the Discord notification workflow"
  }' \
  "http://localhost:5678/webhook/discord-notify"
```

---

## n8n Workflow Setup

### Importing the Workflow

1. Open n8n at `http://localhost:5678`
2. Go to "Workflows" > "Import from File"
3. Select `C:\Ziggie\integrations\n8n\workflows\discord-notifications.json`
4. Click "Import"

### Configuration Required

1. **Set Environment Variable**:
   - Go to Settings > Variables
   - Add `DISCORD_WEBHOOK_URL` with your webhook URL

2. **Configure Authentication** (Optional):
   - Edit the "Webhook Trigger" node
   - Set header authentication if needed

3. **Activate the Workflow**:
   - Toggle the workflow to "Active"

### Workflow Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook/discord-notify` | POST | Main notification endpoint |

### Payload Examples

**Asset Generated**:
```json
{
  "notification_type": "asset",
  "asset_name": "cat_warrior_blue",
  "asset_type": "Unit Sprite",
  "quality": "AAA",
  "faction": "Blue",
  "preview_url": "https://cdn.example.com/preview.png"
}
```

**Deployment**:
```json
{
  "notification_type": "deployment",
  "environment": "production",
  "version": "v1.2.3",
  "status": "Success",
  "services": ["ziggie-api", "nginx", "redis"],
  "duration": "2m 34s"
}
```

**Error**:
```json
{
  "notification_type": "error",
  "error_type": "ConnectionError",
  "error_message": "Failed to connect to database",
  "source": "ziggie-api",
  "severity": "CRITICAL",
  "trace": "Traceback (most recent call last)..."
}
```

**Cost Alert**:
```json
{
  "notification_type": "cost",
  "service": "AWS S3",
  "current_cost": 45.50,
  "budget_limit": 50.00,
  "period": "monthly",
  "forecast": 55.00
}
```

**Backup**:
```json
{
  "notification_type": "backup",
  "backup_type": "PostgreSQL Full",
  "status": "Complete",
  "size": "2.3 GB",
  "duration": "5m 12s",
  "destination": "s3://ziggie-backups/postgres/2025-12-27/"
}
```

---

## Integration Points

### GitHub Actions Integration

```yaml
# .github/workflows/deploy.yml
- name: Notify Discord - Deploy Started
  run: |
    curl -X POST \
      -H "Content-Type: application/json" \
      -d '{
        "notification_type": "deployment",
        "environment": "${{ github.event.inputs.environment }}",
        "version": "${{ github.sha }}",
        "status": "Started"
      }' \
      "${{ secrets.N8N_WEBHOOK_URL }}/discord-notify"

- name: Notify Discord - Deploy Complete
  if: success()
  run: |
    curl -X POST \
      -H "Content-Type: application/json" \
      -d '{
        "notification_type": "deployment",
        "environment": "${{ github.event.inputs.environment }}",
        "version": "${{ github.sha }}",
        "status": "Success",
        "duration": "${{ steps.deploy.outputs.duration }}"
      }' \
      "${{ secrets.N8N_WEBHOOK_URL }}/discord-notify"
```

### AWS SNS Integration

Create an SNS topic that forwards to n8n:

```bash
# Create SNS topic
aws sns create-topic --name ziggie-discord-notifications

# Create subscription to n8n webhook
aws sns subscribe \
  --topic-arn arn:aws:sns:eu-north-1:ACCOUNT:ziggie-discord-notifications \
  --protocol https \
  --notification-endpoint https://your-n8n-domain.com/webhook/sns-to-discord
```

### Asset Pipeline Integration

```python
# In your asset generation script
from integrations.discord import DiscordWebhook, notify_asset_generated

async def on_asset_complete(asset_info):
    webhook = DiscordWebhook()
    await notify_asset_generated(
        webhook,
        asset_name=asset_info['name'],
        asset_type=asset_info['type'],
        quality_rating=asset_info['quality'],
        preview_url=asset_info.get('preview_url'),
        details={
            'Faction': asset_info.get('faction'),
            'Dimensions': asset_info.get('dimensions')
        }
    )
    await webhook.close()
```

---

## Troubleshooting

### Common Issues

**1. Webhook URL Invalid**
```
Error: Invalid webhook token
```
Solution: Regenerate the webhook in Discord Server Settings > Integrations > Webhooks

**2. Rate Limited**
```
Error: 429 Too Many Requests
```
Solution: The module handles rate limiting automatically. For high-volume scenarios, implement queuing.

**3. Permission Denied**
```
Error: Missing Access
```
Solution: Ensure the webhook has permission to post in the target channel.

**4. AWS Secrets Manager Error**
```
Error: AccessDeniedException
```
Solution: Verify IAM permissions include `secretsmanager:GetSecretValue` for the secret ARN.

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger('integrations.discord').setLevel(logging.DEBUG)
```

### Webhook Health Check

```python
async def check_webhook_health(webhook_url: str) -> bool:
    """Check if webhook is valid and accessible."""
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(webhook_url) as response:
            return response.status == 200
```

---

## Security Best Practices

1. **Never commit webhook URLs to git**
   - Use `.gitignore` to exclude `.env` files
   - Use AWS Secrets Manager for production

2. **Rotate webhooks periodically**
   - Delete old webhooks after rotation
   - Update Secrets Manager with new URLs

3. **Use channel-specific webhooks**
   - Limit blast radius if a webhook is compromised
   - Easier to revoke individual webhooks

4. **Enable rate limiting**
   - Implement application-level rate limiting
   - Prevent webhook abuse

5. **Monitor webhook usage**
   - Track notification counts
   - Alert on unusual activity

---

## Support

For issues with this integration:
1. Check the troubleshooting section above
2. Review Discord's webhook documentation: https://discord.com/developers/docs/resources/webhook
3. Open an issue in the Ziggie repository
