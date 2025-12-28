# n8n Quick Reference - Ziggie Ecosystem

> **Purpose**: Fast lookup for common n8n operations, endpoints, and troubleshooting
> **Target**: All team members

---

## Workflow Endpoints (Webhooks)

### Asset Generation
```bash
POST http://n8n:5678/webhook/generate-asset
Content-Type: application/json

{
  "asset_type": "unit_sprite",
  "prompt": "Cat warrior archer",
  "faction_color": "blue",
  "output_format": "png"
}
```

### Batch Generation
```bash
POST http://n8n:5678/webhook/batch-generate
Content-Type: application/json

{
  "assets": [
    {"asset_type": "unit_sprite", "prompt": "Archer", "faction_color": "red"},
    {"asset_type": "building", "prompt": "Barracks", "faction_color": "blue"}
  ],
  "notify_on_complete": true
}
```

### Quality Check
```bash
POST http://n8n:5678/webhook/quality-check
Content-Type: application/json

{
  "s3_key": "game-assets/unit_sprite/red/archer_001.png",
  "quality_threshold": "AA"
}
```

### Agent Orchestration
```bash
POST http://n8n:5678/webhook/orchestrate-agents
Content-Type: application/json

{
  "task": "Generate 50 unit sprites",
  "agents": ["ARTEMIS", "LEONIDAS", "HEPHAESTUS"],
  "priority": "high"
}
```

### Knowledge Base Update
```bash
POST http://n8n:5678/webhook/update-knowledge-base
Content-Type: application/json

{}
```

---

## Service URLs (Internal Docker Network)

| Service | URL | Purpose |
|---------|-----|---------|
| ComfyUI | http://comfyui:8188 | AI image generation |
| Sim Studio | http://sim-studio:8001 | Agent deployment |
| MCP Gateway | http://mcp-gateway:8080 | Knowledge base |
| Ziggie API | http://ziggie-api:8000 | Core API |
| Ollama | http://ollama:11434 | Local LLM |
| Flowise | http://flowise:3000 | LLM workflows |
| Prometheus | http://prometheus:9090 | Metrics |

---

## Common Commands

### View n8n Logs
```bash
docker logs -f ziggie-n8n
```

### Restart n8n
```bash
docker restart ziggie-n8n
```

### Import Workflow
```bash
# Via UI
http://n8n.yourdomain.com:5678/workflows → Import from File

# Via API
curl -X POST http://n8n:5678/rest/workflows \
  -H "Content-Type: application/json" \
  -u admin:${N8N_PASSWORD} \
  -d @asset-generation-pipeline.json
```

### Trigger Manual Execution
```bash
# Via UI
Open workflow → Execute Workflow button

# Via API
curl -X POST http://n8n:5678/rest/workflows/{id}/run \
  -u admin:${N8N_PASSWORD}
```

### View Workflow Executions
```bash
# Via UI
http://n8n.yourdomain.com:5678/executions

# Via API
curl http://n8n:5678/rest/executions \
  -u admin:${N8N_PASSWORD}
```

---

## Environment Variables

```bash
# Required
N8N_PASSWORD=your_password
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

# Service URLs (auto-configured in Docker)
COMFYUI_URL=http://comfyui:8188
SIM_STUDIO_URL=http://sim-studio:8001
MCP_GATEWAY_URL=http://mcp-gateway:8080

# Optional
N8N_METRICS=true
N8N_WORKFLOW_TIMEOUT=3600
```

---

## Scheduled Workflows

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| System Health Monitoring | Every 5 minutes | Check all 15 services |
| Knowledge Base Update | Every 6 hours | Analyze KB staleness |
| Automated Backup | Daily at 3:00 AM | Backup all databases |
| GPU Auto-Shutdown | Every 5 minutes | Shutdown idle GPU instances |

---

## Asset Types and Sizes

| Type | Default Size | Target Size | Use Case |
|------|-------------|-------------|----------|
| `unit_sprite` | 1024x1024 | 128x128 | Characters, units |
| `building` | 1024x1024 | 256x256 | Structures |
| `terrain_tile` | 1024x1024 | 64x64 | Terrain tiles |
| `hero` | 1024x1024 | 256x256 | Hero characters |
| `effect` | 1024x1024 | 128x128 | VFX, particles |
| `prop` | 1024x1024 | 128x128 | Props, items |

---

## Faction Colors

| Faction | Hue Shift | Use Case |
|---------|-----------|----------|
| `red` | 0.0 | Player 1 |
| `blue` | 0.55 | Player 2 |
| `green` | 0.33 | Player 3 |
| `gold` | 0.12 | Player 4 |
| `neutral` | null | NPC, neutral units |

---

## Quality Ratings

| Rating | Score Range | Meaning | Action |
|--------|-------------|---------|--------|
| AAA | 90-100% | Perfect quality | Production-ready |
| AA | 75-89% | Good quality | Minor polish needed |
| A | 50-74% | Acceptable | Requires processing |
| Poor | 0-49% | Unusable | Regenerate |

---

## Elite Agents

### Art Team
- **ARTEMIS**: Art Director
- **LEONIDAS**: Character Artist
- **GAIA**: Environment Artist
- **VULCAN**: VFX Artist

### Technical Team
- **HEPHAESTUS**: Tech Art Director
- **DAEDALUS**: Pipeline Architect
- **ARGUS**: QA Lead

### Design Team
- **TERRA**: Level Designer
- **PROMETHEUS**: Balance Designer
- **IRIS**: UI/UX Designer
- **MYTHOS**: Narrative Designer

### Production Team
- **MAXIMUS**: Executive Producer
- **FORGE**: Technical Producer
- **ATLAS**: Asset Production Manager

---

## Health Check Status

| Status | Condition | Alert Level |
|--------|-----------|-------------|
| `operational` | All services healthy | None |
| `warning` | Some warnings | Log only |
| `degraded` | 1-2 non-critical failures | Discord |
| `critical_failure` | Critical service down | @here mention |

---

## Troubleshooting Quick Fixes

### Workflow not executing
```bash
# Check if workflow is active
# UI: Workflow → Toggle "Active" switch

# Check n8n logs
docker logs -f ziggie-n8n | grep ERROR
```

### ComfyUI timeout
```bash
# Increase timeout in workflow
# HTTP Request node → Options → Timeout: 180000

# Check ComfyUI is running
docker ps | grep comfyui
curl http://comfyui:8188/system_stats
```

### S3 upload fails
```bash
# Verify credentials
docker exec ziggie-n8n env | grep AWS

# Test S3 access
docker exec ziggie-n8n aws s3 ls s3://ziggie-assets-prod/
```

### Discord notification not sending
```bash
# Test webhook
curl -X POST "${DISCORD_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test"}'
```

### Workflow stuck in "Running"
```bash
# View execution details
# UI: Executions → Click execution → View details

# Cancel execution
# UI: Executions → Stop Execution button
```

---

## Metrics (Prometheus)

```promql
# Workflow execution rate
rate(n8n_workflow_executions_total[5m])

# Workflow errors
rate(n8n_workflow_errors_total[5m])

# System health score
ziggie_health_score

# Services unhealthy
ziggie_services_unhealthy
```

---

## API Authentication

```bash
# Basic auth
curl -u admin:${N8N_PASSWORD} http://n8n:5678/rest/workflows

# Example with jq for pretty JSON
curl -u admin:${N8N_PASSWORD} http://n8n:5678/rest/workflows | jq
```

---

## Backup Locations

| Component | S3 Location |
|-----------|-------------|
| Full Backup | `s3://ziggie-backups/backups/YYYY-MM-DD/ziggie-backup-YYYY-MM-DD.tar.gz` |
| MongoDB | Included in tar.gz |
| PostgreSQL | Included in tar.gz |
| n8n Workflows | Included in tar.gz |
| Redis | Included in tar.gz |

---

## Cost Estimates

### Workflow Execution Costs

| Workflow | Avg Duration | AWS Cost/Execution |
|----------|--------------|-------------------|
| Asset Generation | 30-60s | $0.001 (ComfyUI GPU) |
| Batch Generation (50) | 8-10 min | $0.05 |
| Quality Check | 5-10s | $0.0001 |
| System Health | 5-10s | $0.0001 |
| Agent Orchestration | 10-20s | $0.0005 |

### Monthly Totals (Estimated)

| Component | Cost/Month |
|-----------|------------|
| n8n VPS hosting | Included in Hostinger |
| S3 storage (100GB assets) | $2-3 |
| S3 storage (10GB backups) | $0.50 |
| S3 requests | $0.50 |
| Discord | Free |
| Prometheus/Grafana | Included in Docker |
| **Total** | **~$3-4/month** |

---

## Contact / Support

- **n8n Documentation**: https://docs.n8n.io
- **Workflow Issues**: Check `docker logs ziggie-n8n`
- **Integration Issues**: Check service-specific logs
- **Discord Channel**: #ziggie-alerts

---

**Quick Ref Version**: 1.0
**Last Updated**: 2025-12-28
