# SSL/HTTPS Setup Guide for ziggie.cloud

> **L1 Strategic Research Agent - SSL/HTTPS Configuration**
> **Date**: 2025-12-28
> **Target Domain**: ziggie.cloud
> **VPS IP**: 82.25.112.73
> **Status**: READY FOR DEPLOYMENT

---

## Executive Summary

This guide provides step-by-step instructions to configure Let's Encrypt SSL certificates for ziggie.cloud using Certbot in Docker. The configuration supports automatic certificate renewal and achieves A+ SSL rating.

**Estimated Time**: 30-45 minutes
**Downtime**: ~5 minutes during Nginx reload

---

## Current Configuration Analysis

### ✅ Strengths
- Certbot container already defined in docker-compose.yml
- HTTP to HTTPS redirect configured (lines 69-82)
- ACME challenge path configured (/.well-known/acme-challenge/)
- Modern SSL settings (TLSv1.2, TLSv1.3)
- Security headers in place

### ⚠️ Issues to Fix
1. **Line 87**: Placeholder domain `ziggie.yourdomain.com` → Must change to `ziggie.cloud`
2. **Lines 90-91**: Certificate paths reference placeholder domain
3. **Missing**: Initial certificate generation script
4. **Missing**: Domain DNS validation

---

## Prerequisites Checklist

```text
□ Domain ziggie.cloud DNS A record points to 82.25.112.73
□ Ports 80 and 443 open on VPS firewall
□ Docker and Docker Compose installed
□ Root or sudo access to VPS
□ Email for Let's Encrypt notifications
```

### DNS Verification

Run this command to verify DNS is configured correctly:

```bash
# From local machine or VPS
dig +short ziggie.cloud

# Expected output: 82.25.112.73
# If not, update DNS A record and wait for propagation (5-30 minutes)
```

---

## Phase 1: Pre-Deployment Configuration

### Step 1.1: Update Nginx Configuration

**File**: `C:\Ziggie\hostinger-vps\nginx\nginx.conf`

**Changes Required**:

```nginx
# BEFORE (Line 87)
server_name ziggie.yourdomain.com;  # CHANGE THIS

# AFTER
server_name ziggie.cloud;

# BEFORE (Lines 90-91)
ssl_certificate /etc/letsencrypt/live/ziggie.yourdomain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/ziggie.yourdomain.com/privkey.pem;

# AFTER
ssl_certificate /etc/letsencrypt/live/ziggie.cloud/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/ziggie.cloud/privkey.pem;
```

**Complete Updated Server Block**:

```nginx
# Main HTTPS server
server {
    listen 443 ssl http2;
    server_name ziggie.cloud;

    # SSL certificates (managed by certbot)
    ssl_certificate /etc/letsencrypt/live/ziggie.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ziggie.cloud/privkey.pem;

    # SSL settings (ALREADY CORRECT - NO CHANGES NEEDED)
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # Security headers (ALREADY CORRECT - NO CHANGES NEEDED)
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # ... rest of configuration remains unchanged
}
```

### Step 1.2: Enhanced SSL Security Headers (OPTIONAL - RECOMMENDED)

Add these additional security headers for A+ rating:

```nginx
# Add after existing security headers (after line 105)

# HSTS (HTTP Strict Transport Security) - Forces HTTPS for 1 year
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

# CSP (Content Security Policy) - Prevents XSS attacks
add_header Content-Security-Policy "default-src 'self' https:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';" always;

# Permissions Policy (formerly Feature-Policy)
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

### Step 1.3: Create .env File (if not exists)

**File**: `C:\Ziggie\hostinger-vps\.env`

```bash
# Domain Configuration
VPS_DOMAIN=ziggie.cloud

# Let's Encrypt Email (for renewal notifications)
LETSENCRYPT_EMAIL=admin@ziggie.cloud  # CHANGE THIS

# ... existing variables (keep all)
```

---

## Phase 2: Initial Certificate Generation

### Step 2.1: Create Certificate Request Script

**File**: `C:\Ziggie\hostinger-vps\scripts\init-ssl.sh`

```bash
#!/bin/bash
# =============================================================================
# SSL Certificate Initialization Script for ziggie.cloud
# =============================================================================
# Purpose: Generate Let's Encrypt SSL certificates on first deployment
# Run once only, then use auto-renewal
# =============================================================================

set -e  # Exit on error

DOMAIN="ziggie.cloud"
EMAIL="admin@ziggie.cloud"  # CHANGE THIS
STAGING=0  # Set to 1 for testing, 0 for production

echo "========================================"
echo "SSL Certificate Setup for $DOMAIN"
echo "========================================"

# Check if certificates already exist
if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    echo "✅ Certificates already exist for $DOMAIN"
    echo "Skipping certificate generation."
    exit 0
fi

echo "📋 Step 1: Creating certificate directories..."
mkdir -p /var/www/certbot
mkdir -p /etc/letsencrypt

echo "📋 Step 2: Starting Nginx (HTTP only for ACME challenge)..."
docker compose up -d nginx

echo "⏳ Waiting 10 seconds for Nginx to start..."
sleep 10

echo "📋 Step 3: Requesting SSL certificate from Let's Encrypt..."

if [ $STAGING -ne 0 ]; then
    echo "⚠️  STAGING MODE - Using test certificates"
    STAGING_ARG="--staging"
else
    echo "✅ PRODUCTION MODE - Requesting real certificates"
    STAGING_ARG=""
fi

docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    $STAGING_ARG \
    -d $DOMAIN

if [ $? -eq 0 ]; then
    echo "✅ Certificates successfully generated!"
    echo "📋 Step 4: Reloading Nginx with SSL configuration..."
    docker compose exec nginx nginx -s reload
    echo "✅ SSL setup complete!"
    echo ""
    echo "Test your SSL configuration:"
    echo "  https://$DOMAIN/health"
    echo "  https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
else
    echo "❌ Certificate generation failed!"
    echo "Check DNS configuration: dig +short $DOMAIN"
    echo "Check port 80 accessibility: curl -I http://$DOMAIN"
    exit 1
fi
```

**Make executable**:

```bash
chmod +x C:\Ziggie\hostinger-vps\scripts\init-ssl.sh
```

### Step 2.2: Initial Certificate Generation (EXECUTE ON VPS)

**CRITICAL**: Run these commands ON THE VPS (not local machine)

```bash
# SSH into VPS
ssh root@82.25.112.73

# Navigate to project directory
cd /opt/ziggie  # Or wherever docker-compose.yml is located

# Verify DNS (MUST return 82.25.112.73)
dig +short ziggie.cloud

# Run certificate generation script
./scripts/init-ssl.sh
```

**Expected Output**:

```text
========================================
SSL Certificate Setup for ziggie.cloud
========================================
📋 Step 1: Creating certificate directories...
📋 Step 2: Starting Nginx (HTTP only for ACME challenge)...
⏳ Waiting 10 seconds for Nginx to start...
📋 Step 3: Requesting SSL certificate from Let's Encrypt...
✅ PRODUCTION MODE - Requesting real certificates
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Requesting a certificate for ziggie.cloud

Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/ziggie.cloud/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/ziggie.cloud/privkey.pem
✅ Certificates successfully generated!
📋 Step 4: Reloading Nginx with SSL configuration...
✅ SSL setup complete!
```

---

## Phase 3: Certificate Renewal Automation

### Step 3.1: Verify Certbot Container Configuration

The certbot container in `docker-compose.yml` (lines 324-333) is already configured for auto-renewal:

```yaml
# Certbot - SSL Certificate Management
certbot:
  image: certbot/certbot:latest
  container_name: ziggie-certbot
  volumes:
    - certbot_data:/var/www/certbot
    - certbot_certs:/etc/letsencrypt
  entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
  networks:
    - ziggie-network
```

**How it works**:
- Runs `certbot renew` every 12 hours
- Checks if certificates expire within 30 days
- Automatically renews if needed
- Zero manual intervention required

### Step 3.2: Manual Renewal Test

Test renewal process manually:

```bash
# On VPS
docker compose run --rm certbot renew --dry-run

# Expected output:
# Congratulations, all simulated renewals succeeded:
#   /etc/letsencrypt/live/ziggie.cloud/fullchain.pem (success)
```

### Step 3.3: Post-Renewal Hook (Reload Nginx)

**File**: `C:\Ziggie\hostinger-vps\scripts\renew-hook.sh`

```bash
#!/bin/bash
# Post-renewal hook: Reload Nginx after certificate renewal

docker compose exec nginx nginx -s reload
echo "✅ Nginx reloaded with new certificates"
```

Update certbot container to use hook:

```yaml
# Modified certbot service (docker-compose.yml)
certbot:
  image: certbot/certbot:latest
  container_name: ziggie-certbot
  volumes:
    - certbot_data:/var/www/certbot
    - certbot_certs:/etc/letsencrypt
    - ./scripts/renew-hook.sh:/renew-hook.sh:ro
  entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew --deploy-hook /renew-hook.sh; sleep 12h & wait $${!}; done;'"
  networks:
    - ziggie-network
```

---

## Phase 4: Deployment and Verification

### Step 4.1: Full Stack Deployment

```bash
# On VPS
cd /opt/ziggie

# Pull latest images
docker compose pull

# Start all services
docker compose up -d

# Check container status
docker compose ps

# Expected: All containers "Up" or "Up (healthy)"
```

### Step 4.2: Verify SSL Configuration

**Test 1: Basic HTTPS Access**

```bash
# From any machine
curl -I https://ziggie.cloud/health

# Expected: HTTP/2 200
# Expected: strict-transport-security header present
```

**Test 2: Certificate Validity**

```bash
# From any machine
echo | openssl s_client -servername ziggie.cloud -connect ziggie.cloud:443 2>/dev/null | openssl x509 -noout -dates

# Expected output:
# notBefore=Dec 28 XX:XX:XX 2025 GMT
# notAfter=Mar 28 XX:XX:XX 2026 GMT  (90 days from issue)
```

**Test 3: SSL Labs Rating (COMPREHENSIVE)**

Visit: https://www.ssllabs.com/ssltest/analyze.html?d=ziggie.cloud

**Expected Rating**: A or A+

### Step 4.3: Test All Service Endpoints

```bash
# Health endpoint
curl -k https://ziggie.cloud/health

# n8n
curl -I https://ziggie.cloud/n8n/

# API
curl -I https://ziggie.cloud/api/

# Portainer
curl -I https://ziggie.cloud/portainer/

# All should return HTTPS responses (200, 301, or 302)
```

---

## Phase 5: Monitoring and Maintenance

### Step 5.1: Certificate Expiration Monitoring

**Method 1: Manual Check**

```bash
# On VPS
docker compose run --rm certbot certificates

# Output shows expiration dates for all certificates
```

**Method 2: Automated Monitoring (Prometheus + Grafana)**

Add certificate expiration metric to Prometheus:

**File**: `C:\Ziggie\hostinger-vps\prometheus\cert-check.sh`

```bash
#!/bin/bash
# Certificate expiration check for Prometheus

CERT_FILE="/etc/letsencrypt/live/ziggie.cloud/cert.pem"

if [ -f "$CERT_FILE" ]; then
    EXPIRY_DATE=$(openssl x509 -enddate -noout -in "$CERT_FILE" | cut -d= -f2)
    EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
    NOW_EPOCH=$(date +%s)
    DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))
    echo "ssl_certificate_expiry_days{domain=\"ziggie.cloud\"} $DAYS_LEFT"
else
    echo "ssl_certificate_expiry_days{domain=\"ziggie.cloud\"} -1"
fi
```

**Alert Rule** (add to Prometheus alerts):

```yaml
# prometheus/alerts/ssl.yml
groups:
  - name: ssl_alerts
    interval: 1h
    rules:
      - alert: SSLCertificateExpiringSoon
        expr: ssl_certificate_expiry_days < 30
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "SSL certificate expiring soon for {{ $labels.domain }}"
          description: "Certificate expires in {{ $value }} days"

      - alert: SSLCertificateExpired
        expr: ssl_certificate_expiry_days < 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "SSL certificate EXPIRED for {{ $labels.domain }}"
          description: "Certificate has expired!"
```

### Step 5.2: Renewal Logs

```bash
# Check certbot logs
docker compose logs certbot --tail=100

# Check Nginx logs
docker compose logs nginx --tail=100 | grep ssl

# Check renewal history
cat /etc/letsencrypt/renewal/ziggie.cloud.conf
```

### Step 5.3: Common Issues and Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Certificate not found | DNS not propagated | Wait 30 min, retry |
| Port 80 unreachable | Firewall blocking | Open port 80 |
| Rate limit exceeded | Too many attempts | Wait 1 hour, use --staging flag |
| Nginx fails to reload | Syntax error in config | `nginx -t` to test config |
| Certbot container exits | Invalid entrypoint | Check docker compose logs |

---

## Phase 6: Advanced Configuration

### Step 6.1: Wildcard Certificates (OPTIONAL)

For subdomain support (e.g., `*.ziggie.cloud`):

```bash
# Requires DNS challenge (not HTTP)
docker compose run --rm certbot certonly \
    --dns-cloudflare \
    --dns-cloudflare-credentials /etc/letsencrypt/cloudflare.ini \
    --email admin@ziggie.cloud \
    --agree-tos \
    -d ziggie.cloud \
    -d "*.ziggie.cloud"
```

**Requirements**:
- Cloudflare API token (or other DNS provider)
- DNS provider plugin installed in certbot container

### Step 6.2: OCSP Stapling (Performance Optimization)

Add to Nginx SSL server block:

```nginx
# OCSP Stapling (faster certificate verification)
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/letsencrypt/live/ziggie.cloud/chain.pem;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
```

### Step 6.3: HTTP/3 Support (Cutting Edge)

Nginx supports HTTP/3 (QUIC) for even faster performance:

```nginx
# Add to server block
listen 443 quic reuseport;
listen 443 ssl http2;

# Add header to advertise HTTP/3 support
add_header Alt-Svc 'h3=":443"; ma=86400' always;
```

**Note**: Requires Nginx compiled with QUIC support (use `nginx:alpine-quic` image)

---

## Complete Deployment Checklist

### Pre-Deployment

```text
□ DNS A record configured (ziggie.cloud → 82.25.112.73)
□ DNS propagation verified (dig +short ziggie.cloud)
□ Ports 80 and 443 open on VPS firewall
□ Email configured for Let's Encrypt notifications
□ nginx.conf updated with ziggie.cloud domain
□ .env file contains VPS_DOMAIN=ziggie.cloud
```

### Initial SSL Setup

```text
□ init-ssl.sh script created and made executable
□ Script executed successfully on VPS
□ Certificates generated in /etc/letsencrypt/live/ziggie.cloud/
□ Nginx reloaded with SSL configuration
□ HTTPS access verified (curl -I https://ziggie.cloud/health)
```

### Post-Deployment Verification

```text
□ SSL Labs test shows A or A+ rating
□ All service endpoints accessible via HTTPS
□ HTTP redirects to HTTPS (curl -I http://ziggie.cloud)
□ Certificate expiration shows ~90 days
□ Certbot auto-renewal container running
□ Renewal dry-run test passes
```

### Monitoring Setup

```text
□ Prometheus SSL expiration metric configured
□ Grafana dashboard shows certificate status
□ Alert rule for 30-day expiration warning
□ Log aggregation includes certbot renewal logs
```

---

## Rollback Plan

If SSL setup fails or causes issues:

### Step 1: Disable HTTPS Temporarily

```bash
# On VPS
docker compose stop nginx

# Edit nginx.conf: Comment out HTTPS server block (lines 85-258)
# Uncomment HTTP-only server block

docker compose start nginx
```

### Step 2: Remove Failed Certificates

```bash
docker compose run --rm certbot delete --cert-name ziggie.cloud
```

### Step 3: Retry with Staging

```bash
# Set STAGING=1 in init-ssl.sh
./scripts/init-ssl.sh

# Test with staging certificates
# If successful, repeat with STAGING=0
```

---

## Production Deployment Timeline

| Time | Phase | Action |
|------|-------|--------|
| T-0 | Preparation | Update nginx.conf, create init-ssl.sh |
| T+5min | DNS Check | Verify DNS propagation |
| T+10min | Certificate Generation | Run init-ssl.sh on VPS |
| T+15min | Verification | Test HTTPS endpoints |
| T+20min | Monitoring | Configure alerts |
| T+30min | Documentation | Update deployment docs |

**Total Deployment Time**: ~30 minutes

---

## Security Best Practices

### Certificate Security

1. **Never commit certificates to Git**
   - Certificates stored in Docker volumes only
   - .gitignore includes `*.pem`, `*.key`

2. **Restrict certificate file permissions**
   ```bash
   chmod 600 /etc/letsencrypt/live/ziggie.cloud/privkey.pem
   ```

3. **Use strong ciphers only**
   - Already configured in nginx.conf (TLSv1.2, TLSv1.3)
   - Weak ciphers disabled

4. **Enable HSTS**
   - Forces HTTPS for all future visits
   - Prevents downgrade attacks

### Operational Security

1. **Monitor renewal logs**
   - Failed renewals = potential downtime
   - Alert on renewal failures

2. **Test renewal quarterly**
   ```bash
   docker compose run --rm certbot renew --dry-run
   ```

3. **Backup certificates**
   ```bash
   tar -czf letsencrypt-backup-$(date +%Y%m%d).tar.gz /etc/letsencrypt/
   ```

4. **Document renewal process**
   - This guide serves as SOP
   - Update if process changes

---

## Cost Analysis

| Item | Cost | Notes |
|------|------|-------|
| Let's Encrypt Certificates | **$0/year** | Free, automated |
| Certbot Container | **$0/year** | Open source |
| Nginx Container | **$0/year** | Open source |
| VPS Bandwidth (HTTPS overhead) | **~$0.50/month** | Negligible increase |
| **Total SSL Cost** | **$0/year** | 100% free |

**Comparison**: Commercial SSL certificate = $50-300/year

---

## Key Files Reference

| File | Location | Purpose |
|------|----------|---------|
| Main Config | C:\Ziggie\hostinger-vps\nginx\nginx.conf | Nginx SSL configuration |
| SSL-Ready Config | C:\Ziggie\hostinger-vps\nginx\nginx.conf.ssl-ready | Pre-configured SSL template |
| Docker Stack | C:\Ziggie\hostinger-vps\docker-compose.yml | Certbot container definition |
| Init Script | C:\Ziggie\hostinger-vps\scripts\init-ssl.sh | Simple certificate generation |
| **Production Deploy** | **C:\Ziggie\hostinger-vps\scripts\deploy-ssl-production.sh** | **Full production SSL deployment** |
| Renewal Hook | C:\Ziggie\hostinger-vps\scripts\renew-hook.sh | Post-renewal Nginx reload |
| Cert Check | C:\Ziggie\hostinger-vps\prometheus\cert-check.sh | Expiration monitoring |
| Environment | C:\Ziggie\hostinger-vps\.env | Domain configuration |

---

## Production SSL Deployment Script

### Overview

The `deploy-ssl-production.sh` script provides a complete, automated SSL deployment with:

- Full validation before deployment (DNS, ports, dependencies)
- TLS 1.3 support with TLS 1.2 fallback
- HSTS with preload directive (max-age=31536000, includeSubDomains, preload)
- OCSP Stapling for performance
- Automatic renewal via certbot container (12-hour cycle)
- Post-renewal nginx reload hook
- Rollback capability on failure

### Usage

```bash
# SSH into VPS
ssh root@82.25.112.73

# Navigate to project
cd /opt/ziggie

# Make script executable
chmod +x scripts/deploy-ssl-production.sh

# Run production deployment
./scripts/deploy-ssl-production.sh

# Or with options:
STAGING=1 ./scripts/deploy-ssl-production.sh       # Test with staging certs
DRY_RUN=1 ./scripts/deploy-ssl-production.sh       # Dry run, no changes
FORCE_RENEW=1 ./scripts/deploy-ssl-production.sh   # Force certificate renewal
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| STAGING | 0 | Use Let's Encrypt staging server (for testing) |
| FORCE_RENEW | 0 | Force certificate renewal even if valid |
| DRY_RUN | 0 | Dry run mode, no actual changes |
| USE_DNS_CHALLENGE | 0 | Use DNS challenge for wildcard certs |
| LETSENCRYPT_EMAIL | admin@ziggie.cloud | Email for Let's Encrypt notifications |
| COMPOSE_DIR | /opt/ziggie | Path to docker-compose.yml |
| VPS_IP | (auto-detect) | Expected VPS IP for DNS verification |

### Deployment Phases

The script executes in 6 phases:

1. **Validation**: Check root, dependencies, DNS, ports, existing certs
2. **Preparation**: Create directories, temporary nginx config, renewal hooks
3. **Certificate Generation**: Request certificate via webroot or DNS challenge
4. **Production Configuration**: Install SSL nginx config, test, start nginx
5. **Verification**: Test HTTPS, HSTS, TLS version, OCSP, certificate chain
6. **Renewal Test**: Dry-run renewal to verify auto-renewal works

### HSTS Preload Requirements (2025)

To be eligible for HSTS preload list submission at https://hstspreload.org/:

| Requirement | Value | Script Sets |
|-------------|-------|-------------|
| max-age | >= 31536000 (1 year) | 31536000 |
| includeSubDomains | Required | Yes |
| preload directive | Required | Yes |
| Serve HTTPS only | Required | Enforced via redirect |
| Valid certificate | Required | Let's Encrypt |

### Verification Commands

After deployment, verify the configuration:

```bash
# Test HTTPS access
curl -I https://ziggie.cloud/health

# Check TLS version
echo | openssl s_client -connect ziggie.cloud:443 -tls1_3 2>/dev/null | grep TLSv

# Check HSTS header
curl -sI https://ziggie.cloud/health | grep -i strict-transport

# Check certificate expiration
echo | openssl s_client -servername ziggie.cloud -connect ziggie.cloud:443 2>/dev/null | openssl x509 -noout -dates

# Run SSL Labs test
# Visit: https://www.ssllabs.com/ssltest/analyze.html?d=ziggie.cloud
```

### Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| DNS verification failed | A record not configured | Add A record pointing to VPS IP |
| Port 80 blocked | Firewall | `ufw allow 80/tcp` |
| Rate limit exceeded | Too many cert requests | Wait 1 hour, use STAGING=1 |
| Nginx config test fails | Syntax error | Check `docker compose logs nginx` |
| OCSP stapling not working | New certificate | Wait 24 hours for OCSP to propagate |

---

## Next Steps

1. **Run production SSL deployment** on VPS:
   ```bash
   ./scripts/deploy-ssl-production.sh
   ```
2. **Verify SSL Labs rating** (target: A+)
3. **Submit for HSTS preload** at https://hstspreload.org/
4. **Configure monitoring alerts** for certificate expiration
5. **Document in ZIGGIE-ECOSYSTEM-MASTER-STATUS-V5.md**

---

## Support Resources

| Resource | URL |
|----------|-----|
| Let's Encrypt Docs | https://letsencrypt.org/docs/ |
| Certbot Documentation | https://certbot.eff.org/docs/ |
| Nginx SSL Module | https://nginx.org/en/docs/http/ngx_http_ssl_module.html |
| SSL Labs Test | https://www.ssllabs.com/ssltest/ |
| Security Headers Check | https://securityheaders.com/ |
| HSTS Preload Submission | https://hstspreload.org/ |

---

*L1 Strategic Research Agent - SSL/HTTPS Configuration*
*Deliverable: Production-Ready SSL Setup Guide + Deployment Script*
*Status: READY FOR DEPLOYMENT*
*Created: 2025-12-28*
*Updated: 2025-12-28 (Added deploy-ssl-production.sh documentation)*
