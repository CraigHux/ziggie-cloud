#!/bin/bash
# =============================================================================
# SSL Certificate Status Check Script
# =============================================================================
# Displays the status of all SSL certificates for ziggie.cloud
# Useful for manual verification and debugging
#
# Usage: ./check-ssl.sh
# =============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DOMAIN="ziggie.cloud"
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

echo -e "${BLUE}=============================================="
echo "  ZIGGIE SSL CERTIFICATE STATUS"
echo "==============================================${NC}"
echo ""

# Check each domain
ALL_DOMAINS=("$DOMAIN" "${SUBDOMAINS[@]/%/.$DOMAIN}")

for domain in "${ALL_DOMAINS[@]}"; do
    echo -e "${BLUE}Checking: $domain${NC}"
    echo "----------------------------------------"

    # Get certificate info
    CERT_INFO=$(echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | openssl x509 -noout -dates -issuer 2>/dev/null)

    if [ -n "$CERT_INFO" ]; then
        # Extract expiry date
        EXPIRY=$(echo "$CERT_INFO" | grep "notAfter" | cut -d= -f2)
        ISSUER=$(echo "$CERT_INFO" | grep "issuer" | cut -d= -f2-)

        if [ -n "$EXPIRY" ]; then
            # Calculate days until expiry
            EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s 2>/dev/null || date -j -f "%b %d %T %Y %Z" "$EXPIRY" +%s 2>/dev/null)
            CURRENT_EPOCH=$(date +%s)
            DAYS_REMAINING=$(( (EXPIRY_EPOCH - CURRENT_EPOCH) / 86400 ))

            # Determine status
            if [ $DAYS_REMAINING -lt 0 ]; then
                STATUS="${RED}EXPIRED${NC}"
            elif [ $DAYS_REMAINING -lt 7 ]; then
                STATUS="${RED}CRITICAL${NC}"
            elif [ $DAYS_REMAINING -lt 30 ]; then
                STATUS="${YELLOW}WARNING${NC}"
            else
                STATUS="${GREEN}OK${NC}"
            fi

            echo -e "Status: $STATUS"
            echo "Expires: $EXPIRY"
            echo "Days remaining: $DAYS_REMAINING"
            echo "Issuer: $ISSUER"
        else
            echo -e "Status: ${RED}ERROR - Could not parse certificate${NC}"
        fi
    else
        # Try to get more info about the failure
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://$domain" 2>/dev/null)
        if [ "$HTTP_CODE" == "000" ]; then
            echo -e "Status: ${RED}ERROR - Could not connect${NC}"
        else
            echo -e "Status: ${YELLOW}HTTP $HTTP_CODE (SSL may have issues)${NC}"
        fi
    fi
    echo ""
done

# Summary from certbot
echo -e "${BLUE}=============================================="
echo "  CERTBOT CERTIFICATE DETAILS"
echo "==============================================${NC}"
echo ""

if [ -d "/opt/ziggie/certbot/conf" ]; then
    docker run --rm \
        -v /opt/ziggie/certbot/conf:/etc/letsencrypt:ro \
        certbot/certbot certificates 2>/dev/null
else
    echo -e "${YELLOW}Certbot directory not found. Certificates may not be installed.${NC}"
fi

echo ""
echo -e "${BLUE}=============================================="
echo "  SSL LABS QUICK CHECK"
echo "==============================================${NC}"
echo ""
echo "For detailed SSL analysis, visit:"
echo "  https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
echo ""
echo "Expected grade: A or A+"
echo ""
