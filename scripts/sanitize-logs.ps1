# Sanitize API keys from session log files and docs
$files = @()
$files += Get-ChildItem "C:\Ziggie\error-handling\limits\*.txt" -ErrorAction SilentlyContinue
$files += Get-ChildItem "C:\Ziggie\docs\*.md" -ErrorAction SilentlyContinue
$files += Get-ChildItem "C:\Ziggie\docs\**\*.md" -ErrorAction SilentlyContinue

foreach ($file in $files) {
    Write-Host "Sanitizing: $($file.Name)"
    $content = Get-Content $file.FullName -Raw -Encoding UTF8

    # Redact Anthropic keys (sk-ant-...)
    $content = $content -replace 'sk-ant-[a-zA-Z0-9_-]{20,}', '[REDACTED-ANTHROPIC-KEY]'

    # Redact OpenAI keys (sk-proj-... or sk-...)
    $content = $content -replace 'sk-proj-[a-zA-Z0-9_-]{20,}', '[REDACTED-OPENAI-KEY]'
    $content = $content -replace 'sk-[a-zA-Z0-9]{40,}', '[REDACTED-OPENAI-KEY]'

    # Redact AWS secret keys
    $content = $content -replace '(AWS_SECRET_ACCESS_KEY[=:]\s*)[a-zA-Z0-9/+=]{30,}', '$1[REDACTED]'

    # Redact Slack webhooks
    $content = $content -replace 'hooks\.slack\.com/services/[a-zA-Z0-9/]+', 'hooks.slack.com/services/[REDACTED]'

    # Redact YouTube API keys
    $content = $content -replace '(YOUTUBE_API_KEY[=:]\s*)AIza[a-zA-Z0-9_-]{30,}', '$1[REDACTED]'

    Set-Content $file.FullName $content -NoNewline -Encoding UTF8
}

Write-Host "Done sanitizing log files"
