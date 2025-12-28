# Ziggie VPS Deployment - Comprehensive Production Checklist

> **Generated**: 2025-12-28
> **Target**: Hostinger KVM 4 VPS (4 vCPU, 16GB RAM, 200GB NVMe)
> **Stack**: 18-service Docker Compose deployment
> **Domain**: ziggie.cloud

---

## Executive Summary

This document provides a complete, step-by-step deployment procedure for the Ziggie Command Center on Hostinger KVM 4 VPS. The stack includes:

| Category | Services |
|----------|----------|
| **Databases** | PostgreSQL 15, MongoDB 7, Redis 7 |
| **Workflow Orchestration** | n8n, Flowise |
| **AI/LLM** | Ollama, Open WebUI |
| **Application** | Ziggie API, MCP Gateway, Sim Studio |
| **Monitoring** | Prometheus, Grafana, Loki, Promtail |
| **Management** | Portainer, Watchtower, Nginx, Certbot, GitHub Runner |

**Total Services**: 18 containers
**Estimated Deployment Time**: 30-45 minutes
**Monthly Cost**: ~$12-15 (Hostinger KVM 4)

---

## Table of Contents

1. [Pre-Deployment Verification Checklist](#1-pre-deployment-verification-checklist)
2. [VPS Initial Setup](#2-vps-initial-setup)
3. [Docker Installation](#3-docker-installation)
4. [Configuration Files Preparation](#4-configuration-files-preparation)
5. [Staged Service Deployment](#5-staged-service-deployment)
6. [SSL Certificate Setup](#6-ssl-certificate-setup)
7. [Post-Deployment Health Checks](#7-post-deployment-health-checks)
8. [Monitoring Setup](#8-monitoring-setup)
9. [Rollback Procedures](#9-rollback-procedures)
10. [Maintenance Procedures](#10-maintenance-procedures)
11. [Troubleshooting Guide](#11-troubleshooting-guide)

---

## 1. Pre-Deployment Verification Checklist

### 1.1 Hostinger Account & VPS

- [ ] Hostinger KVM 4 VPS provisioned (4 vCPU, 16GB RAM, 200GB NVMe)
- [ ] VPS IP address recorded: `_______________________`
- [ ] Ubuntu 22.04 LTS or 24.04 LTS selected as OS
- [ ] "Docker" application selected during VPS setup (or will install manually)
- [ ] SSH access confirmed from local machine

### 1.2 Domain & DNS

- [ ] Domain registered (e.g., ziggie.cloud)
- [ ] DNS A record pointing to VPS IP
- [ ] DNS propagation confirmed (use `dig ziggie.cloud` or online DNS checker)
- [ ] If using subdomains, wildcard or specific records created

### 1.3 Local Prerequisites

- [ ] SSH client available
- [ ] SSH key pair generated (`ssh-keygen -t ed25519 -C "ziggie-vps"`)
- [ ] Configuration files cloned from repository
- [ ] `.env` file prepared with all secrets (see Section 4.2)

### 1.4 Secrets & Credentials Ready

| Credential | Status | Notes |
|------------|--------|-------|
| PostgreSQL password | [ ] | 24+ chars, no special chars |
| MongoDB password | [ ] | 24+ chars, no special chars |
| Redis password | [ ] | 24+ chars, no special chars |
| n8n password | [ ] | Admin login |
| n8n encryption key | [ ] | 32+ chars for workflow encryption |
| Flowise password | [ ] | Admin login |
| Grafana password | [ ] | Admin login |
| API secret key | [ ] | 32+ chars |
| WebUI secret key | [ ] | 32+ chars |
| AWS Access Key | [ ] | For S3/Bedrock integration |
| AWS Secret Key | [ ] | For S3/Bedrock integration |
| GitHub Token | [ ] | For API access |
| GitHub OAuth credentials | [ ] | For n8n GitHub login |
| GitHub Runner token | [ ] | For self-hosted runner |
| OpenAI API Key | [ ] | Optional, for fallback |
| Anthropic API Key | [ ] | Optional, for fallback |
| Slack Webhook URL | [ ] | For notifications |

---

## 2. VPS Initial Setup

### 2.1 First SSH Connection

```bash
# Connect as root (initial setup)
ssh root@YOUR_VPS_IP

# Accept host key fingerprint
# Enter root password set during VPS provisioning
```

### 2.2 System Update

```bash
# Update package lists and upgrade all packages
apt update && apt upgrade -y

# Install essential tools
apt install -y \
    curl \
    wget \
    git \
    nano \
    htop \
    ncdu \
    ufw \
    fail2ban \
    unzip \
    ca-certificates \
    gnupg \
    lsb-release
```

### 2.3 Create Non-Root User

```bash
# Create ziggie user
adduser ziggie

# Add to sudo group
usermod -aG sudo ziggie

# Copy SSH keys to new user
mkdir -p /home/ziggie/.ssh
cp ~/.ssh/authorized_keys /home/ziggie/.ssh/
chown -R ziggie:ziggie /home/ziggie/.ssh
chmod 700 /home/ziggie/.ssh
chmod 600 /home/ziggie/.ssh/authorized_keys
```

### 2.4 SSH Hardening

```bash
# Edit SSH config
nano /etc/ssh/sshd_config

# Apply these changes:
# PermitRootLogin no
# PasswordAuthentication no
# PubkeyAuthentication yes
# MaxAuthTries 3
# LoginGraceTime 60

# Restart SSH
systemctl restart sshd
```

**IMPORTANT**: Open a NEW terminal and verify you can SSH as `ziggie` before closing root session!

```bash
# From your local machine (new terminal)
ssh ziggie@YOUR_VPS_IP

# Verify sudo access
sudo whoami
# Should output: root
```

### 2.5 Firewall Configuration

```bash
# Set default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow essential ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# Enable firewall
sudo ufw enable

# Verify status
sudo ufw status verbose
```

**Expected Output**:
```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW IN    Anywhere
80/tcp                     ALLOW IN    Anywhere
443/tcp                    ALLOW IN    Anywhere
22/tcp (v6)                ALLOW IN    Anywhere (v6)
80/tcp (v6)                ALLOW IN    Anywhere (v6)
443/tcp (v6)               ALLOW IN    Anywhere (v6)
```

### 2.6 Fail2ban Configuration

```bash
# Create local jail configuration
sudo nano /etc/fail2ban/jail.local

# Add content:
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

# Restart fail2ban
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban

# Verify status
sudo fail2ban-client status sshd
```

---

## 3. Docker Installation

### 3.1 Install Docker Engine

```bash
# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add ziggie to docker group
sudo usermod -aG docker ziggie

# Apply group changes (logout and login, or run):
newgrp docker
```

### 3.2 Verify Docker Installation

```bash
# Check Docker version
docker --version
# Expected: Docker version 24.x.x or 25.x.x

# Check Docker Compose version
docker compose version
# Expected: Docker Compose version v2.x.x

# Run test container
docker run --rm hello-world
# Should pull and run successfully
```

### 3.3 Configure Docker Daemon

```bash
# Create daemon configuration
sudo nano /etc/docker/daemon.json

# Add content:
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    },
    "default-ulimits": {
        "nofile": {
            "Name": "nofile",
            "Hard": 65536,
            "Soft": 65536
        }
    },
    "live-restore": true
}

# Restart Docker
sudo systemctl restart docker

# Verify daemon settings
docker info | grep -A5 "Logging Driver"
```

---

## 4. Configuration Files Preparation

### 4.1 Create Project Directory Structure

```bash
# Create main project directory
sudo mkdir -p /opt/ziggie
sudo chown -R ziggie:ziggie /opt/ziggie
cd /opt/ziggie

# Create subdirectories
mkdir -p \
    nginx/conf.d \
    nginx/ssl \
    prometheus/alerts \
    grafana/provisioning/datasources \
    grafana/provisioning/dashboards \
    grafana/dashboards \
    loki \
    promtail \
    mcp-gateway \
    api \
    sim-studio \
    init-scripts/postgres \
    init-scripts/mongo \
    n8n-workflows \
    backup
```

### 4.2 Create Environment File

```bash
# Create .env file
nano /opt/ziggie/.env
```

**Content** (fill in your actual values):

```bash
# =============================================================================
# ZIGGIE COMMAND CENTER - Environment Variables
# =============================================================================
# Generated: 2025-12-28
# WARNING: Never commit this file to git!
# =============================================================================

# VPS Configuration
VPS_DOMAIN=ziggie.cloud
VPS_IP=YOUR_ACTUAL_VPS_IP

# Database Passwords (generate with: openssl rand -base64 24 | tr -d '/+=')
POSTGRES_PASSWORD=YOUR_SECURE_POSTGRES_PASSWORD
MONGO_PASSWORD=YOUR_SECURE_MONGO_PASSWORD
REDIS_PASSWORD=YOUR_SECURE_REDIS_PASSWORD

# n8n Configuration
N8N_USER=admin
N8N_PASSWORD=YOUR_SECURE_N8N_PASSWORD
N8N_ENCRYPTION_KEY=YOUR_32_CHAR_ENCRYPTION_KEY

# Flowise Configuration
FLOWISE_USER=admin
FLOWISE_PASSWORD=YOUR_SECURE_FLOWISE_PASSWORD

# Open WebUI Configuration
WEBUI_SECRET_KEY=YOUR_SECURE_WEBUI_SECRET

# Grafana Configuration
GRAFANA_USER=admin
GRAFANA_PASSWORD=YOUR_SECURE_GRAFANA_PASSWORD

# Ziggie API Configuration
API_SECRET_KEY=YOUR_SECURE_API_SECRET

# AWS Credentials
AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_KEY
AWS_REGION=eu-north-1

# GitHub Integration
GITHUB_TOKEN=ghp_YOUR_GITHUB_PAT
GITHUB_CLIENT_ID=YOUR_GITHUB_OAUTH_CLIENT_ID
GITHUB_CLIENT_SECRET=YOUR_GITHUB_OAUTH_CLIENT_SECRET
GITHUB_REPO_URL=https://github.com/YOUR_USERNAME/YOUR_REPO
GITHUB_RUNNER_TOKEN=YOUR_RUNNER_REGISTRATION_TOKEN

# AI/LLM API Keys (Optional - for cloud fallback)
OPENAI_API_KEY=sk-YOUR_OPENAI_KEY
ANTHROPIC_API_KEY=sk-ant-YOUR_ANTHROPIC_KEY

# Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/[REDACTED]
```

**Secure the file**:

```bash
chmod 600 /opt/ziggie/.env
```

### 4.3 Upload Configuration Files

**Option A: SCP from local machine**

```bash
# From your local machine (where Ziggie repo is cloned)
scp -r C:\Ziggie\hostinger-vps\* ziggie@YOUR_VPS_IP:/opt/ziggie/
```

**Option B: Git clone (if in repository)**

```bash
cd /opt/ziggie
git clone https://github.com/YOUR_USERNAME/ziggie-vps-config.git .
```

**Option C: Create files manually on VPS**

Use the content from Section 4.4 - 4.7 below.

### 4.4 Nginx Configuration

Create `/opt/ziggie/nginx/nginx.conf`:

```bash
nano /opt/ziggie/nginx/nginx.conf
```

**Content**: Use the nginx.conf from `C:\Ziggie\hostinger-vps\nginx\nginx.conf` but update:
- Line 87: `server_name ziggie.cloud;`
- Line 90-91: Comment out SSL lines initially (until certbot runs)

**Initial HTTP-only config** (before SSL):

```nginx
events {
    worker_connections 1024;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript application/rss+xml application/atom+xml image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general:10m rate=30r/s;

    # Upstream definitions
    upstream n8n { server n8n:5678; }
    upstream ziggie_api { server ziggie-api:8000; }
    upstream mcp_gateway { server mcp-gateway:8080; }
    upstream portainer { server portainer:9000; }
    upstream flowise { server flowise:3000; }
    upstream open_webui { server open-webui:8080; }
    upstream grafana { server grafana:3000; }
    upstream sim_studio { server sim-studio:8001; }
    upstream ollama { server ollama:11434; }

    # HTTP server (initial - before SSL)
    server {
        listen 80;
        server_name ziggie.cloud;

        # Certbot challenge
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        # Health check
        location /health {
            return 200 'Ziggie Command Center OK';
            add_header Content-Type text/plain;
        }

        # All other traffic (temporary until SSL)
        location / {
            return 200 'Ziggie Command Center - SSL setup pending';
            add_header Content-Type text/plain;
        }
    }
}
```

### 4.5 Prometheus Configuration

Create `/opt/ziggie/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers: []

rule_files: []

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'ziggie-api'
    static_configs:
      - targets: ['ziggie-api:8000']
    metrics_path: /metrics
    scrape_timeout: 10s

  - job_name: 'n8n'
    static_configs:
      - targets: ['n8n:5678']

  - job_name: 'mcp-gateway'
    static_configs:
      - targets: ['mcp-gateway:8080']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'docker'
    static_configs:
      - targets: ['host.docker.internal:9323']
```

### 4.6 Loki Configuration

Create `/opt/ziggie/loki/loki-config.yml`:

```yaml
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
  chunk_retain_period: 30s

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

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
```

### 4.7 Promtail Configuration

Create `/opt/ziggie/promtail/promtail-config.yml`:

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: containers
    static_configs:
      - targets:
          - localhost
        labels:
          job: containerlogs
          __path__: /var/lib/docker/containers/*/*log
```

### 4.8 PostgreSQL Init Script

Create `/opt/ziggie/init-scripts/postgres/init-databases.sh`:

```bash
#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE n8n;
    CREATE DATABASE simstudio;
    GRANT ALL PRIVILEGES ON DATABASE n8n TO ziggie;
    GRANT ALL PRIVILEGES ON DATABASE simstudio TO ziggie;
EOSQL
```

Make it executable:

```bash
chmod +x /opt/ziggie/init-scripts/postgres/init-databases.sh
```

---

## 5. Staged Service Deployment

### 5.1 Deployment Strategy

**CRITICAL**: Deploy services in stages to ensure dependencies are healthy before dependent services start.

```
Stage 1: Databases (postgres, mongodb, redis)
    ↓ Wait 30 seconds for health checks
Stage 2: Core Services (n8n, ollama, flowise, open-webui)
    ↓ Wait 15 seconds
Stage 3: Application Services (mcp-gateway, ziggie-api, sim-studio)
    ↓ Wait 15 seconds
Stage 4: Monitoring (prometheus, grafana, loki, promtail)
    ↓ Wait 10 seconds
Stage 5: Management & Proxy (portainer, watchtower, nginx, certbot, github-runner)
```

### 5.2 Stage 1: Database Services

```bash
cd /opt/ziggie

# Start databases only
docker compose up -d postgres mongodb redis

# Wait for health checks
echo "Waiting for databases to become healthy..."
sleep 30

# Verify all databases are healthy
docker compose ps postgres mongodb redis
```

**Expected Output**:
```
NAME              IMAGE                  STATUS                   PORTS
ziggie-postgres   postgres:15-alpine     Up About a minute (healthy)   0.0.0.0:5432->5432/tcp
ziggie-mongodb    mongo:7                Up About a minute (healthy)   0.0.0.0:27017->27017/tcp
ziggie-redis      redis:7-alpine         Up About a minute (healthy)   0.0.0.0:6379->6379/tcp
```

**Verify database connections**:

```bash
# Test PostgreSQL
docker exec -it ziggie-postgres pg_isready -U ziggie
# Expected: /var/run/postgresql:5432 - accepting connections

# Test MongoDB
docker exec -it ziggie-mongodb mongosh --quiet --eval 'db.runCommand("ping")'
# Expected: { ok: 1 }

# Test Redis
docker exec -it ziggie-redis redis-cli -a "$REDIS_PASSWORD" ping
# Expected: PONG
```

### 5.3 Stage 2: Core Services

```bash
# Start core services
docker compose up -d n8n ollama flowise open-webui

# Wait for services
echo "Waiting for core services..."
sleep 15

# Verify
docker compose ps n8n ollama flowise open-webui
```

**Expected Output**:
```
NAME                IMAGE                              STATUS          PORTS
ziggie-n8n          n8nio/n8n:latest                   Up 30 seconds   0.0.0.0:5678->5678/tcp
ziggie-ollama       ollama/ollama:latest               Up 30 seconds   0.0.0.0:11434->11434/tcp
ziggie-flowise      flowiseai/flowise:latest           Up 30 seconds   0.0.0.0:3001->3000/tcp
ziggie-open-webui   ghcr.io/open-webui/open-webui:main Up 30 seconds   0.0.0.0:3002->8080/tcp
```

### 5.4 Stage 3: Application Services

**Note**: These services require Dockerfiles. For initial deployment, you may need to build or skip these.

```bash
# If Dockerfiles exist:
docker compose up -d mcp-gateway ziggie-api sim-studio

# If Dockerfiles don't exist yet, skip this stage
# The services will fail to start without proper Dockerfile and code
```

### 5.5 Stage 4: Monitoring Services

```bash
# Start monitoring stack
docker compose up -d prometheus grafana loki promtail

# Wait for services
sleep 10

# Verify
docker compose ps prometheus grafana loki promtail
```

### 5.6 Stage 5: Management & Proxy

```bash
# Start remaining services
docker compose up -d portainer watchtower nginx certbot

# Note: github-runner requires valid token
# docker compose up -d github-runner

# Verify
docker compose ps
```

### 5.7 Full Stack Verification

```bash
# Check all container status
docker compose ps

# Check for any unhealthy containers
docker ps --filter "health=unhealthy"

# Check resource usage
docker stats --no-stream

# Check logs for errors
docker compose logs --tail=50 | grep -i error
```

---

## 6. SSL Certificate Setup

### 6.1 Verify DNS Resolution

```bash
# Verify DNS is pointing to VPS
dig +short ziggie.cloud
# Should return your VPS IP

# Verify from multiple locations
curl -s "https://dns.google/resolve?name=ziggie.cloud" | jq '.Answer[].data'
```

### 6.2 Obtain SSL Certificate

```bash
# Stop nginx temporarily (certbot needs port 80)
docker compose stop nginx

# Run certbot
docker run -it --rm \
    -v /opt/ziggie/certbot_certs:/etc/letsencrypt \
    -v /opt/ziggie/certbot_data:/var/www/certbot \
    -p 80:80 \
    certbot/certbot certonly \
    --standalone \
    --email your-email@domain.com \
    --agree-tos \
    --no-eff-email \
    -d ziggie.cloud

# Verify certificate exists
ls -la /opt/ziggie/certbot_certs/live/ziggie.cloud/
```

### 6.3 Update Nginx for HTTPS

Replace `/opt/ziggie/nginx/nginx.conf` with the full HTTPS configuration from `C:\Ziggie\hostinger-vps\nginx\nginx.conf`.

**Key changes**:
- Update `server_name` to `ziggie.cloud`
- Ensure SSL paths point to `/etc/letsencrypt/live/ziggie.cloud/`

```bash
# Restart nginx with SSL
docker compose up -d nginx

# Verify HTTPS
curl -I https://ziggie.cloud/health
# Should return HTTP/2 200
```

### 6.4 Configure Auto-Renewal

The certbot container in docker-compose.yml already handles renewal. Verify it's running:

```bash
docker compose ps certbot
```

---

## 7. Post-Deployment Health Checks

### 7.1 Service Health Check Commands

Run these commands after deployment to verify all services:

```bash
#!/bin/bash
# Save as /opt/ziggie/health-check.sh

echo "=== Ziggie Command Center Health Check ==="
echo ""

# Container status
echo "1. Container Status:"
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Health}}"
echo ""

# Database health
echo "2. Database Health:"
echo -n "   PostgreSQL: "
docker exec ziggie-postgres pg_isready -U ziggie > /dev/null && echo "OK" || echo "FAILED"

echo -n "   MongoDB: "
docker exec ziggie-mongodb mongosh --quiet --eval 'db.runCommand("ping").ok' 2>/dev/null && echo "OK" || echo "FAILED"

echo -n "   Redis: "
docker exec ziggie-redis redis-cli -a "$REDIS_PASSWORD" ping 2>/dev/null | grep -q PONG && echo "OK" || echo "FAILED"
echo ""

# Service endpoints
echo "3. Service Endpoints:"
echo -n "   Nginx (HTTP): "
curl -s -o /dev/null -w "%{http_code}" http://localhost/health && echo " OK"

echo -n "   n8n: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:5678/healthz && echo " OK"

echo -n "   Ollama: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:11434/api/tags && echo " OK"

echo -n "   Flowise: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:3001 && echo " OK"

echo -n "   Open WebUI: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:3002 && echo " OK"

echo -n "   Grafana: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health && echo " OK"

echo -n "   Prometheus: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:9090/-/healthy && echo " OK"

echo -n "   Portainer: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/api/system/status && echo " OK"
echo ""

# Resource usage
echo "4. Resource Usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
echo ""

# Disk usage
echo "5. Disk Usage:"
df -h / | tail -1 | awk '{print "   Root: " $5 " used (" $3 " of " $2 ")"}'
docker system df
echo ""

echo "=== Health Check Complete ==="
```

Make executable and run:

```bash
chmod +x /opt/ziggie/health-check.sh
/opt/ziggie/health-check.sh
```

### 7.2 Expected Health Check Results

| Service | Endpoint | Expected Response |
|---------|----------|-------------------|
| Nginx | http://localhost/health | 200 |
| n8n | http://localhost:5678/healthz | 200 |
| Ollama | http://localhost:11434/api/tags | 200 + JSON |
| Flowise | http://localhost:3001 | 200 |
| Open WebUI | http://localhost:3002 | 200 |
| Grafana | http://localhost:3000/api/health | 200 |
| Prometheus | http://localhost:9090/-/healthy | 200 |
| Portainer | http://localhost:9000/api/system/status | 200 |
| PostgreSQL | pg_isready | accepting connections |
| MongoDB | db.ping() | { ok: 1 } |
| Redis | PING | PONG |

### 7.3 External Access Verification

After SSL is configured, verify from your local machine:

```bash
# Health endpoint
curl -s https://ziggie.cloud/health

# n8n (should redirect to login)
curl -I https://ziggie.cloud/n8n/

# Grafana
curl -I https://ziggie.cloud/grafana/

# API
curl -s https://ziggie.cloud/api/health
```

---

## 8. Monitoring Setup

### 8.1 Access Grafana

1. Navigate to `https://ziggie.cloud/grafana/`
2. Login with `admin` / `GRAFANA_PASSWORD` from .env
3. Change password on first login

### 8.2 Add Data Sources

**Prometheus**:
1. Go to Configuration > Data Sources > Add data source
2. Select Prometheus
3. URL: `http://prometheus:9090`
4. Click "Save & Test"

**Loki**:
1. Go to Configuration > Data Sources > Add data source
2. Select Loki
3. URL: `http://loki:3100`
4. Click "Save & Test"

### 8.3 Import Dashboards

Create `/opt/ziggie/grafana/dashboards/ziggie-overview.json`:

```json
{
  "dashboard": {
    "title": "Ziggie Command Center Overview",
    "panels": [
      {
        "title": "Container Status",
        "type": "stat",
        "gridPos": { "h": 4, "w": 6, "x": 0, "y": 0 },
        "targets": [
          {
            "expr": "count(container_last_seen)",
            "legendFormat": "Running Containers"
          }
        ]
      },
      {
        "title": "CPU Usage",
        "type": "gauge",
        "gridPos": { "h": 4, "w": 6, "x": 6, "y": 0 },
        "targets": [
          {
            "expr": "100 - (avg(rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "gauge",
        "gridPos": { "h": 4, "w": 6, "x": 12, "y": 0 },
        "targets": [
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100"
          }
        ]
      }
    ]
  }
}
```

### 8.4 Set Up Alerts

Configure Grafana alerting for:
- Container down (no metrics for 5 minutes)
- High CPU (>80% for 10 minutes)
- High Memory (>90% for 5 minutes)
- Disk space low (<10% free)
- Service 5xx errors (>10 in 5 minutes)

---

## 9. Rollback Procedures

### 9.1 Quick Service Restart

```bash
# Restart single service
docker compose restart <service-name>

# Restart all services
docker compose restart

# Full stack restart (preserves data)
docker compose down
docker compose up -d
```

### 9.2 Rollback to Previous Image

```bash
# List available images
docker images

# Stop service
docker compose stop <service-name>

# Remove current container
docker compose rm -f <service-name>

# Pull specific version
docker pull <image>:<previous-tag>

# Update docker-compose.yml with specific tag
# Then restart
docker compose up -d <service-name>
```

### 9.3 Full Stack Rollback

```bash
# Stop all services
docker compose down

# Remove all containers (data preserved in volumes)
docker container prune -f

# Remove unused images
docker image prune -f

# Restart fresh
docker compose up -d
```

### 9.4 Database Rollback

**PostgreSQL**:

```bash
# Stop PostgreSQL
docker compose stop postgres

# Remove volume (CAUTION: data loss!)
docker volume rm ziggie_postgres_data

# Restart (fresh database)
docker compose up -d postgres
```

**Restore from backup**:

```bash
# If you have a backup
docker exec -i ziggie-postgres psql -U ziggie < backup.sql
```

### 9.5 Nuclear Option: Complete Reset

```bash
# WARNING: This deletes ALL data!

# Stop everything
docker compose down

# Remove all volumes
docker volume rm $(docker volume ls -q | grep ziggie)

# Remove all containers
docker container prune -f

# Remove all images
docker image prune -af

# Fresh start
docker compose up -d
```

---

## 10. Maintenance Procedures

### 10.1 Daily Checks

```bash
# Quick health check
docker compose ps
docker stats --no-stream

# Check disk usage
df -h /
docker system df
```

### 10.2 Weekly Maintenance

```bash
# Update container images
docker compose pull

# Restart with new images
docker compose up -d

# Clean up unused resources
docker system prune -f
docker volume prune -f
```

### 10.3 Backup Procedure

```bash
#!/bin/bash
# Save as /opt/ziggie/backup.sh

BACKUP_DIR="/opt/ziggie/backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "Starting backup to $BACKUP_DIR..."

# PostgreSQL
docker exec ziggie-postgres pg_dumpall -U ziggie > $BACKUP_DIR/postgres_all.sql
echo "PostgreSQL backed up"

# MongoDB
docker exec ziggie-mongodb mongodump --out /data/backup
docker cp ziggie-mongodb:/data/backup $BACKUP_DIR/mongodb
echo "MongoDB backed up"

# n8n data
docker cp ziggie-n8n:/home/node/.n8n $BACKUP_DIR/n8n
echo "n8n backed up"

# Environment file
cp /opt/ziggie/.env $BACKUP_DIR/.env

# Compress
tar -czf $BACKUP_DIR.tar.gz -C /opt/ziggie/backup $(basename $BACKUP_DIR)
rm -rf $BACKUP_DIR

echo "Backup complete: $BACKUP_DIR.tar.gz"

# Upload to S3 (optional)
# aws s3 cp $BACKUP_DIR.tar.gz s3://ziggie-backups-eu/$(basename $BACKUP_DIR.tar.gz)
```

### 10.4 Log Rotation

Docker logs are automatically rotated based on daemon.json configuration (10MB, 3 files).

Check log sizes:

```bash
# Find largest log files
find /var/lib/docker/containers -name "*-json.log" -exec du -h {} \; | sort -rh | head -10
```

---

## 11. Troubleshooting Guide

### 11.1 Container Won't Start

```bash
# Check logs
docker compose logs <service-name> --tail=100

# Check container details
docker inspect <container-name>

# Check if port is in use
sudo lsof -i :<port>
sudo netstat -tlnp | grep <port>
```

### 11.2 Database Connection Issues

```bash
# Test PostgreSQL connection
docker exec -it ziggie-postgres psql -U ziggie -c "SELECT 1"

# Test MongoDB connection
docker exec -it ziggie-mongodb mongosh --eval "db.adminCommand('ping')"

# Test Redis connection
docker exec -it ziggie-redis redis-cli -a "$REDIS_PASSWORD" ping

# Check container network
docker network inspect ziggie-network
```

### 11.3 Nginx 502 Bad Gateway

```bash
# Check if upstream service is running
docker compose ps

# Check nginx error logs
docker compose logs nginx --tail=50

# Verify upstream DNS resolution
docker exec ziggie-nginx nslookup <service-name>

# Test upstream directly
docker exec ziggie-nginx curl -s http://<service-name>:<port>/health
```

### 11.4 Out of Memory

```bash
# Check memory usage
free -h
docker stats --no-stream

# Identify memory hogs
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}" | sort -k2 -h

# Add swap (if needed)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 11.5 Out of Disk Space

```bash
# Check disk usage
df -h /
docker system df

# Clean Docker resources
docker system prune -af
docker volume prune -f

# Find large files
sudo ncdu /
```

### 11.6 SSL Certificate Issues

```bash
# Check certificate expiry
openssl s_client -connect ziggie.cloud:443 2>/dev/null | openssl x509 -noout -dates

# Force certificate renewal
docker run --rm \
    -v /opt/ziggie/certbot_certs:/etc/letsencrypt \
    certbot/certbot renew --force-renewal

# Restart nginx
docker compose restart nginx
```

### 11.7 Service Logs Location

| Service | Log Command |
|---------|-------------|
| All | `docker compose logs --tail=100` |
| Nginx | `docker compose logs nginx` |
| n8n | `docker compose logs n8n` |
| PostgreSQL | `docker compose logs postgres` |
| Application | `docker compose logs ziggie-api` |

---

## Quick Reference Commands

### Start/Stop

```bash
# Start all
docker compose up -d

# Stop all (preserves data)
docker compose down

# Restart specific service
docker compose restart <service>

# View running containers
docker compose ps
```

### Logs

```bash
# All logs
docker compose logs -f

# Specific service
docker compose logs -f <service>

# Last 100 lines
docker compose logs --tail=100
```

### Updates

```bash
# Pull latest images
docker compose pull

# Update and restart
docker compose pull && docker compose up -d

# Update specific service
docker compose pull <service> && docker compose up -d <service>
```

### Debugging

```bash
# Shell into container
docker exec -it <container-name> /bin/sh

# View container details
docker inspect <container-name>

# View network details
docker network inspect ziggie-network
```

---

## Service URLs After Deployment

| Service | URL | Credentials |
|---------|-----|-------------|
| n8n | https://ziggie.cloud/n8n/ | admin / N8N_PASSWORD |
| Flowise | https://ziggie.cloud/flowise/ | admin / FLOWISE_PASSWORD |
| Open WebUI | https://ziggie.cloud/chat/ | First user becomes admin |
| Grafana | https://ziggie.cloud/grafana/ | admin / GRAFANA_PASSWORD |
| Portainer | https://ziggie.cloud:9443 | Set on first access |
| Ziggie API | https://ziggie.cloud/api/ | API key |
| MCP Gateway | https://ziggie.cloud/mcp/ | API key |
| Prometheus | https://ziggie.cloud:9090 | No auth (internal only) |

---

## Files Reference

| File | Location | Purpose |
|------|----------|---------|
| docker-compose.yml | /opt/ziggie/ | Main stack definition |
| .env | /opt/ziggie/ | Environment secrets |
| nginx.conf | /opt/ziggie/nginx/ | Reverse proxy config |
| prometheus.yml | /opt/ziggie/prometheus/ | Metrics scraping config |
| loki-config.yml | /opt/ziggie/loki/ | Log aggregation config |
| promtail-config.yml | /opt/ziggie/promtail/ | Log collection config |
| health-check.sh | /opt/ziggie/ | Health verification script |
| backup.sh | /opt/ziggie/ | Backup script |

---

*Generated by L1 VPS Deployment Research Agent*
*Version: 1.0*
*Date: 2025-12-28*
