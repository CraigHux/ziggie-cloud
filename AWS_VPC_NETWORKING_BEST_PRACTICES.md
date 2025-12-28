# AWS VPC Networking Best Practices for Ziggie Cloud Hybrid Setup

> **Last Updated**: 2025-12-23
> **Context**: Hybrid architecture - Hostinger VPS (82.25.112.73) + AWS EU-North-1 (Stockholm)
> **Use Case**: GPU compute, S3 storage, Secrets Manager integration
> **Domain**: ziggie.cloud (managed through Hostinger)

---

## Executive Summary

This document provides comprehensive AWS VPC networking architecture and best practices for integrating AWS services (GPU EC2, S3, Secrets Manager) with your existing Hostinger VPS infrastructure. The focus is on **security-first design** with **cost optimization** for production deployment.

**Key Decision**: Use **public endpoints with restrictive Security Groups** instead of Site-to-Site VPN for significant cost savings ($36-43/month) while maintaining security.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [VPN vs Public Endpoints Decision Matrix](#2-vpn-vs-public-endpoints-decision-matrix)
3. [VPC Setup for Hybrid Cloud](#3-vpc-setup-for-hybrid-cloud)
4. [Security Group Configurations](#4-security-group-configurations)
5. [VPC Endpoints (Cost Optimization)](#5-vpc-endpoints-cost-optimization)
6. [Network ACL Best Practices](#6-network-acl-best-practices)
7. [DNS Configuration](#7-dns-configuration)
8. [TLS/SSL Certificate Management](#8-tlsssl-certificate-management)
9. [Bastion Host Setup](#9-bastion-host-setup)
10. [Cost Analysis & Free Tier](#10-cost-analysis--free-tier)
11. [Implementation Checklist](#11-implementation-checklist)

---

## 1. Architecture Overview

### Current Infrastructure

```
Hostinger VPS (Primary)
├── IP: 82.25.112.73
├── Location: Europe
├── Docker Containers:
│   ├── Nginx Reverse Proxy
│   ├── Control Center Frontend
│   ├── Knowledge Base API
│   └── Sim Studio Backend
└── Domain: ziggie.cloud (Hostinger DNS)
```

### Proposed AWS Integration

```
AWS EU-North-1 (Stockholm)
├── VPC: 10.0.0.0/16
├── Availability Zones: eu-north-1a, eu-north-1b
├── Subnets:
│   ├── Public Subnet (10.0.1.0/24) - GPU EC2, Bastion
│   └── Private Subnet (10.0.10.0/24) - Future use
├── Services:
│   ├── EC2 GPU Instances (g4dn.xlarge for ComfyUI)
│   ├── S3 Buckets (asset storage)
│   └── Secrets Manager (API keys, credentials)
└── Security:
    ├── Security Groups (stateful firewall)
    ├── VPC Endpoints (S3, Secrets Manager)
    └── IAM Roles with least privilege
```

### Network Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Hostinger VPS (82.25.112.73)                │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────────┐    │
│  │   Nginx    │  │ Control Ctr  │  │  Sim Studio (LLM)    │    │
│  │   :80/443  │→ │  Frontend    │  │  + ComfyUI Client    │    │
│  └────────────┘  └──────────────┘  └──────────────────────┘    │
│         │                                      │                 │
└─────────┼──────────────────────────────────────┼─────────────────┘
          │ HTTPS                                │ HTTPS API
          │ (Let's Encrypt)                      │ (IAM Auth)
          ▼                                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Public Internet (TLS 1.3)                      │
└─────────────────────────────────────────────────────────────────┘
          │                                      │
          ▼                                      ▼
┌─────────────────────────────────────────────────────────────────┐
│            AWS VPC (10.0.0.0/16) - EU-North-1                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │        Public Subnet (10.0.1.0/24) - AZ: eu-north-1a     │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │  │
│  │  │ GPU EC2      │  │ Bastion Host │  │ NAT Gateway   │  │  │
│  │  │ g4dn.xlarge  │  │ (SSH only)   │  │ (if needed)   │  │  │
│  │  │ ComfyUI API  │  │              │  │               │  │  │
│  │  └──────────────┘  └──────────────┘  └───────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │       Private Subnet (10.0.10.0/24) - AZ: eu-north-1b    │  │
│  │         (Reserved for future database instances)         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  VPC Endpoints (PrivateLink):                                   │
│  ├── S3 Gateway Endpoint (FREE)                                 │
│  └── Secrets Manager Interface Endpoint ($7.20/month)           │
│                                                                  │
│  S3 Buckets:                                                    │
│  ├── ziggie-comfyui-assets (private)                            │
│  └── ziggie-game-models (private with VPS access)               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. VPN vs Public Endpoints Decision Matrix

### Connectivity Options Comparison

| Factor | Site-to-Site VPN | AWS Client VPN | Public Endpoints + SG | **Recommended** |
|--------|------------------|----------------|-----------------------|-----------------|
| **Monthly Cost** | $36 (VPN endpoint) | $73+ (endpoint + hours) | $0-7 (VPC endpoints only) | **Public + SG** |
| **Setup Complexity** | High (BGP, IPsec) | Medium (client certs) | Low (Security Groups) | **Public + SG** |
| **VPS Compatibility** | Requires VPS routing | Requires client install | Works immediately | **Public + SG** |
| **Latency** | +5-10ms overhead | +5-10ms overhead | Direct routing | **Public + SG** |
| **Security** | Encrypted tunnel | Encrypted tunnel | TLS + IAM + SG | **Public + SG** |
| **Maintenance** | High (tunnel monitoring) | Medium (cert rotation) | Low (SG rules) | **Public + SG** |
| **AWS Free Tier** | No | No | Yes (data transfer limits) | **Public + SG** |
| **Scalability** | Fixed bandwidth | Per-client licensing | Auto-scaling | **Public + SG** |

### Decision: Public Endpoints with Security Groups

**Rationale**:
1. **Cost Savings**: $36-43/month saved (critical for early-stage deployment)
2. **Security Equivalence**: TLS 1.3 + AWS Signature v4 + IP whitelisting = VPN-grade security
3. **Simplicity**: No VPN gateway management, no routing protocols
4. **Performance**: Lower latency (no VPN overhead)
5. **Free Tier Eligible**: Data transfer within free tier limits

**Security Implementation**:
```
Defense-in-Depth Layers:
1. Network Layer: Security Groups (IP whitelist to 82.25.112.73/32)
2. Transport Layer: TLS 1.3 encryption (all traffic)
3. Application Layer: AWS Signature v4 authentication (S3, Secrets Manager)
4. Identity Layer: IAM roles with least privilege
5. Data Layer: S3 bucket policies, encryption at rest (AES-256)
```

**When to Reconsider VPN**:
- If you add 10+ AWS services requiring inter-service communication
- If you need to route private subnet traffic from VPS
- If compliance requires dedicated network tunnels (HIPAA, PCI-DSS Level 1)

---

## 3. VPC Setup for Hybrid Cloud

### 3.1 VPC Configuration

```bash
# VPC CIDR: 10.0.0.0/16 (65,536 IPs)
# Rationale: RFC 1918 private range, no conflict with VPS network

aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=ziggie-cloud-vpc},{Key=Environment,Value=production}]' \
  --region eu-north-1
```

**VPC Features to Enable**:
```bash
# Enable DNS resolution (required for VPC endpoints)
aws ec2 modify-vpc-attribute \
  --vpc-id vpc-xxxxx \
  --enable-dns-support

# Enable DNS hostnames (required for public EC2 instances)
aws ec2 modify-vpc-attribute \
  --vpc-id vpc-xxxxx \
  --enable-dns-hostnames
```

### 3.2 Subnet Design

#### Public Subnet (10.0.1.0/24)

```bash
# Public subnet for GPU EC2, Bastion Host
aws ec2 create-subnet \
  --vpc-id vpc-xxxxx \
  --cidr-block 10.0.1.0/24 \
  --availability-zone eu-north-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=ziggie-public-subnet-1a},{Key=Type,Value=public}]'

# Enable auto-assign public IP
aws ec2 modify-subnet-attribute \
  --subnet-id subnet-xxxxx \
  --map-public-ip-on-launch
```

#### Private Subnet (10.0.10.0/24) - Future Use

```bash
# Private subnet for databases, internal services
aws ec2 create-subnet \
  --vpc-id vpc-xxxxx \
  --cidr-block 10.0.10.0/24 \
  --availability-zone eu-north-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=ziggie-private-subnet-1b},{Key=Type,Value=private}]'
```

### 3.3 Internet Gateway

```bash
# Create Internet Gateway for public subnet
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=ziggie-igw}]'

# Attach to VPC
aws ec2 attach-internet-gateway \
  --vpc-id vpc-xxxxx \
  --internet-gateway-id igw-xxxxx
```

### 3.4 Route Tables

#### Public Route Table

```bash
# Create route table for public subnet
aws ec2 create-route-table \
  --vpc-id vpc-xxxxx \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=ziggie-public-rt}]'

# Add default route to Internet Gateway
aws ec2 create-route \
  --route-table-id rtb-xxxxx \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id igw-xxxxx

# Associate with public subnet
aws ec2 associate-route-table \
  --subnet-id subnet-xxxxx \
  --route-table-id rtb-xxxxx
```

#### Private Route Table (Future)

```bash
# For private subnet, route through NAT Gateway (if needed)
# NAT Gateway costs $0.045/hour ($32/month) - only deploy if private subnet needs internet
```

---

## 4. Security Group Configurations

Security Groups are **stateful firewalls** at the instance level. They act as the primary access control mechanism.

### 4.1 GPU EC2 Security Group (ComfyUI)

```bash
# Create Security Group for GPU instances
aws ec2 create-security-group \
  --group-name ziggie-gpu-sg \
  --description "Security group for GPU EC2 running ComfyUI" \
  --vpc-id vpc-xxxxx

# Tag the Security Group
aws ec2 create-tags \
  --resources sg-xxxxx \
  --tags Key=Name,Value=ziggie-gpu-sg Key=Service,Value=ComfyUI
```

**Inbound Rules**:

```bash
# Rule 1: SSH from Bastion Host ONLY (not VPS)
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 22 \
  --source-group sg-bastion-xxxxx \
  --description "SSH from bastion host only"

# Rule 2: ComfyUI API (port 8188) from VPS ONLY
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 8188 \
  --cidr 82.25.112.73/32 \
  --description "ComfyUI API from Hostinger VPS only"

# Rule 3: HTTPS (443) from VPS for management
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 443 \
  --cidr 82.25.112.73/32 \
  --description "HTTPS from VPS for management"
```

**Outbound Rules** (default: allow all, can restrict):

```bash
# Restrict outbound to only necessary services
# Rule 1: HTTPS to AWS services (S3, Secrets Manager via VPC endpoints)
aws ec2 authorize-security-group-egress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 443 \
  --cidr 10.0.0.0/16 \
  --description "HTTPS to VPC endpoints"

# Rule 2: Package updates (apt/yum repositories)
aws ec2 authorize-security-group-egress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0 \
  --description "HTTPS for package updates"
```

### 4.2 Bastion Host Security Group

```bash
# Create Security Group for Bastion Host
aws ec2 create-security-group \
  --group-name ziggie-bastion-sg \
  --description "Security group for SSH bastion host" \
  --vpc-id vpc-xxxxx
```

**Inbound Rules**:

```bash
# SSH from VPS ONLY
aws ec2 authorize-security-group-ingress \
  --group-id sg-bastion-xxxxx \
  --protocol tcp \
  --port 22 \
  --cidr 82.25.112.73/32 \
  --description "SSH from Hostinger VPS only"

# Optional: SSH from your home/office IP (for emergency access)
aws ec2 authorize-security-group-ingress \
  --group-id sg-bastion-xxxxx \
  --protocol tcp \
  --port 22 \
  --cidr YOUR_HOME_IP/32 \
  --description "SSH from admin workstation"
```

**Outbound Rules**:

```bash
# SSH to GPU instances within VPC
aws ec2 authorize-security-group-egress \
  --group-id sg-bastion-xxxxx \
  --protocol tcp \
  --port 22 \
  --cidr 10.0.0.0/16 \
  --description "SSH to instances in VPC"
```

### 4.3 VPC Endpoint Security Group

```bash
# Security Group for VPC Endpoints (S3, Secrets Manager)
aws ec2 create-security-group \
  --group-name ziggie-vpc-endpoint-sg \
  --description "Security group for VPC endpoints" \
  --vpc-id vpc-xxxxx
```

**Inbound Rules**:

```bash
# HTTPS from GPU instances
aws ec2 authorize-security-group-ingress \
  --group-id sg-endpoint-xxxxx \
  --protocol tcp \
  --port 443 \
  --source-group sg-gpu-xxxxx \
  --description "HTTPS from GPU instances"

# HTTPS from VPS (for S3 access)
aws ec2 authorize-security-group-ingress \
  --group-id sg-endpoint-xxxxx \
  --protocol tcp \
  --port 443 \
  --cidr 82.25.112.73/32 \
  --description "HTTPS from VPS"
```

### 4.4 Security Group Best Practices

| Practice | Rationale | Implementation |
|----------|-----------|----------------|
| **Least Privilege** | Only open required ports | Deny all by default, allow specific rules |
| **IP Whitelisting** | Limit source IPs to VPS only | Use `/32` CIDR for single IPs |
| **No 0.0.0.0/0 Inbound** | Prevent public internet access | Use VPS IP or Security Group references |
| **Descriptive Names** | Easy troubleshooting | `--description` on every rule |
| **Regular Audits** | Remove unused rules | Monthly review of Security Groups |
| **Separate SGs per Service** | Blast radius containment | Don't reuse SGs across different roles |
| **Stateful Design** | Automatic return traffic | No need to add reverse rules |

---

## 5. VPC Endpoints (Cost Optimization)

VPC Endpoints enable private connectivity to AWS services **without traversing the public internet**, reducing data transfer costs and improving security.

### 5.1 S3 Gateway Endpoint (FREE)

**Key Benefit**: Eliminates data transfer charges for S3 access within the same region.

```bash
# Create S3 Gateway Endpoint (FREE, no hourly charges)
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-xxxxx \
  --service-name com.amazonaws.eu-north-1.s3 \
  --route-table-ids rtb-public-xxxxx rtb-private-xxxxx \
  --tag-specifications 'ResourceType=vpc-endpoint,Tags=[{Key=Name,Value=ziggie-s3-endpoint}]'
```

**Route Table Configuration**:
```bash
# S3 Gateway Endpoint automatically adds route to route tables
# Route: s3-prefix-list → vpce-xxxxx
# No Security Group needed (uses bucket policies)
```

**S3 Bucket Policy for VPC Endpoint**:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowVPCEndpointAccess",
      "Effect": "Allow",
      "Principal": "*",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
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
      "Sid": "AllowVPSAccess",
      "Effect": "Allow",
      "Principal": "*",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
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
```

**Cost Savings**:
- Standard S3 data transfer OUT: $0.09/GB
- Via S3 Gateway Endpoint: **$0.00/GB** (within region)
- **Estimated savings**: $50-200/month depending on usage

### 5.2 Secrets Manager Interface Endpoint

**Cost**: $0.01/hour = **$7.20/month** + $0.01/GB data processed

```bash
# Create Secrets Manager Interface Endpoint
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-xxxxx \
  --vpc-endpoint-type Interface \
  --service-name com.amazonaws.eu-north-1.secretsmanager \
  --subnet-ids subnet-public-xxxxx \
  --security-group-ids sg-endpoint-xxxxx \
  --private-dns-enabled \
  --tag-specifications 'ResourceType=vpc-endpoint,Tags=[{Key=Name,Value=ziggie-secretsmanager-endpoint}]'
```

**Cost-Benefit Analysis**:

| Without VPC Endpoint | With VPC Endpoint |
|----------------------|-------------------|
| Public internet route | Private AWS network |
| Data transfer charges ($0.09/GB) | Endpoint charge ($7.20/month) |
| NAT Gateway required ($32/month) | No NAT Gateway needed |
| Higher latency | Lower latency |
| **Total**: $32/month + data | **Total**: $7.20/month |

**Decision**: Deploy Secrets Manager endpoint to save $24.80/month and improve security.

### 5.3 VPC Endpoint Best Practices

| Practice | Rationale | Implementation |
|----------|-----------|----------------|
| **Gateway over Interface** | Free for S3, DynamoDB | Always use Gateway endpoints when available |
| **Private DNS Enabled** | No code changes needed | `--private-dns-enabled` for Interface endpoints |
| **Endpoint Policies** | Least privilege access | Restrict to specific actions/resources |
| **Multi-AZ Endpoints** | High availability | Deploy Interface endpoints in 2+ subnets |
| **Monitor Endpoint Usage** | Cost optimization | CloudWatch metrics for data processed |

---

## 6. Network ACL Best Practices

Network ACLs (NACLs) are **stateless firewalls** at the subnet level. They provide an additional layer of defense.

### 6.1 Default NACL vs Custom NACL

| Aspect | Default NACL | Custom NACL | **Recommendation** |
|--------|--------------|-------------|-------------------|
| **Rules** | Allow all inbound/outbound | Explicit allow/deny | **Custom NACL** |
| **Stateful** | No (must allow return traffic) | No | N/A |
| **Use Case** | Quick start, low security | Production, compliance | **Custom NACL** |
| **Maintenance** | Low | Medium | **Custom NACL** |

### 6.2 Public Subnet NACL

```bash
# Create Custom NACL for Public Subnet
aws ec2 create-network-acl \
  --vpc-id vpc-xxxxx \
  --tag-specifications 'ResourceType=network-acl,Tags=[{Key=Name,Value=ziggie-public-nacl}]'

# Associate with Public Subnet
aws ec2 replace-network-acl-association \
  --association-id aclassoc-xxxxx \
  --network-acl-id acl-xxxxx
```

**Inbound Rules** (order matters, lower rule number = higher priority):

```bash
# Rule 100: Allow SSH from VPS to Bastion
aws ec2 create-network-acl-entry \
  --network-acl-id acl-xxxxx \
  --rule-number 100 \
  --protocol tcp \
  --port-range From=22,To=22 \
  --cidr-block 82.25.112.73/32 \
  --rule-action allow \
  --ingress

# Rule 110: Allow ComfyUI API from VPS
aws ec2 create-network-acl-entry \
  --network-acl-id acl-xxxxx \
  --rule-number 110 \
  --protocol tcp \
  --port-range From=8188,To=8188 \
  --cidr-block 82.25.112.73/32 \
  --rule-action allow \
  --ingress

# Rule 120: Allow HTTPS from VPS
aws ec2 create-network-acl-entry \
  --network-acl-id acl-xxxxx \
  --rule-number 120 \
  --protocol tcp \
  --port-range From=443,To=443 \
  --cidr-block 82.25.112.73/32 \
  --rule-action allow \
  --ingress

# Rule 130: Allow ephemeral ports for return traffic (CRITICAL for stateless NACLs)
aws ec2 create-network-acl-entry \
  --network-acl-id acl-xxxxx \
  --rule-number 130 \
  --protocol tcp \
  --port-range From=1024,To=65535 \
  --cidr-block 0.0.0.0/0 \
  --rule-action allow \
  --ingress

# Rule 32767: Deny all (implicit, always last)
```

**Outbound Rules**:

```bash
# Rule 100: Allow HTTPS to internet (package updates, VPC endpoints)
aws ec2 create-network-acl-entry \
  --network-acl-id acl-xxxxx \
  --rule-number 100 \
  --protocol tcp \
  --port-range From=443,To=443 \
  --cidr-block 0.0.0.0/0 \
  --rule-action allow \
  --egress

# Rule 110: Allow HTTP to internet (package updates)
aws ec2 create-network-acl-entry \
  --network-acl-id acl-xxxxx \
  --rule-number 110 \
  --protocol tcp \
  --port-range From=80,To=80 \
  --cidr-block 0.0.0.0/0 \
  --rule-action allow \
  --egress

# Rule 120: Allow ephemeral ports for return traffic
aws ec2 create-network-acl-entry \
  --network-acl-id acl-xxxxx \
  --rule-number 120 \
  --protocol tcp \
  --port-range From=1024,To=65535 \
  --cidr-block 0.0.0.0/0 \
  --rule-action allow \
  --egress
```

### 6.3 NACL Best Practices

| Practice | Rationale | Implementation |
|----------|-----------|----------------|
| **Stateless Awareness** | Must allow return traffic | Add ephemeral port rules (1024-65535) |
| **Rule Numbering** | Leave gaps for future rules | Use 100, 110, 120 (not 1, 2, 3) |
| **Security Groups First** | NACLs are secondary defense | Design Security Groups first, NACLs second |
| **Deny Rules Sparingly** | Can cause hard-to-debug issues | Use deny for known bad actors only |
| **Document Rules** | Easy troubleshooting | Add descriptions in tags |
| **Default Deny** | Fail-safe | Implicit deny all at rule 32767 |

### 6.4 NACL vs Security Group - When to Use What

```
Defense-in-Depth Strategy:

┌─────────────────────────────────────────────────────────┐
│  Network ACL (Subnet-Level, Stateless)                  │
│  ├── Broad subnet-wide protection                       │
│  ├── Block known malicious IPs/ranges                   │
│  └── Compliance requirement (DMZ separation)            │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  Security Group (Instance-Level, Stateful)              │
│  ├── Granular per-instance rules                        │
│  ├── Application-specific port control                  │
│  └── Primary access control mechanism                   │
└─────────────────────────────────────────────────────────┘
```

**Use NACLs for**:
- Blocking entire IP ranges (e.g., known malicious countries)
- Subnet-level isolation (e.g., separating DMZ from internal)
- Compliance requirements (PCI-DSS requires network segmentation)

**Use Security Groups for**:
- All primary access control
- Application-specific rules
- Dynamic IP whitelisting (easier to update)

---

## 7. DNS Configuration

### 7.1 Route 53 vs Hostinger DNS Decision

| Factor | Route 53 | Hostinger DNS | **Recommendation** |
|--------|----------|---------------|--------------------|
| **Cost** | $0.50/month per zone + queries | Free with hosting | **Hybrid** |
| **Features** | Health checks, failover, geolocation | Basic A/CNAME records | **Hybrid** |
| **Latency** | Global edge locations | Single region | Route 53 |
| **Integration** | Native AWS (ACM, CloudFront) | Manual updates | Route 53 |
| **Ease of Use** | AWS Console, CLI | Hostinger Panel | Hostinger |
| **SSL Automation** | ACM auto-renewal | Let's Encrypt manual | Route 53 |

### 7.2 Recommended Hybrid Setup

**Use Hostinger DNS for**:
- Main domain: `ziggie.cloud` → 82.25.112.73 (VPS)
- Wildcard: `*.ziggie.cloud` → 82.25.112.73 (VPS handles subdomains)

**Use Route 53 for**:
- AWS-specific subdomains: `aws.ziggie.cloud` (delegated subdomain)
- GPU instances: `comfyui.aws.ziggie.cloud` → GPU EC2 Elastic IP
- S3 static sites: `assets.aws.ziggie.cloud` → CloudFront distribution

### 7.3 DNS Delegation Configuration

**Step 1: Create Route 53 Hosted Zone for Subdomain**

```bash
# Create hosted zone for aws.ziggie.cloud
aws route53 create-hosted-zone \
  --name aws.ziggie.cloud \
  --caller-reference "ziggie-aws-$(date +%s)" \
  --hosted-zone-config Comment="AWS services subdomain"
```

**Step 2: Note the NS Records**

```bash
# Get nameservers for the hosted zone
aws route53 get-hosted-zone --id Z1234567890ABC

# Output (example):
# ns-123.awsdns-12.com
# ns-456.awsdns-34.net
# ns-789.awsdns-56.org
# ns-012.awsdns-78.co.uk
```

**Step 3: Add NS Records in Hostinger DNS**

```
# In Hostinger DNS panel, add:
Type: NS
Name: aws
Value: ns-123.awsdns-12.com (repeat for all 4 nameservers)
TTL: 3600
```

**Step 4: Create A Record in Route 53**

```bash
# Create A record for comfyui.aws.ziggie.cloud
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "comfyui.aws.ziggie.cloud",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [{"Value": "ELASTIC_IP_OF_GPU_EC2"}]
      }
    }]
  }'
```

### 7.4 DNS Best Practices

| Practice | Rationale | Implementation |
|----------|-----------|----------------|
| **Low TTL Initially** | Easy to fix mistakes | TTL=300 (5 min) during setup, increase to 3600 after stable |
| **ALIAS over CNAME** | No CNAME lookup cost | Use Route 53 ALIAS for AWS resources |
| **Health Checks** | Automatic failover | Route 53 health checks for critical services |
| **DNSSEC** | Prevent DNS spoofing | Enable DNSSEC in Route 53 (free) |
| **CAA Records** | Prevent unauthorized SSL | Add CAA record: `0 issue "letsencrypt.org"` |

---

## 8. TLS/SSL Certificate Management

### 8.1 AWS Certificate Manager (ACM) vs Let's Encrypt

| Factor | ACM | Let's Encrypt | **Recommendation** |
|--------|-----|---------------|--------------------|
| **Cost** | FREE | FREE | Both (hybrid) |
| **Auto-Renewal** | Yes (AWS handles) | Yes (certbot) | Both |
| **Wildcard Support** | Yes | Yes (DNS-01 challenge) | Both |
| **Where Valid** | AWS services only (ELB, CloudFront) | Anywhere | **Both** |
| **Validation** | DNS or HTTP | DNS or HTTP | Both |
| **Certificate Transparency** | Yes | Yes | Both |

### 8.2 Certificate Strategy

**For VPS (Hostinger) - Use Let's Encrypt**:

```bash
# On VPS: Install certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Request wildcard certificate (requires DNS validation)
sudo certbot certonly --manual --preferred-challenges=dns -d ziggie.cloud -d *.ziggie.cloud

# Add TXT record to Hostinger DNS as instructed by certbot
# Record: _acme-challenge.ziggie.cloud → random_string

# Certificate files will be at:
# /etc/letsencrypt/live/ziggie.cloud/fullchain.pem
# /etc/letsencrypt/live/ziggie.cloud/privkey.pem

# Auto-renewal (certbot adds cron job automatically)
sudo certbot renew --dry-run
```

**For AWS Resources - Use ACM**:

```bash
# Request certificate for aws.ziggie.cloud subdomain
aws acm request-certificate \
  --domain-name aws.ziggie.cloud \
  --subject-alternative-names *.aws.ziggie.cloud \
  --validation-method DNS \
  --region eu-north-1

# ACM will provide CNAME records to add to Route 53
# AWS will auto-renew before expiration (60 days)
```

### 8.3 TLS Configuration Best Practices

**Nginx Configuration (VPS)**:

```nginx
# /etc/nginx/sites-available/ziggie.cloud
server {
    listen 443 ssl http2;
    server_name ziggie.cloud www.ziggie.cloud;

    # Let's Encrypt Certificates
    ssl_certificate /etc/letsencrypt/live/ziggie.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ziggie.cloud/privkey.pem;

    # TLS 1.3 Only (TLS 1.2 as fallback)
    ssl_protocols TLSv1.3 TLSv1.2;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;

    # HSTS (force HTTPS for 1 year)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # OCSP Stapling (improves SSL handshake)
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/ziggie.cloud/chain.pem;

    # DH Parameters for Perfect Forward Secrecy
    ssl_dhparam /etc/nginx/dhparam.pem;

    location / {
        proxy_pass http://localhost:3000;  # Control Center frontend
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name ziggie.cloud www.ziggie.cloud;
    return 301 https://$server_name$request_uri;
}
```

**Generate DH Parameters**:

```bash
# On VPS (takes 5-10 minutes)
sudo openssl dhparam -out /etc/nginx/dhparam.pem 4096
```

### 8.4 SSL/TLS Best Practices

| Practice | Rationale | Implementation |
|----------|-----------|----------------|
| **TLS 1.3 Only** | Latest protocol, best security | `ssl_protocols TLSv1.3 TLSv1.2;` |
| **HSTS Preload** | Prevent SSL stripping attacks | Add domain to HSTS preload list |
| **OCSP Stapling** | Faster SSL handshake | Enable in Nginx/Apache |
| **Perfect Forward Secrecy** | Protects past sessions | Use ECDHE cipher suites |
| **Certificate Transparency** | Detect rogue certificates | Monitor CT logs (free tools) |
| **Auto-Renewal** | Prevent expiration outages | Certbot cron, ACM auto-renews |

**Test SSL Configuration**:
```bash
# Use SSL Labs (free online tool)
https://www.ssllabs.com/ssltest/analyze.html?d=ziggie.cloud

# Target: A+ rating
```

---

## 9. Bastion Host Setup

### 9.1 Why Bastion Host?

**Problem**: Exposing GPU EC2 instances directly to the internet (SSH port 22) is a security risk.

**Solution**: Bastion host acts as a "jump server" - only entry point for SSH access.

```
VPS (82.25.112.73) → Bastion Host (Public Subnet) → GPU EC2 (Public Subnet)
                    SSH :22                        SSH :22
```

### 9.2 Bastion Host Instance Configuration

**Instance Type**: `t3.nano` (free tier eligible, $0.0052/hour if free tier exhausted)

```bash
# Launch bastion host (Ubuntu 24.04 LTS)
aws ec2 run-instances \
  --image-id ami-0d74f6c3c3e3d3c3c \  # Ubuntu 24.04 LTS in eu-north-1
  --instance-type t3.nano \
  --key-name ziggie-bastion-key \
  --security-group-ids sg-bastion-xxxxx \
  --subnet-id subnet-public-xxxxx \
  --associate-public-ip-address \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=ziggie-bastion},{Key=Role,Value=bastion}]' \
  --iam-instance-profile Name=ZiggieBastionRole \
  --user-data file://bastion-user-data.sh
```

**User Data Script** (`bastion-user-data.sh`):

```bash
#!/bin/bash
# Bastion host hardening script

# Update system
apt-get update && apt-get upgrade -y

# Install fail2ban (auto-ban brute force attempts)
apt-get install -y fail2ban

# Configure fail2ban for SSH
cat > /etc/fail2ban/jail.local <<EOF
[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600
EOF

systemctl enable fail2ban
systemctl start fail2ban

# Disable root login
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# Disable password authentication (key-based only)
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# Enable SSH logging
echo "LogLevel VERBOSE" >> /etc/ssh/sshd_config

# Restart SSH
systemctl restart sshd

# Install CloudWatch Logs agent (monitor SSH access)
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i -E ./amazon-cloudwatch-agent.deb

# Configure CloudWatch Logs
cat > /opt/aws/amazon-cloudwatch-agent/etc/config.json <<EOF
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/auth.log",
            "log_group_name": "/aws/ec2/ziggie-bastion",
            "log_stream_name": "{instance_id}/auth.log"
          }
        ]
      }
    }
  }
}
EOF

/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json \
  -s

echo "Bastion host setup complete"
```

### 9.3 SSH Access Pattern

**Step 1: SSH from VPS to Bastion**

```bash
# On VPS (82.25.112.73)
ssh -i ~/.ssh/ziggie-bastion-key.pem ubuntu@BASTION_PUBLIC_IP
```

**Step 2: SSH from Bastion to GPU EC2**

```bash
# On Bastion Host
ssh -i ~/.ssh/ziggie-gpu-key.pem ubuntu@GPU_PRIVATE_IP
```

**Simplified with SSH Config** (`~/.ssh/config` on VPS):

```bash
# Bastion Host
Host ziggie-bastion
    HostName BASTION_PUBLIC_IP
    User ubuntu
    IdentityFile ~/.ssh/ziggie-bastion-key.pem
    StrictHostKeyChecking yes

# GPU Instance (via Bastion)
Host ziggie-gpu
    HostName GPU_PRIVATE_IP
    User ubuntu
    IdentityFile ~/.ssh/ziggie-gpu-key.pem
    ProxyJump ziggie-bastion
    StrictHostKeyChecking yes
```

**One-Command SSH to GPU**:

```bash
# On VPS
ssh ziggie-gpu
# This automatically connects via bastion
```

### 9.4 Bastion Host Best Practices

| Practice | Rationale | Implementation |
|----------|-----------|----------------|
| **Key-Based Auth Only** | Prevent brute force | Disable password auth in sshd_config |
| **fail2ban** | Auto-ban attackers | 3 failed attempts = 1 hour ban |
| **Minimal Software** | Reduce attack surface | Only SSH, fail2ban, CloudWatch agent |
| **Logging** | Audit trail | CloudWatch Logs for all SSH sessions |
| **No Elastic IP** | Reduce cost | Use public IP, update DNS if changed |
| **Session Timeout** | Auto-disconnect idle sessions | `ClientAliveInterval 300, ClientAliveCountMax 2` |
| **SSH Key Rotation** | Limit key compromise impact | Rotate keys every 90 days |
| **MFA (Optional)** | Extra security layer | Google Authenticator PAM module |

### 9.5 Bastion Host Alternatives

**AWS Systems Manager Session Manager** (SSM):

**Pros**:
- No bastion host needed (cost savings)
- No SSH keys to manage
- Encrypted sessions via AWS API
- Full audit logs in CloudTrail

**Cons**:
- Requires IAM role on instances
- Internet access to AWS SSM endpoint
- Requires SSM agent on instances

**When to Use**:
- If you have many instances (bastion becomes bottleneck)
- If you want to eliminate SSH key management
- If compliance requires full session recording

**Setup**:

```bash
# Attach IAM role to GPU instance
aws iam attach-role-policy \
  --role-name ZiggieGPURole \
  --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

# Connect from VPS (requires AWS CLI)
aws ssm start-session --target i-1234567890abcdef0
```

**Cost Comparison**:

| Solution | Monthly Cost | Setup Complexity |
|----------|--------------|------------------|
| Bastion (t3.nano) | $3.80 | Medium |
| SSM Session Manager | $0 | Low |

**Recommendation**: Start with bastion host (simpler), migrate to SSM if you scale to 10+ instances.

---

## 10. Cost Analysis & Free Tier

### 10.1 AWS Free Tier Overview

**12-Month Free Tier** (new accounts only):
- **EC2**: 750 hours/month of t2.micro or t3.micro (Linux)
- **S3**: 5GB storage, 20,000 GET requests, 2,000 PUT requests
- **Data Transfer**: 100GB outbound (15GB/month)
- **VPC**: Unlimited (no charge for VPC itself)
- **Security Groups**: Unlimited (free)
- **Route 53**: 1 hosted zone ($0.50/month, not free)

**Always Free**:
- **VPC**: Unlimited VPCs, subnets, route tables, NACLs
- **S3 Gateway Endpoint**: Unlimited usage (FREE)
- **CloudWatch**: 10 custom metrics, 10 alarms, 5GB logs

### 10.2 Monthly Cost Estimate (After Free Tier)

| Service | Configuration | Monthly Cost | Free Tier | Notes |
|---------|---------------|--------------|-----------|-------|
| **GPU EC2** | g4dn.xlarge (on-demand) | $376.56 | No | 4 vCPU, 16GB RAM, T4 GPU |
| **GPU EC2** | g4dn.xlarge (spot) | $112.97 | No | 70% savings, risk of interruption |
| **Bastion Host** | t3.nano | $3.80 | 750h free | 2 vCPU, 0.5GB RAM |
| **S3 Storage** | 100GB | $2.30 | 5GB free | Standard storage |
| **S3 Requests** | 100K GET, 10K PUT | $0.44 | 20K GET, 2K PUT free | API calls |
| **Data Transfer** | 50GB outbound | $4.50 | 100GB free (first 12 months) | To VPS |
| **VPC Endpoint (S3)** | Gateway | $0.00 | Always free | Eliminates data transfer |
| **VPC Endpoint (Secrets)** | Interface | $7.20 | No | $0.01/hour |
| **Route 53** | 1 hosted zone + queries | $0.60 | No | $0.50/zone + $0.40/1M queries |
| **Elastic IP** | 1 IP (attached) | $0.00 | Free if attached | $3.60/month if unattached |
| **CloudWatch Logs** | 10GB ingestion | $5.00 | 5GB free | SSH logs, app logs |
| **Secrets Manager** | 5 secrets | $2.00 | No | $0.40/secret/month |
| **NAT Gateway** | (Not needed) | $0.00 | No | Using public endpoints |
| **Site-to-Site VPN** | (Not deployed) | $0.00 | No | Saving $36/month |
| **Total (Spot GPU)** | | **$138.41** | | **Recommended for production** |
| **Total (On-Demand GPU)** | | **$402.00** | | Use for critical workloads |

### 10.3 Cost Optimization Strategies

#### Strategy 1: GPU Spot Instances (70% Savings)

```bash
# Launch GPU instance as Spot (interruption risk)
aws ec2 request-spot-instances \
  --spot-price "0.30" \
  --instance-count 1 \
  --type "persistent" \
  --launch-specification '{
    "ImageId": "ami-xxxxx",
    "InstanceType": "g4dn.xlarge",
    "KeyName": "ziggie-gpu-key",
    "SecurityGroupIds": ["sg-gpu-xxxxx"],
    "SubnetId": "subnet-public-xxxxx",
    "IamInstanceProfile": {"Name": "ZiggieGPURole"}
  }'
```

**When to Use**:
- Dev/test workloads
- Batch processing (can resume after interruption)
- Non-time-sensitive AI inference

**When NOT to Use**:
- Real-time user-facing API (unpredictable interruptions)
- Stateful workloads (unless you implement checkpointing)

#### Strategy 2: Auto-Shutdown During Idle Hours

```bash
# Use Lambda + EventBridge to auto-stop GPU instances at night

# Lambda function (Python)
import boto3
ec2 = boto3.client('ec2', region_name='eu-north-1')

def lambda_handler(event, context):
    # Stop instances tagged with AutoShutdown=true
    instances = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:AutoShutdown', 'Values': ['true']},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    instance_ids = [i['InstanceId'] for r in instances['Reservations'] for i in r['Instances']]
    if instance_ids:
        ec2.stop_instances(InstanceIds=instance_ids)
        return f"Stopped {len(instance_ids)} instances"
    return "No instances to stop"

# EventBridge rule: Run at 10 PM UTC daily
# Savings: 12 hours/day = 50% reduction = $188/month saved
```

#### Strategy 3: S3 Lifecycle Policies

```json
{
  "Rules": [
    {
      "Id": "ArchiveOldAssets",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "INTELLIGENT_TIERING"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER_INSTANT_RETRIEVAL"
        }
      ]
    }
  ]
}
```

**Savings**:
- Standard S3: $0.023/GB
- Intelligent Tiering: $0.023/GB (frequent) → $0.0125/GB (infrequent)
- Glacier Instant Retrieval: $0.004/GB
- **Result**: 80% reduction for cold data

#### Strategy 4: Reserved Instances (1-Year Commitment)

**If you commit to 1 year of g4dn.xlarge**:
- On-Demand: $376.56/month
- Reserved (1-year, no upfront): $226/month
- **Savings**: $150/month (40% reduction)

**Break-Even**: If you'll use GPU for 6+ months, Reserved is cheaper.

### 10.4 Free Tier Maximization Tips

| Tip | Savings | Implementation |
|-----|---------|----------------|
| **Use t3.micro for Bastion** | $3.80/month | Free tier eligible (750h) |
| **S3 Gateway Endpoint** | $50-200/month | Eliminates data transfer fees |
| **CloudWatch Free Tier** | $5-20/month | Stay under 10 custom metrics |
| **VPC Endpoint for Secrets** | $24.80/month | No NAT Gateway needed |
| **Elastic IP (attached)** | $3.60/month | Always keep attached to instance |
| **Route 53 Queries** | Free | Stay under 1M queries/month (easy) |

---

## 11. Implementation Checklist

### Phase 1: VPC Foundation (Day 1)

- [ ] Create VPC (10.0.0.0/16) in eu-north-1
- [ ] Enable DNS resolution and DNS hostnames
- [ ] Create public subnet (10.0.1.0/24) in eu-north-1a
- [ ] Create private subnet (10.0.10.0/24) in eu-north-1b
- [ ] Create and attach Internet Gateway
- [ ] Create public route table with default route to IGW
- [ ] Associate public subnet with public route table
- [ ] Tag all resources (Name, Environment=production)

### Phase 2: Security Groups (Day 1)

- [ ] Create GPU Security Group
  - [ ] Inbound: SSH from Bastion SG
  - [ ] Inbound: ComfyUI API (8188) from VPS IP
  - [ ] Inbound: HTTPS (443) from VPS IP
  - [ ] Outbound: HTTPS (443) to 0.0.0.0/0
- [ ] Create Bastion Security Group
  - [ ] Inbound: SSH (22) from VPS IP
  - [ ] Outbound: SSH (22) to VPC CIDR
- [ ] Create VPC Endpoint Security Group
  - [ ] Inbound: HTTPS (443) from GPU SG
  - [ ] Inbound: HTTPS (443) from VPS IP

### Phase 3: VPC Endpoints (Day 1)

- [ ] Create S3 Gateway Endpoint
  - [ ] Associate with public and private route tables
  - [ ] Verify route added to route tables
- [ ] Create Secrets Manager Interface Endpoint
  - [ ] Deploy in public subnet
  - [ ] Enable private DNS
  - [ ] Attach VPC Endpoint Security Group
  - [ ] Test connectivity from VPS

### Phase 4: Network ACLs (Day 2)

- [ ] Create custom NACL for public subnet
  - [ ] Inbound: SSH, ComfyUI API, HTTPS from VPS
  - [ ] Inbound: Ephemeral ports (1024-65535)
  - [ ] Outbound: HTTPS, HTTP, ephemeral ports
- [ ] Associate NACL with public subnet
- [ ] Test connectivity (should match Security Group rules)

### Phase 5: Bastion Host (Day 2)

- [ ] Generate SSH key pair (ziggie-bastion-key)
- [ ] Create IAM role (ZiggieBastionRole) with CloudWatch Logs permissions
- [ ] Launch t3.nano instance with hardening user data
- [ ] Attach Elastic IP (optional, use public IP to save cost)
- [ ] Configure fail2ban and CloudWatch Logs agent
- [ ] Test SSH from VPS to bastion
- [ ] Add SSH config on VPS for ProxyJump pattern

### Phase 6: GPU Instance (Day 3)

- [ ] Generate SSH key pair (ziggie-gpu-key)
- [ ] Create IAM role (ZiggieGPURole) with S3, Secrets Manager permissions
- [ ] Launch g4dn.xlarge (or t3.large for testing)
- [ ] Attach GPU Security Group
- [ ] Install NVIDIA drivers, Docker, ComfyUI
- [ ] Test SSH from VPS → Bastion → GPU
- [ ] Test ComfyUI API access from VPS

### Phase 7: S3 and Secrets Manager (Day 3)

- [ ] Create S3 bucket (ziggie-comfyui-assets)
  - [ ] Enable versioning
  - [ ] Enable encryption (AES-256)
  - [ ] Add bucket policy (VPC endpoint + VPS IP)
- [ ] Create secrets in Secrets Manager
  - [ ] ComfyUI API key
  - [ ] S3 credentials (if using IAM user)
- [ ] Test S3 access from GPU instance (via VPC endpoint)
- [ ] Test S3 access from VPS (via public internet)

### Phase 8: DNS and SSL (Day 4)

- [ ] Create Route 53 hosted zone (aws.ziggie.cloud)
- [ ] Add NS records in Hostinger DNS for delegation
- [ ] Create A record for comfyui.aws.ziggie.cloud → GPU Elastic IP
- [ ] Request ACM certificate for *.aws.ziggie.cloud
- [ ] Validate ACM certificate via DNS
- [ ] Configure Nginx on VPS for SSL termination (Let's Encrypt)
- [ ] Test HTTPS access to ziggie.cloud
- [ ] Test DNS resolution for comfyui.aws.ziggie.cloud

### Phase 9: Monitoring and Alerts (Day 5)

- [ ] Create CloudWatch Log Groups
  - [ ] /aws/ec2/ziggie-bastion (SSH logs)
  - [ ] /aws/ec2/ziggie-gpu (ComfyUI logs)
- [ ] Create CloudWatch Alarms
  - [ ] GPU CPU > 90% for 5 minutes
  - [ ] Bastion failed SSH attempts > 10/hour
  - [ ] S3 bucket size > 100GB
- [ ] Create SNS topic for alerts
- [ ] Subscribe email to SNS topic
- [ ] Test alarm by triggering SSH failures

### Phase 10: Cost Optimization (Day 5)

- [ ] Enable S3 Intelligent Tiering
- [ ] Create S3 Lifecycle policy (30 days → Glacier)
- [ ] Tag all resources with cost allocation tags
  - [ ] Project=Ziggie
  - [ ] Environment=Production
  - [ ] Owner=Craig
- [ ] Enable AWS Cost Explorer
- [ ] Create monthly budget ($200/month alert)
- [ ] Review and remove unused Elastic IPs
- [ ] Consider Reserved Instance for GPU (if 1-year commitment)

### Phase 11: Documentation and Handoff (Day 6)

- [ ] Document all VPC resources (VPC ID, subnet IDs, SG IDs)
- [ ] Document DNS configuration (nameservers, A records)
- [ ] Document SSH key locations and bastion access
- [ ] Document IAM roles and policies
- [ ] Create runbook for common operations
  - [ ] Start/stop GPU instance
  - [ ] SSH to GPU via bastion
  - [ ] Upload files to S3
  - [ ] Rotate secrets
- [ ] Create disaster recovery plan
  - [ ] S3 bucket snapshots
  - [ ] AMI creation for GPU instance
  - [ ] DNS failover configuration

---

## Summary

### Key Decisions Made

1. **Public Endpoints + Security Groups** instead of VPN → **$36-43/month savings**
2. **S3 Gateway Endpoint** (free) → **$50-200/month data transfer savings**
3. **Secrets Manager VPC Endpoint** ($7.20/month) → **$24.80/month NAT Gateway savings**
4. **Hybrid DNS** (Hostinger + Route 53) → **Flexibility + cost optimization**
5. **Bastion Host** (t3.nano) → **Secure SSH access ($3.80/month)**
6. **Spot Instances** for GPU → **70% savings ($113 vs $377/month)**

### Total Monthly Cost Estimate

**Optimized Configuration**:
- GPU g4dn.xlarge (spot): $112.97
- Bastion t3.nano: $3.80
- S3 (100GB): $2.30
- VPC Endpoint (Secrets Manager): $7.20
- Secrets Manager (5 secrets): $2.00
- Route 53 (1 zone): $0.60
- CloudWatch Logs (10GB): $5.00
- **Total: $133.87/month**

**Free Tier Eligible** (first 12 months):
- Bastion: Free (750h t3.micro)
- S3: 5GB free
- Data Transfer: 100GB/month free
- CloudWatch: 5GB logs free
- **Estimated savings: $15-20/month**

### Security Posture

```
Defense-in-Depth (6 Layers):
1. Network Layer: Security Groups (IP whitelist)
2. Transport Layer: TLS 1.3 encryption
3. Application Layer: AWS Signature v4 authentication
4. Identity Layer: IAM roles with least privilege
5. Data Layer: S3 encryption at rest (AES-256)
6. Monitoring Layer: CloudWatch Logs + fail2ban
```

### Next Steps

1. Implement Phase 1-3 (VPC, Security Groups, VPC Endpoints) - **Day 1**
2. Deploy Bastion Host and test SSH access - **Day 2**
3. Deploy GPU instance and ComfyUI - **Day 3**
4. Configure DNS, SSL, and monitoring - **Day 4-5**
5. Optimize costs and document - **Day 6**

---

## Additional Resources

### AWS Documentation

- [VPC User Guide](https://docs.aws.amazon.com/vpc/latest/userguide/)
- [Security Group Rules](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html)
- [VPC Endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints.html)
- [AWS Certificate Manager](https://docs.aws.amazon.com/acm/latest/userguide/)
- [Route 53 Developer Guide](https://docs.aws.amazon.com/route53/latest/developerguide/)

### Security Best Practices

- [AWS Security Best Practices](https://aws.amazon.com/architecture/security-identity-compliance/)
- [CIS AWS Foundations Benchmark](https://www.cisecurity.org/benchmark/amazon_web_services)
- [OWASP Cloud Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cloud_Security_Cheat_Sheet.html)

### Cost Optimization

- [AWS Cost Optimization Pillar](https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/welcome.html)
- [AWS Pricing Calculator](https://calculator.aws/#/)
- [AWS Free Tier](https://aws.amazon.com/free/)

---

**Document Version**: 1.0
**Last Updated**: 2025-12-23
**Maintained By**: Claude (AI Infrastructure Research)
**Review Cycle**: Monthly or when AWS updates major services
