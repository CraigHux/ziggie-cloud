# Ziggie VPS Docker Deployment Checklist

> **Version**: 2.0.0
> **Date**: 2025-12-28
> **Target**: Hostinger KVM 4 VPS (82.25.112.73)
> **Author**: L1 Strategic Agent - Session C

---

## Table of Contents

1. [Pre-Deployment Requirements](#1-pre-deployment-requirements)
2. [Service Architecture](#2-service-architecture)
3. [Deployment Methods](#3-deployment-methods)
4. [Step-by-Step Deployment](#4-step-by-step-deployment)
5. [Health Verification](#5-health-verification)
6. [Post-Deployment Tasks](#6-post-deployment-tasks)
7. [Troubleshooting](#7-troubleshooting)
8. [Rollback Procedures](#8-rollback-procedures)

---

## 1. Pre-Deployment Requirements

### 1.1 VPS Specifications

| Requirement | Minimum | Recommended | Ziggie VPS |
|-------------|---------|-------------|------------|
| RAM | 8GB | 16GB | 16GB |
| vCPUs | 2 | 4 | 4 |
| Storage | 100GB | 200GB NVMe | 200GB NVMe |
| OS | Ubuntu 22.04+ | Ubuntu 24.04 | Ubuntu 24.04 |

### 1.2 Pre-Requisite Checklist

- [ ] **VPS Provisioned**: Hostinger KVM 4 or equivalent
- [ ] **SSH Access**: Root or sudo access configured
- [ ] **Docker Installed**: Docker Engine 24.0+
- [ ] **Docker Compose**: Docker Compose V2 (plugin)
- [ ] **Domain DNS**: ziggie.cloud pointing to VPS IP
- [ ] **Subdomain DNS**: All 8 subdomains configured
- [ ] **Firewall Rules**: Ports 80, 443, 22 open
- [ ] **SSH Key**: Passwordless SSH access (for remote deployment)

### 1.3 DNS Configuration Required

Configure these DNS records at Hostinger:

| Record Type | Hostname | Value | TTL |
|-------------|----------|-------|-----|
| A | @ | 82.25.112.73 | 14400 |
| A | api | 82.25.112.73 | 14400 |
| A | n8n | 82.25.112.73 | 14400 |
| A | grafana | 82.25.112.73 | 14400 |
| A | portainer | 82.25.112.73 | 14400 |
| A | flowise | 82.25.112.73 | 14400 |
| A | chat | 82.25.112.73 | 14400 |
| A | mcp | 82.25.112.73 | 14400 |
| A | sim | 82.25.112.73 | 14400 |

### 1.4 Verify DNS Propagation

```bash
# Check DNS resolution
dig +short ziggie.cloud
dig +short api.ziggie.cloud
dig +short n8n.ziggie.cloud

# Expected output: 82.25.112.73
```

---

## 2. Service Architecture

### 2.1 Complete 19-Service Stack

```
ZIGGIE COMMAND CENTER - 19 Services
===================================

DATABASES (3 services)
├── postgres       : PostgreSQL 15 (Primary relational DB)
├── mongodb        : MongoDB 7 (Document store, agent state)
└── redis          : Redis 7 (Cache, sessions, message broker)

WORKFLOW ORCHESTRATION (2 services)
├── n8n            : Workflow automation hub
└── flowise        : LLM visual workflow builder

AI/LLM SERVICES (2 services)
├── ollama         : Local LLM inference server
└── open-webui     : Chat interface for Ollama

APPLICATION LAYER (3 services)
├── mcp-gateway    : MCP request router *
├── ziggie-api     : Core API (FastAPI) *
└── sim-studio     : Agent simulation platform *

MONITORING (4 services)
├── prometheus     : Metrics collection
├── grafana        : Dashboards & visualization
├── loki           : Log aggregation
└── promtail       : Log shipping

MANAGEMENT (2 services)
├── portainer      : Docker visual management
└── watchtower     : Auto-update containers

PROXY/SSL (2 services)
├── nginx          : Reverse proxy with SSL
└── certbot        : SSL certificate management

CI/CD (1 service)
└── github-runner  : Self-hosted GitHub Actions runner

* Requires pre-built Docker images (not available by default)
```

### 2.2 Service Dependencies

```
postgres ─┬─> n8n
          ├─> ziggie-api
          └─> sim-studio

mongodb ──┬─> mcp-gateway
          ├─> ziggie-api
          └─> sim-studio

redis ────┬─> n8n
          ├─> mcp-gateway
          └─> ziggie-api

ollama ───┬─> flowise
          ├─> open-webui
          ├─> mcp-gateway
          └─> sim-studio

prometheus ──> grafana

loki ──────> promtail

All services ──> nginx (reverse proxy)
```

### 2.3 Port Mapping

| Service | Internal Port | External Port | Protocol |
|---------|--------------|---------------|----------|
| nginx | 80, 443 | 80, 443 | HTTP/HTTPS |
| portainer | 9000 | 9000 | HTTP |
| n8n | 5678 | 5678 | HTTP |
| flowise | 3000 | 3001 | HTTP |
| open-webui | 8080 | 3002 | HTTP |
| grafana | 3000 | 3000 | HTTP |
| prometheus | 9090 | 9090 | HTTP |
| loki | 3100 | 3100 | HTTP |
| ollama | 11434 | 11434 | HTTP |
| ziggie-api | 8000 | 8000 | HTTP |
| mcp-gateway | 8080 | 8080 | HTTP |
| sim-studio | 8001 | 8001 | HTTP |
| postgres | 5432 | 5432 | TCP |
| mongodb | 27017 | 27017 | TCP |
| redis | 6379 | 6379 | TCP |

---

## 3. Deployment Methods

### 3.1 Method A: Automated Script (Recommended)

Use the production deployment script for automated deployment:

```bash
# From development machine (remote deployment)
./hostinger-vps/scripts/deploy-production.sh --remote

# From VPS directly (local deployment)
./deploy-production.sh

# Preview without executing
./deploy-production.sh --dry-run

# Force restart all services
./deploy-production.sh --force --remote
```

### 3.2 Method B: Manual Deployment

For granular control or troubleshooting:

```bash
# SSH to VPS
ssh root@82.25.112.73

# Navigate to Ziggie directory
cd /opt/ziggie

# Pull latest images
docker compose pull

# Start databases first
docker compose up -d postgres mongodb redis
sleep 30

# Start core services
docker compose up -d n8n ollama flowise open-webui
sleep 20

# Start monitoring
docker compose up -d prometheus grafana loki promtail

# Start management
docker compose up -d portainer watchtower nginx certbot

# Verify all services
docker compose ps
```

### 3.3 Method C: Staged Deployment

For initial setup or major updates:

```bash
# Phase 1: Infrastructure Only (15 services)
docker compose up -d \
    postgres mongodb redis \
    n8n ollama flowise open-webui \
    prometheus grafana loki promtail \
    portainer watchtower nginx certbot

# Phase 2: Applications (after building images)
docker compose up -d mcp-gateway ziggie-api sim-studio
```

---

## 4. Step-by-Step Deployment

### Phase 1: SSH Access

```bash
# Connect to VPS
ssh root@82.25.112.73

# Verify Docker
docker --version
docker compose version
```

### Phase 2: Clone/Update Repository

```bash
# First-time setup
mkdir -p /opt/ziggie
cd /opt/ziggie

# Option A: Clone from GitHub (if public)
git clone https://github.com/your-org/ziggie.git .

# Option B: Upload via rsync (from dev machine)
rsync -avz --progress \
    -e "ssh -i ~/.ssh/id_rsa" \
    ./hostinger-vps/ \
    root@82.25.112.73:/opt/ziggie/
```

### Phase 3: Configure Environment

```bash
cd /opt/ziggie

# Create .env from template
cp .env.example .env

# Generate secure passwords
sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$(openssl rand -base64 24 | tr -d '/+=')/" .env
sed -i "s/MONGO_PASSWORD=.*/MONGO_PASSWORD=$(openssl rand -base64 24 | tr -d '/+=')/" .env
sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$(openssl rand -base64 24 | tr -d '/+=')/" .env
sed -i "s/N8N_PASSWORD=.*/N8N_PASSWORD=$(openssl rand -base64 16 | tr -d '/+=')/" .env
sed -i "s/N8N_ENCRYPTION_KEY=.*/N8N_ENCRYPTION_KEY=$(openssl rand -base64 32 | tr -d '/+=')/" .env
sed -i "s/FLOWISE_PASSWORD=.*/FLOWISE_PASSWORD=$(openssl rand -base64 16 | tr -d '/+=')/" .env
sed -i "s/GRAFANA_PASSWORD=.*/GRAFANA_PASSWORD=$(openssl rand -base64 16 | tr -d '/+=')/" .env
sed -i "s/API_SECRET_KEY=.*/API_SECRET_KEY=$(openssl rand -base64 32 | tr -d '/+=')/" .env

# Update domain
sed -i "s/VPS_DOMAIN=.*/VPS_DOMAIN=ziggie.cloud/" .env

# Secure the file
chmod 600 .env

# Backup credentials
cp .env .env.backup.$(date +%Y%m%d)
```

### Phase 4: Create Configuration Files

```bash
# Create directories
mkdir -p nginx/{conf.d,ssl,html}
mkdir -p prometheus/alerts
mkdir -p grafana/{provisioning,dashboards}
mkdir -p loki promtail
mkdir -p init-scripts/{postgres,mongo}

# Create Prometheus config
cat > prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  - job_name: 'ziggie-services'
    static_configs:
      - targets: ['ziggie-api:8000', 'mcp-gateway:8080', 'n8n:5678']
EOF

# Create Loki config
cat > loki/loki-config.yml << 'EOF'
auth_enabled: false
server:
  http_listen_port: 3100
ingester:
  lifecycler:
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
  chunk_idle_period: 5m
schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h
storage_config:
  boltdb_shipper:
    active_index_directory: /loki/boltdb-shipper-active
    cache_location: /loki/boltdb-shipper-cache
    shared_store: filesystem
  filesystem:
    directory: /loki/chunks
EOF
```

### Phase 5: Deploy Services

```bash
cd /opt/ziggie

# Pull all images (5-10 minutes)
docker compose pull

# Start databases
docker compose up -d postgres mongodb redis
echo "Waiting 30 seconds for databases..."
sleep 30

# Verify database health
docker exec ziggie-postgres pg_isready -U ziggie
docker exec ziggie-redis redis-cli ping

# Start remaining infrastructure
docker compose up -d

# Wait for stabilization
sleep 30

# Check status
docker compose ps
```

### Phase 6: SSL Setup

```bash
# Stop nginx temporarily
docker compose stop nginx

# Request certificates
docker run -it --rm \
    -v /opt/ziggie/certbot_certs:/etc/letsencrypt \
    -v /opt/ziggie/certbot_data:/var/www/certbot \
    -p 80:80 \
    certbot/certbot certonly \
    --standalone \
    --email admin@ziggie.cloud \
    --agree-tos \
    -d ziggie.cloud \
    -d api.ziggie.cloud \
    -d n8n.ziggie.cloud \
    -d grafana.ziggie.cloud \
    -d portainer.ziggie.cloud \
    -d flowise.ziggie.cloud \
    -d chat.ziggie.cloud \
    -d mcp.ziggie.cloud \
    -d sim.ziggie.cloud

# Switch to HTTPS nginx config
cp nginx/nginx-https.conf nginx/nginx.conf

# Restart nginx
docker compose up -d nginx
```

---

## 5. Health Verification

### 5.1 Quick Health Check

```bash
# Run health check script
/opt/ziggie/health-check.sh
```

### 5.2 Manual Verification

```bash
# Container status
docker compose ps

# Database health
docker exec ziggie-postgres pg_isready -U ziggie
docker exec ziggie-mongodb mongosh --quiet --eval 'db.runCommand("ping").ok'
docker exec ziggie-redis redis-cli ping

# Service endpoints
curl -sf http://localhost:5678/healthz && echo "n8n: OK"
curl -sf http://localhost:3000/api/health && echo "Grafana: OK"
curl -sf http://localhost:9090/-/healthy && echo "Prometheus: OK"
curl -sf http://localhost/health && echo "Nginx: OK"
curl -sf http://localhost:11434/api/tags && echo "Ollama: OK"

# Resource usage
docker stats --no-stream
```

### 5.3 Expected Health Status

| Service | Health Check | Expected Response |
|---------|--------------|-------------------|
| postgres | `pg_isready` | accepting connections |
| mongodb | `mongosh ping` | 1 |
| redis | `redis-cli ping` | PONG |
| n8n | HTTP /healthz | 200 |
| grafana | HTTP /api/health | 200 |
| prometheus | HTTP /-/healthy | 200 |
| nginx | HTTP /health | 200 |
| ollama | HTTP /api/tags | 200 |
| portainer | HTTP /api/system/status | 200 |

---

## 6. Post-Deployment Tasks

### 6.1 Initialize Portainer

1. Access: http://82.25.112.73:9000
2. Create admin user on first access
3. Select "Local" Docker environment
4. Enable auto-update for containers

### 6.2 Configure Grafana

1. Access: http://82.25.112.73:3000
2. Login: admin / (password from .env)
3. Add Data Source:
   - Type: Prometheus
   - URL: http://prometheus:9090
   - Save & Test
4. Add Loki Data Source:
   - Type: Loki
   - URL: http://loki:3100
   - Save & Test

### 6.3 Pull LLM Models

```bash
# Pull recommended models
docker exec -it ziggie-ollama ollama pull llama3.2:3b
docker exec -it ziggie-ollama ollama pull codellama:7b
docker exec -it ziggie-ollama ollama pull mistral:7b

# Verify models
docker exec ziggie-ollama ollama list
```

### 6.4 Configure n8n

1. Access: http://82.25.112.73:5678
2. Create admin account
3. Import workflows from /opt/ziggie/n8n-workflows/
4. Configure credentials for GitHub, Anthropic, OpenAI

### 6.5 Setup Backups

```bash
# Enable backup cron jobs
/opt/ziggie/backup/setup-cron.sh

# Verify cron
crontab -l
```

### 6.6 Firewall Configuration

```bash
# Allow required ports
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw allow 9000/tcp # Portainer (restrict by IP if possible)

# Optional: Restrict management ports to specific IPs
ufw allow from YOUR_IP to any port 9000
ufw allow from YOUR_IP to any port 5678

# Enable firewall
ufw enable
```

---

## 7. Troubleshooting

### 7.1 Common Issues

#### Container Won't Start

```bash
# Check logs
docker compose logs <service_name>

# Check events
docker events --filter 'type=container' --since 5m

# Force recreate
docker compose up -d --force-recreate <service_name>
```

#### Database Connection Failed

```bash
# Check database container
docker exec ziggie-postgres pg_isready -U ziggie

# Check connection from another container
docker exec ziggie-n8n ping postgres

# Verify network
docker network inspect ziggie-network
```

#### Out of Memory

```bash
# Check memory usage
docker stats --no-stream

# Find memory hogs
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}" | sort -k2 -h

# Restart heavy services
docker compose restart ollama
```

#### SSL Certificate Issues

```bash
# Check certificate status
docker run --rm -v /opt/ziggie/certbot_certs:/etc/letsencrypt:ro \
    certbot/certbot certificates

# Force renewal
docker run --rm -v /opt/ziggie/certbot_certs:/etc/letsencrypt \
    -v /opt/ziggie/certbot_data:/var/www/certbot \
    certbot/certbot renew --force-renewal
```

### 7.2 Service-Specific Troubleshooting

#### Ollama

```bash
# Check if model is loading
docker logs -f ziggie-ollama

# List available models
docker exec ziggie-ollama ollama list

# Test generation
docker exec ziggie-ollama ollama run llama3.2:3b "Hello"
```

#### n8n

```bash
# Check n8n logs
docker logs -f ziggie-n8n

# Reset n8n database (WARNING: deletes workflows)
docker compose down n8n
docker volume rm ziggie_n8n_data
docker compose up -d n8n
```

---

## 8. Rollback Procedures

### 8.1 Quick Rollback

```bash
# Stop all services
docker compose down

# Restore from backup
cd /opt/ziggie/backup
./restore-all.sh <backup_date>

# Restart services
docker compose up -d
```

### 8.2 Service-Level Rollback

```bash
# Stop specific service
docker compose stop <service>

# Restore service data
./backup/scripts/restore-<service>.sh <backup_date>

# Restart service
docker compose up -d <service>
```

### 8.3 Full Environment Rollback

```bash
# 1. Stop everything
docker compose down

# 2. Remove all volumes (WARNING: destroys all data)
docker volume prune -f

# 3. Restore from S3 backup
./backup/scripts/restore-from-s3.sh <backup_date>

# 4. Restart
docker compose up -d
```

---

## Quick Reference Commands

```bash
# Status
docker compose ps
docker compose logs -f <service>
docker stats --no-stream

# Control
docker compose up -d                    # Start all
docker compose down                     # Stop all
docker compose restart <service>        # Restart one
docker compose pull && docker compose up -d  # Update

# Maintenance
docker system prune -af                 # Clean unused
docker volume prune -f                  # Clean volumes
docker compose exec <service> sh        # Shell access

# Logs
docker compose logs --tail=100 <service>
docker compose logs -f --since 1h

# Health
/opt/ziggie/health-check.sh
curl -sf http://localhost/health
```

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-27 | Session A | Initial draft |
| 2.0.0 | 2025-12-28 | Session C | Complete rewrite with production script |

---

*Generated by L1 Strategic Agent - Session C*
*Target: Ziggie Command Center VPS Deployment*
