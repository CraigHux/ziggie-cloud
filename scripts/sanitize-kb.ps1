# Sanitize secrets from knowledge-base folder
$files = Get-ChildItem "C:\Ziggie\knowledge-base" -Recurse -Include *.md,*.txt -ErrorAction SilentlyContinue

foreach ($f in $files) {
    $content = Get-Content $f.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
    if ($content -match 'sk-ant-api03-|AIzaSy|sk-proj-') {
        $content = $content -replace 'sk-ant-api03-[a-zA-Z0-9_.-]+', '[REDACTED-ANTHROPIC-KEY]'
        $content = $content -replace 'sk-proj-[a-zA-Z0-9_.-]+', '[REDACTED-OPENAI-KEY]'
        $content = $content -replace 'AIzaSy[a-zA-Z0-9_-]+', '[REDACTED-GOOGLE-KEY]'
        Set-Content $f.FullName $content -NoNewline -Encoding UTF8
        Write-Host "Sanitized: $($f.Name)"
    }
}

Write-Host "Done"
