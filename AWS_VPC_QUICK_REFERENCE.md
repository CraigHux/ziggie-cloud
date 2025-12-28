# AWS VPC Quick Reference for Ziggie Cloud

> **Quick Commands and Configuration Snippets**
> **Last Updated**: 2025-12-23

---

## Quick Decision Matrix

| Need | Solution | Cost/Month | Command |
|------|----------|------------|---------|
| VPS to AWS connection | Public endpoints + Security Groups | $0 | See Security Groups below |
| Secure S3 access | S3 Gateway Endpoint | FREE | `aws ec2 create-vpc-endpoint --service s3` |
| SSH to GPU instances | Bastion host (t3.nano) | $3.80 | See Bastion Setup below |
| SSL certificates | ACM (AWS) + Let's Encrypt (VPS) | FREE | `certbot certonly --manual -d *.ziggie.cloud` |
| DNS for AWS services | Route 53 subdomain delegation | $0.60 | `aws route53 create-hosted-zone` |

---

## 1. VPC Setup (One-Time)

```bash
# Create VPC
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=ziggie-vpc}]' \
  --region eu-north-1 \
  --query 'Vpc.VpcId' --output text)

# Enable DNS
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames

# Create public subnet
SUBNET_ID=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone eu-north-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=ziggie-public-subnet}]' \
  --query 'Subnet.SubnetId' --output text)

aws ec2 modify-subnet-attribute --subnet-id $SUBNET_ID --map-public-ip-on-launch

# Create Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=ziggie-igw}]' \
  --query 'InternetGateway.InternetGatewayId' --output text)

aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID

# Create route table
RT_ID=$(aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=ziggie-public-rt}]' \
  --query 'RouteTable.RouteTableId' --output text)

aws ec2 create-route --route-table-id $RT_ID --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID
aws ec2 associate-route-table --subnet-id $SUBNET_ID --route-table-id $RT_ID
```

---

## 2. Security Groups (Critical)

### GPU Instance Security Group

```bash
SG_GPU=$(aws ec2 create-security-group \
  --group-name ziggie-gpu-sg \
  --description "GPU instances (ComfyUI)" \
  --vpc-id $VPC_ID \
  --query 'GroupId' --output text)

# SSH from bastion only (add bastion SG later)
# ComfyUI API from VPS only
aws ec2 authorize-security-group-ingress \
  --group-id $SG_GPU \
  --protocol tcp --port 8188 \
  --cidr 82.25.112.73/32 \
  --description "ComfyUI from VPS"

# HTTPS from VPS
aws ec2 authorize-security-group-ingress \
  --group-id $SG_GPU \
  --protocol tcp --port 443 \
  --cidr 82.25.112.73/32 \
  --description "HTTPS from VPS"
```

### Bastion Security Group

```bash
SG_BASTION=$(aws ec2 create-security-group \
  --group-name ziggie-bastion-sg \
  --description "SSH bastion host" \
  --vpc-id $VPC_ID \
  --query 'GroupId' --output text)

# SSH from VPS only
aws ec2 authorize-security-group-ingress \
  --group-id $SG_BASTION \
  --protocol tcp --port 22 \
  --cidr 82.25.112.73/32 \
  --description "SSH from VPS"

# Now add bastion to GPU SSH rule
aws ec2 authorize-security-group-ingress \
  --group-id $SG_GPU \
  --protocol tcp --port 22 \
  --source-group $SG_BASTION \
  --description "SSH from bastion"
```

---

## 3. VPC Endpoints (Cost Savings)

### S3 Gateway Endpoint (FREE)

```bash
aws ec2 create-vpc-endpoint \
  --vpc-id $VPC_ID \
  --service-name com.amazonaws.eu-north-1.s3 \
  --route-table-ids $RT_ID \
  --tag-specifications 'ResourceType=vpc-endpoint,Tags=[{Key=Name,Value=ziggie-s3-endpoint}]'
```

### Secrets Manager Interface Endpoint ($7.20/month)

```bash
SG_ENDPOINT=$(aws ec2 create-security-group \
  --group-name ziggie-endpoint-sg \
  --description "VPC endpoints" \
  --vpc-id $VPC_ID \
  --query 'GroupId' --output text)

aws ec2 authorize-security-group-ingress \
  --group-id $SG_ENDPOINT \
  --protocol tcp --port 443 \
  --source-group $SG_GPU

aws ec2 create-vpc-endpoint \
  --vpc-id $VPC_ID \
  --vpc-endpoint-type Interface \
  --service-name com.amazonaws.eu-north-1.secretsmanager \
  --subnet-ids $SUBNET_ID \
  --security-group-ids $SG_ENDPOINT \
  --private-dns-enabled \
  --tag-specifications 'ResourceType=vpc-endpoint,Tags=[{Key=Name,Value=ziggie-secrets-endpoint}]'
```

---

## 4. Bastion Host

### Launch Bastion

```bash
# Generate key pair
aws ec2 create-key-pair \
  --key-name ziggie-bastion-key \
  --query 'KeyMaterial' \
  --output text > ~/.ssh/ziggie-bastion-key.pem

chmod 400 ~/.ssh/ziggie-bastion-key.pem

# Launch instance
BASTION_ID=$(aws ec2 run-instances \
  --image-id ami-0d74f6c3c3e3d3c3c \
  --instance-type t3.nano \
  --key-name ziggie-bastion-key \
  --security-group-ids $SG_BASTION \
  --subnet-id $SUBNET_ID \
  --associate-public-ip-address \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=ziggie-bastion}]' \
  --query 'Instances[0].InstanceId' --output text)

# Get public IP
BASTION_IP=$(aws ec2 describe-instances \
  --instance-ids $BASTION_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "Bastion IP: $BASTION_IP"
```

### SSH Config (on VPS)

```bash
cat >> ~/.ssh/config <<EOF
Host ziggie-bastion
    HostName $BASTION_IP
    User ubuntu
    IdentityFile ~/.ssh/ziggie-bastion-key.pem
    StrictHostKeyChecking accept-new

Host ziggie-gpu
    HostName GPU_PRIVATE_IP
    User ubuntu
    IdentityFile ~/.ssh/ziggie-gpu-key.pem
    ProxyJump ziggie-bastion
    StrictHostKeyChecking accept-new
EOF
```

---

## 5. GPU Instance

### Launch GPU Instance

```bash
# Generate key pair
aws ec2 create-key-pair \
  --key-name ziggie-gpu-key \
  --query 'KeyMaterial' \
  --output text > ~/.ssh/ziggie-gpu-key.pem

chmod 400 ~/.ssh/ziggie-gpu-key.pem

# Create IAM role (see IAM section below)

# Launch GPU instance (g4dn.xlarge spot)
aws ec2 request-spot-instances \
  --spot-price "0.30" \
  --instance-count 1 \
  --type "persistent" \
  --launch-specification '{
    "ImageId": "ami-0c55b159cbfafe1f0",
    "InstanceType": "g4dn.xlarge",
    "KeyName": "ziggie-gpu-key",
    "SecurityGroupIds": ["'$SG_GPU'"],
    "SubnetId": "'$SUBNET_ID'",
    "IamInstanceProfile": {"Name": "ZiggieGPURole"}
  }'
```

### IAM Role for GPU

```bash
# Create trust policy
cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "ec2.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

# Create role
aws iam create-role \
  --role-name ZiggieGPURole \
  --assume-role-policy-document file://trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name ZiggieGPURole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-role-policy \
  --role-name ZiggieGPURole \
  --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite

# Create instance profile
aws iam create-instance-profile --instance-profile-name ZiggieGPURole
aws iam add-role-to-instance-profile \
  --instance-profile-name ZiggieGPURole \
  --role-name ZiggieGPURole
```

---

## 6. S3 Bucket

```bash
# Create bucket
aws s3api create-bucket \
  --bucket ziggie-comfyui-assets \
  --region eu-north-1 \
  --create-bucket-configuration LocationConstraint=eu-north-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket ziggie-comfyui-assets \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket ziggie-comfyui-assets \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Bucket policy (VPC endpoint + VPS access)
cat > bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::ziggie-comfyui-assets",
        "arn:aws:s3:::ziggie-comfyui-assets/*"
      ],
      "Condition": {
        "StringEquals": {
          "aws:sourceVpce": "vpce-xxxxx"
        }
      }
    },
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::ziggie-comfyui-assets",
        "arn:aws:s3:::ziggie-comfyui-assets/*"
      ],
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": "82.25.112.73/32"
        }
      }
    }
  ]
}
EOF

aws s3api put-bucket-policy \
  --bucket ziggie-comfyui-assets \
  --policy file://bucket-policy.json
```

---

## 7. DNS Setup

### Route 53 Subdomain Delegation

```bash
# Create hosted zone
ZONE_ID=$(aws route53 create-hosted-zone \
  --name aws.ziggie.cloud \
  --caller-reference "ziggie-$(date +%s)" \
  --query 'HostedZone.Id' --output text)

# Get nameservers
aws route53 get-hosted-zone --id $ZONE_ID \
  --query 'DelegationSet.NameServers' --output table

# Add these NS records to Hostinger DNS:
# Type: NS
# Name: aws
# Value: [each nameserver from above]
```

### A Record for GPU Instance

```bash
# Get GPU Elastic IP (or public IP)
GPU_IP=$(aws ec2 describe-instances \
  --instance-ids i-xxxxx \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

# Create A record
cat > change-batch.json <<EOF
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "comfyui.aws.ziggie.cloud",
      "Type": "A",
      "TTL": 300,
      "ResourceRecords": [{"Value": "$GPU_IP"}]
    }
  }]
}
EOF

aws route53 change-resource-record-sets \
  --hosted-zone-id $ZONE_ID \
  --change-batch file://change-batch.json
```

---

## 8. SSL Certificates

### Let's Encrypt (VPS)

```bash
# On VPS
sudo apt-get install certbot python3-certbot-nginx

# Request wildcard certificate
sudo certbot certonly --manual --preferred-challenges=dns \
  -d ziggie.cloud -d *.ziggie.cloud

# Add TXT record to Hostinger DNS as instructed
# Certificate will be at: /etc/letsencrypt/live/ziggie.cloud/
```

### AWS Certificate Manager

```bash
# Request certificate
CERT_ARN=$(aws acm request-certificate \
  --domain-name aws.ziggie.cloud \
  --subject-alternative-names *.aws.ziggie.cloud \
  --validation-method DNS \
  --region eu-north-1 \
  --query 'CertificateArn' --output text)

# Get DNS validation records
aws acm describe-certificate \
  --certificate-arn $CERT_ARN \
  --query 'Certificate.DomainValidationOptions[0].ResourceRecord' \
  --output table

# Add CNAME record to Route 53 as shown above
```

---

## 9. Common Operations

### SSH to GPU Instance

```bash
# From VPS
ssh ziggie-gpu
```

### Upload to S3 from VPS

```bash
# Configure AWS CLI on VPS
aws configure set aws_access_key_id YOUR_KEY
aws configure set aws_secret_access_key YOUR_SECRET
aws configure set region eu-north-1

# Upload file
aws s3 cp local-file.png s3://ziggie-comfyui-assets/images/
```

### Check Security Group Rules

```bash
# List all rules for GPU SG
aws ec2 describe-security-groups \
  --group-ids $SG_GPU \
  --query 'SecurityGroups[0].IpPermissions' \
  --output table
```

### Monitor Costs

```bash
# Get current month costs
aws ce get-cost-and-usage \
  --time-period Start=2025-12-01,End=2025-12-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --query 'ResultsByTime[0].Total.BlendedCost.Amount' \
  --output text
```

---

## 10. Troubleshooting

### Cannot SSH to Bastion

```bash
# Check Security Group
aws ec2 describe-security-groups --group-ids $SG_BASTION

# Expected: Port 22 from 82.25.112.73/32
# Fix: Add rule if missing
aws ec2 authorize-security-group-ingress \
  --group-id $SG_BASTION \
  --protocol tcp --port 22 \
  --cidr 82.25.112.73/32
```

### Cannot Access ComfyUI API

```bash
# Check GPU Security Group
aws ec2 describe-security-groups --group-ids $SG_GPU

# Expected: Port 8188 from 82.25.112.73/32
# Fix: Add rule if missing
aws ec2 authorize-security-group-ingress \
  --group-id $SG_GPU \
  --protocol tcp --port 8188 \
  --cidr 82.25.112.73/32
```

### S3 Access Denied

```bash
# Check bucket policy
aws s3api get-bucket-policy --bucket ziggie-comfyui-assets

# Check IAM role on GPU instance
aws ec2 describe-instances \
  --instance-ids i-xxxxx \
  --query 'Reservations[0].Instances[0].IamInstanceProfile'
```

### High Costs

```bash
# Check running instances
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[].Instances[].[InstanceId,InstanceType,PublicIpAddress]' \
  --output table

# Stop unused instances
aws ec2 stop-instances --instance-ids i-xxxxx

# Check unattached Elastic IPs (charged $3.60/month each)
aws ec2 describe-addresses \
  --query 'Addresses[?AssociationId==null].[PublicIp,AllocationId]' \
  --output table

# Release unattached IPs
aws ec2 release-address --allocation-id eipalloc-xxxxx
```

---

## Cost Summary (Monthly)

| Service | Configuration | Cost | Notes |
|---------|---------------|------|-------|
| GPU (Spot) | g4dn.xlarge | $113 | 70% savings vs on-demand |
| Bastion | t3.nano | $3.80 | Free tier eligible (12 months) |
| S3 | 100GB | $2.30 | 5GB free tier |
| VPC Endpoint (Secrets) | Interface | $7.20 | Saves $25/month (no NAT) |
| Secrets Manager | 5 secrets | $2.00 | $0.40 per secret |
| Route 53 | 1 zone | $0.60 | + $0.40/1M queries |
| CloudWatch Logs | 10GB | $5.00 | 5GB free tier |
| **Total** | | **$133.87** | **$20 less with free tier** |

---

## Resource IDs Template

Fill in after deployment:

```bash
export VPC_ID=vpc-xxxxx
export SUBNET_PUBLIC=subnet-xxxxx
export SUBNET_PRIVATE=subnet-xxxxx
export IGW_ID=igw-xxxxx
export RT_PUBLIC=rtb-xxxxx
export SG_GPU=sg-xxxxx
export SG_BASTION=sg-xxxxx
export SG_ENDPOINT=sg-xxxxx
export BASTION_ID=i-xxxxx
export BASTION_IP=x.x.x.x
export GPU_ID=i-xxxxx
export GPU_IP=x.x.x.x
export S3_BUCKET=ziggie-comfyui-assets
export ROUTE53_ZONE_ID=Z1234567890ABC
```

Save this to `~/.aws-ziggie-resources` and source it:
```bash
source ~/.aws-ziggie-resources
```

---

**Quick Reference Version**: 1.0
**Last Updated**: 2025-12-23
