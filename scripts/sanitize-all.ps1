# Comprehensive sanitization of ALL files with API keys
$rootPath = "C:\Ziggie"

# Get all text files that might contain secrets
$extensions = @("*.txt", "*.md", "*.yml", "*.yaml", "*.json", "*.env", "*.sh", "*.ps1", "*.py")
$files = @()

foreach ($ext in $extensions) {
    $files += Get-ChildItem -Path $rootPath -Filter $ext -Recurse -ErrorAction SilentlyContinue |
              Where-Object { $_.FullName -notmatch "node_modules|\.git|ziggie-cloud-repo" }
}

$count = 0
foreach ($file in $files) {
    try {
        $content = Get-Content $file.FullName -Raw -Encoding UTF8
        $original = $content

        # Skip binary files
        if ($null -eq $content) { continue }

        # Redact Anthropic keys (sk-ant-api03-... patterns with actual key content)
        $content = $content -replace 'sk-ant-api03-[a-zA-Z0-9_-]{50,}', '[REDACTED-ANTHROPIC-KEY]'
        $content = $content -replace 'sk-ant-[a-zA-Z0-9_-]{50,}', '[REDACTED-ANTHROPIC-KEY]'

        # Redact OpenAI keys
        $content = $content -replace 'sk-proj-[a-zA-Z0-9_-]{50,}', '[REDACTED-OPENAI-KEY]'

        # Redact YouTube/Google API keys (AIza... pattern)
        $content = $content -replace 'AIza[a-zA-Z0-9_-]{35}', '[REDACTED-GOOGLE-API-KEY]'

        # Redact AWS secret keys in various formats
        $content = $content -replace '(AWS_SECRET_ACCESS_KEY[=:"'']\s*)[a-zA-Z0-9/+=]{35,45}', '$1[REDACTED]'
        $content = $content -replace '("aws_secret_access_key":\s*")[^"]{30,}(")', '$1[REDACTED]$2'

        # Redact Slack webhooks
        $content = $content -replace 'hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[a-zA-Z0-9]+', 'hooks.slack.com/services/[REDACTED]'

        # Redact GitHub tokens
        $content = $content -replace 'ghp_[a-zA-Z0-9]{36}', '[REDACTED-GITHUB-TOKEN]'
        $content = $content -replace 'github_pat_[a-zA-Z0-9_]{82}', '[REDACTED-GITHUB-PAT]'

        # Only write if changes were made
        if ($content -ne $original) {
            Set-Content $file.FullName $content -NoNewline -Encoding UTF8
            Write-Host "Sanitized: $($file.FullName.Replace($rootPath, ''))"
            $count++
        }
    } catch {
        # Skip files that can't be read
    }
}

Write-Host "`nTotal files sanitized: $count"
