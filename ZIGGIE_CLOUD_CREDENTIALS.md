# Ziggie Cloud - Complete Setup

**KEEP THIS FILE SECURE - DO NOT COMMIT TO GIT**
**Deployed: 2025-12-23**

---

## Server Access

| Item | Value |
|------|-------|
| Domain | ziggie.cloud |
| IP | 82.25.112.73 |
| SSH | `ssh root@82.25.112.73` |

---

## Running Services (20/20 Active)

### HTTPS Endpoints (via Nginx Reverse Proxy)
| Service | HTTPS URL | Status |
|---------|-----------|--------|
| Landing Page | https://ziggie.cloud | SSL |
| n8n | https://ziggie.cloud/n8n/ | SSL |
| Grafana | https://ziggie.cloud/grafana/ | SSL |
| Flowise | https://ziggie.cloud/flowise/ | SSL |
| Open WebUI | https://ziggie.cloud/chat/ | SSL |
| Ziggie API | https://ziggie.cloud/api/ | SSL |
| MCP Gateway | https://ziggie.cloud/mcp/ | SSL |
| Sim Studio | https://ziggie.cloud/sim/ | SSL |
| Ollama | https://ziggie.cloud/ollama/ | SSL |

### Direct Port Access (Internal/Debug)
| Service | URL | Status |
|---------|-----|--------|
| Portainer | https://ziggie.cloud:9443 | Running |
| Grafana | http://ziggie.cloud:3000 | Running |
| Prometheus | http://ziggie.cloud:9090 | Running |
| Loki | http://ziggie.cloud:3100 | Running |
| Promtail | (log collector) | Running |
| cAdvisor | http://ziggie.cloud:8081 | Running |
| n8n | http://ziggie.cloud:5678 | Running |
| Ollama | http://ziggie.cloud:11434 | Running |
| Flowise | http://ziggie.cloud:3001 | Running |
| Open WebUI | http://ziggie.cloud:3002 | Running |
| Ziggie API | http://ziggie.cloud:8000 | Running |
| MCP Gateway | http://ziggie.cloud:8080 | Running |
| Sim Studio | http://ziggie.cloud:8001 | Running |

### Infrastructure
| Service | Port | Status |
|---------|------|--------|
| Nginx | 80, 443 | Running |
| Certbot | (SSL renewal) | Running |

### Databases
| Service | Port | Status |
|---------|------|--------|
| PostgreSQL | 5432 | Healthy |
| MongoDB | 27017 | Healthy |
| Redis | 6379 | Healthy |

### CI/CD & Auto-Updates
| Service | Status | Notes |
|---------|--------|-------|
| GitHub Runner | Running | Connected to CraigHux/ziggie-cloud |
| Watchtower | Running | Auto-updates containers every 5 mins |

---

## Service Credentials

### Portainer (Docker UI)
- URL: https://ziggie.cloud:9443
- Username: admin
- Password: (you set during setup)

### n8n (Workflow Automation)
- URL: http://ziggie.cloud:5678
- Username: (you set during setup)

### Flowise (LLM Workflows)
- URL: http://ziggie.cloud:3001
- Username: admin
- Password: JKAXqApBUKAsQ+RKV7xDRA==

### Grafana (Monitoring)
- URL: http://ziggie.cloud:3000
- Username: admin
- Password: 7rsY3xi2OMpXw7qufAqhcg==

### Open WebUI (Chat with LLMs)
- URL: http://ziggie.cloud:3002
- First user to register = admin

---

## Database Passwords

| Database | Password |
|----------|----------|
| PostgreSQL | 5ul7uBNzJs+b/uuNP9fRaUnl3dPkbk2S |
| MongoDB | X7Zyace3z/50HrNNIdnwPfMKBjVxOlMh |
| Redis | 1MOMk8Q+CYamnS0gQBtfyvgPpK/x2/i6 |

---

## API Keys

| Key | Value |
|-----|-------|
| API_SECRET_KEY | c0594386626b1490c159c5d64b60eb907c170c6d08efe442d11d720e6149c2c5 |
| N8N_ENCRYPTION_KEY | 20ee8cae1cd376f41db4fca23fe8bfbe |
| WEBUI_SECRET_KEY | e49877ad8be4b6204ef7d825afa33e11326b4b486738c6ee11ef4f69b8ff051a |

---

## LLM Models Installed

| Model | Size | Best For |
|-------|------|----------|
| mistral:7b | 4.4 GB | General reasoning, coding, analysis |
| llama3.2:3b | 2.0 GB | Fast responses, simple tasks |

---

## SSL Certificate

| Item | Value |
|------|-------|
| Provider | Let's Encrypt |
| Domain | ziggie.cloud |
| Expires | 2026-03-23 |
| Auto-Renewal | Yes (Certbot) |

---

## Grafana Alert Rules

| Alert | Condition | Duration |
|-------|-----------|----------|
| High Memory Usage | >80% | 5 minutes |
| High CPU Usage | >300% total | 5 minutes |
| Container Count Low | <18 containers | 2 minutes |

---

## n8n Workflows

| Workflow | Description | Status |
|----------|-------------|--------|
| Ziggie Health Monitor | Checks API, MCP, Ollama every 5 min | Imported |
| GitHub Webhook Handler | Receives push events from GitHub | Imported |

---

## GitHub Repository

| Item | Value |
|------|-------|
| URL | https://github.com/CraigHux/ziggie-cloud |
| Runner | ziggie-vps-runner (self-hosted) |
| Auto-Update | Watchtower (every 5 min) |

---

## Quick Commands

```bash
# SSH into server
ssh root@82.25.112.73

# Check all containers
docker ps

# Restart a service
docker restart ziggie-<service>

# Pull new Ollama model
docker exec ziggie-ollama ollama pull mistral
```
