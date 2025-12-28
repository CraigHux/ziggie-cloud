#!/bin/bash
# =============================================================================
# ZIGGIE COMMAND CENTER - VPS Deployment Script
# =============================================================================
# Run this script after provisioning your Hostinger VPS with Docker
# Usage: ./deploy.sh
# =============================================================================

set -e  # Exit on error

echo "=============================================="
echo "  ZIGGIE COMMAND CENTER - VPS DEPLOYMENT"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# -----------------------------------------------------------------------------
# STEP 1: Check prerequisites
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[1/8] Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker not found. Please select 'Docker' from Hostinger Applications.${NC}"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}Docker Compose not found. Installing...${NC}"
    sudo apt-get update && sudo apt-get install -y docker-compose-plugin
fi

echo -e "${GREEN}Prerequisites OK${NC}"

# -----------------------------------------------------------------------------
# STEP 2: Create directory structure
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[2/8] Creating directory structure...${NC}"

sudo mkdir -p /opt/ziggie
sudo chown -R $USER:$USER /opt/ziggie
cd /opt/ziggie

mkdir -p nginx/conf.d nginx/ssl
mkdir -p prometheus alerts
mkdir -p grafana/provisioning grafana/dashboards
mkdir -p loki promtail
mkdir -p mcp-gateway api sim-studio
mkdir -p init-scripts/postgres init-scripts/mongo
mkdir -p n8n-workflows

echo -e "${GREEN}Directories created${NC}"

# -----------------------------------------------------------------------------
# STEP 3: Check for .env file
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[3/8] Checking environment configuration...${NC}"

if [ ! -f .env ]; then
    echo -e "${RED}.env file not found!${NC}"
    echo "Creating from template..."

    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}Please edit .env with your actual values:${NC}"
        echo "  nano /opt/ziggie/.env"
        exit 1
    else
        echo -e "${RED}.env.example not found. Please upload configuration files.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}Environment configured${NC}"

# -----------------------------------------------------------------------------
# STEP 4: Generate secure passwords if needed
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[4/8] Checking passwords...${NC}"

if grep -q "CHANGE_ME" .env; then
    echo -e "${YELLOW}Generating secure passwords...${NC}"

    # Generate random passwords
    POSTGRES_PW=$(openssl rand -base64 24 | tr -d '/+=')
    MONGO_PW=$(openssl rand -base64 24 | tr -d '/+=')
    REDIS_PW=$(openssl rand -base64 24 | tr -d '/+=')
    N8N_PW=$(openssl rand -base64 16 | tr -d '/+=')
    N8N_KEY=$(openssl rand -base64 32 | tr -d '/+=')
    FLOWISE_PW=$(openssl rand -base64 16 | tr -d '/+=')
    GRAFANA_PW=$(openssl rand -base64 16 | tr -d '/+=')
    API_KEY=$(openssl rand -base64 32 | tr -d '/+=')
    WEBUI_KEY=$(openssl rand -base64 32 | tr -d '/+=')

    # Update .env file
    sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PW/" .env
    sed -i "s/MONGO_PASSWORD=.*/MONGO_PASSWORD=$MONGO_PW/" .env
    sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$REDIS_PW/" .env
    sed -i "s/N8N_PASSWORD=.*/N8N_PASSWORD=$N8N_PW/" .env
    sed -i "s/N8N_ENCRYPTION_KEY=.*/N8N_ENCRYPTION_KEY=$N8N_KEY/" .env
    sed -i "s/FLOWISE_PASSWORD=.*/FLOWISE_PASSWORD=$FLOWISE_PW/" .env
    sed -i "s/GRAFANA_PASSWORD=.*/GRAFANA_PASSWORD=$GRAFANA_PW/" .env
    sed -i "s/API_SECRET_KEY=.*/API_SECRET_KEY=$API_KEY/" .env
    sed -i "s/WEBUI_SECRET_KEY=.*/WEBUI_SECRET_KEY=$WEBUI_KEY/" .env

    echo -e "${GREEN}Passwords generated and saved to .env${NC}"
    echo -e "${YELLOW}IMPORTANT: Save these credentials securely!${NC}"
fi

# -----------------------------------------------------------------------------
# STEP 5: Create minimal configs
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[5/8] Creating configuration files...${NC}"

# Prometheus config
cat > prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'ziggie-api'
    static_configs:
      - targets: ['ziggie-api:8000']

  - job_name: 'n8n'
    static_configs:
      - targets: ['n8n:5678']

  - job_name: 'mcp-gateway'
    static_configs:
      - targets: ['mcp-gateway:8080']
EOF

# Loki config
cat > loki/loki-config.yml << 'EOF'
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/boltdb-shipper-active
    cache_location: /loki/boltdb-shipper-cache
    shared_store: filesystem
  filesystem:
    directory: /loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
EOF

# Promtail config
cat > promtail/promtail-config.yml << 'EOF'
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: containers
    static_configs:
      - targets:
          - localhost
        labels:
          job: containerlogs
          __path__: /var/lib/docker/containers/*/*log
EOF

# Postgres init script for multiple databases
cat > init-scripts/postgres/init-databases.sh << 'EOF'
#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE n8n;
    CREATE DATABASE simstudio;
    GRANT ALL PRIVILEGES ON DATABASE n8n TO ziggie;
    GRANT ALL PRIVILEGES ON DATABASE simstudio TO ziggie;
EOSQL
EOF
chmod +x init-scripts/postgres/init-databases.sh

echo -e "${GREEN}Configuration files created${NC}"

# -----------------------------------------------------------------------------
# STEP 6: Pull Docker images
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[6/8] Pulling Docker images (this may take a while)...${NC}"

docker compose pull

echo -e "${GREEN}Images pulled${NC}"

# -----------------------------------------------------------------------------
# STEP 7: Start services
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[7/8] Starting services...${NC}"

# Start core services first
docker compose up -d postgres mongodb redis
echo "Waiting for databases to be ready..."
sleep 15

# Start remaining services
docker compose up -d

echo -e "${GREEN}Services started${NC}"

# -----------------------------------------------------------------------------
# STEP 8: Verify deployment
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[8/8] Verifying deployment...${NC}"

sleep 10

echo "Container Status:"
docker compose ps

echo ""
echo -e "${GREEN}=============================================="
echo "  DEPLOYMENT COMPLETE!"
echo "==============================================${NC}"
echo ""
echo "Access your services at:"
echo "  Portainer:  http://$(hostname -I | awk '{print $1}'):9000"
echo "  n8n:        http://$(hostname -I | awk '{print $1}'):5678"
echo "  Flowise:    http://$(hostname -I | awk '{print $1}'):3001"
echo "  Open WebUI: http://$(hostname -I | awk '{print $1}'):3002"
echo "  Grafana:    http://$(hostname -I | awk '{print $1}'):3000"
echo "  Ziggie API: http://$(hostname -I | awk '{print $1}'):8000"
echo ""
echo "Next steps:"
echo "  1. Configure your domain DNS to point to this VPS"
echo "  2. Run: certbot --nginx -d yourdomain.com"
echo "  3. Pull LLM models: docker exec -it ziggie-ollama ollama pull llama2"
echo "  4. Access Portainer to manage containers visually"
echo ""
echo -e "${YELLOW}Credentials saved in: /opt/ziggie/.env${NC}"
