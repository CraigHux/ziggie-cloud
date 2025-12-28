# =============================================================================
# ZIGGIE INTEGRATION GATE VERIFICATION SCRIPT
# =============================================================================
# Purpose: Automated verification of all 7 integration gates
# Usage: .\Verify-IntegrationGates.ps1 [-Gate <0-7>] [-ShowDetails] [-FixIssues]
# Author: Claude Opus 4.5
# Created: 2025-12-24
# =============================================================================

param(
    [Parameter(Mandatory=$false)]
    [ValidateRange(0,7)]
    [int]$Gate = -1,  # -1 means run all gates

    [Parameter(Mandatory=$false)]
    [switch]$ShowDetails,

    [Parameter(Mandatory=$false)]
    [switch]$FixIssues,

    [Parameter(Mandatory=$false)]
    [switch]$ExportReport
)

# =============================================================================
# CONFIGURATION
# =============================================================================

$Script:Config = @{
    ZiggiePath = "C:\Ziggie"
    AIGameDevPath = "C:\ai-game-dev-system"
    MeowPingPath = "C:\meowping-rts"
    TeamZiggiePath = "C:\team-ziggie"
    ComfyUIPath = "C:\ComfyUI"
    MCPConfigPath = "C:\Ziggie\.mcp.json"
    UVPath = "C:\ComfyUI\python_embeded\Scripts\uv.exe"
    ReportPath = "C:\Ziggie\agent-reports"
}

$Script:Results = @{
    TotalTests = 0
    Passed = 0
    Failed = 0
    Warnings = 0
    Gates = @{}
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

function Write-TestResult {
    param(
        [string]$Test,
        [string]$Status,  # PASS, FAIL, WARN, INFO
        [string]$Message,
        [string]$Gate
    )

    $Script:Results.TotalTests++

    $color = switch ($Status) {
        "PASS" { "Green"; $Script:Results.Passed++ }
        "FAIL" { "Red"; $Script:Results.Failed++ }
        "WARN" { "Yellow"; $Script:Results.Warnings++ }
        "INFO" { "Cyan" }
        default { "White" }
    }

    $prefix = switch ($Status) {
        "PASS" { "[OK]  " }
        "FAIL" { "[FAIL]" }
        "WARN" { "[WARN]" }
        "INFO" { "[INFO]" }
        default { "[----]" }
    }

    Write-Host "$prefix " -ForegroundColor $color -NoNewline
    Write-Host "$Test" -NoNewline
    if ($Message) {
        Write-Host " - $Message" -ForegroundColor Gray
    } else {
        Write-Host ""
    }

    # Track gate results
    if ($Gate -and -not $Script:Results.Gates.ContainsKey($Gate)) {
        $Script:Results.Gates[$Gate] = @{ Passed = 0; Failed = 0; Warnings = 0 }
    }
    if ($Gate) {
        switch ($Status) {
            "PASS" { $Script:Results.Gates[$Gate].Passed++ }
            "FAIL" { $Script:Results.Gates[$Gate].Failed++ }
            "WARN" { $Script:Results.Gates[$Gate].Warnings++ }
        }
    }
}

function Test-CommandExists {
    param([string]$Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

function Test-PathExists {
    param([string]$Path)
    Test-Path $Path
}

function Get-CommandVersion {
    param([string]$Command, [string]$VersionArg = "--version")
    try {
        $output = & $Command $VersionArg 2>&1
        return $output | Select-Object -First 1
    } catch {
        return $null
    }
}

# =============================================================================
# GATE 0: PLANNING & ASSESSMENT
# =============================================================================

function Test-Gate0 {
    Write-Host "`n" -NoNewline
    Write-Host "=" * 70 -ForegroundColor Cyan
    Write-Host "GATE 0: PLANNING & ASSESSMENT" -ForegroundColor Cyan
    Write-Host "=" * 70 -ForegroundColor Cyan

    # Phase 0.1: Environment Verification
    Write-Host "`n--- Phase 0.1: Environment Verification ---" -ForegroundColor Yellow

    # 0.1.1 Python
    $pythonVersion = Get-CommandVersion "python" "--version"
    if ($pythonVersion -and $pythonVersion -match "Python 3\.(1[0-9]|[2-9][0-9])") {
        Write-TestResult -Test "Python 3.10+" -Status "PASS" -Message $pythonVersion -Gate "Gate0"
    } elseif ($pythonVersion) {
        Write-TestResult -Test "Python 3.10+" -Status "WARN" -Message "$pythonVersion (recommend 3.10+)" -Gate "Gate0"
    } else {
        Write-TestResult -Test "Python 3.10+" -Status "FAIL" -Message "Not found" -Gate "Gate0"
    }

    # 0.1.2 Node.js
    $nodeVersion = Get-CommandVersion "node" "--version"
    if ($nodeVersion -and $nodeVersion -match "v(1[8-9]|[2-9][0-9])\.") {
        Write-TestResult -Test "Node.js 18+" -Status "PASS" -Message $nodeVersion -Gate "Gate0"
    } elseif ($nodeVersion) {
        Write-TestResult -Test "Node.js 18+" -Status "WARN" -Message "$nodeVersion (recommend 18+)" -Gate "Gate0"
    } else {
        Write-TestResult -Test "Node.js 18+" -Status "FAIL" -Message "Not found" -Gate "Gate0"
    }

    # 0.1.3 npm
    $npmVersion = Get-CommandVersion "npm" "--version"
    if ($npmVersion) {
        Write-TestResult -Test "npm" -Status "PASS" -Message "v$npmVersion" -Gate "Gate0"
    } else {
        Write-TestResult -Test "npm" -Status "FAIL" -Message "Not found" -Gate "Gate0"
    }

    # 0.1.4 uv
    if (Test-Path $Script:Config.UVPath) {
        $uvVersion = & $Script:Config.UVPath --version 2>&1
        Write-TestResult -Test "uv (Python package manager)" -Status "PASS" -Message $uvVersion -Gate "Gate0"
    } else {
        Write-TestResult -Test "uv (Python package manager)" -Status "FAIL" -Message "Not found at $($Script:Config.UVPath)" -Gate "Gate0"
    }

    # 0.1.5 npx
    $npxVersion = Get-CommandVersion "npx" "--version"
    if ($npxVersion) {
        Write-TestResult -Test "npx" -Status "PASS" -Message "v$npxVersion" -Gate "Gate0"
    } else {
        Write-TestResult -Test "npx" -Status "FAIL" -Message "Not found" -Gate "Gate0"
    }

    # Phase 0.2: Directory Structure Verification
    Write-Host "`n--- Phase 0.2: Directory Structure Verification ---" -ForegroundColor Yellow

    $directories = @(
        @{ Path = $Script:Config.ZiggiePath; Name = "Ziggie root" },
        @{ Path = "$($Script:Config.ZiggiePath)\coordinator"; Name = "Coordinator" },
        @{ Path = $Script:Config.AIGameDevPath; Name = "ai-game-dev-system" },
        @{ Path = "$($Script:Config.AIGameDevPath)\mcp-servers\hub"; Name = "MCP Hub" },
        @{ Path = "$($Script:Config.AIGameDevPath)\mcp-servers\comfyui-mcp"; Name = "ComfyUI MCP" },
        @{ Path = "$($Script:Config.AIGameDevPath)\mcp-servers\unreal-mcp"; Name = "Unreal MCP" },
        @{ Path = "$($Script:Config.AIGameDevPath)\mcp-servers\godot-mcp"; Name = "Godot MCP" },
        @{ Path = $Script:Config.MeowPingPath; Name = "MeowPing-RTS" },
        @{ Path = $Script:Config.TeamZiggiePath; Name = "Team-Ziggie" },
        @{ Path = $Script:Config.ComfyUIPath; Name = "ComfyUI" }
    )

    foreach ($dir in $directories) {
        if (Test-PathExists $dir.Path) {
            Write-TestResult -Test $dir.Name -Status "PASS" -Message $dir.Path -Gate "Gate0"
        } else {
            Write-TestResult -Test $dir.Name -Status "FAIL" -Message "Not found: $($dir.Path)" -Gate "Gate0"
        }
    }

    # Phase 0.3: MCP Configuration
    Write-Host "`n--- Phase 0.3: MCP Configuration ---" -ForegroundColor Yellow

    if (Test-PathExists $Script:Config.MCPConfigPath) {
        Write-TestResult -Test ".mcp.json exists" -Status "PASS" -Message $Script:Config.MCPConfigPath -Gate "Gate0"

        # Check for backup
        $backupPath = "$($Script:Config.MCPConfigPath).backup"
        if (Test-PathExists $backupPath) {
            Write-TestResult -Test ".mcp.json backup exists" -Status "PASS" -Message $backupPath -Gate "Gate0"
        } else {
            Write-TestResult -Test ".mcp.json backup exists" -Status "WARN" -Message "No backup found - recommend creating one" -Gate "Gate0"

            if ($FixIssues) {
                Copy-Item $Script:Config.MCPConfigPath $backupPath
                Write-TestResult -Test "Created .mcp.json backup" -Status "INFO" -Message $backupPath -Gate "Gate0"
            }
        }

        # Validate JSON structure
        try {
            $mcpConfig = Get-Content $Script:Config.MCPConfigPath -Raw | ConvertFrom-Json
            Write-TestResult -Test ".mcp.json valid JSON" -Status "PASS" -Gate "Gate0"

            # Check for expected servers
            $expectedServers = @("chrome-devtools", "filesystem", "memory")
            foreach ($server in $expectedServers) {
                if ($mcpConfig.mcpServers.PSObject.Properties.Name -contains $server) {
                    Write-TestResult -Test "MCP Server: $server" -Status "PASS" -Gate "Gate0"
                } else {
                    Write-TestResult -Test "MCP Server: $server" -Status "FAIL" -Message "Not configured" -Gate "Gate0"
                }
            }
        } catch {
            Write-TestResult -Test ".mcp.json valid JSON" -Status "FAIL" -Message $_.Exception.Message -Gate "Gate0"
        }
    } else {
        Write-TestResult -Test ".mcp.json exists" -Status "FAIL" -Message "Not found" -Gate "Gate0"
    }

    # Phase 0.4: Python Dependencies
    Write-Host "`n--- Phase 0.4: Python Dependencies ---" -ForegroundColor Yellow

    $packages = @("anthropic", "mcp", "aiohttp", "websockets")
    foreach ($pkg in $packages) {
        $installed = pip show $pkg 2>&1 | Out-String
        # Case-insensitive match and check for "Name:" line presence
        if ($installed -match "(?i)Name:\s*$pkg" -or $installed -match "Version:") {
            $version = if ($installed -match "Version:\s*(\S+)") { $matches[1] } else { "installed" }
            Write-TestResult -Test "pip: $pkg" -Status "PASS" -Message "v$version" -Gate "Gate0"
        } else {
            Write-TestResult -Test "pip: $pkg" -Status "WARN" -Message "Not installed (may need: pip install $pkg)" -Gate "Gate0"
        }
    }

    # Gate 0 Summary
    Write-Host "`n--- GATE 0 SUMMARY ---" -ForegroundColor Magenta
    $g0 = $Script:Results.Gates["Gate0"]
    $g0Status = if ($g0.Failed -eq 0) { "PASSED" } else { "FAILED" }
    Write-Host "Gate 0 Status: $g0Status (Passed: $($g0.Passed), Failed: $($g0.Failed), Warnings: $($g0.Warnings))" -ForegroundColor $(if ($g0Status -eq "PASSED") { "Green" } else { "Red" })

    return $g0.Failed -eq 0
}

# =============================================================================
# GATE 1: LAYER 1 ENHANCEMENT
# =============================================================================

function Test-Gate1 {
    Write-Host "`n" -NoNewline
    Write-Host "=" * 70 -ForegroundColor Cyan
    Write-Host "GATE 1: LAYER 1 ENHANCEMENT" -ForegroundColor Cyan
    Write-Host "=" * 70 -ForegroundColor Cyan

    # Phase 1.1: Filesystem MCP Access
    Write-Host "`n--- Phase 1.1: Filesystem MCP Access ---" -ForegroundColor Yellow

    # Check if .mcp.json has expanded paths
    try {
        $mcpConfig = Get-Content $Script:Config.MCPConfigPath -Raw | ConvertFrom-Json
        $fsArgs = $mcpConfig.mcpServers.filesystem.args -join " "

        $requiredPaths = @("C:/Ziggie", "C:/ai-game-dev-system", "C:/meowping-rts", "C:/team-ziggie")
        $missingPaths = @()

        foreach ($path in $requiredPaths) {
            if ($fsArgs -match [regex]::Escape($path)) {
                Write-TestResult -Test "Filesystem MCP path: $path" -Status "PASS" -Gate "Gate1"
            } else {
                Write-TestResult -Test "Filesystem MCP path: $path" -Status "FAIL" -Message "Not in .mcp.json" -Gate "Gate1"
                $missingPaths += $path
            }
        }

        if ($missingPaths.Count -gt 0) {
            Write-TestResult -Test "Filesystem MCP expansion needed" -Status "WARN" -Message "Add paths: $($missingPaths -join ', ')" -Gate "Gate1"
        }
    } catch {
        Write-TestResult -Test "Filesystem MCP config" -Status "FAIL" -Message $_.Exception.Message -Gate "Gate1"
    }

    # Phase 1.2: Memory MCP (cannot fully verify without MCP connection)
    Write-Host "`n--- Phase 1.2: Memory MCP Status ---" -ForegroundColor Yellow
    Write-TestResult -Test "Memory MCP configured" -Status "INFO" -Message "Requires Claude Code to verify entity count" -Gate "Gate1"

    # Gate 1 Summary
    Write-Host "`n--- GATE 1 SUMMARY ---" -ForegroundColor Magenta
    $g1 = $Script:Results.Gates["Gate1"]
    if (-not $g1) { $g1 = @{ Passed = 0; Failed = 0; Warnings = 0 } }
    $g1Status = if ($g1.Failed -eq 0) { "PASSED" } else { "FAILED" }
    Write-Host "Gate 1 Status: $g1Status (Passed: $($g1.Passed), Failed: $($g1.Failed), Warnings: $($g1.Warnings))" -ForegroundColor $(if ($g1Status -eq "PASSED") { "Green" } else { "Red" })

    return $g1.Failed -eq 0
}

# =============================================================================
# GATE 2: MCP HUB INTEGRATION
# =============================================================================

function Test-Gate2 {
    Write-Host "`n" -NoNewline
    Write-Host "=" * 70 -ForegroundColor Cyan
    Write-Host "GATE 2: MCP HUB INTEGRATION" -ForegroundColor Cyan
    Write-Host "=" * 70 -ForegroundColor Cyan

    # Phase 2.1: Hub Prerequisites
    Write-Host "`n--- Phase 2.1: Hub Prerequisites ---" -ForegroundColor Yellow

    # Check hub server file
    $hubPath = "$($Script:Config.AIGameDevPath)\mcp-servers\hub\mcp_hub_server.py"
    if (Test-PathExists $hubPath) {
        Write-TestResult -Test "MCP Hub server file" -Status "PASS" -Message $hubPath -Gate "Gate2"
    } else {
        Write-TestResult -Test "MCP Hub server file" -Status "FAIL" -Message "Not found: $hubPath" -Gate "Gate2"
    }

    # Phase 2.2: Hub in .mcp.json
    Write-Host "`n--- Phase 2.2: Hub Configuration ---" -ForegroundColor Yellow

    try {
        $mcpConfig = Get-Content $Script:Config.MCPConfigPath -Raw | ConvertFrom-Json
        if ($mcpConfig.mcpServers.PSObject.Properties.Name -contains "hub") {
            Write-TestResult -Test "Hub in .mcp.json" -Status "PASS" -Gate "Gate2"
        } else {
            Write-TestResult -Test "Hub in .mcp.json" -Status "FAIL" -Message "Not configured - add hub server" -Gate "Gate2"
        }
    } catch {
        Write-TestResult -Test "Hub configuration check" -Status "FAIL" -Message $_.Exception.Message -Gate "Gate2"
    }

    # Phase 2.3: Backend Services
    Write-Host "`n--- Phase 2.3: Backend Service Ports ---" -ForegroundColor Yellow

    $ports = @(
        @{ Port = 8188; Name = "ComfyUI" },
        @{ Port = 8080; Name = "Unity MCP" },
        @{ Port = 8081; Name = "Unreal MCP" },
        @{ Port = 6005; Name = "Godot MCP" },
        @{ Port = 1234; Name = "Local LLM (Ollama)" }
    )

    foreach ($p in $ports) {
        $listening = netstat -an | Select-String ":$($p.Port)\s"
        if ($listening) {
            Write-TestResult -Test "$($p.Name) port $($p.Port)" -Status "PASS" -Message "Listening" -Gate "Gate2"
        } else {
            Write-TestResult -Test "$($p.Name) port $($p.Port)" -Status "INFO" -Message "Not listening (start service if needed)" -Gate "Gate2"
        }
    }

    # Gate 2 Summary
    Write-Host "`n--- GATE 2 SUMMARY ---" -ForegroundColor Magenta
    $g2 = $Script:Results.Gates["Gate2"]
    if (-not $g2) { $g2 = @{ Passed = 0; Failed = 0; Warnings = 0 } }
    $g2Status = if ($g2.Failed -eq 0) { "PASSED" } else { "FAILED" }
    Write-Host "Gate 2 Status: $g2Status (Passed: $($g2.Passed), Failed: $($g2.Failed), Warnings: $($g2.Warnings))" -ForegroundColor $(if ($g2Status -eq "PASSED") { "Green" } else { "Red" })

    return $g2.Failed -eq 0
}

# =============================================================================
# GATE 3: GAME ENGINE MCPS
# =============================================================================

function Test-Gate3 {
    Write-Host "`n" -NoNewline
    Write-Host "=" * 70 -ForegroundColor Cyan
    Write-Host "GATE 3: GAME ENGINE MCPS" -ForegroundColor Cyan
    Write-Host "=" * 70 -ForegroundColor Cyan

    $enginesAvailable = 0

    # Unity MCP
    Write-Host "`n--- Phase 3.1: Unity MCP ---" -ForegroundColor Yellow
    $unityMcpPath = "$($Script:Config.AIGameDevPath)\mcp-servers\unity-mcp"
    if (Test-PathExists $unityMcpPath) {
        Write-TestResult -Test "Unity MCP directory" -Status "PASS" -Message $unityMcpPath -Gate "Gate3"
        $enginesAvailable++
    } else {
        Write-TestResult -Test "Unity MCP directory" -Status "FAIL" -Message "Not found" -Gate "Gate3"
    }

    # Unreal MCP
    Write-Host "`n--- Phase 3.2: Unreal MCP ---" -ForegroundColor Yellow
    $unrealMcpPath = "$($Script:Config.AIGameDevPath)\mcp-servers\unreal-mcp\Python"
    $unrealServerFile = "$unrealMcpPath\unreal_mcp_server.py"
    if (Test-PathExists $unrealServerFile) {
        Write-TestResult -Test "Unreal MCP server" -Status "PASS" -Message $unrealServerFile -Gate "Gate3"
        $enginesAvailable++
    } else {
        Write-TestResult -Test "Unreal MCP server" -Status "FAIL" -Message "Not found" -Gate "Gate3"
    }

    # Godot MCP
    Write-Host "`n--- Phase 3.3: Godot MCP ---" -ForegroundColor Yellow
    $godotMcpPath = "$($Script:Config.AIGameDevPath)\mcp-servers\godot-mcp\server"
    if (Test-PathExists $godotMcpPath) {
        Write-TestResult -Test "Godot MCP server directory" -Status "PASS" -Message $godotMcpPath -Gate "Gate3"
        $enginesAvailable++
    } else {
        Write-TestResult -Test "Godot MCP server directory" -Status "FAIL" -Message "Not found" -Gate "Gate3"
    }

    # Gate 3 requires at least ONE engine
    Write-Host "`n--- GATE 3 SUMMARY ---" -ForegroundColor Magenta
    $g3 = $Script:Results.Gates["Gate3"]
    if (-not $g3) { $g3 = @{ Passed = 0; Failed = 0; Warnings = 0 } }
    $g3Status = if ($enginesAvailable -ge 1) { "PASSED" } else { "FAILED" }
    Write-Host "Gate 3 Status: $g3Status ($enginesAvailable/3 game engine MCPs available)" -ForegroundColor $(if ($g3Status -eq "PASSED") { "Green" } else { "Red" })

    return $enginesAvailable -ge 1
}

# =============================================================================
# GATE 4: AI ASSET GENERATION
# =============================================================================

function Test-Gate4 {
    Write-Host "`n" -NoNewline
    Write-Host "=" * 70 -ForegroundColor Cyan
    Write-Host "GATE 4: AI ASSET GENERATION" -ForegroundColor Cyan
    Write-Host "=" * 70 -ForegroundColor Cyan

    # Phase 4.1: ComfyUI Setup
    Write-Host "`n--- Phase 4.1: ComfyUI Setup ---" -ForegroundColor Yellow

    if (Test-PathExists $Script:Config.ComfyUIPath) {
        Write-TestResult -Test "ComfyUI installation" -Status "PASS" -Message $Script:Config.ComfyUIPath -Gate "Gate4"
    } else {
        Write-TestResult -Test "ComfyUI installation" -Status "FAIL" -Message "Not found" -Gate "Gate4"
    }

    # Check ComfyUI MCP server
    $comfyMcpPath = "$($Script:Config.AIGameDevPath)\mcp-servers\comfyui-mcp\server.py"
    if (Test-PathExists $comfyMcpPath) {
        Write-TestResult -Test "ComfyUI MCP server" -Status "PASS" -Message $comfyMcpPath -Gate "Gate4"
    } else {
        Write-TestResult -Test "ComfyUI MCP server" -Status "FAIL" -Message "Not found" -Gate "Gate4"
    }

    # Check port 8188
    Write-Host "`n--- Phase 4.2: ComfyUI Service ---" -ForegroundColor Yellow
    $comfyListening = netstat -an | Select-String ":8188\s"
    if ($comfyListening) {
        Write-TestResult -Test "ComfyUI port 8188" -Status "PASS" -Message "Listening" -Gate "Gate4"

        # Try to connect to ComfyUI API
        try {
            $response = Invoke-WebRequest -Uri "http://127.0.0.1:8188/system_stats" -TimeoutSec 5 -UseBasicParsing
            Write-TestResult -Test "ComfyUI API" -Status "PASS" -Message "Responding" -Gate "Gate4"
        } catch {
            Write-TestResult -Test "ComfyUI API" -Status "WARN" -Message "Port open but API not responding" -Gate "Gate4"
        }
    } else {
        Write-TestResult -Test "ComfyUI port 8188" -Status "INFO" -Message "Not running (start ComfyUI to enable)" -Gate "Gate4"
    }

    # Phase 4.3: ComfyUI in .mcp.json
    Write-Host "`n--- Phase 4.3: ComfyUI MCP Configuration ---" -ForegroundColor Yellow
    try {
        $mcpConfig = Get-Content $Script:Config.MCPConfigPath -Raw | ConvertFrom-Json
        if ($mcpConfig.mcpServers.PSObject.Properties.Name -contains "comfyui") {
            Write-TestResult -Test "ComfyUI in .mcp.json" -Status "PASS" -Gate "Gate4"
        } else {
            Write-TestResult -Test "ComfyUI in .mcp.json" -Status "INFO" -Message "Not configured yet" -Gate "Gate4"
        }
    } catch {
        Write-TestResult -Test "ComfyUI config check" -Status "FAIL" -Message $_.Exception.Message -Gate "Gate4"
    }

    # Gate 4 Summary
    Write-Host "`n--- GATE 4 SUMMARY ---" -ForegroundColor Magenta
    $g4 = $Script:Results.Gates["Gate4"]
    if (-not $g4) { $g4 = @{ Passed = 0; Failed = 0; Warnings = 0 } }
    $g4Status = if ($g4.Failed -eq 0) { "PASSED" } else { "FAILED" }
    Write-Host "Gate 4 Status: $g4Status (Passed: $($g4.Passed), Failed: $($g4.Failed), Warnings: $($g4.Warnings))" -ForegroundColor $(if ($g4Status -eq "PASSED") { "Green" } else { "Red" })

    return $g4.Failed -eq 0
}

# =============================================================================
# GATE 5: AGENT ORCHESTRATION
# =============================================================================

function Test-Gate5 {
    Write-Host "`n" -NoNewline
    Write-Host "=" * 70 -ForegroundColor Cyan
    Write-Host "GATE 5: AGENT ORCHESTRATION" -ForegroundColor Cyan
    Write-Host "=" * 70 -ForegroundColor Cyan

    # Phase 5.1: Coordinator Prerequisites
    Write-Host "`n--- Phase 5.1: Coordinator Prerequisites ---" -ForegroundColor Yellow

    $coordPath = "$($Script:Config.ZiggiePath)\coordinator"
    $requiredFiles = @("main.py", "client.py", "agent_spawner.py", "claude_agent_runner.py", "watcher.py")

    foreach ($file in $requiredFiles) {
        $filePath = "$coordPath\$file"
        if (Test-PathExists $filePath) {
            Write-TestResult -Test "Coordinator: $file" -Status "PASS" -Gate "Gate5"
        } else {
            Write-TestResult -Test "Coordinator: $file" -Status "FAIL" -Message "Not found" -Gate "Gate5"
        }
    }

    # Check ANTHROPIC_API_KEY
    Write-Host "`n--- Phase 5.2: API Key Check ---" -ForegroundColor Yellow
    if ($env:ANTHROPIC_API_KEY) {
        $keyPrefix = $env:ANTHROPIC_API_KEY.Substring(0, [Math]::Min(10, $env:ANTHROPIC_API_KEY.Length))
        Write-TestResult -Test "ANTHROPIC_API_KEY env var" -Status "PASS" -Message "Set ($keyPrefix...)" -Gate "Gate5"
    } else {
        # Check .env file
        $envFile = "$($Script:Config.ZiggiePath)\config\.env"
        if (Test-PathExists $envFile) {
            $envContent = Get-Content $envFile -Raw
            if ($envContent -match "ANTHROPIC_API_KEY") {
                Write-TestResult -Test "ANTHROPIC_API_KEY in .env" -Status "PASS" -Message $envFile -Gate "Gate5"
            } else {
                Write-TestResult -Test "ANTHROPIC_API_KEY" -Status "FAIL" -Message "Not found in env or .env" -Gate "Gate5"
            }
        } else {
            Write-TestResult -Test "ANTHROPIC_API_KEY" -Status "FAIL" -Message "Not set and no .env file" -Gate "Gate5"
        }
    }

    # Check deployment directories
    Write-Host "`n--- Phase 5.3: Deployment Directories ---" -ForegroundColor Yellow
    $deployDirs = @("requests", "responses", "logs")
    foreach ($dir in $deployDirs) {
        $dirPath = "$coordPath\$dir"
        if (Test-PathExists $dirPath) {
            Write-TestResult -Test "Coordinator/$dir" -Status "PASS" -Gate "Gate5"
        } else {
            Write-TestResult -Test "Coordinator/$dir" -Status "WARN" -Message "Not found (will be created on start)" -Gate "Gate5"
        }
    }

    # Gate 5 Summary
    Write-Host "`n--- GATE 5 SUMMARY ---" -ForegroundColor Magenta
    $g5 = $Script:Results.Gates["Gate5"]
    if (-not $g5) { $g5 = @{ Passed = 0; Failed = 0; Warnings = 0 } }
    $g5Status = if ($g5.Failed -eq 0) { "PASSED" } else { "FAILED" }
    Write-Host "Gate 5 Status: $g5Status (Passed: $($g5.Passed), Failed: $($g5.Failed), Warnings: $($g5.Warnings))" -ForegroundColor $(if ($g5Status -eq "PASSED") { "Green" } else { "Red" })

    return $g5.Failed -eq 0
}

# =============================================================================
# GATE 6: KNOWLEDGE GRAPH COMPLETION
# =============================================================================

function Test-Gate6 {
    Write-Host "`n" -NoNewline
    Write-Host "=" * 70 -ForegroundColor Cyan
    Write-Host "GATE 6: KNOWLEDGE GRAPH COMPLETION" -ForegroundColor Cyan
    Write-Host "=" * 70 -ForegroundColor Cyan

    Write-Host "`n--- Phase 6.1: Memory MCP Population ---" -ForegroundColor Yellow
    Write-TestResult -Test "Memory MCP entity count" -Status "INFO" -Message "Requires Claude Code to verify (target: 75+ entities)" -Gate "Gate6"
    Write-TestResult -Test "Memory MCP relations" -Status "INFO" -Message "Requires Claude Code to verify (target: 50+ relations)" -Gate "Gate6"

    # Check for population script
    $popScriptPath = "$($Script:Config.ZiggiePath)\scripts\Populate-MemoryMCP.ps1"
    if (Test-PathExists $popScriptPath) {
        Write-TestResult -Test "Memory population script" -Status "PASS" -Message $popScriptPath -Gate "Gate6"
    } else {
        Write-TestResult -Test "Memory population script" -Status "INFO" -Message "Not found (create for automated population)" -Gate "Gate6"
    }

    # Gate 6 Summary
    Write-Host "`n--- GATE 6 SUMMARY ---" -ForegroundColor Magenta
    $g6 = $Script:Results.Gates["Gate6"]
    if (-not $g6) { $g6 = @{ Passed = 0; Failed = 0; Warnings = 0 } }
    Write-Host "Gate 6 Status: REQUIRES MANUAL VERIFICATION via Claude Code" -ForegroundColor Yellow

    return $true  # Cannot fully verify without MCP
}

# =============================================================================
# GATE 7: PRODUCTION READINESS + AWS
# =============================================================================

function Test-Gate7 {
    Write-Host "`n" -NoNewline
    Write-Host "=" * 70 -ForegroundColor Cyan
    Write-Host "GATE 7: PRODUCTION READINESS + AWS INTEGRATION" -ForegroundColor Cyan
    Write-Host "=" * 70 -ForegroundColor Cyan

    # Phase 7.1: All MCP Verification (summary of previous gates)
    Write-Host "`n--- Phase 7.1: MCP Integration Summary ---" -ForegroundColor Yellow

    $mcpServers = @("chrome-devtools", "filesystem", "memory")
    try {
        $mcpConfig = Get-Content $Script:Config.MCPConfigPath -Raw | ConvertFrom-Json
        foreach ($server in $mcpServers) {
            if ($mcpConfig.mcpServers.PSObject.Properties.Name -contains $server) {
                Write-TestResult -Test "MCP: $server" -Status "PASS" -Gate "Gate7"
            } else {
                Write-TestResult -Test "MCP: $server" -Status "FAIL" -Gate "Gate7"
            }
        }
    } catch {
        Write-TestResult -Test "MCP config" -Status "FAIL" -Message $_.Exception.Message -Gate "Gate7"
    }

    # Phase 7.5: AWS Prerequisites
    Write-Host "`n--- Phase 7.5: AWS Prerequisites ---" -ForegroundColor Yellow

    # Check AWS CLI
    $awsVersion = Get-CommandVersion "aws" "--version"
    if ($awsVersion) {
        Write-TestResult -Test "AWS CLI" -Status "PASS" -Message $awsVersion -Gate "Gate7"
    } else {
        Write-TestResult -Test "AWS CLI" -Status "WARN" -Message "Not installed (install for AWS integration)" -Gate "Gate7"
    }

    # Check AWS credentials
    if (Test-PathExists "$env:USERPROFILE\.aws\credentials") {
        Write-TestResult -Test "AWS credentials file" -Status "PASS" -Gate "Gate7"
    } else {
        Write-TestResult -Test "AWS credentials file" -Status "INFO" -Message "Not found (configure with 'aws configure')" -Gate "Gate7"
    }

    # Check AWS documentation
    $awsDocs = @(
        "AWS-HOSTINGER-MASTER-SETUP-CHECKLIST.md",
        "AWS-ZIGGIE-INTEGRATION-MASTER-PLAN.md"
    )
    foreach ($doc in $awsDocs) {
        $docPath = "$($Script:Config.ZiggiePath)\$doc"
        if (Test-PathExists $docPath) {
            Write-TestResult -Test "AWS Doc: $doc" -Status "PASS" -Gate "Gate7"
        } else {
            Write-TestResult -Test "AWS Doc: $doc" -Status "INFO" -Message "Not found" -Gate "Gate7"
        }
    }

    # Phase 7.6: Security Review
    Write-Host "`n--- Phase 7.6: Security Review ---" -ForegroundColor Yellow

    # Check for exposed secrets (basic check)
    $sensitivePatterns = @("sk-ant-", "sk-proj-", "AKIA", "password", "secret")
    $sensitiveFiles = @(
        "$($Script:Config.ZiggiePath)\.mcp.json",
        "$($Script:Config.ZiggiePath)\config\.env"
    )

    foreach ($file in $sensitiveFiles) {
        if (Test-PathExists $file) {
            $content = Get-Content $file -Raw -ErrorAction SilentlyContinue
            $foundSensitive = $false
            foreach ($pattern in $sensitivePatterns) {
                if ($content -match $pattern) {
                    $foundSensitive = $true
                    break
                }
            }
            if ($foundSensitive) {
                Write-TestResult -Test "Sensitive data in $([System.IO.Path]::GetFileName($file))" -Status "WARN" -Message "May contain secrets - review security" -Gate "Gate7"
            } else {
                Write-TestResult -Test "Security: $([System.IO.Path]::GetFileName($file))" -Status "PASS" -Message "No obvious secrets" -Gate "Gate7"
            }
        }
    }

    # Gate 7 Summary
    Write-Host "`n--- GATE 7 SUMMARY ---" -ForegroundColor Magenta
    $g7 = $Script:Results.Gates["Gate7"]
    if (-not $g7) { $g7 = @{ Passed = 0; Failed = 0; Warnings = 0 } }
    $g7Status = if ($g7.Failed -eq 0) { "PASSED" } else { "FAILED" }
    Write-Host "Gate 7 Status: $g7Status (Passed: $($g7.Passed), Failed: $($g7.Failed), Warnings: $($g7.Warnings))" -ForegroundColor $(if ($g7Status -eq "PASSED") { "Green" } else { "Red" })

    return $g7.Failed -eq 0
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

Write-Host @"

 ____  _             _        ___       _                       _   _
|__  |(_) __ _  __ _(_) ___  |_ _|_ __ | |_ ___  __ _ _ __ __ _| |_(_) ___  _ __
  / / | |/ _` |/ _` | |/ _ \  | || '_ \| __/ _ \/ _` | '__/ _` | __| |/ _ \| '_ \
 / /_ | | (_| | (_| | |  __/  | || | | | ||  __/ (_| | | | (_| | |_| | (_) | | | |
/____|_|\__, |\__, |_|\___| |___|_| |_|\__\___|\__, |_|  \__,_|\__|_|\___/|_| |_|
        |___/ |___/                            |___/
                   GATE VERIFICATION SCRIPT v1.0

"@ -ForegroundColor Cyan

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "Verification started: $timestamp" -ForegroundColor Gray
Write-Host "Target: $($Script:Config.ZiggiePath)" -ForegroundColor Gray

$gateResults = @{}

if ($Gate -eq -1) {
    # Run all gates
    $gateResults["Gate0"] = Test-Gate0
    $gateResults["Gate1"] = Test-Gate1
    $gateResults["Gate2"] = Test-Gate2
    $gateResults["Gate3"] = Test-Gate3
    $gateResults["Gate4"] = Test-Gate4
    $gateResults["Gate5"] = Test-Gate5
    $gateResults["Gate6"] = Test-Gate6
    $gateResults["Gate7"] = Test-Gate7
} else {
    # Run specific gate
    $gateFunction = "Test-Gate$Gate"
    $gateResults["Gate$Gate"] = & $gateFunction
}

# =============================================================================
# FINAL SUMMARY
# =============================================================================

Write-Host "`n" -NoNewline
Write-Host "=" * 70 -ForegroundColor Magenta
Write-Host "VERIFICATION COMPLETE - FINAL SUMMARY" -ForegroundColor Magenta
Write-Host "=" * 70 -ForegroundColor Magenta

Write-Host "`nOverall Results:" -ForegroundColor White
Write-Host "  Total Tests: $($Script:Results.TotalTests)" -ForegroundColor White
Write-Host "  Passed:      $($Script:Results.Passed)" -ForegroundColor Green
Write-Host "  Failed:      $($Script:Results.Failed)" -ForegroundColor Red
Write-Host "  Warnings:    $($Script:Results.Warnings)" -ForegroundColor Yellow

Write-Host "`nGate Status:" -ForegroundColor White
foreach ($gateName in $gateResults.Keys | Sort-Object) {
    $status = if ($gateResults[$gateName]) { "PASSED" } else { "FAILED" }
    $color = if ($gateResults[$gateName]) { "Green" } else { "Red" }
    Write-Host "  $gateName : $status" -ForegroundColor $color
}

$overallStatus = if ($Script:Results.Failed -eq 0) { "ALL GATES PASSED" } else { "GATES REQUIRE ATTENTION" }
$overallColor = if ($Script:Results.Failed -eq 0) { "Green" } else { "Yellow" }

Write-Host "`n$('=' * 70)" -ForegroundColor $overallColor
Write-Host "  $overallStatus" -ForegroundColor $overallColor
Write-Host "$('=' * 70)" -ForegroundColor $overallColor

# Export report if requested
if ($ExportReport) {
    $reportFile = "$($Script:Config.ReportPath)\gate-verification-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $reportData = @{
        Timestamp = $timestamp
        Results = $Script:Results
        GateStatus = $gateResults
    }
    $reportData | ConvertTo-Json -Depth 5 | Out-File $reportFile
    Write-Host "`nReport exported to: $reportFile" -ForegroundColor Cyan
}

Write-Host "`nVerification completed: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
