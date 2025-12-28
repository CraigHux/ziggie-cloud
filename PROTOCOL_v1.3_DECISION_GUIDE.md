# Protocol v1.3 Decision Guide

**Quick Reference: When to Use Hierarchical Deployment (v1.3) vs Standard Deployment (v1.2)**

**Version:** 1.0
**Created:** 2025-11-09
**Status:** Reference Guide

---

## Quick Decision Flowchart

```
┌─────────────────────────────────────┐
│  New Task Requested by User        │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Perform Phases 1-4 (System Check,  │
│  Task Analysis, Pre-Scan, Load      │
│  Balancing)                          │
└────────────┬────────────────────────┘
             │
             ▼
      ┌──────────────┐
      │  Is the task │
      │  well-defined│     NO
      │  & repeatable│─────────────┐
      │  ?           │             │
      └──────┬───────┘             │
             │ YES                 │
             ▼                     ▼
      ┌──────────────┐      ┌──────────────┐
      │  Are success │      │  Use v1.2    │
      │  criteria    │  NO  │  (Standard)  │
      │  clear?      │──────▶              │
      └──────┬───────┘      └──────────────┘
             │ YES
             ▼
      ┌──────────────┐
      │  Is load     │
      │  balancing   │  NO
      │  straight-   │──────┐
      │  forward?    │      │
      └──────┬───────┘      │
             │ YES          │
             ▼              ▼
      ┌──────────────┐   ┌──────────────┐
      │  Is user     │   │  Use v1.2    │
      │  intervention│YES│  (Standard)  │
      │  unlikely?   │───▶              │
      └──────┬───────┘   └──────────────┘
             │ NO
             ▼
      ┌──────────────┐
      │  Recommend   │
      │  v1.3 to user│
      │  (Hierarchical)│
      └──────┬───────┘
             │
             ▼
      ┌──────────────┐
      │  User        │  NO
      │  approves    │──────┐
      │  v1.3?       │      │
      └──────┬───────┘      │
             │ YES          │
             ▼              ▼
      ┌──────────────┐   ┌──────────────┐
      │  Use v1.3    │   │  Use v1.2    │
      │  (Hierarchical)│  │  (Standard)  │
      └──────────────┘   └──────────────┘
```

---

## Comparison Table

| Criteria | v1.2 Standard | v1.3 Hierarchical |
|----------|---------------|-------------------|
| **Task Definition** | Can be novel/experimental | Must be well-defined and repeatable |
| **Success Criteria** | Can be ambiguous | Must be clear and measurable |
| **Load Balancing** | Can be complex/uncertain | Must be straightforward |
| **Task Similarity** | Can be heterogeneous | Should be similar/uniform |
| **User Intervention** | May be needed | Should be unlikely |
| **Deployment Speed** | Moderate (sequential) | Faster (parallel by Overwatch) |
| **Ziggie's Role** | Full execution (Phases 1-9) | Strategy only (1-5, 6, 9) |
| **Overwatch's Role** | Monitor only | Autonomous deployment + monitoring |
| **Complexity** | Simpler (direct control) | More complex (delegation) |
| **Best For** | Novel tasks, debugging, research | Standard deployments, batch ops |

---

## Use v1.3 Hierarchical When

### Task Characteristics

✅ **Well-Defined Tasks**
- Task type is standard (file operations, batch updates, standard deployments)
- Similar tasks have been done before
- Clear input → output mapping
- **Example:** "Archive these 50 files to backup folder"

✅ **Clear Success Criteria**
- Objective pass/fail conditions
- Measurable outcomes
- No subjective evaluation needed
- **Example:** "All files moved successfully, no errors"

✅ **Straightforward Load Balancing**
- Even workload distribution possible
- No complex dependencies between tasks
- Parallelization is beneficial
- **Example:** 50 files, 5 agents, 10 files each = 1:1 variance

✅ **Similar/Uniform Tasks**
- All tasks are the same type
- Same validation criteria for all
- No special cases or exceptions
- **Example:** All tasks are "move file from A to B"

✅ **Minimal User Intervention Expected**
- User unlikely to need to adjust mid-execution
- No decision points during execution
- Fully automatable
- **Example:** Batch operation with no user input needed

### Operational Benefits

✅ **Speed is Important**
- User wants fast completion
- Parallel deployment beneficial
- Overwatch can deploy L2 workers faster than Ziggie sequentially

✅ **Audit Trail Desired**
- User wants comprehensive reporting
- Hierarchical structure provides clear chain of command
- Overwatch final report + L2 completion reports = full audit

✅ **Scalability Matters**
- Task will be repeated regularly
- Want to establish pattern for future
- Building deployment template for reuse

### Examples of Good v1.3 Use Cases

1. **File Archiving:** "Archive all migration files to 'No Longer Needed' folder"
   - Well-defined: Yes (standard file move operation)
   - Clear success: Yes (all files moved, no errors)
   - Load balance: Yes (divide files evenly among agents)
   - Similar tasks: Yes (all file moves)
   - User intervention: No (fully automated)
   - **Verdict: Perfect for v1.3**

2. **Batch Configuration Updates:** "Update API endpoint in 30 config files"
   - Well-defined: Yes (standard find-replace)
   - Clear success: Yes (all files updated correctly)
   - Load balance: Yes (divide files evenly)
   - Similar tasks: Yes (all same operation)
   - User intervention: No (automated with verification)
   - **Verdict: Perfect for v1.3**

3. **Standard Deployment:** "Deploy 8 L2 agents with pre-calculated load balance"
   - Well-defined: Yes (agent deployment is standard)
   - Clear success: Yes (all agents deployed and working)
   - Load balance: Yes (already calculated in Phase 4)
   - Similar tasks: Yes (all agent deployments)
   - User intervention: No (Overwatch handles it)
   - **Verdict: Perfect for v1.3**

---

## Use v1.2 Standard When

### Task Characteristics

⚠️ **Novel/Experimental Tasks**
- Haven't done this type of task before
- Uncertain about approach
- May need to adjust strategy mid-execution
- **Example:** "Implement new architectural pattern we've never tried"

⚠️ **Ambiguous Success Criteria**
- Subjective evaluation needed
- Success depends on user judgment
- No clear pass/fail conditions
- **Example:** "Improve code quality" (what does "improve" mean?)

⚠️ **Complex Load Balancing**
- Uneven workload distribution
- Complex dependencies between tasks
- Difficult to predict task duration
- **Example:** Tasks A and B must finish before C can start

⚠️ **Heterogeneous Tasks**
- Different types of tasks mixed together
- Different validation criteria for each
- Lots of special cases
- **Example:** "Fix bug A, add feature B, update docs C, refactor D"

⚠️ **User Intervention Likely**
- User may want to review mid-execution
- Decision points during execution
- May need to adjust based on results
- **Example:** "Try approach A, if it doesn't work, ask me what to do"

### Operational Considerations

⚠️ **Learning/Research Tasks**
- Exploring new technology
- Gathering information
- Experimenting with approaches
- Ziggie needs to stay involved for learning

⚠️ **Debugging/Troubleshooting**
- Problem diagnosis in progress
- Root cause unknown
- May need to pivot strategy
- Ziggie's direct oversight beneficial

⚠️ **High Risk Operations**
- Irreversible changes
- Production system modifications
- Data deletion/migration
- Ziggie should maintain direct control

### Examples of Good v1.2 Use Cases

1. **Architectural Design:** "Design new hierarchical protocol for nested agent deployment"
   - Well-defined: No (novel design task)
   - Clear success: No (subjective quality evaluation)
   - Load balance: N/A (single L1 agent task)
   - User intervention: Yes (user feedback during design)
   - **Verdict: Use v1.2 (or no Overwatch at all)**

2. **Debugging:** "Fix Control Center Services error - cause unknown"
   - Well-defined: No (diagnosis needed first)
   - Clear success: Somewhat (Services page works, but may need user testing)
   - Load balance: Uncertain (depends on root cause)
   - User intervention: Possible (user may need to test/verify)
   - **Verdict: Use v1.2 (stay involved)**

3. **Code Refactoring:** "Refactor codebase for better maintainability"
   - Well-defined: No (subjective "better maintainability")
   - Clear success: No (requires user judgment)
   - Load balance: Uncertain (depends on what needs refactoring)
   - User intervention: Likely (user wants to review changes)
   - **Verdict: Use v1.2 (Ziggie oversight needed)**

---

## Decision Matrix

Use this matrix to score your task:

| Question | Yes = +1 | No = 0 |
|----------|----------|--------|
| Is the task well-defined and repeatable? | +1 | 0 |
| Are success criteria clear and objective? | +1 | 0 |
| Is load balancing straightforward? | +1 | 0 |
| Are all tasks similar/uniform? | +1 | 0 |
| Is user intervention unlikely? | +1 | 0 |

**Score Interpretation:**
- **5 points:** Strong candidate for v1.3 (Hierarchical) - Recommend to user
- **3-4 points:** Could use v1.3, but ask user preference
- **1-2 points:** Use v1.2 (Standard) - Direct Ziggie oversight
- **0 points:** Definitely v1.2 (Standard) - Do not recommend v1.3

### Example Scoring

**Task: "Archive 50 migration files to backup folder"**
- Well-defined? Yes (+1)
- Clear success? Yes (+1)
- Straightforward load balance? Yes (+1)
- Tasks similar? Yes (+1)
- User intervention unlikely? Yes (+1)
- **Total: 5/5 → Recommend v1.3**

**Task: "Design new protocol integration"**
- Well-defined? No (0)
- Clear success? No (0)
- Straightforward load balance? N/A (0)
- Tasks similar? N/A (0)
- User intervention unlikely? No (0)
- **Total: 0/5 → Use v1.2 or no Overwatch**

---

## User Communication Templates

### Recommending v1.3 to User

```
Based on my analysis, this task is a strong candidate for hierarchical deployment (Protocol v1.3).

Task Characteristics:
- Well-defined: [Yes - standard file archiving]
- Clear success criteria: [Yes - all 50 files moved, no errors]
- Load balancing: [Straightforward - 5 agents, 10 files each]
- Task similarity: [Yes - all file move operations]
- User intervention needed: [No - fully automated]

In hierarchical mode:
1. I'll perform analysis and planning (Phases 1-5)
2. Deploy Overwatch agent to autonomously manage 5 L2 workers
3. Overwatch handles deployment, monitoring, and scoring
4. I'll receive final report and summarize results to you

Benefits:
- Faster deployment (Overwatch deploys workers in parallel)
- Comprehensive audit trail (Overwatch final report + 5 L2 completion reports)
- Same quality standards (100/100 score achievable)

Do you approve hierarchical deployment (v1.3), or would you prefer standard deployment (v1.2) where I deploy workers directly?
```

### User Asks "Which Protocol Should We Use?"

```
Let me assess your task:

[Run through decision matrix]

Based on this assessment, I recommend [v1.2 Standard / v1.3 Hierarchical] because:
- [Reason 1]
- [Reason 2]
- [Reason 3]

Would you like to proceed with [recommended protocol], or would you prefer the other approach?
```

### User Explicitly Requests v1.3 for Unsuitable Task

```
I understand you'd like to use hierarchical deployment (v1.3), but I have concerns:

This task may not be well-suited for v1.3 because:
- [Concern 1: e.g., success criteria are subjective]
- [Concern 2: e.g., user intervention may be needed]
- [Concern 3: e.g., task is novel/experimental]

Recommendations:
1. Use v1.2 (Standard) for this task - I'll maintain direct oversight
2. If you prefer v1.3, I'll attempt it but may need to fall back to v1.2 if issues arise

How would you like to proceed?
```

---

## Fallback Strategy

If v1.3 hierarchical deployment fails, automatically fall back to v1.2:

```
Hierarchical Deployment Failure Protocol:

1. Overwatch detects critical failure (cannot deploy L2 workers, multiple agent failures, etc.)
2. Overwatch reports failure to Ziggie with details
3. Ziggie informs user:

   "Hierarchical deployment encountered an error:
   [Error details from Overwatch]

   I recommend retrying in standard mode (v1.2) where I deploy workers directly.
   This will be slower but gives me more control to handle issues.

   Do you approve switching to standard mode?"

4. If user approves:
   - Ziggie switches to v1.2
   - Deploys L2 workers directly (standard protocol)
   - Provides standard Overwatch monitoring
   - Completes task in standard mode

5. If user declines:
   - Ziggie reports task incomplete
   - Documents failure in ZIGGIE_MEMORY.md
   - Awaits further user instructions
```

---

## Summary

### Use v1.3 (Hierarchical) For:
- ✅ Standard batch operations
- ✅ File archiving/organization
- ✅ Configuration updates
- ✅ Repetitive deployments
- ✅ Well-defined tasks with clear success criteria

### Use v1.2 (Standard) For:
- ⚠️ Novel/experimental tasks
- ⚠️ Debugging and troubleshooting
- ⚠️ Architectural design work
- ⚠️ Tasks requiring user judgment
- ⚠️ High-risk operations
- ⚠️ Research and learning tasks

### Default Behavior:
- **v1.2 is the default** - Use unless task clearly fits v1.3 criteria
- **Always ask user** before using v1.3
- **Provide fallback** if v1.3 fails

### Key Principle:
**When in doubt, use v1.2.** Hierarchical deployment (v1.3) is an optimization for well-defined, repeatable tasks. Standard deployment (v1.2) works for everything and provides more direct control.

---

**Version:** 1.0
**Last Updated:** 2025-11-09
**Maintained By:** Ziggie

**Cats rule. Choose the right tool for the job!** 🎯
