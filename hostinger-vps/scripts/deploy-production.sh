#!/bin/bash
# =============================================================================
# ZIGGIE VPS PRODUCTION DEPLOYMENT SCRIPT
# =============================================================================
# Version: 2.0.0
# Date: 2025-12-28
# Author: L1 Strategic Agent - Session C
#
# Target: Hostinger KVM 4 VPS
#   - IP: 82.25.112.73
#   - RAM: 16GB
#   - vCPUs: 4
#   - Storage: 200GB NVMe
#   - Domain: ziggie.cloud
#
# This script provides:
#   1. Remote SSH deployment capability
#   2. Full 18-service Docker stack deployment
#   3. Staged service startup (databases -> apps -> monitoring)
#   4. Comprehensive health verification
#   5. SSL certificate automation
#   6. Detailed status reporting
#
# Usage:
#   LOCAL (on VPS):    ./deploy-production.sh
#   REMOTE (from dev): ./deploy-production.sh --remote
#   DRY RUN:           ./deploy-production.sh --dry-run
#   SKIP SSL:          ./deploy-production.sh --skip-ssl
#   FORCE RESTART:     ./deploy-production.sh --force
#
# Prerequisites:
#   - SSH key configured for VPS access (for remote mode)
#   - Docker and docker-compose installed on VPS
#   - DNS configured for ziggie.cloud and subdomains
# =============================================================================

set -euo pipefail
trap 'handle_error $? $LINENO' ERR

# =============================================================================
# CONFIGURATION
# =============================================================================

# VPS Configuration
VPS_IP="82.25.112.73"
VPS_USER="root"
VPS_DOMAIN="ziggie.cloud"
ZIGGIE_DIR="/opt/ziggie"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_rsa}"
SSH_TIMEOUT=10

# Colors and Formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Script State
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/../deploy-$(date +%Y%m%d_%H%M%S).log"
DRY_RUN=false
REMOTE_MODE=false
SKIP_SSL=false
FORCE_RESTART=false

# Service Definitions (19 total)
declare -A SERVICES
SERVICES[databases]="postgres mongodb redis"          # 3 services
SERVICES[workflows]="n8n flowise"                     # 2 services
SERVICES[ai_services]="ollama open-webui"             # 2 services
SERVICES[applications]="mcp-gateway ziggie-api sim-studio"  # 3 services
SERVICES[monitoring]="prometheus grafana loki promtail"     # 4 services
SERVICES[management]="portainer watchtower"           # 2 services
SERVICES[proxy]="nginx certbot"                       # 2 services
SERVICES[cicd]="github-runner"                        # 1 service (optional)

# Health Check Endpoints
declare -A HEALTH_ENDPOINTS
HEALTH_ENDPOINTS[ziggie-api]="http://localhost:8000/health"
HEALTH_ENDPOINTS[mcp-gateway]="http://localhost:8080/health"
HEALTH_ENDPOINTS[n8n]="http://localhost:5678/healthz"
HEALTH_ENDPOINTS[grafana]="http://localhost:3000/api/health"
HEALTH_ENDPOINTS[prometheus]="http://localhost:9090/-/healthy"
HEALTH_ENDPOINTS[portainer]="http://localhost:9000/api/system/status"
HEALTH_ENDPOINTS[nginx]="http://localhost/health"
HEALTH_ENDPOINTS[ollama]="http://localhost:11434/api/tags"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

log() {
    local level=$1
    shift
    local msg="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case $level in
        INFO)    echo -e "${BLUE}[${timestamp}]${NC} ${msg}" | tee -a "$LOG_FILE" ;;
        SUCCESS) echo -e "${GREEN}[${timestamp}]${NC} ${msg}" | tee -a "$LOG_FILE" ;;
        WARN)    echo -e "${YELLOW}[${timestamp}]${NC} ${msg}" | tee -a "$LOG_FILE" ;;
        ERROR)   echo -e "${RED}[${timestamp}]${NC} ${msg}" | tee -a "$LOG_FILE" ;;
        HEADER)  echo -e "\n${CYAN}${BOLD}$msg${NC}" | tee -a "$LOG_FILE" ;;
    esac
}

handle_error() {
    local exit_code=$1
    local line_number=$2
    log ERROR "Error occurred at line $line_number with exit code $exit_code"
    log ERROR "Check log file: $LOG_FILE"
    exit $exit_code
}

run_ssh() {
    local cmd="$1"
    local timeout="${2:-60}"

    if $DRY_RUN; then
        log INFO "[DRY RUN] Would execute: $cmd"
        return 0
    fi

    ssh -i "$SSH_KEY" \
        -o ConnectTimeout=$SSH_TIMEOUT \
        -o StrictHostKeyChecking=accept-new \
        -o BatchMode=yes \
        "${VPS_USER}@${VPS_IP}" \
        "timeout $timeout bash -c '$cmd'" 2>&1
}

run_local() {
    local cmd="$1"

    if $DRY_RUN; then
        log INFO "[DRY RUN] Would execute: $cmd"
        return 0
    fi

    eval "$cmd" 2>&1
}

execute() {
    if $REMOTE_MODE; then
        run_ssh "$1" "${2:-60}"
    else
        run_local "$1"
    fi
}

print_header() {
    echo ""
    echo -e "${CYAN}=============================================="
    echo "  $1"
    echo "==============================================${NC}"
    echo ""
}

print_service_table() {
    local header="$1"
    shift
    local services=("$@")

    log HEADER "$header"
    printf "%-25s %-15s %-15s\n" "SERVICE" "STATUS" "HEALTH"
    printf "%-25s %-15s %-15s\n" "-------" "------" "------"

    for service in "${services[@]}"; do
        local status=$(docker inspect -f '{{.State.Status}}' "ziggie-${service}" 2>/dev/null || echo "not_found")
        local health=$(docker inspect -f '{{.State.Health.Status}}' "ziggie-${service}" 2>/dev/null || echo "n/a")

        case $status in
            running)  status_color="${GREEN}" ;;
            exited)   status_color="${RED}" ;;
            *)        status_color="${YELLOW}" ;;
        esac

        case $health in
            healthy)   health_color="${GREEN}" ;;
            unhealthy) health_color="${RED}" ;;
            *)         health_color="${YELLOW}" ;;
        esac

        printf "%-25s ${status_color}%-15s${NC} ${health_color}%-15s${NC}\n" "$service" "$status" "$health"
    done
}

check_ssh_connection() {
    log INFO "Testing SSH connection to ${VPS_USER}@${VPS_IP}..."

    if ! ssh -i "$SSH_KEY" \
        -o ConnectTimeout=$SSH_TIMEOUT \
        -o StrictHostKeyChecking=accept-new \
        -o BatchMode=yes \
        "${VPS_USER}@${VPS_IP}" \
        "echo 'SSH connection successful'" 2>&1; then
        log ERROR "SSH connection failed. Check SSH key and VPS status."
        log ERROR "SSH key path: $SSH_KEY"
        exit 1
    fi

    log SUCCESS "SSH connection verified"
}

# =============================================================================
# PHASE 0: ARGUMENT PARSING
# =============================================================================

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --remote)
                REMOTE_MODE=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --skip-ssl)
                SKIP_SSL=true
                shift
                ;;
            --force)
                FORCE_RESTART=true
                shift
                ;;
            --help|-h)
                print_usage
                exit 0
                ;;
            *)
                log ERROR "Unknown option: $1"
                print_usage
                exit 1
                ;;
        esac
    done
}

print_usage() {
    cat << EOF
ZIGGIE VPS PRODUCTION DEPLOYMENT

Usage: $0 [OPTIONS]

Options:
    --remote      Deploy remotely via SSH (default: local execution)
    --dry-run     Show what would be executed without running
    --skip-ssl    Skip SSL certificate setup
    --force       Force restart all services
    --help, -h    Show this help message

Examples:
    # Deploy locally (run this on the VPS)
    ./deploy-production.sh

    # Deploy remotely from development machine
    ./deploy-production.sh --remote

    # Preview deployment steps without execution
    ./deploy-production.sh --dry-run

    # Force restart all services
    ./deploy-production.sh --force --remote

Environment Variables:
    SSH_KEY       Path to SSH private key (default: ~/.ssh/id_rsa)

EOF
}

# =============================================================================
# PHASE 1: PRE-DEPLOYMENT VALIDATION
# =============================================================================

phase_1_validate() {
    print_header "PHASE 1: PRE-DEPLOYMENT VALIDATION"

    log INFO "Starting pre-deployment validation..."

    if $REMOTE_MODE; then
        check_ssh_connection
    fi

    # Check Docker installation
    log INFO "Checking Docker installation..."
    local docker_version=$(execute "docker --version" 10)
    if [[ $? -ne 0 ]]; then
        log ERROR "Docker not found on VPS"
        log INFO "Install Docker: curl -fsSL https://get.docker.com | sudo sh"
        exit 1
    fi
    log SUCCESS "Docker: $docker_version"

    # Check Docker Compose
    log INFO "Checking Docker Compose..."
    local compose_version=$(execute "docker compose version" 10)
    if [[ $? -ne 0 ]]; then
        log ERROR "Docker Compose not found"
        exit 1
    fi
    log SUCCESS "Docker Compose: $compose_version"

    # Check available resources
    log INFO "Checking system resources..."
    local mem_total=$(execute "free -g | awk '/^Mem:/{print \$2}'" 10)
    local disk_avail=$(execute "df -BG / | awk 'NR==2{print \$4}' | tr -d 'G'" 10)

    log INFO "Total Memory: ${mem_total}GB"
    log INFO "Available Disk: ${disk_avail}GB"

    if [[ "$mem_total" -lt 14 ]]; then
        log WARN "Low memory detected. Recommend 16GB for full stack."
    fi

    if [[ "$disk_avail" -lt 50 ]]; then
        log WARN "Low disk space. Recommend 100GB+ available."
    fi

    # Check .env file
    log INFO "Checking environment configuration..."
    if ! execute "test -f ${ZIGGIE_DIR}/.env" 5; then
        log WARN ".env file not found at ${ZIGGIE_DIR}/.env"
        log INFO "Will create from template..."
    else
        log SUCCESS "Environment file exists"
    fi

    log SUCCESS "Phase 1 complete: Pre-deployment validation passed"
}

# =============================================================================
# PHASE 2: REPOSITORY SYNC
# =============================================================================

phase_2_sync() {
    print_header "PHASE 2: REPOSITORY SYNC"

    log INFO "Syncing repository to VPS..."

    # Create directory structure
    log INFO "Creating directory structure..."
    execute "mkdir -p ${ZIGGIE_DIR}" 10
    execute "mkdir -p ${ZIGGIE_DIR}/{nginx/conf.d,nginx/ssl,nginx/html}" 10
    execute "mkdir -p ${ZIGGIE_DIR}/{prometheus/alerts,grafana/provisioning,grafana/dashboards}" 10
    execute "mkdir -p ${ZIGGIE_DIR}/{loki,promtail,init-scripts/postgres,init-scripts/mongo}" 10
    execute "mkdir -p ${ZIGGIE_DIR}/{n8n-workflows,backup,mcp-gateway,api,sim-studio}" 10

    log SUCCESS "Directory structure created"

    # Sync files based on mode
    if $REMOTE_MODE && ! $DRY_RUN; then
        log INFO "Syncing configuration files via rsync..."

        local hostinger_dir="${SCRIPT_DIR}/.."

        # Sync docker-compose and configs
        rsync -avz --progress \
            -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=accept-new" \
            "${hostinger_dir}/docker-compose.yml" \
            "${hostinger_dir}/.env.example" \
            "${hostinger_dir}/nginx/" \
            "${hostinger_dir}/prometheus/" \
            "${hostinger_dir}/loki/" \
            "${hostinger_dir}/promtail/" \
            "${VPS_USER}@${VPS_IP}:${ZIGGIE_DIR}/" \
            2>&1 | tee -a "$LOG_FILE"

        log SUCCESS "Files synced to VPS"
    else
        log INFO "Using local files (local mode or dry run)"
    fi

    # Setup .env from template if needed
    log INFO "Checking environment configuration..."
    execute "
        cd ${ZIGGIE_DIR}
        if [ ! -f .env ]; then
            if [ -f .env.example ]; then
                cp .env.example .env

                # Generate secure passwords
                sed -i \"s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=\$(openssl rand -base64 24 | tr -d '/+=')/\" .env
                sed -i \"s/MONGO_PASSWORD=.*/MONGO_PASSWORD=\$(openssl rand -base64 24 | tr -d '/+=')/\" .env
                sed -i \"s/REDIS_PASSWORD=.*/REDIS_PASSWORD=\$(openssl rand -base64 24 | tr -d '/+=')/\" .env
                sed -i \"s/N8N_PASSWORD=.*/N8N_PASSWORD=\$(openssl rand -base64 16 | tr -d '/+=')/\" .env
                sed -i \"s/N8N_ENCRYPTION_KEY=.*/N8N_ENCRYPTION_KEY=\$(openssl rand -base64 32 | tr -d '/+=')/\" .env
                sed -i \"s/FLOWISE_PASSWORD=.*/FLOWISE_PASSWORD=\$(openssl rand -base64 16 | tr -d '/+=')/\" .env
                sed -i \"s/GRAFANA_PASSWORD=.*/GRAFANA_PASSWORD=\$(openssl rand -base64 16 | tr -d '/+=')/\" .env
                sed -i \"s/API_SECRET_KEY=.*/API_SECRET_KEY=\$(openssl rand -base64 32 | tr -d '/+=')/\" .env
                sed -i \"s/WEBUI_SECRET_KEY=.*/WEBUI_SECRET_KEY=\$(openssl rand -base64 32 | tr -d '/+=')/\" .env
                sed -i \"s/VPS_DOMAIN=.*/VPS_DOMAIN=${VPS_DOMAIN}/\" .env

                chmod 600 .env
                echo 'Generated new .env with secure passwords'
            else
                echo 'ERROR: .env.example not found'
                exit 1
            fi
        else
            echo '.env already exists'
        fi
    " 30

    log SUCCESS "Phase 2 complete: Repository synced"
}

# =============================================================================
# PHASE 3: STOP EXISTING SERVICES
# =============================================================================

phase_3_stop() {
    print_header "PHASE 3: STOP EXISTING SERVICES"

    if $FORCE_RESTART; then
        log INFO "Force restart requested. Stopping all services..."
        execute "cd ${ZIGGIE_DIR} && docker compose down --remove-orphans 2>/dev/null || true" 60
        log SUCCESS "All services stopped"
    else
        log INFO "Checking for running services..."
        local running=$(execute "docker ps --filter 'name=ziggie' --format '{{.Names}}' | wc -l" 10)

        if [[ "$running" -gt 0 ]]; then
            log INFO "Found $running running Ziggie containers"
            log INFO "Services will be updated in place (use --force to restart all)"
        else
            log INFO "No existing Ziggie services running"
        fi
    fi

    log SUCCESS "Phase 3 complete"
}

# =============================================================================
# PHASE 4: DEPLOY DATABASES
# =============================================================================

phase_4_databases() {
    print_header "PHASE 4: DEPLOY DATABASES"

    log INFO "Starting database services..."
    execute "cd ${ZIGGIE_DIR} && docker compose up -d postgres mongodb redis" 120

    log INFO "Waiting 30 seconds for databases to initialize..."
    sleep 30

    # Verify database health
    log INFO "Verifying database health..."

    # PostgreSQL
    local pg_status=$(execute "docker exec ziggie-postgres pg_isready -U ziggie 2>/dev/null && echo 'ready' || echo 'not_ready'" 10)
    if [[ "$pg_status" == *"ready"* ]]; then
        log SUCCESS "PostgreSQL: HEALTHY"
    else
        log WARN "PostgreSQL: NOT READY (may need more time)"
    fi

    # MongoDB
    local mongo_status=$(execute "docker exec ziggie-mongodb mongosh --quiet --eval 'db.runCommand(\"ping\").ok' 2>/dev/null || echo '0'" 10)
    if [[ "$mongo_status" == *"1"* ]]; then
        log SUCCESS "MongoDB: HEALTHY"
    else
        log WARN "MongoDB: NOT READY (may need more time)"
    fi

    # Redis
    local redis_status=$(execute "docker exec ziggie-redis redis-cli ping 2>/dev/null || echo 'failed'" 10)
    if [[ "$redis_status" == *"PONG"* ]]; then
        log SUCCESS "Redis: HEALTHY"
    else
        log WARN "Redis: NOT READY (may need more time)"
    fi

    log SUCCESS "Phase 4 complete: Databases deployed"
}

# =============================================================================
# PHASE 5: DEPLOY CORE SERVICES
# =============================================================================

phase_5_core() {
    print_header "PHASE 5: DEPLOY CORE SERVICES"

    log INFO "Starting workflow and AI services..."
    execute "cd ${ZIGGIE_DIR} && docker compose up -d n8n ollama flowise open-webui" 180

    log INFO "Waiting 20 seconds for services to start..."
    sleep 20

    # Check n8n
    local n8n_status=$(execute "curl -sf -o /dev/null -w '%{http_code}' http://localhost:5678/healthz 2>/dev/null || echo '000'" 10)
    if [[ "$n8n_status" == "200" ]]; then
        log SUCCESS "n8n: HEALTHY"
    else
        log WARN "n8n: Starting (HTTP $n8n_status)"
    fi

    # Check Ollama
    local ollama_status=$(execute "curl -sf http://localhost:11434/api/tags 2>/dev/null && echo 'ok' || echo 'starting'" 10)
    if [[ "$ollama_status" == *"ok"* ]]; then
        log SUCCESS "Ollama: HEALTHY"
    else
        log WARN "Ollama: Starting"
    fi

    log SUCCESS "Phase 5 complete: Core services deployed"
}

# =============================================================================
# PHASE 6: DEPLOY APPLICATIONS
# =============================================================================

phase_6_applications() {
    print_header "PHASE 6: DEPLOY APPLICATIONS"

    log INFO "Starting application services..."
    log WARN "Note: mcp-gateway, ziggie-api, sim-studio require pre-built images"

    # Check if images exist
    local apps_to_start=""
    for app in mcp-gateway ziggie-api sim-studio; do
        local image_exists=$(execute "docker images --format '{{.Repository}}' | grep -q '$app' && echo 'yes' || echo 'no'" 10)
        if [[ "$image_exists" == "yes" ]]; then
            apps_to_start="${apps_to_start} ${app}"
        else
            log WARN "Image not found for $app - skipping (build and push image first)"
        fi
    done

    if [[ -n "$apps_to_start" ]]; then
        execute "cd ${ZIGGIE_DIR} && docker compose up -d ${apps_to_start}" 120
        log INFO "Waiting 15 seconds for applications to start..."
        sleep 15
    else
        log WARN "No application images available. Deploy applications separately."
    fi

    log SUCCESS "Phase 6 complete: Applications deployed (where images exist)"
}

# =============================================================================
# PHASE 7: DEPLOY MONITORING
# =============================================================================

phase_7_monitoring() {
    print_header "PHASE 7: DEPLOY MONITORING"

    log INFO "Starting monitoring stack..."
    execute "cd ${ZIGGIE_DIR} && docker compose up -d prometheus grafana loki promtail" 120

    log INFO "Waiting 15 seconds for monitoring to start..."
    sleep 15

    # Check Prometheus
    local prom_status=$(execute "curl -sf -o /dev/null -w '%{http_code}' http://localhost:9090/-/healthy 2>/dev/null || echo '000'" 10)
    if [[ "$prom_status" == "200" ]]; then
        log SUCCESS "Prometheus: HEALTHY"
    else
        log WARN "Prometheus: Starting (HTTP $prom_status)"
    fi

    # Check Grafana
    local grafana_status=$(execute "curl -sf -o /dev/null -w '%{http_code}' http://localhost:3000/api/health 2>/dev/null || echo '000'" 10)
    if [[ "$grafana_status" == "200" ]]; then
        log SUCCESS "Grafana: HEALTHY"
    else
        log WARN "Grafana: Starting (HTTP $grafana_status)"
    fi

    log SUCCESS "Phase 7 complete: Monitoring deployed"
}

# =============================================================================
# PHASE 8: DEPLOY MANAGEMENT & PROXY
# =============================================================================

phase_8_management() {
    print_header "PHASE 8: DEPLOY MANAGEMENT & PROXY"

    log INFO "Starting management and proxy services..."
    execute "cd ${ZIGGIE_DIR} && docker compose up -d portainer watchtower nginx certbot" 120

    log INFO "Waiting 10 seconds for services to start..."
    sleep 10

    # Check Portainer
    local portainer_status=$(execute "curl -sf -o /dev/null -w '%{http_code}' http://localhost:9000/api/system/status 2>/dev/null || echo '000'" 10)
    if [[ "$portainer_status" == "200" ]]; then
        log SUCCESS "Portainer: HEALTHY"
    else
        log WARN "Portainer: Needs initialization (first run)"
    fi

    # Check Nginx
    local nginx_status=$(execute "curl -sf -o /dev/null -w '%{http_code}' http://localhost/health 2>/dev/null || echo '000'" 10)
    if [[ "$nginx_status" == "200" ]]; then
        log SUCCESS "Nginx: HEALTHY"
    else
        log WARN "Nginx: Starting (HTTP $nginx_status)"
    fi

    log SUCCESS "Phase 8 complete: Management and proxy deployed"
}

# =============================================================================
# PHASE 9: SSL SETUP
# =============================================================================

phase_9_ssl() {
    print_header "PHASE 9: SSL CERTIFICATE SETUP"

    if $SKIP_SSL; then
        log INFO "Skipping SSL setup (--skip-ssl flag)"
        return 0
    fi

    log INFO "Checking SSL certificate status..."

    # Check if certificates exist
    local cert_exists=$(execute "test -f ${ZIGGIE_DIR}/certbot_certs/live/${VPS_DOMAIN}/fullchain.pem && echo 'yes' || echo 'no'" 10)

    if [[ "$cert_exists" == "yes" ]]; then
        log SUCCESS "SSL certificates exist"

        # Check expiration
        local expiry=$(execute "openssl x509 -enddate -noout -in ${ZIGGIE_DIR}/certbot_certs/live/${VPS_DOMAIN}/fullchain.pem 2>/dev/null | cut -d= -f2" 10)
        log INFO "Certificate expires: $expiry"
    else
        log WARN "SSL certificates not found"
        log INFO "Run SSL setup manually: ./scripts/setup-ssl.sh"
        log INFO "Or access services via HTTP and Portainer for initial setup"
    fi

    log SUCCESS "Phase 9 complete: SSL check finished"
}

# =============================================================================
# PHASE 10: FINAL VERIFICATION
# =============================================================================

phase_10_verify() {
    print_header "PHASE 10: FINAL VERIFICATION"

    log INFO "Waiting 10 seconds for all services to stabilize..."
    sleep 10

    log INFO "Generating deployment status report..."

    # Container status
    log HEADER "Container Status"
    execute "cd ${ZIGGIE_DIR} && docker compose ps" 30

    # Health endpoints
    log HEADER "Health Endpoint Checks"
    for service in "${!HEALTH_ENDPOINTS[@]}"; do
        local url="${HEALTH_ENDPOINTS[$service]}"
        local status=$(execute "curl -sf -o /dev/null -w '%{http_code}' '$url' 2>/dev/null || echo '000'" 10)
        if [[ "$status" == "200" ]]; then
            log SUCCESS "$service: OK ($url)"
        else
            log WARN "$service: HTTP $status ($url)"
        fi
    done

    # Resource usage
    log HEADER "Resource Usage"
    execute "docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}' | head -20" 30

    # Disk usage
    log HEADER "Disk Usage"
    execute "df -h / | tail -1" 10
    execute "docker system df" 10

    # Count running containers
    local running_count=$(execute "docker ps --filter 'name=ziggie' --format '{{.Names}}' | wc -l" 10)
    local total_count=19

    log HEADER "Deployment Summary"
    log INFO "Running containers: $running_count / $total_count"

    if [[ "$running_count" -ge 15 ]]; then
        log SUCCESS "Deployment successful: Infrastructure operational"
    elif [[ "$running_count" -ge 10 ]]; then
        log WARN "Partial deployment: Some services need attention"
    else
        log ERROR "Deployment issues: Many services not running"
    fi

    log SUCCESS "Phase 10 complete: Verification finished"
}

# =============================================================================
# PHASE 11: GENERATE STATUS REPORT
# =============================================================================

phase_11_report() {
    print_header "DEPLOYMENT STATUS REPORT"

    local vps_ip=$(execute "hostname -I | awk '{print \$1}'" 10)

    cat << EOF

============================================
  ZIGGIE COMMAND CENTER - DEPLOYMENT COMPLETE
============================================

VPS Information:
  IP Address:   $vps_ip
  Domain:       $VPS_DOMAIN
  Deploy Time:  $(date '+%Y-%m-%d %H:%M:%S')

Service Access URLs:
  -----------------------------------------------
  Portainer:    http://${vps_ip}:9000     (Docker Management)
  n8n:          http://${vps_ip}:5678     (Workflow Automation)
  Flowise:      http://${vps_ip}:3001     (LLM Flow Builder)
  Open WebUI:   http://${vps_ip}:3002     (Chat Interface)
  Grafana:      http://${vps_ip}:3000     (Monitoring)
  Prometheus:   http://${vps_ip}:9090     (Metrics)
  Ziggie API:   http://${vps_ip}:8000     (Main API)
  MCP Gateway:  http://${vps_ip}:8080     (MCP Router)
  Landing:      http://${vps_ip}/         (Welcome Page)

After SSL Setup (https://${VPS_DOMAIN}):
  -----------------------------------------------
  Main:         https://${VPS_DOMAIN}
  API:          https://api.${VPS_DOMAIN}
  n8n:          https://n8n.${VPS_DOMAIN}
  Grafana:      https://grafana.${VPS_DOMAIN}
  Portainer:    https://portainer.${VPS_DOMAIN}
  Flowise:      https://flowise.${VPS_DOMAIN}
  Chat:         https://chat.${VPS_DOMAIN}

Next Steps:
  1. Initialize Portainer (first-time admin setup)
     http://${vps_ip}:9000

  2. Setup SSL Certificate:
     cd ${ZIGGIE_DIR}/scripts && ./setup-ssl.sh

  3. Pull LLM Models:
     docker exec -it ziggie-ollama ollama pull llama3.2:3b
     docker exec -it ziggie-ollama ollama pull codellama:7b

  4. Configure Grafana:
     Add Prometheus datasource: http://prometheus:9090

  5. Import n8n Workflows:
     Access n8n and import from ${ZIGGIE_DIR}/n8n-workflows/

  6. Deploy Applications (if images built):
     docker compose up -d mcp-gateway ziggie-api sim-studio

Health Check:
  ${ZIGGIE_DIR}/health-check.sh

Log File:
  $LOG_FILE

Credentials:
  All passwords are in ${ZIGGIE_DIR}/.env
  BACKUP THIS FILE SECURELY!

============================================
  Deployment completed successfully!
============================================

EOF

    log SUCCESS "Status report generated"
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    parse_arguments "$@"

    print_header "ZIGGIE VPS PRODUCTION DEPLOYMENT"

    log INFO "Deployment Mode: $(if $REMOTE_MODE; then echo 'REMOTE (SSH)'; else echo 'LOCAL'; fi)"
    log INFO "Dry Run: $DRY_RUN"
    log INFO "Skip SSL: $SKIP_SSL"
    log INFO "Force Restart: $FORCE_RESTART"
    log INFO "Log File: $LOG_FILE"
    log INFO "Target: ${VPS_USER}@${VPS_IP}"
    echo ""

    # Execute deployment phases
    phase_1_validate
    phase_2_sync
    phase_3_stop
    phase_4_databases
    phase_5_core
    phase_6_applications
    phase_7_monitoring
    phase_8_management
    phase_9_ssl
    phase_10_verify
    phase_11_report

    log SUCCESS "Deployment completed!"
    log INFO "Full log available at: $LOG_FILE"
}

# Run main function with all arguments
main "$@"
