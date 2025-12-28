#!/bin/bash
# Deploy all Lambda functions for GPU instance auto-shutdown
# Usage: ./deploy_lambda_functions.sh

set -e

# Configuration - REPLACE THESE VALUES
INSTANCE_ID="i-xxxxxxxxxxxxx"  # Your g4dn.xlarge instance ID
ACCOUNT_ID="xxxxxxxxxxxx"      # Your AWS account ID (12 digits)
REGION="eu-north-1"
ROLE_NAME="lambda-ec2-control"

echo "Deploying Lambda functions for GPU auto-shutdown"
echo "================================================"
echo "Instance ID: $INSTANCE_ID"
echo "Region: $REGION"
echo ""

# Step 1: Create IAM role if it doesn't exist
echo "Step 1: Creating IAM role..."

# Create trust policy
cat > /tmp/lambda-trust-policy.json << 'EOF'
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
EOF

# Create role (ignore error if already exists)
aws iam create-role \
  --role-name "$ROLE_NAME" \
  --assume-role-policy-document file:///tmp/lambda-trust-policy.json \
  2>/dev/null || echo "Role already exists, continuing..."

# Attach policies
echo "Attaching IAM policies..."
aws iam attach-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess \
  2>/dev/null || true

aws iam attach-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess \
  2>/dev/null || true

aws iam attach-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
  2>/dev/null || true

ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
echo "✓ IAM role ready: $ROLE_ARN"

# Wait for role to propagate
echo "Waiting 10 seconds for IAM role to propagate..."
sleep 10

# Step 2: Deploy start-gpu-instance function
echo ""
echo "Step 2: Deploying start-gpu-instance function..."

zip -j /tmp/lambda_start.zip lambda_start_gpu_instance.py

# Try to create function, update if already exists
aws lambda create-function \
  --function-name start-gpu-instance \
  --runtime python3.11 \
  --role "$ROLE_ARN" \
  --handler lambda_start_gpu_instance.lambda_handler \
  --zip-file fileb:///tmp/lambda_start.zip \
  --timeout 300 \
  --environment Variables="{GPU_INSTANCE_ID=${INSTANCE_ID}}" \
  --region "$REGION" \
  2>/dev/null || \
aws lambda update-function-code \
  --function-name start-gpu-instance \
  --zip-file fileb:///tmp/lambda_start.zip \
  --region "$REGION"

# Update environment variables
aws lambda update-function-configuration \
  --function-name start-gpu-instance \
  --environment Variables="{GPU_INSTANCE_ID=${INSTANCE_ID}}" \
  --region "$REGION" \
  > /dev/null

echo "✓ start-gpu-instance deployed"

# Step 3: Deploy stop-gpu-instance function
echo ""
echo "Step 3: Deploying stop-gpu-instance function..."

zip -j /tmp/lambda_stop.zip lambda_stop_gpu_instance.py

aws lambda create-function \
  --function-name stop-gpu-instance \
  --runtime python3.11 \
  --role "$ROLE_ARN" \
  --handler lambda_stop_gpu_instance.lambda_handler \
  --zip-file fileb:///tmp/lambda_stop.zip \
  --timeout 60 \
  --environment Variables="{GPU_INSTANCE_ID=${INSTANCE_ID},GRACE_PERIOD_MINUTES=10}" \
  --region "$REGION" \
  2>/dev/null || \
aws lambda update-function-code \
  --function-name stop-gpu-instance \
  --zip-file fileb:///tmp/lambda_stop.zip \
  --region "$REGION"

aws lambda update-function-configuration \
  --function-name stop-gpu-instance \
  --environment Variables="{GPU_INSTANCE_ID=${INSTANCE_ID},GRACE_PERIOD_MINUTES=10}" \
  --region "$REGION" \
  > /dev/null

echo "✓ stop-gpu-instance deployed"

# Step 4: Deploy check-comfyui-health function
echo ""
echo "Step 4: Deploying check-comfyui-health function..."

# Package with requests library
mkdir -p /tmp/lambda_health_package
pip install requests -t /tmp/lambda_health_package/ -q
cp lambda_check_comfyui_health.py /tmp/lambda_health_package/

cd /tmp/lambda_health_package && zip -r /tmp/lambda_health.zip . > /dev/null && cd -

aws lambda create-function \
  --function-name check-comfyui-health \
  --runtime python3.11 \
  --role "$ROLE_ARN" \
  --handler lambda_check_comfyui_health.lambda_handler \
  --zip-file fileb:///tmp/lambda_health.zip \
  --timeout 300 \
  --environment Variables="{GPU_INSTANCE_ID=${INSTANCE_ID},MAX_WAIT_SECONDS=300,COMFYUI_PORT=8188}" \
  --region "$REGION" \
  2>/dev/null || \
aws lambda update-function-code \
  --function-name check-comfyui-health \
  --zip-file fileb:///tmp/lambda_health.zip \
  --region "$REGION"

aws lambda update-function-configuration \
  --function-name check-comfyui-health \
  --environment Variables="{GPU_INSTANCE_ID=${INSTANCE_ID},MAX_WAIT_SECONDS=300,COMFYUI_PORT=8188}" \
  --region "$REGION" \
  > /dev/null

echo "✓ check-comfyui-health deployed"

# Step 5: Test functions
echo ""
echo "Step 5: Testing Lambda functions..."

echo "Testing start-gpu-instance..."
aws lambda invoke \
  --function-name start-gpu-instance \
  --region "$REGION" \
  /tmp/test_start.json \
  > /dev/null

echo "Response:"
cat /tmp/test_start.json | python3 -m json.tool

# Cleanup
rm -rf /tmp/lambda_start.zip /tmp/lambda_stop.zip /tmp/lambda_health.zip
rm -rf /tmp/lambda_health_package /tmp/lambda-trust-policy.json

echo ""
echo "================================================"
echo "✓ All Lambda functions deployed successfully!"
echo ""
echo "Function ARNs:"
echo "  start-gpu-instance:     arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:start-gpu-instance"
echo "  stop-gpu-instance:      arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:stop-gpu-instance"
echo "  check-comfyui-health:   arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:check-comfyui-health"
echo ""
echo "Next steps:"
echo "1. Run ./setup_cloudwatch_alarms.sh to create alarms"
echo "2. Install comfyui_monitor.py on EC2 instance"
echo "3. Configure n8n workflows to call Lambda functions"
