#!/bin/bash
# =============================================================================
# SSL Configuration Testing Script
# =============================================================================
# Purpose: Comprehensive SSL/HTTPS testing for ziggie.cloud
# =============================================================================

DOMAIN="ziggie.cloud"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "SSL/HTTPS Configuration Test Suite"
echo "Domain: $DOMAIN"
echo "========================================"

# Test 1: DNS Resolution
echo ""
echo "Test 1: DNS Resolution"
echo "----------------------------------------"
IP=$(dig +short $DOMAIN)
if [ -z "$IP" ]; then
    echo -e "${RED}❌ FAIL${NC}: DNS not resolving"
    echo "Fix: Configure A record in DNS settings"
    exit 1
else
    echo -e "${GREEN}✅ PASS${NC}: $DOMAIN → $IP"
fi

# Test 2: Port 80 Accessibility
echo ""
echo "Test 2: HTTP Port 80 Accessibility"
echo "----------------------------------------"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN/health || echo "000")
if [ "$HTTP_STATUS" = "301" ] || [ "$HTTP_STATUS" = "302" ]; then
    echo -e "${GREEN}✅ PASS${NC}: HTTP redirects to HTTPS (Status: $HTTP_STATUS)"
elif [ "$HTTP_STATUS" = "000" ]; then
    echo -e "${RED}❌ FAIL${NC}: Port 80 not accessible"
    echo "Fix: Check firewall rules, ensure nginx is running"
else
    echo -e "${YELLOW}⚠️  WARNING${NC}: Unexpected status code: $HTTP_STATUS"
fi

# Test 3: Port 443 Accessibility
echo ""
echo "Test 3: HTTPS Port 443 Accessibility"
echo "----------------------------------------"
HTTPS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/health || echo "000")
if [ "$HTTPS_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ PASS${NC}: HTTPS accessible (Status: 200)"
elif [ "$HTTPS_STATUS" = "000" ]; then
    echo -e "${RED}❌ FAIL${NC}: HTTPS not accessible"
    echo "Fix: Check SSL certificate, ensure nginx SSL config is correct"
else
    echo -e "${YELLOW}⚠️  WARNING${NC}: Unexpected status code: $HTTPS_STATUS"
fi

# Test 4: Certificate Validity
echo ""
echo "Test 4: SSL Certificate Validity"
echo "----------------------------------------"
CERT_OUTPUT=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ PASS${NC}: Certificate valid"
    echo "$CERT_OUTPUT"
else
    echo -e "${RED}❌ FAIL${NC}: Certificate invalid or not found"
    echo "Fix: Run init-ssl.sh to generate certificate"
fi

# Test 5: Certificate Issuer
echo ""
echo "Test 5: Certificate Issuer (Let's Encrypt)"
echo "----------------------------------------"
ISSUER=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -issuer 2>/dev/null | grep "Let's Encrypt")
if [ -n "$ISSUER" ]; then
    echo -e "${GREEN}✅ PASS${NC}: Certificate issued by Let's Encrypt"
else
    echo -e "${YELLOW}⚠️  WARNING${NC}: Certificate not from Let's Encrypt"
    echo "Issuer: $(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -issuer 2>/dev/null)"
fi

# Test 6: TLS Versions
echo ""
echo "Test 6: TLS Protocol Support"
echo "----------------------------------------"
TLS13=$(echo | openssl s_client -tls1_3 -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | grep "Protocol" | grep "TLSv1.3")
TLS12=$(echo | openssl s_client -tls1_2 -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | grep "Protocol" | grep "TLSv1.2")

if [ -n "$TLS13" ]; then
    echo -e "${GREEN}✅ PASS${NC}: TLS 1.3 supported"
else
    echo -e "${YELLOW}⚠️  WARNING${NC}: TLS 1.3 not supported"
fi

if [ -n "$TLS12" ]; then
    echo -e "${GREEN}✅ PASS${NC}: TLS 1.2 supported"
else
    echo -e "${RED}❌ FAIL${NC}: TLS 1.2 not supported (required)"
fi

# Test 7: Security Headers
echo ""
echo "Test 7: Security Headers"
echo "----------------------------------------"
HEADERS=$(curl -sI https://$DOMAIN/health)

if echo "$HEADERS" | grep -q "Strict-Transport-Security"; then
    echo -e "${GREEN}✅ PASS${NC}: HSTS header present"
else
    echo -e "${YELLOW}⚠️  WARNING${NC}: HSTS header missing (recommended)"
fi

if echo "$HEADERS" | grep -q "X-Content-Type-Options"; then
    echo -e "${GREEN}✅ PASS${NC}: X-Content-Type-Options header present"
else
    echo -e "${YELLOW}⚠️  WARNING${NC}: X-Content-Type-Options header missing"
fi

if echo "$HEADERS" | grep -q "X-Frame-Options"; then
    echo -e "${GREEN}✅ PASS${NC}: X-Frame-Options header present"
else
    echo -e "${YELLOW}⚠️  WARNING${NC}: X-Frame-Options header missing"
fi

# Test 8: All Service Endpoints
echo ""
echo "Test 8: Service Endpoint Accessibility"
echo "----------------------------------------"
ENDPOINTS=("/api/" "/n8n/" "/portainer/" "/grafana/" "/chat/" "/flowise/" "/mcp/")

for ENDPOINT in "${ENDPOINTS[@]}"; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN$ENDPOINT || echo "000")
    if [ "$STATUS" = "200" ] || [ "$STATUS" = "301" ] || [ "$STATUS" = "302" ] || [ "$STATUS" = "401" ] || [ "$STATUS" = "403" ]; then
        echo -e "${GREEN}✅${NC} $ENDPOINT (Status: $STATUS)"
    else
        echo -e "${RED}❌${NC} $ENDPOINT (Status: $STATUS)"
    fi
done

# Summary
echo ""
echo "========================================"
echo "Test Summary"
echo "========================================"
echo "Manual verification recommended:"
echo "  1. SSL Labs Test: https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
echo "  2. Security Headers: https://securityheaders.com/?q=https://$DOMAIN"
echo "  3. Browser Test: Open https://$DOMAIN/health in browser"
echo ""
echo "Expected SSL Labs Grade: A or A+"
echo "Expected Security Headers Grade: A or higher"
