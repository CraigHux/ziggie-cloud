#!/usr/bin/env python3
"""
ZIGGIE MEMORY GRAPH POPULATION SCRIPT
=====================================
Populates the Memory MCP knowledge graph with all Ziggie ecosystem entities.

Target: 75+ entities, 50+ relations
Categories:
  - 5 Project entities
  - 15 Infrastructure entities
  - 20 Agent entities
  - 10 Documentation entities
  - 5 Service entities
  - 20+ additional entities (tools, workflows, integrations)
  - 50+ Relations

Usage:
  python populate_memory_graph.py [--verify] [--export]

Note: This script generates JSON payloads for the Memory MCP.
      Execute via Claude Code using mcp__memory__* tools.
"""

import json
import sys
from datetime import datetime
from typing import TypedDict, List

# =============================================================================
# TYPE DEFINITIONS
# =============================================================================

class Entity(TypedDict):
    name: str
    entityType: str
    observations: List[str]

class Relation(TypedDict):
    from_: str  # 'from' is reserved in Python
    to: str
    relationType: str

# =============================================================================
# PROJECT ENTITIES (5)
# =============================================================================

PROJECT_ENTITIES: List[Entity] = [
    {
        "name": "Ziggie-Ecosystem",
        "entityType": "Project",
        "observations": [
            "Master AI development ecosystem coordinating multiple sub-projects",
            "Contains: MeowPing-RTS, AI-Game-Dev-System, Team-Ziggie agents",
            "Primary location: C:/Ziggie",
            "Uses MCP Hub architecture for tool integration",
            "Production VPS: ziggie.cloud (167.71.48.117)",
            "Status: Active development, 14 sprints completed"
        ]
    },
    {
        "name": "MeowPing-RTS",
        "entityType": "Project",
        "observations": [
            "Real-time strategy game with cat faction theme",
            "Frontend: React TypeScript at C:/Ziggie/frontend",
            "Backend: FastAPI at C:/Ziggie/backend (port 54112)",
            "WebSocket server for real-time multiplayer",
            "Asset generation via ComfyUI and ImagineArt automation",
            "Current phase: AAA Visual Upgrade with AI-generated assets"
        ]
    },
    {
        "name": "AI-Game-Dev-System",
        "entityType": "Project",
        "observations": [
            "Multi-engine AI game development framework",
            "Supports: Unity, Unreal, Godot, Blender, ComfyUI",
            "MCP servers for each engine integration",
            "Location: C:/ai-game-dev-system",
            "Pipeline: Concept Art -> 2D Assets -> 3D Models -> Sprites"
        ]
    },
    {
        "name": "Team-Ziggie",
        "entityType": "Project",
        "observations": [
            "AI agent team organization system",
            "15 Elite agents across 5 specialized teams",
            "L1-L3 agent hierarchy for task distribution",
            "Coordinator: C:/Ziggie/coordinator",
            "Agent skills defined in C:/Ziggie/skills"
        ]
    },
    {
        "name": "VPS-Production",
        "entityType": "Project",
        "observations": [
            "Production deployment on DigitalOcean VPS",
            "Domain: ziggie.cloud",
            "IP: 167.71.48.117",
            "Services: Nginx reverse proxy, Docker containers",
            "Monitoring: Health endpoints, resource tracking"
        ]
    }
]

# =============================================================================
# INFRASTRUCTURE ENTITIES (15)
# =============================================================================

INFRASTRUCTURE_ENTITIES: List[Entity] = [
    {
        "name": "MCP-Memory",
        "entityType": "MCP-Server",
        "observations": [
            "Knowledge graph storage using file-based JSON",
            "Command: npx -y @anthropic/mcp-memory",
            "Environment: MEMORY_FILE_PATH=C:/Ziggie/memory-bank/memory.json",
            "Status: Active - Core integration",
            "Capabilities: Entity CRUD, relation management, graph search"
        ]
    },
    {
        "name": "MCP-Filesystem",
        "entityType": "MCP-Server",
        "observations": [
            "File operations across allowed directories",
            "Command: npx -y @anthropic/mcp-filesystem",
            "Allowed paths: C:/Ziggie, C:/ai-game-dev-system",
            "Status: Active - Core integration",
            "Capabilities: read, write, list, search files"
        ]
    },
    {
        "name": "MCP-Chrome-DevTools",
        "entityType": "MCP-Server",
        "observations": [
            "Browser automation via Chrome DevTools Protocol",
            "Command: npx -y chrome-devtools-mcp@latest",
            "Status: Active - Core integration",
            "Capabilities: Navigation, screenshots, DOM interaction",
            "Use case: ImagineArt automation, web testing"
        ]
    },
    {
        "name": "MCP-ComfyUI",
        "entityType": "MCP-Server",
        "observations": [
            "AI image generation workflow automation",
            "Location: C:/ComfyUI/mcp-servers/comfyui-mcp",
            "Port: 8188 (ComfyUI server)",
            "Status: Available - Pending integration",
            "Capabilities: Workflow execution, image generation, model management"
        ]
    },
    {
        "name": "MCP-Unity",
        "entityType": "MCP-Server",
        "observations": [
            "Unity Editor integration via HTTP transport",
            "URL: http://localhost:8080/mcp",
            "Status: Available - Pending integration",
            "Capabilities: Scene manipulation, asset management, build automation"
        ]
    },
    {
        "name": "MCP-Unreal",
        "entityType": "MCP-Server",
        "observations": [
            "Unreal Engine 5 integration via Python",
            "Transport: stdio via uv",
            "Status: Available - Pending integration",
            "Capabilities: Blueprint scripting, level design, packaging"
        ]
    },
    {
        "name": "MCP-Godot",
        "entityType": "MCP-Server",
        "observations": [
            "Godot 4.x integration via Node.js",
            "Transport: stdio",
            "Status: Available - Pending integration",
            "Capabilities: GDScript execution, scene management"
        ]
    },
    {
        "name": "MCP-SimStudio",
        "entityType": "MCP-Server",
        "observations": [
            "Blender-based 3D asset pipeline",
            "Location: C:/ai-game-dev-system/mcp-servers/sim-studio-mcp",
            "Status: Planned - Future integration",
            "Capabilities: 3D modeling, rigging, animation, rendering"
        ]
    },
    {
        "name": "MCP-LocalLLM",
        "entityType": "MCP-Server",
        "observations": [
            "Local LLM inference via Ollama",
            "Port: 11434 (Ollama server)",
            "Status: Planned - Future integration",
            "Capabilities: Text generation, code completion, embeddings"
        ]
    },
    {
        "name": "MCP-n8n",
        "entityType": "MCP-Server",
        "observations": [
            "Workflow automation server",
            "Port: 5678",
            "Status: Planned - Future integration",
            "Capabilities: Workflow triggers, API orchestration"
        ]
    },
    {
        "name": "Backend-FastAPI",
        "entityType": "Service",
        "observations": [
            "MeowPing game backend server",
            "Location: C:/Ziggie/backend",
            "Port: 54112",
            "Entry: main.py with uvicorn",
            "Features: REST API, WebSocket, SQLite database"
        ]
    },
    {
        "name": "Frontend-React",
        "entityType": "Service",
        "observations": [
            "MeowPing game frontend",
            "Location: C:/Ziggie/frontend",
            "Port: 3000 (dev)",
            "Tech: React, TypeScript, Vite",
            "Features: Game UI, real-time updates, asset display"
        ]
    },
    {
        "name": "VPS-DigitalOcean",
        "entityType": "Infrastructure",
        "observations": [
            "Production server hosting",
            "IP: 167.71.48.117",
            "Region: Frankfurt",
            "OS: Ubuntu 22.04",
            "Access: SSH key-based authentication"
        ]
    },
    {
        "name": "Database-SQLite",
        "entityType": "Database",
        "observations": [
            "Local development database",
            "Location: C:/Ziggie/backend/ziggie.db",
            "Tables: users, games, assets, settings",
            "Status: Active for development"
        ]
    },
    {
        "name": "Memory-Bank",
        "entityType": "Storage",
        "observations": [
            "Persistent knowledge storage",
            "Location: C:/Ziggie/memory-bank",
            "Files: memory.json, context files",
            "Used by: Memory MCP, agent coordination"
        ]
    }
]

# =============================================================================
# AGENT ENTITIES (20)
# =============================================================================

AGENT_ENTITIES: List[Entity] = [
    # Elite Art Team (4)
    {
        "name": "ARTEMIS",
        "entityType": "Elite-Agent",
        "observations": [
            "Elite Art Team - Visual Direction Lead",
            "Specialization: Art direction, style guides, visual consistency",
            "Team: Elite Art Team",
            "Invoke: /elite-art-team"
        ]
    },
    {
        "name": "LEONIDAS",
        "entityType": "Elite-Agent",
        "observations": [
            "Elite Art Team - Character Design Lead",
            "Specialization: Character concepts, unit design, faction identity",
            "Team: Elite Art Team",
            "Invoke: /elite-art-team"
        ]
    },
    {
        "name": "GAIA",
        "entityType": "Elite-Agent",
        "observations": [
            "Elite Art Team - Environment Design Lead",
            "Specialization: Terrain, buildings, biome design",
            "Team: Elite Art Team",
            "Invoke: /elite-art-team"
        ]
    },
    {
        "name": "VULCAN",
        "entityType": "Elite-Agent",
        "observations": [
            "Elite Art Team - VFX Lead",
            "Specialization: Visual effects, particles, animations",
            "Team: Elite Art Team",
            "Invoke: /elite-art-team"
        ]
    },
    # Elite Design Team (4)
    {
        "name": "TERRA",
        "entityType": "Elite-Agent",
        "observations": [
            "Elite Design Team - Level Design Lead",
            "Specialization: Map layouts, terrain flow, strategic zones",
            "Team: Elite Design Team",
            "Invoke: /elite-design-team"
        ]
    },
    {
        "name": "PROMETHEUS",
        "entityType": "Elite-Agent",
        "observations": [
            "Elite Design Team - Game Balance Lead",
            "Specialization: Unit stats, economy, matchups",
            "Team: Elite Design Team",
            "Invoke: /elite-design-team"
        ]
    },
    {
        "name": "IRIS",
        "entityType": "Elite-Agent",
        "observations": [
            "Elite Design Team - UI/UX Lead",
            "Specialization: Interface design, player experience",
            "Team: Elite Design Team",
            "Invoke: /elite-design-team"
        ]
    },
    {
        "name": "MYTHOS",
        "entityType": "Elite-Agent",
        "observations": [
            "Elite Design Team - Narrative Lead",
            "Specialization: Lore, faction stories, campaign",
            "Team: Elite Design Team",
            "Invoke: /elite-design-team"
        ]
    },
    # Elite Technical Team (3)
    {
        "name": "HEPHAESTUS",
        "entityType": "Elite-Agent",
        "observations": [
            "Elite Technical Team - Optimization Lead",
            "Specialization: Performance, profiling, asset optimization",
            "Team: Elite Technical Team",
            "Invoke: /elite-technical-team"
        ]
    },
    {
        "name": "DAEDALUS",
        "entityType": "Elite-Agent",
        "observations": [
            "Elite Technical Team - Pipeline Automation Lead",
            "Specialization: Build automation, CI/CD, tooling",
            "Team: Elite Technical Team",
            "Invoke: /elite-technical-team"
        ]
    },
    {
        "name": "ARGUS",
        "entityType": "Elite-Agent",
        "observations": [
            "Elite Technical Team - QA Lead",
            "Specialization: Testing, quality assurance, bug tracking",
            "Team: Elite Technical Team",
            "Invoke: /elite-technical-team"
        ]
    },
    # Elite Production Team (3)
    {
        "name": "MAXIMUS",
        "entityType": "Elite-Agent",
        "observations": [
            "Elite Production Team - Executive Strategy Lead",
            "Specialization: Project strategy, roadmap, priorities",
            "Team: Elite Production Team",
            "Invoke: /elite-production-team"
        ]
    },
    {
        "name": "FORGE",
        "entityType": "Elite-Agent",
        "observations": [
            "Elite Production Team - Risk Management Lead",
            "Specialization: Risk assessment, mitigation, contingencies",
            "Team: Elite Production Team",
            "Invoke: /elite-production-team"
        ]
    },
    {
        "name": "ATLAS",
        "entityType": "Elite-Agent",
        "observations": [
            "Elite Production Team - Asset Pipeline Velocity Lead",
            "Specialization: Asset throughput, bottleneck resolution",
            "Team: Elite Production Team",
            "Invoke: /elite-production-team"
        ]
    },
    # L1 Architecture Agents (3)
    {
        "name": "L1-Architect-Backend",
        "entityType": "L1-Agent",
        "observations": [
            "Level 1 Architecture Agent - Backend Focus",
            "Location: C:/Ziggie/agents/l1_architecture",
            "Responsibilities: API design, database schema, service architecture"
        ]
    },
    {
        "name": "L1-Architect-Frontend",
        "entityType": "L1-Agent",
        "observations": [
            "Level 1 Architecture Agent - Frontend Focus",
            "Location: C:/Ziggie/agents/l1_architecture",
            "Responsibilities: Component architecture, state management, UI patterns"
        ]
    },
    {
        "name": "L1-Architect-Integration",
        "entityType": "L1-Agent",
        "observations": [
            "Level 1 Architecture Agent - Integration Focus",
            "Location: C:/Ziggie/agents/l1_architecture",
            "Responsibilities: MCP integration, cross-system communication"
        ]
    },
    # L2/L3 Agents (3)
    {
        "name": "L2-Implementer",
        "entityType": "L2-Agent",
        "observations": [
            "Level 2 Implementation Agent",
            "Receives tasks from L1 architects",
            "Executes specific implementation work",
            "Reports progress to coordinator"
        ]
    },
    {
        "name": "L3-Specialist",
        "entityType": "L3-Agent",
        "observations": [
            "Level 3 Specialist Agent",
            "Handles specialized tasks delegated by L2",
            "Focus: Specific technical domains",
            "Examples: ComfyUI workflows, shader coding"
        ]
    },
    {
        "name": "Overwatch",
        "entityType": "Coordinator-Agent",
        "observations": [
            "System-wide monitoring and coordination agent",
            "Location: C:/Ziggie/agents/overwatch",
            "Responsibilities: Health checks, task distribution, status aggregation",
            "Memory log: C:/Ziggie/agents/overwatch/overwatch_memory_log.md"
        ]
    }
]

# =============================================================================
# DOCUMENTATION ENTITIES (10)
# =============================================================================

DOCUMENTATION_ENTITIES: List[Entity] = [
    {
        "name": "ZIGGIE-ECOSYSTEM-MASTER-STATUS-V2",
        "entityType": "Documentation",
        "observations": [
            "Master ecosystem status document",
            "Location: C:/Ziggie/ZIGGIE-ECOSYSTEM-MASTER-STATUS-V2.md",
            "Sections: 10 major sections covering all systems",
            "Update frequency: Per major milestone"
        ]
    },
    {
        "name": "CLAUDE-CODE-INTEGRATION-PLAN",
        "entityType": "Documentation",
        "observations": [
            "7-Stage Claude Code integration plan",
            "Location: C:/Ziggie/CLAUDE-CODE-INTEGRATION-PLAN.md",
            "Contains: 28 phases, 7 quality gates, 100+ tasks",
            "Status: Active execution document"
        ]
    },
    {
        "name": "INTEGRATION-TASK-DEPENDENCY-GRAPH",
        "entityType": "Documentation",
        "observations": [
            "Task dependency mapping for integration",
            "Location: C:/Ziggie/INTEGRATION-TASK-DEPENDENCY-GRAPH.md",
            "Contains: Critical path, blocking tasks, parallelization opportunities"
        ]
    },
    {
        "name": "INTEGRATION-ROLLBACK-PLAYBOOK",
        "entityType": "Documentation",
        "observations": [
            "Rollback procedures for each integration stage",
            "Location: C:/Ziggie/INTEGRATION-ROLLBACK-PLAYBOOK.md",
            "Contains: Decision tree, stage-specific scripts, recovery verification"
        ]
    },
    {
        "name": "INTEGRATION-AWS-STAGE",
        "entityType": "Documentation",
        "observations": [
            "AWS integration stage 7.5",
            "Location: C:/Ziggie/INTEGRATION-AWS-STAGE.md",
            "Contains: S3, Secrets Manager, Lambda, EC2 Spot, Bedrock integration"
        ]
    },
    {
        "name": "CLAUDE-MD-Global",
        "entityType": "Documentation",
        "observations": [
            "Global Claude instructions (CLAUDE.md)",
            "Location: C:/Users/minin/.claude/CLAUDE.md",
            "Contains: Core principles, sprint methodology, technical lessons"
        ]
    },
    {
        "name": "MCP-Configuration",
        "entityType": "Configuration",
        "observations": [
            "MCP server configuration file",
            "Location: C:/Ziggie/.mcp.json",
            "Defines: Active MCP servers, environment variables, args"
        ]
    },
    {
        "name": "Knowledge-Base-Index",
        "entityType": "Documentation",
        "observations": [
            "Master index for knowledge base",
            "Location: C:/Ziggie/knowledge-base/MASTER-INDEX.md",
            "Contains: Navigation hub for all knowledge documents"
        ]
    },
    {
        "name": "Sprint-Retrospectives",
        "entityType": "Documentation",
        "observations": [
            "Sprint retrospective collection",
            "14 sprints documented",
            "Contains: Lessons learned, metrics, technical patterns"
        ]
    },
    {
        "name": "Agent-Skills-Directory",
        "entityType": "Documentation",
        "observations": [
            "Directory of agent skill definitions",
            "Location: C:/Ziggie/skills",
            "Contains: Skill prompts for elite teams, game asset generation"
        ]
    }
]

# =============================================================================
# SERVICE ENTITIES (5)
# =============================================================================

SERVICE_ENTITIES: List[Entity] = [
    {
        "name": "ComfyUI-Server",
        "entityType": "External-Service",
        "observations": [
            "AI image generation server",
            "URL: http://127.0.0.1:8188",
            "Location: C:/ComfyUI",
            "Models: SDXL, ControlNet, LoRA",
            "Use: Asset generation, texture creation"
        ]
    },
    {
        "name": "Ollama-Server",
        "entityType": "External-Service",
        "observations": [
            "Local LLM inference server",
            "URL: http://127.0.0.1:11434",
            "Models: llama3.3, codellama, mistral",
            "Use: Code generation, text processing"
        ]
    },
    {
        "name": "ImagineArt-Service",
        "entityType": "External-Service",
        "observations": [
            "Cloud AI art generation",
            "URL: https://imagineart.ai",
            "Access: Browser automation via Playwright",
            "Use: Concept art, game assets (unlimited free tier)"
        ]
    },
    {
        "name": "Meshy-AI-Service",
        "entityType": "External-Service",
        "observations": [
            "Cloud image-to-3D conversion",
            "API: https://api.meshy.ai",
            "Tier: 200 free/month",
            "Use: 2D to 3D model conversion"
        ]
    },
    {
        "name": "GitHub-Repository",
        "entityType": "External-Service",
        "observations": [
            "Version control hosting",
            "Organization: Multiple repos for Ziggie ecosystem",
            "Features: Issues, PRs, Actions",
            "Access: gh CLI configured"
        ]
    }
]

# =============================================================================
# TOOL ENTITIES (10)
# =============================================================================

TOOL_ENTITIES: List[Entity] = [
    {
        "name": "Blender",
        "entityType": "Tool",
        "observations": [
            "3D modeling and rendering software",
            "Version: 4.2+",
            "Location: C:/Program Files/Blender Foundation/Blender 4.2",
            "Use: 3D modeling, rigging, 8-direction sprite rendering"
        ]
    },
    {
        "name": "Python",
        "entityType": "Tool",
        "observations": [
            "Primary scripting language",
            "Version: 3.11+",
            "Package manager: pip, uv",
            "Use: Backend, automation, AI pipelines"
        ]
    },
    {
        "name": "Node-JS",
        "entityType": "Tool",
        "observations": [
            "JavaScript runtime",
            "Version: 20+",
            "Package manager: npm",
            "Use: MCP servers, frontend tooling"
        ]
    },
    {
        "name": "PowerShell-7",
        "entityType": "Tool",
        "observations": [
            "Windows automation shell",
            "Version: 7.x",
            "Profile: Lazy-loaded for fast startup",
            "Use: Scripts, verification, deployment"
        ]
    },
    {
        "name": "Git",
        "entityType": "Tool",
        "observations": [
            "Version control system",
            "LFS enabled for game assets",
            "Use: Code versioning, collaboration"
        ]
    },
    {
        "name": "Docker",
        "entityType": "Tool",
        "observations": [
            "Container platform",
            "Use: Service isolation, deployment",
            "Compose: Multi-container orchestration"
        ]
    },
    {
        "name": "VSCode",
        "entityType": "Tool",
        "observations": [
            "Primary IDE",
            "Extensions: Claude Code, Python, TypeScript",
            "Use: Development, debugging, Claude integration"
        ]
    },
    {
        "name": "Playwright",
        "entityType": "Tool",
        "observations": [
            "Browser automation framework",
            "Use: ImagineArt automation, E2E testing",
            "Browsers: Firefox (persistent), Chromium"
        ]
    },
    {
        "name": "UV-Package-Manager",
        "entityType": "Tool",
        "observations": [
            "Fast Python package installer",
            "Location: C:/ComfyUI/python_embeded/Scripts/uv.exe",
            "Use: MCP server execution, dependency management"
        ]
    },
    {
        "name": "rclone",
        "entityType": "Tool",
        "observations": [
            "Cloud storage sync tool",
            "Remotes: Google Drive configured",
            "Use: Colab file transfer, backup"
        ]
    }
]

# =============================================================================
# WORKFLOW ENTITIES (5)
# =============================================================================

WORKFLOW_ENTITIES: List[Entity] = [
    {
        "name": "Asset-Generation-Pipeline",
        "entityType": "Workflow",
        "observations": [
            "End-to-end game asset creation workflow",
            "Stages: Concept -> 2D Art -> 3D Model -> Sprites -> Integration",
            "Tools: ImagineArt, ComfyUI, Meshy.ai, Blender",
            "Output: Game-ready sprite sheets"
        ]
    },
    {
        "name": "Sprint-Execution-Workflow",
        "entityType": "Workflow",
        "observations": [
            "7-phase sprint execution model",
            "Phases: Planning, Infrastructure, Implementation, Integration, E2E, Quality Gates, Documentation",
            "Agents: 3-wave parallel deployment",
            "Quality: 10/10 standard, zero test.skip()"
        ]
    },
    {
        "name": "Claude-Code-Integration-Workflow",
        "entityType": "Workflow",
        "observations": [
            "7-stage gated integration process",
            "Stages: Assessment, Foundation, Hub, Engine, Advanced, Optimization, Production",
            "Gates: 7 quality gates with exit criteria",
            "Duration: ~5 hours estimated"
        ]
    },
    {
        "name": "Agent-Coordination-Workflow",
        "entityType": "Workflow",
        "observations": [
            "File-based agent coordination system",
            "Coordinator: C:/Ziggie/coordinator",
            "Pattern: Task file -> Agent pickup -> Execution -> Report",
            "Monitoring: Overwatch agent aggregation"
        ]
    },
    {
        "name": "Deployment-Workflow",
        "entityType": "Workflow",
        "observations": [
            "Production deployment process",
            "Steps: Build -> Test -> Docker -> VPS -> Verify",
            "Target: ziggie.cloud",
            "Rollback: Playbook documented"
        ]
    }
]

# =============================================================================
# RELATIONS (50+)
# =============================================================================

RELATIONS: List[Relation] = [
    # Project relationships
    {"from_": "Ziggie-Ecosystem", "to": "MeowPing-RTS", "relationType": "CONTAINS"},
    {"from_": "Ziggie-Ecosystem", "to": "AI-Game-Dev-System", "relationType": "CONTAINS"},
    {"from_": "Ziggie-Ecosystem", "to": "Team-Ziggie", "relationType": "CONTAINS"},
    {"from_": "Ziggie-Ecosystem", "to": "VPS-Production", "relationType": "DEPLOYS_TO"},

    # MeowPing components
    {"from_": "MeowPing-RTS", "to": "Backend-FastAPI", "relationType": "USES"},
    {"from_": "MeowPing-RTS", "to": "Frontend-React", "relationType": "USES"},
    {"from_": "MeowPing-RTS", "to": "Database-SQLite", "relationType": "USES"},
    {"from_": "MeowPing-RTS", "to": "Asset-Generation-Pipeline", "relationType": "USES"},

    # MCP relationships
    {"from_": "Ziggie-Ecosystem", "to": "MCP-Memory", "relationType": "INTEGRATES"},
    {"from_": "Ziggie-Ecosystem", "to": "MCP-Filesystem", "relationType": "INTEGRATES"},
    {"from_": "Ziggie-Ecosystem", "to": "MCP-Chrome-DevTools", "relationType": "INTEGRATES"},
    {"from_": "AI-Game-Dev-System", "to": "MCP-ComfyUI", "relationType": "INTEGRATES"},
    {"from_": "AI-Game-Dev-System", "to": "MCP-Unity", "relationType": "INTEGRATES"},
    {"from_": "AI-Game-Dev-System", "to": "MCP-Unreal", "relationType": "INTEGRATES"},
    {"from_": "AI-Game-Dev-System", "to": "MCP-Godot", "relationType": "INTEGRATES"},
    {"from_": "AI-Game-Dev-System", "to": "MCP-SimStudio", "relationType": "PLANS_TO_USE"},
    {"from_": "AI-Game-Dev-System", "to": "MCP-LocalLLM", "relationType": "PLANS_TO_USE"},

    # Agent team relationships
    {"from_": "Team-Ziggie", "to": "ARTEMIS", "relationType": "HAS_MEMBER"},
    {"from_": "Team-Ziggie", "to": "LEONIDAS", "relationType": "HAS_MEMBER"},
    {"from_": "Team-Ziggie", "to": "GAIA", "relationType": "HAS_MEMBER"},
    {"from_": "Team-Ziggie", "to": "VULCAN", "relationType": "HAS_MEMBER"},
    {"from_": "Team-Ziggie", "to": "TERRA", "relationType": "HAS_MEMBER"},
    {"from_": "Team-Ziggie", "to": "PROMETHEUS", "relationType": "HAS_MEMBER"},
    {"from_": "Team-Ziggie", "to": "IRIS", "relationType": "HAS_MEMBER"},
    {"from_": "Team-Ziggie", "to": "MYTHOS", "relationType": "HAS_MEMBER"},
    {"from_": "Team-Ziggie", "to": "HEPHAESTUS", "relationType": "HAS_MEMBER"},
    {"from_": "Team-Ziggie", "to": "DAEDALUS", "relationType": "HAS_MEMBER"},
    {"from_": "Team-Ziggie", "to": "ARGUS", "relationType": "HAS_MEMBER"},
    {"from_": "Team-Ziggie", "to": "MAXIMUS", "relationType": "HAS_MEMBER"},
    {"from_": "Team-Ziggie", "to": "FORGE", "relationType": "HAS_MEMBER"},
    {"from_": "Team-Ziggie", "to": "ATLAS", "relationType": "HAS_MEMBER"},
    {"from_": "Team-Ziggie", "to": "Overwatch", "relationType": "HAS_COORDINATOR"},

    # Agent hierarchy
    {"from_": "L1-Architect-Backend", "to": "L2-Implementer", "relationType": "DELEGATES_TO"},
    {"from_": "L1-Architect-Frontend", "to": "L2-Implementer", "relationType": "DELEGATES_TO"},
    {"from_": "L2-Implementer", "to": "L3-Specialist", "relationType": "DELEGATES_TO"},
    {"from_": "Overwatch", "to": "L1-Architect-Backend", "relationType": "MONITORS"},
    {"from_": "Overwatch", "to": "L1-Architect-Frontend", "relationType": "MONITORS"},
    {"from_": "Overwatch", "to": "L1-Architect-Integration", "relationType": "MONITORS"},

    # Documentation relationships
    {"from_": "ZIGGIE-ECOSYSTEM-MASTER-STATUS-V2", "to": "Ziggie-Ecosystem", "relationType": "DOCUMENTS"},
    {"from_": "CLAUDE-CODE-INTEGRATION-PLAN", "to": "Claude-Code-Integration-Workflow", "relationType": "DOCUMENTS"},
    {"from_": "INTEGRATION-TASK-DEPENDENCY-GRAPH", "to": "Claude-Code-Integration-Workflow", "relationType": "SUPPORTS"},
    {"from_": "INTEGRATION-ROLLBACK-PLAYBOOK", "to": "Claude-Code-Integration-Workflow", "relationType": "SUPPORTS"},
    {"from_": "INTEGRATION-AWS-STAGE", "to": "Claude-Code-Integration-Workflow", "relationType": "EXTENDS"},
    {"from_": "MCP-Configuration", "to": "MCP-Memory", "relationType": "CONFIGURES"},
    {"from_": "MCP-Configuration", "to": "MCP-Filesystem", "relationType": "CONFIGURES"},
    {"from_": "MCP-Configuration", "to": "MCP-Chrome-DevTools", "relationType": "CONFIGURES"},

    # Tool usage relationships
    {"from_": "Asset-Generation-Pipeline", "to": "Blender", "relationType": "USES"},
    {"from_": "Asset-Generation-Pipeline", "to": "ComfyUI-Server", "relationType": "USES"},
    {"from_": "Asset-Generation-Pipeline", "to": "ImagineArt-Service", "relationType": "USES"},
    {"from_": "Asset-Generation-Pipeline", "to": "Meshy-AI-Service", "relationType": "USES"},
    {"from_": "MCP-ComfyUI", "to": "ComfyUI-Server", "relationType": "CONNECTS_TO"},
    {"from_": "MCP-LocalLLM", "to": "Ollama-Server", "relationType": "CONNECTS_TO"},

    # Infrastructure relationships
    {"from_": "VPS-Production", "to": "VPS-DigitalOcean", "relationType": "RUNS_ON"},
    {"from_": "Backend-FastAPI", "to": "Database-SQLite", "relationType": "USES"},
    {"from_": "MCP-Memory", "to": "Memory-Bank", "relationType": "STORES_IN"},

    # Workflow relationships
    {"from_": "Sprint-Execution-Workflow", "to": "Team-Ziggie", "relationType": "ORCHESTRATES"},
    {"from_": "Agent-Coordination-Workflow", "to": "Overwatch", "relationType": "MANAGED_BY"},
    {"from_": "Deployment-Workflow", "to": "VPS-Production", "relationType": "TARGETS"},
]

# =============================================================================
# AGGREGATED DATA
# =============================================================================

ALL_ENTITIES: List[Entity] = (
    PROJECT_ENTITIES +
    INFRASTRUCTURE_ENTITIES +
    AGENT_ENTITIES +
    DOCUMENTATION_ENTITIES +
    SERVICE_ENTITIES +
    TOOL_ENTITIES +
    WORKFLOW_ENTITIES
)

# =============================================================================
# OUTPUT FUNCTIONS
# =============================================================================

def generate_mcp_entity_payload() -> dict:
    """Generate payload for mcp__memory__create_entities"""
    return {
        "entities": [
            {
                "name": e["name"],
                "entityType": e["entityType"],
                "observations": e["observations"]
            }
            for e in ALL_ENTITIES
        ]
    }

def generate_mcp_relations_payload() -> dict:
    """Generate payload for mcp__memory__create_relations"""
    return {
        "relations": [
            {
                "from": r["from_"],
                "to": r["to"],
                "relationType": r["relationType"]
            }
            for r in RELATIONS
        ]
    }

def print_summary():
    """Print summary statistics"""
    print("=" * 60)
    print("ZIGGIE MEMORY GRAPH POPULATION SUMMARY")
    print("=" * 60)
    print(f"\nTotal Entities: {len(ALL_ENTITIES)}")
    print(f"  - Projects:       {len(PROJECT_ENTITIES)}")
    print(f"  - Infrastructure: {len(INFRASTRUCTURE_ENTITIES)}")
    print(f"  - Agents:         {len(AGENT_ENTITIES)}")
    print(f"  - Documentation:  {len(DOCUMENTATION_ENTITIES)}")
    print(f"  - Services:       {len(SERVICE_ENTITIES)}")
    print(f"  - Tools:          {len(TOOL_ENTITIES)}")
    print(f"  - Workflows:      {len(WORKFLOW_ENTITIES)}")
    print(f"\nTotal Relations: {len(RELATIONS)}")
    print("=" * 60)

def export_json(filename: str = "memory_population_payload.json"):
    """Export full payload to JSON file"""
    payload = {
        "entities": generate_mcp_entity_payload()["entities"],
        "relations": generate_mcp_relations_payload()["relations"],
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_entities": len(ALL_ENTITIES),
            "total_relations": len(RELATIONS),
            "version": "1.0.0"
        }
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)

    print(f"\nExported to: {filename}")
    return filename

def verify_integrity():
    """Verify all relations reference existing entities"""
    entity_names = {e["name"] for e in ALL_ENTITIES}
    errors = []

    for rel in RELATIONS:
        if rel["from_"] not in entity_names:
            errors.append(f"Missing entity: {rel['from_']} (from)")
        if rel["to"] not in entity_names:
            errors.append(f"Missing entity: {rel['to']} (to)")

    if errors:
        print("\nIntegrity Errors:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("\nIntegrity Check: PASSED (all relations reference valid entities)")
        return True

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print_summary()

    if "--verify" in sys.argv:
        verify_integrity()

    if "--export" in sys.argv:
        export_json()

    # Always print usage instructions
    print("\n" + "=" * 60)
    print("USAGE INSTRUCTIONS")
    print("=" * 60)
    print("""
To populate the Memory MCP knowledge graph, execute this in Claude Code:

1. Run this script to generate JSON:
   python populate_memory_graph.py --export

2. Use the generated payload with Memory MCP tools:
   - mcp__memory__create_entities (with entities array)
   - mcp__memory__create_relations (with relations array)

3. Verify population:
   - mcp__memory__read_graph
   - mcp__memory__search_nodes with query="Ziggie"

Alternative: Copy entity/relation definitions and call MCP tools directly.
""")
