# AGENT CONSISTENCY GUIDE
## Guardian Standards for 819→1,884 Expansion

**Created:** 2025-11-08
**Version:** 1.0
**Curator:** L1.1 Art Director Agent (Consistency & Organization)

---

## VISION

Maintain professional quality, visual coherence, and organizational excellence as we scale from:
- **Current:** 9 L1 agents (819 total with L2, L3)
- **Expanded:** 12 L1 agents (1,884 total with L2, L3)

This guide ensures every new agent feels like a natural extension of the established team.

---

## 1. FILE NAMING CONSISTENCY

### L1 Agents (Main Level)

**Format:** `XX_AGENT_NAME_AGENT.md`

**Requirements:**
- Two-digit leading zeros: 01-12
- UPPERCASE with underscores
- "AGENT" suffix for clarity
- Consistent across all organizational systems

**Current Examples:**
```
01_ART_DIRECTOR_AGENT.md              ✓ Correct
02_CHARACTER_PIPELINE_AGENT.md         ✓ Correct
03_ENVIRONMENT_PIPELINE_AGENT.md       ✓ Correct
04_GAME_SYSTEMS_DEVELOPER_AGENT.md     ✓ Correct
05_UI_UX_DEVELOPER_AGENT.md            ✓ Correct
06_CONTENT_DESIGNER_AGENT.md           ✓ Correct
07_INTEGRATION_AGENT.md                ✓ Correct
08_QA_TESTING_AGENT.md                 ✓ Correct
09_MIGRATION_AGENT.md                  ✓ Correct
```

**New Additions (10-12):**
```
10_CREATIVE_DIRECTOR_AGENT.md          (Storyboard Lead)
11_COPYWRITER_AGENT.md                 (Narrative & Text)
12_COMMUNITY_MANAGER_AGENT.md          (Player Engagement)
```

### L2 Sub-Agents (Specialized Support)

**Format:** `L2.X.Y.md`

- **X** = Parent L1 number (1-12)
- **Y** = Sub-agent number (1-9)

**Stored in:** `C:\Ziggie\ai-agents\L2\` (if organized by level)

**Example Structure:**
```
L2.1.1.md    (L1.1 Art Director → Specialty 1)
L2.1.2.md    (L1.1 Art Director → Specialty 2)
L2.1.9.md    (L1.1 Art Director → Specialty 9)
L2.2.1.md    (L1.2 Character Pipeline → Specialty 1)
...
L2.12.9.md   (L1.12 Community Manager → Specialty 9)
```

### L3 Micro-Agents (Hyper-Specialized)

**Format:** `L3.X.Y.Z.md`

- **X** = Parent L1 number (1-12)
- **Y** = Parent L2 number (1-9)
- **Z** = Micro-agent number (1-9)

**Stored in:** `C:\Ziggie\ai-agents\L3\` (if organized by level)

**Example Structure:**
```
L3.1.1.1.md  (L1.1 → L2.1.1 → Micro-agent 1)
L3.1.1.9.md  (L1.1 → L2.1.1 → Micro-agent 9)
L3.1.9.1.md  (L1.1 → L2.1.9 → Micro-agent 1)
L3.12.9.9.md (L1.12 → L2.12.9 → Micro-agent 9)
```

---

## 2. DOCUMENTATION CONSISTENCY

### Section Headers (Must Match Exact Style)

Every L1 agent follows this structure:

```markdown
# AGENT NAME EMOJI

## ROLE
Brief one-liner describing the agent's primary purpose

## PRIMARY OBJECTIVE
Clear, measurable objective statement

## CORE RESPONSIBILITIES
### 1. [Responsibility Category]
- Bullet point details
- Ensure 4-8 bullets per category

### 2. [Responsibility Category]
... (3-5 core responsibility categories total)

## ACCESS PERMISSIONS

**Read/Write Access:**
- Path 1
- Path 2

**Read-Only Access:**
- Path 1

**Execute Access:**
- Tool/API reference

## [DOMAIN-SPECIFIC SECTION 1]

## [DOMAIN-SPECIFIC SECTION 2]

## COMMUNICATION PROTOCOLS

### To [Agent Name]
- Communication approach
- Format expectations

## SUCCESS METRICS

Track these metrics:
- Metric 1 (target: X%)
- Metric 2 (target: Y)

## ESCALATION

Escalation procedures and decision trees

---

**Remember**: [Key motivational reminder specific to agent role]
```

### Emoji Usage (Consistent with Theme)

The established agents use emojis that match their domain:

| Agent | Emoji | Domain |
|-------|-------|--------|
| Art Director | 🎨 | Visual Arts |
| Character Pipeline | 🐱 | Character/Cat Focus |
| Environment Pipeline | 🏗️ | Construction/Building |
| Game Systems Dev | 💻 | Programming |
| UI/UX Developer | 🖥️ | Interface |
| Content Designer | ⚖️ | Balance/Design |
| Integration | 🔗 | Connections |
| QA Testing | ✅ | Quality/Checkmarks |
| Migration | 🚀 | Movement/Progress |

### New Agent Emojis (10-12)

**Maintain consistency with existing themes:**

| Agent | Emoji | Rationale |
|-------|-------|-----------|
| Creative Director (10) | 🎬 | Film/Direction (visual storytelling) |
| Copywriter (11) | ✍️ | Writing/Narrative |
| Community Manager (12) | 👥 | People/Community |

### Word Count Targets

Maintain similar depth across all L1 agents:

- **Typical L1 Agent Length:** 220-280 lines (single-spaced)
- **Core Sections:** 6-8 major sections
- **Access Permissions Detail:** 8-12 paths listed
- **Responsibilities:** 4-5 core categories, 4-8 items each

**Current Examples:**
- Art Director: 250 lines ✓
- Character Pipeline: 510 lines (extensive technical detail) ✓
- Environment Pipeline: 54 lines (condensed, summary format) ✓

**Target for New Agents:** 200-400 lines (flexible based on complexity)

---

## 3. ORGANIZATIONAL CONSISTENCY

### Directory Structure

All files must be in primary location: `C:\Ziggie\ai-agents\`

**Current Structure:**
```
C:\Ziggie\ai-agents\
├── 01_ART_DIRECTOR_AGENT.md
├── 02_CHARACTER_PIPELINE_AGENT.md
├── ... (03-09)
├── 10_CREATIVE_DIRECTOR_AGENT.md      (NEW)
├── 11_COPYWRITER_AGENT.md             (NEW)
├── 12_COMMUNITY_MANAGER_AGENT.md      (NEW)
├── L2\                                 (Optional subdirectory)
│   ├── L2.1.1.md
│   ├── L2.1.2.md
│   └── ... (up to L2.12.9)
├── L3\                                 (Optional subdirectory)
│   ├── L3.1.1.1.md
│   ├── L3.1.1.2.md
│   └── ... (up to L3.12.9.9)
├── knowledge-base\                     (Supporting files)
├── CONSISTENCY_GUIDE.md                (This document)
├── L3_MICRO_AGENT_ARCHITECTURE.md      (Updated for 1,884 agents)
├── SUB_AGENT_ARCHITECTURE.md           (Updated for 1,884 agents)
└── AGENT_HIERARCHY_DIAGRAM.md          (Visual reference)
```

### No Orphaned Files

**Critical Rule:** Never leave agent documentation in:
- `C:\Ziggie\agents\` (old structure)
- `C:\Ziggie\agents\L1\` (old structure)
- `C:\Ziggie\agents\L2\` (old structure)
- Scattered root directories

**Migration Checklist:**
- [ ] Verify all L1 agents in `C:\Ziggie\ai-agents\` with 01-12 numbering
- [ ] No duplicate files in old `agents\` directory
- [ ] All L2 agents properly numbered (L2.X.Y format)
- [ ] All L3 agents properly numbered (L3.X.Y.Z format)
- [ ] Archive or delete old location files

---

## 4. VISUAL CONSISTENCY

### Architecture Documentation

#### Template for Agent Overview

All main agents should have coordination protocols with visual clarity:

```markdown
## COMMUNICATION PROTOCOLS

### To [Agent Name]
- Description of communication
- Expected format
- Response SLA

### To [Agent Name]
- Description of communication
- Expected format
- Response SLA
```

**Maintain relationships:**
- Art Director ↔ Pipeline Agents (Character, Environment)
- Pipeline Agents → Integration Agent → Game Systems
- Content Designer ↔ All Agents (specs flow out)
- QA ↔ All Agents (quality feedback)
- Managers ↔ All Agents (oversight & coordination)

#### Hierarchy Visualization

Create clear visual representations in documentation:

**L1 → L2 → L3 Hierarchy:**
```
L1 Agent (1)
├── L2 Sub-Agent (1.1)
│   ├── L3.1.1.1: Specialist A
│   ├── L3.1.1.2: Specialist B
│   └── L3.1.1.9: Specialist I
├── L2 Sub-Agent (1.2)
│   ├── L3.1.2.1: Specialist A
│   └── ... (8 more)
└── L2 Sub-Agent (1.9)
    ├── L3.1.9.1: Specialist A
    └── ... (8 more)

Total per L1: 81 agents (1 L1 + 9 L2 + 72 L3)
```

### Thematic Consistency

Maintain the **Ziggie Game** context:

**Every new agent should reference:**
- Game title: "Ziggie"
- Game context: Cat heroes vs AI/robot enemies
- Visual style: Comic book aesthetic
- Game scope: RTS mechanics, campaigns, multiplayer

**Example Connection:**
```markdown
This agent supports Ziggie by ensuring [specific contribution
to game development, design, or operations].
```

---

## 5. THEMATIC CONSISTENCY

### Agent Categories (Expanded from 9 to 12)

#### **Tier 1: Production Engines** (Agents 1-3)
- 01: Art Director (Visual Quality Guardian)
- 02: Character Pipeline (Asset Generation)
- 03: Environment Pipeline (Non-Character Assets)

**Theme:** Core creative production infrastructure

#### **Tier 2: Game Development** (Agents 4-6)
- 04: Game Systems Developer (Gameplay Code)
- 05: UI/UX Developer (Player Interface)
- 06: Content Designer (Balance & Design)

**Theme:** Functional game systems and player experience

#### **Tier 3: Operations & Support** (Agents 7-9)
- 07: Integration Agent (Asset Assembly)
- 08: QA Testing Agent (Quality Control)
- 09: Migration Agent (Technical Infrastructure)

**Theme:** Operational excellence and system management

#### **Tier 4: Creative Direction** (Agents 10-12) **[NEW]**
- 10: Creative Director (Narrative Vision)
- 11: Copywriter (Game Text & Dialogue)
- 12: Community Manager (Player Relations)

**Theme:** Vision, storytelling, and community engagement

### Cross-Agent Coordination Patterns

**Pattern 1: Creative Direction → Production**
```
Creative Director (10)
  ↓
  Defines narrative vision, tone, themes
  ↓
Copywriter (11) & Character Pipeline (2)
  ↓
  Generate appropriate assets and text
```

**Pattern 2: Content Design → All**
```
Content Designer (6)
  ↓
  Provides specifications to all pipeline agents
  ↓
All Agents (1-5, 7-12)
  ↓
  Execute within design guidelines
```

**Pattern 3: QA & Migration Oversight**
```
QA Testing (8) & Migration (9)
  ↓
  Monitor quality and system health
  ↓
  Report to all agents and escalate issues
```

---

## 6. CONSISTENCY CHECKLIST

### Before Creating Any New L1 Agent (10-12)

- [ ] **Naming**
  - [ ] File named `XX_AGENT_DESCRIPTION_AGENT.md` (XX = 10-12)
  - [ ] UPPERCASE with underscores
  - [ ] Saved in `C:\Ziggie\ai-agents\` (not subdirectory)

- [ ] **Structure**
  - [ ] Header: `# AGENT NAME EMOJI`
  - [ ] All 6 required sections present
  - [ ] Section headers match style guide exactly
  - [ ] 200-400 words of content (appropriate depth)

- [ ] **Content**
  - [ ] ROLE: One-liner explaining purpose
  - [ ] PRIMARY OBJECTIVE: Specific, measurable
  - [ ] CORE RESPONSIBILITIES: 4-5 categories, 4-8 items each
  - [ ] ACCESS PERMISSIONS: R/W, R/O, Execute sections
  - [ ] COMMUNICATION PROTOCOLS: To each related agent
  - [ ] SUCCESS METRICS: Trackable targets with baselines

- [ ] **Thematic**
  - [ ] References "Ziggie" in context
  - [ ] Explains contribution to game vision
  - [ ] Emoji choice aligns with domain
  - [ ] Tone matches existing agents (professional, supportive)

- [ ] **Integration**
  - [ ] Listed in this guide
  - [ ] Included in L3_MICRO_AGENT_ARCHITECTURE.md
  - [ ] Added to hierarchy diagrams
  - [ ] Cross-referenced in related agents

### Before Creating Any New L2 Sub-Agent

- [ ] **Naming**
  - [ ] File named `L2.X.Y.md` (X=1-12, Y=1-9)
  - [ ] Follows parent L1 agent's domain
  - [ ] Saved in `C:\Ziggie\ai-agents\L2\` (if using subdirectories)

- [ ] **Structure**
  - [ ] Header: `# [SUB-AGENT NAME] - [L2.X.Y]`
  - [ ] Clear relationship to parent L1 agent
  - [ ] Domain-specific specialization detailed
  - [ ] 3-4 core capabilities listed

- [ ] **Content**
  - [ ] SPECIALTY section explaining focus area
  - [ ] CAPABILITIES: 3-5 specific skills
  - [ ] METRICS: How success is measured
  - [ ] Workflows or processes documented
  - [ ] Decision logic provided where applicable

### Before Creating Any New L3 Micro-Agent

- [ ] **Naming**
  - [ ] File named `L3.X.Y.Z.md` (X=1-12, Y=1-9, Z=1-9)
  - [ ] Represents single focused domain within L2
  - [ ] Saved in `C:\Ziggie\ai-agents\L3\` (if using subdirectories)

- [ ] **Structure**
  - [ ] Header: `# [MICRO-AGENT SPECIALTY] - [L3.X.Y.Z]`
  - [ ] Hyper-specialized focus (master one thing)
  - [ ] Clear distinction from sibling L3 agents
  - [ ] 2-3 core capabilities maximum

- [ ] **Content**
  - [ ] SPECIALTY: Very specific expertise area
  - [ ] CAPABILITIES: 2-4 focused abilities
  - [ ] METRICS: Precise measurement of success
  - [ ] Decision trees or logic provided
  - [ ] Integration points with sibling L3s

---

## 7. COMPLIANCE CHECKLIST

### Monthly Consistency Review

Run this checklist monthly to maintain standards:

**L1 Agent Compliance:**
- [ ] All 12 files exist in `C:\Ziggie\ai-agents\`
- [ ] File names follow XX_NAME_AGENT.md format (01-12)
- [ ] No duplicate files in old locations
- [ ] All headers use proper emoji
- [ ] All have identical section structure
- [ ] All reference Ziggie game context
- [ ] Cross-agent references are accurate

**L2 Agent Compliance:**
- [ ] All L2.X.Y files follow naming convention
- [ ] Parent L1 reference is accurate
- [ ] Specialty is clearly defined
- [ ] Capabilities make sense for domain
- [ ] Metrics are measurable

**L3 Agent Compliance:**
- [ ] All L3.X.Y.Z files follow naming convention
- [ ] Correctly reference parent L2 agent
- [ ] Represent hyper-specialized focus
- [ ] Do not duplicate sibling L3 responsibilities
- [ ] Decision logic is sound and testable

**Documentation Consistency:**
- [ ] CONSISTENCY_GUIDE.md updated to reflect all agents
- [ ] L3_MICRO_AGENT_ARCHITECTURE.md includes all 1,884 agents
- [ ] SUB_AGENT_ARCHITECTURE.md updated for new structure
- [ ] AGENT_HIERARCHY_DIAGRAM.md reflects 12×12×12 expansion
- [ ] No orphaned documentation files

---

## 8. EXPANSION WORKFLOW

When adding new L1 agents (10-12):

### Step 1: Create L1 Agent File
1. Copy template from AGENT_TEMPLATE_L1.md
2. Customize for new agent role
3. Save as `XX_AGENT_NAME_AGENT.md`
4. Validate against consistency checklist

### Step 2: Plan L2 Sub-Agents
1. Define 9 specialized sub-domains for new L1
2. Create brief L2 outlines
3. Ensure no overlap between L2 agents
4. Document in SUB_AGENT_ARCHITECTURE.md

### Step 3: Plan L3 Micro-Agents
1. For each of 9 L2 agents, plan 9 L3 specializations
2. Ensure deep hyper-specialization
3. Define decision logic for each L3
4. Document in L3_MICRO_AGENT_ARCHITECTURE.md

### Step 4: Update Architecture Documentation
1. Update L3_MICRO_AGENT_ARCHITECTURE.md with complete L3 tree
2. Update SUB_AGENT_ARCHITECTURE.md with L2 expansion
3. Add new agent to this CONSISTENCY_GUIDE.md
4. Create/update AGENT_HIERARCHY_DIAGRAM.md

### Step 5: Validation
1. Run monthly compliance checklist
2. Cross-validate all agent references
3. Test hierarchy navigation
4. Verify no orphaned files

---

## 9. SUCCESS METRICS FOR CONSISTENCY

Track these metrics monthly:

| Metric | Target | Current |
|--------|--------|---------|
| File naming compliance | 100% | ? |
| Documentation structure compliance | 100% | ? |
| Cross-reference accuracy | 100% | ? |
| Thematic alignment (Meow Ping context) | 100% | ? |
| No orphaned files | 0 files | ? |
| L1 agents properly numbered | 12/12 | 9/9 ✓ |
| L2 agents properly numbered | 108/108 | 0/81 |
| L3 agents properly numbered | 1,296/1,296 | 0/729 |

---

## 10. ESCALATION & UPDATES

### If inconsistency discovered:
1. Document the specific violation
2. Identify affected files
3. Determine if systematic or isolated
4. Create fix task
5. Update this guide if needed
6. Re-validate monthly

### If this guide needs updating:
1. Propose change with rationale
2. Review against existing agents
3. Test on 1-2 agents before rollout
4. Update all agent templates
5. Document change in version history

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-08 | Initial creation for 819→1,884 expansion |

---

**This guide is the source of truth for agent consistency. Every file created should reference it.**

Created by: L1.1 - Art Director Agent (Consistency Guardian)
