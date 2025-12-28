#!/bin/bash
# Setup script for pre-commit hooks in Ziggie ecosystem
# Run with: bash scripts/setup-pre-commit.sh

echo "======================================================================"
echo "Pre-Commit Hooks Setup for Ziggie Ecosystem"
echo "======================================================================"
echo ""

# Check Python
echo "[1/5] Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "  Found: $PYTHON_VERSION"
else
    echo "  ERROR: Python not found. Please install Python 3.8+"
    exit 1
fi

# Install pre-commit
echo ""
echo "[2/5] Installing pre-commit framework..."
pip3 install pre-commit --quiet
if [ $? -eq 0 ]; then
    VERSION=$(pre-commit --version)
    echo "  Installed: $VERSION"
else
    echo "  ERROR: Failed to install pre-commit"
    exit 1
fi

# Install hooks in Ziggie
echo ""
echo "[3/5] Installing hooks in Ziggie..."
if [ -d "/c/Ziggie" ]; then
    cd /c/Ziggie
elif [ -d "$HOME/Ziggie" ]; then
    cd "$HOME/Ziggie"
else
    cd "$(dirname "$0")/.."
fi

pre-commit install
if [ $? -eq 0 ]; then
    echo "  Hooks installed in $(pwd)"
else
    echo "  WARNING: Could not install hooks (not a git repo?)"
fi

# Install hooks in meowping-rts
echo ""
echo "[4/5] Installing hooks in meowping-rts..."
if [ -d "/c/meowping-rts" ]; then
    cd /c/meowping-rts
elif [ -d "$HOME/meowping-rts" ]; then
    cd "$HOME/meowping-rts"
fi

if [ -f ".pre-commit-config.yaml" ]; then
    pre-commit install
    if [ $? -eq 0 ]; then
        echo "  Hooks installed in $(pwd)"
    else
        echo "  WARNING: Could not install hooks (not a git repo?)"
    fi
fi

# Run initial check
echo ""
echo "[5/5] Running initial validation..."
echo ""
pre-commit run --all-files

echo ""
echo "======================================================================"
echo "Setup Complete!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "  1. Run 'pre-commit run --all-files' for full validation"
echo "  2. Commits will now be validated automatically"
echo "  3. See docs/PRE-COMMIT-HOOKS.md for documentation"
echo ""
