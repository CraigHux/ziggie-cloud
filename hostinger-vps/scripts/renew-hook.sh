#!/bin/bash
# =============================================================================
# SSL Certificate Renewal Hook Script
# =============================================================================
# Purpose: Reload Nginx after successful certificate renewal
# Called automatically by certbot after renewal
# =============================================================================

echo "📋 SSL Certificate Renewal Hook - Reloading Nginx..."

# Reload Nginx configuration to pick up new certificates
docker compose exec nginx nginx -s reload

if [ $? -eq 0 ]; then
    echo "✅ Nginx successfully reloaded with new certificates"
else
    echo "❌ Nginx reload failed! Manual intervention required."
    exit 1
fi
