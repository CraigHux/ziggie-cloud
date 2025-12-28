#!/bin/bash
# migrate_all.sh - Bash version for Git Bash users
# Master migration script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}AI AGENT & CONTROL CENTER MIGRATION${NC}"
echo -e "${CYAN}C:\\meowping-rts → C:\\Ziggie${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Pre-flight checks
echo -e "${YELLOW}PRE-FLIGHT CHECKS${NC}"
echo "────────────────────────────────────────"

# Check if Ziggie exists
if [ ! -d "/c/Ziggie" ]; then
    echo -e "${RED}✗ C:\\Ziggie does not exist!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ C:\\Ziggie exists${NC}"

# Check source directories
if [ ! -d "/c/meowping-rts/ai-agents" ]; then
    echo -e "${RED}✗ Source ai-agents not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Source ai-agents found${NC}"

if [ ! -d "/c/meowping-rts/control-center" ]; then
    echo -e "${RED}✗ Source control-center not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Source control-center found${NC}"

# Check for running processes
echo ""
echo -e "${YELLOW}Checking for running services...${NC}"
if pgrep -x "python" > /dev/null || pgrep -x "node" > /dev/null; then
    echo -e "${RED}⚠ WARNING: Python or Node processes are running!${NC}"
    echo -e "${YELLOW}  Please stop Control Center services before continuing.${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
else
    echo -e "${GREEN}✓ No conflicting processes${NC}"
fi

echo ""
echo -e "${CYAN}========================================${NC}"
echo "Ready to migrate:"
echo "  • ai-agents (~22 MB, 54 files)"
echo "  • control-center (~500 MB, 1500+ files)"
echo ""
echo "This will:"
echo "  1. Create backup"
echo "  2. Copy files to C:\\Ziggie"
echo "  3. Update all hardcoded paths"
echo "  4. Verify migration"
echo -e "${CYAN}========================================${NC}"

echo ""
read -p "Proceed with migration? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Migration cancelled.${NC}"
    exit 0
fi

# Create timestamp
TIMESTAMP=$(date +"%Y-%m-%d_%H%M%S")
BACKUP_ROOT="/c/Backups/Migration_${TIMESTAMP}"

# Phase 1: Backup
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}PHASE 1: BACKUP${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

echo -e "${YELLOW}[1/5] Creating backup directory...${NC}"
mkdir -p "$BACKUP_ROOT"
echo -e "${GREEN}✓ Created: $BACKUP_ROOT${NC}"

echo -e "${YELLOW}[2/5] Backing up ai-agents (22 MB)...${NC}"
cp -r "/c/meowping-rts/ai-agents" "$BACKUP_ROOT/ai-agents"
echo -e "${GREEN}✓ ai-agents backed up${NC}"

echo -e "${YELLOW}[3/5] Backing up control-center (~500 MB, may take time)...${NC}"
cp -r "/c/meowping-rts/control-center" "$BACKUP_ROOT/control-center"
echo -e "${GREEN}✓ control-center backed up${NC}"

echo -e "${YELLOW}[4/5] Backing up Claude configurations...${NC}"
cp -r "/c/meowping-rts/.claude" "$BACKUP_ROOT/.claude-meowping"
cp -r "/c/ComfyUI/.claude" "$BACKUP_ROOT/.claude-comfyui"
echo -e "${GREEN}✓ Claude configs backed up${NC}"

echo -e "${YELLOW}[5/5] Creating manifest...${NC}"
FILES_COUNT=$(find "$BACKUP_ROOT" -type f | wc -l)
echo -e "${GREEN}✓ Backed up $FILES_COUNT files${NC}"

echo "$BACKUP_ROOT" > "/c/Ziggie/backup_location.txt"
echo -e "${GREEN}✓ Backup location saved${NC}"

# Phase 2: Copy
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}PHASE 2: COPY FILES${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

echo -e "${YELLOW}[1/3] Copying ai-agents...${NC}"
cp -r "/c/meowping-rts/ai-agents" "/c/Ziggie/ai-agents"
echo -e "${GREEN}✓ ai-agents copied${NC}"

echo -e "${YELLOW}[2/3] Copying control-center (large, please wait)...${NC}"
cp -r "/c/meowping-rts/control-center" "/c/Ziggie/control-center"
echo -e "${GREEN}✓ control-center copied${NC}"

echo -e "${YELLOW}[3/3] Copying Claude configuration...${NC}"
cp -r "/c/meowping-rts/.claude" "/c/Ziggie/.claude"
echo -e "${GREEN}✓ .claude copied${NC}"

# Phase 3: Update paths
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}PHASE 3: UPDATE PATHS${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

OLD_PATH_UNIX="C:/meowping-rts"
OLD_PATH_WIN="C:\\\\meowping-rts"
NEW_PATH_UNIX="C:/Ziggie"
NEW_PATH_WIN="C:\\\\Ziggie"

FILES_TO_UPDATE=(
    "/c/Ziggie/control-center/backend/config.py"
    "/c/Ziggie/control-center/backend/services/agent_loader.py"
    "/c/Ziggie/control-center/backend/services/kb_manager.py"
    "/c/Ziggie/control-center/backend/api/agents.py"
    "/c/Ziggie/control-center/backend/api/comfyui.py"
    "/c/Ziggie/control-center/backend/api/knowledge.py"
    "/c/Ziggie/control-center/backend/api/projects.py"
    "/c/Ziggie/ai-agents/knowledge-base/.env"
)

UPDATE_COUNT=0
for file in "${FILES_TO_UPDATE[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${YELLOW}Updating: $file${NC}"
        # Replace both path formats
        sed -i "s|$OLD_PATH_UNIX|$NEW_PATH_UNIX|g" "$file"
        sed -i "s|$OLD_PATH_WIN|$NEW_PATH_WIN|g" "$file"
        UPDATE_COUNT=$((UPDATE_COUNT + 1))
        echo -e "${GREEN}  ✓ Updated${NC}"
    else
        echo -e "${YELLOW}  ⚠ File not found: $file${NC}"
    fi
done

# Update test files
echo ""
echo -e "${YELLOW}Updating test files...${NC}"
find "/c/Ziggie/control-center/tests" -name "*.py" -type f | while read -r file; do
    sed -i "s|$OLD_PATH_UNIX|$NEW_PATH_UNIX|g" "$file"
    sed -i "s|$OLD_PATH_WIN|$NEW_PATH_WIN|g" "$file"
    UPDATE_COUNT=$((UPDATE_COUNT + 1))
    echo -e "${GREEN}  ✓ Updated: $(basename "$file")${NC}"
done

echo ""
echo -e "${GREEN}✓ Updated $UPDATE_COUNT files${NC}"

# Phase 4: Verify
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}PHASE 4: VERIFICATION${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

ISSUES=0

echo -e "${YELLOW}[1/4] Verifying directory structure...${NC}"
REQUIRED_DIRS=(
    "/c/Ziggie/ai-agents"
    "/c/Ziggie/ai-agents/knowledge-base"
    "/c/Ziggie/control-center"
    "/c/Ziggie/control-center/backend"
    "/c/Ziggie/control-center/frontend"
    "/c/Ziggie/.claude"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}  ✓ $dir${NC}"
    else
        echo -e "${RED}  ✗ MISSING: $dir${NC}"
        ISSUES=$((ISSUES + 1))
    fi
done

echo ""
echo -e "${YELLOW}[2/4] Verifying critical files...${NC}"
CRITICAL_FILES=(
    "/c/Ziggie/ai-agents/knowledge-base/manage.py"
    "/c/Ziggie/ai-agents/knowledge-base/.env"
    "/c/Ziggie/control-center/backend/main.py"
    "/c/Ziggie/control-center/backend/config.py"
    "/c/Ziggie/control-center/backend/control-center.db"
    "/c/Ziggie/control-center/frontend/package.json"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}  ✓ $file${NC}"
    else
        echo -e "${RED}  ✗ MISSING: $file${NC}"
        ISSUES=$((ISSUES + 1))
    fi
done

echo ""
echo -e "${YELLOW}[3/4] Checking for unreplaced old paths...${NC}"
if grep -q "C:/meowping-rts\|C:\\\\\\\\meowping-rts" "/c/Ziggie/control-center/backend/config.py" 2>/dev/null; then
    echo -e "${RED}  ✗ Old paths still found in config.py${NC}"
    ISSUES=$((ISSUES + 1))
else
    echo -e "${GREEN}  ✓ No old paths in config.py${NC}"
fi

echo ""
echo -e "${YELLOW}[4/4] Counting migrated files...${NC}"
AI_COUNT=$(find "/c/Ziggie/ai-agents" -type f | wc -l)
CC_COUNT=$(find "/c/Ziggie/control-center" -type f | wc -l)
echo "  AI Agents: $AI_COUNT files"
echo "  Control Center: $CC_COUNT files"

# Summary
echo ""
echo -e "${CYAN}========================================${NC}"
if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}MIGRATION COMPLETE!${NC}"
    echo -e "${GREEN}All checks passed successfully.${NC}"
else
    echo -e "${RED}MIGRATION COMPLETED WITH ISSUES!${NC}"
    echo -e "${RED}Found $ISSUES issues - please review.${NC}"
    echo -e "${YELLOW}You can rollback using: ./rollback.sh${NC}"
fi
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Test Control Center services"
echo "  2. Test Knowledge Base functionality"
echo "  3. Verify API endpoints"
echo "  4. Keep backup for at least 1 week"
echo ""
echo -e "${YELLOW}Backup location: $BACKUP_ROOT${NC}"
echo ""
