# Ziggie Bedrock Game Content Generator
# Usage: .\bedrock-game-content.ps1 -Type item|dialogue|quest|lore -Name "Item Name" [-Style "fantasy"]

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("item", "dialogue", "quest", "lore", "character", "location")]
    [string]$Type,

    [Parameter(Mandatory=$true)]
    [string]$Name,

    [string]$Style = "medieval fantasy RTS",

    [string]$Context = "",

    [ValidateSet("nova-lite", "nova-pro")]
    [string]$Model = "nova-pro"
)

$aws = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
$Region = "eu-north-1"

$modelMap = @{
    "nova-lite" = "eu.amazon.nova-lite-v1:0"
    "nova-pro" = "eu.amazon.nova-pro-v1:0"
}

$modelId = $modelMap[$Model]

# Build prompt based on content type
$systemPrompt = "You are a game content writer for Meow Ping, a $Style game featuring cat warriors. Write concise, engaging content."

$prompts = @{
    "item" = "Generate a game item description for: $Name. Include: name, rarity (Common/Uncommon/Rare/Epic/Legendary), stats bonuses, and a flavor text description. Format as JSON."
    "dialogue" = "Write dialogue lines for a character named: $Name. Include 3-5 lines they might say in different situations (greeting, combat, victory, defeat). Format as JSON array."
    "quest" = "Design a quest called: $Name. Include: title, description, objectives (3-5 steps), rewards, and difficulty level. Format as JSON."
    "lore" = "Write lore entry for: $Name. Include historical background, significance in the game world, and any legends associated with it. 2-3 paragraphs."
    "character" = "Create a character profile for: $Name. Include: role/class, personality traits, backstory, abilities, and relationships. Format as structured text."
    "location" = "Describe a game location called: $Name. Include: geography, atmosphere, inhabitants, points of interest, and strategic importance. 2-3 paragraphs."
}

$userPrompt = $prompts[$Type]
if ($Context) {
    $userPrompt += " Additional context: $Context"
}

Write-Host "=== Ziggie Game Content Generator ===" -ForegroundColor Cyan
Write-Host "Type: $Type"
Write-Host "Name: $Name"
Write-Host "Style: $Style"
Write-Host "Model: $Model"
Write-Host ""

# Escape for JSON
$escapedSystem = $systemPrompt -replace '"', '\"'
$escapedUser = $userPrompt -replace '"', '\"'

$messages = "[{`"role`":`"user`",`"content`":[{`"text`":`"$escapedSystem\n\n$escapedUser`"}]}]"

try {
    $result = & $aws bedrock-runtime converse `
        --model-id $modelId `
        --messages $messages `
        --inference-config "{`"maxTokens`":1000}" `
        --region $Region `
        --output json 2>&1

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: $result" -ForegroundColor Red
        exit 1
    }

    $response = $result | ConvertFrom-Json
    $text = $response.output.message.content[0].text
    $usage = $response.usage

    Write-Host "=== Generated Content ===" -ForegroundColor Green
    Write-Host $text
    Write-Host ""
    Write-Host "---" -ForegroundColor Gray
    Write-Host "Tokens: $($usage.inputTokens) in / $($usage.outputTokens) out" -ForegroundColor Gray
    Write-Host "Cost estimate: ~`$$([math]::Round(($usage.inputTokens * 0.0008 + $usage.outputTokens * 0.0032) / 1000, 4))" -ForegroundColor Gray

    # Optionally save to file
    $outputDir = "C:\Ziggie\generated\game-content"
    if (-not (Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }

    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $filename = "$outputDir\${Type}_${Name}_${timestamp}.txt"
    $text | Out-File -FilePath $filename -Encoding UTF8
    Write-Host "Saved to: $filename" -ForegroundColor Gray
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
