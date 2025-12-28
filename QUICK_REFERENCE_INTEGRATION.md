# Quick Reference: Ziggie × AI-Game-Dev-System Integration

> **1-Page Cheat Sheet** - Print this!

---

## What Gets Integrated

```
ai-game-dev-system  →  Ziggie
─────────────────────────────────
7 MCP Servers       →  MCP Gateway Router
15 Elite Agents     →  Elite Agents Directory
100+ KB Files       →  Knowledge Base Sync
1,265 Sprites       →  Asset Library
500K+ Words         →  Searchable Index
```

---

## 4-Week Plan

| Week | Focus | Hours | Key Deliverable |
|------|-------|-------|-----------------|
| 1 | Foundation | 20-25 | Gateway + Agents + KB |
| 2 | Asset Pipeline | 25-30 | Generate 10 sprites in 5min |
| 3 | Multi-Engine | 20-25 | Import to Unity/Unreal/Godot |
| 4 | Research | 15-20 | Deploy 6-8 research agents |

---

## Quick Start Commands

### Week 1: Foundation
```bash
cd C:/Ziggie
mkdir -p mcp-gateway elite-agents knowledge-base-sync knowledge-base/ai-game-dev

# Import elite agents
python elite-agents/importer.py

# Sync knowledge base
python knowledge-base-sync/sync.py

# Start gateway
python mcp-gateway/server.py
```

### Week 2: Asset Pipeline
```bash
# Test ComfyUI connection
curl http://localhost:8188/system_stats

# Generate test batch
python asset-pipeline/orchestrator.py --batch test.json --quality AA

# Check quality
python asset-pipeline/quality_gates.py --image output.png
```

### Week 3: Multi-Engine
```bash
# Import to all engines
python mcp-gateway/session_manager.py --test import_all_engines --file sprite.png

# Health check all
curl http://localhost:8000/health
```

### Week 4: Research
```bash
# Deploy research wave
python research-agents/orchestrator.py --wave 1 --topics research-topics.json

# Query knowledge
python knowledge-base/query.py "ComfyUI workflows"
```

---

## Directory Structure

```
C:/Ziggie/
├── mcp-gateway/
│   ├── server.py              # Main gateway server
│   ├── services.json          # MCP server registry
│   └── agent_mappings.json    # Agent → Tool mappings
│
├── asset-pipeline/
│   ├── orchestrator.py        # Asset generation workflow
│   ├── quality_gates.py       # AAA/AA/A classifier
│   └── comfyui_client.py      # ComfyUI API wrapper
│
├── elite-agents/
│   └── source/                # 15 imported agents
│       ├── artemis.agent.md
│       ├── hephaestus.agent.md
│       └── ... (13 more)
│
├── knowledge-base/
│   └── ai-game-dev/           # 100+ synced files
│       ├── index.json
│       └── knowledge_graph.json
│
└── knowledge-base-sync/
    └── sync.py                # Daily sync script
```

---

## MCP Server Registry

| Server | Type | Port/Command | Purpose |
|--------|------|--------------|---------|
| Unity | HTTP | 8080 | Unity Editor control (18 tools) |
| Unreal | stdio | uv run ... | Unreal Engine (40+ tools) |
| Godot | stdio | node ... | Godot Editor |
| ComfyUI | HTTP | 8188 | SDXL image generation |
| AWS GPU | HTTP | 9001 | On-demand cloud GPU |
| Local LLM | HTTP | 1234 | LM Studio/Ollama |
| SimStudio | HTTP | 3001 | Visual workflows |

---

## Elite Agents Map

| Agent | Specialty | Primary MCP Tools |
|-------|-----------|-------------------|
| ARTEMIS | Art Director | ComfyUI, Quality Gate |
| HEPHAESTUS | Tech Art | Blender, All Engines |
| LEONIDAS | Character | ComfyUI, Blender, Unity |
| GAIA | Environment | ComfyUI, Unreal |
| PROMETHEUS | Game Design | All Engines |
| IRIS | UI/UX | Unity, Unreal |
| ... (9 more) | ... | ... |

---

## Configuration Files

### services.json
```json
{
  "unity": {"url": "http://localhost:8080/mcp", "type": "http"},
  "unreal": {"command": ["uv", "run", "..."], "type": "stdio"},
  "comfyui": {"url": "http://localhost:8188", "type": "http"}
}
```

### agent_mappings.json
```json
{
  "CHARACTER_PIPELINE_AGENT": {
    "elite_agent": "LEONIDAS",
    "primary_tools": ["comfyui", "unity", "blender"]
  }
}
```

### .env
```bash
AI_GAME_DEV_PATH=C:/ai-game-dev-system
ZIGGIE_PATH=C:/Ziggie
UNITY_MCP_URL=http://localhost:8080/mcp
COMFYUI_URL=http://localhost:8188
AWS_COST_LIMIT=50.00
```

---

## Cost Breakdown

### Always-On (Free)
- Gateway, Unity, Unreal, Godot MCP: **$0**
- ComfyUI (local or free tier): **$0**
- Local LLM: **$0**

### On-Demand
- AWS GPU g4dn.xlarge (spot): **$0.16/hr**
  - ~10 hours/month = **$1.60/month**
- AWS S3 (20GB sprites): **$0.46/month**
- Meshy.ai (optional, >200/mo): **$16/month**

**Total**: **$2-18/month**

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Gateway Uptime | >95% |
| Asset Gen Speed | <30s AAA sprite set |
| Multi-Engine Import | >90% success |
| Knowledge Files | >150 |
| Agent Response Time | <5s |

---

## Workflow Example: Generate 10 AAA Sprites

```
Step 1: Start AWS GPU        ⏱️ 2min   → aws_gpu MCP
Step 2: Generate concepts     ⏱️ 50s    → comfyui MCP
Step 3: Quality gate check    ⏱️ 5s     → ziggie internal
Step 4: Render 8-directions   ⏱️ 2min   → blender on AWS
Step 5: Import to Unity       ⏱️ 10s    → unity MCP
Step 6: Stop AWS GPU          ⏱️ 1min   → aws_gpu MCP
─────────────────────────────────────────────────────
Total: ~6 minutes for 8 AAA sprite sets
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Gateway won't start | Check Python 3.10+, install deps |
| MCP not connecting | Verify server running, check health endpoint |
| Asset gen fails | Check ComfyUI running, models downloaded |
| Import fails | Verify engine open, test individually |

---

## Health Checks

```bash
# Gateway
curl http://localhost:8000/health

# Unity MCP
curl http://localhost:8080/mcp/health

# ComfyUI
curl http://localhost:8188/system_stats

# All services
curl http://localhost:8000/services
```

---

## Dependencies

```bash
# Core
pip install fastmcp httpx asyncio aiohttp

# Asset Pipeline
pip install opencv-python numpy pillow boto3

# Knowledge Base
pip install markdown beautifulsoup4

# Optional
pip install discord-webhook networkx
```

---

## Testing Checklist

### Week 1
- [ ] Gateway starts without errors
- [ ] Health checks work for ≥3 services
- [ ] 15 elite agents imported
- [ ] 100+ KB files synced
- [ ] Basic routing test passes

### Week 2
- [ ] Generate 1 sprite (Tier 2)
- [ ] Generate 10 sprites batch
- [ ] Quality gate classifies correctly
- [ ] AWS GPU starts/stops
- [ ] Blender renders 8-dir

### Week 3
- [ ] Import sprite to Unity
- [ ] Import sprite to Unreal
- [ ] Import sprite to Godot
- [ ] Parallel import works
- [ ] Cross-engine comparison

### Week 4
- [ ] Deploy 6 research agents
- [ ] Generate 20+ new KB files
- [ ] Knowledge graph built
- [ ] Agent query returns results

---

## Quick Wins (Day 1)

1. **Knowledge Base** (2 hours)
   ```bash
   python knowledge-base-sync/sync.py
   ```
   → Gain 500K+ words expertise

2. **Elite Agents** (4 hours)
   ```bash
   python elite-agents/importer.py
   ```
   → Gain 15 specialized agents

3. **Asset Library** (1 hour)
   ```bash
   cp -r C:/ai-game-dev-system/assets/ai-generated/* C:/Ziggie/assets/imported/
   ```
   → Gain 1,265 sprites

---

## ROI

| Investment | Return |
|------------|--------|
| 80-100 hours over 4 weeks | 10x capability increase |
| $0-18/month cost | Replace 30+ specialist roles |
| Low risk (proven patterns) | 6-min workflow for AAA assets |

**Breakeven**: Week 2 (asset pipeline alone justifies integration)

---

## Next Steps

### Option A: Full Integration (Recommended)
1. Week 1: Foundation (20-25h)
2. Week 2: Asset Pipeline (25-30h)
3. Week 3: Multi-Engine (20-25h)
4. Week 4: Research (15-20h)

### Option B: Quick Win Only
1. Import elite agents (4h)
2. Sync knowledge base (2h)
3. Test query system (1h)
4. **Stop** - evaluate value

### Option C: Asset Pipeline Only
1. Week 1: Foundation (20-25h)
2. Week 2: Asset Pipeline (25-30h)
3. **Stop** - evaluate value
4. Continue if valuable

---

## Documentation

- **Full Details**: `ZIGGIE_AI_GAME_DEV_INTEGRATION_BRAINSTORM.md`
- **Step-by-Step**: `MCP_GATEWAY_IMPLEMENTATION_CHECKLIST.md`
- **Visual Diagrams**: `MCP_GATEWAY_ARCHITECTURE_DIAGRAM.md`
- **Overview**: `INTEGRATION_SUMMARY.md`
- **This Sheet**: `QUICK_REFERENCE_INTEGRATION.md`

---

## Support

- ai-game-dev-system: `C:/ai-game-dev-system/`
- Unity MCP: https://github.com/CoderGamester/mcp-unity
- Unreal MCP: https://github.com/chongdashu/unreal-mcp
- FastMCP: https://github.com/jlowin/fastmcp

---

**Print this page and keep it handy during implementation!**

**Last Updated**: 2025-12-21
**Version**: 1.0
