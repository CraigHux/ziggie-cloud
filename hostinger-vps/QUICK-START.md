# ZIGGIE VPS - QUICK START GUIDE

> **Target**: Hostinger KVM 4 VPS @ 82.25.112.73
> **Domain**: ziggie.cloud
> **Time to Deploy**: 20-30 minutes
> **Difficulty**: Easy (automated script)

---

## PRE-DEPLOYMENT CHECKLIST (5 minutes)

### On Local Machine (Windows)

```powershell
# 1. Update nginx.conf with your domain
cd C:\Ziggie\hostinger-vps
# Edit nginx/nginx.conf: Replace ziggie.yourdomain.com with ziggie.cloud

# 2. Create .env file (copy from template)
cp .env.example .env

# 3. Fill in .env with your values (CRITICAL)
# Required minimum:
# - VPS_DOMAIN=ziggie.cloud
# - VPS_IP=82.25.112.73
# - Database passwords (will auto-generate if left as CHANGE_ME)
# - API keys from AWS Secrets Manager (optional for infrastructure-only deploy)

# 4. Retrieve AWS secrets (optional, for full deployment)
aws secretsmanager get-secret-value --secret-id ziggie/anthropic-api-key --region eu-north-1 --query SecretString --output text
aws secretsmanager get-secret-value --secret-id ziggie/openai-api-key --region eu-north-1 --query SecretString --output text

# 5. Upload to VPS
scp -r * ziggie@82.25.112.73:/tmp/ziggie-upload/
```

---

## DEPLOYMENT (15 minutes)

### On VPS (SSH)

```bash
# 1. SSH to VPS
ssh ziggie@82.25.112.73

# 2. Move files to /opt/ziggie
sudo mkdir -p /opt/ziggie
sudo chown -R ziggie:ziggie /opt/ziggie
cp -r /tmp/ziggie-upload/* /opt/ziggie/
cd /opt/ziggie

# 3. Make script executable
chmod +x DEPLOY-NOW.sh

# 4. Run deployment
./DEPLOY-NOW.sh

# Wait 15-20 minutes for:
# - Docker images to download (5-10 min)
# - Services to start (5 min)
# - Health checks to complete (2-3 min)
```

**Expected Output**:
```
============================================
  DEPLOYMENT COMPLETE!
============================================

Infrastructure Deployed (15 Services):
  Databases:   postgres, mongodb, redis
  Workflows:   n8n, flowise, open-webui, ollama
  Monitoring:  prometheus, grafana, loki, promtail
  Management:  portainer, watchtower, nginx, certbot

Access services at:
  Portainer:  http://82.25.112.73:9000
  n8n:        http://82.25.112.73:5678
  Flowise:    http://82.25.112.73:3001
  Open WebUI: http://82.25.112.73:3002
  Grafana:    http://82.25.112.73:3000
```

---

## POST-DEPLOYMENT (10 minutes)

### 1. Verify Services Running

```bash
cd /opt/ziggie
./health-check.sh
```

**Expected**: All services should show "OK" status

### 2. Setup Portainer (First-time)

1. Navigate to `http://82.25.112.73:9000`
2. Create admin username and password
3. Select "Local" environment
4. View all containers in UI

### 3. Login to n8n

1. Navigate to `http://82.25.112.73:5678`
2. Login: `admin` / `N8N_PASSWORD` (from .env)
3. Change password on first login

### 4. Setup SSL Certificate (AFTER DNS configured)

```bash
# Verify DNS first
dig +short ziggie.cloud
# Should return: 82.25.112.73

# Stop nginx
docker compose stop nginx

# Run certbot
docker run -it --rm \
  -v /opt/ziggie/certbot_certs:/etc/letsencrypt \
  -v /opt/ziggie/certbot_data:/var/www/certbot \
  -p 80:80 \
  certbot/certbot certonly \
  --standalone \
  --email your-email@example.com \
  --agree-tos \
  -d ziggie.cloud

# Restart nginx
docker compose up -d nginx

# Test HTTPS
curl -I https://ziggie.cloud/health
```

### 5. Pull LLM Models (Optional)

```bash
# Pull Llama 3.2 (3B params - good for 16GB RAM)
docker exec -it ziggie-ollama ollama pull llama3.2:3b

# Pull CodeLlama (7B params - for coding)
docker exec -it ziggie-ollama ollama pull codellama:7b

# Test chat
docker exec -it ziggie-ollama ollama run llama3.2:3b
# Type: "Hello, how are you?"
# Press Ctrl+D to exit
```

---

## SERVICE ACCESS GUIDE

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| **Portainer** | http://VPS_IP:9000 | Create on first access |
| **n8n** | http://VPS_IP:5678 | admin / N8N_PASSWORD (.env) |
| **Flowise** | http://VPS_IP:3001 | admin / FLOWISE_PASSWORD (.env) |
| **Open WebUI** | http://VPS_IP:3002 | Create user on first access |
| **Grafana** | http://VPS_IP:3000 | admin / GRAFANA_PASSWORD (.env) |
| **Prometheus** | http://VPS_IP:9090 | No auth |
| **Landing Page** | http://VPS_IP/ | Public |
| **Health Check** | http://VPS_IP/health | Public |

**With SSL (after setup)**:
- All services accessible via `https://ziggie.cloud/<path>/`
- Example: `https://ziggie.cloud/n8n/`

---

## COMMON COMMANDS

### Service Management

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart specific service
docker compose restart n8n

# View logs
docker compose logs -f n8n

# Check status
docker compose ps

# Run health check
/opt/ziggie/health-check.sh
```

### Database Access

```bash
# PostgreSQL
docker exec -it ziggie-postgres psql -U ziggie -d ziggie

# MongoDB
docker exec -it ziggie-mongodb mongosh

# Redis
docker exec -it ziggie-redis redis-cli -a "$(grep REDIS_PASSWORD .env | cut -d'=' -f2)"
```

### Ollama Commands

```bash
# List models
docker exec -it ziggie-ollama ollama list

# Pull model
docker exec -it ziggie-ollama ollama pull <model>

# Run model
docker exec -it ziggie-ollama ollama run <model>

# Delete model
docker exec -it ziggie-ollama ollama rm <model>
```

### Monitoring

```bash
# View resource usage
docker stats

# View disk usage
docker system df

# View container logs
docker compose logs --tail=100 <service>

# View all logs
docker compose logs -f
```

---

## TROUBLESHOOTING

### Container Won't Start

```bash
# View logs
docker compose logs <service-name> --tail=100

# Check if port is in use
sudo netstat -tlnp | grep <port>

# Restart service
docker compose restart <service-name>
```

### Database Connection Failed

```bash
# Verify database is healthy
docker compose ps postgres mongodb redis

# Test connection
docker exec -it ziggie-postgres pg_isready -U ziggie
docker exec -it ziggie-mongodb mongosh --eval "db.runCommand('ping')"
docker exec -it ziggie-redis redis-cli -a "PASSWORD" ping
```

### Nginx 502 Bad Gateway

```bash
# Check if upstream service is running
docker compose ps n8n

# View nginx logs
docker compose logs nginx --tail=50

# Restart nginx
docker compose restart nginx
```

### Out of Disk Space

```bash
# Check disk usage
df -h /
docker system df

# Clean up unused resources
docker system prune -a
docker volume prune
```

---

## BACKUP & RESTORE

### Manual Backup

```bash
# Backup all databases
/opt/ziggie/backup/scripts/backup-all.sh

# Backup to S3
/opt/ziggie/backup/scripts/backup-s3-sync.sh

# Verify backup
/opt/ziggie/backup/scripts/backup-verify.sh
```

### Setup Automated Backups

```bash
# Setup daily cron job
/opt/ziggie/backup/setup-cron.sh

# Verify cron is running
crontab -l
```

### Restore from Backup

```bash
# Restore PostgreSQL
/opt/ziggie/backup/scripts/restore-postgres.sh /path/to/backup.sql

# Restore MongoDB
/opt/ziggie/backup/scripts/restore-mongodb.sh /path/to/backup/

# Restore from S3
/opt/ziggie/backup/scripts/restore-from-s3.sh
```

---

## NEXT STEPS (Week 2)

### Deploy Application Services

Once infrastructure is stable, deploy application services:

1. **Build Docker Images**:
   ```bash
   # On local machine
   cd C:/Ziggie/ziggie-cloud-repo/api
   docker build -t ghcr.io/YOUR_USERNAME/ziggie-api:latest .
   docker push ghcr.io/YOUR_USERNAME/ziggie-api:latest

   # Repeat for mcp-gateway, sim-studio
   ```

2. **Update docker-compose.yml**:
   ```yaml
   services:
     ziggie-api:
       image: ghcr.io/YOUR_USERNAME/ziggie-api:latest
       # Remove build: section
   ```

3. **Deploy**:
   ```bash
   docker compose pull ziggie-api mcp-gateway sim-studio
   docker compose up -d ziggie-api mcp-gateway sim-studio
   ```

### Configure Monitoring

1. Add Prometheus data source to Grafana
2. Import Docker dashboard (ID: 893)
3. Import Node Exporter dashboard (ID: 1860)
4. Setup alerts for critical services

### Setup CI/CD

1. Generate GitHub runner token
2. Add to .env: `GITHUB_RUNNER_TOKEN=<token>`
3. Start runner: `docker compose up -d github-runner`
4. Configure GitHub Actions workflows

---

## COST MONITORING

### Expected Costs

| Item | Monthly Cost |
|------|--------------|
| Hostinger KVM 4 VPS | $12-15 |
| Domain (ziggie.cloud) | ~$1 (if yearly) |
| SSL Certificate | $0 (Let's Encrypt) |
| **Total** | **$13-16/month** |

**With AWS Integration**:
- S3 Storage (100GB): +$2-5/month
- Secrets Manager: +$1.60/month
- Lambda: +$0.20/month
- **Total with AWS**: $17-23/month

---

## SUPPORT & DOCUMENTATION

### Documentation

- **Comprehensive Checklist**: `C:\Ziggie\docs\VPS-DEPLOYMENT-COMPREHENSIVE-CHECKLIST.md` (1,415 lines)
- **Gap Analysis**: `C:\Ziggie\docs\VPS-DEPLOYMENT-GAP-ANALYSIS.md` (comprehensive)
- **This Quick Start**: `C:\Ziggie\hostinger-vps\QUICK-START.md`

### Logs

- **Deployment Log**: `/opt/ziggie/deploy-YYYYMMDD_HHMMSS.log`
- **Container Logs**: `docker compose logs <service>`
- **System Logs**: `/var/log/syslog`

### Health Checks

```bash
# Quick status
docker compose ps

# Detailed health
/opt/ziggie/health-check.sh

# Resource usage
docker stats --no-stream
```

---

## ESTIMATED TIMELINE

| Phase | Task | Duration |
|-------|------|----------|
| **Pre-Deploy** | Prepare files, configure .env | 5 min |
| **Upload** | SCP files to VPS | 2 min |
| **Deploy** | Run DEPLOY-NOW.sh script | 15-20 min |
| **Verify** | Health checks, test services | 5 min |
| **SSL Setup** | Certbot + nginx restart | 5 min |
| **First Login** | Portainer, n8n, Grafana | 5 min |
| **Pull Models** | Ollama llama3.2:3b | 10 min |
| **Total** | **Full Deployment** | **47-52 min** |

---

**Ready to Deploy?**

```bash
# Run this on VPS:
cd /opt/ziggie
./DEPLOY-NOW.sh
```

**Questions?** Check the comprehensive documentation:
- `C:\Ziggie\docs\VPS-DEPLOYMENT-COMPREHENSIVE-CHECKLIST.md`
- `C:\Ziggie\docs\VPS-DEPLOYMENT-GAP-ANALYSIS.md`
