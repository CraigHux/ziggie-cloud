# n8n Human-in-the-Loop Approval Setup

Interactive approval workflow for the Ziggie asset pipeline using n8n forms.

## Overview

The approval system allows you to review pipeline outputs via a web form instead of console input. When an approval is needed:

1. Pipeline sends request to n8n webhook
2. n8n sends Discord notification with form link
3. You click the link and submit approval form
4. Pipeline receives your decision and continues

## Quick Start - Hostinger VPS (Production)

n8n is running on the Hostinger VPS via nginx reverse proxy:

**Access URL**: https://ziggie.cloud/n8n
**Credentials**: admin / K5t0F5hXkD7peCGQk6RY2g==

> **Note**: Use the HTTPS domain URL, not the direct IP (http://82.25.112.73:5678 shows blank page due to HTTPS-only configuration)

### Import Workflow (ONE-TIME SETUP)

1. Open n8n: <https://ziggie.cloud/n8n>
2. Login with credentials above
3. Click **Workflows** → **Import from File**
4. Select the workflow file (already on VPS at `/opt/ziggie/n8n-workflows/pipeline-approval-workflow.json`)
   - Or upload from local: `C:\Ziggie\n8n-workflows\pipeline-approval-workflow.json`
5. **IMPORTANT**: Set the Discord Webhook URL:
   - Click the **Send Discord Notification** node
   - In "Webhook URL" field, enter your Discord webhook
   - Or set `DISCORD_WEBHOOK_URL` environment variable in VPS `.env`
6. Click **Save** and then **Activate** (toggle in top-right)

### Verify Webhook is Active

```bash
curl -X POST "https://ziggie.cloud/n8n/webhook/pipeline-approval" \
  -H "Content-Type: application/json" \
  -d '{"stage_name": "Test", "asset_name": "test"}'
```

If active, you'll receive a Discord notification with a form link.

## Local n8n (Development - Optional)

```bash
# Install n8n via Docker
docker run -d --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n
```

## Import Workflow

1. Open n8n at http://localhost:5678 (or your VPS URL)
2. Go to **Workflows** → **Import from File**
3. Select: `C:\Ziggie\n8n-workflows\pipeline-approval-workflow.json`
4. Click **Save** and then **Activate** the workflow
5. Copy the webhook URL from the Webhook node

## Configuration

Add to `C:\Ziggie\.secrets\.env.local`:

```env
# Local development
N8N_WEBHOOK_URL=http://localhost:5678/webhook/pipeline-approval
N8N_BASE_URL=http://localhost:5678

# OR VPS production
N8N_WEBHOOK_URL=https://n8n.your-domain.com/webhook/pipeline-approval
N8N_BASE_URL=https://n8n.your-domain.com
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `N8N_WEBHOOK_URL` | Webhook endpoint for approvals | `http://localhost:5678/webhook/pipeline-approval` |
| `N8N_BASE_URL` | n8n base URL | `http://localhost:5678` |
| `DISCORD_WEBHOOK_URL` | Discord notifications | `https://discord.com/api/webhooks/...` |
| `IMGBB_API_KEY` | (Optional) Image hosting for form preview | `your_imgbb_api_key` |

## Testing

```bash
# Test notification system
cd C:\Ziggie\scripts
python pipeline_notifications.py

# Test approval system (will use console fallback if n8n not running)
python pipeline_notifications.py --approval

# Test n8n module directly
python n8n_approval.py
```

## Workflow Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Pipeline       │────▶│  n8n Webhook    │────▶│  Discord        │
│  Stage Complete │     │  (form trigger) │     │  Notification   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │
                              ▼
                        ┌─────────────────┐
                        │  Approval Form  │
                        │  (web browser)  │
                        └─────────────────┘
                              │
                              ▼
                        ┌─────────────────┐
                        │  Decision:      │
                        │  - Approve      │
                        │  - Reject       │
                        │  - Regenerate   │
                        └─────────────────┘
                              │
                              ▼
                        ┌─────────────────┐
                        │  Pipeline       │
                        │  Continues      │
                        └─────────────────┘
```

## Fallback Behavior

If n8n is not available, the system falls back to:
1. **Discord notification** - Sends preview image to Discord (view-only)
2. **Console input** - Prompts for decision in terminal

## Files

| File | Purpose |
|------|---------|
| `n8n-workflows/pipeline-approval-workflow.json` | n8n workflow definition |
| `scripts/n8n_approval.py` | Python integration module |
| `scripts/pipeline_notifications.py` | Main notification system |
| `.secrets/.env.local` | Configuration (API keys, URLs) |

## Troubleshooting

### n8n not accessible
```
[n8n] Could not connect to n8n: Connection refused
```
**Fix**: Start n8n with `docker start n8n` or `n8n start`

### Webhook timeout
```
[n8n] Approval request timed out
```
**Fix**: Form wasn't submitted within timeout period. Default is 1 hour.

### No image preview in form
```
[n8n] Could not upload image for preview
```
**Fix**: Set `IMGBB_API_KEY` for image hosting, or images will be embedded directly

## Security Notes

- Webhook URLs are public endpoints - use HTTPS in production
- Form links are single-use by default
- Consider adding authentication for production use
