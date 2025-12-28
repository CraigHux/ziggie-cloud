<#
.SYNOPSIS
    Launches Google Chrome with remote debugging enabled for MCP integration

.DESCRIPTION
    Launches Chrome with the DevTools Protocol available over HTTP.
    Uses a custom user data directory for security (Chrome 136+).
    Designed for use with Chrome DevTools MCP server.

.PARAMETER Port
    The port for remote debugging (default: 9222)

.PARAMETER DataDir
    Custom user data directory (default: .cache\chrome-devtools-mcp)

.PARAMETER Headless
    Launch Chrome in headless mode

.EXAMPLE
    .\Launch-ChromeDebug.ps1
    .\Launch-ChromeDebug.ps1 -Port 9223 -Headless
#>

param(
    [int]$Port = 9222,
    [string]$DataDir = "$env:USERPROFILE\.cache\chrome-devtools-mcp\chrome-profile-stable",
    [switch]$Headless = $false,
    [switch]$Force = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Chrome DevTools Debug Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if port is already in use
$ExistingConnection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
if ($ExistingConnection -and -not $Force) {
    Write-Host "Port $Port is already in use!" -ForegroundColor Yellow
    Write-Host "Use -Force to kill existing process, or use a different port." -ForegroundColor Yellow

    $response = Read-Host "Kill existing process? (y/N)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Stop-Process -Id $ExistingConnection.OwningProcess -Force
        Write-Host "Killed process $($ExistingConnection.OwningProcess)" -ForegroundColor Green
        Start-Sleep -Seconds 2
    } else {
        exit 1
    }
}

# Create debug profile directory
if (-not (Test-Path $DataDir)) {
    New-Item -ItemType Directory -Path $DataDir -Force | Out-Null
    Write-Host "Created debug profile: $DataDir" -ForegroundColor Green
}

# Find Chrome or Edge executable (Chrome DevTools MCP works with any Chromium browser)
$ChromePaths = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
)

$ChromePath = $null
foreach ($path in $ChromePaths) {
    if (Test-Path $path) {
        $ChromePath = $path
        break
    }
}

if (-not $ChromePath) {
    Write-Error "Chrome/Edge not found. Please verify installation path."
    Write-Host "Searched locations:"
    $ChromePaths | ForEach-Object { Write-Host "  - $_" }
    exit 1
}

Write-Host "Found Chromium browser: $ChromePath" -ForegroundColor Green

# Build Chrome arguments
$ChromeArgs = @(
    "--remote-debugging-port=$Port",
    "--user-data-dir=`"$DataDir`"",
    "--no-first-run",
    "--disable-extensions",
    "--disable-default-apps",
    "--disable-background-networking",
    "--disable-sync",
    "--disable-translate",
    "--metrics-recording-only",
    "--safebrowsing-disable-auto-update"
)

if ($Headless) {
    $ChromeArgs += "--headless=new"
    Write-Host "Mode: Headless" -ForegroundColor Yellow
} else {
    Write-Host "Mode: Visible" -ForegroundColor Yellow
}

# Launch Chrome
Write-Host ""
Write-Host "Launching Chrome with remote debugging..." -ForegroundColor Cyan
Write-Host "Port: $Port" -ForegroundColor White
Write-Host "Profile: $DataDir" -ForegroundColor White
Write-Host ""

Start-Process -FilePath $ChromePath -ArgumentList $ChromeArgs

# Wait for Chrome to start
Write-Host "Waiting for Chrome to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Verify connection
try {
    $response = Invoke-WebRequest -Uri "http://localhost:$Port/json/version" -UseBasicParsing -TimeoutSec 5
    $version = $response.Content | ConvertFrom-Json

    Write-Host ""
    Write-Host "SUCCESS! Chrome is running with remote debugging" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Browser: $($version.Browser)" -ForegroundColor White
    Write-Host "Protocol: $($version.'Protocol-Version')" -ForegroundColor White
    Write-Host ""
    Write-Host "Access Points:" -ForegroundColor Cyan
    Write-Host "  JSON API:     http://localhost:$Port/json" -ForegroundColor White
    Write-Host "  Protocol:     http://localhost:$Port/json/protocol" -ForegroundColor White
    Write-Host "  Version:      http://localhost:$Port/json/version" -ForegroundColor White
    Write-Host ""
    Write-Host "MCP Server can now connect to Chrome!" -ForegroundColor Green

} catch {
    Write-Host ""
    Write-Host "WARNING: Could not verify Chrome connection" -ForegroundColor Yellow
    Write-Host "Chrome may still be starting. Try accessing:" -ForegroundColor Yellow
    Write-Host "  http://localhost:$Port/json" -ForegroundColor White
    Write-Host ""
    Write-Host "If connection fails, check:" -ForegroundColor Yellow
    Write-Host "  1. Chrome is running (check Task Manager)" -ForegroundColor White
    Write-Host "  2. Port $Port is not blocked by firewall" -ForegroundColor White
    Write-Host "  3. No other Chrome instance is running" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
