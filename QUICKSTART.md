# Ziggie - Quick Start Guide

**Get up and running in 5 minutes**

---

## Prerequisites

Before you begin, ensure you have:

- ✅ Python 3.11 or higher
- ✅ Node.js 20 or higher
- ✅ Git
- ✅ 10GB free disk space
- ✅ (Optional) Docker for ComfyUI

---

## Installation

### Step 1: Create Ziggie Directory

```bash
# Create directory
mkdir C:\Ziggie
cd C:\Ziggie

# Create basic structure
mkdir agents control-center game shared tests docs data
```

### Step 2: Install Control Center Backend

```bash
cd control-center\backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn sqlalchemy alembic anthropic pydantic python-dotenv

# Create .env file
copy .env.example .env

# Edit .env and add your API keys:
# ANTHROPIC_API_KEY=your_key_here
# YOUTUBE_API_KEY=your_key_here
```

### Step 3: Install Control Center Frontend

```bash
cd ..\frontend

# Install dependencies
npm install

# Create .env file
echo VITE_API_URL=http://localhost:8000 > .env.local
```

### Step 4: Start Services

```bash
# Terminal 1 - Backend
cd control-center\backend
venv\Scripts\activate
uvicorn main:app --reload

# Terminal 2 - Frontend
cd control-center\frontend
npm run dev
```

### Step 5: Access Control Center

Open browser to: http://localhost:5173

---

## First Tasks

### 1. Explore the Dashboard

- Navigate to http://localhost:5173
- View agent list
- Check knowledge base status
- Review system health

### 2. Invoke Your First Agent

```bash
cd C:\Ziggie\agents

# Create L1 agents directory
mkdir L1-agents

# Copy an agent file (from your existing setup)
# Example: 01_ART_DIRECTOR_AGENT.md

# Open in Claude Code and load the agent
# Give it a task: "Review color palette for game"
```

### 3. Generate Your First Asset

Via Control Center UI:
1. Go to Assets → Generate
2. Enter prompt: "cute warrior cat with sword"
3. Set name: "warrior_cat"
4. Choose category: "unit"
5. Click Generate
6. Wait 2-5 minutes
7. Download result

### 4. Check Knowledge Base

```bash
cd agents\knowledge-base

# View creator database
type metadata\creator-database.json

# Check routing rules
type metadata\routing-rules.json
```

---

## Common Commands

### Control Center

```bash
# Start backend
cd control-center\backend
uvicorn main:app --reload

# Start frontend
cd control-center\frontend
npm run dev

# Run tests
cd control-center\backend
pytest

# Database migration
alembic upgrade head
```

### Game Backend

```bash
# Start game backend
cd game\backend
uvicorn main:app --reload --port 8001

# Run game tests
pytest
```

### Knowledge Base

```bash
# Manual scan
cd agents\knowledge-base
python src\video_scanner.py --creator "InstaSD"

# Process all creators
python src\scheduler.py

# View logs
type logs\pipeline.log
```

---

## Directory Overview

```
C:\Ziggie\
├── agents/              # AI agents & knowledge base
├── control-center/      # Web management UI
├── game/               # Meow Ping RTS
├── shared/             # Scripts & configs
├── tests/              # All tests
├── docs/               # Documentation
└── data/               # Databases & logs
```

---

## Key Files

### Configuration

```
control-center/backend/.env          # Backend config
control-center/frontend/.env.local   # Frontend config
agents/knowledge-base/metadata/      # KB configuration
```

### Documentation

```
README.md                            # Main overview
DIRECTORY_STRUCTURE.md               # Complete structure
ARCHITECTURE.md                      # System architecture
agents/docs/AGENT_DISPATCH.md        # How to use agents
```

### Entry Points

```
control-center/backend/main.py       # Backend app
control-center/frontend/src/main.tsx # Frontend app
game/backend/main.py                 # Game backend
```

---

## Troubleshooting

### Control Center won't start

```bash
# Check Python version
python --version  # Should be 3.11+

# Check if ports are available
netstat -ano | findstr :8000  # Backend
netstat -ano | findstr :5173  # Frontend

# Reinstall dependencies
cd control-center\backend
pip install -r requirements.txt --force-reinstall
```

### Frontend shows errors

```bash
# Clear cache
cd control-center\frontend
rm -rf node_modules
npm install

# Check API connection
curl http://localhost:8000/health
```

### Knowledge Base not working

```bash
# Check API keys
cd agents\knowledge-base
type .env

# Test API connection
python -c "import anthropic; print(anthropic.__version__)"

# Check YouTube API
python src\video_scanner.py --test
```

---

## Next Steps

Once you're up and running:

1. **Read the Architecture** - `ARCHITECTURE.md`
2. **Set up Agents** - Copy agents from meowping-rts
3. **Configure Knowledge Base** - Add your YouTube creators
4. **Deploy Game** - Set up game backend/frontend
5. **Run Tests** - Verify everything works

---

## Support

- **Documentation:** `docs/`
- **Issues:** Create GitHub issue
- **Questions:** Check `docs/guides/troubleshooting.md`

---

**You're ready to go! 🚀**

Next: Read `ARCHITECTURE.md` for a deep dive into the system.
