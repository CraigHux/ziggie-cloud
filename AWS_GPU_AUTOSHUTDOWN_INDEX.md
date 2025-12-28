# AWS GPU Auto-Shutdown - Complete Index

> **Research Date**: 2025-12-23
> **Objective**: Minimize AWS g4dn.xlarge GPU costs through Lambda-based auto-shutdown
> **Result**: 60-90% cost savings with production-ready implementation

---

## Quick Navigation

| What You Need | Start Here |
|---------------|------------|
| **Overview & Decisions** | `AWS_GPU_COST_OPTIMIZATION_SUMMARY.md` |
| **Implementation Steps** | `AWS_LAMBDA_GPU_AUTO_SHUTDOWN_GUIDE.md` |
| **Quick Commands** | `AWS_GPU_AUTOSHUTDOWN_QUICK_REFERENCE.md` |
| **Production Scripts** | `scripts/aws-gpu-autoshutdown/README.md` |
| **This Index** | `AWS_GPU_AUTOSHUTDOWN_INDEX.md` |

---

## Document Hierarchy

### Level 1: Executive Summary (Start Here)

**File**: `AWS_GPU_COST_OPTIMIZATION_SUMMARY.md` (12 pages)

**Contents**:
- Cost savings analysis ($392 → $40-136/month)
- Architecture diagram
- Implementation phases
- Risk mitigation
- Key code snippets
- Next steps

**Audience**: Management, decision-makers

### Level 2: Complete Implementation Guide

**File**: `AWS_LAMBDA_GPU_AUTO_SHUTDOWN_GUIDE.md` (50+ pages)

**Contents**:
1. Architecture overview
2. Lambda function patterns (Python code)
3. Idle detection strategies (multi-metric)
4. CloudWatch alarm configurations
5. n8n integration patterns
6. Cost optimization calculations
7. Implementation checklist
8. Best practices

**Audience**: Engineers implementing the solution

### Level 3: Quick Reference

**File**: `AWS_GPU_AUTOSHUTDOWN_QUICK_REFERENCE.md` (8 pages)

**Contents**:
- One-line cost summary
- Essential commands (start/stop/test)
- Environment variables
- Alarm thresholds
- Emergency procedures
- Troubleshooting
- Cost tracking

**Audience**: Operators, DevOps

### Level 4: Production Scripts

**Location**: `scripts/aws-gpu-autoshutdown/`

**Files**:
- `lambda_start_gpu_instance.py` - Start EC2 instance
- `lambda_stop_gpu_instance.py` - Stop EC2 instance
- `lambda_check_comfyui_health.py` - Health check
- `comfyui_monitor.py` - Custom metrics
- `comfyui-monitor.service` - Systemd service
- `deploy_lambda_functions.sh` - Deploy all Lambda
- `setup_cloudwatch_alarms.sh` - Create alarms
- `README.md` - Script documentation

**Audience**: Engineers deploying the solution

### Level 5: Deliverables Checklist

**File**: `AWS_GPU_AUTOSHUTDOWN_DELIVERABLES.md` (3 pages)

**Contents**:
- Complete file list
- Research findings summary
- Implementation phases
- Quick start commands
- Support resources

**Audience**: Project managers, stakeholders

---

## Key Findings Summary

### Cost Savings

```text
Current State (24/7):    $392/month  ❌ Exceeds budget
With Auto-Shutdown:
  - Aggressive (2h/day): $40/month   ✓ Under $50
  - Moderate (4h/day):   $72/month   ✓ Under $150
  - Peak (8h/day):       $136/month  ✓ Under $150

Savings: 60-90% reduction
```

### Technology Stack

- **AWS Lambda**: Python 3.11 functions (3 total)
- **CloudWatch**: Composite alarm (CPU + Network + Custom)
- **EC2**: g4dn.xlarge with NVIDIA T4 GPU
- **Custom Metric**: ComfyUI queue depth monitor
- **Integration**: n8n workflows on Hostinger VPS

### Idle Detection Strategy

**Multi-metric composite alarm** (ALL must be true):
1. CPU < 5% for 10 minutes
2. Network < 1MB for 10 minutes
3. ComfyUI queue = 0 for 10 minutes

**Result**: Reliable shutdown without premature stops

---

## Implementation Roadmap

### Phase 1: Lambda Functions (1-2 hours)
```bash
cd c:/Ziggie/scripts/aws-gpu-autoshutdown
./deploy_lambda_functions.sh
```

**Deliverable**: 3 Lambda functions deployed

### Phase 2: EC2 Setup (2-3 hours)
```bash
# Launch instance
aws ec2 run-instances --instance-type g4dn.xlarge ...

# Install ComfyUI
ssh ubuntu@INSTANCE_IP
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI && pip install -r requirements.txt

# Install monitoring
scp comfyui_monitor.py ubuntu@INSTANCE_IP:/tmp/
```

**Deliverable**: EC2 instance with ComfyUI and monitoring

### Phase 3: CloudWatch Alarms (1 hour)
```bash
./setup_cloudwatch_alarms.sh
```

**Deliverable**: 4 CloudWatch alarms configured

### Phase 4: n8n Integration (2-3 hours)
```javascript
// n8n workflow
HTTP → Lambda Start → Wait → Health Check → ComfyUI → Store Result
```

**Deliverable**: End-to-end automated image generation

### Phase 5: Monitoring (Ongoing)
```bash
# Weekly cost report
aws ce get-cost-and-usage --time-period ...
```

**Deliverable**: Cost tracking under budget

---

## File Structure

```text
c:/Ziggie/
├── AWS_GPU_AUTOSHUTDOWN_INDEX.md (this file)
├── AWS_GPU_COST_OPTIMIZATION_SUMMARY.md
├── AWS_LAMBDA_GPU_AUTO_SHUTDOWN_GUIDE.md
├── AWS_GPU_AUTOSHUTDOWN_QUICK_REFERENCE.md
├── AWS_GPU_AUTOSHUTDOWN_DELIVERABLES.md
│
└── scripts/
    └── aws-gpu-autoshutdown/
        ├── README.md
        ├── lambda_start_gpu_instance.py
        ├── lambda_stop_gpu_instance.py
        ├── lambda_check_comfyui_health.py
        ├── comfyui_monitor.py
        ├── comfyui-monitor.service
        ├── deploy_lambda_functions.sh
        └── setup_cloudwatch_alarms.sh
```

---

## Common Tasks

### Deploy Everything from Scratch

```bash
# 1. Configure variables
cd c:/Ziggie/scripts/aws-gpu-autoshutdown
nano deploy_lambda_functions.sh  # Set INSTANCE_ID and ACCOUNT_ID
nano setup_cloudwatch_alarms.sh  # Set INSTANCE_ID and ACCOUNT_ID

# 2. Deploy Lambda functions
./deploy_lambda_functions.sh

# 3. Create CloudWatch alarms
./setup_cloudwatch_alarms.sh

# 4. Install monitoring on EC2
scp comfyui_monitor.py ubuntu@INSTANCE_IP:/tmp/
scp comfyui-monitor.service ubuntu@INSTANCE_IP:/tmp/
ssh ubuntu@INSTANCE_IP
sudo mv /tmp/comfyui_monitor.py /opt/
sudo mv /tmp/comfyui-monitor.service /etc/systemd/system/
sudo systemctl enable comfyui-monitor && sudo systemctl start comfyui-monitor
```

### Test Auto-Shutdown

```bash
# Start instance
aws lambda invoke --function-name start-gpu-instance output.json

# Wait for idle (or force alarm)
aws cloudwatch set-alarm-state \
  --alarm-name "GPU-Instance-Truly-Idle" \
  --state-value ALARM \
  --state-reason "Test"

# Verify stopped
aws ec2 describe-instances --instance-ids i-xxxxxxxxxxxxx \
  --query 'Reservations[0].Instances[0].State.Name'
```

### Monitor Costs

```bash
# Current month cost
aws ce get-cost-and-usage \
  --time-period Start=$(date -u +%Y-%m-01),End=$(date -u +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost

# Expected: <$50 normal, <$150 peak
```

---

## Integration Points

### 1. n8n Workflow

**Trigger**: Image generation request
**Actions**:
1. Call Lambda: `start-gpu-instance`
2. Wait 30 seconds
3. Call Lambda: `check-comfyui-health`
4. HTTP POST to ComfyUI: `/prompt`
5. Store result

**Auto-shutdown**: CloudWatch alarm stops instance after 10 min idle

### 2. AWS Services

```text
n8n → Lambda (start) → EC2 (running) → CloudWatch (monitoring)
                                              ↓
                                         Alarm (idle)
                                              ↓
                                    Lambda (stop) → EC2 (stopped)
```

### 3. Cost Tracking

```text
CloudWatch Metrics → Cost Explorer → Budget Alerts → Email
```

---

## Troubleshooting Index

| Problem | Solution | Documentation |
|---------|----------|---------------|
| Instance won't start | Check Lambda logs | `AWS_GPU_AUTOSHUTDOWN_QUICK_REFERENCE.md` section "Emergency Procedures" |
| Instance won't stop | Check alarm state | `AWS_GPU_AUTOSHUTDOWN_QUICK_REFERENCE.md` section "Emergency Procedures" |
| Metrics not publishing | Check service status | `scripts/aws-gpu-autoshutdown/README.md` section "Troubleshooting" |
| High costs | Review running instances | `AWS_GPU_AUTOSHUTDOWN_QUICK_REFERENCE.md` section "Unexpected High Costs" |
| Lambda errors | View CloudWatch logs | `AWS_LAMBDA_GPU_AUTO_SHUTDOWN_GUIDE.md` section "Best Practices" |

---

## Support Resources

### Internal Documentation
- **Implementation**: `AWS_LAMBDA_GPU_AUTO_SHUTDOWN_GUIDE.md`
- **Quick Commands**: `AWS_GPU_AUTOSHUTDOWN_QUICK_REFERENCE.md`
- **Scripts**: `scripts/aws-gpu-autoshutdown/README.md`

### AWS Documentation
- **Lambda**: https://docs.aws.amazon.com/lambda/
- **CloudWatch**: https://docs.aws.amazon.com/cloudwatch/
- **EC2**: https://docs.aws.amazon.com/ec2/
- **Cost Management**: https://docs.aws.amazon.com/cost-management/

### Project Context
- **Region**: EU-North-1 Stockholm
- **Instance**: g4dn.xlarge ($0.526/hour)
- **Integration**: n8n on Hostinger VPS (82.25.112.73)
- **Budget**: <$50/month normal, <$150/month peak

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-23 | Initial research and implementation package |

---

## Next Steps

### Immediate (This Week)
1. [ ] Review `AWS_GPU_COST_OPTIMIZATION_SUMMARY.md` for overview
2. [ ] Configure AWS credentials for deployment
3. [ ] Deploy Lambda functions using `deploy_lambda_functions.sh`
4. [ ] Test manual start/stop

### Short-term (Next Week)
1. [ ] Launch EC2 instance
2. [ ] Install ComfyUI
3. [ ] Install monitoring script
4. [ ] Create CloudWatch alarms
5. [ ] Test auto-shutdown

### Long-term (Next Month)
1. [ ] Integrate with n8n workflows
2. [ ] Monitor first week of costs
3. [ ] Tune idle timeout if needed
4. [ ] Document lessons learned

---

**Status**: Ready for Implementation
**Expected Savings**: 60-90% cost reduction
**Risk Level**: Low (comprehensive safeguards)

---

*All code and configurations are production-ready, based on AWS best practices (2025).*
