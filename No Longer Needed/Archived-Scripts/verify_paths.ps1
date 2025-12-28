# ============================================
# Ziggie - Path Verification Script
# ============================================
#
# This script verifies that all paths have been
# correctly updated to C:\Ziggie and that no
# old paths remain from C:\meowping-rts
#
# Usage: .\verify_paths.ps1
#

param(
    [switch]$Detailed,
    [switch]$Fix
)

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Ziggie - Path Verification" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$script:issuesFound = 0
$script:directoriesChecked = 0
$script:filesChecked = 0

# ============================================
# FUNCTION: Check for old paths in files
# ============================================
function Check-OldPaths {
    Write-Host "Checking for old paths in files..." -ForegroundColor Yellow
    Write-Host ""

    $oldPatterns = @(
        "C:/meowping-rts",
        "C:\meowping-rts",
        "C:\\meowping-rts"
    )

    $pythonFiles = Get-ChildItem -Path "C:\Ziggie" -Filter "*.py" -Recurse -ErrorAction SilentlyContinue
    $envFiles = Get-ChildItem -Path "C:\Ziggie" -Filter ".env*" -Recurse -ErrorAction SilentlyContinue
    $configFiles = Get-ChildItem -Path "C:\Ziggie" -Filter "*.config.*" -Recurse -ErrorAction SilentlyContinue

    $allFiles = @($pythonFiles) + @($envFiles) + @($configFiles) | Where-Object { $_ -ne $null }

    foreach ($file in $allFiles) {
        $script:filesChecked++

        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        if ($null -eq $content) { continue }

        foreach ($pattern in $oldPatterns) {
            if ($content -match [regex]::Escape($pattern)) {
                Write-Host "FOUND OLD PATH" -ForegroundColor Red
                Write-Host "  File: $($file.FullName)" -ForegroundColor Red
                Write-Host "  Pattern: $pattern" -ForegroundColor Red
                Write-Host ""

                if ($Detailed) {
                    $lines = $content -split "`n"
                    for ($i = 0; $i -lt $lines.Count; $i++) {
                        if ($lines[$i] -match [regex]::Escape($pattern)) {
                            Write-Host "    Line $($i+1): $($lines[$i].Substring(0, [Math]::Min(70, $lines[$i].Length)))" -ForegroundColor Yellow
                        }
                    }
                    Write-Host ""
                }

                $script:issuesFound++
            }
        }
    }

    if ($script:issuesFound -eq 0) {
        Write-Host "✓ No old paths found!" -ForegroundColor Green
    } else {
        Write-Host "⚠ Found $($script:issuesFound) files with old paths" -ForegroundColor Red
    }
    Write-Host ""
}

# ============================================
# FUNCTION: Verify directories exist
# ============================================
function Verify-Directories {
    Write-Host "Verifying critical directories exist..." -ForegroundColor Yellow
    Write-Host ""

    $directories = @(
        "C:\Ziggie",
        "C:\Ziggie\ai-agents",
        "C:\Ziggie\ai-agents\knowledge-base",
        "C:\Ziggie\ai-agents\L1-agents",
        "C:\Ziggie\control-center",
        "C:\Ziggie\control-center\backend",
        "C:\Ziggie\control-center\frontend",
        "C:\Ziggie\control-center\backend\api",
        "C:\Ziggie\control-center\backend\services",
        "C:\Ziggie\data",
        "C:\Ziggie\data\logs",
        "C:\ComfyUI"
    )

    foreach ($dir in $directories) {
        $script:directoriesChecked++

        if (Test-Path $dir) {
            Write-Host "✓ $dir" -ForegroundColor Green
        } else {
            Write-Host "✗ MISSING: $dir" -ForegroundColor Red
            $script:issuesFound++
        }
    }
    Write-Host ""
}

# ============================================
# FUNCTION: Verify key files exist
# ============================================
function Verify-Files {
    Write-Host "Verifying key configuration files exist..." -ForegroundColor Yellow
    Write-Host ""

    $files = @(
        "C:\Ziggie\control-center\backend\config.py",
        "C:\Ziggie\control-center\backend\main.py",
        "C:\Ziggie\control-center\backend\requirements.txt",
        "C:\Ziggie\control-center\frontend\package.json",
        "C:\Ziggie\control-center\frontend\vite.config.ts",
        "C:\Ziggie\ai-agents\knowledge-base\.env",
        "C:\Ziggie\ai-agents\knowledge-base\manage.py",
        "C:\Ziggie\ai-agents\01_ART_DIRECTOR_AGENT.md",
        "C:\Ziggie\README.md"
    )

    foreach ($file in $files) {
        if (Test-Path $file) {
            Write-Host "✓ $file" -ForegroundColor Green
        } else {
            Write-Host "✗ MISSING: $file" -ForegroundColor Yellow
            $script:issuesFound++
        }
    }
    Write-Host ""
}

# ============================================
# FUNCTION: Check configuration content
# ============================================
function Verify-ConfigContent {
    Write-Host "Verifying configuration file contents..." -ForegroundColor Yellow
    Write-Host ""

    # Check config.py
    if (Test-Path "C:\Ziggie\control-center\backend\config.py") {
        $configContent = Get-Content "C:\Ziggie\control-center\backend\config.py" -Raw

        if ($configContent -match 'C:\Ziggie|C:/Ziggie') {
            Write-Host "✓ config.py contains correct path references" -ForegroundColor Green
        } else {
            Write-Host "✗ config.py missing C:\Ziggie references" -ForegroundColor Red
            $script:issuesFound++
        }
    }

    # Check .env file
    if (Test-Path "C:\Ziggie\ai-agents\knowledge-base\.env") {
        $envContent = Get-Content "C:\Ziggie\ai-agents\knowledge-base\.env" -Raw

        if ($envContent -match 'C:\\Ziggie|C:/Ziggie') {
            Write-Host "✓ .env contains correct path references" -ForegroundColor Green
        } else {
            Write-Host "✗ .env missing C:\Ziggie references" -ForegroundColor Yellow
        }
    }

    Write-Host ""
}

# ============================================
# FUNCTION: Test Python imports
# ============================================
function Test-PythonImports {
    Write-Host "Testing Python configuration imports..." -ForegroundColor Yellow
    Write-Host ""

    try {
        $output = & python -c "import sys; sys.path.insert(0, 'C:\Ziggie\control-center\backend'); from config import Config; print('OK')" 2>&1

        if ($output -eq "OK") {
            Write-Host "✓ Backend config.py imports successfully" -ForegroundColor Green
        } else {
            Write-Host "⚠ Config import issue: $output" -ForegroundColor Yellow
            $script:issuesFound++
        }
    } catch {
        Write-Host "⚠ Could not test Python imports (Python may not be in PATH)" -ForegroundColor Yellow
    }

    Write-Host ""
}

# ============================================
# FUNCTION: Generate report
# ============================================
function Generate-Report {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "Verification Summary" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""

    Write-Host "Directories checked: $($script:directoriesChecked)" -ForegroundColor White
    Write-Host "Files checked: $($script:filesChecked)" -ForegroundColor White
    Write-Host "Issues found: $($script:issuesFound)" -ForegroundColor $(if ($script:issuesFound -eq 0) { "Green" } else { "Red" })
    Write-Host ""

    if ($script:issuesFound -eq 0) {
        Write-Host "✓ All paths verified successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "You can now safely start the services:" -ForegroundColor Green
        Write-Host "  .\start_backend.bat     # Backend" -ForegroundColor Green
        Write-Host "  .\start_frontend.bat    # Frontend" -ForegroundColor Green
        Write-Host "  .\kb_status.bat         # Knowledge Base" -ForegroundColor Green
    } else {
        Write-Host "⚠ Issues found - review above for details" -ForegroundColor Red
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Yellow
        Write-Host "  1. Review errors above" -ForegroundColor Yellow
        Write-Host "  2. Check CONFIGURATION_UPDATES.md for guidance" -ForegroundColor Yellow
        Write-Host "  3. Run migration scripts if paths weren't updated" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
}

# ============================================
# MAIN EXECUTION
# ============================================

Verify-Directories
Verify-Files
Check-OldPaths
Verify-ConfigContent

if (-not (Test-Path "C:\Ziggie\control-center\backend\config.py")) {
    Write-Host "(Skipping Python test - config.py not found)" -ForegroundColor Gray
} else {
    Test-PythonImports
}

Generate-Report
