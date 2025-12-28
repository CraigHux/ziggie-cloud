#!/bin/bash

################################################################################
# File Integrity Verification Script for Ziggie Migration
# Purpose: Verify all files are present and intact
################################################################################

set -e

VERIFICATION_LOG="/c/Ziggie/VERIFICATION_RESULTS.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Clear previous log
> "$VERIFICATION_LOG"

echo "================================================================================" | tee -a "$VERIFICATION_LOG"
echo "FILE INTEGRITY VERIFICATION - Ziggie Migration" | tee -a "$VERIFICATION_LOG"
echo "Timestamp: $TIMESTAMP" | tee -a "$VERIFICATION_LOG"
echo "================================================================================" | tee -a "$VERIFICATION_LOG"
echo "" | tee -a "$VERIFICATION_LOG"

# Task 1: Count files
echo "[TASK 1] File Count Verification" | tee -a "$VERIFICATION_LOG"
echo "=================================" | tee -a "$VERIFICATION_LOG"

ZIGGIE_FILE_COUNT=$(find /c/Ziggie -type f 2>/dev/null | wc -l)
echo "Total files in /c/Ziggie: $ZIGGIE_FILE_COUNT" | tee -a "$VERIFICATION_LOG"

# Count by subdirectory
echo "" | tee -a "$VERIFICATION_LOG"
echo "File count by subdirectory:" | tee -a "$VERIFICATION_LOG"
for dir in /c/Ziggie/*/; do
    if [ -d "$dir" ]; then
        dir_name=$(basename "$dir")
        file_count=$(find "$dir" -type f 2>/dev/null | wc -l)
        echo "  $dir_name: $file_count files" | tee -a "$VERIFICATION_LOG"
    fi
done

# Task 2: Verify critical directories exist
echo "" | tee -a "$VERIFICATION_LOG"
echo "[TASK 2] Directory Structure Verification" | tee -a "$VERIFICATION_LOG"
echo "==========================================" | tee -a "$VERIFICATION_LOG"

CRITICAL_DIRS=(
    "/c/Ziggie/control-center/backend"
    "/c/Ziggie/control-center/frontend"
    "/c/Ziggie/knowledge-base/src"
    "/c/Ziggie/agents"
    "/c/Ziggie/config"
)

for dir in "${CRITICAL_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "✓ PASS: $dir exists" | tee -a "$VERIFICATION_LOG"
    else
        echo "✗ FAIL: $dir NOT FOUND" | tee -a "$VERIFICATION_LOG"
    fi
done

# Task 3: Verify critical files exist
echo "" | tee -a "$VERIFICATION_LOG"
echo "[TASK 3] Critical Files Verification" | tee -a "$VERIFICATION_LOG"
echo "=====================================" | tee -a "$VERIFICATION_LOG"

CRITICAL_FILES=(
    "/c/Ziggie/control-center/backend/main.py"
    "/c/Ziggie/control-center/backend/config.py"
    "/c/Ziggie/control-center/backend/requirements.txt"
    "/c/Ziggie/control-center/frontend/package.json"
    "/c/Ziggie/knowledge-base/src"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -e "$file" ]; then
        echo "✓ PASS: $file exists" | tee -a "$VERIFICATION_LOG"
    else
        echo "✗ FAIL: $file NOT FOUND" | tee -a "$VERIFICATION_LOG"
    fi
done

# Task 4: Verify file sizes are reasonable
echo "" | tee -a "$VERIFICATION_LOG"
echo "[TASK 4] File Size Verification" | tee -a "$VERIFICATION_LOG"
echo "================================" | tee -a "$VERIFICATION_LOG"

BACKEND_SIZE=$(du -sh /c/Ziggie/control-center/backend 2>/dev/null | cut -f1)
FRONTEND_SIZE=$(du -sh /c/Ziggie/control-center/frontend 2>/dev/null | cut -f1)
KB_SIZE=$(du -sh /c/Ziggie/knowledge-base 2>/dev/null | cut -f1)

echo "Control Center Backend: $BACKEND_SIZE" | tee -a "$VERIFICATION_LOG"
echo "Control Center Frontend: $FRONTEND_SIZE" | tee -a "$VERIFICATION_LOG"
echo "Knowledge Base: $KB_SIZE" | tee -a "$VERIFICATION_LOG"

# Task 5: Check for missing Python dependencies
echo "" | tee -a "$VERIFICATION_LOG"
echo "[TASK 5] Python Environment Check" | tee -a "$VERIFICATION_LOG"
echo "==================================" | tee -a "$VERIFICATION_LOG"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ PASS: Python found - $PYTHON_VERSION" | tee -a "$VERIFICATION_LOG"
else
    echo "⚠ WARNING: Python3 not found in PATH" | tee -a "$VERIFICATION_LOG"
fi

if [ -f "/c/Ziggie/control-center/backend/requirements.txt" ]; then
    echo "✓ PASS: requirements.txt found" | tee -a "$VERIFICATION_LOG"
    echo "  Dependencies:" | tee -a "$VERIFICATION_LOG"
    head -5 /c/Ziggie/control-center/backend/requirements.txt | sed 's/^/    /' | tee -a "$VERIFICATION_LOG"
fi

# Task 6: Check Node.js environment
echo "" | tee -a "$VERIFICATION_LOG"
echo "[TASK 6] Node.js Environment Check" | tee -a "$VERIFICATION_LOG"
echo "===================================" | tee -a "$VERIFICATION_LOG"

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✓ PASS: Node.js found - $NODE_VERSION" | tee -a "$VERIFICATION_LOG"
else
    echo "⚠ WARNING: Node.js not found in PATH" | tee -a "$VERIFICATION_LOG"
fi

if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "✓ PASS: npm found - $NPM_VERSION" | tee -a "$VERIFICATION_LOG"
else
    echo "⚠ WARNING: npm not found in PATH" | tee -a "$VERIFICATION_LOG"
fi

if [ -f "/c/Ziggie/control-center/frontend/package.json" ]; then
    echo "✓ PASS: package.json found" | tee -a "$VERIFICATION_LOG"
fi

# Task 7: Configuration validation
echo "" | tee -a "$VERIFICATION_LOG"
echo "[TASK 7] Configuration Files Validation" | tee -a "$VERIFICATION_LOG"
echo "========================================" | tee -a "$VERIFICATION_LOG"

if [ -f "/c/Ziggie/control-center/backend/config.py" ]; then
    echo "✓ PASS: Backend config.py found" | tee -a "$VERIFICATION_LOG"
    # Check for environment variables
    if grep -q "ZIGGIE_ROOT\|DATABASE_URL\|API_PORT" /c/Ziggie/control-center/backend/config.py; then
        echo "  ✓ Contains expected configuration variables" | tee -a "$VERIFICATION_LOG"
    fi
fi

# Task 8: Generate summary
echo "" | tee -a "$VERIFICATION_LOG"
echo "================================================================================" | tee -a "$VERIFICATION_LOG"
echo "VERIFICATION COMPLETE" | tee -a "$VERIFICATION_LOG"
echo "================================================================================" | tee -a "$VERIFICATION_LOG"
echo "Log saved to: $VERIFICATION_LOG" | tee -a "$VERIFICATION_LOG"
echo "" | tee -a "$VERIFICATION_LOG"

cat "$VERIFICATION_LOG"
