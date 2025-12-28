# MONITORING STACK - QUICK REFERENCE

> **Fast lookup guide for Ziggie monitoring stack operators**

---

## 🔗 DASHBOARD URLs

| Service | URL | Login |
|---------|-----|-------|
| **Grafana** | http://ziggie.cloud:3000 | admin / $GRAFANA_PASSWORD |
| **Prometheus** | http://ziggie.cloud:9090 | None |
| **Alertmanager** | http://ziggie.cloud:9093 | None |
| **Loki** | http://ziggie.cloud:3100 | API only |

---

## 📊 GRAFANA DASHBOARDS

| Dashboard | Key Metrics | When to Check |
|-----------|-------------|---------------|
| **Container Overview** | Running containers, CPU, Memory, Restarts | Daily health check |
| **Resource Usage** | Host CPU/Memory/Disk gauges | Capacity planning |
| **Database Performance** | Connections, queries, cache hits | Database slowness |
| **API Latency** | P95 latency, throughput, errors | API performance issues |
| **Error Rates** | 4xx/5xx rates by service | Incident response |
| **Logs Overview** | Log levels, error stream | Debugging |

---

## 🚨 COMMON ALERTS

### Critical Alerts (Immediate Action)

| Alert | Cause | Fix |
|-------|-------|-----|
| **ZiggieApiDown** | API container crashed | `docker restart ziggie-api` |
| **PostgresDown** | Database unreachable | Check DB logs, restart if needed |
| **HostCriticalCpuUsage** | CPU >95% | Identify high CPU process, scale or optimize |
| **HostCriticalMemoryUsage** | Memory >95% | Check for memory leaks, restart containers |
| **ContainerOOMKilled** | Out of memory | Increase container memory limit |
| **ContainerRestartLoop** | Crash loop | Check logs: `docker logs <container>` |

### Warning Alerts (Action within 1 hour)

| Alert | Cause | Fix |
|-------|-------|-----|
| **HostHighCpuUsage** | CPU >80% | Monitor, prepare to scale |
| **HostHighMemoryUsage** | Memory >85% | Review memory usage trends |
| **PostgresHighConnections** | >80 connections | Check connection pooling config |
| **RedisHighMemoryUsage** | Redis >90% full | Increase maxmemory or eviction policy |
| **HighNetworkTraffic** | >100 MB/s | Check for unusual activity |

---

## 🔧 COMMON COMMANDS

### Check Service Health

```bash
# All containers status
docker compose ps

# Specific service logs
docker logs ziggie-<service> --tail 100 -f

# Prometheus targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health != "up")'

# Grafana health
curl -s http://localhost:3000/api/health

# Loki ready
curl -s http://localhost:3100/ready
```

### Restart Services

```bash
# Restart single service
docker restart ziggie-<service>

# Restart monitoring stack
docker compose restart prometheus grafana loki promtail alertmanager

# Reload Prometheus config (no restart)
docker exec ziggie-prometheus kill -HUP 1

# Reload Alertmanager config (no restart)
docker exec ziggie-alertmanager kill -HUP 1
```

### Query Metrics

```bash
# CPU usage (all containers)
curl 'http://localhost:9090/api/v1/query?query=rate(container_cpu_usage_seconds_total{name=~"ziggie-.*"}[5m])'

# Memory usage (all containers)
curl 'http://localhost:9090/api/v1/query?query=container_memory_usage_bytes{name=~"ziggie-.*"}'

# Check for firing alerts
curl 'http://localhost:9090/api/v1/alerts' | jq '.data.alerts[] | select(.state == "firing")'
```

### Query Logs

```bash
# Loki - Recent errors
curl -G -s 'http://localhost:3100/loki/api/v1/query' \
  --data-urlencode 'query={job="ziggie-services",level=~"error|critical"}' \
  --data-urlencode 'limit=10' | jq .

# Loki - Service-specific logs
curl -G -s 'http://localhost:3100/loki/api/v1/query' \
  --data-urlencode 'query={job="ziggie-services",service="ziggie-api"}' \
  --data-urlencode 'limit=20' | jq .
```

### Test Alerts

```bash
# Send test alert
curl -X POST http://localhost:9093/api/v1/alerts -H 'Content-Type: application/json' -d '[{
  "labels": {
    "alertname": "TestAlert",
    "severity": "warning",
    "service": "test"
  },
  "annotations": {
    "summary": "Test alert",
    "description": "Testing alert routing"
  }
}]'

# Check Alertmanager alerts
curl http://localhost:9093/api/v1/alerts | jq .
```

---

## 🎯 ALERT THRESHOLDS

| Metric | Warning | Critical | Duration |
|--------|---------|----------|----------|
| CPU | >80% | >95% | 5m / 2m |
| Memory | >85% | >95% | 5m / 2m |
| Disk | >80% | >90% | 5m / 2m |
| API P95 Latency | >2s | >5s | 5m / 2m |
| Error Rate | >5% | >10% | 5m / 2m |
| Container Down | N/A | Down | 1m |
| Database Down | N/A | Down | 1m |

---

## 📞 ALERT ROUTING

| Severity | Channels | Repeat Interval |
|----------|----------|-----------------|
| **Critical** | Slack + Email + SMS | 1 hour |
| **Warning** | Slack + Email | 6 hours |
| **Info** | Slack | 24 hours |

### Slack Channels

- `#ziggie-critical` - Critical alerts (P0)
- `#ziggie-alerts` - All alerts
- `#ziggie-database` - Database tier
- `#ziggie-infra` - Infrastructure tier
- `#ziggie-app` - Application tier
- `#ziggie-aws` - AWS resources
- `#ziggie-warnings` - Warning-level only

---

## 🛠️ TROUBLESHOOTING

### Prometheus Not Scraping

```bash
# 1. Check target status
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health != "up")'

# 2. Test target reachability
docker exec ziggie-prometheus wget -O- http://<target>:<port>/metrics

# 3. Check Prometheus logs
docker logs ziggie-prometheus | grep -i error
```

### Grafana No Data

```bash
# 1. Test datasource
curl http://localhost:3000/api/datasources -u admin:$GRAFANA_PASSWORD

# 2. Test Prometheus query
curl 'http://localhost:9090/api/v1/query?query=up'

# 3. Check Grafana logs
docker logs ziggie-grafana | grep -i error
```

### Loki Not Receiving Logs

```bash
# 1. Check Promtail status
docker logs ziggie-promtail | tail -50

# 2. Test Loki ingestion
curl -X POST http://localhost:3100/loki/api/v1/push \
  -H "Content-Type: application/json" \
  -d '{"streams": [{"stream": {"job": "test"}, "values": [["'"$(date +%s)000000000"'", "test"]]}]}'

# 3. Query test log
curl 'http://localhost:3100/loki/api/v1/query?query={job="test"}'
```

### Alerts Not Firing

```bash
# 1. Check alert rules loaded
curl http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[] | select(.state == "pending" or .state == "firing")'

# 2. Check Alertmanager
curl http://localhost:9093/api/v1/alerts

# 3. Test Slack webhook
curl -X POST $SLACK_WEBHOOK_URL -H 'Content-Type: application/json' -d '{"text":"Test"}'
```

---

## 📈 PERFORMANCE METRICS

| Component | Memory | CPU | Impact |
|-----------|--------|-----|--------|
| Prometheus | 1 GB | 0.2 vCPU | LOW |
| Grafana | 512 MB | 0.1 vCPU | LOW |
| Loki | 512 MB | 0.1 vCPU | LOW |
| Promtail | 128 MB | 0.05 vCPU | MINIMAL |
| Exporters (8x) | 1.5 GB | 0.4 vCPU | LOW-MEDIUM |
| **Total** | **3.9 GB** | **0.9 vCPU** | 24% of VPS |

---

## 📅 MAINTENANCE SCHEDULE

### Daily (5 minutes)
- [ ] Review critical alerts in Grafana
- [ ] Check container restart counts
- [ ] Monitor disk usage growth

### Weekly (15 minutes)
- [ ] Review alert false positives
- [ ] Check Prometheus TSDB compaction
- [ ] Verify 30-day retention active
- [ ] Review slow query logs

### Monthly (30 minutes)
- [ ] Tune alert thresholds
- [ ] Rotate passwords
- [ ] Update dashboards
- [ ] Archive old logs (>30 days)

---

## 🆘 EMERGENCY CONTACTS

| Issue | Contact | Channel |
|-------|---------|---------|
| **Production Down** | On-call engineer | Slack + SMS |
| **Database Issues** | DBA team | `#ziggie-database` |
| **Infrastructure** | DevOps lead | `#ziggie-infra` |
| **Application Errors** | Dev team lead | `#ziggie-app` |

---

## 📚 REFERENCE DOCS

- **Full Deployment Guide**: `MONITORING_STACK_DEPLOYMENT_GUIDE.md`
- **Optimization Report**: `../docs/MONITORING_STACK_OPTIMIZATION_REPORT.md`
- **Alert Rules**: `prometheus/alerts/*.yml`
- **Dashboards**: `grafana/dashboards/*.json`

---

**Last Updated**: 2025-12-28
**Quick Reference Version**: 1.0
