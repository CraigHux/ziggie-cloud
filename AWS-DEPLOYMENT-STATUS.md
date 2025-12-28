# AWS DEPLOYMENT STATUS
## Ziggie Ecosystem - Stage 7.5 Complete

> **Last Updated**: 2025-12-24 08:35 UTC
> **Gate 7.5**: PASSED
> **Phase 7.5.6**: COMPLETE

---

## Executive Summary

AWS Foundation is now **OPERATIONAL**. All Phase 7.5 objectives completed.

| Metric | Value |
|--------|-------|
| AWS Account | 785186659442 |
| Region | eu-north-1 (Stockholm) |
| IAM User | ziggie-cli |
| S3 Bucket | ziggie-assets-prod |
| Secrets | 2 stored |
| Status | **DEPLOYED** |

---

## Phase Completion Status

| Phase | Name | Status | Duration |
|-------|------|--------|----------|
| 7.5.1 | Account Verification | ✅ COMPLETE | 5 min |
| 7.5.2 | IAM Setup | ✅ COMPLETE | 10 min |
| 7.5.3 | S3 Asset Storage | ✅ COMPLETE | 5 min |
| 7.5.4 | Secrets Manager | ✅ COMPLETE | 5 min |
| **Gate 7.5** | **AWS Foundation** | ✅ **PASSED** | **25 min** |
| 7.5.5 | Lambda Auto-Shutdown | ✅ COMPLETE | 10 min |
| 7.5.6 | EC2 Spot GPU | ✅ COMPLETE | 15 min |
| 7.5.7 | Bedrock LLM | ✅ COMPLETE | 10 min |

---

## Deployed Resources

### IAM User: ziggie-cli
- **ARN**: `arn:aws:iam::785186659442:user/ziggie-cli`
- **Access Key**: `[REDACTED-AWS-ACCESS-KEY]`
- **Permissions**: AdministratorAccess
- **Console Access**: Disabled (CLI only)
- **MFA**: Not configured (recommended for production)

### S3 Bucket: ziggie-assets-prod
- **Region**: eu-north-1
- **Versioning**: Enabled
- **Encryption**: AES256 (default)
- **Structure**:
  - `game-assets/` - Intelligent Tiering enabled
  - `generated/` - Standard storage
  - `backups/` - Glacier after 90 days
- **CORS**: Configured for ziggie.cloud + localhost

### Secrets Manager
| Secret Name | Purpose |
|-------------|---------|
| `ziggie/anthropic-api-key` | Claude API access |
| `ziggie/youtube-api-key` | YouTube Data API v3 |

### Lambda: ziggie-gpu-auto-shutdown

- **ARN**: `arn:aws:lambda:eu-north-1:785186659442:function:ziggie-gpu-auto-shutdown`
- **Runtime**: Python 3.12
- **Trigger**: CloudWatch Events (every 5 minutes)
- **Purpose**: Auto-stop idle GPU instances (CPU < 5% for 15 min)
- **Notifications**: SNS topic `ziggie-alerts`
- **IAM Role**: `ziggie-lambda-gpu-shutdown-role`

### SNS Topic: ziggie-alerts

- **ARN**: `arn:aws:sns:eu-north-1:785186659442:ziggie-alerts`
- **Purpose**: GPU shutdown notifications

### CloudWatch Events Rule: ziggie-gpu-idle-check

- **Schedule**: Every 5 minutes
- **Target**: Lambda `ziggie-gpu-auto-shutdown`
- **State**: ENABLED

### EC2 Spot GPU Infrastructure

#### Launch Template: ziggie-gpu-spot
- **Template ID**: `lt-092030abcfccb629a`
- **AMI**: `ami-0beaf1366830fe924` (Deep Learning Base OSS Nvidia Driver GPU AMI Ubuntu 22.04)
- **Default Instance Type**: g4dn.xlarge (T4 16GB GPU)
- **Volume**: 100GB gp3
- **Auto-Setup**: ComfyUI via user data script

#### Key Pair: ziggie-gpu-key
- **Key ID**: `key-0a6a11df7c24907d5`
- **Location**: `C:\Ziggie\aws-config\ziggie-gpu-key.pem`

#### Security Group: ziggie-gpu-sg
- **Group ID**: `sg-07c0d59d11ac62192`
- **Inbound Rules**:
  - SSH (22) from 0.0.0.0/0
  - ComfyUI (8188) from 0.0.0.0/0
  - HTTPS (443) from 0.0.0.0/0

#### Available GPU Instance Types (eu-north-1)
| Type | GPU | VRAM | vCPU | RAM | Spot Price |
|------|-----|------|------|-----|------------|
| g4dn.xlarge | T4 | 16GB | 4 | 16GB | ~$0.18/hr |
| g4dn.2xlarge | T4 | 16GB | 8 | 32GB | ~$0.24/hr |
| g5.xlarge | A10G | 24GB | 4 | 16GB | ~$0.43/hr |

---

## Configuration Files Created

| File | Purpose |
|------|---------|
| `C:\Ziggie\aws-config\lifecycle.json` | S3 lifecycle rules |
| `C:\Ziggie\aws-config\cors.json` | S3 CORS configuration |
| `C:\Ziggie\aws-config\get-secret.ps1` | PowerShell secret retrieval |
| `C:\Ziggie\aws-config\lambda-trust-policy.json` | Lambda IAM trust policy |
| `C:\Ziggie\aws-config\lambda-gpu-shutdown-policy.json` | Lambda IAM permissions |
| `C:\Ziggie\aws-config\lambda\lambda_function.py` | GPU auto-shutdown Lambda code |
| `C:\Ziggie\aws-config\gpu-launch-template.json` | EC2 Spot GPU launch template |
| `C:\Ziggie\aws-config\gpu-userdata.sh` | ComfyUI bootstrap script |
| `C:\Ziggie\aws-config\ziggie-gpu-key.pem` | SSH private key for GPU instances |
| `C:\Ziggie\aws-config\launch-gpu.ps1` | Launch GPU spot instance |
| `C:\Ziggie\aws-config\stop-gpu.ps1` | Stop/terminate GPU instances |
| `C:\Ziggie\aws-config\list-gpu.ps1` | List GPU instance status |
| `C:\Ziggie\aws-config\bedrock-chat.ps1` | Bedrock chat helper |
| `C:\Ziggie\aws-config\bedrock-game-content.ps1` | Game content generator |
| `C:\Ziggie\aws-config\ziggie_bedrock.py` | Python Bedrock integration |

### Bedrock LLM (Phase 7.5.7)

- **Region**: eu-north-1
- **Available Models**:
  - Amazon Nova Lite (`eu.amazon.nova-lite-v1:0`) - Fast, cost-effective
  - Amazon Nova Pro (`eu.amazon.nova-pro-v1:0`) - Higher quality
  - Amazon Nova Micro (`eu.amazon.nova-micro-v1:0`) - Fastest, cheapest
  - Claude models (require EULA acceptance in AWS Console)

- **Helper Scripts**:
  - `bedrock-chat.ps1` - General chat with Nova models
  - `bedrock-game-content.ps1` - Generate items, dialogue, quests, lore
  - `ziggie_bedrock.py` - Python module for integration

---

## CLI Commands Reference

```powershell
# Verify AWS identity
aws sts get-caller-identity

# List S3 bucket contents
aws s3 ls s3://ziggie-assets-prod/

# Upload file to S3
aws s3 cp ./file.png s3://ziggie-assets-prod/game-assets/

# Retrieve secret
aws secretsmanager get-secret-value --secret-id ziggie/anthropic-api-key --query SecretString --output text

# List all secrets
aws secretsmanager list-secrets --query 'SecretList[*].Name'

# GPU Instance Management (PowerShell)
.\launch-gpu.ps1                    # Launch spot GPU instance
.\launch-gpu.ps1 -InstanceType g5.xlarge -MaxPrice 0.50  # Launch A10G
.\list-gpu.ps1                      # List running GPU instances
.\stop-gpu.ps1                      # Stop all GPU instances
.\stop-gpu.ps1 i-xxxxx              # Stop specific instance

# SSH to GPU instance
ssh -i C:\Ziggie\aws-config\ziggie-gpu-key.pem ubuntu@<public-ip>

# Bedrock LLM (PowerShell)
.\bedrock-chat.ps1 -Prompt "Hello world"           # Chat with Nova Lite
.\bedrock-chat.ps1 -Prompt "Question" -Model nova-pro  # Use Nova Pro
.\bedrock-game-content.ps1 -Type item -Name "Whisker Blade"  # Generate item
.\bedrock-game-content.ps1 -Type quest -Name "The Lost Catnip"  # Generate quest

# Bedrock LLM (Python)
python -c "from ziggie_bedrock import BedrockClient; c=BedrockClient(); print(c.chat('Hello'))"
```

---

## Cost Estimate (Monthly)

| Service | Estimated Cost |
|---------|----------------|
| S3 Storage (10GB) | $2-5 |
| S3 Requests | $1-3 |
| Secrets Manager (2 secrets) | $0.80 |
| Lambda (288 invocations/day) | $0 (free tier) |
| SNS Notifications | $0 (free tier) |
| CloudWatch Events | $0 (free tier) |
| **Base Total** | **~$4-9/month** |
| | |
| **GPU Spot (on-demand)** | |
| g4dn.xlarge (T4) | ~$0.18/hr |
| g4dn.2xlarge (T4) | ~$0.24/hr |
| g5.xlarge (A10G) | ~$0.43/hr |
| *Example: 10 hrs/month g4dn.xlarge* | *~$1.80* |

---

## Next Steps (Optional)

| Phase | Service | Priority | Status |
|-------|---------|----------|--------|
| 7.5.5 | Lambda Auto-Shutdown | MEDIUM | ✅ COMPLETE |
| 7.5.6 | EC2 Spot (GPU) | LOW | ✅ COMPLETE |
| 7.5.7 | Bedrock LLM | LOW | ✅ COMPLETE |

---

## Security Recommendations

1. **Enable MFA** on ziggie-cli user (AWS Console → IAM → Users → Security credentials)
2. **Rotate API Keys** - The keys stored in Secrets Manager should be rotated at Anthropic/Google
3. **Restrict IAM Policy** - Replace AdministratorAccess with least-privilege policies
4. **Enable CloudTrail** - For audit logging of all AWS API calls

---

*AWS Foundation Stage 7.5 completed by Claude Code on 2025-12-24*
*Phase 7.5.6 EC2 Spot GPU added on 2025-12-24*
*Phase 7.5.7 Bedrock LLM added on 2025-12-24*
