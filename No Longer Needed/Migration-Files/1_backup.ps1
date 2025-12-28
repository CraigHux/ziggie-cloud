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
