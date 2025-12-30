#!/bin/bash
# =============================================================================
# ZIGGIE ASSET PIPELINE - VPS Deployment Script
# =============================================================================
# This script deploys the 24/7 asset pipeline on Hostinger VPS
# Prerequisites: Docker stack already running (run deploy.sh first)
# Usage: ./deploy-asset-pipeline.sh
# =============================================================================

set -e  # Exit on error

echo "=============================================="
echo "  ZIGGIE ASSET PIPELINE - VPS DEPLOYMENT"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PIPELINE_DIR="/opt/ziggie/pipeline"
ASSETS_DIR="/opt/ziggie/assets"
SCRIPTS_DIR="/opt/ziggie/scripts"
LOGS_DIR="/opt/ziggie/logs"
CONFIGS_DIR="/opt/ziggie/configs"

# -----------------------------------------------------------------------------
# PHASE 1: System Dependencies
# -----------------------------------------------------------------------------
echo -e "\n${BLUE}[PHASE 1/6]${NC} ${YELLOW}Installing system dependencies...${NC}"

# Update system
sudo apt update

# Install Python 3.11
if ! command -v python3.11 &> /dev/null; then
    echo "Installing Python 3.11..."
    sudo apt install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install -y python3.11 python3.11-venv python3.11-dev
fi
echo -e "${GREEN}✓ Python 3.11 installed${NC}"

# Install Blender (headless)
if ! command -v blender &> /dev/null; then
    echo "Installing Blender..."
    sudo apt install -y blender
fi
BLENDER_VERSION=$(blender --version 2>/dev/null | head -1 || echo "Not installed")
echo -e "${GREEN}✓ Blender: ${BLENDER_VERSION}${NC}"

# Install additional tools
sudo apt install -y jq curl wget git

echo -e "${GREEN}Phase 1 complete${NC}"

# -----------------------------------------------------------------------------
# PHASE 2: Directory Structure
# -----------------------------------------------------------------------------
echo -e "\n${BLUE}[PHASE 2/6]${NC} ${YELLOW}Creating directory structure...${NC}"

# Create directories
mkdir -p ${PIPELINE_DIR}
mkdir -p ${SCRIPTS_DIR}
mkdir -p ${LOGS_DIR}
mkdir -p ${CONFIGS_DIR}
mkdir -p ${ASSETS_DIR}/{concepts,stage1_generated,stage2_nobg,stage3_upscaled}
mkdir -p ${ASSETS_DIR}/{stage4_3d,stage4_5_rigged,stage5_sprites,stage6_sheets,stage7_factions}
mkdir -p ${ASSETS_DIR}/queue

# Set permissions
chmod -R 755 /opt/ziggie

echo -e "${GREEN}✓ Directories created${NC}"
ls -la ${ASSETS_DIR}

# -----------------------------------------------------------------------------
# PHASE 3: Python Environment
# -----------------------------------------------------------------------------
echo -e "\n${BLUE}[PHASE 3/6]${NC} ${YELLOW}Setting up Python environment...${NC}"

# Create virtual environment
if [ ! -d "${PIPELINE_DIR}/venv" ]; then
    python3.11 -m venv ${PIPELINE_DIR}/venv
fi

# Activate and install dependencies
source ${PIPELINE_DIR}/venv/bin/activate

pip install --upgrade pip wheel setuptools

# Core dependencies
pip install \
    pillow \
    requests \
    aiohttp \
    python-dotenv \
    discord.py

# Optional: Tripo AI SDK for Stage 4.5
pip install tripo3d || echo "Note: tripo3d not installed (optional)"

# Gradio client for HuggingFace APIs
pip install gradio_client

# Verify installations
echo -e "\n${YELLOW}Python packages installed:${NC}"
python -c "import PIL; print(f'  Pillow: {PIL.__version__}')"
python -c "import discord; print(f'  discord.py: {discord.__version__}')"
python -c "import requests; print(f'  requests: {requests.__version__}')"

deactivate
echo -e "${GREEN}Phase 3 complete${NC}"

# -----------------------------------------------------------------------------
# PHASE 4: Deploy Pipeline Scripts
# -----------------------------------------------------------------------------
echo -e "\n${BLUE}[PHASE 4/6]${NC} ${YELLOW}Deploying pipeline scripts...${NC}"

# Check if scripts exist (should be copied from local)
REQUIRED_SCRIPTS=(
    "automated_pipeline.py"
    "discord_bot.py"
    "pipeline_notifications.py"
    "blender_8dir_render.py"
    "blender_thumbnail.py"
)

echo "Checking for required scripts in ${SCRIPTS_DIR}..."
for script in "${REQUIRED_SCRIPTS[@]}"; do
    if [ -f "${SCRIPTS_DIR}/${script}" ]; then
        echo -e "  ${GREEN}✓${NC} ${script}"
    else
        echo -e "  ${RED}✗${NC} ${script} - MISSING!"
        echo -e "${YELLOW}    Copy from local: scp C:/Ziggie/scripts/${script} root@VPS_IP:${SCRIPTS_DIR}/${NC}"
    fi
done

# Create VPS config overlay
cat > ${SCRIPTS_DIR}/vps_config.py << 'VPSCONFIG'
"""VPS-specific configuration overrides for automated_pipeline.py"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment from configs
load_dotenv('/opt/ziggie/configs/.env')

VPS_CONFIG = {
    "input_dir": "/opt/ziggie/assets/concepts",
    "output_dir": "/opt/ziggie/assets",
    "stage1_output": "/opt/ziggie/assets/stage1_generated",
    "stage2_output": "/opt/ziggie/assets/stage2_nobg",
    "stage3_output": "/opt/ziggie/assets/stage3_upscaled",
    "stage4_output": "/opt/ziggie/assets/stage4_3d",
    "stage4_5_output": "/opt/ziggie/assets/stage4_5_rigged",
    "stage5_output": "/opt/ziggie/assets/stage5_sprites",
    "stage6_output": "/opt/ziggie/assets/stage6_sheets",
    "stage7_output": "/opt/ziggie/assets/stage7_factions",

    # VPS Blender path
    "blender_path": "/usr/bin/blender",
    "blender_script": "/opt/ziggie/scripts/blender_8dir_render.py",

    # API Keys from environment
    "runpod_api_key": os.getenv("RUNPOD_API_KEY"),
    "meshy_api_key": os.getenv("MESHY_API_KEY"),
    "tripo_api_key": os.getenv("TRIPO_API_KEY"),
    "discord_webhook_url": os.getenv("DISCORD_WEBHOOK_URL"),
    "huggingface_token": os.getenv("HUGGINGFACE_TOKEN"),
}

def apply_vps_config(config_dict):
    """Overlay VPS config onto main CONFIG"""
    config_dict.update(VPS_CONFIG)
    return config_dict
VPSCONFIG

echo -e "${GREEN}Phase 4 complete${NC}"

# -----------------------------------------------------------------------------
# PHASE 5: Environment Configuration
# -----------------------------------------------------------------------------
echo -e "\n${BLUE}[PHASE 5/6]${NC} ${YELLOW}Setting up environment configuration...${NC}"

if [ ! -f "${CONFIGS_DIR}/.env" ]; then
    cat > ${CONFIGS_DIR}/.env << 'ENVTEMPLATE'
# =============================================================================
# Ziggie Asset Pipeline - VPS Environment Configuration
# =============================================================================

# RunPod Serverless (Stage 1: 2D Generation)
RUNPOD_API_KEY=CHANGE_ME

# Meshy.ai (Stage 4: 2D to 3D)
MESHY_API_KEY=CHANGE_ME

# HuggingFace (Stage 2: Background Removal)
HUGGINGFACE_TOKEN=

# Tripo AI (Stage 4.5: Auto-Rigging - Optional)
TRIPO_API_KEY=

# Discord Bot
DISCORD_BOT_TOKEN=CHANGE_ME
DISCORD_APPROVAL_CHANNEL_ID=CHANGE_ME
DISCORD_WEBHOOK_URL=CHANGE_ME

# n8n Webhooks
N8N_WEBHOOK_URL=https://ziggie.cloud/n8n/webhook/pipeline-approval
N8N_BASE_URL=https://ziggie.cloud/n8n
ENVTEMPLATE

    echo -e "${YELLOW}Environment file created at ${CONFIGS_DIR}/.env${NC}"
    echo -e "${RED}IMPORTANT: Edit this file with your actual API keys!${NC}"
    echo "  nano ${CONFIGS_DIR}/.env"
else
    echo -e "${GREEN}✓ Environment file exists${NC}"
fi

# Secure the file
chmod 600 ${CONFIGS_DIR}/.env

echo -e "${GREEN}Phase 5 complete${NC}"

# -----------------------------------------------------------------------------
# PHASE 6: Discord Bot Service
# -----------------------------------------------------------------------------
echo -e "\n${BLUE}[PHASE 6/6]${NC} ${YELLOW}Setting up Discord bot service...${NC}"

# Create systemd service
cat > /etc/systemd/system/ziggie-discord-bot.service << 'SERVICEDEF'
[Unit]
Description=Ziggie Discord Approval Bot
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ziggie/scripts
Environment="PATH=/opt/ziggie/pipeline/venv/bin:/usr/local/bin:/usr/bin"
EnvironmentFile=/opt/ziggie/configs/.env
ExecStart=/opt/ziggie/pipeline/venv/bin/python discord_bot.py
Restart=always
RestartSec=10
StandardOutput=append:/opt/ziggie/logs/discord_bot.log
StandardError=append:/opt/ziggie/logs/discord_bot_error.log

[Install]
WantedBy=multi-user.target
SERVICEDEF

# Reload systemd
systemctl daemon-reload

# Check if scripts exist before enabling
if [ -f "${SCRIPTS_DIR}/discord_bot.py" ]; then
    systemctl enable ziggie-discord-bot
    systemctl start ziggie-discord-bot

    sleep 3
    STATUS=$(systemctl is-active ziggie-discord-bot)
    if [ "$STATUS" == "active" ]; then
        echo -e "${GREEN}✓ Discord bot service is running${NC}"
    else
        echo -e "${RED}✗ Discord bot service failed to start${NC}"
        echo "  Check logs: journalctl -u ziggie-discord-bot -n 50"
    fi
else
    echo -e "${YELLOW}Discord bot service created but not started (script missing)${NC}"
fi

echo -e "${GREEN}Phase 6 complete${NC}"

# -----------------------------------------------------------------------------
# SUMMARY
# -----------------------------------------------------------------------------
echo ""
echo -e "${GREEN}=============================================="
echo "  ASSET PIPELINE DEPLOYMENT COMPLETE!"
echo "==============================================${NC}"
echo ""
echo "Directory structure:"
echo "  Scripts:  ${SCRIPTS_DIR}"
echo "  Assets:   ${ASSETS_DIR}"
echo "  Logs:     ${LOGS_DIR}"
echo "  Configs:  ${CONFIGS_DIR}"
echo ""
echo "Services:"
echo "  Discord Bot: systemctl status ziggie-discord-bot"
echo ""
echo "Next steps:"
echo "  1. Edit environment file: nano ${CONFIGS_DIR}/.env"
echo "  2. Copy pipeline scripts from local machine"
echo "  3. Test Discord bot: journalctl -u ziggie-discord-bot -f"
echo "  4. Configure n8n workflows for automation"
echo ""
echo "Quick test:"
echo "  source ${PIPELINE_DIR}/venv/bin/activate"
echo "  cd ${SCRIPTS_DIR}"
echo "  python -c \"from PIL import Image; print('PIL OK')\""
echo ""
