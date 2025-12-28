# Migration Supplement - AI Agents & Control Center

This supplement provides migration-specific information for the AI Agent and Control Center systems moved to C:\Ziggie.

## What Was Migrated

From `C:\meowping-rts` to `C:\Ziggie`:
- **ai-agents/** - Complete AI agent system and knowledge base
- **control-center/** - Backend, frontend, and tests
- **.claude/** - Claude agent configurations

## What Remains in Original Locations

- **ComfyUI:** `C:\ComfyUI` (unchanged)
- **Game Code:** `C:\meowping-rts\backend`, `frontend`, etc. (unchanged)
- **Documentation:** Most docs remain in `C:\meowping-rts`

## Directory Structure (Migrated Components)

```
C:\Ziggie\
├── ai-agents\                      # AI Agent system (from meowping-rts)
│   ├── 01_ART_DIRECTOR_AGENT.md   # 8 agent definition files
│   ├── 02_CHARACTER_PIPELINE_AGENT.md
│   ├── ... (6 more agents)
│   ├── knowledge-base\             # Knowledge base management
│   │   ├── manage.py              # CLI manager
│   │   ├── .env                   # Configuration (API keys)
│   │   ├── requirements.txt       # Python dependencies
│   │   ├── src\                   # Source code
│   │   ├── metadata\              # Creator database & routing
│   │   ├── logs\                  # Operation logs
│   │   ├── temp\                  # Temporary files
│   │   └── L1-*\                  # Agent-specific knowledge
│   └── ai-agents\                 # Generated knowledge storage
│
├── control-center\                 # Control Center (from meowping-rts)
│   ├── backend\                   # FastAPI backend
│   │   ├── main.py               # Entry point
│   │   ├── config.py             # Configuration
│   │   ├── requirements.txt      # Python dependencies
│   │   ├── control-center.db     # SQLite database
│   │   ├── api\                  # API endpoints
│   │   ├── services\             # Business logic
│   │   └── database\             # Database models
│   ├── frontend\                  # React frontend
│   │   ├── src\                  # Source code
│   │   ├── package.json          # Dependencies
│   │   └── node_modules\         # ~480 MB
│   └── tests\                     # Test suites
│
├── .claude\                       # Claude config (from meowping-rts)
│   └── settings.local.json       # Permissions
│
├── MIGRATION_PLAN.md             # Complete migration guide
├── QUICK_START.md                # Quick reference
├── README.md                     # Main README (existing)
├── MIGRATION_README.md           # This file
├── migrate_all.ps1               # PowerShell migration
├── migrate_all.sh                # Bash migration
├── 1_backup.ps1 - 4_verify.ps1  # Individual phases
└── rollback.ps1                  # Rollback script
```

## Starting Services

### Control Center Backend
```powershell
cd C:\Ziggie\control-center\backend
python main.py
```
**Port:** 8080
**URL:** http://127.0.0.1:8080

### Control Center Frontend
```powershell
cd C:\Ziggie\control-center\frontend
npm run dev
```
**Port:** 3000
**URL:** http://localhost:3000

### Knowledge Base Manager
```powershell
cd C:\Ziggie\ai-agents\knowledge-base
python manage.py --help
```

## Configuration Files

All paths have been updated to reflect the new location:

### Backend Configuration
**File:** `control-center\backend\config.py`
```python
COMFYUI_DIR: Path = Path(r"C:\ComfyUI")         # Unchanged
MEOWPING_DIR: Path = Path(r"C:\Ziggie")         # Updated from C:\meowping-rts
```

### Knowledge Base Environment
**File:** `ai-agents\knowledge-base\.env`
```bash
KB_PATH=C:\Ziggie\ai-agents\knowledge-base      # Updated
LOG_PATH=C:\Ziggie\ai-agents\knowledge-base\logs
METADATA_PATH=C:\Ziggie\ai-agents\knowledge-base\metadata
TEMP_PATH=C:\Ziggie\ai-agents\knowledge-base\temp
```

## API Endpoints

### Control Center API (Port 8080)
- `GET /api/agents` - List all agents
- `GET /api/agents/{id}` - Get agent details
- `GET /api/agents/stats` - Agent statistics
- `GET /api/knowledge/files` - Knowledge base files
- `GET /api/knowledge/creators` - YouTube creators
- `POST /api/comfyui/start` - Start ComfyUI
- `GET /api/services` - Service status
- `GET /api/system/health` - System health

### ComfyUI API (Port 8188)
- Runs at: `C:\ComfyUI`
- Managed via Control Center
- Direct access: http://127.0.0.1:8188

## Dependencies

### Python (Backend & Knowledge Base)
```powershell
# Control Center backend
cd C:\Ziggie\control-center\backend
pip install -r requirements.txt

# Knowledge Base
cd C:\Ziggie\ai-agents\knowledge-base
pip install -r requirements.txt
```

### Node.js (Frontend)
```powershell
cd C:\Ziggie\control-center\frontend
npm install
```

## External Dependencies

These systems remain in their original locations and are referenced by the migrated components:

### ComfyUI
**Location:** `C:\ComfyUI`
**Used for:** Asset generation, image processing
**Integration:** Via Control Center API

### Game Code
**Location:** `C:\meowping-rts`
**Components:**
- `backend/` - Game backend services
- `frontend/` - Game frontend
- `assets/` - Game assets
- Documentation files

## Migration Scripts

All migration scripts are in `C:\Ziggie`:

### Full Migration
```powershell
.\migrate_all.ps1
```

### Individual Phases
```powershell
.\1_backup.ps1      # Create backup
.\2_copy_files.ps1  # Copy to Ziggie
.\3_update_paths.ps1 # Update paths
.\4_verify.ps1      # Verify migration
```

### Rollback
```powershell
.\rollback.ps1
```

## Troubleshooting

### Port Conflicts
```powershell
# Check what's using ports
netstat -ano | findstr "8080 8188 3000"

# Kill process by PID
taskkill /PID <pid> /F
```

### Path Errors
```powershell
# Verify no old paths remain
cd C:\Ziggie
.\4_verify.ps1

# Manual check
Select-String -Path "control-center\backend\*.py" -Pattern "C:/meowping-rts" -Recurse
```

### Import Errors
```powershell
# Reinstall dependencies
cd C:\Ziggie\control-center\backend
pip install -r requirements.txt --force-reinstall

cd C:\Ziggie\ai-agents\knowledge-base
pip install -r requirements.txt --force-reinstall
```

### Database Errors
```powershell
# Check database exists
Test-Path C:\Ziggie\control-center\backend\control-center.db

# Check file permissions
Get-Acl C:\Ziggie\control-center\backend\control-center.db
```

## Documentation

### Migration Documentation
- **MIGRATION_PLAN.md** - Complete 60+ page migration guide
- **QUICK_START.md** - Quick reference
- **MIGRATION_README.md** - This file

### Component Documentation
- **Control Center API:** `control-center\backend\API_DOCS.md`
- **Knowledge Base:** `ai-agents\knowledge-base\README.md`
- **Agent System:** See main README.md

## File Inventory

### AI Agents (~22 MB, 54 files)
- 8 agent definition markdown files
- Knowledge base system (Python)
- Metadata (creator database, routing rules)
- Logs and temporary files
- Generated agent knowledge

### Control Center (~500 MB, 1500+ files)
- Backend: FastAPI Python application
- Frontend: React + Vite application
- Tests: Integration and unit tests
- Database: SQLite database file
- node_modules: ~480 MB

## Backup Information

After migration, backup location is stored in:
```
C:\Ziggie\backup_location.txt
```

Typical backup location:
```
C:\Backups\Migration_YYYY-MM-DD_HHMMSS\
```

**Keep backups for at least 1 week** after successful migration.

## Testing After Migration

### 1. Backend Startup
```powershell
cd C:\Ziggie\control-center\backend
python main.py
# Should start without errors on port 8080
```

### 2. Frontend Startup
```powershell
cd C:\Ziggie\control-center\frontend
npm run dev
# Should start without errors on port 3000
```

### 3. API Test
```powershell
# Test health endpoint
curl http://127.0.0.1:8080/api/system/health

# Test agents endpoint
curl http://127.0.0.1:8080/api/agents
```

### 4. Knowledge Base Test
```powershell
cd C:\Ziggie\ai-agents\knowledge-base
python manage.py status
# Should show KB status without errors
```

## Migration Status

To check if migration was successful:

```powershell
# Run verification
cd C:\Ziggie
.\4_verify.ps1

# Check verification report
cat verification_report.json
```

## Support

- **Migration Issues:** See MIGRATION_PLAN.md
- **Service Issues:** Check component-specific README files
- **API Issues:** See API_DOCS.md in respective directories
- **Configuration Issues:** Review config files listed above

## Related Documentation

- **Main Platform:** README.md (in this directory)
- **Complete Migration Guide:** MIGRATION_PLAN.md
- **Quick Start:** QUICK_START.md
- **Control Center:** control-center/backend/API_DOCS.md
- **Knowledge Base:** ai-agents/knowledge-base/README.md

---

**Last Updated:** 2025-11-07
**Migration Version:** 1.0
**Status:** Ready for use
