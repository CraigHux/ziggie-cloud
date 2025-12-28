# QUICK REFERENCE CARD
## Agent Creation Standards at a Glance

**Use this when creating or updating any agent file**

---

## FILE NAMING

### L1 Agents
```
Format: XX_AGENT_NAME_AGENT.md
Range:  01-12
Example: 10_CREATIVE_DIRECTOR_AGENT.md ✓
Wrong:   CreativeDirector.md ✗
Wrong:   10_creative_director.md ✗
```

### L2 Agents
```
Format: L2.X.Y.md
X=L1#:  1-12
Y=Sub:  1-9
Example: L2.10.1.md ✓
Wrong:   L2_10_1.md ✗
Wrong:   L2.10.md ✗
```

### L3 Agents
```
Format: L3.X.Y.Z.md
X=L1#:  1-12
Y=L2#:  1-9
Z=Micro: 1-9
Example: L3.10.1.1.md ✓
Wrong:   L3-10-1-1.md ✗
Wrong:   L3_10.1.1.md ✗
```

---

## DOCUMENTATION STRUCTURE

### Required Sections (in order)

```markdown
# AGENT NAME EMOJI

## ROLE
[One-liner]

## PRIMARY OBJECTIVE
[Specific goal]

## CORE RESPONSIBILITIES
### 1. [Category]
- Bullet points

### 2. [Category]
- Bullet points

## ACCESS PERMISSIONS
**Read/Write Access:**
**Read-Only Access:**
**Execute Access:**

## [DOMAIN-SPECIFIC SECTION]
[Custom content]

## COMMUNICATION PROTOCOLS
### To [Agent Name]
- Details

## SUCCESS METRICS
[Measurable targets]

## ESCALATION
[Procedures]

---

**Remember:** [Closing statement]
```

---

## EMOJI USAGE

### Current 9 Agents
```
L1.1 = 🎨 Art Director
L1.2 = 🐱 Character Pipeline
L1.3 = 🏗️ Environment Pipeline
L1.4 = 💻 Game Systems Developer
L1.5 = 🖥️ UI/UX Developer
L1.6 = ⚖️ Content Designer
L1.7 = 🔗 Integration
L1.8 = ✅ QA Testing
L1.9 = 🚀 Migration
```

### New 3 Agents
```
L1.10 = 🎬 Creative Director
L1.11 = ✍️ Copywriter
L1.12 = 👥 Community Manager
```

---

## LINE COUNTS

| Type | Lines | Rule |
|------|-------|------|
| L1 Agent | 200-400 | Comprehensive but concise |
| L2 Agent | 100-200 | More focused |
| L3 Agent | 50-100 | Hyper-specific |
| Documentation | 300-500 | Detailed guidance |

---

## CORE RESPONSIBILITY CATEGORIES

### Typical Count: 4-5 Categories

**Structure:**
```
### 1. [Major Responsibility Area]
- Sub-point 1 (4-8 bullets)
- Sub-point 2
- Sub-point 3
- Sub-point 4

### 2. [Another Major Area]
- Sub-point 1 (4-8 bullets)
...

[Repeat 2-3 more times]
```

---

## ACCESS PERMISSIONS TEMPLATE

### Read/Write Access:
```
- C:\meowping-rts\[primary-work-area]\
- C:\meowping-rts\design-docs\[relevant-files]
- C:\project-data\[data-files]
```
Target: 6-10 paths

### Read-Only Access:
```
- C:\meowping-rts\ref-docs\
- C:\reference-assets\
```
Target: 3-5 paths

### Execute Access:
```
- [Tool/Software]
- [API Endpoints]
- [Script permissions]
```
Target: 1-3 items

---

## COMMUNICATION PROTOCOLS FORMAT

```markdown
## COMMUNICATION PROTOCOLS

### To [Related Agent 1]
- How you communicate
- What information flows
- Expected response time

### To [Related Agent 2]
- Details...

### To [Related Agent 3]
- Details...
```

Target: 3-5 communication pathways per L1 agent

---

## SUCCESS METRICS TEMPLATE

```markdown
## SUCCESS METRICS

Track these metrics:
- [Metric 1]: [Description] (target: [X%/Y units])
- [Metric 2]: [Description] (target: [X%/Y units])
- [Metric 3]: [Description] (target: [X%/Y units])
- [Metric 4]: [Description] (target: [X%/Y units])
```

Target: 3-5 measurable metrics per agent

---

## ZIGGIE CONTEXT

Every agent should mention:
```
- Game title: "Ziggie"
- Concept: Cat heroes vs AI/robot enemies
- Genre: Real-time strategy (RTS)
- Art style: Comic book aesthetic
- Scope: Campaign, multiplayer, multiple factions

[How this agent contributes to the game]
```

---

## COMMON MISTAKES TO AVOID

| Mistake | Problem | Fix |
|---------|---------|-----|
| `09_AGENT.md` not `09_NAME_AGENT.md` | Not descriptive | Always include agent name |
| `L2.10.1.1.md` | Wrong format (too many dots) | Use only 3 dots for L3 |
| Mixed emoji (🎨 vs 🎭) | Inconsistent branding | Check master list |
| 1,000+ line document | Too verbose | Keep L1 under 400 lines |
| "TBD" sections | Incomplete | Fill in all required sections |
| No Ziggie reference | Context lost | Add 1-2 sentences about game |
| Orphaned in old folder | Lost/duplicate | Always use C:\Ziggie\ai-agents\ |

---

## VALIDATION CHECKLIST (Quick Version)

Before submitting any agent file:

- [ ] Filename format correct (XX_NAME_AGENT.md or L#.X.Y.Z.md)
- [ ] All 6 required sections present
- [ ] Proper emoji for domain
- [ ] 200-400 words (for L1)
- [ ] Ziggie mentioned
- [ ] Communication protocols defined
- [ ] No "TBD" or placeholder text
- [ ] Proper markdown formatting
- [ ] No typos or grammar errors
- [ ] Saved in C:\Ziggie\ai-agents\

---

## AGENT TIER RESPONSIBILITIES

### Tier 1: Production (L1.1-3)
- Create visual assets
- Generate characters and environments
- Enforce quality standards
- Manage creative workflow

### Tier 2: Game Systems (L1.4-6)
- Implement game mechanics
- Design user interface
- Balance gameplay
- Create design documents

### Tier 3: Operations (L1.7-9)
- Integrate assets into game
- Test quality
- Manage infrastructure
- Handle migrations

### Tier 4: Creative (L1.10-12)
- Define vision and narrative
- Write all game text
- Engage with community
- Guide creative direction

---

## FILE LOCATION

### ONLY acceptable location:
```
C:\Ziggie\ai-agents\
```

### NOT acceptable:
```
C:\Ziggie\agents\           ✗ Old location
C:\Desktop\                  ✗ Desktop
C:\Users\...\Documents\      ✗ User folder
Desktop                      ✗ Relative path
./ai-agents/                 ✗ Relative path
```

**RULE: Always use absolute path C:\Ziggie\ai-agents\**

---

## QUICK LOOKUP TABLE

### Which Agent Should Handle...?

| Task | Agent | L1 Number |
|------|-------|-----------|
| Character styling | Art Director | 1 |
| Character assets | Character Pipeline | 2 |
| Buildings/props | Environment Pipeline | 3 |
| Game code | Game Systems Dev | 4 |
| Player interface | UI/UX Developer | 5 |
| Game balance | Content Designer | 6 |
| Asset import | Integration | 7 |
| Quality testing | QA Testing | 8 |
| Infrastructure | Migration | 9 |
| Story direction | Creative Director | 10 |
| Dialogue/text | Copywriter | 11 |
| Players/feedback | Community Manager | 12 |

---

## DOCUMENTATION FILES (Master List)

### In C:\Ziggie\ai-agents\

```
CONSISTENCY_GUIDE.md
├─ Standards for all agents
└─ Use this when in doubt

TEMPLATE_L1_AGENT.md
├─ Copy to create new L1 agent
└─ Customize each section

AGENT_HIERARCHY_DIAGRAM.md
├─ Visual organization of 1,404 agents
└─ See how agents relate

EXPANSION_CHECKLIST.md
├─ Task list for 819→1,884 expansion
└─ Track progress here

QUICK_REFERENCE.md
├─ This file
└─ Quick lookup for standards

L3_MICRO_AGENT_ARCHITECTURE.md
├─ Details on all L3 agents
└─ Reference for specialization

SUB_AGENT_ARCHITECTURE.md
├─ Details on all L2 agents
└─ Reference for sub-domains
```

---

## COMMON QUESTIONS

### Q: How many sections must an L1 agent have?
**A:** 6 required sections minimum (ROLE, PRIMARY OBJECTIVE, CORE RESPONSIBILITIES, ACCESS PERMISSIONS, COMMUNICATION PROTOCOLS, SUCCESS METRICS, ESCALATION)

### Q: Can I use different emoji for same domain?
**A:** No. Consistency is critical. Use the master list.

### Q: What if agent doesn't fit any category?
**A:** Create a new L1 category 13+, but verify necessity first.

### Q: How long should agent descriptions be?
**A:** L1: 200-400 lines | L2: 100-200 lines | L3: 50-100 lines

### Q: Where should I save the file?
**A:** Always C:\Ziggie\ai-agents\ - never in subdirectories without explicit instruction

### Q: Can I use L1.1 as filename?
**A:** No. L1 agents use XX_NAME_AGENT.md format (01_ART_DIRECTOR_AGENT.md)

### Q: How many L2 agents per L1?
**A:** Always exactly 9. No more, no fewer.

### Q: How many L3 agents per L2?
**A:** Always exactly 9. No more, no fewer.

---

## CREATING NEW L1 AGENT (Quick Steps)

1. **Copy template:**
   ```
   Copy TEMPLATE_L1_AGENT.md
   ```

2. **Name file correctly:**
   ```
   10_CREATIVE_DIRECTOR_AGENT.md
   (or 11, 12 for new agents)
   ```

3. **Fill in sections:**
   - Replace [BRACKETED] placeholders
   - Remove comments and examples
   - Keep structure identical

4. **Add emoji:**
   ```
   # CREATIVE DIRECTOR AGENT 🎬
   ```

5. **Define 9 sub-domains:**
   - Plan L2.10.1 through L2.10.9
   - Ensure no overlap
   - Document specializations

6. **Validate:**
   - Run checklist above
   - Check file naming
   - Verify Meow Ping context
   - Proofread

7. **Save:**
   ```
   C:\Ziggie\ai-agents\10_CREATIVE_DIRECTOR_AGENT.md
   ```

---

## REFERENCE LINKS

- Full standards: CONSISTENCY_GUIDE.md
- Full template: TEMPLATE_L1_AGENT.md
- Full hierarchy: AGENT_HIERARCHY_DIAGRAM.md
- Full tasks: EXPANSION_CHECKLIST.md
- Full architecture: L3_MICRO_AGENT_ARCHITECTURE.md

---

**Print this page and keep it handy when creating agents!**

Version: 1.0
Created: 2025-11-08
