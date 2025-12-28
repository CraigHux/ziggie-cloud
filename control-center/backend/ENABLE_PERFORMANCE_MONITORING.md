# How to Enable Performance Monitoring

## Quick Setup (5 minutes)

### Step 1: Import the Performance Router

Edit `main.py` and add the performance router:

```python
# Add this import
from api import performance

# Add this line with other router includes
app.include_router(performance.router)
```

### Step 2: Verify It's Working

Start the server and check:

```bash
# Start server
python main.py

# In another terminal, test the endpoint
curl http://localhost:54112/api/performance/metrics
```

You should see:
```json
{
  "success": true,
  "timestamp": "2025-11-10T...",
  "metrics": {
    "total_queries": 0,
    "slow_queries": 0,
    "avg_query_time": 0,
    "queries_by_endpoint": {}
  }
}
```

### Step 3: Test with Real Requests

Make some API calls and check metrics:

```bash
# Make some requests
curl "http://localhost:54112/api/agents?page=1&page_size=50"
curl "http://localhost:54112/api/knowledge/files?page=1&page_size=50"
curl "http://localhost:54112/api/services?page=1&page_size=10"

# Check metrics again
curl http://localhost:54112/api/performance/metrics
```

Now you should see:
```json
{
  "metrics": {
    "total_queries": 3,
    "slow_queries": 0,
    "avg_query_time": 45.2,
    "queries_by_endpoint": {
      "GET /api/agents": {
        "count": 1,
        "total_time": 42.5,
        "avg_time": 42.5,
        "slow_count": 0
      },
      ...
    }
  }
}
```

### Step 4: Check Performance Summary

```bash
curl http://localhost:54112/api/performance/summary
```

Returns:
```json
{
  "success": true,
  "summary": {
    "total_queries": 3,
    "slow_queries": 0,
    "slow_query_percentage": 0.0,
    "avg_query_time_ms": 45.2,
    "performance_grade": "A",
    "slowest_endpoint": {
      "name": "GET /api/agents",
      "avg_time_ms": 42.5
    }
  },
  "recommendations": [...]
}
```

## Advanced Configuration

### Change Slow Query Threshold

```bash
# Set to 150ms instead of default 100ms
curl -X PUT "http://localhost:54112/api/performance/threshold?threshold_ms=150"
```

### View Slow Queries

```bash
# Get last 20 slow queries
curl "http://localhost:54112/api/performance/slow-queries?limit=20"
```

### Export Metrics

```bash
# Export to timestamped JSON file
curl -X POST http://localhost:54112/api/performance/export
```

Returns:
```json
{
  "success": true,
  "message": "Metrics exported successfully",
  "filepath": "C:\\Ziggie\\control-center\\backend\\logs\\performance_metrics_20251110_142530.json"
}
```

### Reset Metrics

```bash
# Clear all collected metrics
curl -X POST http://localhost:54112/api/performance/reset
```

## Monitoring Dashboard Setup

### Option 1: Use FastAPI Docs

Visit: http://localhost:54112/docs#/performance

- Interactive API testing
- All endpoints available
- Real-time testing

### Option 2: Create Custom Dashboard

Example using React/Next.js:

```javascript
// components/PerformanceMonitor.jsx
import { useEffect, useState } from 'react';

export function PerformanceMonitor() {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      const res = await fetch('http://localhost:54112/api/performance/summary');
      const data = await res.json();
      setMetrics(data.summary);
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

  if (!metrics) return <div>Loading...</div>;

  return (
    <div className="performance-dashboard">
      <h2>Performance Grade: {metrics.performance_grade}</h2>
      <div>
        <p>Total Queries: {metrics.total_queries}</p>
        <p>Slow Queries: {metrics.slow_queries} ({metrics.slow_query_percentage}%)</p>
        <p>Avg Query Time: {metrics.avg_query_time_ms}ms</p>
      </div>
      {metrics.slowest_endpoint && (
        <div>
          <h3>Slowest Endpoint</h3>
          <p>{metrics.slowest_endpoint.name}: {metrics.slowest_endpoint.avg_time_ms}ms</p>
        </div>
      )}
    </div>
  );
}
```

### Option 3: Use Existing Monitoring Tools

**Prometheus Integration:**
```python
# Add to main.py
from prometheus_client import Counter, Histogram, generate_latest

query_counter = Counter('api_queries_total', 'Total API queries')
query_duration = Histogram('api_query_duration_seconds', 'API query duration')

@app.get("/metrics")
async def metrics():
    return generate_latest()
```

**Grafana Dashboard:**
- Import metrics from /api/performance/metrics
- Create time-series graphs
- Set up alerts for slow queries

## Alerting Setup

### Simple Email Alerts

```python
# Add to utils/performance.py
import smtplib
from email.message import EmailMessage

def send_alert(message):
    if monitor._metrics["slow_query_percentage"] > 20:
        msg = EmailMessage()
        msg.set_content(f"High slow query rate: {message}")
        msg["Subject"] = "Performance Alert"
        msg["To"] = "admin@example.com"
        # Send email...
```

### Slack Webhook Alerts

```python
import requests

def send_slack_alert(message):
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    requests.post(webhook_url, json={"text": message})
```

## Logging Configuration

### Enable Detailed Logging

Edit `main.py`:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)

# Set performance logger to DEBUG for detailed info
logging.getLogger("performance").setLevel(logging.DEBUG)
```

### View Slow Query Log

```bash
# Real-time monitoring
tail -f logs/slow_queries.log

# Last 50 lines
tail -50 logs/slow_queries.log

# Search for specific endpoint
grep "GET /api/agents" logs/slow_queries.log
```

## Production Deployment

### Environment Variables

```bash
# .env
SLOW_QUERY_THRESHOLD_MS=100
PERFORMANCE_EXPORT_DIR=/var/log/control-center/performance
ENABLE_PERFORMANCE_MONITORING=true
```

### Systemd Service

```ini
# /etc/systemd/system/control-center.service
[Unit]
Description=Control Center Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/control-center/backend
Environment="SLOW_QUERY_THRESHOLD_MS=100"
ExecStart=/usr/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Create logs directory
RUN mkdir -p logs

EXPOSE 54112

CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "54112:54112"
    volumes:
      - ./logs:/app/logs
    environment:
      - SLOW_QUERY_THRESHOLD_MS=100
```

## Troubleshooting

### Performance Router Not Found

**Error:** `ModuleNotFoundError: No module named 'api.performance'`

**Solution:**
```bash
# Verify file exists
ls api/performance.py

# Check imports in main.py
grep "from api import performance" main.py
```

### Metrics Not Updating

**Issue:** Metrics show 0 queries after making requests

**Solution:**
1. Verify decorators are applied:
```python
@track_performance(endpoint="GET /api/agents", query_type="file_scan")
async def list_all_agents(...):
```

2. Check imports:
```python
from utils.performance import track_performance
```

3. Restart server to apply changes

### Slow Query Log Empty

**Issue:** No entries in `logs/slow_queries.log`

**Solutions:**
1. Check threshold: `curl "http://localhost:54112/api/performance/metrics"`
2. Make queries that exceed threshold (>100ms)
3. Verify log directory exists: `mkdir -p logs`
4. Check file permissions

### High Memory Usage

**Issue:** Performance monitoring using too much memory

**Solution:**
```python
# In utils/performance.py, reduce log retention
SLOW_QUERY_LOG_SIZE = 50  # Instead of 100

# Or clear metrics periodically
import schedule
schedule.every().hour.do(reset_performance_stats)
```

## Best Practices

### 1. Regular Monitoring
- Check metrics daily
- Review slow queries weekly
- Export metrics monthly for archival

### 2. Threshold Tuning
- Start with 100ms threshold
- Adjust based on your SLA requirements
- Different thresholds for different endpoints

### 3. Alerting
- Alert on >20% slow query rate
- Alert on any query >1000ms
- Alert on degrading performance trends

### 4. Metrics Archival
```bash
# Cron job to export metrics daily
0 0 * * * curl -X POST http://localhost:54112/api/performance/export
```

### 5. Performance Testing
```bash
# Load testing with Apache Bench
ab -n 1000 -c 10 "http://localhost:54112/api/agents?page=1&page_size=50"

# Check metrics after load test
curl http://localhost:54112/api/performance/summary
```

---

**Next:** See `DB_OPTIMIZATION_REPORT.md` for complete documentation
