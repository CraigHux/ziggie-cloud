# AWS CloudWatch Infrastructure Alarms Setup Script
# Sets up infrastructure health monitoring for Ziggie EC2/EBS resources
# Usage: .\setup-infrastructure-alarms.ps1 [-InstanceId <id>]
#
# Prerequisites:
# - AWS CLI installed at "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
# - Configured AWS credentials with cloudwatch:PutMetricAlarm permission
# - SNS topic ziggie-alerts already exists
# - (Optional) CloudWatch agent installed on EC2 for memory/disk metrics
#
# Created: 2025-12-28
# Account: 785186659442
# Region: eu-north-1

param(
    [string]$InstanceId = "",
    [switch]$SkipAgentMetrics = $false
)

$ErrorActionPreference = "Stop"
$aws = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
$configDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$accountId = "785186659442"
$region = "eu-north-1"
$snsTopicArn = "arn:aws:sns:${region}:${accountId}:ziggie-alerts"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "     ZIGGIE INFRASTRUCTURE CLOUDWATCH ALARMS SETUP" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Verify AWS access
Write-Host "[1/8] Verifying AWS credentials..." -ForegroundColor Yellow
try {
    $identity = & $aws sts get-caller-identity --output json | ConvertFrom-Json
    Write-Host "  OK - Authenticated as: $($identity.Arn)" -ForegroundColor Green
    $accountId = $identity.Account
} catch {
    Write-Host "  FAILED - Could not authenticate with AWS" -ForegroundColor Red
    exit 1
}

# Step 2: Verify SNS topic exists
Write-Host "[2/8] Verifying SNS topic ziggie-alerts..." -ForegroundColor Yellow
try {
    $topics = & $aws sns list-topics --region $region --output json | ConvertFrom-Json
    $found = $topics.Topics | Where-Object { $_.TopicArn -eq $snsTopicArn }
    if ($found) {
        Write-Host "  OK - SNS topic exists: $snsTopicArn" -ForegroundColor Green
    } else {
        Write-Host "  Creating SNS topic ziggie-alerts..." -ForegroundColor Yellow
        & $aws sns create-topic --name ziggie-alerts --region $region
        Write-Host "  OK - SNS topic created" -ForegroundColor Green
    }
} catch {
    Write-Host "  FAILED - SNS check failed: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Get EC2 instances if not specified
Write-Host "[3/8] Identifying EC2 instances..." -ForegroundColor Yellow
$instances = @()
try {
    if ($InstanceId) {
        $instances = @($InstanceId)
        Write-Host "  Using specified instance: $InstanceId" -ForegroundColor Gray
    } else {
        # Get all running instances with ziggie tag or GPU instances
        $result = & $aws ec2 describe-instances `
            --filters "Name=instance-state-name,Values=running,stopped" `
            --query "Reservations[*].Instances[*].[InstanceId,InstanceType,Tags[?Key=='Name'].Value|[0]]" `
            --region $region `
            --output json | ConvertFrom-Json

        foreach ($reservation in $result) {
            foreach ($instance in $reservation) {
                if ($instance[0]) {
                    $instances += $instance[0]
                    Write-Host "  Found: $($instance[0]) ($($instance[1])) - $($instance[2])" -ForegroundColor Gray
                }
            }
        }
    }

    if ($instances.Count -eq 0) {
        Write-Host "  INFO - No EC2 instances found. Creating template alarms for future instances." -ForegroundColor Yellow
        $instances = @("INSTANCE_ID_PLACEHOLDER")
    } else {
        Write-Host "  OK - Found $($instances.Count) instance(s)" -ForegroundColor Green
    }
} catch {
    Write-Host "  WARNING - Could not list instances: $_" -ForegroundColor Yellow
    Write-Host "  Creating template alarms with placeholder instance ID" -ForegroundColor Yellow
    $instances = @("INSTANCE_ID_PLACEHOLDER")
}

# Step 4: Create EC2 StatusCheckFailed Alarm
Write-Host "[4/8] Creating EC2 StatusCheckFailed alarms..." -ForegroundColor Yellow
$alarmsCreated = 0

foreach ($instanceId in $instances) {
    $alarmName = "ziggie-ec2-status-check-$instanceId"

    try {
        & $aws cloudwatch put-metric-alarm `
            --alarm-name $alarmName `
            --alarm-description "Alert when EC2 instance $instanceId fails status checks" `
            --namespace "AWS/EC2" `
            --metric-name "StatusCheckFailed" `
            --dimensions "Name=InstanceId,Value=$instanceId" `
            --statistic Maximum `
            --period 60 `
            --evaluation-periods 2 `
            --threshold 1 `
            --comparison-operator GreaterThanOrEqualToThreshold `
            --alarm-actions $snsTopicArn `
            --ok-actions $snsTopicArn `
            --treat-missing-data notBreaching `
            --region $region

        Write-Host "  OK - Created: $alarmName" -ForegroundColor Green
        $alarmsCreated++
    } catch {
        Write-Host "  FAILED - $alarmName : $_" -ForegroundColor Red
    }
}

# Step 5: Create EC2 CPUUtilization Alarm (>80%)
Write-Host "[5/8] Creating EC2 CPUUtilization alarms (>80%)..." -ForegroundColor Yellow

foreach ($instanceId in $instances) {
    $alarmName = "ziggie-ec2-cpu-high-$instanceId"

    try {
        & $aws cloudwatch put-metric-alarm `
            --alarm-name $alarmName `
            --alarm-description "Alert when EC2 instance $instanceId CPU exceeds 80% for 5 minutes" `
            --namespace "AWS/EC2" `
            --metric-name "CPUUtilization" `
            --dimensions "Name=InstanceId,Value=$instanceId" `
            --statistic Average `
            --period 300 `
            --evaluation-periods 3 `
            --threshold 80 `
            --comparison-operator GreaterThanThreshold `
            --alarm-actions $snsTopicArn `
            --ok-actions $snsTopicArn `
            --treat-missing-data notBreaching `
            --region $region

        Write-Host "  OK - Created: $alarmName" -ForegroundColor Green
        $alarmsCreated++
    } catch {
        Write-Host "  FAILED - $alarmName : $_" -ForegroundColor Red
    }
}

# Step 6: Create EBS Volume Alarms
Write-Host "[6/8] Creating EBS Volume alarms..." -ForegroundColor Yellow

# Get EBS volumes attached to instances
$volumes = @()
foreach ($instanceId in $instances) {
    if ($instanceId -ne "INSTANCE_ID_PLACEHOLDER") {
        try {
            $result = & $aws ec2 describe-volumes `
                --filters "Name=attachment.instance-id,Values=$instanceId" `
                --query "Volumes[*].VolumeId" `
                --region $region `
                --output json | ConvertFrom-Json

            $volumes += $result
        } catch {
            Write-Host "  WARNING - Could not get volumes for $instanceId" -ForegroundColor Yellow
        }
    }
}

if ($volumes.Count -eq 0) {
    Write-Host "  INFO - No volumes found. Creating template alarm." -ForegroundColor Yellow
    $volumes = @("VOLUME_ID_PLACEHOLDER")
}

foreach ($volumeId in $volumes) {
    # High Read IOPS Alarm
    $alarmName = "ziggie-ebs-read-iops-$volumeId"
    try {
        & $aws cloudwatch put-metric-alarm `
            --alarm-name $alarmName `
            --alarm-description "Alert when EBS volume $volumeId read IOPS is high" `
            --namespace "AWS/EBS" `
            --metric-name "VolumeReadOps" `
            --dimensions "Name=VolumeId,Value=$volumeId" `
            --statistic Sum `
            --period 300 `
            --evaluation-periods 3 `
            --threshold 10000 `
            --comparison-operator GreaterThanThreshold `
            --alarm-actions $snsTopicArn `
            --treat-missing-data notBreaching `
            --region $region

        Write-Host "  OK - Created: $alarmName" -ForegroundColor Green
        $alarmsCreated++
    } catch {
        Write-Host "  FAILED - $alarmName : $_" -ForegroundColor Red
    }

    # High Write IOPS Alarm
    $alarmName = "ziggie-ebs-write-iops-$volumeId"
    try {
        & $aws cloudwatch put-metric-alarm `
            --alarm-name $alarmName `
            --alarm-description "Alert when EBS volume $volumeId write IOPS is high" `
            --namespace "AWS/EBS" `
            --metric-name "VolumeWriteOps" `
            --dimensions "Name=VolumeId,Value=$volumeId" `
            --statistic Sum `
            --period 300 `
            --evaluation-periods 3 `
            --threshold 10000 `
            --comparison-operator GreaterThanThreshold `
            --alarm-actions $snsTopicArn `
            --treat-missing-data notBreaching `
            --region $region

        Write-Host "  OK - Created: $alarmName" -ForegroundColor Green
        $alarmsCreated++
    } catch {
        Write-Host "  FAILED - $alarmName : $_" -ForegroundColor Red
    }
}

# Step 7: Create CloudWatch Agent Metrics Alarms (Memory & Disk)
Write-Host "[7/8] Creating CloudWatch Agent alarms (Memory & Disk)..." -ForegroundColor Yellow

if ($SkipAgentMetrics) {
    Write-Host "  SKIPPED - Agent metrics disabled via -SkipAgentMetrics" -ForegroundColor Yellow
} else {
    foreach ($instanceId in $instances) {
        # Memory Utilization Alarm (>85%)
        $alarmName = "ziggie-ec2-memory-high-$instanceId"
        try {
            & $aws cloudwatch put-metric-alarm `
                --alarm-name $alarmName `
                --alarm-description "Alert when EC2 instance $instanceId memory exceeds 85%" `
                --namespace "CWAgent" `
                --metric-name "mem_used_percent" `
                --dimensions "Name=InstanceId,Value=$instanceId" `
                --statistic Average `
                --period 300 `
                --evaluation-periods 3 `
                --threshold 85 `
                --comparison-operator GreaterThanThreshold `
                --alarm-actions $snsTopicArn `
                --ok-actions $snsTopicArn `
                --treat-missing-data notBreaching `
                --region $region

            Write-Host "  OK - Created: $alarmName" -ForegroundColor Green
            $alarmsCreated++
        } catch {
            Write-Host "  WARNING - $alarmName : $_" -ForegroundColor Yellow
            Write-Host "           (CloudWatch agent may not be installed)" -ForegroundColor Gray
        }

        # Disk Utilization Alarm (>80%)
        $alarmName = "ziggie-ec2-disk-high-$instanceId"
        try {
            & $aws cloudwatch put-metric-alarm `
                --alarm-name $alarmName `
                --alarm-description "Alert when EC2 instance $instanceId disk exceeds 80%" `
                --namespace "CWAgent" `
                --metric-name "disk_used_percent" `
                --dimensions "Name=InstanceId,Value=$instanceId" "Name=path,Value=/" "Name=fstype,Value=ext4" `
                --statistic Average `
                --period 300 `
                --evaluation-periods 3 `
                --threshold 80 `
                --comparison-operator GreaterThanThreshold `
                --alarm-actions $snsTopicArn `
                --ok-actions $snsTopicArn `
                --treat-missing-data notBreaching `
                --region $region

            Write-Host "  OK - Created: $alarmName" -ForegroundColor Green
            $alarmsCreated++
        } catch {
            Write-Host "  WARNING - $alarmName : $_" -ForegroundColor Yellow
            Write-Host "           (CloudWatch agent may not be installed)" -ForegroundColor Gray
        }
    }
}

# Step 8: List all alarms
Write-Host "[8/8] Verifying CloudWatch alarms..." -ForegroundColor Yellow
try {
    $alarms = & $aws cloudwatch describe-alarms `
        --alarm-name-prefix "ziggie-" `
        --region $region `
        --output json | ConvertFrom-Json

    Write-Host "  OK - Total Ziggie alarms: $($alarms.MetricAlarms.Count)" -ForegroundColor Green

    foreach ($alarm in $alarms.MetricAlarms) {
        $state = $alarm.StateValue
        $color = switch ($state) {
            "OK" { "Green" }
            "ALARM" { "Red" }
            "INSUFFICIENT_DATA" { "Yellow" }
            default { "Gray" }
        }
        Write-Host "       [$state] $($alarm.AlarmName)" -ForegroundColor $color
    }
} catch {
    Write-Host "  WARNING - Could not list alarms: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "     INFRASTRUCTURE ALARMS SETUP COMPLETE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "SUMMARY:" -ForegroundColor White
Write-Host "  Alarms Created: $alarmsCreated" -ForegroundColor Gray
Write-Host "  SNS Topic: $snsTopicArn" -ForegroundColor Gray
Write-Host "  Region: $region" -ForegroundColor Gray
Write-Host ""
Write-Host "ALARM TYPES CONFIGURED:" -ForegroundColor White
Write-Host "  [EC2] StatusCheckFailed - Instance health" -ForegroundColor Gray
Write-Host "  [EC2] CPUUtilization >80% - High CPU" -ForegroundColor Gray
Write-Host "  [EBS] VolumeReadOps - High read IOPS" -ForegroundColor Gray
Write-Host "  [EBS] VolumeWriteOps - High write IOPS" -ForegroundColor Gray
Write-Host "  [CWAgent] mem_used_percent >85% - High memory" -ForegroundColor Gray
Write-Host "  [CWAgent] disk_used_percent >80% - High disk" -ForegroundColor Gray
Write-Host ""
Write-Host "CLOUDWATCH AGENT NOTE:" -ForegroundColor Yellow
Write-Host "  Memory and disk metrics require CloudWatch agent installed on EC2." -ForegroundColor Gray
Write-Host "  Install guide: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Install-CloudWatch-Agent.html" -ForegroundColor Gray
Write-Host ""
Write-Host "VIEW ALARMS:" -ForegroundColor White
Write-Host "  Console: https://eu-north-1.console.aws.amazon.com/cloudwatch/home?region=eu-north-1#alarmsV2:" -ForegroundColor Cyan
Write-Host ""
Write-Host "CLI Commands:" -ForegroundColor White
Write-Host '  List alarms:' -ForegroundColor Gray
Write-Host '  & $aws cloudwatch describe-alarms --alarm-name-prefix "ziggie-" --region eu-north-1' -ForegroundColor DarkGray
Write-Host ""
Write-Host '  Check alarm state:' -ForegroundColor Gray
Write-Host '  & $aws cloudwatch describe-alarm-history --alarm-name-prefix "ziggie-" --region eu-north-1' -ForegroundColor DarkGray
Write-Host ""
