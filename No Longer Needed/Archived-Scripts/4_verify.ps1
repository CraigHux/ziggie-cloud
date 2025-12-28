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
