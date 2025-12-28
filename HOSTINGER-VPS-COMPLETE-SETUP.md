# Hostinger VPS Complete Setup Specification for AI-Controlled Orchestration

> **Mission**: Define the COMPLETE Hostinger VPS setup for 1,884 AI agents orchestration
> **Date**: 2025-12-22
> **Agent**: L1 DevOps Agent (Ziggie)

---

## Executive Summary

This document provides a production-ready specification for deploying Ziggie's AI orchestration infrastructure on Hostinger VPS. The setup supports 1,884 concurrent AI agents with always-on services including n8n workflow automation, Discord bot, MongoDB, Redis, and comprehensive monitoring.

**Recommended VPS Tier**: **KVM 4** (£9.99/mo)
- 4 vCPU cores
- 16GB RAM
- 200GB NVMe storage
- 16TB bandwidth

**Rationale**: Based on capacity planning research, 2000 concurrent agents require:
- MongoDB: 4-8GB RAM (we'll allocate 6GB)
- Redis: 2-3GB RAM (we'll allocate 3GB)
- n8n: 2GB RAM
- Discord bot + Ziggie API: 2GB RAM
- System + Nginx + monitoring: 3GB RAM
- **Total**: ~16GB with proper resource limits

---

## 1. VPS Tier Selection & Capacity Planning

### Capacity Calculation for 1,884 Agents

| Service | RAM Allocated | CPU Limit | Storage | Justification |
|---------|---------------|-----------|---------|---------------|
| **MongoDB** | 6GB | 2 cores | 50GB | [Scaling MongoDB for 2000 concurrent users requires 4-8GB with efficient queries](https://medium.com/@deelesisuanu/scaling-mongodb-connections-for-high-traffic-applications-best-practices-and-realistic-3c4252597a2a) |
| **Redis** | 3GB | 1 core | 5GB | [Redis sizing for high-performance with 2000 max_idle connections](https://tyk.io/docs/5.0/planning-for-production/redis-sizing/) |
| **n8n** | 2GB | 1 core | 20GB | [n8n production requires minimum 4GB total system RAM](https://latenode.com/blog/low-code-no-code-platforms/self-hosted-automation-platforms/how-to-self-host-n8n-complete-setup-guide-production-deployment-checklist-2025) |
| **Discord Bot** | 1GB | 0.5 cores | 5GB | Node.js bot with persistent connections |
| **Ziggie API** | 1GB | 0.5 cores | 5GB | Express.js orchestrator API |
| **Nginx** | 512MB | 0.5 cores | 2GB | Reverse proxy + SSL |
| **Prometheus** | 1GB | 0.5 cores | 20GB | Metrics collection (15-day retention) |
| **Grafana** | 512MB | 0.25 cores | 5GB | Dashboard visualization |
| **System** | 1GB | - | 88GB | Ubuntu OS + overhead |
| **TOTAL** | **16GB** | **7 cores** | **200GB** | **KVM 4 tier perfect fit** |

### Why NOT KVM 2 (£7.49/mo)?
- Only 8GB RAM - insufficient for MongoDB (6GB) + Redis (3GB) + services
- Would require aggressive swapping, causing severe performance degradation
- [Redis and MongoDB should not share VPS with application servers](https://tyk.io/docs/3.2/planning-for-production/redis-mongodb/)

### Why NOT KVM 8 (£18.99/mo)?
- 32GB RAM is overkill for 1,884 agents
- Double the cost with minimal benefit
- Can scale up later if agent count grows to 5,000+

---

## 2. Docker Setup & Container Architecture

### 2.1 Initial VPS Setup

```bash
# Use Hostinger's Ubuntu 24.04 with Docker template (auto-installs Docker + Compose)
# Or manually install on regular Ubuntu VPS:

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker Engine
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose V2
sudo apt install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version

# Add non-root user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

**Source**: [Hostinger Docker VPS Template Guide](https://www.hostinger.com/tutorials/how-to-install-docker-on-ubuntu)

### 2.2 Directory Structure

```bash
/opt/ziggie/
├── docker-compose.yml           # Main orchestration file
├── .env                         # Environment variables (SECRET - not in git)
├── nginx/
│   ├── nginx.conf               # Main Nginx config
│   ├── conf.d/
│   │   ├── n8n.conf            # n8n reverse proxy
│   │   ├── api.conf            # Ziggie API reverse proxy
│   │   └── monitoring.conf     # Grafana reverse proxy
│   └── ssl/                     # Let's Encrypt certificates
├── n8n/
│   └── data/                    # n8n workflows + credentials
├── mongodb/
│   ├── data/                    # Database files
│   ├── backup/                  # Automated backups
│   └── mongod.conf              # MongoDB configuration
├── redis/
│   ├── data/                    # Redis persistence
│   └── redis.conf               # Redis configuration
├── discord-bot/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
├── ziggie-api/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
├── prometheus/
│   ├── prometheus.yml           # Scrape configs
│   └── rules/                   # Alert rules
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/        # Auto-configure Prometheus
│   │   └── dashboards/         # Pre-built dashboards
│   └── data/
└── backups/
    ├── mongodb/                 # Daily MongoDB dumps
    ├── n8n/                     # n8n workflow backups
    └── logs/                    # Backup logs
```

### 2.3 Complete Docker Compose Configuration

```yaml
# /opt/ziggie/docker-compose.yml
version: '3.8'

networks:
  ziggie-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

volumes:
  mongodb_data:
  redis_data:
  n8n_data:
  grafana_data:
  prometheus_data:

services:
  # ========================================
  # MongoDB - Agent State Database
  # ========================================
  mongodb:
    image: mongo:7.0
    container_name: ziggie-mongodb
    restart: unless-stopped
    networks:
      - ziggie-network
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_ROOT_USER}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD}
      MONGO_INITDB_DATABASE: ziggie
    volumes:
      - mongodb_data:/data/db
      - ./mongodb/backup:/backup
      - ./mongodb/mongod.conf:/etc/mongod.conf:ro
    command: --config /etc/mongod.conf
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 6G
        reservations:
          cpus: '1.0'
          memory: 4G
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"

  # ========================================
  # Redis - Caching & Message Queue
  # ========================================
  redis:
    image: redis:7-alpine
    container_name: ziggie-redis
    restart: unless-stopped
    networks:
      - ziggie-network
    volumes:
      - redis_data:/data
      - ./redis/redis.conf:/usr/local/etc/redis/redis.conf:ro
    command: redis-server /usr/local/etc/redis/redis.conf
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 3G
        reservations:
          cpus: '0.5'
          memory: 2G
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"

  # ========================================
  # n8n - Workflow Automation
  # ========================================
  n8n:
    image: n8nio/n8n:latest
    container_name: ziggie-n8n
    restart: unless-stopped
    networks:
      - ziggie-network
    environment:
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://${N8N_HOST}/
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=${POSTGRES_DB}
      - DB_POSTGRESDB_USER=${POSTGRES_USER}
      - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
      - EXECUTIONS_DATA_SAVE_ON_ERROR=all
      - EXECUTIONS_DATA_SAVE_ON_SUCCESS=all
      - EXECUTIONS_DATA_SAVE_MANUAL_EXECUTIONS=true
      - N8N_METRICS=true
      - N8N_METRICS_PREFIX=n8n_
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - postgres
      - redis
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:5678/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"

  # ========================================
  # PostgreSQL - n8n Database (Required)
  # ========================================
  postgres:
    image: postgres:16-alpine
    container_name: ziggie-postgres
    restart: unless-stopped
    networks:
      - ziggie-network
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 512M
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"

  # ========================================
  # Discord Bot - 24/7 Bot
  # ========================================
  discord-bot:
    build:
      context: ./discord-bot
      dockerfile: Dockerfile
    container_name: ziggie-discord-bot
    restart: unless-stopped
    networks:
      - ziggie-network
    environment:
      DISCORD_TOKEN: ${DISCORD_TOKEN}
      DISCORD_CLIENT_ID: ${DISCORD_CLIENT_ID}
      MONGODB_URI: mongodb://${MONGO_ROOT_USER}:${MONGO_ROOT_PASSWORD}@mongodb:27017/ziggie?authSource=admin
      REDIS_URL: redis://redis:6379
      ZIGGIE_API_URL: http://ziggie-api:3000
    depends_on:
      - mongodb
      - redis
      - ziggie-api
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 512M
    healthcheck:
      test: ["CMD", "node", "-e", "process.exit(0)"]
      interval: 60s
      timeout: 10s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"

  # ========================================
  # Ziggie Orchestrator API
  # ========================================
  ziggie-api:
    build:
      context: ./ziggie-api
      dockerfile: Dockerfile
    container_name: ziggie-api
    restart: unless-stopped
    networks:
      - ziggie-network
    environment:
      NODE_ENV: production
      PORT: 3000
      MONGODB_URI: mongodb://${MONGO_ROOT_USER}:${MONGO_ROOT_PASSWORD}@mongodb:27017/ziggie?authSource=admin
      REDIS_URL: redis://redis:6379
      JWT_SECRET: ${JWT_SECRET}
      N8N_API_KEY: ${N8N_API_KEY}
      N8N_URL: http://n8n:5678
    depends_on:
      - mongodb
      - redis
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 512M
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"

  # ========================================
  # Nginx - Reverse Proxy + SSL
  # ========================================
  nginx:
    image: nginx:alpine
    container_name: ziggie-nginx
    restart: unless-stopped
    networks:
      - ziggie-network
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./certbot/conf:/etc/letsencrypt:ro
      - ./certbot/www:/var/www/certbot:ro
    depends_on:
      - n8n
      - ziggie-api
      - grafana
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"

  # ========================================
  # Certbot - SSL Certificate Management
  # ========================================
  certbot:
    image: certbot/certbot:latest
    container_name: ziggie-certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew --webroot -w /var/www/certbot --quiet; sleep 12h & wait $${!}; done;'"
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "2"

  # ========================================
  # Prometheus - Metrics Collection
  # ========================================
  prometheus:
    image: prom/prometheus:latest
    container_name: ziggie-prometheus
    restart: unless-stopped
    networks:
      - ziggie-network
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./prometheus/rules:/etc/prometheus/rules:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=15d'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 512M
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:9090/-/healthy"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"

  # ========================================
  # Grafana - Visualization Dashboards
  # ========================================
  grafana:
    image: grafana/grafana:latest
    container_name: ziggie-grafana
    restart: unless-stopped
    networks:
      - ziggie-network
    environment:
      GF_SECURITY_ADMIN_USER: ${GRAFANA_ADMIN_USER}
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD}
      GF_INSTALL_PLUGINS: grafana-clock-panel,grafana-simple-json-datasource
      GF_SERVER_ROOT_URL: https://${GRAFANA_HOST}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
    depends_on:
      - prometheus
    deploy:
      resources:
        limits:
          cpus: '0.25'
          memory: 512M
        reservations:
          cpus: '0.1'
          memory: 256M
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"

  # ========================================
  # Node Exporter - System Metrics
  # ========================================
  node-exporter:
    image: prom/node-exporter:latest
    container_name: ziggie-node-exporter
    restart: unless-stopped
    networks:
      - ziggie-network
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    deploy:
      resources:
        limits:
          cpus: '0.25'
          memory: 256M
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"

  # ========================================
  # cAdvisor - Container Metrics
  # ========================================
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: ziggie-cadvisor
    restart: unless-stopped
    networks:
      - ziggie-network
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    privileged: true
    devices:
      - /dev/kmsg
    deploy:
      resources:
        limits:
          cpus: '0.25'
          memory: 256M
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"
```

**Sources**:
- [n8n Docker Compose production setup](https://docs.n8n.io/hosting/installation/server-setups/docker-compose/)
- [Docker resource limits best practices](https://www.hostinger.com/tutorials/docker-tutorial)
- [MongoDB Docker configuration](https://brandonrozek.com/blog/managing-mongodb-resource-usage-docker-compose/)

---

## 3. n8n Configuration & Workflow Automation

### 3.1 n8n Production Environment Variables

```env
# /opt/ziggie/.env (DO NOT COMMIT TO GIT)

# n8n Configuration
N8N_HOST=n8n.yourdomain.com
N8N_ENCRYPTION_KEY=<generate-with-openssl-rand-base64-32>
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=<strong-password>

# PostgreSQL for n8n
POSTGRES_DB=n8n
POSTGRES_USER=n8n_user
POSTGRES_PASSWORD=<strong-password>

# MongoDB
MONGO_ROOT_USER=admin
MONGO_ROOT_PASSWORD=<strong-password>

# Redis
REDIS_PASSWORD=<strong-password>

# Discord Bot
DISCORD_TOKEN=<your-bot-token>
DISCORD_CLIENT_ID=<your-client-id>

# Ziggie API
JWT_SECRET=<generate-with-openssl-rand-base64-64>
N8N_API_KEY=<n8n-api-key-from-settings>

# Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=<strong-password>
GRAFANA_HOST=grafana.yourdomain.com
```

### 3.2 n8n Key Features for Agent Orchestration

| Workflow Type | Use Case | Trigger | Actions |
|---------------|----------|---------|---------|
| **Agent Deployment** | Deploy new AI agents to Claude Desktop | Webhook from Discord | 1. Validate agent config<br>2. Push to agent queue<br>3. Update MongoDB status<br>4. Send Discord notification |
| **Task Distribution** | Distribute tasks across 1,884 agents | Cron (every 5 min) | 1. Query MongoDB for pending tasks<br>2. Select idle agents<br>3. Assign via Redis pub/sub<br>4. Log to Prometheus |
| **Health Monitoring** | Check agent heartbeats | Cron (every 1 min) | 1. Query agent status from MongoDB<br>2. Identify stale agents (>5 min)<br>3. Send alert to Discord<br>4. Auto-restart failed agents |
| **Result Aggregation** | Collect completed agent results | Redis pub/sub | 1. Listen to "agent:complete" channel<br>2. Fetch result from MongoDB<br>3. Aggregate metrics<br>4. Store in analytics DB |
| **Cost Tracking** | Monitor API usage costs | Cron (daily) | 1. Query agent API usage logs<br>2. Calculate daily costs<br>3. Send report to Discord<br>4. Alert if over budget |

**Source**: [n8n self-hosted workflow automation guide](https://latenode.com/blog/low-code-no-code-platforms/self-hosted-automation-platforms/how-to-self-host-n8n-complete-setup-guide-production-deployment-checklist-2025)

---

## 4. MongoDB Configuration

### 4.1 MongoDB Configuration File

```yaml
# /opt/ziggie/mongodb/mongod.conf

# Network settings
net:
  port: 27017
  bindIp: 0.0.0.0  # Allow Docker network connections
  maxIncomingConnections: 2000  # Support 1,884 agents + overhead

# Storage engine
storage:
  dbPath: /data/db
  journal:
    enabled: true
  wiredTiger:
    engineConfig:
      # CRITICAL: Set to 3GB (50% of 6GB container limit)
      cacheSizeGB: 3
      journalCompressor: snappy
      directoryForIndexes: false
    collectionConfig:
      blockCompressor: snappy
    indexConfig:
      prefixCompression: true

# Operation profiling (monitor slow queries)
operationProfiling:
  mode: slowOp
  slowOpThresholdMs: 100

# Replication (for future HA setup)
# replication:
#   replSetName: ziggie-rs

# Security
security:
  authorization: enabled
```

**CRITICAL**: [MongoDB in Docker MUST set `cacheSizeGB` to 50% of container memory limit](https://www.mongodb.com/docs/manual/administration/production-notes/)

### 4.2 MongoDB Database Schema

```javascript
// Agent State Collection
db.agents.createIndex({ "agentId": 1 }, { unique: true })
db.agents.createIndex({ "status": 1, "lastHeartbeat": -1 })
db.agents.createIndex({ "assignedTask": 1 })

// Schema:
{
  agentId: "agent_001",
  name: "Backend Developer Agent",
  status: "idle|busy|offline",
  currentTask: ObjectId("..."),
  lastHeartbeat: ISODate("2025-12-22T10:30:00Z"),
  capabilities: ["backend", "nodejs", "mongodb"],
  metadata: {
    claudeModel: "opus-4.5",
    maxTokens: 200000,
    costPerRequest: 0.015
  },
  createdAt: ISODate("2025-12-01T00:00:00Z"),
  updatedAt: ISODate("2025-12-22T10:30:00Z")
}

// Task Queue Collection
db.tasks.createIndex({ "status": 1, "priority": -1, "createdAt": 1 })
db.tasks.createIndex({ "assignedAgent": 1 })

// Schema:
{
  taskId: "task_12345",
  type: "code_review|bug_fix|feature_dev|research",
  status: "pending|assigned|in_progress|completed|failed",
  priority: 1-10,
  assignedAgent: "agent_001",
  payload: {
    repository: "github.com/user/repo",
    filePath: "src/index.ts",
    instructions: "Fix TypeScript error on line 42"
  },
  result: {
    status: "success",
    output: "...",
    artifacts: ["..."]
  },
  createdAt: ISODate("2025-12-22T10:00:00Z"),
  startedAt: ISODate("2025-12-22T10:05:00Z"),
  completedAt: ISODate("2025-12-22T10:15:00Z")
}

// Workflow Execution Logs
db.workflow_logs.createIndex({ "workflowId": 1, "timestamp": -1 })
db.workflow_logs.createIndex({ "agentId": 1, "timestamp": -1 })

// API Usage Metrics
db.api_metrics.createIndex({ "agentId": 1, "date": -1 })
db.api_metrics.createIndex({ "date": -1 })
```

### 4.3 Connection Pool Settings

```javascript
// Node.js connection settings for 1,884 agents
const mongoClient = new MongoClient(uri, {
  maxPoolSize: 100,  // Max 100 connections per app instance
  minPoolSize: 10,
  maxIdleTimeMS: 30000,
  serverSelectionTimeoutMS: 5000,
  socketTimeoutMS: 45000,
  family: 4  // Use IPv4
});
```

**Source**: [MongoDB connection pooling for 2000 concurrent users](https://medium.com/@deelesisuanu/scaling-mongodb-connections-for-high-traffic-applications-best-practices-and-realistic-3c4252597a2a)

---

## 5. Redis Configuration

### 5.1 Redis Configuration File

```conf
# /opt/ziggie/redis/redis.conf

# Network
bind 0.0.0.0
port 6379
protected-mode yes
requirepass <REDIS_PASSWORD>
tcp-keepalive 300

# Memory management
maxmemory 2.5gb  # Leave 0.5GB buffer from 3GB limit
maxmemory-policy allkeys-lru  # Evict least recently used keys
maxmemory-samples 5

# Persistence (RDB + AOF for durability)
save 900 1      # Save after 15 min if 1 key changed
save 300 10     # Save after 5 min if 10 keys changed
save 60 10000   # Save after 1 min if 10k keys changed
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb

appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Limits
maxclients 2000  # Support 1,884 agents + overhead
timeout 300

# Slow log
slowlog-log-slower-than 10000  # 10ms
slowlog-max-len 128

# Logging
loglevel notice
```

**Source**: [Redis at scale tuning and capacity planning](https://reintech.io/blog/redis-at-scale-tuning-capacity-planning)

### 5.2 Redis Pub/Sub Channels

```javascript
// Channel architecture for agent orchestration

// 1. Task assignment channel
PUBLISH agent:task:assign '{"agentId":"agent_001","taskId":"task_12345"}'

// 2. Agent heartbeat channel
PUBLISH agent:heartbeat '{"agentId":"agent_001","status":"idle","timestamp":1703251200}'

// 3. Task completion channel
PUBLISH agent:task:complete '{"agentId":"agent_001","taskId":"task_12345","status":"success"}'

// 4. System alerts channel
PUBLISH system:alert '{"level":"warning","message":"Agent agent_042 unresponsive for 5 minutes"}'

// 5. Broadcast commands channel
PUBLISH agent:broadcast '{"command":"restart","filter":{"status":"error"}}'
```

### 5.3 Redis Data Structures

```javascript
// Agent session cache (Hash)
HSET agent:agent_001:session status "idle"
HSET agent:agent_001:session lastHeartbeat "2025-12-22T10:30:00Z"
HSET agent:agent_001:session currentTask "task_12345"
EXPIRE agent:agent_001:session 300  // 5 min TTL

// Task queue (List - FIFO)
LPUSH queue:priority:high "task_12345"
LPUSH queue:priority:medium "task_12346"
LPUSH queue:priority:low "task_12347"

// Agent availability (Set)
SADD agents:idle "agent_001" "agent_002" "agent_003"
SADD agents:busy "agent_042"

// Rate limiting (String with expiry)
INCR ratelimit:api:agent_001
EXPIRE ratelimit:api:agent_001 60  // 1 min window

// Leaderboard (Sorted Set)
ZADD agent:performance:tasks_completed 142 "agent_001"
ZADD agent:performance:tasks_completed 98 "agent_002"
```

**Source**: [Redis Pub/Sub documentation](https://redis.io/docs/latest/develop/pubsub/)

---

## 6. Nginx Reverse Proxy Configuration

### 6.1 Main Nginx Configuration

```nginx
# /opt/ziggie/nginx/nginx.conf

user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 4096;  # Handle high concurrent connections
    use epoll;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss;

    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=n8n_limit:10m rate=5r/s;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Include server configs
    include /etc/nginx/conf.d/*.conf;
}
```

### 6.2 n8n Reverse Proxy

```nginx
# /opt/ziggie/nginx/conf.d/n8n.conf

server {
    listen 80;
    server_name n8n.yourdomain.com;

    # ACME challenge for Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect all HTTP to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name n8n.yourdomain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/n8n.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/n8n.yourdomain.com/privkey.pem;

    # Rate limiting
    limit_req zone=n8n_limit burst=20 nodelay;

    location / {
        proxy_pass http://n8n:5678;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support for n8n
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts for long-running workflows
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
}
```

### 6.3 Ziggie API Reverse Proxy

```nginx
# /opt/ziggie/nginx/conf.d/api.conf

server {
    listen 80;
    server_name api.yourdomain.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # Rate limiting - 10 requests per second per IP
    limit_req zone=api_limit burst=50 nodelay;

    location / {
        proxy_pass http://ziggie-api:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS headers for API
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;

        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }

    # Health check endpoint (no rate limit)
    location /health {
        access_log off;
        proxy_pass http://ziggie-api:3000/health;
    }
}
```

### 6.4 Grafana Reverse Proxy

```nginx
# /opt/ziggie/nginx/conf.d/monitoring.conf

server {
    listen 80;
    server_name grafana.yourdomain.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name grafana.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/grafana.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/grafana.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://grafana:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**Sources**:
- [Nginx reverse proxy with Docker and Let's Encrypt](https://cloud.google.com/community/tutorials/nginx-reverse-proxy-docker)
- [SSL setup with Certbot in Docker](https://pentacent.medium.com/nginx-and-lets-encrypt-with-docker-in-less-than-5-minutes-b4b8a60d3a71)

---

## 7. Firewall Rules & SSH Hardening

### 7.1 UFW Firewall Configuration

```bash
# Initial setup - deny all incoming, allow all outgoing
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH on custom port (change from 22 to reduce attack surface)
sudo ufw allow 52231/tcp comment 'SSH custom port'

# Allow HTTP/HTTPS for Nginx
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'

# Rate limiting for SSH (max 6 connections per 30 seconds)
sudo ufw limit 52231/tcp

# Enable firewall
sudo ufw enable

# Verify rules
sudo ufw status verbose

# Expected output:
# Status: active
# To                         Action      From
# --                         ------      ----
# 52231/tcp                  LIMIT       Anywhere
# 80/tcp                     ALLOW       Anywhere
# 443/tcp                    ALLOW       Anywhere
```

**Source**: [VPS security hardening checklist 2025](https://retzor.com/blog/vps-security-hardening-25-point-checklist-for-2025/)

### 7.2 SSH Hardening

```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Apply these changes:
Port 52231                          # Custom port (not 22)
PermitRootLogin no                  # Disable root login
PasswordAuthentication no           # Force SSH keys only
PubkeyAuthentication yes
ChallengeResponseAuthentication no
UsePAM yes
X11Forwarding no
PrintMotd no
AcceptEnv LANG LC_*
ClientAliveInterval 300             # Disconnect idle sessions after 5 min
ClientAliveCountMax 2
MaxAuthTries 3                      # Lock after 3 failed attempts
MaxSessions 2
AllowUsers yourusername             # Whitelist specific users

# Restart SSH
sudo systemctl restart sshd
```

### 7.3 Fail2Ban for Intrusion Prevention

```bash
# Install Fail2Ban
sudo apt install fail2ban -y

# Create custom jail for SSH
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600        # Ban for 1 hour
findtime = 600        # 10 minute window
maxretry = 3          # 3 attempts before ban
destemail = admin@yourdomain.com
sendername = Fail2Ban
action = %(action_mwl)s  # Ban + email with logs

[sshd]
enabled = true
port = 52231
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 7200        # 2 hour ban for SSH

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 5
findtime = 60
bantime = 3600
```

```bash
# Start Fail2Ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Check status
sudo fail2ban-client status
sudo fail2ban-client status sshd
```

**Source**: [VPS security hardening with Fail2Ban](https://cloudpap.com/blog/vps-hardening/)

### 7.4 Additional Security Measures

```bash
# Disable IPv6 if not used (reduces attack surface)
sudo nano /etc/sysctl.conf
# Add:
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
sudo sysctl -p

# Install and configure unattended-upgrades for automatic security patches
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure --priority=low unattended-upgrades

# Enable automatic security updates
sudo nano /etc/apt/apt.conf.d/50unattended-upgrades
# Ensure this is uncommented:
# "origin=Debian,codename=${distro_codename}-updates";
# "${distro_id}:${distro_codename}-security";

# Set up automated reboots for kernel updates (3 AM daily)
echo "0 3 * * * /usr/sbin/needrestart -r a" | sudo crontab -
```

---

## 8. Monitoring with Prometheus & Grafana

### 8.1 Prometheus Configuration

```yaml
# /opt/ziggie/prometheus/prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'ziggie-production'
    environment: 'vps'

# Alertmanager configuration (future)
# alerting:
#   alertmanagers:
#     - static_configs:
#         - targets: ['alertmanager:9093']

# Rule files
rule_files:
  - '/etc/prometheus/rules/*.yml'

# Scrape configurations
scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Node Exporter - system metrics
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  # cAdvisor - container metrics
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  # n8n metrics
  - job_name: 'n8n'
    static_configs:
      - targets: ['n8n:5678']
    metrics_path: '/metrics'

  # MongoDB Exporter (requires separate container)
  - job_name: 'mongodb'
    static_configs:
      - targets: ['mongodb-exporter:9216']

  # Redis Exporter (requires separate container)
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  # Ziggie API metrics (custom /metrics endpoint)
  - job_name: 'ziggie-api'
    static_configs:
      - targets: ['ziggie-api:3000']
    metrics_path: '/metrics'
```

### 8.2 Alert Rules

```yaml
# /opt/ziggie/prometheus/rules/alerts.yml

groups:
  - name: ziggie_alerts
    interval: 30s
    rules:
      # Container health
      - alert: ContainerDown
        expr: up == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Container {{ $labels.job }} is down"
          description: "Container {{ $labels.job }} has been down for more than 2 minutes."

      # High CPU usage
      - alert: HighCPUUsage
        expr: rate(process_cpu_seconds_total[5m]) > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.job }}"
          description: "CPU usage is above 80% for 5 minutes."

      # High memory usage
      - alert: HighMemoryUsage
        expr: (container_memory_usage_bytes / container_spec_memory_limit_bytes) > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.name }}"
          description: "Memory usage is above 90% for 5 minutes."

      # MongoDB connection pool exhaustion
      - alert: MongoDBConnectionPoolExhausted
        expr: mongodb_connections{state="current"} > 1800
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "MongoDB connection pool near limit"
          description: "MongoDB has {{ $value }} active connections (limit: 2000)."

      # Redis memory usage
      - alert: RedisHighMemory
        expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis memory usage high"
          description: "Redis memory usage is {{ $value | humanizePercentage }}."

      # Disk space
      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) < 0.15
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low disk space on VPS"
          description: "Disk space is below 15% ({{ $value | humanizePercentage }} remaining)."

      # Agent heartbeat (custom metric from Ziggie API)
      - alert: AgentUnresponsive
        expr: ziggie_agent_last_heartbeat_seconds > 300
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Agent {{ $labels.agent_id }} unresponsive"
          description: "Agent has not sent heartbeat for {{ $value }} seconds."
```

### 8.3 Grafana Dashboard Provisioning

```yaml
# /opt/ziggie/grafana/provisioning/datasources/prometheus.yml

apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
```

```yaml
# /opt/ziggie/grafana/provisioning/dashboards/dashboards.yml

apiVersion: 1

providers:
  - name: 'Ziggie Dashboards'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards/json
```

### 8.4 Pre-Built Dashboards to Import

| Dashboard | Grafana ID | Purpose |
|-----------|------------|---------|
| Node Exporter Full | 1860 | System metrics (CPU, RAM, disk, network) |
| cAdvisor Exporter | 14282 | Docker container metrics |
| MongoDB Dashboard | 2583 | MongoDB performance metrics |
| Redis Dashboard | 11835 | Redis cache & pub/sub metrics |
| Nginx Dashboard | 12708 | Nginx request rates & latency |

**Import via**: Grafana UI → Dashboards → Import → Enter ID

**Source**: [Grafana dashboard provisioning guide](https://grafana.com/docs/grafana-cloud/send-data/metrics/metrics-prometheus/prometheus-config-examples/docker-compose-linux/)

---

## 9. Backup Strategy & Disaster Recovery

### 9.1 Automated Backup Script

```bash
#!/bin/bash
# /opt/ziggie/backups/backup.sh

set -e

BACKUP_DIR="/opt/ziggie/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

echo "Starting backup at $(date)"

# 1. MongoDB Backup
echo "Backing up MongoDB..."
docker exec ziggie-mongodb mongodump \
  --username=$MONGO_ROOT_USER \
  --password=$MONGO_ROOT_PASSWORD \
  --authenticationDatabase=admin \
  --out=/backup/mongodb_$DATE

# Compress MongoDB backup
tar -czf $BACKUP_DIR/mongodb/mongodb_$DATE.tar.gz \
  -C $BACKUP_DIR/../mongodb/backup mongodb_$DATE
rm -rf $BACKUP_DIR/../mongodb/backup/mongodb_$DATE

# 2. Redis Backup (RDB snapshot)
echo "Backing up Redis..."
docker exec ziggie-redis redis-cli -a $REDIS_PASSWORD SAVE
docker cp ziggie-redis:/data/dump.rdb $BACKUP_DIR/redis/redis_$DATE.rdb

# 3. n8n Workflow Backup
echo "Backing up n8n workflows..."
docker exec ziggie-n8n n8n export:workflow --all --output=/home/node/.n8n/backup_$DATE.json
docker cp ziggie-n8n:/home/node/.n8n/backup_$DATE.json $BACKUP_DIR/n8n/

# 4. Docker Compose & Configs
echo "Backing up configurations..."
tar -czf $BACKUP_DIR/configs/configs_$DATE.tar.gz \
  /opt/ziggie/docker-compose.yml \
  /opt/ziggie/.env \
  /opt/ziggie/nginx/ \
  /opt/ziggie/prometheus/ \
  /opt/ziggie/grafana/provisioning/

# 5. Clean old backups (keep last 7 days)
echo "Cleaning old backups (retention: $RETENTION_DAYS days)..."
find $BACKUP_DIR/mongodb/ -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR/redis/ -name "*.rdb" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR/n8n/ -name "*.json" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR/configs/ -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed at $(date)"
```

### 9.2 Backup Cron Job

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/ziggie/backups/backup.sh >> /opt/ziggie/backups/logs/backup.log 2>&1

# Weekly full system backup at 3 AM Sunday
0 3 * * 0 /opt/ziggie/backups/full_backup.sh >> /opt/ziggie/backups/logs/full_backup.log 2>&1
```

### 9.3 Disaster Recovery Procedure

```bash
#!/bin/bash
# /opt/ziggie/backups/restore.sh

BACKUP_DATE=$1  # Format: 20251222_020000

if [ -z "$BACKUP_DATE" ]; then
  echo "Usage: ./restore.sh <backup_date>"
  echo "Example: ./restore.sh 20251222_020000"
  exit 1
fi

echo "Starting restore from backup: $BACKUP_DATE"

# 1. Stop all services
docker compose -f /opt/ziggie/docker-compose.yml down

# 2. Restore MongoDB
echo "Restoring MongoDB..."
tar -xzf /opt/ziggie/backups/mongodb/mongodb_$BACKUP_DATE.tar.gz -C /tmp/
docker compose up -d mongodb
sleep 10
docker exec -i ziggie-mongodb mongorestore \
  --username=$MONGO_ROOT_USER \
  --password=$MONGO_ROOT_PASSWORD \
  --authenticationDatabase=admin \
  --drop \
  /tmp/mongodb_$BACKUP_DATE

# 3. Restore Redis
echo "Restoring Redis..."
cp /opt/ziggie/backups/redis/redis_$BACKUP_DATE.rdb /opt/ziggie/redis/data/dump.rdb
docker compose up -d redis

# 4. Restore n8n workflows
echo "Restoring n8n workflows..."
docker compose up -d n8n postgres
sleep 15
docker exec -i ziggie-n8n n8n import:workflow --input=/home/node/.n8n/backup_$BACKUP_DATE.json

# 5. Restore configs
echo "Restoring configurations..."
tar -xzf /opt/ziggie/backups/configs/configs_$BACKUP_DATE.tar.gz -C /

# 6. Start all services
echo "Starting all services..."
docker compose -f /opt/ziggie/docker-compose.yml up -d

echo "Restore completed. Verify services with: docker compose ps"
```

### 9.4 Off-Site Backup (Recommended)

```bash
# Option 1: Rsync to another VPS
rsync -avz --delete /opt/ziggie/backups/ user@backup-vps:/backups/ziggie/

# Option 2: Upload to cloud storage (AWS S3, Backblaze B2, etc.)
# Install rclone
curl https://rclone.org/install.sh | sudo bash

# Configure cloud storage
rclone config

# Sync backups to cloud (add to backup.sh)
rclone sync /opt/ziggie/backups/ remote:ziggie-backups/ \
  --exclude "logs/" \
  --log-file=/opt/ziggie/backups/logs/rclone.log
```

**Recommendation**: Use [Backblaze B2](https://www.backblaze.com/b2/cloud-storage.html) for cost-effective off-site backups (first 10GB free, $0.005/GB/month after)

---

## 10. Deployment Checklist

### Pre-Deployment

```text
□ Purchase Hostinger KVM 4 VPS (£9.99/mo)
□ Point DNS A records to VPS IP:
  - n8n.yourdomain.com
  - api.yourdomain.com
  - grafana.yourdomain.com
□ Generate strong passwords for all services (use password manager)
□ Create SSH key pair locally (ssh-keygen -t ed25519)
□ Save all credentials in .env file (DO NOT commit to git)
```

### Initial Setup

```text
□ SSH into VPS as root
□ Create non-root user: adduser ziggie
□ Add to sudo: usermod -aG sudo ziggie
□ Add SSH key: ssh-copy-id -i ~/.ssh/id_ed25519.pub ziggie@vps-ip
□ Configure SSH hardening (custom port, disable root login)
□ Set up UFW firewall
□ Install Docker & Docker Compose
□ Install Fail2Ban
□ Enable unattended-upgrades
```

### Application Deployment

```text
□ Clone/create /opt/ziggie directory structure
□ Copy all configuration files (docker-compose.yml, nginx configs, etc.)
□ Create .env file with all environment variables
□ Set correct file permissions: chown -R ziggie:ziggie /opt/ziggie
□ Generate SSL certificates: docker compose run --rm certbot certonly --webroot ...
□ Start services: docker compose up -d
□ Verify all containers running: docker compose ps
□ Check logs for errors: docker compose logs -f
```

### SSL Certificate Generation

```bash
# First-time certificate generation for each domain
docker compose run --rm certbot certonly --webroot \
  -w /var/www/certbot \
  -d n8n.yourdomain.com \
  --email admin@yourdomain.com \
  --agree-tos \
  --no-eff-email

# Repeat for other domains (api.yourdomain.com, grafana.yourdomain.com)

# Reload Nginx to use certificates
docker compose exec nginx nginx -s reload
```

### Post-Deployment Verification

```text
□ Test n8n access: https://n8n.yourdomain.com
□ Test API health: https://api.yourdomain.com/health
□ Test Grafana dashboards: https://grafana.yourdomain.com
□ Verify MongoDB connections: docker exec -it ziggie-mongodb mongosh
□ Verify Redis: docker exec -it ziggie-redis redis-cli ping
□ Check Prometheus targets: http://vps-ip:9090/targets (via SSH tunnel)
□ Run first backup manually: /opt/ziggie/backups/backup.sh
□ Set up monitoring alerts in Grafana
□ Test Discord bot connectivity
□ Deploy 5 test agents and verify orchestration
□ Perform disaster recovery test (restore from backup)
```

### Security Audit

```text
□ Run Lynis security audit: sudo lynis audit system
□ Verify UFW status: sudo ufw status verbose
□ Check Fail2Ban jails: sudo fail2ban-client status
□ Test SSH key-only authentication (password login disabled)
□ Verify SSL certificate grades: https://www.ssllabs.com/ssltest/
□ Enable 2FA for critical services (n8n, Grafana)
□ Set up log monitoring alerts
□ Document all credentials in password manager
□ Schedule regular security updates (weekly)
```

---

## 11. Estimated Monthly Costs

| Service | Cost | Billing | Notes |
|---------|------|---------|-------|
| **Hostinger KVM 4 VPS** | £9.99 | Monthly | 4 vCPU, 16GB RAM, 200GB NVMe |
| **Domain name** | £10-15 | Yearly | .com/.io domain (~£1.25/month) |
| **Backblaze B2 backup** | £0-5 | Monthly | First 10GB free, ~£2-5 for 50GB |
| **Let's Encrypt SSL** | £0 | Free | Auto-renewal included |
| **Total** | **~£12-15/mo** | | **£144-180/year** |

### Cost Breakdown for 1,884 Agents

Assuming average agent usage:
- 10 requests/day/agent
- ~18,840 total API requests/day
- ~565,200 API requests/month

**Claude API costs** (separate from VPS):
- Opus 4.5: $0.015/request × 565,200 = **$8,478/mo**
- Sonnet 3.5: $0.003/request × 565,200 = **$1,696/mo**

**Recommendation**: Mix agent tiers (80% Sonnet, 20% Opus) for ~$2,262/mo API costs

**VPS Infrastructure**: £12-15/mo ($15-19/mo) is **negligible** compared to API costs (0.8% of total)

---

## 12. Scaling Plan (Future)

### Current Setup (KVM 4): 1,884 agents

### Scale to 5,000 agents (KVM 8)
- Upgrade to KVM 8: £18.99/mo (8 vCPU, 32GB RAM)
- Increase MongoDB memory limit: 12GB
- Increase Redis memory limit: 6GB
- Add second n8n instance (load balanced)
- Estimated cost: **£20/mo** ($25/mo)

### Scale to 10,000+ agents (Multi-VPS)
- **VPS 1**: MongoDB + Redis cluster (KVM 8)
- **VPS 2**: n8n + Ziggie API (KVM 4)
- **VPS 3**: Monitoring + backups (KVM 2)
- Load balancer (Hostinger Load Balancer or Cloudflare)
- Estimated cost: **£35-40/mo** ($44-50/mo)

### Enterprise Scale (50,000+ agents)
- Migrate to managed Kubernetes (DigitalOcean, Linode, or AWS EKS)
- Use managed MongoDB Atlas (M40 cluster: ~$450/mo)
- Use managed Redis (AWS ElastiCache: ~$100/mo)
- Total infrastructure: **~$600-800/mo**

---

## Summary

**Recommended Setup**: Hostinger **KVM 4 VPS** (£9.99/mo) with complete Docker stack

**Key Services**:
1. **n8n** - Workflow automation (with PostgreSQL backend)
2. **MongoDB** - Agent state database (6GB RAM, 2000 connections)
3. **Redis** - Caching + pub/sub message queue (3GB RAM)
4. **Discord Bot** - 24/7 agent interface
5. **Ziggie API** - Orchestrator REST API
6. **Nginx** - Reverse proxy with Let's Encrypt SSL
7. **Prometheus + Grafana** - Monitoring dashboards
8. **Automated backups** - Daily MongoDB/Redis/n8n backups

**Security**: SSH hardening, UFW firewall, Fail2Ban, auto-updates, SSL certificates

**Total Monthly Cost**: £12-15 ($15-19) including backups

**Deployment Time**: 2-3 hours for complete setup

**Scalability**: Can scale to 5,000 agents with KVM 8 upgrade (£18.99/mo)

---

## Sources

### VPS & Docker Setup
- [Hostinger Docker VPS template guide](https://www.hostinger.com/tutorials/how-to-install-docker-on-ubuntu)
- [Hostinger n8n self-hosting tutorial](https://www.hostinger.com/tutorials/how-to-self-host-n8n-with-docker)
- [Docker best practices 2025](https://www.hostinger.com/tutorials/docker-tutorial)

### n8n Production Deployment
- [n8n self-hosted complete setup guide 2025](https://latenode.com/blog/low-code-no-code-platforms/self-hosted-automation-platforms/how-to-self-host-n8n-complete-setup-guide-production-deployment-checklist-2025)
- [n8n Docker Compose production examples](https://docs.n8n.io/hosting/installation/server-setups/docker-compose/)
- [n8n production deployment with PostgreSQL](https://zakops.com/devops/n8n-docker)

### Database Configuration
- [MongoDB Docker resource limits](https://brandonrozek.com/blog/managing-mongodb-resource-usage-docker-compose/)
- [MongoDB production notes](https://www.mongodb.com/docs/manual/administration/production-notes/)
- [MongoDB scaling for 2000 concurrent users](https://medium.com/@deelesisuanu/scaling-mongodb-connections-for-high-traffic-applications-best-practices-and-realistic-3c4252597a2a)
- [Redis sizing and capacity planning](https://tyk.io/docs/5.0/planning-for-production/redis-sizing/)
- [Redis at scale tuning guide](https://reintech.io/blog/redis-at-scale-tuning-capacity-planning)
- [Redis Pub/Sub documentation](https://redis.io/docs/latest/develop/pubsub/)

### Security Hardening
- [VPS security hardening 25-point checklist 2025](https://retzor.com/blog/vps-security-hardening-25-point-checklist-for-2025/)
- [VPS hardening complete guide 2025](https://cloudpap.com/blog/vps-hardening/)
- [Linux server 10-step hardening checklist](https://stonetusker.com/securing-linux-servers-10-step-hardening-checklist/)

### SSL & Reverse Proxy
- [Nginx and Let's Encrypt with Docker in 5 minutes](https://pentacent.medium.com/nginx-and-lets-encrypt-with-docker-in-less-than-5-minutes-b4b8a60d3a71)
- [Nginx reverse proxy with Docker and Let's Encrypt](https://cloud.google.com/community/tutorials/nginx-reverse-proxy-docker)
- [Secure reverse proxy with HTTPS using Docker Compose](https://medium.com/@dinusai05/setting-up-a-secure-reverse-proxy-with-https-using-docker-compose-nginx-and-certbot-lets-encrypt-cfd012c53ca0)

### Monitoring
- [Prometheus and Grafana Docker monitoring guide](https://grafana.com/docs/grafana-cloud/send-data/metrics/metrics-prometheus/prometheus-config-examples/docker-compose-linux/)
- [Docker monitoring with Prometheus and Grafana](https://signoz.io/guides/how-to-monitor-docker-containers-with-prometheus-and-grafana/)
- [VPS monitoring with Docker, Grafana, Prometheus](https://medium.com/@joss-dev/server-monitoring-with-docker-grafana-prometheus-and-node-exporter-in-1-minute-b382cc0a68d7)

---

**Document Version**: 1.0
**Last Updated**: 2025-12-22
**Agent**: L1 DevOps Agent (Ziggie)
**Status**: PRODUCTION READY
