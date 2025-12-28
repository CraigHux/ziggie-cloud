# Migration Guide - Moving to C:\Ziggie

**Complete guide for migrating files from meowping-rts and ComfyUI to the new Ziggie structure**

**Version:** 1.0.0
**Last Updated:** 2025-11-07

---

## Overview

This guide will help you migrate existing files from:
- **C:\meowping-rts** → **C:\Ziggie**
- **C:\ComfyUI** → **C:\Ziggie**

---

## Table of Contents

1. [Pre-Migration Checklist](#pre-migration-checklist)
2. [Migration Strategy](#migration-strategy)
3. [Step-by-Step Migration](#step-by-step-migration)
4. [File Mapping Reference](#file-mapping-reference)
5. [Post-Migration Tasks](#post-migration-tasks)
6. [Verification](#verification)
7. [Rollback Plan](#rollback-plan)

---

## Pre-Migration Checklist

### Before You Start

- [ ] **Backup everything** - Copy both directories to a safe location
- [ ] **Stop all services** - Close running applications
- [ ] **Review structure** - Read DIRECTORY_STRUCTURE.md
- [ ] **Check disk space** - Ensure 20GB+ free space
- [ ] **Note custom changes** - Document any modifications
- [ ] **Export databases** - Backup SQLite databases
- [ ] **List API keys** - Document all .env files

### Create Backup

```bash
# Windows
xcopy C:\meowping-rts C:\BACKUP\meowping-rts /E /I /H
xcopy C:\ComfyUI C:\BACKUP\ComfyUI /E /I /H

# Verify backup
dir C:\BACKUP
```

---

## Migration Strategy

### Approach

We'll use a **phased migration** approach:

1. **Phase 1:** Create new structure
2. **Phase 2:** Migrate AI Agents
3. **Phase 3:** Migrate Control Center
4. **Phase 4:** Migrate Game files
5. **Phase 5:** Migrate Shared resources
6. **Phase 6:** Update configurations
7. **Phase 7:** Test & verify

### Estimated Time

- Small project (<1000 files): **30 minutes**
- Medium project (1000-5000 files): **1-2 hours**
- Large project (5000+ files): **2-4 hours**

---

## Step-by-Step Migration

### Phase 1: Create New Structure

```bash
# Create Ziggie root
mkdir C:\Ziggie
cd C:\Ziggie

# Create top-level directories
mkdir agents control-center game shared tests docs data .github

# Create sub-directories
cd agents
mkdir L1-agents L2-agents L3-agents knowledge-base docs

cd ..\control-center
mkdir backend frontend ComfyUI docs

cd ..\game
mkdir backend frontend assets data missions docs

cd ..\shared
mkdir automation configs templates tools

cd ..\tests
mkdir agents control-center game integration performance fixtures mocks

cd ..\docs
mkdir architecture guides api tutorials

cd ..\data
mkdir databases logs cache exports

# Return to root
cd C:\Ziggie
```

### Phase 2: Migrate AI Agents

#### 2.1 Copy L1 Agents

```bash
# Copy L1 agent files
xcopy C:\meowping-rts\ai-agents\*.md C:\Ziggie\agents\L1-agents\ /Y

# Expected files (8 total):
# - 01_ART_DIRECTOR_AGENT.md
# - 02_CHARACTER_PIPELINE_AGENT.md
# - 03_ENVIRONMENT_PIPELINE_AGENT.md
# - 04_GAME_SYSTEMS_DEVELOPER_AGENT.md
# - 05_UI_UX_DEVELOPER_AGENT.md
# - 06_CONTENT_DESIGNER_AGENT.md
# - 07_INTEGRATION_AGENT.md
# - 08_QA_TESTING_AGENT.md

# Verify
dir C:\Ziggie\agents\L1-agents
```

#### 2.2 Copy Knowledge Base

```bash
# Copy entire knowledge base
xcopy C:\meowping-rts\ai-agents\knowledge-base C:\Ziggie\agents\knowledge-base /E /I /H

# Verify structure
dir C:\Ziggie\agents\knowledge-base
dir C:\Ziggie\agents\knowledge-base\metadata
dir C:\Ziggie\agents\knowledge-base\src
```

#### 2.3 Copy Agent Documentation

```bash
# Copy agent docs
xcopy C:\meowping-rts\ai-agents\*.md C:\Ziggie\agents\docs\ /Y

# Specific files:
# - AI_AGENT_TEAM_README.md → agents/docs/
# - AGENT_DISPATCH.md → agents/docs/
# - L3_MICRO_AGENT_ARCHITECTURE.md → agents/docs/
# - SUB_AGENT_ARCHITECTURE.md → agents/docs/
```

### Phase 3: Migrate Control Center

#### 3.1 Copy Control Center Backend

```bash
# Copy backend
xcopy C:\meowping-rts\control-center\backend C:\Ziggie\control-center\backend /E /I /H

# Verify structure
dir C:\Ziggie\control-center\backend\api
dir C:\Ziggie\control-center\backend\database
dir C:\Ziggie\control-center\backend\services
```

#### 3.2 Copy Control Center Frontend

```bash
# Copy frontend
xcopy C:\meowping-rts\control-center\frontend C:\Ziggie\control-center\frontend /E /I /H

# Verify
dir C:\Ziggie\control-center\frontend\src
```

#### 3.3 Copy ComfyUI Integration

```bash
# Copy ComfyUI workflows and configs
mkdir C:\Ziggie\control-center\ComfyUI\workflows
mkdir C:\Ziggie\control-center\ComfyUI\models

xcopy C:\meowping-rts\ComfyUI\workflows C:\Ziggie\control-center\ComfyUI\workflows /E /I

# Copy ComfyUI documentation
xcopy C:\meowping-rts\control-center\*.md C:\Ziggie\control-center\docs\ /Y
```

#### 3.4 Integrate ComfyUI Management Code

```bash
# Copy agent/KB management code from ComfyUI
copy C:\ComfyUI\api_server\routes\agents_routes.py C:\Ziggie\control-center\backend\api\agents.py
copy C:\ComfyUI\api_server\routes\knowledge_routes.py C:\Ziggie\control-center\backend\api\knowledge.py

copy C:\ComfyUI\api_server\services\agent_service.py C:\Ziggie\control-center\backend\services\agent_service.py
copy C:\ComfyUI\api_server\services\knowledge_service.py C:\Ziggie\control-center\backend\services\knowledge_service.py

# Copy database models
copy C:\ComfyUI\alembic_db\versions\*agent*.py C:\Ziggie\control-center\backend\database\
```

### Phase 4: Migrate Game Files

#### 4.1 Copy Game Backend

```bash
# Copy entire backend
xcopy C:\meowping-rts\backend C:\Ziggie\game\backend /E /I /H

# Verify
dir C:\Ziggie\game\backend\app
dir C:\Ziggie\game\backend\auth
dir C:\Ziggie\game\backend\building
```

#### 4.2 Copy Game Frontend

```bash
# Copy frontend
xcopy C:\meowping-rts\frontend C:\Ziggie\game\frontend /E /I /H

# Verify
dir C:\Ziggie\game\frontend\src
```

#### 4.3 Copy Game Assets

```bash
# Copy assets
xcopy C:\meowping-rts\assets C:\Ziggie\game\assets /E /I /H
xcopy C:\meowping-rts\assests C:\Ziggie\game\assets /E /I /H

# Note: meowping-rts has both "assets" and "assests" folders

# Verify
dir C:\Ziggie\game\assets
```

#### 4.4 Copy Game Data

```bash
# Copy data files
xcopy C:\meowping-rts\data C:\Ziggie\game\data /E /I /H

# Copy missions
xcopy C:\meowping-rts\missions C:\Ziggie\game\missions /E /I /H
```

#### 4.5 Copy Game Documentation

```bash
# Copy game-specific docs
copy C:\meowping-rts\COMBAT_*.md C:\Ziggie\game\docs\
copy C:\meowping-rts\UNITS_*.md C:\Ziggie\game\docs\
copy C:\meowping-rts\BUILD_*.md C:\Ziggie\game\docs\
copy C:\meowping-rts\backend\docs\*.md C:\Ziggie\game\docs\
```

### Phase 5: Migrate Shared Resources

#### 5.1 Copy Automation Scripts

```bash
# Copy all .sh scripts
xcopy C:\meowping-rts\*.sh C:\Ziggie\shared\automation\install\ /Y

# Organize by category
# - 00_INSTALL_*.sh → install/
# - phase*.sh → install/
# - install_*.sh → install/
# - master_*.sh → install/
# - verify_*.sh → maintenance/
# - status.sh → maintenance/
```

#### 5.2 Copy Configuration Files

```bash
# Copy Docker configs
copy C:\meowping-rts\docker-compose.yml C:\Ziggie\shared\configs\docker\
copy C:\meowping-rts\Dockerfile C:\Ziggie\shared\configs\docker\

# Copy environment examples
copy C:\meowping-rts\.env.example C:\Ziggie\shared\configs\environment\
copy C:\meowping-rts\control-center\backend\.env.example C:\Ziggie\shared\configs\environment\control-center.env.example
```

#### 5.3 Copy Tools

```bash
# Copy utility scripts
copy C:\meowping-rts\tools\*.py C:\Ziggie\shared\tools\ 2>nul
copy C:\meowping-rts\tools\*.sh C:\Ziggie\shared\tools\ 2>nul
```

### Phase 6: Migrate Tests

```bash
# Copy backend tests
xcopy C:\meowping-rts\backend\tests C:\Ziggie\tests\game\backend /E /I /H

# Copy Control Center tests
xcopy C:\ComfyUI\tests\backend\test_agents_api.py C:\Ziggie\tests\control-center\backend\
xcopy C:\ComfyUI\tests\backend\test_knowledge_api.py C:\Ziggie\tests\control-center\backend\
xcopy C:\ComfyUI\tests\integration C:\Ziggie\tests\integration /E /I /H

# Copy Knowledge Base tests
xcopy C:\meowping-rts\ai-agents\knowledge-base\test_*.py C:\Ziggie\tests\agents\
```

### Phase 7: Migrate Documentation

```bash
# Copy central documentation
copy C:\meowping-rts\00_README_MASTER.md C:\Ziggie\docs\guides\
copy C:\meowping-rts\SYSTEM_ARCHITECTURE.md C:\Ziggie\docs\architecture\
copy C:\meowping-rts\INSTALLATION_GUIDE.md C:\Ziggie\docs\guides\getting-started\
copy C:\meowping-rts\QUICK_START.md C:\Ziggie\docs\guides\getting-started\

# Copy design docs
xcopy C:\meowping-rts\design-docs C:\Ziggie\docs\guides\game-design /E /I /H

# Copy reference docs
xcopy C:\meowping-rts\ref-docs C:\Ziggie\docs\guides\reference /E /I /H
```

### Phase 8: Migrate Data

```bash
# Copy databases
copy C:\meowping-rts\control-center\backend\*.db C:\Ziggie\data\databases\
copy C:\ComfyUI\*.db C:\Ziggie\data\databases\

# Create .gitkeep files
echo. > C:\Ziggie\data\logs\.gitkeep
echo. > C:\Ziggie\data\cache\.gitkeep
echo. > C:\Ziggie\data\exports\.gitkeep
```

---

## File Mapping Reference

### Complete Mapping Table

| Source (meowping-rts) | Destination (Ziggie) |
|----------------------|---------------------|
| `ai-agents/*.md` | `agents/L1-agents/` |
| `ai-agents/knowledge-base/` | `agents/knowledge-base/` |
| `control-center/backend/` | `control-center/backend/` |
| `control-center/frontend/` | `control-center/frontend/` |
| `backend/` | `game/backend/` |
| `frontend/` | `game/frontend/` |
| `assets/` | `game/assets/` |
| `data/` | `game/data/` |
| `missions/` | `game/missions/` |
| `*.sh` | `shared/automation/` |
| `docker-compose.yml` | `shared/configs/docker/` |
| `.env.example` | `shared/configs/environment/` |
| `backend/tests/` | `tests/game/backend/` |
| `design-docs/` | `docs/guides/game-design/` |
| `ref-docs/` | `docs/guides/reference/` |

| Source (ComfyUI) | Destination (Ziggie) |
|------------------|---------------------|
| `api_server/routes/agents_routes.py` | `control-center/backend/api/agents.py` |
| `api_server/routes/knowledge_routes.py` | `control-center/backend/api/knowledge.py` |
| `api_server/services/agent_service.py` | `control-center/backend/services/agent_service.py` |
| `api_server/services/knowledge_service.py` | `control-center/backend/services/knowledge_service.py` |
| `tests/backend/test_agents_api.py` | `tests/control-center/backend/test_agents_api.py` |
| `tests/backend/test_knowledge_api.py` | `tests/control-center/backend/test_knowledge_api.py` |

---

## Post-Migration Tasks

### 1. Update Import Paths

#### Python Files

```python
# Old (meowping-rts/backend)
from app.models.unit import Unit

# New (game/backend)
from app.models.unit import Unit  # Same path

# Old (control-center/backend)
from api.agents import router

# New (control-center/backend)
from api.agents import router  # Same path
```

#### TypeScript Files

```typescript
// Old
import { AgentCard } from '../components/agents/AgentCard';

// New (same relative paths)
import { AgentCard } from '../components/agents/AgentCard';
```

### 2. Update Configuration Files

#### Update .env files

```bash
# Edit control-center/backend/.env
DATABASE_URL=sqlite:///../../data/databases/control-center.db

# Edit game/backend/.env
DATABASE_URL=sqlite:///../../data/databases/game.db
```

#### Update package.json

```json
// control-center/frontend/package.json
{
  "proxy": "http://localhost:8000"
}

// game/frontend/package.json
{
  "proxy": "http://localhost:8001"
}
```

### 3. Update Docker Compose

```yaml
# shared/configs/docker/docker-compose.yml
version: '3.8'

services:
  control-center-backend:
    build: ../../control-center/backend
    volumes:
      - ../../data:/data

  game-backend:
    build: ../../game/backend
    volumes:
      - ../../data:/data
```

### 4. Update GitHub Actions

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test-agents:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test Agents
        run: |
          cd tests/agents
          pytest

  test-control-center:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test Control Center
        run: |
          cd tests/control-center
          pytest

  test-game:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test Game
        run: |
          cd tests/game
          pytest
```

### 5. Update Documentation Links

Search and replace in all .md files:

```bash
# Old references
meowping-rts/ai-agents/

# New references
agents/

# Old references
control-center/backend/api/

# New references
control-center/backend/api/
```

### 6. Reinstall Dependencies

```bash
# Control Center Backend
cd control-center/backend
pip install -r requirements.txt

# Control Center Frontend
cd ../frontend
npm install

# Game Backend
cd ../../game/backend
pip install -r requirements.txt

# Game Frontend
cd ../frontend
npm install
```

---

## Verification

### Checklist

```bash
# 1. Verify directory structure
dir C:\Ziggie
# Should see: agents, control-center, game, shared, tests, docs, data, .github

# 2. Count agent files
dir C:\Ziggie\agents\L1-agents /B | find /c /v ""
# Should be: 8

# 3. Verify knowledge base
dir C:\Ziggie\agents\knowledge-base\metadata
# Should see: creator-database.json, routing-rules.json

# 4. Check Control Center
dir C:\Ziggie\control-center\backend\api
# Should see: agents.py, knowledge.py, projects.py, etc.

# 5. Check Game backend
dir C:\Ziggie\game\backend\app
# Should see: config/, models/, routes/, services/

# 6. Check tests
dir C:\Ziggie\tests
# Should see: agents/, control-center/, game/, integration/

# 7. Verify automation scripts
dir C:\Ziggie\shared\automation\install
# Should see multiple .sh files

# 8. Check documentation
dir C:\Ziggie\docs
# Should see: architecture/, guides/, api/, tutorials/
```

### Run Tests

```bash
# Test agents
cd C:\Ziggie\tests\agents
pytest

# Test Control Center
cd ..\control-center\backend
pytest

# Test game
cd ..\..\game\backend
pytest

# All tests should pass
```

### Start Services

```bash
# Terminal 1 - Control Center Backend
cd C:\Ziggie\control-center\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

# Terminal 2 - Control Center Frontend
cd C:\Ziggie\control-center\frontend
npm install
npm run dev

# Terminal 3 - Game Backend
cd C:\Ziggie\game\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001

# Terminal 4 - Game Frontend
cd C:\Ziggie\game\frontend
npm install
npm run dev --port 3000
```

### Verify URLs

- Control Center: http://localhost:5173
- Control Center API: http://localhost:8000/docs
- Game: http://localhost:3000
- Game API: http://localhost:8001/docs

---

## Rollback Plan

### If Migration Fails

```bash
# Stop all services
taskkill /F /IM python.exe
taskkill /F /IM node.exe

# Restore from backup
rmdir /S /Q C:\Ziggie

xcopy C:\BACKUP\meowping-rts C:\meowping-rts /E /I /H
xcopy C:\BACKUP\ComfyUI C:\ComfyUI /E /I /H

# Verify restoration
dir C:\meowping-rts
dir C:\ComfyUI
```

### Partial Rollback

If only some components fail, you can restore individual directories:

```bash
# Restore only agents
rmdir /S /Q C:\Ziggie\agents
xcopy C:\BACKUP\meowping-rts\ai-agents C:\Ziggie\agents /E /I /H

# Restore only control-center
rmdir /S /Q C:\Ziggie\control-center
xcopy C:\BACKUP\meowping-rts\control-center C:\Ziggie\control-center /E /I /H
```

---

## Common Issues

### Issue 1: Import Errors

**Problem:** `ModuleNotFoundError` after migration

**Solution:**
```bash
# Ensure you're in the right directory
cd C:\Ziggie\game\backend
pip install -r requirements.txt

# Or create new venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue 2: Database Not Found

**Problem:** `sqlite3.OperationalError: unable to open database file`

**Solution:**
```bash
# Check database path in .env
DATABASE_URL=sqlite:///../../data/databases/control-center.db

# Create database directory if missing
mkdir C:\Ziggie\data\databases

# Copy database
copy C:\meowping-rts\control-center\backend\*.db C:\Ziggie\data\databases\
```

### Issue 3: Frontend Can't Connect to API

**Problem:** `Network Error` in frontend

**Solution:**
```javascript
// Check .env.local
VITE_API_URL=http://localhost:8000

// Verify backend is running
curl http://localhost:8000/health
```

### Issue 4: Missing Files

**Problem:** Some files didn't copy

**Solution:**
```bash
# Use /H flag to include hidden files
xcopy source destination /E /I /H

# Verify copy
dir source /s > source_files.txt
dir destination /s > dest_files.txt
fc source_files.txt dest_files.txt
```

---

## Cleanup

### After Successful Migration

```bash
# Remove old directories (ONLY after verification)
# WARNING: This is permanent!

# Backup first!
xcopy C:\meowping-rts C:\ARCHIVE\meowping-rts /E /I /H
xcopy C:\ComfyUI C:\ARCHIVE\ComfyUI /E /I /H

# Then remove (use with caution)
# rmdir /S /Q C:\meowping-rts
# rmdir /S /Q C:\ComfyUI

# Keep backups for at least 1 week before final deletion
```

### Archive vs Delete

**Recommended:** Keep archives for 1-2 weeks
- Allows easy rollback if issues arise
- Can reference old structure if needed
- Delete after confirming everything works

---

## Summary

✅ **Complete these steps:**

1. [ ] Create backup
2. [ ] Create new structure
3. [ ] Migrate agents
4. [ ] Migrate Control Center
5. [ ] Migrate game files
6. [ ] Migrate shared resources
7. [ ] Migrate tests
8. [ ] Migrate documentation
9. [ ] Update configurations
10. [ ] Verify functionality
11. [ ] Run tests
12. [ ] Archive old directories

**Estimated Total Time:** 1-4 hours depending on project size

---

**For help, see:**
- `DIRECTORY_STRUCTURE.md` - Complete structure reference
- `QUICKSTART.md` - Getting started after migration
- `ARCHITECTURE.md` - System architecture
- `docs/guides/troubleshooting.md` - Troubleshooting guide

---

**Version:** 1.0.0
**Last Updated:** 2025-11-07
