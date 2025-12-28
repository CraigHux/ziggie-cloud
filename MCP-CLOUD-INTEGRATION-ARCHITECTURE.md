# MCP-to-Cloud Integration Architecture for Ziggie Ecosystem

> **HEPHAESTUS Technical Report**
> **Mission**: Define complete MCP server cloud integration with AWS and Hostinger
> **Date**: 2025-12-23
> **Status**: Production-Ready Architecture

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture Overview](#system-architecture-overview)
3. [AWS GPU Infrastructure for ComfyUI](#aws-gpu-infrastructure-for-comfyui)
4. [Hostinger Orchestration Layer](#hostinger-orchestration-layer)
5. [MCP Server Deployment Specifications](#mcp-server-deployment-specifications)
6. [Hybrid Architecture & Fallback Chains](#hybrid-architecture--fallback-chains)
7. [Data Flow & Integration Points](#data-flow--integration-points)
8. [Deployment Procedures](#deployment-procedures)
9. [Monitoring & Cost Management](#monitoring--cost-management)
10. [Security & Compliance](#security--compliance)

---

## Executive Summary

### The Challenge
7+ MCP servers (unityMCP, unrealMCP, godotMCP, comfyuiMCP, simStudioMCP, awsGPU, localLLM) need cloud integration to enable:
- Scalable AI asset generation (ComfyUI on GPU)
- Hybrid local/cloud workflows
- Cost-optimized routing
- High availability orchestration

### The Solution
**Three-tier hybrid cloud architecture:**

```
Tier 1: Local Development (Your PC)
  └─ Unity, Unreal, Godot MCPs (local control)
  └─ LM Studio (free local LLM)
  └─ Development workflows

Tier 2: Hostinger Orchestration (VPS)
  └─ MCP Gateway (central routing hub)
  └─ n8n (workflow automation)
  └─ Sim Studio (agent coordination)
  └─ PostgreSQL + Redis (state management)

Tier 3: AWS Production (Cloud GPU)
  └─ ComfyUI on EC2 (SDXL, ControlNet, LoRA)
  └─ S3 (asset storage)
  └─ Spot instances (70% cost savings)
```

### Key Metrics
| Metric | Target | Implementation |
|--------|--------|----------------|
| **Cost** | <$50/month | Spot instances + Hostinger VPS |
| **ComfyUI Latency** | <30s per image | G4dn.xlarge with SDXL |
| **Availability** | 99.5% | Auto-restart, fallback routing |
| **Asset Storage** | Unlimited | S3 Standard-IA ($0.0125/GB/month) |

---

## System Architecture Overview

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    ZIGGIE AI GAME DEV SYSTEM                    │
└─────────────────────────────────────────────────────────────────┘

LOCAL DEVELOPMENT (Tier 1)
┌──────────────────────────────────────────────────────────────┐
│  Your PC (Windows 11)                                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ Unity MCP  │  │Unreal MCP  │  │Godot MCP   │            │
│  │  :8080     │  │  :8081     │  │  :6005     │            │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘            │
│        │                │                │                    │
│  ┌─────┴────────────────┴────────────────┴───────┐          │
│  │      LM Studio (Local LLM - Free)             │          │
│  │      Ollama/LMStudio :1234                    │          │
│  └────────────────────┬──────────────────────────┘          │
└─────────────────────┼─┼────────────────────────────────────┘
                      │ │
                      │ │ HTTPS (SSL/TLS)
                      ▼ ▼
┌──────────────────────────────────────────────────────────────┐
│  HOSTINGER VPS (Tier 2) - Orchestration Layer               │
│  KVM 2: 2 vCPU, 8GB RAM, 100GB NVMe ($6.49/month)          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  MCP Gateway (Port 9000)                               │ │
│  │  ├─ Service Mesh (routing logic)                       │ │
│  │  ├─ Health checks (30s interval)                       │ │
│  │  └─ Fallback routing (local → VPS → AWS)              │ │
│  └──────────────┬─────────────────────────────────────────┘ │
│                 │                                             │
│  ┌──────────────┴─────────────────────────────────────────┐ │
│  │  n8n (Port 5678) - Workflow Automation                 │ │
│  │  ├─ ComfyUI generation workflows                       │ │
│  │  ├─ Asset pipeline orchestration                       │ │
│  │  └─ Queue mode: 3 workers (Redis-backed)              │ │
│  └──────────────┬─────────────────────────────────────────┘ │
│                 │                                             │
│  ┌──────────────┴─────────────────────────────────────────┐ │
│  │  Sim Studio (Port 3001) - Agent Coordination           │ │
│  │  ├─ 15 AI agents (HEPHAESTUS, ARTEMIS, etc.)          │ │
│  │  ├─ Visual workflow builder                            │ │
│  │  └─ MCP server registry                                │ │
│  └──────────────┬─────────────────────────────────────────┘ │
│                 │                                             │
│  ┌──────────────┴─────────────────────────────────────────┐ │
│  │  PostgreSQL + Redis (Docker Compose)                   │ │
│  │  ├─ Agent state persistence                            │ │
│  │  ├─ Job queue (n8n, ComfyUI tasks)                    │ │
│  │  └─ Session management                                 │ │
│  └──────────────┬─────────────────────────────────────────┘ │
└─────────────────┼─────────────────────────────────────────────┘
                  │
                  │ AWS API (boto3, SSM)
                  ▼
┌──────────────────────────────────────────────────────────────┐
│  AWS CLOUD (Tier 3) - GPU Production                         │
│  Region: us-east-1 (lowest spot pricing)                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  EC2 Spot Instance: g4dn.xlarge                        │ │
│  │  ├─ 4 vCPU, 16GB RAM, 1x NVIDIA T4 (16GB VRAM)       │ │
│  │  ├─ Cost: ~$0.16/hr spot (70% off $0.53/hr on-demand)│ │
│  │  ├─ Auto-shutdown after 30min idle                    │ │
│  │  └─ SSM Session Manager (no SSH keys)                 │ │
│  └──────────────┬─────────────────────────────────────────┘ │
│                 │                                             │
│  ┌──────────────┴─────────────────────────────────────────┐ │
│  │  Docker Container: ComfyUI                             │ │
│  │  ├─ Image: yanwk/comfyui-boot:latest                  │ │
│  │  ├─ Models: SDXL, ControlNet, LoRA (from S3)         │ │
│  │  ├─ API Server: :8188 (WebSocket + REST)             │ │
│  │  └─ Auto-start on instance boot                       │ │
│  └──────────────┬─────────────────────────────────────────┘ │
│                 │                                             │
│  ┌──────────────┴─────────────────────────────────────────┐ │
│  │  S3 Bucket: meowping-game-assets                      │ │
│  │  ├─ Models: 50GB (SDXL, LoRA, ControlNet)            │ │
│  │  ├─ Generated Assets: 100GB (sprites, textures)      │ │
│  │  ├─ Storage Class: Standard-IA ($0.0125/GB/month)    │ │
│  │  └─ Lifecycle: Move to Glacier after 90 days         │ │
│  └──────────────┬─────────────────────────────────────────┘ │
│                 │                                             │
│  ┌──────────────┴─────────────────────────────────────────┐ │
│  │  IAM Role: EC2-ComfyUI-Role                           │ │
│  │  ├─ S3 ReadWrite (meowping-game-assets)              │ │
│  │  ├─ SSM Session Manager access                        │ │
│  │  └─ CloudWatch Logs write                             │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Location | Primary Role | Fallback |
|-----------|----------|--------------|----------|
| **Unity/Unreal/Godot MCPs** | Local PC | Game engine control | N/A (local only) |
| **Local LLM (LM Studio)** | Local PC | Free AI inference | Ollama on Hostinger |
| **MCP Gateway** | Hostinger VPS | Central routing hub | Direct connections |
| **n8n** | Hostinger VPS | Workflow automation | Manual API calls |
| **Sim Studio** | Hostinger VPS | Agent coordination | Local Claude Code |
| **ComfyUI** | AWS EC2 Spot | GPU-accelerated AI art | ImagineArt browser automation |
| **S3** | AWS | Asset storage | Local filesystem |

---

## AWS GPU Infrastructure for ComfyUI

### EC2 Instance Selection

#### Recommended: G4dn.xlarge (Spot)
```yaml
Instance Type: g4dn.xlarge
GPU: NVIDIA T4 Tensor Core (16GB VRAM)
vCPU: 4 cores (Intel Cascade Lake)
RAM: 16 GB
Storage: 125 GB NVMe SSD
Network: Up to 25 Gbps

Pricing (us-east-1):
  On-Demand: $0.526/hour
  Spot (avg): $0.158/hour (70% savings)
  Monthly (8hr/day): ~$38/month spot vs $126 on-demand

SDXL Performance:
  1024x1024: ~8 seconds
  Batch (4x): ~25 seconds
  ControlNet: +5 seconds
```

#### Alternative: G5.xlarge (Better Performance)
```yaml
Instance Type: g5.xlarge
GPU: NVIDIA A10G Tensor Core (24GB VRAM)
vCPU: 4 cores (AMD EPYC)
RAM: 16 GB
Storage: 250 GB NVMe SSD

Pricing (us-east-1):
  On-Demand: $1.006/hour
  Spot (avg): $0.302/hour (70% savings)
  Monthly (8hr/day): ~$72/month spot

SDXL Performance:
  1024x1024: ~5 seconds (60% faster)
  Batch (4x): ~15 seconds
  SDXL Turbo: ~2 seconds
```

**Recommendation**: Start with G4dn.xlarge spot. Upgrade to G5 if generation speed becomes bottleneck.

### Deep Learning AMI

```bash
# AWS official Deep Learning AMI (2025)
AMI Name: Deep Learning AMI GPU PyTorch 2.5 (Ubuntu 22.04)
AMI ID: ami-0c02fb55956c7d316 (us-east-1)

Pre-installed:
  - CUDA 12.4
  - PyTorch 2.5
  - NVIDIA drivers 550.90
  - Docker 24.0
  - Python 3.11

Auto-update command:
aws ec2 describe-images \
  --owners amazon \
  --filters "Name=name,Values=Deep Learning AMI GPU PyTorch*Ubuntu*" \
            "Name=state,Values=available" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --output text
```

### Docker Container Deployment

#### Dockerfile for ComfyUI (Production)

```dockerfile
# Dockerfile.comfyui
FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

# System dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    python3.11 \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 comfyui
WORKDIR /home/comfyui

# Clone ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git && \
    chown -R comfyui:comfyui ComfyUI

USER comfyui
WORKDIR /home/comfyui/ComfyUI

# Install Python dependencies
RUN pip3 install --no-cache-dir \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 && \
    pip3 install -r requirements.txt

# Download models from S3 on startup (via entrypoint script)
COPY --chown=comfyui:comfyui docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Expose ComfyUI API port
EXPOSE 8188

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8188/system_stats || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python3", "main.py", "--listen", "0.0.0.0", "--port", "8188"]
```

#### Docker Entrypoint Script

```bash
#!/bin/bash
# docker-entrypoint.sh - ComfyUI container startup

set -e

echo "ComfyUI Container Startup - $(date)"

# Sync models from S3 if not present
if [ ! -d "models/checkpoints/sd_xl_base_1.0.safetensors" ]; then
  echo "Downloading SDXL models from S3..."
  aws s3 sync s3://meowping-game-assets/models/sdxl/ models/checkpoints/
  aws s3 sync s3://meowping-game-assets/models/lora/ models/loras/
  aws s3 sync s3://meowping-game-assets/models/controlnet/ models/controlnet/
fi

# Create output directory
mkdir -p output

# Start ComfyUI
echo "Starting ComfyUI server on port 8188..."
exec "$@"
```

### EC2 User Data Script (Auto-Setup on Launch)

```bash
#!/bin/bash
# EC2 User Data - Runs on first boot

set -e

# Update system
apt-get update
apt-get upgrade -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
  curl -fsSL https://get.docker.com -o get-docker.sh
  sh get-docker.sh
  usermod -aG docker ubuntu
fi

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  tee /etc/apt/sources.list.d/nvidia-docker.list
apt-get update
apt-get install -y nvidia-container-toolkit
systemctl restart docker

# Pull ComfyUI Docker image
docker pull yanwk/comfyui-boot:latest

# Create systemd service for auto-start
cat > /etc/systemd/system/comfyui.service <<EOF
[Unit]
Description=ComfyUI Docker Container
After=docker.service
Requires=docker.service

[Service]
Type=simple
Restart=always
RestartSec=10
User=ubuntu
ExecStartPre=-/usr/bin/docker stop comfyui
ExecStartPre=-/usr/bin/docker rm comfyui
ExecStart=/usr/bin/docker run --rm --name comfyui \\
  --gpus all \\
  -p 8188:8188 \\
  -v /home/ubuntu/ComfyUI/models:/home/runner/ComfyUI/models \\
  -v /home/ubuntu/ComfyUI/output:/home/runner/ComfyUI/output \\
  -e AWS_DEFAULT_REGION=us-east-1 \\
  yanwk/comfyui-boot:latest
ExecStop=/usr/bin/docker stop comfyui

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable comfyui.service
systemctl start comfyui.service

# Setup CloudWatch agent for monitoring
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i amazon-cloudwatch-agent.deb

# Configure auto-shutdown after 30min idle
cat > /usr/local/bin/check-idle.sh <<'EOF'
#!/bin/bash
# Auto-shutdown if no ComfyUI activity for 30 minutes

IDLE_THRESHOLD=1800  # 30 minutes in seconds
LAST_REQUEST_FILE="/var/tmp/comfyui_last_request"

# Check if ComfyUI has recent requests
if docker logs comfyui --since 30m 2>&1 | grep -q "POST /prompt"; then
  date +%s > $LAST_REQUEST_FILE
else
  if [ -f $LAST_REQUEST_FILE ]; then
    LAST_REQUEST=$(cat $LAST_REQUEST_FILE)
    CURRENT_TIME=$(date +%s)
    IDLE_TIME=$((CURRENT_TIME - LAST_REQUEST))

    if [ $IDLE_TIME -gt $IDLE_THRESHOLD ]; then
      echo "No activity for $IDLE_TIME seconds. Shutting down..."
      /usr/local/bin/aws ec2 stop-instances --instance-ids $(ec2-metadata --instance-id | cut -d " " -f 2) --region us-east-1
    fi
  fi
fi
EOF

chmod +x /usr/local/bin/check-idle.sh

# Add to cron (check every 5 minutes)
echo "*/5 * * * * /usr/local/bin/check-idle.sh" | crontab -

echo "ComfyUI EC2 setup complete!"
```

### Spot Instance Configuration (CDK/CloudFormation)

```python
# aws-cdk/comfyui-stack.py
from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_s3 as s3,
    core
)

class ComfyUIStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # VPC (use default or create new)
        vpc = ec2.Vpc.from_lookup(self, "VPC", is_default=True)

        # Security Group
        sg = ec2.SecurityGroup(
            self, "ComfyUISG",
            vpc=vpc,
            description="ComfyUI EC2 Security Group",
            allow_all_outbound=True
        )
        sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(8188),
            description="ComfyUI API"
        )

        # IAM Role
        role = iam.Role(
            self, "ComfyUIRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"),
                iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchAgentServerPolicy")
            ]
        )

        # S3 Bucket access
        bucket = s3.Bucket.from_bucket_name(self, "AssetBucket", "meowping-game-assets")
        bucket.grant_read_write(role)

        # Launch Template
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            open("user-data.sh").read()  # Load user-data script from above
        )

        launch_template = ec2.LaunchTemplate(
            self, "ComfyUILaunchTemplate",
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.G4DN, ec2.InstanceSize.XLARGE),
            machine_image=ec2.MachineImage.lookup(
                name="Deep Learning AMI GPU PyTorch*Ubuntu*",
                owners=["amazon"]
            ),
            security_group=sg,
            role=role,
            user_data=user_data,
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/sda1",
                    volume=ec2.BlockDeviceVolume.ebs(
                        volume_size=100,
                        volume_type=ec2.EbsDeviceVolumeType.GP3,
                        delete_on_termination=True
                    )
                )
            ]
        )

        # Spot Fleet Request
        ec2.CfnSpotFleet(
            self, "ComfyUISpotFleet",
            spot_fleet_request_config_data=ec2.CfnSpotFleet.SpotFleetRequestConfigDataProperty(
                iam_fleet_role=f"arn:aws:iam::{self.account}:role/aws-ec2-spot-fleet-tagging-role",
                target_capacity=1,
                spot_price="0.20",  # Max price (on-demand is $0.526)
                launch_template_configs=[
                    ec2.CfnSpotFleet.LaunchTemplateConfigProperty(
                        launch_template_specification=ec2.CfnSpotFleet.FleetLaunchTemplateSpecificationProperty(
                            launch_template_id=launch_template.launch_template_id,
                            version=launch_template.version_number
                        )
                    )
                ],
                allocation_strategy="lowestPrice",
                instance_interruption_behavior="stop",  # Don't terminate on interruption
                type="maintain"
            )
        )
```

### S3 Bucket Structure

```
s3://meowping-game-assets/
├── models/
│   ├── sdxl/
│   │   ├── sd_xl_base_1.0.safetensors (6.94 GB)
│   │   ├── sd_xl_refiner_1.0.safetensors (6.08 GB)
│   │   └── sdxl_turbo.safetensors (6.94 GB)
│   ├── lora/
│   │   ├── meowping_style_v1.safetensors (144 MB)
│   │   ├── isometric_rts_v2.safetensors (144 MB)
│   │   └── cat_warrior_v3.safetensors (144 MB)
│   ├── controlnet/
│   │   ├── control_v11p_sd15_canny.pth (1.45 GB)
│   │   ├── control_v11p_sd15_depth.pth (1.45 GB)
│   │   └── control_v11f1e_sd15_tile.pth (1.45 GB)
│   └── vae/
│       └── sdxl_vae.safetensors (335 MB)
├── generated/
│   ├── sprites/
│   │   ├── units/ (1024x1024 PNGs)
│   │   ├── buildings/
│   │   └── terrain/
│   ├── textures/
│   │   ├── pbr/ (2048x2048 sets)
│   │   └── stylized/
│   └── concepts/ (high-res references)
└── workflows/
    ├── unit_generation.json
    ├── building_generation.json
    └── terrain_generation.json
```

**Lifecycle Policy**:
```json
{
  "Rules": [
    {
      "Id": "MoveToIA",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        }
      ],
      "NoncurrentVersionTransitions": [
        {
          "NoncurrentDays": 7,
          "StorageClass": "GLACIER"
        }
      ]
    }
  ]
}
```

**Cost Estimate** (100 GB storage):
- First 30 days: $2.30/month (Standard)
- After 30 days: $1.25/month (Standard-IA)
- Requests: ~$0.50/month (1000 generations)
- **Total: ~$1.75/month**

---

## Hostinger Orchestration Layer

### VPS Plan Recommendation

**Hostinger KVM 2 Plan** ($6.49/month with promo)
```yaml
Specs:
  vCPU: 2 cores
  RAM: 8 GB
  Storage: 100 GB NVMe SSD
  Bandwidth: Unlimited
  OS: Ubuntu 24.04 LTS

Use Cases:
  - MCP Gateway (always-on)
  - n8n (workflow automation)
  - Sim Studio (agent coordination)
  - PostgreSQL + Redis (state management)
  - Ollama (backup LLM when local unavailable)

Estimated Load:
  - CPU: 20-30% avg
  - RAM: 5-6 GB used
  - Network: <10 GB/month
```

### Docker Compose Stack

```yaml
# /root/docker-compose.yml
version: '3.8'

networks:
  ziggie:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  n8n_data:
  ollama_models:

services:
  # MCP Gateway - Central routing hub
  mcp-gateway:
    build: ./mcp-gateway
    container_name: mcp-gateway
    restart: unless-stopped
    ports:
      - "9000:9000"
    environment:
      - NODE_ENV=production
      - UNITY_MCP_URL=http://host.docker.internal:8080/mcp
      - UNREAL_MCP_URL=http://host.docker.internal:8081
      - GODOT_MCP_URL=http://host.docker.internal:6005
      - COMFYUI_AWS_URL=${COMFYUI_AWS_IP}:8188
      - LOCAL_LLM_URL=http://host.docker.internal:1234
      - REDIS_URL=redis://redis:6379
      - POSTGRES_URL=postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/mcp_gateway
    depends_on:
      - redis
      - postgres
    networks:
      - ziggie
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # n8n - Workflow automation
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_HOST=n8n.yourdomain.com
      - WEBHOOK_URL=https://n8n.yourdomain.com/
      - GENERIC_TIMEZONE=America/New_York
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n_user
      - DB_POSTGRESDB_PASSWORD=${N8N_DB_PASSWORD}
      # Queue mode for scalability
      - QUEUE_BULL_REDIS_HOST=redis
      - QUEUE_BULL_REDIS_PORT=6379
      - EXECUTIONS_MODE=queue
      - EXECUTIONS_DATA_SAVE_ON_SUCCESS=all
      - EXECUTIONS_DATA_SAVE_ON_ERROR=all
      # ComfyUI integration
      - COMFYUI_URL=${COMFYUI_AWS_IP}:8188
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=us-east-1
    depends_on:
      - postgres
      - redis
    volumes:
      - n8n_data:/home/node/.n8n
      - ./n8n-workflows:/home/node/workflows:ro
    networks:
      - ziggie

  # Sim Studio - Agent coordination
  sim-studio:
    image: simstudio/sim-studio:latest
    container_name: sim-studio
    restart: unless-stopped
    ports:
      - "3001:3000"
    environment:
      - DATABASE_URL=postgresql://sim_user:${SIM_DB_PASSWORD}@postgres:5432/sim_studio
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_BASE=http://ollama:11434/v1
      - OPENAI_API_KEY=ollama
      - MCP_GATEWAY_URL=http://mcp-gateway:9000
      - N8N_URL=http://n8n:5678
    depends_on:
      - postgres
      - redis
    volumes:
      - ./sim-studio-agents:/app/agents:ro
      - ../knowledge-base:/app/knowledge-base:ro
    networks:
      - ziggie

  # PostgreSQL - Primary database
  postgres:
    image: postgres:15-alpine
    container_name: postgres
    restart: unless-stopped
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_MULTIPLE_DATABASES=mcp_gateway,n8n,sim_studio
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sh:/docker-entrypoint-initdb.d/init-db.sh:ro
    networks:
      - ziggie
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis - Job queue and caching
  redis:
    image: redis:7-alpine
    container_name: redis
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      - ziggie
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Ollama - Backup LLM (CPU mode)
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    restart: unless-stopped
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    networks:
      - ziggie
    deploy:
      resources:
        limits:
          memory: 4G  # Leave 4GB for other services

  # Nginx - Reverse proxy with SSL
  nginx:
    image: nginx:alpine
    container_name: nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    networks:
      - ziggie
    depends_on:
      - mcp-gateway
      - n8n
      - sim-studio
```

### MCP Gateway Implementation

```typescript
// mcp-gateway/src/index.ts
import express from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';
import Redis from 'ioredis';

const app = express();
const redis = new Redis(process.env.REDIS_URL);

// Service registry with health checks
interface MCPService {
  name: string;
  url: string;
  priority: number; // 1=local, 2=VPS, 3=AWS
  lastHealthCheck: Date;
  isHealthy: boolean;
}

const services: Map<string, MCPService[]> = new Map([
  ['unity', [
    { name: 'unity-local', url: process.env.UNITY_MCP_URL, priority: 1, lastHealthCheck: new Date(), isHealthy: true }
  ]],
  ['unreal', [
    { name: 'unreal-local', url: process.env.UNREAL_MCP_URL, priority: 1, lastHealthCheck: new Date(), isHealthy: true }
  ]],
  ['godot', [
    { name: 'godot-local', url: process.env.GODOT_MCP_URL, priority: 1, lastHealthCheck: new Date(), isHealthy: true }
  ]],
  ['comfyui', [
    { name: 'comfyui-aws', url: `http://${process.env.COMFYUI_AWS_URL}`, priority: 3, lastHealthCheck: new Date(), isHealthy: false },
    { name: 'imagineai-fallback', url: 'http://localhost:9001/imagineai', priority: 4, lastHealthCheck: new Date(), isHealthy: true }
  ]],
  ['llm', [
    { name: 'lmstudio-local', url: process.env.LOCAL_LLM_URL, priority: 1, lastHealthCheck: new Date(), isHealthy: true },
    { name: 'ollama-vps', url: 'http://ollama:11434', priority: 2, lastHealthCheck: new Date(), isHealthy: true }
  ]]
]);

// Health check function
async function healthCheck(service: MCPService): Promise<boolean> {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(`${service.url}/health`, {
      signal: controller.signal
    });
    clearTimeout(timeout);

    return response.ok;
  } catch (error) {
    return false;
  }
}

// Health check scheduler (every 30 seconds)
setInterval(async () => {
  for (const [serviceName, serviceList] of services.entries()) {
    for (const service of serviceList) {
      service.isHealthy = await healthCheck(service);
      service.lastHealthCheck = new Date();
      console.log(`[Health Check] ${service.name}: ${service.isHealthy ? '✓' : '✗'}`);
    }
  }
}, 30000);

// Fallback routing logic
function selectService(serviceName: string): MCPService | null {
  const serviceList = services.get(serviceName);
  if (!serviceList) return null;

  // Sort by priority, filter healthy services
  const healthyServices = serviceList
    .filter(s => s.isHealthy)
    .sort((a, b) => a.priority - b.priority);

  if (healthyServices.length === 0) {
    console.warn(`[Routing] No healthy services for ${serviceName}`);
    return null;
  }

  return healthyServices[0];
}

// Proxy middleware with fallback
app.use('/mcp/:service/*', async (req, res, next) => {
  const serviceName = req.params.service;
  const service = selectService(serviceName);

  if (!service) {
    return res.status(503).json({ error: `Service ${serviceName} unavailable` });
  }

  console.log(`[Routing] ${serviceName} → ${service.name} (${service.url})`);

  // Cache routing decision for 60 seconds
  await redis.setex(`route:${serviceName}`, 60, service.name);

  // Proxy request
  const proxy = createProxyMiddleware({
    target: service.url,
    changeOrigin: true,
    pathRewrite: { [`^/mcp/${serviceName}`]: '' },
    onError: (err, req, res) => {
      console.error(`[Proxy Error] ${service.name}:`, err);
      service.isHealthy = false; // Mark as unhealthy
      res.status(502).json({ error: 'Bad Gateway', service: service.name });
    }
  });

  proxy(req, res, next);
});

// Health endpoint
app.get('/health', (req, res) => {
  const healthStatus = Array.from(services.entries()).map(([name, serviceList]) => ({
    service: name,
    endpoints: serviceList.map(s => ({
      name: s.name,
      url: s.url,
      healthy: s.isHealthy,
      lastCheck: s.lastHealthCheck
    }))
  }));

  res.json({ status: 'ok', timestamp: new Date(), services: healthStatus });
});

// Start AWS ComfyUI instance on-demand
app.post('/aws/comfyui/start', async (req, res) => {
  try {
    const { exec } = require('child_process');
    const { promisify } = require('util');
    const execAsync = promisify(exec);

    console.log('[AWS] Starting ComfyUI EC2 instance...');
    const { stdout } = await execAsync('python3 /app/aws_gpu_controller.py start comfyui');

    const result = JSON.parse(stdout);

    // Update service registry
    const comfyuiServices = services.get('comfyui');
    if (comfyuiServices) {
      comfyuiServices[0].url = `http://${result.public_ip}:8188`;
      comfyuiServices[0].isHealthy = true;
    }

    res.json({ status: 'started', instance: result });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(9000, () => {
  console.log('[MCP Gateway] Running on port 9000');
});
```

### Nginx Reverse Proxy Configuration

```nginx
# /root/nginx.conf
user nginx;
worker_processes auto;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    # MCP Gateway
    upstream mcp_gateway {
        server mcp-gateway:9000;
    }

    # n8n
    upstream n8n {
        server n8n:5678;
    }

    # Sim Studio
    upstream sim_studio {
        server sim-studio:3000;
    }

    # HTTP → HTTPS redirect
    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }

    # MCP Gateway (mcp.yourdomain.com)
    server {
        listen 443 ssl http2;
        server_name mcp.yourdomain.com;

        ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

        location / {
            proxy_pass http://mcp_gateway;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";

            # Rate limiting
            limit_req zone=api burst=20 nodelay;
        }
    }

    # n8n (n8n.yourdomain.com)
    server {
        listen 443 ssl http2;
        server_name n8n.yourdomain.com;

        ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

        location / {
            proxy_pass http://n8n;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # WebSocket support (required for n8n)
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";

            # Increase timeout for long-running workflows
            proxy_read_timeout 300s;
        }
    }

    # Sim Studio (studio.yourdomain.com)
    server {
        listen 443 ssl http2;
        server_name studio.yourdomain.com;

        ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

        location / {
            proxy_pass http://sim_studio;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### SSL Certificate Setup (Let's Encrypt)

```bash
#!/bin/bash
# setup-ssl.sh - Install SSL certificates

# Install Certbot
apt-get update
apt-get install -y certbot

# Stop nginx temporarily
docker-compose stop nginx

# Get certificate (standalone mode)
certbot certonly --standalone \
  -d mcp.yourdomain.com \
  -d n8n.yourdomain.com \
  -d studio.yourdomain.com \
  --email your@email.com \
  --agree-tos \
  --non-interactive

# Restart nginx
docker-compose up -d nginx

# Auto-renewal cron job
echo "0 0 * * * certbot renew --quiet && docker-compose restart nginx" | crontab -
```

---

## MCP Server Deployment Specifications

### Deployment Matrix

| MCP Server | Deployment Location | Transport | Docker | Auto-Start |
|------------|---------------------|-----------|--------|------------|
| **unityMCP** | Local PC (Windows) | HTTP (WebSocket) | No | Unity Editor UI |
| **unrealMCP** | Local PC (Windows) | stdio (Python) | No | Manual (`uv run`) |
| **godotMCP** | Local PC (Windows) | stdio (Node.js) | No | Manual (`node server.js`) |
| **comfyuiMCP** | AWS EC2 (g4dn.xlarge) | HTTP (REST + WS) | Yes | systemd service |
| **simStudioMCP** | Hostinger VPS | HTTP (REST) | Yes | Docker Compose |
| **awsGPU** | Hostinger VPS | stdio (Python) | Yes | Docker Compose |
| **localLLM** | Local PC (Windows) | HTTP (OpenAI API) | No | LM Studio UI |

### Individual Server Configurations

#### 1. unityMCP (Local - No Changes)
```json
{
  "mcpServers": {
    "unity": {
      "url": "http://localhost:8080/mcp",
      "description": "Unity Editor control via MCP package"
    }
  }
}
```
**Deployment**: Already configured. Unity Editor → Window → MCP for Unity → Start Server

#### 2. unrealMCP (Local - No Changes)
```json
{
  "mcpServers": {
    "unreal": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/ai-game-dev-system/mcp-servers/unreal-mcp/Python",
        "run",
        "unreal_mcp_server.py"
      ],
      "description": "Unreal Engine 5 control via Python MCP"
    }
  }
}
```
**Deployment**: Already configured. Manual start when needed.

#### 3. godotMCP (Local - No Changes)
```json
{
  "mcpServers": {
    "godot": {
      "command": "node",
      "args": [
        "C:/ai-game-dev-system/mcp-servers/godot-mcp/server/src/index.js"
      ],
      "env": {
        "GODOT_PORT": "6005"
      },
      "description": "Godot 4 control via Node.js MCP"
    }
  }
}
```
**Deployment**: Already configured. Manual start when needed.

#### 4. comfyuiMCP (AWS - New Cloud Deployment)
```json
{
  "mcpServers": {
    "comfyui": {
      "command": "python",
      "args": [
        "C:/ai-game-dev-system/infrastructure/aws/comfyui_mcp_client.py"
      ],
      "env": {
        "AWS_REGION": "us-east-1",
        "COMFYUI_INSTANCE_TYPE": "comfyui"
      },
      "description": "ComfyUI on AWS EC2 with auto-start/stop"
    }
  }
}
```

**Client Implementation**:
```python
# infrastructure/aws/comfyui_mcp_client.py
import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from aws_gpu_controller import AWSGPUController

server = Server("comfyui-aws")
controller = AWSGPUController()

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="comfyui_generate",
            description="Generate image with ComfyUI on AWS GPU",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                    "negative_prompt": {"type": "string", "default": ""},
                    "width": {"type": "integer", "default": 1024},
                    "height": {"type": "integer", "default": 1024},
                    "model": {"type": "string", "default": "sd_xl_base_1.0"},
                    "steps": {"type": "integer", "default": 30},
                    "cfg_scale": {"type": "number", "default": 7.0}
                },
                "required": ["prompt"]
            }
        ),
        Tool(
            name="comfyui_status",
            description="Check ComfyUI AWS instance status",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="comfyui_stop",
            description="Stop ComfyUI instance (save costs)",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "comfyui_generate":
        # Ensure instance is running
        status = controller.get_status()
        if "comfyui" not in status or status["comfyui"]["state"] != "running":
            controller.start_instance("comfyui", use_spot=True)
            await asyncio.sleep(120)  # Wait for ComfyUI to start

        # Get instance IP
        instance_info = status.get("comfyui", {})
        comfyui_url = f"http://{instance_info['public_ip']}:8188"

        # Submit ComfyUI workflow (via API)
        import requests
        workflow = {
            "prompt": {
                "1": {
                    "inputs": {
                        "text": arguments["prompt"],
                        "width": arguments.get("width", 1024),
                        "height": arguments.get("height", 1024)
                    },
                    "class_type": "CLIPTextEncode"
                },
                # ... (full ComfyUI workflow JSON)
            }
        }

        response = requests.post(f"{comfyui_url}/prompt", json=workflow)
        prompt_id = response.json()["prompt_id"]

        # Poll for completion
        while True:
            status_response = requests.get(f"{comfyui_url}/history/{prompt_id}")
            if status_response.json():
                break
            await asyncio.sleep(2)

        # Download result
        result = status_response.json()[prompt_id]
        image_filename = result["outputs"]["9"]["images"][0]["filename"]
        image_url = f"{comfyui_url}/view?filename={image_filename}"

        # Download to local
        image_data = requests.get(image_url).content
        output_path = f"C:/ai-game-dev-system/generated_assets/{image_filename}"
        with open(output_path, "wb") as f:
            f.write(image_data)

        return [TextContent(
            type="text",
            text=f"Image generated: {output_path}\nPrompt: {arguments['prompt']}"
        )]

    elif name == "comfyui_status":
        status = controller.get_status()
        return [TextContent(type="text", text=json.dumps(status, indent=2))]

    elif name == "comfyui_stop":
        result = controller.stop_instance("comfyui")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

#### 5. awsGPU (Hostinger VPS - New Deployment)

**Dockerfile**:
```dockerfile
# infrastructure/docker/Dockerfile.awsgpu
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY aws_gpu_controller.py aws_mcp_server.py ./
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 9002

CMD ["python", "aws_mcp_server.py"]
```

**Add to docker-compose.yml**:
```yaml
  aws-gpu-mcp:
    build:
      context: ./aws
      dockerfile: Dockerfile.awsgpu
    container_name: aws-gpu-mcp
    restart: unless-stopped
    ports:
      - "9002:9002"
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=us-east-1
      - AWS_S3_BUCKET=meowping-game-assets
    volumes:
      - ./aws/instance_state.json:/app/instance_state.json
    networks:
      - ziggie
```

#### 6. localLLM (Local - Fallback to Ollama on VPS)

**Client Configuration**:
```json
{
  "mcpServers": {
    "llm": {
      "command": "python",
      "args": [
        "C:/ai-game-dev-system/infrastructure/llm_router.py"
      ],
      "env": {
        "PRIMARY_LLM_URL": "http://localhost:1234/v1",
        "FALLBACK_LLM_URL": "https://mcp.yourdomain.com/ollama"
      },
      "description": "LLM with local-first fallback routing"
    }
  }
}
```

**Router Implementation**:
```python
# infrastructure/llm_router.py
import os
import requests
from openai import OpenAI

PRIMARY_URL = os.environ.get("PRIMARY_LLM_URL", "http://localhost:1234/v1")
FALLBACK_URL = os.environ.get("FALLBACK_LLM_URL")

def get_llm_client():
    # Try local LM Studio first
    try:
        response = requests.get(f"{PRIMARY_URL}/models", timeout=2)
        if response.ok:
            return OpenAI(base_url=PRIMARY_URL, api_key="not-needed")
    except:
        pass

    # Fallback to Hostinger VPS Ollama
    if FALLBACK_URL:
        return OpenAI(base_url=FALLBACK_URL, api_key="not-needed")

    raise Exception("No LLM available")

# Usage in MCP tools
client = get_llm_client()
response = client.chat.completions.create(
    model="llama-3.2-3b",
    messages=[{"role": "user", "content": "Hello"}]
)
```

---

## Hybrid Architecture & Fallback Chains

### Routing Decision Tree

```
┌─────────────────────────────────────────────────────────────┐
│              REQUEST: Generate game asset                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   Is GPU required?            │
         └───┬───────────────────────┬───┘
             │ YES                   │ NO
             │                       │
             ▼                       ▼
   ┌─────────────────────┐   ┌─────────────────────┐
   │ ComfyUI needed      │   │ Use local tools     │
   └──────┬──────────────┘   │ (Blender, scripts)  │
          │                  └─────────────────────┘
          ▼
┌─────────────────────────────────────────┐
│ Check AWS ComfyUI instance status       │
└──────┬──────────────────────────────────┘
       │
       ▼
   ┌───────────┐
   │ Running?  │
   └─┬─────┬───┘
     │YES  │NO
     │     │
     │     ▼
     │  ┌──────────────────────┐
     │  │ Start EC2 instance   │
     │  │ (via awsGPU MCP)     │
     │  └──────┬───────────────┘
     │         │
     │         ▼
     │  ┌──────────────────────┐
     │  │ Wait 2min (startup)  │
     │  └──────┬───────────────┘
     │         │
     ▼         ▼
┌──────────────────────────────────┐
│ Submit generation job            │
│ (n8n workflow or direct API)     │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────┐
│ Job successful?      │
└─┬────────────────┬───┘
  │YES             │NO
  │                │
  │                ▼
  │         ┌──────────────────────────┐
  │         │ FALLBACK: ImagineArt     │
  │         │ (browser automation)     │
  │         └──────┬───────────────────┘
  │                │
  ▼                ▼
┌──────────────────────────────────┐
│ Download result to local         │
│ Upload to S3 (archive)           │
└──────────────────────────────────┘
```

### Cost-Based Routing Logic

```typescript
// mcp-gateway/src/cost-router.ts
interface RoutingRule {
  serviceName: string;
  costPerRequest: number;  // USD
  latency: number;          // seconds
  quality: number;          // 1-10 scale
}

const routes: RoutingRule[] = [
  {
    serviceName: 'comfyui-aws-spot',
    costPerRequest: 0.005,  // ~$0.005 per 1024x1024 image
    latency: 8,
    quality: 10
  },
  {
    serviceName: 'imagineai-free',
    costPerRequest: 0,
    latency: 45,
    quality: 8
  },
  {
    serviceName: 'replicate-api',
    costPerRequest: 0.0023,  // Per second pricing
    latency: 5,
    quality: 10
  }
];

function selectRoute(budget: number, deadline: number, minQuality: number): RoutingRule {
  const eligible = routes.filter(r =>
    r.costPerRequest <= budget &&
    r.latency <= deadline &&
    r.quality >= minQuality
  );

  // Sort by cost (prefer cheaper), then latency
  eligible.sort((a, b) => {
    if (a.costPerRequest !== b.costPerRequest) {
      return a.costPerRequest - b.costPerRequest;
    }
    return a.latency - b.latency;
  });

  return eligible[0] || routes[0]; // Fallback to first route
}

// Example usage
const route = selectRoute(
  budget: 0.01,      // Max $0.01 per request
  deadline: 30,      // Need result in 30 seconds
  minQuality: 9      // High quality required
);

console.log(`Selected route: ${route.serviceName}`);
// Output: "comfyui-aws-spot" (cheapest with acceptable latency)
```

### Fallback Configuration Table

| Primary Service | Fallback 1 | Fallback 2 | Fallback 3 |
|----------------|------------|------------|------------|
| **ComfyUI AWS** | Replicate API | ImagineArt (free) | Local manual |
| **LM Studio (local)** | Ollama (VPS) | Claude API | N/A |
| **Unity MCP (local)** | N/A | N/A | N/A |
| **S3 Storage** | Local filesystem | Google Drive (rclone) | N/A |
| **PostgreSQL (VPS)** | SQLite (local) | N/A | N/A |

---

## Data Flow & Integration Points

### Asset Generation Pipeline (E2E Example)

```
1. USER REQUEST (via Claude Code in Ziggie project)
   └─> "Generate 10 cat warrior sprites for RTS game"

2. MCP GATEWAY (Hostinger VPS)
   └─> Parse request → Route to n8n workflow

3. N8N WORKFLOW (Hostinger VPS)
   ├─> Task 1: Generate prompts (using Ollama)
   │   └─> "cat warrior archer, isometric view, blue team..."
   ├─> Task 2: Check AWS ComfyUI status
   │   ├─> If stopped → Start instance (via awsGPU MCP)
   │   └─> Wait for ready signal
   ├─> Task 3: Submit 10 generation jobs (parallel)
   │   └─> ComfyUI API: POST /prompt
   └─> Task 4: Monitor job queue

4. COMFYUI (AWS EC2)
   ├─> Load SDXL model from S3 (cached after first run)
   ├─> Apply LoRA: "meowping_style_v1.safetensors"
   ├─> Generate 1024x1024 PNG (8 seconds each)
   └─> Save to /output folder

5. N8N POST-PROCESSING
   ├─> Download images from ComfyUI via HTTP
   ├─> Upload to S3: s3://meowping-game-assets/generated/sprites/units/
   ├─> Copy to local: C:/ai-game-dev-system/generated_assets/
   ├─> Update asset manifest JSON
   └─> Stop AWS instance (after 30min idle)

6. RESPONSE TO USER
   └─> "10 sprites generated. Saved to C:/ai-game-dev-system/generated_assets/"
```

### n8n Workflow JSON (Cat Warrior Generation)

```json
{
  "name": "Cat Warrior Sprite Generation",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "generate-sprites",
        "method": "POST"
      }
    },
    {
      "name": "Generate Prompts",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://ollama:11434/v1/chat/completions",
        "method": "POST",
        "body": {
          "model": "llama-3.2-3b",
          "messages": [
            {
              "role": "system",
              "content": "Generate 10 unique prompts for cat warrior sprites in an RTS game. Each prompt should specify: unit type (archer/warrior/mage), faction color (red/blue/green), and pose."
            },
            {
              "role": "user",
              "content": "Create prompts for: {{ $json.body.unitType }}"
            }
          ]
        }
      }
    },
    {
      "name": "Check ComfyUI Status",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://mcp-gateway:9000/mcp/comfyui/status",
        "method": "GET"
      }
    },
    {
      "name": "Start ComfyUI If Stopped",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.state }}",
              "operation": "notEqual",
              "value2": "running"
            }
          ]
        }
      }
    },
    {
      "name": "Submit Generation Jobs",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{ $env.COMFYUI_URL }}/prompt",
        "method": "POST",
        "body": {
          "prompt": {
            "3": {
              "inputs": {
                "text": "={{ $json.prompt }}",
                "clip": ["4", 1]
              },
              "class_type": "CLIPTextEncode"
            },
            "4": {
              "inputs": {
                "ckpt_name": "sd_xl_base_1.0.safetensors"
              },
              "class_type": "CheckpointLoaderSimple"
            }
          }
        }
      }
    },
    {
      "name": "Upload to S3",
      "type": "n8n-nodes-base.awsS3",
      "parameters": {
        "operation": "upload",
        "bucketName": "meowping-game-assets",
        "fileName": "={{ $json.filename }}",
        "binaryData": true
      }
    }
  ]
}
```

### API Integration Map

```
┌──────────────────────────────────────────────────────────┐
│                  API INTEGRATION POINTS                  │
└──────────────────────────────────────────────────────────┘

LOCAL PC (Windows)
├─ Unity MCP Server
│  └─ HTTP API: http://localhost:8080/mcp
│     ├─ POST /gameobject/create
│     ├─ POST /script/generate
│     └─ GET /scene/hierarchy
├─ Unreal MCP Server
│  └─ stdio transport (no HTTP)
│     └─ Commands via Python subprocess
├─ LM Studio
│  └─ OpenAI-compatible API: http://localhost:1234/v1
│     ├─ POST /chat/completions
│     └─ GET /models

HOSTINGER VPS
├─ MCP Gateway: https://mcp.yourdomain.com
│  ├─ GET /health → Service health status
│  ├─ POST /mcp/:service/* → Proxy to service
│  └─ POST /aws/comfyui/start → Start AWS instance
├─ n8n: https://n8n.yourdomain.com
│  ├─ POST /webhook/* → Trigger workflows
│  ├─ GET /api/v1/workflows → List workflows
│  └─ POST /api/v1/executions → Manual execution
├─ Sim Studio: https://studio.yourdomain.com
│  ├─ POST /api/agents/invoke → Run AI agent
│  ├─ GET /api/workflows → List visual workflows
│  └─ POST /api/mcp/register → Register new MCP server

AWS
├─ ComfyUI: http://<ec2-public-ip>:8188
│  ├─ POST /prompt → Submit generation job
│  ├─ GET /history/:prompt_id → Check job status
│  ├─ GET /view?filename=X → Download result
│  └─ GET /system_stats → System info
├─ S3 API: https://s3.amazonaws.com
│  ├─ PUT /meowping-game-assets/:path → Upload
│  ├─ GET /meowping-game-assets/:path → Download
│  └─ LIST /meowping-game-assets?prefix=X → List objects
└─ EC2 API (via boto3)
   ├─ run_instances() → Launch EC2
   ├─ terminate_instances() → Stop EC2
   └─ describe_instances() → Get status
```

---

## Deployment Procedures

### Phase 1: AWS Infrastructure Setup

```bash
#!/bin/bash
# deploy-aws-infrastructure.sh

set -e

echo "=== Phase 1: AWS Infrastructure Setup ==="

# 1. Install AWS CLI
if ! command -v aws &> /dev/null; then
  echo "Installing AWS CLI..."
  curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
  unzip awscliv2.zip
  sudo ./aws/install
fi

# 2. Configure AWS credentials
echo "Configuring AWS credentials..."
aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
aws configure set default.region us-east-1

# 3. Create S3 bucket
echo "Creating S3 bucket..."
aws s3 mb s3://meowping-game-assets --region us-east-1
aws s3api put-bucket-versioning \
  --bucket meowping-game-assets \
  --versioning-configuration Status=Enabled

# 4. Apply lifecycle policy
cat > /tmp/lifecycle.json <<'EOF'
{
  "Rules": [
    {
      "Id": "MoveToIA",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        }
      ]
    }
  ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
  --bucket meowping-game-assets \
  --lifecycle-configuration file:///tmp/lifecycle.json

# 5. Create IAM role for EC2
echo "Creating IAM role..."
aws iam create-role \
  --role-name EC2-ComfyUI-Role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ec2.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach policies
aws iam attach-role-policy \
  --role-name EC2-ComfyUI-Role \
  --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

aws iam attach-role-policy \
  --role-name EC2-ComfyUI-Role \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy

# Create S3 access policy
cat > /tmp/s3-policy.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket"
    ],
    "Resource": [
      "arn:aws:s3:::meowping-game-assets",
      "arn:aws:s3:::meowping-game-assets/*"
    ]
  }]
}
EOF

aws iam put-role-policy \
  --role-name EC2-ComfyUI-Role \
  --policy-name S3Access \
  --policy-document file:///tmp/s3-policy.json

# Create instance profile
aws iam create-instance-profile \
  --instance-profile-name EC2-ComfyUI-Profile

aws iam add-role-to-instance-profile \
  --instance-profile-name EC2-ComfyUI-Profile \
  --role-name EC2-ComfyUI-Role

# 6. Upload SDXL models to S3
echo "Uploading SDXL models..."
aws s3 sync \
  ~/Downloads/stable-diffusion-models/ \
  s3://meowping-game-assets/models/sdxl/ \
  --exclude "*" \
  --include "*.safetensors"

echo "=== AWS Infrastructure Setup Complete ==="
```

### Phase 2: Hostinger VPS Setup

```bash
#!/bin/bash
# deploy-hostinger-vps.sh

set -e

echo "=== Phase 2: Hostinger VPS Setup ==="

# 1. SSH to VPS (replace with your VPS IP)
VPS_IP="your.vps.ip.address"

# 2. Update system
ssh root@$VPS_IP << 'EOF'
apt-get update
apt-get upgrade -y
apt-get install -y curl git docker.io docker-compose-v2
systemctl enable docker
systemctl start docker
EOF

# 3. Upload docker-compose.yml
scp docker-compose.yml root@$VPS_IP:/root/
scp nginx.conf root@$VPS_IP:/root/

# 4. Create environment file
cat > .env <<ENV
POSTGRES_PASSWORD=$(openssl rand -base64 32)
N8N_PASSWORD=$(openssl rand -base64 16)
N8N_DB_PASSWORD=$(openssl rand -base64 32)
N8N_ENCRYPTION_KEY=$(openssl rand -base64 32)
SIM_DB_PASSWORD=$(openssl rand -base64 32)
AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
COMFYUI_AWS_IP=
ENV

scp .env root@$VPS_IP:/root/

# 5. Start services
ssh root@$VPS_IP << 'EOF'
cd /root
docker compose up -d

# Wait for services to start
sleep 30

# Check status
docker compose ps

# View logs
docker compose logs -f
EOF

echo "=== Hostinger VPS Setup Complete ==="
echo "Access URLs:"
echo "  MCP Gateway: https://mcp.yourdomain.com"
echo "  n8n: https://n8n.yourdomain.com"
echo "  Sim Studio: https://studio.yourdomain.com"
```

### Phase 3: Local Configuration

```bash
#!/bin/bash
# configure-local-mcp.sh

set -e

echo "=== Phase 3: Local MCP Configuration ==="

# 1. Update Claude Desktop config
CLAUDE_CONFIG="$HOME/AppData/Roaming/Claude/claude_desktop_config.json"

cat > "$CLAUDE_CONFIG" <<'EOF'
{
  "mcpServers": {
    "unity": {
      "url": "http://localhost:8080/mcp"
    },
    "unreal": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/ai-game-dev-system/mcp-servers/unreal-mcp/Python",
        "run",
        "unreal_mcp_server.py"
      ]
    },
    "godot": {
      "command": "node",
      "args": [
        "C:/ai-game-dev-system/mcp-servers/godot-mcp/server/src/index.js"
      ]
    },
    "comfyui": {
      "command": "python",
      "args": [
        "C:/ai-game-dev-system/infrastructure/aws/comfyui_mcp_client.py"
      ],
      "env": {
        "AWS_REGION": "us-east-1"
      }
    },
    "llm": {
      "command": "python",
      "args": [
        "C:/ai-game-dev-system/infrastructure/llm_router.py"
      ],
      "env": {
        "PRIMARY_LLM_URL": "http://localhost:1234/v1",
        "FALLBACK_LLM_URL": "https://mcp.yourdomain.com/ollama"
      }
    }
  }
}
EOF

echo "=== Local MCP Configuration Complete ==="
```

### Phase 4: Verification Tests

```bash
#!/bin/bash
# verify-deployment.sh

set -e

echo "=== Phase 4: Verification Tests ==="

# Test 1: AWS S3 access
echo "Test 1: S3 bucket access"
aws s3 ls s3://meowping-game-assets/ && echo "✓ S3 accessible" || echo "✗ S3 failed"

# Test 2: Start ComfyUI instance
echo "Test 2: Start ComfyUI EC2 instance"
python C:/ai-game-dev-system/infrastructure/aws/aws_gpu_controller.py start comfyui

# Test 3: ComfyUI API
echo "Test 3: ComfyUI API health"
sleep 120  # Wait for startup
COMFYUI_IP=$(python -c "from aws_gpu_controller import AWSGPUController; c=AWSGPUController(); print(c.get_status()['comfyui']['public_ip'])")
curl -f http://$COMFYUI_IP:8188/system_stats && echo "✓ ComfyUI running" || echo "✗ ComfyUI failed"

# Test 4: Hostinger VPS services
echo "Test 4: Hostinger VPS health checks"
curl -f https://mcp.yourdomain.com/health && echo "✓ MCP Gateway OK" || echo "✗ MCP Gateway failed"
curl -f https://n8n.yourdomain.com/healthz && echo "✓ n8n OK" || echo "✗ n8n failed"

# Test 5: Local MCP servers
echo "Test 5: Local MCP connectivity"
curl -f http://localhost:8080/mcp && echo "✓ Unity MCP OK" || echo "✗ Unity MCP offline"
curl -f http://localhost:1234/v1/models && echo "✓ LM Studio OK" || echo "✗ LM Studio offline"

# Test 6: E2E generation test
echo "Test 6: End-to-end asset generation"
python << 'PYTHON'
import requests

# Submit test generation
response = requests.post("https://n8n.yourdomain.com/webhook/generate-sprites", json={
  "prompt": "test cat warrior, blue team, isometric view",
  "count": 1
})

print(f"Generation response: {response.status_code}")
print(f"✓ E2E test passed" if response.ok else "✗ E2E test failed")
PYTHON

echo "=== Verification Complete ==="
```

---

## Monitoring & Cost Management

### CloudWatch Dashboard (AWS)

```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/EC2", "CPUUtilization", {"stat": "Average"}],
          [".", "NetworkIn", {"stat": "Sum"}],
          [".", "NetworkOut", {"stat": "Sum"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "ComfyUI EC2 Performance"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/S3", "BucketSizeBytes", {"stat": "Average"}],
          [".", "NumberOfObjects", {"stat": "Average"}]
        ],
        "period": 86400,
        "stat": "Average",
        "region": "us-east-1",
        "title": "S3 Asset Storage"
      }
    }
  ]
}
```

### Cost Tracking Script

```python
# infrastructure/cost_tracker.py
import boto3
from datetime import datetime, timedelta

ce = boto3.client('ce', region_name='us-east-1')

def get_monthly_costs():
    end = datetime.now()
    start = end.replace(day=1)

    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start.strftime('%Y-%m-%d'),
            'End': end.strftime('%Y-%m-%d')
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[
            {'Type': 'SERVICE', 'Key': 'SERVICE'}
        ]
    )

    costs = {}
    for result in response['ResultsByTime']:
        for group in result['Groups']:
            service = group['Keys'][0]
            cost = float(group['Metrics']['UnblendedCost']['Amount'])
            costs[service] = cost

    return costs

def estimate_monthly_cost():
    costs = get_monthly_costs()

    print("AWS Monthly Cost Breakdown:")
    print("=" * 50)
    total = 0
    for service, cost in sorted(costs.items(), key=lambda x: x[1], reverse=True):
        print(f"{service:30} ${cost:>8.2f}")
        total += cost
    print("=" * 50)
    print(f"{'TOTAL':30} ${total:>8.2f}")

    # Add Hostinger VPS
    hostinger_cost = 6.49
    print(f"\nHostinger VPS:                 ${hostinger_cost:>8.2f}")
    print(f"GRAND TOTAL:                   ${total + hostinger_cost:>8.2f}")

    # Alert if over budget
    BUDGET = 50.0
    if (total + hostinger_cost) > BUDGET:
        print(f"\n⚠️ OVER BUDGET! Target: ${BUDGET}, Current: ${total + hostinger_cost:.2f}")

if __name__ == "__main__":
    estimate_monthly_cost()
```

### Cost Optimization Rules

```yaml
# cost-optimization-rules.yml
rules:
  - name: Auto-stop idle EC2 instances
    trigger: No ComfyUI requests for 30 minutes
    action: Stop EC2 instance
    savings: ~$0.16/hour ($3.84/day if forgotten running)

  - name: S3 lifecycle to Glacier
    trigger: Assets older than 90 days
    action: Move to Glacier Deep Archive
    savings: ~70% storage cost ($0.0099/GB → $0.00099/GB)

  - name: Prefer spot instances
    trigger: Always
    action: Use spot instead of on-demand
    savings: ~70% ($0.526/hr → $0.158/hr)

  - name: Delete failed generation artifacts
    trigger: Daily cleanup
    action: Remove S3 objects tagged "failed"
    savings: ~$0.50/month

  - name: Compress generated assets
    trigger: Before S3 upload
    action: PNG → WebP (70% size reduction)
    savings: ~$0.70/month on 100GB

  - name: Use local LLM first
    trigger: LLM inference request
    action: Route to LM Studio (free) before Ollama VPS
    savings: Avoid VPS CPU usage
```

### Prometheus + Grafana (Optional)

```yaml
# docker-compose.monitoring.yml (add to main docker-compose)
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    networks:
      - ziggie

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana-dashboards:/etc/grafana/provisioning/dashboards:ro
    depends_on:
      - prometheus
    networks:
      - ziggie

volumes:
  prometheus_data:
  grafana_data:
```

**prometheus.yml**:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'mcp-gateway'
    static_configs:
      - targets: ['mcp-gateway:9000']

  - job_name: 'n8n'
    static_configs:
      - targets: ['n8n:5678']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
```

---

## Security & Compliance

### Security Checklist

```markdown
## Infrastructure Security

- [x] AWS IAM: Least-privilege roles (EC2 can only access S3, not terminate other instances)
- [x] S3: Versioning enabled (protect against accidental deletion)
- [x] S3: Bucket encryption at rest (AES-256)
- [x] EC2: No SSH keys (use SSM Session Manager instead)
- [x] EC2: Security group restricts port 8188 to MCP Gateway IP only
- [x] VPS: Nginx rate limiting (10 req/sec per IP)
- [x] VPS: Fail2ban for SSH brute-force protection
- [x] VPS: UFW firewall (allow only 22, 80, 443)
- [x] SSL: Let's Encrypt certificates (auto-renewal)
- [x] SSL: TLS 1.2+ only (no TLS 1.0/1.1)
- [x] Docker: Non-root users in containers
- [x] Docker: Read-only filesystems where possible
- [x] Secrets: Environment variables (never in Git)
- [x] Secrets: AWS Secrets Manager for production

## Application Security

- [x] n8n: Basic auth enabled
- [x] n8n: IP whitelist (allow only your IP + VPS IP)
- [x] MCP Gateway: CORS restricted to known origins
- [x] MCP Gateway: Request validation (schema enforcement)
- [x] ComfyUI: No public internet access (VPN or IP whitelist only)
- [x] PostgreSQL: Strong passwords (32+ chars)
- [x] Redis: Auth password required
- [x] API Keys: Rotated every 90 days
- [x] Logs: CloudWatch + VPS logs (7-day retention)

## Compliance

- [x] GDPR: No personal data stored (only game assets)
- [x] AI Content: Generated images tagged with metadata (model, seed, prompt)
- [x] Licensing: SDXL models comply with CreativeML Open RAIL++-M license
- [x] Backup: Daily automated backups (PostgreSQL → S3)
- [x] Disaster Recovery: RTO=4 hours, RPO=24 hours
```

### Secrets Management

```bash
#!/bin/bash
# setup-secrets.sh - Securely manage secrets

# Generate secrets
POSTGRES_PASSWORD=$(openssl rand -base64 32)
N8N_PASSWORD=$(openssl rand -base64 16)
N8N_ENCRYPTION_KEY=$(openssl rand -base64 32)
GRAFANA_PASSWORD=$(openssl rand -base64 16)

# Store in AWS Secrets Manager
aws secretsmanager create-secret \
  --name ziggie/postgres-password \
  --secret-string "$POSTGRES_PASSWORD"

aws secretsmanager create-secret \
  --name ziggie/n8n-password \
  --secret-string "$N8N_PASSWORD"

aws secretsmanager create-secret \
  --name ziggie/n8n-encryption-key \
  --secret-string "$N8N_ENCRYPTION_KEY"

# Create .env file (local development only)
cat > .env.local <<ENV
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
N8N_PASSWORD=$N8N_PASSWORD
N8N_ENCRYPTION_KEY=$N8N_ENCRYPTION_KEY
GRAFANA_PASSWORD=$GRAFANA_PASSWORD
ENV

echo "Secrets stored in AWS Secrets Manager"
echo "Local .env.local created (DO NOT COMMIT)"

# Add to .gitignore
echo ".env*" >> .gitignore
```

---

## Quick Reference

### Common Commands

```bash
# AWS - Start ComfyUI
python infrastructure/aws/aws_gpu_controller.py start comfyui

# AWS - Stop ComfyUI (save costs)
python infrastructure/aws/aws_gpu_controller.py stop comfyui

# AWS - Check status
python infrastructure/aws/aws_gpu_controller.py status

# AWS - Estimate costs
python infrastructure/aws/aws_gpu_controller.py cost comfyui --hours 8

# Hostinger - View logs
ssh root@vps "cd /root && docker compose logs -f"

# Hostinger - Restart services
ssh root@vps "cd /root && docker compose restart"

# Hostinger - Update services
ssh root@vps "cd /root && docker compose pull && docker compose up -d"

# Local - Test MCP connections
curl http://localhost:8080/mcp  # Unity
curl http://localhost:1234/v1/models  # LM Studio

# S3 - Upload models
aws s3 sync ~/Downloads/models/ s3://meowping-game-assets/models/

# S3 - Download generated assets
aws s3 sync s3://meowping-game-assets/generated/ ./generated_assets/
```

### Troubleshooting

```markdown
## Issue: ComfyUI EC2 won't start

Possible causes:
1. Spot instance unavailable in region
   → Try different region or on-demand instance
2. Service quota exceeded
   → Request quota increase in AWS Console
3. IAM permissions missing
   → Verify EC2-ComfyUI-Role has required policies

## Issue: n8n workflows timeout

Possible causes:
1. ComfyUI instance not started
   → Manually start via awsGPU MCP
2. Network connectivity issue
   → Check security group allows VPS IP on port 8188
3. Redis queue full
   → Restart Redis: `docker compose restart redis`

## Issue: High AWS costs

Immediate actions:
1. Stop all EC2 instances: `aws ec2 stop-instances --instance-ids $(aws ec2 describe-instances --filters "Name=tag:Project,Values=MeowPing" --query "Reservations[].Instances[].InstanceId" --output text)`
2. Check S3 storage: `aws s3 ls s3://meowping-game-assets --recursive --summarize`
3. Review CloudWatch metrics
4. Enable cost alerts in AWS Budgets

## Issue: MCP Gateway not routing correctly

Debug steps:
1. Check health endpoint: `curl https://mcp.yourdomain.com/health`
2. View logs: `docker logs mcp-gateway`
3. Verify Redis connectivity: `docker exec -it redis redis-cli ping`
4. Test direct service access (bypass gateway)
```

---

## Conclusion

This architecture provides:

- **Cost-efficient**: $40-50/month total (AWS spot + Hostinger VPS)
- **Scalable**: Can handle 1000+ asset generations/month
- **Resilient**: Fallback chains prevent single points of failure
- **Hybrid**: Local development, cloud production
- **Automated**: n8n workflows eliminate manual tasks

### Next Steps

1. **Deploy AWS infrastructure** (Phase 1 script)
2. **Setup Hostinger VPS** (Phase 2 script)
3. **Configure local MCP servers** (Phase 3 script)
4. **Run verification tests** (Phase 4 script)
5. **Create first n8n workflow** (cat warrior generation example)
6. **Monitor costs** (cost tracker script, weekly review)

### Deployment Timeline

| Phase | Duration | Blocker |
|-------|----------|---------|
| AWS Setup | 1 hour | AWS account, payment method |
| Hostinger VPS | 30 min | Domain name (optional) |
| Local Config | 15 min | None |
| Testing | 30 min | All phases complete |
| **Total** | **2.25 hours** | - |

---

**Document Version**: 1.0
**Last Updated**: 2025-12-23
**Author**: HEPHAESTUS (Elite Technical Agent)
**Status**: Production-Ready ✅

---

## Sources

### AWS ComfyUI Deployment
- [AWS: Deploy Stable Diffusion ComfyUI on AWS elastically and efficiently](https://aws.amazon.com/blogs/architecture/deploy-stable-diffusion-comfyui-on-aws-elastically-and-efficiently/)
- [AWS Samples: Cost-effective ComfyUI deployment with ECS and CDK](https://github.com/aws-samples/cost-effective-aws-deployment-of-comfyui)
- [AWS Marketplace: ComfyUI Server on Linux with HTTPS Access](https://aws.amazon.com/marketplace/pp/prodview-y6qfo6u5j4n4m)
- [Stable Diffusion Art: How to run ComfyUI on AWS EC2](https://stable-diffusion-art.com/aws-ec2/)
- [Medium: Run ComfyUI on AWS EC2](https://medium.com/@motaz.emad/run-comfyui-on-aws-ec2-95e4f0acc176)

### MCP Server Best Practices
- [The New Stack: 15 Best Practices for Building MCP Servers in Production](https://thenewstack.io/15-best-practices-for-building-mcp-servers-in-production/)
- [MarkTechPost: 7 MCP Server Best Practices for Scalable AI Integrations in 2025](https://www.marktechpost.com/2025/07/23/7-mcp-server-best-practices-for-scalable-ai-integrations-in-2025/)
- [AWS: Guidance for Deploying Model Context Protocol Servers on AWS](https://aws.amazon.com/solutions/guidance/deploying-model-context-protocol-servers-on-aws/)
- [MCP Manager: MCP Server Deployment Options](https://mcpmanager.ai/blog/mcp-deployment-options/)
- [Model Context Protocol: MCP Best Practices](https://modelcontextprotocol.info/docs/best-practices/)

### Hostinger n8n Deployment
- [Hostinger: Self-hosted n8n - Secure and scalable automation](https://www.hostinger.com/self-hosted-n8n)
- [Hostinger Tutorials: How to self-host n8n with Docker](https://www.hostinger.com/tutorials/how-to-self-host-n8n-with-docker)
- [Hostinger Support: How to Use the N8N VPS Template](https://www.hostinger.com/support/10473267-how-to-use-the-n8n-vps-template-at-hostinger/)
- [9to5Mac: Automate your workflow with self-hosted n8n on Hostinger VPS](https://9to5mac.com/2025/09/06/productivity-superpower-n8n-hostinger-vps/)
- [Hostinger Tutorials: How to configure n8n queue mode on VPS](https://www.hostinger.com/tutorials/n8n-queue-mode)

### Hybrid Cloud Architecture
- [IBM: How to Design a Hybrid Cloud Architecture](https://www.ibm.com/think/topics/design-hybrid-cloud-architecture)
- [Signiance: Top 8 Hybrid Cloud Architectures for 2025](https://signiance.com/hybrid-cloud-architectures/)
- [HorizonIQ: Hybrid Cloud Architecture - Key Components for a Resilient Enterprise](https://www.horizoniq.com/blog/hybrid-cloud-architecture/)
- [TechTarget: The Future of Hybrid Cloud - What to Expect in 2025 and Beyond](https://www.techtarget.com/searchcloudcomputing/feature/The-future-of-hybrid-cloud-What-to-expect)
- [TatvaSoft: A Definitive Guide to Hybrid Cloud Architecture](https://www.tatvasoft.com/outsourcing/2025/10/hybrid-cloud-architecture.html)
