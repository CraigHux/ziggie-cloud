# Ziggie Control Center - Comprehensive Monitoring Recommendations

**Document Version:** 1.0
**Date:** 2025-11-10
**Purpose:** Prevent future configuration issues through proactive monitoring and alerting

---

## Executive Summary

The Ziggie Control Center experienced configuration detection failures that could have been prevented through proper monitoring. This document provides comprehensive monitoring guidance across health checks, configuration validation, frontend and backend monitoring, alerting rules, and implementation recommendations.

---

## Section 1: Health Check Endpoints

### Primary Backend Health Endpoint

**Endpoint:** `GET http://127.0.0.1:54112/api/health`

**Expected Response:**
- **Status Code:** 200 (OK)
- **Response Body:**
```json
{
  "status": "healthy"
}
```

**Monitoring Configuration:**
- **Frequency:** Every 5 minutes
- **Timeout:** 5 seconds
- **Retry Logic:** 3 attempts with 10-second intervals
- **Alert Threshold:** Failure on 3 consecutive checks

**Rationale:**
This endpoint confirms the backend service is running and responsive. A failing health check indicates the entire control center is inaccessible and requires immediate attention.

---

## Section 2: Configuration Validation

### Frontend Configuration Checks

**Check 1: Frontend .env File Existence**
- **Path:** `C:\Ziggie\control-center\frontend\.env`
- **Requirement:** File must exist
- **Check Frequency:** On deployment, then every hour
- **Alert:** Missing file → CRITICAL

**Check 2: VITE_API_URL Configuration**
- **Expected Value:** `http://127.0.0.1:54112/api`
- **Current Value in .env:** Verify matches
- **Verification Method:** Read .env file and validate format
- **Alert:** Mismatch with backend port → CRITICAL

**Check 3: VITE_WS_URL Configuration**
- **Expected Value:** `ws://127.0.0.1:54112/api/system/ws`
- **Requirement:** Must be valid WebSocket URL format
- **Alert:** Invalid format or port mismatch → CRITICAL

### Backend Configuration Checks

**Check 1: Backend Running on Configured Port**
- **Expected Port:** 54112 (from .env: `PORT=54112`)
- **Verification Method:**
  - Check if port is listening: `netstat -an | findstr 54112`
  - Verify via health endpoint: `curl http://127.0.0.1:54112/api/health`
- **Alert:** Service not listening → CRITICAL

**Check 2: Environment Variable Validation**
- **Required Variables:**
  - `HOST=127.0.0.1`
  - `PORT=54112`
  - `DEBUG=true` (or false in production)
  - `JWT_SECRET` (must be set)
  - `COMFYUI_DIR`, `MEOWPING_DIR`, `AI_AGENTS_ROOT`

**Check 3: Critical Path Validation**
- **COMFYUI_DIR:** `C:\ComfyUI` must exist
- **AI_AGENTS_ROOT:** `C:\Ziggie\ai-agents` must exist
- **MEOWPING_DIR:** `C:\Ziggie` must exist
- **Alert:** Missing path → WARNING

**Check Frequency:**
- On service startup
- Every 15 minutes during operation
- After any configuration change

---

## Section 3: Frontend Monitoring

### Browser-Based Checks

**Check 1: Console Error Monitoring**
- **Metric:** Number of JavaScript errors in browser console
- **Threshold:** 0 errors (any errors are anomalies)
- **Detection Method:**
  - Monitor window.onerror events
  - Track unhandledrejection events
  - Integrate error tracking library (Sentry recommended)
- **Alert:** Any console error → WARNING

**Check 2: API Connection Success Rate**
- **Metric:** Percentage of successful API requests
- **Threshold:** > 99% success rate
- **Target Failure Rate:** < 1%
- **Measurement:**
  - Track all fetch/axios calls
  - Count 2xx vs non-2xx responses
  - Calculate success rate per minute
- **Alert:** Success rate < 95% → WARNING
- **Alert:** Success rate < 80% → CRITICAL

**Check 3: WebSocket Connection Status**
- **Metric:** WebSocket connection state
- **Expected State:** Connected and maintaining connection
- **Check Details:**
  - Monitor connection open/close events
  - Track reconnection attempts
  - Measure connection uptime
- **Alert:** Connection dropped → WARNING
- **Alert:** Cannot reconnect for > 5 minutes → CRITICAL

**Check 4: Page Load Performance**
- **Metrics:**
  - First Contentful Paint (FCP): < 2 seconds
  - Largest Contentful Paint (LCP): < 3 seconds
  - Cumulative Layout Shift (CLS): < 0.1
- **Alert:** FCP > 5 seconds → WARNING
- **Alert:** LCP > 10 seconds → CRITICAL

---

## Section 4: Backend Monitoring

### API Health and Performance Checks

**Check 1: Health Endpoint Response Time**
- **Endpoint:** `GET http://127.0.0.1:54112/api/health`
- **Metric:** Response time in milliseconds
- **Target:** < 500ms for healthy state
- **Yellow Alert (WARNING):** Response time > 2 seconds
- **Red Alert (CRITICAL):** Response time > 5 seconds or timeout
- **Measurement:** Use response headers to get precise timing

**Check 2: System Stats Endpoint**
- **Endpoint:** `GET http://127.0.0.1:54112/api/system/stats`
- **Expected Response Structure:**
```json
{
  "cpu": {
    "usage_percent": 35.2
  },
  "memory": {
    "usage_percent": 52.1
  },
  "disk": {
    "usage_percent": 61.8
  }
}
```

**Validation Checks:**
- **Mock Data Detection:** If `cpu.usage_percent == "0.0"` → CRITICAL
  - This indicates system stats are not collecting real data
  - Backend may be returning hardcoded responses
- **Reasonable Value Range:**
  - CPU usage: 0-100%
  - Memory usage: 0-100%
  - Disk usage: 0-100%
- **Alert:** Any metric showing 0.0% consistently → CRITICAL
- **Alert:** Any metric > 90% → WARNING

**Check 3: Database Connection**
- **Endpoint:** `GET http://127.0.0.1:54112/api/system/stats` (depends on DB)
- **Validation:** Endpoint responds with current system stats (proves DB connection)
- **Alert:** Cannot retrieve stats → CRITICAL (database likely unreachable)

**Check 4: Error Rate Monitoring**
- **Metric:** HTTP 5xx errors in logs
- **Target:** Zero 5xx errors
- **Measurement:** Parse server logs or use error tracking
- **Alert:** 5xx error rate > 0.1% → WARNING
- **Alert:** 5xx error rate > 1% → CRITICAL

**Check 5: Request Latency Distribution**
- **Endpoints to Monitor:**
  - `GET /api/health` < 500ms
  - `GET /api/system/stats` < 1000ms
  - Other API endpoints < 2000ms
- **Percentiles to Track:**
  - p50 (median): baseline
  - p95: < 2x baseline
  - p99: < 5x baseline
- **Alert:** p95 latency > 2 seconds → WARNING
- **Alert:** p99 latency > 5 seconds → CRITICAL

---

## Section 5: Alerting Rules

### Critical Alert Conditions

**CRITICAL Alerts** (Immediate Action Required):

1. **Backend Health Check Failure**
   - Condition: `GET /api/health` fails 3 times in a row
   - Interval: Check every 5 minutes
   - Action: Alert ops team immediately, page on-call engineer
   - Escalation: 5 minutes without response

2. **System Stats Return Mock Data**
   - Condition: CPU usage consistently = 0.0%
   - Interval: Check on every stats request
   - Action: Alert that backend is not collecting real system data
   - Likely Cause: Service restart without proper initialization

3. **WebSocket Disconnection**
   - Condition: WebSocket cannot reconnect for > 5 minutes
   - Action: Alert frontend team, may affect real-time features
   - Escalation: 10 minutes without reconnection

4. **Configuration Mismatch**
   - Condition: .env files have mismatched ports/URLs
   - Interval: Check hourly after deployment
   - Action: Alert deployment team immediately
   - Impact: Frontend cannot communicate with backend

5. **Critical Path Missing**
   - Condition: COMFYUI_DIR or AI_AGENTS_ROOT paths don't exist
   - Interval: Check at startup and every 30 minutes
   - Action: Alert system administrator
   - Impact: Core functionality unavailable

### WARNING Alert Conditions

**WARNING Alerts** (Investigate Within 30 Minutes):

1. **Frontend Console Errors**
   - Condition: Any JavaScript error in browser console
   - Action: Log error details, alert frontend team
   - Context: Include error message, stack trace, timestamp
   - Threshold: Even single error deserves attention

2. **API Response Time Degradation**
   - Condition: `/api/health` response time > 2 seconds
   - Condition: Other API endpoints > 2 seconds
   - Action: Check backend resource utilization
   - Investigation: Look for CPU spikes, memory leaks, slow queries

3. **API Success Rate Drops**
   - Condition: Success rate < 95%
   - Interval: Calculated per 5-minute window
   - Action: Alert backend team
   - Investigation: Check for network issues, service degradation

4. **Memory Usage Warning**
   - Condition: Memory usage > 85%
   - Action: Monitor for memory leak
   - If persistent: Restart backend service

5. **Disk Space Warning**
   - Condition: Disk usage > 85%
   - Action: Alert operations team
   - Investigation: Check for log file accumulation, cache issues

### Escalation Policy

```
Initial Alert (Immediate)
    ↓
5 minutes no response → Escalate to team lead
    ↓
15 minutes no response → Escalate to manager
    ↓
30 minutes no response → Escalate to director
```

---

## Section 6: Simple Monitoring Scripts

### Basic Health Check Script (Bash/PowerShell)

#### Version 1: Basic Health Check (for Bash/Linux)

```bash
#!/bin/bash
# monitoring/health_check.sh
# Purpose: Monitor Ziggie Control Center health
# Usage: ./health_check.sh
# Exit codes: 0 = healthy, 1 = issues found

set -e

BACKEND_URL="http://127.0.0.1:54112"
FRONTEND_CONFIG_PATH="C:\Ziggie\control-center\frontend\.env"
MAX_RESPONSE_TIME=5000  # 5 seconds in ms
FAILED_CHECKS=0

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting health check..."

# Function to print status
print_status() {
  if [ $1 -eq 0 ]; then
    echo "OK: $2"
  else
    echo "ERROR: $2"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
  fi
}

# Check 1: Backend health endpoint
echo "Checking backend health..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/health" 2>/dev/null || echo "000")
if [ "$response" = "200" ]; then
  print_status 0 "Backend responding (HTTP $response)"
else
  print_status 1 "Backend unhealthy (HTTP $response)"
fi

# Check 2: System stats returning real data
echo "Checking system stats..."
stats=$(curl -s "$BACKEND_URL/api/system/stats" 2>/dev/null || echo "{}")
cpu=$(echo "$stats" | grep -o '"usage_percent":[0-9.]*' | head -1 | cut -d':' -f2)

if [ "$cpu" = "0.0" ] || [ -z "$cpu" ]; then
  print_status 1 "System stats returning mock data (CPU: $cpu)"
else
  print_status 0 "System stats returning real data (CPU: $cpu%)"
fi

# Check 3: Frontend .env exists
echo "Checking frontend configuration..."
if [ -f "$FRONTEND_CONFIG_PATH" ]; then
  print_status 0 "Frontend .env file exists"
else
  print_status 1 "Frontend .env file missing"
fi

# Check 4: API URL validation
echo "Validating configuration..."
api_url=$(grep "VITE_API_URL" "$FRONTEND_CONFIG_PATH" 2>/dev/null || echo "")
if [[ "$api_url" == *"54112"* ]]; then
  print_status 0 "Frontend API URL configured correctly"
else
  print_status 1 "Frontend API URL mismatch (found: $api_url)"
fi

# Summary
echo ""
echo "========== Health Check Summary =========="
if [ $FAILED_CHECKS -eq 0 ]; then
  echo "Status: HEALTHY - All checks passed"
  exit 0
else
  echo "Status: ISSUES FOUND - $FAILED_CHECKS check(s) failed"
  exit 1
fi
```

#### Version 2: PowerShell Health Check (for Windows)

```powershell
# monitoring/health_check.ps1
# Purpose: Monitor Ziggie Control Center health
# Usage: .\health_check.ps1
# Exit codes: 0 = healthy, 1 = issues found

param(
    [string]$BackendUrl = "http://127.0.0.1:54112",
    [string]$FrontendEnvPath = "C:\Ziggie\control-center\frontend\.env",
    [int]$MaxResponseTimeMs = 5000
)

$failedChecks = 0
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Write-Host "[$timestamp] Starting health check..."

# Helper function
function Check-Health {
    param(
        [bool]$Passed,
        [string]$Message
    )
    if ($Passed) {
        Write-Host "OK: $Message" -ForegroundColor Green
    } else {
        Write-Host "ERROR: $Message" -ForegroundColor Red
        global:$failedChecks++
    }
}

# Check 1: Backend health endpoint
Write-Host "Checking backend health..."
try {
    $response = Invoke-WebRequest -Uri "$BackendUrl/api/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Check-Health ($response.StatusCode -eq 200) "Backend responding (HTTP $($response.StatusCode))"
} catch {
    Check-Health $false "Backend unhealthy ($_)"
}

# Check 2: System stats returning real data
Write-Host "Checking system stats..."
try {
    $response = Invoke-WebRequest -Uri "$BackendUrl/api/system/stats" -Method GET -TimeoutSec 5 -ErrorAction Stop
    $stats = $response.Content | ConvertFrom-Json
    $cpuUsage = $stats.cpu.usage_percent

    if ($cpuUsage -eq 0.0 -or $null -eq $cpuUsage) {
        Check-Health $false "System stats returning mock data (CPU: $cpuUsage)"
    } else {
        Check-Health $true "System stats returning real data (CPU: $cpuUsage%)"
    }
} catch {
    Check-Health $false "Cannot retrieve system stats ($_)"
}

# Check 3: Frontend .env exists
Write-Host "Checking frontend configuration..."
Check-Health (Test-Path $FrontendEnvPath) "Frontend .env file exists at $FrontendEnvPath"

# Check 4: API URL validation
Write-Host "Validating configuration..."
if (Test-Path $FrontendEnvPath) {
    $envContent = Get-Content $FrontendEnvPath -Raw
    Check-Health ($envContent -like "*54112*") "Frontend API URL configured correctly"
} else {
    Check-Health $false "Cannot validate - .env file missing"
}

# Summary
Write-Host ""
Write-Host "========== Health Check Summary ==========" -ForegroundColor Cyan
if ($failedChecks -eq 0) {
    Write-Host "Status: HEALTHY - All checks passed" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Status: ISSUES FOUND - $failedChecks check(s) failed" -ForegroundColor Red
    exit 1
}
```

### Continuous Monitoring Script

```bash
#!/bin/bash
# monitoring/continuous_monitor.sh
# Purpose: Run health checks at regular intervals
# Usage: ./continuous_monitor.sh

HEALTH_CHECK_SCRIPT="./health_check.sh"
CHECK_INTERVAL=300  # 5 minutes
LOG_FILE="./health_check.log"
ALERT_FILE="./health_alerts.log"

echo "Health check started" >> "$LOG_FILE"

while true; do
  TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

  # Run health check
  if bash "$HEALTH_CHECK_SCRIPT" >> "$LOG_FILE" 2>&1; then
    echo "[$TIMESTAMP] HEALTHY" >> "$LOG_FILE"
  else
    echo "[$TIMESTAMP] UNHEALTHY - Issues detected" >> "$LOG_FILE"
    echo "[$TIMESTAMP] ALERT: Control Center health check failed" >> "$ALERT_FILE"
    # Optional: Send notification (email, Slack, PagerDuty, etc.)
  fi

  # Wait for next check
  sleep "$CHECK_INTERVAL"
done
```

---

## Section 7: Recommended Monitoring Tools

### Quick-Start Monitoring Stack (Recommended)

**For Immediate Implementation (Day 1):**

1. **UptimeRobot** (Free tier available)
   - Cost: Free - $15/month
   - Setup time: 5 minutes
   - Monitors: HTTP endpoints
   - Good for: Backend health checks, simple alerting
   - Dashboard: UptimeRobot.com

2. **Custom Script + Cron** (Already included in this guide)
   - Cost: $0
   - Setup time: 15 minutes
   - Monitors: Any checks you script
   - Good for: Full control, config validation
   - Runs: Locally on the server

**For Comprehensive Monitoring (Week 1):**

3. **Grafana** (Open source, free)
   - Cost: Free (self-hosted) or $9/month (cloud)
   - Setup time: 1-2 hours
   - Monitors: Metrics, logs, availability
   - Good for: Dashboards, long-term trend analysis
   - Website: grafana.com

4. **Prometheus** (Open source, free)
   - Cost: Free (self-hosted)
   - Setup time: 2-3 hours
   - Monitors: Time-series metrics
   - Good for: Backend metrics collection
   - Website: prometheus.io

### Enterprise Monitoring Solutions (Optional)

**Sentry** (Error Tracking for Frontend)
- Cost: Free tier - $100/month+
- Best for: JavaScript errors, error tracking
- Easy integration with React
- Website: sentry.io

**New Relic** (Application Performance Monitoring)
- Cost: Free tier - $500+/month
- Best for: Full APM, infrastructure monitoring
- Comprehensive insights
- Website: newrelic.com

**Datadog** (Observability Platform)
- Cost: $15-100+/user/month
- Best for: Complete observability stack
- Integrates everything
- Website: datadog.com

**PagerDuty** (Incident Response)
- Cost: Free tier - $50+/month
- Best for: Alerting and on-call management
- Integrates with monitoring tools
- Website: pagerduty.com

### Comparison Matrix

| Tool | Cost | Setup Time | Best For | Learning Curve |
|------|------|-----------|----------|-----------------|
| Custom Script | $0 | 15 min | Full control | Low |
| UptimeRobot | Free-$15 | 5 min | Simple uptime | Very Low |
| Grafana | Free | 1-2 hrs | Dashboards | Medium |
| Prometheus | Free | 2-3 hrs | Metrics | Medium-High |
| Sentry | Free-100 | 30 min | Errors | Low |
| New Relic | Paid | 1 hr | APM | Medium |
| Datadog | Paid | 2-3 hrs | Full stack | High |

### Recommended Path

**Phase 1 (Week 1):**
- Deploy custom health check scripts
- Set up UptimeRobot for basic endpoint monitoring
- Estimated cost: $0-15
- Time to benefit: Immediate

**Phase 2 (Month 1):**
- Add Sentry for frontend error tracking
- Deploy Prometheus for backend metrics
- Set up Grafana dashboards
- Estimated cost: Free
- Time to benefit: 1-2 weeks

**Phase 3 (Ongoing):**
- Consider New Relic or Datadog if company growth requires
- Add PagerDuty for incident management
- Expand monitoring to other services

---

## Section 8: Implementation Checklist

### Immediate Actions (Today)

- [ ] Deploy `health_check.sh` to server
- [ ] Schedule health check in cron: `*/5 * * * * /path/to/health_check.sh >> /var/log/health_check.log 2>&1`
- [ ] Set up UptimeRobot account and add `/api/health` endpoint
- [ ] Create alerts for failed checks
- [ ] Test by stopping backend and verifying alerts fire

### Short-term (This Week)

- [ ] Integrate Sentry SDK in frontend code
- [ ] Configure Sentry error reporting
- [ ] Deploy Prometheus on monitoring server
- [ ] Create Prometheus scrape configs for backend
- [ ] Deploy Grafana with basic dashboards

### Medium-term (This Month)

- [ ] Document alert response procedures
- [ ] Create runbooks for common failures
- [ ] Train team on monitoring tools
- [ ] Set up PagerDuty for on-call rotation
- [ ] Review logs and optimize alert thresholds

### Long-term (This Quarter)

- [ ] Implement distributed tracing (Jaeger)
- [ ] Add synthetic monitoring (API transaction monitoring)
- [ ] Create automated remediation (auto-restart services)
- [ ] Establish SLAs and track SLI/SLO metrics
- [ ] Regular review and improvement of monitoring

---

## Section 9: Key Metrics Dashboard

### Recommended Dashboard Components

**System Health View**
```
┌─────────────────────────────────────────┐
│ Backend Health Status                   │
│ Status: [GREEN/RED] HTTP 200/XXX       │
│ Response Time: 234ms (Target: <500ms)  │
│ Last Check: 2 minutes ago               │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ System Resources                        │
│ CPU Usage: 35.2% (OK)                  │
│ Memory Usage: 52.1% (OK)               │
│ Disk Usage: 61.8% (OK)                 │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Frontend Status                         │
│ Console Errors: 0 (OK)                 │
│ API Success Rate: 99.8% (OK)           │
│ WebSocket: Connected (OK)              │
└─────────────────────────────────────────┘
```

**Configuration Status View**
```
┌─────────────────────────────────────────┐
│ Configuration Checks                    │
│ ✓ Backend .env Valid                   │
│ ✓ Frontend .env Valid                  │
│ ✓ Port 54112 Listening                 │
│ ✓ All Required Paths Present           │
└─────────────────────────────────────────┘
```

---

## Section 10: Troubleshooting Guide

### Common Monitoring Scenarios

**Scenario 1: Health Check Returns 404**
```
Symptom: GET /api/health returns 404 Not Found
Root Cause: Backend service crashed or restarted with errors
Solution:
1. SSH to server
2. Check if Python process is running: ps aux | grep python
3. Check backend logs: tail -f logs/backend.log
4. Restart backend: systemctl restart control-center-backend
5. Monitor health check for 5 minutes
```

**Scenario 2: CPU Usage Shows 0.0%**
```
Symptom: System stats endpoint returns "cpu.usage_percent": 0.0
Root Cause: Backend not collecting real metrics (mock data being returned)
Solution:
1. Restart backend service
2. Ensure psutil library is installed: pip install psutil
3. Check backend logs for import errors
4. Verify backend has permission to read system stats
5. Re-test /api/system/stats endpoint
```

**Scenario 3: Frontend API Requests Failing**
```
Symptom: Frontend shows API errors, console shows CORS/connection errors
Root Cause: Port mismatch between frontend .env and backend
Solution:
1. Check frontend .env: grep VITE_API_URL .env
2. Check backend is running: curl http://127.0.0.1:54112/api/health
3. Verify backend port 54112: netstat -an | grep 54112
4. Update frontend .env if needed: VITE_API_URL=http://127.0.0.1:54112/api
5. Rebuild frontend: npm run build
```

**Scenario 4: WebSocket Disconnection Issues**
```
Symptom: WebSocket connection drops intermittently
Root Cause: Network timeout, firewall rules, or backend issues
Solution:
1. Check firewall allows 54112: sudo ufw status
2. Verify WebSocket endpoint: ws://127.0.0.1:54112/api/system/ws
3. Check backend logs for connection errors
4. Test WebSocket with: wscat -c ws://127.0.0.1:54112/api/system/ws
5. Increase WebSocket timeout if needed
```

---

## Conclusion

Implementing these monitoring recommendations will provide:
- Early detection of configuration issues
- Rapid response to service failures
- Visibility into system health
- Data-driven optimization insights
- Peace of mind through automated surveillance

**Start with the basic health check script and UptimeRobot today. Add more sophisticated monitoring as the system grows.**

---

## Appendix: File Locations Reference

### Configuration Files
- Backend config: `C:\Ziggie\control-center\backend\.env`
- Frontend config: `C:\Ziggie\control-center\frontend\.env`
- Backend main: `C:\Ziggie\control-center\backend\app.py`

### Log Locations
- Backend logs: `C:\Ziggie\control-center\backend\logs\` (if exists)
- Frontend logs: Browser console (DevTools)

### Health Check Endpoints
- Backend health: `http://127.0.0.1:54112/api/health`
- System stats: `http://127.0.0.1:54112/api/system/stats`

### Monitoring Scripts Location
- Health check: `C:\Ziggie\control-center\scripts\health_check.sh`
- Continuous monitor: `C:\Ziggie\control-center\scripts\continuous_monitor.sh`

---

**Document prepared for Ziggie Control Center Operations Team**
