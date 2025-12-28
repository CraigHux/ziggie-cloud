# AWS Secrets Manager Implementation Checklist

> **Project**: Ziggie Cloud Credential Management
> **Target**: 20 Docker containers with centralized secret management
> **Estimated Time**: 2-3 hours
> **Monthly Cost**: $7-8 USD

---

## Pre-Implementation Checklist

### Prerequisites

- [ ] AWS Account with admin access
- [ ] VPS running Docker containers
- [ ] EC2 instance in eu-north-1 region
- [ ] Access to current .env files for secret migration
- [ ] Backup of current configuration

### Required Tools

- [ ] AWS CLI v2 installed on VPS
- [ ] jq installed on VPS (`apt install jq` or `apk add jq`)
- [ ] Docker and Docker Compose installed
- [ ] SSH access to VPS

---

## Phase 1: AWS Infrastructure Setup

**Estimated Time**: 30 minutes

### 1.1 IAM Role Creation

- [ ] Create IAM role `ZiggieDockerHostRole`
  - [ ] Use trust policy: `iam-policies/ec2-instance-trust-policy.json`
  - [ ] Verify role created: `aws iam get-role --role-name ZiggieDockerHostRole`

- [ ] Create IAM policy `ZiggieSecretsReadPolicy`
  - [ ] Use policy document: `iam-policies/ziggie-secrets-read-policy.json`
  - [ ] Verify policy created: `aws iam get-policy --policy-arn <ARN>`

- [ ] Attach policy to role
  - [ ] Policy ARN saved: `___________________________________________`
  - [ ] Attachment verified

- [ ] Create instance profile `ZiggieDockerHostProfile`
  - [ ] Add role to instance profile
  - [ ] Verify: `aws iam get-instance-profile --instance-profile-name ZiggieDockerHostProfile`

### 1.2 EC2 Instance Configuration

- [ ] Identify EC2 instance ID: `i-_____________________________`
- [ ] Attach instance profile to EC2 instance
- [ ] Verify role attachment: `aws ec2 describe-instances --instance-ids <ID>`
- [ ] SSH to VPS and test credentials: `aws sts get-caller-identity`

### 1.3 AWS CLI Setup on VPS

- [ ] Install AWS CLI v2
- [ ] Configure region: `aws configure set region eu-north-1`
- [ ] Test access: `aws secretsmanager list-secrets`

---

## Phase 2: Secret Creation

**Estimated Time**: 45 minutes

### 2.1 Inventory Current Secrets

**Document all secrets from .env files:**

| Secret Name | Source Container | Current Location | Migrated? |
|-------------|------------------|------------------|-----------|
| OpenAI API Key | Backend API | `/opt/ziggie/backend/.env` | [ ] |
| ElevenLabs API Key | AI Worker | `/opt/ziggie/ai-worker/.env` | [ ] |
| Meshy.ai API Key | AI Worker | `/opt/ziggie/ai-worker/.env` | [ ] |
| Stripe Secret Key | Backend API | `/opt/ziggie/backend/.env` | [ ] |
| SendGrid API Key | Backend API | `/opt/ziggie/backend/.env` | [ ] |
| PostgreSQL Password | Postgres | `/opt/ziggie/postgres/.env` | [ ] |
| Redis Password | Redis | `/opt/ziggie/redis/.env` | [ ] |
| RabbitMQ Password | RabbitMQ | `/opt/ziggie/rabbitmq/.env` | [ ] |
| JWT Secret | Backend API | `/opt/ziggie/backend/.env` | [ ] |
| n8n Encryption Key | n8n | `/opt/ziggie/n8n/.env` | [ ] |

### 2.2 Create Secrets in AWS

**Method 1: Interactive Script (Recommended)**

- [ ] Copy `scripts/create-secrets.sh` to VPS
- [ ] Make executable: `chmod +x create-secrets.sh`
- [ ] Run script: `./create-secrets.sh`
- [ ] Follow prompts for each secret

**Method 2: Manual CLI Commands**

- [ ] Create `ziggie/prod/openai-api-key`
- [ ] Create `ziggie/prod/elevenlabs-api-key`
- [ ] Create `ziggie/prod/meshy-api-key`
- [ ] Create `ziggie/prod/stripe-secret-key`
- [ ] Create `ziggie/prod/sendgrid-api-key`
- [ ] Create `ziggie/prod/postgres-master`
- [ ] Create `ziggie/prod/redis-password`
- [ ] Create `ziggie/prod/rabbitmq-password`
- [ ] Create `ziggie/prod/jwt-secret`
- [ ] Create `ziggie/prod/n8n-encryption-key`

### 2.3 Verify Secrets

- [ ] List all secrets: `aws secretsmanager list-secrets --region eu-north-1`
- [ ] Count should be: **10 secrets minimum**
- [ ] All tagged with `Service=Ziggie` and `Environment=Production`
- [ ] Test retrieval: `aws secretsmanager get-secret-value --secret-id ziggie/prod/openai-api-key`

---

## Phase 3: Docker Configuration

**Estimated Time**: 60 minutes

### 3.1 Prepare Entrypoint Scripts

- [ ] Copy all scripts to VPS: `scp -r scripts/ your-vps:/opt/ziggie/`
- [ ] Make all scripts executable: `chmod +x /opt/ziggie/scripts/*.sh`
- [ ] Verify scripts present:
  - [ ] `entrypoint.sh` (generic)
  - [ ] `n8n-entrypoint.sh`
  - [ ] `postgres-entrypoint.sh`
  - [ ] `redis-entrypoint.sh`

### 3.2 Update Dockerfiles

**For each container type:**

- [ ] Backend API Dockerfile
  - [ ] Add `RUN apk add --no-cache aws-cli jq`
  - [ ] Copy entrypoint script
  - [ ] Set ENTRYPOINT to use script
  - [ ] Rebuild image: `docker build -t ziggie/backend:latest .`

- [ ] AI Worker Dockerfile
  - [ ] Add AWS CLI and jq
  - [ ] Copy entrypoint script
  - [ ] Rebuild image

- [ ] n8n Container
  - [ ] Volume mount `n8n-entrypoint.sh`
  - [ ] Set custom entrypoint in docker-compose

- [ ] PostgreSQL Container
  - [ ] Volume mount `postgres-entrypoint.sh`
  - [ ] Set custom entrypoint in docker-compose

- [ ] Redis Container
  - [ ] Volume mount `redis-entrypoint.sh`
  - [ ] Set custom entrypoint in docker-compose

### 3.3 Update docker-compose.yml

- [ ] Backup existing: `cp docker-compose.yml docker-compose.yml.backup`
- [ ] Add `AWS_REGION: eu-north-1` to all services
- [ ] Remove all `.env` file references
- [ ] Update entrypoints for modified services
- [ ] Add volume mounts for entrypoint scripts
- [ ] Verify syntax: `docker-compose config`

---

## Phase 4: Testing

**Estimated Time**: 30 minutes

### 4.1 Single Container Test

- [ ] Stop all containers: `docker-compose down`
- [ ] Test backend container: `docker-compose up ziggie-backend`
- [ ] Watch logs for "Secrets loaded successfully"
- [ ] Verify no errors in logs
- [ ] Stop test container: `Ctrl+C`

### 4.2 Full Stack Test

- [ ] Start all containers: `docker-compose up -d`
- [ ] Check all containers running: `docker ps`
- [ ] Check logs for each service: `docker-compose logs <service>`
- [ ] Verify secrets loaded in each container:
  - [ ] Backend API
  - [ ] AI Worker
  - [ ] n8n
  - [ ] PostgreSQL
  - [ ] Redis

### 4.3 Functional Testing

- [ ] Test API health endpoint: `curl http://localhost:3000/health`
- [ ] Test n8n access: `curl http://localhost:5678/healthz`
- [ ] Test database connection: `docker exec -it ziggie-postgres psql -U ziggie_admin -d ziggie_prod -c "SELECT 1;"`
- [ ] Test Redis connection: `docker exec -it ziggie-redis redis-cli ping`
- [ ] Test end-to-end workflow in application

---

## Phase 5: Production Cutover

**Estimated Time**: 15 minutes

### 5.1 Pre-Cutover Backup

- [ ] Backup all .env files: `mkdir -p backups/env-backup-$(date +%Y%m%d)`
- [ ] Copy all .env files to backup directory
- [ ] Verify backup: `ls -la backups/env-backup-*`
- [ ] Upload backup to S3 (optional): `aws s3 cp backups/ s3://ziggie-backups/env-files/ --recursive`

### 5.2 Cutover Execution

- [ ] Stop all containers: `docker-compose down`
- [ ] Start with new configuration: `docker-compose up -d`
- [ ] Monitor logs for 5 minutes: `docker-compose logs -f`
- [ ] Verify all services healthy
- [ ] Test critical workflows

### 5.3 Cleanup

- [ ] **CRITICAL**: Only proceed after 24-hour soak test
- [ ] Remove .env files: `find /opt/ziggie -name ".env*" -exec rm {} \;`
- [ ] Verify removal: `find /opt/ziggie -name ".env*"`
- [ ] Update documentation to reference Secrets Manager

---

## Phase 6: Backup and Monitoring

**Estimated Time**: 30 minutes

### 6.1 Backup Configuration

- [ ] Create S3 bucket for backups: `aws s3 mb s3://ziggie-disaster-recovery --region eu-north-1`
- [ ] Copy backup script to VPS: `scripts/backup-secrets.sh`
- [ ] Set environment variables:
  - [ ] `AWS_REGION=eu-north-1`
  - [ ] `BACKUP_S3_BUCKET=ziggie-disaster-recovery`
  - [ ] `KMS_KEY_ID=<your-kms-key-id>`
- [ ] Test manual backup: `./scripts/backup-secrets.sh`
- [ ] Verify backup in S3: `aws s3 ls s3://ziggie-disaster-recovery/secrets-manager/`

### 6.2 Automated Backup Setup

- [ ] Create cron job: `crontab -e`
- [ ] Add entry: `0 2 * * * /opt/ziggie/scripts/backup-secrets.sh >> /var/log/ziggie-secrets-backup.log 2>&1`
- [ ] Verify cron: `crontab -l`
- [ ] Test cron execution (wait for scheduled time or adjust for immediate test)

### 6.3 Monitoring Setup

- [ ] Enable CloudTrail for Secrets Manager API calls
- [ ] Create CloudWatch dashboard for secret access
- [ ] Set up SNS topic for alerts: `aws sns create-topic --name ziggie-secrets-alerts`
- [ ] Subscribe email to SNS topic
- [ ] Create CloudWatch alarm for unusual access patterns

---

## Phase 7: Documentation and Handoff

**Estimated Time**: 15 minutes

### 7.1 Documentation Updates

- [ ] Update operations runbook with Secrets Manager procedures
- [ ] Document secret rotation schedule
- [ ] Create disaster recovery runbook
- [ ] Update onboarding documentation for new team members

### 7.2 Team Training

- [ ] Share QUICKSTART.md with team
- [ ] Demonstrate secret retrieval process
- [ ] Walk through backup/restore procedure
- [ ] Review IAM access controls

---

## Post-Implementation Validation

### Week 1 Checks

- [ ] Day 1: Monitor all container logs for issues
- [ ] Day 2: Verify backup executed successfully
- [ ] Day 3: Test secret rotation (if applicable)
- [ ] Day 7: Review AWS costs (should be ~$7/month)

### Month 1 Checks

- [ ] Week 2: Audit CloudTrail logs for secret access
- [ ] Week 3: Test disaster recovery restore procedure
- [ ] Week 4: Review IAM policies for least privilege
- [ ] Month end: Document lessons learned

---

## Rollback Plan (If Needed)

**If issues occur, follow these steps:**

1. [ ] Stop all containers: `docker-compose down`
2. [ ] Restore .env files from backup: `cp -r backups/env-backup-YYYYMMDD/.env* /opt/ziggie/`
3. [ ] Revert docker-compose.yml: `mv docker-compose.yml.backup docker-compose.yml`
4. [ ] Restart containers: `docker-compose up -d`
5. [ ] Verify all services healthy
6. [ ] Document rollback reason for post-mortem

---

## Success Criteria

- [ ] All 20 containers running successfully
- [ ] Zero .env files on VPS
- [ ] Secrets fetched from AWS Secrets Manager on every container start
- [ ] Automated daily backups to S3
- [ ] CloudTrail auditing enabled
- [ ] Team trained on new procedures
- [ ] Monthly AWS bill ~$7 USD
- [ ] Zero application downtime during migration

---

## Troubleshooting Checklist

### Issue: Container fails to start

- [ ] Check IAM role attached to EC2 instance
- [ ] Verify AWS CLI installed in container
- [ ] Check entrypoint script has execute permissions
- [ ] Review container logs: `docker logs <container-name>`
- [ ] Test secret retrieval manually: `aws secretsmanager get-secret-value --secret-id <name>`

### Issue: "Access Denied" errors

- [ ] Verify IAM policy attached to role
- [ ] Check policy permissions include `secretsmanager:GetSecretValue`
- [ ] Ensure KMS key permissions allow decryption
- [ ] Review CloudTrail logs for denied API calls

### Issue: "Secret not found"

- [ ] Verify secret exists: `aws secretsmanager list-secrets`
- [ ] Check exact secret name matches (case-sensitive)
- [ ] Confirm region is eu-north-1
- [ ] Check secret tags include `Service=Ziggie`

---

## Cost Tracking

### Monthly Cost Breakdown

| Item | Quantity | Unit Cost | Total |
|------|----------|-----------|-------|
| Secrets Manager | 10 secrets | $0.40/secret | $4.00 |
| API Calls | ~6,000 calls | $0.05/10K | $0.03 |
| KMS Key | 1 key | $1.00/month | $1.00 |
| S3 Storage | ~1 GB | $0.023/GB | $0.02 |
| **TOTAL** | - | - | **$5.05** |

**Budget Alert**: Set CloudWatch billing alarm for $10/month threshold

---

## Contact Information

**Primary Contact**: Craig (Ziggie Cloud Owner)
**AWS Account ID**: `_______________`
**Region**: eu-north-1 (Stockholm)
**VPS IP**: `_______________`

---

## Sign-Off

- [ ] Implementation completed by: `_________________` Date: `___________`
- [ ] Verification completed by: `_________________` Date: `___________`
- [ ] Production approval by: `_________________` Date: `___________`

---

**Document Version**: 1.0
**Last Updated**: 2025-12-23
**Status**: Ready for Implementation
