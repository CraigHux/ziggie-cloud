# Discord Bot Setup for Pipeline Approvals

Interactive approval system using Discord reactions and buttons.

## Overview

The Discord bot provides a more interactive approval experience than webhooks:

| Feature | Webhook | Bot |
|---------|---------|-----|
| Send messages | Yes | Yes |
| Read reactions | No | Yes |
| Button interactions | No | Yes |
| Slash commands | No | Yes |
| Collect feedback | No | Yes |

## Quick Start

### 1. Create Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application** -> Name it "Ziggie Pipeline Bot"
3. Go to **Bot** section in the left menu
4. Click **Reset Token** -> Copy the token (save it securely!)

### 2. Enable Required Intents

In the Bot settings page, enable:
- **MESSAGE CONTENT INTENT** (required for reading messages)
- **SERVER MEMBERS INTENT** (optional, for user info)

### 3. Generate Invite Link

1. Go to **OAuth2** -> **URL Generator**
2. Select scopes:
   - `bot`
   - `applications.commands`
3. Select bot permissions:
   - Send Messages
   - Embed Links
   - Attach Files
   - Add Reactions
   - Read Message History
   - Use Slash Commands
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

### 4. Get Channel ID

1. In Discord, go to **User Settings** -> **Advanced**
2. Enable **Developer Mode**
3. Right-click the channel you want approval messages in
4. Click **Copy Channel ID**

### 5. Configure Environment

Add to `C:\Ziggie\.secrets\.env.local`:

```env
# Discord Bot (for reaction-based approvals)
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_APPROVAL_CHANNEL_ID=your_channel_id_here
```

### 6. Install Dependencies

```bash
pip install discord.py
```

### 7. Test the Bot

```bash
cd C:\Ziggie\scripts
python discord_bot.py --test
```

This will:
1. Connect the bot to Discord
2. Send a test approval request
3. Wait for your decision (click buttons or react)
4. Show the result

## Usage

### Standalone Bot Service

Run the bot as a persistent service:

```bash
python discord_bot.py
```

The bot will stay connected and handle approval requests.

### Pipeline Integration

The bot integrates automatically with the pipeline. Approval priority:

1. **n8n** (web form) - if configured and available
2. **Discord Bot** (reactions/buttons) - if connected
3. **Console** (terminal input) - fallback

```python
from pipeline_notifications import request_approval

# Will try n8n -> Discord bot -> console
decision, feedback = request_approval(
    title="Stage 4: 2D to 3D",
    image_path="path/to/preview.png",
    stage_number=4,
    asset_name="warrior_model.glb"
)
```

### Direct Bot Usage

```python
from discord_bot import request_discord_approval

decision, feedback = request_discord_approval(
    stage_name="Stage 4: 2D to 3D",
    asset_name="warrior_model.glb",
    image_path="path/to/preview.png",
    timeout_seconds=3600
)
```

## Approval Methods

### Reactions

React to the message with:
- Green checkmark: Approve
- Red X: Reject
- Refresh arrow: Regenerate

### Buttons

Click the colored buttons:
- **Approve** (green) - Accept the output
- **Reject** (red) - Opens feedback modal
- **Regenerate** (blue) - Opens feedback modal

### Slash Commands

```
/approve request_id:Stage_4_123456
/reject request_id:Stage_4_123456 reason:Low quality
/pending - List all pending requests
```

## Bot Permissions Breakdown

| Permission | Purpose |
|------------|---------|
| Send Messages | Post approval requests |
| Embed Links | Rich embed messages |
| Attach Files | Include preview images |
| Add Reactions | Add reaction options |
| Read Message History | Track message state |
| Use Slash Commands | /approve, /reject, /pending |

**Numeric permission value**: `274878024768`

**Invite URL template**:
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=274878024768&scope=bot%20applications.commands
```

## Running as a Service

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task -> "Ziggie Discord Bot"
3. Trigger: At startup
4. Action: Start a program
   - Program: `python`
   - Arguments: `C:\Ziggie\scripts\discord_bot.py`
   - Start in: `C:\Ziggie\scripts`

### Linux (systemd)

Create `/etc/systemd/system/ziggie-discord-bot.service`:

```ini
[Unit]
Description=Ziggie Discord Approval Bot
After=network.target

[Service]
Type=simple
User=ziggie
WorkingDirectory=/opt/ziggie/scripts
Environment="DISCORD_BOT_TOKEN=your_token"
Environment="DISCORD_APPROVAL_CHANNEL_ID=your_channel"
ExecStart=/usr/bin/python3 discord_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable ziggie-discord-bot
sudo systemctl start ziggie-discord-bot
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY scripts/discord_bot.py .
COPY scripts/pipeline_notifications.py .
RUN pip install discord.py
CMD ["python", "discord_bot.py"]
```

```yaml
# Add to docker-compose.yml
discord-bot:
  build:
    context: .
    dockerfile: Dockerfile.discord-bot
  environment:
    - DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN}
    - DISCORD_APPROVAL_CHANNEL_ID=${DISCORD_APPROVAL_CHANNEL_ID}
  restart: unless-stopped
```

## Troubleshooting

### Bot not responding to reactions

**Cause**: MESSAGE CONTENT INTENT not enabled

**Fix**: Go to Discord Developer Portal -> Bot -> Enable MESSAGE CONTENT INTENT

### "Unauthorized" error on startup

**Cause**: Invalid or expired bot token

**Fix**: Reset token in Developer Portal and update .env.local

### Bot offline but no errors

**Cause**: Bot may have been removed from server

**Fix**: Re-invite using the OAuth2 URL

### Reactions work but buttons don't

**Cause**: discord.py version too old

**Fix**: `pip install --upgrade discord.py`

### Channel not found

**Cause**: Wrong channel ID or bot lacks access

**Fix**: Verify channel ID, ensure bot has channel permissions

## Security Notes

1. **Never commit bot token** - Keep in .env.local (gitignored)
2. **Rotate token periodically** - Reset in Developer Portal
3. **Limit channel access** - Only give bot access to approval channel
4. **Use private channels** - For sensitive asset previews

## Comparison: n8n vs Discord Bot

| Aspect | n8n | Discord Bot |
|--------|-----|-------------|
| Setup complexity | Medium | Easy |
| Requires VPS | Yes | No (runs anywhere) |
| Web form UI | Yes | No |
| Custom fields | Yes | Limited |
| Real-time | Polling | Instant |
| Mobile friendly | Yes | Yes |
| Offline fallback | No | Console |

**Recommendation**: Use Discord Bot for quick decisions, n8n for complex workflows.
