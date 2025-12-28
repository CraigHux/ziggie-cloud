# Ziggie Control Center - AI-Powered Game Development Ecosystem

![Status](https://img.shields.io/badge/VPS%20Containers-20%2F20-brightgreen)
![AWS](https://img.shields.io/badge/AWS-92%25%20Complete-blue)
![Agents](https://img.shields.io/badge/Core%20Agents-584-purple)
![Elite](https://img.shields.io/badge/Elite%20Agents-15-gold)
![MCP](https://img.shields.io/badge/MCP%20Servers-5%20Active-orange)
![Cost](https://img.shields.io/badge/Monthly%20Cost-$80--130-green)

**Version:** 5.0
**Updated:** 2025-12-27
**Architecture:** Docker-based microservices + AWS cloud infrastructure

---

## What is Ziggie?

Ziggie is an AI-controlled development ecosystem for the **MeowPing RTS** game project. It orchestrates:

- **584 Core AI Agents** (8 L1 + 64 L2 + 512 L3) for automated development
- **15 Elite Agents** for specialized tasks (Art, Design, Technical, Production)
- **5 Active MCP Servers** for AI-to-tool communication
- **20 Docker Containers** on Hostinger VPS for production services
- **AWS Integration** (92% complete) for cloud compute and storage

---

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for MCP servers)
- Node.js 20+ (for MCP servers)
- AWS CLI configured (optional, for cloud features)

### Start Local Services

```bash
# Navigate to project root
cd C:\Ziggie

# Start Docker containers
docker-compose up -d

# Services will be available at:
# - Frontend: http://localhost:3001
# - Backend API: http://localhost:54112
# - MongoDB: localhost:27018
```

### VPS Services (Remote)

All 20 containers are running on Hostinger VPS (82.25.112.73):

| Service | Port | Description |
|---------|------|-------------|
| Portainer | 9000 | Docker management UI |
| n8n | 5678 | Workflow automation |
| Ollama | 11434 | Local LLM inference |
| Flowise | 3001 | LLM flow builder |
| Open WebUI | 3002 | Chat interface |
| Grafana | 3000 | Monitoring dashboards |
| PostgreSQL | 5432 | Primary database |
| MongoDB | 27017 | Document database |
| Redis | 6379 | Cache/sessions |

---

## Directory Structure

```
C:\Ziggie\
├── agents/                      # AI Agent System (584 agents)
│   ├── L1-agents/              # 8 Level 1 (strategic) agents
│   ├── L2-agents/              # 64 Level 2 (tactical) agents
│   └── L3-agents/              # 512 Level 3 (micro) agents
│
├── control-center/             # Web Management Interface
│   ├── backend/                # FastAPI backend (port 54112)
│   └── frontend/               # React frontend (port 3001)
│
├── hostinger-vps/              # VPS Configuration
│   ├── docker-compose.yml      # 18-service stack
│   ├── nginx/                  # Reverse proxy config
│   └── deploy.sh               # One-command deployment
│
├── aws-config/                 # AWS Infrastructure
│   ├── lambda/                 # GPU auto-shutdown function
│   └── lifecycle-policies/     # Cost optimization rules
│
├── docs/                       # Documentation
│   └── retrospective/          # Session learnings
│
├── .mcp.json                   # MCP server configuration
├── CLAUDE.md                   # Claude operating instructions
└── ZIGGIE-ECOSYSTEM-MASTER-STATUS-V5.md  # Current ecosystem status
```

---

## Key Commands

### Infrastructure Verification

```bash
# Check Docker containers
docker ps --format "table {{.Names}}\t{{.Status}}"

# Check MCP servers
curl -s http://localhost:54112/api/system/info

# Check ComfyUI
curl -s http://localhost:8188/system_stats

# Check AWS connectivity
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" sts get-caller-identity
```

### Agent Deployment

```bash
# Deploy Elite teams (in Claude Code)
/elite-technical-team    # HEPHAESTUS, DAEDALUS, ARGUS
/elite-art-team          # ARTEMIS, LEONIDAS, GAIA, VULCAN
/elite-design-team       # TERRA, PROMETHEUS, IRIS, MYTHOS
/elite-production-team   # MAXIMUS, FORGE, ATLAS
/elite-full-team         # All 15 Elite Agents
/game-asset-generation   # ComfyUI + Blender pipeline
```

### AWS Operations

```bash
# Upload assets to S3
aws s3 cp ./assets/ s3://ziggie-assets-prod/game-assets/ --recursive

# Get secret from Secrets Manager
aws secretsmanager get-secret-value --secret-id ziggie/anthropic-api-key --region eu-north-1
```

---

## Current Status (V5.0)

### Infrastructure

| Component | Status | Details |
|-----------|--------|---------|
| Hostinger VPS | RUNNING | 20/20 containers healthy |
| AWS | 92% | S3, Secrets, Lambda, SNS active |
| MCP Servers | 5/10 | filesystem, memory, chrome, comfyui, hub |
| Domain | ACTIVE | ziggie.cloud (SSL valid until 2026-03-23) |

### Agent Systems

| Layer | Count | Purpose |
|-------|-------|---------|
| L1 Agents | 8 | Strategic planning |
| L2 Agents | 64 | Tactical execution |
| L3 Agents | 512 | Micro-task workers |
| Elite Agents | 15 | Specialized teams |

### Gaps Resolved

- All 8 CRITICAL gaps resolved (2025-12-27)
- API keys rotated and stored in AWS Secrets Manager
- VPS containers stable and healthy

---

## Related Workspaces

| Workspace | Path | Description |
|-----------|------|-------------|
| [MeowPing RTS](../meowping-rts/README.md) | C:\meowping-rts | Cat-themed RTS game |
| [AI Game Dev System](../ai-game-dev-system/README.md) | C:\ai-game-dev-system | Knowledge base (60+ docs) |
| [Team Ziggie](../team-ziggie/README.md) | C:\team-ziggie | Agent configurations |

---

## Documentation

| Document | Location | Description |
|----------|----------|-------------|
| Ecosystem Status | [ZIGGIE-ECOSYSTEM-MASTER-STATUS-V5.md](ZIGGIE-ECOSYSTEM-MASTER-STATUS-V5.md) | Complete system state |
| AWS Checklist | [AWS-HOSTINGER-MASTER-SETUP-CHECKLIST.md](AWS-HOSTINGER-MASTER-SETUP-CHECKLIST.md) | Deployment guide |
| Claude Instructions | [CLAUDE.md](CLAUDE.md) | Operating principles |
| Gap Tracking | [ZIGGIE-GAP-RESOLUTION-TRACKING-V5.md](ZIGGIE-GAP-RESOLUTION-TRACKING-V5.md) | 45 gaps status |

---

## Cost Summary

| Category | Monthly | Details |
|----------|---------|---------|
| Hostinger VPS | $9.99 | 4 vCPU, 16GB RAM, 200GB NVMe |
| AWS Base | $10-20 | S3, Secrets, Lambda |
| Claude API | $20-50 | Primary AI |
| Other APIs | $10-20 | OpenAI, ElevenLabs |
| **Normal Total** | **$50-100** | Light usage |
| **Heavy AI Total** | **$150-200** | With GPU compute |

---

## Tech Stack

### Backend
- Python 3.11+ (FastAPI, SQLAlchemy)
- Anthropic Claude API
- AWS SDK (boto3)

### Frontend
- React 18 + TypeScript
- Vite + TailwindCSS

### Infrastructure
- Docker + Docker Compose
- Nginx reverse proxy
- PostgreSQL + MongoDB + Redis
- Prometheus + Grafana + Loki

### AI/ML
- ComfyUI (workflow engine)
- Ollama (local LLM)
- Claude Sonnet 4.5 (analysis)

---

## Security

All API keys are stored in AWS Secrets Manager (eu-north-1):
- `ziggie/anthropic-api-key`
- `ziggie/openai-api-key`
- `ziggie/youtube-api-keys`
- `ziggie/aws-credentials`

**Never store API keys in plaintext files.**

---

## Support

- **Status Document**: [ZIGGIE-ECOSYSTEM-MASTER-STATUS-V5.md](ZIGGIE-ECOSYSTEM-MASTER-STATUS-V5.md)
- **Gap Tracking**: [ZIGGIE-GAP-RESOLUTION-TRACKING-V5.md](ZIGGIE-GAP-RESOLUTION-TRACKING-V5.md)
- **Troubleshooting**: See control-center/backend/README.md

---

**Ziggie Control Center - AI-Powered Game Development**

*For quick setup: `docker-compose up -d`*
*For VPS access: `ssh user@82.25.112.73`*
*For full documentation: See V5 Status Document*
