# Configuration Updates - Migration to C:\Ziggie

**Version:** 1.0.0
**Date:** 2025-11-07
**Status:** Configuration Guide - Infrastructure Update Phase
**Purpose:** Complete reference for all path updates required when migrating from `C:\meowping-rts` and `C:\ComfyUI` to `C:\Ziggie`

---

## Executive Summary

This document provides a comprehensive guide for updating all configurations when the Ziggie platform is deployed to the new `C:\Ziggie` location. All hard-coded paths from `C:\meowping-rts\` and related locations must be updated to `C:\Ziggie\`.

### Key Statistics
- **Files Updated:** 12+ configuration files
- **Path Replacements:** 50+ individual path references
- **Components Affected:**
  - Backend API (FastAPI)
  - Frontend (React)
  - Knowledge Base Pipeline
  - Database connections
  - Automation scripts

### No Longer Needed Paths
- **Old path:** `C:\meowping-rts\` (AI agents & control center only; game stays)
- **Unchanged:** `C:\ComfyUI\` (remains at original location)

---

## Table of Contents

1. [Files Updated](#files-updated)
2. [Path Replacements](#path-replacements)
3. [Environment Variables](#environment-variables)
4. [Configuration Files](#configuration-files)
5. [Database Paths](#database-paths)
6. [Helper Scripts](#helper-scripts)
7. [Verification Steps](#verification-steps)
8. [Troubleshooting](#troubleshooting)

---

## Files Updated

### Backend Configuration Files

| File Path | Component | Key Updates |
|-----------|-----------|------------|
| `C:\Ziggie\control-center\backend\config.py` | Backend Config | MEOWPING_DIR, COMFYUI_DIR paths |
| `C:\Ziggie\control-center\backend\services\agent_loader.py` | Agent Service | Agent directory paths |
| `C:\Ziggie\control-center\backend\services\kb_manager.py` | KB Service | Knowledge base paths |
| `C:\Ziggie\control-center\backend\api\agents.py` | Agent API | Agent discovery paths |
| `C:\Ziggie\control-center\backend\api\knowledge.py` | KB API | KB metadata paths |
| `C:\Ziggie\control-center\backend\api\comfyui.py` | ComfyUI API | ComfyUI workflow paths |
| `C:\Ziggie\control-center\backend\api\projects.py` | Project API | Project data paths |

### Knowledge Base Files

| File Path | Component | Key Updates |
|-----------|-----------|------------|
| `C:\Ziggie\ai-agents\knowledge-base\.env` | KB Config | KB_BASE_PATH, API endpoints |
| `C:\Ziggie\ai-agents\knowledge-base\config.py` | KB Config | Base path references |
| `C:\Ziggie\ai-agents\knowledge-base\src\config.py` | KB Pipeline | Logging and data paths |

### Test Files

| File Path | Component | Key Updates |
|-----------|-----------|------------|
| `C:\Ziggie\tests\control-center\backend\test_*.py` | Tests | Fixture and mock paths |
| `C:\Ziggie\tests\integration\test_agent_*.py` | Integration Tests | Agent discovery paths |

### Frontend Files

| File Path | Component | Key Updates |
|-----------|-----------|------------|
| `C:\Ziggie\control-center\frontend\vite.config.ts` | Build Config | Proxy backend URL |
| `C:\Ziggie\control-center\frontend\public\config.json` | Frontend Config | API base URL |

---

## Path Replacements

### Primary Path Replacement

**Old Format (Multiple Variations):**
- `C:/meowping-rts` (forward slash)
- `C:\meowping-rts` (backslash)
- `C:\\meowping-rts` (escaped backslash in strings)

**New Format:**
- `C:/Ziggie` (forward slash)
- `C:\Ziggie` (backslash)
- `C:\\Ziggie` (escaped backslash in strings)

### Secondary Path Replacements

| Old Path | New Path | Component |
|----------|----------|-----------|
| `C:\meowping-rts\ai-agents` | `C:\Ziggie\ai-agents` | Agent system |
| `C:\meowping-rts\control-center` | `C:\Ziggie\control-center` | Control Center |
| `C:\meowping-rts\ai-agents\knowledge-base` | `C:\Ziggie\ai-agents\knowledge-base` | Knowledge Base |
| `C:\ComfyUI` | `C:\ComfyUI` | ComfyUI (UNCHANGED) |

### Database Path Replacements

| Old Path | New Path | File Type |
|----------|----------|-----------|
| `C:\meowping-rts\control-center\backend\control-center.db` | `C:\Ziggie\control-center\backend\control-center.db` | SQLite |
| `C:\meowping-rts\data\` | `C:\Ziggie\data\` | Data storage |
| `C:\meowping-rts\logs\` | `C:\Ziggie\logs\` | Log files |

---

## Environment Variables

### Knowledge Base .env File

**Location:** `C:\Ziggie\ai-agents\knowledge-base\.env`

**Old Configuration:**
```bash
# Old paths
KB_BASE_PATH=C:\meowping-rts\ai-agents\knowledge-base
KB_AGENTS_PATH=C:\meowping-rts\ai-agents
KB_LOGS_PATH=C:\meowping-rts\ai-agents\knowledge-base\logs
KB_TEMP_PATH=C:\meowping-rts\ai-agents\knowledge-base\temp
KB_METADATA_PATH=C:\meowping-rts\ai-agents\knowledge-base\metadata

# API configuration (usually unchanged)
CLAUDE_API_KEY=your_api_key_here
YOUTUBE_DATA_API_KEY=your_api_key_here
```

**New Configuration:**
```bash
# New paths
KB_BASE_PATH=C:\Ziggie\ai-agents\knowledge-base
KB_AGENTS_PATH=C:\Ziggie\ai-agents
KB_LOGS_PATH=C:\Ziggie\ai-agents\knowledge-base\logs
KB_TEMP_PATH=C:\Ziggie\ai-agents\knowledge-base\temp
KB_METADATA_PATH=C:\Ziggie\ai-agents\knowledge-base\metadata

# API configuration (usually unchanged)
CLAUDE_API_KEY=your_api_key_here
YOUTUBE_DATA_API_KEY=your_api_key_here
```

### Control Center Backend .env File

**Location:** `C:\Ziggie\control-center\backend\.env`

**New Configuration:**
```bash
# Application
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your_secret_key

# Paths
MEOWPING_DIR=C:\Ziggie
COMFYUI_DIR=C:\ComfyUI
AGENTS_DIR=C:\Ziggie\ai-agents
KB_DIR=C:\Ziggie\ai-agents\knowledge-base

# Database
DATABASE_URL=sqlite:///C:\Ziggie\control-center\backend\control-center.db

# API URLs
BACKEND_URL=http://127.0.0.1:8080
FRONTEND_URL=http://localhost:3000

# External APIs
CLAUDE_API_KEY=your_api_key_here
YOUTUBE_DATA_API_KEY=your_api_key_here

# Logging
LOG_LEVEL=INFO
LOG_DIR=C:\Ziggie\data\logs\control-center

# ComfyUI Integration
COMFYUI_HOST=127.0.0.1
COMFYUI_PORT=8188
```

---

## Configuration Files

### 1. Backend Config (config.py)

**File:** `C:\Ziggie\control-center\backend\config.py`

**Key Updates:**

```python
# OLD
from pathlib import Path

class Config:
    MEOWPING_DIR: Path = Path(r"C:\meowping-rts")
    COMFYUI_DIR: Path = Path(r"C:\ComfyUI")
    AGENTS_DIR: Path = MEOWPING_DIR / "ai-agents"
    KB_DIR: Path = AGENTS_DIR / "knowledge-base"

# NEW
from pathlib import Path

class Config:
    MEOWPING_DIR: Path = Path(r"C:\Ziggie")  # Updated
    COMFYUI_DIR: Path = Path(r"C:\ComfyUI")  # Unchanged
    AGENTS_DIR: Path = MEOWPING_DIR / "ai-agents"
    KB_DIR: Path = AGENTS_DIR / "knowledge-base"
```

### 2. Agent Loader Service

**File:** `C:\Ziggie\control-center\backend\services\agent_loader.py`

**Key Updates:**

```python
# OLD
AGENTS_PATH = Path("C:/meowping-rts/ai-agents")
L1_AGENTS_PATH = AGENTS_PATH / "L1-agents"
L2_AGENTS_PATH = AGENTS_PATH / "L2-agents"
L3_AGENTS_PATH = AGENTS_PATH / "L3-agents"

# NEW
AGENTS_PATH = Path("C:/Ziggie/ai-agents")  # Updated
L1_AGENTS_PATH = AGENTS_PATH / "L1-agents"
L2_AGENTS_PATH = AGENTS_PATH / "L2-agents"
L3_AGENTS_PATH = AGENTS_PATH / "L3-agents"
```

### 3. Knowledge Base Manager

**File:** `C:\Ziggie\ai-agents\knowledge-base\config.py`

**Key Updates:**

```python
# OLD
BASE_PATH = Path(r"C:\meowping-rts\ai-agents\knowledge-base")
AGENTS_PATH = Path(r"C:\meowping-rts\ai-agents")
METADATA_PATH = BASE_PATH / "metadata"
LOGS_PATH = BASE_PATH / "logs"
TEMP_PATH = BASE_PATH / "temp"

# NEW
BASE_PATH = Path(r"C:\Ziggie\ai-agents\knowledge-base")  # Updated
AGENTS_PATH = Path(r"C:\Ziggie\ai-agents")  # Updated
METADATA_PATH = BASE_PATH / "metadata"
LOGS_PATH = BASE_PATH / "logs"
TEMP_PATH = BASE_PATH / "temp"
```

### 4. Database Configuration

**File:** `C:\Ziggie\control-center\backend\config.py`

**Key Updates:**

```python
# OLD
SQLALCHEMY_DATABASE_URL = "sqlite:///C:\\meowping-rts\\control-center\\backend\\control-center.db"

# NEW
SQLALCHEMY_DATABASE_URL = "sqlite:///C:\\Ziggie\\control-center\\backend\\control-center.db"
```

### 5. ComfyUI Integration

**File:** `C:\Ziggie\control-center\backend\api\comfyui.py`

**Key Updates:**

```python
# ComfyUI paths - REMAIN UNCHANGED
COMFYUI_PATH = Path(r"C:\ComfyUI")
WORKFLOWS_PATH = COMFYUI_PATH / "api_server" / "workflows"
MODELS_PATH = COMFYUI_PATH / "models"
OUTPUT_PATH = COMFYUI_PATH / "output"

# Project references - UPDATED
AGENT_ASSETS_PATH = Path(r"C:\Ziggie\ai-agents\assets")  # Updated
```

### 6. Vite Frontend Config

**File:** `C:\Ziggie\control-center\frontend\vite.config.ts`

**Key Updates:**

```typescript
// OLD
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true,
      },
    },
  },
});

// NEW - Usually unchanged, but may reference new log paths
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8080',  // Unchanged
        changeOrigin: true,
      },
    },
  },
});
```

---

## Database Paths

### SQLite Database Migration

**Location Change:**
- Old: `C:\meowping-rts\control-center\backend\control-center.db`
- New: `C:\Ziggie\control-center\backend\control-center.db`

**Steps to Update:**

1. **Copy Database File**
   ```powershell
   Copy-Item `
     -Path "C:\meowping-rts\control-center\backend\control-center.db" `
     -Destination "C:\Ziggie\control-center\backend\control-center.db" `
     -Force
   ```

2. **Update Connection String in Code**
   ```python
   # In config.py
   SQLALCHEMY_DATABASE_URL = "sqlite:///C:\\Ziggie\\control-center\\backend\\control-center.db"
   ```

3. **Verify Database Accessibility**
   ```powershell
   Test-Path "C:\Ziggie\control-center\backend\control-center.db"
   # Expected: True
   ```

### Log File Paths

**Create Log Directories:**
```powershell
mkdir -p C:\Ziggie\data\logs\control-center
mkdir -p C:\Ziggie\data\logs\agents
mkdir -p C:\Ziggie\data\logs\comfyui
mkdir -p C:\Ziggie\ai-agents\knowledge-base\logs
```

**Update in Logging Configuration:**
```python
# OLD
LOG_DIR = Path(r"C:\meowping-rts\logs")

# NEW
LOG_DIR = Path(r"C:\Ziggie\data\logs")
```

---

## Helper Scripts

### 1. Start Backend Script

**Create:** `C:\Ziggie\start_backend.bat`

```batch
@echo off
REM Start Control Center Backend
cd /d C:\Ziggie\control-center\backend
echo Starting Control Center Backend...
python main.py
pause
```

### 2. Start Frontend Script

**Create:** `C:\Ziggie\start_frontend.bat`

```batch
@echo off
REM Start Control Center Frontend
cd /d C:\Ziggie\control-center\frontend
echo Starting Control Center Frontend...
npm run dev
pause
```

### 3. Knowledge Base Status Script

**Create:** `C:\Ziggie\kb_status.bat`

```batch
@echo off
REM Check Knowledge Base Status
cd /d C:\Ziggie\ai-agents\knowledge-base
echo Checking Knowledge Base Status...
python manage.py status
pause
```

### 4. Run All Services Script

**Create:** `C:\Ziggie\start_all.bat`

```batch
@echo off
REM Start all Ziggie services
title Ziggie Services

REM Start backend in new window
start "Backend" cmd /k "cd /d C:\Ziggie\control-center\backend && python main.py"

REM Wait for backend to start
timeout /t 3

REM Start frontend in new window
start "Frontend" cmd /k "cd /d C:\Ziggie\control-center\frontend && npm run dev"

REM Notify user
echo.
echo Services started:
echo - Backend: http://127.0.0.1:8080
echo - Frontend: http://localhost:3000
echo.
pause
```

### 5. PowerShell Path Verification Script

**Create:** `C:\Ziggie\verify_paths.ps1`

```powershell
# Verify all paths have been updated correctly

Write-Host "=== Path Verification Report ===" -ForegroundColor Cyan
Write-Host ""

$oldPath = "C:/meowping-rts"
$oldPathEsc = "C:\meowping-rts"

Write-Host "Searching for old paths in Python files..." -ForegroundColor Yellow

$foundIssues = $false
$pythonFiles = Get-ChildItem -Path "C:\Ziggie" -Filter "*.py" -Recurse

foreach ($file in $pythonFiles) {
    $content = Get-Content $file.FullName -Raw

    if ($content -match [regex]::Escape($oldPath) -or $content -match [regex]::Escape($oldPathEsc)) {
        Write-Host "FOUND OLD PATH: $($file.FullName)" -ForegroundColor Red
        $foundIssues = $true
    }
}

if (-not $foundIssues) {
    Write-Host "No old paths found! All paths updated correctly." -ForegroundColor Green
} else {
    Write-Host "Issues found. Review files above." -ForegroundColor Red
}

Write-Host ""
Write-Host "Verifying new paths exist..." -ForegroundColor Yellow

$paths = @(
    "C:\Ziggie\ai-agents",
    "C:\Ziggie\control-center\backend",
    "C:\Ziggie\control-center\frontend",
    "C:\Ziggie\ai-agents\knowledge-base",
    "C:\ComfyUI"
)

foreach ($path in $paths) {
    if (Test-Path $path) {
        Write-Host "✓ $path" -ForegroundColor Green
    } else {
        Write-Host "✗ $path (NOT FOUND)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Verification Complete ===" -ForegroundColor Cyan
```

---

## Verification Steps

### Step 1: Verify Directory Structure

```powershell
# Check main directories exist
Test-Path C:\Ziggie\ai-agents
Test-Path C:\Ziggie\control-center\backend
Test-Path C:\Ziggie\control-center\frontend
Test-Path C:\ComfyUI

# All should return True
```

### Step 2: Verify Configuration Files

```powershell
# Check key config files exist
Test-Path C:\Ziggie\control-center\backend\config.py
Test-Path C:\Ziggie\ai-agents\knowledge-base\.env
Test-Path C:\Ziggie\control-center\frontend\package.json

# All should return True
```

### Step 3: Verify No Old Paths Remain

```powershell
# Search for any remaining old paths
Select-String -Path "C:\Ziggie\**\*.py" -Pattern "C:/meowping-rts" -Recurse
Select-String -Path "C:\Ziggie\**\*.py" -Pattern "C:\meowping-rts" -Recurse

# Should return NO RESULTS
```

### Step 4: Test Backend Startup

```powershell
cd C:\Ziggie\control-center\backend

# Try importing config
python -c "from config import Config; print('Config loaded:', Config.MEOWPING_DIR)"

# Expected output: Config loaded: C:\Ziggie
```

### Step 5: Test Knowledge Base

```powershell
cd C:\Ziggie\ai-agents\knowledge-base

# Check KB status
python manage.py status

# Should show: Knowledge Base Status: OK (no path errors)
```

### Step 6: Test Frontend Dependencies

```powershell
cd C:\Ziggie\control-center\frontend

# Verify npm can find packages
npm list react

# Should show: react@18.x.x
```

### Step 7: Browser Testing

1. **Start Backend:**
   ```powershell
   cd C:\Ziggie\control-center\backend
   python main.py
   ```
   - Expected: Runs on http://127.0.0.1:8080
   - Check: Can access http://127.0.0.1:8080/docs

2. **Start Frontend:**
   ```powershell
   cd C:\Ziggie\control-center\frontend
   npm run dev
   ```
   - Expected: Runs on http://localhost:3000
   - Check: Can access http://localhost:3000

3. **Test API Connectivity:**
   ```powershell
   # From PowerShell
   Invoke-WebRequest -Uri "http://127.0.0.1:8080/api/agents" -Method GET

   # Should return agent list without path errors
   ```

---

## Troubleshooting

### Issue: Backend fails to start - "Config import error"

**Cause:** Old paths in config.py not updated

**Fix:**
```powershell
# Edit config.py and update all paths
code C:\Ziggie\control-center\backend\config.py

# Search for "meowping-rts" and replace with "Ziggie"
```

### Issue: "Knowledge Base not found" error

**Cause:** KB path not updated in .env

**Fix:**
```powershell
# Check and update .env
type C:\Ziggie\ai-agents\knowledge-base\.env

# Verify paths:
# KB_BASE_PATH=C:\Ziggie\ai-agents\knowledge-base
# KB_AGENTS_PATH=C:\Ziggie\ai-agents
```

### Issue: Frontend can't connect to backend (CORS errors)

**Cause:** API base URL mismatch

**Fix:**
```powershell
# Check vite.config.ts proxy settings
type C:\Ziggie\control-center\frontend\vite.config.ts

# Should proxy to: http://127.0.0.1:8080
```

### Issue: Database file not found

**Cause:** Database path in connection string is wrong

**Fix:**
```powershell
# Verify database file exists
Test-Path C:\Ziggie\control-center\backend\control-center.db

# If not, copy from backup
Copy-Item C:\Backups\Migration_*\control-center.db `
  C:\Ziggie\control-center\backend\control-center.db
```

### Issue: Permission denied errors

**Cause:** File permissions not inherited properly after copy

**Fix:**
```powershell
# Grant full permissions
$acl = Get-Acl "C:\Ziggie"
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule `
  ((whoami), "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
$acl.AddAccessRule($rule)
Set-Acl -Path "C:\Ziggie" -AclObject $acl
```

### Issue: ComfyUI paths broken

**Cause:** ComfyUI path was changed (it shouldn't be)

**Fix:**
```powershell
# ComfyUI should ALWAYS be at C:\ComfyUI
# Search and replace any incorrect paths back:
Select-String -Path "C:\Ziggie\**\*.py" -Pattern "C:/ComfyUI|C:\ComfyUI" -Recurse
```

---

## Automated Path Update Script

### PowerShell Batch Update

Save as: `C:\Ziggie\update_all_paths.ps1`

```powershell
# Automated path update for all configuration files

param(
    [switch]$Test,
    [switch]$Verbose
)

$oldPath = "C:/meowping-rts"
$oldPathEsc = "C:\meowping-rts"
$newPath = "C:/Ziggie"
$newPathEsc = "C:\Ziggie"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AUTOMATED PATH UPDATE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($Test) {
    Write-Host "Running in TEST mode - no changes will be made" -ForegroundColor Yellow
}

$filesToUpdate = @(
    "C:\Ziggie\control-center\backend\config.py",
    "C:\Ziggie\control-center\backend\services\agent_loader.py",
    "C:\Ziggie\control-center\backend\services\kb_manager.py",
    "C:\Ziggie\control-center\backend\api\agents.py",
    "C:\Ziggie\control-center\backend\api\knowledge.py",
    "C:\Ziggie\control-center\backend\api\comfyui.py",
    "C:\Ziggie\control-center\backend\api\projects.py",
    "C:\Ziggie\ai-agents\knowledge-base\.env"
)

$updateCount = 0

foreach ($file in $filesToUpdate) {
    if (Test-Path $file) {
        if ($Verbose) {
            Write-Host "Processing: $file" -ForegroundColor Yellow
        }

        $content = Get-Content $file -Raw
        $originalContent = $content

        $content = $content -replace [regex]::Escape($oldPath), $newPath
        $content = $content -replace [regex]::Escape($oldPathEsc), $newPathEsc

        if ($content -ne $originalContent) {
            if (-not $Test) {
                $content | Set-Content $file -NoNewline
                Write-Host "✓ Updated: $file" -ForegroundColor Green
            } else {
                Write-Host "[TEST] Would update: $file" -ForegroundColor Cyan
            }
            $updateCount++
        } elseif ($Verbose) {
            Write-Host "- No changes needed: $file" -ForegroundColor Gray
        }
    } else {
        Write-Host "⚠ Not found: $file" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Update Complete!" -ForegroundColor Green
Write-Host "Files processed: $updateCount" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
```

**Usage:**
```powershell
# Test run (no changes)
.\update_all_paths.ps1 -Test -Verbose

# Actual update
.\update_all_paths.ps1
```

---

## Configuration Checklist

Use this checklist to ensure all configurations are updated:

```
BACKEND CONFIGURATION
- [ ] config.py - MEOWPING_DIR updated to C:\Ziggie
- [ ] config.py - SQLALCHEMY_DATABASE_URL updated
- [ ] agent_loader.py - AGENTS_PATH updated
- [ ] kb_manager.py - BASE_PATH and AGENTS_PATH updated
- [ ] api/agents.py - All agent discovery paths updated
- [ ] api/knowledge.py - KB metadata paths updated
- [ ] api/comfyui.py - Project asset paths updated (ComfyUI path unchanged)
- [ ] .env file - All KB_* environment variables updated

FRONTEND CONFIGURATION
- [ ] vite.config.ts - Backend proxy URL correct (should be 8080)
- [ ] public/config.json - API base URL correct

DATABASE CONFIGURATION
- [ ] Database file copied to C:\Ziggie\control-center\backend\
- [ ] Connection string in config.py updated
- [ ] Database accessible and readable

ENVIRONMENT VARIABLES
- [ ] .env files created/updated in all components
- [ ] API keys present (CLAUDE_API_KEY, YOUTUBE_DATA_API_KEY)
- [ ] Paths use correct separators (\ or /)

VERIFICATION
- [ ] No old paths remain in codebase (search C:\meowping-rts)
- [ ] All directories exist and are accessible
- [ ] Backend starts without errors
- [ ] Frontend builds without errors
- [ ] Knowledge base manager works
- [ ] Database operations successful
- [ ] API endpoints return correct responses

HELPER SCRIPTS
- [ ] start_backend.bat created
- [ ] start_frontend.bat created
- [ ] kb_status.bat created
- [ ] start_all.bat created
- [ ] verify_paths.ps1 created
```

---

## Quick Reference

### Critical Path Changes

| Component | Old | New |
|-----------|-----|-----|
| Base Directory | C:\meowping-rts | C:\Ziggie |
| AI Agents | C:\meowping-rts\ai-agents | C:\Ziggie\ai-agents |
| Knowledge Base | C:\meowping-rts\ai-agents\knowledge-base | C:\Ziggie\ai-agents\knowledge-base |
| Control Center | C:\meowping-rts\control-center | C:\Ziggie\control-center |
| Backend | C:\meowping-rts\control-center\backend | C:\Ziggie\control-center\backend |
| Frontend | C:\meowping-rts\control-center\frontend | C:\Ziggie\control-center\frontend |
| Database | C:\meowping-rts\control-center\backend\control-center.db | C:\Ziggie\control-center\backend\control-center.db |
| ComfyUI | C:\ComfyUI | C:\ComfyUI (UNCHANGED) |

### Service Start Commands

```powershell
# Backend
cd C:\Ziggie\control-center\backend
python main.py

# Frontend
cd C:\Ziggie\control-center\frontend
npm run dev

# Knowledge Base
cd C:\Ziggie\ai-agents\knowledge-base
python manage.py status
```

### Verification Commands

```powershell
# Check for old paths
Select-String -Path "C:\Ziggie\**\*.py" -Pattern "C:/meowping-rts|C:\meowping-rts" -Recurse

# Verify directories
Test-Path C:\Ziggie\ai-agents
Test-Path C:\Ziggie\control-center
Test-Path C:\ComfyUI
```

---

## Support & Rollback

### Immediate Issues

If something breaks immediately after configuration updates:

1. **Stop all services** - Kill backend, frontend, and any KB processes
2. **Check paths** - Run `verify_paths.ps1` to identify issues
3. **Review logs** - Check `C:\Ziggie\data\logs\` for error messages
4. **Fix specific files** - Edit the offending configuration file
5. **Restart services** - Test again

### Complete Rollback

If configuration is severely corrupted:

```powershell
# Restore from backup
.\rollback.ps1

# This will:
# 1. Delete C:\Ziggie (migration destination)
# 2. Restore C:\meowping-rts from backup (if needed)
# 3. Verify restoration
```

---

## Final Verification

After completing all configuration updates, run this final test:

```powershell
# Run comprehensive verification
.\verify_paths.ps1

# Start backend (in one terminal)
cd C:\Ziggie\control-center\backend
python main.py

# Start frontend (in another terminal)
cd C:\Ziggie\control-center\frontend
npm run dev

# In browser, test:
# - http://127.0.0.1:8080/docs (backend API docs)
# - http://localhost:3000 (frontend)

# Test knowledge base
cd C:\Ziggie\ai-agents\knowledge-base
python manage.py status
```

If all components start without path-related errors, the configuration update is complete!

---

## Document Management

**Last Updated:** 2025-11-07
**Version:** 1.0.0
**Status:** Active - Configuration Guide
**Maintained By:** L1.6 - Technical Foundation Agent
**Related Documents:**
- MIGRATION_PLAN.md
- MIGRATION_SUMMARY.md
- MIGRATION_README.md
- DIRECTORY_STRUCTURE.md
- ARCHITECTURE.md

**Change Log:**
| Date | Version | Changes |
|------|---------|---------|
| 2025-11-07 | 1.0.0 | Initial comprehensive configuration update guide |

---

**Ensure all systems can find their files in new location!**
