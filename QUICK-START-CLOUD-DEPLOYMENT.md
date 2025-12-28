# Quick Start: Cloud Deployment for Ziggie

> **5-Minute Guide to Deploy MCP Servers to AWS and Hostinger**
> **Full documentation**: [MCP-CLOUD-INTEGRATION-ARCHITECTURE.md](MCP-CLOUD-INTEGRATION-ARCHITECTURE.md)

---

## Architecture Overview

```
LOCAL PC (Your Windows Machine)
├─ Unity/Unreal/Godot MCPs → Game engine control
├─ LM Studio → Free local LLM
└─ Development workflows

    ↓ HTTPS

HOSTINGER VPS ($6.49/month)
├─ MCP Gateway → Central routing
├─ n8n → Workflow automation
├─ Sim Studio → Agent coordination
└─ PostgreSQL + Redis → State management

    ↓ AWS API

AWS (Spot Instances)
├─ ComfyUI on EC2 G4dn.xlarge (~$38/month for 8hr/day)
└─ S3 Storage (~$2/month for 100GB)

TOTAL COST: ~$47/month
```

---

## Deployment Steps

### Step 1: AWS Infrastructure (30 minutes)

```bash
# Clone deployment scripts
cd C:/Ziggie
git clone https://github.com/yourusername/ziggie-cloud-infra.git
cd ziggie-cloud-infra

# Configure AWS credentials
aws configure
# AWS Access Key ID: [your key]
# AWS Secret Access Key: [your secret]
# Default region: us-east-1

# Run automated setup
./deploy-aws-infrastructure.sh
```

**What this does**:
- Creates S3 bucket `meowping-game-assets`
- Sets up IAM roles for EC2
- Configures spot instance templates
- Uploads SDXL models to S3

### Step 2: Hostinger VPS Setup (20 minutes)

```bash
# SSH to your Hostinger VPS
ssh root@your-vps-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone configuration
git clone https://github.com/yourusername/ziggie-cloud-infra.git
cd ziggie-cloud-infra/hostinger

# Create environment file
cp .env.example .env
nano .env  # Edit with your credentials

# Start services
docker compose up -d

# Setup SSL (if you have a domain)
./setup-ssl.sh yourdomain.com
```

**What this does**:
- Deploys MCP Gateway, n8n, Sim Studio, PostgreSQL, Redis
- Configures Nginx reverse proxy
- Sets up SSL certificates (optional)

### Step 3: Local Configuration (10 minutes)

```bash
# Update Claude Desktop config
notepad %APPDATA%\Roaming\Claude\claude_desktop_config.json
```

Add these servers:
```json
{
  "mcpServers": {
    "comfyui": {
      "command": "python",
      "args": ["C:/ai-game-dev-system/infrastructure/aws/comfyui_mcp_client.py"],
      "env": {"AWS_REGION": "us-east-1"}
    },
    "llm": {
      "command": "python",
      "args": ["C:/ai-game-dev-system/infrastructure/llm_router.py"],
      "env": {
        "PRIMARY_LLM_URL": "http://localhost:1234/v1",
        "FALLBACK_LLM_URL": "https://mcp.yourdomain.com/ollama"
      }
    }
  }
}
```

### Step 4: Test Everything (10 minutes)

```bash
# Test AWS ComfyUI
python infrastructure/aws/aws_gpu_controller.py start comfyui
# Wait 2 minutes for startup
curl http://[EC2-IP]:8188/system_stats

# Test Hostinger VPS
curl https://mcp.yourdomain.com/health

# Test local MCPs
curl http://localhost:8080/mcp  # Unity
curl http://localhost:1234/v1/models  # LM Studio

# Run E2E test
python tests/test_e2e_generation.py
```

---

## Common Commands

### AWS Management
```bash
# Start ComfyUI (only when needed)
python infrastructure/aws/aws_gpu_controller.py start comfyui

# Stop ComfyUI (save costs!)
python infrastructure/aws/aws_gpu_controller.py stop comfyui

# Check costs
python infrastructure/cost_tracker.py
```

### VPS Management
```bash
# View logs
ssh root@vps "docker compose logs -f n8n"

# Restart services
ssh root@vps "docker compose restart"

# Update services
ssh root@vps "docker compose pull && docker compose up -d"
```

### Generate Assets
```bash
# Via Claude Code in Ziggie project
"Generate 10 cat warrior sprites for blue team"

# Via n8n webhook
curl -X POST https://n8n.yourdomain.com/webhook/generate-sprites \
  -H "Content-Type: application/json" \
  -d '{"prompt": "cat warrior archer, isometric view", "count": 10}'
```

---

## Cost Breakdown

| Service | Cost | Usage |
|---------|------|-------|
| **Hostinger VPS (KVM 2)** | $6.49/month | 24/7 orchestration |
| **AWS EC2 Spot (g4dn.xlarge)** | $38/month | 8 hrs/day avg |
| **AWS S3 Storage (100GB)** | $1.75/month | After lifecycle to IA |
| **AWS Data Transfer** | $1/month | <10GB egress |
| **Domain + SSL** | $0/month | Free with Let's Encrypt |
| **TOTAL** | **~$47/month** | |

**Cost Savings**:
- Spot instances: 70% off on-demand ($126 → $38)
- Auto-shutdown: Save $0.16/hour when idle
- S3 lifecycle: 70% cheaper after 30 days
- Local LLM: $0 vs $20/month Claude API

---

## Troubleshooting

### Issue: ComfyUI takes too long to generate
**Solution**: Upgrade to G5.xlarge (60% faster, +$34/month)
```bash
# Edit instance_configs in aws_gpu_controller.py
"instance_type": "g5.xlarge"  # Was g4dn.xlarge
```

### Issue: High AWS costs
**Immediate actions**:
1. Stop all instances: `aws ec2 stop-instances --instance-ids i-xxx`
2. Check S3 usage: `aws s3 ls s3://meowping-game-assets --summarize`
3. Enable cost alerts in AWS Budgets ($50/month threshold)

### Issue: n8n workflows fail
**Debug steps**:
1. Check logs: `docker logs n8n`
2. Verify Redis: `docker exec -it redis redis-cli ping`
3. Restart queue workers: `docker compose restart n8n`

---

## Next Steps

1. **Create your first n8n workflow**
   - Log into n8n: https://n8n.yourdomain.com
   - Import template: `cat_warrior_generation.json`
   - Test with webhook trigger

2. **Setup monitoring**
   - Enable CloudWatch alarms (CPU > 80%)
   - Configure cost alerts ($50/month)
   - Add Grafana dashboards (optional)

3. **Optimize costs**
   - Review auto-shutdown settings (30min idle)
   - Compress assets before S3 upload (WebP)
   - Use S3 Intelligent-Tiering for unpredictable access

4. **Scale up**
   - Add more EC2 instances for parallel generation
   - Upgrade VPS to KVM 4 (4 vCPU, 16GB RAM) if needed
   - Implement GPU render farm (g4dn.12xlarge)

---

## Key Files

| File | Purpose |
|------|---------|
| `MCP-CLOUD-INTEGRATION-ARCHITECTURE.md` | Complete technical specification (1300+ lines) |
| `infrastructure/aws/aws_gpu_controller.py` | AWS EC2 management script |
| `infrastructure/aws/comfyui_mcp_client.py` | MCP client for ComfyUI |
| `hostinger/docker-compose.yml` | VPS service definitions |
| `hostinger/nginx.conf` | Reverse proxy configuration |
| `tests/test_e2e_generation.py` | End-to-end verification tests |

---

**Deployment Time**: ~1 hour
**Monthly Cost**: $47
**Maintenance**: <1 hour/month

**Questions?** See full documentation: [MCP-CLOUD-INTEGRATION-ARCHITECTURE.md](MCP-CLOUD-INTEGRATION-ARCHITECTURE.md)
