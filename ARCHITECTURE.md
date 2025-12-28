# Ziggie - System Architecture

**Complete architectural overview of the Ziggie platform**

**Version:** 3.0.0
**Last Updated:** 2025-11-09
**Status:** EXPANSION COMPLETE - 1,884 AGENTS

---

## Table of Contents

1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Component Architecture](#component-architecture)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Integration Patterns](#integration-patterns)
7. [Scalability](#scalability)
8. [Security](#security)
9. [Performance](#performance)
10. [Deployment](#deployment)

---

## System Overview

### What is Ziggie?

Ziggie is a **unified AI-powered development platform** that combines:

1. **1,884 AI Agents** organized in 3 tiers (12 L1, 144 L2, 1,728 L3)
2. **Knowledge Base Pipeline** that learns from 50+ YouTube experts
3. **Control Center** web interface for management
4. **Game Development Platform** (Meow Ping RTS)
5. **AI Asset Generation** (ComfyUI + Hunyuan3D)

### Design Philosophy

- **Modularity** - Components are independent and loosely coupled
- **Automation** - Reduce manual work through intelligent automation
- **Extensibility** - Easy to add new agents, creators, or features
- **Observability** - Clear visibility into system behavior
- **Developer Experience** - Optimized for productivity

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           ZIGGIE PLATFORM                            │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
        ┌───────────▼──────┐  ┌──▼──────┐  ┌──▼────────────┐
        │   AI AGENTS      │  │ CONTROL │  │ GAME          │
        │   SYSTEM         │  │ CENTER  │  │ DEVELOPMENT   │
        │                  │  │         │  │               │
        │ • 1,884 Agents   │  │ • UI    │  │ • Backend     │
        │ • Knowledge Base │  │ • API   │  │ • Frontend    │
        │ • L1/L2/L3 Tiers │  │ • ComfyUI│ │ • Assets      │
        └──────────────────┘  └─────────┘  └───────────────┘
                │                   │               │
                └───────────────────┼───────────────┘
                                    │
                    ┌───────────────▼────────────────┐
                    │     SHARED INFRASTRUCTURE      │
                    │                                │
                    │ • Automation Scripts           │
                    │ • Shared Configs               │
                    │ • Templates & Tools            │
                    │ • Testing Framework            │
                    │ • Documentation                │
                    └────────────────────────────────┘
```

---

## Component Architecture

### 1. AI Agent System

```
┌────────────────────────────────────────────────────────┐
│                 AI AGENT SYSTEM                        │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │  L1 AGENTS   │  │  L2 AGENTS   │  │  L3 AGENTS  │ │
│  │  (12 total)  │  │  (144 total) │  │ (1,728 total)│ │
│  │              │  │              │  │             │ │
│  │ • Art Dir    │  │ • Style      │  │ • Color Val │ │
│  │ • Character  │  │ • Equipment  │  │ • Prop Check│ │
│  │ • Environment│  │ • Terrain    │  │ • Light Adj │ │
│  │ • Game Sys   │  │ • Combat     │  │ • Physics   │ │
│  │ • UI/UX      │  │ • Layout     │  │ • Animation │ │
│  │ • Content    │  │ • Balance    │  │ • Stats     │ │
│  │ • Integration│  │ • Deploy     │  │ • Build     │ │
│  │ • QA Testing │  │ • Auto Test  │  │ • Unit Test │ │
│  │ • Migration  │  │ • Refactor   │  │ • Update    │ │
│  │ • Director   │  │ • Cinematic  │  │ • Camera    │ │
│  │ • Storyboard │  │ • Visual Plan│  │ • Sequence  │ │
│  │ • Copywriter │  │ • Script     │  │ • Dialog    │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘ │
│         │                 │                 │         │
│         └─────────────────┼─────────────────┘         │
│                           │                           │
│              ┌────────────▼────────────┐              │
│              │   KNOWLEDGE BASE        │              │
│              │                         │              │
│              │ • 50+ YouTube Creators  │              │
│              │ • Auto Scan & Extract   │              │
│              │ • Claude API Analysis   │              │
│              │ • Smart Routing         │              │
│              │ • Weekly Updates        │              │
│              └─────────────────────────┘              │
│                                                        │
└────────────────────────────────────────────────────────┘
```

#### Agent Hierarchy

**L1 Agents (8)** - Primary specialists
- Responsible for high-level strategy
- Coordinate L2 agents
- Final decision authority

**L2 Agents (64)** - Specialized workers
- Handle specific sub-domains
- Execute L1 directives
- Coordinate L3 agents
- 8 per L1 agent

**L3 Agents (512)** - Micro-task executors
- Atomic, focused tasks
- No coordination needed
- Highly specific
- 8 per L2 agent

#### Knowledge Base Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   YOUTUBE    │────▶│   EXTRACT    │────▶│   ANALYZE    │
│   SCANNER    │     │  TRANSCRIPTS │     │ (Claude API) │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                                  ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   AGENTS     │◀────│    ROUTE     │◀────│   VALIDATE   │
│   UPDATED    │     │  TO AGENTS   │     │  CONFIDENCE  │
└──────────────┘     └──────────────┘     └──────────────┘
```

**Components:**
1. **Video Scanner** - Monitors YouTube channels
2. **Transcript Extractor** - Gets video transcripts
3. **AI Analyzer** - Claude API extracts insights
4. **Knowledge Router** - Maps insights to agents
5. **Validator** - Checks confidence scores
6. **Writer** - Updates KB markdown files

---

### 2. Control Center

```
┌────────────────────────────────────────────────────────┐
│                  CONTROL CENTER                        │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │              REACT FRONTEND                     │  │
│  │                                                 │  │
│  │  Dashboard │ Agents │ Knowledge │ Projects     │  │
│  └─────────────────────┬───────────────────────────┘  │
│                        │                              │
│                        │ REST API                     │
│                        │                              │
│  ┌─────────────────────▼───────────────────────────┐  │
│  │              FASTAPI BACKEND                    │  │
│  │                                                 │  │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │  │
│  │  │   API    │  │ SERVICES │  │  DATABASE   │  │  │
│  │  │ ROUTES   │──│  LOGIC   │──│   LAYER     │  │  │
│  │  └──────────┘  └──────────┘  └─────────────┘  │  │
│  └─────────────────────────────────────────────────┘  │
│                        │                              │
│                        │                              │
│  ┌─────────────────────▼───────────────────────────┐  │
│  │              COMFYUI SERVICE                    │  │
│  │                                                 │  │
│  │  • Asset Generation Workflows                  │  │
│  │  • Hunyuan3D Integration                       │  │
│  │  • SDXL Turbo Pipelines                        │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

#### Backend Architecture

```
FastAPI Application
│
├── API Layer (routes)
│   ├── /agents          → Agent management
│   ├── /knowledge       → KB management
│   ├── /projects        → Project tracking
│   ├── /comfyui         → Asset generation
│   ├── /docker          → Container management
│   ├── /services        → Service monitoring
│   ├── /system          → System health
│   └── /usage           → Usage analytics
│
├── Service Layer (business logic)
│   ├── AgentService     → Agent operations
│   ├── KnowledgeService → KB operations
│   ├── ProjectService   → Project ops
│   └── ComfyUIService   → Asset generation
│
└── Data Layer
    ├── SQLAlchemy ORM   → Database models
    └── Alembic          → Migrations
```

#### Frontend Architecture

```
React Application (TypeScript + Vite)
│
├── Pages (routes)
│   ├── Dashboard        → Overview
│   ├── Agents           → Agent management
│   ├── Knowledge        → KB viewer
│   ├── Projects         → Project list
│   └── Settings         → Configuration
│
├── Components (reusable)
│   ├── agents/          → Agent components
│   ├── knowledge/       → KB components
│   ├── projects/        → Project components
│   ├── dashboard/       → Dashboard widgets
│   └── common/          → Shared components
│
├── Services (API clients)
│   ├── agentService     → Agent API
│   ├── knowledgeService → KB API
│   └── api              → Base HTTP client
│
└── State Management
    └── React Context + Hooks
```

---

### 3. Game Development Platform

```
┌────────────────────────────────────────────────────────┐
│              MEOW PING RTS GAME                        │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │          REACT FRONTEND (Game UI)               │  │
│  │                                                 │  │
│  │  • Three.js 3D Rendering                       │  │
│  │  • Sprite-based 2D Rendering                   │  │
│  │  • Combat UI                                   │  │
│  │  • Session/Lobby System                        │  │
│  │  • Building Interface                          │  │
│  └─────────────────────┬───────────────────────────┘  │
│                        │                              │
│                        │ REST API                     │
│                        │                              │
│  ┌─────────────────────▼───────────────────────────┐  │
│  │          FASTAPI BACKEND (Game Logic)           │  │
│  │                                                 │  │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────┐ │  │
│  │  │  COMBAT    │  │   UNITS    │  │ BUILDING │ │  │
│  │  │  SYSTEM    │  │ RECRUITMENT│  │  SYSTEM  │ │  │
│  │  └────────────┘  └────────────┘  └──────────┘ │  │
│  │                                                 │  │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────┐ │  │
│  │  │   AUTH     │  │  SESSION/  │  │   AI     │ │  │
│  │  │   SYSTEM   │  │   LOBBY    │  │ OPPONENT │ │  │
│  │  └────────────┘  └────────────┘  └──────────┘ │  │
│  └─────────────────────┬───────────────────────────┘  │
│                        │                              │
│                        ▼                              │
│  ┌─────────────────────────────────────────────────┐  │
│  │            MONGODB DATABASE                     │  │
│  │                                                 │  │
│  │  • User accounts                               │  │
│  │  • Game sessions                               │  │
│  │  • Unit stats                                  │  │
│  │  • Building data                               │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

#### Game Backend Services

```
Game Backend (FastAPI)
│
├── Authentication
│   ├── JWT token auth
│   ├── User registration
│   └── Session management
│
├── Combat System
│   ├── Combat calculator
│   ├── Wave system
│   ├── Unit behavior AI
│   └── Damage/defense logic
│
├── Unit System
│   ├── Recruitment
│   ├── Tier progression
│   ├── Equipment
│   └── Statistics
│
├── Building System
│   ├── Construction
│   ├── Upgrades
│   ├── Resource production
│   └── Tech tree
│
└── Session/Lobby
    ├── Game sessions
    ├── Matchmaking
    └── Player state
```

---

## Data Flow

### 1. Knowledge Base Update Flow

```
┌─────────────┐
│   YouTube   │ New video uploaded
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Scanner   │ Weekly scan detects new video
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Extractor  │ Download transcript + metadata
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Analyzer   │ Claude API extracts insights
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Router    │ Map insights to relevant agents
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Validator  │ Check confidence scores (>80%)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Writer    │ Update KB markdown files
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Agents    │ Load updated knowledge on next invoke
└─────────────┘
```

### 2. Asset Generation Flow

```
┌──────────────┐
│     USER     │ Request: "Generate warrior cat"
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Control Ctr  │ POST /api/assets/generate
│   Frontend   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Control Ctr  │ Create generation job
│   Backend    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   ComfyUI    │ Execute workflow (2-5 min)
│   Service    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Output Dir  │ Save .glb file
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Blender    │ Render 8-direction sprites
│  Automation  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Game Assets  │ Deploy to game/assets/
│   Directory  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│     USER     │ Asset available in game
└──────────────┘
```

### 3. Agent Invocation Flow

```
┌──────────────┐
│     USER     │ Task: "Generate character with red cape"
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Claude    │ Load agent prompt file
│     Code     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  L1 Agent    │ Load knowledge base
│ (Character)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Apply KB    │ Use InstaSD insights (IP-Adapter 0.40)
│  Knowledge   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Execute    │ Call Control Center API
│    Task      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   ComfyUI    │ Generate asset with settings
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Result    │ Return generated asset
└──────┬───────┘
       │
       ▼
┌──────────────┐
│     USER     │ Receive result with source citation
└──────────────┘
```

---

## Technology Stack

### Backend

| Layer | Technology | Purpose |
|-------|------------|---------|
| Web Framework | FastAPI | REST API, async support |
| Database ORM | SQLAlchemy | Database abstraction |
| Migrations | Alembic | Schema versioning |
| Validation | Pydantic | Data validation |
| AI Analysis | Anthropic Claude | Knowledge extraction |
| Video Data | YouTube Data API | Channel monitoring |
| Auth | JWT | Authentication |
| ASGI Server | Uvicorn | Production server |

### Frontend

| Layer | Technology | Purpose |
|-------|------------|---------|
| Framework | React 18 | UI framework |
| Language | TypeScript | Type safety |
| Build Tool | Vite | Fast dev server |
| Styling | TailwindCSS | Utility-first CSS |
| UI Components | Material-UI | Component library |
| 3D Rendering | Three.js | 3D visualization |
| State | React Context | State management |
| HTTP Client | Axios | API requests |

### AI/ML

| Component | Technology | Purpose |
|-----------|------------|---------|
| Workflow Engine | ComfyUI | Visual AI workflows |
| 3D Generation | Hunyuan3D 2.0 | Text-to-3D |
| Image Generation | SDXL Turbo | Fast image gen |
| Character Consistency | IP-Adapter | Style transfer |
| Pose Control | ControlNet | Pose guidance |
| Analysis | Claude Sonnet 4.5 | Knowledge extraction |

### Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| Containerization | Docker | Service isolation |
| Orchestration | Docker Compose | Multi-container |
| Database (Dev) | SQLite | Development DB |
| Database (Prod) | PostgreSQL | Production DB |
| CI/CD | GitHub Actions | Automation |
| Version Control | Git | Code versioning |

---

## Integration Patterns

### 1. API Communication

All services communicate via REST APIs:

```
Control Center Frontend ←→ Control Center Backend
Control Center Backend  ←→ ComfyUI Service
Game Frontend           ←→ Game Backend
Control Center Backend  ←→ Claude API
Control Center Backend  ←→ YouTube API
```

### 2. Event-Driven Updates

```
Knowledge Base Scan → Event → Notify Agents
Asset Generation    → Event → Update UI
Test Completion     → Event → Update Dashboard
```

### 3. Shared Configuration

```
shared/configs/
├── environment/    → .env templates
├── docker/         → Docker configs
└── security/       → Security settings
```

### 4. Plugin Architecture

Agents are plugins:
- Self-contained markdown files
- Load on-demand
- No tight coupling
- Easy to add/remove

---

## Scalability

### Horizontal Scaling

```
┌─────────────┐
│ Load Balancer│
└──────┬───────┘
       │
   ┌───┴───┐
   │       │
┌──▼──┐ ┌──▼──┐
│API 1│ │API 2│  Backend instances
└──┬──┘ └──┬──┘
   │       │
   └───┬───┘
       │
┌──────▼───────┐
│   Database   │
└──────────────┘
```

### Caching Strategy

```
┌──────────────┐
│   Frontend   │ → Cache API responses (60s)
└──────┬───────┘
       │
┌──────▼───────┐
│   Backend    │ → Cache DB queries (5min)
└──────┬───────┘
       │
┌──────▼───────┐
│   Database   │
└──────────────┘
```

### Database Optimization

- Indexes on frequently queried fields
- Connection pooling
- Read replicas for reporting
- Partitioning for large tables

---

## Security

### API Security

```
┌──────────────┐
│   Request    │
└──────┬───────┘
       │
┌──────▼───────┐
│ CORS Check   │ → Validate origin
└──────┬───────┘
       │
┌──────▼───────┐
│ JWT Auth     │ → Verify token
└──────┬───────┘
       │
┌──────▼───────┐
│ Rate Limit   │ → Prevent abuse
└──────┬───────┘
       │
┌──────▼───────┐
│ Validation   │ → Pydantic schemas
└──────┬───────┘
       │
┌──────▼───────┐
│ Authorization│ → Check permissions
└──────┬───────┘
       │
┌──────▼───────┐
│   Handler    │ → Process request
└──────────────┘
```

### Data Protection

- Environment variables for secrets
- .gitignore for sensitive files
- HTTPS in production
- Database encryption at rest
- Secure API key storage

---

## Performance

### Target Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| API Response | <500ms | ~300ms |
| Page Load | <2s | ~1s |
| Agent Response | <5s | ~2s |
| Asset Generation | <5min | ~3min |
| Knowledge Scan | <60s/video | ~45s |

### Optimization Techniques

1. **Backend**
   - Async/await for I/O
   - Database query optimization
   - Connection pooling
   - Caching frequently accessed data

2. **Frontend**
   - Code splitting
   - Lazy loading
   - Image optimization
   - Virtual scrolling for lists

3. **AI/ML**
   - GPU acceleration
   - Batch processing
   - Model caching
   - Workflow optimization

---

## Deployment

### Development

```bash
# Local development
docker-compose -f docker-compose.dev.yml up
```

### Production

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# With orchestration (future)
kubectl apply -f k8s/
```

### CI/CD Pipeline

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│   Push   │────▶│   Test   │────▶│  Build   │────▶│  Deploy  │
│ to Git   │     │   Suite  │     │  Images  │     │   Prod   │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

---

## Future Architecture

### v2.0 Vision

```
┌─────────────────────────────────────────────────────────┐
│              DISTRIBUTED ZIGGIE PLATFORM                │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐   │
│  │   Region 1  │  │   Region 2  │  │   Region 3   │   │
│  │   (US-East) │  │   (EU)      │  │   (Asia)     │   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘   │
│         └─────────────────┼─────────────────┘           │
│                           │                             │
│              ┌────────────▼────────────┐                │
│              │   GLOBAL ORCHESTRATOR   │                │
│              │                         │                │
│              │  • Load balancing       │                │
│              │  • Agent distribution   │                │
│              │  • Data replication     │                │
│              │  • Real-time sync       │                │
│              └─────────────────────────┘                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Summary

Ziggie's architecture is designed for:

- ✅ **Modularity** - Independent, loosely coupled components
- ✅ **Scalability** - Horizontal scaling support
- ✅ **Performance** - Optimized for speed
- ✅ **Security** - Multiple layers of protection
- ✅ **Maintainability** - Clear separation of concerns
- ✅ **Extensibility** - Easy to add new features

---

**For more details, see:**
- `docs/architecture/` - Detailed architectural docs
- `docs/api/` - API specifications
- `DIRECTORY_STRUCTURE.md` - File organization

---

**Version:** 1.0.0
**Last Updated:** 2025-11-07
**Maintained By:** Ziggie Team
