# MCP Gateway Implementation Checklist
## Ziggie × AI-Game-Dev-System Integration

> **Quick Start Guide for Implementation**
> **Estimated Time**: 4 weeks (1 week per phase)

---

## Phase 1: Foundation (Week 1) ⏱️ 20-25 hours

### Directory Structure Setup
```bash
cd C:/Ziggie

# Create new directories
mkdir -p mcp-gateway
mkdir -p asset-pipeline
mkdir -p elite-agents/source
mkdir -p knowledge-base-sync
mkdir -p knowledge-base/ai-game-dev

# Create placeholder files
touch mcp-gateway/server.py
touch mcp-gateway/router.py
touch mcp-gateway/health_monitor.py
touch mcp-gateway/services.json
touch mcp-gateway/agent_mappings.json
```

### Task List

- [ ] **1.1 Create MCP Gateway Skeleton** (4 hours)
  - [ ] Create `mcp-gateway/server.py` with FastMCP setup
  - [ ] Implement basic health check endpoint
  - [ ] Add service registry loading from JSON
  - [ ] Test basic server startup

- [ ] **1.2 Configure Service Registry** (2 hours)
  - [ ] Create `services.json` with all 7 MCP server definitions
  - [ ] Add Unity MCP (HTTP, port 8080)
  - [ ] Add Unreal MCP (stdio, Python)
  - [ ] Add Godot MCP (stdio, Node.js)
  - [ ] Add ComfyUI (HTTP, port 8188)
  - [ ] Add AWS GPU (HTTP, port 9001)
  - [ ] Add Local LLM (HTTP, port 1234 or 11434)
  - [ ] Add SimStudio (HTTP, port 3001)

- [ ] **1.3 Implement Health Monitor** (4 hours)
  - [ ] Create `health_monitor.py`
  - [ ] Add async health check for HTTP services
  - [ ] Add process check for stdio services
  - [ ] Implement 30-second interval loop
  - [ ] Log health status to file
  - [ ] Add Discord webhook for down alerts (optional)

- [ ] **1.4 Import Elite Agents** (6 hours)
  - [ ] Copy `.github/agents/` from ai-game-dev-system
  - [ ] Parse 15 agent markdown files
  - [ ] Extract: name, model, tools, philosophy, expertise
  - [ ] Convert to Ziggie agent format
  - [ ] Save to `elite-agents/` directory
  - [ ] Create index file mapping agents to specialties

- [ ] **1.5 Sync Knowledge Base** (4 hours)
  - [ ] Create `knowledge-base-sync/sync.py`
  - [ ] Implement one-way sync from ai-game-dev-system
  - [ ] Copy all 100+ markdown files
  - [ ] Build searchable index (title, tags, word count)
  - [ ] Save index as `knowledge-base/ai-game-dev/index.json`
  - [ ] Test search functionality

- [ ] **1.6 Test Basic Gateway** (2 hours)
  - [ ] Start Unity (if available)
  - [ ] Test health check to Unity MCP
  - [ ] Route simple command through gateway
  - [ ] Verify logging works
  - [ ] Document any issues

**Phase 1 Deliverables**:
- ✅ Gateway server running
- ✅ Health monitoring active
- ✅ 15 elite agents imported
- ✅ 100+ knowledge base files synced
- ✅ Basic routing functional

---

## Phase 2: Asset Pipeline (Week 2) ⏱️ 25-30 hours

### Task List

- [ ] **2.1 ComfyUI Integration** (6 hours)
  - [ ] Create `asset-pipeline/comfyui_client.py`
  - [ ] Implement HTTP API wrapper for ComfyUI
  - [ ] Add queue_prompt(), get_image(), check_status()
  - [ ] Test batch generation (10 images)
  - [ ] Handle errors gracefully

- [ ] **2.2 Asset Orchestrator** (8 hours)
  - [ ] Create `asset-pipeline/orchestrator.py`
  - [ ] Implement 3-tier selection logic (AAA/AA/A)
  - [ ] Add batch processing queue
  - [ ] Build prompt templates for units/buildings/props
  - [ ] Add progress tracking
  - [ ] Implement retry logic for failures

- [ ] **2.3 Quality Gate System** (6 hours)
  - [ ] Create `asset-pipeline/quality_gates.py`
  - [ ] Implement silhouette clarity check (resize to 32px, edge detection)
  - [ ] Add color palette matching (compare to style guide)
  - [ ] Implement detail level scoring
  - [ ] Add lighting direction check
  - [ ] Output AAA/AA/A/Poor classification

- [ ] **2.4 AWS GPU On-Demand** (4 hours)
  - [ ] Create `asset-pipeline/aws_control.py`
  - [ ] Implement start_instance() with boto3
  - [ ] Add stop_instance()
  - [ ] Implement cost tracking
  - [ ] Add hard limit ($50/month)
  - [ ] Test spot instance launch

- [ ] **2.5 Blender Render Integration** (3 hours)
  - [ ] Create `asset-pipeline/blender_render.py`
  - [ ] Add 8-direction isometric render script
  - [ ] Implement headless Blender execution
  - [ ] Test sprite sheet generation
  - [ ] Add error handling

- [ ] **2.6 Import Existing Assets** (2 hours)
  - [ ] Copy 1,265 sprites from ai-game-dev-system
  - [ ] Organize by quality tier
  - [ ] Create asset manifest JSON
  - [ ] Test import to Unity/Unreal/Godot

**Phase 2 Deliverables**:
- ✅ Generate 10 AA-quality sprites in <5 minutes
- ✅ Quality gate classifies with >80% accuracy
- ✅ AWS GPU launches on demand
- ✅ Blender renders 8-direction sprites
- ✅ 1,265 existing assets imported

---

## Phase 3: Multi-Engine Support (Week 3) ⏱️ 20-25 hours

### Task List

- [ ] **3.1 Unity MCP Connection** (4 hours)
  - [ ] Configure Unity MCP server (HTTP, port 8080)
  - [ ] Start Unity Editor with MCP package
  - [ ] Test basic commands (create cube, play scene)
  - [ ] Add to gateway router
  - [ ] Document connection setup

- [ ] **3.2 Unreal MCP Connection** (4 hours)
  - [ ] Configure Unreal MCP server (stdio, Python)
  - [ ] Start Unreal Engine 5.7
  - [ ] Enable UnrealMCP plugin
  - [ ] Test basic commands (spawn actor, compile blueprint)
  - [ ] Add to gateway router

- [ ] **3.3 Godot MCP Connection** (4 hours)
  - [ ] Configure Godot MCP server (stdio, Node.js)
  - [ ] Start Godot Editor
  - [ ] Test basic commands (create node, save scene)
  - [ ] Add to gateway router

- [ ] **3.4 Session Manager** (6 hours)
  - [ ] Create `mcp-gateway/session_manager.py`
  - [ ] Implement MultiEngineSessions class
  - [ ] Add broadcast_command() for parallel execution
  - [ ] Implement import_asset_to_all_engines()
  - [ ] Add connection pooling
  - [ ] Handle engine-specific parameters

- [ ] **3.5 Cross-Engine Testing** (4 hours)
  - [ ] Import same sprite to all 3 engines
  - [ ] Compare rendering quality
  - [ ] Test performance in each engine
  - [ ] Document differences
  - [ ] Create comparison report

- [ ] **3.6 Workflow Automation** (2 hours)
  - [ ] Create multi-step workflow JSON templates
  - [ ] Test: ComfyUI → Unity import workflow
  - [ ] Test: Blender → Unreal import workflow
  - [ ] Add workflow validation

**Phase 3 Deliverables**:
- ✅ Unity, Unreal, Godot all connected
- ✅ Parallel import to 3 engines works
- ✅ Session manager handles connections
- ✅ 5+ workflows automated

---

## Phase 4: Research Integration (Week 4) ⏱️ 15-20 hours

### Task List

- [ ] **4.1 Research Orchestrator** (5 hours)
  - [ ] Create `research-agents/orchestrator.py`
  - [ ] Implement wave-based deployment (6-8 agents)
  - [ ] Add topic queue management
  - [ ] Implement parallel execution with asyncio
  - [ ] Add result aggregation

- [ ] **4.2 Define Research Topics** (3 hours)
  - [ ] Create `research-topics.json`
  - [ ] Define Wave 1: Core technical (Unity DOTS, Unreal Nanite, etc.)
  - [ ] Define Wave 2: Specialized (Mobile optimization, VR, etc.)
  - [ ] Define Wave 3: Management (Production, analytics, etc.)
  - [ ] Set deliverables for each topic

- [ ] **4.3 Deploy Research Wave** (4 hours)
  - [ ] Deploy 6-8 research agents in parallel
  - [ ] Monitor progress
  - [ ] Collect results
  - [ ] Verify quality of research output
  - [ ] Add to knowledge base

- [ ] **4.4 Knowledge Graph** (4 hours)
  - [ ] Build graph from 100+ existing files
  - [ ] Add relationships between topics
  - [ ] Implement query interface for agents
  - [ ] Create visualization (optional)
  - [ ] Test agent knowledge lookup

- [ ] **4.5 Agent Query System** (3 hours)
  - [ ] Create `knowledge-base/query.py`
  - [ ] Implement semantic search
  - [ ] Add tag-based filtering
  - [ ] Test: "Find all ComfyUI workflow examples"
  - [ ] Integrate with elite agents

**Phase 4 Deliverables**:
- ✅ Research orchestrator working
- ✅ 20+ new knowledge base files
- ✅ Knowledge graph built
- ✅ Agent query system functional

---

## Testing Checklist

### Gateway Tests
- [ ] Health checks work for all 7 services
- [ ] Routing to HTTP services (Unity, ComfyUI, AWS)
- [ ] Routing to stdio services (Unreal, Godot)
- [ ] Error handling when service is down
- [ ] Graceful degradation
- [ ] Logging captures all requests

### Asset Pipeline Tests
- [ ] Generate 1 sprite (Tier 2)
- [ ] Generate 10 sprites batch (Tier 2)
- [ ] Generate 1 AAA sprite (Tier 3 with Blender)
- [ ] Quality gate classification accuracy
- [ ] AWS GPU starts and stops correctly
- [ ] Cost tracking accurate

### Multi-Engine Tests
- [ ] Import sprite to Unity
- [ ] Import sprite to Unreal
- [ ] Import sprite to Godot
- [ ] Parallel import to all 3
- [ ] Cross-engine quality comparison
- [ ] Workflow execution (5+ steps)

### Knowledge Base Tests
- [ ] Search for "ComfyUI workflows"
- [ ] Search for "Blender rendering"
- [ ] Agent query returns relevant files
- [ ] Index updates when files added
- [ ] Full-text search works

---

## Success Criteria

### Phase 1 Success
- ✅ Gateway server runs without crashes for 24 hours
- ✅ Health checks report status of at least 3 services
- ✅ 15 elite agents imported with all metadata
- ✅ 100+ knowledge base files synced
- ✅ Basic routing test passes

### Phase 2 Success
- ✅ Generate 10 sprites in <10 minutes
- ✅ Quality gate classifies with >70% accuracy
- ✅ AWS GPU launches in <5 minutes
- ✅ Blender renders 8-direction set in <30 seconds
- ✅ 1,265 assets organized and accessible

### Phase 3 Success
- ✅ All 3 game engines connected and responsive
- ✅ Import sprite to all 3 engines in <30 seconds
- ✅ Session manager handles 10+ concurrent requests
- ✅ 5 automated workflows tested
- ✅ Cross-engine comparison report generated

### Phase 4 Success
- ✅ Deploy 6 research agents in parallel
- ✅ Generate 20+ new knowledge base files
- ✅ Knowledge graph contains 150+ nodes
- ✅ Agent query returns results in <2 seconds
- ✅ Research output quality = AAA

---

## Quick Command Reference

### Start Gateway
```bash
cd C:/Ziggie
python mcp-gateway/server.py
```

### Sync Knowledge Base
```bash
python knowledge-base-sync/sync.py
```

### Generate Assets
```bash
python asset-pipeline/orchestrator.py --batch units.json --quality AA
```

### Test Multi-Engine
```bash
python mcp-gateway/session_manager.py --test import_all_engines
```

### Deploy Research
```bash
python research-agents/orchestrator.py --wave 1 --topics research-topics.json
```

---

## Dependencies to Install

```bash
# Core
pip install fastmcp httpx asyncio aiohttp

# Asset Pipeline
pip install opencv-python numpy pillow boto3

# Knowledge Base
pip install markdown beautifulsoup4

# Optional
pip install discord-webhook  # For alerts
pip install networkx          # For knowledge graph
```

---

## Configuration Files

### 1. services.json
```json
{
  "unity": {
    "url": "http://localhost:8080/mcp",
    "type": "http",
    "timeout": 30
  },
  "unreal": {
    "command": ["uv", "run", "C:/ai-game-dev-system/mcp-servers/unreal-mcp/Python/unreal_mcp_server.py"],
    "type": "stdio",
    "timeout": 60
  },
  "godot": {
    "command": ["node", "C:/ai-game-dev-system/mcp-servers/godot-mcp/server/dist/index.js"],
    "type": "stdio",
    "timeout": 30
  },
  "comfyui": {
    "url": "http://localhost:8188",
    "type": "http",
    "timeout": 120
  },
  "aws_gpu": {
    "url": "http://localhost:9001",
    "type": "http",
    "timeout": 300
  },
  "local_llm": {
    "url": "http://localhost:1234",
    "type": "http",
    "timeout": 60
  },
  "simstudio": {
    "url": "http://localhost:3001",
    "type": "http",
    "timeout": 30
  }
}
```

### 2. agent_mappings.json
```json
{
  "CHARACTER_PIPELINE_AGENT": {
    "elite_agent": "LEONIDAS",
    "primary_tools": ["comfyui", "unity", "blender"],
    "knowledge_base": [
      "knowledge-base/ai-game-dev/CHARACTER_DESIGN_SYSTEMS.md",
      "knowledge-base/ai-game-dev/GAME_ANIMATION_PRINCIPLES.md"
    ]
  },
  "ART_DIRECTOR_AGENT": {
    "elite_agent": "ARTEMIS",
    "primary_tools": ["comfyui", "quality_gate"],
    "knowledge_base": [
      "knowledge-base/ai-game-dev/style-guides/AAA-ART-DIRECTION-BEST-PRACTICES-2024-2025.md",
      "knowledge-base/ai-game-dev/GAME-ART-FUNDAMENTALS.md"
    ]
  }
}
```

### 3. .env (Environment Variables)
```bash
# Paths
AI_GAME_DEV_PATH=C:/ai-game-dev-system
ZIGGIE_PATH=C:/Ziggie

# MCP Servers
UNITY_MCP_URL=http://localhost:8080/mcp
COMFYUI_URL=http://localhost:8188

# AWS
AWS_REGION=us-east-1
AWS_COST_LIMIT=50.00

# Optional
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
LOG_LEVEL=INFO
```

---

## Troubleshooting

### Gateway won't start
1. Check Python version (3.10+)
2. Install dependencies: `pip install -r requirements.txt`
3. Check port conflicts: `netstat -ano | findstr :8080`

### MCP server not connecting
1. Verify server is running
2. Check health endpoint manually: `curl http://localhost:8080/health`
3. Review logs in `mcp-gateway/logs/`

### Asset generation fails
1. Check ComfyUI is running: `curl http://localhost:8188/system_stats`
2. Verify models are downloaded
3. Check disk space

### Multi-engine import fails
1. Verify all engines are open
2. Check engine versions match requirements
3. Test each engine individually first

---

## Next Steps After Completion

1. **Integrate with Control Center UI**
   - Add gateway status dashboard
   - Show MCP server health
   - Display asset generation queue

2. **Add More Elite Agents**
   - Expand beyond initial 15
   - Create custom agents for specific workflows

3. **Scale Asset Pipeline**
   - Generate 100+ sprites per batch
   - Implement priority queue
   - Add parallel GPU instances

4. **Build Agent Marketplace**
   - Share elite agent definitions
   - Community-contributed workflows
   - Pre-trained models

---

**Document Version**: 1.0
**Last Updated**: 2025-12-21
**Estimated Total Time**: 80-100 hours (4 weeks @ 20-25 hours/week)
**Success Rate**: High (proven patterns from ai-game-dev-system)
