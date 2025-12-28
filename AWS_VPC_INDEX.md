# AWS VPC Networking for Ziggie Cloud - Index

> **Complete Documentation Package for Hybrid VPS + AWS Infrastructure**
> **Last Updated**: 2025-12-23

---

## Documentation Overview

This package provides comprehensive guidance for integrating AWS services (GPU compute, S3 storage, Secrets Manager) with your existing Hostinger VPS infrastructure at 82.25.112.73.

### Document Structure

```
AWS VPC Documentation Package
├── AWS_VPC_NETWORKING_BEST_PRACTICES.md (Primary Reference - 1,200 lines)
│   └── Comprehensive architecture, design decisions, and best practices
├── AWS_VPC_QUICK_REFERENCE.md (Quick Commands - 400 lines)
│   └── Copy-paste commands and troubleshooting guide
├── scripts/aws-vpc-setup.sh (Automation Script - 500 lines)
│   └── Automated deployment script for VPC infrastructure
└── AWS_VPC_INDEX.md (This file)
    └── Navigation and quick start guide
```

---

## Quick Navigation

| Need | Document | Section |
|------|----------|---------|
| **Understand Architecture** | [Best Practices](./AWS_VPC_NETWORKING_BEST_PRACTICES.md) | Section 1 - Architecture Overview |
| **Make VPN Decision** | [Best Practices](./AWS_VPC_NETWORKING_BEST_PRACTICES.md) | Section 2 - VPN vs Public Endpoints |
| **Configure Security** | [Best Practices](./AWS_VPC_NETWORKING_BEST_PRACTICES.md) | Section 4 - Security Groups |
| **Reduce Costs** | [Best Practices](./AWS_VPC_NETWORKING_BEST_PRACTICES.md) | Section 5 - VPC Endpoints<br>Section 10 - Cost Analysis |
| **Deploy VPC** | [Quick Reference](./AWS_VPC_QUICK_REFERENCE.md) | Section 1 - VPC Setup |
| **Setup Bastion** | [Quick Reference](./AWS_VPC_QUICK_REFERENCE.md) | Section 4 - Bastion Host |
| **Automate Deployment** | [scripts/aws-vpc-setup.sh](./scripts/aws-vpc-setup.sh) | Run: `./aws-vpc-setup.sh all` |
| **Troubleshoot Issues** | [Quick Reference](./AWS_VPC_QUICK_REFERENCE.md) | Section 10 - Troubleshooting |
| **Configure DNS** | [Best Practices](./AWS_VPC_NETWORKING_BEST_PRACTICES.md) | Section 7 - DNS Configuration |
| **Manage SSL Certificates** | [Best Practices](./AWS_VPC_NETWORKING_BEST_PRACTICES.md) | Section 8 - TLS/SSL Management |

---

## Quick Start (5 Minutes to Production)

### Step 1: Review Architecture Decision

**Key Decision**: Use **Public Endpoints + Security Groups** instead of VPN

**Savings**: $36-43/month
**Security**: Equivalent to VPN (TLS 1.3 + IAM + IP whitelisting)

Read: [Section 2 - VPN vs Public Endpoints](./AWS_VPC_NETWORKING_BEST_PRACTICES.md#2-vpn-vs-public-endpoints-decision-matrix)

### Step 2: Deploy VPC Infrastructure (Automated)

```bash
# Clone the script
cd /path/to/ziggie
chmod +x scripts/aws-vpc-setup.sh

# Configure AWS CLI (if not done)
aws configure
# AWS Access Key ID: YOUR_KEY
# AWS Secret Access Key: YOUR_SECRET
# Default region: eu-north-1
# Default output format: json

# Deploy all infrastructure
./scripts/aws-vpc-setup.sh all

# This creates:
# - VPC (10.0.0.0/16)
# - Public subnet (10.0.1.0/24)
# - Private subnet (10.0.10.0/24)
# - Internet Gateway
# - Security Groups (GPU, Bastion, VPC Endpoints)
# - VPC Endpoints (S3 FREE, Secrets Manager $7.20/month)
# - Bastion host (t3.nano)
```

**Duration**: 5-7 minutes
**Cost**: $0 (within free tier for first year)

### Step 3: Verify Deployment

```bash
# Check state file
cat ~/.aws-ziggie-state.json

# SSH to bastion
ssh -i ~/.ssh/ziggie-bastion-key.pem ubuntu@BASTION_IP

# If successful, infrastructure is ready!
```

### Step 4: Deploy GPU Instance (Manual)

```bash
# See: Quick Reference Section 5
# Or run: ./scripts/aws-vpc-setup.sh gpu (coming soon)
```

---

## Architecture Summary

### Current State (VPS Only)

```
Hostinger VPS (82.25.112.73)
├── Nginx (reverse proxy)
├── Control Center Frontend
├── Knowledge Base API
├── Sim Studio Backend
└── Domain: ziggie.cloud
```

### Target State (Hybrid VPS + AWS)

```
┌─────────────────────────────────────────────────────────┐
│ Hostinger VPS (82.25.112.73)                            │
│  - Nginx (web server, SSL termination)                  │
│  - Control Center Frontend                              │
│  - Knowledge Base API                                   │
│  - Sim Studio Backend                                   │
│  - ComfyUI Client (sends requests to AWS)               │
└─────────────────────────────────────────────────────────┘
           │ HTTPS (TLS 1.3)
           ▼
┌─────────────────────────────────────────────────────────┐
│ AWS VPC (10.0.0.0/16) - EU-North-1 Stockholm            │
│                                                          │
│  Public Subnet (10.0.1.0/24)                            │
│  ├── GPU EC2 (g4dn.xlarge) - ComfyUI API                │
│  ├── Bastion Host (t3.nano) - SSH access                │
│  └── VPC Endpoints (S3, Secrets Manager)                │
│                                                          │
│  S3 Buckets                                             │
│  ├── ziggie-comfyui-assets (AI-generated assets)        │
│  └── ziggie-game-models (game asset storage)            │
│                                                          │
│  Secrets Manager                                        │
│  ├── ComfyUI API keys                                   │
│  ├── S3 credentials                                     │
│  └── Database credentials (future)                      │
└─────────────────────────────────────────────────────────┘
```

---

## Key Decisions & Rationale

### 1. Public Endpoints vs VPN

**Decision**: Public endpoints with Security Groups
**Savings**: $36-43/month (no VPN gateway charges)
**Security**: 6 layers of defense-in-depth
**Details**: [Section 2](./AWS_VPC_NETWORKING_BEST_PRACTICES.md#2-vpn-vs-public-endpoints-decision-matrix)

### 2. VPC Endpoints

**Decision**: Deploy S3 Gateway (free) + Secrets Manager Interface ($7.20/month)
**Savings**: $50-200/month (data transfer) + $24.80/month (no NAT Gateway)
**Details**: [Section 5](./AWS_VPC_NETWORKING_BEST_PRACTICES.md#5-vpc-endpoints-cost-optimization)

### 3. Bastion Host

**Decision**: t3.nano bastion host ($3.80/month, free tier eligible)
**Alternative**: AWS Systems Manager Session Manager (free, more complex)
**Details**: [Section 9](./AWS_VPC_NETWORKING_BEST_PRACTICES.md#9-bastion-host-setup)

### 4. DNS Strategy

**Decision**: Hybrid - Hostinger DNS for main domain, Route 53 for AWS subdomain
**Cost**: $0.60/month (Route 53 hosted zone)
**Details**: [Section 7](./AWS_VPC_NETWORKING_BEST_PRACTICES.md#7-dns-configuration)

### 5. GPU Instance Pricing

**Decision**: Spot instances (70% savings) for non-critical workloads
**Cost**: $112.97/month (spot) vs $376.56/month (on-demand)
**Details**: [Section 10.3](./AWS_VPC_NETWORKING_BEST_PRACTICES.md#103-cost-optimization-strategies)

---

## Security Architecture (6 Layers)

```
Layer 1: Network Layer
  └── Security Groups (IP whitelist to VPS: 82.25.112.73/32)

Layer 2: Transport Layer
  └── TLS 1.3 encryption (all HTTPS traffic)

Layer 3: Application Layer
  └── AWS Signature v4 authentication (S3, Secrets Manager)

Layer 4: Identity Layer
  └── IAM roles with least privilege (no hardcoded credentials)

Layer 5: Data Layer
  └── S3 encryption at rest (AES-256), Secrets Manager encryption

Layer 6: Monitoring Layer
  └── CloudWatch Logs + fail2ban (SSH brute force protection)
```

**Result**: Enterprise-grade security without VPN overhead

---

## Cost Breakdown (Monthly)

### Optimized Configuration

| Service | Configuration | Cost | Notes |
|---------|---------------|------|-------|
| **GPU Instance** | g4dn.xlarge (spot) | $112.97 | 70% savings vs on-demand |
| **Bastion Host** | t3.nano | $3.80 | Free tier eligible (first 12 months) |
| **S3 Storage** | 100GB | $2.30 | 5GB free tier |
| **VPC Endpoint (S3)** | Gateway | $0.00 | Always FREE |
| **VPC Endpoint (Secrets)** | Interface | $7.20 | Saves $25/month (no NAT) |
| **Secrets Manager** | 5 secrets | $2.00 | $0.40 per secret |
| **Route 53** | 1 hosted zone | $0.60 | + $0.40/1M queries |
| **CloudWatch Logs** | 10GB | $5.00 | 5GB free tier |
| **Total** | | **$133.87** | **$15-20 less with free tier** |

### Cost Optimization Opportunities

1. **Auto-shutdown GPU at night**: Save 50% ($56/month) if only needed 12 hours/day
2. **Reserved Instance (1-year)**: Save 40% ($150/month) if committed usage
3. **S3 Intelligent Tiering**: Save 80% on cold data (30+ days old)
4. **Systems Manager over Bastion**: Save $3.80/month (but more complex)

**Details**: [Section 10](./AWS_VPC_NETWORKING_BEST_PRACTICES.md#10-cost-analysis--free-tier)

---

## Implementation Phases

### Phase 1: Foundation (Day 1) - AUTOMATED

- [x] Create VPC (10.0.0.0/16)
- [x] Create subnets (public, private)
- [x] Create Internet Gateway
- [x] Configure route tables
- [x] Create Security Groups
- [x] Deploy VPC Endpoints

**Script**: `./scripts/aws-vpc-setup.sh all`

### Phase 2: Bastion Access (Day 1) - AUTOMATED

- [x] Launch bastion host
- [x] Configure fail2ban
- [x] Setup SSH keys
- [x] Test SSH from VPS

**Script**: `./scripts/aws-vpc-setup.sh bastion`

### Phase 3: GPU Deployment (Day 2) - MANUAL

- [ ] Create IAM role for GPU instance
- [ ] Launch g4dn.xlarge (spot or on-demand)
- [ ] Install NVIDIA drivers
- [ ] Deploy ComfyUI
- [ ] Test API from VPS

**Guide**: [Quick Reference Section 5](./AWS_VPC_QUICK_REFERENCE.md#5-gpu-instance)

### Phase 4: Storage Setup (Day 2) - MANUAL

- [ ] Create S3 bucket (ziggie-comfyui-assets)
- [ ] Configure bucket policy (VPC endpoint + VPS access)
- [ ] Enable versioning and encryption
- [ ] Test upload from VPS and GPU instance

**Guide**: [Quick Reference Section 6](./AWS_VPC_QUICK_REFERENCE.md#6-s3-bucket)

### Phase 5: DNS & SSL (Day 3) - MANUAL

- [ ] Create Route 53 hosted zone (aws.ziggie.cloud)
- [ ] Delegate subdomain from Hostinger DNS
- [ ] Create A record for GPU instance
- [ ] Request ACM certificate
- [ ] Configure Let's Encrypt on VPS

**Guide**: [Quick Reference Section 7-8](./AWS_VPC_QUICK_REFERENCE.md#7-dns-setup)

### Phase 6: Monitoring (Day 3) - MANUAL

- [ ] Create CloudWatch Log Groups
- [ ] Configure CloudWatch alarms
- [ ] Setup SNS notifications
- [ ] Enable Cost Explorer
- [ ] Create monthly budget

**Guide**: [Best Practices Section 11](./AWS_VPC_NETWORKING_BEST_PRACTICES.md#phase-9-monitoring-and-alerts-day-5)

---

## Common Operations

### SSH to GPU Instance

```bash
# From VPS
ssh ziggie-gpu

# This uses ProxyJump through bastion automatically
# (After SSH config is setup, see Quick Reference Section 4)
```

### Upload File to S3

```bash
# From VPS
aws s3 cp my-file.png s3://ziggie-comfyui-assets/images/

# From GPU instance (uses VPC endpoint, no data transfer charges)
aws s3 cp /tmp/generated-image.png s3://ziggie-comfyui-assets/outputs/
```

### Access Secret from GPU Instance

```bash
# From GPU instance
aws secretsmanager get-secret-value \
  --secret-id comfyui-api-key \
  --query SecretString \
  --output text
```

### Check Monthly Costs

```bash
# From anywhere with AWS CLI configured
aws ce get-cost-and-usage \
  --time-period Start=2025-12-01,End=2025-12-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

---

## Troubleshooting

### Cannot SSH to Bastion

**Symptom**: `Connection timed out`

**Check**:
1. Is bastion running? `aws ec2 describe-instances --instance-ids BASTION_ID`
2. Is Security Group allowing SSH from VPS? Check port 22 from 82.25.112.73/32
3. Is VPS IP correct? (May change if VPS reboots)

**Fix**: [Quick Reference Section 10](./AWS_VPC_QUICK_REFERENCE.md#cannot-ssh-to-bastion)

### Cannot Access ComfyUI API

**Symptom**: `Connection refused` or `403 Forbidden`

**Check**:
1. Is GPU instance running?
2. Is Security Group allowing port 8188 from VPS?
3. Is ComfyUI service running? (SSH to GPU and check `systemctl status comfyui`)

**Fix**: [Quick Reference Section 10](./AWS_VPC_QUICK_REFERENCE.md#cannot-access-comfyui-api)

### High AWS Costs

**Symptom**: AWS bill > $200/month

**Check**:
1. Running instances: `aws ec2 describe-instances --filters "Name=instance-state-name,Values=running"`
2. Unattached Elastic IPs: `aws ec2 describe-addresses` (charged $3.60/month each)
3. NAT Gateway: Should be $0 (not deployed in this architecture)

**Fix**: [Quick Reference Section 10](./AWS_VPC_QUICK_REFERENCE.md#high-costs)

---

## Next Steps

### Immediate (Today)

1. **Review Architecture**: Read [Best Practices Section 1-2](./AWS_VPC_NETWORKING_BEST_PRACTICES.md#1-architecture-overview)
2. **Deploy VPC**: Run `./scripts/aws-vpc-setup.sh all`
3. **Test Bastion SSH**: Verify connectivity from VPS

### Short-Term (This Week)

1. **Deploy GPU Instance**: Follow [Quick Reference Section 5](./AWS_VPC_QUICK_REFERENCE.md#5-gpu-instance)
2. **Setup S3 Buckets**: Follow [Quick Reference Section 6](./AWS_VPC_QUICK_REFERENCE.md#6-s3-bucket)
3. **Configure DNS**: Follow [Quick Reference Section 7](./AWS_VPC_QUICK_REFERENCE.md#7-dns-setup)

### Medium-Term (This Month)

1. **Deploy ComfyUI**: Install on GPU instance
2. **Integrate with Sim Studio**: Update backend to use AWS ComfyUI API
3. **Monitoring**: Setup CloudWatch alarms and budgets
4. **Documentation**: Update deployment runbooks

### Long-Term (Next Quarter)

1. **Optimize Costs**: Consider Reserved Instances if usage is consistent
2. **High Availability**: Deploy GPU instances in multiple AZs
3. **Auto-Scaling**: Configure auto-scaling for GPU instances based on queue depth
4. **Disaster Recovery**: Implement backup and recovery procedures

---

## Support & Resources

### AWS Documentation

- [VPC User Guide](https://docs.aws.amazon.com/vpc/latest/userguide/)
- [Security Groups Reference](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html)
- [VPC Endpoints Guide](https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints.html)
- [EC2 Pricing](https://aws.amazon.com/ec2/pricing/)
- [S3 Pricing](https://aws.amazon.com/s3/pricing/)

### Cost Calculators

- [AWS Pricing Calculator](https://calculator.aws/#/)
- [EC2 Spot Instance Advisor](https://aws.amazon.com/ec2/spot/instance-advisor/)
- [AWS Free Tier Overview](https://aws.amazon.com/free/)

### Security Best Practices

- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [CIS AWS Foundations Benchmark](https://www.cisecurity.org/benchmark/amazon_web_services)
- [AWS Security Best Practices](https://aws.amazon.com/architecture/security-identity-compliance/)

---

## Document Maintenance

| Document | Last Updated | Next Review | Owner |
|----------|--------------|-------------|-------|
| AWS_VPC_NETWORKING_BEST_PRACTICES.md | 2025-12-23 | 2026-01-23 | Claude |
| AWS_VPC_QUICK_REFERENCE.md | 2025-12-23 | 2026-01-23 | Claude |
| scripts/aws-vpc-setup.sh | 2025-12-23 | 2026-01-23 | Claude |
| AWS_VPC_INDEX.md | 2025-12-23 | 2026-01-23 | Claude |

**Review Triggers**:
- AWS announces new VPC features
- Monthly cost exceeds budget by >20%
- Security incident or vulnerability disclosure
- Major infrastructure changes (new services, regions)

---

## Feedback & Questions

For questions or issues with this documentation:

1. **Technical Issues**: Check [Troubleshooting Section](./AWS_VPC_QUICK_REFERENCE.md#10-troubleshooting)
2. **Cost Concerns**: Review [Cost Analysis](./AWS_VPC_NETWORKING_BEST_PRACTICES.md#10-cost-analysis--free-tier)
3. **Security Questions**: Review [Security Architecture](#security-architecture-6-layers)
4. **Architecture Decisions**: Review [Decision Matrix](./AWS_VPC_NETWORKING_BEST_PRACTICES.md#2-vpn-vs-public-endpoints-decision-matrix)

---

**Index Version**: 1.0
**Documentation Package**: Complete
**Total Pages**: ~2,100 lines across 4 files
**Estimated Reading Time**: 2-3 hours (comprehensive), 30 minutes (quick start)
