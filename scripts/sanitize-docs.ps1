# Sanitize secrets from docs folder
$files = Get-ChildItem "C:\Ziggie\docs" -Recurse -Include *.md,*.txt -ErrorAction SilentlyContinue

foreach ($f in $files) {
    $content = Get-Content $f.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
    if ($content -match 'sk-ant-api03-|AIzaSy') {
        $content = $content -replace 'sk-ant-api03-[a-zA-Z0-9_.-]+', '[REDACTED-ANTHROPIC-KEY]'
        $content = $content -replace 'AIzaSy[a-zA-Z0-9_-]+', '[REDACTED-GOOGLE-KEY]'
        Set-Content $f.FullName $content -NoNewline -Encoding UTF8
        Write-Host "Sanitized: $($f.Name)"
    }
}

# Also check other common locations
$otherFiles = @(
    "C:\Ziggie\ZIGGIE-ECOSYSTEM-MASTER-STATUS-V5.md",
    "C:\Ziggie\ZIGGIE-GAP-RESOLUTION-TRACKING-V5.md"
)

foreach ($path in $otherFiles) {
    if (Test-Path $path) {
        $content = Get-Content $path -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
        if ($content -match 'sk-ant-api03-|AIzaSy') {
            $content = $content -replace 'sk-ant-api03-[a-zA-Z0-9_.-]+', '[REDACTED-ANTHROPIC-KEY]'
            $content = $content -replace 'AIzaSy[a-zA-Z0-9_-]+', '[REDACTED-GOOGLE-KEY]'
            Set-Content $path $content -NoNewline -Encoding UTF8
            Write-Host "Sanitized: $path"
        }
    }
}

Write-Host "Done"
