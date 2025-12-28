#!/bin/bash
# Setup CloudWatch alarms for GPU instance auto-shutdown
# Usage: ./setup_cloudwatch_alarms.sh

set -e

# Configuration - REPLACE THESE VALUES
INSTANCE_ID="i-xxxxxxxxxxxxx"  # Your g4dn.xlarge instance ID
ACCOUNT_ID="xxxxxxxxxxxx"      # Your AWS account ID (12 digits)
REGION="eu-north-1"

# Lambda function ARN
LAMBDA_ARN="arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:stop-gpu-instance"

echo "Setting up CloudWatch alarms for GPU instance auto-shutdown"
echo "============================================================"
echo "Instance ID: $INSTANCE_ID"
echo "Lambda ARN: $LAMBDA_ARN"
echo "Region: $REGION"
echo ""

# Alarm 1: CPU Idle
echo "Creating CPU idle alarm..."
aws cloudwatch put-metric-alarm \
  --region "$REGION" \
  --alarm-name "GPU-Instance-CPU-Idle" \
  --alarm-description "Trigger when CPU < 5% for 10 minutes" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 5.0 \
  --comparison-operator LessThanThreshold \
  --dimensions Name=InstanceId,Value="$INSTANCE_ID" \
  --treat-missing-data notBreaching

echo "✓ CPU idle alarm created"

# Alarm 2: Network Idle
echo "Creating network idle alarm..."
aws cloudwatch put-metric-alarm \
  --region "$REGION" \
  --alarm-name "GPU-Instance-Network-Idle" \
  --alarm-description "Trigger when NetworkOut < 1MB for 10 minutes" \
  --metric-name NetworkOut \
  --namespace AWS/EC2 \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 1048576 \
  --comparison-operator LessThanThreshold \
  --dimensions Name=InstanceId,Value="$INSTANCE_ID" \
  --treat-missing-data notBreaching

echo "✓ Network idle alarm created"

# Alarm 3: ComfyUI Queue Idle (custom metric)
echo "Creating ComfyUI queue idle alarm..."
aws cloudwatch put-metric-alarm \
  --region "$REGION" \
  --alarm-name "GPU-Instance-ComfyUI-Idle" \
  --alarm-description "Trigger when ComfyUI queue = 0 for 10 minutes" \
  --metric-name QueueDepth \
  --namespace ComfyUI \
  --statistic Maximum \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 0 \
  --comparison-operator LessThanOrEqualToThreshold \
  --dimensions Name=InstanceId,Value="$INSTANCE_ID" \
  --treat-missing-data notBreaching

echo "✓ ComfyUI queue idle alarm created"

# Composite Alarm: ALL conditions must be true
echo "Creating composite alarm (ALL idle conditions)..."
aws cloudwatch put-composite-alarm \
  --region "$REGION" \
  --alarm-name "GPU-Instance-Truly-Idle" \
  --alarm-description "Trigger shutdown when ALL idle conditions met" \
  --alarm-rule "ALARM(GPU-Instance-CPU-Idle) AND ALARM(GPU-Instance-Network-Idle) AND ALARM(GPU-Instance-ComfyUI-Idle)" \
  --actions-enabled \
  --alarm-actions "$LAMBDA_ARN"

echo "✓ Composite alarm created with Lambda action"
echo ""
echo "============================================================"
echo "CloudWatch alarms configured successfully!"
echo ""
echo "Next steps:"
echo "1. Verify alarms in AWS Console:"
echo "   https://console.aws.amazon.com/cloudwatch/home?region=$REGION#alarmsV2:"
echo ""
echo "2. Test alarm trigger:"
echo "   aws cloudwatch set-alarm-state \\"
echo "     --alarm-name 'GPU-Instance-Truly-Idle' \\"
echo "     --state-value ALARM \\"
echo "     --state-reason 'Test'"
echo ""
echo "3. Monitor alarm status:"
echo "   aws cloudwatch describe-alarms \\"
echo "     --alarm-names 'GPU-Instance-Truly-Idle'"
