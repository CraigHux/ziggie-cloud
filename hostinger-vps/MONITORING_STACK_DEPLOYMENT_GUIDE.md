# MONITORING STACK DEPLOYMENT GUIDE

> **Target**: Ziggie Command Center - 18-Service Docker Stack
> **Stack**: Prometheus, Grafana, Loki, Promtail, Alertmanager
> **Deployment**: Production-ready monitoring with alerts

---

## TABLE OF CONTENTS

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Deployment Steps](#deployment-steps)
4. [Dashboard Access](#dashboard-access)
5. [Alert Configuration](#alert-configuration)
6. [SNS Integration](#sns-integration)
7. [Troubleshooting](#troubleshooting)
8. [Maintenance](#maintenance)

---

## ARCHITECTURE OVERVIEW

```text
┌─────────────────────────────────────────────────────────────┐
│                    MONITORING ARCHITECTURE                  │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Prometheus  │────▶│ Alertmanager │────▶│  AWS SNS     │
│  (Metrics)   │     │  (Routing)   │     │  (Notify)    │
└──────────────┘     └──────────────┘     └──────────────┘
        │                                          │
        │                                          ▼
        │            ┌──────────────┐     ┌──────────────┐
        └───────────▶│   Grafana    │     │   Slack      │
                     │ (Dashboards) │     │   Email      │
                     └──────────────┘     │   SMS        │
                             │            └──────────────┘
                             ▼
                     ┌──────────────┐
                     │     Loki     │
                     │    (Logs)    │
                     └──────────────┘
                             ▲
                             │
                     ┌──────────────┐
                     │   Promtail   │
                     │ (Collection) │
                     └──────────────┘
                             ▲
                             │
            ┌────────────────┴────────────────┐
            │                                 │
    ┌──────────────┐               ┌──────────────┐
    │   Docker     │               │   System     │
    │  Containers  │               │    Logs      │
    └──────────────┘               └──────────────┘
```

---

## PREREQUISITES

### 1. System Requirements

- **Hostinger KVM 4**: 4 vCPU, 16GB RAM, 200GB NVMe
- **Docker**: Version 24.0+
- **Docker Compose**: Version 2.20+
- **Disk Space**: 30GB minimum for logs/metrics (30-day retention)

### 2. Environment Variables

Create `.env` file in `/hostinger-vps/`:

```bash
# Grafana
GRAFANA_USER=admin
GRAFANA_PASSWORD=<strong-password>

# SMTP (for email alerts)
SMTP_USERNAME=<gmail-account>
SMTP_PASSWORD=<app-password>

# Slack
SLACK_WEBHOOK_URL=<webhook-url>

# AWS (for SNS integration)
AWS_ACCESS_KEY_ID=<from-secrets-manager>
AWS_SECRET_ACCESS_KEY=<from-secrets-manager>
AWS_ACCOUNT_ID=<your-account-id>

# Domain
VPS_DOMAIN=ziggie.cloud
```

### 3. Required Exporters

The following exporters must be added to `docker-compose.yml`:

- **cAdvisor** (container metrics)
- **Node Exporter** (host metrics)
- **PostgreSQL Exporter** (database metrics)
- **MongoDB Exporter** (document store metrics)
- **Redis Exporter** (cache metrics)
- **Nginx Exporter** (proxy metrics)
- **Blackbox Exporter** (endpoint probes)

---

## DEPLOYMENT STEPS

### Phase 1: Add Missing Exporters

Add these services to `docker-compose.yml`:

```yaml
# Container Metrics
cadvisor:
  image: gcr.io/cadvisor/cadvisor:latest
  container_name: ziggie-cadvisor
  restart: unless-stopped
  ports:
    - "8080:8080"
  volumes:
    - /:/rootfs:ro
    - /var/run:/var/run:ro
    - /sys:/sys:ro
    - /var/lib/docker/:/var/lib/docker:ro
  networks:
    - ziggie-network

# Host Metrics
node-exporter:
  image: prom/node-exporter:latest
  container_name: ziggie-node-exporter
  restart: unless-stopped
  ports:
    - "9100:9100"
  command:
    - '--path.rootfs=/host'
  volumes:
    - /:/host:ro,rslave
  networks:
    - ziggie-network

# PostgreSQL Metrics
postgres-exporter:
  image: prometheuscommunity/postgres-exporter:latest
  container_name: ziggie-postgres-exporter
  restart: unless-stopped
  ports:
    - "9187:9187"
  environment:
    - DATA_SOURCE_NAME=postgresql://ziggie:${POSTGRES_PASSWORD}@postgres:5432/ziggie?sslmode=disable
  networks:
    - ziggie-network
  depends_on:
    postgres:
      condition: service_healthy

# MongoDB Metrics
mongodb-exporter:
  image: percona/mongodb_exporter:latest
  container_name: ziggie-mongodb-exporter
  restart: unless-stopped
  ports:
    - "9216:9216"
  environment:
    - MONGODB_URI=mongodb://ziggie:${MONGO_PASSWORD}@mongodb:27017
  networks:
    - ziggie-network
  depends_on:
    mongodb:
      condition: service_healthy

# Redis Metrics
redis-exporter:
  image: oliver006/redis_exporter:latest
  container_name: ziggie-redis-exporter
  restart: unless-stopped
  ports:
    - "9121:9121"
  environment:
    - REDIS_ADDR=redis:6379
    - REDIS_PASSWORD=${REDIS_PASSWORD}
  networks:
    - ziggie-network
  depends_on:
    redis:
      condition: service_healthy

# Nginx Metrics
nginx-exporter:
  image: nginx/nginx-prometheus-exporter:latest
  container_name: ziggie-nginx-exporter
  restart: unless-stopped
  ports:
    - "9113:9113"
  command:
    - '-nginx.scrape-uri=http://nginx:80/stub_status'
  networks:
    - ziggie-network
  depends_on:
    - nginx

# Endpoint Probes
blackbox-exporter:
  image: prom/blackbox-exporter:latest
  container_name: ziggie-blackbox-exporter
  restart: unless-stopped
  ports:
    - "9115:9115"
  volumes:
    - ./blackbox/blackbox.yml:/etc/blackbox_exporter/config.yml:ro
  networks:
    - ziggie-network

# Alertmanager
alertmanager:
  image: prom/alertmanager:latest
  container_name: ziggie-alertmanager
  restart: unless-stopped
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

# AWS CloudWatch Exporter (YACE)
yace-exporter:
  image: ghcr.io/nerdswords/yet-another-cloudwatch-exporter:latest
  container_name: ziggie-yace-exporter
  restart: unless-stopped
  ports:
    - "5000:5000"
  environment:
    - AWS_REGION=eu-north-1
    - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
    - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
  volumes:
    - ./yace/config.yml:/tmp/config.yml:ro
  networks:
    - ziggie-network
```

Add volume:
```yaml
volumes:
  alertmanager_data:
```

### Phase 2: Create Blackbox Exporter Config

Create `blackbox/blackbox.yml`:

```yaml
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: [200, 201, 202, 204]
      method: GET
      follow_redirects: true
      preferred_ip_protocol: "ip4"

  tcp_connect:
    prober: tcp
    timeout: 5s
```

### Phase 3: Deploy Stack

```bash
cd /path/to/hostinger-vps

# 1. Validate configuration
docker compose config

# 2. Pull images
docker compose pull

# 3. Start databases first (with health checks)
docker compose up -d postgres mongodb redis

# Wait 15 seconds for health checks
sleep 15

# 4. Start all services
docker compose up -d

# 5. Verify all containers running
docker compose ps

# 6. Check logs
docker compose logs -f prometheus grafana loki
```

### Phase 4: Verify Deployment

```bash
# 1. Check Prometheus targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health != "up")'

# 2. Check Grafana
curl -s http://localhost:3000/api/health

# 3. Check Loki
curl -s http://localhost:3100/ready

# 4. Check Alertmanager
curl -s http://localhost:9093/-/healthy
```

---

## DASHBOARD ACCESS

### URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://ziggie.cloud:3000 | admin / ${GRAFANA_PASSWORD} |
| **Prometheus** | http://ziggie.cloud:9090 | None |
| **Alertmanager** | http://ziggie.cloud:9093 | None |
| **Loki** | http://ziggie.cloud:3100 | None (API only) |

### Pre-configured Dashboards

| Dashboard | Description | Key Metrics |
|-----------|-------------|-------------|
| **Container Overview** | All container health | CPU, Memory, Restarts |
| **Resource Usage** | Host + containers | CPU, RAM, Disk, Network |
| **Database Performance** | Postgres, Mongo, Redis | Connections, Queries, Cache hit rate |
| **API Latency** | Ziggie services | P50/P95/P99 latency, Error rates |
| **Error Rates** | Application errors | 4xx/5xx rates by service |
| **Logs Overview** | Centralized logs | Log levels, Error timeline |

### Accessing Dashboards

1. Navigate to Grafana: http://ziggie.cloud:3000
2. Login with admin credentials
3. Go to **Dashboards** → **Ziggie** folder
4. Select dashboard from list

---

## ALERT CONFIGURATION

### Alert Categories

| Category | File | Key Alerts | Severity |
|----------|------|------------|----------|
| **Infrastructure** | `alerts/infrastructure.yml` | CPU, Memory, Disk, Container down | Critical/Warning |
| **Databases** | `alerts/databases.yml` | Connection pools, Slow queries | Critical/Warning |
| **Applications** | `alerts/applications.yml` | API errors, High latency | Critical/Warning |
| **AWS** | `alerts/aws.yml` | S3, Lambda, EC2 | Warning |
| **Monitoring** | `alerts/monitoring.yml` | Prometheus down, Loki issues | Critical/Warning |

### Alert Thresholds

| Metric | Warning | Critical | Duration |
|--------|---------|----------|----------|
| **CPU Usage** | >80% | >95% | 5m / 2m |
| **Memory Usage** | >85% | >95% | 5m / 2m |
| **Disk Usage** | >80% | >90% | 5m / 2m |
| **API Latency P95** | >2s | >5s | 5m / 2m |
| **Error Rate** | >5% | >10% | 5m / 2m |
| **Container Down** | N/A | Down | 1m |
| **Database Down** | N/A | Down | 1m |

### Testing Alerts

```bash
# 1. Send test alert to Prometheus
curl -X POST http://localhost:9093/api/v1/alerts -H 'Content-Type: application/json' -d '[{
  "labels": {
    "alertname": "TestAlert",
    "severity": "warning",
    "service": "test"
  },
  "annotations": {
    "summary": "Test alert from deployment",
    "description": "This is a test alert to verify Alertmanager configuration"
  }
}]'

# 2. Check Alertmanager UI
open http://localhost:9093

# 3. Verify Slack notification received
```

---

## SNS INTEGRATION

### Setup Steps

1. **Create SNS Topics** (AWS Console or Terraform):
   ```bash
   aws sns create-topic --name ziggie-critical-alerts --region eu-north-1
   aws sns create-topic --name ziggie-warning-alerts --region eu-north-1
   aws sns create-topic --name ziggie-database-alerts --region eu-north-1
   ```

2. **Subscribe Endpoints**:
   ```bash
   # Email
   aws sns subscribe --topic-arn arn:aws:sns:eu-north-1:ACCOUNT_ID:ziggie-critical-alerts \
     --protocol email --notification-endpoint team@ziggie.cloud

   # SMS (critical only)
   aws sns subscribe --topic-arn arn:aws:sns:eu-north-1:ACCOUNT_ID:ziggie-critical-alerts \
     --protocol sms --notification-endpoint +1234567890
   ```

3. **Deploy SNS Forwarder** (optional, see `sns-integration.yml`)

4. **Update Alertmanager Config** with webhook receivers

5. **Test SNS**:
   ```bash
   aws sns publish --topic-arn arn:aws:sns:eu-north-1:ACCOUNT_ID:ziggie-critical-alerts \
     --subject "Test Alert" --message "Testing SNS integration"
   ```

---

## TROUBLESHOOTING

### Prometheus Not Scraping Targets

```bash
# 1. Check target status
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health != "up")'

# 2. Check Prometheus logs
docker logs ziggie-prometheus | tail -50

# 3. Verify target reachable from Prometheus container
docker exec ziggie-prometheus wget -O- http://ziggie-api:8000/metrics
```

### Grafana Not Showing Data

```bash
# 1. Test datasource connection
curl -u admin:${GRAFANA_PASSWORD} http://localhost:3000/api/datasources

# 2. Test Prometheus query
curl 'http://localhost:9090/api/v1/query?query=up'

# 3. Check Grafana logs
docker logs ziggie-grafana | tail -50
```

### Loki Not Receiving Logs

```bash
# 1. Check Promtail is running
docker logs ziggie-promtail | tail -50

# 2. Test Loki ingestion
curl -X POST http://localhost:3100/loki/api/v1/push -H "Content-Type: application/json" \
  -d '{"streams": [{"stream": {"job": "test"}, "values": [["'"$(date +%s)000000000"'", "test log"]]}]}'

# 3. Query logs
curl 'http://localhost:3100/loki/api/v1/query?query={job="test"}'
```

### Alerts Not Firing

```bash
# 1. Check alert rules loaded
curl http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[] | select(.state == "firing")'

# 2. Check Alertmanager receiving alerts
curl http://localhost:9093/api/v1/alerts

# 3. Verify Slack webhook
curl -X POST ${SLACK_WEBHOOK_URL} -H 'Content-Type: application/json' \
  -d '{"text":"Test alert from Ziggie monitoring"}'
```

---

## MAINTENANCE

### Daily Tasks

- [ ] Review critical alerts in Grafana
- [ ] Check container restart counts
- [ ] Monitor disk usage growth

### Weekly Tasks

- [ ] Review alert false positives
- [ ] Check Prometheus TSDB compaction
- [ ] Verify backup retention (30 days)
- [ ] Review slow query logs

### Monthly Tasks

- [ ] Tune alert thresholds based on patterns
- [ ] Rotate Grafana admin password
- [ ] Update dashboard panels based on usage
- [ ] Review and archive old logs (>30 days)

### Backup Configuration

```bash
#!/bin/bash
# backup-monitoring-configs.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/backup/monitoring/$DATE"

mkdir -p $BACKUP_DIR

# Backup Prometheus config
docker exec ziggie-prometheus tar czf - /etc/prometheus > $BACKUP_DIR/prometheus.tar.gz

# Backup Grafana dashboards
docker exec ziggie-grafana tar czf - /var/lib/grafana/dashboards > $BACKUP_DIR/grafana.tar.gz

# Backup Alertmanager config
docker exec ziggie-alertmanager tar czf - /etc/alertmanager > $BACKUP_DIR/alertmanager.tar.gz

# Sync to S3
aws s3 sync /backup/monitoring/ s3://ziggie-backups/monitoring/
```

---

## COST OPTIMIZATION

### Metrics Retention

- **Default**: 30 days (configured in `prometheus.yml`)
- **Adjustment**: Change `--storage.tsdb.retention.time` flag
- **Storage**: ~100MB per day (for 18 services)

### Log Retention

- **Default**: 30 days (configured in `loki-config.yml`)
- **Adjustment**: Modify `retention_period` in limits_config
- **Storage**: ~500MB per day (all services)

### AWS Costs

- **SNS**: $0.50/million notifications (~$5/month)
- **CloudWatch**: Free tier (10 metrics) or $0.30/metric/month
- **S3 Backups**: ~$1/month (30 days retention)

**Estimated Monthly Cost**: $10-15 for monitoring stack

---

## RESOURCES

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Tutorials](https://grafana.com/tutorials/)
- [Loki Setup Guide](https://grafana.com/docs/loki/latest/)
- [Alertmanager Config](https://prometheus.io/docs/alerting/latest/configuration/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Last Updated**: 2025-12-28
**Maintained By**: L1 Strategic Research Agent (Monitoring Stack Optimization)
