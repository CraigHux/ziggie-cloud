# AWS EC2 Spot Instances for Ziggie Cloud - Complete Research Guide

> **Context**: Cost-effective GPU compute for ComfyUI (SDXL image generation, 3D model processing)
> **Target Region**: EU-North-1 Stockholm
> **Target Instances**: g4dn.xlarge (T4 16GB), g5.xlarge (A10G 24GB)
> **Workload Type**: Batch processing (not real-time) - PERFECT for Spot
> **Research Date**: 2025-12-23

---

## Executive Summary

AWS EC2 Spot Instances provide **60-90% cost savings** over On-Demand for GPU compute, ideal for ComfyUI batch workloads. With proper interruption handling and Spot Fleet configuration, you can achieve production-grade reliability while maintaining massive cost savings.

**Key Findings**:
- On-Demand g4dn.xlarge: $0.526/hr → Spot: ~$0.16-$0.20/hr (70% savings)
- Expected interruption rate: <5% for GPU instances in EU regions
- 2-minute warning system enables graceful checkpoint/resume
- Spot Fleet with `price-capacity-optimized` allocation = automatic failover

---

## 1. Spot Instance Pricing (EU-North-1 Stockholm - 2025)

### Instance Specifications

| Instance Type | GPU | GPU Memory | vCPUs | System RAM | On-Demand Price | Typical Spot Price | Savings |
|---------------|-----|------------|-------|------------|-----------------|-------------------|---------|
| **g4dn.xlarge** | NVIDIA T4 | 16 GB | 4 | 16 GB | $0.526/hr | $0.16-$0.20/hr | 62-70% |
| **g5.xlarge** | NVIDIA A10G | 24 GB | 4 | 16 GB | $1.006/hr | $0.30-$0.40/hr | 60-70% |

**Note**: Spot prices fluctuate based on supply/demand. Above are typical prices for EU-North-1 based on AWS historical data.

### Monthly Cost Comparison (24/7 operation)

| Scenario | Instance | On-Demand Cost | Spot Cost (avg) | Monthly Savings |
|----------|----------|----------------|-----------------|-----------------|
| **Baseline** | g4dn.xlarge | $379.20/mo | $136.80/mo | **$242.40/mo (64%)** |
| **Higher Performance** | g5.xlarge | $724.32/mo | $252.00/mo | **$472.32/mo (65%)** |

### Realistic Batch Processing (8 hrs/day, 20 days/mo)

| Instance | On-Demand Cost | Spot Cost | Monthly Savings |
|----------|----------------|-----------|-----------------|
| g4dn.xlarge | $84.16 | $29.60 | **$54.56/mo (65%)** |
| g5.xlarge | $160.96 | $56.00 | **$104.96/mo (65%)** |

**Recommendation**: Start with g4dn.xlarge Spot for initial testing. Scale to g5.xlarge when you need higher throughput (A10G is ~2x faster than T4 for SDXL).

---

## 2. Spot Interruption Rates & Handling Strategies

### Interruption Rate Data (AWS Historical)

| Instance Family | Region | Interruption Rate | Frequency |
|----------------|--------|-------------------|-----------|
| **g4dn** | EU-North-1 | **<5%** | ~1-2x/month |
| **g5** | EU-North-1 | **<5%** | ~1-2x/month |

**Why GPU Spot is Reliable**:
- GPU instances have LOWER interruption rates than general-purpose
- EU regions typically have LOWER interruption rates than US regions
- Batch workloads are perfect for Spot (vs real-time serving)

### 2-Minute Warning System

AWS provides **2 minutes advance notice** before interruption via:

1. **EventBridge Event** (recommended for automation)
2. **Instance Metadata Service** (IMDSv2 polling)

#### EventBridge Integration (Lambda Handler)

```json
{
  "version": "0",
  "id": "12345678-1234-1234-1234-123456789012",
  "detail-type": "EC2 Spot Instance Interruption Warning",
  "source": "aws.ec2",
  "account": "123456789012",
  "time": "2025-12-23T10:30:00Z",
  "region": "eu-north-1",
  "resources": ["arn:aws:ec2:eu-north-1a:instance/i-1234567890abcdef0"],
  "detail": {
    "instance-id": "i-1234567890abcdef0",
    "instance-action": "terminate"
  }
}
```

**Possible Actions**: `terminate`, `stop`, `hibernate`

#### Instance Metadata Polling (5-second intervals)

```bash
#!/bin/bash
# Poll for interruption notice every 5 seconds

while true; do
  TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" \
    -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

  INTERRUPTION=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" -s \
    http://169.254.169.254/latest/meta-data/spot/instance-action)

  if [ -n "$INTERRUPTION" ]; then
    echo "Interruption detected: $INTERRUPTION"
    # Trigger checkpoint script
    /opt/comfyui/checkpoint.sh
    break
  fi

  sleep 5
done
```

### Interruption Handling Strategies

| Strategy | Use Case | Implementation |
|----------|----------|----------------|
| **Checkpoint/Resume** | Long-running generation (5+ min) | Save state every 30s, resume on new instance |
| **Queue-based** | Batch processing | SQS queue, worker polls, re-queue on interruption |
| **Spot Fleet Diversification** | High availability | Auto-replace with different instance type |
| **Stop/Resume** | Time-flexible workloads | Configure stop behavior, auto-resume when capacity available |

**Recommended for ComfyUI**: Checkpoint/Resume + Queue-based

---

## 3. Spot Fleet Configuration for Automatic Failover

### Allocation Strategy: `price-capacity-optimized` (Recommended)

AWS automatically provisions instances from the **most-available** Spot capacity pools with the **lowest price**.

**Benefits**:
- Decreases interruption likelihood by 70-80%
- Balances cost optimization with availability
- Better than `lowest-price` (which picks risky pools)

### Spot Fleet vs Auto Scaling Group

| Feature | Spot Fleet (EC2 Fleet) | Auto Scaling Group |
|---------|------------------------|-------------------|
| **Lifecycle Management** | Manual | Automatic |
| **Horizontal Scaling** | No | Yes |
| **Recommended For** | Fixed capacity batch jobs | Dynamic scaling workloads |
| **API** | `CreateFleet` | `CreateAutoScalingGroup` |

**Recommendation for ComfyUI**: Use **Auto Scaling Group** with Spot + On-Demand mix (90% Spot, 10% On-Demand fallback).

### Auto Scaling Group Configuration (Terraform)

```hcl
resource "aws_autoscaling_group" "comfyui_workers" {
  name                = "comfyui-spot-workers"
  vpc_zone_identifier = [aws_subnet.eu_north_1a.id, aws_subnet.eu_north_1b.id]
  min_size            = 0
  max_size            = 5
  desired_capacity    = 1

  mixed_instances_policy {
    instances_distribution {
      on_demand_base_capacity                  = 0
      on_demand_percentage_above_base_capacity = 10  # 90% Spot, 10% On-Demand
      spot_allocation_strategy                 = "price-capacity-optimized"
    }

    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.comfyui.id
        version            = "$Latest"
      }

      # Instance diversification (CRITICAL for low interruption)
      override {
        instance_type = "g4dn.xlarge"
      }
      override {
        instance_type = "g4dn.2xlarge"
      }
      override {
        instance_type = "g5.xlarge"
      }
    }
  }

  tag {
    key                 = "Name"
    value               = "ComfyUI-Spot-Worker"
    propagate_at_launch = true
  }
}
```

### Instance Diversification (CRITICAL Best Practice)

**Diversify across AT LEAST 10 instance types** for maximum availability:

```python
INSTANCE_TYPES = [
  "g4dn.xlarge",      # T4 16GB (baseline)
  "g4dn.2xlarge",     # T4 16GB + more CPU
  "g4dn.4xlarge",     # T4 16GB + more CPU
  "g5.xlarge",        # A10G 24GB (higher perf)
  "g5.2xlarge",       # A10G 24GB + more CPU
  "g4ad.xlarge",      # Radeon Pro V520 (AMD alternative)
  "g4ad.2xlarge",     # Radeon Pro V520 + more CPU
  "p3.2xlarge",       # V100 16GB (expensive but powerful)
]
```

**Why Diversification Works**:
- Different instance types = different Spot capacity pools
- Interruption in one pool doesn't affect others
- AWS automatically fails over to available pool
- Reduces interruption rate by **80-90%**

---

## 4. ComfyUI-Specific Best Practices on Spot

### Checkpoint Strategy for Long-Running Workflows

```python
# ComfyUI checkpoint script (every 30 seconds)
import os
import time
import json
import shutil
from pathlib import Path

CHECKPOINT_DIR = Path("/mnt/efs/comfyui/checkpoints")
STATE_FILE = Path("/tmp/comfyui_state.json")

def save_checkpoint(workflow_id, node_index, intermediate_outputs):
    """Save workflow state for resume after interruption"""
    checkpoint = {
        "workflow_id": workflow_id,
        "completed_nodes": node_index,
        "timestamp": time.time(),
        "outputs": intermediate_outputs
    }

    checkpoint_path = CHECKPOINT_DIR / f"{workflow_id}_checkpoint.json"
    with open(checkpoint_path, 'w') as f:
        json.dump(checkpoint, f)

    # Copy intermediate images to persistent storage (EFS)
    for node_id, output_path in intermediate_outputs.items():
        if Path(output_path).exists():
            dest = CHECKPOINT_DIR / f"{workflow_id}_{node_id}.png"
            shutil.copy2(output_path, dest)

def resume_from_checkpoint(workflow_id):
    """Resume workflow from last checkpoint"""
    checkpoint_path = CHECKPOINT_DIR / f"{workflow_id}_checkpoint.json"

    if not checkpoint_path.exists():
        return None

    with open(checkpoint_path, 'r') as f:
        return json.load(f)

# Hook into ComfyUI execution loop
class CheckpointInterceptor:
    def __init__(self, workflow_id):
        self.workflow_id = workflow_id
        self.last_checkpoint_time = 0
        self.checkpoint_interval = 30  # seconds

    def execute_node(self, node, inputs):
        # Execute node normally
        output = original_execute_node(node, inputs)

        # Checkpoint every 30 seconds
        if time.time() - self.last_checkpoint_time > self.checkpoint_interval:
            save_checkpoint(self.workflow_id, node.id, get_intermediate_outputs())
            self.last_checkpoint_time = time.time()

        return output
```

### Queue-Based Architecture (SQS + Spot Workers)

```
User Request → API Gateway → Lambda → SQS Queue
                                           ↓
                                    [Spot Worker Pool]
                                           ↓
                                    Process → S3 Upload
                                           ↓
                                    Notify → API Gateway
```

**Benefits**:
- Decouples request from processing
- Workers can be interrupted without losing work
- Auto-scaling based on queue depth
- Failed jobs auto-retry via SQS visibility timeout

**SQS Message Format**:
```json
{
  "workflow_id": "uuid-1234",
  "workflow_json": {...},
  "input_images": ["s3://bucket/input.png"],
  "output_bucket": "s3://bucket/outputs/",
  "checkpoint_enabled": true
}
```

**Worker Startup Script** (`user_data.sh`):
```bash
#!/bin/bash
# Install interruption handler
cat << 'EOF' > /opt/comfyui/interruption_handler.sh
#!/bin/bash
# Checkpoint current work and re-queue
curl -X POST http://localhost:8188/api/checkpoint
aws sqs send-message \
  --queue-url $SQS_QUEUE_URL \
  --message-body "$(cat /tmp/current_job.json)"
EOF

chmod +x /opt/comfyui/interruption_handler.sh

# Start interruption monitor (polls every 5s)
nohup /opt/comfyui/monitor_interruption.sh &

# Start ComfyUI worker
cd /opt/comfyui
python main.py --listen 0.0.0.0 --port 8188
```

### Persistent Storage Strategy (EFS)

**DO NOT use instance storage for:**
- Models (SDXL checkpoints, LoRAs, VAE)
- Input images
- Output images
- Checkpoints

**USE Amazon EFS (Elastic File System)**:
- Persistent across instance terminations
- Multi-AZ availability
- 1-second mount time
- ~$0.30/GB/month (vs losing hours of compute)

**EFS Mount in Launch Template**:
```bash
# Mount EFS on startup
sudo mount -t efs -o tls fs-12345678:/ /mnt/efs

# ComfyUI model paths
ln -s /mnt/efs/models /opt/comfyui/models
ln -s /mnt/efs/output /opt/comfyui/output
ln -s /mnt/efs/input /opt/comfyui/input
```

### Model Caching Strategy

```bash
# Pre-download models to EFS (one-time setup)
aws s3 sync s3://ziggie-models/ /mnt/efs/models/ --exclude "*" --include "*.safetensors"

# Models needed for ComfyUI SDXL workflows
/mnt/efs/models/
├── checkpoints/
│   └── sd_xl_base_1.0.safetensors       # 6.5 GB
├── vae/
│   └── sdxl_vae.safetensors             # 335 MB
├── loras/
│   ├── cat_character_lora.safetensors   # 144 MB
│   └── isometric_style_lora.safetensors # 144 MB
└── controlnet/
    └── control_v11p_sd15_canny.pth      # 1.5 GB
```

**Startup Time Optimization**:
- Models on EFS = instant availability (no download wait)
- First instance launch: ~2 minutes (NVIDIA driver install)
- Subsequent launches: ~30 seconds (AMI with drivers)

---

## 5. AMI Configuration with Pre-installed NVIDIA Drivers & ComfyUI

### Option 1: AWS Deep Learning AMI (Recommended for Quick Start)

**AMI ID**: `ami-0abcdef1234567890` (EU-North-1, changes quarterly)

**What's Included**:
- NVIDIA Driver 535.x
- CUDA 12.x
- cuDNN 8.x
- PyTorch, TensorFlow pre-installed
- Conda environments for Python 3.10/3.11

**Limitations**:
- Large AMI size (~50 GB)
- Includes unnecessary frameworks
- Not optimized for ComfyUI

### Option 2: Custom AMI (Recommended for Production)

**Build Script** (`build_comfyui_ami.sh`):

```bash
#!/bin/bash
set -e

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install NVIDIA Driver 535 (CUDA 12.2 compatible)
sudo apt-get install -y linux-headers-$(uname -r)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID | sed -e 's/\.//g')
wget https://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-drivers-535

# Install Docker + NVIDIA Container Toolkit
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Clone ComfyUI
cd /opt
sudo git clone https://github.com/comfyanonymous/ComfyUI.git comfyui
cd comfyui

# Install Python dependencies
sudo apt-get install -y python3.11 python3.11-venv
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt

# Install custom nodes
cd custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Manager.git
git clone https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet.git
cd ..

# Create systemd service
sudo cat << 'EOF' > /etc/systemd/system/comfyui.service
[Unit]
Description=ComfyUI Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/comfyui
ExecStart=/opt/comfyui/venv/bin/python main.py --listen 0.0.0.0 --port 8188
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable comfyui.service

# Install CloudWatch agent for monitoring
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb

# Clean up to reduce AMI size
sudo apt-get clean
sudo rm -rf /var/lib/apt/lists/*
rm -rf /home/ubuntu/.cache

echo "AMI build complete. Create AMI from this instance."
```

**Create AMI**:
```bash
# Launch base Ubuntu 22.04 instance
aws ec2 run-instances \
  --image-id ami-0d441f7d1b4a74a5f \
  --instance-type g4dn.xlarge \
  --key-name your-key \
  --user-data file://build_comfyui_ami.sh \
  --region eu-north-1

# Wait for build to complete (~15 minutes)
# SSH into instance, verify ComfyUI works
nvidia-smi
curl http://localhost:8188

# Create AMI
aws ec2 create-image \
  --instance-id i-1234567890abcdef0 \
  --name "ComfyUI-SDXL-v1.0-20251223" \
  --description "ComfyUI + NVIDIA Driver 535 + CUDA 12.2 + SDXL models" \
  --region eu-north-1
```

### Option 3: Docker Container (Most Flexible)

```dockerfile
# Dockerfile
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/comfyui
RUN git clone https://github.com/comfyanonymous/ComfyUI.git .

RUN python3.11 -m venv venv && \
    . venv/bin/activate && \
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 && \
    pip install -r requirements.txt

EXPOSE 8188
CMD ["/opt/comfyui/venv/bin/python", "main.py", "--listen", "0.0.0.0", "--port", "8188"]
```

**Run on Spot Instance**:
```bash
docker run --gpus all -p 8188:8188 \
  -v /mnt/efs/models:/opt/comfyui/models \
  -v /mnt/efs/output:/opt/comfyui/output \
  comfyui:latest
```

---

## 6. Interruption Monitoring & Checkpoint/Resume Implementation

### CloudWatch Monitoring for Spot Interruptions

**EventBridge Rule** (Terraform):
```hcl
resource "aws_cloudwatch_event_rule" "spot_interruption" {
  name        = "comfyui-spot-interruption"
  description = "Capture EC2 Spot Instance interruption warnings"

  event_pattern = jsonencode({
    source      = ["aws.ec2"]
    detail-type = ["EC2 Spot Instance Interruption Warning"]
  })
}

resource "aws_cloudwatch_event_target" "lambda_handler" {
  rule      = aws_cloudwatch_event_rule.spot_interruption.name
  target_id = "HandleSpotInterruption"
  arn       = aws_lambda_function.handle_interruption.arn
}
```

**Lambda Handler** (`handle_interruption.py`):
```python
import json
import boto3
import os

sqs = boto3.client('sqs')
ec2 = boto3.client('ec2')
QUEUE_URL = os.environ['SQS_QUEUE_URL']

def lambda_handler(event, context):
    """
    Handle Spot interruption warning:
    1. Retrieve current job from instance metadata
    2. Re-queue job to SQS
    3. Notify monitoring system
    """
    instance_id = event['detail']['instance-id']
    action = event['detail']['instance-action']

    print(f"Spot interruption warning: {instance_id} will be {action}")

    # Get instance tags to identify current job
    response = ec2.describe_tags(Filters=[
        {'Name': 'resource-id', 'Values': [instance_id]},
        {'Name': 'key', 'Values': ['CurrentJob']}
    ])

    if response['Tags']:
        job_id = response['Tags'][0]['Value']

        # Re-queue job (will be picked up by next available worker)
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps({
                'job_id': job_id,
                'status': 'interrupted',
                'resume_from_checkpoint': True
            }),
            MessageAttributes={
                'Priority': {'StringValue': 'HIGH', 'DataType': 'String'}
            }
        )

        print(f"Re-queued job {job_id} due to interruption")

    return {'statusCode': 200, 'body': 'Interruption handled'}
```

### Instance-Level Interruption Handler

**Startup Script** (`/opt/comfyui/monitor_interruption.sh`):
```bash
#!/bin/bash
# Monitor for Spot interruption warning (polls every 5 seconds)

CHECKPOINT_SCRIPT="/opt/comfyui/checkpoint.sh"
LOG_FILE="/var/log/comfyui/interruption.log"

while true; do
  # Get IMDSv2 token
  TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" \
    -H "X-aws-ec2-metadata-token-ttl-seconds: 21600" 2>/dev/null)

  # Check for interruption notice
  INTERRUPTION=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" -s \
    http://169.254.169.254/latest/meta-data/spot/instance-action 2>/dev/null)

  if [ -n "$INTERRUPTION" ]; then
    echo "$(date): Interruption detected - $INTERRUPTION" >> $LOG_FILE

    # Execute checkpoint script (user-defined)
    if [ -f "$CHECKPOINT_SCRIPT" ]; then
      echo "$(date): Executing checkpoint script" >> $LOG_FILE
      $CHECKPOINT_SCRIPT
    fi

    # Gracefully stop ComfyUI
    systemctl stop comfyui.service

    echo "$(date): Checkpoint complete, instance ready for termination" >> $LOG_FILE
    break
  fi

  sleep 5
done
```

**Checkpoint Script** (`/opt/comfyui/checkpoint.sh`):
```bash
#!/bin/bash
# Checkpoint ComfyUI workflow state to EFS

CHECKPOINT_DIR="/mnt/efs/comfyui/checkpoints"
CURRENT_JOB_FILE="/tmp/current_job.json"

# Save current workflow state via ComfyUI API
curl -X POST http://localhost:8188/api/checkpoint \
  -H "Content-Type: application/json" \
  -d '{"action": "save_state"}' \
  -o $CHECKPOINT_DIR/workflow_state.json

# Tag instance with checkpoint status
INSTANCE_ID=$(ec2-metadata --instance-id | cut -d " " -f 2)
aws ec2 create-tags \
  --resources $INSTANCE_ID \
  --tags Key=CheckpointStatus,Value=Completed \
  --region eu-north-1

# Re-queue current job if active
if [ -f "$CURRENT_JOB_FILE" ]; then
  aws sqs send-message \
    --queue-url $SQS_QUEUE_URL \
    --message-body file://$CURRENT_JOB_FILE \
    --region eu-north-1
fi

echo "Checkpoint saved to $CHECKPOINT_DIR"
```

### Resume Logic in Worker

```python
# Worker startup: check for interrupted jobs
def check_for_resume(workflow_id):
    checkpoint_path = Path(f"/mnt/efs/comfyui/checkpoints/{workflow_id}_checkpoint.json")

    if checkpoint_path.exists():
        with open(checkpoint_path, 'r') as f:
            checkpoint = json.load(f)

        # Resume from last completed node
        print(f"Resuming workflow {workflow_id} from node {checkpoint['completed_nodes']}")
        return checkpoint

    return None

# Main worker loop
while True:
    # Poll SQS for jobs
    messages = sqs.receive_message(QueueUrl=QUEUE_URL, MaxNumberOfMessages=1)

    if 'Messages' in messages:
        message = messages['Messages'][0]
        job = json.loads(message['Body'])

        # Check for existing checkpoint
        checkpoint = check_for_resume(job['workflow_id'])

        if checkpoint:
            # Resume from checkpoint
            execute_workflow_from_checkpoint(job, checkpoint)
        else:
            # Start from beginning
            execute_workflow(job)

        # Delete message after successful processing
        sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=message['ReceiptHandle'])
```

---

## 7. Lambda Integration for Spot Request Management

### Architecture Overview

```
User Request → API Gateway → Lambda (Job Creator)
                                 ↓
                            SQS Queue (Job Queue)
                                 ↓
                      Lambda (Spot Fleet Manager)
                                 ↓
                      Auto Scaling Group (Spot Workers)
                                 ↓
                      ComfyUI Processing → S3 Upload
                                 ↓
                      Lambda (Job Completion Handler)
                                 ↓
                      API Gateway (Notify User)
```

### Lambda Function: Spot Fleet Manager

```python
# spot_fleet_manager.py
import boto3
import os

autoscaling = boto3.client('autoscaling')
sqs = boto3.client('sqs')
cloudwatch = boto3.client('cloudwatch')

ASG_NAME = os.environ['ASG_NAME']
QUEUE_URL = os.environ['SQS_QUEUE_URL']

def lambda_handler(event, context):
    """
    Scale Spot Fleet based on SQS queue depth
    - Queue depth > 10: Scale up
    - Queue depth == 0 for 5 min: Scale down to 0
    """

    # Get queue depth
    queue_attrs = sqs.get_queue_attributes(
        QueueUrl=QUEUE_URL,
        AttributeNames=['ApproximateNumberOfMessages']
    )
    queue_depth = int(queue_attrs['Attributes']['ApproximateNumberOfMessages'])

    # Get current ASG capacity
    asg_response = autoscaling.describe_auto_scaling_groups(
        AutoScalingGroupNames=[ASG_NAME]
    )
    current_capacity = asg_response['AutoScalingGroups'][0]['DesiredCapacity']

    # Calculate desired capacity
    # 1 worker per 5 jobs (assuming 5 min per job)
    desired_capacity = min(5, max(0, queue_depth // 5))

    # Update ASG if needed
    if desired_capacity != current_capacity:
        autoscaling.set_desired_capacity(
            AutoScalingGroupName=ASG_NAME,
            DesiredCapacity=desired_capacity,
            HonorCooldown=False
        )

        print(f"Scaled ASG from {current_capacity} to {desired_capacity} (queue depth: {queue_depth})")

    # Publish metric to CloudWatch
    cloudwatch.put_metric_data(
        Namespace='ComfyUI',
        MetricData=[
            {
                'MetricName': 'QueueDepth',
                'Value': queue_depth,
                'Unit': 'Count'
            },
            {
                'MetricName': 'WorkerCount',
                'Value': desired_capacity,
                'Unit': 'Count'
            }
        ]
    )

    return {
        'statusCode': 200,
        'body': {
            'queue_depth': queue_depth,
            'current_capacity': current_capacity,
            'desired_capacity': desired_capacity
        }
    }
```

**EventBridge Rule** (run every minute):
```hcl
resource "aws_cloudwatch_event_rule" "spot_fleet_scaler" {
  name                = "comfyui-spot-fleet-scaler"
  description         = "Scale Spot Fleet based on queue depth"
  schedule_expression = "rate(1 minute)"
}

resource "aws_cloudwatch_event_target" "spot_fleet_scaler_target" {
  rule      = aws_cloudwatch_event_rule.spot_fleet_scaler.name
  target_id = "SpotFleetManager"
  arn       = aws_lambda_function.spot_fleet_manager.arn
}
```

### Lambda Function: Job Creator

```python
# job_creator.py
import json
import boto3
import uuid
import os

sqs = boto3.client('sqs')
s3 = boto3.client('s3')

QUEUE_URL = os.environ['SQS_QUEUE_URL']
INPUT_BUCKET = os.environ['INPUT_BUCKET']

def lambda_handler(event, context):
    """
    Create ComfyUI job from API Gateway request
    - Upload input image to S3
    - Create job message in SQS
    - Return job ID to user
    """

    # Parse request
    body = json.loads(event['body'])
    workflow_json = body['workflow']
    input_image_base64 = body['input_image']

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Upload input image to S3
    input_key = f"inputs/{job_id}/input.png"
    s3.put_object(
        Bucket=INPUT_BUCKET,
        Key=input_key,
        Body=base64.b64decode(input_image_base64),
        ContentType='image/png'
    )

    # Create SQS message
    job_message = {
        'job_id': job_id,
        'workflow': workflow_json,
        'input_s3_key': input_key,
        'output_s3_prefix': f"outputs/{job_id}/",
        'created_at': int(time.time())
    }

    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(job_message)
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'job_id': job_id,
            'status': 'queued',
            'estimated_wait_time': '5 minutes'
        })
    }
```

### Lambda Function: Job Completion Handler

```python
# job_completion_handler.py
import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
s3 = boto3.client('s3')

JOBS_TABLE = os.environ['JOBS_TABLE']
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event, context):
    """
    Handle job completion notification from worker
    - Update job status in DynamoDB
    - Send SNS notification to user
    - Generate presigned URL for output
    """

    # Parse S3 event (triggered when worker uploads output)
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # Extract job ID from S3 key (outputs/{job_id}/output.png)
        job_id = key.split('/')[1]

        # Update DynamoDB
        table = dynamodb.Table(JOBS_TABLE)
        table.update_item(
            Key={'job_id': job_id},
            UpdateExpression='SET #status = :status, output_s3_key = :key, completed_at = :timestamp',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'completed',
                ':key': key,
                ':timestamp': int(time.time())
            }
        )

        # Generate presigned URL (valid for 1 hour)
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=3600
        )

        # Send SNS notification
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f'ComfyUI Job {job_id} Completed',
            Message=json.dumps({
                'job_id': job_id,
                'status': 'completed',
                'output_url': presigned_url
            })
        )

        print(f"Job {job_id} completed: {presigned_url}")

    return {'statusCode': 200}
```

---

## 8. Cost Optimization Strategies

### Strategy 1: Scheduled Scaling (Business Hours)

```python
# Scale down during off-hours (00:00-08:00 UTC)
SCHEDULE = {
    '0 0 * * *': {'min': 0, 'max': 0, 'desired': 0},     # Midnight: scale to 0
    '0 8 * * *': {'min': 0, 'max': 5, 'desired': 1},     # 8 AM: scale to 1
    '0 18 * * *': {'min': 0, 'max': 10, 'desired': 2},   # 6 PM: scale to 2 (peak)
}
```

**Savings**: 33% if no overnight processing (16 hrs/day vs 24 hrs/day)

### Strategy 2: Spot + On-Demand Mix (90/10)

```hcl
instances_distribution {
  on_demand_base_capacity                  = 0
  on_demand_percentage_above_base_capacity = 10  # 90% Spot, 10% On-Demand
  spot_allocation_strategy                 = "price-capacity-optimized"
}
```

**Benefits**:
- 90% of fleet runs on Spot (cheap)
- 10% on On-Demand (guarantees minimum capacity)
- Auto-failover if Spot unavailable

**Cost**: 90% × $0.18 + 10% × $0.526 = **$0.2146/hr** (vs $0.526 On-Demand = 59% savings)

### Strategy 3: EFS Infrequent Access (IA) for Old Models

```bash
# Move models not accessed in 30 days to EFS IA (80% cheaper)
aws efs put-lifecycle-configuration \
  --file-system-id fs-12345678 \
  --lifecycle-policies \
    TransitionToIA=AFTER_30_DAYS \
    TransitionToPrimaryStorageClass=AFTER_1_ACCESS
```

**Savings**:
- EFS Standard: $0.30/GB/month
- EFS IA: $0.025/GB/month (92% cheaper)
- If 50 GB of models rarely accessed: **$13.75/mo savings**

### Strategy 4: S3 Lifecycle Policies for Outputs

```json
{
  "Rules": [{
    "Id": "DeleteOldOutputs",
    "Status": "Enabled",
    "Filter": {"Prefix": "outputs/"},
    "Expiration": {"Days": 30},
    "Transitions": [{
      "Days": 7,
      "StorageClass": "INTELLIGENT_TIERING"
    }]
  }]
}
```

**Savings**: Auto-delete outputs after 30 days (free up storage)

### Strategy 5: Reserved Instances for Baseline Capacity (Advanced)

If you ALWAYS need at least 1 worker 24/7:

| Option | Cost | When to Use |
|--------|------|-------------|
| On-Demand g4dn.xlarge 24/7 | $379/mo | Never (too expensive) |
| Spot g4dn.xlarge 24/7 | $137/mo | Good for bursty workloads |
| Reserved g4dn.xlarge (1-year, no upfront) | $241/mo | If usage > 80% uptime |
| Spot + Reserved hybrid | $137/mo + $0 baseline | Best of both worlds |

**Recommendation**: Start with 100% Spot, consider Reserved after 3 months if usage is consistent.

---

## 9. Monitoring & Alerting

### CloudWatch Dashboards

**Key Metrics to Track**:

| Metric | Threshold | Alert Action |
|--------|-----------|--------------|
| **SQS Queue Depth** | > 20 | Scale up workers |
| **Spot Interruption Rate** | > 10%/day | Diversify instance types |
| **GPU Utilization** | < 50% | Scale down or switch to smaller instance |
| **EFS Throughput** | > 100 MB/s | Upgrade to Provisioned Throughput |
| **Worker Idle Time** | > 5 min | Scale down |
| **Job Failure Rate** | > 5% | Investigate errors |

**CloudWatch Dashboard JSON** (`comfyui_dashboard.json`):
```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["ComfyUI", "QueueDepth", {"stat": "Average"}],
          ["ComfyUI", "WorkerCount", {"stat": "Average"}]
        ],
        "period": 60,
        "stat": "Average",
        "region": "eu-north-1",
        "title": "Queue Depth vs Worker Count"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/EC2", "CPUUtilization", {"stat": "Average"}],
          ["AWS/EC2", "GPUUtilization", {"stat": "Average"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "eu-north-1",
        "title": "Instance Utilization"
      }
    },
    {
      "type": "log",
      "properties": {
        "query": "SOURCE '/aws/lambda/spot_fleet_manager' | fields @timestamp, @message | filter @message like /Scaled ASG/ | sort @timestamp desc | limit 20",
        "region": "eu-north-1",
        "title": "Recent Scaling Events"
      }
    }
  ]
}
```

### SNS Alerts

```hcl
resource "aws_cloudwatch_metric_alarm" "high_queue_depth" {
  alarm_name          = "comfyui-high-queue-depth"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "QueueDepth"
  namespace           = "ComfyUI"
  period              = 300
  statistic           = "Average"
  threshold           = 20
  alarm_description   = "Queue depth exceeded 20 jobs"
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "high_spot_interruption" {
  alarm_name          = "comfyui-high-spot-interruption-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "SpotInterruptionRate"
  namespace           = "ComfyUI"
  period              = 86400  # 24 hours
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "Spot interruption rate > 10% in 24 hours"
  alarm_actions       = [aws_sns_topic.alerts.arn]
}
```

---

## 10. Production Deployment Checklist

### Phase 1: Initial Setup (Week 1)

- [ ] Create VPC with 2 AZs in EU-North-1
- [ ] Create EFS file system for models/checkpoints
- [ ] Build custom AMI with ComfyUI + NVIDIA drivers
- [ ] Create SQS queue for job management
- [ ] Create S3 buckets for inputs/outputs
- [ ] Deploy Lambda functions (job creator, fleet manager, completion handler)
- [ ] Create DynamoDB table for job tracking

### Phase 2: Spot Fleet Configuration (Week 1)

- [ ] Create Launch Template with ComfyUI AMI
- [ ] Configure Auto Scaling Group with Spot + On-Demand mix (90/10)
- [ ] Add 8+ instance types for diversification
- [ ] Configure `price-capacity-optimized` allocation strategy
- [ ] Set up EventBridge rules for interruption warnings
- [ ] Test interruption handler script

### Phase 3: Monitoring & Alerting (Week 2)

- [ ] Create CloudWatch Dashboard
- [ ] Set up SNS topic for alerts
- [ ] Configure alarms (queue depth, interruption rate, GPU utilization)
- [ ] Enable CloudWatch Logs for Lambda functions
- [ ] Enable VPC Flow Logs for network debugging

### Phase 4: Testing (Week 2)

- [ ] Test single job execution (end-to-end)
- [ ] Test batch processing (10+ jobs)
- [ ] **Simulate Spot interruption** (terminate instance during job)
- [ ] Verify checkpoint/resume works correctly
- [ ] Test scaling up (queue 50 jobs)
- [ ] Test scaling down (idle for 10 minutes)
- [ ] Load test with 100+ concurrent jobs

### Phase 5: Cost Optimization (Week 3)

- [ ] Review CloudWatch metrics for utilization
- [ ] Adjust scaling policies based on real usage
- [ ] Configure EFS IA for old models
- [ ] Set up S3 lifecycle policies for outputs
- [ ] Compare actual costs vs estimates

### Phase 6: Production Launch (Week 3)

- [ ] Deploy API Gateway with rate limiting
- [ ] Enable CloudFront for output delivery
- [ ] Configure IAM roles with least privilege
- [ ] Enable AWS Config for compliance tracking
- [ ] Create runbook for common issues
- [ ] Train team on monitoring/troubleshooting

---

## 11. Troubleshooting Guide

### Issue 1: Spot Interruption Rate > 10%/day

**Symptoms**: Frequent job restarts, high re-queue rate

**Diagnosis**:
```bash
# Check interruption history
aws ec2 describe-spot-instance-requests \
  --filters "Name=state,Values=closed" \
  --query 'SpotInstanceRequests[*].[Status.Code,Status.UpdateTime]' \
  --region eu-north-1
```

**Root Causes**:
1. Limited instance type diversification (< 5 types)
2. Using `lowest-price` allocation strategy
3. Single AZ deployment

**Fixes**:
- Add 5+ more instance types to ASG overrides
- Switch to `price-capacity-optimized` allocation
- Enable all 3 AZs in EU-North-1

### Issue 2: Jobs Failing to Resume After Interruption

**Symptoms**: Jobs restart from beginning, checkpoint not loaded

**Diagnosis**:
```bash
# Check EFS mount
df -h | grep /mnt/efs

# Check checkpoint files
ls -lh /mnt/efs/comfyui/checkpoints/

# Check worker logs
tail -f /var/log/comfyui/worker.log
```

**Root Causes**:
1. EFS not mounted at startup
2. Checkpoint file permissions incorrect
3. Resume logic bug in worker code

**Fixes**:
- Add EFS mount to Launch Template user_data
- Fix file permissions: `chmod 644 /mnt/efs/comfyui/checkpoints/*`
- Test resume logic with manual interruption

### Issue 3: High Costs (> $500/mo)

**Symptoms**: AWS bill higher than expected

**Diagnosis**:
```bash
# Check ASG current capacity
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names comfyui-spot-workers \
  --query 'AutoScalingGroups[0].[MinSize,DesiredCapacity,MaxSize]'

# Check running instances
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=ComfyUI-Spot-Worker" "Name=instance-state-name,Values=running" \
  --query 'Reservations[*].Instances[*].[InstanceId,InstanceType,LaunchTime]'

# Check CloudWatch billing metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Billing \
  --metric-name EstimatedCharges \
  --dimensions Name=ServiceName,Value=AmazonEC2 \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Maximum
```

**Root Causes**:
1. Instances not scaling down during idle
2. EFS Provisioned Throughput enabled (expensive)
3. On-Demand instances running instead of Spot
4. Large EFS storage (old outputs not deleted)

**Fixes**:
- Review scaling policies: `desired_capacity` should be 0 when queue empty
- Disable EFS Provisioned Throughput (use Bursting)
- Verify 90% Spot allocation in ASG
- Enable S3 lifecycle policies to delete outputs > 30 days

### Issue 4: Slow Job Processing (> 10 min/job)

**Symptoms**: Jobs taking 2x expected time

**Diagnosis**:
```bash
# Check GPU utilization
nvidia-smi dmon -s u

# Check EFS throughput
aws cloudwatch get-metric-statistics \
  --namespace AWS/EFS \
  --metric-name ThroughputUtilization \
  --dimensions Name=FileSystemId,Value=fs-12345678 \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average

# Check network bandwidth
iftop -i eth0
```

**Root Causes**:
1. Model loading from EFS too slow (bandwidth limit)
2. NVIDIA driver version mismatch with PyTorch
3. Wrong instance type (CPU bottleneck)

**Fixes**:
- Upgrade EFS to Provisioned Throughput (200 MB/s = $1,200/mo, only if needed)
- Update NVIDIA driver to latest stable (535.x for CUDA 12.2)
- Switch to larger instance type (g4dn.2xlarge or g5.2xlarge)

---

## 12. Cost Summary & Recommendation

### Baseline Scenario: 8 hrs/day, 20 days/mo, g4dn.xlarge

| Component | On-Demand Cost | Spot Cost | Savings |
|-----------|----------------|-----------|---------|
| **Compute (g4dn.xlarge)** | $84.16/mo | $29.60/mo | **$54.56/mo (65%)** |
| **EFS (50 GB models)** | $15.00/mo | $15.00/mo | $0 |
| **S3 (100 GB outputs)** | $2.30/mo | $2.30/mo | $0 |
| **Data Transfer (100 GB out)** | $9.00/mo | $9.00/mo | $0 |
| **Lambda (100K invocations)** | $0.20/mo | $0.20/mo | $0 |
| **SQS (1M requests)** | $0.40/mo | $0.40/mo | $0 |
| **CloudWatch (basic)** | $3.00/mo | $3.00/mo | $0 |
| **TOTAL** | **$114.06/mo** | **$59.50/mo** | **$54.56/mo (48%)** |

### High-Volume Scenario: 24/7, g5.xlarge, 200 jobs/day

| Component | On-Demand Cost | Spot Cost | Savings |
|-----------|----------------|-----------|---------|
| **Compute (g5.xlarge × 3)** | $2,172.96/mo | $756.00/mo | **$1,416.96/mo (65%)** |
| **EFS (200 GB models)** | $60.00/mo | $60.00/mo | $0 |
| **S3 (1 TB outputs)** | $23.00/mo | $23.00/mo | $0 |
| **Data Transfer (500 GB out)** | $45.00/mo | $45.00/mo | $0 |
| **Lambda (1M invocations)** | $2.00/mo | $2.00/mo | $0 |
| **SQS (10M requests)** | $4.00/mo | $4.00/mo | $0 |
| **CloudWatch (detailed)** | $10.00/mo | $10.00/mo | $0 |
| **TOTAL** | **$2,316.96/mo** | **$900.00/mo** | **$1,416.96/mo (61%)** |

---

## 13. Final Recommendations for Ziggie Cloud

### Phase 1: MVP (Weeks 1-2) - **Recommended**

**Goal**: Prove Spot Instances work for ComfyUI workloads with minimal investment

**Configuration**:
- 1 Auto Scaling Group (min=0, max=3, desired=0)
- Instance types: g4dn.xlarge, g4dn.2xlarge, g5.xlarge
- Allocation: 100% Spot (no On-Demand)
- Region: EU-North-1 (2 AZs)
- Storage: EFS Standard (50 GB models)
- Scaling: Queue-based (1 worker per 5 jobs)

**Expected Costs**: **$60-100/mo** (depending on usage)

**Success Criteria**:
- [ ] Job completion rate > 95%
- [ ] Spot interruption rate < 10%/day
- [ ] Cost savings > 60% vs On-Demand
- [ ] Checkpoint/resume works 100% of time

### Phase 2: Production (Weeks 3-4)

**Goal**: Scale to production workload (100+ jobs/day)

**Configuration**:
- Auto Scaling Group (min=0, max=10, desired=auto)
- Instance types: 8+ types for diversification
- Allocation: 90% Spot, 10% On-Demand (reliability)
- Region: EU-North-1 (3 AZs)
- Storage: EFS Standard (200 GB) + IA for old models
- Scaling: Queue-based with scheduled downtime (00:00-08:00 UTC)
- Monitoring: CloudWatch Dashboard + SNS alerts

**Expected Costs**: **$300-600/mo** (100-200 jobs/day)

**Success Criteria**:
- [ ] Job completion rate > 99%
- [ ] P99 latency < 10 minutes
- [ ] Cost < $3/job
- [ ] Zero manual intervention required

### Phase 3: Optimization (Month 2+)

**Goal**: Maximize cost efficiency and performance

**Optimizations**:
- Fine-tune scaling policies based on real usage patterns
- Implement EFS IA for models accessed < 1x/week
- Add S3 Intelligent-Tiering for outputs
- Consider Reserved Instances if baseline usage > 80%
- Profile ComfyUI workflows to optimize node execution

**Expected Costs**: **$200-400/mo** (same workload, 30-40% further savings)

---

## 14. Next Steps

1. **Week 1 Actions**:
   - [ ] Review this research document with team
   - [ ] Create AWS account (if not exists) or set up dedicated sub-account
   - [ ] Set up billing alerts ($100, $300, $500 thresholds)
   - [ ] Build custom ComfyUI AMI (use build script in Section 5)
   - [ ] Create EFS file system and upload SDXL models

2. **Week 2 Actions**:
   - [ ] Deploy Spot Fleet infrastructure (Terraform)
   - [ ] Deploy Lambda functions (job creator, fleet manager)
   - [ ] Test single job end-to-end
   - [ ] Simulate Spot interruption and verify checkpoint works

3. **Week 3 Actions**:
   - [ ] Load test with 50 concurrent jobs
   - [ ] Review costs vs estimates
   - [ ] Deploy to production
   - [ ] Monitor for 1 week

4. **Month 2 Actions**:
   - [ ] Analyze 30-day cost/usage data
   - [ ] Optimize based on learnings
   - [ ] Document operational runbook

---

## 15. References & Additional Resources

### AWS Documentation
- [EC2 Spot Instances Best Practices](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-best-practices.html)
- [Spot Instance Interruption Notices](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-instance-termination-notices.html)
- [Auto Scaling Groups with Spot & On-Demand](https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-mixed-instances-groups.html)
- [EFS Performance](https://docs.aws.amazon.com/efs/latest/ug/performance.html)

### AWS Pricing Calculators
- [EC2 Pricing](https://aws.amazon.com/ec2/pricing/)
- [Spot Instance Pricing History](https://aws.amazon.com/ec2/spot/pricing/)
- [EFS Pricing](https://aws.amazon.com/efs/pricing/)

### ComfyUI Resources
- [ComfyUI GitHub](https://github.com/comfyanonymous/ComfyUI)
- [ComfyUI Custom Nodes](https://github.com/ltdrdata/ComfyUI-Manager)
- [SDXL Models (HuggingFace)](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0)

### Third-Party Tools
- [ec2-spot-interruption-handler](https://github.com/aws/aws-ec2-spot-interruption-handler) - Official AWS tool
- [kube-spot-termination-notice-handler](https://github.com/kube-aws/kube-spot-termination-notice-handler) - Kubernetes version
- [spot-sig-handler](https://github.com/mumoshu/spot-sig-handler) - Lightweight handler

---

**Document Version**: 1.0
**Last Updated**: 2025-12-23
**Next Review**: 2025-01-23 (after 30 days of production usage)
