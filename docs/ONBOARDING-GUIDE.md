# Ziggie Onboarding Guide

> **Getting Started with the Ziggie AI Development Ecosystem**
> **Time to Complete**: 30 minutes
> **Last Updated**: 2025-12-28

---

## Welcome to Ziggie

Ziggie is an AI-controlled development ecosystem for game development projects. It orchestrates multiple AI agents, MCP (Model Context Protocol) servers, and cloud infrastructure to enable automated game asset generation, knowledge management, and development workflows.

### What You'll Learn

1. Understanding the Ziggie architecture
2. Setting up your development environment
3. Starting the core services
4. Navigating the Control Center
5. Working with AI agents
6. Generating game assets

---

## First 5 Minutes: Understanding the Architecture

### Key Workspaces

| Workspace | Path | Purpose |
|-----------|------|---------|
| **Ziggie** | `C:\Ziggie` | Core orchestration, API, MCP gateway |
| **AI Game Dev System** | `C:\ai-game-dev-system` | Knowledge base, asset pipelines |
| **MeowPing RTS** | `C:\meowping-rts` | Game frontend and backend |
| **Team Ziggie** | `C:\team-ziggie` | Agent configurations |

### Agent Hierarchy (1,884 Total)

```
L0: Executive (MAXIMUS)       --> Strategic decisions
L1: Directors (12 agents)     --> Department heads
L2: Specialists (144 agents)  --> Domain experts
L3: Workers (1,728 agents)    --> Task execution
```

### Core Services

| Service | Port | Purpose |
|---------|------|---------|
| Control Center Backend | 54112 | API gateway |
| Control Center Frontend | 3000 | Dashboard UI |
| ComfyUI | 8188 | AI image generation |
| Ollama | 11434 | Local LLM inference |

---

## Minutes 5-15: Environment Setup

### Prerequisites

Ensure you have installed:

- [x] Python 3.11+
- [x] Node.js 18+
- [x] Git with Git LFS
- [x] Docker Desktop (optional but recommended)

### Step 1: Clone or Navigate to Repository

```bash
cd C:\Ziggie
```

### Step 2: Verify Git LFS

Git LFS is configured for game assets. Verify it's working:

```bash
git lfs install
git lfs ls-files  # Should list tracked large files
```

### Step 3: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\activate  # Windows

# Install backend dependencies
pip install -r control-center/backend/requirements.txt
```

### Step 4: Install Frontend Dependencies

```bash
cd control-center/frontend
npm install
cd ../..
```

### Step 5: Verify MCP Configuration

Check that `.mcp.json` exists in the root:

```bash
type .mcp.json
```

This file configures the MCP servers for AI integration.

---

## Minutes 15-20: Starting Core Services

### Quick Start Scripts

Use the provided batch files:

```bash
# Start everything
start_all.bat

# Or start individually:
start_backend.bat   # Backend API
start_frontend.bat  # Dashboard UI
```

### Manual Startup

**Terminal 1: Backend**
```bash
cd C:\Ziggie\control-center\backend
python main.py
```

Expected output:
```
Initializing Control Center backend...
Database initialized
Server starting on http://127.0.0.1:54112
```

**Terminal 2: Frontend**
```bash
cd C:\Ziggie\control-center\frontend
npm run dev
```

Expected output:
```
  - Local:        http://localhost:3000
  - Network:      http://192.168.x.x:3000
```

### Verify Services Running

```bash
# Check backend
curl http://localhost:54112/health

# Check frontend
curl http://localhost:3000
```

---

## Minutes 20-25: Exploring the Control Center

### Access the Dashboard

Open your browser to: **http://localhost:3000**

### Dashboard Sections

| Section | Purpose |
|---------|---------|
| **System Status** | CPU, RAM, disk usage |
| **Services** | Start/stop/restart services |
| **Agents** | View and manage AI agents |
| **Knowledge Base** | Browse documentation |
| **ComfyUI** | AI image generation |

### API Documentation

Interactive API docs: **http://localhost:54112/docs**

---

## Minutes 25-30: First Tasks

### Task 1: Check System Health

Navigate to System Status and verify:
- CPU usage is normal (<80%)
- Memory is available (>20%)
- Disk has space (>10%)

### Task 2: View Agent Hierarchy

Go to Agents section:
1. Browse L1 Directors
2. Explore their L2 Specialists
3. See the full agent architecture

### Task 3: Run a Health Check

Using the terminal:

```bash
curl http://localhost:54112/health/detailed
```

### Task 4: Explore Knowledge Base

Browse the knowledge base at:
- UI: http://localhost:3000/knowledge
- Filesystem: `C:\ai-game-dev-system\knowledge-base\`

---

## Common Tasks Reference

### Starting Services

| Service | Command |
|---------|---------|
| Backend | `python control-center/backend/main.py` |
| Frontend | `cd control-center/frontend && npm run dev` |
| ComfyUI | Start via Control Center or manually |

### Running Tests

```bash
# All tests
python scripts/run_tests.py

# Quick tests
python scripts/run_tests.py --quick

# With coverage
python scripts/run_tests.py --coverage
```

### Git Operations

```bash
# Check status
git status

# Commit changes
git add .
git commit -m "feat: description"

# Push
git push origin master
```

### API Requests

```bash
# Get system stats
curl http://localhost:54112/api/system/stats

# List agents
curl http://localhost:54112/api/agents

# Check service status
curl http://localhost:54112/api/services
```

---

## Key Documentation

| Document | Location | Purpose |
|----------|----------|---------|
| Project CLAUDE.md | `C:\Ziggie\CLAUDE.md` | Project-specific instructions |
| API Documentation | `C:\Ziggie\docs\API-DOCUMENTATION.md` | API reference |
| Cursor IDE Guide | `C:\Ziggie\docs\CURSOR-IDE-GUIDE.md` | IDE setup |
| Ecosystem Status | `C:\Ziggie\ZIGGIE-ECOSYSTEM-MASTER-STATUS-V5.md` | Current state |

---

## Troubleshooting

### Backend Won't Start

1. Check if another instance is running:
   ```bash
   netstat -ano | findstr :54112
   ```

2. Kill existing process:
   ```bash
   taskkill /F /PID <pid>
   ```

3. Check Python dependencies:
   ```bash
   pip install -r control-center/backend/requirements.txt
   ```

### Frontend Won't Start

1. Check Node.js version:
   ```bash
   node --version  # Should be 18+
   ```

2. Clear npm cache:
   ```bash
   npm cache clean --force
   npm install
   ```

### MCP Servers Not Connecting

1. Verify `.mcp.json` configuration
2. Check Node.js is installed
3. Restart the IDE/Cursor

### Port Already in Use

```bash
# Find process using port
netstat -ano | findstr :<port>

# Kill the process
taskkill /F /PID <pid>
```

---

## Next Steps

After completing this onboarding:

1. **Explore the Knowledge Base** - Browse existing documentation at `C:\ai-game-dev-system\knowledge-base\`

2. **Learn Agent Commands** - Review agent skills at `C:\Users\minin\.claude\skills\`

3. **Generate Assets** - Try the `/game-asset-generation` skill

4. **Review Architecture** - Read `ARCHITECTURE.md` for deep dive

5. **Join Development** - Check `ZIGGIE-GAP-RESOLUTION-TRACKING-V5.md` for open tasks

---

## Getting Help

### Resources

| Resource | Location |
|----------|----------|
| Global CLAUDE.md | `C:\Users\minin\.claude\CLAUDE.md` |
| Retrospectives | `C:\Ziggie\docs\retrospective\` |
| Research Docs | `C:\Ziggie\docs\research\` |

### Support Channels

- Check existing documentation first
- Review error logs in console
- Search knowledge base for solutions

---

*Welcome to Ziggie! You're now ready to start developing.*
*Onboarding Guide - Created 2025-12-28*
