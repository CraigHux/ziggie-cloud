#!/bin/bash
# =============================================================================
# SSL Certificate Initialization Script for ziggie.cloud
# =============================================================================
# Purpose: Generate Let's Encrypt SSL certificates on first deployment
# Run once only, then use auto-renewal
# =============================================================================

set -e  # Exit on error

DOMAIN="ziggie.cloud"
EMAIL="admin@ziggie.cloud"  # CHANGE THIS TO ACTUAL EMAIL
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
