#!/bin/bash
# =============================================================================
# Certificate Expiration Check for Prometheus
# =============================================================================
# Purpose: Export certificate expiration metric for Prometheus monitoring
# =============================================================================

DOMAIN="ziggie.cloud"
CERT_FILE="/etc/letsencrypt/live/$DOMAIN/cert.pem"

if [ -f "$CERT_FILE" ]; then
    EXPIRY_DATE=$(openssl x509 -enddate -noout -in "$CERT_FILE" | cut -d= -f2)
    EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
    NOW_EPOCH=$(date +%s)
    DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))
    echo "ssl_certificate_expiry_days{domain=\"$DOMAIN\"} $DAYS_LEFT"
else
    # -1 indicates certificate file not found
    echo "ssl_certificate_expiry_days{domain=\"$DOMAIN\"} -1"
fi
