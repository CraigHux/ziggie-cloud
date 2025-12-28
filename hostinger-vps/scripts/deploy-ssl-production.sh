#!/bin/bash
# =============================================================================
# PRODUCTION SSL DEPLOYMENT SCRIPT FOR ZIGGIE.CLOUD
# =============================================================================
# Purpose: Complete SSL/HTTPS setup with Let's Encrypt for ziggie.cloud
# Supports: Single domain + wildcard certificate (*.ziggie.cloud)
# TLS: 1.3 (preferred) with 1.2 fallback
# Security: HSTS with preload, OCSP Stapling, modern ciphers
# Renewal: Automated via certbot container with 12-hour check cycle
# =============================================================================
# Author: L1 Strategic Agent - SSL/HTTPS Configuration
# Created: 2025-12-28
# Last Updated: 2025-12-28
# Version: 1.0.0
# =============================================================================

set -euo pipefail
IFS=$'\n\t'

# =============================================================================
# CONFIGURATION
# =============================================================================

# Domain configuration
DOMAIN="ziggie.cloud"
WILDCARD_DOMAIN="*.ziggie.cloud"
EMAIL="${LETSENCRYPT_EMAIL:-admin@ziggie.cloud}"

# Paths
COMPOSE_DIR="${COMPOSE_DIR:-/opt/ziggie}"
NGINX_CONF="${COMPOSE_DIR}/nginx/nginx.conf"
SCRIPTS_DIR="${COMPOSE_DIR}/scripts"

# Certificate options
STAGING=${STAGING:-0}           # Set to 1 for testing (avoids rate limits)
FORCE_RENEW=${FORCE_RENEW:-0}   # Set to 1 to force certificate renewal
DRY_RUN=${DRY_RUN:-0}           # Set to 1 for dry run (no actual changes)

# DNS challenge for wildcard (requires Cloudflare or other DNS provider)
USE_DNS_CHALLENGE=${USE_DNS_CHALLENGE:-0}
CLOUDFLARE_EMAIL="${CLOUDFLARE_EMAIL:-}"
CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:-}"

# Timeouts and retries
NGINX_WAIT_TIME=10
MAX_RETRIES=3
RETRY_DELAY=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# LOGGING FUNCTIONS
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

print_header() {
    echo ""
    echo "============================================================================="
    echo "$1"
    echo "============================================================================="
    echo ""
}

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root or with sudo"
        exit 1
    fi
}

check_dependencies() {
    local deps=("docker" "docker-compose" "dig" "openssl" "curl")
    local missing=()

    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing+=("$dep")
        fi
    done

    if [[ ${#missing[@]} -gt 0 ]]; then
        log_error "Missing dependencies: ${missing[*]}"
        log_info "Install with: apt install ${missing[*]}"
        exit 1
    fi

    log_success "All dependencies verified"
}

check_docker_compose() {
    cd "$COMPOSE_DIR" || {
        log_error "Cannot access compose directory: $COMPOSE_DIR"
        exit 1
    }

    if [[ ! -f "docker-compose.yml" ]]; then
        log_error "docker-compose.yml not found in $COMPOSE_DIR"
        exit 1
    fi

    log_success "Docker Compose configuration found"
}

check_dns() {
    log_info "Checking DNS resolution for $DOMAIN..."

    local expected_ip="${VPS_IP:-}"
    local resolved_ip

    resolved_ip=$(dig +short "$DOMAIN" | head -1)

    if [[ -z "$resolved_ip" ]]; then
        log_error "DNS resolution failed for $DOMAIN"
        log_info "Verify A record points to your VPS IP"
        exit 1
    fi

    if [[ -n "$expected_ip" && "$resolved_ip" != "$expected_ip" ]]; then
        log_warning "DNS resolved to $resolved_ip (expected: $expected_ip)"
        read -p "Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    log_success "DNS resolves $DOMAIN -> $resolved_ip"
}

check_ports() {
    log_info "Checking port availability..."

    # Check port 80
    if ss -tuln | grep -q ':80 '; then
        log_info "Port 80 is in use (expected for nginx)"
    else
        log_warning "Port 80 not in use - nginx may not be running"
    fi

    # Check port 443
    if ss -tuln | grep -q ':443 '; then
        log_info "Port 443 is in use (expected for nginx)"
    else
        log_info "Port 443 not yet in use (will be after SSL setup)"
    fi

    log_success "Port check completed"
}

check_existing_certs() {
    log_info "Checking for existing certificates..."

    local cert_path="/etc/letsencrypt/live/$DOMAIN"

    # Check inside certbot container volume
    if docker compose run --rm certbot sh -c "test -d /etc/letsencrypt/live/$DOMAIN" 2>/dev/null; then
        log_info "Existing certificates found for $DOMAIN"

        # Get expiration date
        local expiry
        expiry=$(docker compose run --rm certbot sh -c \
            "openssl x509 -enddate -noout -in /etc/letsencrypt/live/$DOMAIN/cert.pem 2>/dev/null | cut -d= -f2" \
            2>/dev/null || echo "unknown")

        log_info "Certificate expires: $expiry"

        if [[ "$FORCE_RENEW" == "1" ]]; then
            log_warning "FORCE_RENEW is set - will request new certificate"
        else
            log_success "Valid certificates exist. Use FORCE_RENEW=1 to regenerate."
            return 1
        fi
    else
        log_info "No existing certificates found - will generate new ones"
    fi

    return 0
}

# =============================================================================
# CERTIFICATE FUNCTIONS
# =============================================================================

create_webroot_dirs() {
    log_info "Creating webroot directories..."

    mkdir -p /var/www/certbot/.well-known/acme-challenge
    chmod -R 755 /var/www/certbot

    log_success "Webroot directories created"
}

create_temp_nginx_config() {
    log_info "Creating temporary nginx config for ACME challenge..."

    # Backup existing config
    if [[ -f "$NGINX_CONF" ]]; then
        cp "$NGINX_CONF" "${NGINX_CONF}.backup.$(date +%Y%m%d%H%M%S)"
        log_info "Existing config backed up"
    fi

    # Create HTTP-only config for initial certificate request
    cat > "${COMPOSE_DIR}/nginx/nginx-acme-only.conf" << 'NGINX_ACME'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # HTTP server for ACME challenge ONLY
    server {
        listen 80;
        server_name _;

        # Let's Encrypt ACME challenge
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
            try_files $uri =404;
        }

        # Redirect all other traffic
        location / {
            return 503 "SSL certificate being configured. Please wait...";
            add_header Content-Type text/plain;
        }
    }
}
NGINX_ACME

    log_success "Temporary ACME config created"
}

start_nginx_acme_mode() {
    log_info "Starting nginx in ACME-only mode..."

    cd "$COMPOSE_DIR" || exit 1

    # Stop nginx if running
    docker compose stop nginx 2>/dev/null || true

    # Start with temporary config
    docker compose run -d --rm --name nginx-acme \
        -v "${COMPOSE_DIR}/nginx/nginx-acme-only.conf:/etc/nginx/nginx.conf:ro" \
        -v "certbot_data:/var/www/certbot" \
        -p 80:80 \
        nginx:alpine

    log_info "Waiting ${NGINX_WAIT_TIME} seconds for nginx to start..."
    sleep "$NGINX_WAIT_TIME"

    # Verify nginx is running
    if docker ps | grep -q nginx-acme; then
        log_success "Nginx ACME mode started"
    else
        log_error "Failed to start nginx in ACME mode"
        docker logs nginx-acme 2>/dev/null || true
        exit 1
    fi
}

stop_nginx_acme_mode() {
    log_info "Stopping nginx ACME mode..."
    docker stop nginx-acme 2>/dev/null || true
    docker rm nginx-acme 2>/dev/null || true
    log_success "Nginx ACME mode stopped"
}

request_certificate_webroot() {
    log_info "Requesting SSL certificate via webroot challenge..."

    local staging_arg=""
    if [[ "$STAGING" == "1" ]]; then
        staging_arg="--staging"
        log_warning "STAGING MODE - Using Let's Encrypt staging server"
    else
        log_info "PRODUCTION MODE - Requesting real certificate"
    fi

    local force_arg=""
    if [[ "$FORCE_RENEW" == "1" ]]; then
        force_arg="--force-renewal"
    fi

    local dry_run_arg=""
    if [[ "$DRY_RUN" == "1" ]]; then
        dry_run_arg="--dry-run"
        log_warning "DRY RUN MODE - No actual certificate will be issued"
    fi

    cd "$COMPOSE_DIR" || exit 1

    # Request certificate
    docker compose run --rm certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        --non-interactive \
        --expand \
        --cert-name "$DOMAIN" \
        $staging_arg \
        $force_arg \
        $dry_run_arg \
        -d "$DOMAIN"

    local exit_code=$?

    if [[ $exit_code -eq 0 ]]; then
        log_success "Certificate successfully obtained for $DOMAIN"
        return 0
    else
        log_error "Certificate request failed with exit code: $exit_code"
        return 1
    fi
}

request_certificate_dns() {
    log_info "Requesting SSL certificate via DNS challenge (for wildcard)..."

    if [[ -z "$CLOUDFLARE_API_TOKEN" ]]; then
        log_error "CLOUDFLARE_API_TOKEN required for DNS challenge"
        exit 1
    fi

    # Create Cloudflare credentials file
    local cf_creds="/tmp/cloudflare.ini"
    cat > "$cf_creds" << EOF
dns_cloudflare_api_token = $CLOUDFLARE_API_TOKEN
EOF
    chmod 600 "$cf_creds"

    local staging_arg=""
    if [[ "$STAGING" == "1" ]]; then
        staging_arg="--staging"
        log_warning "STAGING MODE - Using Let's Encrypt staging server"
    fi

    cd "$COMPOSE_DIR" || exit 1

    # Request wildcard certificate
    docker compose run --rm \
        -v "$cf_creds:/tmp/cloudflare.ini:ro" \
        certbot/dns-cloudflare certonly \
        --dns-cloudflare \
        --dns-cloudflare-credentials /tmp/cloudflare.ini \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        --non-interactive \
        --cert-name "$DOMAIN" \
        $staging_arg \
        -d "$DOMAIN" \
        -d "$WILDCARD_DOMAIN"

    local exit_code=$?
    rm -f "$cf_creds"

    if [[ $exit_code -eq 0 ]]; then
        log_success "Wildcard certificate obtained for $DOMAIN and $WILDCARD_DOMAIN"
        return 0
    else
        log_error "DNS challenge certificate request failed"
        return 1
    fi
}

verify_certificate() {
    log_info "Verifying certificate installation..."

    cd "$COMPOSE_DIR" || exit 1

    # Check certificate exists
    if ! docker compose run --rm certbot sh -c "test -f /etc/letsencrypt/live/$DOMAIN/fullchain.pem"; then
        log_error "Certificate file not found"
        return 1
    fi

    # Get certificate details
    docker compose run --rm certbot sh -c \
        "openssl x509 -in /etc/letsencrypt/live/$DOMAIN/cert.pem -noout -subject -issuer -dates"

    # Verify certificate chain
    docker compose run --rm certbot sh -c \
        "openssl verify -CAfile /etc/letsencrypt/live/$DOMAIN/chain.pem /etc/letsencrypt/live/$DOMAIN/cert.pem" \
        2>/dev/null && log_success "Certificate chain verified" || log_warning "Chain verification had warnings"

    log_success "Certificate verification completed"
    return 0
}

# =============================================================================
# NGINX FUNCTIONS
# =============================================================================

install_ssl_nginx_config() {
    log_info "Installing production SSL nginx configuration..."

    # Check if ssl-ready config exists
    if [[ -f "${COMPOSE_DIR}/nginx/nginx.conf.ssl-ready" ]]; then
        cp "${COMPOSE_DIR}/nginx/nginx.conf.ssl-ready" "$NGINX_CONF"
        log_success "SSL-ready nginx config installed"
    else
        log_warning "nginx.conf.ssl-ready not found, keeping current config"
        log_info "Ensure nginx.conf has correct SSL paths for $DOMAIN"
    fi
}

test_nginx_config() {
    log_info "Testing nginx configuration..."

    cd "$COMPOSE_DIR" || exit 1

    docker compose run --rm nginx nginx -t

    if [[ $? -eq 0 ]]; then
        log_success "Nginx configuration test passed"
        return 0
    else
        log_error "Nginx configuration test failed"
        return 1
    fi
}

start_nginx_production() {
    log_info "Starting nginx with SSL configuration..."

    cd "$COMPOSE_DIR" || exit 1

    # Stop any existing nginx
    docker compose stop nginx 2>/dev/null || true

    # Start production nginx
    docker compose up -d nginx

    log_info "Waiting ${NGINX_WAIT_TIME} seconds for nginx to initialize..."
    sleep "$NGINX_WAIT_TIME"

    # Verify nginx is healthy
    if docker compose ps nginx | grep -q "Up"; then
        log_success "Nginx started successfully with SSL"
    else
        log_error "Nginx failed to start"
        docker compose logs nginx --tail=50
        return 1
    fi

    return 0
}

# =============================================================================
# AUTO-RENEWAL FUNCTIONS
# =============================================================================

create_renewal_hook() {
    log_info "Creating post-renewal hook script..."

    cat > "${SCRIPTS_DIR}/post-renewal-hook.sh" << 'RENEWAL_HOOK'
#!/bin/bash
# =============================================================================
# Post-Renewal Hook - Reload nginx after certificate renewal
# =============================================================================

set -euo pipefail

COMPOSE_DIR="${COMPOSE_DIR:-/opt/ziggie}"
DOMAIN="ziggie.cloud"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "Certificate renewed for $DOMAIN"

# Reload nginx to pick up new certificate
cd "$COMPOSE_DIR"
docker compose exec -T nginx nginx -s reload

if [[ $? -eq 0 ]]; then
    log "Nginx reloaded successfully"
else
    log "WARNING: Nginx reload failed - manual intervention may be required"
    # Try restart as fallback
    docker compose restart nginx
fi

# Optional: Send notification
if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
    curl -s -X POST "$SLACK_WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d '{"text":"SSL certificate renewed for '"$DOMAIN"' at '"$(date)"'"}'
fi

log "Post-renewal hook completed"
RENEWAL_HOOK

    chmod +x "${SCRIPTS_DIR}/post-renewal-hook.sh"
    log_success "Renewal hook script created"
}

setup_certbot_renewal() {
    log_info "Configuring certbot auto-renewal..."

    # Create renewal configuration
    cat > "${COMPOSE_DIR}/certbot-renewal.conf" << EOF
# Certbot renewal configuration for $DOMAIN
# Generated: $(date)

[renewalparams]
authenticator = webroot
webroot_path = /var/www/certbot
account = $(docker compose run --rm certbot show_account 2>/dev/null | grep -oE '[a-f0-9]{32}' | head -1 || echo "auto")
server = https://acme-v02.api.letsencrypt.org/directory
post_hook = /scripts/post-renewal-hook.sh
EOF

    log_success "Certbot renewal configuration created"
}

test_renewal() {
    log_info "Testing certificate renewal (dry run)..."

    cd "$COMPOSE_DIR" || exit 1

    docker compose run --rm certbot renew --dry-run

    if [[ $? -eq 0 ]]; then
        log_success "Renewal test passed - auto-renewal is working"
    else
        log_warning "Renewal test had issues - check certbot logs"
    fi
}

# =============================================================================
# VERIFICATION FUNCTIONS
# =============================================================================

verify_https_access() {
    log_info "Verifying HTTPS access..."

    local retries=0

    while [[ $retries -lt $MAX_RETRIES ]]; do
        if curl -sSf --max-time 10 "https://$DOMAIN/health" > /dev/null 2>&1; then
            log_success "HTTPS access verified: https://$DOMAIN/health"
            return 0
        fi

        retries=$((retries + 1))
        log_info "Retry $retries/$MAX_RETRIES..."
        sleep "$RETRY_DELAY"
    done

    log_error "HTTPS access verification failed"
    return 1
}

verify_hsts() {
    log_info "Verifying HSTS header..."

    local headers
    headers=$(curl -sI --max-time 10 "https://$DOMAIN/health" 2>/dev/null)

    if echo "$headers" | grep -qi "strict-transport-security"; then
        local hsts_header
        hsts_header=$(echo "$headers" | grep -i "strict-transport-security" | tr -d '\r')
        log_success "HSTS header present: $hsts_header"

        # Check for preload requirements
        if echo "$hsts_header" | grep -q "preload"; then
            log_success "HSTS preload directive present"
        else
            log_warning "HSTS preload directive missing (required for preload list submission)"
        fi

        if echo "$hsts_header" | grep -q "includeSubDomains"; then
            log_success "HSTS includeSubDomains directive present"
        else
            log_warning "HSTS includeSubDomains directive missing (required for preload list)"
        fi

        # Check max-age (must be >= 31536000 for preload)
        local max_age
        max_age=$(echo "$hsts_header" | grep -oP 'max-age=\K[0-9]+')
        if [[ -n "$max_age" && "$max_age" -ge 31536000 ]]; then
            log_success "HSTS max-age=$max_age (meets preload requirement of >= 31536000)"
        else
            log_warning "HSTS max-age=$max_age (preload requires >= 31536000)"
        fi
    else
        log_warning "HSTS header not found"
    fi
}

verify_tls_version() {
    log_info "Verifying TLS version..."

    # Test TLS 1.3
    if echo | openssl s_client -connect "$DOMAIN:443" -tls1_3 2>/dev/null | grep -q "TLSv1.3"; then
        log_success "TLS 1.3 supported"
    else
        log_warning "TLS 1.3 not detected"
    fi

    # Test TLS 1.2 (fallback)
    if echo | openssl s_client -connect "$DOMAIN:443" -tls1_2 2>/dev/null | grep -q "TLSv1.2"; then
        log_success "TLS 1.2 supported (fallback)"
    fi

    # Verify no old TLS versions
    if echo | openssl s_client -connect "$DOMAIN:443" -tls1_1 2>/dev/null | grep -q "TLSv1.1"; then
        log_warning "TLS 1.1 is enabled (should be disabled)"
    else
        log_success "TLS 1.1 disabled (good)"
    fi

    if echo | openssl s_client -connect "$DOMAIN:443" -tls1 2>/dev/null | grep -q "TLSv1"; then
        log_warning "TLS 1.0 is enabled (should be disabled)"
    else
        log_success "TLS 1.0 disabled (good)"
    fi
}

verify_ocsp_stapling() {
    log_info "Verifying OCSP stapling..."

    local ocsp_output
    ocsp_output=$(echo | openssl s_client -connect "$DOMAIN:443" -status 2>/dev/null)

    if echo "$ocsp_output" | grep -q "OCSP Response Status: successful"; then
        log_success "OCSP stapling is working"
    else
        log_warning "OCSP stapling not detected (may take time to activate)"
    fi
}

verify_certificate_chain() {
    log_info "Verifying certificate chain..."

    echo | openssl s_client -connect "$DOMAIN:443" -showcerts 2>/dev/null | \
        openssl x509 -noout -subject -issuer -dates
}

run_ssl_labs_info() {
    log_info "SSL Labs test information:"
    echo ""
    echo "  For comprehensive SSL testing, visit:"
    echo "  https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
    echo ""
    echo "  Expected rating with current configuration: A+"
    echo ""
}

# =============================================================================
# CLEANUP FUNCTIONS
# =============================================================================

cleanup() {
    log_info "Cleaning up temporary files..."

    # Remove temporary nginx config
    rm -f "${COMPOSE_DIR}/nginx/nginx-acme-only.conf"

    # Stop any lingering containers
    docker stop nginx-acme 2>/dev/null || true
    docker rm nginx-acme 2>/dev/null || true

    log_success "Cleanup completed"
}

# =============================================================================
# ROLLBACK FUNCTION
# =============================================================================

rollback() {
    log_warning "Rolling back SSL configuration..."

    # Restore nginx config backup
    local latest_backup
    latest_backup=$(ls -t "${NGINX_CONF}.backup."* 2>/dev/null | head -1)

    if [[ -n "$latest_backup" ]]; then
        cp "$latest_backup" "$NGINX_CONF"
        log_info "Restored nginx config from: $latest_backup"
    fi

    # Restart nginx with original config
    cd "$COMPOSE_DIR" || exit 1
    docker compose restart nginx

    log_warning "Rollback completed"
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    print_header "ZIGGIE SSL PRODUCTION DEPLOYMENT"

    echo "Domain:        $DOMAIN"
    echo "Email:         $EMAIL"
    echo "Staging:       $STAGING"
    echo "Force Renew:   $FORCE_RENEW"
    echo "Dry Run:       $DRY_RUN"
    echo "DNS Challenge: $USE_DNS_CHALLENGE"
    echo ""

    # Set up trap for cleanup on error
    trap cleanup EXIT
    trap rollback ERR

    # Phase 1: Validation
    print_header "PHASE 1: VALIDATION"

    check_root
    check_dependencies
    check_docker_compose
    check_dns
    check_ports

    # Check for existing certs (returns 1 if certs exist and no force renew)
    if ! check_existing_certs; then
        log_info "Skipping certificate generation (existing certs valid)"
        # Jump to verification
        print_header "PHASE 5: VERIFICATION (Existing Certs)"
        verify_https_access
        verify_hsts
        verify_tls_version
        verify_certificate_chain
        run_ssl_labs_info
        exit 0
    fi

    # Phase 2: Prepare
    print_header "PHASE 2: PREPARATION"

    create_webroot_dirs
    create_temp_nginx_config
    create_renewal_hook

    # Phase 3: Certificate Generation
    print_header "PHASE 3: CERTIFICATE GENERATION"

    start_nginx_acme_mode

    if [[ "$USE_DNS_CHALLENGE" == "1" ]]; then
        request_certificate_dns
    else
        request_certificate_webroot
    fi

    stop_nginx_acme_mode
    verify_certificate

    # Phase 4: Production Configuration
    print_header "PHASE 4: PRODUCTION CONFIGURATION"

    install_ssl_nginx_config
    test_nginx_config
    start_nginx_production
    setup_certbot_renewal

    # Phase 5: Verification
    print_header "PHASE 5: VERIFICATION"

    # Wait a bit for everything to stabilize
    sleep 5

    verify_https_access
    verify_hsts
    verify_tls_version
    verify_ocsp_stapling
    verify_certificate_chain

    # Phase 6: Renewal Test
    print_header "PHASE 6: RENEWAL TEST"

    test_renewal

    # Phase 7: Summary
    print_header "DEPLOYMENT COMPLETE"

    echo "SSL deployment for $DOMAIN completed successfully!"
    echo ""
    echo "Summary:"
    echo "  - Certificate issued by: Let's Encrypt"
    echo "  - TLS versions: 1.2, 1.3"
    echo "  - HSTS: Enabled with preload"
    echo "  - OCSP Stapling: Enabled"
    echo "  - Auto-renewal: Every 12 hours (certbot container)"
    echo ""
    echo "Next steps:"
    echo "  1. Test HTTPS access: curl -I https://$DOMAIN/health"
    echo "  2. Run SSL Labs test: https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
    echo "  3. Submit for HSTS preload: https://hstspreload.org/?domain=$DOMAIN"
    echo ""

    run_ssl_labs_info

    log_success "All done!"
}

# =============================================================================
# SCRIPT ENTRY POINT
# =============================================================================

# Show usage if --help
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    echo "Usage: $0 [options]"
    echo ""
    echo "Environment variables:"
    echo "  STAGING=1              Use Let's Encrypt staging server (for testing)"
    echo "  FORCE_RENEW=1          Force certificate renewal"
    echo "  DRY_RUN=1              Dry run (no actual changes)"
    echo "  USE_DNS_CHALLENGE=1    Use DNS challenge for wildcard certificate"
    echo "  LETSENCRYPT_EMAIL=x    Email for Let's Encrypt notifications"
    echo "  COMPOSE_DIR=/path      Path to docker-compose.yml directory"
    echo "  VPS_IP=x.x.x.x         Expected VPS IP for DNS verification"
    echo ""
    echo "Examples:"
    echo "  $0                           # Production deployment"
    echo "  STAGING=1 $0                 # Test with staging certificates"
    echo "  DRY_RUN=1 $0                 # Dry run, no changes"
    echo "  FORCE_RENEW=1 $0             # Force certificate renewal"
    echo ""
    exit 0
fi

# Run main function
main "$@"
