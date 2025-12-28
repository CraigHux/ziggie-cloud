#!/usr/bin/env python3
"""
AWS Lambda Function: Stop GPU Instance
Purpose: Stop EC2 instance after confirming idle state
Triggered by: CloudWatch composite alarm
"""

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
    Double-checks idle conditions before stopping to prevent premature shutdown.

    Returns:
        - 200: Instance stopped or already stopped
        - 500: Error occurred
    """
    try:
        print(f"Checking idle state for instance: {INSTANCE_ID}")

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
        is_idle = verify_idle_state(INSTANCE_ID, GRACE_PERIOD_MINUTES)

        if is_idle:
            # Stop the instance
            ec2.stop_instances(InstanceIds=[INSTANCE_ID])
            print(f"Stopped instance {INSTANCE_ID} after idle confirmation")

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Instance stopped successfully',
                    'instance_id': INSTANCE_ID,
                    'reason': 'Idle conditions verified',
                    'timestamp': datetime.utcnow().isoformat(),
                    'grace_period_minutes': GRACE_PERIOD_MINUTES
                })
            }
        else:
            print(f"Instance {INSTANCE_ID} not idle, skipping shutdown")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Instance active, shutdown cancelled',
                    'instance_id': INSTANCE_ID,
                    'reason': 'Idle verification failed'
                })
            }

    except Exception as e:
        error_message = str(e)
        print(f"Error stopping instance: {error_message}")

        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': error_message,
                'instance_id': INSTANCE_ID
            })
        }


def verify_idle_state(instance_id: str, grace_period_minutes: int) -> bool:
    """
    Verify instance is truly idle by checking multiple metrics.
    Returns True only if ALL conditions indicate idle state.

    Checks:
    1. CPU utilization < 5%
    2. Network output < 10MB
    3. ComfyUI queue depth = 0
    """
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=grace_period_minutes)

    print(f"Verifying idle state from {start_time} to {end_time}")

    # Check 1: CPU utilization
    try:
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

            if avg_cpu > 5.0:
                print(f"CPU too high ({avg_cpu:.2f}%), instance is active")
                return False
        else:
            print("No CPU datapoints, assuming active")
            return False

    except Exception as e:
        print(f"Error checking CPU metric: {e}")
        return False

    # Check 2: Network output
    try:
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

            if total_mb > 10.0:
                print(f"Network too high ({total_mb:.2f} MB), instance is active")
                return False

    except Exception as e:
        print(f"Error checking network metric: {e}")
        # Don't fail on network check - it's less critical than CPU

    # Check 3: ComfyUI queue depth (custom metric)
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

            if max_queue > 0:
                print(f"Queue not empty ({max_queue} jobs), instance is active")
                return False
        else:
            print("No ComfyUI queue datapoints (metric may not be configured)")
            # Don't fail if custom metric is missing - CPU is sufficient

    except Exception as e:
        print(f"Custom metric check skipped: {e}")

    # All checks passed - instance is idle
    print("All idle conditions verified, safe to stop")
    return True
