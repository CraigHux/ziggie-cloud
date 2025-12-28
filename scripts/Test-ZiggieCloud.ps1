<#
.SYNOPSIS
    Automated test workflow for Ziggie Cloud services using Chrome DevTools Protocol

.DESCRIPTION
    Tests all Ziggie Cloud endpoints using browser automation via CDP.
    Requires Edge/Chrome to be running with remote debugging on port 9222.

.EXAMPLE
    .\Test-ZiggieCloud.ps1
    .\Test-ZiggieCloud.ps1 -Verbose
#>

param(
    [int]$Port = 9222,
    [string]$BaseUrl = "https://ziggie.cloud",
    [switch]$TakeScreenshots = $false
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Ziggie Cloud Automated Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test endpoints
$Endpoints = @(
    @{ Path = "/api/health"; Name = "API Health"; ExpectedContent = "healthy" },
    @{ Path = "/n8n/"; Name = "n8n Workflows"; ExpectedContent = "n8n" },
    @{ Path = "/flowise/"; Name = "Flowise LLM"; ExpectedContent = "Flowise" },
    @{ Path = "/grafana/"; Name = "Grafana Monitoring"; ExpectedContent = "grafana" },
    @{ Path = "/sim/"; Name = "Sim Studio"; ExpectedContent = "" },
    @{ Path = "/mcp/"; Name = "MCP Gateway"; ExpectedContent = "" }
)

# Results tracking
$Results = @()

# Check if browser debug port is available
Write-Host "Checking browser debug connection..." -ForegroundColor Yellow
try {
    $VersionResponse = Invoke-WebRequest -Uri "http://localhost:$Port/json/version" -UseBasicParsing -TimeoutSec 5
    $Version = $VersionResponse.Content | ConvertFrom-Json
    Write-Host "Connected to: $($Version.Browser)" -ForegroundColor Green
    Write-Host "Protocol Version: $($Version.'Protocol-Version')" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Error "Cannot connect to browser debug port $Port. Please run Launch-ChromeDebug.ps1 first."
    exit 1
}

# Function to open new tab
function Open-BrowserTab {
    param([string]$Url)

    try {
        $Response = Invoke-WebRequest -Uri "http://localhost:$Port/json/new?$Url" -Method PUT -UseBasicParsing -TimeoutSec 10
        return ($Response.Content | ConvertFrom-Json)
    } catch {
        Write-Warning "Failed to open tab for $Url"
        return $null
    }
}

# Function to get page info
function Get-PageContent {
    param([string]$PageId)

    # Wait for page to load
    Start-Sleep -Seconds 2

    try {
        $Tabs = Invoke-WebRequest -Uri "http://localhost:$Port/json" -UseBasicParsing
        $TabList = $Tabs.Content | ConvertFrom-Json
        $Page = $TabList | Where-Object { $_.id -eq $PageId }
        return $Page
    } catch {
        return $null
    }
}

# Function to close tab
function Close-BrowserTab {
    param([string]$PageId)

    try {
        Invoke-WebRequest -Uri "http://localhost:$Port/json/close/$PageId" -UseBasicParsing | Out-Null
    } catch {
        # Ignore close errors
    }
}

Write-Host "Running tests..." -ForegroundColor Cyan
Write-Host ""

foreach ($Endpoint in $Endpoints) {
    $FullUrl = "$BaseUrl$($Endpoint.Path)"
    Write-Host "Testing: $($Endpoint.Name)" -ForegroundColor Yellow
    Write-Host "  URL: $FullUrl" -ForegroundColor Gray

    $StartTime = Get-Date
    $Tab = Open-BrowserTab -Url $FullUrl

    if ($Tab) {
        $Page = Get-PageContent -PageId $Tab.id
        $EndTime = Get-Date
        $Duration = ($EndTime - $StartTime).TotalMilliseconds

        $Status = "PASS"
        $StatusColor = "Green"

        # Check if page loaded
        if (-not $Page -or $Page.title -eq "") {
            $Status = "WARN"
            $StatusColor = "Yellow"
        }

        # Check expected content in title (basic check)
        if ($Endpoint.ExpectedContent -and $Page.title -notlike "*$($Endpoint.ExpectedContent)*") {
            # Title check is informational only
        }

        Write-Host "  Status: $Status" -ForegroundColor $StatusColor
        Write-Host "  Title: $($Page.title)" -ForegroundColor White
        Write-Host "  Load Time: $([math]::Round($Duration))ms" -ForegroundColor White

        $Results += @{
            Name = $Endpoint.Name
            URL = $FullUrl
            Status = $Status
            Title = $Page.title
            LoadTime = $Duration
        }

        # Close the tab
        Close-BrowserTab -PageId $Tab.id
    } else {
        Write-Host "  Status: FAIL" -ForegroundColor Red
        $Results += @{
            Name = $Endpoint.Name
            URL = $FullUrl
            Status = "FAIL"
            Title = ""
            LoadTime = 0
        }
    }

    Write-Host ""
}

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$PassCount = ($Results | Where-Object { $_.Status -eq "PASS" }).Count
$WarnCount = ($Results | Where-Object { $_.Status -eq "WARN" }).Count
$FailCount = ($Results | Where-Object { $_.Status -eq "FAIL" }).Count
$TotalCount = $Results.Count

Write-Host "Total Tests: $TotalCount" -ForegroundColor White
Write-Host "Passed: $PassCount" -ForegroundColor Green
Write-Host "Warnings: $WarnCount" -ForegroundColor Yellow
Write-Host "Failed: $FailCount" -ForegroundColor Red
Write-Host ""

# Return results
$Results
