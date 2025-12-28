# Migration Safety & Compliance Plan
**Version:** 1.0
**Date:** 2025-11-07
**Status:** Pre-Migration Safety Documentation
**Scope:** C:\meowping-rts → C:\Ziggie Migration

---

## Table of Contents
1. [Backup Strategy](#backup-strategy)
2. [Risk Assessment](#risk-assessment)
3. [Mitigation Strategies](#mitigation-strategies)
4. [Rollback Plan](#rollback-plan)
5. [Safety Checklist](#safety-checklist)
6. [Recovery Procedures](#recovery-procedures)

---

## Backup Strategy

### Backup Locations & Verification

#### Primary Backup Location
```
Base Path: C:\Backups\Migration_[TIMESTAMP]
├── ai-agents/              (22 MB, 54 files)
├── control-center/         (500 MB+, 1500+ files)
├── .claude-meowping/       (Claude config)
├── .claude-comfyui/        (ComfyUI Claude config)
└── manifest.json           (metadata & verification)
```

#### Backup Verification Checklist
- [ ] Backup directory created with proper timestamp
- [ ] All source files copied (54 files for ai-agents)
- [ ] control-center with node_modules copied (500+ MB)
- [ ] .claude configurations backed up
- [ ] manifest.json created with file count & checksums
- [ ] Backup location recorded in `backup_location.txt`
- [ ] Read-only permissions set on backup (protection)

#### Backup Integrity Verification
```powershell
# After backup completes, verify:
# 1. File counts match
$sourceAICount = (Get-ChildItem "C:\meowping-rts\ai-agents" -Recurse -File).Count
$backupAICount = (Get-ChildItem "C:\Backups\Migration_*\ai-agents" -Recurse -File).Count
# Expected: $sourceAICount -eq $backupAICount

# 2. Check backup manifest exists
Test-Path "C:\Backups\Migration_*/manifest.json"
# Expected: True

# 3. Verify backup size
$backupSize = [math]::Round((Get-ChildItem "C:\Backups\Migration_*" -Recurse -File |
    Measure-Object -Property Length -Sum).Sum / 1MB, 2)
# Expected: ~550+ MB

# 4. Verify backup location recorded
Test-Path "C:\Ziggie\backup_location.txt"
# Expected: True
```

---

## Risk Assessment

### Risk Matrix Summary

| Risk Category | Risk ID | Severity | Status | Mitigation |
|---------------|---------|----------|--------|-----------|
| File Corruption | RISK-001 | HIGH | Mitigated | Full backup + verification |
| Path Breakage | RISK-002 | HIGH | Mitigated | Automated path replacement |
| API Key Exposure | RISK-003 | CRITICAL | Mitigated | Secured .env backup |
| Service Disruption | RISK-004 | MEDIUM | Mitigated | Rollback capability |
| Config Mismatch | RISK-005 | MEDIUM | Mitigated | Verification scripts |
| Database Corruption | RISK-006 | HIGH | Mitigated | Database integrity check |

### Detailed Risk Analysis

#### RISK-001: File Corruption During Copy
**Severity:** HIGH
**Probability:** LOW
**Impact:** Complete system failure if critical files corrupted

**Mitigation:**
1. **Backup First** - Complete backup before any copy operations
2. **Incremental Verification** - Verify file counts after each copy phase
3. **Hash Verification** - Create manifest with file hashes
4. **Rollback Available** - Can restore from backup if corruption detected

**Detection Method:**
```powershell
# After file copy, verify integrity
$files = Get-ChildItem "C:\Ziggie\ai-agents" -Recurse -File
foreach ($file in $files) {
    if ($file.Length -eq 0 -and $file.Name -ne ".gitkeep") {
        Write-Warning "Empty file detected: $($file.FullName)"
    }
}
```

---

#### RISK-002: Path References Breaking in Code
**Severity:** HIGH
**Probability:** MEDIUM
**Impact:** Backend/frontend services fail to start; Cannot find resources

**Mitigation:**
1. **Automated Path Replacement** - PowerShell script replaces all hardcoded paths
2. **Verification Scan** - Verify no old paths remain after replacement
3. **Regex Patterns** - Search for both forward-slash and backslash versions:
   - Pattern 1: `C:/meowping-rts`
   - Pattern 2: `C:\\meowping-rts`

**Files Requiring Updates (Verified):**
```
C:\Ziggie\control-center\backend\config.py
C:\Ziggie\control-center\backend\services\agent_loader.py
C:\Ziggie\control-center\backend\services\kb_manager.py
C:\Ziggie\control-center\backend\api\agents.py
C:\Ziggie\control-center\backend\api\comfyui.py
C:\Ziggie\control-center\backend\api\knowledge.py
C:\Ziggie\control-center\backend\api\projects.py
C:\Ziggie\ai-agents\knowledge-base\.env
```

**Detection Method:**
```powershell
# After path replacement, scan for remaining old paths
Select-String -Path "C:\Ziggie\**\*.py" `
    -Pattern "C:/meowping-rts|C:\\meowping-rts" `
    -Recurse

Select-String -Path "C:\Ziggie\ai-agents\knowledge-base\.env" `
    -Pattern "C:/meowping-rts|C:\\meowping-rts"

# Expected: No results found
```

---

#### RISK-003: API Keys & Secrets Exposure
**Severity:** CRITICAL
**Probability:** LOW (with proper handling)
**Impact:** Unauthorized access to systems and services

**Sensitive Files Identified:**
```
C:\Ziggie\ai-agents\knowledge-base\.env
├── OPENAI_API_KEY=***
├── ANTHROPIC_API_KEY=***
├── COMFYUI_API_KEY=***
└── DATABASE_PASSWORD=***
```

**Mitigation:**
1. **Backup Security** - Backup stored securely with restricted access
2. **Environment Isolation** - .env files not committed to version control
3. **Permission Control** - Backup directory marked read-only
4. **Segregated Backup** - API keys only in isolated backup, not in general files

**Pre-Migration Safety:**
- [ ] Backup location secured with restricted permissions
- [ ] .env file permissions set to read-only (owner only)
- [ ] No API keys logged during backup process
- [ ] Backup stored on secure drive (not network share)

---

#### RISK-004: Running Services Disruption
**Severity:** MEDIUM
**Probability:** MEDIUM
**Impact:** System downtime, incomplete requests lost

**Services to Stop Before Migration:**
```
1. Control Center Backend (Port 8080)
   - Process: python main.py
   - Location: C:\meowping-rts\control-center\backend

2. Control Center Frontend (Port 3000)
   - Process: npm run dev
   - Location: C:\meowping-rts\control-center\frontend

3. Knowledge Base Scheduler
   - Process: python manage.py
   - Location: C:\meowping-rts\ai-agents\knowledge-base

4. ComfyUI (Port 8188)
   - Process: python main.py
   - Location: C:\ComfyUI
   - Note: May stay running if not in migration path
```

**Mitigation:**
1. **Pre-Migration Shutdown** - All services stopped before starting backup
2. **Port Verification** - Confirm ports are free before file operations
3. **Process Monitoring** - Check for residual processes
4. **Graceful Restart** - Services restarted only after verification passes

**Service Stop Procedure:**
```powershell
# Check for running processes
tasklist | findstr /I "python node"

# Check for port usage
netstat -ano | findstr "8080 8188 3000"

# Kill processes if needed (gracefully first)
Stop-Process -Name python -ErrorAction SilentlyContinue
Stop-Process -Name node -ErrorAction SilentlyContinue

# Verify ports are free
Test-NetConnection -ComputerName localhost -Port 8080 -WarningAction SilentlyContinue
Test-NetConnection -ComputerName localhost -Port 3000 -WarningAction SilentlyContinue
Test-NetConnection -ComputerName localhost -Port 8188 -WarningAction SilentlyContinue
```

---

#### RISK-005: Configuration Mismatch
**Severity:** MEDIUM
**Probability:** LOW
**Impact:** Services start but with wrong paths, data not found

**Configuration Files to Verify:**
```
C:\Ziggie\control-center\backend\config.py
├── COMFYUI_DIR: Path
├── MEOWPING_DIR: Path → Should be C:\Ziggie
├── AI_AGENTS_DIR: Path
└── KB_PATH: Path

C:\Ziggie\ai-agents\knowledge-base\.env
├── KB_PATH=C:\Ziggie\ai-agents\knowledge-base
├── LOG_PATH=C:\Ziggie\ai-agents\knowledge-base\logs
├── METADATA_PATH=C:\Ziggie\ai-agents\knowledge-base\metadata
└── TEMP_PATH=C:\Ziggie\ai-agents\knowledge-base\temp
```

**Verification Method:**
```powershell
# Check config.py for correct paths
$config = Get-Content "C:\Ziggie\control-center\backend\config.py" -Raw
if ($config -match 'MEOWPING_DIR.*"C:\\Ziggie"') {
    Write-Host "✓ config.py paths correct"
} else {
    Write-Host "✗ config.py paths incorrect"
}

# Check .env for correct paths
$env = Get-Content "C:\Ziggie\ai-agents\knowledge-base\.env" -Raw
if ($env -match 'KB_PATH=C:\\Ziggie') {
    Write-Host "✓ .env paths correct"
} else {
    Write-Host "✗ .env paths incorrect"
}
```

---

#### RISK-006: Database Location Changes
**Severity:** HIGH
**Probability:** LOW
**Impact:** Database inaccessible, data loss

**Database Files:**
```
C:\Ziggie\control-center\backend\control-center.db
├── Location: Same relative path as source
├── Size: 73 KB (backed up)
└── Integrity: SQLite database
```

**Database Verification:**
```powershell
# Check database file exists
Test-Path "C:\Ziggie\control-center\backend\control-center.db"
# Expected: True

# Check file size (should be > 0)
$db = Get-Item "C:\Ziggie\control-center\backend\control-center.db"
Write-Host "Database size: $($db.Length) bytes"
# Expected: > 0 bytes

# Verify with Python
python -c "
import sqlite3
db = sqlite3.connect(r'C:\Ziggie\control-center\backend\control-center.db')
cursor = db.cursor()
cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")
tables = cursor.fetchall()
print(f'Tables found: {len(tables)}')
db.close()
"
```

---

## Mitigation Strategies

### Pre-Migration Safety Measures

#### 1. System Readiness
```powershell
# ✓ Verify disk space
$drive = Get-Volume -DriveLetter C
$freeGB = [math]::Round($drive.SizeRemaining / 1GB, 2)
Write-Host "Free space: $freeGB GB"
# Expected: > 2 GB (backup ~550 MB + copy ~550 MB + buffer)

# ✓ Check Windows Admin status
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) { Write-Error "Must run as Administrator" }

# ✓ Verify C:\Ziggie exists and is writable
New-Item -ItemType Directory -Path "C:\Ziggie" -Force -ErrorAction SilentlyContinue
Test-Path "C:\Ziggie"
# Expected: True
```

#### 2. Service Shutdown Procedure
```powershell
# ✓ Stop all services gracefully
Write-Host "Stopping services..."

# List all Python processes
$pythonProcs = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcs) {
    foreach ($proc in $pythonProcs) {
        Write-Host "Stopping Python process: $($proc.Name) (PID: $($proc.Id))"
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
}

# List all Node processes
$nodeProcs = Get-Process node -ErrorAction SilentlyContinue
if ($nodeProcs) {
    foreach ($proc in $nodeProcs) {
        Write-Host "Stopping Node process: $($proc.Name) (PID: $($proc.Id))"
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
}

# ✓ Verify ports are free
Start-Sleep -Seconds 3
Write-Host "Verifying ports are free..."
foreach ($port in @(8080, 8188, 3000)) {
    $conn = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
    if ($conn.TcpTestSucceeded) {
        Write-Error "Port $port still in use!"
    } else {
        Write-Host "✓ Port $port is free"
    }
}
```

#### 3. Environment Variable Documentation
```powershell
# Document current environment before migration
Write-Host "Documenting environment variables..."

$envVars = @{
    PYTHON_PATH = $env:PYTHON_PATH
    PYTHONHOME = $env:PYTHONHOME
    NODE_PATH = $env:NODE_PATH
    PATH = $env:PATH
    APPDATA = $env:APPDATA
    LOCALAPPDATA = $env:LOCALAPPDATA
    TEMP = $env:TEMP
}

$envVars | ConvertTo-Json | Out-File "C:\Ziggie\env_backup.json"
Write-Host "✓ Environment variables backed up to env_backup.json"
```

#### 4. Current Working Directory Recording
```powershell
# Record current working directories for verification
$cwd = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    comfyui_dir = if (Test-Path "C:\ComfyUI") { "C:\ComfyUI" } else { "NOT FOUND" }
    meowping_dir = if (Test-Path "C:\meowping-rts") { "C:\meowping-rts" } else { "NOT FOUND" }
    ziggie_dir = if (Test-Path "C:\Ziggie") { "C:\Ziggie" } else { "NOT FOUND" }
    python_exe = (Get-Command python -ErrorAction SilentlyContinue).Source
    node_exe = (Get-Command node -ErrorAction SilentlyContinue).Source
}

$cwd | ConvertTo-Json | Out-File "C:\Ziggie\working_dirs.json"
Write-Host "✓ Working directories recorded"
```

---

## Rollback Plan

### Quick Rollback (< 5 minutes)

**Step 1: Stop New Services**
```powershell
# Stop any services running from new location
Stop-Process -Name python -Force -ErrorAction SilentlyContinue
Stop-Process -Name node -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
```

**Step 2: Delete Migrated Files**
```powershell
# Remove files copied to new location
Remove-Item "C:\Ziggie\ai-agents" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "C:\Ziggie\control-center" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "✓ Deleted migrated directories from C:\Ziggie"
```

**Step 3: Restore from Backup**
```powershell
# Get backup location
$backupRoot = Get-Content "C:\Ziggie\backup_location.txt" -Raw | ForEach-Object { $_.Trim() }

# Restore to original location
Copy-Item "$backupRoot\ai-agents" "C:\meowping-rts\ai-agents" -Recurse -Force
Copy-Item "$backupRoot\control-center" "C:\meowping-rts\control-center" -Recurse -Force

Write-Host "✓ Restored files from backup"
```

**Step 4: Verify Restoration**
```powershell
# Verify original location restored
$aiAgentsExists = Test-Path "C:\meowping-rts\ai-agents\knowledge-base"
$controlCenterExists = Test-Path "C:\meowping-rts\control-center\backend"

if ($aiAgentsExists -and $controlCenterExists) {
    Write-Host "✓ Rollback successful - original files restored"
} else {
    Write-Host "✗ Rollback failed - contact support"
}
```

### Full Rollback Procedure (if Quick Rollback Fails)

**Step 1: Manual Restoration**
```powershell
# If automatic rollback fails, manually restore from backup
$backupPath = Read-Host "Enter full path to backup directory"
# Example: C:\Backups\Migration_2025-11-07_143022

if (-not (Test-Path $backupPath)) {
    Write-Host "ERROR: Backup path not found!"
    exit 1
}

# Stop running processes
taskkill /IM python.exe /F 2>$null
taskkill /IM node.exe /F 2>$null

# Copy files back
Copy-Item "$backupPath\ai-agents" "C:\meowping-rts\ai-agents" -Recurse -Force
Copy-Item "$backupPath\control-center" "C:\meowping-rts\control-center" -Recurse -Force
Copy-Item "$backupPath\.claude-meowping" "C:\meowping-rts\.claude" -Recurse -Force
```

**Step 2: Verify Old Location**
```powershell
# Verify files are back in original location
$aiAgentsFiles = (Get-ChildItem "C:\meowping-rts\ai-agents" -Recurse -File).Count
$controlCenterFiles = (Get-ChildItem "C:\meowping-rts\control-center" -Recurse -File).Count

Write-Host "ai-agents files: $aiAgentsFiles (expected ~54)"
Write-Host "control-center files: $controlCenterFiles (expected ~1500)"

if ($aiAgentsFiles -gt 50 -and $controlCenterFiles -gt 1000) {
    Write-Host "✓ Files restored successfully"
} else {
    Write-Host "✗ File count mismatch - verify manually"
}
```

**Step 3: Recovery Time Estimates**
```
Quick Rollback: 3-5 minutes
  - Stop services: 1 min
  - Delete files: 1 min
  - Restore from backup: 2-3 min
  - Verify: 1 min

Full Rollback: 5-10 minutes
  - Manual file operations: 5-10 min
  - Verification: 5 min
  - Service restart: 2 min

Total Maximum Recovery Time: 10-15 minutes
```

---

## Safety Checklist

### Pre-Migration Checklist (Day Of)

#### System Preparation
- [ ] Administrator privileges confirmed
- [ ] C:\Ziggie directory exists and is writable
- [ ] Minimum 2 GB free space verified on C: drive
- [ ] Backup target location prepared (C:\Backups\)
- [ ] Network connectivity verified (if remote backup)
- [ ] Antivirus/Windows Defender disabled temporarily
- [ ] All editor windows closed (no file locks)

#### Service Status
- [ ] Control Center backend stopped
- [ ] Control Center frontend stopped
- [ ] Knowledge Base scheduler stopped
- [ ] ComfyUI stopped (if in migration path)
- [ ] No Python processes running: `tasklist | findstr python`
- [ ] No Node processes running: `tasklist | findstr node`
- [ ] Port 8080 is free: `netstat -ano | findstr 8080`
- [ ] Port 3000 is free: `netstat -ano | findstr 3000`
- [ ] Port 8188 is free: `netstat -ano | findstr 8188`

#### Documentation
- [ ] Current working directory recorded (`working_dirs.json`)
- [ ] Environment variables documented (`env_backup.json`)
- [ ] Database backed up separately (control-center.db)
- [ ] API keys secured in backup
- [ ] List of affected team members prepared
- [ ] Support contact information available

#### Backup Verification
- [ ] Backup directory created: `C:\Backups\Migration_[TIMESTAMP]`
- [ ] All files copied to backup (54 files in ai-agents)
- [ ] Backup size verified (~550 MB+)
- [ ] Manifest file created
- [ ] Backup location recorded: `backup_location.txt`
- [ ] Backup access permissions set correctly
- [ ] Backup readable and verifiable

#### Pre-Flight Test (Optional)
- [ ] Migration scripts tested on similar system
- [ ] Rollback scripts tested and verified working
- [ ] Path replacement regex validated
- [ ] No Python syntax errors in migration scripts
- [ ] PowerShell execution policy allows scripts

---

### During Migration Checklist

#### Phase 1: Backup (15 minutes)
- [ ] Backup script started
- [ ] Progress messages visible in console
- [ ] No errors during file copy
- [ ] All subdirectories created in backup
- [ ] Manifest.json file created
- [ ] Backup completion confirmed

#### Phase 2: File Copy (10 minutes)
- [ ] File copy script started
- [ ] AI Agents directory copied
- [ ] Control Center directory copied (node_modules included)
- [ ] .claude configuration copied
- [ ] No permission errors encountered
- [ ] No "file in use" errors

#### Phase 3: Path Updates (5 minutes)
- [ ] Path update script started
- [ ] config.py file updated
- [ ] All .py files updated (checked count)
- [ ] .env file updated with new paths
- [ ] All test files updated
- [ ] No read-only file errors

#### Phase 4: Verification (5 minutes)
- [ ] Verification script started
- [ ] All required directories found
- [ ] All critical files present
- [ ] No old paths found in config files
- [ ] File count matches expected
- [ ] Database file verified
- [ ] Verification report generated: `verification_report.json`
- [ ] Verification passed (0 issues)

---

### Post-Migration Checklist

#### Immediate Verification (< 1 hour)
- [ ] No Python import errors
- [ ] Backend starts without FileNotFoundError
- [ ] Frontend loads in browser
- [ ] API endpoints respond
- [ ] Database queries work
- [ ] Knowledge Base can access agent files
- [ ] ComfyUI integration verified

#### Extended Testing (1-7 days)
- [ ] User acceptance testing completed
- [ ] No runtime path errors in logs
- [ ] All features function correctly
- [ ] File uploads/downloads work
- [ ] Agent system operational
- [ ] No crashes or unexpected errors
- [ ] Performance acceptable

#### Cleanup & Archive
- [ ] Backup verified and accessible
- [ ] Verification report reviewed
- [ ] Migration logs archived
- [ ] Team notified of completion
- [ ] Documentation updated
- [ ] Old location cleanup approved
- [ ] Old files deleted (only after 1 week success)

---

## Recovery Procedures

### Scenario 1: Files Corrupted During Copy

**Detection:**
```powershell
# Empty file detected
$emptyFiles = Get-ChildItem "C:\Ziggie" -Recurse -File | Where-Object { $_.Length -eq 0 }
if ($emptyFiles) {
    Write-Host "✗ Corrupted files detected!"
    foreach ($file in $emptyFiles) {
        Write-Host "  - $($file.FullName)"
    }
}
```

**Recovery:**
1. Stop all services
2. Delete corrupted files: `Remove-Item C:\Ziggie\ai-agents -Recurse -Force`
3. Restore from backup: `Copy-Item "$backup\ai-agents" "C:\Ziggie\ai-agents" -Recurse -Force`
4. Re-run verification script

---

### Scenario 2: Database Locked/Inaccessible

**Detection:**
```powershell
# Check if database is locked
$dbPath = "C:\Ziggie\control-center\backend\control-center.db"
try {
    [IO.FileStream]$fs = [IO.File]::Open($dbPath, 'Open', 'Read')
    $fs.Close()
    Write-Host "✓ Database accessible"
} catch {
    Write-Host "✗ Database locked: $_"
}
```

**Recovery:**
1. Check for processes holding lock:
   ```powershell
   Get-Process | Where-Object { $_.Handles -gt 1000 }
   ```
2. Kill offending processes: `Stop-Process -Name python -Force`
3. Copy fresh database from backup
4. Restart services

---

### Scenario 3: Path Updates Incomplete

**Detection:**
```powershell
# Scan for old paths
$oldPaths = Select-String -Path "C:\Ziggie\**\*.py" `
    -Pattern "C:/meowping-rts|C:\\meowping-rts" `
    -Recurse

if ($oldPaths) {
    Write-Host "✗ Old paths found in:"
    $oldPaths | ForEach-Object { Write-Host "  - $($_.Path)" }
}
```

**Recovery:**
1. Re-run path update script: `.\3_update_paths.ps1`
2. Manually edit remaining files
3. Re-run verification: `.\4_verify.ps1`

---

### Scenario 4: Services Won't Start

**Detection:**
```powershell
# Test backend startup
cd C:\Ziggie\control-center\backend
python main.py 2>&1 | Tee-Object -FilePath startup_error.log

# Check for errors in log
Select-String "Error|Exception|FileNotFoundError" startup_error.log
```

**Recovery:**
1. Check logs for specific error message
2. If path error: Re-run path updates
3. If import error: Verify dependencies installed
4. If port error: Check netstat for conflicts
5. If all else fails: Rollback to previous state

---

### Scenario 5: Complete Migration Failure

**Recovery Procedure:**

```powershell
# STEP 1: Stop all services
Write-Host "EMERGENCY STOP - Stopping all services..."
taskkill /IM python.exe /F 2>$null
taskkill /IM node.exe /F 2>$null
Start-Sleep -Seconds 5

# STEP 2: Get backup location
$backupLocation = Get-Content "C:\Ziggie\backup_location.txt" -Raw
$backupLocation = $backupLocation.Trim()

if (-not (Test-Path $backupLocation)) {
    Write-Host "ERROR: Cannot find backup at $backupLocation"
    Write-Host "Manual recovery required. Backup may be at:"
    Get-ChildItem "C:\Backups" -Directory | Sort-Object CreationTime -Descending | Select-Object -First 5
    exit 1
}

# STEP 3: Delete migrated content
Write-Host "Removing migrated content..."
Remove-Item "C:\Ziggie\ai-agents" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "C:\Ziggie\control-center" -Recurse -Force -ErrorAction SilentlyContinue

# STEP 4: Restore original
Write-Host "Restoring original content..."
Copy-Item "$backupLocation\ai-agents" "C:\meowping-rts\ai-agents" -Recurse -Force
Copy-Item "$backupLocation\control-center" "C:\meowping-rts\control-center" -Recurse -Force

# STEP 5: Verify
$ai = Test-Path "C:\meowping-rts\ai-agents\knowledge-base\manage.py"
$cc = Test-Path "C:\meowping-rts\control-center\backend\main.py"

if ($ai -and $cc) {
    Write-Host "✓ RECOVERY SUCCESSFUL"
    Write-Host "Original files restored to C:\meowping-rts"
} else {
    Write-Host "✗ RECOVERY FAILED"
    Write-Host "Manual intervention required"
    Write-Host "Contact support with backup location: $backupLocation"
}
```

---

## Critical Contacts & Resources

### Support Information
- **Migration Owner:** [Your Name]
- **Contact:** [Your Email/Phone]
- **Escalation:** [Team Lead/Manager]
- **Backup Location:** Recorded in `C:\Ziggie\backup_location.txt`

### Documentation References
- **Full Migration Plan:** `C:\Ziggie\MIGRATION_PLAN.md`
- **Quick Reference:** `C:\Ziggie\MIGRATION_QUICKREF.txt`
- **Architecture:** `C:\Ziggie\ARCHITECTURE.md`

### External Dependencies
- **ComfyUI:** Remains at `C:\ComfyUI` (NOT moved)
- **Game Code:** Remains at `C:\meowping-rts` (NOT moved)
- **Python:** Verify accessible from new location
- **Node.js:** Verify accessible from new location

---

## Sign-Off

**This migration safety plan ensures:**

1. ✓ Complete backup before any changes
2. ✓ Risk assessment for all critical areas
3. ✓ Automated mitigation strategies
4. ✓ Detailed rollback procedures
5. ✓ Pre-flight safety checklist
6. ✓ Emergency recovery procedures
7. ✓ Recovery time <15 minutes

**Migration Approval:**
- [ ] Technical Lead Review: _______________ Date: ______
- [ ] IT Security Review: _______________ Date: ______
- [ ] Project Manager Approval: _______________ Date: ______

**Pre-Migration Confirmation:**
- [ ] All checklist items completed
- [ ] Backup verified and accessible
- [ ] Rollback procedures tested
- [ ] Team notified
- [ ] Ready to proceed

---

**Document Version:** 1.0
**Last Updated:** 2025-11-07
**Status:** Ready for Migration Execution
**Next Step:** Execute Pre-Migration Checklist, then run `migrate_all.ps1`

---
