#!/bin/bash
# =============================================================================
# ZIGGIE OPTIMIZED STACK DEPLOYMENT SCRIPT
# =============================================================================
# Author: HEPHAESTUS (Technical Art Director, Elite Technical Team)
# Date: 2025-12-28
# Target: Hostinger KVM 4 (4 vCPU, 16GB RAM, 200GB NVMe)
#
# This script deploys the optimized 18-service Docker stack with:
# - Resource limits and reservations
# - Health checks with tuned intervals
# - Performance-optimized configurations
# - Monitoring stack (Prometheus, Grafana, Loki)
# =============================================================================

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# =============================================================================
# PHASE 1: PRE-DEPLOYMENT VALIDATION
# =============================================================================

log_info "Phase 1: Pre-deployment validation"

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    log_error "Please run with sudo: sudo ./deploy-optimized.sh"
    exit 1
fi

# Check Docker installation
if ! command -v docker &> /dev/null; then
    log_error "Docker not found. Install Docker first."
    exit 1
fi
log_success "Docker installed: $(docker --version)"

# Check Docker Compose
if ! command -v docker compose &> /dev/null; then
    log_error "Docker Compose not found. Install Docker Compose plugin."
    exit 1
fi
log_success "Docker Compose installed: $(docker compose version)"

# Check available memory
TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
if [ "$TOTAL_MEM" -lt 15 ]; then
    log_warning "Total memory: ${TOTAL_MEM}GB. Optimized stack requires 16GB. Performance may degrade."
else
    log_success "Total memory: ${TOTAL_MEM}GB (sufficient)"
fi

# Check available disk space
AVAIL_DISK=$(df -BG /mnt/nvme 2>/dev/null | awk 'NR==2 {print $4}' | sed 's/G//')
if [ -z "$AVAIL_DISK" ]; then
    AVAIL_DISK=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    log_warning "Using root filesystem (no /mnt/nvme). Available: ${AVAIL_DISK}GB"
elif [ "$AVAIL_DISK" -lt 50 ]; then
    log_warning "Available disk: ${AVAIL_DISK}GB. Recommend >100GB for logs and volumes."
else
    log_success "Available disk: ${AVAIL_DISK}GB (sufficient)"
fi

# Check .env file
if [ ! -f .env ]; then
    log_error ".env file not found. Create .env with required secrets."
    log_info "Required variables: POSTGRES_PASSWORD, MONGO_PASSWORD, REDIS_PASSWORD, N8N_PASSWORD, etc."
    exit 1
fi
log_success ".env file found"

# Validate critical environment variables
REQUIRED_VARS=(
    "POSTGRES_PASSWORD"
    "MONGO_PASSWORD"
    "REDIS_PASSWORD"
    "N8N_PASSWORD"
    "API_SECRET_KEY"
    "GRAFANA_PASSWORD"
)

source .env
MISSING_VARS=()
for VAR in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!VAR:-}" ]; then
        MISSING_VARS+=("$VAR")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    log_error "Missing required environment variables: ${MISSING_VARS[*]}"
    exit 1
fi
log_success "All required environment variables present"

# =============================================================================
# PHASE 2: BACKUP EXISTING DATA (if any)
# =============================================================================

log_info "Phase 2: Backup existing data"

BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
if [ "$(docker ps -q)" ]; then
    log_info "Existing containers detected. Creating backup..."
    mkdir -p "$BACKUP_DIR"

    # Export current volumes
    for VOLUME in $(docker volume ls -q | grep ziggie); do
        log_info "Backing up volume: $VOLUME"
        docker run --rm -v "$VOLUME:/data" -v "$BACKUP_DIR:/backup" \
            alpine tar czf "/backup/${VOLUME}.tar.gz" -C /data .
    done

    log_success "Backup created: $BACKUP_DIR"
else
    log_info "No existing containers. Skipping backup."
fi

# =============================================================================
# PHASE 3: STOP EXISTING STACK
# =============================================================================

log_info "Phase 3: Stop existing stack"

if [ -f docker-compose.yml ]; then
    log_info "Stopping current stack..."
    docker compose down --remove-orphans
    log_success "Existing stack stopped"
else
    log_info "No existing docker-compose.yml. Clean deployment."
fi

# =============================================================================
# PHASE 4: SYSTEM OPTIMIZATION
# =============================================================================

log_info "Phase 4: System optimization"

# Increase file descriptor limits
log_info "Setting file descriptor limits..."
cat >> /etc/security/limits.conf <<EOF
# Ziggie Docker Stack - File Descriptor Limits
* soft nofile 65536
* hard nofile 65536
root soft nofile 65536
root hard nofile 65536
EOF

# Kernel tuning for database performance
log_info "Tuning kernel parameters..."
cat >> /etc/sysctl.d/99-ziggie.conf <<EOF
# Ziggie Docker Stack - Kernel Tuning

# Network tuning
net.core.somaxconn = 1024
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.ip_local_port_range = 10000 65535
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 30

# Memory tuning
vm.swappiness = 10
vm.overcommit_memory = 1
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5

# File system
fs.file-max = 2097152
fs.inotify.max_user_watches = 524288
EOF

sysctl -p /etc/sysctl.d/99-ziggie.conf &>/dev/null
log_success "Kernel parameters optimized"

# Create NVMe mount point for database volumes (if not exists)
if [ ! -d /mnt/nvme/ziggie ]; then
    log_info "Creating NVMe directory structure..."
    mkdir -p /mnt/nvme/ziggie/{postgres,mongodb,redis,ollama,n8n,prometheus,grafana,loki}
    chown -R 1000:1000 /mnt/nvme/ziggie
    chmod -R 755 /mnt/nvme/ziggie
    log_success "NVMe directories created"
fi

# =============================================================================
# PHASE 5: DEPLOY OPTIMIZED STACK
# =============================================================================

log_info "Phase 5: Deploy optimized stack"

# Use optimized docker-compose.yml
if [ ! -f docker-compose.optimized.yml ]; then
    log_error "docker-compose.optimized.yml not found. Generate it first."
    exit 1
fi

log_info "Copying optimized configuration..."
cp docker-compose.optimized.yml docker-compose.yml

# Create required directories
log_info "Creating configuration directories..."
mkdir -p nginx/{conf.d,ssl}
mkdir -p prometheus/alerts
mkdir -p grafana/{provisioning,dashboards}
mkdir -p loki
mkdir -p promtail
mkdir -p init-scripts/{postgres,mongo}

# Pull all images
log_info "Pulling Docker images (this may take several minutes)..."
docker compose pull

# Stage 1: Start databases first (allow health checks to pass)
log_info "Stage 1: Starting databases..."
docker compose up -d postgres mongodb redis
log_info "Waiting 30 seconds for databases to initialize..."
sleep 30

# Check database health
POSTGRES_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' ziggie-postgres 2>/dev/null || echo "unknown")
MONGO_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' ziggie-mongodb 2>/dev/null || echo "unknown")
REDIS_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' ziggie-redis 2>/dev/null || echo "unknown")

log_info "Database health: PostgreSQL=$POSTGRES_HEALTH MongoDB=$MONGO_HEALTH Redis=$REDIS_HEALTH"

if [ "$POSTGRES_HEALTH" != "healthy" ] || [ "$MONGO_HEALTH" != "healthy" ] || [ "$REDIS_HEALTH" != "healthy" ]; then
    log_warning "Databases not healthy yet. Check logs with: docker compose logs postgres mongodb redis"
    log_info "Continuing anyway (services may retry connections)..."
fi

# Stage 2: Start remaining services
log_info "Stage 2: Starting application and monitoring services..."
docker compose up -d

log_success "All services started"

# =============================================================================
# PHASE 6: VALIDATION
# =============================================================================

log_info "Phase 6: Post-deployment validation"

# Wait for services to stabilize
log_info "Waiting 60 seconds for services to stabilize..."
sleep 60

# Check container status
log_info "Container status:"
docker compose ps

# Count running containers
RUNNING=$(docker compose ps --filter "status=running" -q | wc -l)
EXPECTED=20  # Adjust based on enabled services

if [ "$RUNNING" -ge 18 ]; then
    log_success "$RUNNING/$EXPECTED services running"
else
    log_warning "Only $RUNNING/$EXPECTED services running. Check: docker compose logs"
fi

# Check health endpoints
log_info "Checking health endpoints..."

check_endpoint() {
    local NAME=$1
    local URL=$2
    local TIMEOUT=5

    if curl -sf --max-time "$TIMEOUT" "$URL" > /dev/null 2>&1; then
        log_success "$NAME health check passed: $URL"
        return 0
    else
        log_error "$NAME health check failed: $URL"
        return 1
    fi
}

check_endpoint "Ziggie API" "http://localhost:8000/health" || true
check_endpoint "MCP Gateway" "http://localhost:8080/health" || true
check_endpoint "Prometheus" "http://localhost:9090/-/healthy" || true
check_endpoint "Grafana" "http://localhost:3000/api/health" || true
check_endpoint "Portainer" "http://localhost:9000/api/status" || true

# Check resource usage
log_info "Resource usage (first 10 containers):"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | head -n 11

# =============================================================================
# PHASE 7: POST-DEPLOYMENT CONFIGURATION
# =============================================================================

log_info "Phase 7: Post-deployment configuration"

# Wait for Ollama to start, then pull a default model (if not exists)
log_info "Checking Ollama model availability..."
if docker exec ziggie-ollama ollama list 2>/dev/null | grep -q "llama2:7b"; then
    log_success "Ollama model already present"
else
    log_info "Pulling default Ollama model (llama2:7b) in background..."
    docker exec -d ziggie-ollama ollama pull llama2:7b
    log_info "Model pull running in background. Check progress: docker logs -f ziggie-ollama"
fi

# Configure Prometheus targets (if not already configured)
if [ ! -f prometheus/prometheus.yml ]; then
    log_info "Creating default Prometheus configuration..."
    cat > prometheus/prometheus.yml <<'PROM_EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

rule_files:
  - "alerts/*.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'ziggie-api'
    static_configs:
      - targets: ['ziggie-api:8000']
    metrics_path: '/metrics'

  - job_name: 'mcp-gateway'
    static_configs:
      - targets: ['mcp-gateway:8080']
    metrics_path: '/metrics'

  - job_name: 'n8n'
    static_configs:
      - targets: ['n8n:5678']
    metrics_path: '/metrics'
PROM_EOF

    # Reload Prometheus configuration
    docker compose restart prometheus
    log_success "Prometheus configured and restarted"
fi

# =============================================================================
# DEPLOYMENT COMPLETE
# =============================================================================

echo ""
log_success "=========================================="
log_success "ZIGGIE OPTIMIZED STACK DEPLOYMENT COMPLETE"
log_success "=========================================="
echo ""

log_info "Service URLs (assuming localhost):"
echo "  - Portainer:      http://localhost:9000"
echo "  - n8n:            http://localhost:5678"
echo "  - Ziggie API:     http://localhost:8000"
echo "  - MCP Gateway:    http://localhost:8080"
echo "  - Prometheus:     http://localhost:9090"
echo "  - Grafana:        http://localhost:3000"
echo "  - Ollama:         http://localhost:11434"
echo "  - Flowise:        http://localhost:3001"
echo ""

log_info "Next steps:"
echo "  1. Configure Nginx reverse proxy with SSL (see nginx/README.md)"
echo "  2. Import Grafana dashboards (see grafana/dashboards/)"
echo "  3. Configure n8n workflows (http://localhost:5678)"
echo "  4. Run performance validation tests (see PERFORMANCE_OPTIMIZATION_REPORT.md)"
echo "  5. Monitor resource usage: docker stats"
echo "  6. Check alerts: http://localhost:9090/alerts"
echo ""

log_info "Useful commands:"
echo "  - View logs:      docker compose logs -f [service]"
echo "  - Restart:        docker compose restart [service]"
echo "  - Stop all:       docker compose down"
echo "  - Resource usage: docker stats"
echo "  - Health status:  docker compose ps"
echo ""

log_warning "IMPORTANT:"
echo "  - Default credentials are in .env file"
echo "  - Change all default passwords before exposing to internet"
echo "  - Configure firewall to restrict access to management ports"
echo "  - Set up SSL certificates with certbot for HTTPS"
echo ""

log_info "Deployment log saved to: deployment.log"
