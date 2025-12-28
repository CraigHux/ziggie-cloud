# CLAUDE CODE INTEGRATION PLAN
## Ziggie Ecosystem Full Integration Roadmap

> **Document ID**: ZIGGIE-INTEGRATION-PLAN-V1.0
> **Created**: 2025-12-24
> **Author**: Claude Opus 4.5
> **Status**: PLANNING
> **Methodology**: 7-Stage Gated Integration

---

## EXECUTIVE SUMMARY

This document provides a comprehensive step-by-step integration plan to connect Claude Code with the full Ziggie ecosystem. Following the proven 7-Phase Sprint Execution Model, this plan uses:

- **7 Stages** (major milestones)
- **28 Phases** (execution units within stages)
- **7 Quality Gates** (stage exit criteria)
- **100+ Tasks** (granular action items)

### Integration Scope

| Component | Current | Target | Impact |
|-----------|---------|--------|--------|
| MCP Servers | 3 active | 10+ active | 90+ tools available |
| Filesystem Access | C:/Ziggie only | 4 directories | Full project access |
| Memory Graph | Empty | 50+ entities | Persistent knowledge |
| Game Engines | 0 connected | 3 engines | Unity, Unreal, Godot |
| AI Generation | 0 connected | ComfyUI + Cloud | Asset pipeline |
| Agent System | File-based only | Full orchestration | 1,884 agents |

---

## SUPPORTING DOCUMENTS

This integration plan is supported by comprehensive operational documents for production-ready execution:

| Document | Location | Purpose |
|----------|----------|---------|
| **Task Dependency Graph** | [INTEGRATION-TASK-DEPENDENCY-GRAPH.md](INTEGRATION-TASK-DEPENDENCY-GRAPH.md) | Visual task flow, critical path, parallelization opportunities |
| **Verification Scripts** | [scripts/Verify-IntegrationGates.ps1](scripts/Verify-IntegrationGates.ps1) | Automated PowerShell verification for all 7 gates |
| **Rollback Playbook** | [INTEGRATION-ROLLBACK-PLAYBOOK.md](INTEGRATION-ROLLBACK-PLAYBOOK.md) | Stage-by-stage rollback procedures, recovery scripts |
| **AWS Integration Stage** | [INTEGRATION-AWS-STAGE.md](INTEGRATION-AWS-STAGE.md) | Stage 7.5: S3, Secrets Manager, Lambda, EC2 Spot, Bedrock |
| **Memory Population Script** | [scripts/populate_memory_graph.py](scripts/populate_memory_graph.py) | Python script to create 70+ entities, 58 relations |
| **Memory Population Payload** | [scripts/memory_population_payload.json](scripts/memory_population_payload.json) | JSON payload for Memory MCP tools |

### Quick Commands

```powershell
# Run gate verification (all gates)
.\scripts\Verify-IntegrationGates.ps1

# Run specific gate verification
.\scripts\Verify-IntegrationGates.ps1 -Gate 0

# Export gate verification report
.\scripts\Verify-IntegrationGates.ps1 -Gate 0 -ExportReport

# Generate memory population JSON
python scripts\populate_memory_graph.py --verify --export
```

---

## STAGE 0: PLANNING & ASSESSMENT
### Duration: 30 minutes | Gate: Assessment Complete

#### Phase 0.1: Environment Verification

| Task ID | Task | Command/Action | Expected Result | Status |
|---------|------|----------------|-----------------|--------|
| 0.1.1 | Verify Python installation | `python --version` | Python 3.10+ | [ ] |
| 0.1.2 | Verify Node.js installation | `node --version` | Node 18+ | [ ] |
| 0.1.3 | Verify npm installation | `npm --version` | npm 9+ | [ ] |
| 0.1.4 | Verify uv installation | `C:/ComfyUI/python_embeded/Scripts/uv.exe --version` | uv installed | [ ] |
| 0.1.5 | Verify npx availability | `npx --version` | npx available | [ ] |

#### Phase 0.2: Directory Structure Verification

| Task ID | Task | Path | Expected | Status |
|---------|------|------|----------|--------|
| 0.2.1 | Verify Ziggie root | `C:/Ziggie` | Exists | [ ] |
| 0.2.2 | Verify coordinator | `C:/Ziggie/coordinator/` | Contains main.py, client.py | [ ] |
| 0.2.3 | Verify ai-game-dev-system | `C:/ai-game-dev-system/` | Exists | [ ] |
| 0.2.4 | Verify mcp-servers hub | `C:/ai-game-dev-system/mcp-servers/hub/` | Contains mcp_hub_server.py | [ ] |
| 0.2.5 | Verify ComfyUI MCP | `C:/ai-game-dev-system/mcp-servers/comfyui-mcp/` | Contains server.py | [ ] |
| 0.2.6 | Verify Unreal MCP | `C:/ai-game-dev-system/mcp-servers/unreal-mcp/` | Contains Python/ | [ ] |
| 0.2.7 | Verify Godot MCP | `C:/ai-game-dev-system/mcp-servers/godot-mcp/` | Contains server/ | [ ] |
| 0.2.8 | Verify Unity MCP | `C:/ai-game-dev-system/mcp-servers/unity-mcp/` | Exists | [ ] |
| 0.2.9 | Verify MeowPing-RTS | `C:/meowping-rts/` | Exists | [ ] |
| 0.2.10 | Verify team-ziggie | `C:/team-ziggie/` | Exists | [ ] |

#### Phase 0.3: Current MCP Configuration Backup

| Task ID | Task | Command/Action | Status |
|---------|------|----------------|--------|
| 0.3.1 | Backup current .mcp.json | `copy C:\Ziggie\.mcp.json C:\Ziggie\.mcp.json.backup` | [ ] |
| 0.3.2 | Document current configuration | Read and record current state | [ ] |
| 0.3.3 | Verify backup integrity | `type C:\Ziggie\.mcp.json.backup` | [ ] |

#### Phase 0.4: Dependency Verification

| Task ID | Task | Command | Expected | Status |
|---------|------|---------|----------|--------|
| 0.4.1 | Check anthropic package | `pip show anthropic` | Installed | [ ] |
| 0.4.2 | Check mcp package | `pip show mcp` | May need install | [ ] |
| 0.4.3 | Check aiohttp package | `pip show aiohttp` | May need install | [ ] |
| 0.4.4 | Check websockets package | `pip show websockets` | May need install | [ ] |

### GATE 0: Assessment Complete
**Exit Criteria**:
- [ ] All environment tools verified (Python, Node, npm, uv)
- [ ] All directory structures confirmed
- [ ] .mcp.json backup created
- [ ] Dependency gaps identified

---

## STAGE 1: LAYER 1 ENHANCEMENT
### Duration: 15 minutes | Gate: Layer 1 Operational

> **Objective**: Maximize the capabilities of currently active MCPs before adding new ones.

#### Phase 1.1: Expand Filesystem MCP Access

**Current State**: Filesystem MCP only accesses `C:/Ziggie`
**Target State**: Access to 4 major project directories

| Task ID | Task | Action | Status |
|---------|------|--------|--------|
| 1.1.1 | Open .mcp.json for editing | Edit `C:\Ziggie\.mcp.json` | [ ] |
| 1.1.2 | Update filesystem args | Add additional paths | [ ] |
| 1.1.3 | Save configuration | Write file | [ ] |
| 1.1.4 | Restart Claude Code | Required for MCP reload | [ ] |
| 1.1.5 | Verify expanded access | Test read from new paths | [ ] |

**Configuration Change**:
```json
{
  "filesystem": {
    "command": "cmd",
    "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-filesystem",
      "C:/Ziggie",
      "C:/ai-game-dev-system",
      "C:/meowping-rts",
      "C:/team-ziggie"
    ]
  }
}
```

**Verification Tests**:
| Test ID | Test | Command | Expected | Status |
|---------|------|---------|----------|--------|
| 1.1.V1 | Read from ai-game-dev | `mcp__filesystem__read_file` on ai-game-dev path | Success | [ ] |
| 1.1.V2 | List ai-game-dev directory | `mcp__filesystem__list_directory` | Returns contents | [ ] |
| 1.1.V3 | Read from meowping-rts | `mcp__filesystem__read_file` on meowping path | Success | [ ] |

#### Phase 1.2: Populate Memory MCP - Core Entities

**Current State**: Empty knowledge graph
**Target State**: 50+ entities with relationships

**Entity Schema Design**:
```
Entity Types:
├── project          (Ziggie, MeowPing-RTS, ai-game-dev-system)
├── infrastructure   (MCP servers, VPS, databases)
├── agent            (Elite agents, L1-L3 hierarchy)
├── documentation    (Key files, locations)
├── service          (External services, APIs)
└── configuration    (Settings, credentials metadata)
```

| Task ID | Task | Entity Count | Status |
|---------|------|--------------|--------|
| 1.2.1 | Create Project entities | 5 entities | [ ] |
| 1.2.2 | Create Infrastructure entities | 15 entities | [ ] |
| 1.2.3 | Create Agent entities | 20 entities | [ ] |
| 1.2.4 | Create Documentation entities | 10 entities | [ ] |
| 1.2.5 | Create Service entities | 5 entities | [ ] |

**Project Entities (Phase 1.2.1)**:
```json
{
  "entities": [
    {
      "name": "Ziggie-Ecosystem",
      "entityType": "project",
      "observations": [
        "Root project at C:/Ziggie",
        "Contains coordinator, agent deployment, documentation",
        "Master status document: ZIGGIE-ECOSYSTEM-MASTER-STATUS-V2.md"
      ]
    },
    {
      "name": "MeowPing-RTS",
      "entityType": "project",
      "observations": [
        "Cat-themed RTS game project",
        "Location: C:/meowping-rts",
        "Uses assets from ai-game-dev-system"
      ]
    },
    {
      "name": "AI-Game-Dev-System",
      "entityType": "project",
      "observations": [
        "AI asset generation infrastructure",
        "Location: C:/ai-game-dev-system",
        "Contains MCP servers, ComfyUI workflows, pipelines"
      ]
    },
    {
      "name": "Team-Ziggie",
      "entityType": "project",
      "observations": [
        "Team documentation and resources",
        "Location: C:/team-ziggie"
      ]
    },
    {
      "name": "VPS-Production",
      "entityType": "project",
      "observations": [
        "Production VPS at 82.25.112.73",
        "6/7 containers running",
        "SSH access available"
      ]
    }
  ]
}
```

**Infrastructure Entities (Phase 1.2.2)**:
```json
{
  "entities": [
    {
      "name": "MCP-Hub",
      "entityType": "infrastructure",
      "observations": [
        "Central MCP gateway aggregating 7+ backends",
        "Location: C:/ai-game-dev-system/mcp-servers/hub/mcp_hub_server.py",
        "Provides 90+ tools via single connection",
        "Backends: Unity, Unreal, Godot, ComfyUI, SimStudio, LocalLLM, n8n"
      ]
    },
    {
      "name": "Unity-MCP",
      "entityType": "infrastructure",
      "observations": [
        "18 tools for Unity Editor control",
        "Port: 8080 (HTTP transport)",
        "Capabilities: scene, GameObject, asset management"
      ]
    },
    {
      "name": "Unreal-MCP",
      "entityType": "infrastructure",
      "observations": [
        "40+ tools for Unreal Engine control",
        "Port: 8081",
        "Location: C:/ai-game-dev-system/mcp-servers/unreal-mcp/Python/",
        "Capabilities: actors, blueprints, levels"
      ]
    },
    {
      "name": "Godot-MCP",
      "entityType": "infrastructure",
      "observations": [
        "4 modules for Godot Editor control",
        "Port: 6005",
        "Location: C:/ai-game-dev-system/mcp-servers/godot-mcp/server/",
        "Capabilities: scenes, nodes, scripts"
      ]
    },
    {
      "name": "ComfyUI-MCP",
      "entityType": "infrastructure",
      "observations": [
        "7 tools for AI image generation",
        "Port: 8188",
        "Location: C:/ai-game-dev-system/mcp-servers/comfyui-mcp/server.py",
        "Capabilities: SDXL, LoRA, sprite generation"
      ]
    },
    {
      "name": "SimStudio-MCP",
      "entityType": "infrastructure",
      "observations": [
        "10 tools for workflow orchestration",
        "Port: 3001",
        "Capabilities: AI workflow management, pipelines"
      ]
    },
    {
      "name": "LocalLLM-MCP",
      "entityType": "infrastructure",
      "observations": [
        "8 tools for local LLM integration",
        "Port: 1234",
        "Capabilities: Ollama, LM Studio prompts"
      ]
    },
    {
      "name": "N8N-MCP",
      "entityType": "infrastructure",
      "observations": [
        "400+ workflow integrations",
        "Port: 5678",
        "Capabilities: automation, webhooks, integrations"
      ]
    },
    {
      "name": "AWS-GPU-MCP",
      "entityType": "infrastructure",
      "observations": [
        "6 tools for cloud GPU control",
        "Capabilities: EC2 GPU instances, S3 storage"
      ]
    },
    {
      "name": "Agent-Coordinator",
      "entityType": "infrastructure",
      "observations": [
        "File-based agent deployment system",
        "Location: C:/Ziggie/coordinator/",
        "Key files: main.py, client.py, agent_spawner.py, claude_agent_runner.py",
        "Deploy command: python coordinator/client.py deploy"
      ]
    },
    {
      "name": "Chrome-DevTools-MCP",
      "entityType": "infrastructure",
      "observations": [
        "Active MCP for browser automation",
        "Version: 0.12.1",
        "6/6 tests passed",
        "Capabilities: screenshots, DOM manipulation, navigation"
      ]
    },
    {
      "name": "Filesystem-MCP",
      "entityType": "infrastructure",
      "observations": [
        "Active MCP for file operations",
        "Currently limited to C:/Ziggie",
        "Target: Expand to 4 directories"
      ]
    },
    {
      "name": "Memory-MCP",
      "entityType": "infrastructure",
      "observations": [
        "Active MCP for knowledge persistence",
        "Currently empty",
        "Target: 50+ entities with relationships"
      ]
    },
    {
      "name": "ComfyUI-Local",
      "entityType": "infrastructure",
      "observations": [
        "Local ComfyUI installation",
        "Location: C:/ComfyUI",
        "Python embedded at: C:/ComfyUI/python_embeded/"
      ]
    },
    {
      "name": "Anthropic-API",
      "entityType": "infrastructure",
      "observations": [
        "Claude API for agent execution",
        "Used by claude_agent_runner.py",
        "Models: haiku, sonnet, opus"
      ]
    }
  ]
}
```

**Agent Entities (Phase 1.2.3)**:
```json
{
  "entities": [
    {
      "name": "Elite-AI-Team",
      "entityType": "agent",
      "observations": [
        "18 Elite AI Agents across 4 teams",
        "Art Team: ARTEMIS, LEONIDAS, GAIA, VULCAN",
        "Design Team: TERRA, PROMETHEUS, IRIS, MYTHOS",
        "Technical Team: HEPHAESTUS, DAEDALUS, ARGUS",
        "Production Team: MAXIMUS, FORGE, ATLAS"
      ]
    },
    {
      "name": "Agent-Hierarchy",
      "entityType": "agent",
      "observations": [
        "12x12x12 hierarchy = 1,884 total agents",
        "L1: 12 Strategic Directors",
        "L2: 144 Domain Experts (12 per L1)",
        "L3: 1,728 Specialist Workers (12 per L2)"
      ]
    },
    {
      "name": "L1-Art-Director",
      "entityType": "agent",
      "observations": [
        "ID: L1.1",
        "Role: Strategic Art Direction",
        "Reports: 12 L2 agents, 144 L3 agents"
      ]
    }
  ]
}
```

#### Phase 1.3: Create Memory Relations

| Task ID | Task | Relation Type | Status |
|---------|------|---------------|--------|
| 1.3.1 | Link projects to infrastructure | USES, DEPENDS_ON | [ ] |
| 1.3.2 | Link agents to projects | WORKS_ON, MANAGES | [ ] |
| 1.3.3 | Link MCPs to hub | AGGREGATED_BY | [ ] |
| 1.3.4 | Link services to infrastructure | PROVIDES, CONNECTS_TO | [ ] |

**Relations to Create**:
```json
{
  "relations": [
    {"from": "Ziggie-Ecosystem", "to": "Agent-Coordinator", "relationType": "USES"},
    {"from": "Ziggie-Ecosystem", "to": "MCP-Hub", "relationType": "CAN_INTEGRATE"},
    {"from": "MeowPing-RTS", "to": "AI-Game-Dev-System", "relationType": "USES_ASSETS_FROM"},
    {"from": "MeowPing-RTS", "to": "ComfyUI-MCP", "relationType": "GENERATES_WITH"},
    {"from": "MCP-Hub", "to": "Unity-MCP", "relationType": "AGGREGATES"},
    {"from": "MCP-Hub", "to": "Unreal-MCP", "relationType": "AGGREGATES"},
    {"from": "MCP-Hub", "to": "Godot-MCP", "relationType": "AGGREGATES"},
    {"from": "MCP-Hub", "to": "ComfyUI-MCP", "relationType": "AGGREGATES"},
    {"from": "MCP-Hub", "to": "SimStudio-MCP", "relationType": "AGGREGATES"},
    {"from": "MCP-Hub", "to": "LocalLLM-MCP", "relationType": "AGGREGATES"},
    {"from": "MCP-Hub", "to": "N8N-MCP", "relationType": "AGGREGATES"},
    {"from": "Agent-Coordinator", "to": "Anthropic-API", "relationType": "CALLS"},
    {"from": "Elite-AI-Team", "to": "MeowPing-RTS", "relationType": "WORKS_ON"},
    {"from": "Elite-AI-Team", "to": "Agent-Hierarchy", "relationType": "PART_OF"}
  ]
}
```

#### Phase 1.4: Verify Layer 1 Enhancement

| Test ID | Test | Method | Expected | Status |
|---------|------|--------|----------|--------|
| 1.4.V1 | Filesystem expanded | Read from C:/ai-game-dev-system | Success | [ ] |
| 1.4.V2 | Memory populated | `mcp__memory__read_graph` | 50+ entities | [ ] |
| 1.4.V3 | Relations created | `mcp__memory__search_nodes` | Find relations | [ ] |

### GATE 1: Layer 1 Operational
**Exit Criteria**:
- [ ] Filesystem MCP accesses 4 directories
- [ ] Memory MCP contains 50+ entities
- [ ] Memory MCP contains 15+ relations
- [ ] All verification tests pass

---

## STAGE 2: MCP HUB INTEGRATION
### Duration: 30 minutes | Gate: Hub Operational

> **Objective**: Add MCP Hub for single-point access to all game engine backends.

#### Phase 2.1: Hub Prerequisites

| Task ID | Task | Command | Expected | Status |
|---------|------|---------|----------|--------|
| 2.1.1 | Install mcp package | `pip install mcp` | Success | [ ] |
| 2.1.2 | Install aiohttp package | `pip install aiohttp` | Success | [ ] |
| 2.1.3 | Verify hub server exists | Check file at path | Exists | [ ] |
| 2.1.4 | Review hub configuration | Read mcp_hub_server.py | Understand backends | [ ] |

#### Phase 2.2: Add Hub to .mcp.json

| Task ID | Task | Action | Status |
|---------|------|--------|--------|
| 2.2.1 | Open .mcp.json | Edit file | [ ] |
| 2.2.2 | Add hub server configuration | Insert JSON block | [ ] |
| 2.2.3 | Save and validate JSON | Write file | [ ] |

**Configuration to Add**:
```json
{
  "mcpServers": {
    "hub": {
      "command": "C:/ComfyUI/python_embeded/Scripts/uv.exe",
      "args": [
        "run",
        "--with", "mcp",
        "--with", "aiohttp",
        "python",
        "C:/ai-game-dev-system/mcp-servers/hub/mcp_hub_server.py"
      ]
    }
  }
}
```

#### Phase 2.3: Start Backend Services

> **NOTE**: Hub requires backend services to be running for full functionality.

| Task ID | Task | Command | Port | Status |
|---------|------|---------|------|--------|
| 2.3.1 | Start ComfyUI (if needed) | ComfyUI launcher | 8188 | [ ] |
| 2.3.2 | Start Unity MCP (if Unity open) | Via Unity Editor | 8080 | [ ] |
| 2.3.3 | Start Godot MCP (if Godot open) | Via Godot plugin | 6005 | [ ] |
| 2.3.4 | Start Local LLM (if Ollama installed) | `ollama serve` | 1234 | [ ] |

**Backend Availability Matrix**:
| Backend | Required For | Auto-Start | Manual Start |
|---------|--------------|------------|--------------|
| ComfyUI | Asset generation | No | Launch ComfyUI app |
| Unity | Unity Editor control | No | Open Unity with MCP plugin |
| Unreal | Unreal Editor control | No | Open Unreal with MCP plugin |
| Godot | Godot Editor control | No | Open Godot with MCP plugin |
| Local LLM | Free AI text | No | `ollama serve` |
| n8n | Workflow automation | No | `n8n start` |

#### Phase 2.4: Restart and Test Hub

| Task ID | Task | Action | Status |
|---------|------|--------|--------|
| 2.4.1 | Restart Claude Code | Reload MCPs | [ ] |
| 2.4.2 | Test hub_status tool | Call via MCP | [ ] |
| 2.4.3 | Test hub_list_backends | Call via MCP | [ ] |
| 2.4.4 | Document available backends | Record which are online | [ ] |

**Verification Tests**:
| Test ID | Test | Expected | Status |
|---------|------|----------|--------|
| 2.4.V1 | hub_status returns | JSON with backend status | [ ] |
| 2.4.V2 | At least 1 backend online | ComfyUI or LocalLLM | [ ] |
| 2.4.V3 | Hub tools accessible | Can call hub_route_call | [ ] |

### GATE 2: Hub Operational
**Exit Criteria**:
- [ ] MCP Hub added to .mcp.json
- [ ] Claude Code restarted and Hub connected
- [ ] hub_status tool functional
- [ ] At least one backend service accessible

---

## STAGE 3: GAME ENGINE MCPS
### Duration: 45 minutes | Gate: Game Engines Accessible

> **Objective**: Enable control of Unity, Unreal, and Godot via MCP.

#### Phase 3.1: Unity MCP Integration

**Prerequisites**:
- Unity Editor installed
- Unity MCP plugin installed in project

| Task ID | Task | Action | Status |
|---------|------|--------|--------|
| 3.1.1 | Verify Unity MCP plugin | Check Unity project | [ ] |
| 3.1.2 | Start Unity Editor | Open project with MCP | [ ] |
| 3.1.3 | Verify port 8080 active | `netstat -an | findstr 8080` | [ ] |
| 3.1.4 | Test via Hub | `hub_route_call` to unity | [ ] |

**Alternative: Direct MCP Configuration**:
```json
{
  "mcpServers": {
    "unity": {
      "url": "http://localhost:8080/mcp",
      "description": "Unity MCP Server"
    }
  }
}
```

**Unity MCP Tools (18 total)**:
| Category | Tools | Description |
|----------|-------|-------------|
| Scene | create_scene, load_scene, save_scene | Scene management |
| GameObject | create_gameobject, modify_gameobject, delete_gameobject | Object manipulation |
| Assets | import_asset, create_prefab, instantiate_prefab | Asset pipeline |
| Components | add_component, modify_component | Component system |
| Materials | create_material, assign_material | Material management |

#### Phase 3.2: Unreal MCP Integration

**Prerequisites**:
- Unreal Engine installed
- Python with MCP package

| Task ID | Task | Action | Status |
|---------|------|--------|--------|
| 3.2.1 | Verify Unreal MCP files | Check `C:/ai-game-dev-system/mcp-servers/unreal-mcp/Python/` | [ ] |
| 3.2.2 | Start Unreal Editor | Open project | [ ] |
| 3.2.3 | Start Unreal MCP server | `uv run unreal_mcp_server.py` | [ ] |
| 3.2.4 | Verify port 8081 active | `netstat -an | findstr 8081` | [ ] |
| 3.2.5 | Test via Hub | `hub_route_call` to unreal | [ ] |

**Direct MCP Configuration**:
```json
{
  "mcpServers": {
    "unreal": {
      "command": "C:/ComfyUI/python_embeded/Scripts/uv.exe",
      "args": [
        "--directory",
        "C:/ai-game-dev-system/mcp-servers/unreal-mcp/Python",
        "run",
        "unreal_mcp_server.py"
      ]
    }
  }
}
```

**Unreal MCP Tools (40+ total)**:
| Category | Tools | Description |
|----------|-------|-------------|
| Actors | spawn_actor, modify_actor, delete_actor | Actor management |
| Blueprints | create_blueprint, compile_blueprint | Blueprint system |
| Levels | create_level, load_level, save_level | Level management |
| Assets | import_asset, create_material | Asset pipeline |

#### Phase 3.3: Godot MCP Integration

**Prerequisites**:
- Godot 4.x installed
- Node.js with MCP package

| Task ID | Task | Action | Status |
|---------|------|--------|--------|
| 3.3.1 | Verify Godot MCP files | Check `C:/ai-game-dev-system/mcp-servers/godot-mcp/server/` | [ ] |
| 3.3.2 | Build Godot MCP | `npm install && npm run build` | [ ] |
| 3.3.3 | Start Godot Editor | Open project with plugin | [ ] |
| 3.3.4 | Verify port 6005 active | `netstat -an | findstr 6005` | [ ] |
| 3.3.5 | Test via Hub | `hub_route_call` to godot | [ ] |

**Direct MCP Configuration**:
```json
{
  "mcpServers": {
    "godot": {
      "command": "node",
      "args": [
        "--experimental-modules",
        "C:/ai-game-dev-system/mcp-servers/godot-mcp/server/dist/index.js"
      ],
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

**Godot MCP Tools (4 modules)**:
| Module | Capabilities |
|--------|--------------|
| Scenes | Create, load, save scenes |
| Nodes | Add, modify, remove nodes |
| Scripts | Create, edit GDScript files |
| Resources | Manage resources and assets |

### GATE 3: Game Engines Accessible
**Exit Criteria**:
- [ ] At least one game engine MCP operational
- [ ] Can communicate with engine via Hub or direct MCP
- [ ] Basic tool calls succeed (list scenes, get info)

---

## STAGE 4: AI ASSET GENERATION
### Duration: 30 minutes | Gate: Asset Pipeline Operational

> **Objective**: Enable AI asset generation via ComfyUI MCP.

#### Phase 4.1: ComfyUI MCP Setup

| Task ID | Task | Action | Status |
|---------|------|--------|--------|
| 4.1.1 | Verify ComfyUI installation | Check `C:/ComfyUI` exists | [ ] |
| 4.1.2 | Start ComfyUI | Launch application | [ ] |
| 4.1.3 | Verify port 8188 active | `netstat -an | findstr 8188` | [ ] |
| 4.1.4 | Verify MCP server file | Check `C:/ai-game-dev-system/mcp-servers/comfyui-mcp/server.py` | [ ] |

#### Phase 4.2: Add ComfyUI MCP to Configuration

**Configuration**:
```json
{
  "mcpServers": {
    "comfyui": {
      "command": "C:/ComfyUI/python_embeded/Scripts/uv.exe",
      "args": [
        "run",
        "--with", "mcp",
        "--with", "websockets",
        "python",
        "C:/ai-game-dev-system/mcp-servers/comfyui-mcp/server.py"
      ],
      "env": {
        "COMFYUI_HOST": "127.0.0.1",
        "COMFYUI_PORT": "8188",
        "COMFYUI_DIR": "C:/ComfyUI/ComfyUI",
        "OUTPUT_DIR": "C:/ai-game-dev-system/assets/ai-generated"
      }
    }
  }
}
```

| Task ID | Task | Action | Status |
|---------|------|--------|--------|
| 4.2.1 | Add ComfyUI to .mcp.json | Insert configuration | [ ] |
| 4.2.2 | Restart Claude Code | Reload MCPs | [ ] |
| 4.2.3 | Test connection | Call ComfyUI tool | [ ] |

#### Phase 4.3: Test Asset Generation

**ComfyUI MCP Tools (7 total)**:
| Tool | Description | Test |
|------|-------------|------|
| list_workflows | List available workflows | [ ] |
| get_workflow | Get workflow details | [ ] |
| execute_workflow | Run generation | [ ] |
| get_status | Check generation status | [ ] |
| list_models | List available models | [ ] |
| list_loras | List LoRA models | [ ] |
| generate_image | Direct image generation | [ ] |

| Test ID | Test | Expected | Status |
|---------|------|----------|--------|
| 4.3.V1 | List workflows | Returns workflow list | [ ] |
| 4.3.V2 | List models | Returns model list | [ ] |
| 4.3.V3 | Generate test image | Creates image file | [ ] |

### GATE 4: Asset Pipeline Operational
**Exit Criteria**:
- [ ] ComfyUI running and accessible
- [ ] ComfyUI MCP connected
- [ ] Can list workflows and models
- [ ] Can generate at least one test image

---

## STAGE 5: AGENT ORCHESTRATION
### Duration: 45 minutes | Gate: Agent Deployment Operational

> **Objective**: Enable full agent deployment and management.

#### Phase 5.1: Coordinator Prerequisites

| Task ID | Task | Command | Status |
|---------|------|---------|--------|
| 5.1.1 | Verify coordinator files | Check `C:/Ziggie/coordinator/` | [ ] |
| 5.1.2 | Verify ANTHROPIC_API_KEY | Check environment variable | [ ] |
| 5.1.3 | Install anthropic package | `pip install anthropic` | [ ] |
| 5.1.4 | Create deployment directories | mkdir requests, responses | [ ] |

**Required Coordinator Files**:
| File | Purpose | Status |
|------|---------|--------|
| main.py | Entry point, starts watcher | [ ] |
| client.py | CLI deployment client | [ ] |
| agent_spawner.py | Process management | [ ] |
| claude_agent_runner.py | Anthropic SDK execution | [ ] |
| watcher.py | File monitoring | [ ] |

#### Phase 5.2: Start Coordinator Service

| Task ID | Task | Command | Status |
|---------|------|---------|--------|
| 5.2.1 | Start coordinator | `python -m coordinator.main` | [ ] |
| 5.2.2 | Verify watcher running | Check console output | [ ] |
| 5.2.3 | Check log file created | Check `agent-deployment/logs/` | [ ] |

**Coordinator Start Command**:
```bash
cd C:\Ziggie
python -m coordinator.main
```

**Expected Output**:
```
============================================================
ZIGGIE Agent Deployment Coordinator
File-Based MVP v1.0
============================================================
Deployment Directory: C:\Ziggie\agent-deployment
Log Directory: C:\Ziggie\agent-deployment\logs
Starting coordinator service...
```

#### Phase 5.3: Test Agent Deployment

| Task ID | Task | Command | Status |
|---------|------|---------|--------|
| 5.3.1 | Deploy test agent | `python coordinator/client.py deploy --agent test --task "Hello"` | [ ] |
| 5.3.2 | Check request created | Check requests/ directory | [ ] |
| 5.3.3 | Wait for processing | Monitor coordinator logs | [ ] |
| 5.3.4 | Check response | Check responses/ directory | [ ] |
| 5.3.5 | Verify success | Read response.txt | [ ] |

**Test Deployment Command**:
```bash
python coordinator/client.py deploy --agent test --task "Say hello and confirm you are working"
```

**Expected Flow**:
```
1. Request JSON written to requests/
2. Watcher detects new file
3. agent_spawner.py creates subprocess
4. claude_agent_runner.py calls Anthropic API
5. Response written to responses/
```

#### Phase 5.4: Test L1 Agent Deployment

| Task ID | Task | Command | Status |
|---------|------|---------|--------|
| 5.4.1 | Deploy L1.1 Art Director | `python coordinator/client.py deploy --agent L1.1 --task "audit"` | [ ] |
| 5.4.2 | Check status | `python coordinator/client.py status --agent L1.1` | [ ] |
| 5.4.3 | Read response | Check agent working directory | [ ] |

### GATE 5: Agent Deployment Operational
**Exit Criteria**:
- [ ] Coordinator service starts successfully
- [ ] Test agent deployment completes
- [ ] L1 agent deployment completes
- [ ] Response files generated correctly

---

## STAGE 6: KNOWLEDGE GRAPH COMPLETION
### Duration: 30 minutes | Gate: Knowledge Graph Complete

> **Objective**: Complete the memory MCP population with full ecosystem knowledge.

#### Phase 6.1: Agent Hierarchy Entities

| Task ID | Task | Count | Status |
|---------|------|-------|--------|
| 6.1.1 | Create L1 Agent entities | 12 entities | [ ] |
| 6.1.2 | Create Elite Team entities | 18 entities | [ ] |
| 6.1.3 | Create skill entities | 10 entities | [ ] |

**L1 Agent Entities**:
```json
{
  "entities": [
    {"name": "L1.1-Art-Director", "entityType": "agent", "observations": ["Strategic art direction", "12 L2 reports", "Skills: elite-art-team"]},
    {"name": "L1.2-Design-Director", "entityType": "agent", "observations": ["Game design leadership", "12 L2 reports", "Skills: elite-design-team"]},
    {"name": "L1.3-Technical-Director", "entityType": "agent", "observations": ["Technical architecture", "12 L2 reports", "Skills: elite-technical-team"]},
    {"name": "L1.4-Production-Director", "entityType": "agent", "observations": ["Production management", "12 L2 reports", "Skills: elite-production-team"]}
  ]
}
```

#### Phase 6.2: Service & API Entities

| Task ID | Task | Count | Status |
|---------|------|-------|--------|
| 6.2.1 | Create API key entities (names only) | 5 entities | [ ] |
| 6.2.2 | Create cloud service entities | 5 entities | [ ] |
| 6.2.3 | Create VPS service entities | 3 entities | [ ] |

#### Phase 6.3: Documentation Entities

| Task ID | Task | Count | Status |
|---------|------|-------|--------|
| 6.3.1 | Create key file entities | 10 entities | [ ] |
| 6.3.2 | Create knowledge base entities | 5 entities | [ ] |

**Key Documentation Entities**:
```json
{
  "entities": [
    {"name": "ZIGGIE-MASTER-STATUS-V2", "entityType": "documentation", "observations": ["Master ecosystem status", "Location: C:/Ziggie/ZIGGIE-ECOSYSTEM-MASTER-STATUS-V2.md", "Contains 10 sections"]},
    {"name": "INTEGRATION-PLAN", "entityType": "documentation", "observations": ["Integration roadmap", "Location: C:/Ziggie/CLAUDE-CODE-INTEGRATION-PLAN.md", "7 stages, 28 phases"]},
    {"name": "MCP-CONFIG", "entityType": "documentation", "observations": ["MCP configuration", "Location: C:/Ziggie/.mcp.json", "Active MCP servers"]}
  ]
}
```

#### Phase 6.4: Complete Relations

| Task ID | Task | Relations | Status |
|---------|------|-----------|--------|
| 6.4.1 | Agent hierarchy relations | 20+ relations | [ ] |
| 6.4.2 | Service dependency relations | 10+ relations | [ ] |
| 6.4.3 | Documentation reference relations | 10+ relations | [ ] |

### GATE 6: Knowledge Graph Complete
**Exit Criteria**:
- [ ] 75+ entities in memory graph
- [ ] 50+ relations created
- [ ] All major components represented
- [ ] Search returns relevant results

---

## STAGE 7: PRODUCTION READINESS
### Duration: 30 minutes | Gate: Production Ready

> **Objective**: Verify full integration and document capabilities.

#### Phase 7.1: Integration Verification

| Test ID | Test | Component | Expected | Status |
|---------|------|-----------|----------|--------|
| 7.1.1 | Filesystem MCP | 4 directories | All accessible | [ ] |
| 7.1.2 | Memory MCP | Knowledge graph | 75+ entities | [ ] |
| 7.1.3 | Chrome DevTools MCP | Browser control | Screenshots work | [ ] |
| 7.1.4 | Hub MCP | Backend aggregation | Status returns | [ ] |
| 7.1.5 | ComfyUI MCP | Asset generation | Can generate | [ ] |
| 7.1.6 | Agent Coordinator | Deployment | Can deploy agents | [ ] |

#### Phase 7.2: Capability Documentation

| Task ID | Task | Output | Status |
|---------|------|--------|--------|
| 7.2.1 | Document all MCP tools | Tool inventory | [ ] |
| 7.2.2 | Document Bash commands | Command reference | [ ] |
| 7.2.3 | Create quick reference | Cheat sheet | [ ] |

#### Phase 7.3: Security Review

| Task ID | Task | Check | Status |
|---------|------|-------|--------|
| 7.3.1 | API keys not in memory | Search memory for keys | [ ] |
| 7.3.2 | No credentials in .mcp.json | Review configuration | [ ] |
| 7.3.3 | Backup files secured | Check .backup files | [ ] |

#### Phase 7.4: Final Status Update

| Task ID | Task | Action | Status |
|---------|------|--------|--------|
| 7.4.1 | Update MASTER-STATUS-V2 | Add completion notes | [ ] |
| 7.4.2 | Update memory graph | Add integration status | [ ] |
| 7.4.3 | Create session summary | Document achievements | [ ] |

### GATE 7: Production Ready
**Exit Criteria**:
- [ ] All 6 previous gates passed
- [ ] Full integration verified
- [ ] Capabilities documented
- [ ] Security review passed
- [ ] Status documents updated

---

## QUICK REFERENCE: FINAL .mcp.json

After full integration, your `.mcp.json` should look like:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "chrome-devtools-mcp@latest"],
      "env": {
        "SystemRoot": "C:\\Windows",
        "PROGRAMFILES": "C:\\Program Files"
      }
    },
    "filesystem": {
      "command": "cmd",
      "args": [
        "/c", "npx", "-y", "@modelcontextprotocol/server-filesystem",
        "C:/Ziggie",
        "C:/ai-game-dev-system",
        "C:/meowping-rts",
        "C:/team-ziggie"
      ],
      "env": {}
    },
    "memory": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-memory"],
      "env": {}
    },
    "hub": {
      "command": "C:/ComfyUI/python_embeded/Scripts/uv.exe",
      "args": [
        "run",
        "--with", "mcp",
        "--with", "aiohttp",
        "python",
        "C:/ai-game-dev-system/mcp-servers/hub/mcp_hub_server.py"
      ]
    },
    "comfyui": {
      "command": "C:/ComfyUI/python_embeded/Scripts/uv.exe",
      "args": [
        "run",
        "--with", "mcp",
        "--with", "websockets",
        "python",
        "C:/ai-game-dev-system/mcp-servers/comfyui-mcp/server.py"
      ],
      "env": {
        "COMFYUI_HOST": "127.0.0.1",
        "COMFYUI_PORT": "8188",
        "COMFYUI_DIR": "C:/ComfyUI/ComfyUI",
        "OUTPUT_DIR": "C:/ai-game-dev-system/assets/ai-generated"
      }
    }
  }
}
```

---

## QUICK REFERENCE: BASH COMMANDS

### Agent Deployment
```bash
# Start coordinator
python -m coordinator.main

# Deploy agent
python coordinator/client.py deploy --agent L1.1 --task "your task"

# Check status
python coordinator/client.py status --agent L1.1
```

### MCP Server Manual Start
```bash
# Start ComfyUI MCP
C:/ComfyUI/python_embeded/Scripts/uv.exe run --with mcp --with websockets python C:/ai-game-dev-system/mcp-servers/comfyui-mcp/server.py

# Start Hub MCP
C:/ComfyUI/python_embeded/Scripts/uv.exe run --with mcp --with aiohttp python C:/ai-game-dev-system/mcp-servers/hub/mcp_hub_server.py
```

### Port Verification
```bash
# Check ComfyUI
netstat -an | findstr 8188

# Check Unity MCP
netstat -an | findstr 8080

# Check Godot MCP
netstat -an | findstr 6005
```

---

## INTEGRATION SUMMARY

| Stage | Duration | Key Outcome | Gate |
|-------|----------|-------------|------|
| 0 | 30 min | Assessment complete | Prerequisites verified |
| 1 | 15 min | Layer 1 enhanced | Filesystem + Memory operational |
| 2 | 30 min | Hub integrated | 90+ tools accessible |
| 3 | 45 min | Game engines connected | Unity/Unreal/Godot control |
| 4 | 30 min | Asset pipeline ready | ComfyUI generation works |
| 5 | 45 min | Agents deployable | Coordinator operational |
| 6 | 30 min | Knowledge complete | 75+ entities, 50+ relations |
| 7 | 30 min | Production ready | Full verification passed |

**Total Estimated Duration**: 4 hours 15 minutes

---

## DOCUMENT METADATA

| Field | Value |
|-------|-------|
| Document ID | ZIGGIE-INTEGRATION-PLAN-V1.0 |
| Created | 2025-12-24 |
| Author | Claude Opus 4.5 |
| Methodology | 7-Stage Gated Integration |
| Total Stages | 7 |
| Total Phases | 28 |
| Total Tasks | 100+ |
| Estimated Duration | 4 hours 15 minutes |

---

# APPENDIX A: DEEP DETAIL - PRE-FLIGHT CHECKLISTS

## A.1 Master Pre-Flight Checklist (Run Before Starting)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                     ZIGGIE INTEGRATION PRE-FLIGHT CHECK                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Run this checklist BEFORE starting any integration stage                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

SYSTEM REQUIREMENTS
[ ] Windows 10/11 with PowerShell 7+
[ ] 16GB+ RAM available
[ ] 50GB+ disk space free
[ ] Internet connection active
[ ] Administrator privileges available (if needed)

ENVIRONMENT TOOLS
[ ] Python 3.10+ installed and in PATH
[ ] Node.js 18+ installed and in PATH
[ ] npm 9+ installed and in PATH
[ ] Git installed and in PATH
[ ] uv installed at C:/ComfyUI/python_embeded/Scripts/uv.exe

ANTHROPIC ACCESS
[ ] ANTHROPIC_API_KEY environment variable set
[ ] API key has sufficient credits
[ ] API key not expired

FILESYSTEM STRUCTURE
[ ] C:/Ziggie exists
[ ] C:/ai-game-dev-system exists
[ ] C:/ComfyUI exists
[ ] C:/meowping-rts exists (optional)
[ ] C:/team-ziggie exists (optional)

BACKUP STATUS
[ ] .mcp.json backed up to .mcp.json.backup
[ ] Important configs documented
[ ] Recovery plan understood

NETWORK PORTS (Check none are in use)
[ ] Port 8080 (Unity MCP)
[ ] Port 8081 (Unreal MCP)
[ ] Port 8188 (ComfyUI)
[ ] Port 6005 (Godot MCP)
[ ] Port 1234 (LocalLLM)
[ ] Port 3001 (Sim Studio)
[ ] Port 5678 (n8n)
```

## A.2 Stage-Specific Pre-Flight Checklists

### Stage 0: Assessment Pre-Flight
```
[ ] All system requirements from A.1 verified
[ ] Previous Claude Code session closed
[ ] Terminal/PowerShell open in C:/Ziggie
[ ] Read access to all project directories confirmed
```

### Stage 1: Layer 1 Enhancement Pre-Flight
```
[ ] Stage 0 GATE PASSED
[ ] .mcp.json is valid JSON (parse test passed)
[ ] No syntax errors in current config
[ ] Memory MCP accessible (test with read_graph)
[ ] Filesystem MCP accessible (test with list_directory)
```

### Stage 2: Hub Integration Pre-Flight
```
[ ] Stage 1 GATE PASSED
[ ] MCP Hub server file exists and readable
[ ] mcp package installed (pip show mcp)
[ ] aiohttp package installed (pip show aiohttp)
[ ] At least one backend service startable
```

### Stage 3: Game Engines Pre-Flight
```
[ ] Stage 2 GATE PASSED
[ ] At least one game engine installed (Unity/Unreal/Godot)
[ ] Engine MCP plugin/addon installed
[ ] Engine project exists to test with
[ ] Backend port available (8080/8081/6005)
```

### Stage 4: Asset Generation Pre-Flight
```
[ ] Stage 3 GATE PASSED (or skipped with reason)
[ ] ComfyUI installed at C:/ComfyUI
[ ] ComfyUI can start successfully
[ ] At least one SDXL model available
[ ] websockets package installed
```

### Stage 5: Agent Orchestration Pre-Flight
```
[ ] Stage 4 GATE PASSED (or skipped with reason)
[ ] Coordinator files all present
[ ] ANTHROPIC_API_KEY valid and tested
[ ] anthropic package installed
[ ] Write access to coordinator directories
```

### Stage 6: Knowledge Graph Pre-Flight
```
[ ] Stage 5 GATE PASSED
[ ] Memory MCP operational
[ ] Entity schema understood
[ ] Relation types defined
[ ] No duplicate entity names planned
```

### Stage 7: Production Pre-Flight
```
[ ] ALL previous gates passed
[ ] All verification tests documented
[ ] Security review checklist ready
[ ] Status update template prepared
```

---

# APPENDIX B: ROLLBACK PROCEDURES

## B.1 Master Rollback Command

**Emergency Full Rollback** (restores to pre-integration state):
```powershell
# EMERGENCY ROLLBACK - Run from C:/Ziggie
Copy-Item -Path ".mcp.json.backup" -Destination ".mcp.json" -Force
Write-Host "Rollback complete. Restart Claude Code to apply."
```

## B.2 Stage-Specific Rollback Procedures

### Stage 1 Rollback: Filesystem/Memory Enhancement
```powershell
# Rollback filesystem expansion
# 1. Restore original .mcp.json
Copy-Item -Path "C:\Ziggie\.mcp.json.backup" -Destination "C:\Ziggie\.mcp.json" -Force

# 2. Clear memory graph (if needed)
# Use mcp__memory__delete_entities with all entity names

# 3. Restart Claude Code
Write-Host "Stage 1 Rollback complete. Restart Claude Code."
```

**When to rollback Stage 1**:
- Filesystem MCP fails to start after path expansion
- Memory MCP becomes unresponsive
- Claude Code crashes on startup

### Stage 2 Rollback: Hub Integration
```powershell
# Rollback Hub integration
# 1. Remove hub from .mcp.json
$config = Get-Content "C:\Ziggie\.mcp.json" | ConvertFrom-Json
$config.mcpServers.PSObject.Properties.Remove("hub")
$config | ConvertTo-Json -Depth 10 | Set-Content "C:\Ziggie\.mcp.json"

# 2. Restart Claude Code
Write-Host "Stage 2 Rollback complete. Hub removed. Restart Claude Code."
```

**When to rollback Stage 2**:
- Hub server fails to start
- Hub causes timeouts
- Hub conflicts with other MCPs

### Stage 3 Rollback: Game Engine MCPs
```powershell
# Rollback specific game engine MCP
# Example: Remove Unity MCP
$config = Get-Content "C:\Ziggie\.mcp.json" | ConvertFrom-Json
$config.mcpServers.PSObject.Properties.Remove("unity")  # or "unreal", "godot"
$config | ConvertTo-Json -Depth 10 | Set-Content "C:\Ziggie\.mcp.json"

Write-Host "Game engine MCP removed. Restart Claude Code."
```

**When to rollback Stage 3**:
- Engine MCP causes Claude Code crashes
- Port conflicts with other services
- Engine plugin not compatible

### Stage 4 Rollback: ComfyUI MCP
```powershell
# Rollback ComfyUI MCP
$config = Get-Content "C:\Ziggie\.mcp.json" | ConvertFrom-Json
$config.mcpServers.PSObject.Properties.Remove("comfyui")
$config | ConvertTo-Json -Depth 10 | Set-Content "C:\Ziggie\.mcp.json"

Write-Host "ComfyUI MCP removed. Restart Claude Code."
```

**When to rollback Stage 4**:
- ComfyUI MCP connection fails
- websockets issues
- ComfyUI not running

### Stage 5 Rollback: Coordinator
```powershell
# Stop coordinator if running
Stop-Process -Name "python" -ErrorAction SilentlyContinue

# Clean up deployment directories
Remove-Item -Path "C:\Ziggie\agent-deployment\requests\*" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "C:\Ziggie\agent-deployment\responses\*" -Force -ErrorAction SilentlyContinue

Write-Host "Coordinator stopped and cleaned. Can restart fresh."
```

**When to rollback Stage 5**:
- Coordinator crashes repeatedly
- Agent deployments hang
- API key issues

---

# APPENDIX C: TROUBLESHOOTING GUIDE

## C.1 Common Issues by Stage

### Stage 0: Assessment Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| Python not found | `'python' is not recognized` | Add Python to PATH or use full path |
| Node not found | `'node' is not recognized` | Install Node.js from nodejs.org |
| uv not found | `uv.exe not found` | Check ComfyUI installation path |
| Permission denied | `Access denied` errors | Run PowerShell as Administrator |

### Stage 1: Layer 1 Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| JSON parse error | `.mcp.json invalid JSON` | Use JSON validator, check commas/brackets |
| Filesystem MCP won't start | `npx error` or timeout | Check npm/npx installation, try `npm cache clean --force` |
| Memory MCP empty | `read_graph returns {}` | Normal - population comes later |
| Path not accessible | `ENOENT` error | Verify path exists, check slashes (use /) |

**JSON Validation Command**:
```powershell
# Validate .mcp.json syntax
Get-Content "C:\Ziggie\.mcp.json" | ConvertFrom-Json
# If this returns object, JSON is valid
# If error, shows line number of issue
```

### Stage 2: Hub Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| Hub won't start | `ModuleNotFoundError: mcp` | `pip install mcp aiohttp` |
| Hub timeout | `Connection timed out` | Check if any backend is running |
| No backends | `hub_status shows all offline` | Start at least one backend service |
| Port conflict | `Address already in use` | Find and kill conflicting process |

**Debug Hub Startup**:
```powershell
# Test Hub server directly
cd C:\ai-game-dev-system\mcp-servers\hub
C:\ComfyUI\python_embeded\Scripts\uv.exe run --with mcp --with aiohttp python mcp_hub_server.py

# Watch for error messages
# Ctrl+C to stop after testing
```

### Stage 3: Game Engine Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| Unity MCP not responding | `port 8080 timeout` | Ensure Unity is open with MCP plugin active |
| Unreal MCP crash | `Python error` | Check Unreal MCP Python dependencies |
| Godot MCP not found | `dist/index.js missing` | Run `npm install && npm run build` in godot-mcp/server/ |
| Port already in use | `EADDRINUSE` | `netstat -an \| findstr :PORT` then kill process |

**Port Check Command**:
```powershell
# Find what's using a port (example: 8080)
netstat -ano | findstr :8080
# Returns PID in last column

# Kill process by PID
taskkill /PID <PID> /F
```

### Stage 4: ComfyUI Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| ComfyUI not running | `port 8188 not open` | Start ComfyUI application first |
| websockets error | `ModuleNotFoundError: websockets` | `pip install websockets` |
| No models found | `list_models returns []` | Check C:/ComfyUI/models/ has SDXL models |
| Generation fails | `workflow error` | Check ComfyUI console for error details |

**ComfyUI Health Check**:
```powershell
# Test ComfyUI is responding
Invoke-WebRequest -Uri "http://127.0.0.1:8188/system_stats" -Method GET
# Should return JSON with system info
```

### Stage 5: Coordinator Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| Import error | `ModuleNotFoundError: coordinator` | Run from C:/Ziggie with `python -m coordinator.main` |
| API key error | `Invalid API key` | Check ANTHROPIC_API_KEY env var |
| No response | Agent stuck `working` | Check claude_agent_runner.py for API errors |
| Permission error | `Cannot create file` | Check write permissions in coordinator/ |

**Coordinator Debug Mode**:
```powershell
# Run coordinator with verbose output
cd C:\Ziggie
$env:PYTHONPATH = "."
python -m coordinator.main 2>&1 | Tee-Object -FilePath "coordinator_debug.log"
```

### Stage 6: Memory Graph Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| Duplicate entity | `Entity already exists` | Use different name or delete first |
| Relation fails | `Entity not found` | Create both entities before relation |
| Graph too large | Memory slowdown | Consider pruning old entities |
| Search returns nothing | Query too specific | Use broader search terms |

### Stage 7: Production Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| Verification fails | Test doesn't pass | Review specific stage rollback |
| Security issue | Credential found | Remove from memory, rotate key |
| Performance | Slow response | Check which MCPs are timing out |

## C.2 Universal Diagnostic Commands

```powershell
# === DIAGNOSTIC SCRIPT ===
# Save as C:\Ziggie\diagnose.ps1

Write-Host "=== ZIGGIE INTEGRATION DIAGNOSTICS ===" -ForegroundColor Cyan

# Check Python
Write-Host "`nPython:" -ForegroundColor Yellow
python --version 2>&1

# Check Node
Write-Host "`nNode.js:" -ForegroundColor Yellow
node --version 2>&1

# Check npm
Write-Host "`nnpm:" -ForegroundColor Yellow
npm --version 2>&1

# Check uv
Write-Host "`nuv:" -ForegroundColor Yellow
& "C:\ComfyUI\python_embeded\Scripts\uv.exe" --version 2>&1

# Check API key
Write-Host "`nANTHROPIC_API_KEY:" -ForegroundColor Yellow
if ($env:ANTHROPIC_API_KEY) { Write-Host "SET (hidden)" } else { Write-Host "NOT SET" -ForegroundColor Red }

# Check ports
Write-Host "`nPort Status:" -ForegroundColor Yellow
$ports = @(8080, 8081, 8188, 6005, 1234, 3001, 5678)
foreach ($port in $ports) {
    $result = netstat -an | Select-String ":$port "
    if ($result) {
        Write-Host "  Port $port : IN USE" -ForegroundColor Red
    } else {
        Write-Host "  Port $port : Available" -ForegroundColor Green
    }
}

# Check .mcp.json
Write-Host "`n.mcp.json:" -ForegroundColor Yellow
try {
    $config = Get-Content "C:\Ziggie\.mcp.json" | ConvertFrom-Json
    Write-Host "  Valid JSON with $($config.mcpServers.PSObject.Properties.Count) servers"
} catch {
    Write-Host "  INVALID JSON: $_" -ForegroundColor Red
}

# Check key directories
Write-Host "`nDirectories:" -ForegroundColor Yellow
$dirs = @(
    "C:\Ziggie",
    "C:\Ziggie\coordinator",
    "C:\ai-game-dev-system",
    "C:\ai-game-dev-system\mcp-servers\hub",
    "C:\ComfyUI"
)
foreach ($dir in $dirs) {
    if (Test-Path $dir) {
        Write-Host "  $dir : EXISTS" -ForegroundColor Green
    } else {
        Write-Host "  $dir : MISSING" -ForegroundColor Red
    }
}

Write-Host "`n=== END DIAGNOSTICS ===" -ForegroundColor Cyan
```

---

# APPENDIX D: AUTOMATION SCRIPTS

## D.1 Stage 0: Environment Verification Script

```powershell
# save as C:\Ziggie\scripts\verify_environment.ps1

$errors = @()

# Python check
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.1[0-9]") {
    Write-Host "[OK] Python: $pythonVersion" -ForegroundColor Green
} else {
    $errors += "Python 3.10+ required, found: $pythonVersion"
}

# Node check
$nodeVersion = node --version 2>&1
if ($nodeVersion -match "v(1[8-9]|2[0-9])\.") {
    Write-Host "[OK] Node: $nodeVersion" -ForegroundColor Green
} else {
    $errors += "Node 18+ required, found: $nodeVersion"
}

# uv check
if (Test-Path "C:\ComfyUI\python_embeded\Scripts\uv.exe") {
    Write-Host "[OK] uv: Found" -ForegroundColor Green
} else {
    $errors += "uv not found at expected location"
}

# API key check
if ($env:ANTHROPIC_API_KEY -and $env:ANTHROPIC_API_KEY.Length -gt 10) {
    Write-Host "[OK] ANTHROPIC_API_KEY: Set" -ForegroundColor Green
} else {
    $errors += "ANTHROPIC_API_KEY not set or invalid"
}

# Results
if ($errors.Count -eq 0) {
    Write-Host "`nAll checks passed! Ready for integration." -ForegroundColor Green
    exit 0
} else {
    Write-Host "`nErrors found:" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}
```

## D.2 Stage 1: Expand Filesystem MCP Script

```powershell
# save as C:\Ziggie\scripts\expand_filesystem.ps1

$mcpJsonPath = "C:\Ziggie\.mcp.json"
$backupPath = "C:\Ziggie\.mcp.json.backup"

# Backup first
Copy-Item -Path $mcpJsonPath -Destination $backupPath -Force
Write-Host "Backup created: $backupPath" -ForegroundColor Yellow

# Read current config
$config = Get-Content $mcpJsonPath | ConvertFrom-Json

# Update filesystem args
$newArgs = @(
    "/c", "npx", "-y", "@modelcontextprotocol/server-filesystem",
    "C:/Ziggie",
    "C:/ai-game-dev-system",
    "C:/meowping-rts",
    "C:/team-ziggie"
)

$config.mcpServers.filesystem.args = $newArgs

# Write back
$config | ConvertTo-Json -Depth 10 | Set-Content $mcpJsonPath

Write-Host "Filesystem MCP expanded to 4 directories." -ForegroundColor Green
Write-Host "Restart Claude Code to apply changes." -ForegroundColor Yellow
```

## D.3 Stage 2: Add Hub MCP Script

```powershell
# save as C:\Ziggie\scripts\add_hub.ps1

$mcpJsonPath = "C:\Ziggie\.mcp.json"

# Read current config
$config = Get-Content $mcpJsonPath | ConvertFrom-Json

# Add hub configuration
$hubConfig = @{
    command = "C:/ComfyUI/python_embeded/Scripts/uv.exe"
    args = @(
        "run",
        "--with", "mcp",
        "--with", "aiohttp",
        "python",
        "C:/ai-game-dev-system/mcp-servers/hub/mcp_hub_server.py"
    )
}

# Add to mcpServers
$config.mcpServers | Add-Member -MemberType NoteProperty -Name "hub" -Value $hubConfig -Force

# Write back
$config | ConvertTo-Json -Depth 10 | Set-Content $mcpJsonPath

Write-Host "Hub MCP added to configuration." -ForegroundColor Green
Write-Host "Restart Claude Code to apply changes." -ForegroundColor Yellow
```

## D.4 Health Check Script

```powershell
# save as C:\Ziggie\scripts\health_check.ps1

Write-Host "=== INTEGRATION HEALTH CHECK ===" -ForegroundColor Cyan

$results = @()

# Check .mcp.json servers
try {
    $config = Get-Content "C:\Ziggie\.mcp.json" | ConvertFrom-Json
    $serverCount = $config.mcpServers.PSObject.Properties.Count
    $results += @{Component="MCP Config"; Status="OK"; Detail="$serverCount servers configured"}
} catch {
    $results += @{Component="MCP Config"; Status="FAIL"; Detail=$_.Exception.Message}
}

# Check port 8188 (ComfyUI)
$comfyui = netstat -an | Select-String ":8188.*LISTENING"
if ($comfyui) {
    $results += @{Component="ComfyUI"; Status="OK"; Detail="Port 8188 listening"}
} else {
    $results += @{Component="ComfyUI"; Status="WARN"; Detail="Port 8188 not listening"}
}

# Check Hub server file
if (Test-Path "C:\ai-game-dev-system\mcp-servers\hub\mcp_hub_server.py") {
    $results += @{Component="Hub Server"; Status="OK"; Detail="File exists"}
} else {
    $results += @{Component="Hub Server"; Status="FAIL"; Detail="File missing"}
}

# Check Coordinator files
$coordFiles = @("main.py", "client.py", "claude_agent_runner.py", "watcher.py")
$missingCoord = @()
foreach ($file in $coordFiles) {
    if (-not (Test-Path "C:\Ziggie\coordinator\$file")) {
        $missingCoord += $file
    }
}
if ($missingCoord.Count -eq 0) {
    $results += @{Component="Coordinator"; Status="OK"; Detail="All files present"}
} else {
    $results += @{Component="Coordinator"; Status="FAIL"; Detail="Missing: $($missingCoord -join ', ')"}
}

# Display results
Write-Host "`nResults:" -ForegroundColor Yellow
foreach ($r in $results) {
    $color = switch ($r.Status) {
        "OK" { "Green" }
        "WARN" { "Yellow" }
        "FAIL" { "Red" }
    }
    Write-Host "  [$($r.Status)] $($r.Component): $($r.Detail)" -ForegroundColor $color
}

Write-Host "`n=== END HEALTH CHECK ===" -ForegroundColor Cyan
```

---

# APPENDIX E: DEPENDENCY CHAINS

## E.1 Stage Dependencies (Must Complete In Order)

```
Stage 0 ─────────────────────────────────────────────────────────────────────►
   │
   ▼
Stage 1 (Layer 1) ───────────────────────────────────────────────────────────►
   │
   ├──► Filesystem expanded ──┬──► Stage 2 (Hub)
   │                          │
   └──► Memory populated ─────┘
                              │
                              ▼
                        Stage 2 (Hub) ───────────────────────────────────────►
                              │
                              ├──► Stage 3 (Game Engines) [OPTIONAL]
                              │         │
                              │         ▼
                              ├──► Stage 4 (ComfyUI)
                              │         │
                              │         ▼
                              └──► Stage 5 (Coordinator)
                                        │
                                        ▼
                                  Stage 6 (Knowledge Graph)
                                        │
                                        ▼
                                  Stage 7 (Production)
```

## E.2 Task Dependencies Within Stages

### Stage 1 Task Dependencies
```
1.1.1 (Open .mcp.json)
   │
   ▼
1.1.2 (Update args)
   │
   ▼
1.1.3 (Save file)
   │
   ▼
1.1.4 (Restart Claude) ──► 1.1.5 (Verify access)
                                │
                                ▼
                          1.2.1-1.2.5 (Create entities) ──► 1.3.x (Create relations)
                                                                 │
                                                                 ▼
                                                           1.4.x (Verification)
```

### Stage 2 Task Dependencies
```
2.1.1 (Install mcp) ──┬──► 2.1.3 (Verify hub file)
                      │           │
2.1.2 (Install aiohttp)──┘        ▼
                            2.2.1-2.2.3 (Add to config)
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
              2.3.1 (ComfyUI) 2.3.2 (Unity) 2.3.3-4 (etc.)
                    │             │             │
                    └─────────────┴─────────────┘
                                  │
                                  ▼
                            2.4.1 (Restart) ──► 2.4.2-4 (Tests)
```

## E.3 Parallel Execution Opportunities

**What CAN run in parallel**:
```
Stage 3 Parallel:
├── 3.1 Unity MCP ──────┐
├── 3.2 Unreal MCP ─────┼──► All can start simultaneously
└── 3.3 Godot MCP ──────┘

Stage 6 Parallel:
├── 6.1 Agent entities ─┐
├── 6.2 Service entities┼──► All can create simultaneously
└── 6.3 Doc entities ───┘
```

**What MUST be sequential**:
```
.mcp.json edit ──► Restart Claude Code ──► Verify MCPs
Entity creation ──► Relation creation (entities must exist first)
Stage N gate pass ──► Stage N+1 start
```

---

# APPENDIX F: RISK ASSESSMENT

## F.1 Risk Matrix by Stage

| Stage | Risk | Probability | Impact | Mitigation |
|-------|------|-------------|--------|------------|
| 0 | Missing dependencies | Medium | High | Verify all before starting |
| 1 | JSON syntax error | Medium | Medium | Backup first, validate JSON |
| 1 | Path permission denied | Low | High | Run as admin if needed |
| 2 | Hub server crash | Medium | Medium | Debug standalone first |
| 2 | Package conflict | Low | Medium | Use isolated environment |
| 3 | Engine not installed | Medium | Low | Stage is optional |
| 3 | Port conflict | Medium | Medium | Check ports before starting |
| 4 | ComfyUI not running | Medium | Medium | Start ComfyUI first |
| 4 | No models available | Medium | Low | Download SDXL model |
| 5 | API key invalid | Medium | High | Test key before coordinator |
| 5 | Coordinator crash | Low | Medium | Check Python environment |
| 6 | Duplicate entities | Low | Low | Check before creating |
| 7 | Gate failure | Low | High | Review failed stage |

## F.2 Critical Path Analysis

**Critical Path** (longest sequence, determines minimum time):
```
Stage 0 (30 min)
    ↓
Stage 1 (15 min)
    ↓
Stage 2 (30 min)
    ↓
Stage 4 (30 min)  ← Can skip Stage 3 if no game engines
    ↓
Stage 5 (45 min)
    ↓
Stage 6 (30 min)
    ↓
Stage 7 (30 min)
─────────────────
Total: 3 hours 30 minutes (skipping Stage 3)
```

**With Game Engines** (Stage 3):
```
Total: 4 hours 15 minutes
```

## F.3 Failure Recovery Points

```
CHECKPOINT 1: After Stage 0
├── Safe state: Original config preserved
├── Recovery: Simply start over
└── Data loss: None

CHECKPOINT 2: After Stage 1 Gate
├── Safe state: Filesystem expanded, memory populated
├── Recovery: Rollback .mcp.json, clear memory
└── Data loss: Entity data (can recreate)

CHECKPOINT 3: After Stage 2 Gate
├── Safe state: Hub operational
├── Recovery: Remove hub from config
└── Data loss: None

CHECKPOINT 4: After Stage 5 Gate
├── Safe state: Full agent system operational
├── Recovery: Stop coordinator, clean directories
└── Data loss: Agent responses (can regenerate)

CHECKPOINT 5: After Stage 7 Gate
├── Safe state: FULL INTEGRATION COMPLETE
├── Recovery: N/A - Production ready
└── Data loss: N/A
```

---

# APPENDIX G: DECISION TREES

## G.1 Stage 3 Decision: Which Game Engine?

```
                    Do you have Unity installed?
                              │
              ┌───────────────┴───────────────┐
              │ YES                           │ NO
              ▼                               ▼
     Unity MCP is best            Do you have Unreal installed?
     option for you                           │
                              ┌───────────────┴───────────────┐
                              │ YES                           │ NO
                              ▼                               ▼
                     Unreal MCP                    Do you have Godot?
                     is your option                          │
                                             ┌───────────────┴───────────────┐
                                             │ YES                           │ NO
                                             ▼                               ▼
                                        Godot MCP                    SKIP Stage 3
                                        is your option               (proceed to 4)
```

## G.2 Hub vs Individual MCPs Decision

```
                How many backends will you use regularly?
                              │
              ┌───────────────┴───────────────┐
              │ 1-2 backends                  │ 3+ backends
              ▼                               ▼
     Consider individual            MCP Hub is recommended
     MCP configurations             (single connection = all tools)
              │                               │
              ▼                               ▼
     Pros: Simpler config          Pros: One config for all
     Cons: Multiple entries        Cons: All backends in one
```

## G.3 Troubleshooting Decision Tree

```
                    MCP not responding?
                              │
              ┌───────────────┴───────────────┐
              │ After config change           │ Was working before
              ▼                               ▼
     Check JSON syntax              Check if service is running
     (validate .mcp.json)           (netstat for port)
              │                               │
     ┌────────┴────────┐           ┌─────────┴─────────┐
     │ JSON OK         │ JSON BAD  │ Port open         │ Port closed
     ▼                 ▼           ▼                   ▼
   Restart        Fix syntax    Check Claude       Start the
   Claude Code    & retry       Code logs          service
```

---

# APPENDIX H: SUCCESS METRICS

## H.1 Quantified Success Criteria

| Stage | Metric | Target | Measurement Method |
|-------|--------|--------|-------------------|
| 0 | Dependencies verified | 5/5 | verify_environment.ps1 |
| 1 | Directories accessible | 4/4 | mcp__filesystem__list_directory |
| 1 | Entities created | 50+ | mcp__memory__read_graph count |
| 1 | Relations created | 15+ | mcp__memory__read_graph count |
| 2 | Hub tools accessible | 6/6 | Tool call success |
| 2 | Backends online | ≥1 | hub_status result |
| 3 | Engine tools accessible | ≥1 | Tool call success |
| 4 | Workflows listed | ≥1 | list_workflows result |
| 4 | Image generated | 1+ | File created |
| 5 | Agent deployed | 1+ | Response file exists |
| 6 | Total entities | 75+ | read_graph count |
| 6 | Total relations | 50+ | read_graph count |
| 7 | All tests passed | 100% | Verification checklist |

## H.2 Integration Completion Scorecard

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    INTEGRATION COMPLETION SCORECARD                    ║
╠═══════════════════════════════════════════════════════════════════════╣
║ Stage 0: Assessment               [ ] PASSED  [ ] FAILED  [ ] SKIPPED ║
║ Stage 1: Layer 1 Enhancement      [ ] PASSED  [ ] FAILED  [ ] SKIPPED ║
║ Stage 2: Hub Integration          [ ] PASSED  [ ] FAILED  [ ] SKIPPED ║
║ Stage 3: Game Engines             [ ] PASSED  [ ] FAILED  [ ] SKIPPED ║
║ Stage 4: Asset Generation         [ ] PASSED  [ ] FAILED  [ ] SKIPPED ║
║ Stage 5: Agent Orchestration      [ ] PASSED  [ ] FAILED  [ ] SKIPPED ║
║ Stage 6: Knowledge Graph          [ ] PASSED  [ ] FAILED  [ ] SKIPPED ║
║ Stage 7: Production Ready         [ ] PASSED  [ ] FAILED  [ ] SKIPPED ║
╠═══════════════════════════════════════════════════════════════════════╣
║ Overall Status: ___ / 8 Stages Passed                                  ║
║ Integration Level: [ ] Minimal  [ ] Partial  [ ] Full  [ ] Production ║
║ Date Completed: ____________________                                   ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

# APPENDIX I: EXECUTION PLAYBOOKS

## I.1 Stage 0 Execution Playbook (Copy-Paste Ready)

```powershell
# ============================================================
# STAGE 0: ASSESSMENT EXECUTION PLAYBOOK
# Run each section in order, verify results before proceeding
# ============================================================

Write-Host "=== STAGE 0: ASSESSMENT ===" -ForegroundColor Cyan
Write-Host "Started: $(Get-Date)" -ForegroundColor Yellow

# --- Phase 0.1: Environment Verification ---
Write-Host "`n--- Phase 0.1: Environment Verification ---" -ForegroundColor Green

Write-Host "Checking Python..." -NoNewline
$python = python --version 2>&1
if ($python -match "Python 3") { Write-Host " OK: $python" -ForegroundColor Green }
else { Write-Host " FAIL" -ForegroundColor Red; exit 1 }

Write-Host "Checking Node.js..." -NoNewline
$node = node --version 2>&1
if ($node -match "v") { Write-Host " OK: $node" -ForegroundColor Green }
else { Write-Host " FAIL" -ForegroundColor Red; exit 1 }

Write-Host "Checking npm..." -NoNewline
$npm = npm --version 2>&1
if ($npm) { Write-Host " OK: $npm" -ForegroundColor Green }
else { Write-Host " FAIL" -ForegroundColor Red; exit 1 }

Write-Host "Checking uv..." -NoNewline
if (Test-Path "C:\ComfyUI\python_embeded\Scripts\uv.exe") {
    Write-Host " OK: Found" -ForegroundColor Green
} else { Write-Host " FAIL: Not found" -ForegroundColor Red; exit 1 }

# --- Phase 0.2: Directory Structure ---
Write-Host "`n--- Phase 0.2: Directory Structure ---" -ForegroundColor Green

$directories = @(
    "C:\Ziggie",
    "C:\Ziggie\coordinator",
    "C:\ai-game-dev-system",
    "C:\ai-game-dev-system\mcp-servers\hub",
    "C:\ComfyUI"
)

foreach ($dir in $directories) {
    Write-Host "Checking $dir..." -NoNewline
    if (Test-Path $dir) { Write-Host " OK" -ForegroundColor Green }
    else { Write-Host " MISSING" -ForegroundColor Yellow }
}

# --- Phase 0.3: Backup Configuration ---
Write-Host "`n--- Phase 0.3: Backup Configuration ---" -ForegroundColor Green

$mcpJson = "C:\Ziggie\.mcp.json"
$backup = "C:\Ziggie\.mcp.json.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"

Write-Host "Creating backup..." -NoNewline
Copy-Item -Path $mcpJson -Destination $backup -Force
Write-Host " OK: $backup" -ForegroundColor Green

# --- Phase 0.4: Dependencies ---
Write-Host "`n--- Phase 0.4: Dependencies ---" -ForegroundColor Green

$packages = @("anthropic", "mcp", "aiohttp", "websockets")
foreach ($pkg in $packages) {
    Write-Host "Checking $pkg..." -NoNewline
    $result = pip show $pkg 2>&1
    if ($result -match "Name: $pkg") { Write-Host " OK" -ForegroundColor Green }
    else { Write-Host " NOT INSTALLED" -ForegroundColor Yellow }
}

# --- GATE 0 CHECK ---
Write-Host "`n=== GATE 0: ASSESSMENT COMPLETE ===" -ForegroundColor Cyan
Write-Host "Review results above. If all OK, proceed to Stage 1."
Write-Host "Completed: $(Get-Date)" -ForegroundColor Yellow
```

## I.2 Stage 1 Execution Playbook

```powershell
# ============================================================
# STAGE 1: LAYER 1 ENHANCEMENT EXECUTION PLAYBOOK
# ============================================================

Write-Host "=== STAGE 1: LAYER 1 ENHANCEMENT ===" -ForegroundColor Cyan
Write-Host "Started: $(Get-Date)" -ForegroundColor Yellow

# --- Phase 1.1: Expand Filesystem MCP ---
Write-Host "`n--- Phase 1.1: Expand Filesystem MCP ---" -ForegroundColor Green

$mcpJson = "C:\Ziggie\.mcp.json"
$config = Get-Content $mcpJson | ConvertFrom-Json

# Update filesystem args
$newArgs = @(
    "/c", "npx", "-y", "@modelcontextprotocol/server-filesystem",
    "C:/Ziggie",
    "C:/ai-game-dev-system",
    "C:/meowping-rts",
    "C:/team-ziggie"
)

$config.mcpServers.filesystem.args = $newArgs
$config | ConvertTo-Json -Depth 10 | Set-Content $mcpJson

Write-Host "Filesystem MCP expanded to 4 directories" -ForegroundColor Green
Write-Host "RESTART CLAUDE CODE NOW to apply changes" -ForegroundColor Yellow

# --- Phase 1.2: Memory Population Script ---
Write-Host "`n--- Phase 1.2: Memory Population ---" -ForegroundColor Green
Write-Host "After restart, use mcp__memory__create_entities with the entity JSON from the plan"
Write-Host "Entity types to create: project, infrastructure, agent, documentation, service"

# --- GATE 1 CHECK ---
Write-Host "`n=== GATE 1: LAYER 1 OPERATIONAL ===" -ForegroundColor Cyan
Write-Host "After Claude Code restart, verify:"
Write-Host "  [ ] Filesystem reads from C:/ai-game-dev-system work"
Write-Host "  [ ] Memory MCP contains 50+ entities"
Write-Host "  [ ] Memory MCP contains 15+ relations"
```

## I.3 Stage 2 Execution Playbook

```powershell
# ============================================================
# STAGE 2: MCP HUB INTEGRATION EXECUTION PLAYBOOK
# ============================================================

Write-Host "=== STAGE 2: MCP HUB INTEGRATION ===" -ForegroundColor Cyan

# --- Phase 2.1: Prerequisites ---
Write-Host "`n--- Phase 2.1: Hub Prerequisites ---" -ForegroundColor Green

Write-Host "Installing required packages..."
pip install mcp aiohttp --quiet
Write-Host "Packages installed" -ForegroundColor Green

# Verify hub server
$hubPath = "C:\ai-game-dev-system\mcp-servers\hub\mcp_hub_server.py"
if (Test-Path $hubPath) {
    Write-Host "Hub server file: OK" -ForegroundColor Green
} else {
    Write-Host "Hub server file: MISSING" -ForegroundColor Red
    exit 1
}

# --- Phase 2.2: Add Hub to Configuration ---
Write-Host "`n--- Phase 2.2: Add Hub to .mcp.json ---" -ForegroundColor Green

$mcpJson = "C:\Ziggie\.mcp.json"
$config = Get-Content $mcpJson | ConvertFrom-Json

$hubConfig = @{
    command = "C:/ComfyUI/python_embeded/Scripts/uv.exe"
    args = @(
        "run",
        "--with", "mcp",
        "--with", "aiohttp",
        "python",
        "C:/ai-game-dev-system/mcp-servers/hub/mcp_hub_server.py"
    )
}

$config.mcpServers | Add-Member -MemberType NoteProperty -Name "hub" -Value $hubConfig -Force
$config | ConvertTo-Json -Depth 10 | Set-Content $mcpJson

Write-Host "Hub added to configuration" -ForegroundColor Green
Write-Host "RESTART CLAUDE CODE NOW" -ForegroundColor Yellow

# --- GATE 2 CHECK ---
Write-Host "`n=== GATE 2: HUB OPERATIONAL ===" -ForegroundColor Cyan
Write-Host "After restart, test with: hub_status tool"
```

## I.4 Full Integration Execution Script

```powershell
# ============================================================
# FULL INTEGRATION EXECUTION SCRIPT
# Runs Stages 0-2 in sequence with user confirmations
# Save as: C:\Ziggie\scripts\full_integration.ps1
# ============================================================

param(
    [switch]$SkipConfirmations
)

function Confirm-Continue {
    param([string]$Message)
    if (-not $SkipConfirmations) {
        $response = Read-Host "$Message (y/n)"
        if ($response -ne 'y') {
            Write-Host "Aborted by user" -ForegroundColor Yellow
            exit 0
        }
    }
}

Write-Host @"
╔══════════════════════════════════════════════════════════════════╗
║           ZIGGIE FULL INTEGRATION EXECUTION SCRIPT                ║
╠══════════════════════════════════════════════════════════════════╣
║ This script will execute Stages 0-2 of the integration plan      ║
║ Claude Code restart required between stages                       ║
╚══════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

$startTime = Get-Date
Write-Host "Started: $startTime"

# Execute Stage 0
Write-Host "`n" + "="*60
Write-Host "EXECUTING STAGE 0: ASSESSMENT"
Write-Host "="*60
& "$PSScriptRoot\stage0_assessment.ps1"
Confirm-Continue "Stage 0 complete. Continue to Stage 1?"

# Execute Stage 1
Write-Host "`n" + "="*60
Write-Host "EXECUTING STAGE 1: LAYER 1 ENHANCEMENT"
Write-Host "="*60
& "$PSScriptRoot\stage1_layer1.ps1"

Write-Host "`n!!! CLAUDE CODE RESTART REQUIRED !!!" -ForegroundColor Yellow
Write-Host "1. Close this terminal"
Write-Host "2. Restart Claude Code"
Write-Host "3. Run: .\continue_integration.ps1"

$endTime = Get-Date
$duration = $endTime - $startTime
Write-Host "`nStages 0-1 Duration: $($duration.TotalMinutes) minutes"
```

---

# APPENDIX J: MONITORING & OBSERVABILITY

## J.1 Real-Time Monitoring Dashboard Script

```powershell
# ============================================================
# INTEGRATION MONITORING DASHBOARD
# Save as: C:\Ziggie\scripts\monitor_dashboard.ps1
# Run in separate terminal during integration
# ============================================================

param(
    [int]$RefreshSeconds = 5
)

function Get-MCPStatus {
    $status = @{}

    # Check filesystem MCP (via .mcp.json)
    try {
        $config = Get-Content "C:\Ziggie\.mcp.json" | ConvertFrom-Json
        $status["MCP Config"] = "OK ($($config.mcpServers.PSObject.Properties.Count) servers)"
    } catch {
        $status["MCP Config"] = "ERROR"
    }

    # Check ports
    $ports = @{
        "ComfyUI (8188)" = 8188
        "Unity MCP (8080)" = 8080
        "Unreal MCP (8081)" = 8081
        "Godot MCP (6005)" = 6005
        "LocalLLM (1234)" = 1234
        "n8n (5678)" = 5678
    }

    foreach ($name in $ports.Keys) {
        $port = $ports[$name]
        $listening = netstat -an | Select-String ":$port.*LISTENING"
        $status[$name] = if ($listening) { "ONLINE" } else { "OFFLINE" }
    }

    return $status
}

function Get-CoordinatorStatus {
    $pythonProcs = Get-Process -Name python* -ErrorAction SilentlyContinue
    $coordinatorRunning = $pythonProcs | Where-Object {
        $_.CommandLine -like "*coordinator*"
    }

    return if ($coordinatorRunning) { "RUNNING" } else { "STOPPED" }
}

function Get-MemoryStats {
    $memory = Get-Process | Measure-Object WorkingSet -Sum
    return [math]::Round($memory.Sum / 1GB, 2)
}

# Main monitoring loop
while ($true) {
    Clear-Host

    Write-Host @"
╔══════════════════════════════════════════════════════════════════╗
║              ZIGGIE INTEGRATION MONITORING DASHBOARD              ║
╠══════════════════════════════════════════════════════════════════╣
"@ -ForegroundColor Cyan

    Write-Host "Last Updated: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Yellow
    Write-Host "Refresh Rate: ${RefreshSeconds}s`n"

    # MCP Status
    Write-Host "MCP & SERVICE STATUS:" -ForegroundColor Green
    Write-Host "-" * 40
    $mcpStatus = Get-MCPStatus
    foreach ($key in $mcpStatus.Keys | Sort-Object) {
        $value = $mcpStatus[$key]
        $color = if ($value -match "OK|ONLINE") { "Green" }
                 elseif ($value -match "OFFLINE") { "Yellow" }
                 else { "Red" }
        Write-Host ("  {0,-25} : {1}" -f $key, $value) -ForegroundColor $color
    }

    # Coordinator Status
    Write-Host "`nCOORDINATOR STATUS:" -ForegroundColor Green
    Write-Host "-" * 40
    $coordStatus = Get-CoordinatorStatus
    $color = if ($coordStatus -eq "RUNNING") { "Green" } else { "Yellow" }
    Write-Host "  Agent Coordinator      : $coordStatus" -ForegroundColor $color

    # System Resources
    Write-Host "`nSYSTEM RESOURCES:" -ForegroundColor Green
    Write-Host "-" * 40
    $memoryGB = Get-MemoryStats
    Write-Host "  Total Memory Used      : ${memoryGB} GB"

    # Recent Files
    Write-Host "`nRECENT ACTIVITY (Last 5 min):" -ForegroundColor Green
    Write-Host "-" * 40
    $recentFiles = Get-ChildItem -Path "C:\Ziggie" -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-5) } |
        Select-Object -First 5

    if ($recentFiles) {
        foreach ($file in $recentFiles) {
            Write-Host "  $($file.Name) - $($file.LastWriteTime.ToString('HH:mm:ss'))"
        }
    } else {
        Write-Host "  (No recent file changes)"
    }

    Write-Host "`n╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to exit"

    Start-Sleep -Seconds $RefreshSeconds
}
```

## J.2 Log Aggregation Script

```powershell
# ============================================================
# LOG AGGREGATOR - Collects all integration logs
# Save as: C:\Ziggie\scripts\aggregate_logs.ps1
# ============================================================

$logDir = "C:\Ziggie\integration-logs"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputFile = "$logDir\aggregated_$timestamp.log"

# Create log directory
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

# Log sources
$logSources = @(
    @{Path="C:\Ziggie\agent-deployment\logs\*.log"; Name="Coordinator"},
    @{Path="C:\Ziggie\coordinator\*.log"; Name="Agent Runner"},
    @{Path="C:\ComfyUI\*.log"; Name="ComfyUI"}
)

Write-Host "Aggregating logs to: $outputFile" -ForegroundColor Cyan

foreach ($source in $logSources) {
    $files = Get-ChildItem -Path $source.Path -ErrorAction SilentlyContinue
    if ($files) {
        Add-Content -Path $outputFile -Value "`n=== $($source.Name) LOGS ==="
        foreach ($file in $files) {
            Add-Content -Path $outputFile -Value "`n--- $($file.Name) ---"
            Get-Content $file.FullName | Add-Content -Path $outputFile
        }
    }
}

Write-Host "Log aggregation complete: $outputFile" -ForegroundColor Green
```

## J.3 Integration Event Logging

```powershell
# ============================================================
# INTEGRATION EVENT LOGGER
# Save as: C:\Ziggie\scripts\log_event.ps1
# Usage: .\log_event.ps1 -Stage 1 -Phase 2 -Event "Completed" -Details "All entities created"
# ============================================================

param(
    [Parameter(Mandatory=$true)][int]$Stage,
    [Parameter(Mandatory=$true)][int]$Phase,
    [Parameter(Mandatory=$true)][string]$Event,
    [string]$Details = "",
    [ValidateSet("INFO","WARN","ERROR","SUCCESS")][string]$Level = "INFO"
)

$logFile = "C:\Ziggie\integration-logs\integration_events.jsonl"
$logDir = Split-Path $logFile
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

$logEntry = @{
    timestamp = (Get-Date -Format "o")
    stage = $Stage
    phase = $Phase
    event = $Event
    details = $Details
    level = $Level
    hostname = $env:COMPUTERNAME
    user = $env:USERNAME
} | ConvertTo-Json -Compress

Add-Content -Path $logFile -Value $logEntry

Write-Host "[$Level] Stage $Stage.Phase $Phase : $Event" -ForegroundColor $(
    switch ($Level) {
        "SUCCESS" { "Green" }
        "WARN" { "Yellow" }
        "ERROR" { "Red" }
        default { "White" }
    }
)
```

---

# APPENDIX K: PERFORMANCE BENCHMARKS

## K.1 Expected Performance Metrics

| Metric | Baseline | Target | Critical Threshold |
|--------|----------|--------|-------------------|
| Claude Code startup | 5-10s | <10s | >30s = Issue |
| MCP tool call latency | 100-500ms | <500ms | >2s = Issue |
| Memory MCP read_graph | 50-200ms | <500ms | >1s = Issue |
| Hub status check | 200-500ms | <1s | >3s = Issue |
| ComfyUI generation | 5-30s | varies | >120s = Timeout |
| Agent deployment | 2-10s | <30s | >60s = Issue |
| Filesystem read (1MB) | 50-100ms | <500ms | >2s = Issue |

## K.2 Benchmark Test Script

```powershell
# ============================================================
# INTEGRATION PERFORMANCE BENCHMARK
# Save as: C:\Ziggie\scripts\run_benchmarks.ps1
# ============================================================

$results = @()

function Measure-Operation {
    param(
        [string]$Name,
        [scriptblock]$Operation,
        [int]$Iterations = 3
    )

    $times = @()
    for ($i = 0; $i -lt $Iterations; $i++) {
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        try {
            & $Operation | Out-Null
            $sw.Stop()
            $times += $sw.ElapsedMilliseconds
        } catch {
            $times += -1  # Error indicator
        }
    }

    $validTimes = $times | Where-Object { $_ -ge 0 }
    return @{
        Name = $Name
        Min = ($validTimes | Measure-Object -Minimum).Minimum
        Max = ($validTimes | Measure-Object -Maximum).Maximum
        Avg = [math]::Round(($validTimes | Measure-Object -Average).Average, 2)
        Errors = ($times | Where-Object { $_ -lt 0 }).Count
    }
}

Write-Host "=== INTEGRATION PERFORMANCE BENCHMARK ===" -ForegroundColor Cyan
Write-Host "Started: $(Get-Date)`n"

# Benchmark: File System Read
Write-Host "Testing: File System Read..." -NoNewline
$result = Measure-Operation -Name "Filesystem Read" -Operation {
    Get-Content "C:\Ziggie\.mcp.json" | Out-Null
}
$results += $result
Write-Host " Done" -ForegroundColor Green

# Benchmark: Directory Listing
Write-Host "Testing: Directory Listing..." -NoNewline
$result = Measure-Operation -Name "Directory List" -Operation {
    Get-ChildItem "C:\Ziggie" | Out-Null
}
$results += $result
Write-Host " Done" -ForegroundColor Green

# Benchmark: JSON Parse
Write-Host "Testing: JSON Parse..." -NoNewline
$result = Measure-Operation -Name "JSON Parse" -Operation {
    Get-Content "C:\Ziggie\.mcp.json" | ConvertFrom-Json | Out-Null
}
$results += $result
Write-Host " Done" -ForegroundColor Green

# Benchmark: Port Check
Write-Host "Testing: Port Check..." -NoNewline
$result = Measure-Operation -Name "Port Check" -Operation {
    Test-NetConnection -ComputerName localhost -Port 8188 -WarningAction SilentlyContinue | Out-Null
}
$results += $result
Write-Host " Done" -ForegroundColor Green

# Display Results
Write-Host "`n=== BENCHMARK RESULTS ===" -ForegroundColor Cyan
Write-Host ("{0,-25} {1,10} {2,10} {3,10} {4,8}" -f "Operation", "Min(ms)", "Max(ms)", "Avg(ms)", "Errors")
Write-Host "-" * 70

foreach ($r in $results) {
    $color = if ($r.Errors -gt 0) { "Red" } elseif ($r.Avg -gt 1000) { "Yellow" } else { "Green" }
    Write-Host ("{0,-25} {1,10} {2,10} {3,10} {4,8}" -f $r.Name, $r.Min, $r.Max, $r.Avg, $r.Errors) -ForegroundColor $color
}

# Save results
$benchmarkFile = "C:\Ziggie\integration-logs\benchmark_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$results | ConvertTo-Json | Set-Content $benchmarkFile
Write-Host "`nResults saved to: $benchmarkFile"
```

---

# APPENDIX L: INTEGRATION TESTING SUITE

## L.1 Automated Integration Tests

```powershell
# ============================================================
# INTEGRATION TEST SUITE
# Save as: C:\Ziggie\scripts\run_integration_tests.ps1
# ============================================================

$testResults = @()
$passCount = 0
$failCount = 0

function Test-Assertion {
    param(
        [string]$TestName,
        [scriptblock]$Test,
        [string]$Expected
    )

    try {
        $result = & $Test
        $passed = $result -eq $true -or $result -match $Expected

        if ($passed) {
            Write-Host "[PASS] $TestName" -ForegroundColor Green
            $script:passCount++
            return @{Name=$TestName; Status="PASS"; Result=$result}
        } else {
            Write-Host "[FAIL] $TestName - Expected: $Expected, Got: $result" -ForegroundColor Red
            $script:failCount++
            return @{Name=$TestName; Status="FAIL"; Expected=$Expected; Actual=$result}
        }
    } catch {
        Write-Host "[ERROR] $TestName - $($_.Exception.Message)" -ForegroundColor Red
        $script:failCount++
        return @{Name=$TestName; Status="ERROR"; Error=$_.Exception.Message}
    }
}

Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║            ZIGGIE INTEGRATION TEST SUITE                          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "Started: $(Get-Date)`n"

# === STAGE 0 TESTS ===
Write-Host "=== STAGE 0: ENVIRONMENT TESTS ===" -ForegroundColor Yellow

$testResults += Test-Assertion -TestName "Python installed" -Test {
    (python --version 2>&1) -match "Python 3"
} -Expected "True"

$testResults += Test-Assertion -TestName "Node.js installed" -Test {
    (node --version 2>&1) -match "v"
} -Expected "True"

$testResults += Test-Assertion -TestName "uv executable exists" -Test {
    Test-Path "C:\ComfyUI\python_embeded\Scripts\uv.exe"
} -Expected "True"

# === STAGE 1 TESTS ===
Write-Host "`n=== STAGE 1: LAYER 1 TESTS ===" -ForegroundColor Yellow

$testResults += Test-Assertion -TestName ".mcp.json is valid JSON" -Test {
    try {
        Get-Content "C:\Ziggie\.mcp.json" | ConvertFrom-Json | Out-Null
        $true
    } catch { $false }
} -Expected "True"

$testResults += Test-Assertion -TestName "Ziggie directory accessible" -Test {
    Test-Path "C:\Ziggie"
} -Expected "True"

$testResults += Test-Assertion -TestName "ai-game-dev-system directory exists" -Test {
    Test-Path "C:\ai-game-dev-system"
} -Expected "True"

$testResults += Test-Assertion -TestName "Coordinator files exist" -Test {
    (Test-Path "C:\Ziggie\coordinator\main.py") -and
    (Test-Path "C:\Ziggie\coordinator\client.py") -and
    (Test-Path "C:\Ziggie\coordinator\claude_agent_runner.py")
} -Expected "True"

# === STAGE 2 TESTS ===
Write-Host "`n=== STAGE 2: HUB TESTS ===" -ForegroundColor Yellow

$testResults += Test-Assertion -TestName "Hub server file exists" -Test {
    Test-Path "C:\ai-game-dev-system\mcp-servers\hub\mcp_hub_server.py"
} -Expected "True"

$testResults += Test-Assertion -TestName "mcp package installed" -Test {
    (pip show mcp 2>&1) -match "Name: mcp"
} -Expected "True"

$testResults += Test-Assertion -TestName "aiohttp package installed" -Test {
    (pip show aiohttp 2>&1) -match "Name: aiohttp"
} -Expected "True"

# === STAGE 4 TESTS ===
Write-Host "`n=== STAGE 4: COMFYUI TESTS ===" -ForegroundColor Yellow

$testResults += Test-Assertion -TestName "ComfyUI directory exists" -Test {
    Test-Path "C:\ComfyUI"
} -Expected "True"

$testResults += Test-Assertion -TestName "ComfyUI MCP server file exists" -Test {
    Test-Path "C:\ai-game-dev-system\mcp-servers\comfyui-mcp\server.py"
} -Expected "True"

# === STAGE 5 TESTS ===
Write-Host "`n=== STAGE 5: AGENT TESTS ===" -ForegroundColor Yellow

$testResults += Test-Assertion -TestName "ANTHROPIC_API_KEY environment variable set" -Test {
    $env:ANTHROPIC_API_KEY -and $env:ANTHROPIC_API_KEY.Length -gt 10
} -Expected "True"

$testResults += Test-Assertion -TestName "anthropic package installed" -Test {
    (pip show anthropic 2>&1) -match "Name: anthropic"
} -Expected "True"

# === SUMMARY ===
Write-Host "`n╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                      TEST SUMMARY                                  ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

$total = $passCount + $failCount
$passRate = if ($total -gt 0) { [math]::Round(($passCount / $total) * 100, 1) } else { 0 }

Write-Host "Total Tests : $total"
Write-Host "Passed      : $passCount" -ForegroundColor Green
Write-Host "Failed      : $failCount" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "Green" })
Write-Host "Pass Rate   : $passRate%"

if ($failCount -eq 0) {
    Write-Host "`n✓ ALL TESTS PASSED" -ForegroundColor Green
} else {
    Write-Host "`n✗ SOME TESTS FAILED - Review before proceeding" -ForegroundColor Red
}

# Save results
$testFile = "C:\Ziggie\integration-logs\test_results_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
@{
    Timestamp = (Get-Date -Format "o")
    Total = $total
    Passed = $passCount
    Failed = $failCount
    PassRate = $passRate
    Results = $testResults
} | ConvertTo-Json -Depth 5 | Set-Content $testFile

Write-Host "Results saved to: $testFile"
```

---

# APPENDIX M: MAINTENANCE PROCEDURES

## M.1 Daily Maintenance Checklist

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                     DAILY MAINTENANCE CHECKLIST                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║ HEALTH CHECKS (5 minutes)                                                     ║
║ [ ] Run health_check.ps1 script                                               ║
║ [ ] Verify all active MCPs responding                                         ║
║ [ ] Check disk space > 10GB free                                              ║
║ [ ] Review overnight logs for errors                                          ║
║                                                                               ║
║ LOG ROTATION (2 minutes)                                                      ║
║ [ ] Archive logs older than 7 days                                            ║
║ [ ] Delete logs older than 30 days                                            ║
║ [ ] Check log directory size < 1GB                                            ║
║                                                                               ║
║ MEMORY GRAPH (3 minutes)                                                      ║
║ [ ] Verify memory MCP accessible                                              ║
║ [ ] Check entity count (should be stable or growing)                          ║
║ [ ] No orphaned entities                                                      ║
║                                                                               ║
║ BACKUP STATUS (2 minutes)                                                     ║
║ [ ] Verify .mcp.json.backup exists                                            ║
║ [ ] Backup age < 24 hours                                                     ║
║                                                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## M.2 Weekly Maintenance Checklist

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                     WEEKLY MAINTENANCE CHECKLIST                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║ PERFORMANCE REVIEW (10 minutes)                                               ║
║ [ ] Run performance benchmarks                                                ║
║ [ ] Compare to baseline metrics                                               ║
║ [ ] Investigate any degradation                                               ║
║                                                                               ║
║ PACKAGE UPDATES (15 minutes)                                                  ║
║ [ ] Check for MCP package updates: pip list --outdated                        ║
║ [ ] Check for Node.js package updates: npm outdated                           ║
║ [ ] Review changelogs before updating                                         ║
║ [ ] Update in test environment first                                          ║
║                                                                               ║
║ CONFIGURATION REVIEW (10 minutes)                                             ║
║ [ ] Review .mcp.json for unnecessary entries                                  ║
║ [ ] Verify all paths still valid                                              ║
║ [ ] Check for deprecated configurations                                       ║
║                                                                               ║
║ KNOWLEDGE GRAPH MAINTENANCE (15 minutes)                                      ║
║ [ ] Review and clean up orphaned entities                                     ║
║ [ ] Add new entities for new components                                       ║
║ [ ] Verify relations are current                                              ║
║                                                                               ║
║ BACKUP VERIFICATION (5 minutes)                                               ║
║ [ ] Test restore from backup                                                  ║
║ [ ] Create fresh backup                                                       ║
║ [ ] Archive weekly backup offsite                                             ║
║                                                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## M.3 Log Rotation Script

```powershell
# ============================================================
# LOG ROTATION SCRIPT
# Save as: C:\Ziggie\scripts\rotate_logs.ps1
# Schedule: Daily via Task Scheduler
# ============================================================

$logDirs = @(
    "C:\Ziggie\agent-deployment\logs",
    "C:\Ziggie\coordinator",
    "C:\Ziggie\integration-logs"
)

$archiveDir = "C:\Ziggie\log-archives"
$retentionDays = 30
$archiveAfterDays = 7

# Create archive directory
New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd"

foreach ($dir in $logDirs) {
    if (-not (Test-Path $dir)) { continue }

    # Archive old logs (> 7 days)
    Get-ChildItem -Path $dir -Filter "*.log" -File |
        Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$archiveAfterDays) } |
        ForEach-Object {
            $archivePath = "$archiveDir\$($_.BaseName)_$timestamp.log.gz"
            # Compress and move
            Compress-Archive -Path $_.FullName -DestinationPath $archivePath -Force
            Remove-Item $_.FullName -Force
            Write-Host "Archived: $($_.Name)"
        }

    # Delete very old logs (> 30 days)
    Get-ChildItem -Path $archiveDir -Filter "*.gz" -File |
        Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$retentionDays) } |
        ForEach-Object {
            Remove-Item $_.FullName -Force
            Write-Host "Deleted: $($_.Name)"
        }
}

Write-Host "Log rotation complete"
```

---

# APPENDIX N: UPGRADE PATHS

## N.1 Component Upgrade Matrix

| Component | Current Check | Upgrade Command | Rollback |
|-----------|---------------|-----------------|----------|
| Python | `python --version` | Install from python.org | Keep old version in PATH |
| Node.js | `node --version` | Install from nodejs.org | nvm use <old_version> |
| npm packages | `npm outdated` | `npm update` | `npm install <pkg>@<version>` |
| pip packages | `pip list --outdated` | `pip install -U <pkg>` | `pip install <pkg>==<version>` |
| Claude Code | Check VS Code extensions | Update via VS Code | Reinstall previous version |
| MCP servers | Check git log | `git pull` | `git checkout <commit>` |

## N.2 Safe Upgrade Procedure

```powershell
# ============================================================
# SAFE UPGRADE PROCEDURE
# Save as: C:\Ziggie\scripts\safe_upgrade.ps1
# ============================================================

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("pip","npm","mcp")]
    [string]$Component,

    [Parameter(Mandatory=$true)]
    [string]$Package,

    [string]$Version = "latest"
)

Write-Host "=== SAFE UPGRADE PROCEDURE ===" -ForegroundColor Cyan

# Step 1: Create backup
Write-Host "`n1. Creating backup..." -ForegroundColor Yellow
$backupDir = "C:\Ziggie\upgrade-backups\$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

# Backup current state
switch ($Component) {
    "pip" {
        pip freeze > "$backupDir\requirements.txt"
        $currentVersion = (pip show $Package 2>&1) -match "Version:" | ForEach-Object { $_.Split(":")[1].Trim() }
    }
    "npm" {
        npm list --json > "$backupDir\npm_packages.json"
        $currentVersion = (npm list $Package --json 2>&1 | ConvertFrom-Json).dependencies.$Package.version
    }
    "mcp" {
        Copy-Item "C:\Ziggie\.mcp.json" "$backupDir\.mcp.json"
        $currentVersion = "N/A"
    }
}

Write-Host "Current version: $currentVersion"
Write-Host "Backup created: $backupDir"

# Step 2: Run pre-upgrade tests
Write-Host "`n2. Running pre-upgrade tests..." -ForegroundColor Yellow
& "C:\Ziggie\scripts\run_integration_tests.ps1"
$preTestResult = $LASTEXITCODE

if ($preTestResult -ne 0) {
    Write-Host "Pre-upgrade tests failed. Aborting." -ForegroundColor Red
    exit 1
}

# Step 3: Perform upgrade
Write-Host "`n3. Performing upgrade..." -ForegroundColor Yellow
switch ($Component) {
    "pip" {
        if ($Version -eq "latest") {
            pip install -U $Package
        } else {
            pip install "$Package==$Version"
        }
    }
    "npm" {
        if ($Version -eq "latest") {
            npm update $Package
        } else {
            npm install "$Package@$Version"
        }
    }
}

# Step 4: Run post-upgrade tests
Write-Host "`n4. Running post-upgrade tests..." -ForegroundColor Yellow
& "C:\Ziggie\scripts\run_integration_tests.ps1"
$postTestResult = $LASTEXITCODE

if ($postTestResult -ne 0) {
    Write-Host "Post-upgrade tests failed. Rolling back..." -ForegroundColor Red

    # Rollback
    switch ($Component) {
        "pip" {
            pip install "$Package==$currentVersion"
        }
        "npm" {
            npm install "$Package@$currentVersion"
        }
        "mcp" {
            Copy-Item "$backupDir\.mcp.json" "C:\Ziggie\.mcp.json" -Force
        }
    }

    Write-Host "Rollback complete" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n=== UPGRADE SUCCESSFUL ===" -ForegroundColor Green
Write-Host "Upgraded: $Package"
Write-Host "From: $currentVersion"
Write-Host "To: $(if ($Version -eq 'latest') { 'latest' } else { $Version })"
```

---

# APPENDIX O: DISASTER RECOVERY

## O.1 Disaster Recovery Plan

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                       DISASTER RECOVERY PLAN                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║ SEVERITY LEVELS:                                                              ║
║   LEVEL 1 (Low)   : Single MCP not responding                                 ║
║   LEVEL 2 (Medium): Multiple MCPs failing, degraded functionality             ║
║   LEVEL 3 (High)  : Claude Code not starting, full integration failure        ║
║   LEVEL 4 (Critical): Data loss, corrupted configurations                     ║
║                                                                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║ LEVEL 1 RECOVERY (5-10 minutes):                                              ║
║   1. Identify failing MCP from error messages                                 ║
║   2. Check MCP service status (port check)                                    ║
║   3. Restart specific MCP service                                             ║
║   4. If still failing, remove from .mcp.json temporarily                      ║
║   5. Document issue for investigation                                         ║
║                                                                               ║
║ LEVEL 2 RECOVERY (15-30 minutes):                                             ║
║   1. Stop all non-essential MCPs                                              ║
║   2. Restart Claude Code                                                      ║
║   3. Add MCPs back one at a time                                              ║
║   4. Identify which MCP causes conflict                                       ║
║   5. Review logs for root cause                                               ║
║                                                                               ║
║ LEVEL 3 RECOVERY (30-60 minutes):                                             ║
║   1. Close Claude Code completely                                             ║
║   2. Restore .mcp.json from backup:                                           ║
║      Copy-Item .mcp.json.backup .mcp.json -Force                              ║
║   3. Restart Claude Code with minimal config                                  ║
║   4. Verify basic functionality                                               ║
║   5. Gradually restore configuration                                          ║
║                                                                               ║
║ LEVEL 4 RECOVERY (1-4 hours):                                                 ║
║   1. Document current state completely                                        ║
║   2. Restore from most recent known-good backup                               ║
║   3. Re-run integration stages from last checkpoint                           ║
║   4. Rebuild memory graph from scratch if needed                              ║
║   5. Full integration test suite                                              ║
║   6. Post-mortem analysis                                                     ║
║                                                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## O.2 Emergency Recovery Script

```powershell
# ============================================================
# EMERGENCY RECOVERY SCRIPT
# Save as: C:\Ziggie\scripts\emergency_recovery.ps1
# Usage: .\emergency_recovery.ps1 -Level <1-4>
# ============================================================

param(
    [Parameter(Mandatory=$true)]
    [ValidateRange(1,4)]
    [int]$Level
)

Write-Host @"
╔══════════════════════════════════════════════════════════════════╗
║           EMERGENCY RECOVERY - LEVEL $Level                           ║
╚══════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Red

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$recoveryLog = "C:\Ziggie\integration-logs\recovery_$timestamp.log"

function Log-Recovery {
    param([string]$Message)
    $logEntry = "[$(Get-Date -Format 'HH:mm:ss')] $Message"
    Write-Host $logEntry
    Add-Content -Path $recoveryLog -Value $logEntry
}

Log-Recovery "Starting Level $Level recovery"

switch ($Level) {
    1 {
        Log-Recovery "LEVEL 1: Single MCP Recovery"

        # Check all port statuses
        $ports = @{8080="Unity"; 8081="Unreal"; 8188="ComfyUI"; 6005="Godot"; 1234="LocalLLM"}
        foreach ($port in $ports.Keys) {
            $status = netstat -an | Select-String ":$port.*LISTENING"
            if (-not $status) {
                Log-Recovery "Port $port ($($ports[$port])): NOT RESPONDING"
            }
        }

        Log-Recovery "Review output above and restart failing services"
    }

    2 {
        Log-Recovery "LEVEL 2: Multi-MCP Recovery"

        # Create minimal config
        $minimalConfig = @{
            mcpServers = @{
                filesystem = @{
                    command = "cmd"
                    args = @("/c", "npx", "-y", "@modelcontextprotocol/server-filesystem", "C:/Ziggie")
                }
            }
        }

        # Backup current
        Copy-Item "C:\Ziggie\.mcp.json" "C:\Ziggie\.mcp.json.pre_recovery_$timestamp"

        # Write minimal config
        $minimalConfig | ConvertTo-Json -Depth 10 | Set-Content "C:\Ziggie\.mcp.json"

        Log-Recovery "Minimal config written. RESTART CLAUDE CODE NOW"
        Log-Recovery "Original config backed up to .mcp.json.pre_recovery_$timestamp"
    }

    3 {
        Log-Recovery "LEVEL 3: Full Config Recovery"

        # Find most recent backup
        $backups = Get-ChildItem "C:\Ziggie\.mcp.json.backup*" | Sort-Object LastWriteTime -Descending

        if ($backups) {
            $latestBackup = $backups[0]
            Log-Recovery "Restoring from: $($latestBackup.Name)"

            # Backup current broken config
            Copy-Item "C:\Ziggie\.mcp.json" "C:\Ziggie\.mcp.json.broken_$timestamp"

            # Restore
            Copy-Item $latestBackup.FullName "C:\Ziggie\.mcp.json" -Force

            Log-Recovery "Config restored. RESTART CLAUDE CODE NOW"
        } else {
            Log-Recovery "ERROR: No backup found!"
            Log-Recovery "Creating minimal config instead"

            # Fall back to Level 2 procedure
            & $PSCommandPath -Level 2
        }
    }

    4 {
        Log-Recovery "LEVEL 4: Full System Recovery"
        Log-Recovery "This requires manual intervention"

        Write-Host @"

CRITICAL RECOVERY STEPS:
========================

1. Document the failure:
   - Screenshot any error messages
   - Copy all logs to safe location
   - Note what actions led to failure

2. Restore from backup:
   - Locate most recent working backup
   - Restore C:\Ziggie\.mcp.json
   - Consider full directory restore if needed

3. Re-run integration:
   - Start from Stage 0
   - Verify each gate before proceeding
   - Stop at first failure

4. Rebuild if necessary:
   - Memory graph may need full rebuild
   - Re-run mcp__memory__create_entities
   - Verify all entities and relations

5. Post-mortem:
   - Document root cause
   - Update disaster recovery procedures
   - Add additional safeguards

"@ -ForegroundColor Yellow
    }
}

Log-Recovery "Recovery procedure complete"
Write-Host "`nRecovery log saved to: $recoveryLog" -ForegroundColor Cyan
```

---

# APPENDIX P: TEAM HANDOFF DOCUMENTATION

## P.1 Handoff Checklist

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                       TEAM HANDOFF CHECKLIST                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║ DOCUMENTATION PROVIDED:                                                       ║
║ [ ] CLAUDE-CODE-INTEGRATION-PLAN.md - Full integration guide                  ║
║ [ ] ZIGGIE-ECOSYSTEM-MASTER-STATUS-V2.md - Current system state               ║
║ [ ] .mcp.json - Current MCP configuration                                     ║
║ [ ] All scripts in C:\Ziggie\scripts\                                         ║
║                                                                               ║
║ ACCESS VERIFIED:                                                              ║
║ [ ] Local machine access (admin if needed)                                    ║
║ [ ] Environment variables set (ANTHROPIC_API_KEY)                             ║
║ [ ] Git access to repositories                                                ║
║ [ ] VPS access (if applicable)                                                ║
║                                                                               ║
║ KNOWLEDGE TRANSFER:                                                           ║
║ [ ] Integration architecture explained                                        ║
║ [ ] Current integration status reviewed                                       ║
║ [ ] Known issues documented                                                   ║
║ [ ] Troubleshooting procedures reviewed                                       ║
║ [ ] Emergency contacts provided                                               ║
║                                                                               ║
║ PRACTICAL WALKTHROUGH:                                                        ║
║ [ ] Run health check together                                                 ║
║ [ ] Deploy a test agent together                                              ║
║ [ ] Demonstrate MCP tool usage                                                ║
║ [ ] Show monitoring dashboard                                                 ║
║ [ ] Practice a rollback procedure                                             ║
║                                                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## P.2 Quick Reference Card

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ZIGGIE INTEGRATION QUICK REFERENCE                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║ COMMON COMMANDS:                                                              ║
║   Health Check     : .\scripts\health_check.ps1                               ║
║   Run Tests        : .\scripts\run_integration_tests.ps1                      ║
║   Monitor Dashboard: .\scripts\monitor_dashboard.ps1                          ║
║   Start Coordinator: python -m coordinator.main                               ║
║   Deploy Agent     : python coordinator/client.py deploy --agent X --task "Y" ║
║                                                                               ║
║ KEY FILES:                                                                    ║
║   MCP Config       : C:\Ziggie\.mcp.json                                      ║
║   Integration Plan : C:\Ziggie\CLAUDE-CODE-INTEGRATION-PLAN.md                ║
║   Master Status    : C:\Ziggie\ZIGGIE-ECOSYSTEM-MASTER-STATUS-V2.md           ║
║   Backup Config    : C:\Ziggie\.mcp.json.backup                               ║
║                                                                               ║
║ EMERGENCY PROCEDURES:                                                         ║
║   Quick Rollback   : Copy-Item .mcp.json.backup .mcp.json -Force              ║
║   Full Recovery    : .\scripts\emergency_recovery.ps1 -Level 3                ║
║   View Logs        : Get-Content .\integration-logs\*.log -Tail 50            ║
║                                                                               ║
║ PORT REFERENCE:                                                               ║
║   8080  : Unity MCP         8081  : Unreal MCP                                ║
║   8188  : ComfyUI           6005  : Godot MCP                                 ║
║   1234  : LocalLLM          5678  : n8n                                       ║
║   3001  : Sim Studio                                                          ║
║                                                                               ║
║ ESCALATION:                                                                   ║
║   Level 1-2 : Self-service using documentation                                ║
║   Level 3   : Contact: [Your contact info]                                    ║
║   Level 4   : Contact: [Emergency contact]                                    ║
║                                                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

# APPENDIX Q: VERSION CONTROL STRATEGY

## Q.1 Configuration Version Control

```powershell
# ============================================================
# CONFIGURATION VERSION CONTROL
# Save as: C:\Ziggie\scripts\version_config.ps1
# ============================================================

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("save","list","restore","diff")]
    [string]$Action,

    [string]$Version,
    [string]$Message = ""
)

$configDir = "C:\Ziggie\config-versions"
$mcpJson = "C:\Ziggie\.mcp.json"

# Ensure version directory exists
New-Item -ItemType Directory -Path $configDir -Force | Out-Null

switch ($Action) {
    "save" {
        # Create version
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $versionFile = "$configDir\mcp_v$timestamp.json"
        $metaFile = "$configDir\mcp_v$timestamp.meta"

        # Copy config
        Copy-Item $mcpJson $versionFile

        # Create metadata
        @{
            Version = $timestamp
            Message = $Message
            Created = (Get-Date -Format "o")
            Hash = (Get-FileHash $mcpJson).Hash
        } | ConvertTo-Json | Set-Content $metaFile

        Write-Host "Version saved: v$timestamp" -ForegroundColor Green
        if ($Message) { Write-Host "Message: $Message" }
    }

    "list" {
        Write-Host "=== SAVED VERSIONS ===" -ForegroundColor Cyan
        Get-ChildItem "$configDir\*.meta" | ForEach-Object {
            $meta = Get-Content $_.FullName | ConvertFrom-Json
            Write-Host "v$($meta.Version) - $($meta.Message)" -ForegroundColor Yellow
            Write-Host "  Created: $($meta.Created)"
        }
    }

    "restore" {
        if (-not $Version) {
            Write-Host "Specify version with -Version parameter" -ForegroundColor Red
            exit 1
        }

        $versionFile = "$configDir\mcp_v$Version.json"
        if (-not (Test-Path $versionFile)) {
            Write-Host "Version not found: v$Version" -ForegroundColor Red
            exit 1
        }

        # Backup current
        $backup = "$configDir\mcp_pre_restore_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
        Copy-Item $mcpJson $backup

        # Restore
        Copy-Item $versionFile $mcpJson -Force

        Write-Host "Restored v$Version" -ForegroundColor Green
        Write-Host "Previous config backed up to: $backup"
    }

    "diff" {
        if (-not $Version) {
            Write-Host "Specify version with -Version parameter" -ForegroundColor Red
            exit 1
        }

        $versionFile = "$configDir\mcp_v$Version.json"
        if (-not (Test-Path $versionFile)) {
            Write-Host "Version not found: v$Version" -ForegroundColor Red
            exit 1
        }

        # Simple diff
        $current = Get-Content $mcpJson
        $saved = Get-Content $versionFile

        Compare-Object $saved $current -SyncWindow 0 | ForEach-Object {
            if ($_.SideIndicator -eq "<=") {
                Write-Host "- $($_.InputObject)" -ForegroundColor Red
            } else {
                Write-Host "+ $($_.InputObject)" -ForegroundColor Green
            }
        }
    }
}
```

## Q.2 Git Integration for Configurations

```powershell
# ============================================================
# GIT INTEGRATION FOR CONFIGURATIONS
# Save as: C:\Ziggie\scripts\git_config.ps1
# ============================================================

# Initialize git for config tracking
if (-not (Test-Path "C:\Ziggie\.git")) {
    Set-Location "C:\Ziggie"
    git init

    # Create .gitignore
    @"
# Ignore sensitive files
*.backup
*.log
*.tmp
agent-deployment/responses/
integration-logs/

# Track configs
!.mcp.json
!*.md
"@ | Set-Content ".gitignore"

    git add .gitignore .mcp.json *.md
    git commit -m "Initial configuration tracking"

    Write-Host "Git repository initialized for config tracking" -ForegroundColor Green
} else {
    Write-Host "Git already initialized" -ForegroundColor Yellow
}

# Add current state
git add -A
$changes = git status --porcelain

if ($changes) {
    Write-Host "Changes detected:" -ForegroundColor Yellow
    Write-Host $changes

    $message = Read-Host "Commit message (or Enter to skip)"
    if ($message) {
        git commit -m $message
        Write-Host "Changes committed" -ForegroundColor Green
    }
} else {
    Write-Host "No changes to commit" -ForegroundColor Green
}
```

---

**END OF INTEGRATION PLAN**
