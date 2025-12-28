# MCP Cloud Deployment Checklist

> **Track your progress deploying the Ziggie cloud infrastructure**
> **Estimated time**: 2.5 hours
> **Target cost**: $47/month

---

## Pre-Deployment Requirements

### AWS Account Setup
- [ ] AWS account created (https://aws.amazon.com)
- [ ] Payment method added
- [ ] IAM user created with programmatic access
- [ ] Access key ID and secret saved securely
- [ ] AWS CLI installed locally (`winget install Amazon.AWSCLI`)
- [ ] AWS credentials configured (`aws configure`)
- [ ] Service quotas verified (EC2 G4dn instances: need 4 vCPU minimum)

### Hostinger VPS Setup
- [ ] Hostinger account created (https://hostinger.com)
- [ ] KVM 2 plan purchased ($6.49/month with promo)
- [ ] Ubuntu 24.04 LTS selected as OS
- [ ] VPS IP address noted: `___________________`
- [ ] Root password set
- [ ] SSH key uploaded (optional but recommended)

### Domain & DNS (Optional)
- [ ] Domain name purchased (or using free subdomain)
- [ ] DNS A records created:
  - [ ] `mcp.yourdomain.com` → VPS IP
  - [ ] `n8n.yourdomain.com` → VPS IP
  - [ ] `studio.yourdomain.com` → VPS IP
- [ ] DNS propagation verified (use https://dnschecker.org)

### Local Prerequisites
- [ ] Python 3.10+ installed
- [ ] Git installed
- [ ] LM Studio installed (for local LLM)
- [ ] Claude Desktop installed
- [ ] Unity/Unreal/Godot MCP servers configured (from C:/ai-game-dev-system)

---

## Phase 1: AWS Infrastructure (30 minutes)

### S3 Bucket Setup
- [ ] Run `aws s3 mb s3://meowping-game-assets --region us-east-1`
- [ ] Enable versioning
- [ ] Configure lifecycle policy (Standard → IA after 30 days)
- [ ] Test access: `aws s3 ls s3://meowping-game-assets`

### IAM Role Configuration
- [ ] Create role `EC2-ComfyUI-Role`
- [ ] Attach `AmazonSSMManagedInstanceCore` policy
- [ ] Attach `CloudWatchAgentServerPolicy` policy
- [ ] Create inline S3 access policy (ReadWrite to meowping-game-assets)
- [ ] Create instance profile `EC2-ComfyUI-Profile`
- [ ] Add role to instance profile

### Security Group Setup
- [ ] Create security group `meowping-comfyui-sg`
- [ ] Add inbound rule: TCP 8188 from VPS IP only
- [ ] Add inbound rule: TCP 22 (for SSM, no public internet)
- [ ] Verify outbound allows HTTPS (443) for model downloads

### EC2 Launch Template
- [ ] Create launch template for G4dn.xlarge
- [ ] Select Deep Learning AMI (latest PyTorch Ubuntu)
- [ ] Attach IAM role `EC2-ComfyUI-Profile`
- [ ] Add user data script (from MCP-CLOUD-INTEGRATION-ARCHITECTURE.md)
- [ ] Configure 100GB gp3 EBS volume
- [ ] Test launch (on-demand first, then terminate)

### Spot Fleet Configuration
- [ ] Create spot fleet request
- [ ] Set target capacity: 1
- [ ] Set max spot price: $0.20 (on-demand is $0.526)
- [ ] Configure allocation strategy: lowestPrice
- [ ] Set interruption behavior: stop (not terminate)
- [ ] Add tags: Project=MeowPing, Tool=ComfyUI

### Model Upload to S3
- [ ] Download SDXL base model (6.94 GB)
- [ ] Download SDXL refiner (optional, 6.08 GB)
- [ ] Download LoRA models for MeowPing style
- [ ] Upload to S3: `aws s3 sync ~/Downloads/models/ s3://meowping-game-assets/models/sdxl/`
- [ ] Verify upload: `aws s3 ls s3://meowping-game-assets/models/sdxl/`

**Phase 1 Completion Time**: __________ (Target: 30 min)

---

## Phase 2: Hostinger VPS Setup (45 minutes)

### Initial VPS Configuration
- [ ] SSH to VPS: `ssh root@[VPS-IP]`
- [ ] Update system: `apt-get update && apt-get upgrade -y`
- [ ] Set hostname: `hostnamectl set-hostname ziggie-vps`
- [ ] Configure timezone: `timedatectl set-timezone America/New_York`
- [ ] Install essential tools: `apt-get install -y curl git htop`

### Docker Installation
- [ ] Install Docker: `curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh`
- [ ] Enable Docker: `systemctl enable docker`
- [ ] Test Docker: `docker run hello-world`
- [ ] Install Docker Compose: `apt-get install -y docker-compose-v2`
- [ ] Verify: `docker compose version`

### Firewall Configuration
- [ ] Install UFW: `apt-get install -y ufw`
- [ ] Allow SSH: `ufw allow 22/tcp`
- [ ] Allow HTTP: `ufw allow 80/tcp`
- [ ] Allow HTTPS: `ufw allow 443/tcp`
- [ ] Enable firewall: `ufw enable`
- [ ] Verify rules: `ufw status`

### Clone Project Repository
- [ ] Create working directory: `mkdir -p /root/ziggie-cloud`
- [ ] Navigate: `cd /root/ziggie-cloud`
- [ ] Clone repo: `git clone [your-repo-url] .`
- [ ] Verify files: `ls -la docker-compose.yml nginx.conf`

### Configure Environment Variables
- [ ] Copy template: `cp .env.example .env`
- [ ] Generate secrets:
  ```bash
  POSTGRES_PASSWORD=$(openssl rand -base64 32)
  N8N_PASSWORD=$(openssl rand -base64 16)
  N8N_ENCRYPTION_KEY=$(openssl rand -base64 32)
  ```
- [ ] Edit .env: `nano .env`
- [ ] Set AWS credentials in .env
- [ ] Set ComfyUI AWS IP (will update after EC2 launch)
- [ ] Save and verify: `cat .env | grep -v PASSWORD`

### Start Docker Services
- [ ] Pull images: `docker compose pull`
- [ ] Start services: `docker compose up -d`
- [ ] Wait 60 seconds for initialization
- [ ] Check status: `docker compose ps`
- [ ] Verify all containers show "running" status

### Service Health Checks
- [ ] PostgreSQL: `docker exec -it postgres pg_isready`
- [ ] Redis: `docker exec -it redis redis-cli ping`
- [ ] MCP Gateway: `curl http://localhost:9000/health`
- [ ] n8n: `curl http://localhost:5678/healthz`
- [ ] Sim Studio: `curl http://localhost:3001/api/health`
- [ ] View logs: `docker compose logs -f` (Ctrl+C to exit)

### SSL Certificate Setup (If using domain)
- [ ] Stop Nginx: `docker compose stop nginx`
- [ ] Install Certbot: `apt-get install -y certbot`
- [ ] Request certificate:
  ```bash
  certbot certonly --standalone \
    -d mcp.yourdomain.com \
    -d n8n.yourdomain.com \
    -d studio.yourdomain.com \
    --email your@email.com \
    --agree-tos
  ```
- [ ] Verify certificate: `ls /etc/letsencrypt/live/yourdomain.com/`
- [ ] Update nginx.conf with correct domain
- [ ] Restart Nginx: `docker compose up -d nginx`
- [ ] Test HTTPS: `curl https://mcp.yourdomain.com/health`
- [ ] Setup auto-renewal cron: `echo "0 0 * * * certbot renew --quiet && docker compose restart nginx" | crontab -`

**Phase 2 Completion Time**: __________ (Target: 45 min)

---

## Phase 3: Local MCP Configuration (15 minutes)

### Install Python Dependencies
- [ ] Navigate: `cd C:/ai-game-dev-system/infrastructure`
- [ ] Create venv: `python -m venv venv`
- [ ] Activate: `venv\Scripts\activate`
- [ ] Install: `pip install boto3 mcp requests`
- [ ] Verify: `python -c "import boto3; print(boto3.__version__)"`

### Create MCP Client Scripts
- [ ] Copy `comfyui_mcp_client.py` from architecture doc
- [ ] Copy `llm_router.py` from architecture doc
- [ ] Test AWS connection: `python comfyui_mcp_client.py --test`
- [ ] Test LLM router: `python llm_router.py --test`

### Update Claude Desktop Config
- [ ] Backup existing config:
  ```bash
  copy "%APPDATA%\Roaming\Claude\claude_desktop_config.json" "%APPDATA%\Roaming\Claude\claude_desktop_config.json.backup"
  ```
- [ ] Open config: `notepad %APPDATA%\Roaming\Claude\claude_desktop_config.json`
- [ ] Add comfyui MCP server entry
- [ ] Add llm MCP server entry
- [ ] Verify existing Unity/Unreal/Godot entries still present
- [ ] Save and validate JSON syntax (use https://jsonlint.com)

### Restart Claude Desktop
- [ ] Close Claude Desktop completely (check Task Manager)
- [ ] Relaunch Claude Desktop
- [ ] Verify MCP servers loaded (check status indicator)
- [ ] Test simple command: "Check ComfyUI status"

**Phase 3 Completion Time**: __________ (Target: 15 min)

---

## Phase 4: Integration Testing (30 minutes)

### AWS Connectivity Tests
- [ ] Start ComfyUI instance:
  ```bash
  python infrastructure/aws/aws_gpu_controller.py start comfyui
  ```
- [ ] Wait 2 minutes for instance boot
- [ ] Verify EC2 running: `aws ec2 describe-instances --filters "Name=tag:Name,Values=MeowPing-ComfyUI"`
- [ ] Get public IP: `python -c "from aws_gpu_controller import AWSGPUController; c=AWSGPUController(); print(c.get_status()['comfyui']['public_ip'])"`
- [ ] Test ComfyUI API: `curl http://[EC2-IP]:8188/system_stats`
- [ ] Expected output: JSON with GPU info

### S3 Access Tests
- [ ] Upload test file: `echo "test" > test.txt && aws s3 cp test.txt s3://meowping-game-assets/test/`
- [ ] Download test file: `aws s3 cp s3://meowping-game-assets/test/test.txt test-download.txt`
- [ ] Verify: `cat test-download.txt` (should show "test")
- [ ] Cleanup: `rm test.txt test-download.txt && aws s3 rm s3://meowping-game-assets/test/test.txt`

### VPS Service Tests
- [ ] MCP Gateway health: `curl https://mcp.yourdomain.com/health`
  - [ ] Expected: JSON with all service statuses
- [ ] n8n login: Open https://n8n.yourdomain.com
  - [ ] Login with credentials from .env
  - [ ] Create test workflow (Hello World webhook)
  - [ ] Test webhook: `curl -X POST https://n8n.yourdomain.com/webhook-test/hello`
- [ ] Sim Studio: Open https://studio.yourdomain.com
  - [ ] Verify UI loads
  - [ ] Check agent list

### Local MCP Tests
- [ ] Unity MCP: `curl http://localhost:8080/mcp`
  - [ ] Expected: MCP server info JSON
- [ ] LM Studio: `curl http://localhost:1234/v1/models`
  - [ ] Expected: List of loaded models
- [ ] Test in Claude Desktop:
  - [ ] "Create a red cube in Unity at (0, 0, 0)"
  - [ ] Verify cube appears in Unity scene

### End-to-End Asset Generation Test
- [ ] In Claude Desktop (in Ziggie project):
  ```
  Generate a single test sprite: cat warrior, blue team, isometric view.
  Use ComfyUI on AWS. Save to C:/ai-game-dev-system/generated_assets/test/
  ```
- [ ] Expected workflow:
  1. Claude calls comfyui MCP
  2. MCP client starts EC2 if needed
  3. Submits generation job to ComfyUI
  4. Polls for completion
  5. Downloads image to local path
- [ ] Verify output file exists
- [ ] Open image and verify quality
- [ ] Check S3 upload: `aws s3 ls s3://meowping-game-assets/generated/`

**Phase 4 Completion Time**: __________ (Target: 30 min)

---

## Phase 5: Cost Optimization (15 minutes)

### Enable Auto-Shutdown
- [ ] Verify EC2 user data includes check-idle.sh script
- [ ] Test idle detection: SSH to EC2 via SSM
  ```bash
  aws ssm start-session --target [instance-id]
  cat /usr/local/bin/check-idle.sh
  ```
- [ ] Verify cron job: `crontab -l | grep check-idle`
- [ ] Expected: `*/5 * * * * /usr/local/bin/check-idle.sh`

### Configure S3 Lifecycle
- [ ] Verify lifecycle policy applied:
  ```bash
  aws s3api get-bucket-lifecycle-configuration --bucket meowping-game-assets
  ```
- [ ] Expected: Transition to STANDARD_IA after 30 days

### Setup Cost Alerts
- [ ] Navigate to AWS Budgets: https://console.aws.amazon.com/billing/home#/budgets
- [ ] Create budget: "Monthly Cost Alert"
- [ ] Set amount: $60/month
- [ ] Add alert thresholds:
  - [ ] 80% ($48) → Email warning
  - [ ] 100% ($60) → Email alert
  - [ ] 120% ($72) → Email critical
- [ ] Set alert email: __________________
- [ ] Save budget

### Enable CloudWatch Alarms
- [ ] Create alarm: EC2 CPU > 80% for 5 minutes
  - [ ] Action: Send SNS notification
  - [ ] Email: __________________
- [ ] Create alarm: ComfyUI idle for 30 minutes
  - [ ] Action: Stop instance (via Lambda)
- [ ] Test SNS: `aws sns publish --topic-arn [arn] --message "Test"`

### Run Initial Cost Report
- [ ] Execute: `python infrastructure/cost_tracker.py`
- [ ] Review output (should be ~$0 for first day)
- [ ] Schedule weekly reports:
  ```bash
  # Windows Task Scheduler or cron
  schtasks /create /tn "Ziggie Cost Report" /tr "python C:\ai-game-dev-system\infrastructure\cost_tracker.py" /sc weekly /d MON /st 09:00
  ```

**Phase 5 Completion Time**: __________ (Target: 15 min)

---

## Phase 6: Documentation & Handoff (15 minutes)

### Create Operations Runbook
- [ ] Document VPS IP, credentials (in password manager)
- [ ] Document AWS account ID, region
- [ ] Document S3 bucket name, IAM role ARNs
- [ ] Document emergency contacts (if team environment)

### Setup Monitoring Dashboard
- [ ] (Optional) Deploy Grafana: `docker compose --profile monitoring up -d`
- [ ] Import dashboards from `grafana-dashboards/`
- [ ] Configure Prometheus data source
- [ ] Test dashboard access: https://yourdomain.com:3000

### Backup Critical Data
- [ ] Backup PostgreSQL:
  ```bash
  docker exec postgres pg_dump -U postgres -d sim_studio > backup-sim-studio.sql
  docker exec postgres pg_dump -U postgres -d n8n > backup-n8n.sql
  ```
- [ ] Backup n8n workflows: `docker cp n8n:/home/node/.n8n/workflows ./n8n-workflows-backup/`
- [ ] Upload backups to S3:
  ```bash
  aws s3 sync ./backups/ s3://meowping-game-assets/backups/$(date +%Y-%m-%d)/
  ```

### Schedule Automated Backups
- [ ] Create backup script: `/root/ziggie-cloud/backup.sh`
- [ ] Make executable: `chmod +x backup.sh`
- [ ] Add to crontab (daily at 2 AM):
  ```bash
  echo "0 2 * * * /root/ziggie-cloud/backup.sh" | crontab -
  ```
- [ ] Test backup: `./backup.sh && ls -lh backups/`

### Update Project README
- [ ] Add deployment info to Ziggie README.md
- [ ] Document MCP endpoints
- [ ] Add troubleshooting section
- [ ] Commit and push to Git

**Phase 6 Completion Time**: __________ (Target: 15 min)

---

## Post-Deployment Verification

### 24-Hour Checkup
- [ ] Date: __________
- [ ] Check AWS costs: https://console.aws.amazon.com/billing/
- [ ] Verify EC2 auto-stopped after idle period
- [ ] Review CloudWatch logs for errors
- [ ] Test asset generation again (verify still works)

### 7-Day Review
- [ ] Date: __________
- [ ] Review cost report (should be <$10 for first week)
- [ ] Check S3 storage growth (expect ~1-5 GB)
- [ ] Verify n8n workflows executed successfully
- [ ] Review VPS resource usage (CPU, RAM, disk)
- [ ] Test all fallback chains (local LLM → VPS Ollama)

### 30-Day Audit
- [ ] Date: __________
- [ ] Full cost review (target: <$50/month)
- [ ] S3 lifecycle verified (files moved to IA)
- [ ] Review generated asset quality
- [ ] Optimize n8n workflows based on usage
- [ ] Consider scaling adjustments (upgrade/downgrade)

---

## Troubleshooting Quick Reference

### ComfyUI won't start
1. Check spot availability: `aws ec2 describe-spot-price-history --instance-types g4dn.xlarge`
2. Try on-demand: `python aws_gpu_controller.py start comfyui --no-spot`
3. Check service quotas: https://console.aws.amazon.com/servicequotas/

### n8n workflows timeout
1. Check logs: `docker logs n8n`
2. Increase timeout in workflow settings (max 300s)
3. Restart Redis: `docker compose restart redis`

### High costs
1. Stop all instances: `python aws_gpu_controller.py stop comfyui`
2. Check S3 usage: `aws s3 ls s3://meowping-game-assets --recursive --summarize`
3. Review CloudWatch metrics for unexpected usage

### SSL certificate renewal fails
1. Stop Nginx: `docker compose stop nginx`
2. Renew manually: `certbot renew`
3. Restart Nginx: `docker compose up -d nginx`

---

## Deployment Sign-Off

**Deployment Date**: __________
**Deployed By**: __________
**Total Time Spent**: __________ hours (Target: 2.5 hours)
**Initial Monthly Cost Estimate**: $__________ (Target: $47)

### Verification Checklist
- [ ] All 7+ MCP servers accessible
- [ ] E2E asset generation test passed
- [ ] Cost alerts configured
- [ ] Backups configured
- [ ] Documentation complete

**Status**: ⬜ Complete ⬜ Incomplete ⬜ Blocked

**Notes**:
______________________________________________________________________________
______________________________________________________________________________
______________________________________________________________________________

---

**Next Steps After Deployment**:
1. Generate 10 test assets (various categories)
2. Create n8n workflow for batch generation
3. Setup Sim Studio agents for asset pipeline
4. Integrate with Unity/Unreal projects
5. Monitor costs weekly for first month

**Support Resources**:
- Full documentation: `MCP-CLOUD-INTEGRATION-ARCHITECTURE.md`
- Quick start guide: `QUICK-START-CLOUD-DEPLOYMENT.md`
- AWS troubleshooting: https://repost.aws/
- Hostinger support: https://www.hostinger.com/support
