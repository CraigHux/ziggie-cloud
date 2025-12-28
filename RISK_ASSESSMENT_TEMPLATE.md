# RISK ASSESSMENT TEMPLATE
## Production Deployment Risk Analysis - Protocol v1.1c

**Assessment Date:** [YYYY-MM-DD]
**Status:** [PLANNING | IN PROGRESS | DEPLOYED | RETROSPECTIVE]
**Change Type:** [Security | Feature | Infrastructure | Bug Fix | Performance | Refactoring]
**Risk Level:** [LOW | MEDIUM | HIGH | CRITICAL]
**Assessor Team:** [List L1/L2/L3 agents involved]

---

## EXECUTIVE SUMMARY

[2-3 paragraph summary of what this risk assessment covers]

**Risk Rating:** [LOW | MEDIUM | HIGH | CRITICAL]
**Deployment Status:** [NOT YET DEPLOYED | DEPLOYED | ROLLED BACK]
**Implementation Complexity:** [LOW | MEDIUM | HIGH]
**Rollback Complexity:** [SIMPLE | MEDIUM | COMPLEX]
**Business Impact:** [POSITIVE | NEUTRAL | NEGATIVE with justification]

**Key Risks Identified:**
1. [Risk 1 summary]
2. [Risk 2 summary]
3. [Risk 3 summary]
4. [...]

**Recommendation:** [APPROVE | APPROVE WITH CONDITIONS | DEFER | REJECT]

---

## RISK SCORING MATRIX

### Risk Levels

| Risk Level | Criteria |
|-----------|----------|
| **LOW** | No user impact, easy rollback, well-tested |
| **MEDIUM** | Minor user impact, tested rollback, good test coverage |
| **HIGH** | Significant user impact, complex rollback, partial test coverage |
| **CRITICAL** | System down, data loss possible, no rollback, insufficient testing |

### Risk Calculation

**Risk Score = Likelihood × Impact**

| Score Range | Risk Level |
|-------------|-----------|
| 1-3 | LOW |
| 4-6 | MEDIUM |
| 7-9 | HIGH |
| 10+ | CRITICAL |

### Likelihood Scale

1. **MINIMAL:** < 5% chance
2. **LOW:** 5-25% chance
3. **MEDIUM:** 25-50% chance
4. **HIGH:** 50-75% chance
5. **CRITICAL:** > 75% chance

### Impact Scale

1. **MINIMAL:** No user impact, internal only
2. **LOW:** Minor inconvenience, workaround available
3. **MEDIUM:** Degraded service, affects some users
4. **HIGH:** Service unavailable, affects all users
5. **CRITICAL:** Data loss, security breach, system down

### Overall Assessment: [LOW | MEDIUM | HIGH | CRITICAL]

**Justification:**
- **User Impact:** [Description]
- **Rollback:** [SIMPLE | MEDIUM | COMPLEX]
- **Testing:** [INSUFFICIENT | PARTIAL | COMPREHENSIVE]
- **Breaking Changes:** [NONE | MINOR | MAJOR]
- **Technical Debt:** [NONE | MINOR | MODERATE | SIGNIFICANT]
- **[Other factors]:** [...]

---

## CHANGE SUMMARY

### What Will Be Changed

**Files Modified:**
- **File:** [Path to file]
  - **Lines:** [Line numbers or count]
  - **Change:** [Description of change]
  - **Impact:** [What this affects]

**Files Created:**
- **File:** [Path to new file]
  - **Purpose:** [Why this file is needed]
  - **Size:** [Lines of code or file size]

**Files Deleted:**
- **File:** [Path to deleted file]
  - **Reason:** [Why removing this file]
  - **Impact:** [What depends on this file]

**Dependencies Changed:**
- **Package:** [Package name]
  - **From:** [Old version]
  - **To:** [New version]
  - **Reason:** [Why upgrading/downgrading]

**Configuration Changed:**
- **Setting:** [Configuration key]
  - **From:** [Old value]
  - **To:** [New value]
  - **Impact:** [What this affects]

**Total Impact:** [X files, Y lines, Z dependencies]

---

### Why Change Is Needed

**Problem Statement:**
[Describe the problem being solved]

**Root Cause:**
[What is the underlying cause of the problem?]

**Current Impact:**
- [Impact 1]
- [Impact 2]
- [...]

**Proposed Solution:**
[High-level description of how this change solves the problem]

**Alternatives Considered:**
1. **Alternative 1:** [Description]
   - **Pros:** [...]
   - **Cons:** [...]
   - **Why not chosen:** [...]

2. **Alternative 2:** [Description]
   - **Pros:** [...]
   - **Cons:** [...]
   - **Why not chosen:** [...]

---

### Expected Outcome

**After Deployment:**
- [Outcome 1]
- [Outcome 2]
- [...]

**Success Metrics:**
- [Metric 1: How to measure success]
- [Metric 2: ...]
- [...]

---

## TECHNICAL RISKS

### Risk Template

**For each technical risk, use this format:**

### Risk [N]: [Risk Name]
**Likelihood:** [MINIMAL | LOW | MEDIUM | HIGH | CRITICAL] | **Impact:** [MINIMAL | LOW | MEDIUM | HIGH | CRITICAL] | **Overall Risk:** [LOW | MEDIUM | HIGH | CRITICAL]

**Description:**
[What is the risk? What could go wrong?]

**Failure Scenarios:**
1. [Scenario 1]
2. [Scenario 2]
3. [...]

**Impact:**
- [Impact if this risk materializes]
- [Who/what is affected]
- [How severe is the impact]

**Mitigation:**
1. **[Mitigation strategy 1]:**
   - [Implementation details]
   - [How this reduces risk]

2. **[Mitigation strategy 2]:**
   - [Implementation details]
   - [How this reduces risk]

**Residual Risk:** [MINIMAL | LOW | MEDIUM | HIGH] - [Explanation]

**Testing Required:**
- [Test case 1]
- [Test case 2]
- [...]

**Owner:** [Who is responsible for this risk]
**Timeline:** [When to address]

---

### Example Technical Risks to Consider

1. **Breaking Changes to API**
2. **Performance Degradation**
3. **Data Loss or Corruption**
4. **Dependency Conflicts**
5. **Backward Compatibility**
6. **Database Migration Failures**
7. **Configuration Errors**
8. **Resource Exhaustion (CPU, Memory, Disk)**
9. **Race Conditions**
10. **Deadlocks or Blocking**
11. **Third-Party Service Dependencies**
12. **Network Failures**
13. **Timeout Issues**
14. **Error Handling Gaps**
15. **Logging Gaps**

---

## SECURITY RISKS

### Security Risk Template

### Security Risk [N]: [Risk Name]
**Before:** [Risk level before change] | **After:** [Risk level after change] | **Risk Change:** [+INCREASED | -REDUCED | =UNCHANGED]

**Description:**
[What is the security risk?]

**Threat Model:**
- **Attacker Profile:** [Who might exploit this?]
- **Attack Vector:** [How could they attack?]
- **Exploitability:** [LOW | MEDIUM | HIGH]
- **Impact if Exploited:** [What happens if successful?]

**Vulnerability Assessment:**
- **Before Change:** [Security posture before]
- **After Change:** [Security posture after]
- **Net Effect:** [Better | Worse | Same]

**Mitigation:**
1. [Security control 1]
2. [Security control 2]
3. [...]

**Residual Risk:** [LOW | MEDIUM | HIGH] - [Explanation]

**Security Testing Required:**
- [Security test 1]
- [Security test 2]
- [...]

**Security Sign-Off Required:** [YES | NO]
**Security Reviewer:** [L1 SECURITY or other]

---

### Example Security Risks to Consider

1. **Authentication Bypass**
2. **Authorization Escalation**
3. **Injection Attacks (SQL, Command, etc.)**
4. **Cross-Site Scripting (XSS)**
5. **Cross-Site Request Forgery (CSRF)**
6. **Insecure Deserialization**
7. **Sensitive Data Exposure**
8. **Security Misconfiguration**
9. **Weak Cryptography**
10. **Insufficient Logging/Monitoring**
11. **Rate Limiting Bypass**
12. **DoS/DDoS Vulnerabilities**
13. **Session Management Issues**
14. **Insecure Dependencies**
15. **API Security Weaknesses**

---

## PERFORMANCE RISKS

### Performance Risk Template

### Performance Risk [N]: [Risk Name]
**Before:** [Metric before] | **After:** [Expected metric after] | **Change:** [+IMPROVED | -DEGRADED | =UNCHANGED]

**Description:**
[What is the performance risk?]

**Metrics Affected:**
- **Response Time:** [Before → After]
- **Throughput:** [Before → After]
- **CPU Usage:** [Before → After]
- **Memory Usage:** [Before → After]
- **Disk I/O:** [Before → After]
- **Network I/O:** [Before → After]

**Impact:**
- [Impact on user experience]
- [Impact on system capacity]
- [Impact on costs]

**Mitigation:**
1. [Performance optimization 1]
2. [Performance optimization 2]
3. [...]

**Residual Risk:** [LOW | MEDIUM | HIGH] - [Explanation]

**Performance Testing Required:**
- [Load test scenario 1]
- [Load test scenario 2]
- [...]

**Performance Targets:**
- [Target 1: P95 response time < Xms]
- [Target 2: Throughput > Y requests/second]
- [Target 3: ...]

---

### Example Performance Risks to Consider

1. **Response Time Degradation**
2. **Throughput Reduction**
3. **Memory Leaks**
4. **CPU Spikes**
5. **Database Query Performance**
6. **N+1 Query Problems**
7. **Cache Inefficiency**
8. **Disk I/O Bottlenecks**
9. **Network Latency**
10. **Concurrency Issues**
11. **Resource Contention**
12. **Scalability Limits**

---

## TESTING COVERAGE

### What Was Tested

**Unit Tests:**
- [Test 1: Description]
- [Test 2: Description]
- [...]
- **Total:** [X unit tests]

**Integration Tests:**
- [Test 1: Description]
- [Test 2: Description]
- [...]
- **Total:** [X integration tests]

**End-to-End Tests:**
- [Test 1: Description]
- [Test 2: Description]
- [...]
- **Total:** [X E2E tests]

**Manual Tests:**
- [Test 1: Description]
- [Test 2: Description]
- [...]
- **Total:** [X manual tests]

**Coverage Metrics:**
- **Line Coverage:** [X%]
- **Branch Coverage:** [X%]
- **Function Coverage:** [X%]
- **Endpoint Coverage:** [X out of Y endpoints]

---

### What Was NOT Tested

**Untested Scenarios:**
- [Scenario 1: Why not tested?]
- [Scenario 2: Why not tested?]
- [...]

**Testing Gaps:**
- [Gap 1: What's missing?]
- [Gap 2: What's missing?]
- [...]

**Deferred Testing:**
- [Test 1: Why deferred? When will it be done?]
- [Test 2: Why deferred? When will it be done?]
- [...]

---

### Regression Tests Needed

**Immediate Regression Tests (Before Production):**
1. [Test 1]
   - **Purpose:** [What this verifies]
   - **Effort:** [Time estimate]
   - **Owner:** [Who runs this]

2. [Test 2]
   - **Purpose:** [...]
   - **Effort:** [...]
   - **Owner:** [...]

**Total Regression Testing Effort:** [X hours/days]

---

### CI/CD Integration Needed

**Current State:** [Tests are manual | Partially automated | Fully automated]

**Required CI/CD Integration:**

1. **Pre-Deployment Tests**
   ```yaml
   # Example CI/CD configuration
   name: Pre-Deployment Tests
   on: [push, pull_request]
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Run tests
           run: [commands]
   ```

2. **Deployment Gates**
   - [Gate 1: Condition for blocking deployment]
   - [Gate 2: ...]

3. **Post-Deployment Monitoring**
   - [Monitor 1: What to track]
   - [Monitor 2: ...]

**Implementation:**
- **Effort:** [X hours]
- **Owner:** [Who implements]
- **Timeline:** [When to complete]

---

## ROLLBACK PROCEDURE

### Rollback Complexity: [SIMPLE | MEDIUM | COMPLEX]

**When to Rollback:**
- [Condition 1: Critical threshold for rollback]
- [Condition 2: ...]
- [...]

**Decision Criteria:**
```
IF [condition] THEN rollback immediately
IF [condition] THEN investigate and potentially rollback
IF [condition] THEN monitor closely but don't rollback yet
```

---

### Rollback Steps (Detailed)

**Step 1: Assess Impact**
```bash
# Commands to check system state
[command 1]
[command 2]
```

**Expected Output:**
- [What healthy output looks like]
- [What unhealthy output looks like]

---

**Step 2: Stop Service**
```bash
# Commands to stop the service
[stop command 1]
[stop command 2]
```

**Verification:**
```bash
# Verify service stopped
[verification command]
```

---

**Step 3: Revert Code Changes**

**Option A: Git Revert (Recommended)**
```bash
cd [directory]
git log --oneline -5  # Find commit to revert
git revert [commit-hash]
git push
```

**Option B: Manual Revert**
```bash
# File: [path]
# Change [description]
# From: [new value]
# To: [old value]
```

---

**Step 4: Revert Configuration**
```bash
# Restore configuration files
[config restore commands]
```

---

**Step 5: Revert Database (if applicable)**
```bash
# Rollback database migrations
[migration rollback commands]
```

**WARNING:** [Any data loss implications]

---

**Step 6: Restart Service**
```bash
# Restart with old code
[restart commands]
```

**Verification:**
```bash
# Verify service healthy
[health check commands]
```

---

**Step 7: Verify Rollback**

**Checklist:**
- [ ] Service responding
- [ ] All critical endpoints working
- [ ] No errors in logs
- [ ] Performance back to baseline
- [ ] Users can access system
- [ ] Data integrity verified

---

**Step 8: Notify Stakeholders**
- [ ] Team notified of rollback
- [ ] Reason documented
- [ ] Post-mortem scheduled
- [ ] Fix plan created

**Total Rollback Time:** [X minutes/hours]

---

### Rollback Testing (Dry Run)

**Pre-Deployment Rollback Test:**
1. Deploy to staging
2. Verify deployment works
3. Execute rollback procedure
4. Verify system restored
5. Document any rollback issues
6. Refine rollback procedure

**Status:** [NOT PERFORMED | COMPLETED | ISSUES FOUND]
**Effort:** [X hours]
**Owner:** [Who tests rollback]

---

## MONITORING REQUIREMENTS

### What to Monitor Post-Deployment

**Critical Metrics (First 24 Hours):**

1. **[Metric 1 Name]**
   ```bash
   # How to measure
   [command or query]
   ```
   - **Expected:** [Normal value or range]
   - **Alert if:** [Threshold for concern]
   - **Critical if:** [Threshold for immediate action]

2. **[Metric 2 Name]**
   ```bash
   [command or query]
   ```
   - **Expected:** [...]
   - **Alert if:** [...]
   - **Critical if:** [...]

3. **[Metric 3 Name]**
   - **Measurement:** [How to measure]
   - **Expected:** [...]
   - **Alert if:** [...]
   - **Critical if:** [...]

---

### Alert Thresholds

**Critical Alerts (Immediate Response - Page On-Call):**
- [Condition 1] - Example: Error rate > 5%
- [Condition 2] - Example: Response time > 5 seconds
- [Condition 3] - Example: Service down

**Warning Alerts (Review Within 1 Hour):**
- [Condition 1] - Example: Error rate > 1%
- [Condition 2] - Example: Response time > 1 second
- [Condition 3] - Example: Memory usage > 85%

**Info Alerts (Review Daily):**
- [Condition 1] - Example: Error rate > 0.1%
- [Condition 2] - Example: Response time trending upward
- [Condition 3] - Example: Resource usage > 70%

---

### Health Checks

**Automated Health Check Script:**

```bash
#!/bin/bash
# Health check script (run every [X] minutes)

# Check 1: [Description]
[command 1]
if [ $? -ne 0 ]; then
  echo "CRITICAL: [Check 1] failed"
  exit 1
fi

# Check 2: [Description]
[command 2]
if [ $? -ne 0 ]; then
  echo "CRITICAL: [Check 2] failed"
  exit 1
fi

echo "OK: All health checks passed"
```

**Health Check Frequency:**
- First 24 hours: Every [X] minutes
- First week: Every [X] minutes
- Ongoing: Every [X] minutes

---

### Monitoring Dashboard

**Recommended Metrics to Display:**

1. **[Category 1 Name]**
   - [Metric 1]
   - [Metric 2]
   - [...]

2. **[Category 2 Name]**
   - [Metric 1]
   - [Metric 2]
   - [...]

**Dashboard Implementation:**
- **Tool:** [Grafana | Datadog | Custom | etc.]
- **Effort:** [X hours]
- **Owner:** [Who creates dashboard]

---

## DEPLOYMENT CHECKLIST

### Pre-Deployment Steps

**Code Verification:**
- [ ] Code changes reviewed and approved
- [ ] Code review comments addressed
- [ ] Changes committed to version control
- [ ] Commit message clear and descriptive
- [ ] Branch merged to main (if applicable)
- [ ] Build successful
- [ ] No linting errors
- [ ] No security scan failures

**Testing:**
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All E2E tests pass
- [ ] Manual testing complete
- [ ] Regression testing complete
- [ ] Performance testing complete (if applicable)
- [ ] Security testing complete (if applicable)
- [ ] Load testing complete (if applicable)
- [ ] Rollback procedure tested

**Documentation:**
- [ ] README updated
- [ ] API documentation updated
- [ ] Deployment guide updated
- [ ] Runbook updated
- [ ] Rollback procedure documented
- [ ] Known issues documented

**Environment:**
- [ ] Staging environment tested
- [ ] Database migrations tested (if applicable)
- [ ] Configuration verified
- [ ] Secrets/credentials verified
- [ ] System resources healthy (CPU < X%, Memory < Y%)
- [ ] Backup taken
- [ ] Rollback plan ready

**Communication:**
- [ ] Team notified of deployment
- [ ] Stakeholders informed
- [ ] Maintenance window scheduled (if needed)
- [ ] On-call engineer identified
- [ ] Escalation path defined

**Monitoring:**
- [ ] Alerts configured
- [ ] Dashboard ready
- [ ] Logging verified
- [ ] Health checks configured

---

### Deployment Steps

**Step 1: Pre-Deployment Verification**
```bash
# [Commands to verify readiness]
```

**Step 2: Backup**
```bash
# [Backup commands]
```

**Step 3: Deploy Code**
```bash
# [Deployment commands]
```

**Step 4: Database Migration (if applicable)**
```bash
# [Migration commands]
```

**Step 5: Configuration Update (if applicable)**
```bash
# [Config update commands]
```

**Step 6: Service Restart**
```bash
# [Restart commands]
```

**Step 7: Immediate Verification**
```bash
# [Verification commands]
```

---

### Post-Deployment Validation

**Immediate Validation (5 minutes):**
- [ ] Service started successfully
- [ ] Health check passes
- [ ] Critical endpoints responding
- [ ] No errors in logs
- [ ] Performance within acceptable range

**1-Hour Validation:**
- [ ] All metrics within normal range
- [ ] No unexpected errors
- [ ] User reports normal (no complaints)
- [ ] Performance stable

**24-Hour Validation:**
- [ ] All monitoring data reviewed
- [ ] No anomalies detected
- [ ] Error rate acceptable
- [ ] Performance acceptable
- [ ] Ready for full release (if staged rollout)

**1-Week Validation:**
- [ ] Metrics stable over time
- [ ] No issues reported
- [ ] Success criteria met
- [ ] Change considered successful

---

### Who Approves Deployment?

**Approval Matrix:**

| Risk Level | Approver | Documentation Required |
|-----------|----------|------------------------|
| LOW | L2 Developer + L1 Overwatch | Code review, test results |
| MEDIUM | L1 Overwatch + L1 Security/QA | Risk assessment, test plan |
| HIGH | L1 Team + Stakeholder | Full risk analysis, rollback plan |
| CRITICAL | Business Owner + CTO | Executive summary, business impact |

**This Change: [LOW | MEDIUM | HIGH | CRITICAL]**
- **Approver:** [Who must approve]
- **Documentation:** [What is required]
- **Status:** [PENDING | APPROVED | REJECTED]

---

## SIGN-OFF

### Assessment Team

**[Role 1 - e.g., L1 OVERWATCH]**
- **Assessment:** [Risk level, readiness opinion]
- **Concerns:** [Any concerns or blockers]
- **Recommendation:** [APPROVE | APPROVE WITH CONDITIONS | DEFER | REJECT]
- **Date:** [YYYY-MM-DD]

**[Role 2 - e.g., L1 QA]**
- **Assessment:** [...]
- **Concerns:** [...]
- **Recommendation:** [...]
- **Date:** [YYYY-MM-DD]

**[Role 3 - e.g., L1 SECURITY]**
- **Assessment:** [...]
- **Concerns:** [...]
- **Recommendation:** [...]
- **Date:** [YYYY-MM-DD]

**[Role 4 - e.g., L2 BACKEND DEVELOPER]**
- **Assessment:** [...]
- **Concerns:** [...]
- **Recommendation:** [...]
- **Date:** [YYYY-MM-DD]

**[Role 5 - e.g., L2 DEVOPS]**
- **Assessment:** [...]
- **Concerns:** [...]
- **Recommendation:** [...]
- **Date:** [YYYY-MM-DD]

---

### Final Approval

**RISK ASSESSMENT STATUS:** [APPROVED | APPROVED WITH CONDITIONS | DEFERRED | REJECTED]

**DEPLOYMENT RECOMMENDATION:** [PROCEED | PROCEED WITH CAUTION | DEFER | ABORT]

**Conditions (if any):**
1. [Condition 1]
2. [Condition 2]
3. [...]

**Follow-Up Work Required:**
1. [Follow-up 1] - Owner: [X], Timeline: [Y]
2. [Follow-up 2] - Owner: [X], Timeline: [Y]
3. [...]

**Final Sign-Off:**
- **[Primary Approver Role - e.g., L1 OVERWATCH AGENT]**
- **Date:** [YYYY-MM-DD]
- **Status:** [APPROVED | REJECTED]
- **Comments:** [Any final comments]

---

## APPENDIX A: RISK ASSESSMENT PROCESS

### When to Create a Risk Assessment

**Required For:**
- All production deployments
- Security-related changes
- Infrastructure changes
- Breaking changes
- Database schema changes
- Dependency upgrades (major versions)
- Configuration changes affecting production
- Any change rated MEDIUM risk or higher

**Optional For:**
- Minor bug fixes (LOW risk)
- Documentation updates
- Internal tooling changes
- Development environment changes

---

### Risk Assessment Workflow

```
1. Change Proposed
   ↓
2. Initial Risk Classification (L2 Developer)
   ↓
3. If MEDIUM+ → Create Risk Assessment (L2 Developer)
   ↓
4. Review by L1 Team (Overwatch, QA, Security as needed)
   ↓
5. Revisions if needed
   ↓
6. Final Approval (See Approval Matrix)
   ↓
7. Deployment (if approved)
   ↓
8. Post-Deployment Review (24 hours)
   ↓
9. Archive Risk Assessment
```

---

### Risk Assessment Timeline

**For LOW risk changes:**
- Risk assessment: 1-2 hours
- Review: 30 minutes
- Approval: Same day

**For MEDIUM risk changes:**
- Risk assessment: 2-4 hours
- Review: 1-2 hours
- Approval: 1-2 days

**For HIGH risk changes:**
- Risk assessment: 4-8 hours
- Review: 2-4 hours
- Approval: 3-5 days

**For CRITICAL risk changes:**
- Risk assessment: 8+ hours
- Review: 4-8 hours
- Approval: 1-2 weeks

---

## APPENDIX B: TESTING CHECKLIST

### Testing Categories

**Functional Testing:**
- [ ] All features work as expected
- [ ] Error handling works correctly
- [ ] Edge cases handled
- [ ] Happy path tested
- [ ] Unhappy path tested

**Security Testing:**
- [ ] Authentication works
- [ ] Authorization works
- [ ] Input validation works
- [ ] No injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Rate limiting works (if applicable)
- [ ] Secrets not exposed
- [ ] Logs don't contain sensitive data

**Performance Testing:**
- [ ] Response time acceptable
- [ ] Throughput acceptable
- [ ] No memory leaks
- [ ] No CPU spikes
- [ ] Scalability tested
- [ ] Load testing complete

**Compatibility Testing:**
- [ ] Backward compatible (if required)
- [ ] Works with existing clients
- [ ] Works with existing services
- [ ] Browser compatibility (if frontend)
- [ ] Mobile compatibility (if applicable)

**Regression Testing:**
- [ ] Existing features still work
- [ ] No unintended side effects
- [ ] Integration tests pass
- [ ] E2E tests pass

**Deployment Testing:**
- [ ] Deployment procedure tested
- [ ] Rollback procedure tested
- [ ] Configuration tested
- [ ] Migration tested (if applicable)

---

## DOCUMENT VERSION CONTROL

**Version:** [X.Y]
**Status:** [DRAFT | FINAL | ARCHIVED]
**Date:** [YYYY-MM-DD]
**Next Review:** [YYYY-MM-DD or condition]

**Change History:**
- v1.0 ([Date]): Initial version
- v1.1 ([Date]): [Description of changes]
- v[X.Y] ([Date]): [Description of changes]

**Distribution:**
- [Name/Role 1]
- [Name/Role 2]
- [...]

**Related Documents:**
- [Link to related doc 1]
- [Link to related doc 2]
- [...]

---

## APPENDIX C: PROTOCOL v1.1c INTEGRATION

### Risk Assessment in Protocol v1.1c

**Requirement:** Risk assessments are **required** for:
- All MEDIUM+ risk changes
- All security-related changes
- All production deployments
- Any change affecting production users

**Integration Points:**

1. **Before Mission Start (Planning):**
   - Create risk assessment for planned changes
   - Review with team
   - Get approval before implementation

2. **After Mission Complete (Retrospective):**
   - Create risk assessment for deployed changes
   - Document what was learned
   - Identify gaps for future improvements

3. **During Retrospective:**
   - Review risk assessment accuracy
   - Identify risks that materialized
   - Identify risks that were missed
   - Update risk assessment template

---

### Sign-Off Requirements

**By Risk Level:**

| Risk Level | Who Signs Off | Timeline |
|-----------|---------------|----------|
| LOW | L2 Developer + L1 Overwatch | Same day |
| MEDIUM | L1 Overwatch + L1 QA/Security | 1-2 days |
| HIGH | L1 Team + Stakeholder | 3-5 days |
| CRITICAL | Business Owner + CTO | 1-2 weeks |

---

### Risk Assessment Quality Gates

**Quality Gate 1: Completeness**
- [ ] All sections filled out
- [ ] All risks identified
- [ ] All mitigations documented
- [ ] Rollback procedure complete

**Quality Gate 2: Accuracy**
- [ ] Risk levels justified
- [ ] Testing coverage realistic
- [ ] Timelines reasonable
- [ ] Resource estimates accurate

**Quality Gate 3: Clarity**
- [ ] Non-technical stakeholders can understand
- [ ] Recommendations clear
- [ ] Rollback steps actionable
- [ ] Sign-off requirements clear

---

## END OF TEMPLATE

**Template Version:** 1.0
**Last Updated:** 2025-11-10
**Maintained By:** L1 OVERWATCH
**Protocol:** v1.1c

---

**INSTRUCTIONS FOR USE:**

1. **Copy this template** to new file: `RISK_ASSESSMENT_[FEATURE_NAME].md`
2. **Fill out all sections** relevant to your change
3. **Remove sections** not applicable (mark as "N/A" if unclear)
4. **Replace all [PLACEHOLDERS]** with actual values
5. **Delete instruction blocks** like this one before finalizing
6. **Review with team** before starting implementation
7. **Update during implementation** as new risks identified
8. **Archive after deployment** for future reference

**REMEMBER:**
- Be honest about risks (don't minimize)
- Include "unknown risks" if insufficient information
- Make rollback procedures ACTIONABLE (actual commands)
- This is about production safety, not documentation overhead
- Better to overestimate risk than underestimate

**GOVERNANCE:**
Risk assessments are not just documentation—they are a governance requirement to prevent production incidents.
