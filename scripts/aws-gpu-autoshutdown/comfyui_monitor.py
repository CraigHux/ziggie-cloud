#!/usr/bin/env python3
"""
ComfyUI Queue Depth Monitor
Purpose: Publish custom CloudWatch metric for accurate idle detection
Deployment: Run as systemd service on EC2 instance
"""

import boto3
import requests
import time
import os
import sys
from datetime import datetime

# Configuration
REGION = 'eu-north-1'
INSTANCE_ID = os.environ.get('INSTANCE_ID')
COMFYUI_URL = os.environ.get('COMFYUI_URL', 'http://localhost:8188')
METRIC_INTERVAL_SECONDS = 60

# Initialize CloudWatch client
cloudwatch = boto3.client('cloudwatch', region_name=REGION)

def get_queue_depth():
    """Query ComfyUI API for current queue depth."""
    try:
        response = requests.get(f"{COMFYUI_URL}/queue", timeout=5)

        if response.status_code == 200:
            data = response.json()

            # Count pending and running jobs
            pending = len(data.get('queue_pending', []))
            running = len(data.get('queue_running', []))
            total = pending + running

            print(f"[{datetime.now().isoformat()}] Queue depth: {total} (pending={pending}, running={running})")
            return total
        else:
            print(f"[{datetime.now().isoformat()}] ComfyUI API returned status {response.status_code}")
            return 0

    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now().isoformat()}] Error getting queue depth: {e}")
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
                    'Timestamp': datetime.utcnow(),
                    'Dimensions': [
                        {
                            'Name': 'InstanceId',
                            'Value': INSTANCE_ID
                        }
                    ]
                }
            ]
        )
        print(f"[{datetime.now().isoformat()}] Published queue depth metric: {queue_depth}")
        return True

    except Exception as e:
        print(f"[{datetime.now().isoformat()}] Error publishing metric: {e}")
        return False


def main():
    """Main monitoring loop."""
    if not INSTANCE_ID:
        print("ERROR: INSTANCE_ID environment variable not set")
        sys.exit(1)

    print(f"Starting ComfyUI queue depth monitor")
    print(f"Instance ID: {INSTANCE_ID}")
    print(f"ComfyUI URL: {COMFYUI_URL}")
    print(f"Metric interval: {METRIC_INTERVAL_SECONDS}s")
    print(f"Region: {REGION}")
    print("-" * 60)

    # Run monitoring loop
    while True:
        try:
            # Get current queue depth
            queue_depth = get_queue_depth()

            # Publish to CloudWatch
            put_metric(queue_depth)

            # Wait before next check
            time.sleep(METRIC_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("\nShutting down monitor...")
            break

        except Exception as e:
            print(f"[{datetime.now().isoformat()}] Unexpected error: {e}")
            # Continue running even if error occurs
            time.sleep(METRIC_INTERVAL_SECONDS)


if __name__ == '__main__':
    main()
