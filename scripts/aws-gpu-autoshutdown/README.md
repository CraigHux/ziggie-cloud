# AWS GPU Auto-Shutdown Scripts

Complete deployment scripts for Lambda-based EC2 auto-shutdown system.

## Files Overview

| File | Purpose | Deployment |
|------|---------|------------|
| `lambda_start_gpu_instance.py` | Start EC2 instance | AWS Lambda |
| `lambda_stop_gpu_instance.py` | Stop EC2 instance | AWS Lambda |
| `lambda_check_comfyui_health.py` | Health check ComfyUI | AWS Lambda |
| `comfyui_monitor.py` | Publish queue metrics | EC2 instance |
| `comfyui-monitor.service` | Systemd service config | EC2 instance |
| `deploy_lambda_functions.sh` | Deploy all Lambda functions | Local |
| `setup_cloudwatch_alarms.sh` | Create CloudWatch alarms | Local |

## Quick Start

### Prerequisites

1. **AWS CLI configured** with credentials
2. **Python 3.x** installed locally
3. **EC2 g4dn.xlarge instance** launched in EU-North-1
4. **ComfyUI** installed on EC2 instance

### Step 1: Configure Variables

Edit the following files and replace placeholders:

**In `deploy_lambda_functions.sh`**:
```bash
INSTANCE_ID="i-xxxxxxxxxxxxx"  # Your EC2 instance ID
ACCOUNT_ID="xxxxxxxxxxxx"      # Your AWS account ID
```

**In `setup_cloudwatch_alarms.sh`**:
```bash
INSTANCE_ID="i-xxxxxxxxxxxxx"  # Your EC2 instance ID
ACCOUNT_ID="xxxxxxxxxxxx"      # Your AWS account ID
```

**In `comfyui-monitor.service`**:
```ini
Environment="INSTANCE_ID=i-xxxxxxxxxxxxx"
```

### Step 2: Deploy Lambda Functions

```bash
cd c:/Ziggie/scripts/aws-gpu-autoshutdown

# Make scripts executable
chmod +x deploy_lambda_functions.sh
chmod +x setup_cloudwatch_alarms.sh

# Deploy Lambda functions
./deploy_lambda_functions.sh
```

Expected output:
```
✓ IAM role ready
✓ start-gpu-instance deployed
✓ stop-gpu-instance deployed
✓ check-comfyui-health deployed
```

### Step 3: Create CloudWatch Alarms

```bash
./setup_cloudwatch_alarms.sh
```

Expected output:
```
✓ CPU idle alarm created
✓ Network idle alarm created
✓ ComfyUI queue idle alarm created
✓ Composite alarm created with Lambda action
```

### Step 4: Install Monitoring Script on EC2

SSH into your EC2 instance:

```bash
# Copy files to EC2
scp comfyui_monitor.py ubuntu@YOUR_INSTANCE_IP:/tmp/
scp comfyui-monitor.service ubuntu@YOUR_INSTANCE_IP:/tmp/

# SSH into instance
ssh ubuntu@YOUR_INSTANCE_IP

# Install monitoring script
sudo mv /tmp/comfyui_monitor.py /opt/
sudo chmod +x /opt/comfyui_monitor.py

# Install systemd service
sudo mv /tmp/comfyui-monitor.service /etc/systemd/system/

# Edit service file with your instance ID
sudo nano /etc/systemd/system/comfyui-monitor.service
# Replace __REPLACE_WITH_INSTANCE_ID__ with your actual instance ID

# Install dependencies
sudo pip3 install boto3 requests

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable comfyui-monitor.service
sudo systemctl start comfyui-monitor.service

# Check status
sudo systemctl status comfyui-monitor.service

# View logs
sudo journalctl -u comfyui-monitor.service -f
```

Expected log output:
```
Starting ComfyUI queue depth monitor
Instance ID: i-xxxxxxxxxxxxx
ComfyUI URL: http://localhost:8188
[2025-12-23T...] Queue depth: 0 (pending=0, running=0)
[2025-12-23T...] Published queue depth metric: 0
```

### Step 5: Verify Metrics in CloudWatch

```bash
# Check if custom metric is publishing
aws cloudwatch get-metric-statistics \
  --namespace ComfyUI \
  --metric-name QueueDepth \
  --dimensions Name=InstanceId,Value=i-xxxxxxxxxxxxx \
  --start-time $(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Maximum \
  --region eu-north-1
```

Should return datapoints if monitoring is working.

### Step 6: Test Auto-Shutdown

```bash
# Test alarm trigger manually
aws cloudwatch set-alarm-state \
  --alarm-name "GPU-Instance-Truly-Idle" \
  --state-value ALARM \
  --state-reason "Manual test" \
  --region eu-north-1

# Check if instance is stopping (wait ~30 seconds)
aws ec2 describe-instances \
  --instance-ids i-xxxxxxxxxxxxx \
  --query 'Reservations[0].Instances[0].State.Name' \
  --output text
```

Expected: `stopping` or `stopped`

## Usage

### Start Instance (n8n or Manual)

```bash
aws lambda invoke \
  --function-name start-gpu-instance \
  --region eu-north-1 \
  output.json

cat output.json
```

Response:
```json
{
  "statusCode": 200,
  "body": {
    "message": "Instance started successfully",
    "public_ip": "13.48.xxx.xxx",
    "comfyui_url": "http://13.48.xxx.xxx:8188"
  }
}
```

### Check Health

```bash
aws lambda invoke \
  --function-name check-comfyui-health \
  --region eu-north-1 \
  output.json

cat output.json
```

### Manual Stop (Emergency)

```bash
# Direct EC2 stop (bypasses Lambda)
aws ec2 stop-instances --instance-ids i-xxxxxxxxxxxxx
```

## Monitoring

### View Lambda Logs

```bash
# Start function logs
aws logs tail /aws/lambda/start-gpu-instance --follow

# Stop function logs
aws logs tail /aws/lambda/stop-gpu-instance --follow

# Health check logs
aws logs tail /aws/lambda/check-comfyui-health --follow
```

### View Alarm Status

```bash
aws cloudwatch describe-alarms \
  --alarm-names "GPU-Instance-Truly-Idle" \
  --region eu-north-1
```

### Check Current Costs

```bash
aws ce get-cost-and-usage \
  --time-period Start=$(date -u +%Y-%m-01),End=$(date -u +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --region eu-north-1
```

## Troubleshooting

### Instance Won't Start

1. Check Lambda logs:
   ```bash
   aws logs tail /aws/lambda/start-gpu-instance --follow
   ```

2. Verify IAM permissions:
   ```bash
   aws iam get-role --role-name lambda-ec2-control
   ```

3. Try manual start:
   ```bash
   aws ec2 start-instances --instance-ids i-xxxxxxxxxxxxx
   ```

### Instance Won't Stop

1. Check alarm state:
   ```bash
   aws cloudwatch describe-alarms --alarm-names "GPU-Instance-Truly-Idle"
   ```

2. Check Lambda logs:
   ```bash
   aws logs tail /aws/lambda/stop-gpu-instance --follow
   ```

3. Force stop:
   ```bash
   aws ec2 stop-instances --instance-ids i-xxxxxxxxxxxxx --force
   ```

### Custom Metric Not Publishing

1. Check service status on EC2:
   ```bash
   sudo systemctl status comfyui-monitor.service
   ```

2. View service logs:
   ```bash
   sudo journalctl -u comfyui-monitor.service -n 50
   ```

3. Verify ComfyUI is running:
   ```bash
   curl http://localhost:8188/queue
   ```

4. Check IAM role attached to EC2 instance:
   ```bash
   aws ec2 describe-instances --instance-ids i-xxxxxxxxxxxxx \
     --query 'Reservations[0].Instances[0].IamInstanceProfile'
   ```

## Customization

### Change Idle Timeout

Edit Lambda environment variable:

```bash
aws lambda update-function-configuration \
  --function-name stop-gpu-instance \
  --environment Variables="{GPU_INSTANCE_ID=i-xxxxxxxxxxxxx,GRACE_PERIOD_MINUTES=5}" \
  --region eu-north-1
```

### Change CloudWatch Alarm Period

```bash
# 5 minutes instead of 10 minutes
aws cloudwatch put-metric-alarm \
  --alarm-name "GPU-Instance-CPU-Idle" \
  --period 150 \
  --evaluation-periods 2 \
  --region eu-north-1
```

## Cost Estimates

| Usage Pattern | Hours/Day | Monthly Cost |
|---------------|-----------|--------------|
| Aggressive (auto-shutdown) | 2 | $40 |
| Moderate | 4 | $72 |
| Peak | 8 | $136 |
| 24/7 (no auto-shutdown) | 24 | $392 |

**Recommendation**: Start with aggressive (10 min idle timeout) and adjust based on usage patterns.

## Support

- **Full Documentation**: `c:/Ziggie/AWS_LAMBDA_GPU_AUTO_SHUTDOWN_GUIDE.md`
- **Quick Reference**: `c:/Ziggie/AWS_GPU_AUTOSHUTDOWN_QUICK_REFERENCE.md`
- **AWS Lambda Docs**: https://docs.aws.amazon.com/lambda/
- **CloudWatch Docs**: https://docs.aws.amazon.com/cloudwatch/
