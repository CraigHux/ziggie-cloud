# Ziggie Directory Structure - Complete Reference

**Version:** 1.0.0
**Last Updated:** 2025-11-07

---

## Overview

This document provides a complete reference for the Ziggie directory structure, explaining what goes where and why.

---

## Guiding Principles

1. **Separation of Concerns** - Each major component has its own top-level directory
2. **Discoverability** - Intuitive naming and organization
3. **Scalability** - Structure supports growth without reorganization
4. **Documentation Co-location** - Docs live near the code they document
5. **Test Mirroring** - Tests mirror source code structure
6. **Shared Resources** - Common utilities in dedicated shared directory

---

## Complete Directory Tree

```
C:\Ziggie\
│
├── agents/                                # AI AGENT SYSTEM (584 agents)
│   ├── L1-agents/                         # Level 1 - Primary Agents (8)
│   │   ├── 01_ART_DIRECTOR_AGENT.md
│   │   ├── 02_CHARACTER_PIPELINE_AGENT.md
│   │   ├── 03_ENVIRONMENT_PIPELINE_AGENT.md
│   │   ├── 04_GAME_SYSTEMS_DEVELOPER_AGENT.md
│   │   ├── 05_UI_UX_DEVELOPER_AGENT.md
│   │   ├── 06_CONTENT_DESIGNER_AGENT.md
│   │   ├── 07_INTEGRATION_AGENT.md
│   │   ├── 08_QA_TESTING_AGENT.md
│   │   └── README.md
│   │
│   ├── L2-agents/                         # Level 2 - Specialized Agents (64)
│   │   ├── art-director/
│   │   │   ├── 01_style_consistency.md
│   │   │   ├── 02_color_palette.md
│   │   │   ├── 03_asset_review.md
│   │   │   └── ... (8 total)
│   │   ├── character-pipeline/
│   │   │   ├── 01_base_generation.md
│   │   │   ├── 02_equipment_variations.md
│   │   │   └── ... (8 total)
│   │   ├── environment-pipeline/
│   │   ├── game-systems/
│   │   ├── ui-ux/
│   │   ├── content-designer/
│   │   ├── integration/
│   │   ├── qa-testing/
│   │   └── README.md
│   │
│   ├── L3-agents/                         # Level 3 - Micro Agents (512)
│   │   ├── art-director/
│   │   │   ├── style-consistency/
│   │   │   │   ├── 01_color_validation.md
│   │   │   │   ├── 02_proportion_check.md
│   │   │   │   └── ... (8 total)
│   │   │   └── ... (8 L2 × 8 L3 = 64)
│   │   ├── character-pipeline/
│   │   └── ... (8 L1 × 64 L3 each = 512 total)
│   │
│   ├── knowledge-base/                    # KNOWLEDGE BASE PIPELINE
│   │   ├── L1-art-director/               # Agent-specific KB
│   │   │   ├── style-guides/
│   │   │   ├── color-theory/
│   │   │   └── README.md
│   │   ├── L1-character-pipeline/
│   │   │   ├── comfyui-workflows/
│   │   │   ├── ip-adapter-knowledge/
│   │   │   ├── prompt-engineering/
│   │   │   └── README.md
│   │   ├── L1-environment-pipeline/
│   │   ├── L1-game-systems/
│   │   ├── L1-ui-ux/
│   │   ├── L1-content-designer/
│   │   ├── L1-integration/
│   │   ├── L1-qa-testing/
│   │   │
│   │   ├── cross-agent-knowledge/         # Shared KB
│   │   │   ├── ai-tools-updates/
│   │   │   ├── automation-patterns/
│   │   │   ├── best-practices/
│   │   │   └── industry-news/
│   │   │
│   │   ├── metadata/                      # KB System Config
│   │   │   ├── creator-database.json      # 50+ YouTube creators
│   │   │   ├── routing-rules.json         # Knowledge routing
│   │   │   ├── scan-log.txt               # Scan history
│   │   │   └── pipeline-status.json       # System status
│   │   │
│   │   ├── src/                           # KB Pipeline Code
│   │   │   ├── video_scanner.py           # YouTube scanner
│   │   │   ├── transcript_extractor.py    # Transcript extraction
│   │   │   ├── ai_analyzer.py             # Claude API analyzer
│   │   │   ├── knowledge_writer.py        # KB file writer
│   │   │   ├── scheduler.py               # Automated scheduling
│   │   │   ├── config.py                  # Configuration
│   │   │   └── logger.py                  # Logging
│   │   │
│   │   ├── temp/                          # Temporary processing
│   │   ├── logs/                          # KB logs
│   │   ├── README.md                      # KB overview
│   │   ├── SETUP_GUIDE.md                 # Setup instructions
│   │   └── USER_GUIDE.md                  # Usage guide
│   │
│   └── docs/                              # Agent Documentation
│       ├── AGENT_DISPATCH.md              # How to invoke agents
│       ├── AGENT_TEAM_README.md           # Team overview
│       ├── L3_MICRO_AGENT_ARCHITECTURE.md # L3 architecture
│       ├── SUB_AGENT_ARCHITECTURE.md      # Sub-agent design
│       └── workflows/                     # Common workflows
│
├── control-center/                        # CONTROL CENTER WEB APP
│   ├── backend/                           # FastAPI Backend
│   │   ├── api/                           # API Endpoints
│   │   │   ├── agents.py                  # Agent management
│   │   │   ├── knowledge.py               # KB management
│   │   │   ├── projects.py                # Project management
│   │   │   ├── comfyui.py                 # ComfyUI integration
│   │   │   ├── docker.py                  # Docker management
│   │   │   ├── services.py                # Service monitoring
│   │   │   ├── system.py                  # System info
│   │   │   ├── usage.py                   # Usage analytics
│   │   │   └── __init__.py
│   │   │
│   │   ├── database/                      # Database Layer
│   │   │   ├── models.py                  # SQLAlchemy models
│   │   │   ├── db.py                      # DB connection
│   │   │   └── __init__.py
│   │   │
│   │   ├── services/                      # Business Logic
│   │   │   ├── agent_service.py
│   │   │   ├── knowledge_service.py
│   │   │   ├── project_service.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── config.py                      # Backend config
│   │   ├── main.py                        # FastAPI app
│   │   ├── requirements.txt               # Python deps
│   │   └── .env.example                   # Env template
│   │
│   ├── frontend/                          # React Frontend
│   │   ├── src/
│   │   │   ├── components/                # React components
│   │   │   │   ├── agents/
│   │   │   │   │   ├── AgentCard.tsx
│   │   │   │   │   ├── AgentList.tsx
│   │   │   │   │   └── AgentDetail.tsx
│   │   │   │   ├── knowledge/
│   │   │   │   │   ├── KnowledgeViewer.tsx
│   │   │   │   │   ├── CreatorList.tsx
│   │   │   │   │   └── ScanHistory.tsx
│   │   │   │   ├── projects/
│   │   │   │   ├── dashboard/
│   │   │   │   ├── layout/
│   │   │   │   └── common/
│   │   │   │
│   │   │   ├── pages/                     # Page components
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   ├── Agents.tsx
│   │   │   │   ├── Knowledge.tsx
│   │   │   │   ├── Projects.tsx
│   │   │   │   └── Settings.tsx
│   │   │   │
│   │   │   ├── services/                  # API clients
│   │   │   │   ├── agentService.ts
│   │   │   │   ├── knowledgeService.ts
│   │   │   │   └── api.ts
│   │   │   │
│   │   │   ├── hooks/                     # Custom hooks
│   │   │   │   ├── useAgents.ts
│   │   │   │   ├── useKnowledge.ts
│   │   │   │   └── useProjects.ts
│   │   │   │
│   │   │   ├── types/                     # TypeScript types
│   │   │   ├── utils/                     # Utilities
│   │   │   ├── styles/                    # Global styles
│   │   │   ├── App.tsx                    # Root component
│   │   │   └── main.tsx                   # Entry point
│   │   │
│   │   ├── public/                        # Static assets
│   │   ├── package.json                   # Node deps
│   │   ├── vite.config.ts                 # Vite config
│   │   └── tsconfig.json                  # TS config
│   │
│   ├── ComfyUI/                           # ComfyUI Integration
│   │   ├── workflows/                     # Workflow templates
│   │   │   ├── text_to_3d_basic.json
│   │   │   ├── text_to_3d_advanced.json
│   │   │   ├── sdxl_turbo_EXACT_character_clone.json
│   │   │   ├── sdxl_turbo_equipment_variations.json
│   │   │   ├── sdxl_turbo_animation_poses.json
│   │   │   └── sdxl_turbo_size_progression.json
│   │   │
│   │   ├── models/                        # Model storage
│   │   │   ├── hunyuan3d/
│   │   │   ├── sdxl/
│   │   │   ├── controlnet/
│   │   │   └── .gitkeep
│   │   │
│   │   ├── output/                        # Generated outputs
│   │   ├── input/                         # Input images
│   │   ├── temp/                          # Temp files
│   │   │
│   │   ├── Dockerfile                     # ComfyUI container
│   │   ├── docker-compose.yml             # Docker compose
│   │   ├── download_models.sh             # Model downloader
│   │   └── README.md
│   │
│   └── docs/                              # Control Center Docs
│       ├── USER_GUIDE.md
│       ├── API_REFERENCE.md
│       ├── DEPLOYMENT.md
│       └── TROUBLESHOOTING.md
│
├── game/                                  # MEOW PING RTS GAME
│   ├── backend/                           # Game Backend
│   │   ├── app/
│   │   │   ├── config/                    # Game config
│   │   │   │   ├── unit_stats.py
│   │   │   │   ├── wave_config.py
│   │   │   │   └── __init__.py
│   │   │   │
│   │   │   ├── models/                    # Data models
│   │   │   │   ├── unit.py
│   │   │   │   ├── unit_types.py
│   │   │   │   ├── combat_schemas.py
│   │   │   │   └── __init__.py
│   │   │   │
│   │   │   ├── routes/                    # API routes
│   │   │   │   ├── combat.py
│   │   │   │   ├── units.py
│   │   │   │   └── __init__.py
│   │   │   │
│   │   │   ├── services/                  # Game logic
│   │   │   │   ├── combat_service.py
│   │   │   │   ├── unit_service.py
│   │   │   │   ├── unit_behavior.py
│   │   │   │   └── player_unit_ai_service.py
│   │   │   │
│   │   │   ├── schemas/                   # Pydantic schemas
│   │   │   ├── tasks/                     # Background tasks
│   │   │   ├── utils/                     # Utilities
│   │   │   └── __init__.py
│   │   │
│   │   ├── auth/                          # Authentication
│   │   │   ├── routes.py
│   │   │   ├── service.py
│   │   │   └── dependencies.py
│   │   │
│   │   ├── building/                      # Building system
│   │   │   ├── routes.py
│   │   │   └── service.py
│   │   │
│   │   ├── session/                       # Session/Lobby
│   │   │   ├── routes.py
│   │   │   └── service.py
│   │   │
│   │   ├── database/                      # Database
│   │   │   ├── models.py
│   │   │   ├── connection.py
│   │   │   ├── building_models.py
│   │   │   └── session_models.py
│   │   │
│   │   ├── config/                        # Configuration
│   │   │   ├── settings.py
│   │   │   └── building_config.py
│   │   │
│   │   ├── tests/                         # Backend tests
│   │   │   ├── unit/
│   │   │   └── integration/
│   │   │
│   │   ├── main.py                        # FastAPI app
│   │   └── requirements.txt
│   │
│   ├── frontend/                          # Game Frontend
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── auth/                  # Login/register
│   │   │   │   ├── combat/                # Combat UI
│   │   │   │   ├── game/                  # Game rendering
│   │   │   │   ├── session/               # Lobby UI
│   │   │   │   ├── layout/                # Layout
│   │   │   │   ├── ui/                    # UI components
│   │   │   │   └── test/                  # Test components
│   │   │   │
│   │   │   ├── pages/                     # Game pages
│   │   │   ├── contexts/                  # React contexts
│   │   │   ├── hooks/                     # Custom hooks
│   │   │   ├── services/                  # API clients
│   │   │   ├── types/                     # TypeScript types
│   │   │   ├── utils/                     # Utilities
│   │   │   └── styles/                    # Styles
│   │   │
│   │   ├── public/
│   │   │   └── assets/                    # Game assets
│   │   │       ├── sprites/
│   │   │       ├── icons/
│   │   │       ├── audio/
│   │   │       └── fonts/
│   │   │
│   │   └── package.json
│   │
│   ├── assets/                            # Source Assets
│   │   ├── characters/
│   │   │   ├── cats/                      # Hero faction
│   │   │   │   ├── hero-meowping/
│   │   │   │   ├── warrior-cat/
│   │   │   │   └── archer-cat/
│   │   │   └── ai-enemies/                # Enemy faction
│   │   │       ├── robot-soldier/
│   │   │       └── drone/
│   │   │
│   │   ├── environment/
│   │   │   ├── terrain/
│   │   │   ├── buildings/
│   │   │   └── props/
│   │   │
│   │   ├── vfx/                           # Visual effects
│   │   ├── icons/                         # UI icons
│   │   ├── audio/                         # Sound effects
│   │   │
│   │   ├── generated/                     # AI-generated
│   │   │   ├── 3d-models/                 # .glb files
│   │   │   ├── sprites/                   # Rendered sprites
│   │   │   └── sprite-sheets/             # Compiled sheets
│   │   │
│   │   └── .cache/                        # Asset cache
│   │
│   ├── data/                              # Game Data
│   │   ├── unit-stats.json                # Unit statistics
│   │   ├── balance-config.json            # Balance params
│   │   ├── tech-tree.json                 # Tech tree
│   │   └── character-specs.json           # Character specs
│   │
│   ├── missions/                          # Campaign Missions
│   │   ├── 01-tutorial.json
│   │   ├── 02-first-battle.json
│   │   └── ...
│   │
│   └── docs/                              # Game Docs
│       ├── GAME_DESIGN.md
│       ├── COMBAT_SYSTEM.md
│       ├── UNITS_REFERENCE.md
│       └── API_GUIDE.md
│
├── shared/                                # SHARED RESOURCES
│   ├── automation/                        # Automation Scripts
│   │   ├── install/
│   │   │   ├── 01_core_infrastructure.sh
│   │   │   ├── 02_backend_services.sh
│   │   │   └── ...
│   │   │
│   │   ├── deployment/
│   │   │   ├── deploy.sh
│   │   │   ├── rollback.sh
│   │   │   └── health-check.sh
│   │   │
│   │   ├── maintenance/
│   │   │   ├── backup.sh
│   │   │   ├── cleanup.sh
│   │   │   └── update.sh
│   │   │
│   │   └── README.md
│   │
│   ├── configs/                           # Shared Configs
│   │   ├── docker/
│   │   │   ├── docker-compose.yml
│   │   │   ├── docker-compose.prod.yml
│   │   │   └── Dockerfile.template
│   │   │
│   │   ├── environment/
│   │   │   ├── .env.development.example
│   │   │   ├── .env.production.example
│   │   │   └── .env.test.example
│   │   │
│   │   └── security/
│   │       ├── cors.yaml
│   │       └── api-keys.yaml.example
│   │
│   ├── templates/                         # Reusable Templates
│   │   ├── agent-templates/
│   │   │   ├── L1_AGENT_TEMPLATE.md
│   │   │   ├── L2_AGENT_TEMPLATE.md
│   │   │   └── L3_AGENT_TEMPLATE.md
│   │   │
│   │   ├── doc-templates/
│   │   │   ├── API_DOC_TEMPLATE.md
│   │   │   ├── USER_GUIDE_TEMPLATE.md
│   │   │   └── ARCHITECTURE_TEMPLATE.md
│   │   │
│   │   └── workflow-templates/
│   │       └── comfyui-workflow-template.json
│   │
│   └── tools/                             # Utility Scripts
│       ├── db-migrate.py                  # Database migration
│       ├── asset-optimizer.py             # Asset optimization
│       ├── log-analyzer.py                # Log analysis
│       └── performance-profiler.py        # Performance profiling
│
├── tests/                                 # ALL TESTS
│   ├── agents/                            # Agent Tests
│   │   ├── test_agent_system.py
│   │   ├── test_agent_dispatch.py
│   │   └── test_knowledge_base.py
│   │
│   ├── control-center/                    # Control Center Tests
│   │   ├── backend/
│   │   │   ├── test_agents_api.py
│   │   │   ├── test_knowledge_api.py
│   │   │   └── test_projects_api.py
│   │   │
│   │   └── frontend/
│   │       ├── AgentCard.test.tsx
│   │       └── KnowledgeViewer.test.tsx
│   │
│   ├── game/                              # Game Tests
│   │   ├── backend/
│   │   │   ├── test_combat.py
│   │   │   ├── test_units.py
│   │   │   └── test_auth.py
│   │   │
│   │   └── frontend/
│   │       └── GameRenderer.test.tsx
│   │
│   ├── integration/                       # Integration Tests
│   │   ├── test_end_to_end.py
│   │   ├── test_agent_workflow.py
│   │   └── test_asset_pipeline.py
│   │
│   ├── performance/                       # Performance Tests
│   │   ├── test_api_performance.py
│   │   └── test_rendering_performance.py
│   │
│   ├── fixtures/                          # Test Fixtures
│   ├── mocks/                             # Mock Data
│   ├── conftest.py                        # pytest config
│   └── README.md
│
├── docs/                                  # CENTRAL DOCUMENTATION
│   ├── architecture/                      # Architecture Docs
│   │   ├── SYSTEM_OVERVIEW.md
│   │   ├── AGENT_ARCHITECTURE.md
│   │   ├── API_ARCHITECTURE.md
│   │   ├── DATABASE_SCHEMA.md
│   │   └── DIAGRAMS.md
│   │
│   ├── guides/                            # How-To Guides
│   │   ├── getting-started/
│   │   │   ├── INSTALLATION.md
│   │   │   ├── FIRST_STEPS.md
│   │   │   └── TROUBLESHOOTING.md
│   │   │
│   │   ├── development/
│   │   │   ├── CONTRIBUTING.md
│   │   │   ├── CODE_STYLE.md
│   │   │   ├── TESTING_GUIDE.md
│   │   │   └── DEBUGGING.md
│   │   │
│   │   └── operations/
│   │       ├── DEPLOYMENT.md
│   │       ├── MONITORING.md
│   │       └── MAINTENANCE.md
│   │
│   ├── api/                               # API Documentation
│   │   ├── control-center/
│   │   │   ├── AGENTS_API.md
│   │   │   ├── KNOWLEDGE_API.md
│   │   │   └── PROJECTS_API.md
│   │   │
│   │   └── game/
│   │       ├── COMBAT_API.md
│   │       ├── UNITS_API.md
│   │       └── AUTH_API.md
│   │
│   └── tutorials/                         # Tutorials
│       ├── 01_creating_first_agent.md
│       ├── 02_generating_game_asset.md
│       ├── 03_adding_knowledge_source.md
│       └── 04_deploying_to_production.md
│
├── data/                                  # DATA STORAGE
│   ├── databases/                         # Database Files
│   │   ├── control-center.db
│   │   ├── game.db
│   │   └── .gitkeep
│   │
│   ├── logs/                              # System Logs
│   │   ├── control-center/
│   │   ├── game/
│   │   ├── agents/
│   │   └── .gitkeep
│   │
│   ├── cache/                             # Temporary Cache
│   │   └── .gitkeep
│   │
│   └── exports/                           # Data Exports
│       └── .gitkeep
│
├── .github/                               # GITHUB CONFIGURATION
│   ├── workflows/                         # CI/CD Pipelines
│   │   ├── test.yml                       # Run tests
│   │   ├── deploy.yml                     # Deploy
│   │   └── docs.yml                       # Build docs
│   │
│   ├── ISSUE_TEMPLATE/                    # Issue Templates
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── agent_request.md
│   │
│   └── PULL_REQUEST_TEMPLATE.md
│
├── .gitignore                             # Git Ignore Rules
├── .editorconfig                          # Editor Config
├── .prettierrc                            # Code Formatting
├── README.md                              # Main README
├── QUICKSTART.md                          # Quick Start Guide
├── ARCHITECTURE.md                        # Architecture Overview
├── DIRECTORY_STRUCTURE.md                 # This File
├── CHANGELOG.md                           # Version History
└── LICENSE                                # License File
```

---

## Directory Purpose Reference

### Top-Level Directories

| Directory | Purpose | Key Contents |
|-----------|---------|--------------|
| `agents/` | AI Agent system | 584 agents, KB pipeline |
| `control-center/` | Web management UI | Backend, frontend, ComfyUI |
| `game/` | Meow Ping RTS | Game backend, frontend, assets |
| `shared/` | Shared resources | Scripts, configs, templates |
| `tests/` | All tests | Unit, integration, performance |
| `docs/` | Central documentation | Architecture, guides, tutorials |
| `data/` | Data storage | Databases, logs, cache |
| `.github/` | GitHub config | Workflows, issue templates |

---

## Agent System Structure

### Three-Tier Agent Hierarchy

```
L1 (8 agents) - Primary specialists
  └─> L2 (64 agents) - Specialized sub-agents (8 per L1)
      └─> L3 (512 agents) - Micro agents (8 per L2)
```

### Agent Directory Pattern

```
agents/
├── L1-agents/              # Top-level agents (8)
│   └── 01_ART_DIRECTOR_AGENT.md
│
├── L2-agents/              # Specialized agents (64)
│   └── art-director/       # Group by L1 parent
│       ├── 01_style_consistency.md
│       └── ... (8 per L1)
│
└── L3-agents/              # Micro agents (512)
    └── art-director/       # Group by L1 parent
        └── style-consistency/  # Group by L2 parent
            ├── 01_color_validation.md
            └── ... (8 per L2)
```

---

## Knowledge Base Structure

### Agent-Specific Knowledge

```
agents/knowledge-base/
└── L1-{agent-name}/        # One per L1 agent
    ├── {category-1}/       # Knowledge categories
    ├── {category-2}/
    └── README.md
```

### Cross-Agent Knowledge

```
agents/knowledge-base/
└── cross-agent-knowledge/  # Shared by all agents
    ├── ai-tools-updates/
    ├── automation-patterns/
    └── industry-news/
```

### Knowledge Pipeline

```
agents/knowledge-base/
├── metadata/               # System configuration
│   ├── creator-database.json
│   └── routing-rules.json
│
└── src/                   # Pipeline code
    ├── video_scanner.py
    ├── ai_analyzer.py
    └── knowledge_writer.py
```

---

## Control Center Structure

### Backend API Pattern

```
control-center/backend/
├── api/                   # API endpoints
│   ├── {resource}.py      # e.g., agents.py
│   └── __init__.py
│
├── services/              # Business logic
│   ├── {resource}_service.py
│   └── __init__.py
│
└── database/              # Data layer
    ├── models.py
    └── db.py
```

### Frontend Component Pattern

```
control-center/frontend/src/
├── components/            # Reusable components
│   └── {feature}/        # Group by feature
│       ├── {Component}.tsx
│       └── {Component}.test.tsx
│
├── pages/                # Page components
│   └── {Page}.tsx
│
└── services/             # API clients
    └── {resource}Service.ts
```

---

## Game Structure

### Backend Pattern

```
game/backend/
├── app/                  # Main application
│   ├── config/          # Configuration
│   ├── models/          # Data models
│   ├── routes/          # API routes
│   ├── services/        # Business logic
│   └── utils/           # Utilities
│
├── {feature}/           # Feature modules
│   ├── routes.py
│   ├── service.py
│   └── __init__.py
│
└── database/            # Database layer
```

### Asset Organization

```
game/assets/
├── characters/          # Organized by faction
│   ├── cats/           # Hero faction
│   │   └── {character}/
│   └── ai-enemies/     # Enemy faction
│       └── {character}/
│
├── environment/        # Environment assets
│   ├── terrain/
│   ├── buildings/
│   └── props/
│
└── generated/          # AI-generated
    ├── 3d-models/
    ├── sprites/
    └── sprite-sheets/
```

---

## Test Structure

### Test Mirroring Principle

Tests mirror the source code structure:

```
Source:  game/backend/app/services/combat_service.py
Test:    tests/game/backend/services/test_combat_service.py

Source:  control-center/frontend/src/components/agents/AgentCard.tsx
Test:    tests/control-center/frontend/components/AgentCard.test.tsx
```

### Test Categories

```
tests/
├── {component}/        # Unit tests (mirror source)
├── integration/        # Integration tests
├── performance/        # Performance tests
├── fixtures/          # Test data
└── mocks/             # Mock objects
```

---

## Shared Resources

### Automation Scripts

```
shared/automation/
├── install/           # Installation scripts
├── deployment/        # Deployment scripts
├── maintenance/       # Maintenance scripts
└── README.md
```

### Configuration Files

```
shared/configs/
├── docker/            # Docker configs
├── environment/       # Environment configs
└── security/          # Security configs
```

### Templates

```
shared/templates/
├── agent-templates/   # Agent prompt templates
├── doc-templates/     # Documentation templates
└── workflow-templates/# Workflow templates
```

---

## Documentation Organization

### Three-Level Documentation

1. **Component-Level** - `{component}/docs/` - Specific to that component
2. **Feature-Level** - `docs/guides/{feature}/` - Feature guides
3. **System-Level** - `docs/architecture/` - Overall architecture

### Documentation Types

| Type | Location | Purpose |
|------|----------|---------|
| API Reference | `docs/api/` | API endpoints |
| Architecture | `docs/architecture/` | System design |
| Guides | `docs/guides/` | How-to guides |
| Tutorials | `docs/tutorials/` | Step-by-step |
| Component Docs | `{component}/docs/` | Component-specific |

---

## File Naming Conventions

### Python Files

```
snake_case.py              # Standard Python
test_*.py                  # Test files
*_service.py               # Service layer
*_model.py                 # Data models
*_schema.py                # Pydantic schemas
```

### TypeScript/JavaScript Files

```
PascalCase.tsx             # React components
camelCase.ts               # Utilities, services
*.test.tsx                 # Component tests
*.spec.ts                  # Unit tests
```

### Markdown Files

```
UPPERCASE.md               # Important docs (README, CHANGELOG)
Title_Case.md              # Standard docs
lowercase.md               # Reference files
```

### Configuration Files

```
.{name}                    # Dotfiles (.gitignore, .env)
{name}.json                # JSON configs
{name}.yaml                # YAML configs
{name}.config.js           # JS configs
```

---

## Best Practices

### 1. Keep Related Files Together

```
✅ Good:
component/
├── Component.tsx
├── Component.test.tsx
├── Component.styles.ts
└── Component.types.ts

❌ Bad:
components/Component.tsx
tests/Component.test.tsx
styles/Component.styles.ts
types/Component.types.ts
```

### 2. Use Index Files

```
✅ Good:
agents/L1-agents/
├── 01_ART_DIRECTOR_AGENT.md
├── 02_CHARACTER_PIPELINE_AGENT.md
└── README.md (explains structure)

❌ Bad:
agents/L1-agents/
├── 01_ART_DIRECTOR_AGENT.md
└── 02_CHARACTER_PIPELINE_AGENT.md (no context)
```

### 3. Consistent Naming

```
✅ Good:
- agents/ (plural)
- tests/ (plural)
- docs/ (plural)

❌ Bad:
- agent/ (inconsistent)
- test/ (inconsistent)
- documentation/ (verbose)
```

### 4. Logical Grouping

```
✅ Good:
api/
├── agents.py (grouped by resource)
├── knowledge.py
└── projects.py

❌ Bad:
api/
├── get_agents.py (grouped by operation)
├── post_agents.py
└── get_knowledge.py
```

### 5. Clear Separation

```
✅ Good:
- Source code in src/
- Tests in tests/
- Docs in docs/
- Data in data/

❌ Bad:
- Everything mixed together
```

---

## Migration Guide

### Moving Files from Old Structure

#### From meowping-rts:

```bash
# AI Agents
meowping-rts/ai-agents/               → Ziggie/agents/

# Control Center
meowping-rts/control-center/          → Ziggie/control-center/

# Game Backend
meowping-rts/backend/                 → Ziggie/game/backend/

# Game Frontend
meowping-rts/frontend/                → Ziggie/game/frontend/

# Assets
meowping-rts/assets/                  → Ziggie/game/assets/

# Automation Scripts
meowping-rts/*.sh                     → Ziggie/shared/automation/

# Documentation
meowping-rts/*.md                     → Ziggie/docs/guides/
```

#### From ComfyUI:

```bash
# Agent Management
ComfyUI/api_server/routes/agents_routes.py  → Ziggie/control-center/backend/api/agents.py
ComfyUI/api_server/services/agent_service.py → Ziggie/control-center/backend/services/agent_service.py

# Knowledge Base
ComfyUI/api_server/routes/knowledge_routes.py → Ziggie/control-center/backend/api/knowledge.py
ComfyUI/api_server/services/knowledge_service.py → Ziggie/control-center/backend/services/knowledge_service.py

# Tests
ComfyUI/tests/backend/test_agents_api.py    → Ziggie/tests/control-center/backend/test_agents_api.py
ComfyUI/tests/integration/test_agents_api.py → Ziggie/tests/integration/test_agents_workflow.py
```

---

## Maintenance

### Regular Cleanup

1. **Remove old temp files:** `data/cache/`, `*/temp/`
2. **Archive old logs:** `data/logs/*/archive/`
3. **Clean build artifacts:** `*/dist/`, `*/build/`
4. **Prune unused deps:** `pip-autoremove`, `npm prune`

### Directory Health Checks

```bash
# Check for orphaned files
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -delete

# Verify structure
ls -la agents/L1-agents/    # Should have 8 files
ls -la control-center/      # Should have backend/, frontend/, ComfyUI/

# Check for gitignored files
git status --ignored
```

---

## Quick Reference

### Find Things Fast

```bash
# Find agent
ls agents/L1-agents/*{keyword}*

# Find API endpoint
ls control-center/backend/api/*{resource}*

# Find test
ls tests/**/*test*{feature}*

# Find documentation
ls docs/**/*{topic}*
```

### Common Paths

```bash
# Agent dispatch guide
agents/docs/AGENT_DISPATCH.md

# Control Center API
control-center/backend/api/

# Game backend
game/backend/app/

# Knowledge Base config
agents/knowledge-base/metadata/

# Automation scripts
shared/automation/

# Central docs
docs/
```

---

## Summary

The Ziggie directory structure is designed for:

- ✅ **Clarity** - Easy to understand
- ✅ **Scalability** - Supports growth
- ✅ **Maintainability** - Easy to maintain
- ✅ **Discoverability** - Easy to find things
- ✅ **Consistency** - Predictable patterns
- ✅ **Separation** - Clear boundaries

**When in doubt:** Group related files together, use clear names, and document your decisions.

---

**Last Updated:** 2025-11-07
**Version:** 1.0.0
**Maintained By:** Ziggie Team
