# AWS Secrets Manager Quick Start Guide

> **Estimated Time**: 2-3 hours
> **Prerequisites**: AWS Account, VPS with Docker, AWS CLI installed

---

## Phase 1: AWS Setup (30 minutes)

### Step 1: Install AWS CLI on VPS

```bash
# SSH to your VPS
ssh your-vps

# Install AWS CLI v2 (Linux)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version  # Should show aws-cli/2.x.x
```

### Step 2: Create IAM Role for EC2

```bash
# On your local machine with AWS admin access

# Create IAM role
aws iam create-role \
    --role-name ZiggieDockerHostRole \
    --assume-role-policy-document file://iam-policies/ec2-instance-trust-policy.json \
    --region eu-north-1

# Create IAM policy
aws iam create-policy \
    --policy-name ZiggieSecretsReadPolicy \
    --policy-document file://iam-policies/ziggie-secrets-read-policy.json \
    --region eu-north-1

# Attach policy to role (replace ACCOUNT_ID)
aws iam attach-role-policy \
    --role-name ZiggieDockerHostRole \
    --policy-arn arn:aws:iam::ACCOUNT_ID:policy/ZiggieSecretsReadPolicy

# Create instance profile
aws iam create-instance-profile \
    --instance-profile-name ZiggieDockerHostProfile

# Add role to instance profile
aws iam add-role-to-instance-profile \
    --instance-profile-name ZiggieDockerHostProfile \
    --role-name ZiggieDockerHostRole
```

### Step 3: Attach IAM Role to EC2 Instance

```bash
# Find your EC2 instance ID
aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=ziggie-vps" \
    --query 'Reservations[0].Instances[0].InstanceId' \
    --output text \
    --region eu-north-1

# Attach instance profile (replace i-xxxxx with your instance ID)
aws ec2 associate-iam-instance-profile \
    --instance-id i-xxxxxxxxxxxxx \
    --iam-instance-profile Name=ZiggieDockerHostProfile \
    --region eu-north-1
```

### Step 4: Configure AWS CLI on VPS

```bash
# SSH to VPS
ssh your-vps

# Configure AWS CLI (use instance role, so no keys needed)
aws configure set region eu-north-1

# Test credentials
aws sts get-caller-identity
# Should show your EC2 instance role
```

---

## Phase 2: Create Secrets (45 minutes)

### Option A: Interactive Script (Recommended)

```bash
# Copy script to VPS
scp scripts/create-secrets.sh your-vps:/tmp/

# SSH to VPS and run
ssh your-vps
cd /tmp
chmod +x create-secrets.sh
./create-secrets.sh
```

The script will prompt you for each secret value.

### Option B: Manual Creation

```bash
# Create OpenAI API Key
aws secretsmanager create-secret \
    --name ziggie/prod/openai-api-key \
    --description "OpenAI API Key" \
    --secret-string '{"api_key":"[REDACTED-OPENAI-KEY]"}' \
    --tags Key=Environment,Value=Production Key=Service,Value=Ziggie \
    --region eu-north-1

# Create ElevenLabs API Key
aws secretsmanager create-secret \
    --name ziggie/prod/elevenlabs-api-key \
    --description "ElevenLabs API Key" \
    --secret-string '{"api_key":"YOUR_KEY_HERE"}' \
    --tags Key=Environment,Value=Production Key=Service,Value=Ziggie \
    --region eu-north-1

# Create Meshy.ai API Key
aws secretsmanager create-secret \
    --name ziggie/prod/meshy-api-key \
    --description "Meshy.ai API Key" \
    --secret-string '{"api_key":"YOUR_KEY_HERE"}' \
    --tags Key=Environment,Value=Production Key=Service,Value=Ziggie \
    --region eu-north-1

# Create Database Credentials
aws secretsmanager create-secret \
    --name ziggie/prod/postgres-master \
    --description "PostgreSQL master credentials" \
    --secret-string '{
        "username": "ziggie_admin",
        "password": "YOUR_STRONG_PASSWORD",
        "host": "postgres",
        "port": 5432,
        "dbname": "ziggie_prod",
        "engine": "postgres",
        "connection_string": "postgresql://ziggie_admin:YOUR_STRONG_PASSWORD@postgres:5432/ziggie_prod"
    }' \
    --tags Key=Environment,Value=Production Key=Service,Value=Ziggie \
    --region eu-north-1

# Create JWT Secret
aws secretsmanager create-secret \
    --name ziggie/prod/jwt-secret \
    --description "JWT signing secret" \
    --secret-string '{"secret":"YOUR_RANDOM_256BIT_STRING"}' \
    --tags Key=Environment,Value=Production Key=Service,Value=Ziggie \
    --region eu-north-1

# Create Redis Password
aws secretsmanager create-secret \
    --name ziggie/prod/redis-password \
    --description "Redis password" \
    --secret-string '{"password":"YOUR_REDIS_PASSWORD"}' \
    --tags Key=Environment,Value=Production Key=Service,Value=Ziggie \
    --region eu-north-1

# Create RabbitMQ Password
aws secretsmanager create-secret \
    --name ziggie/prod/rabbitmq-password \
    --description "RabbitMQ password" \
    --secret-string '{"password":"YOUR_RABBITMQ_PASSWORD"}' \
    --tags Key=Environment,Value=Production Key=Service,Value=Ziggie \
    --region eu-north-1

# Create n8n Encryption Key
aws secretsmanager create-secret \
    --name ziggie/prod/n8n-encryption-key \
    --description "n8n encryption key" \
    --secret-string '{"key":"YOUR_N8N_ENCRYPTION_KEY"}' \
    --tags Key=Environment,Value=Production Key=Service,Value=Ziggie \
    --region eu-north-1
```

### Verify Secrets

```bash
# List all Ziggie secrets
aws secretsmanager list-secrets \
    --region eu-north-1 \
    --query 'SecretList[?Tags[?Key==`Service` && Value==`Ziggie`]].Name' \
    --output table

# Should show:
# -----------------------------------
# |         ListSecrets             |
# +---------------------------------+
# |  ziggie/prod/openai-api-key     |
# |  ziggie/prod/elevenlabs-api-key |
# |  ziggie/prod/meshy-api-key      |
# |  ziggie/prod/postgres-master    |
# |  ziggie/prod/jwt-secret         |
# |  ziggie/prod/redis-password     |
# |  ziggie/prod/rabbitmq-password  |
# |  ziggie/prod/n8n-encryption-key |
# +---------------------------------+
```

---

## Phase 3: Update Docker Containers (60 minutes)

### Step 1: Copy Entrypoint Scripts to VPS

```bash
# From your local machine
scp -r scripts/ your-vps:/opt/ziggie/

# SSH to VPS
ssh your-vps
cd /opt/ziggie
chmod +x scripts/*.sh
```

### Step 2: Update Dockerfile (Example: Backend API)

```dockerfile
FROM node:20-alpine

# Install AWS CLI and jq for secret fetching
RUN apk add --no-cache aws-cli jq

WORKDIR /app

# Copy application files
COPY package*.json ./
RUN npm ci --only=production
COPY . .

# Copy entrypoint script
COPY scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Use entrypoint to fetch secrets before starting app
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["node", "dist/index.js"]
```

### Step 3: Rebuild Images

```bash
# On VPS
cd /opt/ziggie

# Rebuild backend image
docker build -t ziggie/backend:latest -f backend/Dockerfile .

# Rebuild other images as needed
docker build -t ziggie/ai-worker:latest -f ai-worker/Dockerfile .
```

### Step 4: Update docker-compose.yml

```yaml
version: '3.8'

services:
  ziggie-backend:
    image: ziggie/backend:latest
    container_name: ziggie-backend
    restart: unless-stopped
    environment:
      AWS_REGION: eu-north-1
      NODE_ENV: production
    ports:
      - "3000:3000"
    networks:
      - ziggie-network

  n8n:
    image: n8nio/n8n:latest
    container_name: ziggie-n8n
    restart: unless-stopped
    entrypoint: ["/scripts/n8n-entrypoint.sh"]
    volumes:
      - /opt/ziggie/scripts/n8n-entrypoint.sh:/scripts/n8n-entrypoint.sh:ro
      - n8n_data:/home/node/.n8n
    environment:
      AWS_REGION: eu-north-1
      N8N_HOST: n8n.ziggie.cloud
      N8N_PROTOCOL: https
    ports:
      - "5678:5678"
    networks:
      - ziggie-network

  postgres:
    image: postgres:15-alpine
    container_name: ziggie-postgres
    restart: unless-stopped
    entrypoint: ["/scripts/postgres-entrypoint.sh"]
    volumes:
      - /opt/ziggie/scripts/postgres-entrypoint.sh:/scripts/postgres-entrypoint.sh:ro
      - postgres_data:/var/lib/postgresql/data
    environment:
      AWS_REGION: eu-north-1
      POSTGRES_DB: ziggie_prod
    networks:
      - ziggie-network

  redis:
    image: redis:7-alpine
    container_name: ziggie-redis
    restart: unless-stopped
    entrypoint: ["/scripts/redis-entrypoint.sh"]
    volumes:
      - /opt/ziggie/scripts/redis-entrypoint.sh:/scripts/redis-entrypoint.sh:ro
      - redis_data:/data
    environment:
      AWS_REGION: eu-north-1
    networks:
      - ziggie-network

networks:
  ziggie-network:
    driver: bridge

volumes:
  n8n_data:
  postgres_data:
  redis_data:
```

---

## Phase 4: Test Single Container (15 minutes)

### Test Backend Container

```bash
# Stop all containers
docker-compose down

# Start only backend for testing
docker-compose up ziggie-backend

# Watch logs for "Secrets loaded successfully"
# Should see:
# === Ziggie Container Startup ===
# Fetching secrets from AWS Secrets Manager...
# Secrets loaded successfully
# Starting application...
```

### Verify Secrets Are Loaded

```bash
# Exec into container
docker exec -it ziggie-backend sh

# Check environment variables (don't print actual values in prod!)
env | grep -i "API_KEY" | sed 's/=.*/=***REDACTED***/'

# Should show:
# OPENAI_API_KEY=***REDACTED***
# ELEVENLABS_API_KEY=***REDACTED***
# MESHY_API_KEY=***REDACTED***
```

---

## Phase 5: Full Deployment (30 minutes)

### Step 1: Backup Current .env Files

```bash
# On VPS
cd /opt/ziggie
mkdir -p backups/env-backup-$(date +%Y%m%d)
find . -name ".env*" -exec cp {} backups/env-backup-$(date +%Y%m%d)/ \;
```

### Step 2: Deploy All Containers

```bash
# Stop all containers
docker-compose down

# Start all containers with new configuration
docker-compose up -d

# Watch logs for all containers
docker-compose logs -f
```

### Step 3: Verify All Services

```bash
# Check all containers are running
docker ps

# Test API endpoint
curl http://localhost:3000/health

# Test n8n
curl http://localhost:5678/healthz

# Test database connection
docker exec -it ziggie-postgres psql -U ziggie_admin -d ziggie_prod -c "SELECT 1;"
```

### Step 4: Remove .env Files (CRITICAL)

```bash
# Only after verifying everything works!
cd /opt/ziggie
find . -name ".env*" -exec rm {} \;

# Verify no .env files remain
find . -name ".env*"
# Should return nothing
```

---

## Phase 6: Setup Backups (15 minutes)

### Create Backup Cron Job

```bash
# On VPS
crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/ziggie/scripts/backup-secrets.sh >> /var/log/ziggie-secrets-backup.log 2>&1
```

### Test Backup Script

```bash
cd /opt/ziggie
export AWS_REGION=eu-north-1
export BACKUP_S3_BUCKET=ziggie-disaster-recovery
export KMS_KEY_ID=arn:aws:kms:eu-north-1:ACCOUNT_ID:key/KEY_ID

./scripts/backup-secrets.sh
```

---

## Troubleshooting

### Issue: "Unable to locate credentials"

**Solution**: EC2 instance role not attached or configured incorrectly

```bash
# Verify instance has role
aws sts get-caller-identity

# Should show:
# {
#     "UserId": "AROA...:i-xxxxx",
#     "Account": "123456789012",
#     "Arn": "arn:aws:sts::123456789012:assumed-role/ZiggieDockerHostRole/i-xxxxx"
# }
```

### Issue: "Access Denied" when fetching secrets

**Solution**: IAM policy missing permissions

```bash
# Check attached policies
aws iam list-attached-role-policies --role-name ZiggieDockerHostRole

# Verify policy has secretsmanager:GetSecretValue
aws iam get-policy-version \
    --policy-arn arn:aws:iam::ACCOUNT_ID:policy/ZiggieSecretsReadPolicy \
    --version-id v1
```

### Issue: Container fails to start with "command not found: aws"

**Solution**: AWS CLI not installed in Docker image

```dockerfile
# Add to Dockerfile
RUN apk add --no-cache aws-cli jq  # Alpine
# OR
RUN apt-get update && apt-get install -y awscli jq  # Debian/Ubuntu
```

### Issue: "Secret not found"

**Solution**: Secret name mismatch or wrong region

```bash
# List all secrets
aws secretsmanager list-secrets --region eu-north-1

# Verify exact name matches
aws secretsmanager get-secret-value \
    --secret-id ziggie/prod/openai-api-key \
    --region eu-north-1
```

---

## Cost Monitoring

```bash
# Check current month costs
aws ce get-cost-and-usage \
    --time-period Start=$(date -d "$(date +%Y-%m-01)" +%Y-%m-%d),End=$(date +%Y-%m-%d) \
    --granularity MONTHLY \
    --metrics UnblendedCost \
    --filter file://cost-filter.json

# cost-filter.json
{
  "Dimensions": {
    "Key": "SERVICE",
    "Values": ["AWS Secrets Manager"]
  }
}
```

---

## Next Steps

1. **Enable CloudTrail** - Audit all secret access
2. **Set up CloudWatch Alarms** - Alert on unusual access patterns
3. **Document rotation procedures** - For API keys
4. **Test disaster recovery** - Run restore script in staging
5. **Review IAM policies quarterly** - Ensure least privilege

---

## Support

- **AWS Documentation**: https://docs.aws.amazon.com/secretsmanager/
- **Full Research**: See AWS_SECRETS_MANAGER_RESEARCH.md
- **Issues**: Create ticket with logs from `docker-compose logs`

---

**Estimated Monthly Cost**: $7-8 USD
**Implementation Time**: 2-3 hours
**Security Improvement**: 10/10 (eliminates .env file exposure)
