# 24/7 VPS Pipeline Deployment Plan

> **Created**: 2025-12-30 (Session O)
> **Purpose**: Move Ziggie Asset Pipeline to 24/7 autonomous execution on Hostinger VPS
> **Target**: Full pipeline running continuously with Discord human-in-the-loop approvals
> **Estimated Setup Time**: 2-3 hours

---

## Executive Summary

This plan migrates the Ziggie asset pipeline from local execution to 24/7 cloud operation on Hostinger VPS, enabling continuous asset generation with human approval gates via Discord.

**Before**: Local machine runs pipeline → Limited to when PC is on (~8 hrs/day)
**After**: VPS runs pipeline 24/7 → Continuous operation with Discord approvals

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    HOSTINGER VPS (82.25.112.73)                         │
│                         Ubuntu 22.04 LTS                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   n8n       │  │ Discord Bot │  │   Blender   │  │   Python    │   │
│  │ Orchestrator│  │ Ziggie-mini │  │  Headless   │  │  PIL/Pillow │   │
│  │  Port 5678  │  │   24/7      │  │  CLI Only   │  │ Stages 3,6,7│   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   │
│         │                │                │                │          │
│         └────────────────┴────────────────┴────────────────┘          │
│                                   │                                    │
└───────────────────────────────────┼────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
           ┌────────▼────────┐            ┌────────▼────────┐
           │   CLOUD APIs    │            │   CLOUD STORAGE │
           ├─────────────────┤            ├─────────────────┤
           │ RunPod (Stage 1)│            │ AWS S3          │
           │ HuggingFace (2) │            │ GitHub Repo     │
           │ Meshy.ai (4)    │            │ Discord CDN     │
           │ Tripo AI (4.5)  │            │                 │
           └─────────────────┘            └─────────────────┘
```

---

## Prerequisites Checklist

### Local Machine Requirements
- [ ] SSH access to Hostinger VPS configured
- [ ] All API keys available in `.env.local`
- [ ] Pipeline scripts tested locally (Stages 1-7)

### VPS Requirements (Current State)
- [ ] SSH accessible at 82.25.112.73
- [ ] Docker installed
- [ ] n8n container running
- [ ] Sufficient disk space (>10GB free)

### API Access Verified
- [ ] RunPod API key valid
- [ ] Meshy API key valid
- [ ] HuggingFace access working
- [ ] Discord Bot token valid
- [ ] Tripo AI key valid (if using Stage 4.5)

---

## Phase 1: VPS Environment Setup (30 min)

### 1.1 Connect to VPS and Verify State

```bash
# From local machine
ssh root@82.25.112.73

# On VPS - Check current state
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
df -h  # Check disk space
python3 --version  # Should be 3.10+
```

### 1.2 Install System Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install Python 3.11+ and pip
apt install -y python3.11 python3.11-venv python3-pip

# Install Blender (headless)
apt install -y blender

# Verify Blender
blender --version
# Expected: Blender 3.x or 4.x

# Install additional dependencies
apt install -y git wget curl jq
```

### 1.3 Create Pipeline Directory Structure

```bash
# Create Ziggie directory structure
mkdir -p /opt/ziggie/{scripts,assets,logs,configs}
mkdir -p /opt/ziggie/assets/{stage1_generated,stage2_nobg,stage3_upscaled}
mkdir -p /opt/ziggie/assets/{stage4_3d,stage4_5_rigged,stage5_sprites}
mkdir -p /opt/ziggie/assets/{stage6_sheets,stage7_factions}

# Set permissions
chmod -R 755 /opt/ziggie
```

### 1.4 Setup Python Virtual Environment

```bash
# Create venv
python3.11 -m venv /opt/ziggie/venv

# Activate
source /opt/ziggie/venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install pillow requests gradio_client discord.py aiohttp python-dotenv
pip install tripo3d  # For Stage 4.5 (optional)

# Verify
python -c "import PIL; print(f'Pillow {PIL.__version__}')"
python -c "import discord; print(f'discord.py {discord.__version__}')"
```

---

## Phase 2: Deploy Pipeline Scripts (20 min)

### 2.1 Copy Scripts from Local to VPS

```bash
# From local Windows machine (PowerShell)
scp C:/Ziggie/scripts/automated_pipeline.py root@82.25.112.73:/opt/ziggie/scripts/
scp C:/Ziggie/scripts/discord_bot.py root@82.25.112.73:/opt/ziggie/scripts/
scp C:/Ziggie/scripts/pipeline_notifications.py root@82.25.112.73:/opt/ziggie/scripts/
scp C:/Ziggie/scripts/blender_8dir_render.py root@82.25.112.73:/opt/ziggie/scripts/
scp C:/Ziggie/scripts/blender_thumbnail.py root@82.25.112.73:/opt/ziggie/scripts/
```

### 2.2 Create VPS Environment File

```bash
# On VPS
cat > /opt/ziggie/configs/.env << 'EOF'
# RunPod Serverless
RUNPOD_API_KEY=<your-runpod-api-key>

# Meshy.ai 3D Generation
MESHY_API_KEY=<your-meshy-api-key>

# Discord Bot
DISCORD_BOT_TOKEN=<your-discord-bot-token>
DISCORD_APPROVAL_CHANNEL_ID=<your-channel-id>
DISCORD_WEBHOOK_URL=<your-discord-webhook-url>

# n8n Webhooks
N8N_WEBHOOK_URL=https://ziggie.cloud/n8n/webhook/pipeline-approval
N8N_BASE_URL=https://ziggie.cloud/n8n

# Tripo AI (Optional - for Stage 4.5)
TRIPO_API_KEY=

# Paths
BLENDER_PATH=/usr/bin/blender
OUTPUT_DIR=/opt/ziggie/assets
EOF

# Secure the file
chmod 600 /opt/ziggie/configs/.env
```

### 2.3 Update Pipeline Script for VPS Paths

Create a VPS-specific config overlay:

```bash
cat > /opt/ziggie/scripts/vps_config.py << 'EOF'
"""VPS-specific configuration overrides for automated_pipeline.py"""
import os
from pathlib import Path

# Load environment
from dotenv import load_dotenv
load_dotenv('/opt/ziggie/configs/.env')

VPS_CONFIG = {
    "input_dir": "/opt/ziggie/assets/concepts",
    "output_dir": "/opt/ziggie/assets",
    "stage1_output": "/opt/ziggie/assets/stage1_generated",
    "stage2_output": "/opt/ziggie/assets/stage2_nobg",
    "stage3_output": "/opt/ziggie/assets/stage3_upscaled",
    "stage4_output": "/opt/ziggie/assets/stage4_3d",
    "stage4_5_output": "/opt/ziggie/assets/stage4_5_rigged",
    "stage5_output": "/opt/ziggie/assets/stage5_sprites",
    "stage6_output": "/opt/ziggie/assets/stage6_sheets",
    "stage7_output": "/opt/ziggie/assets/stage7_factions",

    # VPS Blender path
    "blender_path": "/usr/bin/blender",
    "blender_script": "/opt/ziggie/scripts/blender_8dir_render.py",

    # API Keys from environment
    "runpod_api_key": os.getenv("RUNPOD_API_KEY"),
    "meshy_api_key": os.getenv("MESHY_API_KEY"),
    "tripo_api_key": os.getenv("TRIPO_API_KEY"),
    "discord_webhook_url": os.getenv("DISCORD_WEBHOOK_URL"),
}

def apply_vps_config(config_dict):
    """Overlay VPS config onto main CONFIG"""
    config_dict.update(VPS_CONFIG)
    return config_dict
EOF
```

---

## Phase 3: Deploy Discord Bot as Service (15 min)

### 3.1 Create Systemd Service for Discord Bot

```bash
cat > /etc/systemd/system/ziggie-discord-bot.service << 'EOF'
[Unit]
Description=Ziggie Discord Approval Bot
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ziggie/scripts
Environment="PATH=/opt/ziggie/venv/bin:/usr/local/bin:/usr/bin"
EnvironmentFile=/opt/ziggie/configs/.env
ExecStart=/opt/ziggie/venv/bin/python discord_bot.py
Restart=always
RestartSec=10
StandardOutput=append:/opt/ziggie/logs/discord_bot.log
StandardError=append:/opt/ziggie/logs/discord_bot_error.log

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
systemctl daemon-reload
systemctl enable ziggie-discord-bot
systemctl start ziggie-discord-bot

# Check status
systemctl status ziggie-discord-bot
```

### 3.2 Verify Discord Bot is Running

```bash
# Check logs
tail -f /opt/ziggie/logs/discord_bot.log

# Expected output:
# [Discord Bot] Bot ready: Ziggie-mini#3047
# [Discord Bot] Guilds: ['Your Server Name']
# [Discord Bot] Channel found: #announcements
```

---

## Phase 4: Configure n8n Orchestration (30 min)

### 4.1 Access n8n Dashboard

```
URL: https://ziggie.cloud/n8n
# or if not configured: http://82.25.112.73:5678
```

### 4.2 Import Pipeline Workflow

Create this workflow in n8n:

```json
{
  "name": "Ziggie Asset Pipeline - 24/7",
  "nodes": [
    {
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300],
      "parameters": {
        "path": "pipeline-start",
        "httpMethod": "POST",
        "responseMode": "onReceived"
      }
    },
    {
      "name": "Parse Request",
      "type": "n8n-nodes-base.set",
      "position": [450, 300],
      "parameters": {
        "values": {
          "string": [
            {"name": "prompt", "value": "={{$json.prompt}}"},
            {"name": "asset_type", "value": "={{$json.asset_type || 'unit'}}"},
            {"name": "skip_stages", "value": "={{$json.skip_stages || ''}}"}
          ]
        }
      }
    },
    {
      "name": "Execute Pipeline",
      "type": "n8n-nodes-base.executeCommand",
      "position": [650, 300],
      "parameters": {
        "command": "cd /opt/ziggie/scripts && source /opt/ziggie/venv/bin/activate && python automated_pipeline.py --prompt \"{{$node['Parse Request'].json.prompt}}\" --asset-type {{$node['Parse Request'].json.asset_type}}"
      }
    },
    {
      "name": "Send Discord Notification",
      "type": "n8n-nodes-base.httpRequest",
      "position": [850, 300],
      "parameters": {
        "method": "POST",
        "url": "={{$env.DISCORD_WEBHOOK_URL}}",
        "jsonParameters": true,
        "bodyParametersJson": "={\"content\": \"Pipeline completed for: {{$node['Parse Request'].json.prompt}}\"}"
      }
    }
  ],
  "connections": {
    "Webhook Trigger": {"main": [[{"node": "Parse Request", "type": "main", "index": 0}]]},
    "Parse Request": {"main": [[{"node": "Execute Pipeline", "type": "main", "index": 0}]]},
    "Execute Pipeline": {"main": [[{"node": "Send Discord Notification", "type": "main", "index": 0}]]}
  }
}
```

### 4.3 Create Scheduled Pipeline Workflow

For batch processing overnight:

```json
{
  "name": "Ziggie Batch Pipeline - Scheduled",
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [250, 300],
      "parameters": {
        "rule": {
          "interval": [{"field": "hours", "hoursInterval": 4}]
        }
      }
    },
    {
      "name": "Check Queue",
      "type": "n8n-nodes-base.executeCommand",
      "position": [450, 300],
      "parameters": {
        "command": "cat /opt/ziggie/assets/queue.json 2>/dev/null || echo '[]'"
      }
    },
    {
      "name": "Process Queue",
      "type": "n8n-nodes-base.executeCommand",
      "position": [650, 300],
      "parameters": {
        "command": "cd /opt/ziggie/scripts && source /opt/ziggie/venv/bin/activate && python batch_processor.py"
      }
    }
  ]
}
```

---

## Phase 5: Create Pipeline Entry Points (20 min)

### 5.1 Discord Slash Command Integration

Update discord_bot.py to add slash commands:

```python
# Add to discord_bot.py on VPS

@bot.tree.command(name="generate", description="Start asset generation pipeline")
@app_commands.describe(
    prompt="Description of the asset to generate",
    asset_type="Type of asset (unit, building, terrain)"
)
async def generate_asset(interaction: discord.Interaction, prompt: str, asset_type: str = "unit"):
    await interaction.response.defer()

    # Add to queue
    queue_path = "/opt/ziggie/assets/queue.json"
    queue = json.load(open(queue_path)) if os.path.exists(queue_path) else []
    queue.append({
        "prompt": prompt,
        "asset_type": asset_type,
        "requested_by": str(interaction.user),
        "requested_at": datetime.now().isoformat()
    })
    json.dump(queue, open(queue_path, 'w'), indent=2)

    await interaction.followup.send(f"Added to queue: **{prompt}**\nQueue position: {len(queue)}")
```

### 5.2 GitHub Actions Trigger

Create `.github/workflows/trigger-pipeline.yml` in meowping-rts repo:

```yaml
name: Trigger Asset Pipeline

on:
  workflow_dispatch:
    inputs:
      prompt:
        description: 'Asset description'
        required: true
        type: string
      asset_type:
        description: 'Asset type'
        required: true
        type: choice
        options:
          - unit
          - building
          - terrain
          - hero

jobs:
  trigger:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Pipeline via Webhook
        run: |
          curl -X POST ${{ secrets.N8N_WEBHOOK_URL }}/pipeline-start \
            -H "Content-Type: application/json" \
            -d '{"prompt": "${{ inputs.prompt }}", "asset_type": "${{ inputs.asset_type }}"}'
```

### 5.3 Web Form Entry Point (n8n)

Create a simple form webhook:

```
n8n Webhook URL: https://ziggie.cloud/n8n/webhook/pipeline-form

Form fields:
- prompt (text): Asset description
- asset_type (select): unit/building/terrain
- priority (select): normal/high/low
```

---

## Phase 6: Setup Monitoring & Health Checks (15 min)

### 6.1 Create Health Check Script

```bash
cat > /opt/ziggie/scripts/health_check.py << 'EOF'
#!/usr/bin/env python3
"""Health check for 24/7 pipeline components"""
import os
import sys
import subprocess
import requests
from datetime import datetime

def check_discord_bot():
    """Check if Discord bot service is running"""
    result = subprocess.run(['systemctl', 'is-active', 'ziggie-discord-bot'],
                          capture_output=True, text=True)
    return result.stdout.strip() == 'active'

def check_n8n():
    """Check if n8n is responding"""
    try:
        response = requests.get('http://localhost:5678/healthz', timeout=5)
        return response.status_code == 200
    except:
        return False

def check_disk_space():
    """Check if enough disk space available"""
    import shutil
    total, used, free = shutil.disk_usage('/opt/ziggie')
    free_gb = free / (1024**3)
    return free_gb > 5  # Minimum 5GB free

def check_blender():
    """Check if Blender is installed"""
    result = subprocess.run(['which', 'blender'], capture_output=True)
    return result.returncode == 0

def main():
    checks = {
        'Discord Bot': check_discord_bot(),
        'n8n': check_n8n(),
        'Disk Space': check_disk_space(),
        'Blender': check_blender(),
    }

    print(f"\n=== Ziggie Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    all_passed = True
    for name, status in checks.items():
        icon = '✅' if status else '❌'
        print(f"{icon} {name}: {'OK' if status else 'FAILED'}")
        if not status:
            all_passed = False

    print(f"\nOverall: {'ALL SYSTEMS GO' if all_passed else 'ISSUES DETECTED'}")
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
EOF

chmod +x /opt/ziggie/scripts/health_check.py
```

### 6.2 Create Cron Job for Health Monitoring

```bash
# Add to crontab
(crontab -l 2>/dev/null; echo "*/30 * * * * /opt/ziggie/venv/bin/python /opt/ziggie/scripts/health_check.py >> /opt/ziggie/logs/health.log 2>&1") | crontab -

# Add daily log rotation
(crontab -l 2>/dev/null; echo "0 0 * * * find /opt/ziggie/logs -name '*.log' -mtime +7 -delete") | crontab -
```

### 6.3 Discord Health Alert Webhook

```bash
cat > /opt/ziggie/scripts/health_alert.py << 'EOF'
#!/usr/bin/env python3
"""Send health alerts to Discord"""
import os
import requests
from health_check import main as run_health_check

WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

def send_alert(message):
    if WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json={
            "content": f"🚨 **Ziggie Health Alert**\n{message}"
        })

if __name__ == '__main__':
    # Capture health check output
    import io
    import sys
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()

    exit_code = run_health_check()

    output = buffer.getvalue()
    sys.stdout = old_stdout

    if exit_code != 0:
        send_alert(output)
        print("Alert sent to Discord")
EOF
```

---

## Phase 7: Verification & Testing (20 min)

### 7.1 Component Verification Checklist

```bash
# Run on VPS

echo "=== Ziggie 24/7 Pipeline Verification ==="

# 1. Python Environment
echo -n "Python: "
/opt/ziggie/venv/bin/python --version

# 2. PIL
echo -n "PIL: "
/opt/ziggie/venv/bin/python -c "import PIL; print(PIL.__version__)"

# 3. Discord.py
echo -n "Discord.py: "
/opt/ziggie/venv/bin/python -c "import discord; print(discord.__version__)"

# 4. Blender
echo -n "Blender: "
blender --version | head -1

# 5. Discord Bot Service
echo -n "Discord Bot: "
systemctl is-active ziggie-discord-bot

# 6. n8n
echo -n "n8n: "
curl -s http://localhost:5678/healthz && echo "OK" || echo "FAILED"

# 7. Disk Space
echo -n "Disk Free: "
df -h /opt/ziggie | tail -1 | awk '{print $4}'

# 8. Environment Variables
echo -n "Env vars: "
[ -f /opt/ziggie/configs/.env ] && echo "Loaded" || echo "MISSING"
```

### 7.2 End-to-End Test

```bash
# Test Stage 3 (PIL Upscaling) locally on VPS
cd /opt/ziggie/scripts
source /opt/ziggie/venv/bin/activate

# Create test image
python -c "
from PIL import Image
img = Image.new('RGB', (256, 256), color='red')
img.save('/opt/ziggie/assets/test_input.png')
print('Test image created')
"

# Test PIL upscaling (Stage 3)
python -c "
from PIL import Image
img = Image.open('/opt/ziggie/assets/test_input.png')
upscaled = img.resize((1024, 1024), Image.LANCZOS)
upscaled.save('/opt/ziggie/assets/test_upscaled.png')
print('Upscaling test: PASSED')
"

# Test Blender (Stage 5) - requires a GLB file
# blender --background --python /opt/ziggie/scripts/blender_8dir_render.py -- --input test.glb --output /opt/ziggie/assets/stage5_sprites
```

### 7.3 Test Discord Bot Approval Flow

```bash
# Send test approval request
cd /opt/ziggie/scripts
source /opt/ziggie/venv/bin/activate

python -c "
from discord_bot import request_discord_approval

decision, feedback = request_discord_approval(
    stage_name='VPS Test',
    asset_name='test_deployment',
    description='Testing 24/7 VPS deployment - please approve',
    stage_number=1,
    timeout_seconds=60
)

print(f'Decision: {decision}')
print(f'Feedback: {feedback}')
"
```

---

## Phase 8: Documentation & Handoff (10 min)

### 8.1 Create Operations Runbook

```bash
cat > /opt/ziggie/docs/OPERATIONS-RUNBOOK.md << 'EOF'
# Ziggie 24/7 Pipeline - Operations Runbook

## Quick Commands

### Start/Stop/Restart Discord Bot
```bash
systemctl start ziggie-discord-bot
systemctl stop ziggie-discord-bot
systemctl restart ziggie-discord-bot
```

### View Logs
```bash
# Discord bot logs
tail -f /opt/ziggie/logs/discord_bot.log

# Health check logs
tail -f /opt/ziggie/logs/health.log

# Pipeline output
ls -la /opt/ziggie/assets/stage*
```

### Manual Pipeline Run
```bash
cd /opt/ziggie/scripts
source /opt/ziggie/venv/bin/activate
python automated_pipeline.py --prompt "Your prompt here"
```

### Health Check
```bash
/opt/ziggie/venv/bin/python /opt/ziggie/scripts/health_check.py
```

## Troubleshooting

### Discord Bot Not Responding
1. Check service status: `systemctl status ziggie-discord-bot`
2. Check logs: `tail -50 /opt/ziggie/logs/discord_bot_error.log`
3. Restart: `systemctl restart ziggie-discord-bot`

### n8n Workflow Not Triggering
1. Check n8n container: `docker ps | grep n8n`
2. Check webhook URL is correct
3. Restart: `docker restart n8n`

### Disk Space Low
1. Check: `df -h /opt/ziggie`
2. Clean old assets: `find /opt/ziggie/assets -mtime +30 -delete`
3. Archive to S3: `aws s3 sync /opt/ziggie/assets s3://ziggie-assets-prod/archive/`
EOF
```

### 8.2 Update Ecosystem Status

After deployment, update `ZIGGIE-ECOSYSTEM-MASTER-STATUS-V5.md` with:

```markdown
## 24/7 Pipeline Status

| Component | Location | Status |
|-----------|----------|--------|
| Discord Bot | Hostinger VPS | ✅ Running |
| n8n Orchestration | Hostinger VPS | ✅ Active |
| PIL Processing | Hostinger VPS | ✅ Available |
| Blender Headless | Hostinger VPS | ✅ Installed |
| Cloud APIs | Serverless | ✅ Connected |

**Deployment Date**: 2025-12-30
**Uptime Target**: 99.9%
```

---

## Rollback Plan

If deployment fails:

```bash
# 1. Stop VPS services
systemctl stop ziggie-discord-bot

# 2. Restore local operation
# On Windows, run pipeline locally as before

# 3. Notify via Discord webhook
curl -X POST $DISCORD_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{"content": "⚠️ VPS deployment rolled back - running locally"}'
```

---

## Cost Summary

| Component | Monthly Cost |
|-----------|-------------|
| Hostinger VPS (existing) | $12 |
| RunPod API usage | ~$5-15 |
| Meshy.ai API | $0 (200 free) |
| HuggingFace API | $0 (free tier) |
| **Total** | **~$17-27/month** |

---

## Next Steps After Deployment

1. [ ] Monitor for 24 hours - check health logs
2. [ ] Run 3 complete pipeline tests
3. [ ] Configure S3 automatic backup
4. [ ] Set up budget alerts
5. [ ] Create asset queue workflow in n8n
6. [ ] Document any issues encountered

---

**Document Status**: Ready for Execution
**Author**: Session O (Ziggie Ecosystem)
**Last Updated**: 2025-12-30
