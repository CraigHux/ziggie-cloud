# Sanitize AWS secrets from all files
# Keep example keys but redact real ones

$files = Get-ChildItem "C:\Ziggie" -Recurse -Include *.md,*.txt -ErrorAction SilentlyContinue

$safePatterns = @(
    "AKIAIOSFODNN7EXAMPLE",  # AWS example key
    "AKIAXXXXXXXXXXXXXXXX",  # Placeholder
    "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"  # AWS example secret
)

foreach ($f in $files) {
    $content = Get-Content $f.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
    if ($null -eq $content) { continue }

    $modified = $false

    # Find all AKIA keys
    $matches = [regex]::Matches($content, 'AKIA[A-Z0-9]{16}')
    foreach ($match in $matches) {
        if ($match.Value -notin $safePatterns -and $match.Value -ne "AKIAXXXXXXXXXXXXXXXX") {
            $content = $content -replace [regex]::Escape($match.Value), '[REDACTED-AWS-ACCESS-KEY]'
            $modified = $true
        }
    }

    # Find AWS secret keys (40 chars after aws_secret_access_key or similar)
    $content = $content -replace '(aws_secret_access_key\s*[=:]\s*)[A-Za-z0-9+/=]{40}', '$1[REDACTED-AWS-SECRET]'
    $content = $content -replace '(AWS_SECRET_ACCESS_KEY\s*[=:]\s*)[A-Za-z0-9+/=]{40}', '$1[REDACTED-AWS-SECRET]'

    if ($modified -or $content -match '\[REDACTED-AWS') {
        Set-Content $f.FullName $content -NoNewline -Encoding UTF8
        Write-Host "Sanitized: $($f.Name)"
    }
}

Write-Host "Done"
