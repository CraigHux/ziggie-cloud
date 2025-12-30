# =============================================================================
# ZIGGIE ASSET PIPELINE - Local to VPS Sync Script
# =============================================================================
# Syncs pipeline scripts and configurations from local Windows machine to VPS
#
# Prerequisites:
#   - SSH key configured for root@VPS (no password)
#   - VPS has /opt/ziggie directory structure created
#   - OpenSSH client installed (Windows 10+)
#
# Usage:
#   .\sync-to-vps.ps1                    # Sync all files
#   .\sync-to-vps.ps1 -Scripts           # Sync scripts only
#   .\sync-to-vps.ps1 -Workflows         # Sync n8n workflows only
#   .\sync-to-vps.ps1 -DryRun            # Show what would be synced
#   .\sync-to-vps.ps1 -RestartServices   # Restart VPS services after sync
# =============================================================================

param(
    [switch]$Scripts,
    [switch]$Workflows,
    [switch]$Configs,
    [switch]$DryRun,
    [switch]$RestartServices,
    [switch]$Verbose,
    [string]$VpsHost = "82.25.112.73",
    [string]$VpsUser = "root"
)

# Configuration
$LocalBase = "C:\Ziggie"
$VpsBase = "/opt/ziggie"

# Colors
$Green = "`e[32m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Blue = "`e[34m"
$Reset = "`e[0m"

# File mappings: local -> VPS
$ScriptFiles = @(
    @{Local = "scripts\automated_pipeline.py"; Remote = "scripts/automated_pipeline.py"},
    @{Local = "scripts\discord_bot.py"; Remote = "scripts/discord_bot.py"},
    @{Local = "scripts\pipeline_notifications.py"; Remote = "scripts/pipeline_notifications.py"},
    @{Local = "scripts\blender_8dir_render.py"; Remote = "scripts/blender_8dir_render.py"},
    @{Local = "scripts\blender_thumbnail.py"; Remote = "scripts/blender_thumbnail.py"},
    @{Local = "scripts\health_check.py"; Remote = "scripts/health_check.py"}
)

$WorkflowFiles = @(
    @{Local = "n8n-workflows\asset-pipeline-24-7.json"; Remote = "n8n-workflows/asset-pipeline-24-7.json"}
)

$ConfigFiles = @(
    @{Local = "hostinger-vps\scripts\deploy-asset-pipeline.sh"; Remote = "deploy/deploy-asset-pipeline.sh"}
)

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host "$Blue=============================================$Reset"
    Write-Host "$Blue  $Text$Reset"
    Write-Host "$Blue=============================================$Reset"
    Write-Host ""
}

function Write-Status {
    param(
        [string]$Status,
        [string]$Message
    )

    switch ($Status) {
        "OK"      { Write-Host "${Green}[OK]${Reset} $Message" }
        "SKIP"    { Write-Host "${Yellow}[SKIP]${Reset} $Message" }
        "ERROR"   { Write-Host "${Red}[ERROR]${Reset} $Message" }
        "INFO"    { Write-Host "${Blue}[INFO]${Reset} $Message" }
        "DRY"     { Write-Host "${Yellow}[DRY RUN]${Reset} Would sync: $Message" }
    }
}

function Test-SshConnection {
    Write-Status "INFO" "Testing SSH connection to ${VpsUser}@${VpsHost}..."

    try {
        $result = ssh -o ConnectTimeout=5 -o BatchMode=yes "${VpsUser}@${VpsHost}" "echo connected" 2>&1
        if ($result -eq "connected") {
            Write-Status "OK" "SSH connection successful"
            return $true
        }
    }
    catch {
        Write-Status "ERROR" "SSH connection failed: $_"
    }

    Write-Status "ERROR" "Cannot connect to VPS. Check SSH key configuration."
    Write-Host ""
    Write-Host "To set up SSH key authentication:"
    Write-Host "  1. Generate key: ssh-keygen -t ed25519"
    Write-Host "  2. Copy to VPS: ssh-copy-id ${VpsUser}@${VpsHost}"
    Write-Host ""
    return $false
}

function Sync-File {
    param(
        [string]$LocalPath,
        [string]$RemotePath
    )

    $FullLocalPath = Join-Path $LocalBase $LocalPath
    $FullRemotePath = "${VpsBase}/${RemotePath}"

    # Check if local file exists
    if (-not (Test-Path $FullLocalPath)) {
        Write-Status "SKIP" "$LocalPath (file not found locally)"
        return $false
    }

    if ($DryRun) {
        Write-Status "DRY" "$LocalPath -> $FullRemotePath"
        return $true
    }

    # Create remote directory if needed
    $RemoteDir = Split-Path $FullRemotePath -Parent
    ssh "${VpsUser}@${VpsHost}" "mkdir -p $RemoteDir" 2>&1 | Out-Null

    # Copy file
    try {
        $scpResult = scp "$FullLocalPath" "${VpsUser}@${VpsHost}:${FullRemotePath}" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Status "OK" "$LocalPath -> $FullRemotePath"
            return $true
        }
        else {
            Write-Status "ERROR" "Failed to sync $LocalPath : $scpResult"
            return $false
        }
    }
    catch {
        Write-Status "ERROR" "Exception syncing $LocalPath : $_"
        return $false
    }
}

function Sync-Category {
    param(
        [string]$Name,
        [array]$Files
    )

    Write-Host ""
    Write-Host "${Yellow}Syncing $Name...$Reset"

    $Success = 0
    $Failed = 0

    foreach ($file in $Files) {
        if (Sync-File -LocalPath $file.Local -RemotePath $file.Remote) {
            $Success++
        }
        else {
            $Failed++
        }
    }

    Write-Host "  $Success synced, $Failed skipped/failed"
    return @{Success = $Success; Failed = $Failed}
}

function Restart-VpsServices {
    Write-Host ""
    Write-Host "${Yellow}Restarting VPS services...$Reset"

    if ($DryRun) {
        Write-Status "DRY" "Would restart ziggie-discord-bot service"
        return
    }

    # Restart Discord bot
    Write-Status "INFO" "Restarting Discord bot service..."
    $result = ssh "${VpsUser}@${VpsHost}" "systemctl restart ziggie-discord-bot 2>&1 && systemctl is-active ziggie-discord-bot"

    if ($result -eq "active") {
        Write-Status "OK" "Discord bot service restarted and active"
    }
    else {
        Write-Status "ERROR" "Discord bot service restart failed: $result"
    }
}

function Show-VpsStatus {
    Write-Host ""
    Write-Host "${Yellow}VPS Service Status...$Reset"

    # Check services
    $services = @("ziggie-discord-bot", "docker")

    foreach ($service in $services) {
        $status = ssh "${VpsUser}@${VpsHost}" "systemctl is-active $service 2>/dev/null || echo 'not-found'"
        switch ($status) {
            "active"    { Write-Status "OK" "$service is running" }
            "inactive"  { Write-Status "ERROR" "$service is stopped" }
            "not-found" { Write-Status "SKIP" "$service not installed" }
            default     { Write-Status "INFO" "$service status: $status" }
        }
    }

    # Check n8n
    $n8nStatus = ssh "${VpsUser}@${VpsHost}" "curl -s -o /dev/null -w '%{http_code}' http://localhost:5678/healthz 2>/dev/null || echo 'failed'"
    if ($n8nStatus -eq "200") {
        Write-Status "OK" "n8n is responding"
    }
    else {
        Write-Status "ERROR" "n8n not responding (status: $n8nStatus)"
    }
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

Write-Header "ZIGGIE PIPELINE - VPS SYNC"

Write-Host "Configuration:"
Write-Host "  VPS Host:    ${VpsUser}@${VpsHost}"
Write-Host "  Local Base:  $LocalBase"
Write-Host "  VPS Base:    $VpsBase"

if ($DryRun) {
    Write-Host ""
    Write-Host "${Yellow}*** DRY RUN MODE - No changes will be made ***$Reset"
}

# Test connection first
if (-not (Test-SshConnection)) {
    exit 1
}

# Determine what to sync
$SyncAll = -not ($Scripts -or $Workflows -or $Configs)

$TotalSuccess = 0
$TotalFailed = 0

# Sync scripts
if ($SyncAll -or $Scripts) {
    $result = Sync-Category -Name "Pipeline Scripts" -Files $ScriptFiles
    $TotalSuccess += $result.Success
    $TotalFailed += $result.Failed
}

# Sync workflows
if ($SyncAll -or $Workflows) {
    $result = Sync-Category -Name "n8n Workflows" -Files $WorkflowFiles
    $TotalSuccess += $result.Success
    $TotalFailed += $result.Failed
}

# Sync configs
if ($SyncAll -or $Configs) {
    $result = Sync-Category -Name "Configuration Files" -Files $ConfigFiles
    $TotalSuccess += $result.Success
    $TotalFailed += $result.Failed
}

# Summary
Write-Header "SYNC SUMMARY"
Write-Host "  Total files synced:  ${Green}$TotalSuccess${Reset}"
Write-Host "  Total skipped/failed: ${Yellow}$TotalFailed${Reset}"

# Restart services if requested
if ($RestartServices -and ($TotalSuccess -gt 0 -or $DryRun)) {
    Restart-VpsServices
}

# Show VPS status
Show-VpsStatus

Write-Host ""
Write-Host "${Green}Sync complete!${Reset}"
Write-Host ""

# Post-sync tips
if (-not $DryRun -and $TotalSuccess -gt 0) {
    Write-Host "Next steps:"
    Write-Host "  1. SSH to VPS: ssh ${VpsUser}@${VpsHost}"
    Write-Host "  2. Run deployment: /opt/ziggie/deploy/deploy-asset-pipeline.sh"
    Write-Host "  3. Check logs: journalctl -u ziggie-discord-bot -f"
    Write-Host ""
}
