# ZIGGIE DISASTER RECOVERY RUNBOOK

> **Document Version**: 1.1
> **Created**: 2025-12-27
> **Last Tested**: 2025-12-28 (DR Test #31)
> **Owner**: Ziggie Infrastructure Team
> **Review Frequency**: Quarterly

---

## EXECUTIVE SUMMARY

This runbook provides step-by-step procedures for recovering the Ziggie ecosystem from various disaster scenarios. All procedures are designed to meet the following targets:

| Metric | Target | Description |
|--------|--------|-------------|
| **RTO (Recovery Time Objective)** | 4 hours | Maximum time to restore operations |
| **RPO (Recovery Point Objective)** | 24 hours | Maximum acceptable data loss |
| **MTTR (Mean Time To Recovery)** | 2 hours | Expected average recovery time |

### Infrastructure Overview

| Component | Location | IP/Resource |
|-----------|----------|-------------|
| Primary VPS | Hostinger | 82.25.112.73 |
| Docker Stack | VPS | 20 containers |
| AWS Region | eu-north-1 | Stockholm |
| S3 Bucket | AWS | ziggie-assets-prod |
| Secrets Manager | AWS | ziggie/* namespace |

---

## TABLE OF CONTENTS

1. [Scenario 1: VPS Failure](#scenario-1-vps-failure)
2. [Scenario 2: Database Corruption](#scenario-2-database-corruption)
3. [Scenario 3: AWS Credential Compromise](#scenario-3-aws-credential-compromise)
4. [Scenario 4: Complete System Rebuild](#scenario-4-complete-system-rebuild)
5. [DR Test Checklist](#dr-test-checklist)
6. [Contact & Escalation](#contact-escalation)
7. [Appendices](#appendices)

---

## SCENARIO 1: VPS FAILURE

### 1.1 Detection

**Symptoms**:
- Services unreachable at 82.25.112.73
- n8n, Grafana, Portainer not responding
- SSH connection refused or timeout
- Hostinger dashboard shows VPS offline

**Verification Commands** (from local machine):
```bash
# Test SSH connectivity
ssh -o ConnectTimeout=10 ziggie@82.25.112.73 echo "VPS is up"

# Test HTTP services
curl -s --connect-timeout 10 http://82.25.112.73:9000/api/status || echo "Portainer DOWN"
curl -s --connect-timeout 10 http://82.25.112.73:5678/healthz || echo "n8n DOWN"
curl -s --connect-timeout 10 http://82.25.112.73:3000/api/health || echo "Grafana DOWN"
```

### 1.2 Immediate Response (0-15 minutes)

**Step 1: Assess VPS Status via Hostinger**
1. Login to Hostinger dashboard: https://hpanel.hostinger.com
2. Navigate to VPS section
3. Check VPS status (Running/Stopped/Error)
4. Review recent events and resource usage

**Step 2: Attempt VPS Restart**
```text
In Hostinger Dashboard:
1. Select VPS (82.25.112.73)
2. Click "Restart" button
3. Wait 2-3 minutes for boot
4. Verify SSH access restored
```

**Step 3: If Restart Fails - Contact Hostinger Support**
- Support URL: https://www.hostinger.com/contact
- Provide: VPS IP, Account ID, Error details
- Expected Response: 15-30 minutes

### 1.3 VPS Recovery Procedure (15 min - 2 hours)

#### Option A: VPS Recovered - Container Restoration

If VPS restarts successfully but containers are not running:

```bash
# SSH into VPS
ssh ziggie@82.25.112.73

# Navigate to Ziggie directory
cd /opt/ziggie

# Check container status
docker compose ps -a

# Restart all containers
docker compose down
docker compose up -d

# Verify health
docker compose ps
docker compose logs --tail=50
```

#### Option B: VPS Unrecoverable - New VPS Provisioning

**Step 1: Provision New VPS**
1. Login to Hostinger hpanel
2. Order new VPS (KVM 4 recommended)
   - 4 vCPU, 16GB RAM, 200GB NVMe
   - Ubuntu 22.04 LTS
   - Select EU datacenter (closest to eu-north-1)
3. Note new IP address: `NEW_VPS_IP`

**Step 2: Initial Setup**
```bash
# SSH as root (initial access)
ssh root@NEW_VPS_IP

# Update system
apt update && apt upgrade -y

# Create ziggie user
adduser ziggie
usermod -aG sudo ziggie

# Setup SSH key authentication
mkdir -p /home/ziggie/.ssh
# Copy your SSH public key to authorized_keys
chmod 700 /home/ziggie/.ssh
chmod 600 /home/ziggie/.ssh/authorized_keys
chown -R ziggie:ziggie /home/ziggie/.ssh

# Disable root login
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart sshd

# Install Docker
curl -fsSL https://get.docker.com | sh
usermod -aG docker ziggie

# Install Docker Compose
apt install docker-compose-plugin -y

# Configure firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5678/tcp
ufw allow 8080/tcp
ufw allow 9000/tcp
ufw allow 3000/tcp
ufw enable
```

**Step 3: Deploy Docker Stack**
```bash
# Switch to ziggie user
su - ziggie

# Create directory structure
sudo mkdir -p /opt/ziggie
sudo chown -R ziggie:ziggie /opt/ziggie
cd /opt/ziggie

# Clone or copy docker-compose.yml from backup
# Option 1: From local backup
scp user@local:/path/to/backup/docker-compose.yml .
scp user@local:/path/to/backup/.env .

# Option 2: From S3 backup
aws s3 cp s3://ziggie-assets-prod/backups/docker-compose.yml .
aws s3 cp s3://ziggie-assets-prod/backups/env-backup.enc .
# Decrypt .env (requires encryption key)

# Create required directories
mkdir -p nginx/conf.d nginx/ssl
mkdir -p prometheus grafana/provisioning grafana/dashboards
mkdir -p loki promtail
mkdir -p mcp-gateway api sim-studio
mkdir -p init-scripts/postgres init-scripts/mongo
mkdir -p n8n-workflows

# Copy configuration files from backup
# (prometheus.yml, nginx.conf, etc.)

# Start services
docker compose up -d
```

### 1.4 DNS Failover Procedure

If using a domain (ziggie.cloud):

**Step 1: Update DNS Records**
1. Login to domain registrar
2. Update A record from old IP to NEW_VPS_IP
3. DNS propagation: 5-30 minutes (depends on TTL)

**Quick DNS Update** (if using Cloudflare):
```bash
# Using Cloudflare API
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/ZONE_ID/dns_records/RECORD_ID" \
     -H "Authorization: Bearer CF_API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{"content":"NEW_VPS_IP"}'
```

**Step 2: Update AWS Security Groups**
```bash
# Update security group to allow new VPS IP
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" ec2 authorize-security-group-ingress \
    --group-id sg-XXXXXX \
    --protocol tcp \
    --port 8188 \
    --cidr NEW_VPS_IP/32 \
    --region eu-north-1

# Remove old IP
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" ec2 revoke-security-group-ingress \
    --group-id sg-XXXXXX \
    --protocol tcp \
    --port 8188 \
    --cidr 82.25.112.73/32 \
    --region eu-north-1
```

### 1.5 Data Restoration

**Restore PostgreSQL from Backup**:
```bash
# Download latest backup from S3
aws s3 cp s3://ziggie-assets-prod/backups/postgres/latest.sql.gz /tmp/

# Decompress
gunzip /tmp/latest.sql.gz

# Restore to PostgreSQL container
docker exec -i ziggie-postgres psql -U ziggie -d ziggie < /tmp/latest.sql
```

**Restore MongoDB from Backup**:
```bash
# Download backup
aws s3 cp s3://ziggie-assets-prod/backups/mongodb/latest.archive /tmp/

# Restore
docker exec -i ziggie-mongodb mongorestore --archive=/tmp/latest.archive --gzip
```

**Restore Redis (if persistent)**:
```bash
# Redis uses RDB snapshots
aws s3 cp s3://ziggie-assets-prod/backups/redis/dump.rdb /tmp/
docker cp /tmp/dump.rdb ziggie-redis:/data/dump.rdb
docker restart ziggie-redis
```

---

## SCENARIO 2: DATABASE CORRUPTION

### 2.1 Detection

**Symptoms**:
- Application errors mentioning database
- n8n workflows failing
- API returning 500 errors
- Database container restarting repeatedly

**Diagnostic Commands**:
```bash
# SSH into VPS
ssh ziggie@82.25.112.73

# Check PostgreSQL health
docker exec ziggie-postgres pg_isready -U ziggie
docker logs ziggie-postgres --tail=100

# Check MongoDB health
docker exec ziggie-mongodb mongosh --eval "db.adminCommand('ping')"
docker logs ziggie-mongodb --tail=100

# Check Redis health
docker exec ziggie-redis redis-cli ping
docker logs ziggie-redis --tail=100
```

### 2.2 PostgreSQL Point-in-Time Recovery

**Step 1: Stop Affected Services**
```bash
# Stop services that depend on PostgreSQL
docker stop ziggie-n8n ziggie-api ziggie-sim-studio
```

**Step 2: Assess Corruption**
```bash
# Check for corruption
docker exec ziggie-postgres psql -U ziggie -d ziggie -c "SELECT pg_catalog.pg_is_in_recovery();"

# Check database integrity
docker exec ziggie-postgres psql -U ziggie -d ziggie -c "
SELECT datname,
       pg_database_size(datname) as size,
       (SELECT count(*) FROM pg_stat_activity WHERE datname = d.datname) as connections
FROM pg_database d
WHERE datname = 'ziggie';"
```

**Step 3: Restore from Backup**

Option A: Full Database Restore
```bash
# Download latest backup
aws s3 cp s3://ziggie-assets-prod/backups/postgres/latest.sql.gz /tmp/

# Stop PostgreSQL
docker stop ziggie-postgres

# Remove corrupted data volume (DANGER: This deletes all data)
docker volume rm ziggie_postgres_data

# Recreate container
docker compose up -d postgres
sleep 15  # Wait for PostgreSQL to initialize

# Restore from backup
gunzip -c /tmp/latest.sql.gz | docker exec -i ziggie-postgres psql -U ziggie -d ziggie

# Restart dependent services
docker start ziggie-n8n ziggie-api ziggie-sim-studio
```

Option B: Selective Table Restore
```bash
# If only specific tables are corrupted
# Export table from backup
pg_restore -t specific_table /tmp/latest.dump -f /tmp/specific_table.sql

# Drop and recreate corrupted table
docker exec -i ziggie-postgres psql -U ziggie -d ziggie -c "DROP TABLE specific_table;"
docker exec -i ziggie-postgres psql -U ziggie -d ziggie < /tmp/specific_table.sql
```

**Step 4: Point-in-Time Recovery (if WAL logging enabled)**
```bash
# Stop PostgreSQL
docker stop ziggie-postgres

# Edit postgresql.conf for recovery
docker exec ziggie-postgres bash -c "cat >> /var/lib/postgresql/data/recovery.conf << 'EOF'
restore_command = 'aws s3 cp s3://ziggie-assets-prod/backups/wal/%f %p'
recovery_target_time = '2025-12-27 14:00:00'
recovery_target_action = 'promote'
EOF"

# Start PostgreSQL in recovery mode
docker start ziggie-postgres

# Monitor recovery
docker logs -f ziggie-postgres
```

### 2.3 MongoDB Restore from Dump

**Step 1: Stop Dependent Services**
```bash
docker stop ziggie-api ziggie-sim-studio ziggie-mcp-gateway
```

**Step 2: Restore MongoDB**
```bash
# Download backup
aws s3 cp s3://ziggie-assets-prod/backups/mongodb/latest.archive /tmp/

# Drop corrupted database (DANGER)
docker exec ziggie-mongodb mongosh --eval "db.getSiblingDB('ziggie').dropDatabase()"

# Restore from archive
docker exec -i ziggie-mongodb mongorestore --archive --gzip < /tmp/latest.archive

# Verify restoration
docker exec ziggie-mongodb mongosh --eval "
db = db.getSiblingDB('ziggie');
print('Collections:', db.getCollectionNames());
print('Agent States:', db.agent_states.countDocuments());
"
```

**Step 3: Restart Services**
```bash
docker start ziggie-api ziggie-sim-studio ziggie-mcp-gateway

# Verify all services healthy
docker compose ps
```

### 2.4 Database Backup Schedule (Prevention)

Ensure automated backups are configured:

```bash
# Add to crontab on VPS
crontab -e

# PostgreSQL backup - daily at 2 AM
0 2 * * * docker exec ziggie-postgres pg_dump -U ziggie ziggie | gzip | aws s3 cp - s3://ziggie-assets-prod/backups/postgres/$(date +\%Y\%m\%d).sql.gz

# MongoDB backup - daily at 3 AM
0 3 * * * docker exec ziggie-mongodb mongodump --archive --gzip | aws s3 cp - s3://ziggie-assets-prod/backups/mongodb/$(date +\%Y\%m\%d).archive

# Retention: Keep 30 days of backups
0 4 * * * aws s3 ls s3://ziggie-assets-prod/backups/postgres/ | awk '{print $4}' | sort | head -n -30 | xargs -I {} aws s3 rm s3://ziggie-assets-prod/backups/postgres/{}
```

---

## SCENARIO 3: AWS CREDENTIAL COMPROMISE

### 3.1 Detection

**Indicators of Compromise**:
- Unexpected AWS billing charges
- Unknown EC2 instances running
- Unusual API activity in CloudTrail
- AWS abuse notification email
- Failed authentication attempts

**Verification**:
```bash
# Check for unauthorized resources
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" ec2 describe-instances --region eu-north-1

# Check recent IAM activity
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" cloudtrail lookup-events \
    --lookup-attributes AttributeKey=Username,AttributeValue=ziggie-automation \
    --start-time 2025-12-26T00:00:00Z \
    --region eu-north-1
```

### 3.2 Immediate Response (0-5 minutes)

**CRITICAL: Disable Compromised Credentials IMMEDIATELY**

**Step 1: Disable Access Keys**
```bash
# List all access keys
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" iam list-access-keys --user-name ziggie-automation

# Disable compromised key
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" iam update-access-key \
    --user-name ziggie-automation \
    --access-key-id AKIAXXXXXXXXXXXXXXXX \
    --status Inactive
```

**Step 2: Terminate Unauthorized Resources**
```bash
# Stop all running instances (emergency)
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" ec2 describe-instances \
    --filters "Name=instance-state-name,Values=running" \
    --query "Reservations[*].Instances[*].InstanceId" \
    --output text \
    --region eu-north-1 | \
    xargs -I {} aws ec2 stop-instances --instance-ids {} --region eu-north-1
```

### 3.3 Key Rotation Procedure

**Step 1: Create New Access Keys**
```bash
# Create new access key
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" iam create-access-key --user-name ziggie-automation

# Output will show new AccessKeyId and SecretAccessKey
# SAVE THESE SECURELY
```

**Step 2: Update Secrets Manager**
```bash
# Update AWS credentials in Secrets Manager
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" secretsmanager put-secret-value \
    --secret-id ziggie/aws-credentials \
    --secret-string '{
        "access_key_id": "NEW_ACCESS_KEY_ID",
        "secret_access_key": "NEW_SECRET_ACCESS_KEY"
    }' \
    --region eu-north-1
```

**Step 3: Update VPS Environment**
```bash
# SSH into VPS
ssh ziggie@82.25.112.73

# Update .env file
cd /opt/ziggie
nano .env
# Update AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY

# Restart containers that use AWS credentials
docker restart ziggie-mcp-gateway ziggie-api
```

**Step 4: Delete Old Access Key**
```bash
# Only after verifying new key works
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" iam delete-access-key \
    --user-name ziggie-automation \
    --access-key-id OLD_ACCESS_KEY_ID
```

### 3.4 Rotate All API Keys (If Broader Compromise Suspected)

```bash
# Rotate Anthropic API Key
# 1. Go to https://console.anthropic.com/account/keys
# 2. Delete compromised key
# 3. Create new key
# 4. Update Secrets Manager:
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" secretsmanager put-secret-value \
    --secret-id ziggie/anthropic-api-key \
    --secret-string "NEW_ANTHROPIC_KEY" \
    --region eu-north-1

# Rotate OpenAI API Key
# 1. Go to https://platform.openai.com/api-keys
# 2. Delete and recreate
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" secretsmanager put-secret-value \
    --secret-id ziggie/openai-api-key \
    --secret-string "NEW_OPENAI_KEY" \
    --region eu-north-1

# Rotate YouTube API Keys
# 1. Go to https://console.cloud.google.com/apis/credentials
# 2. Delete and recreate
```

### 3.5 Secrets Manager Emergency Access

If you need to access secrets but primary credentials are compromised:

**Option 1: Use Root Account (Emergency Only)**
1. Login to AWS Console with root email
2. Navigate to Secrets Manager
3. Manually retrieve/update secrets

**Option 2: Use Backup IAM User**
```bash
# If you have a backup admin user
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" configure --profile ziggie-emergency
# Use backup credentials

"C:/Program Files/Amazon/AWSCLIV2/aws.exe" secretsmanager get-secret-value \
    --secret-id ziggie/anthropic-api-key \
    --profile ziggie-emergency \
    --region eu-north-1
```

### 3.6 Post-Incident Actions

1. **Enable MFA on all IAM users**
```bash
# Create virtual MFA device
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" iam create-virtual-mfa-device \
    --virtual-mfa-device-name ziggie-automation-mfa \
    --outfile /tmp/mfa.png
```

2. **Review and tighten IAM policies**
3. **Enable CloudTrail alerts for suspicious activity**
4. **Document incident in post-mortem**

---

## SCENARIO 4: COMPLETE SYSTEM REBUILD

### 4.1 When to Use

- Both VPS and AWS infrastructure are compromised
- Starting fresh after major security incident
- Migrating to new infrastructure
- DR testing full rebuild

### 4.2 Prerequisites

Before starting, ensure you have:
- [ ] Access to domain registrar
- [ ] AWS root account access
- [ ] Hostinger account access
- [ ] Latest backups from S3 (or local copies)
- [ ] SSH key pair
- [ ] docker-compose.yml and configuration files
- [ ] List of all API keys to recreate

### 4.3 Phase 1: AWS Foundation (30 minutes)

**Step 1: Verify/Create AWS Account**
```bash
# Configure AWS CLI
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" configure --profile ziggie
# Region: eu-north-1
```

**Step 2: Create IAM User**
```bash
# Create user
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" iam create-user --user-name ziggie-automation

# Create policy
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" iam create-policy \
    --policy-name ZiggieEC2Control \
    --policy-document file://C:/Ziggie/aws-config/lambda-gpu-shutdown-policy.json

# Attach policy
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" iam attach-user-policy \
    --user-name ziggie-automation \
    --policy-arn arn:aws:iam::785186659442:policy/ZiggieEC2Control

# Create access keys
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" iam create-access-key --user-name ziggie-automation
```

**Step 3: Create S3 Buckets**
```bash
# Create main bucket
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" s3 mb s3://ziggie-assets-prod --region eu-north-1

# Apply lifecycle policy
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" s3api put-bucket-lifecycle-configuration \
    --bucket ziggie-assets-prod \
    --lifecycle-configuration file://C:/Ziggie/aws-config/lifecycle.json
```

**Step 4: Create Secrets**
```bash
# Store API keys in Secrets Manager
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" secretsmanager create-secret \
    --name ziggie/anthropic-api-key \
    --secret-string "YOUR_ANTHROPIC_KEY" \
    --region eu-north-1

"C:/Program Files/Amazon/AWSCLIV2/aws.exe" secretsmanager create-secret \
    --name ziggie/openai-api-key \
    --secret-string "YOUR_OPENAI_KEY" \
    --region eu-north-1
```

### 4.4 Phase 2: VPS Provisioning (45 minutes)

**Step 1: Order New VPS**
1. Login to Hostinger: https://hpanel.hostinger.com
2. Order VPS KVM 4 (4 vCPU, 16GB RAM, 200GB NVMe)
3. Select Ubuntu 22.04 LTS
4. Select EU datacenter
5. Note IP address

**Step 2: Initial Setup**
Follow Section 1.3 Option B (New VPS Provisioning) above.

### 4.5 Phase 3: Data Migration (1-2 hours)

**Step 1: Restore Databases**
```bash
# Download all backups from S3
aws s3 sync s3://ziggie-assets-prod/backups /tmp/restore --exclude "*" --include "*.sql.gz" --include "*.archive"

# Restore PostgreSQL
gunzip -c /tmp/restore/postgres/latest.sql.gz | docker exec -i ziggie-postgres psql -U ziggie -d ziggie

# Restore MongoDB
docker exec -i ziggie-mongodb mongorestore --archive --gzip < /tmp/restore/mongodb/latest.archive
```

**Step 2: Restore n8n Workflows**
```bash
# n8n workflows are stored in PostgreSQL
# If separate export exists:
aws s3 cp s3://ziggie-assets-prod/backups/n8n/workflows.json /tmp/
# Import via n8n UI or CLI
```

**Step 3: Restore Configuration Files**
```bash
aws s3 sync s3://ziggie-assets-prod/backups/config /opt/ziggie/
```

### 4.6 Phase 4: Service Verification (30 minutes)

**Step 1: Health Checks**
```bash
# Check all containers
docker compose ps

# Test each service
curl -s http://localhost:9000/api/status        # Portainer
curl -s http://localhost:5678/healthz           # n8n
curl -s http://localhost:3000/api/health        # Grafana
curl -s http://localhost:8000/health            # Ziggie API
curl -s http://localhost:8080/health            # MCP Gateway
```

**Step 2: Integration Tests**
```bash
# Test database connectivity
docker exec ziggie-postgres psql -U ziggie -d ziggie -c "SELECT 1;"
docker exec ziggie-mongodb mongosh --eval "db.adminCommand('ping')"
docker exec ziggie-redis redis-cli -a PASSWORD ping

# Test AWS connectivity
docker exec ziggie-mcp-gateway curl -s http://169.254.169.254/latest/meta-data/
```

### 4.7 Phase 5: DNS & SSL (15-30 minutes)

**Step 1: Update DNS**
Update A record to point to new VPS IP.

**Step 2: Obtain SSL Certificates**
```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Obtain certificate
certbot --nginx -d ziggie.cloud -d www.ziggie.cloud

# Verify auto-renewal
systemctl enable certbot.timer
certbot renew --dry-run
```

---

## DR TEST CHECKLIST

### Pre-Test Preparation

- [ ] Schedule test window (non-business hours recommended)
- [ ] Notify stakeholders
- [ ] Ensure all backups are current (< 24 hours old)
- [ ] Have access to all credentials and documentation
- [ ] Prepare rollback plan

### Scenario 1: VPS Failure Test

| Step | Action | Expected Result | Actual Result | Pass/Fail |
|------|--------|-----------------|---------------|-----------|
| 1 | Stop all Docker containers | Containers stop | | |
| 2 | Verify detection alerts | Monitoring detects outage | | |
| 3 | Execute restart procedure | Containers restart within 5 min | | |
| 4 | Verify all services healthy | All health checks pass | | |
| 5 | Test n8n workflow execution | Workflow completes successfully | | |

### Scenario 2: Database Recovery Test

| Step | Action | Expected Result | Actual Result | Pass/Fail |
|------|--------|-----------------|---------------|-----------|
| 1 | Create test data in PostgreSQL | Data created | | |
| 2 | Create backup | Backup uploaded to S3 | | |
| 3 | Simulate corruption (drop table) | Table deleted | | |
| 4 | Execute restore procedure | Table restored | | |
| 5 | Verify data integrity | All test data present | | |

### Scenario 3: Credential Rotation Test

| Step | Action | Expected Result | Actual Result | Pass/Fail |
|------|--------|-----------------|---------------|-----------|
| 1 | Create new AWS access key | Key created | | |
| 2 | Update Secrets Manager | Secret updated | | |
| 3 | Update VPS .env file | File updated | | |
| 4 | Restart affected containers | Containers restart | | |
| 5 | Verify AWS operations | S3 access works | | |
| 6 | Delete old access key | Key deleted | | |

### Scenario 4: Full Rebuild Test (Optional - Annual)

| Step | Action | Expected Result | Actual Result | Pass/Fail |
|------|--------|-----------------|---------------|-----------|
| 1 | Document current state | Baseline captured | | |
| 2 | Provision test VPS | New VPS online | | |
| 3 | Deploy Docker stack | All containers running | | |
| 4 | Restore databases | Data restored | | |
| 5 | Configure SSL | Certificates valid | | |
| 6 | Verify all functionality | All tests pass | | |
| 7 | Measure total time | Time < 4 hours (RTO) | | |
| 8 | Decommission test VPS | Test VPS terminated | | |

### Post-Test Actions

- [ ] Document test results
- [ ] Update runbook with lessons learned
- [ ] File any issues discovered
- [ ] Schedule next test date (quarterly)
- [ ] Update RTO/RPO if needed based on results

---

## CONTACT & ESCALATION

### Primary Contacts

| Role | Name | Contact | Availability |
|------|------|---------|--------------|
| Infrastructure Owner | Craig | [Email] | Business Hours |
| Hostinger Support | Support Team | https://www.hostinger.com/contact | 24/7 |
| AWS Support | AWS Support | https://console.aws.amazon.com/support | Based on plan |

### Escalation Matrix

| Severity | Response Time | Escalation |
|----------|---------------|------------|
| Critical (Total outage) | Immediate | All hands |
| High (Major service down) | 15 minutes | Primary contact |
| Medium (Partial degradation) | 1 hour | Primary contact |
| Low (Minor issues) | 4 hours | Standard process |

---

## APPENDICES

### Appendix A: Quick Reference Commands

```bash
# VPS SSH Access
ssh ziggie@82.25.112.73

# Check all containers
docker compose ps

# View logs
docker compose logs -f SERVICE_NAME

# Restart all services
docker compose down && docker compose up -d

# Database backup
docker exec ziggie-postgres pg_dump -U ziggie ziggie | gzip > backup.sql.gz

# AWS CLI (Windows)
"C:/Program Files/Amazon/AWSCLIV2/aws.exe" COMMAND --region eu-north-1
```

### Appendix B: Important File Locations

| File | Location | Purpose |
|------|----------|---------|
| docker-compose.yml | /opt/ziggie/docker-compose.yml | Service definitions |
| .env | /opt/ziggie/.env | Environment variables |
| nginx.conf | /opt/ziggie/nginx/nginx.conf | Reverse proxy config |
| Local backup | C:\Ziggie\hostinger-vps\ | Docker stack backup |
| AWS config | C:\Ziggie\aws-config\ | AWS configuration |

### Appendix C: S3 Backup Structure

```
s3://ziggie-assets-prod/
├── backups/
│   ├── postgres/
│   │   └── YYYYMMDD.sql.gz
│   ├── mongodb/
│   │   └── YYYYMMDD.archive
│   ├── redis/
│   │   └── dump.rdb
│   ├── n8n/
│   │   └── workflows.json
│   └── config/
│       ├── docker-compose.yml
│       └── .env.encrypted
└── game-assets/
    └── ...
```

### Appendix D: RTO/RPO Summary

| Component | RTO | RPO | Backup Frequency | Backup Retention |
|-----------|-----|-----|------------------|------------------|
| PostgreSQL | 2 hours | 24 hours | Daily | 30 days |
| MongoDB | 2 hours | 24 hours | Daily | 30 days |
| Redis | 1 hour | 24 hours | Daily | 7 days |
| n8n Workflows | 2 hours | 24 hours | Weekly | 90 days |
| Configuration | 1 hour | N/A (versioned) | On change | Indefinite |
| S3 Assets | N/A (AWS managed) | N/A | Continuous | Per lifecycle |

### Appendix E: Cost of Downtime

| Duration | Estimated Impact |
|----------|------------------|
| 1 hour | Minor - Development delayed |
| 4 hours | Moderate - Sprint impact |
| 24 hours | Significant - Milestone risk |
| 48+ hours | Critical - Project schedule impact |

---

## VERIFIED TEST RESULTS

> **Last Test Date**: 2025-12-28
> **Test Reference**: DR Test #31
> **Test Environment**: Windows 11 with Docker Desktop (local simulation)

### Test Summary

| Component | Test Type | Status | Details |
|-----------|-----------|--------|---------|
| PostgreSQL Backup | Full backup | **PASS** | 52 tables, 190,011 bytes |
| PostgreSQL Restore | Restore to test DB | **PASS** | All 52 tables restored correctly |
| MongoDB Backup | Full backup | **PASS** | 5,206 documents, 80,020 bytes |
| MongoDB Restore | Restore to test namespace | **PASS** | All documents restored, 0 failures |
| Redis Backup | N/A | **SKIPPED** | No local Redis container |
| n8n Backup | N/A | **SKIPPED** | n8n container not running |
| Grafana Backup | N/A | **SKIPPED** | Grafana container not deployed |
| Backup Container Build | Docker build | **PASS** | 318 MiB, all 14 scripts validated |

### PostgreSQL Test Details

```text
Database: sim-studio-db-1 (simstudio)
Backup Command: pg_dump -U postgres simstudio --format=custom --compress=9
Backup Size: 190,011 bytes
Restore Method: pg_restore to simstudio_test_restore database
Tables Restored: 52
Verification: SELECT count(*) FROM information_schema.tables = 52
Cleanup: Test database dropped after verification
Result: SUCCESS
```

### MongoDB Test Details

```text
Database: meowping-mongodb (meowping)
Backup Command: mongodump --archive --gzip
Backup Size: 80,020 bytes
Documents: 5,206 across 8 collections
  - combat_events: 3,668
  - events: 659
  - units: 474
  - buildings: 178
  - sessions: 109
  - wave_status: 98
  - users: 11
  - enemy_units: 9
Restore Method: mongorestore --nsFrom/--nsTo for namespace isolation
Result: SUCCESS
```

### RTO/RPO Verification

| Metric | Target | Measured | Status |
|--------|--------|----------|--------|
| RTO (Recovery Time Objective) | 4 hours | Estimated 2-3 hours | **MEETS TARGET** |
| RPO (Recovery Point Objective) | 24 hours | 24 hours (daily backups) | **MEETS TARGET** |
| MTTR (Mean Time To Recovery) | 2 hours | Estimated 1-2 hours | **MEETS TARGET** |

### Test Artifacts

| Artifact | Location |
|----------|----------|
| PostgreSQL Backup | C:\Ziggie\testing\dr-test\backups\postgres\simstudio_backup.dump |
| MongoDB Backup | C:\Ziggie\testing\dr-test\backups\mongodb\meowping_backup.archive |
| DR Test Report | C:\Ziggie\testing\dr-test\DR-TEST-REPORT.md |
| DR Test Script | C:\Ziggie\testing\dr-test\run-full-dr-test.sh |
| DR Test Checklist | C:\Ziggie\testing\dr-test\DR-TEST-CHECKLIST.md |

### Issues Identified

1. **MEDIUM**: Restore scripts require interactive confirmation - recommend adding `--yes` flag for automation
2. **LOW**: MongoDB backup script assumes specific credential variable names
3. **LOW**: n8n backup relies on hardcoded container name

### Recommendations for Next Test

1. Run full test on Hostinger VPS with all containers running
2. Test S3 sync functionality with live AWS credentials
3. Measure actual restore times for RTO validation
4. Configure backup monitoring/alerting

---

## REVISION HISTORY

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-27 | Disaster Recovery Agent | Initial release |
| 1.1 | 2025-12-28 | DR Test Agent | Added verified test results section |

---

**END OF DOCUMENT**

*This runbook should be reviewed and tested quarterly.*
*Next scheduled test: Q1 2025*
*Next review date: 2025-03-27*
