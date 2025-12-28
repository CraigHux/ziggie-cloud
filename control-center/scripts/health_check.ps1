###############################################################################
# Ziggie Control Center - Health Check Script (PowerShell)
# Purpose: Comprehensive health monitoring for the Control Center
# Version: 1.0
# Author: Monitoring Specialist (L3.MONITORING.SETUP)
# Date: 2025-11-10
#
# Usage: .\health_check.ps1
# Exit Codes:
#   0 = All checks passed, system is healthy
#   1 = One or more checks failed, issues detected
#
# Description:
# This PowerShell script performs comprehensive health checks on the Ziggie
# Control Center, including backend service connectivity, configuration
# validation, system stats verification, and frontend environment checks.
#
# Note: On Windows, this is the recommended version. For Linux/Mac, use health_check.sh
###############################################################################

param(
    [string]$BackendUrl = "http://127.0.0.1:54112",
    [string]$BackendHost = "127.0.0.1",
    [int]$BackendPort = 54112,
    [string]$FrontendEnvPath = "C:\Ziggie\control-center\frontend\.env",
    [string]$BackendEnvPath = "C:\Ziggie\control-center\backend\.env",
    [string]$ComfyuiDir = "C:\ComfyUI",
    [string]$AiAgentsDir = "C:\Ziggie\ai-agents",
    [string]$MeowpingDir = "C:\Ziggie",
    [int]$CurlTimeout = 5,
    [int]$MaxResponseTimeMs = 5000
)

# Initialize counters
$script:PassedChecks = 0
$script:WarningChecks = 0
$script:FailedChecks = 0
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

###############################################################################
# Helper Functions
###############################################################################

# Print colored status message
function Print-Status {
    param(
        [Parameter(Mandatory=$true)]
        [ValidateSet("PASS", "FAIL", "WARN", "INFO")]
        [string]$Status,

        [Parameter(Mandatory=$true)]
        [string]$Message
    )

    switch ($Status) {
        "PASS" {
            Write-Host "✓ PASS: $Message" -ForegroundColor Green
            $script:PassedChecks++
        }
        "FAIL" {
            Write-Host "✗ FAIL: $Message" -ForegroundColor Red
            $script:FailedChecks++
        }
        "WARN" {
            Write-Host "⚠ WARN: $Message" -ForegroundColor Yellow
            $script:WarningChecks++
        }
        "INFO" {
            Write-Host "→ INFO: $Message" -ForegroundColor Cyan
        }
    }
}

# Print section header
function Print-Section {
    param([string]$Title)

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "$Title" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

# Print final summary
function Print-Summary {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "HEALTH CHECK SUMMARY" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Timestamp: $timestamp"
    Write-Host "Passed: $script:PassedChecks" -ForegroundColor Green
    Write-Host "Warnings: $script:WarningChecks" -ForegroundColor Yellow
    Write-Host "Failed: $script:FailedChecks" -ForegroundColor Red
    Write-Host ""
}

###############################################################################
# Check Functions
###############################################################################

# Check 1: Backend Service Health Endpoint
function Test-BackendHealth {
    Print-Section "BACKEND HEALTH CHECK"

    Write-Host "Testing: GET $BackendUrl/api/health"

    try {
        $response = Invoke-WebRequest -Uri "$BackendUrl/api/health" `
            -Method GET `
            -TimeoutSec $CurlTimeout `
            -ErrorAction Stop

        if ($response.StatusCode -eq 200) {
            Print-Status "PASS" "Backend healthy (HTTP $($response.StatusCode))"
            return $true
        } else {
            Print-Status "FAIL" "Backend unhealthy (HTTP $($response.StatusCode))"
            return $false
        }
    } catch {
        Print-Status "FAIL" "Backend not responding: $($_.Exception.Message)"
        return $false
    }
}

# Check 2: Backend Service Port Listening
function Test-BackendPort {
    Print-Section "BACKEND PORT LISTENING CHECK"

    Write-Host "Testing: Is port $BackendPort listening on $BackendHost?"

    try {
        $netstat = netstat -ano
        $portFound = $netstat | Select-String -Pattern ":$BackendPort\s+"

        if ($portFound) {
            Print-Status "PASS" "Backend port $BackendPort is listening"
            return $true
        } else {
            Print-Status "FAIL" "Backend port $BackendPort is not listening"
            return $false
        }
    } catch {
        Print-Status "WARN" "Could not verify port status: $($_.Exception.Message)"
        return $true
    }
}

# Check 3: System Stats Endpoint - Real Data Validation
function Test-SystemStats {
    Print-Section "SYSTEM STATS VALIDATION"

    Write-Host "Testing: GET $BackendUrl/api/system/stats"

    try {
        $response = Invoke-WebRequest -Uri "$BackendUrl/api/system/stats" `
            -Method GET `
            -TimeoutSec $CurlTimeout `
            -ErrorAction Stop

        $stats = $response.Content | ConvertFrom-Json

        # Check if we have CPU data
        if ($null -eq $stats.cpu -or $null -eq $stats.cpu.usage_percent) {
            Print-Status "FAIL" "System stats endpoint not returning valid data"
            return $false
        }

        $cpuUsage = $stats.cpu.usage_percent

        # Validate that we're getting real data (not all zeros)
        if ($cpuUsage -eq 0.0 -or $null -eq $cpuUsage) {
            Print-Status "FAIL" "System stats returning mock data (CPU: $cpuUsage%) - backend may need restart"
            return $false
        } elseif ($cpuUsage -match '^[0-9]+\.?[0-9]*$' -and $cpuUsage -ge 0 -and $cpuUsage -le 100) {
            Print-Status "PASS" "System stats returning real data (CPU: $cpuUsage%)"
            return $true
        } else {
            Print-Status "WARN" "System stats CPU value may be invalid (CPU: $cpuUsage%)"
            return $true
        }
    } catch {
        Print-Status "FAIL" "Cannot retrieve system stats: $($_.Exception.Message)"
        return $false
    }
}

# Check 4: Backend Configuration File
function Test-BackendConfig {
    Print-Section "BACKEND CONFIGURATION CHECK"

    Write-Host "Checking: $BackendEnvPath"

    if (-not (Test-Path $BackendEnvPath)) {
        Print-Status "FAIL" "Backend .env configuration file missing"
        return $false
    }

    Print-Status "PASS" "Backend .env configuration file exists"

    $envContent = Get-Content $BackendEnvPath -Raw

    # Check for required variables
    if ($envContent -match "PORT=54112") {
        Print-Status "PASS" "Backend PORT configured correctly (54112)"
    } else {
        Print-Status "WARN" "Backend PORT not set to 54112"
    }

    if ($envContent -match "HOST=127\.0\.0\.1") {
        Print-Status "PASS" "Backend HOST configured correctly (127.0.0.1)"
    } else {
        Print-Status "WARN" "Backend HOST not set to 127.0.0.1"
    }

    return $true
}

# Check 5: Frontend Configuration File
function Test-FrontendConfig {
    Print-Section "FRONTEND CONFIGURATION CHECK"

    Write-Host "Checking: $FrontendEnvPath"

    if (-not (Test-Path $FrontendEnvPath)) {
        Print-Status "FAIL" "Frontend .env configuration file missing"
        return $false
    }

    Print-Status "PASS" "Frontend .env configuration file exists"

    $envContent = Get-Content $FrontendEnvPath -Raw

    # Check VITE_API_URL
    if ($envContent -match "VITE_API_URL=http://127\.0\.0\.1:54112/api") {
        Print-Status "PASS" "VITE_API_URL configured correctly"
    } else {
        $apiUrl = ($envContent | Select-String -Pattern "VITE_API_URL.*").Line
        if ($apiUrl) {
            Print-Status "FAIL" "VITE_API_URL mismatch - Expected: http://127.0.0.1:54112/api, Found: $apiUrl"
        } else {
            Print-Status "FAIL" "VITE_API_URL not found in configuration"
        }
        return $false
    }

    # Check VITE_WS_URL
    if ($envContent -match "VITE_WS_URL=ws://127\.0\.0\.1:54112/api/system/ws") {
        Print-Status "PASS" "VITE_WS_URL configured correctly"
    } else {
        $wsUrl = ($envContent | Select-String -Pattern "VITE_WS_URL.*").Line
        if ($wsUrl) {
            Print-Status "WARN" "VITE_WS_URL mismatch - Expected: ws://127.0.0.1:54112/api/system/ws, Found: $wsUrl"
        } else {
            Print-Status "WARN" "VITE_WS_URL not found in configuration"
        }
    }

    return $true
}

# Check 6: Critical Paths Existence
function Test-CriticalPaths {
    Print-Section "CRITICAL PATHS VALIDATION"

    # Check ComfyUI directory
    if (Test-Path $ComfyuiDir -PathType Container) {
        Print-Status "PASS" "ComfyUI directory exists: $ComfyuiDir"
    } else {
        Print-Status "WARN" "ComfyUI directory not found: $ComfyuiDir"
    }

    # Check AI Agents directory
    if (Test-Path $AiAgentsDir -PathType Container) {
        Print-Status "PASS" "AI Agents directory exists: $AiAgentsDir"
    } else {
        Print-Status "WARN" "AI Agents directory not found: $AiAgentsDir"
    }

    # Check Ziggie root directory
    if (Test-Path $MeowpingDir -PathType Container) {
        Print-Status "PASS" "Ziggie root directory exists: $MeowpingDir"
        return $true
    } else {
        Print-Status "FAIL" "Ziggie root directory not found: $MeowpingDir"
        return $false
    }
}

# Check 7: Database/Backend Data Connection
function Test-DatabaseConnectivity {
    Print-Section "DATABASE CONNECTIVITY CHECK"

    Write-Host "Testing: Backend database connectivity via stats endpoint"

    try {
        $response = Invoke-WebRequest -Uri "$BackendUrl/api/system/stats" `
            -Method GET `
            -TimeoutSec $CurlTimeout `
            -ErrorAction Stop

        $stats = $response.Content | ConvertFrom-Json

        # If we can get stats, database is likely connected
        if ($null -ne $stats.memory) {
            Print-Status "PASS" "Database/Backend data connection working"
            return $true
        } else {
            Print-Status "WARN" "Cannot verify database connectivity"
            return $true
        }
    } catch {
        Print-Status "WARN" "Cannot verify database connectivity: $($_.Exception.Message)"
        return $true
    }
}

###############################################################################
# Main Execution
###############################################################################

# Print header
Write-Host ""
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║ Ziggie Control Center - Health Check   ║" -ForegroundColor Cyan
Write-Host "║ Started: $timestamp         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan

# Run all checks
Test-BackendHealth | Out-Null
Test-BackendPort | Out-Null
Test-SystemStats | Out-Null
Test-BackendConfig | Out-Null
Test-FrontendConfig | Out-Null
Test-CriticalPaths | Out-Null
Test-DatabaseConnectivity | Out-Null

# Print summary
Print-Summary

# Determine exit code and final status
if ($script:FailedChecks -eq 0) {
    Write-Host "Status: HEALTHY - System is operational" -ForegroundColor Green
    Write-Host "All critical checks passed. No immediate action required."
    exit 0
} else {
    Write-Host "Status: UNHEALTHY - Issues detected" -ForegroundColor Red
    Write-Host "$($script:FailedChecks) critical check(s) failed. Immediate investigation required."
    if ($script:WarningChecks -gt 0) {
        Write-Host "$($script:WarningChecks) warning(s) detected. Please review." -ForegroundColor Yellow
    }
    exit 1
}
