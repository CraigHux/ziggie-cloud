# AWS + Hostinger Master Setup Checklist

> **Generated**: 2025-12-22
> **Purpose**: Complete AI-controlled cloud infrastructure for Ziggie Ecosystem
> **Target Cost**: <$50/month normal ops, <$150/month peak GPU usage

---

## Pre-Setup Requirements

### Accounts & Credentials
- [ ] AWS Account: 7851-8665-9442 (EU-North-1 Stockholm)
- [ ] AWS CLI configured with profile "ziggie"
- [ ] Hostinger account active
- [ ] Domain configured (optional but recommended)
- [ ] SSH key pair generated for VPS access

### Local Development
- [ ] Python 3.11+ installed
- [ ] boto3 installed (`pip install boto3`)
- [ ] Ansible installed (`pip install ansible`)
- [ ] Pulumi installed (optional, for IaC)

---

## Phase 1: Hostinger VPS Setup (Week 1)

### 1.1 Provision VPS
- [ ] Purchase KVM 4 plan (£9.99/mo)
  - 4 vCPU, 16GB RAM, 200GB NVMe SSD
  - Ubuntu 22.04 LTS
  - Location: Choose closest to EU-North-1 (European DC)
- [ ] Note VPS IP address: `__________________`
- [ ] Set root password (temporary)

### 1.2 Initial Security Hardening
```bash
# SSH into VPS
ssh root@YOUR_VPS_IP

# Update system
apt update && apt upgrade -y

# Create non-root user
adduser ziggie
usermod -aG sudo ziggie

# Configure SSH
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd

# Setup firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 5678/tcp  # n8n
ufw allow 8080/tcp  # MCP Gateway
ufw enable
```
- [ ] Non-root user created
- [ ] SSH key authentication enabled
- [ ] Root login disabled
- [ ] Firewall configured

### 1.3 Install Docker & Docker Compose
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
usermod -aG docker ziggie

# Install Docker Compose
apt install docker-compose-plugin -y

# Verify
docker --version
docker compose version
```
- [ ] Docker installed
- [ ] Docker Compose installed
- [ ] ziggie user added to docker group

### 1.4 Deploy Core Services Stack
```bash
# Create project directory
mkdir -p /opt/ziggie
cd /opt/ziggie

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # n8n Workflow Orchestration
  n8n:
    image: n8nio/n8n:latest
    container_name: ziggie-n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_HOST=${VPS_DOMAIN}
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://${VPS_DOMAIN}/
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - postgres
      - redis

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: ziggie-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_USER=ziggie
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=ziggie
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ziggie"]
      interval: 10s
      timeout: 5s
      retries: 5

  # MongoDB for Agent State
  mongodb:
    image: mongo:7
    container_name: ziggie-mongodb
    restart: unless-stopped
    environment:
      - MONGO_INITDB_ROOT_USERNAME=ziggie
      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_PASSWORD}
    volumes:
      - mongodb_data:/data/db
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache & Message Broker
  redis:
    image: redis:7-alpine
    container_name: ziggie-redis
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # MCP Gateway Hub
  mcp-gateway:
    image: node:20-alpine
    container_name: ziggie-mcp-gateway
    restart: unless-stopped
    working_dir: /app
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=production
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
      - AWS_REGION=eu-north-1
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    volumes:
      - ./mcp-gateway:/app
    command: npm start
    depends_on:
      - redis

  # Ziggie API Backend
  ziggie-api:
    image: python:3.11-slim
    container_name: ziggie-api
    restart: unless-stopped
    working_dir: /app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://ziggie:${POSTGRES_PASSWORD}@postgres:5432/ziggie
      - MONGODB_URL=mongodb://ziggie:${MONGO_PASSWORD}@mongodb:27017
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
      - AWS_REGION=eu-north-1
    volumes:
      - ./api:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000
    depends_on:
      - postgres
      - mongodb
      - redis

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: ziggie-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - certbot_data:/var/www/certbot
    depends_on:
      - n8n
      - mcp-gateway
      - ziggie-api

  # Prometheus Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: ziggie-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus

  # Grafana Dashboard
  grafana:
    image: grafana/grafana:latest
    container_name: ziggie-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus

volumes:
  n8n_data:
  postgres_data:
  mongodb_data:
  redis_data:
  prometheus_data:
  grafana_data:
  certbot_data:
EOF

# Create .env file
cat > .env << 'EOF'
VPS_DOMAIN=ziggie.yourdomain.com
N8N_PASSWORD=CHANGE_ME_SECURE_PASSWORD_1
POSTGRES_PASSWORD=CHANGE_ME_SECURE_PASSWORD_2
MONGO_PASSWORD=CHANGE_ME_SECURE_PASSWORD_3
REDIS_PASSWORD=CHANGE_ME_SECURE_PASSWORD_4
GRAFANA_PASSWORD=CHANGE_ME_SECURE_PASSWORD_5
AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_KEY
EOF

# Start services
docker compose up -d
```
- [ ] docker-compose.yml created
- [ ] .env file configured with secure passwords
- [ ] All containers running: `docker compose ps`

### 1.5 SSL Certificate Setup
```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Obtain certificate (after DNS is configured)
certbot --nginx -d ziggie.yourdomain.com

# Auto-renewal
systemctl enable certbot.timer
```
- [ ] Domain DNS pointing to VPS IP
- [ ] SSL certificate obtained
- [ ] Auto-renewal enabled

### 1.6 Verify VPS Services
- [ ] n8n accessible at https://domain:5678
- [ ] MCP Gateway responding at :8080
- [ ] Ziggie API health check at :8000/health
- [ ] Grafana accessible at :3000
- [ ] All containers healthy: `docker compose ps`

---

## Phase 2: AWS Foundation (Week 2)

### 2.1 AWS CLI Configuration
```bash
# Configure AWS CLI with Ziggie profile
aws configure --profile ziggie

# Verify
aws sts get-caller-identity --profile ziggie
```
- [ ] AWS CLI configured
- [ ] Profile "ziggie" working
- [ ] Region set to eu-north-1

### 2.2 IAM Setup (Least Privilege)
```bash
# Create policy file
cat > ziggie-ec2-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:StartInstances",
                "ec2:StopInstances",
                "ec2:DescribeInstances",
                "ec2:DescribeInstanceStatus"
            ],
            "Resource": "arn:aws:ec2:eu-north-1:785186659442:instance/*",
            "Condition": {
                "StringEquals": {
                    "ec2:ResourceTag/Project": "Ziggie"
                }
            }
        }
    ]
}
EOF

# Create IAM policy
aws iam create-policy \
    --policy-name ZiggieEC2Control \
    --policy-document file://ziggie-ec2-policy.json \
    --profile ziggie

# Create IAM user for programmatic access
aws iam create-user --user-name ziggie-automation --profile ziggie

# Attach policy
aws iam attach-user-policy \
    --user-name ziggie-automation \
    --policy-arn arn:aws:iam::785186659442:policy/ZiggieEC2Control \
    --profile ziggie

# Create access keys
aws iam create-access-key --user-name ziggie-automation --profile ziggie
```
- [ ] ZiggieEC2Control policy created
- [ ] ziggie-automation user created
- [ ] Access keys generated and stored securely

### 2.3 S3 Bucket Setup
```bash
# Create buckets
aws s3 mb s3://ziggie-assets-eu --region eu-north-1 --profile ziggie
aws s3 mb s3://ziggie-backups-eu --region eu-north-1 --profile ziggie
aws s3 mb s3://ziggie-models-eu --region eu-north-1 --profile ziggie

# Enable versioning on backups
aws s3api put-bucket-versioning \
    --bucket ziggie-backups-eu \
    --versioning-configuration Status=Enabled \
    --profile ziggie

# Set lifecycle policy (delete old versions after 30 days)
cat > lifecycle-policy.json << 'EOF'
{
    "Rules": [
        {
            "ID": "DeleteOldVersions",
            "Status": "Enabled",
            "NoncurrentVersionExpiration": {
                "NoncurrentDays": 30
            }
        },
        {
            "ID": "MoveToGlacier",
            "Status": "Enabled",
            "Transitions": [
                {
                    "Days": 90,
                    "StorageClass": "GLACIER"
                }
            ]
        }
    ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
    --bucket ziggie-backups-eu \
    --lifecycle-configuration file://lifecycle-policy.json \
    --profile ziggie
```
- [ ] ziggie-assets-eu bucket created
- [ ] ziggie-backups-eu bucket created (versioned)
- [ ] ziggie-models-eu bucket created
- [ ] Lifecycle policies applied

### 2.4 Secrets Manager Setup
```bash
# Store Hostinger VPS credentials
aws secretsmanager create-secret \
    --name ziggie/hostinger/ssh \
    --description "Hostinger VPS SSH credentials" \
    --secret-string '{"host":"YOUR_VPS_IP","user":"ziggie","key_path":"/path/to/key"}' \
    --profile ziggie

# Store database passwords
aws secretsmanager create-secret \
    --name ziggie/hostinger/databases \
    --description "Hostinger database credentials" \
    --secret-string '{"postgres":"PASS1","mongodb":"PASS2","redis":"PASS3"}' \
    --profile ziggie

# Store API keys
aws secretsmanager create-secret \
    --name ziggie/api-keys \
    --description "Third-party API keys" \
    --secret-string '{"openai":"","anthropic":"","elevenlabs":""}' \
    --profile ziggie
```
- [ ] SSH credentials stored
- [ ] Database passwords stored
- [ ] API keys stored

### 2.5 Budget Alerts Setup
```bash
# Create budget with alerts
cat > budget.json << 'EOF'
{
    "BudgetName": "ZiggieMonthlyBudget",
    "BudgetLimit": {
        "Amount": "100",
        "Unit": "USD"
    },
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST",
    "CostFilters": {}
}
EOF

cat > notifications.json << 'EOF'
[
    {
        "Notification": {
            "NotificationType": "ACTUAL",
            "ComparisonOperator": "GREATER_THAN",
            "Threshold": 50,
            "ThresholdType": "PERCENTAGE"
        },
        "Subscribers": [
            {
                "SubscriptionType": "EMAIL",
                "Address": "YOUR_EMAIL@domain.com"
            }
        ]
    },
    {
        "Notification": {
            "NotificationType": "ACTUAL",
            "ComparisonOperator": "GREATER_THAN",
            "Threshold": 80,
            "ThresholdType": "PERCENTAGE"
        },
        "Subscribers": [
            {
                "SubscriptionType": "EMAIL",
                "Address": "YOUR_EMAIL@domain.com"
            }
        ]
    },
    {
        "Notification": {
            "NotificationType": "FORECASTED",
            "ComparisonOperator": "GREATER_THAN",
            "Threshold": 100,
            "ThresholdType": "PERCENTAGE"
        },
        "Subscribers": [
            {
                "SubscriptionType": "EMAIL",
                "Address": "YOUR_EMAIL@domain.com"
            }
        ]
    }
]
EOF

aws budgets create-budget \
    --account-id 785186659442 \
    --budget file://budget.json \
    --notifications-with-subscribers file://notifications.json \
    --profile ziggie
```
- [ ] Monthly budget created ($100)
- [ ] 50% alert configured
- [ ] 80% alert configured
- [ ] Forecast alert configured

### 2.6 VPC Configuration
```bash
# Create VPC
aws ec2 create-vpc \
    --cidr-block 10.0.0.0/16 \
    --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=ziggie-vpc},{Key=Project,Value=Ziggie}]' \
    --profile ziggie

# Note VPC ID: vpc-________________

# Create subnet
aws ec2 create-subnet \
    --vpc-id vpc-YOUR_VPC_ID \
    --cidr-block 10.0.1.0/24 \
    --availability-zone eu-north-1a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=ziggie-subnet-public}]' \
    --profile ziggie

# Create Internet Gateway
aws ec2 create-internet-gateway \
    --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=ziggie-igw}]' \
    --profile ziggie

# Attach to VPC
aws ec2 attach-internet-gateway \
    --internet-gateway-id igw-YOUR_IGW_ID \
    --vpc-id vpc-YOUR_VPC_ID \
    --profile ziggie
```
- [ ] VPC created (10.0.0.0/16)
- [ ] Public subnet created
- [ ] Internet Gateway attached
- [ ] Route table configured

---

## Phase 3: AWS GPU Infrastructure (Week 3)

### 3.1 Security Group for GPU Instances
```bash
# Create security group
aws ec2 create-security-group \
    --group-name ziggie-gpu-sg \
    --description "Security group for Ziggie GPU instances" \
    --vpc-id vpc-YOUR_VPC_ID \
    --profile ziggie

# Note Security Group ID: sg-________________

# Add rules
aws ec2 authorize-security-group-ingress \
    --group-id sg-YOUR_SG_ID \
    --protocol tcp \
    --port 22 \
    --cidr YOUR_VPS_IP/32 \
    --profile ziggie

aws ec2 authorize-security-group-ingress \
    --group-id sg-YOUR_SG_ID \
    --protocol tcp \
    --port 8188 \
    --cidr YOUR_VPS_IP/32 \
    --profile ziggie
```
- [ ] Security group created
- [ ] SSH access from VPS only
- [ ] ComfyUI port from VPS only

### 3.2 Launch Template for GPU Instances
```bash
# Create launch template
cat > launch-template.json << 'EOF'
{
    "LaunchTemplateName": "ziggie-gpu-template",
    "LaunchTemplateData": {
        "ImageId": "ami-0c94855ba95c71c99",
        "InstanceType": "g4dn.xlarge",
        "KeyName": "ziggie-key",
        "SecurityGroupIds": ["sg-YOUR_SG_ID"],
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "VolumeSize": 100,
                    "VolumeType": "gp3",
                    "DeleteOnTermination": true
                }
            }
        ],
        "TagSpecifications": [
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": "ziggie-gpu"},
                    {"Key": "Project", "Value": "Ziggie"},
                    {"Key": "AutoShutdown", "Value": "true"}
                ]
            }
        ],
        "UserData": "BASE64_ENCODED_STARTUP_SCRIPT"
    }
}
EOF

aws ec2 create-launch-template \
    --cli-input-json file://launch-template.json \
    --profile ziggie
```
- [ ] Launch template created
- [ ] g4dn.xlarge configured
- [ ] 100GB gp3 storage
- [ ] Auto-shutdown tag enabled

### 3.3 Spot Instance Request (Cost Savings)
```bash
# Request spot instance (60-70% cheaper)
aws ec2 request-spot-instances \
    --instance-count 1 \
    --type "one-time" \
    --launch-specification '{
        "ImageId": "ami-0c94855ba95c71c99",
        "InstanceType": "g4dn.xlarge",
        "KeyName": "ziggie-key",
        "SecurityGroupIds": ["sg-YOUR_SG_ID"],
        "SubnetId": "subnet-YOUR_SUBNET_ID"
    }' \
    --profile ziggie
```
- [ ] Spot pricing verified (~$0.15-0.20/hr vs $0.52/hr on-demand)
- [ ] Spot instance launch tested

### 3.4 Auto-Shutdown Lambda Function
```python
# auto_shutdown.py - Deploy as Lambda
import boto3
import datetime

def lambda_handler(event, context):
    ec2 = boto3.client('ec2', region_name='eu-north-1')

    # Find instances with AutoShutdown tag
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:AutoShutdown', 'Values': ['true']},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            launch_time = instance['LaunchTime']

            # Check if running for more than 2 hours
            running_hours = (datetime.datetime.now(launch_time.tzinfo) - launch_time).total_seconds() / 3600

            if running_hours > 2:
                print(f"Stopping instance {instance_id} (running {running_hours:.1f} hours)")
                ec2.stop_instances(InstanceIds=[instance_id])

    return {'statusCode': 200, 'body': 'Shutdown check complete'}
```
- [ ] Lambda function created
- [ ] EventBridge rule (every 15 minutes)
- [ ] IAM role with EC2 permissions

### 3.5 ComfyUI AMI Setup
```bash
# Launch base instance
aws ec2 run-instances \
    --image-id ami-0c94855ba95c71c99 \
    --instance-type g4dn.xlarge \
    --key-name ziggie-key \
    --security-group-ids sg-YOUR_SG_ID \
    --subnet-id subnet-YOUR_SUBNET_ID \
    --profile ziggie

# SSH in and install ComfyUI
# (After connecting to instance)
sudo apt update && sudo apt upgrade -y
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt

# Install models (SDXL, etc.)
# ...

# Create AMI from configured instance
aws ec2 create-image \
    --instance-id i-YOUR_INSTANCE_ID \
    --name "ziggie-comfyui-ami" \
    --description "ComfyUI with SDXL models pre-installed" \
    --profile ziggie
```
- [ ] Base GPU instance launched
- [ ] ComfyUI installed
- [ ] SDXL models downloaded
- [ ] Custom AMI created
- [ ] AMI ID noted: ami-________________

---

## Phase 4: Integration & Testing (Week 4)

### 4.1 MCP Gateway AWS Integration
```javascript
// mcp-gateway/aws-bridge.js
const AWS = require('aws-sdk');

const ec2 = new AWS.EC2({ region: 'eu-north-1' });

async function startGPUInstance() {
    const params = {
        InstanceIds: ['i-YOUR_GPU_INSTANCE_ID']
    };

    const result = await ec2.startInstances(params).promise();
    console.log('GPU instance starting:', result);

    // Wait for running state
    await ec2.waitFor('instanceRunning', params).promise();

    // Get public IP
    const describe = await ec2.describeInstances(params).promise();
    return describe.Reservations[0].Instances[0].PublicIpAddress;
}

async function stopGPUInstance() {
    const params = {
        InstanceIds: ['i-YOUR_GPU_INSTANCE_ID']
    };

    await ec2.stopInstances(params).promise();
    console.log('GPU instance stopped');
}

module.exports = { startGPUInstance, stopGPUInstance };
```
- [ ] AWS SDK configured in MCP Gateway
- [ ] Start/stop functions working
- [ ] IP address retrieval working

### 4.2 n8n Workflow Integration
- [ ] Create "Start GPU" workflow
- [ ] Create "Stop GPU" workflow
- [ ] Create "Generate Asset" workflow (full pipeline)
- [ ] Webhook triggers configured

### 4.3 Infrastructure Health Checks
```bash
# Test VPS connectivity
curl -s https://your-domain/health

# Test n8n
curl -s https://your-domain:5678/healthz

# Test MCP Gateway
curl -s http://your-domain:8080/health

# Test AWS GPU start
aws ec2 start-instances --instance-ids i-YOUR_ID --profile ziggie

# Verify ComfyUI accessible
curl -s http://GPU_IP:8188/system_stats
```
- [ ] VPS health endpoint responding
- [ ] n8n accessible and authenticated
- [ ] MCP Gateway responding
- [ ] GPU instance starts successfully
- [ ] ComfyUI accessible on GPU

### 4.4 End-to-End Pipeline Test
1. [ ] Trigger asset generation from local Claude Code
2. [ ] MCP Gateway receives request
3. [ ] n8n workflow starts GPU instance
4. [ ] ComfyUI generates asset
5. [ ] Asset uploaded to S3
6. [ ] GPU instance auto-stops
7. [ ] Asset URL returned to Claude Code

### 4.5 Monitoring & Alerting
- [ ] Prometheus scraping all endpoints
- [ ] Grafana dashboards configured
- [ ] Alert rules for:
  - [ ] Service down
  - [ ] High CPU/memory
  - [ ] GPU cost threshold
  - [ ] Failed generation jobs

---

## Post-Setup Verification

### Security Checklist
- [ ] No root SSH access
- [ ] SSH key authentication only
- [ ] Firewall rules minimal
- [ ] Secrets in AWS Secrets Manager
- [ ] IAM least privilege verified
- [ ] SSL certificates valid
- [ ] Budget alerts configured

### Performance Checklist
- [ ] VPS response time <100ms
- [ ] GPU startup time <3 minutes
- [ ] Asset generation <60 seconds
- [ ] API latency <200ms

### Documentation Checklist
- [ ] All passwords documented securely
- [ ] IP addresses recorded
- [ ] AMI IDs recorded
- [ ] Instance IDs recorded
- [ ] Runbook for common operations

---

## Quick Reference

### Key URLs
| Service | URL |
|---------|-----|
| n8n | https://domain:5678 |
| MCP Gateway | https://domain:8080 |
| Ziggie API | https://domain:8000 |
| Grafana | https://domain:3000 |
| ComfyUI (GPU) | http://GPU_IP:8188 |

### AWS Resource IDs
| Resource | ID |
|----------|-----|
| VPC | vpc-________________ |
| Subnet | subnet-________________ |
| Security Group | sg-________________ |
| GPU Instance | i-________________ |
| ComfyUI AMI | ami-________________ |

### Hostinger VPS
| Field | Value |
|-------|-------|
| IP Address | ________________ |
| SSH User | ziggie |
| SSH Port | 22 |

### Cost Tracking
| Month | AWS | Hostinger | Total |
|-------|-----|-----------|-------|
| Dec 2024 | $__ | £9.99 | $__ |
| Jan 2025 | $__ | £9.99 | $__ |

---

## Emergency Procedures

### GPU Cost Runaway
```bash
# Immediately stop all GPU instances
aws ec2 stop-instances \
    --instance-ids $(aws ec2 describe-instances \
        --filters "Name=instance-type,Values=g4dn.*" \
        --query "Reservations[].Instances[].InstanceId" \
        --output text --profile ziggie) \
    --profile ziggie
```

### VPS Recovery
```bash
# SSH to VPS and restart all services
ssh ziggie@VPS_IP
cd /opt/ziggie
docker compose down
docker compose up -d
```

### Backup Restoration
```bash
# Restore from S3 backup
aws s3 sync s3://ziggie-backups-eu/latest /opt/ziggie/restore --profile ziggie
```

---

## ADDENDUM: L1 Agent Research Findings (2025-12-23)

> **Research Method**: 6 parallel L1 agents with web search
> **Documentation**: 19 files, 10,000+ lines of comprehensive guides
> **Status**: Ready for implementation

### New Services Identified

#### AWS Bedrock (NOT in original checklist)
**Purpose**: LLM alternative to reduce OpenAI costs by 63%
**Monthly Cost**: $7-8 (vs $20+ OpenAI)
**Benefits**:
- Claude 3.5 Sonnet for code/reasoning tasks
- Claude 3 Haiku for simple chatbots
- EU data residency (GDPR compliant)
- No vendor lock-in

**Documentation**:
- `AWS-BEDROCK-EXECUTIVE-SUMMARY.md`
- `AWS-BEDROCK-QUICKSTART.md`

---

### Updated Cost Optimization (2025 Prices)

#### EC2 Spot Instances
| Instance | On-Demand | Spot (2025) | Savings |
|----------|-----------|-------------|---------|
| g4dn.xlarge | $0.526/hr | $0.16-0.20/hr | 62-70% |
| g5.xlarge | $1.006/hr | $0.30-0.40/hr | 60-70% |

**Documentation**: `AWS_EC2_SPOT_INSTANCES_RESEARCH.md`

#### VPC Endpoints (Cost Saver)
| Endpoint Type | Cost | Savings vs NAT |
|---------------|------|----------------|
| S3 Gateway | FREE | $32/month |
| Secrets Manager Interface | $7.20/month | $24.80/month |

**Total Network Savings**: $56.80/month

**Documentation**: `AWS_VPC_INDEX.md`

---

### Enhanced Security Configuration

#### Security Groups (IP Whitelisting)
```bash
# GPU Instance - Only allow VPS access
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxx \
    --protocol tcp \
    --port 8188 \
    --cidr 82.25.112.73/32 \
    --profile ziggie
```

#### 6-Layer Security Architecture
1. **Network**: Security Groups (IP whitelist)
2. **Transport**: TLS 1.3
3. **Application**: AWS Signature v4
4. **Identity**: IAM least privilege
5. **Data**: Encryption at rest
6. **Monitoring**: CloudTrail + fail2ban

**Documentation**: `AWS_VPC_NETWORKING_BEST_PRACTICES.md`

---

### n8n Workflow Patterns

#### GPU Instance Lifecycle
```
Trigger → Lambda Start → Health Check → ComfyUI API → S3 Upload → Done
                                ↓
           CloudWatch Alarm → Lambda Stop (10 min idle)
```

#### Bedrock Integration
```
n8n HTTP Node → AWS Bedrock API → Claude 3.5 Sonnet → Response
```

**Documentation**:
- `AWS_LAMBDA_GPU_AUTO_SHUTDOWN_GUIDE.md`
- `AWS-BEDROCK-CODE-EXAMPLES.md`

---

### Revised Monthly Cost Projections

| Configuration | Original Est. | Optimized (2025) | Savings |
|---------------|---------------|------------------|---------|
| Normal Ops | <$50 | $60-70 | Realistic |
| Peak GPU | <$150 | $90-136 | 40% better |
| With Bedrock | N/A | +$7-8 | 63% LLM savings |

---

### Complete Documentation Index

```
c:\Ziggie\
├── AWS-ZIGGIE-INTEGRATION-MASTER-PLAN.md    # NEW: Executive summary
├── AWS-HOSTINGER-MASTER-SETUP-CHECKLIST.md  # Original + this addendum
│
├── Lambda & GPU Auto-Shutdown
│   ├── AWS_LAMBDA_GPU_AUTO_SHUTDOWN_GUIDE.md
│   ├── AWS_GPU_COST_OPTIMIZATION_SUMMARY.md
│   ├── AWS_GPU_AUTOSHUTDOWN_QUICK_REFERENCE.md
│   └── AWS_GPU_AUTOSHUTDOWN_DELIVERABLES.md
│
├── S3 Storage
│   └── AWS-S3-INTEGRATION-GUIDE.md
│
├── Secrets Manager
│   ├── AWS_SECRETS_MANAGER_RESEARCH.md
│   └── AWS_SECRETS_QUICKSTART.md
│
├── Bedrock LLM
│   ├── AWS-BEDROCK-RESEARCH.md
│   ├── AWS-BEDROCK-EXECUTIVE-SUMMARY.md
│   ├── AWS-BEDROCK-QUICKSTART.md
│   ├── AWS-BEDROCK-COST-CALCULATOR.md
│   ├── AWS-BEDROCK-CODE-EXAMPLES.md
│   ├── AWS-BEDROCK-QUICK-REFERENCE.md
│   └── AWS-BEDROCK-INDEX.md
│
├── EC2 Spot Instances
│   └── AWS_EC2_SPOT_INSTANCES_RESEARCH.md
│
└── VPC Networking
    ├── AWS_VPC_NETWORKING_BEST_PRACTICES.md
    ├── AWS_VPC_QUICK_REFERENCE.md
    └── AWS_VPC_INDEX.md
```

---

### Implementation Priority (Updated)

1. **Week 1**: Phase 1-2 (VPS is already done via Ziggie Cloud)
2. **Week 1**: Phase 2 AWS Foundation + Secrets Manager
3. **Week 2**: Phase 3 S3 + GPU Infrastructure
4. **Week 2**: Phase 4 n8n Integration
5. **Week 3**: Phase 5 Bedrock (optional, high ROI)
6. **Ongoing**: Monitoring + cost optimization

---

*Last Updated: 2025-12-23*
*Version: 2.0 (L1 Agent Research Addendum)*
*Research Agents: 6 parallel L1 agents*
*Documentation: 19 files, 10,000+ lines*
