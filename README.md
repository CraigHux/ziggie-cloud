# Ziggie Cloud Infrastructure

Complete Docker-based infrastructure for Ziggie AI Command Center.

## Server Details

| Item | Value |
|------|-------|
| Domain | ziggie.cloud |
| IP | 82.25.112.73 |
| VPS | Hostinger KVM 4 (4 vCPU, 16GB RAM, 200GB NVMe) |

## Services (20 Total)

### Management & Monitoring
- **Portainer** (9443) - Docker UI
- **Grafana** (3000) - Dashboards
- **Prometheus** (9090) - Metrics
- **Loki** (3100) - Logs
- **Promtail** - Log collector
- **cAdvisor** (8081) - Container metrics

### AI & Workflows
- **n8n** (5678) - Workflow automation
- **Ollama** (11434) - Local LLMs (mistral:7b, llama3.2:3b)
- **Flowise** (3001) - LLM workflow builder
- **Open WebUI** (3002) - Chat interface

### Ziggie Core
- **Ziggie API** (8000) - Main backend
- **MCP Gateway** (8080) - MCP routing
- **Sim Studio** (8001) - Agent simulation

### Infrastructure
- **Nginx** (80, 443) - Reverse proxy
- **Certbot** - SSL certificates

### Databases
- **PostgreSQL** (5432)
- **MongoDB** (27017)
- **Redis** (6379)

### CI/CD
- **GitHub Runner** - Self-hosted
- **Watchtower** - Auto-updates

## Quick Start

```bash
# SSH into server
ssh root@82.25.112.73

# Check containers
docker ps

# View logs
docker logs ziggie-<service>

# Restart service
docker restart ziggie-<service>
```

## Deployment

```bash
# Clone and deploy
git clone https://github.com/CraigHux/ziggie-cloud.git
cd ziggie-cloud
cp .env.example .env
# Edit .env with your values
./deploy.sh
```

## Models Installed

| Model | Size | Purpose |
|-------|------|---------|
| mistral:7b | 4.4 GB | General reasoning, coding |
| llama3.2:3b | 2.0 GB | Fast responses |

## License

Private - CraigHux
