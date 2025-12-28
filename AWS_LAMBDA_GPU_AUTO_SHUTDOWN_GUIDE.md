# AWS Lambda GPU Instance Auto-Shutdown Guide

> **Purpose**: Minimize AWS g4dn.xlarge GPU costs through automated idle detection and shutdown
> **Target Cost**: <$50/month normal, <$150/month peak GPU usage
> **Region**: EU-North-1 Stockholm
> **Integration**: n8n workflows on Hostinger VPS (82.25.112.73)
> **Last Updated**: 2025-12-23

---

## Executive Summary

**Cost Savings Potential**:
- g4dn.xlarge on-demand: ~$0.526/hour (~$378/month if running 24/7)
- With aggressive auto-shutdown (2 hours/day avg): ~$31.56/month (91% savings)
- With moderate use (4 hours/day avg): ~$63.12/month (83% savings)
- With peak use (8 hours/day avg): ~$126.24/month (66% savings)

**Key Strategy**: Run GPU instance ONLY when ComfyUI workflows are actively processing, shut down during idle periods.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Lambda Function Patterns](#lambda-function-patterns)
3. [Idle Detection Strategies](#idle-detection-strategies)
4. [CloudWatch Alarm Configurations](#cloudwatch-alarm-configurations)
5. [n8n Integration Patterns](#n8n-integration-patterns)
6. [Cost Optimization Calculations](#cost-optimization-calculations)
7. [Implementation Checklist](#implementation-checklist)
8. [Best Practices](#best-practices)

---

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────┐
│ Ziggie Cloud (Hostinger VPS - 82.25.112.73)               │
│ ┌─────────────────────────────────────────────────────┐    │
│ │ n8n Workflow Engine                                  │    │
│ │ ┌─────────────┐  ┌──────────────┐  ┌─────────────┐ │    │
│ │ │Image Gen    │→ │Lambda Start  │→ │Wait for     │ │    │
│ │ │Request      │  │GPU Instance  │  │Ready        │ │    │
│ │ └─────────────┘  └──────────────┘  └─────────────┘ │    │
│ │ ┌─────────────┐  ┌──────────────┐  ┌─────────────┐ │    │
│ │ │ComfyUI API  │→ │Process Image │→ │Store Result │ │    │
│ │ │Call         │  │Generation    │  │              │ │    │
│ │ └─────────────┘  └──────────────┘  └─────────────┘ │    │
│ └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ AWS EU-North-1 (Stockholm)                                  │
│ ┌─────────────────────────────────────────────────────┐    │
│ │ EC2 g4dn.xlarge GPU Instance                         │    │
│ │ ┌─────────────┐  ┌──────────────┐  ┌─────────────┐ │    │
│ │ │ComfyUI      │  │CloudWatch    │  │Custom       │ │    │
│ │ │Server       │→ │Agent         │→ │Metrics      │ │    │
│ │ └─────────────┘  └──────────────┘  └─────────────┘ │    │
│ └─────────────────────────────────────────────────────┘    │
│ ┌─────────────────────────────────────────────────────┐    │
│ │ CloudWatch Alarms                                    │    │
│ │ ┌─────────────┐  ┌──────────────┐  ┌─────────────┐ │    │
│ │ │CPU < 5%     │  │Network < 1MB │  │Custom: No   │ │    │
│ │ │for 10 min   │  │for 10 min    │  │Queue Jobs   │ │    │
│ │ └─────────────┘  └──────────────┘  └─────────────┘ │    │
│ │                         ↓                             │    │
│ │ ┌─────────────────────────────────────────────────┐ │    │
│ │ │ Lambda: Auto-Shutdown Function                   │ │    │
│ │ │ Stops EC2 instance when all alarms trigger       │ │    │
│ │ └─────────────────────────────────────────────────┘ │    │
│ └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Workflow States

| State | EC2 Status | Cost | Trigger |
|-------|------------|------|---------|
| **Idle** | Stopped | $0/hour (EBS only: ~$0.08/hour) | Default state |
| **Starting** | Starting | $0/hour (transition) | n8n workflow starts instance |
| **Active** | Running | $0.526/hour | ComfyUI processing images |
| **Cooldown** | Running | $0.526/hour | Waiting for idle confirmation |
| **Shutting Down** | Stopping | $0.526/hour (transition) | Lambda shutdown triggered |

---

## Lambda Function Patterns

### 1. Start GPU Instance Function

**Purpose**: Start EC2 instance when n8n triggers image generation

**Python Implementation**:
```python
# lambda_start_gpu_instance.py
import json
import boto3
import os
from typing import Dict, Any

ec2 = boto3.client('ec2', region_name='eu-north-1')
INSTANCE_ID = os.environ['GPU_INSTANCE_ID']

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Start GPU instance and wait for it to be running.
    Called by n8n workflow when image generation is requested.
    """
    try:
        # Get current instance state
        response = ec2.describe_instances(InstanceIds=[INSTANCE_ID])
        instance = response['Reservations'][0]['Instances'][0]
        current_state = instance['State']['Name']

        print(f"Instance {INSTANCE_ID} current state: {current_state}")

        # If already running, return immediately
        if current_state == 'running':
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Instance already running',
                    'instance_id': INSTANCE_ID,
                    'state': current_state,
                    'public_ip': instance.get('PublicIpAddress', 'pending')
                })
            }

        # Start the instance
        if current_state == 'stopped':
            ec2.start_instances(InstanceIds=[INSTANCE_ID])
            print(f"Started instance {INSTANCE_ID}")

            # Wait for instance to be running (with timeout)
            waiter = ec2.get_waiter('instance_running')
            waiter.wait(
                InstanceIds=[INSTANCE_ID],
                WaiterConfig={'Delay': 15, 'MaxAttempts': 20}  # 5 min timeout
            )

            # Get updated instance info with public IP
            response = ec2.describe_instances(InstanceIds=[INSTANCE_ID])
            instance = response['Reservations'][0]['Instances'][0]

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Instance started successfully',
                    'instance_id': INSTANCE_ID,
                    'state': 'running',
                    'public_ip': instance.get('PublicIpAddress'),
                    'comfyui_url': f"http://{instance.get('PublicIpAddress')}:8188"
                })
            }

        # Instance is in transition state
        return {
            'statusCode': 202,
            'body': json.dumps({
                'message': f'Instance is {current_state}, wait and retry',
                'instance_id': INSTANCE_ID,
                'state': current_state
            })
        }

    except Exception as e:
        print(f"Error starting instance: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'instance_id': INSTANCE_ID
            })
        }
```

**Node.js Alternative**:
```javascript
// lambda_start_gpu_instance.js
const AWS = require('aws-sdk');
const ec2 = new AWS.EC2({ region: 'eu-north-1' });
const INSTANCE_ID = process.env.GPU_INSTANCE_ID;

exports.handler = async (event) => {
    try {
        // Get current instance state
        const describeResponse = await ec2.describeInstances({
            InstanceIds: [INSTANCE_ID]
        }).promise();

        const instance = describeResponse.Reservations[0].Instances[0];
        const currentState = instance.State.Name;

        console.log(`Instance ${INSTANCE_ID} current state: ${currentState}`);

        // If already running, return immediately
        if (currentState === 'running') {
            return {
                statusCode: 200,
                body: JSON.stringify({
                    message: 'Instance already running',
                    instance_id: INSTANCE_ID,
                    state: currentState,
                    public_ip: instance.PublicIpAddress || 'pending'
                })
            };
        }

        // Start the instance
        if (currentState === 'stopped') {
            await ec2.startInstances({ InstanceIds: [INSTANCE_ID] }).promise();
            console.log(`Started instance ${INSTANCE_ID}`);

            // Wait for running state
            await ec2.waitFor('instanceRunning', {
                InstanceIds: [INSTANCE_ID],
                $waiter: { delay: 15, maxAttempts: 20 }
            }).promise();

            // Get updated instance info
            const updatedResponse = await ec2.describeInstances({
                InstanceIds: [INSTANCE_ID]
            }).promise();

            const updatedInstance = updatedResponse.Reservations[0].Instances[0];

            return {
                statusCode: 200,
                body: JSON.stringify({
                    message: 'Instance started successfully',
                    instance_id: INSTANCE_ID,
                    state: 'running',
                    public_ip: updatedInstance.PublicIpAddress,
                    comfyui_url: `http://${updatedInstance.PublicIpAddress}:8188`
                })
            };
        }

        return {
            statusCode: 202,
            body: JSON.stringify({
                message: `Instance is ${currentState}, wait and retry`,
                instance_id: INSTANCE_ID,
                state: currentState
            })
        };

    } catch (error) {
        console.error('Error starting instance:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({
                error: error.message,
                instance_id: INSTANCE_ID
            })
        };
    }
};
```

### 2. Stop GPU Instance Function

**Purpose**: Stop EC2 instance when idle conditions are met

**Python Implementation**:
```python
# lambda_stop_gpu_instance.py
import json
import boto3
import os
from typing import Dict, Any
from datetime import datetime, timedelta

ec2 = boto3.client('ec2', region_name='eu-north-1')
cloudwatch = boto3.client('cloudwatch', region_name='eu-north-1')
INSTANCE_ID = os.environ['GPU_INSTANCE_ID']
GRACE_PERIOD_MINUTES = int(os.environ.get('GRACE_PERIOD_MINUTES', '10'))

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Stop GPU instance after confirming idle state.
    Triggered by CloudWatch alarm when idle conditions persist.
    """
    try:
        # Verify instance is running
        response = ec2.describe_instances(InstanceIds=[INSTANCE_ID])
        instance = response['Reservations'][0]['Instances'][0]
        current_state = instance['State']['Name']

        print(f"Instance {INSTANCE_ID} current state: {current_state}")

        if current_state != 'running':
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': f'Instance already {current_state}, no action needed',
                    'instance_id': INSTANCE_ID,
                    'state': current_state
                })
            }

        # Double-check idle conditions before stopping
        if verify_idle_state(INSTANCE_ID, GRACE_PERIOD_MINUTES):
            # Stop the instance
            ec2.stop_instances(InstanceIds=[INSTANCE_ID])
            print(f"Stopped instance {INSTANCE_ID} after idle confirmation")

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Instance stopped successfully',
                    'instance_id': INSTANCE_ID,
                    'reason': 'Idle conditions verified',
                    'timestamp': datetime.utcnow().isoformat()
                })
            }
        else:
            print(f"Instance {INSTANCE_ID} not idle, skipping shutdown")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Instance active, shutdown cancelled',
                    'instance_id': INSTANCE_ID
                })
            }

    except Exception as e:
        print(f"Error stopping instance: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'instance_id': INSTANCE_ID
            })
        }

def verify_idle_state(instance_id: str, grace_period_minutes: int) -> bool:
    """
    Verify instance is truly idle by checking multiple metrics.
    Returns True only if ALL conditions indicate idle state.
    """
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=grace_period_minutes)

    # Check CPU utilization
    cpu_response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=60,
        Statistics=['Average']
    )

    cpu_datapoints = cpu_response.get('Datapoints', [])
    if cpu_datapoints:
        avg_cpu = sum(dp['Average'] for dp in cpu_datapoints) / len(cpu_datapoints)
        print(f"Average CPU over {grace_period_minutes} min: {avg_cpu:.2f}%")
        if avg_cpu > 5.0:  # More than 5% CPU = active
            return False

    # Check network out (data being sent)
    network_response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='NetworkOut',
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=60,
        Statistics=['Sum']
    )

    network_datapoints = network_response.get('Datapoints', [])
    if network_datapoints:
        total_network = sum(dp['Sum'] for dp in network_datapoints)
        total_mb = total_network / (1024 * 1024)
        print(f"Total network out over {grace_period_minutes} min: {total_mb:.2f} MB")
        if total_mb > 10.0:  # More than 10MB sent = active
            return False

    # Check custom metric: ComfyUI queue depth (if implemented)
    try:
        queue_response = cloudwatch.get_metric_statistics(
            Namespace='ComfyUI',
            MetricName='QueueDepth',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,
            Statistics=['Maximum']
        )

        queue_datapoints = queue_response.get('Datapoints', [])
        if queue_datapoints:
            max_queue = max(dp['Maximum'] for dp in queue_datapoints)
            print(f"Max queue depth over {grace_period_minutes} min: {max_queue}")
            if max_queue > 0:  # Jobs in queue = active
                return False
    except Exception as e:
        print(f"Custom metric check skipped: {str(e)}")

    # All checks passed - instance is idle
    print("All idle conditions verified")
    return True
```

### 3. Health Check Function

**Purpose**: Verify ComfyUI is ready to accept requests after instance start

**Python Implementation**:
```python
# lambda_check_comfyui_health.py
import json
import boto3
import requests
import os
import time
from typing import Dict, Any

ec2 = boto3.client('ec2', region_name='eu-north-1')
INSTANCE_ID = os.environ['GPU_INSTANCE_ID']
COMFYUI_PORT = int(os.environ.get('COMFYUI_PORT', '8188'))
MAX_WAIT_SECONDS = int(os.environ.get('MAX_WAIT_SECONDS', '300'))

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Wait for ComfyUI server to be ready after instance start.
    Returns ComfyUI URL when healthy, error if timeout.
    """
    try:
        # Get instance public IP
        response = ec2.describe_instances(InstanceIds=[INSTANCE_ID])
        instance = response['Reservations'][0]['Instances'][0]
        public_ip = instance.get('PublicIpAddress')

        if not public_ip:
            return {
                'statusCode': 503,
                'body': json.dumps({
                    'error': 'Instance has no public IP yet',
                    'instance_id': INSTANCE_ID
                })
            }

        comfyui_url = f"http://{public_ip}:{COMFYUI_PORT}"
        health_endpoint = f"{comfyui_url}/system_stats"

        # Poll health endpoint with exponential backoff
        start_time = time.time()
        attempt = 1

        while (time.time() - start_time) < MAX_WAIT_SECONDS:
            try:
                print(f"Health check attempt {attempt} for {health_endpoint}")
                response = requests.get(health_endpoint, timeout=5)

                if response.status_code == 200:
                    print(f"ComfyUI is healthy at {comfyui_url}")
                    return {
                        'statusCode': 200,
                        'body': json.dumps({
                            'message': 'ComfyUI is ready',
                            'url': comfyui_url,
                            'health_status': response.json(),
                            'ready_in_seconds': int(time.time() - start_time)
                        })
                    }

            except requests.exceptions.RequestException as e:
                print(f"Health check failed: {str(e)}")

            # Exponential backoff: 5s, 10s, 15s, 20s, 30s, 30s...
            wait_time = min(30, 5 * attempt)
            time.sleep(wait_time)
            attempt += 1

        # Timeout reached
        return {
            'statusCode': 504,
            'body': json.dumps({
                'error': 'ComfyUI health check timeout',
                'url': comfyui_url,
                'timeout_seconds': MAX_WAIT_SECONDS
            })
        }

    except Exception as e:
        print(f"Error checking ComfyUI health: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'instance_id': INSTANCE_ID
            })
        }
```

---

## Idle Detection Strategies

### 1. CPU-Based Idle Detection

**Metric**: `AWS/EC2 CPUUtilization`
**Threshold**: < 5% average over 10 minutes
**Pros**: Simple, built-in metric, no custom code
**Cons**: GPU may be idle while CPU shows activity

**CloudWatch Alarm Configuration**:
```json
{
  "AlarmName": "GPU-Instance-CPU-Idle",
  "ComparisonOperator": "LessThanThreshold",
  "EvaluationPeriods": 2,
  "MetricName": "CPUUtilization",
  "Namespace": "AWS/EC2",
  "Period": 300,
  "Statistic": "Average",
  "Threshold": 5.0,
  "ActionsEnabled": true,
  "AlarmActions": [
    "arn:aws:lambda:eu-north-1:ACCOUNT_ID:function:stop-gpu-instance"
  ],
  "Dimensions": [
    {
      "Name": "InstanceId",
      "Value": "i-xxxxxxxxxxxxx"
    }
  ]
}
```

### 2. Network-Based Idle Detection

**Metric**: `AWS/EC2 NetworkOut`
**Threshold**: < 1 MB total over 10 minutes
**Pros**: Detects when instance stops serving data
**Cons**: Background processes may send data

**CloudWatch Alarm Configuration**:
```json
{
  "AlarmName": "GPU-Instance-Network-Idle",
  "ComparisonOperator": "LessThanThreshold",
  "EvaluationPeriods": 2,
  "MetricName": "NetworkOut",
  "Namespace": "AWS/EC2",
  "Period": 300,
  "Statistic": "Sum",
  "Threshold": 1048576,
  "ActionsEnabled": true,
  "AlarmActions": [
    "arn:aws:lambda:eu-north-1:ACCOUNT_ID:function:stop-gpu-instance"
  ],
  "Dimensions": [
    {
      "Name": "InstanceId",
      "Value": "i-xxxxxxxxxxxxx"
    }
  ]
}
```

### 3. Custom Metric: ComfyUI Queue Depth (RECOMMENDED)

**Metric**: `ComfyUI/QueueDepth`
**Threshold**: 0 jobs for 10 minutes
**Pros**: Most accurate, directly tracks work
**Cons**: Requires custom CloudWatch agent

**Implementation on EC2 Instance**:
```python
# /opt/comfyui_monitor.py
import boto3
import requests
import time
import os

cloudwatch = boto3.client('cloudwatch', region_name='eu-north-1')
INSTANCE_ID = os.environ.get('INSTANCE_ID')
COMFYUI_URL = "http://localhost:8188"

def get_queue_depth():
    """Query ComfyUI API for current queue depth."""
    try:
        response = requests.get(f"{COMFYUI_URL}/queue", timeout=5)
        if response.status_code == 200:
            data = response.json()
            # queue_pending + queue_running
            pending = len(data.get('queue_pending', []))
            running = len(data.get('queue_running', []))
            return pending + running
    except Exception as e:
        print(f"Error getting queue depth: {e}")
    return 0

def put_metric(queue_depth):
    """Send queue depth to CloudWatch."""
    try:
        cloudwatch.put_metric_data(
            Namespace='ComfyUI',
            MetricData=[
                {
                    'MetricName': 'QueueDepth',
                    'Value': queue_depth,
                    'Unit': 'Count',
                    'Dimensions': [
                        {'Name': 'InstanceId', 'Value': INSTANCE_ID}
                    ]
                }
            ]
        )
        print(f"Published queue depth: {queue_depth}")
    except Exception as e:
        print(f"Error publishing metric: {e}")

if __name__ == '__main__':
    # Run every 60 seconds
    while True:
        queue_depth = get_queue_depth()
        put_metric(queue_depth)
        time.sleep(60)
```

**Systemd Service** (`/etc/systemd/system/comfyui-monitor.service`):
```ini
[Unit]
Description=ComfyUI Queue Depth Monitor
After=network.target

[Service]
Type=simple
User=ubuntu
Environment="INSTANCE_ID=i-xxxxxxxxxxxxx"
ExecStart=/usr/bin/python3 /opt/comfyui_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**CloudWatch Alarm for Custom Metric**:
```json
{
  "AlarmName": "GPU-Instance-ComfyUI-Idle",
  "ComparisonOperator": "LessThanOrEqualToThreshold",
  "EvaluationPeriods": 2,
  "MetricName": "QueueDepth",
  "Namespace": "ComfyUI",
  "Period": 300,
  "Statistic": "Maximum",
  "Threshold": 0,
  "ActionsEnabled": true,
  "AlarmActions": [
    "arn:aws:lambda:eu-north-1:ACCOUNT_ID:function:stop-gpu-instance"
  ],
  "Dimensions": [
    {
      "Name": "InstanceId",
      "Value": "i-xxxxxxxxxxxxx"
    }
  ],
  "TreatMissingData": "notBreaching"
}
```

### 4. GPU Utilization Monitoring (Advanced)

**Metric**: `NVIDIA/GPUUtilization` (via CloudWatch agent)
**Threshold**: < 5% for 10 minutes
**Pros**: Direct GPU monitoring
**Cons**: Requires NVIDIA CloudWatch plugin

**CloudWatch Agent Configuration** (`/opt/aws/amazon-cloudwatch-agent/etc/config.json`):
```json
{
  "metrics": {
    "namespace": "NVIDIA",
    "metrics_collected": {
      "nvidia_smi": {
        "measurement": [
          {
            "name": "utilization_gpu",
            "rename": "GPUUtilization",
            "unit": "Percent"
          },
          {
            "name": "memory_used",
            "rename": "GPUMemoryUsed",
            "unit": "Megabytes"
          }
        ],
        "metrics_collection_interval": 60
      }
    }
  }
}
```

### Recommended Multi-Metric Strategy

Use **composite alarm** combining multiple signals:

```python
# Create composite alarm (AWS CLI)
aws cloudwatch put-composite-alarm \
  --alarm-name "GPU-Instance-Truly-Idle" \
  --alarm-rule "ALARM(GPU-Instance-CPU-Idle) AND ALARM(GPU-Instance-Network-Idle) AND ALARM(GPU-Instance-ComfyUI-Idle)" \
  --actions-enabled \
  --alarm-actions "arn:aws:lambda:eu-north-1:ACCOUNT_ID:function:stop-gpu-instance"
```

---

## CloudWatch Alarm Configurations

### Alarm Setup Script

**Bash Script** (`setup_cloudwatch_alarms.sh`):
```bash
#!/bin/bash
# Setup CloudWatch alarms for GPU instance auto-shutdown

INSTANCE_ID="i-xxxxxxxxxxxxx"
LAMBDA_ARN="arn:aws:lambda:eu-north-1:ACCOUNT_ID:function:stop-gpu-instance"
REGION="eu-north-1"

# 1. CPU Idle Alarm
aws cloudwatch put-metric-alarm \
  --region $REGION \
  --alarm-name "GPU-Instance-CPU-Idle" \
  --alarm-description "Trigger when CPU < 5% for 10 minutes" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 5.0 \
  --comparison-operator LessThanThreshold \
  --dimensions Name=InstanceId,Value=$INSTANCE_ID \
  --treat-missing-data notBreaching

# 2. Network Idle Alarm
aws cloudwatch put-metric-alarm \
  --region $REGION \
  --alarm-name "GPU-Instance-Network-Idle" \
  --alarm-description "Trigger when NetworkOut < 1MB for 10 minutes" \
  --metric-name NetworkOut \
  --namespace AWS/EC2 \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 1048576 \
  --comparison-operator LessThanThreshold \
  --dimensions Name=InstanceId,Value=$INSTANCE_ID \
  --treat-missing-data notBreaching

# 3. ComfyUI Queue Idle Alarm
aws cloudwatch put-metric-alarm \
  --region $REGION \
  --alarm-name "GPU-Instance-ComfyUI-Idle" \
  --alarm-description "Trigger when ComfyUI queue = 0 for 10 minutes" \
  --metric-name QueueDepth \
  --namespace ComfyUI \
  --statistic Maximum \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 0 \
  --comparison-operator LessThanOrEqualToThreshold \
  --dimensions Name=InstanceId,Value=$INSTANCE_ID \
  --treat-missing-data notBreaching

# 4. Composite Alarm (ALL conditions must be true)
aws cloudwatch put-composite-alarm \
  --region $REGION \
  --alarm-name "GPU-Instance-Truly-Idle" \
  --alarm-description "Trigger shutdown when ALL idle conditions met" \
  --alarm-rule "ALARM(GPU-Instance-CPU-Idle) AND ALARM(GPU-Instance-Network-Idle) AND ALARM(GPU-Instance-ComfyUI-Idle)" \
  --actions-enabled \
  --alarm-actions $LAMBDA_ARN

echo "CloudWatch alarms configured successfully"
```

### Testing Alarms

**Force Alarm State for Testing**:
```bash
# Test alarm triggers without waiting for real conditions
aws cloudwatch set-alarm-state \
  --alarm-name "GPU-Instance-Truly-Idle" \
  --state-value ALARM \
  --state-reason "Testing auto-shutdown"

# Reset alarm
aws cloudwatch set-alarm-state \
  --alarm-name "GPU-Instance-Truly-Idle" \
  --state-value OK \
  --state-reason "Test complete"
```

---

## n8n Integration Patterns

### 1. n8n Workflow: Start GPU Instance

**Workflow JSON** (`n8n_start_gpu_workflow.json`):
```json
{
  "name": "Start GPU Instance for Image Generation",
  "nodes": [
    {
      "parameters": {
        "method": "POST",
        "url": "https://lambda.eu-north-1.amazonaws.com/2015-03-31/functions/start-gpu-instance/invocations",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "awsApi",
        "options": {
          "timeout": 300000
        }
      },
      "name": "Invoke Start Lambda",
      "type": "n8n-nodes-base.httpRequest",
      "position": [250, 300]
    },
    {
      "parameters": {
        "amount": 30,
        "unit": "seconds"
      },
      "name": "Wait for Instance",
      "type": "n8n-nodes-base.wait",
      "position": [450, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://lambda.eu-north-1.amazonaws.com/2015-03-31/functions/check-comfyui-health/invocations",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "awsApi"
      },
      "name": "Check ComfyUI Health",
      "type": "n8n-nodes-base.httpRequest",
      "position": [650, 300]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{$json.statusCode}}",
              "operation": "equals",
              "value2": "200"
            }
          ]
        }
      },
      "name": "Health OK?",
      "type": "n8n-nodes-base.if",
      "position": [850, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "={{$node['Check ComfyUI Health'].json.body.url}}/prompt",
        "bodyParameters": {
          "parameters": [
            {
              "name": "prompt",
              "value": "={{$json.prompt}}"
            }
          ]
        },
        "options": {
          "timeout": 300000
        }
      },
      "name": "Generate Image",
      "type": "n8n-nodes-base.httpRequest",
      "position": [1050, 200]
    }
  ],
  "connections": {
    "Invoke Start Lambda": {
      "main": [[{"node": "Wait for Instance", "type": "main", "index": 0}]]
    },
    "Wait for Instance": {
      "main": [[{"node": "Check ComfyUI Health", "type": "main", "index": 0}]]
    },
    "Check ComfyUI Health": {
      "main": [[{"node": "Health OK?", "type": "main", "index": 0}]]
    },
    "Health OK?": {
      "main": [
        [{"node": "Generate Image", "type": "main", "index": 0}],
        [{"node": "Wait for Instance", "type": "main", "index": 0}]
      ]
    }
  }
}
```

### 2. n8n HTTP Request Node Configuration

**AWS Lambda Invocation via HTTP**:
```text
Node: HTTP Request
Method: POST
URL: https://lambda.eu-north-1.amazonaws.com/2015-03-31/functions/start-gpu-instance/invocations
Authentication: AWS (IAM)
  - Access Key ID: [From AWS IAM User]
  - Secret Access Key: [From AWS IAM User]
  - Region: eu-north-1
  - Service: lambda
Body:
  {
    "source": "n8n_workflow",
    "request_id": "={{$workflow.id}}"
  }
```

### 3. Alternative: AWS SDK Node

**n8n AWS Lambda Node** (if available):
```text
Node: AWS Lambda
Action: Invoke
Function Name: start-gpu-instance
Invocation Type: RequestResponse
Payload:
  {
    "source": "n8n",
    "workflow_id": "={{$workflow.id}}",
    "trigger_time": "={{$now}}"
  }
Credentials: AWS IAM
```

### 4. Error Handling Pattern

**Retry Logic for Instance Start**:
```json
{
  "name": "Retry Start with Backoff",
  "nodes": [
    {
      "parameters": {
        "functionCode": "const maxRetries = 5;\nconst retryDelay = [5, 10, 20, 40, 60];\n\nfor (let attempt = 0; attempt < maxRetries; attempt++) {\n  try {\n    const response = await $('Invoke Start Lambda').first();\n    if (response.json.statusCode === 200) {\n      return [{json: response.json}];\n    }\n  } catch (error) {\n    console.log(`Attempt ${attempt + 1} failed: ${error.message}`);\n  }\n  \n  if (attempt < maxRetries - 1) {\n    await new Promise(resolve => setTimeout(resolve, retryDelay[attempt] * 1000));\n  }\n}\n\nthrow new Error('Failed to start GPU instance after 5 retries');"
      },
      "name": "Retry Logic",
      "type": "n8n-nodes-base.code"
    }
  ]
}
```

### 5. Cost Tracking Webhook

**Send Cost Alerts to n8n**:
```python
# In Lambda function: notify n8n of instance state changes
import requests

N8N_WEBHOOK_URL = os.environ['N8N_WEBHOOK_URL']

def notify_n8n(event_type, instance_id, details):
    """Send instance state change to n8n for cost tracking."""
    try:
        payload = {
            'event': event_type,
            'instance_id': instance_id,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details
        }
        requests.post(N8N_WEBHOOK_URL, json=payload, timeout=5)
    except Exception as e:
        print(f"Failed to notify n8n: {e}")

# Usage in Lambda
notify_n8n('instance_started', INSTANCE_ID, {
    'public_ip': public_ip,
    'estimated_cost_per_hour': 0.526
})
```

---

## Cost Optimization Calculations

### Current Pricing (EU-North-1 Stockholm, 2025)

| Resource | Type | Cost | Notes |
|----------|------|------|-------|
| **g4dn.xlarge** | On-Demand | $0.526/hour | 4 vCPU, 16GB RAM, 1x NVIDIA T4 |
| **EBS gp3** | 100GB | $0.088/hour ($8/month) | Storage persists when stopped |
| **Data Transfer** | Out to Internet | $0.09/GB | First 1GB/month free |
| **CloudWatch** | Alarms | $0.10/alarm/month | First 10 alarms free |
| **Lambda** | Invocations | $0.20/1M requests | First 1M free |

### Scenarios

#### Scenario 1: 24/7 Running (No Auto-Shutdown)

```text
Monthly Cost Calculation:
- Instance: $0.526/hour × 730 hours = $384.00
- EBS: $8.00
- CloudWatch: $0.00 (under free tier)
- Lambda: $0.00 (under free tier)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: $392.00/month
```

**Result**: EXCEEDS BUDGET ($150 peak limit)

#### Scenario 2: Aggressive Auto-Shutdown (2 hours/day avg)

```text
Assumptions:
- 10 image generation sessions/day
- Each session: 10 minutes active + 2 minutes startup
- Total runtime: 120 minutes/day (2 hours)

Monthly Cost Calculation:
- Instance: $0.526/hour × 60 hours = $31.56
- EBS: $8.00
- CloudWatch: $0.00 (4 alarms, under free tier)
- Lambda: $0.00 (~300 invocations/month, under free tier)
- Data Transfer: $0.45 (5GB/month @ $0.09/GB)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: $40.01/month (90% savings vs 24/7)
```

**Result**: WELL UNDER BUDGET ($50 normal limit)

#### Scenario 3: Moderate Use (4 hours/day avg)

```text
Assumptions:
- 20 sessions/day
- Each session: 10 minutes active + 2 minutes startup
- Total runtime: 240 minutes/day (4 hours)

Monthly Cost Calculation:
- Instance: $0.526/hour × 120 hours = $63.12
- EBS: $8.00
- CloudWatch: $0.00
- Lambda: $0.00 (~600 invocations/month)
- Data Transfer: $0.90 (10GB/month)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: $72.02/month (82% savings vs 24/7)
```

**Result**: EXCEEDS NORMAL ($50), UNDER PEAK ($150)

#### Scenario 4: Peak Use (8 hours/day avg)

```text
Assumptions:
- 40 sessions/day
- Each session: 10 minutes active + 2 minutes startup
- Total runtime: 480 minutes/day (8 hours)

Monthly Cost Calculation:
- Instance: $0.526/hour × 240 hours = $126.24
- EBS: $8.00
- CloudWatch: $0.00
- Lambda: $0.00 (~1,200 invocations/month)
- Data Transfer: $1.80 (20GB/month)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: $136.04/month (66% savings vs 24/7)
```

**Result**: UNDER PEAK BUDGET ($150)

### Savings Summary

| Scenario | Avg Hours/Day | Monthly Cost | Savings vs 24/7 | Within Budget? |
|----------|---------------|--------------|-----------------|----------------|
| 24/7 Running | 24 | $392.00 | 0% | NO |
| Aggressive | 2 | $40.01 | 90% | YES ($50 normal) |
| Moderate | 4 | $72.02 | 82% | YES ($150 peak) |
| Peak | 8 | $136.04 | 66% | YES ($150 peak) |

**Key Insight**: Auto-shutdown enables 60-90% cost savings while staying within budget.

---

## Implementation Checklist

### Phase 1: AWS Lambda Setup

- [ ] Create IAM role for Lambda with EC2 permissions
  ```bash
  aws iam create-role --role-name lambda-ec2-control \
    --assume-role-policy-document file://lambda-trust-policy.json

  aws iam attach-role-policy --role-name lambda-ec2-control \
    --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess

  aws iam attach-role-policy --role-name lambda-ec2-control \
    --policy-arn arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess
  ```

- [ ] Deploy `lambda_start_gpu_instance.py` function
  ```bash
  zip lambda_start.zip lambda_start_gpu_instance.py

  aws lambda create-function \
    --function-name start-gpu-instance \
    --runtime python3.11 \
    --role arn:aws:iam::ACCOUNT_ID:role/lambda-ec2-control \
    --handler lambda_start_gpu_instance.lambda_handler \
    --zip-file fileb://lambda_start.zip \
    --timeout 300 \
    --environment Variables="{GPU_INSTANCE_ID=i-xxxxxxxxxxxxx}"
  ```

- [ ] Deploy `lambda_stop_gpu_instance.py` function
  ```bash
  zip lambda_stop.zip lambda_stop_gpu_instance.py

  aws lambda create-function \
    --function-name stop-gpu-instance \
    --runtime python3.11 \
    --role arn:aws:iam::ACCOUNT_ID:role/lambda-ec2-control \
    --handler lambda_stop_gpu_instance.lambda_handler \
    --zip-file fileb://lambda_stop.zip \
    --timeout 60 \
    --environment Variables="{GPU_INSTANCE_ID=i-xxxxxxxxxxxxx,GRACE_PERIOD_MINUTES=10}"
  ```

- [ ] Deploy `lambda_check_comfyui_health.py` function
  ```bash
  # Package with requests library
  mkdir lambda_health_package
  pip install requests -t lambda_health_package/
  cp lambda_check_comfyui_health.py lambda_health_package/
  cd lambda_health_package && zip -r ../lambda_health.zip . && cd ..

  aws lambda create-function \
    --function-name check-comfyui-health \
    --runtime python3.11 \
    --role arn:aws:iam::ACCOUNT_ID:role/lambda-ec2-control \
    --handler lambda_check_comfyui_health.lambda_handler \
    --zip-file fileb://lambda_health.zip \
    --timeout 300 \
    --environment Variables="{GPU_INSTANCE_ID=i-xxxxxxxxxxxxx,MAX_WAIT_SECONDS=300}"
  ```

- [ ] Test Lambda functions manually
  ```bash
  aws lambda invoke --function-name start-gpu-instance output.json
  cat output.json
  ```

### Phase 2: EC2 Instance Setup

- [ ] Launch g4dn.xlarge instance in EU-North-1
  ```bash
  aws ec2 run-instances \
    --image-id ami-xxxxxxxxx \  # Ubuntu 22.04 with NVIDIA drivers
    --instance-type g4dn.xlarge \
    --key-name your-keypair \
    --security-group-ids sg-xxxxxxxxx \
    --subnet-id subnet-xxxxxxxxx \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=ComfyUI-GPU},{Key=AutoShutdown,Value=true}]'
  ```

- [ ] Install ComfyUI and dependencies
- [ ] Configure ComfyUI to start on boot
  ```bash
  sudo systemctl enable comfyui.service
  ```

- [ ] Install custom CloudWatch monitoring script
  ```bash
  sudo cp comfyui_monitor.py /opt/
  sudo cp comfyui-monitor.service /etc/systemd/system/
  sudo systemctl enable comfyui-monitor.service
  sudo systemctl start comfyui-monitor.service
  ```

- [ ] Verify custom metrics appear in CloudWatch
  ```bash
  aws cloudwatch get-metric-statistics \
    --namespace ComfyUI \
    --metric-name QueueDepth \
    --dimensions Name=InstanceId,Value=i-xxxxxxxxxxxxx \
    --start-time $(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 60 \
    --statistics Maximum
  ```

### Phase 3: CloudWatch Alarms

- [ ] Create CPU idle alarm
- [ ] Create network idle alarm
- [ ] Create ComfyUI queue idle alarm
- [ ] Create composite alarm
- [ ] Run `setup_cloudwatch_alarms.sh` script
- [ ] Test alarms with `set-alarm-state` command

### Phase 4: n8n Integration

- [ ] Create AWS IAM user for n8n with Lambda invoke permissions
  ```bash
  aws iam create-user --user-name n8n-lambda-invoker

  aws iam create-access-key --user-name n8n-lambda-invoker

  aws iam attach-user-policy --user-name n8n-lambda-invoker \
    --policy-arn arn:aws:iam::aws:policy/AWSLambda_FullAccess
  ```

- [ ] Add AWS credentials to n8n
- [ ] Import `n8n_start_gpu_workflow.json` workflow
- [ ] Configure HTTP Request nodes with Lambda URLs
- [ ] Test end-to-end workflow
- [ ] Add error handling and retries

### Phase 5: Monitoring & Optimization

- [ ] Set up CloudWatch dashboard for costs
  ```bash
  # Dashboard config in AWS Console:
  # - EC2 instance running hours
  # - Lambda invocation count
  # - Alarm state timeline
  # - ComfyUI queue depth
  ```

- [ ] Configure AWS Budget alerts
  ```bash
  aws budgets create-budget \
    --account-id ACCOUNT_ID \
    --budget file://budget-config.json \
    --notifications-with-subscribers file://budget-notifications.json
  ```

- [ ] Review costs weekly
- [ ] Adjust idle timeout if needed (10 min → 5 min for more savings)

---

## Best Practices

### 1. Security

**IAM Least Privilege**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ec2:DescribeInstances",
        "ec2:DescribeInstanceStatus"
      ],
      "Resource": "arn:aws:ec2:eu-north-1:ACCOUNT_ID:instance/i-xxxxxxxxxxxxx"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:GetMetricStatistics",
        "cloudwatch:DescribeAlarms"
      ],
      "Resource": "*"
    }
  ]
}
```

**Restrict Lambda Invocation**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "events.amazonaws.com"
      },
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:eu-north-1:ACCOUNT_ID:function:stop-gpu-instance",
      "Condition": {
        "ArnLike": {
          "AWS:SourceArn": "arn:aws:cloudwatch:eu-north-1:ACCOUNT_ID:alarm:*"
        }
      }
    }
  ]
}
```

### 2. Reliability

**Add SNS Notifications for Failures**:
```python
# In Lambda function
import boto3
sns = boto3.client('sns', region_name='eu-north-1')
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def notify_failure(error_message):
    """Send SNS notification on Lambda failure."""
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject='GPU Instance Control FAILURE',
        Message=f"Lambda function failed: {error_message}"
    )
```

**Implement Dead Letter Queue**:
```bash
aws sqs create-queue --queue-name lambda-gpu-control-dlq

aws lambda update-function-configuration \
  --function-name stop-gpu-instance \
  --dead-letter-config TargetArn=arn:aws:sqs:eu-north-1:ACCOUNT_ID:lambda-gpu-control-dlq
```

### 3. Cost Monitoring

**Create Cost Anomaly Detection**:
```bash
aws ce create-anomaly-monitor \
  --anomaly-monitor Name=GPU-Instance-Costs,MonitorType=DIMENSIONAL \
  --monitor-specification file://anomaly-monitor-config.json

aws ce create-anomaly-subscription \
  --anomaly-subscription Name=GPU-Cost-Alerts \
  --subscription file://anomaly-subscription-config.json
```

**Budget Alert Configuration** (`budget-config.json`):
```json
{
  "BudgetName": "GPU-Instance-Monthly-Budget",
  "BudgetLimit": {
    "Amount": "150",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST",
  "CostFilters": {
    "TagKeyValue": ["user:Project$ComfyUI-GPU"]
  }
}
```

### 4. Graceful Shutdown

**Add Shutdown Hook to ComfyUI**:
```python
# /opt/comfyui_shutdown_hook.py
import signal
import sys
import time
import requests

def graceful_shutdown(signum, frame):
    """Wait for queue to drain before allowing shutdown."""
    print("Shutdown signal received, checking queue...")

    while True:
        try:
            response = requests.get("http://localhost:8188/queue", timeout=5)
            data = response.json()
            queue_size = len(data.get('queue_pending', [])) + len(data.get('queue_running', []))

            if queue_size == 0:
                print("Queue empty, allowing shutdown")
                sys.exit(0)
            else:
                print(f"Queue has {queue_size} jobs, waiting...")
                time.sleep(30)
        except Exception as e:
            print(f"Error checking queue: {e}")
            sys.exit(1)

signal.signal(signal.SIGTERM, graceful_shutdown)
signal.pause()
```

### 5. Testing Strategy

**Test Checklist**:
```bash
# 1. Manual start/stop
aws lambda invoke --function-name start-gpu-instance test_output.json
aws lambda invoke --function-name stop-gpu-instance test_output.json

# 2. Verify instance state transitions
aws ec2 describe-instances --instance-ids i-xxxxxxxxxxxxx \
  --query 'Reservations[0].Instances[0].State.Name'

# 3. Test alarm triggers
aws cloudwatch set-alarm-state --alarm-name "GPU-Instance-Truly-Idle" \
  --state-value ALARM --state-reason "Test"

# 4. End-to-end n8n workflow test
# (Execute workflow in n8n UI with test payload)

# 5. Cost validation
aws ce get-cost-and-usage \
  --time-period Start=2025-12-01,End=2025-12-24 \
  --granularity DAILY \
  --metrics BlendedCost \
  --filter file://cost-filter.json
```

### 6. Documentation

**Runbook Template**:
```markdown
# GPU Instance Control Runbook

## Emergency Procedures

### Instance Won't Start
1. Check Lambda logs: `aws logs tail /aws/lambda/start-gpu-instance --follow`
2. Verify IAM permissions on Lambda role
3. Check instance limits in EC2 quota dashboard
4. Manual start: `aws ec2 start-instances --instance-ids i-xxxxxxxxxxxxx`

### Instance Won't Stop
1. Check Lambda logs: `aws logs tail /aws/lambda/stop-gpu-instance --follow`
2. Verify CloudWatch alarms: `aws cloudwatch describe-alarms`
3. Manual stop: `aws ec2 stop-instances --instance-ids i-xxxxxxxxxxxxx`

### Unexpected Costs
1. Check current instance state: `aws ec2 describe-instances --instance-ids i-xxxxxxxxxxxxx`
2. Review CloudWatch alarm history
3. Check for stuck instances: `aws ec2 describe-instances --filters "Name=tag:AutoShutdown,Values=true"`
4. Force stop if necessary

## Maintenance

### Update Lambda Functions
```bash
# Update code
zip lambda_start.zip lambda_start_gpu_instance.py
aws lambda update-function-code --function-name start-gpu-instance --zip-file fileb://lambda_start.zip
```

### Adjust Idle Timeout
```bash
# Change grace period from 10 min to 5 min
aws lambda update-function-configuration \
  --function-name stop-gpu-instance \
  --environment Variables="{GPU_INSTANCE_ID=i-xxxxxxxxxxxxx,GRACE_PERIOD_MINUTES=5}"
```
```

---

## Quick Start Commands

### Deploy Everything (One-Shot Script)

**`deploy_gpu_autoshutdown.sh`**:
```bash
#!/bin/bash
set -e

echo "Deploying GPU Auto-Shutdown System..."

# Variables
REGION="eu-north-1"
INSTANCE_ID="i-xxxxxxxxxxxxx"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# 1. Create IAM role
echo "Creating IAM role..."
aws iam create-role --role-name lambda-ec2-control \
  --assume-role-policy-document file://lambda-trust-policy.json || true

aws iam attach-role-policy --role-name lambda-ec2-control \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess || true

aws iam attach-role-policy --role-name lambda-ec2-control \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess || true

ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/lambda-ec2-control"

# Wait for role to propagate
sleep 10

# 2. Deploy Lambda functions
echo "Deploying Lambda functions..."

# Start function
zip -j lambda_start.zip lambda_start_gpu_instance.py
aws lambda create-function \
  --function-name start-gpu-instance \
  --runtime python3.11 \
  --role $ROLE_ARN \
  --handler lambda_start_gpu_instance.lambda_handler \
  --zip-file fileb://lambda_start.zip \
  --timeout 300 \
  --environment Variables="{GPU_INSTANCE_ID=${INSTANCE_ID}}" \
  --region $REGION || \
aws lambda update-function-code \
  --function-name start-gpu-instance \
  --zip-file fileb://lambda_start.zip \
  --region $REGION

# Stop function
zip -j lambda_stop.zip lambda_stop_gpu_instance.py
aws lambda create-function \
  --function-name stop-gpu-instance \
  --runtime python3.11 \
  --role $ROLE_ARN \
  --handler lambda_stop_gpu_instance.lambda_handler \
  --zip-file fileb://lambda_stop.zip \
  --timeout 60 \
  --environment Variables="{GPU_INSTANCE_ID=${INSTANCE_ID},GRACE_PERIOD_MINUTES=10}" \
  --region $REGION || \
aws lambda update-function-code \
  --function-name stop-gpu-instance \
  --zip-file fileb://lambda_stop.zip \
  --region $REGION

# Health check function
mkdir -p lambda_health_package
pip install requests -t lambda_health_package/ -q
cp lambda_check_comfyui_health.py lambda_health_package/
cd lambda_health_package && zip -r ../lambda_health.zip . > /dev/null && cd ..
aws lambda create-function \
  --function-name check-comfyui-health \
  --runtime python3.11 \
  --role $ROLE_ARN \
  --handler lambda_check_comfyui_health.lambda_handler \
  --zip-file fileb://lambda_health.zip \
  --timeout 300 \
  --environment Variables="{GPU_INSTANCE_ID=${INSTANCE_ID},MAX_WAIT_SECONDS=300}" \
  --region $REGION || \
aws lambda update-function-code \
  --function-name check-comfyui-health \
  --zip-file fileb://lambda_health.zip \
  --region $REGION

# 3. Create CloudWatch alarms
echo "Creating CloudWatch alarms..."
bash setup_cloudwatch_alarms.sh

echo "✓ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Install comfyui_monitor.py on EC2 instance"
echo "2. Configure n8n workflows"
echo "3. Test with: aws lambda invoke --function-name start-gpu-instance output.json"
```

---

## Summary

### Key Takeaways

1. **Cost Savings**: 60-90% reduction with aggressive auto-shutdown
2. **Recommended Strategy**: Composite alarm (CPU + Network + ComfyUI queue)
3. **Optimal Timeout**: 10 minutes idle detection, 5-10 minute grace period
4. **Integration**: n8n triggers Lambda → Lambda controls EC2 → CloudWatch monitors
5. **Budget Compliance**: Easily stay under $50/month normal, $150/month peak

### Implementation Priority

| Priority | Task | Impact |
|----------|------|--------|
| **P0** | Deploy Lambda start/stop functions | Core functionality |
| **P0** | Create composite CloudWatch alarm | Reliable idle detection |
| **P1** | Install ComfyUI queue monitor | Accurate shutdown timing |
| **P1** | Integrate with n8n workflows | End-to-end automation |
| **P2** | Set up cost monitoring dashboards | Budget tracking |
| **P2** | Configure SNS failure alerts | Reliability |

### Next Steps

1. Review Lambda function code and customize for your instance ID
2. Deploy Phase 1 (Lambda functions) using provided scripts
3. Set up EC2 instance with ComfyUI and monitoring agent
4. Create CloudWatch alarms
5. Test manually before integrating with n8n
6. Monitor costs for first week and adjust timeouts if needed

---

**For questions or issues, refer to AWS documentation:**
- [Lambda with EC2](https://docs.aws.amazon.com/lambda/latest/dg/services-ec2.html)
- [CloudWatch Alarms](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html)
- [EC2 Instance Lifecycle](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html)
