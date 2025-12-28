# AI Cloud Infrastructure - Quick Reference

> **Quick access commands and patterns for AI-controlled AWS and Hostinger infrastructure**

---

## AWS Quick Commands

### Start/Stop EC2 Instance
```python
import boto3
ec2 = boto3.client('ec2', region_name='eu-north-1')

# Start
ec2.start_instances(InstanceIds=['i-0123456789abcdef'])

# Stop
ec2.stop_instances(InstanceIds=['i-0123456789abcdef'])

# Status
response = ec2.describe_instances(InstanceIds=['i-0123456789abcdef'])
state = response['Reservations'][0]['Instances'][0]['State']['Name']
```

### Upload/Download S3
```python
s3 = boto3.client('s3', region_name='eu-north-1')

# Upload
s3.upload_file('local.txt', 'bucket-name', 'remote.txt')

# Download
s3.download_file('bucket-name', 'remote.txt', 'local.txt')
```

### Get Secret
```python
secrets = boto3.client('secretsmanager', region_name='eu-north-1')
response = secrets.get_secret_value(SecretId='ziggie/api-key')
secret = json.loads(response['SecretString'])
```

---

## Hostinger Quick Commands

### SSH Command Execution
```python
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('vps.example.com', username='root', key_filename='/path/to/key')

stdin, stdout, stderr = ssh.exec_command('systemctl status nginx')
print(stdout.read().decode())

ssh.close()
```

### Fabric Deployment
```python
from fabric import Connection

conn = Connection('vps.example.com', user='root', connect_kwargs={'key_filename': '/path/to/key'})

# Upload and extract
conn.put('app.tar.gz', '/tmp/')
conn.run('tar -xzf /tmp/app.tar.gz -C /var/www/')

# Restart service
conn.sudo('systemctl restart app')
```

### Hostinger API
```python
import requests

headers = {'Authorization': 'Bearer YOUR_API_TOKEN'}
response = requests.get('https://api.hostinger.com/v1/vps', headers=headers)
vps_list = response.json()
```

---

## IAM Best Practices Checklist

- [ ] Use IAM roles for EC2/Lambda (not access keys)
- [ ] Grant minimum permissions required
- [ ] Use resource tags to restrict access (`ec2:ResourceTag/Project`)
- [ ] Store credentials in AWS Secrets Manager
- [ ] Enable CloudTrail for audit logging
- [ ] Rotate access keys every 90 days
- [ ] Use MFA for production accounts

---

## Cost Tracking

```python
import boto3
from datetime import datetime

ce = boto3.client('ce', region_name='us-east-1')

# Get current month cost
now = datetime.utcnow()
response = ce.get_cost_and_usage(
    TimePeriod={
        'Start': f'{now.year}-{now.month:02d}-01',
        'End': f'{now.year}-{now.month:02d}-{now.day:02d}'
    },
    Granularity='MONTHLY',
    Metrics=['UnblendedCost']
)

total_cost = float(response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])
print(f"Current month cost: ${total_cost:.2f}")
```

---

## Common Error Handling

```python
from botocore.exceptions import ClientError
import time

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except ClientError as e:
            if e.response['Error']['Code'] == 'ThrottlingException':
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
            raise

# Usage
retry_with_backoff(lambda: ec2.describe_instances())
```

---

## Pulumi Quick Deploy

```bash
# Initialize
pulumi new aws-python --name ziggie-infrastructure

# Configure
pulumi config set aws:region eu-north-1

# Preview
pulumi preview

# Deploy
pulumi up

# Destroy
pulumi destroy
```

---

## Ansible Quick Deploy

```bash
# Test connection
ansible -i inventory/hostinger.ini all -m ping

# Deploy
ansible-playbook -i inventory/hostinger.ini playbooks/deploy-ziggie.yml

# Deploy with variables
ansible-playbook -i inventory/hostinger.ini playbooks/deploy-ziggie.yml \
  -e "version=v1.2.0" -e "environment=production"
```

---

## Security Patterns

### Store Secret in AWS
```python
import boto3
import json

secrets = boto3.client('secretsmanager', region_name='eu-north-1')
secrets.create_secret(
    Name='ziggie/hostinger-token',
    SecretString=json.dumps({'token': 'xxx'}),
    Tags=[{'Key': 'Project', 'Value': 'Ziggie'}]
)
```

### Retrieve Secret
```python
response = secrets.get_secret_value(SecretId='ziggie/hostinger-token')
secret_data = json.loads(response['SecretString'])
token = secret_data['token']
```

---

## Monitoring & Alerts

### CloudWatch Log
```python
logs = boto3.client('logs', region_name='eu-north-1')

logs.put_log_events(
    logGroupName='/ziggie/infrastructure',
    logStreamName='agent-actions',
    logEvents=[{
        'timestamp': int(time.time() * 1000),
        'message': json.dumps({'action': 'start_instance', 'instance_id': 'i-xxx'})
    }]
)
```

### Cost Alert
```python
budgets = boto3.client('budgets', region_name='us-east-1')
account_id = boto3.client('sts').get_caller_identity()['Account']

budgets.create_budget(
    AccountId=account_id,
    Budget={
        'BudgetName': 'ziggie-monthly-budget',
        'BudgetLimit': {'Amount': '100', 'Unit': 'USD'},
        'TimeUnit': 'MONTHLY',
        'BudgetType': 'COST'
    },
    NotificationsWithSubscribers=[{
        'Notification': {
            'NotificationType': 'ACTUAL',
            'ComparisonOperator': 'GREATER_THAN',
            'Threshold': 80.0,
            'ThresholdType': 'PERCENTAGE'
        },
        'Subscribers': [{'SubscriptionType': 'EMAIL', 'Address': 'craig@example.com'}]
    }]
)
```

---

## Environment Variables

```bash
# AWS
export AWS_REGION=eu-north-1
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=[REDACTED]

# Hostinger
export HOSTINGER_API_TOKEN=hXXXXXXXXXXXXXXXX
export HOSTINGER_VPS_HOST=vps.example.com
export HOSTINGER_SSH_KEY=/path/to/hostinger_key

# Cost Alerts
export COST_ALERT_EMAIL=craig@example.com
export COST_ALERT_THRESHOLD=100.00
```

---

## Integration with Ziggie Agents

```python
from services.cloud.cloud_interface import ZiggieCloudInterface, CloudProvider

cloud = ZiggieCloudInterface()

# Start AWS instance
cloud.start_instance(
    provider=CloudProvider.AWS,
    instance_id='i-0123456789abcdef',
    agent_id='agent-marcus'
)

# Deploy to Hostinger
cloud.deploy_application(
    provider=CloudProvider.HOSTINGER,
    app_name='ziggie-backend',
    version='v1.3.0',
    agent_id='agent-chen'
)

# Get status
status = cloud.get_resource_status(
    provider=CloudProvider.AWS,
    resource_id='i-0123456789abcdef'
)
print(status.status)  # 'running', 'stopped', etc.
```

---

## Troubleshooting

### AWS Connection Issues
```python
# Test credentials
import boto3
sts = boto3.client('sts')
identity = sts.get_caller_identity()
print(f"Account: {identity['Account']}")
print(f"User ARN: {identity['Arn']}")
```

### Hostinger SSH Issues
```bash
# Test SSH connection
ssh -i ~/.ssh/hostinger_key root@vps.example.com -v

# Check SSH key permissions
chmod 600 ~/.ssh/hostinger_key
```

### Pulumi State Issues
```bash
# Reset state
pulumi stack export > backup.json
pulumi stack rm --force
pulumi stack init production
pulumi stack import < backup.json
```

---

**See**: [AI_CLOUD_INFRASTRUCTURE_INTEGRATION_SPEC.md](AI_CLOUD_INFRASTRUCTURE_INTEGRATION_SPEC.md) for complete documentation
