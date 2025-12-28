# AWS GPU Auto-Shutdown Quick Reference

> **Quick access commands and configurations for GPU instance cost optimization**
> **Instance**: g4dn.xlarge in EU-North-1 Stockholm
> **Target**: <$50/month normal, <$150/month peak

---

## One-Line Cost Summary

```text
24/7 Running: $392/month
2 hours/day:  $40/month  (90% savings) ✓ UNDER BUDGET
4 hours/day:  $72/month  (82% savings) ✓ UNDER PEAK
8 hours/day:  $136/month (66% savings) ✓ UNDER PEAK
```

---

## Essential Commands

### Start GPU Instance
```bash
# Via AWS Lambda
aws lambda invoke \
  --function-name start-gpu-instance \
  --region eu-north-1 \
  output.json && cat output.json

# Direct EC2 command
aws ec2 start-instances --instance-ids i-xxxxxxxxxxxxx
```

### Stop GPU Instance
```bash
# Via AWS Lambda
aws lambda invoke \
  --function-name stop-gpu-instance \
  --region eu-north-1 \
  output.json && cat output.json

# Direct EC2 command
aws ec2 stop-instances --instance-ids i-xxxxxxxxxxxxx
```

### Check Instance Status
```bash
aws ec2 describe-instances --instance-ids i-xxxxxxxxxxxxx \
  --query 'Reservations[0].Instances[0].[State.Name,PublicIpAddress]' \
  --output text
```

### Check Running Hours (Current Month)
```bash
# Get cost and usage data
aws ce get-cost-and-usage \
  --time-period Start=$(date -u +%Y-%m-01),End=$(date -u +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost \
  --filter file://cost-filter.json
```

### Test Alarm Manually
```bash
# Force alarm to trigger
aws cloudwatch set-alarm-state \
  --alarm-name "GPU-Instance-Truly-Idle" \
  --state-value ALARM \
  --state-reason "Manual test"

# Reset alarm
aws cloudwatch set-alarm-state \
  --alarm-name "GPU-Instance-Truly-Idle" \
  --state-value OK \
  --state-reason "Test complete"
```

---

## Lambda Environment Variables

### start-gpu-instance
```bash
GPU_INSTANCE_ID=i-xxxxxxxxxxxxx
```

### stop-gpu-instance
```bash
GPU_INSTANCE_ID=i-xxxxxxxxxxxxx
GRACE_PERIOD_MINUTES=10
```

### check-comfyui-health
```bash
GPU_INSTANCE_ID=i-xxxxxxxxxxxxx
COMFYUI_PORT=8188
MAX_WAIT_SECONDS=300
```

---

## CloudWatch Alarm Thresholds

| Alarm | Metric | Threshold | Period | Actions |
|-------|--------|-----------|--------|---------|
| CPU-Idle | CPUUtilization | < 5% | 10 min | - |
| Network-Idle | NetworkOut | < 1 MB | 10 min | - |
| ComfyUI-Idle | QueueDepth | = 0 | 10 min | - |
| Truly-Idle | Composite AND | All above | - | Stop instance |

---

## n8n Workflow Skeleton

```javascript
// 1. Start GPU Instance
POST https://lambda.eu-north-1.amazonaws.com/2015-03-31/functions/start-gpu-instance/invocations
Auth: AWS IAM

// 2. Wait 30 seconds
Wait 30s

// 3. Check ComfyUI Health
POST https://lambda.eu-north-1.amazonaws.com/2015-03-31/functions/check-comfyui-health/invocations
Auth: AWS IAM

// 4. Generate Image (if healthy)
POST {{comfyui_url}}/prompt
Body: { "prompt": "..." }

// Instance auto-stops after 10 min idle (CloudWatch alarm)
```

---

## Emergency Procedures

### Instance Stuck Running (Wasting Money)
```bash
# 1. Check why alarm didn't trigger
aws cloudwatch describe-alarms --alarm-names "GPU-Instance-Truly-Idle"

# 2. Force stop immediately
aws ec2 stop-instances --instance-ids i-xxxxxxxxxxxxx

# 3. Check for issues
aws logs tail /aws/lambda/stop-gpu-instance --follow
```

### Instance Won't Start
```bash
# 1. Check Lambda logs
aws logs tail /aws/lambda/start-gpu-instance --follow

# 2. Verify instance exists and is stoppable
aws ec2 describe-instances --instance-ids i-xxxxxxxxxxxxx

# 3. Check IAM permissions
aws iam get-role --role-name lambda-ec2-control

# 4. Manual start as fallback
aws ec2 start-instances --instance-ids i-xxxxxxxxxxxxx
```

### Unexpected High Costs
```bash
# 1. Check current running instances
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" "Name=tag:AutoShutdown,Values=true" \
  --query 'Reservations[*].Instances[*].[InstanceId,LaunchTime,State.Name]'

# 2. Review costs this month
aws ce get-cost-and-usage \
  --time-period Start=$(date -u +%Y-%m-01),End=$(date -u +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost

# 3. Stop all GPU instances if needed
aws ec2 stop-instances --instance-ids i-xxxxxxxxxxxxx
```

---

## Cost Filter JSON

**File**: `cost-filter.json`
```json
{
  "Dimensions": {
    "Key": "INSTANCE_TYPE",
    "Values": ["g4dn.xlarge"]
  }
}
```

---

## IAM Trust Policy

**File**: `lambda-trust-policy.json`
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

---

## EC2 User Data (Auto-Start ComfyUI)

```bash
#!/bin/bash
# Install ComfyUI monitoring on first boot

# Install Python dependencies
pip3 install boto3 requests

# Copy monitoring script
cat > /opt/comfyui_monitor.py << 'EOF'
import boto3
import requests
import time
import os

cloudwatch = boto3.client('cloudwatch', region_name='eu-north-1')
INSTANCE_ID = os.environ.get('INSTANCE_ID')
COMFYUI_URL = "http://localhost:8188"

def get_queue_depth():
    try:
        response = requests.get(f"{COMFYUI_URL}/queue", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return len(data.get('queue_pending', [])) + len(data.get('queue_running', []))
    except:
        pass
    return 0

def put_metric(queue_depth):
    try:
        cloudwatch.put_metric_data(
            Namespace='ComfyUI',
            MetricData=[{
                'MetricName': 'QueueDepth',
                'Value': queue_depth,
                'Unit': 'Count',
                'Dimensions': [{'Name': 'InstanceId', 'Value': INSTANCE_ID}]
            }]
        )
    except Exception as e:
        print(f"Error: {e}")

while True:
    put_metric(get_queue_depth())
    time.sleep(60)
EOF

# Create systemd service
cat > /etc/systemd/system/comfyui-monitor.service << 'EOF'
[Unit]
Description=ComfyUI Queue Monitor
After=network.target

[Service]
Type=simple
User=ubuntu
Environment="INSTANCE_ID=$(ec2-metadata --instance-id | cut -d ' ' -f 2)"
ExecStart=/usr/bin/python3 /opt/comfyui_monitor.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
systemctl enable comfyui-monitor.service
systemctl start comfyui-monitor.service
```

---

## Monitoring Dashboard

### CloudWatch Metrics to Track

```bash
# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name GPU-Instance-Costs \
  --dashboard-body file://dashboard-config.json
```

**Dashboard Widgets**:
1. EC2 Running Hours (current month)
2. Estimated Cost (running hours × $0.526)
3. Lambda Invocation Count
4. CloudWatch Alarm State
5. ComfyUI Queue Depth

---

## Adjustment Commands

### Change Idle Timeout (10 min → 5 min)
```bash
# Update Lambda environment
aws lambda update-function-configuration \
  --function-name stop-gpu-instance \
  --environment Variables="{GPU_INSTANCE_ID=i-xxxxxxxxxxxxx,GRACE_PERIOD_MINUTES=5}"

# Update CloudWatch alarm periods
aws cloudwatch put-metric-alarm \
  --alarm-name "GPU-Instance-CPU-Idle" \
  --period 150 \
  --evaluation-periods 2  # 5 min total
```

### Add Email Notifications
```bash
# Create SNS topic
aws sns create-topic --name gpu-instance-alerts

# Subscribe email
aws sns subscribe \
  --topic-arn arn:aws:sns:eu-north-1:ACCOUNT_ID:gpu-instance-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com

# Add to alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "GPU-Instance-Truly-Idle" \
  --alarm-actions \
    "arn:aws:lambda:eu-north-1:ACCOUNT_ID:function:stop-gpu-instance" \
    "arn:aws:sns:eu-north-1:ACCOUNT_ID:gpu-instance-alerts"
```

---

## Testing Checklist

```bash
# 1. Start instance via Lambda
aws lambda invoke --function-name start-gpu-instance test1.json
cat test1.json | jq .

# 2. Verify instance running
aws ec2 describe-instances --instance-ids i-xxxxxxxxxxxxx \
  --query 'Reservations[0].Instances[0].State.Name'

# 3. Check ComfyUI health
aws lambda invoke --function-name check-comfyui-health test2.json
cat test2.json | jq .

# 4. Generate test image via ComfyUI API
curl -X POST http://INSTANCE_IP:8188/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test prompt"}'

# 5. Wait for idle (10 min)
sleep 600

# 6. Verify alarm triggered
aws cloudwatch describe-alarm-history \
  --alarm-name "GPU-Instance-Truly-Idle" \
  --max-records 5

# 7. Verify instance stopped
aws ec2 describe-instances --instance-ids i-xxxxxxxxxxxxx \
  --query 'Reservations[0].Instances[0].State.Name'
```

---

## Cost Tracking

### Weekly Cost Report
```bash
#!/bin/bash
# weekly_cost_report.sh

END_DATE=$(date -u +%Y-%m-%d)
START_DATE=$(date -u -d '7 days ago' +%Y-%m-%d)

echo "GPU Instance Costs: $START_DATE to $END_DATE"
echo "================================================"

aws ce get-cost-and-usage \
  --time-period Start=$START_DATE,End=$END_DATE \
  --granularity DAILY \
  --metrics BlendedCost \
  --filter file://cost-filter.json \
  --output table
```

### Monthly Budget Check
```bash
#!/bin/bash
# check_budget.sh

MONTH_START=$(date -u +%Y-%m-01)
TODAY=$(date -u +%Y-%m-%d)

COST=$(aws ce get-cost-and-usage \
  --time-period Start=$MONTH_START,End=$TODAY \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --filter file://cost-filter.json \
  --query 'ResultsByTime[0].Total.BlendedCost.Amount' \
  --output text)

echo "Current month GPU costs: \$$COST"

if (( $(echo "$COST > 150" | bc -l) )); then
  echo "⚠️  OVER PEAK BUDGET ($150)"
elif (( $(echo "$COST > 50" | bc -l) )); then
  echo "⚠️  Over normal budget ($50), under peak ($150)"
else
  echo "✓ Under normal budget ($50)"
fi
```

---

## Troubleshooting

### Lambda Logs
```bash
# View recent logs
aws logs tail /aws/lambda/start-gpu-instance --follow
aws logs tail /aws/lambda/stop-gpu-instance --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/stop-gpu-instance \
  --filter-pattern "ERROR"
```

### CloudWatch Metric Data
```bash
# Check if ComfyUI metrics are being published
aws cloudwatch get-metric-statistics \
  --namespace ComfyUI \
  --metric-name QueueDepth \
  --dimensions Name=InstanceId,Value=i-xxxxxxxxxxxxx \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Maximum
```

### Verify IAM Permissions
```bash
# Test Lambda can describe instances
aws lambda invoke \
  --function-name start-gpu-instance \
  --log-type Tail \
  test.json \
  --query 'LogResult' \
  --output text | base64 -d
```

---

## Key Files Reference

| File | Location | Purpose |
|------|----------|---------|
| `lambda_start_gpu_instance.py` | Lambda function | Start EC2 instance |
| `lambda_stop_gpu_instance.py` | Lambda function | Stop EC2 instance |
| `lambda_check_comfyui_health.py` | Lambda function | Health check |
| `comfyui_monitor.py` | `/opt/` on EC2 | Custom metrics |
| `setup_cloudwatch_alarms.sh` | Local script | Create alarms |
| `deploy_gpu_autoshutdown.sh` | Local script | Full deployment |
| `cost-filter.json` | Local config | Cost queries |
| `lambda-trust-policy.json` | Local config | IAM role |

---

## Support Resources

- **Full Guide**: `AWS_LAMBDA_GPU_AUTO_SHUTDOWN_GUIDE.md`
- **AWS Lambda Docs**: https://docs.aws.amazon.com/lambda/
- **AWS CloudWatch Docs**: https://docs.aws.amazon.com/cloudwatch/
- **AWS Cost Explorer**: https://console.aws.amazon.com/cost-management/home

---

**Last Updated**: 2025-12-23
**Region**: EU-North-1 Stockholm
**Instance Type**: g4dn.xlarge ($0.526/hour)
