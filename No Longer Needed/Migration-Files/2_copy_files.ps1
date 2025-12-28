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
