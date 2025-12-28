# AI-Controlled Cloud Infrastructure Integration Specification

> **Project**: Ziggie AI Agent System
> **Target Clouds**: AWS (EU-North-1, Account: 7851-8665-9442), Hostinger VPS
> **Purpose**: Enable AI agents to programmatically control cloud infrastructure
> **Author**: BMAD Infrastructure Agent
> **Date**: 2025-12-22

---

## Executive Summary

This specification defines how Ziggie AI agents will programmatically control both AWS and Hostinger cloud infrastructure. The integration enables agents to:

- Start/stop EC2 instances and manage AWS services
- Deploy applications to Hostinger VPS
- Track costs and set alerts
- Manage secrets and credentials securely
- Execute infrastructure-as-code deployments

**Key Technologies**:
- **AWS**: boto3, Pulumi, Terraform
- **Hostinger**: SSH automation (Paramiko/Fabric), Hostinger API, Ansible
- **Security**: AWS Secrets Manager, IAM roles, audit logging

---

## Table of Contents

1. [AWS Integration](#1-aws-integration)
2. [Hostinger Integration](#2-hostinger-integration)
3. [Infrastructure as Code (IaC)](#3-infrastructure-as-code-iac)
4. [Security Patterns](#4-security-patterns)
5. [Agent-to-Cloud Communication](#5-agent-to-cloud-communication)
6. [Cost Tracking & Alerts](#6-cost-tracking--alerts)
7. [Implementation Roadmap](#7-implementation-roadmap)
8. [Integration with Existing Ziggie Architecture](#8-integration-with-existing-ziggie-architecture)

---

## 1. AWS Integration

### 1.1 boto3 SDK Setup

**Installation**:
```bash
pip install boto3 botocore
```

**Configuration Methods**:

#### Method 1: IAM Roles (Recommended for Production)
```python
import boto3

# Automatically uses IAM role attached to EC2 instance or Lambda
ec2 = boto3.client('ec2', region_name='eu-north-1')
s3 = boto3.client('s3', region_name='eu-north-1')
```

**When to use**: Running from EC2 instances, Lambda functions, or ECS tasks.

#### Method 2: Access Keys (Development/Local)
```python
import boto3

# Option A: Environment variables
# AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
# AWS_SECRET_ACCESS_KEY=[REDACTED]
# AWS_DEFAULT_REGION=eu-north-1

session = boto3.Session(
    region_name='eu-north-1'
)
ec2 = session.client('ec2')

# Option B: Explicit credentials (NOT RECOMMENDED)
ec2 = boto3.client(
    'ec2',
    region_name='eu-north-1',
    aws_access_key_id='ACCESS_KEY',
    aws_secret_access_key='SECRET_KEY'
)
```

**When to use**: Local development, testing, CI/CD pipelines.

#### Method 3: AWS CLI Configuration
```bash
# Configure AWS CLI (creates ~/.aws/credentials)
aws configure
# AWS Access Key ID: AKIAIOSFODNN7EXAMPLE
# AWS Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
# Default region name: eu-north-1
# Default output format: json

# Python will automatically use these credentials
import boto3
ec2 = boto3.client('ec2')  # Uses ~/.aws/credentials
```

### 1.2 Service-Specific API Patterns

#### EC2 Instance Management
```python
import boto3
from typing import List, Dict

class AWSInstanceManager:
    def __init__(self, region='eu-north-1'):
        self.ec2 = boto3.client('ec2', region_name=region)
        self.region = region

    def start_instance(self, instance_id: str) -> Dict:
        """Start an EC2 instance"""
        response = self.ec2.start_instances(InstanceIds=[instance_id])
        return {
            'instance_id': instance_id,
            'state': response['StartingInstances'][0]['CurrentState']['Name'],
            'previous_state': response['StartingInstances'][0]['PreviousState']['Name']
        }

    def stop_instance(self, instance_id: str) -> Dict:
        """Stop an EC2 instance"""
        response = self.ec2.stop_instances(InstanceIds=[instance_id])
        return {
            'instance_id': instance_id,
            'state': response['StoppingInstances'][0]['CurrentState']['Name'],
            'previous_state': response['StoppingInstances'][0]['PreviousState']['Name']
        }

    def list_instances(self, filters: List[Dict] = None) -> List[Dict]:
        """List EC2 instances with optional filters"""
        params = {}
        if filters:
            params['Filters'] = filters

        response = self.ec2.describe_instances(**params)

        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append({
                    'instance_id': instance['InstanceId'],
                    'state': instance['State']['Name'],
                    'type': instance['InstanceType'],
                    'public_ip': instance.get('PublicIpAddress'),
                    'private_ip': instance.get('PrivateIpAddress'),
                    'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                })

        return instances

    def get_instance_status(self, instance_id: str) -> Dict:
        """Get detailed instance status"""
        response = self.ec2.describe_instance_status(InstanceIds=[instance_id])
        if not response['InstanceStatuses']:
            return {'instance_id': instance_id, 'status': 'not_found'}

        status = response['InstanceStatuses'][0]
        return {
            'instance_id': instance_id,
            'instance_state': status['InstanceState']['Name'],
            'system_status': status['SystemStatus']['Status'],
            'instance_status': status['InstanceStatus']['Status']
        }
```

#### S3 Storage Management
```python
import boto3
from pathlib import Path

class S3Manager:
    def __init__(self, region='eu-north-1'):
        self.s3 = boto3.client('s3', region_name=region)
        self.region = region

    def upload_file(self, local_path: str, bucket: str, key: str) -> Dict:
        """Upload file to S3"""
        try:
            self.s3.upload_file(local_path, bucket, key)
            return {'success': True, 'bucket': bucket, 'key': key}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def download_file(self, bucket: str, key: str, local_path: str) -> Dict:
        """Download file from S3"""
        try:
            self.s3.download_file(bucket, key, local_path)
            return {'success': True, 'local_path': local_path}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def list_objects(self, bucket: str, prefix: str = '') -> List[Dict]:
        """List objects in S3 bucket"""
        response = self.s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

        if 'Contents' not in response:
            return []

        return [
            {
                'key': obj['Key'],
                'size': obj['Size'],
                'last_modified': obj['LastModified'].isoformat(),
                'storage_class': obj['StorageClass']
            }
            for obj in response['Contents']
        ]
```

#### Lambda Function Management
```python
import boto3
import json

class LambdaManager:
    def __init__(self, region='eu-north-1'):
        self.lambda_client = boto3.client('lambda', region_name=region)

    def invoke_function(self, function_name: str, payload: Dict) -> Dict:
        """Invoke a Lambda function"""
        response = self.lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',  # Synchronous
            Payload=json.dumps(payload)
        )

        result = json.loads(response['Payload'].read())
        return {
            'status_code': response['StatusCode'],
            'result': result,
            'log_result': response.get('LogResult')
        }

    def create_function(self, function_name: str, role_arn: str,
                       handler: str, code_zip: bytes) -> Dict:
        """Create a new Lambda function"""
        response = self.lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.11',
            Role=role_arn,
            Handler=handler,
            Code={'ZipFile': code_zip},
            Timeout=30,
            MemorySize=256
        )
        return {
            'function_arn': response['FunctionArn'],
            'function_name': response['FunctionName']
        }
```

### 1.3 IAM Best Practices

#### Principle of Least Privilege
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ZiggieEC2Management",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ec2:DescribeInstanceStatus"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "ec2:ResourceTag/Project": "Ziggie"
        }
      }
    },
    {
      "Sid": "ZiggieS3Access",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::ziggie-deployments/*",
        "arn:aws:s3:::ziggie-deployments"
      ]
    },
    {
      "Sid": "ZiggieSecretsAccess",
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "arn:aws:secretsmanager:eu-north-1:785186659442:secret:ziggie/*"
    }
  ]
}
```

#### IAM Role for EC2 Instances
```python
import boto3

iam = boto3.client('iam')

# Create trust policy (allows EC2 to assume role)
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"Service": "ec2.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }
    ]
}

# Create role
response = iam.create_role(
    RoleName='ZiggieAgentRole',
    AssumeRolePolicyDocument=json.dumps(trust_policy),
    Description='IAM role for Ziggie AI agents running on EC2'
)

# Attach policy
iam.attach_role_policy(
    RoleName='ZiggieAgentRole',
    PolicyArn='arn:aws:iam::aws:policy/ReadOnlyAccess'
)
```

### 1.4 Error Handling & Retry Logic

```python
import boto3
from botocore.exceptions import ClientError, BotoCoreError
import time

class ResilientAWSClient:
    def __init__(self, service: str, region='eu-north-1', max_retries=3):
        self.client = boto3.client(service, region_name=region)
        self.max_retries = max_retries

    def execute_with_retry(self, operation: str, **kwargs):
        """Execute AWS operation with exponential backoff retry"""
        for attempt in range(self.max_retries):
            try:
                method = getattr(self.client, operation)
                return method(**kwargs)
            except ClientError as e:
                error_code = e.response['Error']['Code']

                # Retry on throttling
                if error_code in ['ThrottlingException', 'RequestLimitExceeded']:
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        time.sleep(wait_time)
                        continue

                # Don't retry on permission errors
                if error_code in ['AccessDenied', 'UnauthorizedOperation']:
                    raise

                # Retry on temporary errors
                if error_code in ['InternalError', 'ServiceUnavailable']:
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue

                raise
            except BotoCoreError as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise

        raise Exception(f"Failed after {self.max_retries} retries")

# Usage
ec2_client = ResilientAWSClient('ec2', region='eu-north-1')
instances = ec2_client.execute_with_retry(
    'describe_instances',
    Filters=[{'Name': 'tag:Project', 'Values': ['Ziggie']}]
)
```

---

## 2. Hostinger Integration

### 2.1 Hostinger API Access

**Official Documentation**: [https://developers.hostinger.com/](https://developers.hostinger.com/)

#### API Authentication
```python
import requests
from typing import Dict, Optional

class HostingerAPIClient:
    def __init__(self, api_token: str):
        self.base_url = 'https://api.hostinger.com/v1'
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }

    def get_vps_list(self) -> Dict:
        """List all VPS instances"""
        response = requests.get(
            f'{self.base_url}/vps',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_vps_details(self, vps_id: str) -> Dict:
        """Get VPS details"""
        response = requests.get(
            f'{self.base_url}/vps/{vps_id}',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def reboot_vps(self, vps_id: str) -> Dict:
        """Reboot VPS instance"""
        response = requests.post(
            f'{self.base_url}/vps/{vps_id}/reboot',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_server_stats(self, vps_id: str) -> Dict:
        """Get CPU, RAM, disk usage"""
        response = requests.get(
            f'{self.base_url}/vps/{vps_id}/stats',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

# Environment variable for API token
import os
hostinger = HostingerAPIClient(api_token=os.getenv('HOSTINGER_API_TOKEN'))
```

#### DNS Management via API
```python
class HostingerDNSManager:
    def __init__(self, api_token: str):
        self.client = HostingerAPIClient(api_token)

    def list_dns_records(self, domain: str) -> Dict:
        """List DNS records for domain"""
        response = requests.get(
            f'{self.client.base_url}/domains/{domain}/dns',
            headers=self.client.headers
        )
        response.raise_for_status()
        return response.json()

    def create_dns_record(self, domain: str, record_type: str,
                         name: str, value: str, ttl: int = 3600) -> Dict:
        """Create DNS record (A, CNAME, TXT, etc.)"""
        payload = {
            'type': record_type,
            'name': name,
            'value': value,
            'ttl': ttl
        }
        response = requests.post(
            f'{self.client.base_url}/domains/{domain}/dns',
            headers=self.client.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
```

### 2.2 SSH Automation (Paramiko)

**Installation**:
```bash
pip install paramiko
```

#### Basic SSH Connection
```python
import paramiko
from typing import Tuple

class HostingerSSHClient:
    def __init__(self, hostname: str, username: str,
                 password: str = None, key_filename: str = None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.client = None

    def connect(self):
        """Establish SSH connection"""
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if self.key_filename:
            self.client.connect(
                self.hostname,
                username=self.username,
                key_filename=self.key_filename
            )
        else:
            self.client.connect(
                self.hostname,
                username=self.username,
                password=self.password
            )

    def execute_command(self, command: str) -> Tuple[str, str, int]:
        """Execute command and return (stdout, stderr, exit_code)"""
        if not self.client:
            self.connect()

        stdin, stdout, stderr = self.client.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()

        return (
            stdout.read().decode('utf-8'),
            stderr.read().decode('utf-8'),
            exit_code
        )

    def upload_file(self, local_path: str, remote_path: str):
        """Upload file via SFTP"""
        if not self.client:
            self.connect()

        sftp = self.client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()

    def download_file(self, remote_path: str, local_path: str):
        """Download file via SFTP"""
        if not self.client:
            self.connect()

        sftp = self.client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()

    def close(self):
        """Close SSH connection"""
        if self.client:
            self.client.close()
            self.client = None

# Usage
ssh = HostingerSSHClient(
    hostname='vps.example.com',
    username='root',
    key_filename='/path/to/private_key'
)

# Execute commands
stdout, stderr, exit_code = ssh.execute_command('systemctl status nginx')
print(f"Nginx status: {stdout}")

# Deploy application
ssh.upload_file('app.tar.gz', '/var/www/app.tar.gz')
ssh.execute_command('cd /var/www && tar -xzf app.tar.gz')
ssh.execute_command('systemctl restart app')

ssh.close()
```

### 2.3 Fabric for High-Level Tasks

**Installation**:
```bash
pip install fabric
```

#### Deployment Automation
```python
from fabric import Connection, Config
from invoke import task

class HostingerDeployer:
    def __init__(self, host: str, user: str, key_filename: str):
        config = Config(overrides={'sudo': {'password': None}})
        self.conn = Connection(
            host=host,
            user=user,
            connect_kwargs={'key_filename': key_filename},
            config=config
        )

    def deploy_ziggie_backend(self, version: str):
        """Deploy Ziggie backend to Hostinger VPS"""
        # 1. Stop current service
        self.conn.sudo('systemctl stop ziggie-backend', warn=True)

        # 2. Backup current version
        self.conn.run(f'cp -r /var/www/ziggie /var/www/ziggie-backup-{version}')

        # 3. Upload new version
        self.conn.put(f'dist/ziggie-{version}.tar.gz', '/tmp/')

        # 4. Extract
        self.conn.run('tar -xzf /tmp/ziggie-{version}.tar.gz -C /var/www/ziggie')

        # 5. Install dependencies
        with self.conn.cd('/var/www/ziggie'):
            self.conn.run('pnpm install --production')

        # 6. Run migrations
        with self.conn.cd('/var/www/ziggie'):
            self.conn.run('pnpm prisma migrate deploy')

        # 7. Start service
        self.conn.sudo('systemctl start ziggie-backend')

        # 8. Verify
        result = self.conn.run('systemctl is-active ziggie-backend')
        if result.stdout.strip() == 'active':
            print(f"✅ Deployment successful: {version}")
            return True
        else:
            print(f"❌ Deployment failed: {version}")
            self.rollback(version)
            return False

    def rollback(self, version: str):
        """Rollback to previous version"""
        self.conn.sudo('systemctl stop ziggie-backend')
        self.conn.run(f'rm -rf /var/www/ziggie')
        self.conn.run(f'cp -r /var/www/ziggie-backup-{version} /var/www/ziggie')
        self.conn.sudo('systemctl start ziggie-backend')

# Usage
deployer = HostingerDeployer(
    host='vps.example.com',
    user='root',
    key_filename='/path/to/key'
)
deployer.deploy_ziggie_backend('v1.2.0')
```

---

## 3. Infrastructure as Code (IaC)

### 3.1 Pulumi (Python-Native IaC)

**Installation**:
```bash
pip install pulumi pulumi-aws
```

#### Pulumi Program for Ziggie AWS Infrastructure
```python
# pulumi_ziggie/__main__.py
import pulumi
import pulumi_aws as aws
import json

# Configuration
config = pulumi.Config()
project_name = pulumi.get_project()
stack = pulumi.get_stack()

# VPC
vpc = aws.ec2.Vpc(
    "ziggie-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={
        "Name": f"ziggie-vpc-{stack}",
        "Project": "Ziggie"
    }
)

# Subnet
subnet = aws.ec2.Subnet(
    "ziggie-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    availability_zone="eu-north-1a",
    tags={
        "Name": f"ziggie-subnet-{stack}",
        "Project": "Ziggie"
    }
)

# Security Group
security_group = aws.ec2.SecurityGroup(
    "ziggie-sg",
    vpc_id=vpc.id,
    description="Security group for Ziggie backend",
    ingress=[
        {
            "protocol": "tcp",
            "from_port": 22,
            "to_port": 22,
            "cidr_blocks": ["0.0.0.0/0"],
            "description": "SSH"
        },
        {
            "protocol": "tcp",
            "from_port": 8000,
            "to_port": 8000,
            "cidr_blocks": ["0.0.0.0/0"],
            "description": "Backend API"
        }
    ],
    egress=[
        {
            "protocol": "-1",
            "from_port": 0,
            "to_port": 0,
            "cidr_blocks": ["0.0.0.0/0"]
        }
    ],
    tags={
        "Name": f"ziggie-sg-{stack}",
        "Project": "Ziggie"
    }
)

# IAM Role for EC2
role = aws.iam.Role(
    "ziggie-ec2-role",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Principal": {"Service": "ec2.amazonaws.com"}
        }]
    })
)

# Attach policies
aws.iam.RolePolicyAttachment(
    "ziggie-s3-policy",
    role=role.name,
    policy_arn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
)

# Instance profile
instance_profile = aws.iam.InstanceProfile(
    "ziggie-instance-profile",
    role=role.name
)

# EC2 Instance
instance = aws.ec2.Instance(
    "ziggie-backend",
    instance_type="t3.micro",
    ami="ami-0014ce3e52359afbd",  # Amazon Linux 2023 (eu-north-1)
    subnet_id=subnet.id,
    vpc_security_group_ids=[security_group.id],
    iam_instance_profile=instance_profile.name,
    user_data="""#!/bin/bash
        yum update -y
        yum install -y docker git
        systemctl start docker
        systemctl enable docker
    """,
    tags={
        "Name": f"ziggie-backend-{stack}",
        "Project": "Ziggie"
    }
)

# S3 Bucket for deployments
bucket = aws.s3.Bucket(
    "ziggie-deployments",
    bucket=f"ziggie-deployments-{stack}",
    versioning=aws.s3.BucketVersioningArgs(enabled=True),
    tags={
        "Project": "Ziggie"
    }
)

# Outputs
pulumi.export("instance_id", instance.id)
pulumi.export("instance_public_ip", instance.public_ip)
pulumi.export("bucket_name", bucket.bucket)
```

**Deployment**:
```bash
# Initialize Pulumi project
pulumi new aws-python --name ziggie-infrastructure

# Set AWS region
pulumi config set aws:region eu-north-1

# Preview changes
pulumi preview

# Deploy
pulumi up

# Destroy
pulumi destroy
```

### 3.2 Terraform for AWS

```hcl
# main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "ziggie-terraform-state"
    key    = "infrastructure/terraform.tfstate"
    region = "eu-north-1"
  }
}

provider "aws" {
  region = "eu-north-1"
}

# Variables
variable "project_name" {
  default = "ziggie"
}

variable "environment" {
  default = "production"
}

# VPC
resource "aws_vpc" "ziggie_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name    = "${var.project_name}-vpc"
    Project = var.project_name
  }
}

# EC2 Instance
resource "aws_instance" "ziggie_backend" {
  ami           = "ami-0014ce3e52359afbd"
  instance_type = "t3.micro"

  subnet_id              = aws_subnet.ziggie_subnet.id
  vpc_security_group_ids = [aws_security_group.ziggie_sg.id]

  user_data = file("user_data.sh")

  tags = {
    Name    = "${var.project_name}-backend"
    Project = var.project_name
  }
}

# Outputs
output "instance_public_ip" {
  value = aws_instance.ziggie_backend.public_ip
}
```

### 3.3 Ansible for Hostinger VPS

```yaml
# playbooks/deploy-ziggie.yml
---
- name: Deploy Ziggie to Hostinger VPS
  hosts: hostinger_vps
  become: yes
  vars:
    app_name: ziggie
    app_user: ziggie
    app_dir: /var/www/ziggie
    version: "{{ lookup('env', 'ZIGGIE_VERSION') | default('latest', true) }}"

  tasks:
    - name: Update system packages
      apt:
        update_cache: yes
        upgrade: dist

    - name: Install required packages
      apt:
        name:
          - nodejs
          - npm
          - nginx
          - postgresql
          - redis-server
        state: present

    - name: Create application user
      user:
        name: "{{ app_user }}"
        shell: /bin/bash
        create_home: yes

    - name: Create application directory
      file:
        path: "{{ app_dir }}"
        state: directory
        owner: "{{ app_user }}"
        group: "{{ app_user }}"
        mode: '0755'

    - name: Stop existing service
      systemd:
        name: ziggie-backend
        state: stopped
      ignore_errors: yes

    - name: Upload application files
      synchronize:
        src: ../dist/
        dest: "{{ app_dir }}/"
        delete: yes
        rsync_opts:
          - "--exclude=node_modules"
          - "--exclude=.git"

    - name: Install pnpm
      npm:
        name: pnpm
        global: yes

    - name: Install dependencies
      shell: pnpm install --production
      args:
        chdir: "{{ app_dir }}"
      become_user: "{{ app_user }}"

    - name: Run database migrations
      shell: pnpm prisma migrate deploy
      args:
        chdir: "{{ app_dir }}"
      become_user: "{{ app_user }}"
      environment:
        DATABASE_URL: "{{ lookup('env', 'DATABASE_URL') }}"

    - name: Copy systemd service file
      template:
        src: templates/ziggie-backend.service.j2
        dest: /etc/systemd/system/ziggie-backend.service

    - name: Reload systemd
      systemd:
        daemon_reload: yes

    - name: Start Ziggie backend
      systemd:
        name: ziggie-backend
        state: started
        enabled: yes

    - name: Wait for service to start
      wait_for:
        port: 8000
        timeout: 60

    - name: Verify service is running
      uri:
        url: http://localhost:8000/health
        status_code: 200
```

**Inventory File**:
```ini
# inventory/hostinger.ini
[hostinger_vps]
vps1 ansible_host=192.168.1.100 ansible_user=root ansible_ssh_private_key_file=~/.ssh/hostinger_key

[hostinger_vps:vars]
ansible_python_interpreter=/usr/bin/python3
```

**Run Playbook**:
```bash
ansible-playbook -i inventory/hostinger.ini playbooks/deploy-ziggie.yml
```

---

## 4. Security Patterns

### 4.1 AWS Secrets Manager Integration

```python
import boto3
import json
from typing import Dict, Any

class SecretsManager:
    def __init__(self, region='eu-north-1'):
        self.client = boto3.client('secretsmanager', region_name=region)
        self.region = region

    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """Retrieve secret from AWS Secrets Manager"""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)

            if 'SecretString' in response:
                return json.loads(response['SecretString'])
            else:
                # Binary secret
                import base64
                return base64.b64decode(response['SecretBinary'])

        except Exception as e:
            raise Exception(f"Failed to retrieve secret {secret_name}: {str(e)}")

    def create_secret(self, secret_name: str, secret_value: Dict[str, Any]) -> str:
        """Create a new secret"""
        response = self.client.create_secret(
            Name=secret_name,
            SecretString=json.dumps(secret_value),
            Tags=[
                {'Key': 'Project', 'Value': 'Ziggie'},
                {'Key': 'ManagedBy', 'Value': 'ZiggieAgent'}
            ]
        )
        return response['ARN']

    def update_secret(self, secret_name: str, secret_value: Dict[str, Any]):
        """Update existing secret"""
        self.client.update_secret(
            SecretId=secret_name,
            SecretString=json.dumps(secret_value)
        )

    def delete_secret(self, secret_name: str, recovery_window_days: int = 30):
        """Delete secret (with recovery window)"""
        self.client.delete_secret(
            SecretId=secret_name,
            RecoveryWindowInDays=recovery_window_days
        )

# Usage in Ziggie agents
secrets = SecretsManager(region='eu-north-1')

# Store Hostinger API token
secrets.create_secret(
    'ziggie/hostinger-api-token',
    {'token': 'hXXXXXXXXXXXXXXX'}
)

# Retrieve database credentials
db_credentials = secrets.get_secret('ziggie/database-credentials')
# Returns: {'username': 'ziggie', 'password': 'xxxxx', 'host': 'db.example.com'}
```

### 4.2 Environment Variable Management

```python
import os
from pathlib import Path
from typing import Optional

class ConfigManager:
    """Secure configuration management for Ziggie agents"""

    def __init__(self, env_file: Optional[str] = None):
        self.env_file = env_file or '.env'
        self._load_env()

    def _load_env(self):
        """Load environment variables from .env file"""
        env_path = Path(self.env_file)
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()

    def get(self, key: str, default: Optional[str] = None) -> str:
        """Get configuration value"""
        # 1. Try AWS Secrets Manager (production)
        if self._is_production():
            try:
                secrets = SecretsManager()
                secret_data = secrets.get_secret(f'ziggie/{key}')
                return secret_data.get('value', default)
            except:
                pass

        # 2. Try environment variable
        value = os.getenv(key)
        if value:
            return value

        # 3. Return default
        if default is None:
            raise ValueError(f"Configuration key '{key}' not found")
        return default

    def _is_production(self) -> bool:
        """Check if running in production"""
        return os.getenv('ENVIRONMENT', 'development') == 'production'

# Usage
config = ConfigManager()
aws_region = config.get('AWS_REGION', 'eu-north-1')
hostinger_token = config.get('HOSTINGER_API_TOKEN')
```

### 4.3 Audit Logging

```python
import boto3
import json
from datetime import datetime
from typing import Dict, Any

class AuditLogger:
    """Log all infrastructure changes for compliance"""

    def __init__(self, region='eu-north-1'):
        self.cloudwatch = boto3.client('logs', region_name=region)
        self.log_group = '/ziggie/infrastructure-audit'
        self.log_stream = f"agent-{datetime.utcnow().strftime('%Y-%m-%d')}"
        self._ensure_log_stream()

    def _ensure_log_stream(self):
        """Create log group and stream if they don't exist"""
        try:
            self.cloudwatch.create_log_group(logGroupName=self.log_group)
        except self.cloudwatch.exceptions.ResourceAlreadyExistsException:
            pass

        try:
            self.cloudwatch.create_log_stream(
                logGroupName=self.log_group,
                logStreamName=self.log_stream
            )
        except self.cloudwatch.exceptions.ResourceAlreadyExistsException:
            pass

    def log_action(self, action: str, resource: str, details: Dict[str, Any],
                   agent_id: str, success: bool):
        """Log infrastructure action"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'agent_id': agent_id,
            'action': action,
            'resource': resource,
            'details': details,
            'success': success
        }

        self.cloudwatch.put_log_events(
            logGroupName=self.log_group,
            logStreamName=self.log_stream,
            logEvents=[
                {
                    'timestamp': int(datetime.utcnow().timestamp() * 1000),
                    'message': json.dumps(log_entry)
                }
            ]
        )

# Usage in Ziggie agents
audit = AuditLogger()

# Log EC2 instance start
audit.log_action(
    action='START_INSTANCE',
    resource='i-0123456789abcdef',
    details={'instance_type': 't3.micro', 'region': 'eu-north-1'},
    agent_id='agent-marcus-001',
    success=True
)
```

---

## 5. Agent-to-Cloud Communication

### 5.1 Unified Cloud Interface for Ziggie Agents

```python
# cloud_interface.py
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

class CloudProvider(Enum):
    AWS = "aws"
    HOSTINGER = "hostinger"

@dataclass
class CloudResource:
    """Unified cloud resource representation"""
    provider: CloudProvider
    resource_type: str
    resource_id: str
    status: str
    metadata: Dict

class ZiggieCloudInterface:
    """Unified interface for Ziggie agents to control cloud infrastructure"""

    def __init__(self):
        # AWS clients
        self.aws_ec2 = AWSInstanceManager(region='eu-north-1')
        self.aws_s3 = S3Manager(region='eu-north-1')
        self.aws_lambda = LambdaManager(region='eu-north-1')

        # Hostinger clients
        self.hostinger_api = HostingerAPIClient(
            api_token=ConfigManager().get('HOSTINGER_API_TOKEN')
        )
        self.hostinger_ssh = HostingerSSHClient(
            hostname=ConfigManager().get('HOSTINGER_VPS_HOST'),
            username='root',
            key_filename=ConfigManager().get('HOSTINGER_SSH_KEY')
        )

        # Audit logging
        self.audit = AuditLogger()

    def start_instance(self, provider: CloudProvider, instance_id: str,
                      agent_id: str) -> Dict:
        """Start compute instance (AWS EC2 or Hostinger VPS)"""
        if provider == CloudProvider.AWS:
            result = self.aws_ec2.start_instance(instance_id)
            self.audit.log_action(
                action='START_INSTANCE',
                resource=instance_id,
                details={'provider': 'aws', 'result': result},
                agent_id=agent_id,
                success=True
            )
            return result

        elif provider == CloudProvider.HOSTINGER:
            result = self.hostinger_api.reboot_vps(instance_id)
            self.audit.log_action(
                action='START_INSTANCE',
                resource=instance_id,
                details={'provider': 'hostinger', 'result': result},
                agent_id=agent_id,
                success=True
            )
            return result

        raise ValueError(f"Unknown provider: {provider}")

    def deploy_application(self, provider: CloudProvider,
                          app_name: str, version: str, agent_id: str) -> bool:
        """Deploy application to cloud"""
        if provider == CloudProvider.AWS:
            # Deploy to ECS or Lambda
            pass

        elif provider == CloudProvider.HOSTINGER:
            deployer = HostingerDeployer(
                host=ConfigManager().get('HOSTINGER_VPS_HOST'),
                user='root',
                key_filename=ConfigManager().get('HOSTINGER_SSH_KEY')
            )
            success = deployer.deploy_ziggie_backend(version)

            self.audit.log_action(
                action='DEPLOY_APPLICATION',
                resource=f'hostinger-vps-{app_name}',
                details={'version': version, 'success': success},
                agent_id=agent_id,
                success=success
            )
            return success

        raise ValueError(f"Unknown provider: {provider}")

    def get_resource_status(self, provider: CloudProvider,
                           resource_id: str) -> CloudResource:
        """Get status of cloud resource"""
        if provider == CloudProvider.AWS:
            status = self.aws_ec2.get_instance_status(resource_id)
            return CloudResource(
                provider=CloudProvider.AWS,
                resource_type='ec2_instance',
                resource_id=resource_id,
                status=status['instance_state'],
                metadata=status
            )

        elif provider == CloudProvider.HOSTINGER:
            details = self.hostinger_api.get_vps_details(resource_id)
            return CloudResource(
                provider=CloudProvider.HOSTINGER,
                resource_type='vps',
                resource_id=resource_id,
                status=details.get('status', 'unknown'),
                metadata=details
            )

# Usage by Ziggie agents
cloud = ZiggieCloudInterface()

# Agent Marcus starts AWS EC2 instance
cloud.start_instance(
    provider=CloudProvider.AWS,
    instance_id='i-0123456789abcdef',
    agent_id='agent-marcus-001'
)

# Agent Chen deploys to Hostinger
cloud.deploy_application(
    provider=CloudProvider.HOSTINGER,
    app_name='ziggie-backend',
    version='v1.3.0',
    agent_id='agent-chen-002'
)
```

### 5.2 Agent Capabilities Registration

```python
# agent_capabilities.py
from typing import List, Callable
from dataclasses import dataclass

@dataclass
class CloudCapability:
    """Cloud operation capability for an agent"""
    name: str
    description: str
    required_permissions: List[str]
    handler: Callable

class AgentCloudRegistry:
    """Registry of cloud capabilities for each agent"""

    def __init__(self):
        self.capabilities: Dict[str, List[CloudCapability]] = {}

    def register_capability(self, agent_id: str, capability: CloudCapability):
        """Register a cloud capability for an agent"""
        if agent_id not in self.capabilities:
            self.capabilities[agent_id] = []
        self.capabilities[agent_id].append(capability)

    def get_agent_capabilities(self, agent_id: str) -> List[CloudCapability]:
        """Get all capabilities for an agent"""
        return self.capabilities.get(agent_id, [])

    def can_execute(self, agent_id: str, capability_name: str) -> bool:
        """Check if agent can execute capability"""
        capabilities = self.get_agent_capabilities(agent_id)
        return any(cap.name == capability_name for cap in capabilities)

# Register capabilities for Marcus (Backend Agent)
registry = AgentCloudRegistry()

registry.register_capability(
    agent_id='agent-marcus',
    capability=CloudCapability(
        name='deploy_backend',
        description='Deploy backend services to AWS/Hostinger',
        required_permissions=['ec2:StartInstances', 'ec2:StopInstances'],
        handler=lambda: cloud.deploy_application(
            CloudProvider.AWS, 'ziggie-backend', 'latest', 'agent-marcus'
        )
    )
)

registry.register_capability(
    agent_id='agent-marcus',
    capability=CloudCapability(
        name='manage_database',
        description='Manage RDS database instances',
        required_permissions=['rds:DescribeDBInstances', 'rds:StartDBInstance'],
        handler=lambda: None  # Handler implementation
    )
)
```

---

## 6. Cost Tracking & Alerts

### 6.1 AWS Cost Explorer API

```python
import boto3
from datetime import datetime, timedelta
from typing import Dict, List

class AWSCostTracker:
    def __init__(self, region='eu-north-1'):
        self.ce_client = boto3.client('ce', region_name='us-east-1')  # Cost Explorer is global
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)

    def get_monthly_cost(self, year: int, month: int) -> Dict:
        """Get total AWS cost for a specific month"""
        start_date = f"{year}-{month:02d}-01"

        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"

        response = self.ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'}
            ]
        )

        costs_by_service = {}
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                service = group['Keys'][0]
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                costs_by_service[service] = cost

        total_cost = sum(costs_by_service.values())

        return {
            'period': f"{year}-{month:02d}",
            'total_cost': round(total_cost, 2),
            'currency': 'USD',
            'by_service': costs_by_service
        }

    def get_current_month_forecast(self) -> Dict:
        """Get forecasted cost for current month"""
        now = datetime.utcnow()
        start_date = f"{now.year}-{now.month:02d}-01"

        if now.month == 12:
            end_date = f"{now.year + 1}-01-31"
        else:
            end_date = f"{now.year}-{now.month + 1:02d}-01"

        response = self.ce_client.get_cost_forecast(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Metric='UNBLENDED_COST',
            Granularity='MONTHLY'
        )

        forecast = float(response['Total']['Amount'])
        return {
            'period': f"{now.year}-{now.month:02d}",
            'forecasted_cost': round(forecast, 2),
            'currency': 'USD'
        }

    def set_cost_alert(self, threshold: float, email: str):
        """Create CloudWatch alarm for cost threshold"""
        alarm_name = f"ziggie-cost-alert-{threshold}"

        # Create SNS topic for alerts
        sns = boto3.client('sns', region_name='eu-north-1')
        topic_response = sns.create_topic(Name='ziggie-cost-alerts')
        topic_arn = topic_response['TopicArn']

        # Subscribe email
        sns.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=email
        )

        # Note: Cost alerts require AWS Budgets API, not CloudWatch
        budgets = boto3.client('budgets', region_name='us-east-1')

        budgets.create_budget(
            AccountId=boto3.client('sts').get_caller_identity()['Account'],
            Budget={
                'BudgetName': 'ziggie-monthly-budget',
                'BudgetLimit': {
                    'Amount': str(threshold),
                    'Unit': 'USD'
                },
                'TimeUnit': 'MONTHLY',
                'BudgetType': 'COST'
            },
            NotificationsWithSubscribers=[
                {
                    'Notification': {
                        'NotificationType': 'ACTUAL',
                        'ComparisonOperator': 'GREATER_THAN',
                        'Threshold': 80.0,  # Alert at 80% of budget
                        'ThresholdType': 'PERCENTAGE'
                    },
                    'Subscribers': [
                        {
                            'SubscriptionType': 'EMAIL',
                            'Address': email
                        }
                    ]
                }
            ]
        )

# Usage
cost_tracker = AWSCostTracker()

# Get current month cost
current_cost = cost_tracker.get_monthly_cost(2025, 12)
print(f"December 2025 cost: ${current_cost['total_cost']}")
print(f"Breakdown: {current_cost['by_service']}")

# Get forecast
forecast = cost_tracker.get_current_month_forecast()
print(f"Forecasted cost: ${forecast['forecasted_cost']}")

# Set alert at $100/month
cost_tracker.set_cost_alert(threshold=100.0, email='craig@example.com')
```

### 6.2 Hostinger Cost Tracking

```python
class HostingerCostTracker:
    """Track Hostinger VPS costs (manual tracking since no API)"""

    def __init__(self):
        self.monthly_cost = {
            'vps_basic': 4.99,  # Example pricing
            'vps_premium': 8.99,
            'domain': 1.00
        }

    def get_monthly_cost(self) -> Dict:
        """Calculate total monthly Hostinger cost"""
        total = sum(self.monthly_cost.values())
        return {
            'total_cost': round(total, 2),
            'currency': 'USD',
            'breakdown': self.monthly_cost
        }

    def get_combined_cloud_cost(self, aws_cost: float) -> Dict:
        """Get combined AWS + Hostinger cost"""
        hostinger_cost = self.get_monthly_cost()['total_cost']
        total = aws_cost + hostinger_cost

        return {
            'total_cost': round(total, 2),
            'aws_cost': aws_cost,
            'hostinger_cost': hostinger_cost,
            'currency': 'USD'
        }
```

---

## 7. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

**Goal**: Basic AWS and Hostinger connectivity

- [ ] Install boto3, paramiko, fabric
- [ ] Configure AWS credentials (IAM user with restricted permissions)
- [ ] Test EC2 instance start/stop
- [ ] Test S3 upload/download
- [ ] Configure SSH key authentication for Hostinger VPS
- [ ] Test basic SSH commands execution

**Deliverables**:
- `aws_client.py` - AWS SDK wrapper
- `hostinger_client.py` - Hostinger SSH/API wrapper
- Unit tests for basic operations

### Phase 2: Security & Secrets (Week 3)

**Goal**: Secure credential management

- [ ] Implement AWS Secrets Manager integration
- [ ] Store Hostinger credentials in Secrets Manager
- [ ] Create IAM roles for production agents
- [ ] Implement audit logging for all cloud operations
- [ ] Set up CloudWatch log groups

**Deliverables**:
- `secrets_manager.py` - Secrets management module
- `audit_logger.py` - Audit logging module
- IAM policies JSON files

### Phase 3: Infrastructure as Code (Week 4-5)

**Goal**: Automated infrastructure provisioning

- [ ] Create Pulumi program for AWS infrastructure
- [ ] Create Ansible playbooks for Hostinger VPS
- [ ] Test infrastructure deployment/teardown
- [ ] Version control IaC configurations
- [ ] Document infrastructure architecture

**Deliverables**:
- `pulumi_ziggie/` - Pulumi project
- `ansible/` - Ansible playbooks
- Infrastructure documentation

### Phase 4: Unified Agent Interface (Week 6)

**Goal**: Simple API for Ziggie agents

- [ ] Implement `ZiggieCloudInterface` class
- [ ] Create capability registration system
- [ ] Integrate with existing Ziggie agent framework
- [ ] Add cloud operations to agent command set
- [ ] Test agent-driven deployments

**Deliverables**:
- `cloud_interface.py` - Unified cloud interface
- `agent_capabilities.py` - Capability registry
- Updated agent documentation

### Phase 5: Cost Management (Week 7)

**Goal**: Track and alert on cloud costs

- [ ] Implement AWS Cost Explorer integration
- [ ] Set up budget alerts
- [ ] Create cost dashboard in Control Center
- [ ] Document cost optimization strategies
- [ ] Set up monthly cost reports

**Deliverables**:
- `cost_tracker.py` - Cost tracking module
- Cost dashboard UI component
- Monthly cost report automation

### Phase 6: Production Hardening (Week 8)

**Goal**: Production-ready security and reliability

- [ ] Implement retry logic with exponential backoff
- [ ] Add comprehensive error handling
- [ ] Set up monitoring and alerting
- [ ] Conduct security audit
- [ ] Load testing for cloud operations
- [ ] Create runbooks for common issues

**Deliverables**:
- Production deployment guide
- Security audit report
- Monitoring dashboards
- Incident response runbooks

---

## 8. Integration with Existing Ziggie Architecture

### 8.1 Control Center Integration

Add cloud management endpoints to Ziggie Control Center backend:

```python
# control-center/backend/api/cloud.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List
from ..services.cloud_interface import ZiggieCloudInterface
from ..middleware.auth import require_auth

router = APIRouter(prefix="/api/cloud", tags=["cloud"])

cloud = ZiggieCloudInterface()

@router.get("/instances")
async def list_instances(current_user = Depends(require_auth)):
    """List all cloud instances (AWS + Hostinger)"""
    aws_instances = cloud.aws_ec2.list_instances()
    hostinger_vps = cloud.hostinger_api.get_vps_list()

    return {
        "aws": aws_instances,
        "hostinger": hostinger_vps
    }

@router.post("/instances/{provider}/{instance_id}/start")
async def start_instance(
    provider: str,
    instance_id: str,
    current_user = Depends(require_auth)
):
    """Start cloud instance"""
    from ..services.cloud_interface import CloudProvider

    provider_enum = CloudProvider(provider)
    result = cloud.start_instance(
        provider=provider_enum,
        instance_id=instance_id,
        agent_id=f"user-{current_user['id']}"
    )
    return result

@router.get("/costs/current")
async def get_current_costs(current_user = Depends(require_auth)):
    """Get current month cloud costs"""
    from datetime import datetime
    from ..services.cost_tracker import AWSCostTracker, HostingerCostTracker

    now = datetime.utcnow()
    aws_tracker = AWSCostTracker()
    hostinger_tracker = HostingerCostTracker()

    aws_cost = aws_tracker.get_monthly_cost(now.year, now.month)
    combined = hostinger_tracker.get_combined_cloud_cost(aws_cost['total_cost'])

    return combined
```

### 8.2 Agent Command Extensions

Add cloud management commands to agent CLI:

```python
# coordinator/cloud_commands.py
from typing import Dict
from .schemas import AgentCommand, AgentResponse
from ..services.cloud_interface import ZiggieCloudInterface, CloudProvider

cloud = ZiggieCloudInterface()

def handle_cloud_command(command: AgentCommand) -> AgentResponse:
    """Handle cloud-related agent commands"""

    if command.command == "cloud:start-instance":
        provider = CloudProvider(command.params['provider'])
        instance_id = command.params['instance_id']

        result = cloud.start_instance(
            provider=provider,
            instance_id=instance_id,
            agent_id=command.agent_id
        )

        return AgentResponse(
            success=True,
            message=f"Started instance {instance_id}",
            data=result
        )

    elif command.command == "cloud:deploy":
        provider = CloudProvider(command.params['provider'])
        app_name = command.params['app_name']
        version = command.params['version']

        success = cloud.deploy_application(
            provider=provider,
            app_name=app_name,
            version=version,
            agent_id=command.agent_id
        )

        return AgentResponse(
            success=success,
            message=f"Deployed {app_name} v{version}",
            data={'version': version}
        )

    elif command.command == "cloud:status":
        provider = CloudProvider(command.params['provider'])
        resource_id = command.params['resource_id']

        status = cloud.get_resource_status(provider, resource_id)

        return AgentResponse(
            success=True,
            message=f"Resource status: {status.status}",
            data=status.__dict__
        )

    raise ValueError(f"Unknown cloud command: {command.command}")
```

### 8.3 Environment Configuration

Update `.env.example` with cloud credentials:

```bash
# AWS Configuration
AWS_REGION=eu-north-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=[REDACTED]
AWS_ACCOUNT_ID=785186659442

# Hostinger Configuration
HOSTINGER_API_TOKEN=hXXXXXXXXXXXXXXXX
HOSTINGER_VPS_HOST=vps.example.com
HOSTINGER_SSH_KEY=/path/to/hostinger_key
HOSTINGER_SSH_USER=root

# Cloud Operations
ENABLE_CLOUD_MANAGEMENT=true
CLOUD_AUDIT_LOG_GROUP=/ziggie/infrastructure-audit
COST_ALERT_EMAIL=craig@example.com
COST_ALERT_THRESHOLD=100.00
```

---

## Appendix A: Complete File Structure

```
ziggie/
├── services/
│   ├── cloud/
│   │   ├── __init__.py
│   │   ├── aws_client.py          # AWS SDK wrapper (boto3)
│   │   ├── hostinger_client.py    # Hostinger API/SSH wrapper
│   │   ├── cloud_interface.py     # Unified interface for agents
│   │   ├── secrets_manager.py     # AWS Secrets Manager integration
│   │   ├── audit_logger.py        # CloudWatch audit logging
│   │   ├── cost_tracker.py        # Cost Explorer integration
│   │   └── agent_capabilities.py  # Capability registration
│   └── ...
├── infrastructure/
│   ├── pulumi/
│   │   ├── __main__.py           # Pulumi AWS infrastructure
│   │   ├── Pulumi.yaml
│   │   └── requirements.txt
│   ├── terraform/
│   │   ├── main.tf               # Terraform AWS configuration
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── ansible/
│       ├── inventory/
│       │   └── hostinger.ini
│       ├── playbooks/
│       │   ├── deploy-ziggie.yml
│       │   └── setup-vps.yml
│       └── templates/
│           └── ziggie-backend.service.j2
├── control-center/
│   └── backend/
│       └── api/
│           └── cloud.py          # Cloud management API endpoints
└── docs/
    ├── CLOUD_INTEGRATION.md      # This document
    ├── AWS_SETUP_GUIDE.md
    └── HOSTINGER_SETUP_GUIDE.md
```

---

## Appendix B: Quick Start Commands

### AWS Setup
```bash
# Install AWS CLI
pip install awscli boto3

# Configure credentials
aws configure
# Region: eu-north-1
# Access Key: AKIAIOSFODNN7EXAMPLE
# Secret Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# Test connection
aws ec2 describe-instances --region eu-north-1
```

### Hostinger Setup
```bash
# Install SSH tools
pip install paramiko fabric

# Generate SSH key
ssh-keygen -t ed25519 -C "ziggie-agent" -f ~/.ssh/hostinger_key

# Copy public key to VPS
ssh-copy-id -i ~/.ssh/hostinger_key.pub root@vps.example.com

# Test connection
ssh -i ~/.ssh/hostinger_key root@vps.example.com
```

### Pulumi Setup
```bash
# Install Pulumi
pip install pulumi pulumi-aws

# Initialize project
cd infrastructure/pulumi
pulumi new aws-python --name ziggie-infrastructure

# Configure
pulumi config set aws:region eu-north-1

# Deploy
pulumi up
```

### Ansible Setup
```bash
# Install Ansible
pip install ansible

# Test connection
ansible -i infrastructure/ansible/inventory/hostinger.ini all -m ping

# Run playbook
ansible-playbook -i infrastructure/ansible/inventory/hostinger.ini \
  infrastructure/ansible/playbooks/deploy-ziggie.yml
```

---

## Sources

### AWS & boto3
- [12 Best Practices to Keep Your Boto3 Scripts from Breaking in Production](https://medium.com/@u.mair/12-best-practices-to-keep-your-boto3-scripts-from-breaking-in-production-f0f726bdfba0)
- [AWS Automation using Python and Boto3 - Detailed Guide](https://www.whizlabs.com/blog/aws-automation-with-python-and-boto3/)
- [AWS Secrets Manager with boto3 in python](https://www.learnaws.org/2021/02/26/aws-secrets-manager-boto3-guide/)

### Terraform
- [Terraform on AWS: The Complete Beginner Guide 2025](https://atmosly.com/knowledge/terraform-on-aws-the-most-complete-beginner-guide-for-2025)
- [Best practices for using the Terraform AWS Provider](https://docs.aws.amazon.com/prescriptive-guidance/latest/terraform-aws-provider-best-practices/introduction.html)

### Pulumi
- [Mastering AWS Infrastructure as Code with Pulumi and Python](https://blogs.perficient.com/2025/03/27/mastering-aws-infrastructure-as-code-with-pulumi-and-python/)
- [AWS with Pulumi](https://www.pulumi.com/aws/)

### Hostinger
- [Hostinger API Reference](https://developers.hostinger.com/)
- [Power up your VPS: Automate, scale, and take full control with Hostinger API](https://www.hostinger.com/blog/hostinger-api)
- [Using Hostinger VPS API With Postman: A Step-by-Step Guide](https://support.hostinger.com/en/articles/11079560-using-hostinger-vps-api-with-postman-a-step-by-step-guide)

### Ansible
- [Use Ansible to Manage Multiple VPS Instances Efficiently](https://blog.hosteons.com/2025/07/22/use-ansible-to-manage-multiple-vps-instances-efficiently/)
- [Automating Server Management with Ansible on Linux VPS](https://shape.host/resources/automating-server-management-with-ansible-on-linux-vps)

### SSH Automation
- [Welcome to Paramiko!](https://www.paramiko.org/)
- [Welcome to Fabric!](https://www.fabfile.org/)
- [SSH Scripting with Fabric and Python](https://www.blog.pythonlibrary.org/2024/10/16/ssh-scripting-with-fabric-and-python/)

---

**End of Specification**

*Generated by: BMAD Infrastructure Agent*
*Date: 2025-12-22*
*Version: 1.0*
