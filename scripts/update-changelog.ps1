#Requires -Version 5.1
<#
.SYNOPSIS
    Updates the CHANGELOG.md file using git-cliff.

.DESCRIPTION
    This script generates or updates the CHANGELOG.md file based on git commit history
    using git-cliff with conventional commits format.

.PARAMETER Tag
    Optional version tag for the new release (e.g., "v1.0.0").
    If not provided, generates unreleased changelog.

.PARAMETER Unreleased
    Only include unreleased commits.

.PARAMETER Latest
    Only include the latest tag.

.PARAMETER Output
    Output file path. Defaults to CHANGELOG.md in the repository root.

.EXAMPLE
    .\update-changelog.ps1
    Generates full changelog with all versions.

.EXAMPLE
    .\update-changelog.ps1 -Tag "v1.0.0"
    Tags the current commits as v1.0.0 and generates changelog.

.EXAMPLE
    .\update-changelog.ps1 -Unreleased
    Shows only unreleased commits.

.NOTES
    Author: Ziggie DevOps Agent
    Requires: git-cliff (installed via winget)
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$Tag,

    [Parameter(Mandatory = $false)]
    [switch]$Unreleased,

    [Parameter(Mandatory = $false)]
    [switch]$Latest,

    [Parameter(Mandatory = $false)]
    [string]$Output = "CHANGELOG.md"
)

# Configuration
$ErrorActionPreference = "Stop"
$GIT_CLIFF_PATH = "C:\Users\minin\AppData\Local\Microsoft\WinGet\Packages\orhun.git-cliff_Microsoft.Winget.Source_8wekyb3d8bbwe\git-cliff-2.11.0\git-cliff.exe"

# Functions
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

function Test-GitCliffInstalled {
    if (-not (Test-Path $GIT_CLIFF_PATH)) {
        Write-Log "git-cliff not found at: $GIT_CLIFF_PATH" "ERROR"
        Write-Log "Please install git-cliff using: winget install git-cliff" "ERROR"
        exit 1
    }
    Write-Log "git-cliff found at: $GIT_CLIFF_PATH" "INFO"
}

function Test-GitRepository {
    $gitDir = Join-Path $PSScriptRoot "..\\.git"
    if (-not (Test-Path $gitDir)) {
        Write-Log "Not a git repository. Please run from a git-initialized directory." "ERROR"
        exit 1
    }
    Write-Log "Git repository confirmed" "INFO"
}

function Test-CliffConfig {
    $configPath = Join-Path $PSScriptRoot "..\\cliff.toml"
    if (-not (Test-Path $configPath)) {
        Write-Log "cliff.toml not found. Please create configuration first." "WARN"
        return $false
    }
    Write-Log "cliff.toml configuration found" "INFO"
    return $true
}

function Get-CommitCount {
    $count = git rev-list --count HEAD 2>$null
    if ($LASTEXITCODE -ne 0) {
        return 0
    }
    return [int]$count
}

function Update-Changelog {
    param(
        [string]$OutputPath,
        [string]$Tag,
        [bool]$UnreleasedOnly,
        [bool]$LatestOnly
    )

    $repoRoot = Split-Path -Parent $PSScriptRoot
    $outputFile = Join-Path $repoRoot $OutputPath

    Write-Log "Generating changelog..." "INFO"

    # Build command arguments
    $args = @()

    if ($UnreleasedOnly) {
        $args += "--unreleased"
    }

    if ($LatestOnly) {
        $args += "--latest"
    }

    if ($Tag) {
        $args += "--tag"
        $args += $Tag
    }

    $args += "--output"
    $args += $outputFile

    # Change to repo root and run git-cliff
    Push-Location $repoRoot
    try {
        Write-Log "Running: git-cliff $($args -join ' ')" "INFO"
        & $GIT_CLIFF_PATH @args

        if ($LASTEXITCODE -eq 0) {
            Write-Log "Changelog generated successfully: $outputFile" "SUCCESS"

            # Show preview
            if (Test-Path $outputFile) {
                Write-Host "`n--- CHANGELOG PREVIEW (first 30 lines) ---" -ForegroundColor Cyan
                Get-Content $outputFile -TotalCount 30
                Write-Host "--- END PREVIEW ---`n" -ForegroundColor Cyan
            }
        } else {
            Write-Log "git-cliff exited with code: $LASTEXITCODE" "WARN"
        }
    }
    finally {
        Pop-Location
    }

    return $outputFile
}

# Main execution
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "   Ziggie Changelog Generator        " -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Pre-flight checks
Test-GitCliffInstalled
Test-GitRepository
$hasConfig = Test-CliffConfig

$commitCount = Get-CommitCount
Write-Log "Repository has $commitCount commit(s)" "INFO"

if ($commitCount -eq 0) {
    Write-Log "No commits found. Please make at least one commit first." "WARN"
    exit 0
}

# Generate changelog
$result = Update-Changelog -OutputPath $Output -Tag $Tag -UnreleasedOnly $Unreleased.IsPresent -LatestOnly $Latest.IsPresent

Write-Host ""
Write-Log "Changelog update complete!" "SUCCESS"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review the changelog: Get-Content $result" -ForegroundColor White
Write-Host "  2. Stage for commit: git add $Output" -ForegroundColor White
Write-Host "  3. Commit changes: git commit -m 'docs: update changelog'" -ForegroundColor White
Write-Host ""
