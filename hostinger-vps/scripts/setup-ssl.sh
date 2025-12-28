#!/bin/bash
# =============================================================================
# ZIGGIE SSL/TLS SETUP SCRIPT
# =============================================================================
# This script automates the SSL certificate setup for ziggie.cloud
# Run on the VPS after docker-compose is running
#
# Usage: ./setup-ssl.sh [--staging]
#   --staging: Use Let's Encrypt staging environment for testing
#
# Prerequisites:
#   - Docker and docker-compose installed
#   - DNS records configured (A records for all subdomains)
#   - Ports 80 and 443 open
# =============================================================================

set -e

# Configuration
DOMAIN="ziggie.cloud"
EMAIL="admin@ziggie.cloud"
ZIGGIE_DIR="/opt/ziggie"
CERTBOT_DIR="${ZIGGIE_DIR}/certbot"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Subdomains to include in certificate
SUBDOMAINS=(
    "api"
    "n8n"
    "grafana"
    "portainer"
    "flowise"
    "chat"
    "mcp"
    "sim"
)

# Check for staging flag
STAGING=""
if [ "$1" == "--staging" ]; then
    STAGING="--staging"
    echo -e "${YELLOW}Using Let's Encrypt STAGING environment${NC}"
fi

echo -e "${BLUE}=============================================="
echo "  ZIGGIE SSL/TLS SETUP"
echo "==============================================${NC}"

# -----------------------------------------------------------------------------
# STEP 1: Verify Prerequisites
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[1/6] Verifying prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERROR: Docker not installed${NC}"
    exit 1
fi

# Check docker-compose
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}ERROR: Docker Compose not installed${NC}"
    exit 1
fi

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}WARNING: Not running as root. Some operations may fail.${NC}"
fi

echo -e "${GREEN}Prerequisites OK${NC}"

# -----------------------------------------------------------------------------
# STEP 2: Verify DNS
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[2/6] Verifying DNS configuration...${NC}"

VPS_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null)
echo "VPS IP: $VPS_IP"

# Check main domain
DOMAIN_IP=$(dig +short "$DOMAIN" A 2>/dev/null | head -1)
if [ "$DOMAIN_IP" != "$VPS_IP" ]; then
    echo -e "${RED}ERROR: $DOMAIN does not resolve to $VPS_IP (got: $DOMAIN_IP)${NC}"
    echo "Please configure DNS at Hostinger before continuing."
    exit 1
fi
echo -e "${GREEN}$DOMAIN -> $VPS_IP OK${NC}"

# Check subdomains
for sub in "${SUBDOMAINS[@]}"; do
    SUB_IP=$(dig +short "$sub.$DOMAIN" A 2>/dev/null | head -1)
    if [ "$SUB_IP" != "$VPS_IP" ]; then
        echo -e "${YELLOW}WARNING: $sub.$DOMAIN does not resolve to $VPS_IP${NC}"
    else
        echo -e "${GREEN}$sub.$DOMAIN -> $VPS_IP OK${NC}"
    fi
done

# -----------------------------------------------------------------------------
# STEP 3: Create Directory Structure
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[3/6] Creating directory structure...${NC}"

mkdir -p "${CERTBOT_DIR}/conf"
mkdir -p "${CERTBOT_DIR}/www"
chmod 755 "${CERTBOT_DIR}"

echo -e "${GREEN}Directories created${NC}"

# -----------------------------------------------------------------------------
# STEP 4: Create Initial HTTP-Only Nginx Config
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[4/6] Starting temporary HTTP nginx for ACME challenge...${NC}"

# Create temporary config
cat > "${ZIGGIE_DIR}/nginx/nginx-initial.conf" << 'EOF'
events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name ziggie.cloud *.ziggie.cloud;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
            allow all;
        }

        location / {
            return 200 'Ziggie Cloud - SSL Setup in Progress';
            add_header Content-Type text/plain;
        }
    }
}
EOF

# Stop existing nginx if running
docker stop ziggie-nginx 2>/dev/null || true
docker rm ziggie-nginx 2>/dev/null || true

# Start temporary nginx
docker run -d \
    --name ziggie-nginx-init \
    --network ziggie-network \
    -p 80:80 \
    -v "${ZIGGIE_DIR}/nginx/nginx-initial.conf:/etc/nginx/nginx.conf:ro" \
    -v "${CERTBOT_DIR}/www:/var/www/certbot:rw" \
    nginx:alpine

# Wait for nginx to start
sleep 3

# Test nginx is running
if ! curl -s "http://localhost" > /dev/null 2>&1; then
    echo -e "${RED}ERROR: Nginx failed to start${NC}"
    docker logs ziggie-nginx-init
    exit 1
fi

echo -e "${GREEN}Temporary nginx started${NC}"

# -----------------------------------------------------------------------------
# STEP 5: Request SSL Certificates
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[5/6] Requesting SSL certificates from Let's Encrypt...${NC}"

# Build domain list
DOMAIN_ARGS="-d $DOMAIN"
for sub in "${SUBDOMAINS[@]}"; do
    DOMAIN_ARGS="$DOMAIN_ARGS -d $sub.$DOMAIN"
done

# Request certificate
docker run --rm \
    -v "${CERTBOT_DIR}/conf:/etc/letsencrypt" \
    -v "${CERTBOT_DIR}/www:/var/www/certbot" \
    certbot/certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        $STAGING \
        $DOMAIN_ARGS

CERT_STATUS=$?

# Stop temporary nginx
docker stop ziggie-nginx-init 2>/dev/null || true
docker rm ziggie-nginx-init 2>/dev/null || true

if [ $CERT_STATUS -ne 0 ]; then
    echo -e "${RED}ERROR: Certificate request failed${NC}"
    exit 1
fi

echo -e "${GREEN}Certificates obtained successfully${NC}"

# -----------------------------------------------------------------------------
# STEP 6: Deploy HTTPS Configuration
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[6/6] Deploying HTTPS configuration...${NC}"

# Copy HTTPS config
if [ -f "${ZIGGIE_DIR}/nginx/nginx-https.conf" ]; then
    cp "${ZIGGIE_DIR}/nginx/nginx-https.conf" "${ZIGGIE_DIR}/nginx/nginx.conf"
    echo -e "${GREEN}HTTPS nginx config deployed${NC}"
else
    echo -e "${YELLOW}WARNING: nginx-https.conf not found, using existing config${NC}"
fi

# Update docker-compose to use correct paths
cd "${ZIGGIE_DIR}"

# Restart full stack
docker compose up -d

# Wait for services
sleep 10

# Verify HTTPS
if curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/health" 2>/dev/null | grep -q "200"; then
    echo -e "${GREEN}HTTPS verification: OK${NC}"
else
    echo -e "${YELLOW}WARNING: HTTPS verification incomplete. Check nginx logs.${NC}"
fi

# -----------------------------------------------------------------------------
# COMPLETE
# -----------------------------------------------------------------------------
echo -e "\n${GREEN}=============================================="
echo "  SSL SETUP COMPLETE!"
echo "==============================================${NC}"
echo ""
echo "Your services are now available at:"
echo ""
echo "  Main:      https://$DOMAIN"
echo "  API:       https://api.$DOMAIN"
echo "  n8n:       https://n8n.$DOMAIN"
echo "  Grafana:   https://grafana.$DOMAIN"
echo "  Portainer: https://portainer.$DOMAIN"
echo "  Flowise:   https://flowise.$DOMAIN"
echo "  Chat:      https://chat.$DOMAIN"
echo "  MCP:       https://mcp.$DOMAIN"
echo "  Sim:       https://sim.$DOMAIN"
echo ""
echo "Certificate details:"
docker run --rm \
    -v "${CERTBOT_DIR}/conf:/etc/letsencrypt:ro" \
    certbot/certbot certificates 2>/dev/null | grep -A5 "Certificate Name"
echo ""
echo "Auto-renewal is configured via the certbot container."
echo ""
if [ -n "$STAGING" ]; then
    echo -e "${YELLOW}NOTE: You used --staging. Re-run without --staging for production certificates.${NC}"
fi
