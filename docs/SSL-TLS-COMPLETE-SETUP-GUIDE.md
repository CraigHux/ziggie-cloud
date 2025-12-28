# Ziggie Cloud SSL/TLS Complete Setup Guide

> **Domain**: ziggie.cloud
> **VPS Provider**: Hostinger KVM 4
> **Stack**: Docker + Nginx + Certbot
> **Last Updated**: 2025-12-28

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Prerequisites Checklist](#prerequisites-checklist)
3. [DNS Configuration at Hostinger](#dns-configuration-at-hostinger)
4. [Step-by-Step SSL Setup Procedure](#step-by-step-ssl-setup-procedure)
5. [Nginx HTTPS Configuration Template](#nginx-https-configuration-template)
6. [Auto-Renewal Setup](#auto-renewal-setup)
7. [Certificate Monitoring and Alerts](#certificate-monitoring-and-alerts)
8. [Subdomain Strategy](#subdomain-strategy)
9. [Troubleshooting Guide](#troubleshooting-guide)
10. [Quick Reference Commands](#quick-reference-commands)

---

## Executive Summary

This guide provides production-ready SSL/TLS configuration for the Ziggie ecosystem using:

- **Let's Encrypt**: Free, automated SSL certificates
- **Certbot**: ACME client for certificate management
- **Nginx**: Reverse proxy with TLS termination
- **Docker**: Containerized deployment

**Architecture Overview**:
```
Internet → Nginx (443/SSL) → Docker Internal Network → Services
                ↓
         Certbot (auto-renewal every 12h)
```

---

## Prerequisites Checklist

Before starting, verify the following:

| Requirement | Command to Verify | Expected Result |
|-------------|-------------------|-----------------|
| VPS Running | `ssh root@your-vps-ip` | Connected |
| Docker Installed | `docker --version` | Docker version 24+ |
| Docker Compose | `docker compose version` | Docker Compose v2+ |
| Domain DNS | `dig ziggie.cloud +short` | Your VPS IP address |
| Port 80 Open | `curl -I http://ziggie.cloud` | HTTP response |
| Port 443 Open | `nc -zv ziggie.cloud 443` | Connection succeeded |

---

## DNS Configuration at Hostinger

### Step 1: Access Hostinger DNS Zone Editor

1. Log in to [hpanel.hostinger.com](https://hpanel.hostinger.com)
2. Navigate to **Domains** > **ziggie.cloud** > **DNS / Nameservers**
3. Click on **DNS Records**

### Step 2: Configure DNS Records

Add the following DNS records for your VPS IP address (replace `YOUR_VPS_IP`):

#### A Records (Required)

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | YOUR_VPS_IP | 3600 |
| A | api | YOUR_VPS_IP | 3600 |
| A | n8n | YOUR_VPS_IP | 3600 |
| A | grafana | YOUR_VPS_IP | 3600 |
| A | portainer | YOUR_VPS_IP | 3600 |
| A | flowise | YOUR_VPS_IP | 3600 |
| A | chat | YOUR_VPS_IP | 3600 |
| A | mcp | YOUR_VPS_IP | 3600 |
| A | sim | YOUR_VPS_IP | 3600 |

#### Wildcard Record (Optional - For Future Subdomains)

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | * | YOUR_VPS_IP | 3600 |

#### CAA Records (Recommended for Security)

| Type | Name | Value | TTL |
|------|------|-------|-----|
| CAA | @ | 0 issue "letsencrypt.org" | 3600 |
| CAA | @ | 0 issuewild "letsencrypt.org" | 3600 |

### Step 3: Verify DNS Propagation

Wait 5-15 minutes, then verify:

```bash
# Check main domain
dig ziggie.cloud +short

# Check subdomains
dig api.ziggie.cloud +short
dig grafana.ziggie.cloud +short

# Check CAA record
dig ziggie.cloud CAA +short
```

---

## Step-by-Step SSL Setup Procedure

### Phase 1: Prepare the VPS Environment

SSH into your VPS and run these commands:

```bash
# Connect to VPS
ssh root@YOUR_VPS_IP

# Navigate to Ziggie directory
cd /opt/ziggie

# Ensure nginx directories exist
mkdir -p nginx/conf.d nginx/ssl
mkdir -p certbot/conf certbot/www

# Set proper permissions
chmod 755 certbot certbot/conf certbot/www
```

### Phase 2: Create Initial HTTP-Only Nginx Config

Create a temporary HTTP-only configuration for initial certificate request:

```bash
cat > /opt/ziggie/nginx/nginx-initial.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name ziggie.cloud *.ziggie.cloud;

        # ACME Challenge Location (CRITICAL for Certbot)
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
            allow all;
        }

        # Temporary response for testing
        location / {
            return 200 'Ziggie Cloud - Awaiting SSL Configuration';
            add_header Content-Type text/plain;
        }
    }
}
EOF
```

### Phase 3: Start Nginx with HTTP-Only Config

```bash
# Stop any running nginx container
docker stop ziggie-nginx 2>/dev/null || true
docker rm ziggie-nginx 2>/dev/null || true

# Start nginx with initial config
docker run -d \
  --name ziggie-nginx-init \
  --network ziggie-network \
  -p 80:80 \
  -v /opt/ziggie/nginx/nginx-initial.conf:/etc/nginx/nginx.conf:ro \
  -v /opt/ziggie/certbot/www:/var/www/certbot:rw \
  nginx:alpine

# Verify it's running
curl -I http://ziggie.cloud
```

### Phase 4: Request SSL Certificates

#### Option A: Individual Certificates (Recommended for Production)

Request certificates for each subdomain explicitly:

```bash
# Request main domain + all subdomains
docker run --rm -it \
  -v /opt/ziggie/certbot/conf:/etc/letsencrypt \
  -v /opt/ziggie/certbot/www:/var/www/certbot \
  certbot/certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email admin@ziggie.cloud \
    --agree-tos \
    --no-eff-email \
    -d ziggie.cloud \
    -d api.ziggie.cloud \
    -d n8n.ziggie.cloud \
    -d grafana.ziggie.cloud \
    -d portainer.ziggie.cloud \
    -d flowise.ziggie.cloud \
    -d chat.ziggie.cloud \
    -d mcp.ziggie.cloud \
    -d sim.ziggie.cloud
```

#### Option B: Wildcard Certificate (Requires DNS Challenge)

For wildcard certificates, you need DNS-01 challenge:

```bash
# Install Hostinger DNS plugin for Certbot (if available)
# Note: Hostinger doesn't have an official Certbot plugin
# Use manual DNS challenge instead:

docker run --rm -it \
  -v /opt/ziggie/certbot/conf:/etc/letsencrypt \
  certbot/certbot certonly \
    --manual \
    --preferred-challenges=dns \
    --email admin@ziggie.cloud \
    --agree-tos \
    --no-eff-email \
    -d "ziggie.cloud" \
    -d "*.ziggie.cloud"

# When prompted, add TXT record at Hostinger:
# Type: TXT
# Name: _acme-challenge
# Value: [provided by certbot]
# Wait 2-5 minutes after adding, then press Enter
```

### Phase 5: Verify Certificates

```bash
# Check certificate files exist
ls -la /opt/ziggie/certbot/conf/live/ziggie.cloud/

# Expected files:
# - cert.pem (server certificate)
# - chain.pem (intermediate certificates)
# - fullchain.pem (cert + chain)
# - privkey.pem (private key)

# Check certificate details
docker run --rm \
  -v /opt/ziggie/certbot/conf:/etc/letsencrypt:ro \
  certbot/certbot certificates
```

### Phase 6: Stop Initial Nginx

```bash
docker stop ziggie-nginx-init
docker rm ziggie-nginx-init
```

### Phase 7: Start Full Stack with HTTPS

```bash
cd /opt/ziggie
docker compose up -d
```

---

## Nginx HTTPS Configuration Template

Replace the contents of `/opt/ziggie/nginx/nginx.conf` with this production-ready configuration:

```nginx
events {
    worker_connections 1024;
}

http {
    # ==========================================================================
    # BASIC SETTINGS
    # ==========================================================================
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript
               application/rss+xml application/atom+xml image/svg+xml;

    # ==========================================================================
    # RATE LIMITING
    # ==========================================================================
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general:10m rate=30r/s;
    limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

    # ==========================================================================
    # SSL SESSION SETTINGS (Shared across all servers)
    # ==========================================================================
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    # ==========================================================================
    # UPSTREAM DEFINITIONS
    # ==========================================================================
    upstream n8n {
        server n8n:5678;
    }

    upstream ziggie_api {
        server ziggie-api:8000;
    }

    upstream mcp_gateway {
        server mcp-gateway:8080;
    }

    upstream portainer {
        server portainer:9000;
    }

    upstream flowise {
        server flowise:3000;
    }

    upstream open_webui {
        server open-webui:8080;
    }

    upstream grafana {
        server grafana:3000;
    }

    upstream sim_studio {
        server sim-studio:8001;
    }

    upstream ollama {
        server ollama:11434;
    }

    # ==========================================================================
    # HTTP TO HTTPS REDIRECT
    # ==========================================================================
    server {
        listen 80;
        listen [::]:80;
        server_name ziggie.cloud *.ziggie.cloud;

        # ACME Challenge (Must remain for renewals)
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
            allow all;
        }

        # Redirect all other HTTP traffic to HTTPS
        location / {
            return 301 https://$host$request_uri;
        }
    }

    # ==========================================================================
    # MAIN DOMAIN - ziggie.cloud
    # ==========================================================================
    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name ziggie.cloud;

        # SSL Certificates
        ssl_certificate /etc/letsencrypt/live/ziggie.cloud/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/ziggie.cloud/privkey.pem;

        # Modern SSL Configuration (TLS 1.2 and 1.3 only)
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # OCSP Stapling
        ssl_stapling on;
        ssl_stapling_verify on;
        resolver 8.8.8.8 8.8.4.4 valid=300s;
        resolver_timeout 5s;

        # Security Headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

        # Root - Landing Page
        location / {
            root /usr/share/nginx/html;
            index index.html;
        }

        # Health Check
        location /health {
            return 200 'Ziggie Command Center OK';
            add_header Content-Type text/plain;
        }
    }

    # ==========================================================================
    # API SUBDOMAIN - api.ziggie.cloud
    # ==========================================================================
    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name api.ziggie.cloud;

        ssl_certificate /etc/letsencrypt/live/ziggie.cloud/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/ziggie.cloud/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Content-Type-Options "nosniff" always;

        location / {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://ziggie_api;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
    }

    # ==========================================================================
    # N8N SUBDOMAIN - n8n.ziggie.cloud
    # ==========================================================================
    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name n8n.ziggie.cloud;

        ssl_certificate /etc/letsencrypt/live/ziggie.cloud/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/ziggie.cloud/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        location / {
            proxy_pass http://n8n;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_buffering off;
            proxy_read_timeout 86400;
        }

        # n8n Webhooks
        location /webhook/ {
            proxy_pass http://n8n/webhook/;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # ==========================================================================
    # GRAFANA SUBDOMAIN - grafana.ziggie.cloud
    # ==========================================================================
    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name grafana.ziggie.cloud;

        ssl_certificate /etc/letsencrypt/live/ziggie.cloud/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/ziggie.cloud/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        location / {
            proxy_pass http://grafana;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # ==========================================================================
    # PORTAINER SUBDOMAIN - portainer.ziggie.cloud
    # ==========================================================================
    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name portainer.ziggie.cloud;

        ssl_certificate /etc/letsencrypt/live/ziggie.cloud/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/ziggie.cloud/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        location / {
            proxy_pass http://portainer;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # ==========================================================================
    # FLOWISE SUBDOMAIN - flowise.ziggie.cloud
    # ==========================================================================
    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name flowise.ziggie.cloud;

        ssl_certificate /etc/letsencrypt/live/ziggie.cloud/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/ziggie.cloud/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        location / {
            proxy_pass http://flowise;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # ==========================================================================
    # CHAT (Open WebUI) SUBDOMAIN - chat.ziggie.cloud
    # ==========================================================================
    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name chat.ziggie.cloud;

        ssl_certificate /etc/letsencrypt/live/ziggie.cloud/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/ziggie.cloud/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        location / {
            proxy_pass http://open_webui;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # ==========================================================================
    # MCP GATEWAY SUBDOMAIN - mcp.ziggie.cloud
    # ==========================================================================
    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name mcp.ziggie.cloud;

        ssl_certificate /etc/letsencrypt/live/ziggie.cloud/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/ziggie.cloud/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        location / {
            proxy_pass http://mcp_gateway;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 86400;
        }
    }

    # ==========================================================================
    # SIM STUDIO SUBDOMAIN - sim.ziggie.cloud
    # ==========================================================================
    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name sim.ziggie.cloud;

        ssl_certificate /etc/letsencrypt/live/ziggie.cloud/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/ziggie.cloud/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        location / {
            proxy_pass http://sim_studio;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

---

## Auto-Renewal Setup

### Method 1: Docker-Based Renewal (Recommended)

The Docker Compose file already includes a certbot container with auto-renewal. Verify it's configured:

```yaml
# In docker-compose.yml
certbot:
  image: certbot/certbot:latest
  container_name: ziggie-certbot
  volumes:
    - certbot_data:/var/www/certbot
    - certbot_certs:/etc/letsencrypt
  entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
```

### Method 2: Cron-Based Renewal (Alternative)

Create a renewal script on the VPS host:

```bash
# Create renewal script
cat > /opt/ziggie/scripts/renew-ssl.sh << 'EOF'
#!/bin/bash
# =============================================================================
# SSL Certificate Renewal Script
# Runs via cron every 12 hours
# =============================================================================

set -e

LOG_FILE="/var/log/ziggie-ssl-renewal.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] Starting SSL renewal check..." >> "$LOG_FILE"

# Run certbot renew
docker run --rm \
  -v /opt/ziggie/certbot/conf:/etc/letsencrypt \
  -v /opt/ziggie/certbot/www:/var/www/certbot \
  certbot/certbot renew --quiet >> "$LOG_FILE" 2>&1

RENEW_STATUS=$?

if [ $RENEW_STATUS -eq 0 ]; then
    echo "[$TIMESTAMP] Renewal check completed successfully" >> "$LOG_FILE"

    # Reload nginx to pick up new certificates
    docker exec ziggie-nginx nginx -s reload >> "$LOG_FILE" 2>&1

    if [ $? -eq 0 ]; then
        echo "[$TIMESTAMP] Nginx reloaded successfully" >> "$LOG_FILE"
    else
        echo "[$TIMESTAMP] ERROR: Failed to reload Nginx" >> "$LOG_FILE"
    fi
else
    echo "[$TIMESTAMP] ERROR: Renewal check failed with status $RENEW_STATUS" >> "$LOG_FILE"
fi
EOF

chmod +x /opt/ziggie/scripts/renew-ssl.sh
```

### Set Up Cron Job

```bash
# Edit crontab
crontab -e

# Add these lines (renewal at 3 AM and 3 PM daily)
0 3,15 * * * /opt/ziggie/scripts/renew-ssl.sh >> /var/log/ziggie-ssl-renewal.log 2>&1
```

### Post-Renewal Nginx Reload

Create a deploy hook for automatic nginx reload:

```bash
mkdir -p /opt/ziggie/certbot/conf/renewal-hooks/deploy

cat > /opt/ziggie/certbot/conf/renewal-hooks/deploy/reload-nginx.sh << 'EOF'
#!/bin/bash
# Reload nginx after successful renewal
docker exec ziggie-nginx nginx -s reload
EOF

chmod +x /opt/ziggie/certbot/conf/renewal-hooks/deploy/reload-nginx.sh
```

---

## Certificate Monitoring and Alerts

### Prometheus Alert Rules

Create `/opt/ziggie/prometheus/alerts/ssl-alerts.yml`:

```yaml
groups:
  - name: ssl-certificate-alerts
    rules:
      # Alert 30 days before expiry
      - alert: SSLCertificateExpiringSoon
        expr: probe_ssl_earliest_cert_expiry - time() < 86400 * 30
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "SSL certificate expiring soon"
          description: "SSL certificate for {{ $labels.instance }} expires in less than 30 days"

      # Alert 7 days before expiry (critical)
      - alert: SSLCertificateExpiringCritical
        expr: probe_ssl_earliest_cert_expiry - time() < 86400 * 7
        for: 1h
        labels:
          severity: critical
        annotations:
          summary: "SSL certificate expiring CRITICAL"
          description: "SSL certificate for {{ $labels.instance }} expires in less than 7 days!"

      # Alert if certificate already expired
      - alert: SSLCertificateExpired
        expr: probe_ssl_earliest_cert_expiry - time() <= 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "SSL certificate EXPIRED"
          description: "SSL certificate for {{ $labels.instance }} has expired!"
```

### Blackbox Exporter Configuration

Add to Prometheus for SSL probing. Create `/opt/ziggie/prometheus/blackbox.yml`:

```yaml
modules:
  https_2xx:
    prober: http
    timeout: 5s
    http:
      method: GET
      preferred_ip_protocol: ip4
      tls_config:
        insecure_skip_verify: false

  ssl_expiry:
    prober: http
    timeout: 5s
    http:
      method: GET
      preferred_ip_protocol: ip4
```

### Add Blackbox Exporter to Docker Compose

Add this service to `docker-compose.yml`:

```yaml
  blackbox-exporter:
    image: prom/blackbox-exporter:latest
    container_name: ziggie-blackbox
    restart: unless-stopped
    ports:
      - "9115:9115"
    volumes:
      - ./prometheus/blackbox.yml:/etc/blackbox_exporter/config.yml:ro
    networks:
      - ziggie-network
```

### Add SSL Probes to Prometheus

Update `/opt/ziggie/prometheus/prometheus.yml`:

```yaml
  - job_name: 'ssl-certs'
    metrics_path: /probe
    params:
      module: [https_2xx]
    static_configs:
      - targets:
          - https://ziggie.cloud
          - https://api.ziggie.cloud
          - https://n8n.ziggie.cloud
          - https://grafana.ziggie.cloud
          - https://portainer.ziggie.cloud
          - https://flowise.ziggie.cloud
          - https://chat.ziggie.cloud
          - https://mcp.ziggie.cloud
          - https://sim.ziggie.cloud
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115
```

### Manual Certificate Check Script

Create `/opt/ziggie/scripts/check-ssl.sh`:

```bash
#!/bin/bash
# =============================================================================
# SSL Certificate Status Check
# Usage: ./check-ssl.sh
# =============================================================================

echo "=============================================="
echo "  ZIGGIE SSL CERTIFICATE STATUS"
echo "=============================================="

DOMAINS=(
    "ziggie.cloud"
    "api.ziggie.cloud"
    "n8n.ziggie.cloud"
    "grafana.ziggie.cloud"
    "portainer.ziggie.cloud"
    "flowise.ziggie.cloud"
    "chat.ziggie.cloud"
    "mcp.ziggie.cloud"
    "sim.ziggie.cloud"
)

for domain in "${DOMAINS[@]}"; do
    echo ""
    echo "Checking: $domain"
    echo "----------------------------------------"

    # Get certificate expiry
    expiry=$(echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)

    if [ -n "$expiry" ]; then
        # Calculate days until expiry
        expiry_epoch=$(date -d "$expiry" +%s)
        current_epoch=$(date +%s)
        days_remaining=$(( (expiry_epoch - current_epoch) / 86400 ))

        if [ $days_remaining -lt 7 ]; then
            status="CRITICAL"
        elif [ $days_remaining -lt 30 ]; then
            status="WARNING"
        else
            status="OK"
        fi

        echo "Status: $status"
        echo "Expires: $expiry"
        echo "Days remaining: $days_remaining"
    else
        echo "Status: ERROR - Could not connect"
    fi
done

echo ""
echo "=============================================="
echo "  CHECK COMPLETE"
echo "=============================================="
```

---

## Subdomain Strategy

### Current Subdomain Allocation

| Subdomain | Service | Port | Purpose |
|-----------|---------|------|---------|
| ziggie.cloud | Landing Page | 443 | Main entry point |
| api.ziggie.cloud | Ziggie API | 8000 | REST/GraphQL API |
| n8n.ziggie.cloud | n8n | 5678 | Workflow automation |
| grafana.ziggie.cloud | Grafana | 3000 | Monitoring dashboards |
| portainer.ziggie.cloud | Portainer | 9000 | Docker management |
| flowise.ziggie.cloud | Flowise | 3001 | LLM workflow builder |
| chat.ziggie.cloud | Open WebUI | 3002 | Chat interface |
| mcp.ziggie.cloud | MCP Gateway | 8080 | MCP request routing |
| sim.ziggie.cloud | Sim Studio | 8001 | Agent simulation |

### Future Subdomain Reservations

| Subdomain | Purpose | Notes |
|-----------|---------|-------|
| docs.ziggie.cloud | Documentation | Docusaurus or similar |
| status.ziggie.cloud | Status page | Uptime monitoring |
| ws.ziggie.cloud | WebSocket | Dedicated WS endpoint |
| cdn.ziggie.cloud | CDN | Static assets (consider S3) |
| auth.ziggie.cloud | Authentication | Keycloak or similar |
| metrics.ziggie.cloud | Prometheus | Direct Prometheus access |

### Adding a New Subdomain

1. **Add DNS Record at Hostinger**:
   - Type: A
   - Name: newservice
   - Value: YOUR_VPS_IP

2. **Request Certificate** (if not using wildcard):
   ```bash
   docker run --rm -it \
     -v /opt/ziggie/certbot/conf:/etc/letsencrypt \
     -v /opt/ziggie/certbot/www:/var/www/certbot \
     certbot/certbot certonly \
       --webroot \
       --webroot-path=/var/www/certbot \
       --expand \
       -d ziggie.cloud \
       -d newservice.ziggie.cloud
   ```

3. **Add Nginx Server Block**:
   ```nginx
   server {
       listen 443 ssl http2;
       server_name newservice.ziggie.cloud;

       ssl_certificate /etc/letsencrypt/live/ziggie.cloud/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/ziggie.cloud/privkey.pem;
       # ... rest of config
   }
   ```

4. **Reload Nginx**:
   ```bash
   docker exec ziggie-nginx nginx -t && docker exec ziggie-nginx nginx -s reload
   ```

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: Certificate Request Fails with "Connection Refused"

**Cause**: Port 80 not open or nginx not running

**Solution**:
```bash
# Check if port 80 is open
sudo netstat -tlnp | grep :80

# Check firewall (if using ufw)
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check if nginx is running
docker ps | grep nginx
```

#### Issue: "Too Many Certificates" Error

**Cause**: Let's Encrypt rate limit (5 certificates per domain per week)

**Solution**:
- Wait 7 days, or
- Use staging environment for testing:
  ```bash
  certbot certonly --staging -d ziggie.cloud
  ```

#### Issue: Certificate Not Auto-Renewing

**Solution**:
```bash
# Check certbot container logs
docker logs ziggie-certbot

# Manual renewal test
docker run --rm \
  -v /opt/ziggie/certbot/conf:/etc/letsencrypt \
  -v /opt/ziggie/certbot/www:/var/www/certbot \
  certbot/certbot renew --dry-run

# Check renewal timer in container
docker exec ziggie-certbot ls -la /etc/letsencrypt/renewal/
```

#### Issue: Mixed Content Warnings

**Cause**: HTTP resources loaded on HTTPS page

**Solution**:
- Ensure all internal links use `https://`
- Add Content-Security-Policy header:
  ```nginx
  add_header Content-Security-Policy "upgrade-insecure-requests" always;
  ```

#### Issue: WebSocket Connections Fail

**Cause**: Missing upgrade headers

**Solution**:
Ensure these headers are in proxy config:
```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

#### Issue: ERR_SSL_VERSION_OR_CIPHER_MISMATCH

**Cause**: Old TLS version or weak cipher

**Solution**:
Update SSL configuration to use only TLS 1.2 and 1.3:
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
```

---

## Quick Reference Commands

### Certificate Management

```bash
# View all certificates
docker run --rm -v /opt/ziggie/certbot/conf:/etc/letsencrypt:ro \
  certbot/certbot certificates

# Force renewal (use sparingly)
docker run --rm \
  -v /opt/ziggie/certbot/conf:/etc/letsencrypt \
  -v /opt/ziggie/certbot/www:/var/www/certbot \
  certbot/certbot renew --force-renewal

# Revoke a certificate
docker run --rm -it \
  -v /opt/ziggie/certbot/conf:/etc/letsencrypt \
  certbot/certbot revoke --cert-path /etc/letsencrypt/live/ziggie.cloud/cert.pem

# Delete a certificate
docker run --rm -it \
  -v /opt/ziggie/certbot/conf:/etc/letsencrypt \
  certbot/certbot delete --cert-name ziggie.cloud
```

### Nginx Commands

```bash
# Test configuration
docker exec ziggie-nginx nginx -t

# Reload configuration (no downtime)
docker exec ziggie-nginx nginx -s reload

# View error logs
docker logs ziggie-nginx --tail 100

# View access logs
docker exec ziggie-nginx tail -f /var/log/nginx/access.log
```

### SSL Testing

```bash
# Check certificate expiry
echo | openssl s_client -servername ziggie.cloud -connect ziggie.cloud:443 2>/dev/null | openssl x509 -noout -dates

# Full SSL test (cipher info)
openssl s_client -connect ziggie.cloud:443 -servername ziggie.cloud </dev/null 2>/dev/null | head -20

# SSL Labs test (online)
# Visit: https://www.ssllabs.com/ssltest/analyze.html?d=ziggie.cloud
```

### DNS Verification

```bash
# Check A record
dig ziggie.cloud A +short

# Check all subdomains
for sub in api n8n grafana portainer flowise chat mcp sim; do
  echo "$sub.ziggie.cloud: $(dig $sub.ziggie.cloud A +short)"
done

# Check CAA record
dig ziggie.cloud CAA +short
```

---

## Appendix: Complete File Paths

| File | Path | Purpose |
|------|------|---------|
| Nginx Config | `/opt/ziggie/nginx/nginx.conf` | Main nginx configuration |
| Certbot Certs | `/opt/ziggie/certbot/conf/live/ziggie.cloud/` | SSL certificates |
| Renewal Hooks | `/opt/ziggie/certbot/conf/renewal-hooks/deploy/` | Post-renewal scripts |
| SSL Check Script | `/opt/ziggie/scripts/check-ssl.sh` | Manual SSL status check |
| Renewal Script | `/opt/ziggie/scripts/renew-ssl.sh` | Cron-based renewal |
| SSL Alerts | `/opt/ziggie/prometheus/alerts/ssl-alerts.yml` | Prometheus alerting |
| Renewal Log | `/var/log/ziggie-ssl-renewal.log` | Renewal operation logs |

---

*Document Created: 2025-12-28*
*Author: L1 SSL/TLS Research Agent*
*Status: Production-Ready*
