#!/bin/bash
# Ziggie GPU Instance Bootstrap Script
# Auto-installs ComfyUI for AI asset generation

set -e

# Log everything
exec > >(tee /var/log/ziggie-bootstrap.log) 2>&1

echo "=== Ziggie GPU Bootstrap Started at $(date) ==="

# Update system
apt-get update
apt-get upgrade -y

# Install required packages
apt-get install -y git python3-pip python3-venv

# Create ziggie user directory
mkdir -p /home/ubuntu/ziggie
cd /home/ubuntu/ziggie

# Clone ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install ComfyUI requirements
pip install -r requirements.txt

# Install additional nodes for game asset generation
cd custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Manager.git
cd ..

# Create systemd service for ComfyUI
cat > /etc/systemd/system/comfyui.service << 'EOF'
[Unit]
Description=ComfyUI Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ziggie/ComfyUI
ExecStart=/home/ubuntu/ziggie/ComfyUI/venv/bin/python main.py --listen 0.0.0.0 --port 8188
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Set ownership
chown -R ubuntu:ubuntu /home/ubuntu/ziggie

# Enable and start ComfyUI
systemctl daemon-reload
systemctl enable comfyui
systemctl start comfyui

# Tag instance as ready
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/region)

# Install AWS CLI if not present
if ! command -v aws &> /dev/null; then
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip -q awscliv2.zip
    ./aws/install
fi

# Tag instance as ready
aws ec2 create-tags --resources $INSTANCE_ID --tags Key=Status,Value=Ready --region $REGION || true

echo "=== Ziggie GPU Bootstrap Complete at $(date) ==="
echo "ComfyUI available at http://<public-ip>:8188"
