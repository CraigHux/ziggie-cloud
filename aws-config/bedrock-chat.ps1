# Ziggie Bedrock Chat Helper
# Usage: .\bedrock-chat.ps1 -Prompt "Your question" [-Model nova-lite|nova-pro|nova-micro]

param(
    [Parameter(Mandatory=$true)]
    [string]$Prompt,

    [ValidateSet("nova-lite", "nova-pro", "nova-micro")]
    [string]$Model = "nova-lite",

    [int]$MaxTokens = 500
)

$aws = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
$Region = "eu-north-1"

# Map model names to inference profile IDs
$modelMap = @{
    "nova-lite" = "eu.amazon.nova-lite-v1:0"
    "nova-pro" = "eu.amazon.nova-pro-v1:0"
    "nova-micro" = "eu.amazon.nova-micro-v1:0"
}

$modelId = $modelMap[$Model]

Write-Host "=== Ziggie Bedrock Chat ===" -ForegroundColor Cyan
Write-Host "Model: $Model ($modelId)"
Write-Host "Prompt: $Prompt"
Write-Host ""

# Build messages JSON (escape for PowerShell)
$escapedPrompt = $Prompt -replace '"', '\"'
$messages = "[{`"role`":`"user`",`"content`":[{`"text`":`"$escapedPrompt`"}]}]"

try {
    $result = & $aws bedrock-runtime converse `
        --model-id $modelId `
        --messages $messages `
        --inference-config "{`"maxTokens`":$MaxTokens}" `
        --region $Region `
        --output json 2>&1

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: $result" -ForegroundColor Red
        exit 1
    }

    $response = $result | ConvertFrom-Json
    $text = $response.output.message.content[0].text
    $usage = $response.usage

    Write-Host "Response:" -ForegroundColor Green
    Write-Host $text
    Write-Host ""
    Write-Host "Tokens: $($usage.inputTokens) in / $($usage.outputTokens) out" -ForegroundColor Gray
    Write-Host "Latency: $($response.metrics.latencyMs)ms" -ForegroundColor Gray
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
