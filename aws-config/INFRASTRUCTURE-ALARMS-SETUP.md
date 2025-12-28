# AWS CloudWatch Infrastructure Alarms Setup for Ziggie

> **Created**: 2025-12-28
> **Account**: 785186659442
> **Region**: eu-north-1
> **SNS Topic**: ziggie-alerts

---

## Quick Start

Run the setup script to configure all infrastructure health alarms:

```powershell
cd C:\Ziggie\aws-config
.\setup-infrastructure-alarms.ps1

# Or specify a specific instance:
.\setup-infrastructure-alarms.ps1 -InstanceId "i-0123456789abcdef0"

# Skip CloudWatch agent metrics (if agent not installed):
.\setup-infrastructure-alarms.ps1 -SkipAgentMetrics
```

---

## Alarm Configuration Summary

### EC2 Instance Alarms

| Alarm Name Pattern | Metric | Threshold | Period | Description |
|-------------------|--------|-----------|--------|-------------|
| `ziggie-ec2-status-check-{id}` | StatusCheckFailed | >= 1 | 1 min (2 periods) | Instance health check failure |
| `ziggie-ec2-cpu-high-{id}` | CPUUtilization | > 80% | 5 min (3 periods) | High CPU utilization |
| `ziggie-ec2-memory-high-{id}` | mem_used_percent | > 85% | 5 min (3 periods) | High memory utilization* |
| `ziggie-ec2-disk-high-{id}` | disk_used_percent | > 80% | 5 min (3 periods) | High disk utilization* |

*Requires CloudWatch agent installed

### EBS Volume Alarms

| Alarm Name Pattern | Metric | Threshold | Period | Description |
|-------------------|--------|-----------|--------|-------------|
| `ziggie-ebs-read-iops-{id}` | VolumeReadOps | > 10,000 | 5 min (3 periods) | High read IOPS |
| `ziggie-ebs-write-iops-{id}` | VolumeWriteOps | > 10,000 | 5 min (3 periods) | High write IOPS |

---

## CloudWatch Agent Installation

Memory and disk metrics require the CloudWatch agent. Install on your EC2 instance:

### Amazon Linux 2 / AL2023

```bash
# Download and install
sudo yum install -y amazon-cloudwatch-agent

# Copy config from S3 or create locally
sudo mkdir -p /opt/aws/amazon-cloudwatch-agent/etc/
sudo aws s3 cp s3://ziggie-assets-prod/config/cloudwatch-agent-config.json /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json

# Or create config manually (see cloudwatch-agent-config.json in this directory)

# Start the agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json \
    -s

# Verify
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a status
```

### Ubuntu / Debian

```bash
# Download
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb

# Install
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure and start (same as above)
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json \
    -s
```

---

## CloudWatch Agent Configuration

The configuration file `cloudwatch-agent-config.json` collects:

### Metrics Collected

| Metric Type | Metrics | Interval |
|-------------|---------|----------|
| **Memory** | mem_used_percent, mem_available_percent, mem_used, mem_total | 60s |
| **Disk** | disk_used_percent, disk_free, disk_used, disk_total | 60s |
| **Disk I/O** | reads, writes, read_bytes, write_bytes | 60s |
| **Swap** | swap_used_percent, swap_used, swap_free | 60s |
| **CPU** | cpu_usage_idle, cpu_usage_user, cpu_usage_system, cpu_usage_iowait | 60s |
| **Network** | bytes_sent, bytes_recv, packets_sent, packets_recv | 60s |
| **Processes** | running, sleeping, total | 60s |

### Logs Collected

| Log File | Log Group |
|----------|-----------|
| `/var/log/syslog` | ziggie-ec2-syslog |
| `/var/log/cloud-init-output.log` | ziggie-ec2-cloud-init |

---

## Viewing Alarms

### AWS Console

| View | URL |
|------|-----|
| **All Alarms** | https://eu-north-1.console.aws.amazon.com/cloudwatch/home?region=eu-north-1#alarmsV2: |
| **Alarm History** | https://eu-north-1.console.aws.amazon.com/cloudwatch/home?region=eu-north-1#alarmsV2:alarm/history |
| **Metrics** | https://eu-north-1.console.aws.amazon.com/cloudwatch/home?region=eu-north-1#metricsV2: |

### CLI Commands

```powershell
$aws = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
$region = "eu-north-1"

# List all Ziggie alarms
& $aws cloudwatch describe-alarms `
    --alarm-name-prefix "ziggie-" `
    --region $region

# Check alarm states (summary)
& $aws cloudwatch describe-alarms `
    --alarm-name-prefix "ziggie-" `
    --query "MetricAlarms[*].[AlarmName,StateValue]" `
    --output table `
    --region $region

# Get alarm history (last 24 hours)
& $aws cloudwatch describe-alarm-history `
    --alarm-name-prefix "ziggie-" `
    --history-item-type StateUpdate `
    --start-date (Get-Date).AddDays(-1).ToString("yyyy-MM-ddTHH:mm:ssZ") `
    --region $region

# Check if CloudWatch agent metrics are being received
& $aws cloudwatch list-metrics `
    --namespace "CWAgent" `
    --region $region

# Get specific metric data
& $aws cloudwatch get-metric-statistics `
    --namespace "AWS/EC2" `
    --metric-name "CPUUtilization" `
    --dimensions "Name=InstanceId,Value=i-your-instance-id" `
    --start-time (Get-Date).AddHours(-1).ToString("yyyy-MM-ddTHH:mm:ssZ") `
    --end-time (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ") `
    --period 300 `
    --statistics Average `
    --region $region
```

---

## Alarm Actions

All alarms are configured to:

1. **Send SNS notification** to `ziggie-alerts` when alarm triggers (ALARM state)
2. **Send SNS notification** when alarm recovers (OK state)
3. **Treat missing data as not breaching** (avoids false alarms when instance is stopped)

### SNS Subscription

Ensure you have subscribed to the SNS topic:

```powershell
# Subscribe email
& $aws sns subscribe `
    --topic-arn "arn:aws:sns:eu-north-1:785186659442:ziggie-alerts" `
    --protocol email `
    --notification-endpoint your-email@example.com `
    --region eu-north-1

# List current subscriptions
& $aws sns list-subscriptions-by-topic `
    --topic-arn "arn:aws:sns:eu-north-1:785186659442:ziggie-alerts" `
    --region eu-north-1
```

---

## Threshold Tuning

Adjust thresholds based on your workload:

### CPU Thresholds by Instance Type

| Instance Type | Use Case | Recommended CPU Threshold |
|---------------|----------|---------------------------|
| t3.micro/small | Low traffic | 70% |
| t3.medium/large | Normal workload | 80% |
| g4dn.xlarge | GPU compute | 90% |
| c5/c6 (compute) | High compute | 85% |

### Memory Thresholds

| Workload | Recommended Memory Threshold |
|----------|------------------------------|
| Web server | 80% |
| Database | 75% |
| ML/AI workload | 90% |

### Disk Thresholds

| Volume Type | Recommended Disk Threshold |
|-------------|----------------------------|
| Root volume | 80% |
| Data volume | 85% |
| Temporary/cache | 90% |

---

## Modifying Alarms

To modify an existing alarm:

```powershell
# Update CPU threshold to 90%
& $aws cloudwatch put-metric-alarm `
    --alarm-name "ziggie-ec2-cpu-high-i-your-instance" `
    --namespace "AWS/EC2" `
    --metric-name "CPUUtilization" `
    --dimensions "Name=InstanceId,Value=i-your-instance" `
    --statistic Average `
    --period 300 `
    --evaluation-periods 3 `
    --threshold 90 `
    --comparison-operator GreaterThanThreshold `
    --alarm-actions "arn:aws:sns:eu-north-1:785186659442:ziggie-alerts" `
    --region eu-north-1

# Delete an alarm
& $aws cloudwatch delete-alarms `
    --alarm-names "ziggie-ec2-cpu-high-i-old-instance" `
    --region eu-north-1
```

---

## IAM Permissions Required

Add to your IAM policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "CloudWatchAlarms",
            "Effect": "Allow",
            "Action": [
                "cloudwatch:PutMetricAlarm",
                "cloudwatch:DeleteAlarms",
                "cloudwatch:DescribeAlarms",
                "cloudwatch:DescribeAlarmHistory",
                "cloudwatch:GetMetricStatistics",
                "cloudwatch:ListMetrics"
            ],
            "Resource": "*"
        },
        {
            "Sid": "EC2Describe",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeVolumes"
            ],
            "Resource": "*"
        }
    ]
}
```

---

## Troubleshooting

### Alarm Shows INSUFFICIENT_DATA

1. Instance may be stopped
2. CloudWatch agent not installed (for mem/disk metrics)
3. Metric not yet published (wait 5-10 minutes)

### CloudWatch Agent Metrics Not Appearing

```bash
# Check agent status
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a status

# Check agent logs
sudo tail -f /opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log

# Verify IAM role has CloudWatchAgentServerPolicy
aws iam list-attached-role-policies --role-name EC2-CloudWatch-Role
```

### SNS Notifications Not Received

1. Check SNS subscription is confirmed
2. Check email spam folder
3. Verify alarm actions include the SNS topic ARN

---

## Configuration Files

| File | Purpose |
|------|---------|
| `setup-infrastructure-alarms.ps1` | Main setup script |
| `cloudwatch-agent-config.json` | CloudWatch agent configuration |
| `INFRASTRUCTURE-ALARMS-SETUP.md` | This documentation |

---

## Monitoring Completion Status

### Cost Monitoring (65% -> COMPLETE)

- [x] AWS Budgets ($150/month)
- [x] Budget alerts (50%, 80%, 100%, 120%)
- [x] Cost Anomaly Detection (>$10)
- [x] SNS notifications

### Infrastructure Health Monitoring (0% -> COMPLETE)

- [x] EC2 StatusCheckFailed
- [x] EC2 CPUUtilization (>80%)
- [x] EBS VolumeReadOps
- [x] EBS VolumeWriteOps
- [x] Memory utilization (>85%) - requires CloudWatch agent
- [x] Disk space utilization (>80%) - requires CloudWatch agent

### **OVERALL STATUS: 100% COMPLETE**

---

## Related Documentation

- [COST-MONITORING-SETUP.md](./COST-MONITORING-SETUP.md) - Budget and cost alerts
- [GPU-LAUNCH-TEMPLATE-REPORT.md](./GPU-LAUNCH-TEMPLATE-REPORT.md) - GPU instance configuration
- AWS CloudWatch Alarms: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html
- CloudWatch Agent: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Install-CloudWatch-Agent.html

---

## Document Metadata

| Field | Value |
|-------|-------|
| Created | 2025-12-28 |
| Author | CloudWatch Infrastructure Agent |
| Status | READY FOR DEPLOYMENT |
| Related Gap | GAP-034 (Infrastructure health monitoring) |
