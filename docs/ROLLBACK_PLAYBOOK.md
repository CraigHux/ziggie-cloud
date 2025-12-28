# Emergency Rollback Playbook
**Repository**: CraigHux/ziggie-cloud
**Author**: DAEDALUS (Pipeline Architect)
**Created**: 2025-12-28
**Classification**: CRITICAL OPERATIONS

---

## Overview

This playbook provides step-by-step procedures for rolling back failed deployments. Follow these procedures in order of severity.

**Target Rollback Time**: < 60 seconds for automated, < 5 minutes for manual

---

## Quick Decision Matrix

| Scenario | Rollback Type | Time | Command |
|----------|---------------|------|---------|
| Service crashed immediately | Container Restart | 30s | `rollback.yml` (container_restart) |
| API errors after deploy | Previous Commit | 60s | `rollback.yml` (previous_commit) |
| Database migration failed | Specific Commit | 2m | `rollback.yml` (specific_commit) |
| Complete system failure | Full Restore | 5m | Manual procedure |
| Workflow unavailable | Manual Rollback | 5m | SSH + manual steps |

---

## Table of Contents

1. [Automated Rollback Procedures](#automated-rollback-procedures)
2. [Manual Rollback Procedures](#manual-rollback-procedures)
3. [Database Rollback](#database-rollback)
4. [Verification Steps](#verification-steps)
5. [Post-Rollback Actions](#post-rollback-actions)
6. [Rollback Decision Tree](#rollback-decision-tree)

---

## Automated Rollback Procedures

### Level 1: Container Restart (Fastest - 30 seconds)

**When to Use**:
- Service crashed but code is fine
- Memory leak or resource exhaustion
- Temporary network issue
- Container in unhealthy state

**Procedure**:
```bash
# Trigger rollback workflow
gh workflow run rollback.yml \
  -f rollback_type=container_restart \
  -f services="all" \
  -f reason="Service crash - restarting containers"

# Monitor
gh run watch

# Verify (after 30 seconds)
curl https://ziggie.cloud/api/health
```

**What It Does**:
1. Stops affected containers
2. Removes stopped containers
3. Starts fresh containers (same code/config)
4. Waits 15 seconds for stabilization
5. Runs health checks

**Expected Duration**: 30-45 seconds

### Level 2: Previous Commit Rollback (60 seconds)

**When to Use**:
- Deployment introduced bugs
- Breaking API changes
- Configuration errors in latest commit
- Performance degradation

**Procedure**:
```bash
# Check current commit
git log -1 --oneline

# Trigger rollback to previous commit
gh workflow run rollback.yml \
  -f rollback_type=previous_commit \
  -f services="all" \
  -f reason="Deployment introduced API breaking changes"

# Monitor
gh run watch

# Verify
curl https://ziggie.cloud/api/health
```

**What It Does**:
1. Creates backup of current state
2. Checks out code from HEAD~1 (previous commit)
3. Rebuilds Docker images
4. Stops current containers
5. Starts containers with previous code
6. Runs health checks

**Expected Duration**: 60-90 seconds

### Level 3: Specific Commit Rollback (2 minutes)

**When to Use**:
- Need to rollback multiple commits
- Known good commit SHA identified
- Bisecting to find last working version

**Procedure**:
```bash
# Find last known good commit
git log --oneline -10

# Example output:
# abc1234 (HEAD) feat: add new feature (BROKEN)
# def5678 fix: bug fix (BROKEN)
# ghi9012 feat: previous feature (LAST GOOD)

# Trigger rollback to specific commit
gh workflow run rollback.yml \
  -f rollback_type=specific_commit \
  -f target_commit=ghi9012 \
  -f services="all" \
  -f reason="Rolling back to last known good commit before feature X"

# Monitor
gh run watch

# Verify
curl https://ziggie.cloud/api/health
```

**What It Does**:
1. Validates commit SHA exists
2. Creates backup
3. Checks out code from specified commit
4. Rebuilds Docker images
5. Deploys specified version
6. Runs health checks

**Expected Duration**: 2-3 minutes

### Level 4: Selective Service Rollback

**When to Use**:
- Only one service is broken
- Other services working fine
- Want to minimize disruption

**Procedure**:
```bash
# Rollback only ziggie-api
gh workflow run rollback.yml \
  -f rollback_type=previous_commit \
  -f services="ziggie-api" \
  -f reason="API regression - rolling back API only"

# Verify affected service
curl https://ziggie.cloud/api/health

# Verify other services unaffected
curl https://ziggie.cloud/mcp/health
curl https://ziggie.cloud/sim/health
```

**Available Services**:
- `ziggie-api`
- `mcp-gateway`
- `sim-studio`
- `all` (default)

---

## Manual Rollback Procedures

### When GitHub Actions Unavailable

**Scenarios**:
- GitHub Actions down
- Self-hosted runner offline
- Network connectivity issues
- Workflow file corrupted

**Full Manual Rollback**:

```bash
# ============================================================
# STEP 1: SSH to VPS
# ============================================================
ssh root@82.25.112.73

# ============================================================
# STEP 2: Navigate to deployment directory
# ============================================================
cd /opt/ziggie

# ============================================================
# STEP 3: Backup current state
# ============================================================
BACKUP_DIR="backups/manual_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Save current container states
docker ps -a > "$BACKUP_DIR/container_states.txt"

# Save current docker-compose
cp docker-compose.yml "$BACKUP_DIR/"

# Save current commit
git rev-parse HEAD > "$BACKUP_DIR/current_commit.txt"

# ============================================================
# STEP 4: Find last good backup
# ============================================================
ls -lht backups/ | head -5

# Example output:
# drwxr-xr-x 2 root root 4096 Dec 28 12:00 20251228_120000/
# drwxr-xr-x 2 root root 4096 Dec 28 11:30 20251228_113000/

# ============================================================
# STEP 5: Restore from backup (OPTION A)
# ============================================================
RESTORE_FROM="backups/20251228_113000"
cp "$RESTORE_FROM/docker-compose.yml" .

# Restart services
docker compose down
docker compose up -d

# ============================================================
# STEP 6: Rollback code (OPTION B)
# ============================================================
# Check git log
git log --oneline -10

# Rollback to specific commit
git fetch origin
git reset --hard <commit-sha>

# Rebuild services
docker compose build ziggie-api mcp-gateway sim-studio

# Restart
docker compose down
docker compose up -d

# ============================================================
# STEP 7: Verify
# ============================================================
# Wait for startup
sleep 30

# Check containers
docker ps

# Check health
curl http://localhost:8000/health
curl http://localhost:8080/health
curl http://localhost:8001/health

# Check logs
docker compose logs -f --tail=50
```

**Expected Duration**: 3-5 minutes

---

## Database Rollback

### PostgreSQL Schema Rollback

**Scenario**: Database migration failed or caused issues

**Procedure**:

```bash
# SSH to VPS
ssh root@82.25.112.73
cd /opt/ziggie

# ============================================================
# OPTION 1: Restore from automated backup
# ============================================================
# Find backup
BACKUP_DIR="backups/$(ls -t backups/ | head -1)"
ls -lh "$BACKUP_DIR"

# Restore schema only (fast)
docker exec -i ziggie-postgres psql -U ziggie < "$BACKUP_DIR/postgres_schema.sql"

# ============================================================
# OPTION 2: Rollback specific migration
# ============================================================
# If using Alembic (Python)
docker exec -it ziggie-api alembic downgrade -1

# If using manual migrations
docker exec -i ziggie-postgres psql -U ziggie -d ziggie <<EOF
-- Your rollback SQL here
DROP TABLE IF EXISTS new_table;
ALTER TABLE users DROP COLUMN IF EXISTS new_column;
EOF

# ============================================================
# OPTION 3: Full database restore (LAST RESORT)
# ============================================================
# Stop services using database
docker compose stop ziggie-api sim-studio n8n

# Drop and recreate database
docker exec -it ziggie-postgres psql -U ziggie -c "DROP DATABASE ziggie;"
docker exec -it ziggie-postgres psql -U ziggie -c "CREATE DATABASE ziggie;"

# Restore from full backup (if available)
# Note: This requires full database dump, not just schema
docker exec -i ziggie-postgres psql -U ziggie -d ziggie < /path/to/full_backup.sql

# Restart services
docker compose start ziggie-api sim-studio n8n
```

### MongoDB Rollback

```bash
# SSH to VPS
ssh root@82.25.112.73

# Connect to MongoDB
docker exec -it ziggie-mongodb mongosh -u ziggie -p

# List databases
show dbs

# Use database
use ziggie

# Drop problematic collection
db.problematic_collection.drop()

# Or restore from backup
# (Requires mongodump backup)
docker exec -i ziggie-mongodb mongorestore \
  --uri="mongodb://ziggie:password@localhost:27017" \
  --db=ziggie \
  /path/to/backup
```

---

## Verification Steps

After any rollback, verify all critical systems:

### 1. Container Status

```bash
# All containers should be "Up"
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.State}}'

# Expected:
# ziggie-api         Up 2 minutes    running
# ziggie-mcp-gateway Up 2 minutes    running
# ziggie-sim-studio  Up 2 minutes    running
# ziggie-postgres    Up 2 minutes    running (healthy)
# ziggie-mongodb     Up 2 minutes    running (healthy)
# ziggie-redis       Up 2 minutes    running (healthy)
```

### 2. Health Checks

```bash
#!/bin/bash
# health-check.sh

echo "=== Health Checks ==="

# Ziggie API
API_STATUS=$(curl -s http://localhost:8000/health | jq -r '.status')
echo "Ziggie API: $API_STATUS"

# MCP Gateway
MCP_STATUS=$(curl -s http://localhost:8080/health | jq -r '.status')
echo "MCP Gateway: $MCP_STATUS"

# Sim Studio
SIM_STATUS=$(curl -s http://localhost:8001/health | jq -r '.status')
echo "Sim Studio: $SIM_STATUS"

# All should be "healthy"
```

### 3. Database Connectivity

```bash
# PostgreSQL
docker exec ziggie-postgres pg_isready -U ziggie
# Expected: ziggie-postgres:5432 - accepting connections

# Redis
docker exec ziggie-redis redis-cli -a <password> ping
# Expected: PONG

# MongoDB
docker exec ziggie-mongodb mongosh --quiet --eval "db.runCommand('ping').ok"
# Expected: 1
```

### 4. Smoke Tests

```bash
# Test critical API endpoints
curl -X GET https://ziggie.cloud/api/system/info
curl -X GET https://ziggie.cloud/api/agents
curl -X GET https://ziggie.cloud/api/services

# Test MCP Gateway
curl -X GET https://ziggie.cloud/mcp/backends
```

### 5. Log Inspection

```bash
# Check for errors in last 50 lines
docker compose logs --tail=50 | grep -i error

# If errors found, investigate specific service
docker compose logs ziggie-api --tail=100
```

---

## Post-Rollback Actions

### 1. Incident Report

Create incident report in `docs/incidents/`:

```markdown
# Incident Report: <Date>

## Summary
Deployment of commit <SHA> failed, rolled back to <previous-SHA>

## Timeline
- 12:00 UTC: Deployment started
- 12:05 UTC: Health checks failed
- 12:06 UTC: Rollback initiated
- 12:08 UTC: Rollback completed
- 12:10 UTC: Services verified healthy

## Root Cause
<Describe what went wrong>

## Impact
- Services down: 3 minutes
- Affected users: <number or "none - caught in health checks">

## Prevention
- [ ] Add test for <specific issue>
- [ ] Update validation in <stage>
- [ ] Document edge case in <location>
```

### 2. Fix Forward

After rollback, create fix:

```bash
# Create fix branch
git checkout -b fix/deployment-issue-20251228

# Implement fix
<make changes>

# Test locally
docker compose build
docker compose up -d
# Verify fix works

# Commit and push
git add .
git commit -m "fix: resolve deployment issue from 2025-12-28"
git push origin fix/deployment-issue-20251228

# Create PR
gh pr create \
  --title "Fix: Deployment issue from 2025-12-28" \
  --body "Resolves deployment failure. See incident report in docs/incidents/"
```

### 3. Update Monitoring

Add monitoring for issue that caused rollback:

```bash
# Example: Add health check for new endpoint
# In .github/workflows/health-check.yml

- name: Check new endpoint
  run: |
    curl -f https://ziggie.cloud/api/new-endpoint || {
      echo "::error::New endpoint not responding"
      exit 1
    }
```

### 4. Notify Team

```bash
# Via Slack (if configured)
curl -X POST "$SLACK_WEBHOOK_URL" \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "🔄 Rollback completed",
    "attachments": [{
      "color": "warning",
      "fields": [
        {"title": "Reason", "value": "Deployment failed health checks", "short": false},
        {"title": "Status", "value": "Services restored and healthy", "short": true},
        {"title": "Duration", "value": "3 minutes downtime", "short": true}
      ]
    }]
  }'
```

---

## Rollback Decision Tree

```
Deployment Failed
        ↓
┌───────────────────────────────────────┐
│ Are services running?                 │
├───────────────────────────────────────┤
│ YES → Level 1: Container Restart     │
│  NO → Continue...                     │
└───────────────────────────────────────┘
        ↓
┌───────────────────────────────────────┐
│ Is it a code issue?                   │
├───────────────────────────────────────┤
│ YES → Level 2: Previous Commit       │
│  NO → Continue...                     │
└───────────────────────────────────────┘
        ↓
┌───────────────────────────────────────┐
│ Is it a database issue?               │
├───────────────────────────────────────┤
│ YES → Database Rollback               │
│  NO → Continue...                     │
└───────────────────────────────────────┘
        ↓
┌───────────────────────────────────────┐
│ Is it a specific service?             │
├───────────────────────────────────────┤
│ YES → Selective Service Rollback     │
│  NO → Continue...                     │
└───────────────────────────────────────┘
        ↓
┌───────────────────────────────────────┐
│ Is GitHub Actions available?          │
├───────────────────────────────────────┤
│ YES → Level 3: Specific Commit       │
│  NO → Manual Rollback                 │
└───────────────────────────────────────┘
```

---

## Rollback Checklist

Before initiating rollback:

- [ ] Identify affected services
- [ ] Determine rollback type needed
- [ ] Note current commit SHA (for incident report)
- [ ] Check if database migrations are involved
- [ ] Verify backup availability

During rollback:

- [ ] Initiate rollback workflow or manual procedure
- [ ] Monitor rollback progress
- [ ] Watch for errors in logs
- [ ] Time the rollback duration

After rollback:

- [ ] Verify all containers running
- [ ] Run health checks
- [ ] Test critical endpoints
- [ ] Check database connectivity
- [ ] Inspect logs for errors
- [ ] Create incident report
- [ ] Notify team
- [ ] Plan fix forward

---

## Emergency Contacts

| Role | Contact | Availability |
|------|---------|--------------|
| Infrastructure Lead | DAEDALUS | 24/7 |
| DevOps Engineer | TBD | Business hours |
| On-Call Engineer | TBD | 24/7 rotation |

---

## Common Rollback Scenarios

### Scenario 1: API Not Responding

**Symptoms**:
- Health check fails
- 502 Bad Gateway
- Container keeps restarting

**Rollback**:
```bash
gh workflow run rollback.yml \
  -f rollback_type=previous_commit \
  -f services="ziggie-api" \
  -f reason="API not responding - 502 errors"
```

**Duration**: 60-90 seconds

### Scenario 2: Database Migration Failed

**Symptoms**:
- Service starts but errors on DB queries
- Migration logs show errors
- New columns/tables missing

**Rollback**:
```bash
# 1. Rollback code
gh workflow run rollback.yml \
  -f rollback_type=previous_commit \
  -f reason="Database migration failed"

# 2. Rollback database
ssh root@82.25.112.73
docker exec -it ziggie-api alembic downgrade -1
```

**Duration**: 2-3 minutes

### Scenario 3: Memory Leak

**Symptoms**:
- Container using 100% memory
- OOM kills
- Service slowing down over time

**Rollback**:
```bash
# Immediate: Restart containers
gh workflow run rollback.yml \
  -f rollback_type=container_restart \
  -f reason="Memory leak - restarting services"

# Then: Rollback code to find source
gh workflow run rollback.yml \
  -f rollback_type=previous_commit \
  -f reason="Investigating memory leak"
```

**Duration**: 30 seconds (restart), then fix forward

### Scenario 4: Breaking Configuration Change

**Symptoms**:
- Services won't start
- Environment variable errors
- Missing dependencies

**Rollback**:
```bash
# SSH to VPS
ssh root@82.25.112.73
cd /opt/ziggie

# Restore previous docker-compose.yml
BACKUP=$(ls -t backups/ | head -1)
cp "backups/$BACKUP/docker-compose.yml" .

# Restart
docker compose down
docker compose up -d
```

**Duration**: 2-3 minutes

---

## Rollback Testing

Test rollback procedures regularly:

```bash
# Quarterly rollback drill
# 1. Deploy test change
git commit --allow-empty -m "test: rollback drill"
git push origin main

# 2. Wait for deployment
gh run watch

# 3. Trigger rollback
gh workflow run rollback.yml \
  -f rollback_type=previous_commit \
  -f reason="Quarterly rollback drill - test only"

# 4. Verify rollback works
gh run watch

# 5. Document results
echo "Rollback drill successful - <duration>" >> docs/rollback-drills.log
```

---

**Document Version**: 1.0
**Last Updated**: 2025-12-28
**Classification**: CRITICAL OPERATIONS
**Review Schedule**: Quarterly
**Owner**: DAEDALUS (Pipeline Architect)
