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
