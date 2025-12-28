#!/bin/bash
# =============================================================================
# SSL Certificate Renewal Script
# =============================================================================
# Runs via cron every 12 hours to check and renew certificates if needed.
# Let's Encrypt certificates are valid for 90 days; renewal is attempted
# when less than 30 days remain.
#
# Usage:
#   ./renew-ssl.sh           # Normal renewal check
#   ./renew-ssl.sh --force   # Force renewal
#
# Cron setup (run as root):
#   0 3,15 * * * /opt/ziggie/scripts/renew-ssl.sh >> /var/log/ziggie-ssl-renewal.log 2>&1
# =============================================================================

set -e

# Configuration
ZIGGIE_DIR="/opt/ziggie"
CERTBOT_DIR="${ZIGGIE_DIR}/certbot"
LOG_FILE="/var/log/ziggie-ssl-renewal.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Colors (for interactive use)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check for force flag
FORCE_RENEWAL=""
if [ "$1" == "--force" ]; then
    FORCE_RENEWAL="--force-renewal"
    echo "[$TIMESTAMP] Force renewal requested" >> "$LOG_FILE"
fi

echo "[$TIMESTAMP] Starting SSL renewal check..." >> "$LOG_FILE"

# Check if certbot directory exists
if [ ! -d "${CERTBOT_DIR}/conf/live" ]; then
    echo "[$TIMESTAMP] ERROR: No certificates found in ${CERTBOT_DIR}/conf/live" >> "$LOG_FILE"
    exit 1
fi

# Run certbot renewal
docker run --rm \
    -v "${CERTBOT_DIR}/conf:/etc/letsencrypt" \
    -v "${CERTBOT_DIR}/www:/var/www/certbot" \
    certbot/certbot renew \
        --quiet \
        $FORCE_RENEWAL \
        >> "$LOG_FILE" 2>&1

RENEW_STATUS=$?

if [ $RENEW_STATUS -eq 0 ]; then
    echo "[$TIMESTAMP] Renewal check completed successfully" >> "$LOG_FILE"

    # Check if certificates were actually renewed by checking modification time
    CERT_FILE="${CERTBOT_DIR}/conf/live/ziggie.cloud/fullchain.pem"
    if [ -f "$CERT_FILE" ]; then
        CERT_MTIME=$(stat -c %Y "$CERT_FILE" 2>/dev/null || stat -f %m "$CERT_FILE" 2>/dev/null)
        CURRENT_TIME=$(date +%s)
        TIME_DIFF=$((CURRENT_TIME - CERT_MTIME))

        # If cert was modified in the last 5 minutes, it was renewed
        if [ $TIME_DIFF -lt 300 ]; then
            echo "[$TIMESTAMP] Certificate was renewed. Reloading nginx..." >> "$LOG_FILE"

            # Reload nginx to pick up new certificates
            docker exec ziggie-nginx nginx -t >> "$LOG_FILE" 2>&1
            if [ $? -eq 0 ]; then
                docker exec ziggie-nginx nginx -s reload >> "$LOG_FILE" 2>&1
                if [ $? -eq 0 ]; then
                    echo "[$TIMESTAMP] Nginx reloaded successfully" >> "$LOG_FILE"
                else
                    echo "[$TIMESTAMP] ERROR: Failed to reload nginx" >> "$LOG_FILE"
                fi
            else
                echo "[$TIMESTAMP] ERROR: Nginx config test failed" >> "$LOG_FILE"
            fi
        else
            echo "[$TIMESTAMP] No renewal needed at this time" >> "$LOG_FILE"
        fi
    fi
else
    echo "[$TIMESTAMP] ERROR: Renewal check failed with status $RENEW_STATUS" >> "$LOG_FILE"
fi

# Cleanup old logs (keep last 30 days)
if [ -f "$LOG_FILE" ]; then
    LINES=$(wc -l < "$LOG_FILE")
    if [ $LINES -gt 1000 ]; then
        tail -500 "$LOG_FILE" > "${LOG_FILE}.tmp"
        mv "${LOG_FILE}.tmp" "$LOG_FILE"
        echo "[$TIMESTAMP] Log file trimmed (was $LINES lines)" >> "$LOG_FILE"
    fi
fi

echo "[$TIMESTAMP] Renewal script completed" >> "$LOG_FILE"
