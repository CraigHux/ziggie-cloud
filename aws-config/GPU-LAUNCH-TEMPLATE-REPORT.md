# Ziggie GPU Spot Launch Template - Complete Configuration Report

> **Report Date**: 2025-12-27
> **AWS Region**: eu-north-1
> **Template Status**: CONFIGURED AND READY

---

## Executive Summary

The `ziggie-gpu-spot` launch template is **fully configured** and ready for production use. All necessary components including the launch template, security group, user data script, and management scripts are in place.

---

## 1. Launch Template Configuration

### Template Details

| Property | Value |
|----------|-------|
| **Template Name** | `ziggie-gpu-spot` |
| **Version Description** | Ziggie GPU Spot Instance with ComfyUI |
| **AMI ID** | `ami-0beaf1366830fe924` (Deep Learning AMI - Ubuntu) |
| **Instance Type** | `g4dn.xlarge` |
| **Key Pair** | `ziggie-gpu-key` |
| **Security Group** | `sg-07c0d59d11ac62192` (ziggie-gpu-sg) |
| **Storage** | 100 GB gp3 SSD (delete on termination) |

### Spot Configuration

| Property | Value |
|----------|-------|
| **Market Type** | Spot |
| **Spot Instance Type** | one-time |
| **Max Price** | Default (current spot price) |
| **Interruption Behavior** | terminate |

### Tags Applied

| Tag Key | Tag Value | Resource Type |
|---------|-----------|---------------|
| Name | Ziggie-GPU-Worker | instance |
| Project | Ziggie | instance, volume |
| Type | GPU | instance |
| Environment | Production | instance |

### Metadata Configuration

| Property | Value |
|----------|-------|
| **IMDSv2** | Required (HttpTokens: required) |
| **Hop Limit** | 2 |
| **HTTP Endpoint** | Enabled |

---

## 2. Security Group Configuration

**Security Group ID**: `sg-07c0d59d11ac62192`

### Recommended Inbound Rules

| Port | Protocol | Source | Description |
|------|----------|--------|-------------|
| 22 | TCP | Your IP / VPS IP | SSH access |
| 8188 | TCP | Your IP / VPS IP | ComfyUI Web UI |

### Recommended Outbound Rules

| Port | Protocol | Destination | Description |
|------|----------|-------------|-------------|
| All | All | 0.0.0.0/0 | Internet access for packages |

---

## 3. User Data Script Summary

**File**: `C:\Ziggie\aws-config\gpu-userdata.sh`

The bootstrap script performs the following actions:

1. **System Update**
   - `apt-get update && upgrade`
   - Install git, python3-pip, python3-venv

2. **ComfyUI Installation**
   - Clone ComfyUI repository
   - Create Python virtual environment
   - Install PyTorch with CUDA 12.1 support
   - Install ComfyUI requirements
   - Install ComfyUI-Manager for easy node management

3. **Service Configuration**
   - Create systemd service for ComfyUI
   - Auto-start on boot
   - Restart on failure (10 sec delay)
   - Listen on 0.0.0.0:8188

4. **AWS Integration**
   - Install AWS CLI if not present
   - Tag instance with Status=Ready when complete

**Bootstrap Time**: Approximately 5-10 minutes

---

## 4. Management Scripts

### Launch GPU Instance

**File**: `C:\Ziggie\aws-config\launch-gpu.ps1`

```powershell
# Usage
.\launch-gpu.ps1 [-InstanceType g4dn.xlarge] [-MaxPrice 0.25]

# Example: Launch with default settings
.\launch-gpu.ps1

# Example: Launch with 2xlarge and custom max price
.\launch-gpu.ps1 -InstanceType g4dn.2xlarge -MaxPrice 0.40
```

**Default Subnet**: `subnet-040ca7f02458c6f42` (eu-north-1c)

### Stop GPU Instance

**File**: `C:\Ziggie\aws-config\stop-gpu.ps1`

```powershell
# Usage: Stop specific instance
.\stop-gpu.ps1 i-1234567890abcdef0

# Usage: List and stop all Ziggie GPU instances
.\stop-gpu.ps1
```

### List GPU Instances

**File**: `C:\Ziggie\aws-config\list-gpu.ps1`

```powershell
# Usage: Show all Ziggie GPU instances and current spot prices
.\list-gpu.ps1
```

---

## 5. Cost Estimates

### g4dn.xlarge Specifications

| Spec | Value |
|------|-------|
| **GPU** | 1x NVIDIA T4 (16 GB) |
| **vCPU** | 4 |
| **RAM** | 16 GB |
| **Storage** | 125 GB NVMe SSD (instance) |

### Pricing (eu-north-1, approximate)

| Pricing Model | Hourly Rate | Daily (8 hrs) | Monthly |
|---------------|-------------|---------------|---------|
| On-Demand | ~$0.52 | ~$4.16 | ~$374 |
| Spot | ~$0.15-0.20 | ~$1.20-1.60 | ~$36-60 |
| **Savings** | **70%** | - | - |

---

## 6. Lambda Auto-Shutdown Protection

**Lambda Function**: `ziggie-gpu-auto-shutdown`
**Status**: ACTIVE

The auto-shutdown Lambda monitors all Ziggie GPU instances and terminates them after 30 minutes of idle time. This prevents runaway costs from forgotten instances.

**Trigger**: EventBridge rule (5-minute schedule)
**Alert**: SNS topic `ziggie-alerts`

---

## 7. Quick Start Commands

### Launch a GPU Instance

```powershell
# Navigate to config directory
cd C:\Ziggie\aws-config

# Launch with defaults
.\launch-gpu.ps1

# Or use full AWS CLI path
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" ec2 run-instances `
    --launch-template LaunchTemplateName=ziggie-gpu-spot `
    --instance-market-options "MarketType=spot,SpotOptions={MaxPrice=0.25,SpotInstanceType=one-time}" `
    --subnet-id subnet-040ca7f02458c6f42 `
    --region eu-north-1
```

### Connect to Instance

```bash
# SSH connection
ssh -i C:\Ziggie\aws-config\ziggie-gpu-key.pem ubuntu@<PUBLIC_IP>

# Access ComfyUI (after ~5 min bootstrap)
http://<PUBLIC_IP>:8188
```

### Check Instance Status

```powershell
.\list-gpu.ps1

# Or direct AWS CLI
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" ec2 describe-instances `
    --filters "Name=tag:Project,Values=Ziggie" "Name=tag:Type,Values=GPU" `
    --query "Reservations[*].Instances[*].[InstanceId,PublicIpAddress,State.Name]" `
    --output table `
    --region eu-north-1
```

### Terminate Instance

```powershell
.\stop-gpu.ps1 i-1234567890abcdef0

# Or direct AWS CLI
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" ec2 terminate-instances `
    --instance-ids i-1234567890abcdef0 `
    --region eu-north-1
```

---

## 8. Verification Commands

### Check Launch Template Exists

```powershell
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" ec2 describe-launch-templates `
    --launch-template-names ziggie-gpu-spot `
    --region eu-north-1
```

### Get Launch Template Details

```powershell
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" ec2 describe-launch-template-versions `
    --launch-template-name ziggie-gpu-spot `
    --region eu-north-1 `
    --output json
```

### Check Security Group

```powershell
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" ec2 describe-security-groups `
    --group-ids sg-07c0d59d11ac62192 `
    --region eu-north-1
```

### Check Current Spot Prices

```powershell
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" ec2 describe-spot-price-history `
    --instance-types g4dn.xlarge g4dn.2xlarge g5.xlarge `
    --product-descriptions "Linux/UNIX" `
    --region eu-north-1 `
    --max-items 3 `
    --output table
```

---

## 9. Files Reference

| File | Location | Purpose |
|------|----------|---------|
| Launch Template JSON | `C:\Ziggie\aws-config\gpu-launch-template.json` | Template definition |
| User Data Script | `C:\Ziggie\aws-config\gpu-userdata.sh` | Bootstrap script |
| SSH Key | `C:\Ziggie\aws-config\ziggie-gpu-key.pem` | Instance access |
| Launch Script | `C:\Ziggie\aws-config\launch-gpu.ps1` | PowerShell launcher |
| Stop Script | `C:\Ziggie\aws-config\stop-gpu.ps1` | Instance terminator |
| List Script | `C:\Ziggie\aws-config\list-gpu.ps1` | Status checker |

---

## 10. Troubleshooting

### Template Not Found Error

If the launch template doesn't exist in AWS, create it:

```powershell
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" ec2 create-launch-template `
    --cli-input-json file://C:\Ziggie\aws-config\gpu-launch-template.json `
    --region eu-north-1
```

### Security Group Not Found

Create the security group:

```powershell
# Create security group
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" ec2 create-security-group `
    --group-name ziggie-gpu-sg `
    --description "Ziggie GPU Instance Security Group" `
    --vpc-id <YOUR_VPC_ID> `
    --region eu-north-1

# Add SSH rule
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" ec2 authorize-security-group-ingress `
    --group-name ziggie-gpu-sg `
    --protocol tcp `
    --port 22 `
    --cidr <YOUR_IP>/32 `
    --region eu-north-1

# Add ComfyUI rule
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" ec2 authorize-security-group-ingress `
    --group-name ziggie-gpu-sg `
    --protocol tcp `
    --port 8188 `
    --cidr <YOUR_IP>/32 `
    --region eu-north-1
```

### Spot Instance Capacity Error

If you receive a capacity error, try:
1. A different availability zone (change subnet)
2. A different instance type (g4dn.2xlarge, g5.xlarge)
3. Increase max spot price

---

## Document Metadata

| Field | Value |
|-------|-------|
| Document ID | GPU-LAUNCH-TEMPLATE-REPORT |
| Created | 2025-12-27 |
| Author | AWS Infrastructure Agent |
| Status | COMPLETE |
| Template Status | CONFIGURED |
| Location | `C:\Ziggie\aws-config\GPU-LAUNCH-TEMPLATE-REPORT.md` |

---

**END OF REPORT**
