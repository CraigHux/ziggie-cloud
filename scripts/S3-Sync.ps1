# =============================================================================
# S3 Asset Sync Script for Ziggie (Windows PowerShell)
# =============================================================================
# Syncs game assets between local directories and S3 bucket
# Usage: .\S3-Sync.ps1 -Command upload -AssetType units
# =============================================================================

param(
    [Parameter(Position=0)]
    [ValidateSet('upload', 'download', 'sync', 'list', 'stats', 'help')]
    [string]$Command = 'help',

    [Parameter(Position=1)]
    [ValidateSet('units', 'buildings', 'terrain', 'effects', 'ui', 'audio', 'all')]
    [string]$AssetType = 'all'
)

# Configuration
$S3Bucket = if ($env:S3_BUCKET) { $env:S3_BUCKET } else { "ziggie-assets-prod" }
$AwsRegion = if ($env:AWS_REGION) { $env:AWS_REGION } else { "eu-north-1" }
$LocalAssetsDir = if ($env:LOCAL_ASSETS_DIR) { $env:LOCAL_ASSETS_DIR } else { ".\assets" }
$S3Prefix = if ($env:S3_PREFIX) { $env:S3_PREFIX } else { "game-assets" }
$AwsCli = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"

# Logging functions
function Write-Info { param([string]$Message) Write-Host "[INFO] $Message" -ForegroundColor Green }
function Write-Warn { param([string]$Message) Write-Host "[WARN] $Message" -ForegroundColor Yellow }
function Write-Err { param([string]$Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

# Check AWS CLI
function Test-AwsCli {
    if (-not (Test-Path $AwsCli)) {
        $AwsCli = "aws"
        if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
            Write-Err "AWS CLI is not installed. Please install it first."
            exit 1
        }
    }
    return $AwsCli
}

# Check AWS credentials
function Test-AwsCredentials {
    $cli = Test-AwsCli
    try {
        & $cli sts get-caller-identity --region $AwsRegion 2>&1 | Out-Null
        Write-Info "AWS credentials verified"
        return $true
    } catch {
        Write-Err "AWS credentials not configured. Run 'aws configure' first."
        exit 1
    }
}

# Upload assets to S3
function Invoke-Upload {
    param([string]$Type)

    $sourceDir = $LocalAssetsDir
    $s3Path = "s3://$S3Bucket/$S3Prefix"

    if ($Type -ne 'all') {
        $sourceDir = Join-Path $LocalAssetsDir $Type
        $s3Path = "s3://$S3Bucket/$S3Prefix/$Type"
    }

    if (-not (Test-Path $sourceDir)) {
        Write-Err "Source directory does not exist: $sourceDir"
        exit 1
    }

    Write-Info "Uploading assets from $sourceDir to $s3Path..."

    $cli = Test-AwsCli
    & $cli s3 sync $sourceDir $s3Path `
        --region $AwsRegion `
        --delete `
        --exclude "*.tmp" `
        --exclude "*.bak" `
        --exclude ".DS_Store" `
        --exclude "Thumbs.db"

    Write-Info "Upload complete!"
}

# Download assets from S3
function Invoke-Download {
    param([string]$Type)

    $destDir = $LocalAssetsDir
    $s3Path = "s3://$S3Bucket/$S3Prefix"

    if ($Type -ne 'all') {
        $destDir = Join-Path $LocalAssetsDir $Type
        $s3Path = "s3://$S3Bucket/$S3Prefix/$Type"
    }

    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }

    Write-Info "Downloading assets from $s3Path to $destDir..."

    $cli = Test-AwsCli
    & $cli s3 sync $s3Path $destDir `
        --region $AwsRegion `
        --exclude "*.tmp" `
        --exclude "*.bak"

    Write-Info "Download complete!"
}

# Bidirectional sync
function Invoke-Sync {
    param([string]$Type)

    Write-Info "Performing bidirectional sync for: $Type"
    Invoke-Download -Type $Type
    Invoke-Upload -Type $Type
    Write-Info "Sync complete!"
}

# List assets in S3
function Invoke-List {
    param([string]$Type)

    $s3Path = "s3://$S3Bucket/$S3Prefix"
    if ($Type -and $Type -ne 'all') {
        $s3Path = "$s3Path/$Type"
    }

    Write-Info "Listing assets in $s3Path..."

    $cli = Test-AwsCli
    & $cli s3 ls $s3Path --recursive --region $AwsRegion --human-readable --summarize
}

# Get bucket stats
function Get-BucketStats {
    Write-Info "Getting bucket statistics..."

    Write-Host ""
    Write-Host "=== S3 Bucket: $S3Bucket ===" -ForegroundColor Cyan
    Write-Host ""

    $cli = Test-AwsCli
    & $cli s3 ls "s3://$S3Bucket/$S3Prefix/" --recursive --region $AwsRegion --summarize | Select-Object -Last 2

    Write-Host ""
    Write-Host "=== Asset Types ===" -ForegroundColor Cyan

    $folders = @('units', 'buildings', 'terrain', 'effects', 'ui', 'audio')
    foreach ($folder in $folders) {
        $count = (& $cli s3 ls "s3://$S3Bucket/$S3Prefix/$folder/" --recursive --region $AwsRegion 2>$null | Measure-Object -Line).Lines
        Write-Host "  ${folder}: $count files"
    }
}

# Print usage
function Show-Help {
    Write-Host @"
S3 Asset Sync Script for Ziggie

Usage: .\S3-Sync.ps1 -Command <command> -AssetType <type>

Commands:
  upload    - Upload local assets to S3
  download  - Download assets from S3
  sync      - Bidirectional sync (local wins)
  list      - List assets in S3
  stats     - Show bucket statistics
  help      - Show this help

Asset types: units, buildings, terrain, effects, ui, audio, all (default)

Environment variables:
  S3_BUCKET        - S3 bucket name (default: ziggie-assets-prod)
  AWS_REGION       - AWS region (default: eu-north-1)
  LOCAL_ASSETS_DIR - Local assets directory (default: .\assets)

Examples:
  .\S3-Sync.ps1 -Command upload -AssetType units
  .\S3-Sync.ps1 -Command download -AssetType all
  .\S3-Sync.ps1 -Command sync
  .\S3-Sync.ps1 -Command list -AssetType buildings
"@
}

# Main
switch ($Command) {
    'upload' {
        Test-AwsCredentials
        Invoke-Upload -Type $AssetType
    }
    'download' {
        Test-AwsCredentials
        Invoke-Download -Type $AssetType
    }
    'sync' {
        Test-AwsCredentials
        Invoke-Sync -Type $AssetType
    }
    'list' {
        Test-AwsCredentials
        Invoke-List -Type $AssetType
    }
    'stats' {
        Test-AwsCredentials
        Get-BucketStats
    }
    'help' {
        Show-Help
    }
}
