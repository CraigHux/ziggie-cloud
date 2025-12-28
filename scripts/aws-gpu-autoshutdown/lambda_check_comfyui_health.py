#!/usr/bin/env python3
"""
AWS Lambda Function: Check ComfyUI Health
Purpose: Verify ComfyUI is ready to accept requests after instance start
Triggered by: n8n workflow after instance start
"""

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
    Polls health endpoint with exponential backoff.

    Returns:
        - 200: ComfyUI is healthy and ready
        - 503: Instance has no public IP yet
        - 504: Health check timeout
        - 500: Error occurred
    """
    try:
        print(f"Checking ComfyUI health for instance: {INSTANCE_ID}")

        # Get instance public IP
        response = ec2.describe_instances(InstanceIds=[INSTANCE_ID])
        instance = response['Reservations'][0]['Instances'][0]
        public_ip = instance.get('PublicIpAddress')

        if not public_ip:
            return {
                'statusCode': 503,
                'body': json.dumps({
                    'error': 'Instance has no public IP yet',
                    'instance_id': INSTANCE_ID,
                    'state': instance['State']['Name'],
                    'retry_in_seconds': 15
                })
            }

        comfyui_url = f"http://{public_ip}:{COMFYUI_PORT}"
        health_endpoint = f"{comfyui_url}/system_stats"

        print(f"Health checking ComfyUI at: {health_endpoint}")

        # Poll health endpoint with exponential backoff
        start_time = time.time()
        attempt = 1

        while (time.time() - start_time) < MAX_WAIT_SECONDS:
            try:
                print(f"Health check attempt {attempt} for {health_endpoint}")

                response = requests.get(health_endpoint, timeout=5)

                if response.status_code == 200:
                    elapsed = int(time.time() - start_time)
                    print(f"ComfyUI is healthy at {comfyui_url} (ready in {elapsed}s)")

                    return {
                        'statusCode': 200,
                        'body': json.dumps({
                            'message': 'ComfyUI is ready',
                            'url': comfyui_url,
                            'public_ip': public_ip,
                            'health_status': response.json(),
                            'ready_in_seconds': elapsed,
                            'attempts': attempt
                        })
                    }

            except requests.exceptions.RequestException as e:
                print(f"Health check failed (attempt {attempt}): {str(e)}")

            # Exponential backoff: 5s, 10s, 15s, 20s, 30s, 30s...
            wait_time = min(30, 5 * attempt)
            print(f"Waiting {wait_time}s before next attempt...")
            time.sleep(wait_time)
            attempt += 1

        # Timeout reached
        elapsed = int(time.time() - start_time)
        print(f"ComfyUI health check timeout after {elapsed}s ({attempt} attempts)")

        return {
            'statusCode': 504,
            'body': json.dumps({
                'error': 'ComfyUI health check timeout',
                'url': comfyui_url,
                'timeout_seconds': MAX_WAIT_SECONDS,
                'elapsed_seconds': elapsed,
                'attempts': attempt,
                'suggestion': 'Check ComfyUI logs on EC2 instance'
            })
        }

    except Exception as e:
        error_message = str(e)
        print(f"Error checking ComfyUI health: {error_message}")

        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': error_message,
                'instance_id': INSTANCE_ID
            })
        }
