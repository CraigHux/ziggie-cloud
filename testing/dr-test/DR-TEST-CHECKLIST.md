# Ziggie Disaster Recovery Test Checklist

> **Document Version**: 1.0
> **Created**: 2025-12-28
> **Frequency**: Quarterly
> **Owner**: Ziggie Infrastructure Team

---

## Purpose

This checklist provides a structured procedure for conducting quarterly disaster recovery tests of the Ziggie ecosystem. Following this checklist ensures consistent, repeatable, and verifiable DR testing.

---

## Pre-Test Requirements

### Environment Verification

| Requirement | Verification Command | Expected Result | Verified |
|-------------|---------------------|-----------------|----------|
| SSH access to VPS | `ssh ziggie@82.25.112.73 echo "OK"` | Returns "OK" | [ ] |
| Docker running | `docker ps` | Lists containers | [ ] |
| PostgreSQL container | `docker ps \| grep postgres` | Container running | [ ] |
| MongoDB container | `docker ps \| grep mongodb` | Container running | [ ] |
| Redis container | `docker ps \| grep redis` | Container running | [ ] |
| n8n container | `docker ps \| grep n8n` | Container running | [ ] |
| Grafana container | `docker ps \| grep grafana` | Container running | [ ] |
| AWS CLI configured | `aws sts get-caller-identity` | Returns identity | [ ] |
| S3 bucket accessible | `aws s3 ls s3://ziggie-assets-prod/` | Lists contents | [ ] |

### Documentation Check

| Document | Location | Current | Reviewed |
|----------|----------|---------|----------|
| DR Runbook | `C:\Ziggie\docs\DISASTER-RECOVERY-RUNBOOK.md` | v1.0 | [ ] |
| Backup Scripts | `C:\Ziggie\hostinger-vps\backup\scripts\` | v1.0 | [ ] |
| This Checklist | `C:\Ziggie\testing\dr-test\DR-TEST-CHECKLIST.md` | v1.0 | [ ] |

### Notification

| Stakeholder | Notification Method | Notified |
|-------------|--------------------| ---------|
| Infrastructure Owner | Email/Slack | [ ] |
| On-call Engineer | Slack | [ ] |
| DR Test documented in calendar | Calendar | [ ] |

---

## Test Execution Procedure

### Phase 1: Preparation (10 minutes)

#### Step 1.1: Connect to VPS
```bash
ssh ziggie@82.25.112.73
```
- [ ] Connected successfully
- [ ] Verified user: `whoami` returns `ziggie`

#### Step 1.2: Navigate to Test Directory
```bash
cd /opt/ziggie/testing/dr-test
# OR if testing from Windows, upload the script first:
# scp C:/Ziggie/testing/dr-test/run-full-dr-test.sh ziggie@82.25.112.73:/opt/ziggie/testing/dr-test/
```
- [ ] Directory exists
- [ ] Test script present

#### Step 1.3: Verify Container Status
```bash
docker compose ps
```
| Container | Expected Status | Actual Status | Pass |
|-----------|-----------------|---------------|------|
| ziggie-postgres | Up | | [ ] |
| ziggie-mongodb | Up | | [ ] |
| ziggie-redis | Up | | [ ] |
| ziggie-n8n | Up | | [ ] |
| ziggie-grafana | Up | | [ ] |

#### Step 1.4: Record Baseline Metrics
```bash
# PostgreSQL table count
docker exec ziggie-postgres psql -U ziggie -d ziggie -t -c \
  "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';"

# MongoDB document count
docker exec ziggie-mongodb mongosh --quiet --eval \
  "db.getSiblingDB('ziggie').stats().objects"

# Redis key count
docker exec ziggie-redis redis-cli DBSIZE
```

| Database | Baseline Count | Recorded |
|----------|----------------|----------|
| PostgreSQL Tables | | [ ] |
| MongoDB Documents | | [ ] |
| Redis Keys | | [ ] |

---

### Phase 2: Backup Tests (15 minutes)

#### Step 2.1: Run Full DR Test Script
```bash
chmod +x run-full-dr-test.sh
./run-full-dr-test.sh 2>&1 | tee dr-test-output.log
```
- [ ] Script executed without errors
- [ ] Output log created

#### Step 2.2: Verify PostgreSQL Backup

| Test | Command | Expected | Actual | Pass |
|------|---------|----------|--------|------|
| Backup Created | `ls -la test-backups/postgres/*.dump` | File exists | | [ ] |
| File Size > 0 | `stat -c%s test-backups/postgres/*.dump` | > 0 bytes | | [ ] |
| Tables Matched | Compare with baseline | Match | | [ ] |

#### Step 2.3: Verify MongoDB Backup

| Test | Command | Expected | Actual | Pass |
|------|---------|----------|--------|------|
| Backup Created | `ls -la test-backups/mongodb/*.archive` | File exists | | [ ] |
| File Size > 0 | `stat -c%s test-backups/mongodb/*.archive` | > 0 bytes | | [ ] |
| Docs Matched | Compare with baseline | Match | | [ ] |

#### Step 2.4: Verify Redis Backup

| Test | Command | Expected | Actual | Pass |
|------|---------|----------|--------|------|
| Backup Created | `ls -la test-backups/redis/*.rdb` | File exists | | [ ] |
| File Size > 0 | `stat -c%s test-backups/redis/*.rdb` | > 0 bytes | | [ ] |

#### Step 2.5: Verify n8n Backup

| Test | Command | Expected | Actual | Pass |
|------|---------|----------|--------|------|
| Backup Created | `ls -la test-backups/n8n/*.json` | File exists | | [ ] |
| Valid JSON | `jq empty test-backups/n8n/*.json` | No error | | [ ] |
| Workflows Found | `grep -c '"name"' test-backups/n8n/*.json` | > 0 | | [ ] |

#### Step 2.6: Verify Grafana Backup

| Test | Command | Expected | Actual | Pass |
|------|---------|----------|--------|------|
| Backup Dir Created | `ls -la test-backups/grafana/` | Directory exists | | [ ] |
| Dashboard Files | `ls test-backups/grafana/*/dashboard_*.json` | Files exist | | [ ] |

---

### Phase 3: Restore Tests (20 minutes)

#### Step 3.1: PostgreSQL Restore Test

**Test Method**: Restore to isolated test database, verify, then cleanup.

```bash
# Create test database
docker exec ziggie-postgres psql -U ziggie -c "CREATE DATABASE ziggie_dr_test;"

# Restore
cat test-backups/postgres/*.dump | docker exec -i ziggie-postgres \
  pg_restore -U ziggie -d ziggie_dr_test --no-owner --no-privileges

# Verify
docker exec ziggie-postgres psql -U ziggie -d ziggie_dr_test -t -c \
  "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';"

# Cleanup
docker exec ziggie-postgres psql -U ziggie -c "DROP DATABASE ziggie_dr_test;"
```

| Step | Expected | Actual | Pass |
|------|----------|--------|------|
| Test DB Created | Success | | [ ] |
| Restore Completed | No errors | | [ ] |
| Table Count Matches | = Baseline | | [ ] |
| Cleanup Completed | DB dropped | | [ ] |

#### Step 3.2: MongoDB Restore Test

**Test Method**: Restore to different namespace, verify, then cleanup.

```bash
# Restore to test namespace
cat test-backups/mongodb/*.archive | docker exec -i ziggie-mongodb \
  mongorestore --archive --gzip \
  --nsFrom='ziggie.*' --nsTo='ziggie_dr_test.*' --drop

# Verify
docker exec ziggie-mongodb mongosh --quiet --eval \
  "db.getSiblingDB('ziggie_dr_test').stats().objects"

# Cleanup
docker exec ziggie-mongodb mongosh --quiet --eval \
  "db.getSiblingDB('ziggie_dr_test').dropDatabase()"
```

| Step | Expected | Actual | Pass |
|------|----------|--------|------|
| Restore Completed | No errors | | [ ] |
| Document Count Matches | = Baseline | | [ ] |
| Cleanup Completed | DB dropped | | [ ] |

#### Step 3.3: Redis Restore Verification

**Test Method**: Verify backup file integrity (actual restore requires restart).

```bash
# Check RDB file header
file test-backups/redis/*.rdb

# Verify file not corrupted
hexdump -C test-backups/redis/*.rdb | head -5
```

| Test | Expected | Actual | Pass |
|------|----------|--------|------|
| File Type | Redis RDB | | [ ] |
| Header Valid | REDIS | | [ ] |

#### Step 3.4: n8n Workflow Validation

```bash
# Validate JSON structure
jq '.' test-backups/n8n/*.json > /dev/null

# Count workflows
jq 'length' test-backups/n8n/*.json
```

| Test | Expected | Actual | Pass |
|------|----------|--------|------|
| JSON Valid | No errors | | [ ] |
| Workflow Count | > 0 | | [ ] |

---

### Phase 4: S3 Sync Test (10 minutes)

#### Step 4.1: Upload Test Backup to S3

```bash
# Create test file
echo "DR Test $(date)" > /tmp/dr_test.txt

# Upload to S3
aws s3 cp /tmp/dr_test.txt s3://ziggie-assets-prod/backups/dr-test/

# Verify upload
aws s3 ls s3://ziggie-assets-prod/backups/dr-test/

# Cleanup
aws s3 rm s3://ziggie-assets-prod/backups/dr-test/dr_test.txt
```

| Step | Expected | Actual | Pass |
|------|----------|--------|------|
| Upload Succeeded | No error | | [ ] |
| File Listed in S3 | File visible | | [ ] |
| Cleanup Completed | File removed | | [ ] |

---

### Phase 5: RTO Measurement (5 minutes)

#### Step 5.1: Record Total Test Time

| Metric | Value | Recorded |
|--------|-------|----------|
| Test Start Time | | [ ] |
| Test End Time | | [ ] |
| Total Duration | | [ ] |
| RTO Target | 4 hours (14,400 sec) | N/A |
| RTO Met? | Yes/No | [ ] |

---

## Post-Test Actions

### Cleanup

| Task | Command | Completed |
|------|---------|-----------|
| Remove test backups | `rm -rf test-backups/*` | [ ] |
| Remove test databases | Verified in restore tests | [ ] |
| Remove S3 test files | Verified in S3 test | [ ] |

### Documentation

| Task | Location | Completed |
|------|----------|-----------|
| Review test report | `reports/dr-test-report-*.md` | [ ] |
| Update DR Runbook | If issues found | [ ] |
| File issues | GitHub Issues | [ ] |
| Update ecosystem status | ZIGGIE-ECOSYSTEM-MASTER-STATUS-V5.md | [ ] |

### Notification

| Stakeholder | Method | Notified |
|-------------|--------|----------|
| Infrastructure Owner | Email with report | [ ] |
| Team | Slack summary | [ ] |

---

## Test Result Summary

### Overall Score

| Category | Passed | Failed | Skipped | Total |
|----------|--------|--------|---------|-------|
| Backup Tests | | | | 5 |
| Restore Tests | | | | 5 |
| S3 Tests | | | | 1 |
| **TOTAL** | | | | 11 |

### Pass Rate Calculation

```
Pass Rate = (Passed / (Passed + Failed)) * 100 = ____%
```

### RTO/RPO Assessment

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| RTO | 4 hours | | PASS/FAIL |
| RPO | 24 hours | 24 hours (daily backups) | PASS |

---

## Sign-Off

### Test Execution Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Test Executor | | | |
| Infrastructure Owner | | | |

### Approval

| Item | Approved | Comments |
|------|----------|----------|
| All critical tests passed | [ ] | |
| RTO target met | [ ] | |
| No data loss during tests | [ ] | |
| Runbook accurate | [ ] | |

### Next Scheduled Test

| Item | Value |
|------|-------|
| Next Test Date | (Current date + 3 months) |
| Scheduled By | |
| Calendar Entry Created | [ ] |

---

## Appendix A: Quick Reference Commands

```bash
# Full automated test
./run-full-dr-test.sh

# Quick test (skip restore)
./run-full-dr-test.sh --skip-restore

# Quiet mode (minimal output)
./run-full-dr-test.sh --quiet

# View latest report
cat reports/dr-test-report-*.md | tail -100
```

---

## Appendix B: Troubleshooting

### Container Not Running

```bash
# Start specific container
docker compose up -d <service_name>

# View container logs
docker logs <container_name> --tail=50
```

### Backup Script Fails

```bash
# Check script permissions
chmod +x run-full-dr-test.sh

# Run with debug
bash -x run-full-dr-test.sh
```

### S3 Access Denied

```bash
# Verify credentials
aws sts get-caller-identity

# Check bucket policy
aws s3api get-bucket-policy --bucket ziggie-assets-prod
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-28 | DR Test Agent | Initial release |

---

**END OF CHECKLIST**
