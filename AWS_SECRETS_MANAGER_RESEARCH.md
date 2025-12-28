# AWS Secrets Manager Research for Ziggie Cloud

> **Context**: Ziggie Cloud runs 20 Docker containers with various API keys and secrets
> **Region**: EU-North-1 (Stockholm)
> **Use Case**: Centralized secret management for OpenAI, ElevenLabs, Meshy.ai, database passwords
> **Last Updated**: 2025-12-23

---

## Executive Summary

AWS Secrets Manager is the recommended solution for Ziggie Cloud's multi-container environment with third-party API credentials. While more expensive than Parameter Store ($0.40/secret/month vs free tier), it provides native rotation, versioning, and cross-service integration critical for production environments.

**Key Recommendation**: Use Secrets Manager for sensitive credentials (API keys, DB passwords) + Parameter Store for non-sensitive config (URLs, timeouts).

---

## 1. Secrets Manager vs Parameter Store (SSM)

### Feature Comparison Matrix

| Feature | Secrets Manager | Parameter Store | Winner for Ziggie |
|---------|-----------------|-----------------|-------------------|
| **Cost** | $0.40/secret/month + $0.05/10K API calls | Free (Standard), $0.05/param/month (Advanced) | Parameter Store |
| **Rotation** | Native automatic rotation | Manual only | **Secrets Manager** |
| **Secret Size** | 64 KB | 8 KB (Advanced) | Secrets Manager |
| **Versioning** | Automatic with staging labels | Manual versioning | **Secrets Manager** |
| **Cross-Region Replication** | Built-in | Manual | Secrets Manager |
| **API Key Management** | Designed for credentials | Designed for config | **Secrets Manager** |
| **Integration** | RDS, DocumentDB, Redshift native | No native DB integration | Secrets Manager |
| **Encryption** | KMS (mandatory) | KMS (optional) | Tie |

### Decision Matrix for Ziggie Cloud

| Secret Type | Storage | Reasoning |
|-------------|---------|-----------|
| OpenAI API Key | Secrets Manager | High-value, rotation needed |
| ElevenLabs API Key | Secrets Manager | High-value, rotation needed |
| Meshy.ai API Key | Secrets Manager | High-value, rotation needed |
| Database Passwords | Secrets Manager | Native RDS rotation |
| n8n Webhook URLs | Parameter Store | Non-sensitive config |
| Container Timeouts | Parameter Store | Non-sensitive config |
| Feature Flags | Parameter Store | Non-sensitive config |

**Recommended Approach**: Hybrid strategy with ~10-15 secrets in Secrets Manager (~$6-8/month) + unlimited non-sensitive config in Parameter Store (free).

---

## 2. Setting Up Secrets Manager with Rotation

### 2.1 Creating Secrets via AWS CLI

```bash
# Prerequisites: AWS CLI configured with eu-north-1 region
aws configure set region eu-north-1

# Create OpenAI API Key secret
aws secretsmanager create-secret \
    --name ziggie/prod/openai-api-key \
    --description "OpenAI API Key for Ziggie Cloud production" \
    --secret-string '{"api_key":"[REDACTED-OPENAI-KEY]"}' \
    --tags Key=Environment,Value=Production Key=Service,Value=Ziggie

# Create database credentials with automatic RDS rotation
aws secretsmanager create-secret \
    --name ziggie/prod/postgres-master \
    --description "PostgreSQL master credentials" \
    --secret-string '{
        "username": "ziggie_admin",
        "password": "GENERATED_STRONG_PASSWORD",
        "engine": "postgres",
        "host": "ziggie-db.xxxxx.eu-north-1.rds.amazonaws.com",
        "port": 5432,
        "dbname": "ziggie_prod"
    }' \
    --tags Key=Environment,Value=Production

# Create ElevenLabs API Key
aws secretsmanager create-secret \
    --name ziggie/prod/elevenlabs-api-key \
    --description "ElevenLabs API Key" \
    --secret-string '{"api_key":"your_elevenlabs_key_here"}' \
    --tags Key=Environment,Value=Production Key=Service,Value=Ziggie

# Create Meshy.ai API Key
aws secretsmanager create-secret \
    --name ziggie/prod/meshy-api-key \
    --description "Meshy.ai API Key" \
    --secret-string '{"api_key":"your_meshy_key_here"}' \
    --tags Key=Environment,Value=Production Key=Service,Value=Ziggie
```

### 2.2 Automatic Rotation Setup

#### For RDS/PostgreSQL (Native Support)

```bash
# Enable automatic rotation for PostgreSQL credentials (30-day cycle)
aws secretsmanager rotate-secret \
    --secret-id ziggie/prod/postgres-master \
    --rotation-lambda-arn arn:aws:lambda:eu-north-1:ACCOUNT_ID:function:SecretsManagerPostgreSQLRotation \
    --rotation-rules AutomaticallyAfterDays=30

# AWS creates rotation Lambda automatically for RDS
aws secretsmanager rotate-secret \
    --secret-id ziggie/prod/postgres-master \
    --rotation-lambda-arn arn:aws:serverlessrepo:us-east-1:297356227924:applications/SecretsManagerRDSPostgreSQLRotationSingleUser
```

#### For API Keys (Custom Rotation Lambda)

API keys from OpenAI, ElevenLabs, Meshy.ai don't support automatic rotation (requires manual regeneration via their dashboards). However, you can set up Lambda functions to:

1. Send notifications 30 days before expiration
2. Trigger manual rotation workflows
3. Validate API key validity daily

**Custom Rotation Lambda Example** (Python):

```python
# lambda_rotation_validator.py
import boto3
import requests
import os

secretsmanager = boto3.client('secretsmanager', region_name='eu-north-1')
sns = boto3.client('sns', region_name='eu-north-1')

def lambda_handler(event, context):
    """Validate API keys and notify if invalid"""

    secrets_to_check = [
        'ziggie/prod/openai-api-key',
        'ziggie/prod/elevenlabs-api-key',
        'ziggie/prod/meshy-api-key'
    ]

    for secret_name in secrets_to_check:
        # Get secret value
        response = secretsmanager.get_secret_value(SecretId=secret_name)
        secret_data = json.loads(response['SecretString'])
        api_key = secret_data.get('api_key')

        # Validate key (example for OpenAI)
        if 'openai' in secret_name:
            is_valid = validate_openai_key(api_key)
        elif 'elevenlabs' in secret_name:
            is_valid = validate_elevenlabs_key(api_key)
        elif 'meshy' in secret_name:
            is_valid = validate_meshy_key(api_key)

        if not is_valid:
            # Send SNS notification
            sns.publish(
                TopicArn=os.environ['SNS_TOPIC_ARN'],
                Subject=f'CRITICAL: Invalid API Key Detected',
                Message=f'The API key for {secret_name} is invalid. Please rotate immediately.'
            )

    return {'statusCode': 200, 'body': 'Validation complete'}

def validate_openai_key(api_key):
    """Test OpenAI API key validity"""
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.get('https://api.openai.com/v1/models', headers=headers)
    return response.status_code == 200

def validate_elevenlabs_key(api_key):
    """Test ElevenLabs API key validity"""
    headers = {'xi-api-key': api_key}
    response = requests.get('https://api.elevenlabs.io/v1/user', headers=headers)
    return response.status_code == 200

def validate_meshy_key(api_key):
    """Test Meshy.ai API key validity"""
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.get('https://api.meshy.ai/v1/user', headers=headers)
    return response.status_code == 200
```

**EventBridge Rule for Daily Validation**:

```bash
# Create EventBridge rule to run validation daily at 9 AM UTC
aws events put-rule \
    --name ziggie-daily-api-key-validation \
    --schedule-expression "cron(0 9 * * ? *)" \
    --state ENABLED \
    --description "Daily API key validation for Ziggie Cloud"

# Add Lambda as target
aws events put-targets \
    --rule ziggie-daily-api-key-validation \
    --targets "Id"="1","Arn"="arn:aws:lambda:eu-north-1:ACCOUNT_ID:function:ZiggieAPIKeyValidator"
```

---

## 3. Docker Integration: Fetching Secrets at Container Startup

### 3.1 Architecture Pattern

```text
Container Startup Sequence:
┌─────────────────────────────────────────────────────────┐
│ 1. Container starts with IAM role credentials          │
│ 2. Entrypoint script fetches secrets from AWS          │
│ 3. Secrets injected as environment variables           │
│ 4. Application process starts with secrets in memory   │
│ 5. Secrets never written to disk                       │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Entrypoint Script Pattern

**entrypoint.sh** (Generic for all containers):

```bash
#!/bin/bash
set -e

# Function to fetch secret from AWS Secrets Manager
fetch_secret() {
    local secret_name=$1
    local json_key=$2

    aws secretsmanager get-secret-value \
        --secret-id "$secret_name" \
        --region eu-north-1 \
        --query SecretString \
        --output text | jq -r ".$json_key"
}

# Fetch secrets and export as environment variables
export OPENAI_API_KEY=$(fetch_secret "ziggie/prod/openai-api-key" "api_key")
export ELEVENLABS_API_KEY=$(fetch_secret "ziggie/prod/elevenlabs-api-key" "api_key")
export MESHY_API_KEY=$(fetch_secret "ziggie/prod/meshy-api-key" "api_key")
export DATABASE_URL=$(fetch_secret "ziggie/prod/postgres-master" "connection_string")

# Start the main application
exec "$@"
```

### 3.3 Docker Compose Configuration

**docker-compose.yml** (with AWS Secrets Manager):

```yaml
version: '3.8'

services:
  ziggie-backend:
    image: ziggie/backend:latest
    entrypoint: ["/app/entrypoint.sh"]
    command: ["node", "dist/index.js"]
    volumes:
      - ./entrypoint.sh:/app/entrypoint.sh:ro
    environment:
      AWS_REGION: eu-north-1
      # IAM role credentials provided by EC2 instance role
    networks:
      - ziggie-network
    depends_on:
      - postgres

  ziggie-ai-worker:
    image: ziggie/ai-worker:latest
    entrypoint: ["/app/entrypoint.sh"]
    command: ["python", "main.py"]
    volumes:
      - ./entrypoint.sh:/app/entrypoint.sh:ro
    environment:
      AWS_REGION: eu-north-1
    networks:
      - ziggie-network

  n8n:
    image: n8nio/n8n:latest
    entrypoint: ["/entrypoint-wrapper.sh"]
    volumes:
      - ./n8n-entrypoint.sh:/entrypoint-wrapper.sh:ro
      - n8n_data:/home/node/.n8n
    environment:
      AWS_REGION: eu-north-1
      N8N_ENCRYPTION_KEY: ${N8N_ENCRYPTION_KEY}  # Fetched from Secrets Manager
    ports:
      - "5678:5678"
    networks:
      - ziggie-network

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - ziggie-network

secrets:
  db_password:
    external: true
    name: ziggie_db_password

networks:
  ziggie-network:
    driver: bridge

volumes:
  n8n_data:
  postgres_data:
```

### 3.4 Dockerfile Example with Secret Fetching

```dockerfile
# Dockerfile for Ziggie Backend
FROM node:20-alpine

# Install AWS CLI and jq for secret fetching
RUN apk add --no-cache aws-cli jq

WORKDIR /app

# Copy application files
COPY package*.json ./
RUN npm ci --only=production

COPY . .

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Use entrypoint to fetch secrets before starting app
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["node", "dist/index.js"]
```

### 3.5 Alternative: AWS Secrets Manager Agent (Sidecar Pattern)

For higher security, use AWS Secrets Manager Agent as a sidecar container:

```yaml
services:
  ziggie-backend:
    image: ziggie/backend:latest
    environment:
      OPENAI_API_KEY_PATH: /secrets/openai-api-key
      DATABASE_URL_PATH: /secrets/postgres-master
    volumes:
      - secrets-volume:/secrets:ro
    depends_on:
      - secrets-agent

  secrets-agent:
    image: public.ecr.aws/aws-secrets-manager/secrets-manager-agent:latest
    environment:
      AWS_REGION: eu-north-1
      SECRETS_MANAGER_TTL: 300  # Cache for 5 minutes
    volumes:
      - secrets-volume:/secrets

volumes:
  secrets-volume:
```

---

## 4. n8n Credential Storage Integration with AWS Secrets Manager

### 4.1 n8n Architecture with Secrets Manager

n8n stores credentials in its internal SQLite/PostgreSQL database by default. To integrate with AWS Secrets Manager:

**Option 1: Environment Variable Injection** (Recommended)

```bash
# n8n-entrypoint.sh
#!/bin/bash
set -e

# Fetch secrets from AWS Secrets Manager
export OPENAI_API_KEY=$(aws secretsmanager get-secret-value \
    --secret-id ziggie/prod/openai-api-key \
    --region eu-north-1 \
    --query SecretString \
    --output text | jq -r '.api_key')

export ELEVENLABS_API_KEY=$(aws secretsmanager get-secret-value \
    --secret-id ziggie/prod/elevenlabs-api-key \
    --region eu-north-1 \
    --query SecretString \
    --output text | jq -r '.api_key')

export N8N_ENCRYPTION_KEY=$(aws secretsmanager get-secret-value \
    --secret-id ziggie/prod/n8n-encryption-key \
    --region eu-north-1 \
    --query SecretString \
    --output text | jq -r '.key')

# Start n8n with environment variables
exec n8n start
```

**n8n Workflow Configuration** (use environment variables):

```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.openAi",
      "credentials": {
        "openAiApi": {
          "apiKey": "={{$env.OPENAI_API_KEY}}"
        }
      }
    }
  ]
}
```

### 4.2 n8n Custom Credential Type (Advanced)

Create custom n8n credential type that fetches from AWS:

**credentials/AwsSecretsManagerApi.credentials.ts**:

```typescript
import {
  ICredentialType,
  INodeProperties,
} from 'n8n-workflow';

export class AwsSecretsManagerApi implements ICredentialType {
  name = 'awsSecretsManagerApi';
  displayName = 'AWS Secrets Manager API';
  documentationUrl = 'https://docs.aws.amazon.com/secretsmanager/';
  properties: INodeProperties[] = [
    {
      displayName: 'Region',
      name: 'region',
      type: 'string',
      default: 'eu-north-1',
    },
    {
      displayName: 'Secret Name',
      name: 'secretName',
      type: 'string',
      default: 'ziggie/prod/openai-api-key',
    },
    {
      displayName: 'JSON Key',
      name: 'jsonKey',
      type: 'string',
      default: 'api_key',
      description: 'Key to extract from JSON secret',
    },
  ];
}
```

### 4.3 n8n Backup Strategy with Secrets Manager

```bash
# Export n8n workflows and credentials (encrypted)
docker exec n8n n8n export:workflow --all --output=/backup/workflows.json
docker exec n8n n8n export:credentials --all --output=/backup/credentials.json

# Store backups in S3 with encryption
aws s3 cp /backup/workflows.json s3://ziggie-backups/n8n/workflows-$(date +%Y%m%d).json \
    --server-side-encryption aws:kms \
    --sse-kms-key-id arn:aws:kms:eu-north-1:ACCOUNT_ID:key/KEY_ID

aws s3 cp /backup/credentials.json s3://ziggie-backups/n8n/credentials-$(date +%Y%m%d).json \
    --server-side-encryption aws:kms \
    --sse-kms-key-id arn:aws:kms:eu-north-1:ACCOUNT_ID:key/KEY_ID
```

---

## 5. IAM Policies for Secure Secret Access

### 5.1 Least Privilege Policy (Production-Ready)

**ziggie-secrets-read-policy.json**:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadZiggieProductionSecrets",
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": [
        "arn:aws:secretsmanager:eu-north-1:ACCOUNT_ID:secret:ziggie/prod/*"
      ],
      "Condition": {
        "StringEquals": {
          "secretsmanager:VersionStage": "AWSCURRENT"
        }
      }
    },
    {
      "Sid": "DecryptSecrets",
      "Effect": "Allow",
      "Action": [
        "kms:Decrypt",
        "kms:DescribeKey"
      ],
      "Resource": [
        "arn:aws:kms:eu-north-1:ACCOUNT_ID:key/KEY_ID"
      ],
      "Condition": {
        "StringEquals": {
          "kms:ViaService": "secretsmanager.eu-north-1.amazonaws.com"
        }
      }
    }
  ]
}
```

### 5.2 Service-Specific IAM Roles

**EC2 Instance Role for Docker Host**:

```bash
# Create IAM role
aws iam create-role \
    --role-name ZiggieDockerHostRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "ec2.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }'

# Attach secrets read policy
aws iam attach-role-policy \
    --role-name ZiggieDockerHostRole \
    --policy-arn arn:aws:iam::ACCOUNT_ID:policy/ziggie-secrets-read-policy

# Create instance profile
aws iam create-instance-profile \
    --instance-profile-name ZiggieDockerHostProfile

aws iam add-role-to-instance-profile \
    --instance-profile-name ZiggieDockerHostProfile \
    --role-name ZiggieDockerHostRole

# Attach to EC2 instance
aws ec2 associate-iam-instance-profile \
    --instance-id i-xxxxxxxxxxxxx \
    --iam-instance-profile Name=ZiggieDockerHostProfile
```

### 5.3 Per-Container IAM Roles (ECS Task Roles)

If using ECS instead of Docker Compose:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BackendContainerSecrets",
      "Effect": "Allow",
      "Action": ["secretsmanager:GetSecretValue"],
      "Resource": [
        "arn:aws:secretsmanager:eu-north-1:ACCOUNT_ID:secret:ziggie/prod/openai-api-key-*",
        "arn:aws:secretsmanager:eu-north-1:ACCOUNT_ID:secret:ziggie/prod/postgres-master-*"
      ]
    },
    {
      "Sid": "AIWorkerSecrets",
      "Effect": "Allow",
      "Action": ["secretsmanager:GetSecretValue"],
      "Resource": [
        "arn:aws:secretsmanager:eu-north-1:ACCOUNT_ID:secret:ziggie/prod/elevenlabs-api-key-*",
        "arn:aws:secretsmanager:eu-north-1:ACCOUNT_ID:secret:ziggie/prod/meshy-api-key-*"
      ]
    }
  ]
}
```

### 5.4 Secret Tagging for Access Control

```bash
# Tag secrets with access control metadata
aws secretsmanager tag-resource \
    --secret-id ziggie/prod/openai-api-key \
    --tags Key=AccessLevel,Value=HighSecurity Key=Container,Value=Backend

# IAM policy using tags
{
  "Condition": {
    "StringEquals": {
      "secretsmanager:ResourceTag/Container": "Backend"
    }
  }
}
```

---

## 6. Cost Comparison and Optimization

### 6.1 Secrets Manager Cost Breakdown (EU-North-1)

| Component | Pricing | Ziggie Cloud Estimate |
|-----------|---------|------------------------|
| Secret storage | $0.40/secret/month | 15 secrets = $6.00/month |
| API calls | $0.05/10,000 calls | 20 containers × 10 restarts/day × 30 days = 6,000 calls = $0.03/month |
| **Total** | - | **$6.03/month** |

### 6.2 Parameter Store Cost (For Comparison)

| Tier | Pricing | Limits |
|------|---------|--------|
| Standard | **FREE** | 10,000 params, 4 KB each, no rotation |
| Advanced | $0.05/param/month | 100,000 params, 8 KB each, parameter policies |

### 6.3 Cost Optimization Strategies

**Strategy 1: Hybrid Approach** (Recommended)

```text
Secrets Manager (15 secrets):
- OpenAI API Key ($0.40)
- ElevenLabs API Key ($0.40)
- Meshy.ai API Key ($0.40)
- Database master password ($0.40)
- Database read-replica password ($0.40)
- n8n encryption key ($0.40)
- JWT signing key ($0.40)
- Stripe API key ($0.40)
- SendGrid API key ($0.40)
- Twilio API key ($0.40)
- Redis password ($0.40)
- RabbitMQ password ($0.40)
- SSL certificate private key ($0.40)
- Backup encryption key ($0.40)
- GitHub deploy token ($0.40)
Total: $6.00/month

Parameter Store (FREE):
- Application URLs (unlimited)
- Feature flags (unlimited)
- Timeout configurations (unlimited)
- Non-sensitive config (unlimited)
Total: $0.00/month

GRAND TOTAL: $6.00/month
```

**Strategy 2: API Call Reduction**

```bash
# Cache secrets in container for 5 minutes
# Reduces API calls from 6,000/month to 1,200/month

# entrypoint-cached.sh
CACHE_FILE="/tmp/secrets_cache"
CACHE_TTL=300  # 5 minutes

if [ -f "$CACHE_FILE" ]; then
    CACHE_AGE=$(($(date +%s) - $(stat -c %Y "$CACHE_FILE")))
    if [ $CACHE_AGE -lt $CACHE_TTL ]; then
        source "$CACHE_FILE"
        exec "$@"
    fi
fi

# Fetch fresh secrets
export OPENAI_API_KEY=$(fetch_secret "ziggie/prod/openai-api-key" "api_key")
echo "export OPENAI_API_KEY='$OPENAI_API_KEY'" > "$CACHE_FILE"

exec "$@"
```

**Cost Savings**: $0.03/month → $0.006/month (80% reduction in API call costs)

### 6.4 Annual Cost Projection

| Year | Secrets Manager | Parameter Store | Total | Notes |
|------|-----------------|-----------------|-------|-------|
| 2025 | $72.36 | $0.00 | $72.36 | 15 secrets, 6K API calls/month |
| 2026 | $72.36 | $0.00 | $72.36 | Assuming no growth |
| 2027 | $120.60 | $0.00 | $120.60 | 25 secrets (growth scenario) |

**ROI Analysis**:
- Cost to implement: ~4 hours engineering time
- Cost to maintain: ~1 hour/month
- Security incident prevention: **Priceless**
- Compliance benefits: SOC 2, ISO 27001 audit readiness

---

## 7. Example Docker Compose Configuration with Secrets

### 7.1 Complete Production Setup

**docker-compose.production.yml**:

```yaml
version: '3.8'

services:
  # API Gateway
  ziggie-api:
    image: ziggie/api:${VERSION:-latest}
    container_name: ziggie-api
    restart: unless-stopped
    entrypoint: ["/app/scripts/entrypoint.sh"]
    command: ["node", "dist/server.js"]
    volumes:
      - ./scripts/entrypoint.sh:/app/scripts/entrypoint.sh:ro
      - api_logs:/app/logs
    environment:
      NODE_ENV: production
      AWS_REGION: eu-north-1
      LOG_LEVEL: info
      PORT: 3000
    ports:
      - "3000:3000"
    networks:
      - ziggie-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  # AI Processing Worker
  ziggie-ai-worker:
    image: ziggie/ai-worker:${VERSION:-latest}
    container_name: ziggie-ai-worker
    restart: unless-stopped
    entrypoint: ["/app/scripts/entrypoint.sh"]
    command: ["python", "src/worker.py"]
    volumes:
      - ./scripts/entrypoint.sh:/app/scripts/entrypoint.sh:ro
      - ai_worker_data:/data
    environment:
      PYTHON_ENV: production
      AWS_REGION: eu-north-1
      WORKER_CONCURRENCY: 4
    networks:
      - ziggie-network
    depends_on:
      rabbitmq:
        condition: service_healthy
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 4G
          cpus: '2.0'

  # n8n Workflow Automation
  n8n:
    image: n8nio/n8n:latest
    container_name: ziggie-n8n
    restart: unless-stopped
    entrypoint: ["/scripts/n8n-entrypoint.sh"]
    volumes:
      - ./scripts/n8n-entrypoint.sh:/scripts/n8n-entrypoint.sh:ro
      - n8n_data:/home/node/.n8n
    environment:
      N8N_HOST: n8n.ziggie.cloud
      N8N_PROTOCOL: https
      AWS_REGION: eu-north-1
      WEBHOOK_URL: https://n8n.ziggie.cloud
      GENERIC_TIMEZONE: Europe/Stockholm
      N8N_LOG_LEVEL: info
    ports:
      - "5678:5678"
    networks:
      - ziggie-network
    depends_on:
      postgres:
        condition: service_healthy

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: ziggie-postgres
    restart: unless-stopped
    entrypoint: ["/scripts/postgres-entrypoint.sh"]
    volumes:
      - ./scripts/postgres-entrypoint.sh:/scripts/postgres-entrypoint.sh:ro
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d:ro
    environment:
      POSTGRES_DB: ziggie_prod
      AWS_REGION: eu-north-1
      # Password fetched from Secrets Manager in entrypoint
    ports:
      - "5432:5432"
    networks:
      - ziggie-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 2G

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: ziggie-redis
    restart: unless-stopped
    entrypoint: ["/scripts/redis-entrypoint.sh"]
    command: ["redis-server", "/etc/redis/redis.conf"]
    volumes:
      - ./scripts/redis-entrypoint.sh:/scripts/redis-entrypoint.sh:ro
      - ./config/redis.conf:/etc/redis/redis.conf:ro
      - redis_data:/data
    environment:
      AWS_REGION: eu-north-1
    ports:
      - "6379:6379"
    networks:
      - ziggie-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  # RabbitMQ Message Queue
  rabbitmq:
    image: rabbitmq:3-management-alpine
    container_name: ziggie-rabbitmq
    restart: unless-stopped
    entrypoint: ["/scripts/rabbitmq-entrypoint.sh"]
    volumes:
      - ./scripts/rabbitmq-entrypoint.sh:/scripts/rabbitmq-entrypoint.sh:ro
      - rabbitmq_data:/var/lib/rabbitmq
    environment:
      AWS_REGION: eu-north-1
      RABBITMQ_DEFAULT_USER: ziggie
      # Password fetched from Secrets Manager in entrypoint
    ports:
      - "5672:5672"
      - "15672:15672"
    networks:
      - ziggie-network
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: ziggie-nginx
    restart: unless-stopped
    volumes:
      - ./config/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - nginx_logs:/var/log/nginx
    ports:
      - "80:80"
      - "443:443"
    networks:
      - ziggie-network
    depends_on:
      - ziggie-api
      - n8n

networks:
  ziggie-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  rabbitmq_data:
    driver: local
  n8n_data:
    driver: local
  ai_worker_data:
    driver: local
  api_logs:
    driver: local
  nginx_logs:
    driver: local
```

### 7.2 Entrypoint Scripts for Each Service

**scripts/entrypoint.sh** (Generic API/Worker):

```bash
#!/bin/bash
set -euo pipefail

echo "=== Ziggie Container Startup ==="
echo "Fetching secrets from AWS Secrets Manager..."

# Function to fetch secret value
fetch_secret() {
    local secret_name=$1
    local json_key=$2

    aws secretsmanager get-secret-value \
        --secret-id "$secret_name" \
        --region "${AWS_REGION}" \
        --query SecretString \
        --output text 2>/dev/null | jq -r ".$json_key"
}

# Fetch all required secrets
export OPENAI_API_KEY=$(fetch_secret "ziggie/prod/openai-api-key" "api_key")
export ELEVENLABS_API_KEY=$(fetch_secret "ziggie/prod/elevenlabs-api-key" "api_key")
export MESHY_API_KEY=$(fetch_secret "ziggie/prod/meshy-api-key" "api_key")
export STRIPE_SECRET_KEY=$(fetch_secret "ziggie/prod/stripe-secret-key" "api_key")
export SENDGRID_API_KEY=$(fetch_secret "ziggie/prod/sendgrid-api-key" "api_key")
export JWT_SECRET=$(fetch_secret "ziggie/prod/jwt-secret" "secret")

# Fetch database connection string
export DATABASE_URL=$(fetch_secret "ziggie/prod/postgres-master" "connection_string")

# Fetch Redis password
REDIS_PASSWORD=$(fetch_secret "ziggie/prod/redis-password" "password")
export REDIS_URL="redis://:${REDIS_PASSWORD}@redis:6379/0"

# Fetch RabbitMQ credentials
RABBITMQ_PASSWORD=$(fetch_secret "ziggie/prod/rabbitmq-password" "password")
export RABBITMQ_URL="amqp://ziggie:${RABBITMQ_PASSWORD}@rabbitmq:5672"

echo "Secrets loaded successfully"
echo "Starting application..."

# Execute the main process
exec "$@"
```

**scripts/postgres-entrypoint.sh**:

```bash
#!/bin/bash
set -euo pipefail

echo "=== PostgreSQL Startup ==="
echo "Fetching database password from Secrets Manager..."

# Fetch password
POSTGRES_PASSWORD=$(aws secretsmanager get-secret-value \
    --secret-id ziggie/prod/postgres-master \
    --region "${AWS_REGION}" \
    --query SecretString \
    --output text | jq -r '.password')

export POSTGRES_PASSWORD

echo "Database password loaded"

# Run original PostgreSQL entrypoint
exec docker-entrypoint.sh postgres
```

**scripts/redis-entrypoint.sh**:

```bash
#!/bin/bash
set -euo pipefail

echo "=== Redis Startup ==="
echo "Fetching Redis password from Secrets Manager..."

# Fetch password
REDIS_PASSWORD=$(aws secretsmanager get-secret-value \
    --secret-id ziggie/prod/redis-password \
    --region "${AWS_REGION}" \
    --query SecretString \
    --output text | jq -r '.password')

# Update Redis config with password
sed -i "s/REDIS_PASSWORD_PLACEHOLDER/${REDIS_PASSWORD}/g" /etc/redis/redis.conf

echo "Redis password configured"

# Execute Redis server
exec "$@"
```

**scripts/n8n-entrypoint.sh**:

```bash
#!/bin/bash
set -euo pipefail

echo "=== n8n Startup ==="
echo "Fetching credentials from Secrets Manager..."

# Fetch n8n encryption key
export N8N_ENCRYPTION_KEY=$(aws secretsmanager get-secret-value \
    --secret-id ziggie/prod/n8n-encryption-key \
    --region "${AWS_REGION}" \
    --query SecretString \
    --output text | jq -r '.key')

# Fetch database URL
export DB_POSTGRESDB_HOST=postgres
export DB_POSTGRESDB_PORT=5432
export DB_POSTGRESDB_DATABASE=n8n
export DB_POSTGRESDB_USER=$(aws secretsmanager get-secret-value \
    --secret-id ziggie/prod/postgres-master \
    --region "${AWS_REGION}" \
    --query SecretString \
    --output text | jq -r '.username')
export DB_POSTGRESDB_PASSWORD=$(aws secretsmanager get-secret-value \
    --secret-id ziggie/prod/postgres-master \
    --region "${AWS_REGION}" \
    --query SecretString \
    --output text | jq -r '.password')

# Fetch API keys for n8n integrations
export OPENAI_API_KEY=$(aws secretsmanager get-secret-value \
    --secret-id ziggie/prod/openai-api-key \
    --region "${AWS_REGION}" \
    --query SecretString \
    --output text | jq -r '.api_key')

echo "Credentials loaded"

# Start n8n
exec n8n start
```

---

## 8. AWS CLI Commands for Secret Management

### 8.1 Create/Update Secrets

```bash
# Create a new secret
aws secretsmanager create-secret \
    --name ziggie/prod/openai-api-key \
    --description "OpenAI API Key for production" \
    --secret-string '{"api_key":"[REDACTED-OPENAI-KEY]"}' \
    --tags Key=Environment,Value=Production Key=Service,Value=Ziggie \
    --region eu-north-1

# Update existing secret value
aws secretsmanager update-secret \
    --secret-id ziggie/prod/openai-api-key \
    --secret-string '{"api_key":"[REDACTED-OPENAI-KEY]"}' \
    --region eu-north-1

# Update secret from file
aws secretsmanager update-secret \
    --secret-id ziggie/prod/openai-api-key \
    --secret-string file://secret.json \
    --region eu-north-1

# Rotate secret immediately
aws secretsmanager rotate-secret \
    --secret-id ziggie/prod/postgres-master \
    --region eu-north-1
```

### 8.2 Retrieve Secrets

```bash
# Get current secret value
aws secretsmanager get-secret-value \
    --secret-id ziggie/prod/openai-api-key \
    --region eu-north-1 \
    --query SecretString \
    --output text

# Get specific JSON key from secret
aws secretsmanager get-secret-value \
    --secret-id ziggie/prod/openai-api-key \
    --region eu-north-1 \
    --query SecretString \
    --output text | jq -r '.api_key'

# Get secret metadata (no value)
aws secretsmanager describe-secret \
    --secret-id ziggie/prod/openai-api-key \
    --region eu-north-1

# List all secrets with tag
aws secretsmanager list-secrets \
    --filters Key=tag-key,Values=Environment Key=tag-value,Values=Production \
    --region eu-north-1
```

### 8.3 Secret Versioning

```bash
# Get specific version
aws secretsmanager get-secret-value \
    --secret-id ziggie/prod/openai-api-key \
    --version-id EXAMPLE-VERSION-ID \
    --region eu-north-1

# List all versions
aws secretsmanager list-secret-version-ids \
    --secret-id ziggie/prod/openai-api-key \
    --region eu-north-1

# Get previous version (rollback scenario)
aws secretsmanager get-secret-value \
    --secret-id ziggie/prod/openai-api-key \
    --version-stage AWSPREVIOUS \
    --region eu-north-1
```

### 8.4 Delete/Restore Secrets

```bash
# Schedule deletion (7-30 days recovery window)
aws secretsmanager delete-secret \
    --secret-id ziggie/prod/old-api-key \
    --recovery-window-in-days 30 \
    --region eu-north-1

# Restore deleted secret
aws secretsmanager restore-secret \
    --secret-id ziggie/prod/old-api-key \
    --region eu-north-1

# Force delete (IMMEDIATE, NO RECOVERY)
aws secretsmanager delete-secret \
    --secret-id ziggie/prod/old-api-key \
    --force-delete-without-recovery \
    --region eu-north-1
```

### 8.5 Bulk Operations

**Bash script for bulk secret creation**:

```bash
#!/bin/bash
# bulk-create-secrets.sh

REGION="eu-north-1"
SECRETS_FILE="secrets.json"

# secrets.json format:
# {
#   "ziggie/prod/openai-api-key": {"api_key": "sk-xxxxx"},
#   "ziggie/prod/elevenlabs-api-key": {"api_key": "el-xxxxx"}
# }

jq -r 'to_entries[] | @json' "$SECRETS_FILE" | while read -r entry; do
    SECRET_NAME=$(echo "$entry" | jq -r '.key')
    SECRET_VALUE=$(echo "$entry" | jq -r '.value | @json')

    echo "Creating secret: $SECRET_NAME"

    aws secretsmanager create-secret \
        --name "$SECRET_NAME" \
        --secret-string "$SECRET_VALUE" \
        --tags Key=Environment,Value=Production Key=Service,Value=Ziggie \
        --region "$REGION" \
        2>/dev/null || \
    aws secretsmanager update-secret \
        --secret-id "$SECRET_NAME" \
        --secret-string "$SECRET_VALUE" \
        --region "$REGION"
done
```

### 8.6 Monitoring and Auditing

```bash
# Enable CloudWatch logging for secret access
aws secretsmanager put-resource-policy \
    --secret-id ziggie/prod/openai-api-key \
    --resource-policy '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "logs.amazonaws.com"},
            "Action": "secretsmanager:GetSecretValue",
            "Resource": "*"
        }]
    }' \
    --region eu-north-1

# Query CloudTrail for secret access
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=ResourceName,AttributeValue=ziggie/prod/openai-api-key \
    --region eu-north-1 \
    --max-results 50

# Get secret access metrics from CloudWatch
aws cloudwatch get-metric-statistics \
    --namespace AWS/SecretsManager \
    --metric-name GetSecretValueCount \
    --dimensions Name=SecretId,Value=ziggie/prod/openai-api-key \
    --start-time 2025-12-01T00:00:00Z \
    --end-time 2025-12-23T23:59:59Z \
    --period 86400 \
    --statistics Sum \
    --region eu-north-1
```

---

## 9. Disaster Recovery: Backing Up and Restoring Secrets

### 9.1 Backup Strategy

**Full backup script** (backup-secrets.sh):

```bash
#!/bin/bash
set -euo pipefail

REGION="eu-north-1"
BACKUP_DIR="./secrets-backup-$(date +%Y%m%d-%H%M%S)"
ENCRYPTION_KEY_ID="arn:aws:kms:eu-north-1:ACCOUNT_ID:key/KEY_ID"

mkdir -p "$BACKUP_DIR"

echo "=== Secrets Manager Backup ==="
echo "Region: $REGION"
echo "Backup directory: $BACKUP_DIR"

# List all secrets
SECRETS=$(aws secretsmanager list-secrets \
    --region "$REGION" \
    --query 'SecretList[?Tags[?Key==`Service` && Value==`Ziggie`]].Name' \
    --output text)

echo "Found $(echo $SECRETS | wc -w) secrets to backup"

# Backup each secret
for SECRET_NAME in $SECRETS; do
    echo "Backing up: $SECRET_NAME"

    # Get secret metadata
    aws secretsmanager describe-secret \
        --secret-id "$SECRET_NAME" \
        --region "$REGION" \
        > "$BACKUP_DIR/${SECRET_NAME//\//_}_metadata.json"

    # Get secret value (encrypted)
    aws secretsmanager get-secret-value \
        --secret-id "$SECRET_NAME" \
        --region "$REGION" \
        > "$BACKUP_DIR/${SECRET_NAME//\//_}_value.json"

    # Get all versions
    aws secretsmanager list-secret-version-ids \
        --secret-id "$SECRET_NAME" \
        --region "$REGION" \
        > "$BACKUP_DIR/${SECRET_NAME//\//_}_versions.json"
done

# Create backup manifest
cat > "$BACKUP_DIR/manifest.json" <<EOF
{
  "backup_date": "$(date -Iseconds)",
  "region": "$REGION",
  "secret_count": $(echo $SECRETS | wc -w),
  "secrets": $(echo "$SECRETS" | jq -R 'split(" ")')
}
EOF

# Encrypt backup directory
tar czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

# Upload to S3 with encryption
aws s3 cp "${BACKUP_DIR}.tar.gz" \
    "s3://ziggie-disaster-recovery/secrets-manager/${BACKUP_DIR##*/}.tar.gz" \
    --server-side-encryption aws:kms \
    --sse-kms-key-id "$ENCRYPTION_KEY_ID" \
    --region "$REGION"

echo "Backup completed: ${BACKUP_DIR}.tar.gz"
echo "Uploaded to S3: s3://ziggie-disaster-recovery/secrets-manager/"
```

### 9.2 Restore Strategy

**Full restore script** (restore-secrets.sh):

```bash
#!/bin/bash
set -euo pipefail

REGION="eu-north-1"
BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup-file.tar.gz>"
    exit 1
fi

echo "=== Secrets Manager Restore ==="
echo "Backup file: $BACKUP_FILE"

# Download from S3 if URL provided
if [[ "$BACKUP_FILE" == s3://* ]]; then
    LOCAL_BACKUP="/tmp/$(basename $BACKUP_FILE)"
    aws s3 cp "$BACKUP_FILE" "$LOCAL_BACKUP" --region "$REGION"
    BACKUP_FILE="$LOCAL_BACKUP"
fi

# Extract backup
BACKUP_DIR="${BACKUP_FILE%.tar.gz}"
tar xzf "$BACKUP_FILE"

# Read manifest
MANIFEST="$BACKUP_DIR/manifest.json"
SECRETS=$(jq -r '.secrets[]' "$MANIFEST")

echo "Restoring $(jq -r '.secret_count' $MANIFEST) secrets from $(jq -r '.backup_date' $MANIFEST)"

# Restore each secret
for SECRET_NAME in $SECRETS; do
    VALUE_FILE="$BACKUP_DIR/${SECRET_NAME//\//_}_value.json"
    METADATA_FILE="$BACKUP_DIR/${SECRET_NAME//\//_}_metadata.json"

    echo "Restoring: $SECRET_NAME"

    # Extract secret value
    SECRET_STRING=$(jq -r '.SecretString' "$VALUE_FILE")

    # Get tags from metadata
    TAGS=$(jq -r '.Tags // [] | map("Key=\(.Key),Value=\(.Value)") | join(" ")' "$METADATA_FILE")

    # Create or update secret
    aws secretsmanager create-secret \
        --name "$SECRET_NAME" \
        --secret-string "$SECRET_STRING" \
        --tags $TAGS \
        --region "$REGION" \
        2>/dev/null || \
    aws secretsmanager update-secret \
        --secret-id "$SECRET_NAME" \
        --secret-string "$SECRET_STRING" \
        --region "$REGION"
done

# Cleanup
rm -rf "$BACKUP_DIR"
[ -f "$LOCAL_BACKUP" ] && rm "$LOCAL_BACKUP"

echo "Restore completed successfully"
```

### 9.3 Cross-Region Replication

```bash
# Enable replication to eu-west-1 (Ireland) for disaster recovery
aws secretsmanager replicate-secret-to-regions \
    --secret-id ziggie/prod/openai-api-key \
    --add-replica-regions Region=eu-west-1,KmsKeyId=arn:aws:kms:eu-west-1:ACCOUNT_ID:key/KEY_ID \
    --region eu-north-1

# Replicate all production secrets
for SECRET in $(aws secretsmanager list-secrets --region eu-north-1 --query 'SecretList[?Tags[?Key==`Environment` && Value==`Production`]].Name' --output text); do
    echo "Replicating: $SECRET"
    aws secretsmanager replicate-secret-to-regions \
        --secret-id "$SECRET" \
        --add-replica-regions Region=eu-west-1 \
        --region eu-north-1
done
```

### 9.4 Automated Backup with Lambda

**Lambda function** (backup-secrets-lambda.py):

```python
import boto3
import json
import os
from datetime import datetime

s3 = boto3.client('s3')
secretsmanager = boto3.client('secretsmanager', region_name='eu-north-1')

def lambda_handler(event, context):
    """Daily backup of all Ziggie secrets to S3"""

    bucket = os.environ['BACKUP_BUCKET']
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

    # List all secrets with Ziggie tag
    response = secretsmanager.list_secrets()
    ziggie_secrets = [
        s for s in response['SecretList']
        if any(t.get('Key') == 'Service' and t.get('Value') == 'Ziggie' for t in s.get('Tags', []))
    ]

    backup_data = {
        'backup_date': datetime.now().isoformat(),
        'region': 'eu-north-1',
        'secret_count': len(ziggie_secrets),
        'secrets': []
    }

    for secret in ziggie_secrets:
        secret_name = secret['Name']

        # Get secret value
        value_response = secretsmanager.get_secret_value(SecretId=secret_name)

        # Get metadata
        metadata = secretsmanager.describe_secret(SecretId=secret_name)

        backup_data['secrets'].append({
            'name': secret_name,
            'value': value_response['SecretString'],
            'version_id': value_response['VersionId'],
            'tags': metadata.get('Tags', []),
            'description': metadata.get('Description', '')
        })

    # Upload to S3
    s3.put_object(
        Bucket=bucket,
        Key=f'secrets-backup/{timestamp}/backup.json',
        Body=json.dumps(backup_data, indent=2),
        ServerSideEncryption='aws:kms',
        SSEKMSKeyId=os.environ['KMS_KEY_ID']
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Backup completed',
            'secrets_backed_up': len(ziggie_secrets),
            'backup_key': f'secrets-backup/{timestamp}/backup.json'
        })
    }
```

**EventBridge rule for daily backup**:

```bash
# Create EventBridge rule
aws events put-rule \
    --name ziggie-daily-secrets-backup \
    --schedule-expression "cron(0 2 * * ? *)" \
    --state ENABLED \
    --description "Daily backup of Ziggie secrets at 2 AM UTC"

# Add Lambda as target
aws events put-targets \
    --rule ziggie-daily-secrets-backup \
    --targets "Id"="1","Arn"="arn:aws:lambda:eu-north-1:ACCOUNT_ID:function:BackupSecretsFunction"
```

### 9.5 Point-in-Time Recovery

```bash
# List available backups
aws s3 ls s3://ziggie-disaster-recovery/secrets-manager/ --recursive

# Restore from specific date
RESTORE_DATE="20251220-140000"
./restore-secrets.sh "s3://ziggie-disaster-recovery/secrets-manager/secrets-backup-${RESTORE_DATE}.tar.gz"

# Verify restoration
aws secretsmanager list-secrets --region eu-north-1 --query 'SecretList[?Tags[?Key==`Service` && Value==`Ziggie`]].[Name,LastChangedDate]' --output table
```

---

## 10. Implementation Checklist

### Phase 1: Setup (Week 1)

- [ ] Create KMS key for secret encryption
- [ ] Create IAM role for EC2 instance (ZiggieDockerHostRole)
- [ ] Attach IAM role to VPS EC2 instance
- [ ] Install AWS CLI v2 on VPS
- [ ] Configure AWS CLI with eu-north-1 region
- [ ] Create S3 bucket for backups (ziggie-disaster-recovery)

### Phase 2: Secret Migration (Week 1-2)

- [ ] Audit current .env files for all 20 containers
- [ ] Categorize secrets (API keys vs config)
- [ ] Create all secrets in Secrets Manager (15 estimated)
- [ ] Tag secrets with Environment=Production, Service=Ziggie
- [ ] Test secret retrieval from VPS
- [ ] Document secret naming convention

### Phase 3: Docker Integration (Week 2)

- [ ] Create entrypoint.sh scripts for each container type
- [ ] Update Dockerfiles to include AWS CLI and jq
- [ ] Modify docker-compose.yml with new entrypoints
- [ ] Test single container with Secrets Manager integration
- [ ] Test all 20 containers with Secrets Manager
- [ ] Remove .env files from VPS (backup first!)

### Phase 4: n8n Integration (Week 2-3)

- [ ] Create n8n-specific entrypoint script
- [ ] Migrate n8n credentials to environment variables
- [ ] Test n8n workflows with new credential injection
- [ ] Document n8n credential setup process
- [ ] Backup n8n database to S3

### Phase 5: Rotation & Monitoring (Week 3)

- [ ] Enable rotation for RDS credentials (if using RDS)
- [ ] Create Lambda for API key validation
- [ ] Set up EventBridge rules for daily validation
- [ ] Configure SNS topic for alerts
- [ ] Test rotation process end-to-end
- [ ] Document rotation procedures

### Phase 6: Backup & DR (Week 3-4)

- [ ] Create backup Lambda function
- [ ] Set up daily backup EventBridge rule
- [ ] Test backup script manually
- [ ] Test restore script in staging environment
- [ ] Enable cross-region replication to eu-west-1
- [ ] Document disaster recovery procedures

### Phase 7: Optimization (Week 4)

- [ ] Implement secret caching in containers
- [ ] Monitor API call costs for 1 week
- [ ] Optimize API call patterns
- [ ] Review and adjust IAM policies (least privilege)
- [ ] Performance test container startup times
- [ ] Document cost optimization strategies

### Phase 8: Production Cutover (Week 4)

- [ ] Final backup of all .env files
- [ ] Switch all containers to Secrets Manager
- [ ] Monitor for 48 hours
- [ ] Verify all 20 containers running correctly
- [ ] Delete .env files from VPS
- [ ] Update runbooks and documentation

---

## 11. Cost Estimate Summary

### Monthly Costs (Ziggie Cloud - 20 Containers)

| Service | Quantity | Unit Cost | Total |
|---------|----------|-----------|-------|
| Secrets Manager | 15 secrets | $0.40/secret | $6.00 |
| API Calls | ~6,000 calls | $0.05/10K | $0.03 |
| KMS Key | 1 key | $1.00/month | $1.00 |
| S3 Backup Storage | ~1 GB | $0.023/GB | $0.02 |
| Lambda (backup) | ~3,000 invocations | Free tier | $0.00 |
| Data Transfer | Minimal | Free tier | $0.00 |
| **TOTAL** | - | - | **$7.05/month** |

### Annual Cost Projection

- **Year 1**: $84.60
- **Year 2**: $84.60 (assuming no growth)
- **Year 3**: $141.00 (assuming 25 secrets)

### ROI Calculation

**Costs**:
- Implementation: 40 hours × $0 (your time) = $0
- AWS services: $7.05/month = $84.60/year

**Benefits**:
- Security incident prevention: **Priceless**
- Compliance readiness (SOC 2, ISO 27001): **High value**
- Centralized secret rotation: **Reduces operational overhead**
- Disaster recovery capability: **Business continuity**

**Conclusion**: $84.60/year is negligible compared to the risk of compromised credentials.

---

## 12. Additional Resources

### AWS Documentation

- [Secrets Manager User Guide](https://docs.aws.amazon.com/secretsmanager/)
- [Secrets Manager Best Practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)
- [Secrets Manager Pricing](https://aws.amazon.com/secrets-manager/pricing/)
- [Docker Integration Guide](https://docs.aws.amazon.com/secretsmanager/latest/userguide/integrating_docker.html)

### Security Best Practices

1. **Never log secret values** - Mask in application logs
2. **Use IAM roles, not access keys** - EC2 instance profiles
3. **Enable CloudTrail** - Audit all secret access
4. **Rotate regularly** - 30-90 day rotation for high-value secrets
5. **Use separate secrets per environment** - dev/staging/prod isolation
6. **Implement least privilege** - Each container gets only its secrets
7. **Monitor API call patterns** - Detect anomalous access
8. **Encrypt backups** - Use KMS for S3 backup encryption

### Alternative Solutions Considered

| Solution | Pros | Cons | Verdict |
|----------|------|------|---------|
| HashiCorp Vault | Full-featured, open-source | Self-hosted complexity | Not recommended (overhead) |
| AWS Parameter Store | Free, simple | No rotation, 8 KB limit | Use for non-sensitive config |
| Kubernetes Secrets | Native K8s integration | Requires K8s migration | Not applicable (Docker Compose) |
| .env files + Git-Crypt | Simple, version-controlled | No rotation, manual management | Not recommended (current state) |
| AWS Secrets Manager | Native rotation, versioning, AWS integration | $0.40/secret/month | **RECOMMENDED** |

---

## Conclusion

AWS Secrets Manager is the optimal solution for Ziggie Cloud's credential management needs. The hybrid approach (Secrets Manager for sensitive credentials + Parameter Store for config) balances security, cost, and operational simplicity.

**Key Takeaways**:

1. **Cost**: ~$7/month for 15 secrets + KMS key
2. **Security**: Native rotation, versioning, audit logging
3. **Integration**: Seamless with Docker via entrypoint scripts
4. **Disaster Recovery**: Automated backups to S3, cross-region replication
5. **Compliance**: SOC 2, ISO 27001 ready

**Next Steps**:

1. Review this document with team
2. Begin Phase 1 (Setup) - estimated 2-4 hours
3. Migrate secrets incrementally (1-2 containers per day)
4. Monitor and optimize over first month

**Success Metrics**:

- Zero credentials in .env files on VPS
- 100% secret retrieval success rate
- < 500ms container startup overhead
- Zero security incidents related to credential exposure

---

*Document maintained by Ziggie Cloud Infrastructure Team*
*Last Updated: 2025-12-23*
