# AGENT ARCHITECTURE VALIDATION SUITE
# Validates agent expansion toward 1,884 target (12 L1, 144 L2, 1,728 L3)
# Version: 1.0
# Created: 2025-11-08

param(
    [switch]$Verbose,
    [switch]$FixIssues,
    [switch]$GenerateReport
)

$ErrorCount = 0
$WarningCount = 0
$PassCount = 0
$TestResults = @()

function Test-Result {
    param(
        [string]$TestID,
        [string]$TestName,
        [bool]$Condition,
        [string]$Message,
        [switch]$Critical,
        [string]$Details = ""
    )

    $result = @{
        TestID = $TestID
        TestName = $TestName
        Status = if ($Condition) { "PASS" } elseif ($Critical) { "FAIL" } else { "WARN" }
        Message = $Message
        Details = $Details
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }

    $script:TestResults += $result

    if ($Condition) {
        Write-Host "✓ PASS [$TestID]: $TestName" -ForegroundColor Green
        $script:PassCount++
    } elseif ($Critical) {
        Write-Host "❌ FAIL [$TestID]: $TestName - $Message" -ForegroundColor Red
        $script:ErrorCount++
    } else {
        Write-Host "⚠️  WARN [$TestID]: $TestName - $Message" -ForegroundColor Yellow
        $script:WarningCount++
    }

    if ($Verbose -and $Details) {
        Write-Host "   Details: $Details" -ForegroundColor Gray
    }
}

# ============================================================================
# CONFIGURATION
# ============================================================================

$AgentsPath = "C:\Ziggie\ai-agents"
$SubAgentFile = "$AgentsPath\SUB_AGENT_ARCHITECTURE.md"
$L3File = "$AgentsPath\L3_MICRO_AGENT_ARCHITECTURE.md"

$ExpectedCounts = @{
    L1 = 12
    L2 = 144
    L3 = 1728
    Total = 1884
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

function Get-L1Files {
    $files = @()
    for ($i = 1; $i -le 12; $i++) {
        $pattern = "{0:D2}_*_AGENT.md" -f $i
        $found = Get-ChildItem $AgentsPath -Filter $pattern -ErrorAction SilentlyContinue
        if ($found) {
            $files += @{
                Number = $i
                Path = $found.FullName
                Name = $found.Name
                Exists = $true
            }
        } else {
            $files += @{
                Number = $i
                Path = "$AgentsPath\{0:D2}_AGENT.md" -f $i
                Name = "{0:D2}_AGENT.md" -f $i
                Exists = $false
            }
        }
    }
    return $files
}

function Get-L2Agents {
    if (-not (Test-Path $SubAgentFile)) {
        return @()
    }

    $content = Get-Content $SubAgentFile
    $agents = @()

    foreach ($line in $content) {
        if ($line -match '^### Sub-Agent (\d+)\.(\d+):\s+\*\*(.+?)\*\*') {
            $agents += @{
                L1 = [int]$matches[1]
                L2 = [int]$matches[2]
                ID = "L2.$($matches[1]).$($matches[2])"
                Name = $matches[3]
            }
        }
    }

    return $agents
}

function Get-L3Agents {
    if (-not (Test-Path $L3File)) {
        return @()
    }

    $content = Get-Content $L3File
    $agents = @()

    foreach ($line in $content) {
        if ($line -match '^### L3\.(\d+)\.(\d+)\.(\d+):\s+(.+)') {
            $agents += @{
                L1 = [int]$matches[1]
                L2 = [int]$matches[2]
                L3 = [int]$matches[3]
                ID = "L3.$($matches[1]).$($matches[2]).$($matches[3])"
                Name = $matches[4].TrimStart('*').TrimEnd('*').Trim()
                ParentL2 = "L2.$($matches[1]).$($matches[2])"
            }
        }
    }

    return $agents
}

# ============================================================================
# BANNER
# ============================================================================

Clear-Host
Write-Host @"
╔═══════════════════════════════════════════════════════════════╗
║          AGENT ARCHITECTURE VALIDATION SUITE v1.0             ║
║          Target: 1,884 Agents (12 L1, 144 L2, 1,728 L3)       ║
╚═══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

Write-Host "`nStarting validation at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" -ForegroundColor Gray

# ============================================================================
# TEST SUITE 1: FILE STRUCTURE
# ============================================================================

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "TEST SUITE 1: FILE STRUCTURE VALIDATION" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# Test 1.1: Root directory exists
Test-Result -TestID "FS-001" -TestName "Agent root directory exists" `
    -Condition (Test-Path $AgentsPath) `
    -Message "Path not found: $AgentsPath" `
    -Critical

# Test 1.2-1.13: L1 Agent Files
$l1Files = Get-L1Files
for ($i = 0; $i -lt $l1Files.Count; $i++) {
    $file = $l1Files[$i]
    $testNum = 2 + $i
    Test-Result -TestID "FS-$('{0:D3}' -f $testNum)" -TestName "L1.$($file.Number) agent file exists" `
        -Condition $file.Exists `
        -Message "Missing: $($file.Name)" `
        -Critical:($file.Number -le 9) `
        -Details $file.Path
}

# Test 1.14: SUB_AGENT_ARCHITECTURE.md exists
Test-Result -TestID "FS-014" -TestName "SUB_AGENT_ARCHITECTURE.md exists" `
    -Condition (Test-Path $SubAgentFile) `
    -Message "Critical file missing" `
    -Critical `
    -Details $SubAgentFile

# Test 1.15: L3_MICRO_AGENT_ARCHITECTURE.md exists
Test-Result -TestID "FS-015" -TestName "L3_MICRO_AGENT_ARCHITECTURE.md exists" `
    -Condition (Test-Path $L3File) `
    -Message "Critical file missing" `
    -Critical `
    -Details $L3File

# Test 1.16: Template file exists
$templateExists = Test-Path "$AgentsPath\TEMPLATE_L1_AGENT.md"
Test-Result -TestID "FS-016" -TestName "Template file exists" `
    -Condition $templateExists `
    -Message "TEMPLATE_L1_AGENT.md not found" `
    -Details "$AgentsPath\TEMPLATE_L1_AGENT.md"

# ============================================================================
# TEST SUITE 2: AGENT COUNTS
# ============================================================================

Write-Host "`n═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "TEST SUITE 2: AGENT COUNT VALIDATION" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# Count agents
$l1Count = ($l1Files | Where-Object { $_.Exists }).Count
$l2Agents = Get-L2Agents
$l2Count = $l2Agents.Count
$l3Agents = Get-L3Agents
$l3Count = $l3Agents.Count
$totalCount = $l1Count + $l2Count + $l3Count

# Test 2.1: L1 Count
$l1Complete = ($l1Count -eq $ExpectedCounts.L1)
$l1Percent = [math]::Round(($l1Count / $ExpectedCounts.L1) * 100, 1)
Test-Result -TestID "CV-001" -TestName "L1 agent count" `
    -Condition $l1Complete `
    -Message "Expected $($ExpectedCounts.L1), found $l1Count ($l1Percent`% complete)" `
    -Critical `
    -Details "Gap: $($ExpectedCounts.L1 - $l1Count) agents missing"

# Test 2.2: L2 Count
$l2Complete = ($l2Count -eq $ExpectedCounts.L2)
$l2Percent = [math]::Round(($l2Count / $ExpectedCounts.L2) * 100, 1)
Test-Result -TestID "CV-002" -TestName "L2 agent count" `
    -Condition $l2Complete `
    -Message "Expected $($ExpectedCounts.L2), found $l2Count ($l2Percent`% complete)" `
    -Critical `
    -Details "Gap: $($ExpectedCounts.L2 - $l2Count) agents missing"

# Test 2.3: L3 Count
$l3Complete = ($l3Count -eq $ExpectedCounts.L3)
$l3Percent = [math]::Round(($l3Count / $ExpectedCounts.L3) * 100, 1)
Test-Result -TestID "CV-003" -TestName "L3 agent count" `
    -Condition $l3Complete `
    -Message "Expected $($ExpectedCounts.L3), found $l3Count ($l3Percent`% complete)" `
    -Critical `
    -Details "Gap: $($ExpectedCounts.L3 - $l3Count) agents missing"

# Test 2.4: Total Count
$totalComplete = ($totalCount -eq $ExpectedCounts.Total)
$totalPercent = [math]::Round(($totalCount / $ExpectedCounts.Total) * 100, 1)
Test-Result -TestID "CV-004" -TestName "Total agent count" `
    -Condition $totalComplete `
    -Message "Expected $($ExpectedCounts.Total), found $totalCount ($totalPercent`% complete)" `
    -Critical `
    -Details "Gap: $($ExpectedCounts.Total - $totalCount) agents missing"

# Display progress
Write-Host "`nCURRENT PROGRESS:" -ForegroundColor Gray
Write-Host "  L1:    $l1Count / $($ExpectedCounts.L1)  ($l1Percent`% complete)" -ForegroundColor Gray
Write-Host "  L2:    $l2Count / $($ExpectedCounts.L2)  ($l2Percent`% complete)" -ForegroundColor Gray
Write-Host "  L3:    $l3Count / $($ExpectedCounts.L3)  ($l3Percent`% complete)" -ForegroundColor Gray
Write-Host "  Total: $totalCount / $($ExpectedCounts.Total)  ($totalPercent`% complete)" -ForegroundColor Gray

# ============================================================================
# TEST SUITE 3: DISTRIBUTION VALIDATION
# ============================================================================

Write-Host "`n═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "TEST SUITE 3: DISTRIBUTION VALIDATION" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# Test 3.1-3.12: L2 per L1 (should be 12 each)
for ($i = 1; $i -le 12; $i++) {
    $l2ForL1 = ($l2Agents | Where-Object { $_.L1 -eq $i }).Count
    $expected = 12
    $isCorrect = ($l2ForL1 -eq $expected)

    Test-Result -TestID "DV-$('{0:D3}' -f $i)" -TestName "L1.$i has 12 L2 sub-agents" `
        -Condition $isCorrect `
        -Message "Expected $expected, found $l2ForL1" `
        -Details "L1.$i distribution"
}

# Test 3.13+: L3 per L2 sample check (check first 10 L2s)
$testNum = 13
$l2Sample = $l2Agents | Select-Object -First 10
foreach ($l2 in $l2Sample) {
    $l3ForL2 = ($l3Agents | Where-Object { $_.ParentL2 -eq $l2.ID }).Count
    $expected = 12
    $isCorrect = ($l3ForL2 -eq $expected)

    Test-Result -TestID "DV-$('{0:D3}' -f $testNum)" -TestName "$($l2.ID) has 12 L3 micro-agents" `
        -Condition $isCorrect `
        -Message "Expected $expected, found $l3ForL2" `
        -Details "$($l2.Name)"

    $testNum++
}

# ============================================================================
# TEST SUITE 4: DUPLICATE DETECTION
# ============================================================================

Write-Host "`n═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "TEST SUITE 4: DUPLICATE ID DETECTION" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# Test 4.1: Duplicate L2 IDs
$l2IDs = $l2Agents | ForEach-Object { $_.ID }
$l2Duplicates = $l2IDs | Group-Object | Where-Object { $_.Count -gt 1 }
$noDuplicateL2 = ($l2Duplicates.Count -eq 0)

$dupDetails = if ($l2Duplicates) {
    "Duplicates: " + (($l2Duplicates | ForEach-Object { "$($_.Name) (x$($_.Count))" }) -join ", ")
} else {
    "All L2 IDs unique"
}

Test-Result -TestID "DD-001" -TestName "No duplicate L2 IDs" `
    -Condition $noDuplicateL2 `
    -Message "Found $($l2Duplicates.Count) duplicate L2 ID(s)" `
    -Critical `
    -Details $dupDetails

# Test 4.2: Duplicate L3 IDs
$l3IDs = $l3Agents | ForEach-Object { $_.ID }
$l3Duplicates = $l3IDs | Group-Object | Where-Object { $_.Count -gt 1 }
$noDuplicateL3 = ($l3Duplicates.Count -eq 0)

$dupDetails = if ($l3Duplicates) {
    "Duplicates: " + (($l3Duplicates | ForEach-Object { "$($_.Name) (x$($_.Count))" }) -join ", ")
} else {
    "All L3 IDs unique"
}

Test-Result -TestID "DD-002" -TestName "No duplicate L3 IDs" `
    -Condition $noDuplicateL3 `
    -Message "Found $($l3Duplicates.Count) duplicate L3 ID(s)" `
    -Critical `
    -Details $dupDetails

# ============================================================================
# TEST SUITE 5: REFERENCE VALIDATION
# ============================================================================

Write-Host "`n═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "TEST SUITE 5: CROSS-REFERENCE VALIDATION" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# Test 5.1: L2 parent references
$validL1s = ($l1Files | Where-Object { $_.Exists } | ForEach-Object { $_.Number })
$l2Orphans = @()

foreach ($l2 in $l2Agents) {
    if ($l2.L1 -notin $validL1s) {
        $l2Orphans += $l2.ID
    }
}

$noL2Orphans = ($l2Orphans.Count -eq 0)
$orphanDetails = if ($l2Orphans) {
    "Orphaned L2s: " + ($l2Orphans -join ", ")
} else {
    "All L2s have valid parent L1"
}

Test-Result -TestID "RV-001" -TestName "All L2 agents have valid parent L1" `
    -Condition $noL2Orphans `
    -Message "Found $($l2Orphans.Count) orphaned L2 agent(s)" `
    -Critical `
    -Details $orphanDetails

# Test 5.2: L3 parent references
$validL2IDs = $l2Agents | ForEach-Object { $_.ID }
$l3Orphans = @()

foreach ($l3 in $l3Agents) {
    if ($l3.ParentL2 -notin $validL2IDs) {
        $l3Orphans += $l3.ID
    }
}

$noL3Orphans = ($l3Orphans.Count -eq 0)
$orphanDetails = if ($l3Orphans) {
    "Orphaned L3s (first 10): " + (($l3Orphans | Select-Object -First 10) -join ", ")
} else {
    "All L3s have valid parent L2"
}

Test-Result -TestID "RV-002" -TestName "All L3 agents have valid parent L2" `
    -Condition $noL3Orphans `
    -Message "Found $($l3Orphans.Count) orphaned L3 agent(s)" `
    -Critical `
    -Details $orphanDetails

# ============================================================================
# TEST SUITE 6: FORMAT VALIDATION
# ============================================================================

Write-Host "`n═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "TEST SUITE 6: FORMAT VALIDATION" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# Test 6.1: L2 format consistency
if (Test-Path $SubAgentFile) {
    $subContent = Get-Content $SubAgentFile -Raw
    $properFormat = $subContent -match '### Sub-Agent \d+\.\d+: \*\*.+?\*\*'

    Test-Result -TestID "FV-001" -TestName "L2 agents follow proper format" `
        -Condition $properFormat `
        -Message "L2 format issues detected" `
        -Details "Expected: ### Sub-Agent X.Y: **Name**"
}

# Test 6.2: L3 format consistency
if (Test-Path $L3File) {
    $l3Content = Get-Content $L3File -Raw
    $properFormat = $l3Content -match '### L3\.\d+\.\d+\.\d+:'

    Test-Result -TestID "FV-002" -TestName "L3 agents follow proper format" `
        -Condition $properFormat `
        -Message "L3 format issues detected" `
        -Details "Expected: ### L3.X.Y.Z: Name"
}

# ============================================================================
# SUMMARY
# ============================================================================

Write-Host "`n═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "VALIDATION SUMMARY" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

$totalTests = $PassCount + $WarningCount + $ErrorCount
$passRate = if ($totalTests -gt 0) {
    [math]::Round(($PassCount / $totalTests) * 100, 1)
} else {
    0
}

Write-Host "`nTEST RESULTS:" -ForegroundColor Gray
Write-Host "  Passed:   $PassCount tests" -ForegroundColor Green
Write-Host "  Warnings: $WarningCount tests" -ForegroundColor Yellow
Write-Host "  Failed:   $ErrorCount tests" -ForegroundColor Red
Write-Host "  Total:    $totalTests tests" -ForegroundColor Gray
$prColor = if ($passRate -eq 100) { "Green" } elseif ($passRate -ge 90) { "Yellow" } else { "Red" }
Write-Host "  Pass Rate: $passRate`%" -ForegroundColor $prColor

# Final verdict
Write-Host ""
if ($ErrorCount -gt 0) {
    Write-Host "⚠️  VALIDATION FAILED - Fix critical errors before deployment" -ForegroundColor Red
    $exitCode = 1
} elseif ($WarningCount -gt 0) {
    Write-Host "⚠️  VALIDATION PASSED WITH WARNINGS" -ForegroundColor Yellow
    $exitCode = 0
} else {
    Write-Host "✓ VALIDATION PASSED - All systems go!" -ForegroundColor Green
    $exitCode = 0
}

Write-Host "`nCompleted at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray

# Report generation temporarily disabled due to PowerShell encoding issues
# Run with -Verbose for detailed output

if ($null -eq $exitCode) {
    $exitCode = 0
}

exit $exitCode
