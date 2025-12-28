# Ziggie Project - Claude Operating Instructions

> **Scope**: Project-level override for Ziggie AI ecosystem
> **Inherits**: Global CLAUDE.md (~/.claude/CLAUDE.md)
> **Last Updated**: 2025-12-27 (Session A Retrospective)

---

## Project Overview

Ziggie is an AI-controlled development ecosystem for the MeowPing RTS game project. It orchestrates multiple AI agents, MCP servers, and cloud infrastructure to enable automated game asset generation, knowledge management, and development workflows.

### Key Workspaces

| Workspace | Path | Purpose |
|-----------|------|---------|
| **Ziggie** | C:\Ziggie | Core orchestration, API, MCP gateway |
| **MeowPing RTS** | C:\meowping-rts | Game frontend and backend |
| **AI Game Dev System** | C:\ai-game-dev-system | Knowledge base, asset pipelines |
| **Team Ziggie** | C:\team-ziggie | Agent configurations and templates |

---

## Project-Specific Principles

### 1. Agent Hierarchy (1,884 Total)

```text
L0: Executive (MAXIMUS)           → 1 agent
L1: Directors (6 categories)      → 12 agents
L2: Specialists (per director)    → 12 per L1 = 144 agents
L3: Workers (per specialist)      → 12 per L2 = 1,728 agents
                                    ─────────────
                                    1,885 total
```

### 2. Elite Agent Teams

**Technical Team** (invoke via `/elite-technical-team`):
- HEPHAESTUS: Tech Art Director (shaders, LOD, performance)
- DAEDALUS: Pipeline Architect (CI/CD, automation)
- ARGUS: QA Lead (testing, validation)

**Art Team** (invoke via `/elite-art-team`):
- ARTEMIS: Art Director (visual direction, style guides)
- LEONIDAS: Character Artist (unit designs, animations)
- GAIA: Environment Artist (terrain, buildings, props)
- VULCAN: VFX Artist (particles, effects, shaders)

**Design Team** (invoke via `/elite-design-team`):
- TERRA: Level Designer (map layouts, objectives)
- PROMETHEUS: Balance Designer (game mechanics, economy)
- IRIS: UI/UX Designer (interfaces, player experience)
- MYTHOS: Narrative Designer (lore, dialogue, story)

**Production Team** (invoke via `/elite-production-team`):
- MAXIMUS: Executive Producer (vision, strategy)
- FORGE: Technical Producer (risks, blockers)
- ATLAS: Asset Production Manager (pipeline velocity)

### 3. MCP Server Configuration

Active MCP servers for this project:

```json
{
  "filesystem": "C:/Ziggie, C:/ai-game-dev-system, C:/meowping-rts, C:/team-ziggie",
  "memory": "Knowledge graph for project state",
  "chrome-devtools": "Browser automation and debugging",
  "comfyui": "AI image generation (port 8188)",
  "hub": "Multi-backend orchestration"
}
```

---

## Infrastructure Configuration

### AWS Resources (eu-north-1)

| Resource | Status | ID/ARN |
|----------|--------|--------|
| S3 Bucket | Active | ziggie-assets-prod |
| Secrets Manager | Active | ziggie/* namespace |
| Lambda (GPU Shutdown) | Active | ziggie-gpu-auto-shutdown |
| EventBridge Rule | Active | ziggie-gpu-idle-check |
| SNS Topic | Active | ziggie-alerts |
| GPU Launch Template | Ready | ziggie-gpu-spot |

### Docker Services (Hostinger VPS)

18-service stack defined in `C:\Ziggie\hostinger-vps\docker-compose.yml`:

```text
Databases:    postgres, mongodb, redis
Workflows:    n8n, flowise
AI/LLM:       ollama, open-webui, comfyui
Application:  ziggie-api, mcp-gateway, sim-studio
Monitoring:   prometheus, grafana, loki, promtail
Management:   portainer, watchtower, nginx
```

---

## Key File Locations

### Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| MCP Config | C:\Ziggie\.mcp.json | MCP server definitions |
| Docker Stack | C:\Ziggie\hostinger-vps\docker-compose.yml | 18-service stack |
| Nginx Config | C:\Ziggie\hostinger-vps\nginx\nginx.conf | Reverse proxy |
| Deploy Script | C:\Ziggie\hostinger-vps\deploy.sh | One-command deployment |
| AWS Config | C:\Ziggie\aws-config\ | Lambda, lifecycle, CORS |

### Documentation

| Document | Location | Purpose |
|----------|----------|---------|
| Ecosystem Status | C:\Ziggie\ZIGGIE-ECOSYSTEM-MASTER-STATUS-V5.md | Current state |
| AWS Checklist | C:\Ziggie\AWS-HOSTINGER-MASTER-SETUP-CHECKLIST.md | Deployment guide |
| Retrospective | C:\Ziggie\docs\retrospective\ | Session learnings |
| Knowledge Base | C:\ai-game-dev-system\knowledge-base\ | 60+ reference docs |

### Agent Definitions

| Category | Location |
|----------|----------|
| L1 Agents | C:\Ziggie\agents\l1_* |
| Elite Agents | C:\Users\minin\.claude\skills\ |
| BMAD Agents | C:\ai-game-dev-system\bmad-agent\ |

---

## Project-Specific Quality Gates

### Gate 1: Security (ZERO TOLERANCE)

```text
- No API keys in code or plaintext files
- All secrets in AWS Secrets Manager
- SSH key-only authentication
- Rate limiting enabled
```

### Gate 2: Infrastructure

```text
- Docker containers healthy
- MCP servers responding
- Database connections verified
- Health endpoints returning 200
```

### Gate 3: Asset Pipeline

```text
- ComfyUI server running (port 8188)
- Asset naming conventions followed
- Quality ratings assigned (AAA/AA/A/Poor)
- S3 sync completed
```

### Gate 4: Documentation

```text
- Changes documented in relevant .md files
- ZIGGIE-ECOSYSTEM-MASTER-STATUS updated
- Agent outputs saved to appropriate locations
```

---

## Common Commands

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

### Asset Operations

```bash
# Upload to S3
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" s3 cp ./assets/ s3://ziggie-assets-prod/game-assets/ --recursive

# List S3 assets
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" s3 ls s3://ziggie-assets-prod/game-assets/ --recursive

# Get secret
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" secretsmanager get-secret-value --secret-id ziggie/anthropic-api-key --region eu-north-1
```

### Agent Deployment

```text
# Deploy single Elite team
/elite-technical-team
/elite-art-team
/elite-design-team
/elite-production-team

# Deploy full Elite team (15 agents)
/elite-full-team

# Generate game assets
/game-asset-generation
```

---

## Session Patterns for Ziggie

### 1. Infrastructure Session

```text
Phase 1: Security Audit (FIRST)
  - Scan .env files across all workspaces
  - Check for exposed credentials
  - Verify Secrets Manager migration

Phase 2: Health Check
  - Docker container status
  - MCP server connectivity
  - AWS resource verification

Phase 3: Gap Analysis
  - Compare documentation to reality
  - Identify CRITICAL/HIGH/MEDIUM/LOW gaps
  - Update ecosystem status

Phase 4: Remediation
  - Fix P0 issues immediately
  - Create tickets for P1-P3
  - Update documentation
```

### 2. Asset Generation Session

```text
Phase 1: ComfyUI Verification
  - Server running on 8188
  - Models loaded
  - Output directories configured

Phase 2: Generation
  - Use appropriate workflow
  - Apply faction color variants
  - Quality check each batch

Phase 3: Post-Processing
  - Background removal if needed
  - Sprite sheet assembly
  - Quality rating assignment

Phase 4: Integration
  - Upload to S3
  - Update asset index
  - Sync to game frontend
```

### 3. Knowledge Session

```text
Phase 1: Scope Definition
  - Identify topics to research
  - Deploy specialized agents in parallel

Phase 2: Research
  - WebSearch for external sources
  - FileSystem for internal docs
  - Cross-reference findings

Phase 3: Synthesis
  - Compile findings into knowledge docs
  - Update MASTER-INDEX.md
  - Cross-link related documents

Phase 4: Validation
  - BMAD verification pass
  - Gap analysis
  - Quality rating
```

---

## Gap Tracking

Current gaps from Session A Retrospective (42 total):

| Severity | Count | Top Priority |
|----------|-------|--------------|
| CRITICAL | 6 | Rotate exposed API keys, fix crashed containers |
| HIGH | 12 | CI/CD, SSL, backups |
| MEDIUM | 15 | Monitoring, optimization |
| LOW | 9 | Documentation, naming |

See: `C:\Ziggie\ZIGGIE-ECOSYSTEM-MASTER-STATUS-V5.md` for full gap list.

---

## Cost Management

### Monthly Budget Targets

```text
Development:  $10-15/month  (VPS only)
Production:   $47-62/month  (VPS + AWS base)
Heavy AI:     $150-220/month (+ GPU instances)
```

### Cost Control Rules

1. GPU instances: spot pricing only (70% savings)
2. Lambda auto-shutdown: 30-minute idle threshold
3. S3 lifecycle: transition to Glacier after 90 days
4. Budget alerts: 50%, 80%, 100% thresholds

---

## Retrospective References

Session A analysis created comprehensive documentation:

| Document | Lines | Key Content |
|----------|-------|-------------|
| L1-SESSION-LESSONS.md | 587 | 10 lessons, 5 patterns, 5 anti-patterns |
| ELITE-TECHNICAL-PATTERNS.md | 610 | Docker, AWS, CI/CD patterns |
| ELITE-PRODUCTION-METHODOLOGY.md | 568 | WBS, risk management, velocity |
| BMAD-GAP-ANALYSIS-PATTERNS.md | 525 | 5-category framework, quality gates |
| RETROSPECTIVE-SESSION-A-REPORT.md | 407 | Comprehensive synthesis |

---

*Project CLAUDE.md for Ziggie AI Ecosystem*
*Inherits from: ~/.claude/CLAUDE.md (global)*
*Created: 2025-12-27 (Session A Retrospective)*
