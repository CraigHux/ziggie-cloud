# Sanitize secrets from root and docs folders
$paths = @(
    "C:\Ziggie\AWS-ZIGGIE-INTEGRATION-MASTER-PLAN.md",
    "C:\Ziggie\AWS_SECRETS_MANAGER_RESEARCH.md",
    "C:\Ziggie\AWS_SECRETS_QUICKSTART.md",
    "C:\Ziggie\docs\archive\2025-12-24_ZIGGIE-ECOSYSTEM-MASTER-STATUS-V2.md",
    "C:\Ziggie\docs\retrospective\L1-SESSION-LESSONS.md",
    "C:\Ziggie\INTEGRATION-AWS-STAGE.md"
)

foreach ($path in $paths) {
    if (Test-Path $path) {
        $content = Get-Content $path -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
        if ($content -match 'sk-proj-|sk-ant-api03-|AIzaSy') {
            $content = $content -replace 'sk-ant-api03-[a-zA-Z0-9_.-]+', '[REDACTED-ANTHROPIC-KEY]'
            $content = $content -replace 'sk-proj-[a-zA-Z0-9_.-]+', '[REDACTED-OPENAI-KEY]'
            $content = $content -replace 'AIzaSy[a-zA-Z0-9_-]+', '[REDACTED-GOOGLE-KEY]'
            Set-Content $path $content -NoNewline -Encoding UTF8
            Write-Host "Sanitized: $path"
        }
    }
}

Write-Host "Done"
