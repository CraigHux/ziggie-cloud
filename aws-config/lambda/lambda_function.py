# lambda_function.py - Auto-shutdown idle GPU instances
# Ziggie Ecosystem - GPU Cost Control
import boto3
from datetime import datetime, timedelta
import json

def lambda_handler(event, context):
    """
    Auto-shutdown GPU instances that have been idle for 15+ minutes.
    Triggered by CloudWatch Events every 5 minutes.

    Looks for instances with tags:
    - Project: Ziggie
    - Type: GPU
    """
    ec2 = boto3.client('ec2', region_name='eu-north-1')
    cloudwatch = boto3.client('cloudwatch', region_name='eu-north-1')
    sns = boto3.client('sns', region_name='eu-north-1')

    SNS_TOPIC_ARN = 'arn:aws:sns:eu-north-1:785186659442:ziggie-alerts'
    IDLE_THRESHOLD_PERCENT = 5.0  # CPU < 5% = idle
    IDLE_CHECK_MINUTES = 15

    print(f"Starting GPU idle check at {datetime.utcnow().isoformat()}")

    # Find running instances tagged with Project=Ziggie and Type=GPU
    try:
        response = ec2.describe_instances(
            Filters=[
                {'Name': 'instance-state-name', 'Values': ['running']},
                {'Name': 'tag:Project', 'Values': ['Ziggie']},
                {'Name': 'tag:Type', 'Values': ['GPU']}
            ]
        )
    except Exception as e:
        print(f"Error describing instances: {e}")
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }

    instances_to_stop = []
    instances_checked = 0

    for reservation in response.get('Reservations', []):
        for instance in reservation.get('Instances', []):
            instance_id = instance['InstanceId']
            instances_checked += 1

            # Get instance name from tags
            instance_name = 'Unknown'
            for tag in instance.get('Tags', []):
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']
                    break

            print(f"Checking instance {instance_id} ({instance_name})")

            # Check CPU utilization over last 15 minutes
            try:
                metrics = cloudwatch.get_metric_statistics(
                    Namespace='AWS/EC2',
                    MetricName='CPUUtilization',
                    Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                    StartTime=datetime.utcnow() - timedelta(minutes=IDLE_CHECK_MINUTES),
                    EndTime=datetime.utcnow(),
                    Period=300,  # 5 minutes
                    Statistics=['Average']
                )
            except Exception as e:
                print(f"Error getting metrics for {instance_id}: {e}")
                continue

            if metrics.get('Datapoints'):
                avg_cpu = sum(d['Average'] for d in metrics['Datapoints']) / len(metrics['Datapoints'])
                print(f"Instance {instance_id} CPU: {avg_cpu:.1f}%")

                # If average CPU < threshold over check period, consider idle
                if avg_cpu < IDLE_THRESHOLD_PERCENT:
                    instances_to_stop.append({
                        'id': instance_id,
                        'name': instance_name,
                        'cpu': avg_cpu
                    })
                    print(f"Instance {instance_id} marked for shutdown (idle)")
            else:
                print(f"No metrics available for {instance_id}")

    print(f"Checked {instances_checked} instances, {len(instances_to_stop)} idle")

    # Stop idle instances
    if instances_to_stop:
        instance_ids = [i['id'] for i in instances_to_stop]

        try:
            ec2.stop_instances(InstanceIds=instance_ids)
            print(f"Stopped instances: {instance_ids}")

            # Build notification message
            details = "\n".join([
                f"- {i['name']} ({i['id']}): CPU {i['cpu']:.1f}%"
                for i in instances_to_stop
            ])

            # Send notification
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject='Ziggie GPU Auto-Shutdown Alert',
                Message=f"""Ziggie GPU Auto-Shutdown triggered at {datetime.utcnow().isoformat()}

Stopped {len(instances_to_stop)} idle GPU instance(s):

{details}

These instances were idle (CPU < {IDLE_THRESHOLD_PERCENT}%) for {IDLE_CHECK_MINUTES}+ minutes.

To restart, use: aws ec2 start-instances --instance-ids <id>
"""
            )
            print("Notification sent")

        except Exception as e:
            print(f"Error stopping instances: {e}")
            return {
                'statusCode': 500,
                'body': f'Error stopping instances: {str(e)}'
            }

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Stopped {len(instances_to_stop)} idle instances',
                'instances': instance_ids
            })
        }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'No idle instances found',
            'checked': instances_checked
        })
    }
