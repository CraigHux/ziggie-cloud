#!/usr/bin/env python3
"""
AWS Lambda Function: Start GPU Instance
Purpose: Start EC2 g4dn.xlarge instance when ComfyUI image generation is requested
Triggered by: n8n workflow HTTP request
"""

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

    Returns:
        - 200: Instance running with public IP
        - 202: Instance starting, retry needed
        - 500: Error occurred
    """
    try:
        print(f"Starting GPU instance: {INSTANCE_ID}")

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
                    'public_ip': instance.get('PublicIpAddress', 'pending'),
                    'comfyui_url': f"http://{instance.get('PublicIpAddress')}:8188"
                })
            }

        # Start the instance if stopped
        if current_state == 'stopped':
            ec2.start_instances(InstanceIds=[INSTANCE_ID])
            print(f"Started instance {INSTANCE_ID}")

            # Wait for instance to be running (with timeout)
            waiter = ec2.get_waiter('instance_running')
            waiter.wait(
                InstanceIds=[INSTANCE_ID],
                WaiterConfig={
                    'Delay': 15,        # Check every 15 seconds
                    'MaxAttempts': 20   # 5 minute timeout (15s × 20)
                }
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
                    'comfyui_url': f"http://{instance.get('PublicIpAddress')}:8188",
                    'started_at': instance['LaunchTime'].isoformat()
                })
            }

        # Instance is in transition state (starting, stopping, etc.)
        return {
            'statusCode': 202,
            'body': json.dumps({
                'message': f'Instance is {current_state}, wait and retry',
                'instance_id': INSTANCE_ID,
                'state': current_state,
                'retry_in_seconds': 30
            })
        }

    except Exception as e:
        error_message = str(e)
        print(f"Error starting instance: {error_message}")

        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': error_message,
                'instance_id': INSTANCE_ID
            })
        }
