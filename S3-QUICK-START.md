# AWS S3 Quick Start for Ziggie Cloud

> **Fast setup guide** - Get S3 running in 15 minutes
> **Region**: EU-North-1 (Stockholm)
> **Use case**: Game asset storage + automated backups

---

## 1. Install AWS CLI (5 minutes)

```bash
# Windows
winget install Amazon.AWSCLI

# Verify
aws --version

# Configure
aws configure
# Access Key: [from AWS Console → IAM → Users → Security Credentials]
# Secret Key: [from same page]
# Region: eu-north-1
# Output: json
```

---

## 2. Create Buckets (2 minutes)

```bash
# Assets bucket (public read via CDN)
aws s3api create-bucket \
    --bucket ziggie-cloud-assets \
    --region eu-north-1 \
    --create-bucket-configuration LocationConstraint=eu-north-1

# Backups bucket (private)
aws s3api create-bucket \
    --bucket ziggie-cloud-backups \
    --region eu-north-1 \
    --create-bucket-configuration LocationConstraint=eu-north-1

# Enable versioning for backups
aws s3api put-bucket-versioning \
    --bucket ziggie-cloud-backups \
    --versioning-configuration Status=Enabled
```

---

## 3. Daily Operations (Copy/Paste Commands)

### Upload Game Assets

```bash
# Single file
aws s3 cp archer-sprite.png s3://ziggie-cloud-assets/game-assets/sprites/ \
    --storage-class INTELLIGENT_TIERING

# Entire directory (preserves structure)
aws s3 sync C:/Ziggie/assets/generated/ s3://ziggie-cloud-assets/game-assets/ \
    --storage-class INTELLIGENT_TIERING \
    --exclude "*.tmp" \
    --exclude ".git/*"
```

### Backup n8n Workflows

```bash
# Manual backup
BACKUP_DATE=$(date +%Y%m%d-%H%M%S)
aws s3 sync /var/lib/docker/volumes/n8n_data/_data/ \
    s3://ziggie-cloud-backups/n8n/workflows/${BACKUP_DATE}/ \
    --storage-class GLACIER_IR
```

### Download Assets for Local Dev

```bash
# Download all sprites
aws s3 sync s3://ziggie-cloud-assets/game-assets/sprites/ C:/Ziggie/sprites/

# Download specific file
aws s3 cp s3://ziggie-cloud-assets/game-assets/models/archer.glb ./
```

### List Bucket Contents

```bash
# List top-level folders
aws s3 ls s3://ziggie-cloud-assets/

# List all files in prefix
aws s3 ls s3://ziggie-cloud-assets/game-assets/sprites/ --recursive

# Show bucket size
aws s3 ls s3://ziggie-cloud-assets/ --recursive --summarize
```

---

## 4. Automated Backup Script (5 minutes setup)

Create `C:\Ziggie\scripts\backup-to-s3.sh`:

```bash
#!/bin/bash
set -e

BACKUP_DATE=$(date +%Y%m%d-%H%M%S)

# Backup n8n workflows
echo "Backing up n8n workflows..."
aws s3 sync /var/lib/docker/volumes/n8n_data/_data/ \
    s3://ziggie-cloud-backups/n8n/workflows/${BACKUP_DATE}/ \
    --storage-class GLACIER_IR \
    --delete

# Backup Flowise chatflows
echo "Backing up Flowise chatflows..."
aws s3 sync /var/lib/docker/volumes/flowise_data/_data/ \
    s3://ziggie-cloud-backups/flowise/chatflows/${BACKUP_DATE}/ \
    --storage-class GLACIER_IR \
    --delete

# Sync ComfyUI outputs
echo "Syncing ComfyUI outputs..."
aws s3 sync /var/lib/docker/volumes/comfyui_data/_data/output/ \
    s3://ziggie-cloud-assets/comfyui/generated/ \
    --storage-class INTELLIGENT_TIERING \
    --exclude "*.tmp"

echo "Backup completed: ${BACKUP_DATE}"
```

Make executable and run:
```bash
chmod +x C:/Ziggie/scripts/backup-to-s3.sh
./backup-to-s3.sh
```

---

## 5. Cost Monitoring (3 minutes)

```bash
# Check current month costs (via CloudWatch)
aws cloudwatch get-metric-statistics \
    --namespace AWS/S3 \
    --metric-name BucketSizeBytes \
    --dimensions Name=BucketName,Value=ziggie-cloud-assets Name=StorageType,Value=StandardStorage \
    --start-time $(date -u -d '30 days ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 86400 \
    --statistics Average

# Estimated monthly cost formula:
# (Bucket Size in GB × $0.0245) + (Objects/1000 × $0.0025) = Monthly Storage Cost
```

**Example**: 100GB with 10,000 objects
- Storage: 100 × $0.0245 = $2.45
- Monitoring: 10 × $0.0025 = $0.025
- Total: $2.48/month

---

## 6. CDN Setup (Optional - 10 minutes)

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
    --origin-domain-name ziggie-cloud-assets.s3.eu-north-1.amazonaws.com \
    --default-root-object index.html

# Note the distribution domain (e.g., d1234abcd.cloudfront.net)
# Use in game: https://d1234abcd.cloudfront.net/game-assets/sprites/archer.png
```

For custom domain (assets.ziggie.cloud):
1. Request SSL cert in us-east-1: `aws acm request-certificate --domain-name assets.ziggie.cloud --region us-east-1`
2. Validate via DNS (add CNAME from email)
3. Update CloudFront distribution with cert
4. Add CNAME in DNS: `assets.ziggie.cloud CNAME d1234abcd.cloudfront.net`

---

## 7. Troubleshooting

### "Access Denied" errors
```bash
# Check IAM permissions
aws iam get-user

# Verify bucket policy allows your user
aws s3api get-bucket-policy --bucket ziggie-cloud-assets
```

### Slow uploads
```bash
# Use multipart for files >100MB
aws configure set default.s3.multipart_threshold 100MB
aws configure set default.s3.multipart_chunksize 50MB
```

### Restore from Glacier
```bash
# Initiate restoration (takes 3-5 hours for GLACIER_IR)
aws s3api restore-object \
    --bucket ziggie-cloud-backups \
    --key n8n/workflows/20251201-020000/workflow.json \
    --restore-request '{"Days":7,"GlacierJobParameters":{"Tier":"Standard"}}'

# Check restoration status
aws s3api head-object \
    --bucket ziggie-cloud-backups \
    --key n8n/workflows/20251201-020000/workflow.json
```

---

## 8. Docker Integration (For VPS)

Add to `docker-compose.yml`:

```yaml
services:
  aws-backup:
    image: amazon/aws-cli:latest
    volumes:
      - ~/.aws:/root/.aws:ro
      - n8n_data:/data/n8n:ro
      - flowise_data:/data/flowise:ro
      - comfyui_data:/data/comfyui:ro
    environment:
      - AWS_DEFAULT_REGION=eu-north-1
    command: |
      sh -c "
        while true; do
          aws s3 sync /data/n8n/ s3://ziggie-cloud-backups/n8n/\$(date +%Y%m%d-%H%M%S)/ --storage-class GLACIER_IR
          aws s3 sync /data/flowise/ s3://ziggie-cloud-backups/flowise/\$(date +%Y%m%d-%H%M%S)/ --storage-class GLACIER_IR
          aws s3 sync /data/comfyui/output/ s3://ziggie-cloud-assets/comfyui/generated/ --storage-class INTELLIGENT_TIERING
          sleep 86400
        done
      "
    restart: unless-stopped
```

Start backup service:
```bash
docker-compose up -d aws-backup
```

---

## 9. Emergency Recovery

### Restore n8n workflows
```bash
# List available backups
aws s3 ls s3://ziggie-cloud-backups/n8n/workflows/

# Restore latest backup
LATEST_BACKUP=$(aws s3 ls s3://ziggie-cloud-backups/n8n/workflows/ | tail -1 | awk '{print $2}')
aws s3 sync s3://ziggie-cloud-backups/n8n/workflows/${LATEST_BACKUP} /var/lib/docker/volumes/n8n_data/_data/

# Restart n8n
docker restart n8n
```

### Restore database
```bash
# Download backup
aws s3 cp s3://ziggie-cloud-backups/databases/postgres-20251223-020000.sql.gz /tmp/

# Restore
gunzip /tmp/postgres-20251223-020000.sql.gz
docker exec -i postgres psql -U postgres < /tmp/postgres-20251223-020000.sql
```

---

## 10. Security Checklist

- [ ] IAM user has minimal permissions (only S3 access)
- [ ] Access keys stored securely (not in Git)
- [ ] Backups bucket has versioning enabled
- [ ] Backups bucket blocks public access
- [ ] Server-side encryption enabled (AES256)
- [ ] CloudWatch alarms set for unusual activity
- [ ] Access logs enabled for audit trail

---

## Quick Reference Card

| Task | Command |
|------|---------|
| **Upload file** | `aws s3 cp file.png s3://bucket/path/` |
| **Upload folder** | `aws s3 sync ./local/ s3://bucket/path/` |
| **Download file** | `aws s3 cp s3://bucket/path/file.png ./` |
| **Download folder** | `aws s3 sync s3://bucket/path/ ./local/` |
| **List files** | `aws s3 ls s3://bucket/path/` |
| **Delete file** | `aws s3 rm s3://bucket/path/file.png` |
| **Bucket size** | `aws s3 ls s3://bucket/ --recursive --summarize` |
| **Copy between buckets** | `aws s3 cp s3://bucket1/file s3://bucket2/file` |

---

**Next Steps**:
1. Run commands in section 1-2 to set up buckets
2. Test upload/download with a sample file
3. Set up automated backup script (section 4)
4. Review costs weekly for first month
5. See full guide (AWS-S3-INTEGRATION-GUIDE.md) for advanced features

**Support**: See full integration guide for troubleshooting, CDN setup, and advanced configurations.
