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
