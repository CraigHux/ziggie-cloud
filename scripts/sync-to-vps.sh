#!/bin/bash
# =============================================================================
# ZIGGIE ASSET PIPELINE - Local to VPS Sync Script (Bash)
# =============================================================================
# Syncs pipeline scripts and configurations from local machine to VPS
# Works in Git Bash, WSL, or native Linux
#
# Usage:
#   ./sync-to-vps.sh                  # Sync all files
#   ./sync-to-vps.sh --scripts        # Sync scripts only
#   ./sync-to-vps.sh --workflows      # Sync n8n workflows only
#   ./sync-to-vps.sh --dry-run        # Show what would be synced
#   ./sync-to-vps.sh --restart        # Restart VPS services after sync
# =============================================================================

set -e

# Configuration
VPS_HOST="${VPS_HOST:-82.25.112.73}"
VPS_USER="${VPS_USER:-root}"
LOCAL_BASE="${LOCAL_BASE:-/c/Ziggie}"  # Git Bash path
VPS_BASE="/opt/ziggie"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Flags
SYNC_SCRIPTS=false
SYNC_WORKFLOWS=false
SYNC_CONFIGS=false
DRY_RUN=false
RESTART_SERVICES=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --scripts|-s)
            SYNC_SCRIPTS=true
            shift
            ;;
        --workflows|-w)
            SYNC_WORKFLOWS=true
            shift
            ;;
        --configs|-c)
            SYNC_CONFIGS=true
            shift
            ;;
        --dry-run|-n)
            DRY_RUN=true
            shift
            ;;
        --restart|-r)
            RESTART_SERVICES=true
            shift
            ;;
        --host)
            VPS_HOST="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --scripts, -s     Sync pipeline scripts only"
            echo "  --workflows, -w   Sync n8n workflows only"
            echo "  --configs, -c     Sync configuration files only"
            echo "  --dry-run, -n     Show what would be synced"
            echo "  --restart, -r     Restart VPS services after sync"
            echo "  --host HOST       VPS hostname (default: $VPS_HOST)"
            echo "  --help, -h        Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# If no category specified, sync all
if ! $SYNC_SCRIPTS && ! $SYNC_WORKFLOWS && ! $SYNC_CONFIGS; then
    SYNC_SCRIPTS=true
    SYNC_WORKFLOWS=true
    SYNC_CONFIGS=true
fi

# Detect Windows path format
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Git Bash or Cygwin - convert paths
    LOCAL_BASE="/c/Ziggie"
elif [[ -d "/mnt/c/Ziggie" ]]; then
    # WSL
    LOCAL_BASE="/mnt/c/Ziggie"
elif [[ -d "C:/Ziggie" ]]; then
    LOCAL_BASE="C:/Ziggie"
fi

echo ""
echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}  ZIGGIE PIPELINE - VPS SYNC${NC}"
echo -e "${BLUE}=============================================${NC}"
echo ""

echo "Configuration:"
echo "  VPS Host:    ${VPS_USER}@${VPS_HOST}"
echo "  Local Base:  $LOCAL_BASE"
echo "  VPS Base:    $VPS_BASE"
echo ""

if $DRY_RUN; then
    echo -e "${YELLOW}*** DRY RUN MODE - No changes will be made ***${NC}"
    echo ""
fi

# Test SSH connection
test_ssh() {
    echo -e "${BLUE}[INFO]${NC} Testing SSH connection..."
    if ssh -o ConnectTimeout=5 -o BatchMode=yes "${VPS_USER}@${VPS_HOST}" "echo connected" 2>/dev/null | grep -q "connected"; then
        echo -e "${GREEN}[OK]${NC} SSH connection successful"
        return 0
    else
        echo -e "${RED}[ERROR]${NC} SSH connection failed"
        echo ""
        echo "To set up SSH key authentication:"
        echo "  1. Generate key: ssh-keygen -t ed25519"
        echo "  2. Copy to VPS: ssh-copy-id ${VPS_USER}@${VPS_HOST}"
        return 1
    fi
}

# Sync a single file
sync_file() {
    local local_path="$1"
    local remote_path="$2"

    local full_local="${LOCAL_BASE}/${local_path}"
    local full_remote="${VPS_BASE}/${remote_path}"

    if [[ ! -f "$full_local" ]]; then
        echo -e "${YELLOW}[SKIP]${NC} $local_path (not found)"
        return 1
    fi

    if $DRY_RUN; then
        echo -e "${YELLOW}[DRY]${NC} Would sync: $local_path -> $full_remote"
        return 0
    fi

    # Create remote directory
    ssh "${VPS_USER}@${VPS_HOST}" "mkdir -p $(dirname $full_remote)" 2>/dev/null

    # Copy file
    if scp "$full_local" "${VPS_USER}@${VPS_HOST}:${full_remote}" 2>/dev/null; then
        echo -e "${GREEN}[OK]${NC} $local_path -> $full_remote"
        return 0
    else
        echo -e "${RED}[ERROR]${NC} Failed: $local_path"
        return 1
    fi
}

# Counters
SUCCESS=0
FAILED=0

# Test connection first
if ! test_ssh; then
    exit 1
fi

# Sync scripts
if $SYNC_SCRIPTS; then
    echo ""
    echo -e "${YELLOW}Syncing Pipeline Scripts...${NC}"

    for script in \
        "scripts/automated_pipeline.py:scripts/automated_pipeline.py" \
        "scripts/discord_bot.py:scripts/discord_bot.py" \
        "scripts/pipeline_notifications.py:scripts/pipeline_notifications.py" \
        "scripts/blender_8dir_render.py:scripts/blender_8dir_render.py" \
        "scripts/blender_thumbnail.py:scripts/blender_thumbnail.py" \
        "scripts/health_check.py:scripts/health_check.py"
    do
        local_path="${script%%:*}"
        remote_path="${script##*:}"
        if sync_file "$local_path" "$remote_path"; then
            ((SUCCESS++))
        else
            ((FAILED++))
        fi
    done
fi

# Sync workflows
if $SYNC_WORKFLOWS; then
    echo ""
    echo -e "${YELLOW}Syncing n8n Workflows...${NC}"

    for workflow in \
        "n8n-workflows/asset-pipeline-24-7.json:n8n-workflows/asset-pipeline-24-7.json"
    do
        local_path="${workflow%%:*}"
        remote_path="${workflow##*:}"
        if sync_file "$local_path" "$remote_path"; then
            ((SUCCESS++))
        else
            ((FAILED++))
        fi
    done
fi

# Sync configs
if $SYNC_CONFIGS; then
    echo ""
    echo -e "${YELLOW}Syncing Configuration Files...${NC}"

    for config in \
        "hostinger-vps/scripts/deploy-asset-pipeline.sh:deploy/deploy-asset-pipeline.sh"
    do
        local_path="${config%%:*}"
        remote_path="${config##*:}"
        if sync_file "$local_path" "$remote_path"; then
            ((SUCCESS++))
        else
            ((FAILED++))
        fi
    done
fi

# Summary
echo ""
echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}  SYNC SUMMARY${NC}"
echo -e "${BLUE}=============================================${NC}"
echo ""
echo -e "  Total synced:        ${GREEN}$SUCCESS${NC}"
echo -e "  Total skipped/failed: ${YELLOW}$FAILED${NC}"

# Restart services if requested
if $RESTART_SERVICES && [[ $SUCCESS -gt 0 || $DRY_RUN == true ]]; then
    echo ""
    echo -e "${YELLOW}Restarting VPS services...${NC}"

    if $DRY_RUN; then
        echo -e "${YELLOW}[DRY]${NC} Would restart ziggie-discord-bot"
    else
        if ssh "${VPS_USER}@${VPS_HOST}" "systemctl restart ziggie-discord-bot && systemctl is-active ziggie-discord-bot" | grep -q "active"; then
            echo -e "${GREEN}[OK]${NC} Discord bot service restarted"
        else
            echo -e "${RED}[ERROR]${NC} Service restart failed"
        fi
    fi
fi

# Show VPS status
echo ""
echo -e "${YELLOW}VPS Service Status...${NC}"

# Check Discord bot
status=$(ssh "${VPS_USER}@${VPS_HOST}" "systemctl is-active ziggie-discord-bot 2>/dev/null || echo 'not-found'")
case $status in
    active)    echo -e "${GREEN}[OK]${NC} ziggie-discord-bot is running" ;;
    inactive)  echo -e "${RED}[ERROR]${NC} ziggie-discord-bot is stopped" ;;
    not-found) echo -e "${YELLOW}[SKIP]${NC} ziggie-discord-bot not installed" ;;
    *)         echo -e "${BLUE}[INFO]${NC} ziggie-discord-bot: $status" ;;
esac

# Check Docker
status=$(ssh "${VPS_USER}@${VPS_HOST}" "systemctl is-active docker 2>/dev/null || echo 'not-found'")
case $status in
    active)    echo -e "${GREEN}[OK]${NC} docker is running" ;;
    inactive)  echo -e "${RED}[ERROR]${NC} docker is stopped" ;;
    not-found) echo -e "${YELLOW}[SKIP]${NC} docker not installed" ;;
    *)         echo -e "${BLUE}[INFO]${NC} docker: $status" ;;
esac

# Check n8n
n8n_status=$(ssh "${VPS_USER}@${VPS_HOST}" "curl -s -o /dev/null -w '%{http_code}' http://localhost:5678/healthz 2>/dev/null || echo 'failed'")
if [[ "$n8n_status" == "200" ]]; then
    echo -e "${GREEN}[OK]${NC} n8n is responding"
else
    echo -e "${RED}[ERROR]${NC} n8n not responding (status: $n8n_status)"
fi

echo ""
echo -e "${GREEN}Sync complete!${NC}"
echo ""

if ! $DRY_RUN && [[ $SUCCESS -gt 0 ]]; then
    echo "Next steps:"
    echo "  1. SSH to VPS: ssh ${VPS_USER}@${VPS_HOST}"
    echo "  2. Run deployment: /opt/ziggie/deploy/deploy-asset-pipeline.sh"
    echo "  3. Check logs: journalctl -u ziggie-discord-bot -f"
    echo ""
fi
