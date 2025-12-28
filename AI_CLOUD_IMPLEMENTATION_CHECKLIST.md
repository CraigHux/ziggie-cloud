# AI Cloud Infrastructure - Implementation Checklist

> **Step-by-step implementation guide for AI-controlled AWS and Hostinger infrastructure**

---

## Phase 1: Foundation (Week 1-2)

### AWS Setup

- [ ] **Install AWS CLI and boto3**
  ```bash
  pip install awscli boto3 botocore
  ```

- [ ] **Create IAM User for Ziggie**
  - Go to AWS Console > IAM > Users > Add User
  - Username: `ziggie-agent`
  - Access type: Programmatic access
  - Attach policies: `AmazonEC2FullAccess`, `AmazonS3FullAccess` (temporary, will restrict later)
  - Save Access Key ID and Secret Access Key

- [ ] **Configure AWS CLI**
  ```bash
  aws configure
  # AWS Access Key ID: AKIAIOSFODNN7EXAMPLE
  # AWS Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
  # Default region name: eu-north-1
  # Default output format: json
  ```

- [ ] **Test AWS Connection**
  ```bash
  aws ec2 describe-instances --region eu-north-1
  ```

- [ ] **Create `aws_client.py`**
  - Implement `AWSInstanceManager` class
  - Implement `S3Manager` class
  - Implement `LambdaManager` class
  - Add error handling and retry logic

- [ ] **Write Unit Tests for AWS Client**
  ```bash
  pytest tests/test_aws_client.py
  ```

### Hostinger Setup

- [ ] **Generate SSH Key for Ziggie**
  ```bash
  ssh-keygen -t ed25519 -C "ziggie-agent" -f ~/.ssh/ziggie_hostinger
  chmod 600 ~/.ssh/ziggie_hostinger
  ```

- [ ] **Copy Public Key to Hostinger VPS**
  ```bash
  ssh-copy-id -i ~/.ssh/ziggie_hostinger.pub root@YOUR_VPS_IP
  ```

- [ ] **Test SSH Connection**
  ```bash
  ssh -i ~/.ssh/ziggie_hostinger root@YOUR_VPS_IP
  ```

- [ ] **Get Hostinger API Token**
  - Log in to Hostinger panel
  - Go to Settings > API
  - Generate API token
  - Save token to `.env` file

- [ ] **Install Paramiko and Fabric**
  ```bash
  pip install paramiko fabric
  ```

- [ ] **Create `hostinger_client.py`**
  - Implement `HostingerAPIClient` class
  - Implement `HostingerSSHClient` class
  - Implement `HostingerDeployer` class (using Fabric)

- [ ] **Write Unit Tests for Hostinger Client**
  ```bash
  pytest tests/test_hostinger_client.py
  ```

### Environment Configuration

- [ ] **Create `.env` File**
  ```bash
  cp .env.example .env
  ```

- [ ] **Add Cloud Credentials**
  ```env
  # AWS
  AWS_REGION=eu-north-1
  AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
  AWS_SECRET_ACCESS_KEY=[REDACTED]
  AWS_ACCOUNT_ID=785186659442

  # Hostinger
  HOSTINGER_API_TOKEN=hXXXXXXXXXXXXXXXX
  HOSTINGER_VPS_HOST=YOUR_VPS_IP
  HOSTINGER_SSH_KEY=/path/to/.ssh/ziggie_hostinger
  HOSTINGER_SSH_USER=root
  ```

- [ ] **Test Environment Loading**
  ```python
  from services.cloud.config_manager import ConfigManager
  config = ConfigManager()
  print(config.get('AWS_REGION'))  # Should print: eu-north-1
  ```

---

## Phase 2: Security & Secrets (Week 3)

### AWS Secrets Manager

- [ ] **Create Secrets Manager Client**
  - Implement `SecretsManager` class in `secrets_manager.py`
  - Add methods: `get_secret`, `create_secret`, `update_secret`, `delete_secret`

- [ ] **Store Hostinger Credentials in Secrets Manager**
  ```python
  from services.cloud.secrets_manager import SecretsManager
  secrets = SecretsManager(region='eu-north-1')

  secrets.create_secret(
      'ziggie/hostinger-api-token',
      {'token': 'hXXXXXXXXXXXXXXXX'}
  )

  secrets.create_secret(
      'ziggie/hostinger-ssh',
      {
          'host': 'YOUR_VPS_IP',
          'user': 'root',
          'key_path': '/path/to/.ssh/ziggie_hostinger'
      }
  )
  ```

- [ ] **Update `ConfigManager` to Use Secrets Manager**
  - Modify `get()` method to check Secrets Manager first (in production)
  - Fallback to environment variables (in development)

- [ ] **Test Secret Retrieval**
  ```python
  config = ConfigManager()
  token = config.get('HOSTINGER_API_TOKEN')  # Should retrieve from Secrets Manager
  ```

### IAM Roles and Policies

- [ ] **Create Least Privilege IAM Policy**
  - Create `iam-policies/ziggie-agent-policy.json`
  - Restrict EC2 actions to instances with tag `Project=Ziggie`
  - Restrict S3 actions to `ziggie-deployments` bucket
  - Allow Secrets Manager read access to `ziggie/*` secrets

- [ ] **Apply IAM Policy**
  ```bash
  aws iam create-policy --policy-name ZiggieAgentPolicy \
    --policy-document file://iam-policies/ziggie-agent-policy.json

  aws iam attach-user-policy --user-name ziggie-agent \
    --policy-arn arn:aws:iam::785186659442:policy/ZiggieAgentPolicy
  ```

- [ ] **Create IAM Role for EC2 Instances**
  - Create `iam-policies/ziggie-ec2-trust-policy.json`
  - Create IAM role `ZiggieEC2Role`
  - Attach `ZiggieAgentPolicy` to role

- [ ] **Test IAM Permissions**
  ```python
  # Should succeed (instance tagged with Project=Ziggie)
  ec2.start_instances(InstanceIds=['i-tagged-instance'])

  # Should fail (instance not tagged)
  ec2.start_instances(InstanceIds=['i-untagged-instance'])  # AccessDenied
  ```

### Audit Logging

- [ ] **Create CloudWatch Log Group**
  ```bash
  aws logs create-log-group --log-group-name /ziggie/infrastructure-audit
  ```

- [ ] **Implement `AuditLogger` Class**
  - Create `audit_logger.py`
  - Add `log_action()` method
  - Add automatic log stream creation

- [ ] **Integrate Audit Logging into All Cloud Operations**
  ```python
  # Example in aws_client.py
  def start_instance(self, instance_id: str, agent_id: str):
      result = self.ec2.start_instances(InstanceIds=[instance_id])

      # Log the action
      self.audit.log_action(
          action='START_INSTANCE',
          resource=instance_id,
          details={'result': result},
          agent_id=agent_id,
          success=True
      )

      return result
  ```

- [ ] **Test Audit Logging**
  ```bash
  aws logs tail /ziggie/infrastructure-audit --follow
  ```

---

## Phase 3: Infrastructure as Code (Week 4-5)

### Pulumi Setup

- [ ] **Install Pulumi**
  ```bash
  pip install pulumi pulumi-aws
  ```

- [ ] **Initialize Pulumi Project**
  ```bash
  mkdir -p infrastructure/pulumi
  cd infrastructure/pulumi
  pulumi new aws-python --name ziggie-infrastructure
  ```

- [ ] **Configure Pulumi**
  ```bash
  pulumi config set aws:region eu-north-1
  ```

- [ ] **Create Pulumi Program**
  - Edit `infrastructure/pulumi/__main__.py`
  - Define VPC, Subnets, Security Groups
  - Define EC2 instances with appropriate tags
  - Define S3 bucket for deployments
  - Define IAM roles

- [ ] **Test Pulumi Deployment**
  ```bash
  pulumi preview  # Review changes
  pulumi up       # Deploy infrastructure
  ```

- [ ] **Export Pulumi Outputs**
  ```bash
  pulumi stack output instance_id
  pulumi stack output instance_public_ip
  ```

### Terraform Alternative (Optional)

- [ ] **Install Terraform**
  ```bash
  # Download from terraform.io
  ```

- [ ] **Create Terraform Configuration**
  - Create `infrastructure/terraform/main.tf`
  - Define AWS provider
  - Define resources (VPC, EC2, S3)

- [ ] **Initialize Terraform**
  ```bash
  cd infrastructure/terraform
  terraform init
  ```

- [ ] **Apply Terraform**
  ```bash
  terraform plan
  terraform apply
  ```

### Ansible for Hostinger

- [ ] **Install Ansible**
  ```bash
  pip install ansible
  ```

- [ ] **Create Ansible Inventory**
  ```bash
  mkdir -p infrastructure/ansible/inventory
  ```

  Create `infrastructure/ansible/inventory/hostinger.ini`:
  ```ini
  [hostinger_vps]
  vps1 ansible_host=YOUR_VPS_IP ansible_user=root ansible_ssh_private_key_file=~/.ssh/ziggie_hostinger

  [hostinger_vps:vars]
  ansible_python_interpreter=/usr/bin/python3
  ```

- [ ] **Test Ansible Connection**
  ```bash
  ansible -i infrastructure/ansible/inventory/hostinger.ini all -m ping
  ```

- [ ] **Create Deployment Playbook**
  - Create `infrastructure/ansible/playbooks/deploy-ziggie.yml`
  - Add tasks for: system updates, package installation, file upload, service restart

- [ ] **Create Service Template**
  - Create `infrastructure/ansible/templates/ziggie-backend.service.j2`

- [ ] **Run Deployment Playbook**
  ```bash
  ansible-playbook -i infrastructure/ansible/inventory/hostinger.ini \
    infrastructure/ansible/playbooks/deploy-ziggie.yml
  ```

---

## Phase 4: Unified Agent Interface (Week 6)

### Cloud Interface Implementation

- [ ] **Create `cloud_interface.py`**
  - Implement `CloudProvider` enum
  - Implement `CloudResource` dataclass
  - Implement `ZiggieCloudInterface` class with methods:
    - `start_instance()`
    - `stop_instance()`
    - `deploy_application()`
    - `get_resource_status()`

- [ ] **Create `agent_capabilities.py`**
  - Implement `CloudCapability` dataclass
  - Implement `AgentCloudRegistry` class
  - Add capability registration for each agent type

- [ ] **Register Agent Capabilities**
  ```python
  registry = AgentCloudRegistry()

  # Marcus (Backend Agent)
  registry.register_capability('agent-marcus', CloudCapability(
      name='deploy_backend',
      description='Deploy backend services',
      required_permissions=['ec2:StartInstances'],
      handler=deploy_backend_handler
  ))

  # Chen (Frontend Agent)
  registry.register_capability('agent-chen', CloudCapability(
      name='deploy_frontend',
      description='Deploy frontend to S3/CloudFront',
      required_permissions=['s3:PutObject'],
      handler=deploy_frontend_handler
  ))
  ```

### Control Center Integration

- [ ] **Add Cloud API Endpoints**
  - Create `control-center/backend/api/cloud.py`
  - Add endpoints:
    - `GET /api/cloud/instances` - List all instances
    - `POST /api/cloud/instances/{provider}/{id}/start` - Start instance
    - `POST /api/cloud/instances/{provider}/{id}/stop` - Stop instance
    - `POST /api/cloud/deploy` - Deploy application
    - `GET /api/cloud/costs/current` - Get current costs

- [ ] **Update Frontend to Show Cloud Resources**
  - Add cloud management page to Control Center UI
  - Show AWS instances and Hostinger VPS
  - Add start/stop buttons
  - Show cost dashboard

### Agent Command Extensions

- [ ] **Add Cloud Commands to Agent CLI**
  - Create `coordinator/cloud_commands.py`
  - Implement handlers:
    - `cloud:start-instance`
    - `cloud:stop-instance`
    - `cloud:deploy`
    - `cloud:status`

- [ ] **Test Agent Cloud Commands**
  ```bash
  # Via Ziggie Coordinator
  python coordinator/main.py execute-command \
    --agent marcus \
    --command "cloud:deploy" \
    --params '{"provider": "aws", "app_name": "ziggie-backend", "version": "v1.0.0"}'
  ```

---

## Phase 5: Cost Management (Week 7)

### AWS Cost Tracking

- [ ] **Create `cost_tracker.py`**
  - Implement `AWSCostTracker` class
  - Add methods:
    - `get_monthly_cost(year, month)` - Get cost for specific month
    - `get_current_month_forecast()` - Get forecasted cost
    - `set_cost_alert(threshold, email)` - Create budget alert

- [ ] **Set Up Cost Alert**
  ```python
  from services.cloud.cost_tracker import AWSCostTracker
  tracker = AWSCostTracker()
  tracker.set_cost_alert(threshold=100.0, email='craig@example.com')
  ```

- [ ] **Test Cost Retrieval**
  ```python
  import datetime
  now = datetime.datetime.utcnow()
  cost = tracker.get_monthly_cost(now.year, now.month)
  print(f"Current month cost: ${cost['total_cost']}")
  ```

### Hostinger Cost Tracking

- [ ] **Create `HostingerCostTracker` Class**
  - Add manual cost entries (since no API)
  - Implement `get_monthly_cost()` method
  - Implement `get_combined_cloud_cost()` method

### Cost Dashboard

- [ ] **Add Cost Endpoint to API**
  ```python
  # In control-center/backend/api/cloud.py
  @router.get("/costs/current")
  async def get_current_costs():
      aws_cost = aws_tracker.get_monthly_cost(now.year, now.month)
      combined = hostinger_tracker.get_combined_cloud_cost(aws_cost['total_cost'])
      return combined
  ```

- [ ] **Create Cost Dashboard UI Component**
  - Show total monthly cost (AWS + Hostinger)
  - Show cost breakdown by service
  - Show forecast for current month
  - Add cost trend chart

- [ ] **Set Up Monthly Cost Report Automation**
  - Create cron job to email cost report on 1st of each month
  ```bash
  # Add to crontab
  0 0 1 * * python /path/to/ziggie/scripts/send_cost_report.py
  ```

---

## Phase 6: Production Hardening (Week 8)

### Error Handling & Resilience

- [ ] **Implement Retry Logic**
  - Create `ResilientAWSClient` class with exponential backoff
  - Add retry logic to all AWS operations
  - Add retry logic to SSH operations

- [ ] **Add Comprehensive Error Handling**
  ```python
  try:
      result = cloud.start_instance(provider, instance_id, agent_id)
  except ClientError as e:
      if e.response['Error']['Code'] == 'AccessDenied':
          log.error(f"Permission denied for instance {instance_id}")
          raise
      elif e.response['Error']['Code'] == 'InstanceLimitExceeded':
          log.error("Instance limit exceeded")
          raise
      else:
          log.error(f"Unexpected error: {e}")
          raise
  ```

- [ ] **Implement Circuit Breaker Pattern**
  - Prevent cascading failures
  - Auto-disable failed cloud operations temporarily

### Monitoring & Alerting

- [ ] **Set Up CloudWatch Alarms**
  ```python
  cloudwatch = boto3.client('cloudwatch', region_name='eu-north-1')
  cloudwatch.put_metric_alarm(
      AlarmName='ziggie-ec2-high-cpu',
      MetricName='CPUUtilization',
      Namespace='AWS/EC2',
      Statistic='Average',
      Period=300,
      EvaluationPeriods=2,
      Threshold=80.0,
      ComparisonOperator='GreaterThanThreshold',
      Dimensions=[{'Name': 'InstanceId', 'Value': 'i-xxx'}]
  )
  ```

- [ ] **Create Health Check Endpoints**
  - Add `/health/aws` endpoint - Check AWS connectivity
  - Add `/health/hostinger` endpoint - Check Hostinger SSH/API

- [ ] **Set Up Monitoring Dashboard**
  - CloudWatch dashboard for AWS resources
  - Custom dashboard in Control Center for both clouds

### Security Audit

- [ ] **Review IAM Permissions**
  - Ensure least privilege principle
  - Remove unused permissions
  - Document required permissions

- [ ] **Enable CloudTrail Logging**
  ```bash
  aws cloudtrail create-trail --name ziggie-audit-trail \
    --s3-bucket-name ziggie-audit-logs
  aws cloudtrail start-logging --name ziggie-audit-trail
  ```

- [ ] **Review Security Groups**
  - Ensure minimum necessary ports open
  - Restrict SSH to known IP ranges
  - Enable VPC flow logs

- [ ] **Scan for Hardcoded Secrets**
  ```bash
  # Use git-secrets or similar
  git secrets --scan
  ```

- [ ] **Enable MFA for AWS Root Account**
  - Go to AWS Console > IAM > Root User
  - Enable virtual MFA device

### Load Testing

- [ ] **Test Cloud Operations Under Load**
  ```python
  # Test concurrent instance starts
  import concurrent.futures

  def start_test_instance(instance_id):
      return cloud.start_instance(CloudProvider.AWS, instance_id, 'test-agent')

  with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
      futures = [executor.submit(start_test_instance, f'i-test-{i}') for i in range(10)]
      results = [f.result() for f in futures]
  ```

- [ ] **Verify Rate Limiting**
  - Test AWS API rate limits
  - Verify retry logic works correctly

### Documentation

- [ ] **Create Production Deployment Guide**
  - Step-by-step production setup
  - Security checklist
  - Monitoring setup

- [ ] **Create Security Audit Report**
  - IAM permissions review
  - Network security review
  - Secret management review

- [ ] **Create Runbooks**
  - Runbook: EC2 instance fails to start
  - Runbook: Hostinger VPS unreachable
  - Runbook: Cost spike detected
  - Runbook: Deployment failure rollback

- [ ] **Update Team Documentation**
  - Add cloud integration to README
  - Update agent capabilities documentation
  - Document cloud command usage

---

## Verification

### Final Checks

- [ ] **AWS Integration Works**
  - Start/stop EC2 instance
  - Upload/download S3 file
  - Invoke Lambda function
  - Retrieve secret from Secrets Manager

- [ ] **Hostinger Integration Works**
  - Execute SSH command
  - Deploy application via Fabric
  - Call Hostinger API
  - Manage DNS records

- [ ] **Security Verified**
  - All credentials in Secrets Manager
  - No hardcoded secrets in code
  - CloudTrail enabled
  - Audit logs working

- [ ] **Cost Tracking Works**
  - Current month cost retrieval
  - Cost forecast retrieval
  - Budget alerts configured
  - Cost dashboard functional

- [ ] **Agent Integration Works**
  - Agents can execute cloud commands
  - Capability registry functional
  - Cloud operations logged in audit trail

- [ ] **Documentation Complete**
  - Main specification document
  - Quick reference guide
  - Implementation checklist (this file)
  - Runbooks for common issues

---

## Go-Live Checklist

- [ ] **Production Environment Variables Set**
- [ ] **IAM Policies Applied**
- [ ] **Secrets Manager Populated**
- [ ] **CloudTrail Enabled**
- [ ] **Cost Alerts Configured**
- [ ] **Monitoring Dashboards Created**
- [ ] **Health Checks Passing**
- [ ] **Security Audit Complete**
- [ ] **Team Trained on Cloud Operations**
- [ ] **Rollback Procedures Documented**

---

**Status Tracking**:
- [ ] Phase 1 Complete (Foundation)
- [ ] Phase 2 Complete (Security)
- [ ] Phase 3 Complete (IaC)
- [ ] Phase 4 Complete (Agent Integration)
- [ ] Phase 5 Complete (Cost Management)
- [ ] Phase 6 Complete (Production Hardening)
- [ ] Production Ready

---

**See Also**:
- [AI_CLOUD_INFRASTRUCTURE_INTEGRATION_SPEC.md](AI_CLOUD_INFRASTRUCTURE_INTEGRATION_SPEC.md) - Complete specification
- [AI_CLOUD_QUICK_REFERENCE.md](AI_CLOUD_QUICK_REFERENCE.md) - Quick reference guide
