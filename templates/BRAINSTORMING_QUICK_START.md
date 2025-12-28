# BRAINSTORMING SESSIONS - QUICK START GUIDE

**Use this guide for rapid deployment of L1 brainstorming teams**

---

## STEP 1: CHECK IF YOU NEED BRAINSTORMING

**Score these criteria (need ≥2 for brainstorming):**

- [ ] Decision impact >8 hours of work
- [ ] 3+ viable approaches exist
- [ ] Spans 3+ expertise domains
- [ ] Wrong choice costs >40 hours rework
- [ ] No established solution pattern
- [ ] User explicitly requested architectural input
- [ ] Affects core system architecture

**Score:** ___/7

**Decision:**
- ≥2 → **Deploy Brainstorming Session**
- <2 → Direct implementation

---

## STEP 2: SELECT TEAM SIZE

| Team | When to Use | Decision Impact |
|------|-------------|-----------------|
| 2 agents | Medium complexity | 8-24 hours |
| **3 agents** | **Standard (recommended)** | **1-3 weeks** |
| 5 agents | Critical decision | >3 weeks |

**Selected:** _____ agents

---

## STEP 3: DEFINE FOCUS AREAS

**Standard 3-Agent Team:**

1. **L1.1 - Architecture Specialist**
   - Focus: _________________________________
   - Deliverable file: L1.1_______________.md

2. **L1.2 - Implementation Specialist**
   - Focus: _________________________________
   - Deliverable file: L1.2_______________.md

3. **L1.3 - Protocol/Integration Designer**
   - Focus: _________________________________
   - Deliverable file: L1.3_______________.md

---

## STEP 4: DEPLOY (PARALLEL!)

**IMPORTANT:** Deploy ALL agents in a SINGLE message with multiple Task tool calls.

**Template:**

```markdown
I'm deploying a brainstorming session to [solve X problem].

[Task 1: L1.1 - Architecture Specialist]
MISSION: [Title]
FOCUS: [Specific area]
TASK: [What to analyze]
DELIVERABLE: C:\Ziggie\agent-reports\L1.1_[NAME].md

[Copy full prompt from template library]

[Task 2: L1.2 - Implementation Specialist]
MISSION: [Title]
FOCUS: [Specific area]
TASK: [What to analyze]
DELIVERABLE: C:\Ziggie\agent-reports\L1.2_[NAME].md

[Copy full prompt from template library]

[Task 3: L1.3 - Protocol Designer]
MISSION: [Title]
FOCUS: [Specific area]
TASK: [What to analyze]
DELIVERABLE: C:\Ziggie\agent-reports\L1.3_[NAME].md

[Copy full prompt from template library]
```

---

## STEP 5: WAIT FOR COMPLETION

All agents will work in parallel (~40-45 minutes).

**Monitor:**
- Agent completion status
- No intervention needed (autonomous)

---

## STEP 6: SYNTHESIZE FINDINGS

**Read all agent reports:**
1. C:\Ziggie\agent-reports\L1.1_[NAME].md
2. C:\Ziggie\agent-reports\L1.2_[NAME].md
3. C:\Ziggie\agent-reports\L1.3_[NAME].md

**Identify consensus:**
- All 3 agents agree = 100% consensus (VERY HIGH confidence)
- 2/3 agents agree = 67% consensus (MODERATE confidence)
- Agents disagree = Investigate further

**Select recommendation:**
- Document rationale
- Present to user

---

## STEP 7: PRESENT TO USER

**Format:**

```markdown
## Brainstorming Session Complete

**Agents Deployed:** 3 L1 Sonnet agents
**Consensus:** [X/3 agents agree]

**UNANIMOUS RECOMMENDATION:** [Approach Name]

**Supporting Evidence:**
- L1.1 scored it [X/100] feasibility
- L1.2 estimates [Y hours] to MVP
- L1.3 confirms [protocol/integration compatibility]

**Next Steps:**
1. [Step 1]
2. [Step 2]

[Ask user for approval]
```

---

## EXAMPLE: HIERARCHICAL DEPLOYMENT ARCHITECTURE

**Problem:** Overwatch agents can't deploy L2 workers (Task tool limitation)

**Activation Score:** 6/7 criteria met ✓

**Team Deployed:**
- L1.1 - Architecture Specialist (5 approaches analyzed)
- L1.2 - Implementation Specialist (proof-of-concept code)
- L1.3 - Protocol Designer (Protocol v1.3 spec)

**Execution:** 42 minutes (parallel)

**Consensus:** 100% (all 3 agents recommended Hybrid Python Coordinator)

**Outcome:** File-Based MVP built in 2 hours, validated with real deployment

**Result:** Perfect success

---

## COMMON MISTAKES TO AVOID

❌ **Deploying agents sequentially** → Use parallel deployment
❌ **Overlapping focus areas** → Ensure distinct specializations
❌ **Vague prompts** → Provide specific tasks and deliverables
❌ **Skipping synthesis** → Always analyze all reports together
❌ **Ignoring consensus** → 3/3 agreement is STRONG signal

---

## CHECKLIST

Session Planning:
- [ ] Activation criteria scored (≥2)
- [ ] Team size selected
- [ ] Focus areas defined (no overlap)
- [ ] Deliverable filenames chosen

Deployment:
- [ ] All agents deployed in SINGLE message (parallel)
- [ ] Each agent has specific focus area
- [ ] Deliverable paths specified
- [ ] Model set to Sonnet

Synthesis:
- [ ] All agent reports read
- [ ] Consensus level calculated
- [ ] Recommendation selected
- [ ] Rationale documented

Presentation:
- [ ] Synthesis presented to user
- [ ] Consensus strength communicated
- [ ] Next steps outlined
- [ ] User approval requested

---

**Full Documentation:** C:\Ziggie\PROTOCOL_BRAINSTORMING_SESSIONS.md
**Template Library:** C:\Ziggie\templates\brainstorming\
**Example Session:** C:\Ziggie\agent-reports\L1_BRAINSTORMING_SESSION_TRANSCRIPT.md
