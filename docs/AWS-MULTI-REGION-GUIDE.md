# AWS Multi-Region Guide for Ziggie

> **Purpose**: Guide for setting up multi-region infrastructure for high availability and disaster recovery
> **Primary Region**: eu-north-1 (Stockholm)
> **Secondary Region**: eu-west-1 (Ireland)
> **Last Updated**: 2025-12-28

---

## Table of Contents

1. [Multi-Region Strategy](#1-multi-region-strategy)
2. [Route 53 DNS Configuration](#2-route-53-dns-configuration)
3. [S3 Cross-Region Replication](#3-s3-cross-region-replication)
4. [Database Replication](#4-database-replication)
5. [Secrets Manager Replication](#5-secrets-manager-replication)
6. [Failover Patterns](#6-failover-patterns)
7. [Cost Considerations](#7-cost-considerations)
8. [Implementation Checklist](#8-implementation-checklist)

---

## 1. Multi-Region Strategy

### Architecture Overview

```
                    Route 53 (Global DNS)
                           |
          +----------------+----------------+
          |                                 |
    eu-north-1 (Primary)           eu-west-1 (Secondary)
          |                                 |
    +-----+-----+                    +------+------+
    |     |     |                    |      |      |
   VPS   S3   RDS                  VPS(DR) S3    RDS(Read)
```

### Strategy Types

| Strategy | RTO | RPO | Cost | Use Case |
|----------|-----|-----|------|----------|
| Active-Passive | 15-30 min | ~0 | $$ | Standard DR |
| Active-Active | ~0 | ~0 | $$$$ | Zero downtime |
| Pilot Light | 30-60 min | Minutes | $ | Cost-conscious |

**Recommended for Ziggie**: Active-Passive with automated failover

### Region Selection

| Region | Purpose | Latency to EU |
|--------|---------|---------------|
| eu-north-1 | Primary (Stockholm) | Baseline |
| eu-west-1 | Secondary (Ireland) | +10-15ms |
| eu-central-1 | Alternative (Frankfurt) | +5-10ms |

---

## 2. Route 53 DNS Configuration

### Hosted Zone Setup

```bash
# Create hosted zone
aws route53 create-hosted-zone \
  --name ziggie.ai \
  --caller-reference "ziggie-$(date +%s)"

# Get hosted zone ID
ZONE_ID=$(aws route53 list-hosted-zones-by-name \
  --dns-name ziggie.ai \
  --query 'HostedZones[0].Id' \
  --output text | cut -d'/' -f3)
```

### Health Check Configuration

```bash
# Create health check for primary region
aws route53 create-health-check \
  --caller-reference "primary-health-$(date +%s)" \
  --health-check-config '{
    "IPAddress": "PRIMARY_VPS_IP",
    "Port": 443,
    "Type": "HTTPS",
    "ResourcePath": "/health",
    "RequestInterval": 30,
    "FailureThreshold": 3
  }'
```

### Failover Routing Policy

```json
{
  "Comment": "Failover routing for Ziggie API",
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "api.ziggie.ai",
        "Type": "A",
        "SetIdentifier": "primary",
        "Failover": "PRIMARY",
        "TTL": 60,
        "ResourceRecords": [{"Value": "PRIMARY_VPS_IP"}],
        "HealthCheckId": "PRIMARY_HEALTH_CHECK_ID"
      }
    },
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "api.ziggie.ai",
        "Type": "A",
        "SetIdentifier": "secondary",
        "Failover": "SECONDARY",
        "TTL": 60,
        "ResourceRecords": [{"Value": "SECONDARY_VPS_IP"}]
      }
    }
  ]
}
```

### Latency-Based Routing (Active-Active)

```json
{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "api.ziggie.ai",
        "Type": "A",
        "SetIdentifier": "eu-north-1",
        "Region": "eu-north-1",
        "TTL": 60,
        "ResourceRecords": [{"Value": "PRIMARY_VPS_IP"}],
        "HealthCheckId": "PRIMARY_HEALTH_CHECK_ID"
      }
    },
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "api.ziggie.ai",
        "Type": "A",
        "SetIdentifier": "eu-west-1",
        "Region": "eu-west-1",
        "TTL": 60,
        "ResourceRecords": [{"Value": "SECONDARY_VPS_IP"}],
        "HealthCheckId": "SECONDARY_HEALTH_CHECK_ID"
      }
    }
  ]
}
```

---

## 3. S3 Cross-Region Replication

### Enable Versioning (Required)

```bash
# Enable versioning on source bucket
aws s3api put-bucket-versioning \
  --bucket ziggie-assets-prod \
  --versioning-configuration Status=Enabled

# Create destination bucket in secondary region
aws s3api create-bucket \
  --bucket ziggie-assets-dr \
  --region eu-west-1 \
  --create-bucket-configuration LocationConstraint=eu-west-1

# Enable versioning on destination
aws s3api put-bucket-versioning \
  --bucket ziggie-assets-dr \
  --versioning-configuration Status=Enabled
```

### IAM Role for Replication

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"Service": "s3.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }
  ]
}
```

```bash
# Create IAM role
aws iam create-role \
  --role-name ziggie-s3-replication-role \
  --assume-role-policy-document file://trust-policy.json

# Attach replication policy
aws iam put-role-policy \
  --role-name ziggie-s3-replication-role \
  --policy-name ReplicationPolicy \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "s3:GetReplicationConfiguration",
          "s3:ListBucket",
          "s3:GetObjectVersionForReplication",
          "s3:GetObjectVersionAcl",
          "s3:GetObjectVersionTagging"
        ],
        "Resource": [
          "arn:aws:s3:::ziggie-assets-prod",
          "arn:aws:s3:::ziggie-assets-prod/*"
        ]
      },
      {
        "Effect": "Allow",
        "Action": [
          "s3:ReplicateObject",
          "s3:ReplicateDelete",
          "s3:ReplicateTags"
        ],
        "Resource": "arn:aws:s3:::ziggie-assets-dr/*"
      }
    ]
  }'
```

### Configure Replication

```bash
aws s3api put-bucket-replication \
  --bucket ziggie-assets-prod \
  --replication-configuration '{
    "Role": "arn:aws:iam::ACCOUNT_ID:role/ziggie-s3-replication-role",
    "Rules": [
      {
        "ID": "ReplicateAll",
        "Status": "Enabled",
        "Priority": 1,
        "Filter": {},
        "Destination": {
          "Bucket": "arn:aws:s3:::ziggie-assets-dr",
          "StorageClass": "STANDARD"
        },
        "DeleteMarkerReplication": {
          "Status": "Enabled"
        }
      }
    ]
  }'
```

---

## 4. Database Replication

### PostgreSQL on RDS (Optional Cloud DB)

```bash
# Create primary RDS instance
aws rds create-db-instance \
  --db-instance-identifier ziggie-primary \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username ziggie \
  --master-user-password "${POSTGRES_PASSWORD}" \
  --allocated-storage 100 \
  --region eu-north-1 \
  --multi-az \
  --backup-retention-period 7

# Create read replica in secondary region
aws rds create-db-instance-read-replica \
  --db-instance-identifier ziggie-replica \
  --source-db-instance-identifier arn:aws:rds:eu-north-1:ACCOUNT:db:ziggie-primary \
  --region eu-west-1 \
  --db-instance-class db.t3.medium
```

### VPS PostgreSQL Replication

For Hostinger VPS, use logical replication:

```sql
-- On Primary (eu-north-1)
-- postgresql.conf
wal_level = logical
max_wal_senders = 5
max_replication_slots = 5

-- Create publication
CREATE PUBLICATION ziggie_pub FOR ALL TABLES;

-- Create replication user
CREATE USER replicator WITH REPLICATION PASSWORD 'secure_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO replicator;
```

```sql
-- On Secondary (eu-west-1)
-- Create subscription
CREATE SUBSCRIPTION ziggie_sub
  CONNECTION 'host=primary.ziggie.ai dbname=ziggie user=replicator password=secure_password'
  PUBLICATION ziggie_pub;
```

### MongoDB Replica Set

```javascript
// Initialize replica set
rs.initiate({
  _id: "ziggie-rs",
  members: [
    { _id: 0, host: "primary.ziggie.ai:27017", priority: 2 },
    { _id: 1, host: "secondary.ziggie.ai:27017", priority: 1 },
    { _id: 2, host: "arbiter.ziggie.ai:27017", arbiterOnly: true }
  ]
})
```

---

## 5. Secrets Manager Replication

### Enable Secret Replication

```bash
# Create secret with replication
aws secretsmanager create-secret \
  --name ziggie/api-keys \
  --secret-string '{"anthropic":"xxx","openai":"yyy"}' \
  --add-replica-regions '[{"Region":"eu-west-1"}]' \
  --region eu-north-1
```

### Replicate Existing Secrets

```bash
# Add replica to existing secret
aws secretsmanager replicate-secret-to-regions \
  --secret-id ziggie/database-credentials \
  --add-replica-regions '[{"Region":"eu-west-1"}]' \
  --region eu-north-1
```

### Application Configuration

```python
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name: str, region: str = "eu-north-1") -> dict:
    """Get secret with automatic failover to secondary region."""

    try:
        client = boto3.client("secretsmanager", region_name=region)
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])
    except ClientError as e:
        if region == "eu-north-1":
            # Failover to secondary region
            return get_secret(secret_name, region="eu-west-1")
        raise e
```

---

## 6. Failover Patterns

### Automated Failover with Lambda

```python
# lambda_function.py
import boto3

def lambda_handler(event, context):
    """Trigger failover when primary health check fails."""

    route53 = boto3.client('route53')

    # Get current health status
    health_status = event['detail']['statusCode']

    if health_status == 'FAILURE':
        # Update DNS to point to secondary
        route53.change_resource_record_sets(
            HostedZoneId=ZONE_ID,
            ChangeBatch={
                'Changes': [{
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': 'api.ziggie.ai',
                        'Type': 'A',
                        'TTL': 60,
                        'ResourceRecords': [{'Value': SECONDARY_IP}]
                    }
                }]
            }
        )

        # Send notification
        sns = boto3.client('sns')
        sns.publish(
            TopicArn=ALERT_TOPIC,
            Subject='Ziggie Failover Activated',
            Message=f'Primary region failed. Traffic routed to secondary.'
        )
```

### EventBridge Rule

```bash
aws events put-rule \
  --name "ziggie-health-check-failure" \
  --event-pattern '{
    "source": ["aws.route53"],
    "detail-type": ["Route 53 Health Check Status Change"],
    "detail": {
      "eventTypeCode": ["AWS_ROUTE53_HEALTH_CHECK_STATUS_CHANGED"],
      "statusCode": ["FAILURE"]
    }
  }'

aws events put-targets \
  --rule "ziggie-health-check-failure" \
  --targets '[{
    "Id": "failover-lambda",
    "Arn": "arn:aws:lambda:eu-north-1:ACCOUNT:function:ziggie-failover"
  }]'
```

### Manual Failover Procedure

```bash
#!/bin/bash
# failover.sh - Manual failover script

PRIMARY_IP="xxx.xxx.xxx.xxx"
SECONDARY_IP="yyy.yyy.yyy.yyy"
ZONE_ID="ZXXXXXXXXX"

echo "Initiating failover to secondary region..."

# Update DNS
aws route53 change-resource-record-sets \
  --hosted-zone-id $ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.ziggie.ai",
        "Type": "A",
        "TTL": 60,
        "ResourceRecords": [{"Value": "'$SECONDARY_IP'"}]
      }
    }]
  }'

# Promote read replica (if using RDS)
aws rds promote-read-replica \
  --db-instance-identifier ziggie-replica \
  --region eu-west-1

echo "Failover complete. Secondary region is now primary."
```

---

## 7. Cost Considerations

### Monthly Cost Estimates

| Component | Primary Only | Multi-Region |
|-----------|--------------|--------------|
| Route 53 Hosted Zone | $0.50 | $0.50 |
| Health Checks (2) | $0 | $1.00 |
| S3 Replication | $0 | $5-20 |
| Secrets Manager | $0.40/secret | $0.80/secret |
| Cross-Region Data Transfer | $0 | $0.02/GB |
| Secondary VPS | $0 | $12/month |
| **Total Additional** | - | **~$20-50/month** |

### Cost Optimization Tips

1. **Use S3 Intelligent Tiering** in DR region
2. **Keep DR VPS minimal** - scale up only during failover
3. **Replicate only critical data** - use lifecycle rules
4. **Monitor data transfer** - optimize to reduce cross-region traffic

---

## 8. Implementation Checklist

### Phase 1: DNS Setup (Week 1)

- [ ] Create Route 53 hosted zone
- [ ] Configure health checks for primary
- [ ] Set up failover routing policy
- [ ] Update domain registrar nameservers
- [ ] Test DNS resolution

### Phase 2: S3 Replication (Week 1)

- [ ] Enable versioning on primary bucket
- [ ] Create DR bucket in secondary region
- [ ] Create IAM replication role
- [ ] Configure replication rules
- [ ] Verify replication is working

### Phase 3: Secrets Replication (Week 2)

- [ ] Enable replication on critical secrets
- [ ] Update application to use regional endpoints
- [ ] Test secret retrieval from both regions

### Phase 4: Database Replication (Week 2)

- [ ] Configure PostgreSQL logical replication
- [ ] Set up MongoDB replica set (if applicable)
- [ ] Test failover procedures
- [ ] Document recovery steps

### Phase 5: Automated Failover (Week 3)

- [ ] Create failover Lambda function
- [ ] Configure EventBridge rules
- [ ] Test automated failover
- [ ] Set up alerting

### Phase 6: Documentation & Testing (Week 3)

- [ ] Document runbook procedures
- [ ] Conduct failover drill
- [ ] Measure RTO and RPO
- [ ] Train team on procedures

---

## Quick Reference

### AWS CLI Commands

```bash
# Check replication status
aws s3api get-bucket-replication --bucket ziggie-assets-prod

# List health checks
aws route53 list-health-checks

# Check health check status
aws route53 get-health-check-status --health-check-id HC_ID

# List replicated secrets
aws secretsmanager list-secrets --filter Key=replication-status,Values=Replicated
```

### Key ARNs Template

```
Primary Region: eu-north-1
- S3: arn:aws:s3:::ziggie-assets-prod
- Secrets: arn:aws:secretsmanager:eu-north-1:ACCOUNT:secret:ziggie/*
- Route53: arn:aws:route53:::hostedzone/ZONE_ID

Secondary Region: eu-west-1
- S3: arn:aws:s3:::ziggie-assets-dr
- Secrets: arn:aws:secretsmanager:eu-west-1:ACCOUNT:secret:ziggie/*
```

---

*AWS Multi-Region Guide for Ziggie AI Ecosystem*
*Part of LOW priority gap completion (#41)*
