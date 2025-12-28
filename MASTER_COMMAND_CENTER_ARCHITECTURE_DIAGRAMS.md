# MASTER COMMAND CENTER - ARCHITECTURE DIAGRAMS

**Purpose:** Visual reference for system architecture
**Last Updated:** 2025-12-21

---

## 1. CURRENT STATE vs. TARGET STATE

### Current State (As-Is)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ISOLATED WORKSPACES                             │
└─────────────────────────────────────────────────────────────────────────┘

    Ziggie (C:/Ziggie)                FitFlow (C:/FitFlow)
    ┌──────────────────┐              ┌──────────────────┐
    │ Control Center   │              │ Backend API      │
    │ Port 8080        │              │ Port 3100        │
    │                  │              │                  │
    │ Agents: 1,884    │              │ Agents: ???      │
    │ MCP: ComfyUI     │              │ MCP: ???         │
    └──────────────────┘              └──────────────────┘
            ↓ (isolated)                       ↓ (isolated)
    ┌──────────────────┐              ┌──────────────────┐
    │ ComfyUI (8188)   │              │ (No services)    │
    │ Ollama (11434)   │              │                  │
    └──────────────────┘              └──────────────────┘

    ai-game-dev-system               SimStudio
    ┌──────────────────┐              ┌──────────────────┐
    │ Unity MCP (8080) │              │ Sim Engine       │
    │ Unreal MCP       │              │ (TBD)            │
    │ Godot MCP        │              │                  │
    └──────────────────┘              └──────────────────┘

PROBLEMS:
❌ No cross-workspace coordination
❌ Duplicated MCP server instances
❌ Agent silos (no knowledge sharing)
❌ Manual context switching
❌ Inconsistent monitoring
```

### Target State (To-Be)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ZIGGIE MASTER COMMAND CENTER                         │
│                         http://localhost:4000                           │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │                    UNIFIED CONTROL PLANE                        │   │
│  │                                                                 │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │   │
│  │  │ API Gateway  │  │Agent Orchestr│  │  MCP Gateway │         │   │
│  │  │   (Kong)     │  │  (LangGraph) │  │  (AgentCore) │         │   │
│  │  │  Port 4000   │  │              │  │              │         │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘         │   │
│  │                                                                 │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │   │
│  │  │Service Discov│  │  Observability│  │  Auth & RBAC │         │   │
│  │  │   (Consul)   │  │(Prometheus+G)│  │    (JWT)     │         │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘         │   │
│  └────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
         │                       │                          │
         ▼                       ▼                          ▼
┌────────────────┐      ┌────────────────┐       ┌────────────────┐
│  WORKSPACES    │      │ AGENT REGISTRY │       │  MCP SERVERS   │
│  (5 projects)  │      │  (1,884+)      │       │  (7+ unified)  │
│                │      │                │       │                │
│ • Ziggie       │      │ • L0: 1        │       │ • comfyui      │
│ • FitFlow      │      │ • L1: 22       │       │ • unity        │
│ • ai-game-dev  │      │ • L2: 176      │       │ • unreal       │
│ • SimStudio    │      │ • L3: 1,408    │       │ • godot        │
│ • MeowPing NFT │      │ • BMAD: 3      │       │ • aws_gpu      │
│                │      │ • Elite: 15    │       │ • local_llm    │
└────────────────┘      └────────────────┘       └────────────────┘

BENEFITS:
✅ Single pane of glass for all workspaces
✅ Shared infrastructure (40% cost reduction)
✅ Cross-agent knowledge sharing
✅ Unified observability
✅ Automated coordination
```

---

## 2. LAYERED ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              React Dashboard (Port 4001)                      │  │
│  │  • Workspace Management  • Agent Monitor  • MCP Console      │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY LAYER                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   Kong API Gateway (Port 4000)                │  │
│  │  • Routing  • Rate Limiting  • Authentication  • CORS        │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATION LAYER                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐  │
│  │ Workspace Coord  │  │ Agent Orchestr   │  │  MCP Gateway    │  │
│  │                  │  │                  │  │                 │  │
│  │ • Multi-project  │  │ • Task dispatch  │  │ • Tool discovery│  │
│  │ • Dependencies   │  │ • Wave execution │  │ • Routing       │  │
│  │ • Port allocation│  │ • Load balancing │  │ • Aggregation   │  │
│  └──────────────────┘  └──────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        SERVICE MESH LAYER                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Envoy Sidecars (mTLS)                      │  │
│  │  • Load balancing  • Circuit breakers  • Retry policies      │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         SERVICE LAYER                               │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐          │
│  │ Agent Services│  │ MCP Servers   │  │ Workspace Apps│          │
│  │               │  │               │  │               │          │
│  │ • L1 Agents   │  │ • ComfyUI     │  │ • MeowPing    │          │
│  │ • L2 Agents   │  │ • Unity MCP   │  │ • FitFlow     │          │
│  │ • L3 Agents   │  │ • Unreal MCP  │  │ • SimStudio   │          │
│  │ • BMAD/Elite  │  │ • Ollama      │  │ • More...     │          │
│  └───────────────┘  └───────────────┘  └───────────────┘          │
└─────────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐  │
│  │  SQLite DB       │  │  Consul KV Store │  │ Prometheus TSDB │  │
│  │                  │  │                  │  │                 │  │
│  │ • Workspaces     │  │ • Configurations │  │ • Metrics       │  │
│  │ • Agents         │  │ • Service catalog│  │ • Time series   │  │
│  │ • Tasks          │  │ • Health checks  │  │ • Alerts        │  │
│  └──────────────────┘  └──────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. AGENT HIERARCHY ARCHITECTURE

```
                          ┌──────────────────────┐
                          │   L0: COORDINATOR    │
                          │                      │
                          │      Ziggie          │
                          │  (Master Command)    │
                          └──────────┬───────────┘
                                     │
              ┌──────────────────────┴──────────────────────┐
              │                                             │
    ┌─────────▼─────────┐                      ┌───────────▼──────────┐
    │  L1: SPECIALISTS  │                      │   ELITE TEAMS        │
    │  (22 total)       │                      │   (15 specialists)   │
    │                   │                      │                      │
    │ Workspace-Based:  │                      │ • Art Team (4)       │
    │ • Ziggie (8)      │                      │ • Design Team (4)    │
    │ • FitFlow (5)     │                      │ • Technical Team (3) │
    │ • ai-game-dev (4) │                      │ • Production Team (3)│
    │ • SimStudio (3)   │                      │ • BMAD Team (3)      │
    │ • MeowPing NFT(2) │                      │                      │
    └─────────┬─────────┘                      └──────────────────────┘
              │
              └──────────────────────┬──────────────────────
                                     │
                          ┌──────────▼───────────┐
                          │  L2: SPECIALIZED     │
                          │  (176 total)         │
                          │                      │
                          │ 8 per L1 agent       │
                          │ • Art Director → 8   │
                          │ • Character Pipe → 8 │
                          │ • Environment → 8    │
                          │ • ... etc            │
                          └──────────┬───────────┘
                                     │
                          ┌──────────▼───────────┐
                          │  L3: MICRO AGENTS    │
                          │  (1,408 total)       │
                          │                      │
                          │ 8 per L2 agent       │
                          │ Highly specialized   │
                          │ Single-task focused  │
                          └──────────────────────┘

TOTAL AGENT COUNT: 1,625 (L0+L1+L2+L3+BMAD+Elite)
COORDINATION MODEL: Hierarchical Multi-Agent System (HMAS)
COMMUNICATION: Agent-to-Agent Protocol (A2A) via pub/sub bus
```

---

## 4. MCP GATEWAY ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MCP GATEWAY HUB                              │
│                     http://localhost:8080/api/mcp                   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   GATEWAY CORE                               │   │
│  │                                                              │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌────────────────┐  │   │
│  │  │Tool Discovery │  │ Smart Routing │  │  Load Balancer │  │   │
│  │  └───────────────┘  └───────────────┘  └────────────────┘  │   │
│  │                                                              │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌────────────────┐  │   │
│  │  │ Auth & RBAC   │  │Rate Limiting  │  │ Circuit Breaker│  │   │
│  │  └───────────────┘  └───────────────┘  └────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│ ComfyUI MCP│  │ Unity MCP  │  │ Unreal MCP │  │ Godot MCP  │
│            │  │            │  │            │  │            │
│ Transport: │  │ Transport: │  │ Transport: │  │ Transport: │
│   HTTP     │  │   HTTP     │  │   stdio    │  │   stdio    │
│ Port: 8188 │  │ Port: 8080 │  │ Process ID │  │ Process ID │
│            │  │            │  │   12345    │  │   12346    │
│ Tools:     │  │ Tools:     │  │            │  │            │
│ • generate │  │ • compile  │  │ Tools:     │  │ Tools:     │
│ • upscale  │  │ • package  │  │ • build    │  │ • export   │
│ • animate  │  │ • deploy   │  │ • optimize │  │ • test     │
└────────────┘  └────────────┘  └────────────┘  └────────────┘

         │              │              │              │
         ▼              ▼              ▼              ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│ AWS GPU MCP│  │ Local LLM  │  │SimStudio   │
│            │  │   (Ollama) │  │    MCP     │
│ Transport: │  │            │  │            │
│   HTTP     │  │ Transport: │  │ Transport: │
│ Cloud API  │  │   HTTP     │  │   WebSocket│
│            │  │ Port:11434 │  │ Port: 5000 │
│ Tools:     │  │            │  │            │
│ • train    │  │ Tools:     │  │ Tools:     │
│ • infer    │  │ • chat     │  │ • simulate │
│ • deploy   │  │ • embed    │  │ • analyze  │
└────────────┘  └────────────┘  └────────────┘

PROTOCOL SUPPORT:
• HTTP/REST: ComfyUI, Unity, AWS GPU, Local LLM
• stdio: Unreal, Godot (subprocess communication)
• WebSocket: SimStudio (real-time updates)

FEATURES:
✅ Unified tool discovery across all servers
✅ Intelligent routing based on tool capabilities
✅ Load balancing for multi-instance servers
✅ Circuit breakers for fault isolation
✅ Centralized authentication (JWT)
✅ Rate limiting per user/workspace
✅ Metrics collection for all tool calls
```

---

## 5. WORKSPACE COORDINATION FLOW

```
┌─────────────────────────────────────────────────────────────────────┐
│                      TASK REQUEST                                   │
│  "Generate 10 new cat warrior variations for MeowPing"             │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 L0 COORDINATOR (Ziggie)                             │
│  • Analyze task requirements                                        │
│  • Identify affected workspaces: ["Ziggie", "MeowPing RTS"]        │
│  • Check workspace dependencies                                     │
│  • Allocate resources (agents, MCP servers, ports)                  │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  WAVE 1:      │  │  WAVE 2:      │  │  WAVE 3:      │
│  Foundation   │  │  Integration  │  │  Completion   │
│               │  │               │  │               │
│ Agents:       │  │ Agents:       │  │ Agents:       │
│ • Art Director│  │ • Character   │  │ • QA Testing  │
│ • ARTEMIS     │  │   Pipeline    │  │ • Integration │
│               │  │ • BMAD Backend│  │               │
│ Tasks:        │  │               │  │ Tasks:        │
│ • Define style│  │ Tasks:        │  │ • E2E testing │
│ • Create      │  │ • Generate    │  │ • Deploy to   │
│   prompts     │  │   assets      │  │   game        │
│               │  │ • Render      │  │ • Documentation│
│               │  │   sprites     │  │               │
│ MCP Calls:    │  │               │  │ MCP Calls:    │
│ • None (plan) │  │ MCP Calls:    │  │ • None        │
│               │  │ • comfyui     │  │   (validation)│
│               │  │   .generate() │  │               │
└───────────────┘  │ • comfyui     │  └───────────────┘
                   │   .render()   │
                   └───────────────┘

         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     RESULT AGGREGATION                              │
│  • 10 character variations generated                                │
│  • Sprite sheets rendered                                           │
│  • Assets deployed to game                                          │
│  • Quality gates passed                                             │
│  • Total time: 2m 34s (12x faster than manual)                      │
└─────────────────────────────────────────────────────────────────────┘

COORDINATION PATTERNS:
• Wave-based execution (sequential waves, parallel within wave)
• Priority-based workspace scheduling (P0 → P1 → P2)
• Dependency resolution (ComfyUI shared across workspaces)
• Resource pooling (agents, MCP servers, GPU access)
```

---

## 6. SERVICE MESH DATA PLANE

```
┌────────────────────────────────────────────────────────────────────┐
│                      CONTROL PLANE (Ziggie Core)                   │
│  • Configuration Management  • Certificate Authority (mTLS)        │
│  • Service Discovery (Consul)  • Observability (Prometheus)        │
└────────────────────────┬───────────────────────────────────────────┘
                         │ Configures & Monitors
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│  DATA PLANE 1  │ │  DATA PLANE 2  │ │  DATA PLANE 3  │
│                │ │                │ │                │
│ ┌────────────┐ │ │ ┌────────────┐ │ │ ┌────────────┐ │
│ │   Envoy    │◄┼─┼►│   Envoy    │◄┼─┼►│   Envoy    │ │
│ │  Sidecar   │ │ │ │  Sidecar   │ │ │ │  Sidecar   │ │
│ │            │ │ │ │            │ │ │ │            │ │
│ │ Features:  │ │ │ │ Features:  │ │ │ │ Features:  │ │
│ │ • mTLS     │ │ │ │ • mTLS     │ │ │ │ • mTLS     │ │
│ │ • Retries  │ │ │ │ • Retries  │ │ │ │ • Retries  │ │
│ │ • Timeouts │ │ │ │ • Timeouts │ │ │ │ • Timeouts │ │
│ │ • Metrics  │ │ │ │ • Metrics  │ │ │ │ • Metrics  │ │
│ └─────┬──────┘ │ │ └─────┬──────┘ │ │ └─────┬──────┘ │
│       │        │ │       │        │ │       │        │
│ ┌─────▼──────┐ │ │ ┌─────▼──────┐ │ │ ┌─────▼──────┐ │
│ │L1 Agent    │ │ │ │MCP Server  │ │ │ │Workspace   │ │
│ │(Art Dir)   │ │ │ │(ComfyUI)   │ │ │ │(FitFlow)   │ │
│ └────────────┘ │ │ └────────────┘ │ │ └────────────┘ │
└────────────────┘ └────────────────┘ └────────────────┘

TRAFFIC FLOW:
Art Director → Envoy → (mTLS) → Envoy → ComfyUI
                ↓
             Metrics
                ↓
           Prometheus

BENEFITS:
• Zero-trust security (mTLS everywhere)
• Automatic retries on failures
• Circuit breakers prevent cascading failures
• Distributed tracing across all hops
• Canary deployments for agent updates
```

---

## 7. OBSERVABILITY ARCHITECTURE

```
┌────────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                             │
│  • Ziggie Control Center  • Agent Services  • MCP Servers         │
│  • Workspaces            • Databases        • External APIs        │
└────────────────────────┬───────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│  METRICS       │ │   LOGS         │ │   TRACES       │
│  (Prometheus)  │ │  (Loki/ELK)    │ │  (Jaeger)      │
│                │ │                │ │                │
│ Data Points:   │ │ Sources:       │ │ Spans:         │
│ • Counter      │ │ • stdout       │ │ • HTTP requests│
│ • Gauge        │ │ • stderr       │ │ • MCP calls    │
│ • Histogram    │ │ • Application  │ │ • Agent tasks  │
│ • Summary      │ │   logs         │ │ • DB queries   │
│                │ │ • Access logs  │ │                │
│ Scrape:        │ │                │ │ Export:        │
│ Every 15s      │ │ Stream real-   │ │ Batch every    │
│                │ │ time           │ │ 10s            │
└────────┬───────┘ └────────┬───────┘ └────────┬───────┘
         │                  │                  │
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────────┐
│                    VISUALIZATION LAYER                             │
│                    Grafana (Port 3050)                             │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │              MASTER COMMAND CENTER DASHBOARD                  │ │
│  │                                                               │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │ │
│  │  │ Agent Stats │  │ MCP Metrics │  │  Workspace  │          │ │
│  │  │             │  │             │  │   Health    │          │ │
│  │  │ Active: 245 │  │ Req/min:450 │  │ On-track: 4 │          │ │
│  │  │ Idle: 1,380 │  │ P95: 95ms   │  │ At-risk: 1  │          │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘          │ │
│  │                                                               │ │
│  │  ┌───────────────────────────────────────────────────────┐   │ │
│  │  │         Task Completion Rate (Last Hour)              │   │ │
│  │  │  [████████████████████████░░] 87 tasks/hour           │   │ │
│  │  └───────────────────────────────────────────────────────┘   │ │
│  │                                                               │ │
│  │  ┌───────────────────────────────────────────────────────┐   │ │
│  │  │         Service Dependency Graph                       │   │ │
│  │  │                                                        │   │ │
│  │  │    Ziggie ──► ComfyUI ──► GPU                         │   │ │
│  │  │      │                                                 │   │ │
│  │  │      └──────► Ollama ──► CPU                          │   │ │
│  │  │      │                                                 │   │ │
│  │  │      └──────► Consul ──► Health                       │   │ │
│  │  └───────────────────────────────────────────────────────┘   │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘

ALERTING:
┌────────────────────────────────────────────┐
│  Prometheus Alertmanager                   │
│                                            │
│  Rules:                                    │
│  • Agent utilization > 90% → Page oncall  │
│  • MCP p95 latency > 200ms → Slack notify│
│  • Workspace health = blocked → Email    │
│  • Error rate > 5% → Auto-rollback       │
└────────────────────────────────────────────┘
```

---

## 8. DEPLOYMENT TOPOLOGY

```
┌────────────────────────────────────────────────────────────────────┐
│                      DEVELOPMENT (Local)                           │
│                   Windows 10/11 Workstation                        │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  ZIGGIE MASTER COMMAND CENTER                                │ │
│  │  Port 4000 (Kong) + 8080 (FastAPI) + 4001 (React)           │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Services    │  │   Databases  │  │ Observability│           │
│  │              │  │              │  │              │           │
│  │ • Consul     │  │ • SQLite     │  │ • Prometheus │           │
│  │ • MCP Svrs   │  │ • MongoDB    │  │ • Grafana    │           │
│  │ • Workspaces │  │              │  │ • Jaeger     │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                    PRODUCTION (Cloud - Future)                     │
│                       AWS/Azure/GCP                                │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                  Kubernetes Cluster                           │ │
│  │                                                               │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │ │
│  │  │   Pod 1     │  │   Pod 2     │  │   Pod 3     │          │ │
│  │  │             │  │             │  │             │          │ │
│  │  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │          │ │
│  │  │ │ Ziggie  │ │  │ │ ComfyUI │ │  │ │  Ollama │ │          │ │
│  │  │ │  API    │ │  │ │   MCP   │ │  │ │   MCP   │ │          │ │
│  │  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │          │ │
│  │  │             │  │             │  │             │          │ │
│  │  │ Replicas: 3 │  │ Replicas: 2 │  │ Replicas: 1 │          │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘          │ │
│  │                                                               │ │
│  │  ┌──────────────────────────────────────────────────────┐    │ │
│  │  │              Istio Service Mesh                       │    │ │
│  │  │  • Load Balancing  • mTLS  • Observability           │    │ │
│  │  └──────────────────────────────────────────────────────┘    │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Managed DB  │  │  Object Store│  │  Monitoring  │           │
│  │              │  │              │  │              │           │
│  │ • PostgreSQL │  │ • S3/Blob    │  │ • CloudWatch │           │
│  │ • Redis      │  │ • Assets     │  │ • DataDog    │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└────────────────────────────────────────────────────────────────────┘

DEPLOYMENT STRATEGY:
Development → Staging → Production
    ↓            ↓           ↓
  Local      Docker      Kubernetes
             Compose
```

---

## 9. SECURITY ARCHITECTURE

```
┌────────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                               │
└────────────────────────────────────────────────────────────────────┘

Layer 1: NETWORK ISOLATION
┌────────────────────────────────────────────────────────────────────┐
│  • Development: localhost only (127.0.0.1)                         │
│  • Production: VPC with private subnets                            │
│  • Firewall rules: Deny all, allow specific ports                  │
└────────────────────────────────────────────────────────────────────┘

Layer 2: API GATEWAY AUTHENTICATION
┌────────────────────────────────────────────────────────────────────┐
│  Kong API Gateway                                                  │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  JWT Plugin:                                                  │ │
│  │  • Verify token signature                                     │ │
│  │  • Check expiration                                           │ │
│  │  • Extract claims (user_id, workspace, permissions)           │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘

Layer 3: ROLE-BASED ACCESS CONTROL (RBAC)
┌────────────────────────────────────────────────────────────────────┐
│  Permissions Matrix:                                               │
│  ┌────────────────┬────────┬────────┬────────┬────────┐           │
│  │ Resource       │ Admin  │ L1     │ L2/L3  │ BMAD   │           │
│  ├────────────────┼────────┼────────┼────────┼────────┤           │
│  │ Workspace Mgmt │   ✅   │   ❌   │   ❌   │   ❌   │           │
│  │ Agent Dispatch │   ✅   │   ✅   │   ❌   │   ✅   │           │
│  │ MCP Tool Call  │   ✅   │   ✅   │   ✅   │   ✅   │           │
│  │ Config Change  │   ✅   │   ❌   │   ❌   │   ❌   │           │
│  └────────────────┴────────┴────────┴────────┴────────┘           │
└────────────────────────────────────────────────────────────────────┘

Layer 4: SERVICE MESH mTLS
┌────────────────────────────────────────────────────────────────────┐
│  Envoy Sidecars:                                                   │
│  • All inter-service traffic encrypted with mTLS                   │
│  • Automatic certificate rotation (24h)                            │
│  • Certificate Authority: Consul Connect                           │
└────────────────────────────────────────────────────────────────────┘

Layer 5: INPUT VALIDATION
┌────────────────────────────────────────────────────────────────────┐
│  Pydantic Models:                                                  │
│  • Type checking on all API inputs                                 │
│  • Range validation (e.g., port 1-65535)                           │
│  • Pattern matching (e.g., email, URL)                             │
│  • XSS/SQL injection prevention                                    │
└────────────────────────────────────────────────────────────────────┘

Layer 6: RATE LIMITING
┌────────────────────────────────────────────────────────────────────┐
│  Kong Rate Limiting:                                               │
│  • Per-user: 100 req/min                                           │
│  • Per-workspace: 500 req/min                                      │
│  • MCP tools: 10 concurrent, 100/min                               │
│  • Admin APIs: 20 req/min                                          │
└────────────────────────────────────────────────────────────────────┘

Layer 7: AUDIT LOGGING
┌────────────────────────────────────────────────────────────────────┐
│  All sensitive operations logged:                                  │
│  • Who (user_id, agent_id)                                         │
│  • What (action, resource, outcome)                                │
│  • When (timestamp)                                                │
│  • Where (IP address, workspace)                                   │
│  • Why (request context, correlation_id)                           │
│                                                                    │
│  Retention: 90 days (compliance)                                   │
└────────────────────────────────────────────────────────────────────┘
```

---

**Document Version:** 1.0.0
**Last Updated:** 2025-12-21
**Maintained By:** L1 Integration Architect
**Review Cadence:** Monthly or after major architecture changes
