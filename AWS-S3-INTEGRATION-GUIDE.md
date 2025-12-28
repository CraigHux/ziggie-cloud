# AWS S3 Integration Guide for Ziggie Cloud

> **Context**: Asset storage and backup solution for Ziggie Cloud infrastructure
> **AWS Region**: EU-North-1 (Stockholm)
> **Services**: ComfyUI, n8n, Flowise, Grafana
> **Last Updated**: 2025-12-23

---

## Executive Summary

AWS S3 integration for Ziggie Cloud provides:
- **Cost-effective storage**: $0.0245/GB/month in eu-north-1 (S3 Standard)
- **Intelligent-Tiering**: Automatic cost optimization (30% savings on infrequent access)
- **Glacier archival**: $0.004/GB/month for old assets (83% cost reduction)
- **CloudFront CDN**: Global delivery with edge caching
- **Automated backups**: Docker-based sync from VPS to S3

**Estimated Monthly Costs** (eu-north-1):
- 100GB active assets: ~$3-4/month (S3 Standard + Intelligent-Tiering)
- 500GB with lifecycle: ~$8-12/month (mixed storage classes)
- 1TB with CDN: ~$20-30/month (storage + data transfer + CloudFront)

---

## 1. S3 Bucket Configuration

### 1.1 Bucket Structure

```text
ziggie-cloud-assets/          # Public read via CloudFront
├── game-assets/
│   ├── sprites/              # 2D game sprites
│   ├── 3d-models/            # GLB/FBX models
│   ├── textures/             # PNG/JPG textures
│   └── animations/           # Animation files
├── comfyui/
│   ├── generated/            # AI-generated images
│   └── workflows/            # ComfyUI workflow JSON
└── shared/                   # Shared assets

ziggie-cloud-backups/         # Private bucket
├── n8n/
│   ├── workflows/            # n8n workflow backups
│   └── credentials/          # Encrypted credentials (KMS)
├── flowise/
│   └── chatflows/            # Flowise chatflow exports
├── grafana/
│   └── dashboards/           # Dashboard configs
└── databases/                # Database dumps
```

### 1.2 Bucket Creation Commands

```bash
# Install AWS CLI
winget install Amazon.AWSCLI

# Configure credentials
aws configure
# AWS Access Key ID: [your-key]
# AWS Secret Access Key: [your-secret]
# Default region: eu-north-1
# Default output format: json

# Create public assets bucket
aws s3api create-bucket \
    --bucket ziggie-cloud-assets \
    --region eu-north-1 \
    --create-bucket-configuration LocationConstraint=eu-north-1

# Create private backups bucket
aws s3api create-bucket \
    --bucket ziggie-cloud-backups \
    --region eu-north-1 \
    --create-bucket-configuration LocationConstraint=eu-north-1

# Enable versioning for backups (disaster recovery)
aws s3api put-bucket-versioning \
    --bucket ziggie-cloud-backups \
    --versioning-configuration Status=Enabled
```

### 1.3 Bucket Policy for Public Read (Assets Only)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::ziggie-cloud-assets/game-assets/*"
    },
    {
      "Sid": "CloudFrontOriginAccess",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudfront.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::ziggie-cloud-assets/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::ACCOUNT_ID:distribution/DISTRIBUTION_ID"
        }
      }
    }
  ]
}
```

Apply policy:
```bash
aws s3api put-bucket-policy \
    --bucket ziggie-cloud-assets \
    --policy file://bucket-policy.json
```

### 1.4 CORS Configuration (Web Frontend Access)

```json
{
  "CORSRules": [
    {
      "AllowedOrigins": [
        "https://ziggie.cloud",
        "https://*.ziggie.cloud",
        "http://localhost:3000"
      ],
      "AllowedMethods": ["GET", "HEAD"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3600,
      "ExposeHeaders": ["ETag"]
    }
  ]
}
```

Apply CORS:
```bash
aws s3api put-bucket-cors \
    --bucket ziggie-cloud-assets \
    --cors-configuration file://cors.json
```

---

## 2. S3 Intelligent-Tiering Configuration

### 2.1 Enable Intelligent-Tiering

Intelligent-Tiering automatically moves objects between access tiers:
- **Frequent Access**: Objects accessed regularly (standard pricing)
- **Infrequent Access**: Not accessed for 30 days (40% savings)
- **Archive Instant Access**: Not accessed for 90 days (68% savings)
- **Archive Access**: Not accessed for 180 days (71% savings - optional)
- **Deep Archive Access**: Not accessed for 270 days (95% savings - optional)

**Configuration**:
```json
{
  "Id": "GameAssetsTiering",
  "Status": "Enabled",
  "Filter": {
    "Prefix": "game-assets/"
  },
  "Tierings": [
    {
      "Days": 90,
      "AccessTier": "ARCHIVE_ACCESS"
    },
    {
      "Days": 180,
      "AccessTier": "DEEP_ARCHIVE_ACCESS"
    }
  ]
}
```

Apply configuration:
```bash
aws s3api put-bucket-intelligent-tiering-configuration \
    --bucket ziggie-cloud-assets \
    --id GameAssetsTiering \
    --intelligent-tiering-configuration file://intelligent-tiering.json
```

### 2.2 Upload with Intelligent-Tiering Storage Class

```bash
# Upload single file
aws s3 cp generated-asset.png \
    s3://ziggie-cloud-assets/comfyui/generated/ \
    --storage-class INTELLIGENT_TIERING

# Sync entire directory
aws s3 sync ./local-assets/ \
    s3://ziggie-cloud-assets/game-assets/ \
    --storage-class INTELLIGENT_TIERING
```

### 2.3 Cost Comparison (eu-north-1 pricing)

| Storage Class | Cost/GB/Month | Use Case |
|---------------|---------------|----------|
| S3 Standard | $0.0245 | Active assets, <30 days |
| Intelligent-Tiering (Frequent) | $0.0245 + $0.0025 monitoring | Auto-optimization |
| Intelligent-Tiering (Infrequent) | $0.0147 + $0.0025 monitoring | 30-90 days old |
| Intelligent-Tiering (Archive) | $0.0045 + $0.0025 monitoring | 90-180 days old |
| S3 Glacier Flexible Retrieval | $0.0040 | Long-term backups |
| S3 Glacier Deep Archive | $0.0018 | Archival (>270 days) |

**Recommendation**: Use Intelligent-Tiering for game-assets/ (unknown access patterns), Glacier for backups/ (known archival).

---

## 3. Lifecycle Policies for Glacier Transitions

### 3.1 Lifecycle Policy for Backups

```json
{
  "Rules": [
    {
      "Id": "BackupArchival",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "n8n/workflows/"
      },
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "GLACIER_IR"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        },
        {
          "Days": 365,
          "StorageClass": "DEEP_ARCHIVE"
        }
      ],
      "NoncurrentVersionTransitions": [
        {
          "NoncurrentDays": 7,
          "StorageClass": "GLACIER_IR"
        }
      ],
      "Expiration": {
        "Days": 730
      }
    },
    {
      "Id": "ComfyUICleanup",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "comfyui/generated/"
      },
      "Transitions": [
        {
          "Days": 60,
          "StorageClass": "INTELLIGENT_TIERING"
        }
      ],
      "Expiration": {
        "Days": 180
      }
    }
  ]
}
```

Apply lifecycle policy:
```bash
aws s3api put-bucket-lifecycle-configuration \
    --bucket ziggie-cloud-backups \
    --lifecycle-configuration file://lifecycle.json
```

### 3.2 Policy Explanation

| Rule | Timeline | Action |
|------|----------|--------|
| **Backups** | Day 0-30 | S3 Standard (fast access) |
|  | Day 30-90 | Glacier Instant Retrieval (millisecond access) |
|  | Day 90-365 | Glacier Flexible Retrieval (minutes-hours access) |
|  | Day 365-730 | Deep Archive (12-hour retrieval) |
|  | Day 730+ | Delete (2-year retention) |
| **ComfyUI** | Day 0-60 | S3 Standard |
|  | Day 60-180 | Intelligent-Tiering |
|  | Day 180+ | Delete (6-month retention) |

---

## 4. Docker Container Integration on VPS

### 4.1 AWS CLI in Docker Container

Create shared AWS credentials volume:

```dockerfile
# Dockerfile.aws-sync
FROM amazon/aws-cli:latest

RUN yum install -y cronie

COPY sync-to-s3.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/sync-to-s3.sh

# Cron job for automated backups
RUN echo "0 2 * * * /usr/local/bin/sync-to-s3.sh" | crontab -

CMD ["crond", "-f"]
```

**sync-to-s3.sh**:
```bash
#!/bin/bash
set -e

BACKUP_DATE=$(date +%Y%m%d-%H%M%S)

# Backup n8n workflows
if [ -d "/data/n8n" ]; then
    aws s3 sync /data/n8n/ \
        s3://ziggie-cloud-backups/n8n/workflows/${BACKUP_DATE}/ \
        --storage-class GLACIER_IR \
        --delete
fi

# Backup Flowise chatflows
if [ -d "/data/flowise" ]; then
    aws s3 sync /data/flowise/ \
        s3://ziggie-cloud-backups/flowise/chatflows/${BACKUP_DATE}/ \
        --storage-class GLACIER_IR \
        --delete
fi

# Sync ComfyUI generated images
if [ -d "/data/comfyui/output" ]; then
    aws s3 sync /data/comfyui/output/ \
        s3://ziggie-cloud-assets/comfyui/generated/ \
        --storage-class INTELLIGENT_TIERING \
        --exclude "*.tmp"
fi

echo "Backup completed: ${BACKUP_DATE}"
```

### 4.2 Docker Compose Configuration

```yaml
# docker-compose.yml (add to existing services)
services:
  aws-sync:
    build:
      context: .
      dockerfile: Dockerfile.aws-sync
    volumes:
      - ~/.aws:/root/.aws:ro  # AWS credentials (read-only)
      - /var/lib/docker/volumes/n8n_data/_data:/data/n8n:ro
      - /var/lib/docker/volumes/flowise_data/_data:/data/flowise:ro
      - /var/lib/docker/volumes/comfyui_data/_data:/data/comfyui:ro
    environment:
      - AWS_DEFAULT_REGION=eu-north-1
    restart: unless-stopped
```

### 4.3 Manual Sync Commands

```bash
# One-time sync of game assets from VPS
aws s3 sync /home/ziggie/game-assets/ \
    s3://ziggie-cloud-assets/game-assets/ \
    --storage-class INTELLIGENT_TIERING \
    --exclude "*.tmp" \
    --exclude ".git/*"

# Download all sprites for local development
aws s3 sync s3://ziggie-cloud-assets/game-assets/sprites/ \
    ./local-sprites/

# Restore n8n workflows from backup
aws s3 sync s3://ziggie-cloud-backups/n8n/workflows/20251223-020000/ \
    /data/n8n/
```

---

## 5. S3 as Backup Destination

### 5.1 n8n Workflow Backup Pattern

Create n8n workflow that runs daily:

```json
{
  "name": "S3 Backup Workflow",
  "nodes": [
    {
      "name": "Schedule",
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [250, 300],
      "parameters": {
        "rule": {
          "interval": [{"field": "hours", "hours": 24}]
        }
      }
    },
    {
      "name": "Export Workflows",
      "type": "n8n-nodes-base.n8n",
      "position": [450, 300],
      "parameters": {
        "resource": "workflow",
        "operation": "getAll"
      }
    },
    {
      "name": "AWS S3",
      "type": "n8n-nodes-base.awsS3",
      "position": [650, 300],
      "parameters": {
        "operation": "upload",
        "bucketName": "ziggie-cloud-backups",
        "fileName": "={{$now.format('YYYY-MM-DD')}}/workflows.json",
        "binaryData": true,
        "options": {
          "storageClass": "GLACIER_IR"
        }
      },
      "credentials": {
        "aws": {
          "id": "1",
          "name": "AWS Account"
        }
      }
    }
  ],
  "connections": {
    "Schedule": {"main": [[{"node": "Export Workflows"}]]},
    "Export Workflows": {"main": [[{"node": "AWS S3"}]]}
  }
}
```

### 5.2 Flowise Chatflow Backup

Create shell script for Flowise:

```bash
#!/bin/bash
# flowise-backup.sh

BACKUP_DIR="/tmp/flowise-backup"
BACKUP_DATE=$(date +%Y-%m-%d)

# Export chatflows via Flowise API
curl -X GET http://localhost:3000/api/v1/chatflows \
    -H "Authorization: Bearer ${FLOWISE_API_KEY}" \
    -o ${BACKUP_DIR}/chatflows-${BACKUP_DATE}.json

# Upload to S3
aws s3 cp ${BACKUP_DIR}/chatflows-${BACKUP_DATE}.json \
    s3://ziggie-cloud-backups/flowise/chatflows/${BACKUP_DATE}/ \
    --storage-class GLACIER_IR

# Cleanup
rm -rf ${BACKUP_DIR}
```

### 5.3 Database Backup to S3

```bash
#!/bin/bash
# postgres-backup.sh

BACKUP_DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="postgres-${BACKUP_DATE}.sql.gz"

# Dump PostgreSQL database
docker exec postgres pg_dumpall -U postgres | gzip > /tmp/${BACKUP_FILE}

# Upload to S3 with encryption
aws s3 cp /tmp/${BACKUP_FILE} \
    s3://ziggie-cloud-backups/databases/${BACKUP_FILE} \
    --storage-class GLACIER_IR \
    --server-side-encryption AES256

# Cleanup
rm /tmp/${BACKUP_FILE}

echo "Database backup completed: ${BACKUP_FILE}"
```

---

## 6. Cost Estimation

### 6.1 Pricing Breakdown (EU-North-1)

| Component | Unit Cost | Notes |
|-----------|-----------|-------|
| **Storage** | | |
| S3 Standard | $0.0245/GB/month | First 50 TB |
| Intelligent-Tiering monitoring | $0.0025/1000 objects | Auto-tiering fee |
| Glacier Instant Retrieval | $0.0040/GB/month | Millisecond access |
| Glacier Flexible Retrieval | $0.0040/GB/month | Minutes-hours access |
| Glacier Deep Archive | $0.0018/GB/month | 12-hour retrieval |
| **Data Transfer** | | |
| PUT/COPY/POST | $0.005/1000 requests | Upload costs |
| GET/SELECT | $0.0004/1000 requests | Download costs |
| Data transfer OUT to internet | $0.09/GB | First 10 TB/month |
| Data transfer to CloudFront | $0.00/GB | Free! |
| **Retrieval** | | |
| Glacier retrieval | $0.01/GB | Standard retrieval |
| Deep Archive retrieval | $0.02/GB | Standard retrieval (12h) |

### 6.2 Monthly Cost Scenarios

#### Scenario 1: 100GB Active Game Assets
```text
Storage:
- 100GB Intelligent-Tiering: 100 × $0.0245 = $2.45
- Monitoring (10K objects): 10 × $0.0025 = $0.025
- Total storage: $2.48/month

Data Transfer (assume 50GB/month downloads):
- 50GB to CloudFront: $0.00 (free)
- CloudFront to users: ~$4.25 (see CloudFront section)
- Total transfer: $4.25/month

Total: ~$6.73/month
```

#### Scenario 2: 500GB Mixed Storage
```text
Storage:
- 200GB Active (Intelligent-Tiering Frequent): 200 × $0.0270 = $5.40
- 200GB Infrequent (30-90 days): 200 × $0.0172 = $3.44
- 100GB Archive (90+ days): 100 × $0.0070 = $0.70
- Total storage: $9.54/month

Data Transfer (100GB/month):
- CloudFront delivery: ~$8.50/month
- Total: ~$18.04/month
```

#### Scenario 3: 1TB with CDN + Backups
```text
Storage:
- 600GB Game Assets (mixed tiers): ~$12.00
- 300GB Backups (Glacier IR): 300 × $0.0040 = $1.20
- 100GB Deep Archive: 100 × $0.0018 = $0.18
- Total storage: $13.38/month

Data Transfer (200GB/month via CDN):
- CloudFront delivery: ~$17.00/month
- Total: ~$30.38/month
```

### 6.3 Cost Optimization Tips

1. **Use Intelligent-Tiering for Unknown Access Patterns**
   - Game assets with unpredictable access
   - No retrieval fees (unlike Glacier)

2. **Direct to Glacier for Known Archival**
   - n8n workflow backups (rarely accessed)
   - Old 3D model versions

3. **Leverage CloudFront for Data Transfer**
   - S3 → CloudFront is free
   - CloudFront → Users is cheaper than S3 → Users

4. **Object Lifecycle Management**
   - Auto-delete temporary files (ComfyUI temp outputs)
   - Transition old backups to Deep Archive

5. **Requester Pays (Optional)**
   - Enable for public assets if users download heavily
   - Shifts data transfer costs to downloader

---

## 7. CloudFront CDN Integration

### 7.1 CloudFront Distribution Creation

```bash
# Create CloudFront distribution via CLI
aws cloudfront create-distribution \
    --origin-domain-name ziggie-cloud-assets.s3.eu-north-1.amazonaws.com \
    --default-root-object index.html
```

**CloudFront Configuration JSON**:
```json
{
  "DistributionConfig": {
    "CallerReference": "ziggie-cloud-cdn-2025",
    "Comment": "Ziggie Cloud Game Assets CDN",
    "Enabled": true,
    "Origins": {
      "Quantity": 1,
      "Items": [
        {
          "Id": "S3-ziggie-cloud-assets",
          "DomainName": "ziggie-cloud-assets.s3.eu-north-1.amazonaws.com",
          "S3OriginConfig": {
            "OriginAccessIdentity": ""
          },
          "OriginAccessControlId": "OAC_ID_HERE"
        }
      ]
    },
    "DefaultCacheBehavior": {
      "TargetOriginId": "S3-ziggie-cloud-assets",
      "ViewerProtocolPolicy": "redirect-to-https",
      "AllowedMethods": {
        "Quantity": 2,
        "Items": ["GET", "HEAD"]
      },
      "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
      "Compress": true
    },
    "PriceClass": "PriceClass_100",
    "ViewerCertificate": {
      "CloudFrontDefaultCertificate": true
    }
  }
}
```

### 7.2 Origin Access Control (OAC)

Modern replacement for Origin Access Identity (OAI):

```bash
# Create OAC
aws cloudfront create-origin-access-control \
    --origin-access-control-config file://oac.json

# oac.json
{
  "Name": "ziggie-cloud-s3-oac",
  "Description": "OAC for Ziggie Cloud S3 bucket",
  "SigningProtocol": "sigv4",
  "SigningBehavior": "always",
  "OriginAccessControlOriginType": "s3"
}
```

Update S3 bucket policy to allow CloudFront OAC access (see section 1.3).

### 7.3 Custom Domain Setup

```bash
# Request SSL certificate in us-east-1 (required for CloudFront)
aws acm request-certificate \
    --domain-name assets.ziggie.cloud \
    --validation-method DNS \
    --region us-east-1

# Validate via DNS (add CNAME records in your DNS provider)

# Update CloudFront distribution with custom domain
aws cloudfront update-distribution \
    --id DISTRIBUTION_ID \
    --distribution-config file://distribution-with-domain.json
```

**Add to DNS**:
```text
assets.ziggie.cloud CNAME d1234abcd.cloudfront.net
```

### 7.4 Cache Policies

**Optimized for Game Assets** (CachingOptimized policy):
```json
{
  "Id": "658327ea-f89d-4fab-a63d-7e88639e58f6",
  "Name": "Managed-CachingOptimized",
  "MinTTL": 1,
  "DefaultTTL": 86400,
  "MaxTTL": 31536000,
  "ParametersInCacheKeyAndForwardedToOrigin": {
    "EnableAcceptEncodingGzip": true,
    "EnableAcceptEncodingBrotli": true
  }
}
```

**Custom Policy for Versioned Assets**:
```json
{
  "Name": "GameAssetsLongCache",
  "MinTTL": 86400,
  "DefaultTTL": 2592000,
  "MaxTTL": 31536000,
  "Comment": "30-day cache for versioned game assets"
}
```

### 7.5 CloudFront Pricing (2025 Estimates)

| Region | First 10TB | Next 40TB | Next 100TB |
|--------|------------|-----------|------------|
| **North America, Europe** | $0.085/GB | $0.080/GB | $0.060/GB |
| **Asia** | $0.120/GB | $0.085/GB | $0.080/GB |
| **Global Average** | ~$0.085/GB | ~$0.080/GB | ~$0.060/GB |

**HTTPS Requests**: $0.010/10,000 requests

**Example**: 200GB/month data transfer
- First 10TB tier: 200GB × $0.085 = $17.00/month
- HTTPS requests (1M): 100 × $0.010 = $1.00/month
- Total: ~$18.00/month

### 7.6 Invalidation for Cache Busting

```bash
# Invalidate all sprites after update
aws cloudfront create-invalidation \
    --distribution-id DISTRIBUTION_ID \
    --paths "/game-assets/sprites/*"

# Invalidate specific file
aws cloudfront create-invalidation \
    --distribution-id DISTRIBUTION_ID \
    --paths "/game-assets/units/archer-v2.png"
```

**Cost**: First 1,000 invalidation paths/month are free, $0.005 per path thereafter.

**Alternative**: Use versioned filenames to avoid invalidations
```text
BAD:  /sprites/archer.png
GOOD: /sprites/archer-v1.2.3.png
GOOD: /sprites/archer.png?v=20251223
```

---

## 8. AWS CLI Commands Reference

### 8.1 Common Operations

```bash
# List all buckets
aws s3 ls

# List bucket contents
aws s3 ls s3://ziggie-cloud-assets/game-assets/

# Upload single file
aws s3 cp local-file.png s3://ziggie-cloud-assets/sprites/

# Upload with metadata
aws s3 cp model.glb s3://ziggie-cloud-assets/3d-models/ \
    --metadata "version=1.2.3,author=ComfyUI" \
    --content-type "model/gltf-binary"

# Sync directory (upload only new/changed files)
aws s3 sync ./local-assets/ s3://ziggie-cloud-assets/game-assets/ \
    --delete  # Remove files from S3 that don't exist locally

# Download entire bucket
aws s3 sync s3://ziggie-cloud-assets/ ./local-backup/

# Copy between buckets
aws s3 cp s3://ziggie-cloud-assets/sprites/ \
    s3://ziggie-cloud-backups/sprites-backup/ \
    --recursive

# Move files (copy + delete source)
aws s3 mv s3://bucket/old-path/ s3://bucket/new-path/ --recursive

# Delete file
aws s3 rm s3://ziggie-cloud-assets/temp/old-file.png

# Delete all files in prefix
aws s3 rm s3://ziggie-cloud-assets/temp/ --recursive
```

### 8.2 Presigned URLs (Temporary Access)

```bash
# Generate presigned URL (expires in 1 hour)
aws s3 presign s3://ziggie-cloud-backups/database/backup.sql.gz \
    --expires-in 3600

# Output: https://ziggie-cloud-backups.s3.amazonaws.com/database/backup.sql.gz?X-Amz-Algorithm=...
```

Use case: Share private backups with team members temporarily.

### 8.3 Storage Class Management

```bash
# Check storage class of objects
aws s3api list-objects-v2 \
    --bucket ziggie-cloud-assets \
    --prefix game-assets/ \
    --query "Contents[*].[Key,StorageClass]" \
    --output table

# Change storage class of existing object
aws s3 cp s3://ziggie-cloud-assets/old-asset.png \
    s3://ziggie-cloud-assets/old-asset.png \
    --storage-class GLACIER_IR \
    --metadata-directive COPY

# Restore object from Glacier
aws s3api restore-object \
    --bucket ziggie-cloud-backups \
    --key workflows/2024-01-01/backup.json \
    --restore-request '{"Days":7,"GlacierJobParameters":{"Tier":"Standard"}}'
```

### 8.4 Monitoring and Analytics

```bash
# Get bucket size
aws s3 ls s3://ziggie-cloud-assets/ --recursive --summarize

# Enable CloudWatch metrics (detailed monitoring)
aws s3api put-bucket-metrics-configuration \
    --bucket ziggie-cloud-assets \
    --id EntireBucket \
    --metrics-configuration '{"Id":"EntireBucket"}'

# Query S3 Storage Lens (advanced analytics)
aws s3control get-storage-lens-configuration \
    --account-id ACCOUNT_ID \
    --config-id default-account-dashboard
```

---

## 9. Integration Patterns

### 9.1 ComfyUI Output to S3

Mount S3 bucket as filesystem using s3fs-fuse (Linux VPS):

```bash
# Install s3fs
apt-get install s3fs

# Mount S3 bucket
mkdir /mnt/s3-comfyui-output
echo "AWS_ACCESS_KEY:AWS_SECRET_KEY" > ~/.passwd-s3fs
chmod 600 ~/.passwd-s3fs

s3fs ziggie-cloud-assets /mnt/s3-comfyui-output \
    -o passwd_file=~/.passwd-s3fs \
    -o url=https://s3.eu-north-1.amazonaws.com \
    -o use_cache=/tmp/s3fs-cache \
    -o allow_other \
    -o use_path_request_style

# Configure ComfyUI to output to /mnt/s3-comfyui-output/comfyui/generated/
```

**Auto-mount on boot** (add to /etc/fstab):
```text
s3fs#ziggie-cloud-assets /mnt/s3-comfyui-output fuse _netdev,allow_other,use_cache=/tmp/s3fs-cache,passwd_file=/root/.passwd-s3fs,url=https://s3.eu-north-1.amazonaws.com 0 0
```

### 9.2 n8n S3 Integration Node

Configure AWS credentials in n8n:
1. Settings → Credentials → Add Credential
2. Type: AWS
3. Access Key ID: [your-key]
4. Secret Access Key: [your-secret]
5. Region: eu-north-1

**Workflow Example**: Auto-backup on workflow save
```json
{
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "workflow-saved",
        "httpMethod": "POST"
      }
    },
    {
      "name": "S3 Upload",
      "type": "n8n-nodes-base.awsS3",
      "parameters": {
        "operation": "upload",
        "bucketName": "ziggie-cloud-backups",
        "fileName": "={{$json.workflow.name}}-{{$now.format('YYYY-MM-DD-HHmmss')}}.json",
        "binaryData": true,
        "options": {
          "storageClass": "GLACIER_IR"
        }
      }
    }
  ]
}
```

### 9.3 Game Engine Asset Loading from CloudFront

**Unity C# Example**:
```csharp
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

public class S3AssetLoader : MonoBehaviour
{
    private const string CDN_BASE_URL = "https://assets.ziggie.cloud";

    public IEnumerator LoadSprite(string assetPath, System.Action<Sprite> callback)
    {
        string url = $"{CDN_BASE_URL}/game-assets/sprites/{assetPath}";

        using (UnityWebRequest request = UnityWebRequestTexture.GetTexture(url))
        {
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                Texture2D texture = DownloadHandlerTexture.GetContent(request);
                Sprite sprite = Sprite.Create(
                    texture,
                    new Rect(0, 0, texture.width, texture.height),
                    new Vector2(0.5f, 0.5f)
                );
                callback(sprite);
            }
            else
            {
                Debug.LogError($"Failed to load sprite: {request.error}");
            }
        }
    }
}

// Usage
StartCoroutine(LoadSprite("archer-red.png", (sprite) => {
    GetComponent<SpriteRenderer>().sprite = sprite;
}));
```

**Godot GDScript Example**:
```gdscript
extends Node

const CDN_BASE_URL = "https://assets.ziggie.cloud"

func load_texture(asset_path: String) -> void:
    var http_request = HTTPRequest.new()
    add_child(http_request)
    http_request.connect("request_completed", self, "_on_texture_loaded")

    var url = CDN_BASE_URL + "/game-assets/sprites/" + asset_path
    http_request.request(url)

func _on_texture_loaded(result, response_code, headers, body):
    if response_code == 200:
        var image = Image.new()
        var error = image.load_png_from_buffer(body)
        if error == OK:
            var texture = ImageTexture.new()
            texture.create_from_image(image)
            $Sprite.texture = texture
    else:
        print("Failed to load texture: ", response_code)
```

### 9.4 Grafana Dashboard Backup to S3

```bash
#!/bin/bash
# grafana-backup.sh

GRAFANA_URL="http://localhost:3000"
GRAFANA_API_KEY="your-api-key"
BACKUP_DATE=$(date +%Y-%m-%d)

# Get all dashboard UIDs
DASHBOARD_UIDS=$(curl -s -H "Authorization: Bearer ${GRAFANA_API_KEY}" \
    ${GRAFANA_URL}/api/search?type=dash-db | jq -r '.[].uid')

# Export each dashboard
mkdir -p /tmp/grafana-backup
for UID in ${DASHBOARD_UIDS}; do
    curl -s -H "Authorization: Bearer ${GRAFANA_API_KEY}" \
        ${GRAFANA_URL}/api/dashboards/uid/${UID} | jq '.dashboard' \
        > /tmp/grafana-backup/${UID}.json
done

# Upload to S3
aws s3 sync /tmp/grafana-backup/ \
    s3://ziggie-cloud-backups/grafana/dashboards/${BACKUP_DATE}/ \
    --storage-class GLACIER_IR

# Cleanup
rm -rf /tmp/grafana-backup
```

---

## 10. Security Best Practices

### 10.1 IAM User for VPS (Least Privilege)

Create dedicated IAM user for VPS sync:

```bash
# Create IAM user
aws iam create-user --user-name ziggie-vps-sync

# Create access key
aws iam create-access-key --user-name ziggie-vps-sync
```

**IAM Policy** (minimal permissions):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::ziggie-cloud-assets/*",
        "arn:aws:s3:::ziggie-cloud-backups/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::ziggie-cloud-assets",
        "arn:aws:s3:::ziggie-cloud-backups"
      ]
    }
  ]
}
```

Attach policy:
```bash
aws iam put-user-policy \
    --user-name ziggie-vps-sync \
    --policy-name S3SyncPolicy \
    --policy-document file://iam-policy.json
```

### 10.2 Bucket Encryption

**Server-Side Encryption (SSE-S3)**:
```bash
aws s3api put-bucket-encryption \
    --bucket ziggie-cloud-backups \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            },
            "BucketKeyEnabled": true
        }]
    }'
```

**AWS KMS Encryption (for sensitive data)**:
```bash
# Create KMS key
aws kms create-key --description "Ziggie Cloud Backups Encryption"

# Enable KMS encryption on bucket
aws s3api put-bucket-encryption \
    --bucket ziggie-cloud-backups \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "aws:kms",
                "KMSMasterKeyID": "arn:aws:kms:eu-north-1:ACCOUNT_ID:key/KEY_ID"
            }
        }]
    }'
```

### 10.3 Block Public Access (Backups Bucket)

```bash
aws s3api put-public-access-block \
    --bucket ziggie-cloud-backups \
    --public-access-block-configuration \
        "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

### 10.4 Access Logging

Enable S3 access logs for audit trails:

```bash
# Create logging bucket
aws s3api create-bucket \
    --bucket ziggie-cloud-logs \
    --region eu-north-1 \
    --create-bucket-configuration LocationConstraint=eu-north-1

# Enable logging
aws s3api put-bucket-logging \
    --bucket ziggie-cloud-assets \
    --bucket-logging-status '{
        "LoggingEnabled": {
            "TargetBucket": "ziggie-cloud-logs",
            "TargetPrefix": "s3-access-logs/"
        }
    }'
```

---

## 11. Monitoring and Alerts

### 11.1 CloudWatch Alarms

```bash
# Alert when bucket size exceeds threshold
aws cloudwatch put-metric-alarm \
    --alarm-name ziggie-assets-size-alert \
    --alarm-description "Alert when assets bucket exceeds 500GB" \
    --metric-name BucketSizeBytes \
    --namespace AWS/S3 \
    --statistic Average \
    --period 86400 \
    --evaluation-periods 1 \
    --threshold 536870912000 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=BucketName,Value=ziggie-cloud-assets Name=StorageType,Value=StandardStorage

# Alert on high request rate
aws cloudwatch put-metric-alarm \
    --alarm-name ziggie-assets-requests-spike \
    --metric-name NumberOfObjects \
    --namespace AWS/S3 \
    --statistic Sum \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 10000 \
    --comparison-operator GreaterThanThreshold
```

### 11.2 S3 Inventory for Cost Analysis

Enable daily inventory reports:

```bash
aws s3api put-bucket-inventory-configuration \
    --bucket ziggie-cloud-assets \
    --id DailyInventory \
    --inventory-configuration '{
        "Destination": {
            "S3BucketDestination": {
                "Bucket": "arn:aws:s3:::ziggie-cloud-logs",
                "Prefix": "inventory",
                "Format": "CSV"
            }
        },
        "IsEnabled": true,
        "Id": "DailyInventory",
        "IncludedObjectVersions": "Current",
        "OptionalFields": ["Size", "StorageClass", "ETag"],
        "Schedule": {
            "Frequency": "Daily"
        }
    }'
```

---

## 12. Disaster Recovery

### 12.1 Cross-Region Replication

Enable replication to secondary region for critical backups:

```bash
# Create destination bucket in another region
aws s3api create-bucket \
    --bucket ziggie-cloud-backups-replica \
    --region eu-west-1 \
    --create-bucket-configuration LocationConstraint=eu-west-1

# Enable versioning (required for replication)
aws s3api put-bucket-versioning \
    --bucket ziggie-cloud-backups \
    --versioning-configuration Status=Enabled

aws s3api put-bucket-versioning \
    --bucket ziggie-cloud-backups-replica \
    --versioning-configuration Status=Enabled

# Create IAM role for replication (see AWS docs for policy)

# Enable replication
aws s3api put-bucket-replication \
    --bucket ziggie-cloud-backups \
    --replication-configuration file://replication.json
```

**replication.json**:
```json
{
  "Role": "arn:aws:iam::ACCOUNT_ID:role/s3-replication-role",
  "Rules": [
    {
      "Status": "Enabled",
      "Priority": 1,
      "DeleteMarkerReplication": {"Status": "Disabled"},
      "Filter": {"Prefix": "critical/"},
      "Destination": {
        "Bucket": "arn:aws:s3:::ziggie-cloud-backups-replica",
        "StorageClass": "GLACIER"
      }
    }
  ]
}
```

### 12.2 Backup Verification Script

```bash
#!/bin/bash
# verify-backups.sh

# Check if today's backup exists
BACKUP_DATE=$(date +%Y-%m-%d)
REQUIRED_BACKUPS=(
    "n8n/workflows/${BACKUP_DATE}"
    "flowise/chatflows/${BACKUP_DATE}"
    "databases/postgres-${BACKUP_DATE}"
)

MISSING_BACKUPS=()

for BACKUP_PATH in "${REQUIRED_BACKUPS[@]}"; do
    if ! aws s3 ls s3://ziggie-cloud-backups/${BACKUP_PATH} > /dev/null 2>&1; then
        MISSING_BACKUPS+=("${BACKUP_PATH}")
    fi
done

if [ ${#MISSING_BACKUPS[@]} -eq 0 ]; then
    echo "All backups verified for ${BACKUP_DATE}"
else
    echo "ALERT: Missing backups:"
    printf '%s\n' "${MISSING_BACKUPS[@]}"
    exit 1
fi
```

---

## Summary & Next Steps

### Recommended Implementation Order

1. **Phase 1: Foundation** (Week 1)
   - Create S3 buckets (assets + backups)
   - Configure IAM user with least privilege
   - Enable versioning on backups bucket

2. **Phase 2: Automation** (Week 2)
   - Set up Docker-based sync container
   - Create cron jobs for daily backups
   - Test backup restoration process

3. **Phase 3: Optimization** (Week 3)
   - Enable Intelligent-Tiering on assets
   - Configure lifecycle policies
   - Set up CloudWatch alarms

4. **Phase 4: CDN** (Week 4)
   - Create CloudFront distribution
   - Configure custom domain
   - Migrate game asset URLs to CDN

5. **Phase 5: Monitoring** (Ongoing)
   - Review monthly costs
   - Analyze S3 Inventory reports
   - Optimize storage classes based on usage

### Key Commands Cheat Sheet

```bash
# Upload game assets
aws s3 sync ./local-assets/ s3://ziggie-cloud-assets/game-assets/ \
    --storage-class INTELLIGENT_TIERING

# Backup n8n workflows
aws s3 sync /data/n8n/ s3://ziggie-cloud-backups/n8n/ \
    --storage-class GLACIER_IR

# List bucket costs (via CloudWatch)
aws cloudwatch get-metric-statistics \
    --namespace AWS/S3 \
    --metric-name BucketSizeBytes \
    --dimensions Name=BucketName,Value=ziggie-cloud-assets \
    --start-time 2025-01-01T00:00:00Z \
    --end-time 2025-01-31T23:59:59Z \
    --period 86400 \
    --statistics Average

# Invalidate CDN cache
aws cloudfront create-invalidation \
    --distribution-id DISTRIBUTION_ID \
    --paths "/game-assets/*"
```

### Cost Control Checklist

- [ ] Enable S3 Intelligent-Tiering for unknown access patterns
- [ ] Set lifecycle policies to auto-archive old backups
- [ ] Use CloudFront for data transfer (free S3→CloudFront)
- [ ] Monitor costs via AWS Cost Explorer monthly
- [ ] Delete temporary files (set auto-expiration policies)
- [ ] Use versioned filenames to avoid CDN invalidation costs
- [ ] Review storage class distribution quarterly

---

## Resources

- **AWS S3 Pricing**: https://aws.amazon.com/s3/pricing/
- **CloudFront Pricing**: https://aws.amazon.com/cloudfront/pricing/
- **AWS CLI Reference**: https://docs.aws.amazon.com/cli/latest/reference/s3/
- **Intelligent-Tiering Guide**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/intelligent-tiering.html
- **Lifecycle Policies**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html

---

**Document Status**: Complete
**Target Infrastructure**: Ziggie Cloud VPS + AWS S3 (eu-north-1)
**Estimated Monthly Cost**: $10-30 for 500GB-1TB with CDN
**Next Review**: After Phase 1 implementation
