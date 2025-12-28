# MASTER COMMAND CENTER - QUICK START GUIDE

**Purpose:** Get the unified orchestration layer running in 1-2 hours
**Prerequisites:** Existing Ziggie Control Center operational

---

## PHASE 1: INFRASTRUCTURE SETUP (30 minutes)

### Step 1: Install Core Components

```bash
# 1. Install Kong API Gateway (Windows)
winget install Kong.Kong --accept-source-agreements --accept-package-agreements

# 2. Install Consul (Service Discovery)
winget install HashiCorp.Consul

# 3. Install Prometheus (Metrics)
winget install Prometheus.Prometheus

# 4. Install Grafana (Dashboards)
winget install GrafanaLabs.Grafana

# Verify installations
kong version
consul version
prometheus --version
grafana-server --version
```

### Step 2: Start Core Services

```bash
# Start Consul (Service Discovery)
consul agent -dev -ui -client=0.0.0.0

# Start Prometheus (edit prometheus.yml first)
prometheus --config.file=C:/Ziggie/shared/configs/prometheus/prometheus.yml

# Start Grafana
grafana-server --homepath="C:/Program Files/GrafanaLabs/grafana"

# Start Kong (create config first)
kong start -c C:/Ziggie/shared/configs/kong/kong.conf
```

### Step 3: Verify Services

```bash
# Check service health
curl http://localhost:8500/ui/dc1/services    # Consul UI
curl http://localhost:9090/graph              # Prometheus UI
curl http://localhost:3000                    # Grafana UI (admin/admin)
curl http://localhost:8001                    # Kong Admin API
```

---

## PHASE 2: MCP GATEWAY SETUP (20 minutes)

### Step 1: Add MCP Gateway to Ziggie Control Center

```bash
cd C:/Ziggie/control-center/backend/api

# Create mcp_gateway.py (copy from integration strategy doc)
# Content already provided in main strategy document
```

### Step 2: Register in FastAPI Main

```python
# C:\Ziggie\control-center\backend\main.py

from api import mcp_gateway  # Add this import

# Add to app router registration (around line 30)
app.include_router(mcp_gateway.router)
```

### Step 3: Test MCP Gateway

```bash
# Restart backend
cd C:/Ziggie/control-center/backend
python main.py

# Test unified tool discovery
curl http://localhost:8080/api/mcp/tools

# Expected response:
{
  "tools": [
    {"name": "comfyui_generate", "server": "comfyui"},
    {"name": "ollama_chat", "server": "local_llm"},
    ...
  ],
  "server_count": 7
}

# Test health check
curl http://localhost:8080/api/mcp/health

# Expected response:
{
  "servers": {
    "comfyui": "healthy",
    "local_llm": "healthy",
    "unity": "not_started",
    ...
  },
  "overall": "degraded"
}
```

---

## PHASE 3: WORKSPACE REGISTRY (15 minutes)

### Step 1: Create Database Migration

```bash
cd C:/Ziggie/control-center/backend

# Create migration script
python -c "
from database.models import Base, engine
from database.db import init_db
import asyncio

async def migrate():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('Database migrated successfully')

asyncio.run(migrate())
"
```

### Step 2: Seed Workspace Data

```python
# C:\Ziggie\control-center\backend\scripts\seed_workspaces.py

from database.db import get_db
from database.models import Workspace, WorkspaceStatus
import asyncio

async def seed_workspaces():
    async for db in get_db():
        workspaces = [
            Workspace(
                name="Ziggie",
                path="C:/Ziggie",
                status=WorkspaceStatus.ACTIVE,
                priority="P0",
                health="on-track",
                port_range_start=3000,
                port_range_end=3099,
                mcp_servers=["comfyui", "local_llm"],
                metadata={"owner": "L0 Coordinator", "projects": ["MeowPing RTS"]}
            ),
            Workspace(
                name="FitFlow",
                path="C:/FitFlow",
                status=WorkspaceStatus.ACTIVE,
                priority="P1",
                health="on-track",
                port_range_start=3100,
                port_range_end=3199,
                mcp_servers=["comfyui", "aws_gpu"],
                metadata={"owner": "Product Manager", "projects": ["FitFlow App"]}
            ),
            # Add other workspaces...
        ]

        for workspace in workspaces:
            db.add(workspace)
        await db.commit()
        print(f"Seeded {len(workspaces)} workspaces")

asyncio.run(seed_workspaces())
```

```bash
# Run seed script
python scripts/seed_workspaces.py
```

### Step 3: Create Workspace API

```python
# C:\Ziggie\control-center\backend\api\workspaces.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db
from database.models import Workspace
from sqlalchemy import select

router = APIRouter(prefix="/api/workspaces", tags=["Workspaces"])

@router.get("/")
async def list_workspaces(db: AsyncSession = Depends(get_db)):
    """List all workspaces"""
    result = await db.execute(select(Workspace))
    workspaces = result.scalars().all()
    return {
        "workspaces": [
            {
                "id": w.id,
                "name": w.name,
                "status": w.status.value,
                "priority": w.priority,
                "health": w.health,
                "port_range": f"{w.port_range_start}-{w.port_range_end}",
                "mcp_servers": w.mcp_servers,
                "metadata": w.metadata
            }
            for w in workspaces
        ],
        "count": len(workspaces)
    }

@router.get("/{workspace_name}")
async def get_workspace(workspace_name: str, db: AsyncSession = Depends(get_db)):
    """Get workspace details"""
    result = await db.execute(
        select(Workspace).where(Workspace.name == workspace_name)
    )
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(404, f"Workspace {workspace_name} not found")
    return workspace

# Register in main.py
# app.include_router(workspaces.router)
```

---

## PHASE 4: AGENT REGISTRY (15 minutes)

### Step 1: Seed Agent Data

```python
# C:\Ziggie\control-center\backend\scripts\seed_agents.py

from database.db import get_db
from database.models import Agent, AgentTier, AgentStatus
import asyncio

async def seed_agents():
    async for db in get_db():
        agents = [
            # L0 Coordinator
            Agent(
                name="Ziggie",
                tier=AgentTier.L0,
                workspace="ziggie",
                skills=["coordination", "protocol_management"],
                specialization="Master Coordinator",
                status=AgentStatus.IDLE
            ),

            # L1 Agents (Ziggie workspace)
            Agent(
                name="Art Director",
                tier=AgentTier.L1,
                workspace="ziggie",
                skills=["style_consistency", "visual_direction", "asset_review"],
                specialization="Art Direction",
                status=AgentStatus.IDLE
            ),
            Agent(
                name="Character Pipeline",
                tier=AgentTier.L1,
                workspace="ziggie",
                skills=["3d_modeling", "comfyui", "character_generation"],
                specialization="Character Assets",
                status=AgentStatus.IDLE
            ),

            # BMAD Agents
            Agent(
                name="BMAD Backend",
                tier=AgentTier.BMAD,
                workspace="ziggie",
                skills=["fastapi", "database_design", "api_development"],
                specialization="Backend Engineering",
                team="BMAD",
                status=AgentStatus.IDLE
            ),

            # Elite Agents
            Agent(
                name="ARTEMIS",
                tier=AgentTier.ELITE,
                workspace="ziggie",
                skills=["visual_direction", "art_leadership"],
                specialization="Visual Direction",
                team="Elite-Art",
                status=AgentStatus.IDLE
            ),

            # Add remaining agents...
        ]

        for agent in agents:
            db.add(agent)
        await db.commit()
        print(f"Seeded {len(agents)} agents")

asyncio.run(seed_agents())
```

### Step 2: Create Agent API

```python
# C:\Ziggie\control-center\backend\api\agents_registry.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db
from database.models import Agent, AgentTier
from sqlalchemy import select, func

router = APIRouter(prefix="/api/agents", tags=["Agent Registry"])

@router.get("/")
async def list_agents(
    tier: str = None,
    workspace: str = None,
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    """List agents with optional filters"""
    query = select(Agent)

    if tier:
        query = query.where(Agent.tier == AgentTier[tier.upper()])
    if workspace:
        query = query.where(Agent.workspace == workspace)
    if status:
        query = query.where(Agent.status == status)

    result = await db.execute(query)
    agents = result.scalars().all()

    return {
        "agents": [
            {
                "id": a.id,
                "name": a.name,
                "tier": a.tier.value,
                "workspace": a.workspace,
                "skills": a.skills,
                "status": a.status.value,
                "team": a.team,
                "workload": f"{a.workload_percentage}%"
            }
            for a in agents
        ],
        "count": len(agents)
    }

@router.get("/stats")
async def agent_statistics(db: AsyncSession = Depends(get_db)):
    """Get agent statistics"""
    # Count by tier
    tier_counts = await db.execute(
        select(Agent.tier, func.count(Agent.id)).group_by(Agent.tier)
    )

    # Count by workspace
    workspace_counts = await db.execute(
        select(Agent.workspace, func.count(Agent.id)).group_by(Agent.workspace)
    )

    # Count by status
    status_counts = await db.execute(
        select(Agent.status, func.count(Agent.id)).group_by(Agent.status)
    )

    return {
        "by_tier": {tier.value: count for tier, count in tier_counts},
        "by_workspace": {ws: count for ws, count in workspace_counts},
        "by_status": {status.value: count for status, count in status_counts},
        "total": await db.scalar(select(func.count(Agent.id)))
    }

# Register in main.py
# app.include_router(agents_registry.router)
```

---

## PHASE 5: VALIDATION & TESTING (10 minutes)

### Step 1: Test Full Stack

```bash
# 1. Test MCP Gateway
curl http://localhost:8080/api/mcp/tools
curl http://localhost:8080/api/mcp/health

# 2. Test Workspace Registry
curl http://localhost:8080/api/workspaces
curl http://localhost:8080/api/workspaces/Ziggie

# 3. Test Agent Registry
curl http://localhost:8080/api/agents?tier=L1
curl http://localhost:8080/api/agents/stats

# 4. Test Service Discovery (Consul)
curl http://localhost:8500/v1/catalog/services

# 5. Test Metrics (Prometheus)
curl http://localhost:9090/api/v1/query?query=up
```

### Step 2: Register Services with Consul

```python
# C:\Ziggie\control-center\backend\scripts\register_services.py

from services.service_discovery import ServiceDiscovery

sd = ServiceDiscovery(consul_host="localhost", consul_port=8500)

# Register Ziggie Control Center
sd.register_service(
    service_name="ziggie-control-center",
    service_id="ziggie-cc-1",
    address="localhost",
    port=8080,
    tags=["api", "master-command-center"]
)

# Register ComfyUI MCP
sd.register_service(
    service_name="comfyui-mcp",
    service_id="comfyui-1",
    address="localhost",
    port=8188,
    tags=["mcp", "ai-generation"]
)

# Register Ollama (Local LLM)
sd.register_service(
    service_name="ollama-mcp",
    service_id="ollama-1",
    address="localhost",
    port=11434,
    tags=["mcp", "llm"]
)

print("Services registered with Consul")
```

---

## VERIFICATION CHECKLIST

```text
□ Kong API Gateway running (port 8001 admin, 8000 proxy)
□ Consul service discovery running (port 8500 UI)
□ Prometheus metrics collection running (port 9090)
□ Grafana dashboards running (port 3000)

□ MCP Gateway API responding (/api/mcp/tools)
□ Workspace Registry API responding (/api/workspaces)
□ Agent Registry API responding (/api/agents)

□ Database tables created (workspaces, agents)
□ Seed data loaded (5 workspaces, 20+ agents)

□ Services registered in Consul
□ Metrics being collected by Prometheus

□ All health checks passing
```

---

## NEXT STEPS

After completing this quick start:

1. **Configure Kong Gateway Routes**
   - Route workspace traffic through Kong
   - Add rate limiting and authentication

2. **Setup Distributed Tracing**
   - Install Jaeger
   - Instrument FastAPI with OpenTelemetry

3. **Deploy Agent Communication Bus**
   - Implement pub/sub messaging
   - Add agent coordination logic

4. **Create Grafana Dashboards**
   - Import master command center dashboard
   - Setup alerts for degraded services

---

## TROUBLESHOOTING

### Kong Won't Start
```bash
# Check if port 8000/8001 already in use
netstat -ano | findstr "8000"

# Kill conflicting process
taskkill /PID <PID> /F

# Restart Kong
kong restart
```

### Consul Connection Refused
```bash
# Verify Consul is running
consul members

# Check if port 8500 is open
curl http://localhost:8500/v1/status/leader

# Restart Consul
consul leave
consul agent -dev -ui
```

### Database Migration Fails
```bash
# Delete existing database
rm C:/Ziggie/control-center/backend/control_center.db

# Recreate from scratch
python scripts/init_db.py
```

---

**Time to Complete:** 1-2 hours
**Difficulty:** Intermediate
**Support:** Refer to main integration strategy document for detailed explanations
