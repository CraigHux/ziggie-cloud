# ZIGGIE OPTIMIZED STACK - VALIDATION GUIDE

> **Author**: HEPHAESTUS (Technical Art Director, Elite Technical Team)
> **Date**: 2025-12-28
> **Purpose**: Step-by-step validation checklist for optimized Docker stack

---

## VALIDATION PHASES

### Phase 1: Pre-Deployment Checks

**Before running deploy-optimized.sh:**

```bash
# Check system resources
free -h
df -h
lscpu

# Verify Docker
docker --version
docker compose version

# Check .env file
cat .env | grep -E "POSTGRES_PASSWORD|MONGO_PASSWORD|REDIS_PASSWORD"

# Ensure no conflicting containers
docker ps -a
```

**Expected Results**:
- ✅ Total RAM: ≥16GB
- ✅ Available disk: ≥100GB
- ✅ Docker version: ≥24.0
- ✅ All required env vars present
- ✅ No running containers on conflicting ports

---

### Phase 2: Deployment Execution

**Run deployment:**

```bash
# Make executable
chmod +x deploy-optimized.sh

# Run with sudo
sudo ./deploy-optimized.sh 2>&1 | tee deployment.log
```

**Expected Duration**: 5-10 minutes (depending on image download speed)

**Watch for**:
- ✅ All 6 phases complete without errors
- ✅ Databases reach "healthy" status
- ✅ ≥18 containers running
- ⚠️ Warnings are OK, errors are NOT

---

### Phase 3: Container Health Validation

**Check all containers:**

```bash
# List all containers with status
docker compose ps

# Check health status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Count healthy containers
docker ps --filter "health=healthy" | wc -l
```

**Expected Results**:
- ✅ PostgreSQL: healthy
- ✅ MongoDB: healthy
- ✅ Redis: healthy
- ✅ Ziggie API: running (may not have health check)
- ✅ MCP Gateway: running
- ✅ n8n: running
- ✅ Nginx: running
- ✅ Prometheus: running
- ✅ Grafana: running

**If Unhealthy**:
```bash
# Check specific container logs
docker logs ziggie-postgres --tail 50
docker logs ziggie-mongodb --tail 50
docker logs ziggie-redis --tail 50

# Restart unhealthy container
docker compose restart <service-name>
```

---

### Phase 4: Resource Limit Validation

**Verify resource limits are enforced:**

```bash
# Check memory limits
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.CPUPerc}}"

# Inspect specific container limits
docker inspect ziggie-postgres | jq '.[0].HostConfig.Memory'
docker inspect ziggie-ollama | jq '.[0].HostConfig.Memory'
docker inspect ziggie-api | jq '.[0].HostConfig.Memory'
```

**Expected Results**:
| Container | Memory Limit | CPU Limit |
|-----------|--------------|-----------|
| ziggie-postgres | 3221225472 (3GB) | 0.8 |
| ziggie-ollama | 4294967296 (4GB) | 0.8 |
| ziggie-api | 2147483648 (2GB) | 1.0 |
| ziggie-mcp-gateway | 1610612736 (1.5GB) | 0.8 |
| ziggie-redis | 536870912 (512MB) | 0.3 |
| ziggie-mongodb | 1610612736 (1.5GB) | 0.3 |

**Validation Command**:
```bash
# This should show limits for all containers
for container in $(docker ps --format '{{.Names}}'); do
    echo "=== $container ==="
    docker inspect $container | jq '.[0].HostConfig | {Memory, NanoCpus}'
done
```

---

### Phase 5: Network Connectivity

**Test inter-container communication:**

```bash
# Test PostgreSQL connection from API container
docker exec ziggie-api nc -zv postgres 5432

# Test MongoDB connection
docker exec ziggie-api nc -zv mongodb 27017

# Test Redis connection
docker exec ziggie-api nc -zv redis 6379

# Test Ollama connection
docker exec ziggie-api nc -zv ollama 11434

# Test MCP Gateway connection
docker exec ziggie-api nc -zv mcp-gateway 8080
```

**Expected Results**:
- ✅ All connections succeed (Connection to X 5432 port [tcp/*] succeeded!)
- ❌ If any fail, check network configuration: `docker network inspect ziggie-network`

---

### Phase 6: Service Health Endpoints

**Test HTTP health endpoints:**

```bash
# Function to test endpoint
test_health() {
    local NAME=$1
    local URL=$2
    echo -n "Testing $NAME... "
    if curl -sf --max-time 5 "$URL" > /dev/null; then
        echo "✅ OK"
    else
        echo "❌ FAILED"
    fi
}

# Test all endpoints
test_health "Ziggie API" "http://localhost:8000/health"
test_health "MCP Gateway" "http://localhost:8080/health"
test_health "Prometheus" "http://localhost:9090/-/healthy"
test_health "Grafana" "http://localhost:3000/api/health"
test_health "n8n" "http://localhost:5678/healthz"
test_health "Portainer" "http://localhost:9000/api/status"
test_health "Ollama" "http://localhost:11434/api/tags"
```

**Expected Results**:
- ✅ All endpoints return HTTP 200
- ❌ If any fail, check logs: `docker logs <container-name>`

---

### Phase 7: Database Performance

**PostgreSQL Performance Test:**

```bash
# Check connection count
docker exec ziggie-postgres psql -U ziggie -c "SELECT count(*) FROM pg_stat_activity;"

# Check shared_buffers setting
docker exec ziggie-postgres psql -U ziggie -c "SHOW shared_buffers;"

# Expected: 768MB

# Check effective_cache_size
docker exec ziggie-postgres psql -U ziggie -c "SHOW effective_cache_size;"

# Expected: 2.25GB

# Check random_page_cost (should be 1.1 for NVMe)
docker exec ziggie-postgres psql -U ziggie -c "SHOW random_page_cost;"

# Expected: 1.1
```

**Redis Performance Test:**

```bash
# Check maxmemory setting
docker exec ziggie-redis redis-cli -a $REDIS_PASSWORD CONFIG GET maxmemory

# Expected: 471859200 (450MB)

# Check maxmemory-policy
docker exec ziggie-redis redis-cli -a $REDIS_PASSWORD CONFIG GET maxmemory-policy

# Expected: allkeys-lru

# Run Redis benchmark (optional)
docker exec ziggie-redis redis-benchmark -a $REDIS_PASSWORD -q -n 10000
```

**MongoDB Performance Test:**

```bash
# Check wiredTiger cache size
docker exec ziggie-mongodb mongosh admin -u ziggie -p $MONGO_PASSWORD \
    --eval "db.serverStatus().wiredTiger.cache['maximum bytes configured']"

# Expected: ~1073741824 (1GB)
```

---

### Phase 8: Monitoring Stack

**Verify Prometheus is scraping targets:**

```bash
# Check Prometheus targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'
```

**Expected Results**:
```json
{"job":"prometheus","health":"up"}
{"job":"cadvisor","health":"up"}
{"job":"node-exporter","health":"up"}
{"job":"ziggie-api","health":"up"}
{"job":"mcp-gateway","health":"up"}
```

**Check Grafana data sources:**

```bash
# List Grafana data sources (requires Grafana API key or admin login)
curl -s -u admin:$GRAFANA_PASSWORD http://localhost:3000/api/datasources | jq '.[] | {name, type, url}'
```

---

### Phase 9: Load Testing (Optional)

**API Load Test:**

```bash
# Install apache2-utils if not present
apt-get install -y apache2-utils

# Run load test (100 concurrent, 10k requests)
ab -n 10000 -c 100 http://localhost:8000/health

# Check results
# Expected:
# - Requests per second: >1000
# - 50th percentile: <50ms
# - 95th percentile: <500ms
# - 99th percentile: <1000ms
# - Failed requests: 0
```

**Ollama Load Test (if API exists):**

```bash
# Simple inference test
time docker exec ziggie-ollama ollama run llama2:7b "Say hello in 5 words"

# Expected: <30s first run (cold start), <10s subsequent runs
```

---

### Phase 10: Alert Validation

**Check Prometheus alerts:**

```bash
# List all alerts
curl -s http://localhost:9090/api/v1/rules | jq '.data.groups[] | .name'

# Expected output:
# "resource_alerts"

# Check active alerts (should be empty on fresh deployment)
curl -s http://localhost:9090/api/v1/alerts | jq '.data.alerts[] | {alertname, state}'

# Expected: [] (no active alerts)
```

**Trigger test alert (memory threshold):**

```bash
# Temporarily increase container memory usage to test alert
docker run --rm -it --name memory-hog -m 256m alpine sh -c 'dd if=/dev/zero of=/dev/null bs=1M count=10000'

# Wait 2 minutes, then check Prometheus alerts
# Should see "ContainerMemoryNearLimit" alert firing
```

---

## PERFORMANCE BENCHMARKS

### Target Metrics (After Optimization)

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| **API P95 Latency** | <500ms | >1s |
| **API P99 Latency** | <1s | >2s |
| **API Error Rate** | <1% | >5% |
| **PostgreSQL Connections** | <80 | >95 |
| **Redis Hit Rate** | >90% | <70% |
| **Host Memory Available** | >2GB | <1GB |
| **Host CPU Utilization** | <80% | >90% |
| **Disk I/O Wait** | <10% | >50% |
| **Container Restarts** | 0 | >5/hour |

### How to Monitor

**Real-time monitoring:**
```bash
# Watch resource usage (updates every 2s)
watch -n 2 'docker stats --no-stream'

# Monitor specific service logs
docker logs -f ziggie-api
docker logs -f ziggie-postgres

# Monitor all logs
docker compose logs -f
```

**Prometheus queries (via browser: http://localhost:9090/graph):**

```promql
# API latency P95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="ziggie-api"}[5m]))

# Container memory usage percentage
(container_memory_usage_bytes / container_spec_memory_limit_bytes) * 100

# PostgreSQL active connections
pg_stat_database_numbackends

# Redis hit rate
rate(redis_keyspace_hits_total[5m]) / (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m]))

# Host CPU usage
100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Host memory available
node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes * 100
```

---

## TROUBLESHOOTING CHECKLIST

### Container Won't Start

```bash
# Check logs
docker logs ziggie-<service-name> --tail 100

# Common issues:
# 1. Port already in use
#    Fix: netstat -tlnp | grep <port>; kill process or change port
# 2. Volume permissions
#    Fix: sudo chown -R 1000:1000 /mnt/nvme/ziggie/<service>
# 3. Missing environment variable
#    Fix: Check .env file, restart: docker compose up -d <service>
```

### Container Keeps Restarting

```bash
# Check restart count
docker inspect ziggie-<service> | jq '.[0].RestartCount'

# Common causes:
# 1. OOM (out of memory)
#    Check: docker inspect ziggie-<service> | jq '.[0].State.OOMKilled'
#    Fix: Increase memory limit in docker-compose.yml
# 2. Health check failing
#    Check: docker inspect ziggie-<service> | jq '.[0].State.Health'
#    Fix: Adjust health check timeout/interval
# 3. Dependency not ready
#    Fix: Increase depends_on condition timeout or add manual delay
```

### Service Unhealthy

```bash
# Check health check details
docker inspect ziggie-<service> | jq '.[0].State.Health.Log[-1]'

# Common fixes:
# 1. Health check timeout too aggressive
#    Fix: Increase timeout in healthcheck section
# 2. Service slow to start
#    Fix: Increase start_period in healthcheck
# 3. Actual service failure
#    Fix: Check application logs, fix underlying issue
```

### High Memory Usage

```bash
# Identify memory hog
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}" | sort -k3 -hr

# Common culprits:
# 1. Ollama with large model
#    Fix: Use smaller model (Q4_K_M quantization) or increase limit
# 2. PostgreSQL query bloat
#    Fix: Optimize queries, add indexes, vacuum database
# 3. n8n workflow execution
#    Fix: Enable execution data pruning (already configured)
```

### High CPU Usage

```bash
# Identify CPU hog
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}" | sort -k2 -hr

# Common culprits:
# 1. Ollama inference
#    Fix: Normal during model inference, reduce OLLAMA_NUM_PARALLEL
# 2. PostgreSQL vacuum
#    Fix: Normal during maintenance, schedule during off-hours
# 3. Prometheus scraping
#    Fix: Increase scrape_interval in prometheus.yml
```

### Slow API Response

```bash
# Check API logs for slow queries
docker logs ziggie-api --tail 100 | grep -i "slow\|timeout"

# Check database performance
docker exec ziggie-postgres psql -U ziggie -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE state = 'active' AND now() - pg_stat_activity.query_start > interval '5 seconds';"

# Check Redis latency
docker exec ziggie-redis redis-cli -a $REDIS_PASSWORD --latency-history

# Optimization steps:
# 1. Add database indexes
# 2. Implement Redis caching
# 3. Optimize slow queries
# 4. Increase worker count
```

---

## ROLLBACK PROCEDURE

If deployment fails or performance degrades:

### Quick Rollback (Use Backup)

```bash
# Stop optimized stack
docker compose down

# Restore original configuration
cp docker-compose.yml.bak docker-compose.yml  # (if you backed it up)

# Restore volumes from backup
BACKUP_DIR="./backups/YYYYMMDD_HHMMSS"  # Replace with actual backup timestamp
for VOLUME_BACKUP in $BACKUP_DIR/*.tar.gz; do
    VOLUME_NAME=$(basename $VOLUME_BACKUP .tar.gz)
    docker run --rm -v $VOLUME_NAME:/data -v $BACKUP_DIR:/backup \
        alpine tar xzf /backup/${VOLUME_NAME}.tar.gz -C /data
done

# Restart old stack
docker compose up -d
```

### Gradual Rollback (Remove Limits Only)

```bash
# Edit docker-compose.yml, remove deploy.resources sections
# Keep other optimizations (health checks, tuning parameters)

# Restart services one by one
docker compose up -d --no-deps <service-name>
```

---

## SUCCESS CRITERIA

**Deployment is successful if**:
✅ All 18+ containers running
✅ All critical services healthy (PostgreSQL, Redis, Ziggie API)
✅ API P95 latency <500ms under normal load
✅ No containers restarting
✅ Host memory available >2GB
✅ Host CPU <80%
✅ Prometheus scraping all targets
✅ No critical alerts firing

**If ALL criteria met**: Deployment successful. Proceed to production traffic.

**If ANY criterion fails**: Investigate, fix, or rollback. DO NOT proceed to production.

---

## CONTINUOUS MONITORING

**Daily checks (automated via cron):**

```bash
# Create monitoring script
cat > /usr/local/bin/ziggie-health-check.sh <<'EOF'
#!/bin/bash
# Daily Ziggie health check

LOGFILE="/var/log/ziggie-health-$(date +%Y%m%d).log"

echo "=== Ziggie Health Check - $(date) ===" >> $LOGFILE

# Container health
docker ps --format "{{.Names}}\t{{.Status}}" >> $LOGFILE

# Resource usage
docker stats --no-stream --format "table {{.Name}}\t{{.MemPerc}}\t{{.CPUPerc}}" >> $LOGFILE

# Disk space
df -h /mnt/nvme >> $LOGFILE

# Active alerts
curl -s http://localhost:9090/api/v1/alerts | jq '.data.alerts[] | {alertname, state}' >> $LOGFILE

echo "==========================================" >> $LOGFILE
EOF

chmod +x /usr/local/bin/ziggie-health-check.sh

# Add to cron (run daily at 9 AM)
echo "0 9 * * * /usr/local/bin/ziggie-health-check.sh" | crontab -
```

**Weekly review:**
- Check Grafana dashboards for trends
- Review Prometheus alerts history
- Check disk space growth rate
- Plan capacity upgrades if needed

---

*End of Validation Guide*
*Generated by: HEPHAESTUS, Technical Art Director (Elite Technical Team)*
*Date: 2025-12-28*
