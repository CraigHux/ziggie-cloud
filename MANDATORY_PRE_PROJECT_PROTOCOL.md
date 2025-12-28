# 🎯 MANDATORY PRE-PROJECT PROTOCOL
## Ziggie's Standard Operating Procedure

**Version:** 1.2
**Created:** 2025-11-09
**Last Updated:** 2025-11-09
**Status:** MANDATORY - Must Follow for ALL Projects
**Purpose:** Ensure optimal performance, prevent issues, maximize efficiency
**Changelog:**
- v1.1 - Added pre-scanning, dynamic load balancing, and predictive detection optimizations
- v1.2 - Added mandatory agent reports, better load distribution, real-time Overwatch logging, execution time tracking, and lower workload variance requirements (targeting 100/100 scores)

---

## 🚨 CRITICAL RULE

**BEFORE starting ANY project or task, Ziggie MUST:**

1. ✅ Complete FULL system check
2. ✅ Analyze task requirements
3. ✅ **PRE-SCAN workload** (new v1.1)
4. ✅ Calculate **dynamic load balancing**
5. ✅ Recommend deployment strategy
6. ✅ Get USER CONFIRMATION before proceeding
7. ✅ Deploy Overwatch Agent (mandatory)
8. ✅ Execute with monitoring
9. ✅ Deliver final report

**NO EXCEPTIONS** - This protocol is MANDATORY for all work.

---

## 📋 PHASE 1: SYSTEM CHECK (ALWAYS FIRST)

### **1.1 Hardware Assessment**

Run these checks FIRST:

```bash
# CPU Cores/Threads
nproc

# Memory Available (if possible)
free -h 2>/dev/null || echo "Manual check needed"

# Disk Space
df -h C:\ 2>/dev/null || powershell -Command "Get-PSDrive C"

# Running Processes (heavy apps)
tasklist | grep -E "chrome|docker|node|python" | wc -l
```

**Document:**
- CPU cores available: [NUMBER]
- RAM available: [AMOUNT]
- Disk space free: [AMOUNT]
- Heavy processes running: [COUNT]

### **1.2 Current System Load**

Check what's already running:

```bash
# Docker status
docker ps 2>/dev/null | wc -l

# Active Claude Code sessions
ps aux | grep -i claude | wc -l

# Other development tools
netstat -an | grep LISTEN | wc -l
```

**Document:**
- Docker containers active: [COUNT]
- Development servers running: [COUNT]
- Network services active: [COUNT]

### **1.3 System Health Rating**

Calculate system availability:

| Resource | Usage | Available | Status |
|----------|-------|-----------|--------|
| CPU | [X%] | [Y cores] | 🟢/🟡/🔴 |
| RAM | [X%] | [Y GB] | 🟢/🟡/🔴 |
| Disk | [X%] | [Y GB] | 🟢/🟡/🔴 |

**Rating Guide:**
- 🟢 GREEN (0-60% usage) - Safe for heavy workloads
- 🟡 YELLOW (60-80% usage) - Moderate workloads only
- 🔴 RED (80%+ usage) - Light workloads, reduce agents

---

## 📊 PHASE 2: TASK ANALYSIS

### **2.1 Task Classification**

Classify the project/task:

**Type:**
- [ ] File Operations (read/write/edit)
- [ ] Agent Creation/Expansion
- [ ] Documentation Updates
- [ ] Code Development
- [ ] System Architecture
- [ ] Quality Assurance
- [ ] Research/Analysis
- [ ] Other: ___________

**Complexity:**
- [ ] Simple (5-15 min, single file)
- [ ] Medium (15-60 min, multiple files)
- [ ] Complex (1-4 hours, architecture)
- [ ] Major (4+ hours, large expansion)

**Urgency:**
- [ ] Critical (must complete ASAP)
- [ ] High (needed today)
- [ ] Medium (needed this week)
- [ ] Low (when convenient)

### **2.2 Resource Requirements**

Estimate needed resources:

**File Operations:**
- Files to read: [COUNT]
- Files to write: [COUNT]
- Files to edit: [COUNT]
- Estimated file size: [TOTAL MB]

**Processing Requirements:**
- Heavy reasoning needed: [YES/NO]
- Large file processing: [YES/NO]
- Multiple parallel operations: [YES/NO]
- Real-time validation needed: [YES/NO]

### **2.3 Pre-Scanning & Workload Analysis** 🆕 v1.1

**CRITICAL OPTIMIZATION:** Before deploying agents, pre-scan to understand exact workload distribution.

**For File Operations (editing/find-replace tasks):**

Run automated pre-scan to count instances:

```bash
# Example: Searching for pattern to replace
grep -r "pattern_to_find" target_directory/ | wc -l

# Example: Count instances per file
for file in *.md; do
  count=$(grep -c "pattern" "$file" 2>/dev/null || echo "0")
  echo "$file: $count instances"
done
```

**Document Pre-Scan Results:**

| File | Instances | Complexity | Priority |
|------|-----------|------------|----------|
| file1.md | 15 | High | 1 |
| file2.md | 8 | Medium | 2 |
| file3.md | 2 | Low | 3 |
| **TOTAL** | **25** | — | — |

**Workload Distribution Analysis:**

Calculate optimal agent assignment:

```
Total Workload: [X instances/files/tasks]
Planned Workers: [Y agents]
Ideal per Agent: X ÷ Y = [Z instances per agent]
Max Load per Agent: 40% of total (prevent bottlenecks)
```

**Example:**
- Total: 21 instances across 7 files
- Workers: 4 agents
- Ideal: 21 ÷ 4 = 5.25 instances per agent
- Max allowed: 21 × 0.40 = 8.4 instances (any agent >8 = rebalance)

**Red Flags:**
- ⚠️ Any single agent assigned >40% of total work
- ⚠️ Workload variance >3:1 ratio between agents
- ⚠️ Files with 0 instances assigned to agents

**🆕 v1.2 - Optimal Variance Target:**
- 🎯 **Target variance: <2:1 ratio** (for 100/100 scores)
- ✅ Acceptable variance: 2:1 to 3:1 ratio (good, 90-95/100 scores)
- ⚠️ Warning variance: 3:1 to 4:1 ratio (acceptable, 85-90/100 scores)
- ❌ Poor variance: >4:1 ratio (inefficient, <85/100 scores)

### **2.4 Predictive Instance Detection** 🆕 v1.1

**Advanced Analysis:** Use pattern recognition to predict hidden work.

**Common Patterns:**

1. **Branding/Naming Fixes:**
   - Search for variations: lowercase, UPPERCASE, Title Case, hyphenated
   - Example: "meowping-rts", "Meow Ping RTS", "MeowPing", "MEOWPING_RTS"

2. **Path Updates:**
   - Search absolute paths: `C:\old\path\`
   - Search relative paths: `./old/path/`, `../old/path/`
   - Search URL paths: `https://old.domain/path/`

3. **Code Refactoring:**
   - Function names in different contexts: declarations, calls, comments, docs
   - Variable names with different cases: camelCase, snake_case, PascalCase

**Predictive Scan Commands:**

```bash
# Multi-pattern search (case variations)
grep -ri "pattern" . | grep -v ".git"

# Find all file types that might contain the pattern
find . -type f \( -name "*.md" -o -name "*.json" -o -name "*.yaml" \) -exec grep -l "pattern" {} \;

# Count total across all variations
grep -rE "pattern1|pattern2|pattern3" . | wc -l
```

**Document Predicted Workload:**
- Primary pattern: [X instances]
- Variations detected: [Y instances]
- **Total predicted:** [X+Y instances]
- Confidence level: [High/Medium/Low]

---

## 🎯 PHASE 3: DEPLOYMENT STRATEGY

### **3.1 Agent Count Recommendation**

Based on system check + task analysis:

**System Status: [GREEN/YELLOW/RED]**

#### If GREEN (0-60% CPU usage):

| Task Type | Total Agents | Workers | Overwatch | Model |
|-----------|--------------|---------|-----------|-------|
| Simple | 5-7 agents | 4-6 | 1 | Haiku |
| Medium | 9 agents | 8 | 1 | Sonnet (PROVEN) |
| Complex | 9-11 agents | 8-10 | 1 | Sonnet |
| Major | 13 agents | 12 | 1 | Haiku majority |

#### If YELLOW (60-80% CPU usage):

| Task Type | Total Agents | Workers | Overwatch | Model |
|-----------|--------------|---------|-----------|-------|
| Simple | 3-5 agents | 2-4 | 1 | Haiku |
| Medium | 5-7 agents | 4-6 | 1 | Sonnet |
| Complex | 5 agents | 4 | 1 | Sonnet |
| Major | 7 agents | 6 | 1 | Haiku |

#### If RED (80%+ CPU usage):

| Task Type | Total Agents | Workers | Overwatch | Model |
|-----------|--------------|---------|-----------|-------|
| All Tasks | 3 agents | 2 | 1 | Haiku |

**Recommended: WAIT for system resources to free up**

### **3.2 Agent Selection Strategy**

Choose agents based on task:

**For File Operations:**
- L2/L3 Agents (specialists)
- Model: Haiku (fast)
- Count: 4-8 workers + 1 Overwatch

**For Architecture Work:**
- L1 Agents (strategic)
- Model: Sonnet
- Count: 4-6 workers + 1 Overwatch

**For Code Development:**
- L1/L2 Mix (strategy + execution)
- Model: Sonnet/Haiku mix
- Count: 6-8 workers + 1 Overwatch

**For Documentation:**
- L2/L3 Agents (specialists)
- Model: Haiku (fast)
- Count: 8-12 workers + 1 Overwatch

### **3.3 Hierarchical Structure**

Plan the team hierarchy:

```
EXAMPLE: Medium Complexity Task (9 agents total)

Overwatch AI Agent (1) - Sonnet
└─ Monitors all 8 workers

L1 Coordinator (1) - Sonnet
├─ Overall strategy
└─ Coordinates L2 agents

L2 Specialists (3-4) - Sonnet/Haiku
├─ Domain experts
├─ Execute core tasks
└─ Manage L3 agents (if needed)

L3 Micro-Specialists (2-3) - Haiku
└─ Quick validations
└─ Batch operations
```

### **3.4 Dynamic Load Balancing** 🆕 v1.1

**CRITICAL FOR 100/100 SCORES:** Distribute workload to prevent any agent from carrying >40% of total work.

**Load Balancing Formula:**

```
Step 1: Calculate Total Workload (from Phase 2.3 pre-scan)
  Total = [Sum of all instances/files/tasks]

Step 2: Determine Worker Count (from Phase 3.1)
  Workers = [Number of working agents, excluding Overwatch]

Step 3: Calculate Ideal Load per Agent
  Ideal_Load = Total ÷ Workers

Step 4: Calculate Maximum Load (40% rule)
  Max_Load = Total × 0.40

Step 5: Verify No Agent Exceeds Max
  If any agent assigned > Max_Load:
    ⚠️ REBALANCE REQUIRED
```

**Rebalancing Strategies:**

**Strategy 1: Split High-Load Files**
```
Problem: File 01 has 15 instances, but Agent 1 would carry 60% of work
Solution: Split file 01 between Agent 1 (lines 1-100) and Agent 2 (lines 101-200)
Result: Agent 1: 8 instances, Agent 2: 7 instances
```

**Strategy 2: Add Additional Agent**
```
Problem: 4 agents would result in 1 agent carrying 45% of work
Solution: Deploy 5 agents instead to reduce individual load
Result: Max load drops to 30% per agent
```

**Strategy 3: Group Small Files**
```
Problem: Files 5, 6, 7, 8 each have 1-2 instances
Solution: Assign multiple small files to single agent
Result: Agent 4: Files 5-8 (5 instances total = 24%)
```

**Load Balancing Table:**

After pre-scan, create distribution table:

| Agent | Assigned Files/Tasks | Instance Count | % of Total | Status |
|-------|---------------------|----------------|------------|--------|
| L2.8.1 | Files 01, 02 | 8 | 38% | ✅ BALANCED |
| L2.8.2 | Files 03, 04 | 6 | 29% | ✅ BALANCED |
| L2.8.3 | Files 05, 06 | 4 | 19% | ✅ BALANCED |
| L2.8.4 | Files 07, 08 | 3 | 14% | ✅ BALANCED |
| **Total** | **8 files** | **21** | **100%** | ✅ **OPTIMAL** |

**Validation Rules:**

✅ **PASS Criteria (100/100 target):** 🆕 v1.2
- No agent >40% of total workload ✅
- Workload variance <2:1 ratio (highest:lowest) 🎯
- All agents have meaningful work (>10% of total)
- Load distribution balanced within 15% variance

✅ **ACCEPTABLE Criteria (90-95/100):**
- No agent >40% of total workload
- Workload variance 2:1 to 3:1 ratio
- All agents have meaningful work (>5% of total)

⚠️ **WARNING Criteria (85-90/100):**
- Any agent 35-40% of total (acceptable but near limit)
- Workload variance 3:1 to 4:1
- Some agents <5% (underutilized)

❌ **FAIL Criteria (<85/100):**
- Any agent >40% of total (MUST rebalance)
- Workload variance >4:1 (inefficient distribution)
- Multiple agents with <5% (poor distribution)

**Example - Before Dynamic Load Balancing:**
```
Agent 1: 13 instances (61.9%) ❌ FAILS - Exceeds 40% limit
Agent 2: 4 instances (19.0%)
Agent 3: 3 instances (14.3%)
Agent 4: 1 instance (4.8%)
Variance: 13:1 ratio (13/1 = 13:1) ❌ FAILS - Exceeds 3:1
```

**Example - After Dynamic Load Balancing:**
```
Agent 1: 8 instances (38.0%) ✅ PASS - Under 40%
Agent 2: 6 instances (28.6%) ✅ PASS
Agent 3: 4 instances (19.0%) ✅ PASS
Agent 4: 3 instances (14.3%) ✅ PASS
Variance: 2.67:1 ratio (8/3 = 2.67:1) ✅ PASS - Under 3:1
```

---

## ✅ PHASE 4: USER CONFIRMATION (MANDATORY)

### **4.1 Present Complete Analysis**

**FORMAT:**

```
📊 SYSTEM CHECK RESULTS:
- CPU: [X cores available, Y% usage] - Status: [GREEN/YELLOW/RED]
- RAM: [X GB available, Y% usage] - Status: [GREEN/YELLOW/RED]
- System Health: [GREEN/YELLOW/RED]

📋 TASK ANALYSIS:
- Type: [Task type]
- Complexity: [Simple/Medium/Complex/Major]
- Estimated Duration: [X hours]
- Files Involved: [X files]

🔍 PRE-SCAN RESULTS: 🆕 v1.1
- Total Workload: [X instances/files/tasks]
- Predicted Variations: [Y additional instances]
- Total Expected: [X+Y instances]
- Confidence: [High/Medium/Low]

⚖️ LOAD BALANCING ANALYSIS: 🆕 v1.1
- Workers Planned: [X agents]
- Ideal Load per Agent: [Y instances] ([Z%])
- Maximum Allowed per Agent: [W instances] (40%)
- Load Distribution: ✅ BALANCED / ⚠️ WARNING / ❌ REBALANCE NEEDED
- Workload Variance: [A:B ratio] (target <3:1)

🎯 RECOMMENDED DEPLOYMENT:
- Total Agents: [X agents]
  ├─ Overwatch: 1 (Sonnet) - MANDATORY
  ├─ L1 Agents: [X] ([Model])
  ├─ L2 Agents: [X] ([Model])
  └─ L3 Agents: [X] ([Model])

- Agent Selection & Load Distribution:
  ├─ Agent 1 ([Name]): [X instances] ([Y%]) - Status: ✅/⚠️/❌
  ├─ Agent 2 ([Name]): [X instances] ([Y%]) - Status: ✅/⚠️/❌
  ├─ Agent 3 ([Name]): [X instances] ([Y%]) - Status: ✅/⚠️/❌
  └─ Agent 4 ([Name]): [X instances] ([Y%]) - Status: ✅/⚠️/❌

- Estimated Resource Usage: [X%] CPU
- Estimated Completion Time: [X minutes/hours]
- Expected Overwatch Score: [X/100] (based on load balance)

⚠️ RISKS/CONSIDERATIONS:
- [Any potential issues]
- [Resource constraints]
- [Alternative approaches]

💡 ALTERNATIVE APPROACHES (if applicable):
1. [Approach 1]: [Pros/Cons]
2. [Approach 2]: [Pros/Cons]
```

### **4.2 Request Confirmation**

**ASK USER:**

> "Based on the analysis above, I recommend deploying **[X agents]** with **[strategy name]**.
>
> This will use approximately **[X%]** of your CPU and take **[X hours]**.
>
> **Do you approve this approach?** Or would you prefer:
> - Alternative 1: [Different approach]
> - Alternative 2: [Different approach]
> - Modify: [Let me know what to adjust]"

### **4.3 Wait for Explicit Approval**

**DO NOT PROCEED UNTIL USER SAYS:**
- "Yes, proceed"
- "Approved"
- "Go ahead"
- "Start"
- Or similar confirmation

**IF USER WANTS CHANGES:**
- Revise strategy
- Present new recommendation
- Wait for confirmation again

---

## 🚀 PHASE 5: DEPLOYMENT (AFTER APPROVAL)

### **5.1 Deploy Overwatch FIRST (Mandatory)**

```
ALWAYS deploy Overwatch before workers:

1. Start Overwatch AI Agent
   - Model: Sonnet
   - Role: Monitor all agents + system health
   - Task: Continuous monitoring throughout project
   - Report: Final comprehensive report on completion

2. Wait for Overwatch confirmation: "Monitoring active"

3. Proceed with worker deployment
```

**🆕 v1.2 - Real-Time Overwatch Logging Requirements:**

Overwatch MUST provide real-time monitoring logs during execution:

```markdown
**Required Log Format:**
[HH:MM:SS] Overwatch: [Agent ID] - [Status] - [Details]

**Example Logs:**
[14:53:25] Overwatch: Monitoring initialized - 7 workers + Ziggie
[14:53:26] Overwatch: L2.8.1 started - Migration Archiver (14 files)
[14:53:27] Overwatch: L2.8.2 started - Expansion Archiver (12 files)
[14:53:30] Overwatch: L2.8.1 progress - 7/14 files processed (50%)
[14:53:45] Overwatch: L2.8.1 completed - 14/14 files SUCCESS
[14:53:48] Overwatch: L2.8.2 completed - 12/12 files SUCCESS
[14:54:10] Overwatch: All agents completed - generating final report
```

**What to Log:**
- ✅ Agent start times (timestamp when agent begins work)
- ✅ Progress updates (every 25%, 50%, 75% completion)
- ✅ Agent completion times (timestamp when agent finishes)
- ✅ Any warnings or errors detected
- ✅ System resource spikes (CPU >80%, RAM >90%)
- ✅ Bottleneck detection (agent taking 2x expected time)

### **5.2 Deploy Working Agents**

Based on approved strategy:

```
Deploy agents in order:
1. L1 Coordinators (if any)
2. L2 Specialists (if any)
3. L3 Micro-specialists (if any)

Stagger deployment if >8 agents:
- Deploy 4-6 agents initially
- Monitor system load
- Deploy remaining agents if system stable
```

**🆕 v1.2 - Mandatory Agent Completion Reports:**

**CRITICAL:** ALL working agents MUST create completion reports upon finishing their tasks.

**Required Report Format:**

```markdown
# [AGENT_ID] COMPLETION REPORT

**Agent:** [ID and Name]
**Task:** [Brief description]
**Status:** SUCCESS / FAILED / PARTIAL

**Execution Metrics:**
- Start Time: [HH:MM:SS]
- End Time: [HH:MM:SS]
- Duration: [X minutes Y seconds]
- Files Processed: [X/Y]
- Operations Performed: [X operations]

**Results:**
- [List of completed items]
- [Any errors or warnings]
- [Verification status]

**Issues Encountered:**
- [None / List any issues]

**Final Status:** [VERIFIED COMPLETE / NEEDS REVIEW]
```

**Example Report:**

```markdown
# L2.8.1 COMPLETION REPORT

**Agent:** L2.8.1 - Migration Archiver
**Task:** Archive migration files to "No Longer Needed" folder
**Status:** SUCCESS

**Execution Metrics:**
- Start Time: 14:53:26
- End Time: 14:53:45
- Duration: 19 seconds
- Files Processed: 14/14
- Operations Performed: 16 (14 moves + 2 folder creates)

**Results:**
- Created folder: C:\Ziggie\No Longer Needed\Migration-Files\
- Moved 14 migration files successfully
- All files verified in archive location
- No errors encountered

**Issues Encountered:** None

**Final Status:** VERIFIED COMPLETE
```

**Where to Save:**
- File path: `C:\Ziggie\agent-reports\[AGENT_ID]_COMPLETION_REPORT.md`
- Create `agent-reports/` folder if it doesn't exist
- Use agent ID as filename prefix (e.g., `L2.8.1_COMPLETION_REPORT.md`)

### **5.3 Monitor Throughout**

Overwatch monitors:
- Agent health (freezes, loops, failures)
- System resources (CPU, RAM usage)
- Task progress (completion rates)
- Quality (file updates, validations)

**If issues detected:**
- Overwatch reports immediately
- Pause deployment if needed
- Address issues before continuing

---

## 📊 PHASE 6: EXECUTION MONITORING

### **6.1 Real-Time Tracking**

Track throughout execution:

**Agent Status:**
- [ ] All agents active
- [ ] Progress being made
- [ ] No freezes/loops detected
- [ ] Files being updated correctly

**System Health:**
- [ ] CPU usage within limits
- [ ] RAM usage stable
- [ ] No system slowdowns
- [ ] Other apps still responsive

**Quality Checks:**
- [ ] Work meeting standards
- [ ] Files updating correctly
- [ ] Documentation maintained
- [ ] Change logs updated

**🆕 v1.2 - Execution Time Tracking Requirements:**

**MANDATORY:** Track execution time for ALL agents and overall operation.

**What to Track:**

1. **Per-Agent Timing:**
   ```
   Agent ID: L2.8.1
   Start: 14:53:26
   End: 14:53:45
   Duration: 19 seconds
   Efficiency: 0.74 files/second (14 files ÷ 19 sec)
   ```

2. **Overall Operation Timing:**
   ```
   Operation Start: 14:53:25 (Overwatch deployed)
   First Agent Start: 14:53:26
   Last Agent Complete: 14:54:10
   Operation End: 14:54:15 (All reports generated)

   Total Duration: 50 seconds
   Agent Work Time: 44 seconds (first→last agent)
   Reporting Time: 5 seconds
   ```

3. **Performance Benchmarks:**
   - Fastest agent: [Agent ID] - [X seconds]
   - Slowest agent: [Agent ID] - [Y seconds]
   - Average agent time: [Z seconds]
   - Efficiency variance: [A%] (deviation from average)

**How to Use Timing Data:**
- Identify bottlenecks (agents taking 2x+ average time)
- Optimize future load distribution
- Set realistic time estimates
- Detect performance degradation
- Measure improvement over time

### **6.2 Intervention Protocol**

If Overwatch detects issues:

**Level 1 - Warning:**
- Agent slow but progressing
- System resources elevated
- **Action:** Monitor closely, no intervention yet

**Level 2 - Intervention:**
- Agent frozen/looping
- System resources critical
- **Action:** Pause agent, diagnose, restart or replace

**Level 3 - Emergency Stop:**
- Multiple agents failing
- System stability at risk
- **Action:** Stop all agents, save work, report to user

---

## ✅ PHASE 7: COMPLETION & VALIDATION

### **7.1 Final Validation**

Before reporting complete:

**Quality Checks:**
- [ ] All tasks completed
- [ ] All files updated and saved
- [ ] All validations passed
- [ ] Documentation updated
- [ ] Change logs current

**System Checks:**
- [ ] All agents put tools down
- [ ] No processes left hanging
- [ ] System resources released
- [ ] No errors or warnings

**Deliverables:**
- [ ] All requested outputs created
- [ ] All modifications verified
- [ ] All reports generated
- [ ] All files accessible

### **7.2 Overwatch Final Report**

Overwatch delivers comprehensive report:

**Required Sections:**
1. Agent Status Table (all agents, completion status)
2. Incidents Detected (freezes, loops, issues)
3. Performance Metrics (efficiency, completion time)
4. Bottleneck Analysis (what slowed work, if anything)
5. Recommendations (future improvements)
6. Final Verdict (GREEN/YELLOW/RED light)

### **7.3 Ziggie Summary Report**

Ziggie provides user-friendly summary:

**Include:**
- What was accomplished
- Agent deployment stats
- Files created/modified
- Quality score (X/100)
- Production readiness
- Any issues encountered
- Recommendations for user

---

## 📝 PHASE 8: DOCUMENTATION

### **8.1 Update Memory**

Update ZIGGIE_MEMORY.md with:
- Session summary
- Agents deployed
- Tasks accomplished
- Lessons learned
- Performance metrics

### **8.2 Update Change Logs**

Update change logs with:
- All modifications made
- Files affected
- Reasoning/justification
- Verification steps
- Impact assessment

### **8.3 Archive Reports**

Save all reports to designated folder:
- Overwatch monitoring report
- Final validation report
- Performance metrics
- User summary

---

## 🎯 QUICK REFERENCE CHECKLIST

**Before Starting ANY Task:**

- [ ] 1. Run complete system check
- [ ] 2. Analyze task requirements
- [ ] 3. 🆕 **PRE-SCAN workload** (count instances, identify patterns)
- [ ] 4. 🆕 **CALCULATE dynamic load balancing** (40% max rule)
- [ ] 5. Calculate resource needs
- [ ] 6. Recommend deployment strategy
- [ ] 7. Present complete analysis to user (including load balance)
- [ ] 8. Wait for explicit approval
- [ ] 9. Deploy Overwatch FIRST
- [ ] 10. Deploy working agents (per load balance plan)
- [ ] 11. Monitor throughout
- [ ] 12. Validate completion
- [ ] 13. Overwatch final report
- [ ] 14. Ziggie summary report
- [ ] 15. Update documentation
- [ ] 16. Archive reports

**IF ANY STEP SKIPPED = PROTOCOL VIOLATION**

**v1.1 OPTIMIZATION REQUIREMENTS:**
- ✅ Always pre-scan before deploying agents
- ✅ Always calculate load balancing (no agent >40%)
- ✅ Always include load distribution in user confirmation
- ✅ Target 100/100 Overwatch scores through optimal distribution

**🆕 v1.2 REQUIREMENTS FOR 100/100 SCORES:**
1. ✅ **Mandatory Agent Reports** - ALL agents create completion reports
2. ✅ **Better Load Distribution** - Target <2:1 workload variance, all agents >10%
3. ✅ **Real-Time Overwatch Logging** - Timestamped monitoring logs during execution
4. ✅ **Execution Time Tracking** - Track per-agent and overall operation timing
5. ✅ **Lower Workload Variance** - Aim for <2:1 ratio between highest/lowest agents

**Implementing ALL v1.2 requirements = Consistent 100/100 scores!**

---

## 💡 EXCEPTION HANDLING

### **Urgent/Emergency Tasks**

If user says "URGENT" or "EMERGENCY":

**Streamlined Protocol:**
1. Quick system check (30 seconds)
2. Present fast recommendation (1 minute)
3. Deploy on user approval
4. Still deploy Overwatch (non-negotiable)
5. Full reporting after completion

**DO NOT SKIP:**
- System check (even if quick)
- User confirmation
- Overwatch deployment
- Final reporting

---

## 📊 SUCCESS METRICS

Track protocol effectiveness:

**Per Project:**
- System health before/after
- Resource usage (predicted vs actual)
- Agent efficiency (X/10 rating)
- Issues detected/prevented
- Completion time (estimated vs actual)

**Overall Trends:**
- Protocol compliance: [X%]
- User satisfaction: [X/10]
- Issue prevention rate: [X%]
- Resource optimization: [X%]

---

## 🔄 CONTINUOUS IMPROVEMENT

**After Each Project:**
1. Review what worked well
2. Identify what could improve
3. Update protocol if needed
4. Document lessons learned
5. Share insights with user

**Monthly Review:**
- Analyze all projects from month
- Calculate success metrics
- Identify patterns
- Recommend protocol updates
- Get user feedback

---

## 🎯 COMMITMENT

**Ziggie's Commitment to User:**

> "I, Ziggie, commit to following this Mandatory Pre-Project Protocol for EVERY task, no matter how small or large. I will ALWAYS:
>
> 1. Check system health FIRST
> 2. Analyze requirements thoroughly
> 3. Recommend the best approach
> 4. Get your confirmation BEFORE proceeding
> 5. Deploy Overwatch for monitoring
> 6. Execute with quality and efficiency
> 7. Deliver comprehensive reports
>
> If I skip ANY step, consider it a protocol violation and remind me to follow proper procedure.
>
> This protocol ensures your system stays healthy, work is done efficiently, and you stay informed throughout."

**Signed:** Ziggie
**Date:** 2025-11-09
**Version:** 1.2 - MANDATORY (Targeting 100/100 Scores)
**v1.1 Optimizations:** Pre-scanning, Dynamic Load Balancing, Predictive Detection
**v1.2 Enhancements:** Mandatory Agent Reports, Better Load Distribution (<2:1 variance), Real-Time Overwatch Logging, Execution Time Tracking, Lower Workload Variance

---

## 📞 USER OVERRIDE

**User can override protocol IF:**
- They explicitly state "skip protocol"
- Emergency situation requires immediate action
- User has complete understanding of risks

**Even with override, MINIMUM requirements:**
- Deploy Overwatch (for safety)
- Final report (for documentation)

---

**END OF MANDATORY PROTOCOL**

🐱 **Cats rule. Protocols prevent chaos!** 🎯
