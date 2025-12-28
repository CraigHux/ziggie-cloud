# AWS INTEGRATION STAGE
## Ziggie Ecosystem Cloud Services Integration

> **Document ID**: ZIGGIE-AWS-INTEGRATION-V1.0
> **Created**: 2025-12-24
> **Purpose**: Detailed AWS integration as Stage 7.5 of the integration plan
> **Prerequisites**: Gate 6 passed, AWS account configured

---

## EXECUTIVE SUMMARY

This document extends the Claude Code Integration Plan with comprehensive AWS integration. AWS services provide:

- **S3**: Asset storage and CDN delivery
- **Secrets Manager**: Secure credential management
- **Lambda**: GPU auto-shutdown for cost control
- **EC2 Spot**: Cost-effective GPU compute
- **Bedrock**: Alternative LLM provider

### AWS Integration Scope

| Service | Purpose | Monthly Cost (Est.) | Priority |
|---------|---------|---------------------|----------|
| S3 + CloudFront | Asset storage/CDN | $10-30 | HIGH |
| Secrets Manager | Credential security | $5-10 | CRITICAL |
| Lambda | Auto-shutdown GPU | $0-5 | HIGH |
| EC2 Spot (GPU) | ComfyUI batch | $20-100 | MEDIUM |
| Bedrock | LLM alternative | $20-50 | LOW |

**Total Estimated**: $55-195/month (varies by GPU usage)

---

## STAGE 7.5: AWS FOUNDATION

### Duration: 2-3 hours | Gate: AWS Foundation Operational

---

### Phase 7.5.1: AWS Account Verification

| Task ID | Task | Action | Expected | Status |
|---------|------|--------|----------|--------|
| 7.5.1.1 | Verify AWS CLI installed | `aws --version` | aws-cli/2.x | [ ] |
| 7.5.1.2 | Verify AWS credentials | `aws sts get-caller-identity` | Account ID | [ ] |
| 7.5.1.3 | Verify region configured | `aws configure get region` | eu-north-1 | [ ] |
| 7.5.1.4 | Check account ID | Compare to 7851-8665-9442 | Match | [ ] |

**Verification Commands**:
```powershell
# Check AWS CLI
aws --version

# Check credentials
aws sts get-caller-identity

# Check region
aws configure get region

# If not configured, run:
aws configure
# Enter: Access Key, Secret Key, Region (eu-north-1), Output (json)
```

---

### Phase 7.5.2: IAM Setup

| Task ID | Task | Action | Status |
|---------|------|--------|--------|
| 7.5.2.1 | Create Ziggie IAM user | Create programmatic user | [ ] |
| 7.5.2.2 | Create S3 policy | S3 bucket access | [ ] |
| 7.5.2.3 | Create Secrets policy | Secrets Manager access | [ ] |
| 7.5.2.4 | Create EC2 policy | EC2 start/stop access | [ ] |
| 7.5.2.5 | Create Lambda role | Lambda execution role | [ ] |
| 7.5.2.6 | Attach policies to user | Link all policies | [ ] |

**IAM Policy: S3 Access**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ZiggieS3Access",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::ziggie-assets-*",
                "arn:aws:s3:::ziggie-assets-*/*"
            ]
        }
    ]
}
```

**IAM Policy: Secrets Manager**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ZiggieSecretsAccess",
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret"
            ],
            "Resource": "arn:aws:secretsmanager:eu-north-1:*:secret:ziggie/*"
        }
    ]
}
```

**IAM Policy: EC2 Control**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ZiggieEC2Control",
            "Effect": "Allow",
            "Action": [
                "ec2:StartInstances",
                "ec2:StopInstances",
                "ec2:DescribeInstances"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "ec2:ResourceTag/Project": "Ziggie"
                }
            }
        }
    ]
}
```

---

### Phase 7.5.3: S3 Asset Storage Setup

| Task ID | Task | Action | Status |
|---------|------|--------|--------|
| 7.5.3.1 | Create assets bucket | `ziggie-assets-prod` | [ ] |
| 7.5.3.2 | Enable versioning | Protect against accidental deletes | [ ] |
| 7.5.3.3 | Configure lifecycle | Move to Glacier after 90 days | [ ] |
| 7.5.3.4 | Enable Intelligent-Tiering | Automatic cost optimization | [ ] |
| 7.5.3.5 | Create CloudFront distribution | CDN for asset delivery | [ ] |
| 7.5.3.6 | Configure CORS | Frontend access | [ ] |

**S3 Bucket Creation**:
```bash
# Create bucket in EU-North-1 (Stockholm)
aws s3 mb s3://ziggie-assets-prod --region eu-north-1

# Enable versioning
aws s3api put-bucket-versioning \
    --bucket ziggie-assets-prod \
    --versioning-configuration Status=Enabled

# Create folder structure
aws s3api put-object --bucket ziggie-assets-prod --key game-assets/
aws s3api put-object --bucket ziggie-assets-prod --key generated/
aws s3api put-object --bucket ziggie-assets-prod --key backups/
```

**Lifecycle Policy (lifecycle.json)**:
```json
{
    "Rules": [
        {
            "ID": "MoveToGlacierAfter90Days",
            "Status": "Enabled",
            "Filter": {
                "Prefix": "backups/"
            },
            "Transitions": [
                {
                    "Days": 90,
                    "StorageClass": "GLACIER"
                }
            ]
        },
        {
            "ID": "IntelligentTieringForAssets",
            "Status": "Enabled",
            "Filter": {
                "Prefix": "game-assets/"
            },
            "Transitions": [
                {
                    "Days": 0,
                    "StorageClass": "INTELLIGENT_TIERING"
                }
            ]
        }
    ]
}
```

**Apply Lifecycle**:
```bash
aws s3api put-bucket-lifecycle-configuration \
    --bucket ziggie-assets-prod \
    --lifecycle-configuration file://lifecycle.json
```

**CORS Configuration (cors.json)**:
```json
{
    "CORSRules": [
        {
            "AllowedHeaders": ["*"],
            "AllowedMethods": ["GET", "HEAD"],
            "AllowedOrigins": [
                "https://ziggie.cloud",
                "http://localhost:*"
            ],
            "ExposeHeaders": ["ETag"],
            "MaxAgeSeconds": 3600
        }
    ]
}
```

---

### Phase 7.5.4: Secrets Manager Setup

| Task ID | Task | Action | Status |
|---------|------|--------|--------|
| 7.5.4.1 | Create secrets namespace | `ziggie/` prefix | [ ] |
| 7.5.4.2 | Migrate Anthropic API key | Store securely | [ ] |
| 7.5.4.3 | Migrate OpenAI API key | Store securely | [ ] |
| 7.5.4.4 | Migrate database credentials | Store securely | [ ] |
| 7.5.4.5 | Create rotation schedule | 90-day rotation | [ ] |
| 7.5.4.6 | Update .env to use AWS | Fetch from Secrets Manager | [ ] |

**Create Secrets**:
```bash
# Anthropic API Key
aws secretsmanager create-secret \
    --name "ziggie/api-keys/anthropic" \
    --description "Anthropic Claude API Key" \
    --secret-string '{"api_key":"sk-ant-xxxxx"}'

# OpenAI API Key
aws secretsmanager create-secret \
    --name "ziggie/api-keys/openai" \
    --description "OpenAI API Key" \
    --secret-string '{"api_key":"[REDACTED-OPENAI-KEY]"}'

# Database Credentials
aws secretsmanager create-secret \
    --name "ziggie/database/postgres" \
    --description "PostgreSQL credentials" \
    --secret-string '{"username":"admin","password":"xxxxx","host":"db.ziggie.cloud","port":"5432"}'
```

**Python Script to Fetch Secrets**:
```python
# fetch_secrets.py - Use this in applications
import boto3
import json

def get_secret(secret_name: str) -> dict:
    """Fetch secret from AWS Secrets Manager"""
    client = boto3.client('secretsmanager', region_name='eu-north-1')

    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Usage
anthropic_key = get_secret('ziggie/api-keys/anthropic')['api_key']
openai_key = get_secret('ziggie/api-keys/openai')['api_key']
```

---

### Phase 7.5.5: Lambda Auto-Shutdown Setup

| Task ID | Task | Action | Status |
|---------|------|--------|--------|
| 7.5.5.1 | Create Lambda function | `ziggie-gpu-auto-shutdown` | [ ] |
| 7.5.5.2 | Create CloudWatch rule | Check every 5 minutes | [ ] |
| 7.5.5.3 | Configure idle threshold | 15 minutes idle = shutdown | [ ] |
| 7.5.5.4 | Create SNS notification | Alert on shutdown | [ ] |
| 7.5.5.5 | Test with dummy instance | Verify shutdown works | [ ] |

**Lambda Function (Python)**:
```python
# lambda_function.py - Auto-shutdown idle GPU instances
import boto3
from datetime import datetime, timedelta

def lambda_handler(event, context):
    """
    Auto-shutdown GPU instances that have been idle for 15+ minutes.
    Triggered by CloudWatch Events every 5 minutes.
    """
    ec2 = boto3.client('ec2', region_name='eu-north-1')
    cloudwatch = boto3.client('cloudwatch', region_name='eu-north-1')
    sns = boto3.client('sns', region_name='eu-north-1')

    # Find running instances tagged with Project=Ziggie and Type=GPU
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']},
            {'Name': 'tag:Project', 'Values': ['Ziggie']},
            {'Name': 'tag:Type', 'Values': ['GPU']}
        ]
    )

    instances_to_stop = []

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']

            # Check CPU utilization over last 15 minutes
            metrics = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=datetime.utcnow() - timedelta(minutes=15),
                EndTime=datetime.utcnow(),
                Period=300,  # 5 minutes
                Statistics=['Average']
            )

            if metrics['Datapoints']:
                avg_cpu = sum(d['Average'] for d in metrics['Datapoints']) / len(metrics['Datapoints'])

                # If average CPU < 5% over 15 minutes, consider idle
                if avg_cpu < 5.0:
                    instances_to_stop.append(instance_id)
                    print(f"Instance {instance_id} idle (CPU: {avg_cpu:.1f}%), marking for shutdown")

    # Stop idle instances
    if instances_to_stop:
        ec2.stop_instances(InstanceIds=instances_to_stop)

        # Send notification
        sns.publish(
            TopicArn='arn:aws:sns:eu-north-1:785186659442:ziggie-alerts',
            Subject='Ziggie GPU Auto-Shutdown',
            Message=f'Stopped idle GPU instances: {", ".join(instances_to_stop)}'
        )

        return {
            'statusCode': 200,
            'body': f'Stopped {len(instances_to_stop)} idle instances'
        }

    return {
        'statusCode': 200,
        'body': 'No idle instances found'
    }
```

**CloudWatch Event Rule**:
```bash
# Create scheduled rule (every 5 minutes)
aws events put-rule \
    --name ziggie-gpu-idle-check \
    --schedule-expression "rate(5 minutes)" \
    --state ENABLED

# Add Lambda as target
aws events put-targets \
    --rule ziggie-gpu-idle-check \
    --targets "Id"="1","Arn"="arn:aws:lambda:eu-north-1:785186659442:function:ziggie-gpu-auto-shutdown"
```

---

### Phase 7.5.6: EC2 Spot Instance Configuration

| Task ID | Task | Action | Status |
|---------|------|--------|--------|
| 7.5.6.1 | Create launch template | g4dn.xlarge with ComfyUI AMI | [ ] |
| 7.5.6.2 | Configure Spot request | Max price: $0.20/hr | [ ] |
| 7.5.6.3 | Create security group | SSH + ComfyUI port 8188 | [ ] |
| 7.5.6.4 | Create key pair | For SSH access | [ ] |
| 7.5.6.5 | Test Spot request | Verify instance launches | [ ] |

**Security Group Creation**:
```bash
# Create security group
aws ec2 create-security-group \
    --group-name ziggie-gpu-sg \
    --description "Ziggie GPU instance security group"

# Allow SSH from VPS only
aws ec2 authorize-security-group-ingress \
    --group-name ziggie-gpu-sg \
    --protocol tcp \
    --port 22 \
    --cidr 82.25.112.73/32

# Allow ComfyUI API from VPS only
aws ec2 authorize-security-group-ingress \
    --group-name ziggie-gpu-sg \
    --protocol tcp \
    --port 8188 \
    --cidr 82.25.112.73/32
```

**Launch Template (launch-template.json)**:
```json
{
    "LaunchTemplateName": "ziggie-gpu-spot",
    "LaunchTemplateData": {
        "ImageId": "ami-0123456789abcdef0",
        "InstanceType": "g4dn.xlarge",
        "KeyName": "ziggie-gpu-key",
        "SecurityGroupIds": ["sg-xxxxxxxxx"],
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
                    {"Key": "Project", "Value": "Ziggie"},
                    {"Key": "Type", "Value": "GPU"},
                    {"Key": "Name", "Value": "Ziggie-ComfyUI-Spot"}
                ]
            }
        ],
        "UserData": "IyEvYmluL2Jhc2gKIyBTdGFydCBDb21meVVJIG9uIGJvb3QKY2QgL29wdC9jb21meXVpCnB5dGhvbiBtYWluLnB5IC0tbGlzdGVuIDAuMC4wLjAgJg=="
    }
}
```

**Request Spot Instance**:
```bash
# Request Spot instance
aws ec2 request-spot-instances \
    --spot-price "0.20" \
    --instance-count 1 \
    --type "one-time" \
    --launch-specification file://spot-spec.json
```

---

### Phase 7.5.7: Bedrock LLM Integration (Optional)

| Task ID | Task | Action | Status |
|---------|------|--------|--------|
| 7.5.7.1 | Enable Bedrock access | Request model access | [ ] |
| 7.5.7.2 | Configure Claude access | claude-3-sonnet | [ ] |
| 7.5.7.3 | Create Bedrock wrapper | Python client | [ ] |
| 7.5.7.4 | Test API call | Verify response | [ ] |

**Bedrock Python Client**:
```python
# bedrock_client.py - AWS Bedrock LLM integration
import boto3
import json

class BedrockClient:
    def __init__(self, region='eu-north-1'):
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=region
        )

    def invoke_claude(self, prompt: str, max_tokens: int = 4096) -> str:
        """Call Claude 3 Sonnet via Bedrock"""
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        })

        response = self.client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=body
        )

        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']

# Usage
bedrock = BedrockClient()
response = bedrock.invoke_claude("Explain game asset pipelines")
print(response)
```

---

## GATE 7.5: AWS FOUNDATION OPERATIONAL

### Exit Criteria

| Criterion | Target | Verification |
|-----------|--------|--------------|
| AWS CLI configured | ✓ | `aws sts get-caller-identity` |
| IAM policies created | 5 policies | AWS Console |
| S3 bucket created | ziggie-assets-prod | `aws s3 ls` |
| Secrets migrated | 3+ secrets | `aws secretsmanager list-secrets` |
| Lambda deployed | ziggie-gpu-auto-shutdown | `aws lambda list-functions` |
| Spot template created | ziggie-gpu-spot | `aws ec2 describe-launch-templates` |

### Gate Verification Script

```powershell
# Verify-AWSGate.ps1
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "AWS INTEGRATION GATE VERIFICATION" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Check AWS CLI
$awsVersion = aws --version 2>&1
if ($awsVersion -match "aws-cli") {
    Write-Host "[OK] AWS CLI: $awsVersion" -ForegroundColor Green
} else {
    Write-Host "[FAIL] AWS CLI not installed" -ForegroundColor Red
}

# Check credentials
$identity = aws sts get-caller-identity 2>&1
if ($identity -match "Account") {
    Write-Host "[OK] AWS credentials configured" -ForegroundColor Green
} else {
    Write-Host "[FAIL] AWS credentials not configured" -ForegroundColor Red
}

# Check S3 bucket
$buckets = aws s3 ls 2>&1
if ($buckets -match "ziggie-assets") {
    Write-Host "[OK] S3 bucket exists" -ForegroundColor Green
} else {
    Write-Host "[WARN] S3 bucket not found" -ForegroundColor Yellow
}

# Check Secrets Manager
$secrets = aws secretsmanager list-secrets --query "SecretList[?contains(Name, 'ziggie')].Name" --output text 2>&1
if ($secrets) {
    Write-Host "[OK] Secrets configured: $secrets" -ForegroundColor Green
} else {
    Write-Host "[WARN] No Ziggie secrets found" -ForegroundColor Yellow
}

# Check Lambda
$lambdas = aws lambda list-functions --query "Functions[?contains(FunctionName, 'ziggie')].FunctionName" --output text 2>&1
if ($lambdas) {
    Write-Host "[OK] Lambda functions: $lambdas" -ForegroundColor Green
} else {
    Write-Host "[WARN] No Ziggie Lambda functions found" -ForegroundColor Yellow
}

Write-Host "`nAWS Gate verification complete"
```

---

## COST MONITORING

### Budget Alerts Setup

```bash
# Create budget with email alerts
aws budgets create-budget \
    --account-id 785186659442 \
    --budget file://budget.json \
    --notifications-with-subscribers file://notifications.json
```

**budget.json**:
```json
{
    "BudgetName": "Ziggie-Monthly",
    "BudgetLimit": {
        "Amount": "100",
        "Unit": "USD"
    },
    "BudgetType": "COST",
    "TimeUnit": "MONTHLY"
}
```

**notifications.json**:
```json
[
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
                "Address": "your-email@example.com"
            }
        ]
    }
]
```

---

## INTEGRATION WITH EXISTING SYSTEM

### MCP Configuration for AWS

Add to `.mcp.json`:

```json
{
  "mcpServers": {
    "aws-s3": {
      "command": "C:/ComfyUI/python_embeded/Scripts/uv.exe",
      "args": [
        "run", "--with", "mcp", "--with", "boto3", "python",
        "C:/ai-game-dev-system/mcp-servers/aws-mcp/s3_server.py"
      ],
      "env": {
        "AWS_REGION": "eu-north-1"
      }
    },
    "aws-secrets": {
      "command": "C:/ComfyUI/python_embeded/Scripts/uv.exe",
      "args": [
        "run", "--with", "mcp", "--with", "boto3", "python",
        "C:/ai-game-dev-system/mcp-servers/aws-mcp/secrets_server.py"
      ],
      "env": {
        "AWS_REGION": "eu-north-1"
      }
    }
  }
}
```

---

## DOCUMENT METADATA

| Field | Value |
|-------|-------|
| Document ID | ZIGGIE-AWS-INTEGRATION-V1.0 |
| Created | 2025-12-24 |
| AWS Region | eu-north-1 (Stockholm) |
| Account ID | 7851-8665-9442 |
| Services | S3, Secrets Manager, Lambda, EC2 Spot, Bedrock |
| Estimated Cost | $55-195/month |

---

**END OF AWS INTEGRATION STAGE**
