# Ziggie Monitoring Stack Documentation

> **L1 Agent Deliverable**: Comprehensive monitoring configuration for production
> **Stack**: Prometheus + Grafana + Loki + AlertManager
> **Services Monitored**: 18 Docker containers + AWS resources
> **Last Updated**: 2025-12-28

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prometheus Configuration](#prometheus-configuration)
3. [AlertManager Configuration](#alertmanager-configuration)
4. [Grafana Dashboards](#grafana-dashboards)
5. [Loki Log Aggregation](#loki-log-aggregation)
6. [AWS Integration](#aws-integration)
7. [Alert Rules Reference](#alert-rules-reference)
8. [Deployment Instructions](#deployment-instructions)
9. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
+------------------+     +------------------+     +------------------+
|   18 Docker      |     |   AWS Resources  |     |   Host System    |
|   Containers     |     |   (S3, Lambda)   |     |   (VPS)          |
+--------+---------+     +--------+---------+     +--------+---------+
         |                        |                        |
         v                        v                        v
+--------+---------+     +--------+---------+     +--------+---------+
|   cAdvisor       |     |   YACE Exporter  |     |   Node Exporter  |
|   (Container)    |     |   (CloudWatch)   |     |   (Host)         |
+--------+---------+     +--------+---------+     +--------+---------+
         |                        |                        |
         +------------------------+------------------------+
                                  |
                                  v
                         +--------+---------+
                         |   Prometheus     |
                         |   (Metrics)      |
                         +--------+---------+
                                  |
              +-------------------+-------------------+
              |                   |                   |
              v                   v                   v
     +--------+---------+ +-------+--------+ +-------+--------+
     |   Grafana        | |  AlertManager  | |   Recording    |
     |   (Dashboards)   | |  (Alerts)      | |   Rules        |
     +------------------+ +--------+-------+ +----------------+
                                   |
                    +--------------+--------------+
                    |              |              |
                    v              v              v
               +----+----+   +----+----+   +----+----+
               |  Slack  |   |  Email  |   | PagerDuty|
               +---------+   +---------+   +----------+

+------------------+     +------------------+
|   Docker Logs    |     |   System Logs    |
+--------+---------+     +--------+---------+
         |                        |
         v                        v
+--------+------------------------+---------+
|              Promtail                     |
|         (Log Collection)                  |
+-------------------+-----------------------+
                    |
                    v
          +---------+---------+
          |       Loki        |
          |  (Log Aggregation)|
          +---------+---------+
                    |
                    v
          +---------+---------+
          |     Grafana       |
          |  (Log Explorer)   |
          +-------------------+
```

---

## Prometheus Configuration

### File Location

```
C:\Ziggie\hostinger-vps\prometheus\prometheus.yml
```

### Scrape Targets (18 Services)

| Job Name | Target | Port | Tier |
|----------|--------|------|------|
| prometheus | localhost | 9090 | monitoring |
| cadvisor | cadvisor | 8080 | infrastructure |
| node-exporter | node-exporter | 9100 | infrastructure |
| postgres | postgres-exporter | 9187 | database |
| mongodb | mongodb-exporter | 9216 | database |
| redis | redis-exporter | 9121 | database |
| n8n | n8n | 5678 | workflow |
| ollama | ollama | 11434 | ai |
| flowise | flowise | 3000 | ai |
| open-webui | open-webui | 8080 | ai |
| ziggie-api | ziggie-api | 8000 | application |
| mcp-gateway | mcp-gateway | 8080 | application |
| sim-studio | sim-studio | 8001 | application |
| nginx | nginx-exporter | 9113 | infrastructure |
| grafana | grafana | 3000 | monitoring |
| loki | loki | 3100 | monitoring |
| portainer | portainer | 9000 | management |
| aws-cloudwatch | yace-exporter | 5000 | cloud |
| blackbox-http | blackbox-exporter | 9115 | probes |

### Storage Configuration

```yaml
storage.tsdb.retention.time: 30d
storage.tsdb.path: /prometheus
```

Estimated storage: ~1GB per 10 million samples.

---

## AlertManager Configuration

### File Location

```
C:\Ziggie\hostinger-vps\alertmanager\alertmanager.yml
```

### Alert Routing

| Severity | Channel | Group Wait | Repeat Interval |
|----------|---------|------------|-----------------|
| critical | #ziggie-critical + Email | 10s | 1h |
| warning | #ziggie-warnings | 2m | 6h |
| info | #ziggie-alerts | 30s | 4h |

### Alert Categories

| Category | Channel | Examples |
|----------|---------|----------|
| Infrastructure | #ziggie-infra | Host CPU, Memory, Disk |
| Database | #ziggie-database | Postgres, MongoDB, Redis |
| Application | #ziggie-app | API errors, latency |
| AWS | #ziggie-aws | S3, Lambda, costs |

### Inhibition Rules

1. Critical alerts suppress warnings for the same service
2. HostDown suppresses all container alerts
3. PostgresDown suppresses dependent application alerts

---

## Grafana Dashboards

### File Locations

```
C:\Ziggie\hostinger-vps\grafana\dashboards\
  - container-overview.json
  - database-performance.json
  - api-latency.json
  - error-rates.json
```

### Dashboard Overview

#### 1. Container Overview (ziggie-containers)

- **Running Containers**: Count of active containers
- **Host CPU/Memory/Disk**: Gauge widgets
- **Container CPU Usage**: Time series by container
- **Container Memory Usage**: Time series by container
- **Network I/O**: RX/TX per container
- **Disk I/O**: Read/Write per container
- **Container Status Table**: CPU%, Memory, Uptime

#### 2. Database Performance (ziggie-databases)

**PostgreSQL Section**:
- Status (UP/DOWN)
- Active Connections
- Transactions/sec
- Cache Hit Ratio
- Database Size
- Deadlocks (1h)
- Transaction Rate graph
- Row Operations graph

**MongoDB Section**:
- Status (UP/DOWN)
- Current Connections
- Operations/sec
- Data Size

**Redis Section**:
- Status (UP/DOWN)
- Memory Usage gauge
- Connected Clients
- Hit Rate
- Commands/sec
- Total Keys

#### 3. API Latency (ziggie-api-latency)

- Requests/sec
- P50/P95 Latency stats
- Error Rate
- Latency Percentiles graph (P50, P90, P95, P99)
- Requests by Endpoint
- Requests by Status Code
- Endpoint Performance Table

#### 4. Error Rates (ziggie-errors)

- Error Rate gauges per service
- Error Rate Trend (all services)
- HTTP Status Breakdown (pie charts)
- Error Logs from Loki

---

## Loki Log Aggregation

### Configuration Files

```
C:\Ziggie\hostinger-vps\loki\loki-config.yml
C:\Ziggie\hostinger-vps\promtail\promtail-config.yml
```

### Retention Policy

| Setting | Value | Description |
|---------|-------|-------------|
| retention_period | 720h (30 days) | Default log retention |
| max_query_length | 30d | Maximum query timespan |
| ingestion_rate_mb | 10 | Max MB/s ingestion |
| per_stream_rate_limit | 3MB | Per-stream rate limit |
| max_entries_limit_per_query | 50000 | Max log entries returned |

### Log Labels

| Label | Description | Example |
|-------|-------------|---------|
| job | Log source type | containerlogs, nginx, syslog |
| service | Container name | ziggie-api, ziggie-postgres |
| tier | Service tier | database, application, ai |
| level | Log severity | error, warn, info, debug |
| container_id | Docker container ID | abc123... |

### Log Queries (LogQL)

```logql
# All errors from Ziggie API
{service="ziggie-api"} |= "error"

# Database connection errors
{tier="database"} |~ "connection|timeout"

# 5xx errors in last hour
{job="nginx", log_type="access"} | json | status >= 500

# Critical errors across all services
{job="containerlogs"} |~ "(?i)(critical|fatal)"
```

---

## AWS Integration

### YACE CloudWatch Exporter

**Configuration**: `C:\Ziggie\hostinger-vps\yace\yace-config.yml`

### Monitored AWS Resources

| Service | Metrics | Poll Interval |
|---------|---------|---------------|
| S3 | BucketSizeBytes, NumberOfObjects | 24h |
| Lambda | Invocations, Duration, Errors, Throttles | 60s |
| EC2 (GPU) | CPUUtilization, Network, Disk | 60s |
| Secrets Manager | CallCount | 5m |
| Billing | EstimatedCharges | 6h |

### Cost Alerts

| Threshold | Alert Level | Action |
|-----------|-------------|--------|
| $25 (50%) | Info | Review usage |
| $40 (80%) | Warning | Optimize resources |
| $50 (100%) | Critical | Immediate action |

### GPU Instance Monitoring

- Idle detection: CPU < 5% for 30 minutes
- Running time alert: > 4 hours
- Spot interruption warning: 2-minute notice

---

## Alert Rules Reference

### Location

```
C:\Ziggie\hostinger-vps\prometheus\alerts\
  - infrastructure.yml
  - databases.yml
  - applications.yml
  - aws.yml
```

### Critical Alerts (Immediate Action Required)

| Alert | Condition | For |
|-------|-----------|-----|
| HostCriticalCpuUsage | CPU > 95% | 2m |
| HostCriticalMemoryUsage | Memory > 95% | 2m |
| HostCriticalDiskUsage | Disk > 90% | 2m |
| ContainerOOMKilled | OOM events > 0 | 0m |
| ContainerRestartLoop | Restarts > 3 in 15m | 0m |
| PostgresDown | pg_up == 0 | 1m |
| MongoDBDown | mongodb_up == 0 | 1m |
| RedisDown | redis_up == 0 | 1m |
| ZiggieApiDown | up == 0 | 1m |
| MCPGatewayDown | up == 0 | 1m |
| NginxDown | nginx_up == 0 | 1m |
| AWSSpotInstanceInterruption | warning == 1 | 0m |
| AWSCostBudgetExceeded | charges > $50 | 1h |

### Warning Alerts (Investigate Soon)

| Alert | Condition | For |
|-------|-----------|-----|
| HostHighCpuUsage | CPU > 80% | 5m |
| HostHighMemoryUsage | Memory > 85% | 5m |
| HostHighDiskUsage | Disk > 80% | 5m |
| HostDiskWillFillIn24Hours | prediction < 0 | 30m |
| PostgresHighConnections | connections > 80 | 5m |
| PostgresSlowQueries | avg > 1s | 5m |
| RedisHighMemoryUsage | > 90% of max | 5m |
| ZiggieApiHighLatency | P95 > 2s | 5m |
| ZiggieApiHighErrorRate | errors > 5% | 5m |
| AWSGPUInstanceIdle | CPU < 5% | 30m |
| AWSLambdaErrors | errors > 0.1/s | 5m |

---

## Deployment Instructions

### Prerequisites

1. Docker and Docker Compose installed
2. AWS credentials configured (for YACE)
3. Slack webhook URL (for alerts)
4. SMTP credentials (for email alerts)

### Deployment Steps

```bash
# 1. Navigate to hostinger-vps directory
cd /opt/ziggie/hostinger-vps

# 2. Create required directories
mkdir -p prometheus/alerts grafana/dashboards loki promtail alertmanager/templates yace

# 3. Copy configuration files
cp prometheus/prometheus.yml /etc/prometheus/
cp prometheus/alerts/*.yml /etc/prometheus/alerts/
cp alertmanager/alertmanager.yml /etc/alertmanager/
cp loki/loki-config.yml /etc/loki/
cp promtail/promtail-config.yml /etc/promtail/

# 4. Set environment variables
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/[REDACTED]
export SMTP_USERNAME=your-smtp-user
export SMTP_PASSWORD=your-smtp-password

# 5. Add monitoring services to docker-compose.yml
# (See docker-compose.monitoring.yml section below)

# 6. Start the stack
docker compose up -d

# 7. Verify services
docker compose ps
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:3000/api/health  # Grafana
curl http://localhost:3100/ready       # Loki
curl http://localhost:9093/-/healthy   # AlertManager
```

### Docker Compose Additions

Add these services to your `docker-compose.yml`:

```yaml
services:
  # Container metrics exporter
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: ziggie-cadvisor
    privileged: true
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    networks:
      - ziggie-network

  # Host metrics exporter
  node-exporter:
    image: prom/node-exporter:latest
    container_name: ziggie-node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    networks:
      - ziggie-network

  # PostgreSQL exporter
  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: ziggie-postgres-exporter
    environment:
      - DATA_SOURCE_NAME=postgresql://ziggie:${POSTGRES_PASSWORD}@postgres:5432/ziggie?sslmode=disable
    ports:
      - "9187:9187"
    depends_on:
      - postgres
    networks:
      - ziggie-network

  # MongoDB exporter
  mongodb-exporter:
    image: percona/mongodb_exporter:latest
    container_name: ziggie-mongodb-exporter
    environment:
      - MONGODB_URI=mongodb://ziggie:${MONGO_PASSWORD}@mongodb:27017
    ports:
      - "9216:9216"
    depends_on:
      - mongodb
    networks:
      - ziggie-network

  # Redis exporter
  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: ziggie-redis-exporter
    environment:
      - REDIS_ADDR=redis://redis:6379
      - REDIS_PASSWORD=${REDIS_PASSWORD}
    ports:
      - "9121:9121"
    depends_on:
      - redis
    networks:
      - ziggie-network

  # Nginx exporter
  nginx-exporter:
    image: nginx/nginx-prometheus-exporter:latest
    container_name: ziggie-nginx-exporter
    command:
      - -nginx.scrape-uri=http://nginx:8080/stub_status
    ports:
      - "9113:9113"
    depends_on:
      - nginx
    networks:
      - ziggie-network

  # AlertManager
  alertmanager:
    image: prom/alertmanager:latest
    container_name: ziggie-alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro
      - ./alertmanager/templates:/etc/alertmanager/templates:ro
      - alertmanager_data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    networks:
      - ziggie-network

  # Blackbox exporter (endpoint probes)
  blackbox-exporter:
    image: prom/blackbox-exporter:latest
    container_name: ziggie-blackbox-exporter
    ports:
      - "9115:9115"
    volumes:
      - ./blackbox/blackbox.yml:/etc/blackbox_exporter/config.yml:ro
    networks:
      - ziggie-network

  # AWS CloudWatch exporter
  yace-exporter:
    image: ghcr.io/nerdswords/yet-another-cloudwatch-exporter:latest
    container_name: ziggie-yace-exporter
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=eu-north-1
    ports:
      - "5000:5000"
    volumes:
      - ./yace/yace-config.yml:/tmp/config.yml:ro
    command:
      - '-config.file=/tmp/config.yml'
    networks:
      - ziggie-network

volumes:
  alertmanager_data:
```

---

## Troubleshooting

### Prometheus Not Scraping Targets

```bash
# Check target health
curl http://localhost:9090/api/v1/targets | jq .

# Check Prometheus logs
docker logs ziggie-prometheus --tail 100

# Verify network connectivity
docker exec ziggie-prometheus wget -qO- http://ziggie-api:8000/metrics
```

### AlertManager Not Sending Alerts

```bash
# Check AlertManager status
curl http://localhost:9093/api/v2/status

# View current alerts
curl http://localhost:9093/api/v2/alerts

# Check Slack webhook
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test alert"}' \
  $SLACK_WEBHOOK_URL
```

### Loki Not Receiving Logs

```bash
# Check Promtail positions
docker exec ziggie-promtail cat /tmp/positions.yaml

# Check Loki readiness
curl http://localhost:3100/ready

# Query recent logs
curl -G -s "http://localhost:3100/loki/api/v1/query" \
  --data-urlencode 'query={job="containerlogs"}' | jq .
```

### Grafana Dashboards Not Loading

```bash
# Check provisioning status
docker logs ziggie-grafana | grep -i provision

# Verify datasource connectivity
curl -u admin:$GRAFANA_PASSWORD \
  http://localhost:3000/api/datasources

# Reload dashboards
curl -X POST -u admin:$GRAFANA_PASSWORD \
  http://localhost:3000/api/admin/provisioning/dashboards/reload
```

### AWS Metrics Not Appearing

```bash
# Check YACE logs
docker logs ziggie-yace-exporter --tail 100

# Verify AWS credentials
docker exec ziggie-yace-exporter aws sts get-caller-identity

# Check CloudWatch access
docker exec ziggie-yace-exporter aws cloudwatch list-metrics \
  --namespace AWS/Lambda --region eu-north-1
```

---

## Maintenance Tasks

### Weekly

1. Review alert trends in Grafana
2. Check disk usage predictions
3. Verify backup metrics are being collected

### Monthly

1. Review and update alert thresholds
2. Archive old logs beyond retention
3. Audit AWS cost trends
4. Update dashboard layouts if needed

### Quarterly

1. Prometheus storage capacity review
2. Alert rule effectiveness review
3. Dashboard usability review
4. Update to latest exporter versions

---

## Files Created

| File | Location | Purpose |
|------|----------|---------|
| prometheus.yml | hostinger-vps/prometheus/ | Main Prometheus config |
| infrastructure.yml | hostinger-vps/prometheus/alerts/ | Infrastructure alerts |
| databases.yml | hostinger-vps/prometheus/alerts/ | Database alerts |
| applications.yml | hostinger-vps/prometheus/alerts/ | Application alerts |
| aws.yml | hostinger-vps/prometheus/alerts/ | AWS alerts |
| alertmanager.yml | hostinger-vps/alertmanager/ | AlertManager routing |
| slack.tmpl | hostinger-vps/alertmanager/templates/ | Slack templates |
| loki-config.yml | hostinger-vps/loki/ | Loki config |
| promtail-config.yml | hostinger-vps/promtail/ | Promtail config |
| yace-config.yml | hostinger-vps/yace/ | AWS exporter config |
| datasources.yml | hostinger-vps/grafana/provisioning/datasources/ | Grafana datasources |
| dashboards.yml | hostinger-vps/grafana/provisioning/dashboards/ | Dashboard provisioning |
| container-overview.json | hostinger-vps/grafana/dashboards/ | Container dashboard |
| database-performance.json | hostinger-vps/grafana/dashboards/ | Database dashboard |
| api-latency.json | hostinger-vps/grafana/dashboards/ | API latency dashboard |
| error-rates.json | hostinger-vps/grafana/dashboards/ | Error rates dashboard |

---

*L1 Monitoring Stack Research Agent - Deliverable Complete*
