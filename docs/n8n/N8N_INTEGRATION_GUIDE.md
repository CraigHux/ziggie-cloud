# n8n Integration Guide for Ziggie Ecosystem

> **Purpose**: Step-by-step integration configuration for n8n workflows with Ziggie services
> **Target**: DevOps, Infrastructure team
> **Prerequisites**: Docker, AWS CLI, n8n basic knowledge

---

## Overview

This guide covers integrating n8n with:
- **ComfyUI** (AI image generation)
- **Sim Studio** (Agent deployment)
- **MCP Gateway** (Knowledge base)
- **AWS S3** (Asset storage)
- **Discord** (Notifications)
- **Prometheus** (Metrics)

---

## 1. n8n Docker Configuration

### docker-compose.yml Entry

```yaml
services:
  n8n:
    image: n8nio/n8n:latest
    container_name: ziggie-n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      # Basic Configuration
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}

      # Webhook Configuration
      - WEBHOOK_URL=https://n8n.yourdomain.com
      - N8N_HOST=n8n.yourdomain.com
      - N8N_PROTOCOL=https
      - N8N_PORT=443

      # Timezone and Locale
      - GENERIC_TIMEZONE=Europe/Stockholm
      - TZ=Europe/Stockholm

      # Metrics and Monitoring
      - N8N_METRICS=true
      - N8N_METRICS_INCLUDE_WORKFLOW_ID_LABEL=true

      # Execution Settings
      - EXECUTIONS_PROCESS=main
      - EXECUTIONS_DATA_SAVE_ON_SUCCESS=all
      - EXECUTIONS_DATA_SAVE_ON_ERROR=all
      - EXECUTIONS_DATA_SAVE_MANUAL_EXECUTIONS=true

      # Workflow Settings
      - N8N_PAYLOAD_SIZE_MAX=16
      - N8N_DEFAULT_BINARY_DATA_MODE=filesystem

      # External Service URLs (internal Docker network)
      - COMFYUI_URL=http://comfyui:8188
      - OLLAMA_URL=http://ollama:11434
      - FLOWISE_URL=http://flowise:3000
      - ZIGGIE_API_URL=http://ziggie-api:8000
      - MCP_GATEWAY_URL=http://mcp-gateway:8080
      - SIM_STUDIO_URL=http://sim-studio:8001
      - PROMETHEUS_URL=http://prometheus:9090

      # Notification Webhooks
      - DISCORD_WEBHOOK_URL=${DISCORD_WEBHOOK_URL}

      # AWS Configuration (for S3 node)
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=eu-north-1

    volumes:
      # Persistent data
      - n8n_data:/home/node/.n8n

      # Workflow backups (read-only)
      - ./n8n-workflows:/workflows:ro

      # Temporary execution data
      - /tmp/n8n:/tmp/n8n

    networks:
      - ziggie-network

    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:5678/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 45s

volumes:
  n8n_data:
    driver: local

networks:
  ziggie-network:
    driver: bridge
```

---

## 2. Environment Variables Setup

### Create `.env` file

```bash
# n8n Authentication
N8N_PASSWORD=your_secure_password_here

# Discord Webhook (create in Discord server settings)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN

# AWS Credentials (from AWS IAM)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=eu-north-1
```

### Security Best Practice: Use AWS Secrets Manager

Instead of plain text in `.env`:

```bash
# Fetch secrets at runtime
export N8N_PASSWORD=$(aws secretsmanager get-secret-value \
  --secret-id ziggie/n8n-password \
  --region eu-north-1 \
  --query SecretString \
  --output text)

export DISCORD_WEBHOOK_URL=$(aws secretsmanager get-secret-value \
  --secret-id ziggie/discord-webhook \
  --region eu-north-1 \
  --query SecretString \
  --output text)
```

---

## 3. AWS S3 Credentials Configuration

### Option A: Environment Variables (simpler)

Already configured in docker-compose.yml above.

### Option B: n8n Credentials UI (recommended for production)

1. Navigate to: `http://n8n.yourdomain.com:5678`
2. Login with admin credentials
3. Go to: **Settings → Credentials → New**
4. Select: **AWS**
5. Configure:
   - **Name**: `ziggie-aws-s3`
   - **Access Key ID**: From AWS IAM
   - **Secret Access Key**: From AWS IAM
   - **Region**: `eu-north-1`
6. Save

---

## 4. Discord Webhook Setup

### Create Webhook in Discord

1. Open Discord server
2. Go to: **Server Settings → Integrations → Webhooks**
3. Click: **New Webhook**
4. Configure:
   - **Name**: Ziggie Notifications
   - **Channel**: #ziggie-alerts (or your channel)
5. Copy webhook URL
6. Add to `.env` file as `DISCORD_WEBHOOK_URL`

### Test Discord Integration

```bash
curl -X POST "${DISCORD_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "embeds": [{
      "title": "Test Notification",
      "description": "n8n integration test",
      "color": 5763719
    }]
  }'
```

Expected: Message appears in Discord channel.

---

## 5. Import Existing Workflows

### Method A: Via n8n UI (Manual)

1. Navigate to: `http://n8n.yourdomain.com:5678/workflows`
2. Click: **Import from File**
3. Upload each JSON file from `C:/Ziggie/n8n-workflows/`
4. Activate workflows

### Method B: Via Docker Volume (Automatic)

Workflows mounted as read-only volume will auto-appear in n8n UI.

```bash
# Verify mount
docker exec ziggie-n8n ls /workflows

# Expected output:
# asset-generation-pipeline.json
# batch-generation.json
# quality-check.json
# agent-orchestration.json
# knowledge-base-update.json
# system-health-monitoring.json
# automated-backup.json
# gpu-auto-shutdown.json
```

---

## 6. Service Integration Configuration

### 6.1 ComfyUI Integration

**Service**: AI Image Generation
**Container**: `comfyui`
**Port**: 8188
**Health Check**: `GET http://comfyui:8188/system_stats`

**Integration Verification**:
```bash
# From n8n container
docker exec ziggie-n8n curl -s http://comfyui:8188/system_stats

# Expected: JSON response with system info
```

**Workflow Nodes Using ComfyUI**:
- Asset Generation Pipeline → "Generate with ComfyUI" node
- Batch Generation → Calls asset pipeline internally

---

### 6.2 Sim Studio Integration

**Service**: Agent Deployment
**Container**: `sim-studio`
**Port**: 8001
**Endpoint**: `POST http://sim-studio:8001/api/agents/deploy`

**Integration Verification**:
```bash
# From n8n container
docker exec ziggie-n8n curl -s http://sim-studio:8001/health

# Expected: { "status": "healthy" }
```

**Workflow Nodes Using Sim Studio**:
- Agent Orchestration → "Deploy to Sim Studio" node

---

### 6.3 MCP Gateway Integration

**Service**: Knowledge Base
**Container**: `mcp-gateway`
**Port**: 8080
**Endpoint**: `GET http://mcp-gateway:8080/memory/read_graph`

**Integration Verification**:
```bash
# From n8n container
docker exec ziggie-n8n curl -s http://mcp-gateway:8080/memory/read_graph

# Expected: JSON with entities and relations
```

**Workflow Nodes Using MCP Gateway**:
- Knowledge Base Update → "Read Current Knowledge Graph" node
- System Health Monitoring → "Check MCP Gateway Health" node

---

### 6.4 AWS S3 Integration

**Service**: Asset Storage
**Bucket**: `ziggie-assets-prod`
**Region**: `eu-north-1`

**Integration Verification**:
```bash
# Test S3 access
aws s3 ls s3://ziggie-assets-prod/ --region eu-north-1

# Expected: List of objects
```

**Required Permissions** (IAM Policy):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::ziggie-assets-prod/*",
        "arn:aws:s3:::ziggie-assets-prod",
        "arn:aws:s3:::ziggie-backups/*",
        "arn:aws:s3:::ziggie-backups"
      ]
    }
  ]
}
```

**Workflow Nodes Using S3**:
- Asset Generation Pipeline → "Upload to S3" node
- Automated Backup → "Upload to S3" node

---

### 6.5 Prometheus Integration

**Service**: Metrics Collection
**Container**: `prometheus`
**Port**: 9090
**Endpoint**: `POST http://prometheus:9090/api/v1/write`

**Integration Verification**:
```bash
# Check Prometheus targets
curl -s http://prometheus:9090/api/v1/targets

# Expected: JSON with target status
```

**Workflow Nodes Using Prometheus**:
- System Health Monitoring → "Push Metrics to Prometheus" node

---

## 7. Webhook Endpoint Configuration

### Webhook Base URL

**Internal**: `http://n8n:5678` (within Docker network)
**External**: `https://n8n.yourdomain.com` (public internet)

### Available Webhook Endpoints

| Workflow | Path | Method | Purpose |
|----------|------|--------|---------|
| Asset Generation | `/webhook/generate-asset` | POST | Generate single asset |
| Batch Generation | `/webhook/batch-generate` | POST | Generate multiple assets |
| Quality Check | `/webhook/quality-check` | POST | Validate asset quality |
| Agent Orchestration | `/webhook/orchestrate-agents` | POST | Deploy Elite agents |
| Knowledge Base Update | `/webhook/update-knowledge-base` | POST | Trigger KB health check |

### Test Webhook Endpoints

```bash
# Example: Asset Generation
curl -X POST http://n8n:5678/webhook/generate-asset \
  -H "Content-Type: application/json" \
  -d '{
    "asset_type": "unit_sprite",
    "prompt": "Test cat warrior",
    "faction_color": "blue"
  }'

# Expected: JSON response with assetId and assetUrl
```

---

## 8. Nginx Reverse Proxy Configuration

### nginx.conf for n8n

```nginx
server {
    listen 80;
    server_name n8n.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name n8n.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/n8n.yourdomain.com.crt;
    ssl_certificate_key /etc/nginx/ssl/n8n.yourdomain.com.key;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-Content-Type-Options nosniff;

    # Increase timeouts for long-running workflows
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;

    location / {
        proxy_pass http://n8n:5678;
        proxy_http_version 1.1;

        # WebSocket support (for n8n UI)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Standard proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Buffer settings
        proxy_buffering off;
        proxy_buffer_size 4k;
    }
}
```

---

## 9. Scheduled Workflow Activation

### Enable Scheduled Triggers

After importing workflows, activate these scheduled triggers:

1. **System Health Monitoring**
   - Schedule: Every 5 minutes
   - Navigate to workflow → Toggle "Active" switch

2. **Knowledge Base Update**
   - Schedule: Every 6 hours
   - Navigate to workflow → Toggle "Active" switch

3. **Automated Backup**
   - Schedule: Daily at 3:00 AM
   - Navigate to workflow → Toggle "Active" switch

4. **GPU Auto-Shutdown**
   - Schedule: Every 5 minutes
   - Navigate to workflow → Toggle "Active" switch

### Verify Scheduled Executions

```bash
# Check n8n logs
docker logs -f ziggie-n8n

# Expected: Scheduled execution logs every 5 minutes/6 hours
```

---

## 10. Monitoring and Observability

### n8n Metrics Endpoint

```bash
# Enable metrics in docker-compose (already configured)
N8N_METRICS=true

# Access metrics
curl http://n8n:5678/metrics

# Expected: Prometheus-format metrics
```

### Prometheus Configuration

Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'n8n'
    static_configs:
      - targets: ['n8n:5678']
    metrics_path: /metrics
    scrape_interval: 30s
```

### Grafana Dashboard

Import dashboard for n8n monitoring:

**Key Metrics**:
- `n8n_workflow_executions_total` - Total executions per workflow
- `n8n_workflow_execution_duration_seconds` - Execution time
- `n8n_workflow_errors_total` - Error count
- `ziggie_health_score` - System health (custom metric from workflow)

---

## 11. Troubleshooting

### Issue: Workflows not appearing

**Solution**:
```bash
# Check volume mount
docker exec ziggie-n8n ls /workflows

# Re-import manually if needed
# UI: Workflows → Import from File
```

### Issue: ComfyUI unreachable

**Solution**:
```bash
# Check ComfyUI is running
docker ps | grep comfyui

# Test network connectivity
docker exec ziggie-n8n curl http://comfyui:8188/system_stats

# Check both containers on same network
docker network inspect ziggie-network
```

### Issue: S3 upload fails

**Solution**:
```bash
# Verify AWS credentials
docker exec ziggie-n8n env | grep AWS

# Test S3 access
docker exec ziggie-n8n aws s3 ls s3://ziggie-assets-prod/

# Check IAM permissions (see section 6.4)
```

### Issue: Discord notifications not sending

**Solution**:
```bash
# Verify webhook URL is set
docker exec ziggie-n8n env | grep DISCORD

# Test webhook manually
curl -X POST "${DISCORD_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test from curl"}'
```

### Issue: Workflow execution timeout

**Solution**:
```bash
# Increase timeout in workflow node settings
# HTTP Request node → Options → Timeout: 180000 (3 minutes)

# Or increase global timeout in docker-compose
- N8N_WORKFLOW_TIMEOUT=3600  # 1 hour
```

---

## 12. Security Hardening

### 12.1 Enable HTTPS for Webhooks

```bash
# Set WEBHOOK_URL to HTTPS
WEBHOOK_URL=https://n8n.yourdomain.com
N8N_PROTOCOL=https
N8N_PORT=443
```

### 12.2 Implement Webhook Authentication

Add to workflow webhook trigger:

```javascript
// Webhook Trigger → Authentication → Header Auth
const signature = headers['x-ziggie-signature'];
const secret = $env.WEBHOOK_SECRET;

const expectedSignature = crypto
  .createHmac('sha256', secret)
  .update(JSON.stringify(body))
  .digest('hex');

if (signature !== expectedSignature) {
  throw new Error('Invalid signature');
}
```

### 12.3 Rate Limiting

Add to nginx.conf:

```nginx
# Limit requests per IP
limit_req_zone $binary_remote_addr zone=webhook_limit:10m rate=10r/s;

location /webhook/ {
    limit_req zone=webhook_limit burst=20;
    proxy_pass http://n8n:5678;
}
```

---

## 13. Deployment Checklist

- [ ] Docker Compose configured with all environment variables
- [ ] AWS S3 credentials configured (UI or environment)
- [ ] Discord webhook URL set
- [ ] All 8 workflows imported
- [ ] ComfyUI connectivity verified
- [ ] Sim Studio connectivity verified
- [ ] MCP Gateway connectivity verified
- [ ] S3 upload permissions tested
- [ ] Scheduled workflows activated (4 total)
- [ ] Nginx reverse proxy configured
- [ ] SSL certificate installed
- [ ] Prometheus scraping n8n metrics
- [ ] Grafana dashboard created
- [ ] Webhook endpoints tested
- [ ] Discord notifications tested
- [ ] Backup workflow tested
- [ ] GPU auto-shutdown tested (if applicable)

---

## 14. Next Steps

1. **Week 1**: Deploy core workflows (asset generation, health monitoring)
2. **Week 2**: Add backup automation and GPU shutdown
3. **Week 3**: Implement webhook authentication and rate limiting
4. **Week 4**: Set up Grafana dashboards and alerts

---

**Document Version**: 1.0
**Last Updated**: 2025-12-28
**Maintained By**: L1 Strategic Research Agent - n8n Workflow Optimization
