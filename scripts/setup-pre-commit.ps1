# Setup script for pre-commit hooks in Ziggie ecosystem
# Run with: powershell -ExecutionPolicy Bypass -File scripts\setup-pre-commit.ps1

Write-Host "=" * 70
Write-Host "Pre-Commit Hooks Setup for Ziggie Ecosystem"
Write-Host "=" * 70
Write-Host ""

# Check Python
Write-Host "[1/5] Checking Python installation..."
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Install pre-commit
Write-Host ""
Write-Host "[2/5] Installing pre-commit framework..."
pip install pre-commit --quiet
if ($LASTEXITCODE -eq 0) {
    $version = pre-commit --version
    Write-Host "  Installed: $version" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Failed to install pre-commit" -ForegroundColor Red
    exit 1
}

# Install hooks in Ziggie
Write-Host ""
Write-Host "[3/5] Installing hooks in C:\Ziggie..."
Set-Location C:\Ziggie
pre-commit install
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Hooks installed in C:\Ziggie" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Could not install hooks (not a git repo?)" -ForegroundColor Yellow
}

# Install hooks in meowping-rts
Write-Host ""
Write-Host "[4/5] Installing hooks in C:\meowping-rts..."
Set-Location C:\meowping-rts
pre-commit install
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Hooks installed in C:\meowping-rts" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Could not install hooks (not a git repo?)" -ForegroundColor Yellow
}

# Run initial check
Write-Host ""
Write-Host "[5/5] Running initial validation..."
Set-Location C:\Ziggie
Write-Host ""
Write-Host "Running on C:\Ziggie (first 5 hooks)..."
pre-commit run trailing-whitespace --all-files 2>$null
pre-commit run end-of-file-fixer --all-files 2>$null
pre-commit run check-yaml --all-files 2>$null
pre-commit run check-json --all-files 2>$null
pre-commit run no-test-skip --all-files 2>$null

Write-Host ""
Write-Host "=" * 70
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=" * 70
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Run 'pre-commit run --all-files' for full validation"
Write-Host "  2. Commits will now be validated automatically"
Write-Host "  3. See docs/PRE-COMMIT-HOOKS.md for documentation"
Write-Host ""
