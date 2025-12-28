# 3_update_paths.ps1 - Update all hardcoded paths

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PATH UPDATES - Phase 3" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$oldPathMeow = "C:/meowping-rts"
$oldPathMeowEsc = "C:\\meowping-rts"
$newPath = "C:/Ziggie"
$newPathEsc = "C:\\Ziggie"

$filesToUpdate = @(
    "C:\Ziggie\control-center\backend\config.py",
    "C:\Ziggie\control-center\backend\services\agent_loader.py",
    "C:\Ziggie\control-center\backend\services\kb_manager.py",
    "C:\Ziggie\control-center\backend\api\agents.py",
    "C:\Ziggie\control-center\backend\api\comfyui.py",
    "C:\Ziggie\control-center\backend\api\knowledge.py",
    "C:\Ziggie\control-center\backend\api\projects.py",
    "C:\Ziggie\ai-agents\knowledge-base\.env"
)

$updateCount = 0
foreach ($file in $filesToUpdate) {
    if (Test-Path $file) {
        Write-Host "Updating: $file" -ForegroundColor Yellow

        $content = Get-Content $file -Raw
        $originalContent = $content

        # Replace both forward slash and backslash versions
        $content = $content -replace [regex]::Escape($oldPathMeow), $newPath
        $content = $content -replace [regex]::Escape($oldPathMeowEsc), $newPathEsc

        if ($content -ne $originalContent) {
            $content | Set-Content $file -NoNewline
            $updateCount++
            Write-Host "  ✓ Updated" -ForegroundColor Green
        } else {
            Write-Host "  - No changes needed" -ForegroundColor Gray
        }
    } else {
        Write-Host "  ⚠ File not found: $file" -ForegroundColor Yellow
    }
}

# Update test files
Write-Host ""
Write-Host "Updating test files..." -ForegroundColor Yellow
$testFiles = Get-ChildItem "C:\Ziggie\control-center\tests" -Filter "*.py" -Recurse
foreach ($file in $testFiles) {
    $content = Get-Content $file.FullName -Raw
    $originalContent = $content

    $content = $content -replace [regex]::Escape($oldPathMeow), $newPath
    $content = $content -replace [regex]::Escape($oldPathMeowEsc), $newPathEsc

    if ($content -ne $originalContent) {
        $content | Set-Content $file.FullName -NoNewline
        $updateCount++
        Write-Host "  ✓ Updated: $($file.Name)" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PATH UPDATES COMPLETE!" -ForegroundColor Green
Write-Host "Files updated: $updateCount" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
