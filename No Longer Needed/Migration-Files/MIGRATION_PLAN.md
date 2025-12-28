# AI Agent & Control Center Migration Plan
## Complete Migration from C:\meowping-rts & C:\ComfyUI to C:\Ziggie

**Date:** 2025-11-07
**Migration Type:** Safe, reversible directory consolidation
**Estimated Time:** 30-45 minutes
**Risk Level:** Low (with backups)

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Pre-Migration Checklist](#pre-migration-checklist)
3. [System Inventory](#system-inventory)
4. [File Mapping Strategy](#file-mapping-strategy)
5. [Migration Steps](#migration-steps)
6. [Path Update Requirements](#path-update-requirements)
7. [Verification Steps](#verification-steps)
8. [Rollback Plan](#rollback-plan)
9. [Post-Migration Tasks](#post-migration-tasks)

---

## Executive Summary

### What We're Moving
- **AI Agents System** (`C:\meowping-rts\ai-agents`) → `C:\Ziggie\ai-agents`
- **Control Center** (`C:\meowping-rts\control-center`) → `C:\Ziggie\control-center`
- **Claude Configurations** (`.claude` directories)

### What We're NOT Moving
- The main meowping-rts game codebase (stays in place)
- ComfyUI installation (stays in place)
- Other project documentation files

### Key Considerations
- **22 MB** of AI agents data (54 files)
- **~500 MB** of Control Center (including node_modules)
- **12 files** with hardcoded paths need updating
- No git repositories to preserve
- Active dependencies on ComfyUI and meowping-rts paths

---

## Pre-Migration Checklist

### 1. System Prerequisites
```powershell
# Run these checks before starting
[] Verify C:\Ziggie exists and is writable
[] Close all running services (ComfyUI, Control Center backend/frontend)
[] Stop any Python processes accessing these directories
[] Ensure at least 1 GB free space on C: drive
[] Have administrator privileges
[] Backup storage available (external drive or cloud)
```

### 2. Service Status Check
```powershell
# Check for running processes
tasklist | findstr "python node"
netstat -ano | findstr "8080 8188 3000"

# If any services are running, stop them:
# - Control Center backend (port 8080)
# - Control Center frontend (port 3000)
# - ComfyUI (port 8188)
```

### 3. Backup Prerequisites
```powershell
[] Create backup location: C:\Backups\Migration_2025-11-07
[] Test write access to backup location
[] Verify backup has sufficient space (~550 MB)
```

---

## System Inventory

### AI Agents Directory Structure
```
C:\meowping-rts\ai-agents\
├── 01_ART_DIRECTOR_AGENT.md
├── 02_CHARACTER_PIPELINE_AGENT.md
├── 03_ENVIRONMENT_PIPELINE_AGENT.md
├── 04_GAME_SYSTEMS_DEVELOPER_AGENT.md
├── 05_UI_UX_DEVELOPER_AGENT.md
├── 06_CONTENT_DESIGNER_AGENT.md
├── 07_INTEGRATION_AGENT.md
├── 08_QA_TESTING_AGENT.md
├── knowledge-base\
│   ├── .env (contains API keys - CRITICAL)
│   ├── .env.example
│   ├── manage.py
│   ├── requirements.txt
│   ├── src\
│   ├── metadata\
│   ├── logs\
│   ├── temp\
│   └── L1-* directories (agent-specific knowledge)
└── ai-agents\ (generated knowledge subdirectories)
```

### Control Center Structure
```
C:\meowping-rts\control-center\
├── backend\
│   ├── main.py
│   ├── config.py (HARDCODED PATHS)
│   ├── requirements.txt
│   ├── api\
│   ├── database\
│   ├── services\ (HARDCODED PATHS)
│   └── control-center.db (SQLite database)
├── frontend\
│   ├── package.json
│   ├── src\
│   └── node_modules\ (~480 MB)
└── tests\
```

### Files with Hardcoded Paths
1. `control-center/backend/config.py` - Lines 22-24, 30, 36, 43
2. `control-center/backend/services/agent_loader.py` - Line 16
3. `control-center/backend/services/kb_manager.py` - Lines 18-19
4. `control-center/backend/api/agents.py` (likely)
5. `control-center/backend/api/comfyui.py` (likely)
6. `control-center/backend/api/knowledge.py` (likely)
7. `ai-agents/knowledge-base/.env` - Lines 26-35
8. Various test files in `control-center/tests/`

---

## File Mapping Strategy

### Migration Mapping
```
SOURCE                                  → DESTINATION
─────────────────────────────────────────────────────────────
C:\meowping-rts\ai-agents\              → C:\Ziggie\ai-agents\
C:\meowping-rts\control-center\         → C:\Ziggie\control-center\
C:\meowping-rts\.claude\                → C:\Ziggie\.claude\
C:\ComfyUI\.claude\                     → (stays, may update references)
```

### Directory Organization at C:\Ziggie
```
C:\Ziggie\
├── ai-agents\                   (from meowping-rts)
│   ├── *.md                     (8 agent definition files)
│   ├── knowledge-base\          (complete KB system)
│   └── ai-agents\               (generated knowledge)
├── control-center\              (from meowping-rts)
│   ├── backend\
│   ├── frontend\
│   └── tests\
├── .claude\                     (from meowping-rts)
│   └── settings.local.json
└── MIGRATION_PLAN.md           (this file)
```

---

## Migration Steps

### Phase 1: Backup (15 minutes)

**PowerShell Script:** `C:\Ziggie\1_backup.ps1`

```powershell
# 1_backup.ps1 - Create complete backup before migration

$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$backupRoot = "C:\Backups\Migration_$timestamp"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MIGRATION BACKUP - Phase 1" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create backup directory
Write-Host "[1/5] Creating backup directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
Write-Host "✓ Created: $backupRoot" -ForegroundColor Green

# Backup ai-agents
Write-Host "[2/5] Backing up ai-agents (22 MB)..." -ForegroundColor Yellow
Copy-Item -Path "C:\meowping-rts\ai-agents" -Destination "$backupRoot\ai-agents" -Recurse -Force
Write-Host "✓ ai-agents backed up" -ForegroundColor Green

# Backup control-center
Write-Host "[3/5] Backing up control-center (~500 MB, may take time)..." -ForegroundColor Yellow
Copy-Item -Path "C:\meowping-rts\control-center" -Destination "$backupRoot\control-center" -Recurse -Force
Write-Host "✓ control-center backed up" -ForegroundColor Green

# Backup .claude configs
Write-Host "[4/5] Backing up Claude configurations..." -ForegroundColor Yellow
Copy-Item -Path "C:\meowping-rts\.claude" -Destination "$backupRoot\.claude-meowping" -Recurse -Force
Copy-Item -Path "C:\ComfyUI\.claude" -Destination "$backupRoot\.claude-comfyui" -Recurse -Force
Write-Host "✓ Claude configs backed up" -ForegroundColor Green

# Create manifest
Write-Host "[5/5] Creating backup manifest..." -ForegroundColor Yellow
$manifest = @{
    timestamp = $timestamp
    source_ai_agents = "C:\meowping-rts\ai-agents"
    source_control_center = "C:\meowping-rts\control-center"
    destination = "C:\Ziggie"
    files_count = (Get-ChildItem -Path $backupRoot -Recurse -File | Measure-Object).Count
    total_size_mb = [math]::Round((Get-ChildItem -Path $backupRoot -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
}
$manifest | ConvertTo-Json | Out-File "$backupRoot\manifest.json"
Write-Host "✓ Manifest created" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BACKUP COMPLETE!" -ForegroundColor Green
Write-Host "Location: $backupRoot" -ForegroundColor White
Write-Host "Total Size: $($manifest.total_size_mb) MB" -ForegroundColor White
Write-Host "Files: $($manifest.files_count)" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backup location saved to: backup_location.txt" -ForegroundColor Yellow
$backupRoot | Out-File "C:\Ziggie\backup_location.txt"
```

### Phase 2: Copy Files (10 minutes)

**PowerShell Script:** `C:\Ziggie\2_copy_files.ps1`

```powershell
# 2_copy_files.ps1 - Copy files to new location

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FILE COPY - Phase 2" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verify Ziggie directory exists
if (-not (Test-Path "C:\Ziggie")) {
    Write-Host "ERROR: C:\Ziggie does not exist!" -ForegroundColor Red
    exit 1
}

# Copy ai-agents
Write-Host "[1/3] Copying ai-agents..." -ForegroundColor Yellow
Copy-Item -Path "C:\meowping-rts\ai-agents" -Destination "C:\Ziggie\ai-agents" -Recurse -Force
Write-Host "✓ ai-agents copied to C:\Ziggie\ai-agents" -ForegroundColor Green

# Copy control-center
Write-Host "[2/3] Copying control-center (large, please wait)..." -ForegroundColor Yellow
Copy-Item -Path "C:\meowping-rts\control-center" -Destination "C:\Ziggie\control-center" -Recurse -Force
Write-Host "✓ control-center copied to C:\Ziggie\control-center" -ForegroundColor Green

# Copy .claude config
Write-Host "[3/3] Copying Claude configuration..." -ForegroundColor Yellow
Copy-Item -Path "C:\meowping-rts\.claude" -Destination "C:\Ziggie\.claude" -Recurse -Force
Write-Host "✓ .claude copied to C:\Ziggie\.claude" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FILE COPY COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
```

### Phase 3: Update Paths (5 minutes)

**PowerShell Script:** `C:\Ziggie\3_update_paths.ps1`

```powershell
# 3_update_paths.ps1 - Update all hardcoded paths

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PATH UPDATES - Phase 3" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$oldPathMeow = "C:/meowping-rts"
$oldPathMeowEsc = "C:\\meowping-rts"
$newPath = "C:/Ziggie"
$newPathEsc = "C:\\Ziggie"

$filesToUpdate = @(
    "C:\Ziggie\control-center\backend\config.py",
    "C:\Ziggie\control-center\backend\services\agent_loader.py",
    "C:\Ziggie\control-center\backend\services\kb_manager.py",
    "C:\Ziggie\control-center\backend\api\agents.py",
    "C:\Ziggie\control-center\backend\api\comfyui.py",
    "C:\Ziggie\control-center\backend\api\knowledge.py",
    "C:\Ziggie\control-center\backend\api\projects.py",
    "C:\Ziggie\ai-agents\knowledge-base\.env"
)

$updateCount = 0
foreach ($file in $filesToUpdate) {
    if (Test-Path $file) {
        Write-Host "Updating: $file" -ForegroundColor Yellow

        $content = Get-Content $file -Raw
        $originalContent = $content

        # Replace both forward slash and backslash versions
        $content = $content -replace [regex]::Escape($oldPathMeow), $newPath
        $content = $content -replace [regex]::Escape($oldPathMeowEsc), $newPathEsc

        if ($content -ne $originalContent) {
            $content | Set-Content $file -NoNewline
            $updateCount++
            Write-Host "  ✓ Updated" -ForegroundColor Green
        } else {
            Write-Host "  - No changes needed" -ForegroundColor Gray
        }
    } else {
        Write-Host "  ⚠ File not found: $file" -ForegroundColor Yellow
    }
}

# Update test files
Write-Host ""
Write-Host "Updating test files..." -ForegroundColor Yellow
$testFiles = Get-ChildItem "C:\Ziggie\control-center\tests" -Filter "*.py" -Recurse
foreach ($file in $testFiles) {
    $content = Get-Content $file.FullName -Raw
    $originalContent = $content

    $content = $content -replace [regex]::Escape($oldPathMeow), $newPath
    $content = $content -replace [regex]::Escape($oldPathMeowEsc), $newPathEsc

    if ($content -ne $originalContent) {
        $content | Set-Content $file.FullName -NoNewline
        $updateCount++
        Write-Host "  ✓ Updated: $($file.Name)" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PATH UPDATES COMPLETE!" -ForegroundColor Green
Write-Host "Files updated: $updateCount" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
```

### Phase 4: Verification (5 minutes)

**PowerShell Script:** `C:\Ziggie\4_verify.ps1`

```powershell
# 4_verify.ps1 - Verify migration success

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VERIFICATION - Phase 4" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$issues = @()

# Check directory structure
Write-Host "[1/6] Verifying directory structure..." -ForegroundColor Yellow
$requiredDirs = @(
    "C:\Ziggie\ai-agents",
    "C:\Ziggie\ai-agents\knowledge-base",
    "C:\Ziggie\control-center",
    "C:\Ziggie\control-center\backend",
    "C:\Ziggie\control-center\frontend",
    "C:\Ziggie\.claude"
)

foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "  ✓ $dir" -ForegroundColor Green
    } else {
        Write-Host "  ✗ MISSING: $dir" -ForegroundColor Red
        $issues += "Missing directory: $dir"
    }
}

# Check critical files
Write-Host ""
Write-Host "[2/6] Verifying critical files..." -ForegroundColor Yellow
$criticalFiles = @(
    "C:\Ziggie\ai-agents\knowledge-base\manage.py",
    "C:\Ziggie\ai-agents\knowledge-base\.env",
    "C:\Ziggie\control-center\backend\main.py",
    "C:\Ziggie\control-center\backend\config.py",
    "C:\Ziggie\control-center\backend\control-center.db",
    "C:\Ziggie\control-center\frontend\package.json"
)

foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ MISSING: $file" -ForegroundColor Red
        $issues += "Missing file: $file"
    }
}

# Check for old paths in config
Write-Host ""
Write-Host "[3/6] Checking for unreplaced old paths..." -ForegroundColor Yellow
$configFile = "C:\Ziggie\control-center\backend\config.py"
if (Test-Path $configFile) {
    $content = Get-Content $configFile -Raw
    if ($content -match "C:/meowping-rts" -or $content -match "C:\\\\meowping-rts") {
        Write-Host "  ✗ Old paths still found in config.py" -ForegroundColor Red
        $issues += "config.py contains old paths"
    } else {
        Write-Host "  ✓ No old paths in config.py" -ForegroundColor Green
    }
}

# Check .env file
Write-Host ""
Write-Host "[4/6] Verifying .env configuration..." -ForegroundColor Yellow
$envFile = "C:\Ziggie\ai-agents\knowledge-base\.env"
if (Test-Path $envFile) {
    $content = Get-Content $envFile -Raw
    if ($content -match "C:/meowping-rts" -or $content -match "C:\\\\meowping-rts") {
        Write-Host "  ✗ Old paths still found in .env" -ForegroundColor Red
        $issues += ".env contains old paths"
    } else {
        Write-Host "  ✓ .env paths updated" -ForegroundColor Green
    }
} else {
    Write-Host "  ✗ .env file missing" -ForegroundColor Red
    $issues += ".env file missing"
}

# Count files
Write-Host ""
Write-Host "[5/6] Counting migrated files..." -ForegroundColor Yellow
$aiAgentsCount = (Get-ChildItem "C:\Ziggie\ai-agents" -Recurse -File | Measure-Object).Count
$controlCenterCount = (Get-ChildItem "C:\Ziggie\control-center" -Recurse -File | Measure-Object).Count
Write-Host "  AI Agents: $aiAgentsCount files" -ForegroundColor White
Write-Host "  Control Center: $controlCenterCount files" -ForegroundColor White

# Calculate sizes
Write-Host ""
Write-Host "[6/6] Calculating sizes..." -ForegroundColor Yellow
$aiAgentsSize = [math]::Round((Get-ChildItem "C:\Ziggie\ai-agents" -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
$controlCenterSize = [math]::Round((Get-ChildItem "C:\Ziggie\control-center" -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
Write-Host "  AI Agents: $aiAgentsSize MB" -ForegroundColor White
Write-Host "  Control Center: $controlCenterSize MB" -ForegroundColor White

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($issues.Count -eq 0) {
    Write-Host "VERIFICATION PASSED!" -ForegroundColor Green
    Write-Host "All checks completed successfully." -ForegroundColor Green
} else {
    Write-Host "VERIFICATION FAILED!" -ForegroundColor Red
    Write-Host "Issues found:" -ForegroundColor Red
    foreach ($issue in $issues) {
        Write-Host "  - $issue" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "DO NOT PROCEED. Review issues and re-run migration." -ForegroundColor Red
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Save report
$report = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    passed = ($issues.Count -eq 0)
    issues = $issues
    file_counts = @{
        ai_agents = $aiAgentsCount
        control_center = $controlCenterCount
    }
    sizes_mb = @{
        ai_agents = $aiAgentsSize
        control_center = $controlCenterSize
    }
}
$report | ConvertTo-Json -Depth 10 | Out-File "C:\Ziggie\verification_report.json"
Write-Host "Report saved to: C:\Ziggie\verification_report.json" -ForegroundColor Yellow
```

---

## Path Update Requirements

### Critical Files Requiring Updates

#### 1. Control Center Backend Config
**File:** `C:\Ziggie\control-center\backend\config.py`

**Changes:**
```python
# OLD
COMFYUI_DIR: Path = Path(r"C:\ComfyUI")  # NO CHANGE - ComfyUI stays
MEOWPING_DIR: Path = Path(r"C:\meowping-rts")  # CHANGE THIS

# NEW
COMFYUI_DIR: Path = Path(r"C:\ComfyUI")  # Unchanged
MEOWPING_DIR: Path = Path(r"C:\Ziggie")  # Updated

# Service configurations - update cwd paths
"kb_scheduler": {
    "cwd": str(Path(r"C:\Ziggie\ai-agents")),  # Was C:\meowping-rts\ai-agents
    ...
}
```

#### 2. Agent Loader Service
**File:** `C:\Ziggie\control-center\backend\services\agent_loader.py`

**Changes:**
```python
# OLD
self.ai_agents_root = Path("C:/meowping-rts/ai-agents")

# NEW
self.ai_agents_root = Path("C:/Ziggie/ai-agents")
```

#### 3. Knowledge Base Manager
**File:** `C:\Ziggie\control-center\backend\services\kb_manager.py`

**Changes:**
```python
# OLD
self.kb_root = Path("C:/meowping-rts/ai-agents/knowledge-base")
self.ai_agents_root = Path("C:/meowping-rts/ai-agents")

# NEW
self.kb_root = Path("C:/Ziggie/ai-agents/knowledge-base")
self.ai_agents_root = Path("C:/Ziggie/ai-agents")
```

#### 4. Knowledge Base Environment
**File:** `C:\Ziggie\ai-agents\knowledge-base\.env`

**Changes:**
```bash
# OLD
KB_PATH=C:\meowping-rts\ai-agents\knowledge-base
LOG_PATH=C:\meowping-rts\ai-agents\knowledge-base\logs
METADATA_PATH=C:\meowping-rts\ai-agents\knowledge-base\metadata
TEMP_PATH=C:\meowping-rts\ai-agents\knowledge-base\temp

# NEW
KB_PATH=C:\Ziggie\ai-agents\knowledge-base
LOG_PATH=C:\Ziggie\ai-agents\knowledge-base\logs
METADATA_PATH=C:\Ziggie\ai-agents\knowledge-base\metadata
TEMP_PATH=C:\Ziggie\ai-agents\knowledge-base\temp
```

### Path Update Pattern
**Search for:** `C:/meowping-rts` OR `C:\\meowping-rts`
**Replace with:** `C:/Ziggie` OR `C:\\Ziggie`

**Preserve:** All `C:/ComfyUI` and `C:\\ComfyUI` paths remain unchanged

---

## Verification Steps

### Manual Verification Checklist

#### 1. File System Check
```powershell
# Verify directory structure
Test-Path C:\Ziggie\ai-agents
Test-Path C:\Ziggie\control-center
Test-Path C:\Ziggie\.claude

# Count files
(Get-ChildItem C:\Ziggie\ai-agents -Recurse -File).Count
# Expected: ~54 files

(Get-ChildItem C:\Ziggie\control-center -Recurse -File).Count
# Expected: ~1500+ files (including node_modules)
```

#### 2. Configuration Verification
```powershell
# Check for old paths
Select-String -Path "C:\Ziggie\control-center\backend\*.py" -Pattern "C:/meowping-rts" -Recurse
# Expected: No results

Select-String -Path "C:\Ziggie\ai-agents\knowledge-base\.env" -Pattern "C:\\meowping-rts"
# Expected: No results
```

#### 3. Database Integrity
```powershell
# Verify SQLite database exists and is valid
Test-Path C:\Ziggie\control-center\backend\control-center.db
# Expected: True

# Check file size (should be > 0)
(Get-Item C:\Ziggie\control-center\backend\control-center.db).Length
# Expected: > 0 bytes
```

#### 4. Python Dependencies
```powershell
# Verify requirements files exist
Test-Path C:\Ziggie\control-center\backend\requirements.txt
Test-Path C:\Ziggie\ai-agents\knowledge-base\requirements.txt
# Expected: Both True
```

#### 5. Frontend Dependencies
```powershell
# Verify node_modules exists
Test-Path C:\Ziggie\control-center\frontend\node_modules
# Expected: True

# Verify package.json
Test-Path C:\Ziggie\control-center\frontend\package.json
# Expected: True
```

#### 6. Service Startup Test (Optional)
```powershell
# Test backend startup (should fail gracefully with import errors, not path errors)
cd C:\Ziggie\control-center\backend
python main.py
# Expected: Imports load, may fail on missing dependencies, but no FileNotFoundError for C:\meowping-rts
```

---

## Rollback Plan

### If Migration Fails

**PowerShell Script:** `C:\Ziggie\rollback.ps1`

```powershell
# rollback.ps1 - Restore from backup if migration fails

Write-Host "========================================" -ForegroundColor Red
Write-Host "MIGRATION ROLLBACK" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

# Get backup location
if (Test-Path "C:\Ziggie\backup_location.txt") {
    $backupRoot = Get-Content "C:\Ziggie\backup_location.txt" -Raw | ForEach-Object { $_.Trim() }
    Write-Host "Found backup: $backupRoot" -ForegroundColor Yellow
} else {
    Write-Host "ERROR: Cannot find backup location!" -ForegroundColor Red
    Write-Host "Please manually specify backup directory:" -ForegroundColor Yellow
    $backupRoot = Read-Host "Enter backup path"
}

if (-not (Test-Path $backupRoot)) {
    Write-Host "ERROR: Backup directory not found: $backupRoot" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "This will DELETE C:\Ziggie\ai-agents and C:\Ziggie\control-center" -ForegroundColor Red
Write-Host "and restore original files to C:\meowping-rts" -ForegroundColor Red
Write-Host ""
$confirm = Read-Host "Type 'ROLLBACK' to continue"

if ($confirm -ne "ROLLBACK") {
    Write-Host "Rollback cancelled." -ForegroundColor Yellow
    exit 0
}

# Remove migrated directories
Write-Host ""
Write-Host "[1/3] Removing migrated directories from C:\Ziggie..." -ForegroundColor Yellow
if (Test-Path "C:\Ziggie\ai-agents") {
    Remove-Item "C:\Ziggie\ai-agents" -Recurse -Force
    Write-Host "  ✓ Removed ai-agents" -ForegroundColor Green
}
if (Test-Path "C:\Ziggie\control-center") {
    Remove-Item "C:\Ziggie\control-center" -Recurse -Force
    Write-Host "  ✓ Removed control-center" -ForegroundColor Green
}

# Restore to original location (if needed)
Write-Host ""
Write-Host "[2/3] Verifying original files..." -ForegroundColor Yellow
if (-not (Test-Path "C:\meowping-rts\ai-agents")) {
    Write-Host "  Restoring ai-agents to C:\meowping-rts..." -ForegroundColor Yellow
    Copy-Item "$backupRoot\ai-agents" "C:\meowping-rts\ai-agents" -Recurse -Force
    Write-Host "  ✓ Restored ai-agents" -ForegroundColor Green
} else {
    Write-Host "  ✓ Original ai-agents still intact" -ForegroundColor Green
}

if (-not (Test-Path "C:\meowping-rts\control-center")) {
    Write-Host "  Restoring control-center to C:\meowping-rts..." -ForegroundColor Yellow
    Copy-Item "$backupRoot\control-center" "C:\meowping-rts\control-center" -Recurse -Force
    Write-Host "  ✓ Restored control-center" -ForegroundColor Green
} else {
    Write-Host "  ✓ Original control-center still intact" -ForegroundColor Green
}

# Verify restoration
Write-Host ""
Write-Host "[3/3] Verifying restoration..." -ForegroundColor Yellow
$verified = $true
if (-not (Test-Path "C:\meowping-rts\ai-agents")) {
    Write-Host "  ✗ ai-agents not found" -ForegroundColor Red
    $verified = $false
}
if (-not (Test-Path "C:\meowping-rts\control-center")) {
    Write-Host "  ✗ control-center not found" -ForegroundColor Red
    $verified = $false
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($verified) {
    Write-Host "ROLLBACK COMPLETE!" -ForegroundColor Green
    Write-Host "Original files restored to C:\meowping-rts" -ForegroundColor Green
} else {
    Write-Host "ROLLBACK FAILED!" -ForegroundColor Red
    Write-Host "Please manually restore from: $backupRoot" -ForegroundColor Red
}
Write-Host "========================================" -ForegroundColor Cyan
```

### Manual Rollback Steps

1. **Delete migrated files:**
   ```powershell
   Remove-Item C:\Ziggie\ai-agents -Recurse -Force
   Remove-Item C:\Ziggie\control-center -Recurse -Force
   ```

2. **Restore from backup:**
   ```powershell
   # Get backup location from backup_location.txt
   $backup = "C:\Backups\Migration_YYYY-MM-DD_HHMMSS"

   Copy-Item "$backup\ai-agents" "C:\meowping-rts\ai-agents" -Recurse -Force
   Copy-Item "$backup\control-center" "C:\meowping-rts\control-center" -Recurse -Force
   Copy-Item "$backup\.claude-meowping" "C:\meowping-rts\.claude" -Recurse -Force
   ```

3. **Verify restoration:**
   ```powershell
   Test-Path C:\meowping-rts\ai-agents
   Test-Path C:\meowping-rts\control-center
   ```

---

## Post-Migration Tasks

### 1. Service Configuration Updates

#### Update Control Center Startup Scripts
If there are any startup scripts or shortcuts pointing to old locations, update them:

```powershell
# Example: Update startup script
# OLD: cd C:\meowping-rts\control-center\backend
# NEW: cd C:\Ziggie\control-center\backend
```

### 2. Environment Setup

#### Backend Environment
```powershell
cd C:\Ziggie\control-center\backend

# Verify Python environment
python --version

# Install/verify dependencies (if needed)
pip install -r requirements.txt

# Test import
python -c "import config; print(config.settings.MEOWPING_DIR)"
# Expected: C:\Ziggie
```

#### Frontend Environment
```powershell
cd C:\Ziggie\control-center\frontend

# Node modules should already be present
# If needed, reinstall:
# npm install

# Verify
npm list --depth=0
```

#### Knowledge Base Environment
```powershell
cd C:\Ziggie\ai-agents\knowledge-base

# Verify .env file
cat .env | Select-String "KB_PATH"
# Expected: C:\Ziggie\ai-agents\knowledge-base

# Verify Python dependencies
pip install -r requirements.txt
```

### 3. Database Verification

```powershell
# Connect to SQLite database and verify tables
cd C:\Ziggie\control-center\backend

# If sqlite3 is available:
sqlite3 control-center.db ".tables"
# Expected: Show all tables

# Or use Python:
python -c "from database.db import engine; print(engine)"
```

### 4. Start Services Test

#### Test Control Center Backend
```powershell
cd C:\Ziggie\control-center\backend
python main.py

# Expected:
# - Server starts on port 8080
# - No path-related errors
# - Can connect to http://127.0.0.1:8080
```

#### Test Control Center Frontend
```powershell
cd C:\Ziggie\control-center\frontend
npm run dev

# Expected:
# - Vite dev server starts
# - Opens on port 3000
# - Can connect to http://localhost:3000
```

#### Test Knowledge Base Manager
```powershell
cd C:\Ziggie\ai-agents\knowledge-base
python manage.py --help

# Expected:
# - Shows help menu
# - No import errors
# - No path errors
```

### 5. Update Documentation

Files to update with new paths:
- Any README files that reference directory locations
- Internal documentation
- Setup guides
- Developer onboarding docs

### 6. Update Claude Agent Configurations

Create/update `C:\Ziggie\.claude\settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(chmod:*)",
      "Bash(python:*)",
      "Bash(npm:*)",
      "Bash(node:*)",
      "Bash(ls:*)",
      "Bash(cd:*)",
      "Bash(curl:*)"
    ],
    "deny": [],
    "ask": []
  }
}
```

### 7. Clean Up Old Directories (OPTIONAL)

**ONLY after confirming everything works for at least 1 week:**

```powershell
# DANGER ZONE - Only run after thorough testing

# Remove old directories (KEEP BACKUP!)
Remove-Item C:\meowping-rts\ai-agents -Recurse -Force
Remove-Item C:\meowping-rts\control-center -Recurse -Force

# Update meowping-rts documentation
# Add note about new locations in C:\Ziggie
```

### 8. Update Scheduled Tasks (If Any)

If the Knowledge Base scheduler or any other automation is configured:

```powershell
# List scheduled tasks
Get-ScheduledTask | Where-Object {$_.TaskPath -like "*meowping*" -or $_.TaskName -like "*control-center*"}

# Update task paths using Task Scheduler UI or:
# Export task, edit XML, re-import
```

### 9. Final Verification Checklist

```
[] Backend starts without errors
[] Frontend connects to backend successfully
[] Knowledge Base can access agent files
[] Database queries work
[] File uploads/downloads work (if applicable)
[] All API endpoints respond correctly
[] ComfyUI integration still works
[] No hardcoded path errors in logs
[] Backup is still accessible
[] Documentation updated
[] Team notified of new location
```

---

## Master Migration Script

**PowerShell Script:** `C:\Ziggie\migrate_all.ps1`

```powershell
# migrate_all.ps1 - Master migration script
# Runs all phases in sequence with confirmations

param(
    [switch]$SkipBackup = $false,
    [switch]$Auto = $false
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI AGENT & CONTROL CENTER MIGRATION" -ForegroundColor Cyan
Write-Host "C:\meowping-rts → C:\Ziggie" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Pre-flight checks
Write-Host "PRE-FLIGHT CHECKS" -ForegroundColor Yellow
Write-Host "────────────────────────────────────────" -ForegroundColor Gray

# Check if Ziggie exists
if (-not (Test-Path "C:\Ziggie")) {
    Write-Host "✗ C:\Ziggie does not exist!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ C:\Ziggie exists" -ForegroundColor Green

# Check source directories
if (-not (Test-Path "C:\meowping-rts\ai-agents")) {
    Write-Host "✗ Source ai-agents not found" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Source ai-agents found" -ForegroundColor Green

if (-not (Test-Path "C:\meowping-rts\control-center")) {
    Write-Host "✗ Source control-center not found" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Source control-center found" -ForegroundColor Green

# Check for running processes
Write-Host ""
Write-Host "Checking for running services..." -ForegroundColor Yellow
$pythonProcs = Get-Process python -ErrorAction SilentlyContinue
$nodeProcs = Get-Process node -ErrorAction SilentlyContinue

if ($pythonProcs -or $nodeProcs) {
    Write-Host "⚠ WARNING: Python or Node processes are running!" -ForegroundColor Red
    Write-Host "  Please stop Control Center services before continuing." -ForegroundColor Yellow
    if (-not $Auto) {
        $continue = Read-Host "Continue anyway? (y/N)"
        if ($continue -ne "y") { exit 0 }
    }
} else {
    Write-Host "✓ No conflicting processes" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Ready to migrate:" -ForegroundColor White
Write-Host "  • ai-agents (~22 MB, 54 files)" -ForegroundColor White
Write-Host "  • control-center (~500 MB, 1500+ files)" -ForegroundColor White
Write-Host ""
Write-Host "This will:" -ForegroundColor White
Write-Host "  1. Create backup" -ForegroundColor White
Write-Host "  2. Copy files to C:\Ziggie" -ForegroundColor White
Write-Host "  3. Update all hardcoded paths" -ForegroundColor White
Write-Host "  4. Verify migration" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan

if (-not $Auto) {
    Write-Host ""
    $confirm = Read-Host "Proceed with migration? (y/N)"
    if ($confirm -ne "y") {
        Write-Host "Migration cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Phase 1: Backup
Write-Host ""
if (-not $SkipBackup) {
    & "C:\Ziggie\1_backup.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Backup failed! Aborting migration." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⚠ Skipping backup (as requested)" -ForegroundColor Yellow
}

# Phase 2: Copy
Write-Host ""
& "C:\Ziggie\2_copy_files.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "File copy failed! Check errors above." -ForegroundColor Red
    exit 1
}

# Phase 3: Update paths
Write-Host ""
& "C:\Ziggie\3_update_paths.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Path update failed! Check errors above." -ForegroundColor Red
    exit 1
}

# Phase 4: Verify
Write-Host ""
& "C:\Ziggie\4_verify.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Verification failed! Review issues before proceeding." -ForegroundColor Red
    Write-Host "You can rollback using: .\rollback.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MIGRATION COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Test Control Center services" -ForegroundColor White
Write-Host "  2. Test Knowledge Base functionality" -ForegroundColor White
Write-Host "  3. Verify API endpoints" -ForegroundColor White
Write-Host "  4. Keep backup for at least 1 week" -ForegroundColor White
Write-Host ""
Write-Host "Backup location: $(Get-Content C:\Ziggie\backup_location.txt)" -ForegroundColor Yellow
Write-Host "Verification report: C:\Ziggie\verification_report.json" -ForegroundColor Yellow
Write-Host ""
```

---

## Quick Reference Commands

### Run Full Migration
```powershell
cd C:\Ziggie
.\migrate_all.ps1
```

### Run Individual Phases
```powershell
# Phase 1: Backup only
.\1_backup.ps1

# Phase 2: Copy files only
.\2_copy_files.ps1

# Phase 3: Update paths only
.\3_update_paths.ps1

# Phase 4: Verify only
.\4_verify.ps1
```

### Rollback
```powershell
.\rollback.ps1
```

### Manual Path Check
```powershell
# Search for old paths
Select-String -Path "C:\Ziggie\**\*.py" -Pattern "C:/meowping-rts" -Recurse
Select-String -Path "C:\Ziggie\**\.env" -Pattern "C:\\meowping-rts" -Recurse
```

---

## Risk Assessment

### Low Risk Items
- Copying files (original stays intact)
- Creating backups
- Path verification

### Medium Risk Items
- Path replacements (automated, but could miss edge cases)
- Service restarts (may require debugging)

### High Risk Items (Mitigated)
- None (all originals preserved, rollback available)

### Critical Dependencies
1. **ComfyUI** - Must remain at `C:\ComfyUI` (not moved)
2. **meowping-rts game code** - Stays at `C:\meowping-rts` (not moved)
3. **Python environment** - Must be accessible from new location
4. **Node.js** - Must be accessible for frontend

---

## Success Criteria

Migration is successful when:

1. ✓ All files copied to `C:\Ziggie`
2. ✓ No hardcoded paths reference `C:\meowping-rts`
3. ✓ Control Center backend starts without errors
4. ✓ Control Center frontend loads successfully
5. ✓ Knowledge Base can access agent files
6. ✓ Database is accessible and functional
7. ✓ API endpoints respond correctly
8. ✓ ComfyUI integration still works
9. ✓ Backup is verified and accessible
10. ✓ Verification script passes all checks

---

## Timeline

**Total Estimated Time:** 30-45 minutes

- **Backup:** 15 minutes (large file copy)
- **Copy:** 10 minutes (node_modules is large)
- **Path Updates:** 5 minutes (automated)
- **Verification:** 5 minutes (automated + manual checks)
- **Testing:** 10-15 minutes (manual service testing)

---

## Support & Troubleshooting

### Common Issues

#### Issue: "Access Denied" during copy
**Solution:** Run PowerShell as Administrator

#### Issue: Old paths still found after update
**Solution:**
1. Check if files are read-only: `Get-Item <file> | Select-Object IsReadOnly`
2. Remove read-only: `Set-ItemProperty <file> -Name IsReadOnly -Value $false`
3. Re-run path update script

#### Issue: Services won't start
**Solution:**
1. Check logs for specific errors
2. Verify Python/Node paths in environment
3. Check if ports are available
4. Verify database file permissions

#### Issue: Database connection errors
**Solution:**
1. Check database file exists: `Test-Path C:\Ziggie\control-center\backend\control-center.db`
2. Check file permissions
3. Verify SQLite is installed
4. Check database isn't locked by another process

---

## Appendix A: File Inventory

### AI Agents Directory (54 files, ~22 MB)
- 8 agent definition markdown files
- Knowledge base system (Python)
- Metadata and configuration
- Logs and temporary files
- Generated agent knowledge

### Control Center (1500+ files, ~500 MB)
- Backend: FastAPI Python application
- Frontend: React + Vite application
- Tests: Integration and unit tests
- Database: SQLite database file
- node_modules: ~480 MB

---

## Appendix B: Path Reference Table

| Component | Old Path | New Path |
|-----------|----------|----------|
| AI Agents Root | `C:\meowping-rts\ai-agents` | `C:\Ziggie\ai-agents` |
| Knowledge Base | `C:\meowping-rts\ai-agents\knowledge-base` | `C:\Ziggie\ai-agents\knowledge-base` |
| Control Center | `C:\meowping-rts\control-center` | `C:\Ziggie\control-center` |
| Backend | `C:\meowping-rts\control-center\backend` | `C:\Ziggie\control-center\backend` |
| Frontend | `C:\meowping-rts\control-center\frontend` | `C:\Ziggie\control-center\frontend` |
| Claude Config | `C:\meowping-rts\.claude` | `C:\Ziggie\.claude` |
| ComfyUI | `C:\ComfyUI` | `C:\ComfyUI` (NO CHANGE) |
| Game Code | `C:\meowping-rts` | `C:\meowping-rts` (NO CHANGE) |

---

## Appendix C: Dependencies

### External Dependencies (Not Moved)
- ComfyUI: `C:\ComfyUI`
- ComfyUI Python: `C:\ComfyUI\python_embeded\python.exe`
- meowping-rts game code: `C:\meowping-rts\backend`, `frontend`, etc.

### Internal Dependencies (Moving)
- AI agent definitions
- Knowledge base system
- Control Center backend/frontend
- SQLite database
- Claude configurations

---

**End of Migration Plan**

Generated: 2025-11-07
Version: 1.0
Status: Ready for execution
