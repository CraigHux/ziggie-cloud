# INTEGRATION ROLLBACK PLAYBOOK
## Ziggie Ecosystem Recovery Procedures

> **Document ID**: ZIGGIE-ROLLBACK-PLAYBOOK-V1.0
> **Created**: 2025-12-24
> **Purpose**: Step-by-step rollback procedures for each integration stage
> **Severity Levels**: CRITICAL | HIGH | MEDIUM | LOW

---

## EXECUTIVE SUMMARY

This playbook provides detailed rollback procedures for every stage of the Claude Code integration. Use this when:

- Integration causes system instability
- MCP servers fail to connect
- Configuration changes break existing functionality
- Need to return to a known-good state

### Quick Reference: Rollback Priority

| Stage | Rollback Time | Risk Level | Complexity |
|-------|---------------|------------|------------|
| Stage 0 | 5 min | LOW | Simple |
| Stage 1 | 10 min | MEDIUM | Moderate |
| Stage 2 | 15 min | MEDIUM | Moderate |
| Stage 3 | 20 min | LOW | Simple |
| Stage 4 | 10 min | LOW | Simple |
| Stage 5 | 15 min | HIGH | Complex |
| Stage 6 | 5 min | LOW | Simple |
| Stage 7 | 30 min | HIGH | Complex |

---

## ROLLBACK DECISION TREE

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ROLLBACK DECISION TREE                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Problem Detected                                                   │
│        │                                                            │
│        ▼                                                            │
│  ┌─────────────┐     YES     ┌─────────────────────┐               │
│  │ Claude Code ├────────────►│ STAGE 1 ROLLBACK    │               │
│  │ won't start?│             │ Restore .mcp.json   │               │
│  └──────┬──────┘             └─────────────────────┘               │
│         │ NO                                                        │
│         ▼                                                           │
│  ┌─────────────┐     YES     ┌─────────────────────┐               │
│  │ MCP servers ├────────────►│ STAGE 2 ROLLBACK    │               │
│  │ not working?│             │ Remove Hub config   │               │
│  └──────┬──────┘             └─────────────────────┘               │
│         │ NO                                                        │
│         ▼                                                           │
│  ┌─────────────┐     YES     ┌─────────────────────┐               │
│  │ ComfyUI     ├────────────►│ STAGE 4 ROLLBACK    │               │
│  │ MCP failing?│             │ Remove ComfyUI MCP  │               │
│  └──────┬──────┘             └─────────────────────┘               │
│         │ NO                                                        │
│         ▼                                                           │
│  ┌─────────────┐     YES     ┌─────────────────────┐               │
│  │ Coordinator ├────────────►│ STAGE 5 ROLLBACK    │               │
│  │ crashing?   │             │ Stop coordinator    │               │
│  └──────┬──────┘             └─────────────────────┘               │
│         │ NO                                                        │
│         ▼                                                           │
│  ┌─────────────┐     YES     ┌─────────────────────┐               │
│  │ AWS issues? ├────────────►│ STAGE 7 ROLLBACK    │               │
│  │             │             │ Disable AWS configs │               │
│  └─────────────┘             └─────────────────────┘               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## STAGE 0: PLANNING & ASSESSMENT ROLLBACK

### Trigger Conditions
- Environment verification scripts failing
- Incorrect baseline captured
- Need to re-assess from scratch

### Rollback Steps

```powershell
# STAGE 0 ROLLBACK: Reset Assessment
# Time: ~5 minutes
# Risk: LOW

# 1. Remove any created backup files
Remove-Item "C:\Ziggie\.mcp.json.backup" -ErrorAction SilentlyContinue

# 2. Clear verification reports
Remove-Item "C:\Ziggie\agent-reports\gate-verification-*.json" -ErrorAction SilentlyContinue

# 3. Reset todo list (if tracked externally)
# No persistent changes made in Stage 0

Write-Host "Stage 0 rollback complete - ready to re-assess"
```

### Verification After Rollback
```powershell
# Verify clean state
Test-Path "C:\Ziggie\.mcp.json.backup"  # Should be False
```

---

## STAGE 1: LAYER 1 ENHANCEMENT ROLLBACK

### Trigger Conditions
- Filesystem MCP cannot access expanded paths
- Claude Code fails to start after .mcp.json modification
- Memory MCP population fails
- Need to revert to original MCP configuration

### Rollback Steps

```powershell
# STAGE 1 ROLLBACK: Restore Original MCP Config
# Time: ~10 minutes
# Risk: MEDIUM (affects MCP functionality)

# 1. Stop Claude Code (user action required)
Write-Host "ACTION REQUIRED: Close Claude Code / VS Code"
Read-Host "Press Enter after closing Claude Code..."

# 2. Restore original .mcp.json from backup
$backupPath = "C:\Ziggie\.mcp.json.backup"
$configPath = "C:\Ziggie\.mcp.json"

if (Test-Path $backupPath) {
    Copy-Item $backupPath $configPath -Force
    Write-Host "Restored .mcp.json from backup" -ForegroundColor Green
} else {
    # Create minimal working config
    $minimalConfig = @{
        mcpServers = @{
            "chrome-devtools" = @{
                command = "cmd"
                args = @("/c", "npx", "-y", "chrome-devtools-mcp@latest")
                env = @{
                    SystemRoot = "C:\Windows"
                    PROGRAMFILES = "C:\Program Files"
                }
            }
            filesystem = @{
                command = "cmd"
                args = @("/c", "npx", "-y", "@modelcontextprotocol/server-filesystem", "C:/Ziggie")
                env = @{}
            }
            memory = @{
                command = "cmd"
                args = @("/c", "npx", "-y", "@modelcontextprotocol/server-memory")
                env = @{}
            }
        }
    }
    $minimalConfig | ConvertTo-Json -Depth 5 | Out-File $configPath -Encoding UTF8
    Write-Host "Created minimal .mcp.json (no backup found)" -ForegroundColor Yellow
}

# 3. Clear memory MCP graph (optional - if corrupted)
# Memory MCP stores in npx cache, usually auto-clears

Write-Host "Stage 1 rollback complete"
Write-Host "ACTION REQUIRED: Restart Claude Code"
```

### Memory MCP Reset (if needed)
```powershell
# Full memory MCP reset (loses all entities)
$memoryCache = "$env:USERPROFILE\.npm\_npx"
Write-Host "Memory MCP cache location: $memoryCache"
Write-Host "To fully reset, delete memory-related cache folders"
```

### Verification After Rollback
```powershell
# Verify .mcp.json is valid
$config = Get-Content "C:\Ziggie\.mcp.json" -Raw | ConvertFrom-Json
$config.mcpServers.PSObject.Properties.Name
# Should show: chrome-devtools, filesystem, memory
```

---

## STAGE 2: MCP HUB INTEGRATION ROLLBACK

### Trigger Conditions
- MCP Hub server fails to start
- Hub causes conflicts with other MCPs
- Backend services not responding through hub
- Need to use direct MCP connections instead

### Rollback Steps

```powershell
# STAGE 2 ROLLBACK: Remove MCP Hub
# Time: ~15 minutes
# Risk: MEDIUM

# 1. Stop Claude Code
Write-Host "ACTION REQUIRED: Close Claude Code / VS Code"
Read-Host "Press Enter after closing Claude Code..."

# 2. Remove hub from .mcp.json
$configPath = "C:\Ziggie\.mcp.json"
$config = Get-Content $configPath -Raw | ConvertFrom-Json

# Remove hub server if present
if ($config.mcpServers.PSObject.Properties.Name -contains "hub") {
    $config.mcpServers.PSObject.Properties.Remove("hub")
    $config | ConvertTo-Json -Depth 5 | Out-File $configPath -Encoding UTF8
    Write-Host "Removed hub from .mcp.json" -ForegroundColor Green
} else {
    Write-Host "Hub not found in .mcp.json" -ForegroundColor Yellow
}

# 3. Kill any running hub processes
$hubProcesses = Get-Process -Name "python*" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match "mcp_hub_server" }
if ($hubProcesses) {
    $hubProcesses | Stop-Process -Force
    Write-Host "Stopped hub processes" -ForegroundColor Green
}

# 4. Backend services can continue running independently
Write-Host "Backend services (ComfyUI, Unity, etc.) unaffected"

Write-Host "Stage 2 rollback complete"
Write-Host "ACTION REQUIRED: Restart Claude Code"
```

### Verification After Rollback
```powershell
# Verify hub removed
$config = Get-Content "C:\Ziggie\.mcp.json" -Raw | ConvertFrom-Json
$config.mcpServers.PSObject.Properties.Name -contains "hub"  # Should be False
```

---

## STAGE 3: GAME ENGINE MCPS ROLLBACK

### Trigger Conditions
- Game engine MCPs causing crashes
- Unity/Unreal/Godot integration failing
- Need to remove specific engine MCP

### Rollback Steps

```powershell
# STAGE 3 ROLLBACK: Remove Game Engine MCPs
# Time: ~20 minutes
# Risk: LOW (engines work independently)

# 1. Stop Claude Code
Write-Host "ACTION REQUIRED: Close Claude Code / VS Code"
Read-Host "Press Enter after closing Claude Code..."

# 2. Remove engine MCPs from .mcp.json
$configPath = "C:\Ziggie\.mcp.json"
$config = Get-Content $configPath -Raw | ConvertFrom-Json

$engineMCPs = @("unity", "unreal", "godot")
foreach ($engine in $engineMCPs) {
    if ($config.mcpServers.PSObject.Properties.Name -contains $engine) {
        $config.mcpServers.PSObject.Properties.Remove($engine)
        Write-Host "Removed $engine MCP" -ForegroundColor Green
    }
}

$config | ConvertTo-Json -Depth 5 | Out-File $configPath -Encoding UTF8

# 3. Stop any running engine MCP servers
# Unity MCP - typically runs as part of Unity Editor
# Unreal MCP - Python process
Get-Process -Name "python*" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match "unreal_mcp_server" } |
    Stop-Process -Force -ErrorAction SilentlyContinue

# Godot MCP - Node.js process
Get-Process -Name "node*" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match "godot-mcp" } |
    Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Stage 3 rollback complete"
Write-Host "Game engines still work, just not via MCP"
```

### Selective Rollback (Single Engine)
```powershell
# Remove only Unity MCP
$config = Get-Content "C:\Ziggie\.mcp.json" -Raw | ConvertFrom-Json
$config.mcpServers.PSObject.Properties.Remove("unity")
$config | ConvertTo-Json -Depth 5 | Out-File "C:\Ziggie\.mcp.json" -Encoding UTF8
```

---

## STAGE 4: AI ASSET GENERATION ROLLBACK

### Trigger Conditions
- ComfyUI MCP failing to generate assets
- MCP blocking ComfyUI normal operation
- Need to use ComfyUI directly without MCP

### Rollback Steps

```powershell
# STAGE 4 ROLLBACK: Remove ComfyUI MCP
# Time: ~10 minutes
# Risk: LOW (ComfyUI works independently)

# 1. Stop Claude Code
Write-Host "ACTION REQUIRED: Close Claude Code / VS Code"
Read-Host "Press Enter after closing Claude Code..."

# 2. Remove comfyui from .mcp.json
$configPath = "C:\Ziggie\.mcp.json"
$config = Get-Content $configPath -Raw | ConvertFrom-Json

if ($config.mcpServers.PSObject.Properties.Name -contains "comfyui") {
    $config.mcpServers.PSObject.Properties.Remove("comfyui")
    $config | ConvertTo-Json -Depth 5 | Out-File $configPath -Encoding UTF8
    Write-Host "Removed comfyui from .mcp.json" -ForegroundColor Green
}

# 3. ComfyUI itself is unaffected - still accessible at http://127.0.0.1:8188
Write-Host "ComfyUI still available at http://127.0.0.1:8188"
Write-Host "Use direct API calls or web interface"

Write-Host "Stage 4 rollback complete"
```

### Alternative: Keep ComfyUI but use Bash
```powershell
# Instead of MCP, use Bash tool to call ComfyUI API
# Example command for Claude Code:
# curl -X POST http://127.0.0.1:8188/prompt -d '{"prompt": {...}}'
```

---

## STAGE 5: AGENT ORCHESTRATION ROLLBACK

### Trigger Conditions
- Coordinator service crashing
- Agent spawner consuming too many resources
- Anthropic API errors
- Need to stop all agent activity

### Rollback Steps

```powershell
# STAGE 5 ROLLBACK: Stop Agent Orchestration
# Time: ~15 minutes
# Risk: HIGH (may have running agents)

# 1. Stop coordinator service
$coordProcesses = Get-Process -Name "python*" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match "coordinator" }

if ($coordProcesses) {
    Write-Host "Stopping coordinator processes..." -ForegroundColor Yellow
    $coordProcesses | Stop-Process -Force
    Write-Host "Coordinator stopped" -ForegroundColor Green
}

# 2. Stop any spawned agents
$agentProcesses = Get-Process -Name "python*" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match "claude_agent_runner" }

if ($agentProcesses) {
    Write-Host "Stopping agent processes..." -ForegroundColor Yellow
    $agentProcesses | Stop-Process -Force
    Write-Host "Agents stopped" -ForegroundColor Green
}

# 3. Clear pending requests (optional - to prevent restart issues)
$requestsDir = "C:\Ziggie\coordinator\requests"
if (Test-Path $requestsDir) {
    $pendingRequests = Get-ChildItem $requestsDir -Filter "*.json"
    if ($pendingRequests.Count -gt 0) {
        Write-Host "Found $($pendingRequests.Count) pending requests"
        $pendingRequests | Move-Item -Destination "C:\Ziggie\coordinator\requests_backup\" -Force
        Write-Host "Moved pending requests to backup folder" -ForegroundColor Yellow
    }
}

# 4. Document active agents (for manual follow-up)
$responsesDir = "C:\Ziggie\coordinator\responses"
if (Test-Path $responsesDir) {
    $recentResponses = Get-ChildItem $responsesDir -Filter "*.json" |
        Where-Object { $_.LastWriteTime -gt (Get-Date).AddHours(-1) }
    Write-Host "Recent agent responses: $($recentResponses.Count)"
}

Write-Host "Stage 5 rollback complete"
Write-Host "WARNING: Check for any partially completed agent tasks"
```

### Emergency Stop (All Python Processes)
```powershell
# EMERGENCY: Stop ALL Python processes
# WARNING: This will stop ALL Python, not just Ziggie
Get-Process -Name "python*" | Stop-Process -Force
Write-Host "All Python processes stopped" -ForegroundColor Red
```

### Verification After Rollback
```powershell
# Verify no coordinator processes
Get-Process -Name "python*" | Where-Object { $_.CommandLine -match "coordinator" }
# Should return nothing
```

---

## STAGE 6: KNOWLEDGE GRAPH ROLLBACK

### Trigger Conditions
- Memory MCP graph corrupted
- Incorrect entities causing issues
- Need to start with clean graph

### Rollback Steps

```powershell
# STAGE 6 ROLLBACK: Clear Memory Graph
# Time: ~5 minutes
# Risk: LOW (data loss, but recoverable via script)

# Option A: Delete specific entities via MCP (preferred)
# Use Claude Code to run:
# mcp__memory__delete_entities with specific entity names

# Option B: Full graph reset (nuclear option)
# The memory MCP stores data in npx cache

Write-Host "Memory MCP Graph Reset Options:"
Write-Host ""
Write-Host "Option A (Preferred): Use Claude Code to delete specific entities"
Write-Host "  mcp__memory__delete_entities with entity names"
Write-Host ""
Write-Host "Option B (Full Reset): Clear npx cache"
Write-Host "  This will reset ALL memory MCP data"

$confirm = Read-Host "Perform full reset? (yes/no)"
if ($confirm -eq "yes") {
    # Find and clear memory server cache
    $npxCache = "$env:USERPROFILE\.npm\_npx"
    Write-Host "NPX cache location: $npxCache"
    Write-Host "Memory data is volatile - restart Claude Code to clear"

    # Stop Claude Code, memory will reset on next start
    Write-Host "ACTION REQUIRED: Restart Claude Code to reset memory graph"
}

Write-Host "Stage 6 rollback complete"
```

### Re-populate After Rollback
```powershell
# After rollback, re-run population script
# .\scripts\Populate-MemoryMCP.ps1
Write-Host "Re-run Populate-MemoryMCP.ps1 to restore entities"
```

---

## STAGE 7: PRODUCTION READINESS / AWS ROLLBACK

### Trigger Conditions
- AWS services causing costs
- VPC configuration issues
- Need to disconnect AWS integration
- Security concerns with AWS access

### Rollback Steps

```powershell
# STAGE 7 ROLLBACK: Disable AWS Integration
# Time: ~30 minutes
# Risk: HIGH (may have running AWS resources)

Write-Host "=" * 60 -ForegroundColor Red
Write-Host "AWS ROLLBACK - CHECK FOR RUNNING RESOURCES!" -ForegroundColor Red
Write-Host "=" * 60 -ForegroundColor Red

# 1. Check for running EC2 instances (if AWS CLI installed)
if (Get-Command "aws" -ErrorAction SilentlyContinue) {
    Write-Host "`nChecking for running EC2 instances..." -ForegroundColor Yellow
    $instances = aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query "Reservations[].Instances[].InstanceId" --output text 2>&1

    if ($instances -and $instances -ne "") {
        Write-Host "RUNNING INSTANCES FOUND:" -ForegroundColor Red
        Write-Host $instances
        Write-Host "`nWARNING: Stop these instances to avoid charges!"
        Write-Host "Command: aws ec2 stop-instances --instance-ids <instance-id>"
    } else {
        Write-Host "No running instances found" -ForegroundColor Green
    }

    # Check for Lambda functions
    Write-Host "`nChecking Lambda functions..." -ForegroundColor Yellow
    $lambdas = aws lambda list-functions --query "Functions[].FunctionName" --output text 2>&1
    if ($lambdas) {
        Write-Host "Lambda functions (review for deletion):"
        Write-Host $lambdas
    }
} else {
    Write-Host "AWS CLI not installed - manual check required" -ForegroundColor Yellow
    Write-Host "Log into AWS Console: https://console.aws.amazon.com"
    Write-Host "Check: EC2, Lambda, S3, Secrets Manager for active resources"
}

# 2. Remove AWS-related MCP configurations
$configPath = "C:\Ziggie\.mcp.json"
$config = Get-Content $configPath -Raw | ConvertFrom-Json

$awsMCPs = @("aws-gpu", "s3", "secrets-manager")
$removed = @()
foreach ($mcp in $awsMCPs) {
    if ($config.mcpServers.PSObject.Properties.Name -contains $mcp) {
        $config.mcpServers.PSObject.Properties.Remove($mcp)
        $removed += $mcp
    }
}

if ($removed.Count -gt 0) {
    $config | ConvertTo-Json -Depth 5 | Out-File $configPath -Encoding UTF8
    Write-Host "`nRemoved AWS MCPs: $($removed -join ', ')" -ForegroundColor Green
}

# 3. Document AWS state for recovery
$awsStateFile = "C:\Ziggie\agent-reports\aws-rollback-state-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"
@"
# AWS Rollback State
Generated: $(Get-Date)

## Resources to Check
- EC2 Instances (especially GPU instances)
- Lambda Functions (auto-shutdown)
- S3 Buckets (asset storage)
- Secrets Manager entries
- VPC/Security Groups

## Actions Taken
- Removed AWS MCPs from .mcp.json
- Checked for running instances

## Recovery Steps
1. Re-add AWS MCPs to .mcp.json
2. Verify AWS credentials
3. Re-enable Lambda functions
4. Test connectivity
"@ | Out-File $awsStateFile

Write-Host "`nRollback state saved to: $awsStateFile" -ForegroundColor Cyan

Write-Host "`n" + "=" * 60 -ForegroundColor Yellow
Write-Host "Stage 7 rollback complete" -ForegroundColor Yellow
Write-Host "IMPORTANT: Verify no AWS resources are still running/billing" -ForegroundColor Red
Write-Host "=" * 60 -ForegroundColor Yellow
```

### AWS Cost Emergency
```powershell
# EMERGENCY: Stop all EC2 instances
aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query "Reservations[].Instances[].InstanceId" --output text | ForEach-Object {
    aws ec2 stop-instances --instance-ids $_
    Write-Host "Stopped instance: $_" -ForegroundColor Yellow
}
```

---

## FULL SYSTEM ROLLBACK (NUCLEAR OPTION)

### When to Use
- Complete system failure
- Multiple stages failing
- Need to start completely fresh

### Full Rollback Steps

```powershell
# FULL SYSTEM ROLLBACK
# Time: ~45 minutes
# Risk: CRITICAL (loses all integration work)

Write-Host "=" * 70 -ForegroundColor Red
Write-Host "FULL SYSTEM ROLLBACK - THIS WILL RESET EVERYTHING" -ForegroundColor Red
Write-Host "=" * 70 -ForegroundColor Red

$confirm = Read-Host "Type 'ROLLBACK' to confirm"
if ($confirm -ne "ROLLBACK") {
    Write-Host "Rollback cancelled" -ForegroundColor Yellow
    exit
}

# 1. Stop all processes
Write-Host "`n[1/6] Stopping all processes..." -ForegroundColor Yellow
Get-Process -Name "python*" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "node*" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "mcp" } | Stop-Process -Force

# 2. Restore original .mcp.json
Write-Host "[2/6] Restoring .mcp.json..." -ForegroundColor Yellow
$backupPath = "C:\Ziggie\.mcp.json.backup"
if (Test-Path $backupPath) {
    Copy-Item $backupPath "C:\Ziggie\.mcp.json" -Force
    Write-Host "  Restored from backup" -ForegroundColor Green
} else {
    # Create minimal config
    $minimalConfig = @{
        mcpServers = @{
            "chrome-devtools" = @{
                command = "cmd"
                args = @("/c", "npx", "-y", "chrome-devtools-mcp@latest")
            }
            filesystem = @{
                command = "cmd"
                args = @("/c", "npx", "-y", "@modelcontextprotocol/server-filesystem", "C:/Ziggie")
            }
            memory = @{
                command = "cmd"
                args = @("/c", "npx", "-y", "@modelcontextprotocol/server-memory")
            }
        }
    }
    $minimalConfig | ConvertTo-Json -Depth 5 | Out-File "C:\Ziggie\.mcp.json" -Encoding UTF8
    Write-Host "  Created minimal config" -ForegroundColor Yellow
}

# 3. Clear coordinator queues
Write-Host "[3/6] Clearing coordinator queues..." -ForegroundColor Yellow
$coordDirs = @("requests", "responses", "logs")
foreach ($dir in $coordDirs) {
    $path = "C:\Ziggie\coordinator\$dir"
    if (Test-Path $path) {
        $backupDir = "C:\Ziggie\coordinator\${dir}_rollback_$(Get-Date -Format 'yyyyMMdd')"
        Move-Item $path $backupDir -Force -ErrorAction SilentlyContinue
        New-Item $path -ItemType Directory -Force | Out-Null
    }
}

# 4. Check AWS resources
Write-Host "[4/6] Checking AWS resources..." -ForegroundColor Yellow
if (Get-Command "aws" -ErrorAction SilentlyContinue) {
    $instances = aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --output text 2>&1
    if ($instances) {
        Write-Host "  WARNING: Running AWS instances detected - check manually" -ForegroundColor Red
    }
}

# 5. Document rollback
Write-Host "[5/6] Documenting rollback..." -ForegroundColor Yellow
$rollbackLog = "C:\Ziggie\agent-reports\FULL-ROLLBACK-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"
@"
# Full System Rollback Log
Executed: $(Get-Date)
Reason: User-initiated full rollback

## Actions Taken
- Stopped all Python/Node MCP processes
- Restored .mcp.json to minimal state
- Cleared coordinator queues (backed up)
- Checked AWS resources

## Recovery Steps
1. Restart Claude Code
2. Re-run integration from Stage 0
3. Reference CLAUDE-CODE-INTEGRATION-PLAN.md
"@ | Out-File $rollbackLog

# 6. Summary
Write-Host "[6/6] Rollback complete" -ForegroundColor Green
Write-Host ""
Write-Host "=" * 70 -ForegroundColor Yellow
Write-Host "FULL ROLLBACK COMPLETE" -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Yellow
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Restart Claude Code"
Write-Host "2. Verify basic MCP functionality"
Write-Host "3. Re-run integration from Stage 0 if needed"
Write-Host ""
Write-Host "Rollback log: $rollbackLog"
```

---

## RECOVERY VERIFICATION CHECKLIST

After any rollback, verify system health:

```powershell
# Post-Rollback Verification
Write-Host "Running post-rollback verification..."

# 1. .mcp.json is valid JSON
try {
    Get-Content "C:\Ziggie\.mcp.json" -Raw | ConvertFrom-Json | Out-Null
    Write-Host "[OK] .mcp.json is valid" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] .mcp.json is invalid" -ForegroundColor Red
}

# 2. Core directories exist
$dirs = @("C:\Ziggie", "C:\Ziggie\coordinator", "C:\Ziggie\scripts")
foreach ($dir in $dirs) {
    if (Test-Path $dir) {
        Write-Host "[OK] $dir exists" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] $dir missing" -ForegroundColor Red
    }
}

# 3. No zombie processes
$zombies = Get-Process -Name "python*" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "coordinator|mcp|agent" }
if ($zombies) {
    Write-Host "[WARN] Found running processes:" -ForegroundColor Yellow
    $zombies | ForEach-Object { Write-Host "  $($_.Id): $($_.ProcessName)" }
} else {
    Write-Host "[OK] No zombie processes" -ForegroundColor Green
}

Write-Host ""
Write-Host "Verification complete. Restart Claude Code to continue."
```

---

## DOCUMENT METADATA

| Field | Value |
|-------|-------|
| Document ID | ZIGGIE-ROLLBACK-PLAYBOOK-V1.0 |
| Created | 2025-12-24 |
| Stages Covered | 0-7 + Full System |
| Scripts Included | 15+ |
| Estimated Recovery Times | 5-45 minutes |

---

**END OF ROLLBACK PLAYBOOK**
