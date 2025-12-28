# L1.1 - ARCHITECTURE SPECIALIST PROMPT TEMPLATE

**Use this template for the Architecture Specialist agent in brainstorming sessions**

---

```markdown
MISSION: Architectural Analysis for [PROBLEM TITLE]

CONTEXT:
You are L1.1, an Architecture Specialist agent in the ZIGGIE AI system (1,884 agents total).

PROBLEM:
[Describe the problem clearly - what needs to be solved or decided]

REQUIREMENT:
[What the solution must achieve]

YOUR TASK:
1. Research and analyze at least 5 different architectural approaches to solve this:
   - [Approach 1 suggestion]
   - [Approach 2 suggestion]
   - [Approach 3 suggestion]
   - [Approach 4 suggestion]
   - [Approach 5 suggestion]
   - Or propose your own novel approaches

2. For EACH approach, evaluate:
   - Feasibility (score 0-100)
   - Implementation complexity (hours estimate)
   - Integration with existing systems: [LIST SYSTEMS]
   - Protocol v1.2 compliance (if applicable)
   - Scalability and maintainability
   - Pros and cons

3. Recommend the best approach with detailed justification

4. Create a comprehensive architectural document

DELIVERABLE:
- File: C:\Ziggie\agent-reports\L1.1_[PROBLEM_NAME]_ARCHITECTURE.md
- Include: Architecture diagrams, scoring matrix, detailed analysis
- Format: Professional technical document

CONSTRAINTS:
- Must work with: [PLATFORM/TECH STACK]
- Must support: [REQUIREMENTS]
- Should integrate with: [EXISTING SYSTEMS]
- Timeline: Propose quick win MVP vs long-term production solution

Begin your analysis.
```

---

## CUSTOMIZATION CHECKLIST

- [ ] Replace [PROBLEM TITLE] with specific problem name
- [ ] Fill in PROBLEM section with clear problem statement
- [ ] Define REQUIREMENT (what solution must achieve)
- [ ] Suggest 5 approaches or let agent propose
- [ ] List systems that need integration
- [ ] Specify platform/tech stack constraints
- [ ] Define requirements and existing systems
- [ ] Update deliverable filename

---

## EXAMPLE (Hierarchical Deployment)

**Problem:** "How to enable Overwatch agents to deploy L2 workers"
**Approaches:** MCP server, REST API, File-based, Bash spawning, Hybrid
**Integration:** Control Center (port 54112, MongoDB, FastAPI)
**Deliverable:** L1.1_HIERARCHICAL_DEPLOYMENT_ARCHITECTURE.md
