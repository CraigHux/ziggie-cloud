# FitFlow Patterns - Quick Reference for Ziggie

**Purpose**: Fast lookup for proven enterprise patterns from FitFlow
**FitFlow Stats**: 584 pts | 986+ tests | 14 sprints @ 100% | 10/10 quality

---

## 1. Testing Pattern: Agent Execution Validation

### FitFlow Pattern
```typescript
// Create authenticated session with JWT + DB session
await session.createAuthenticatedSession(context, email, { role: 'ADMIN' })
```

### Ziggie Adaptation
```typescript
// Create agent execution context
await agentSession.createAgentContext(agentId, permissions)
await agentSession.executeAgentTask(agentId, taskType, input, expectedOutput)
```

**Files**:
- FitFlow: `packages/e2e-tests/fixtures/test-helpers.ts`
- Ziggie: `tests/agents/agent-test-helpers.ts`

---

## 2. RBAC Pattern: Hierarchical Permissions

### FitFlow Pattern
```typescript
// 5-tier role hierarchy: SUPER_ADMIN > ADMIN > CONTENT_EDITOR > INSTRUCTOR > END_USER
export const adminProcedure = authProcedure.use(requireAdmin)
export const instructorProcedure = authProcedure.use(requireInstructor)
```

### Ziggie Adaptation
```python
# 4-tier agent hierarchy: SYSTEM > L1 > L2 > L3
@router.post("/assets/approve", dependencies=[Depends(require_tier([AgentTier.L1]))])
@router.post("/tasks/delegate", dependencies=[Depends(require_tier([AgentTier.L2, AgentTier.L1]))])
```

**Files**:
- FitFlow: `packages/api/src/middleware/rbac.ts`
- Ziggie: `control-center/backend/middleware/agent_rbac.py`

---

## 3. State Machine Pattern: Workflow Validation

### FitFlow Pattern
```typescript
// Valid state transitions
const STATE_TRANSITIONS: Record<ClassStatus, ClassStatus[]> = {
  DRAFT: ['SUBMITTED'],
  SUBMITTED: ['UNDER_REVIEW'],
  UNDER_REVIEW: ['APPROVED', 'CHANGES_REQUESTED', 'REJECTED'],
  CHANGES_REQUESTED: ['SUBMITTED'], // Allow resubmission
  APPROVED: ['PUBLISHED'],
  REJECTED: [], // Terminal
  PUBLISHED: [] // Terminal
}
```

### Ziggie Adaptation
```python
STATE_TRANSITIONS: Dict[AgentTaskStatus, List[AgentTaskStatus]] = {
    AgentTaskStatus.PENDING: [AgentTaskStatus.ASSIGNED, AgentTaskStatus.CANCELLED],
    AgentTaskStatus.ASSIGNED: [AgentTaskStatus.IN_PROGRESS, AgentTaskStatus.CANCELLED],
    AgentTaskStatus.IN_PROGRESS: [AgentTaskStatus.REVIEW_REQUESTED, AgentTaskStatus.COMPLETED, AgentTaskStatus.FAILED],
    AgentTaskStatus.REVIEW_REQUESTED: [AgentTaskStatus.APPROVED, AgentTaskStatus.REJECTED],
    # ... etc
}
```

**Files**:
- FitFlow: `packages/api/src/services/class-state-machine.ts`
- Ziggie: `control-center/backend/services/agent_state_machine.py`

---

## 4. Audit Logging Pattern: SOC 2/GDPR Compliant Tracking

### FitFlow Pattern
```typescript
model AuditLog {
  id          String   @id @default(cuid())
  action      String   // 'USER_SUSPENDED', 'ROLE_CHANGED', etc.
  entityType  String   // 'User', 'Class', etc.
  entityId    String
  userId      String   // Who performed the action
  ipAddress   String?  // From x-forwarded-for
  metadata    Json?    // Additional context
  createdAt   DateTime @default(now())

  @@index([action])
  @@index([entityType, entityId])
  @@index([userId])
  @@index([createdAt])
}
```

### Ziggie Adaptation
```prisma
model AgentAuditLog {
  id          String      @id @default(cuid())
  action      AgentAction // 'TASK_DELEGATED', 'ASSET_APPROVED', etc.
  agentId     String
  entityType  String      // 'TASK', 'ASSET', 'WORKFLOW', etc.
  entityId    String
  metadata    Json?
  ipAddress   String?
  duration    Int?        // Task execution time (ms)
  createdAt   DateTime    @default(now())

  @@index([action])
  @@index([agentId])
  @@index([entityType, entityId])
  @@index([createdAt])
}
```

**Usage**:
```python
await AgentAuditLogger.log_action(
    action=AgentAction.TASK_DELEGATED,
    agent_id=from_agent_id,
    entity_type='TASK',
    entity_id=task_id,
    metadata={'toAgentId': to_agent_id, 'taskType': task_type}
)
```

**Files**:
- FitFlow: `packages/api/src/routers/audit.ts`, `packages/database/prisma/schema.prisma`
- Ziggie: `control-center/backend/services/audit_log.py`, `control-center/backend/prisma/schema.prisma`

---

## 5. tRPC Pattern: Type-Safe Inter-Agent Communication

### FitFlow Pattern
```typescript
export const adminRouter = createTRPCRouter({
  getUsers: adminProcedure
    .input(z.object({
      search: z.string().optional(),
      role: z.enum(['ADMIN', 'INSTRUCTOR', 'END_USER']).optional(),
      limit: z.number().min(1).max(100).default(20),
      cursor: z.string().optional(),
    }))
    .query(async ({ ctx, input }) => {
      const items = await ctx.prisma.user.findMany({ /* ... */ })
      return { items, nextCursor }
    })
})
```

### Ziggie Adaptation
```typescript
export const agentCommunicationRouter = createTRPCRouter({
  delegateToL3: l2Procedure
    .input(z.object({
      fromAgentId: z.string(),
      toAgentId: z.string(),
      taskType: z.string(),
      input: z.record(z.any()),
      deadline: z.date().optional()
    }))
    .mutation(async ({ ctx, input }) => {
      // Validate target is L3
      const targetAgent = await ctx.prisma.agent.findUnique({ where: { id: input.toAgentId } })
      if (targetAgent.tier !== 'L3') throw new TRPCError({ code: 'BAD_REQUEST', message: 'Can only delegate to L3' })

      // Create task delegation
      const task = await ctx.prisma.agentTask.create({ data: { /* ... */ } })

      // Audit log
      await AgentAuditLogger.log_task_delegation(/* ... */)

      return task
    })
})
```

**Files**:
- FitFlow: `packages/api/src/routers/admin.ts`, `packages/api/src/trpc.ts`
- Ziggie: `control-center/backend/src/routers/agent-communication.ts`, `control-center/backend/src/trpc.ts`

---

## 6. Sprint Methodology: 7-Phase Agent Development

### FitFlow 7-Phase Model
```
Phase 0: Planning (5%)       -> Sprint setup, task assignment
Phase 1: Infrastructure (10%) -> Database, migrations, foundations
Phase 2: Implementation (50%) -> Parallel agent execution (CORE PHASE)
Phase 3: Integration (15%)    -> TypeScript verification, cross-agent merge
Phase 4: E2E Testing (10%)    -> Full test suite execution
Phase 5: Quality Gates (5%)   -> 7-gate verification
Phase 6: Documentation (5%)   -> Evidence, retrospective
```

### Ziggie Adaptation
```
Phase 0: Agent Planning (5%)
├── Define L2 agent responsibilities
├── Identify 12 L3 sub-agents
└── Create agent specification

Phase 1: Agent Infrastructure (10%)
├── Database schema (Prisma migration)
├── API endpoints (FastAPI routes)
└── Agent permissions (RBAC)

Phase 2: Agent Implementation (50%) - PARALLEL
├── Wave 1: L2 Core Logic
├── Wave 2: L3 Agents 1-6
└── Wave 3: L3 Agents 7-12

Phase 3: Integration (15%)
├── TypeScript/Python 0 errors
└── Cross-agent communication tests

Phase 4: E2E Testing (10%)
├── 12 L3 agent tests
├── 1 L2 orchestration test
└── 3 integration tests

Phase 5: Quality Gates (5%)
├── Agent state validation
├── E2E pass rate ≥65%
├── API contract validation
├── Performance benchmarks
└── Audit log integrity

Phase 6: Documentation (5%)
└── Evidence, lessons learned
```

---

## 7. Quality Gates: Agent Validation Framework

### FitFlow Gates
```
Gate 1: TypeScript Errors = 0
Gate 2: E2E Test Pass Rate ≥65%
Gate 3: Production Builds = All packages
Gate 4: Linting = No errors
Gate 5: Database Migrations = All applied
```

### Ziggie Gates
```
Gate 1: Agent State Validation (no ERROR state, no stuck agents)
Gate 2: E2E Test Pass Rate ≥65%
Gate 3: API Contract Validation (OpenAPI spec matches)
Gate 4: Performance Benchmarks (task time, memory, API latency)
Gate 5: Audit Log Integrity (100% coverage)
```

**Implementation**:
```python
class AgentQualityGates:
    async def gate_1_agent_state_validation(self) -> Dict
    async def gate_2_e2e_test_pass_rate(self) -> Dict
    async def gate_3_api_contract_validation(self) -> Dict
    async def gate_4_performance_benchmarks(self) -> Dict
    async def gate_5_audit_log_integrity(self) -> Dict

    async def run_all_gates(self) -> Dict:
        """Run all gates in parallel, return overall pass/fail"""
```

**Files**:
- Ziggie: `tests/quality_gates/agent_quality_gates.py`

---

## 8. Database Schema Patterns

### FitFlow Core Models
```prisma
model User {
  id            String    @id @default(cuid())
  email         String    @unique
  role          Role      @default(END_USER)
  sessions      Session[]
  auditLogs     AuditLog[]
}

model Session {
  id           String   @id @default(cuid())
  sessionToken String   @unique
  userId       String
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  expires      DateTime
}
```

### Ziggie Adaptation
```prisma
model Agent {
  id          String      @id @default(cuid())
  name        String
  tier        AgentTier
  permissions AgentPermission[]
  status      AgentStatus @default(ACTIVE)
  sessions    AgentSession[]
  auditLogs   AgentAuditLog[]
  tasksAssigned AgentTask[] @relation("AssignedTasks")
  tasksCreated  AgentTask[] @relation("CreatedTasks")
}

model AgentSession {
  id           String   @id @default(cuid())
  sessionToken String   @unique
  agentId      String
  agent        Agent    @relation(fields: [agentId], references: [id], onDelete: Cascade)
  expiresAt    DateTime
}

model AgentTask {
  id                String          @id @default(cuid())
  taskType          String
  status            AgentTaskStatus @default(PENDING)
  creatorAgentId    String
  assignedAgentId   String?
  input             Json
  output            Json?
  duration          Int?            // Execution time (ms)
  createdAt         DateTime        @default(now())
}
```

**Key Relationships**:
- Agent → Session (1:many) ≈ User → Session
- Agent → AuditLog (1:many) ≈ User → AuditLog
- Agent → Task (1:many, as creator) ≈ User → Content
- Agent → Task (1:many, as assignee) ≈ Reviewer → ContentReview

---

## Quick Decision Matrix

| Need | FitFlow Pattern | Ziggie Application | Priority |
|------|----------------|-------------------|----------|
| **Test agent execution** | E2E test helpers | `agentSession.executeAgentTask()` | HIGH |
| **Control agent permissions** | RBAC middleware | Tier-based `require_tier()` | HIGH |
| **Track agent actions** | Audit logging | `AgentAuditLogger.log_action()` | HIGH |
| **Validate workflows** | State machine | `AgentStateMachine.validate_transition()` | MEDIUM |
| **Inter-agent messaging** | tRPC procedures | Agent communication router | MEDIUM |
| **Organize development** | 7-phase sprints | Agent development sprints | LOW |
| **Verify quality** | 5 quality gates | Agent quality gates | MEDIUM |

---

## Integration Roadmap (Quick View)

```
Week 1-2:  Foundation (RBAC, Sessions, Audit Log schema)
Week 3-4:  Testing (E2E fixtures, first 10 tests, quality gates)
Week 5-6:  State Machine (AgentStateMachine, task state validation)
Week 7-8:  tRPC (Agent communication routers, tier procedures)
Week 9-10: Sprint Methodology (7-phase process, first sprint)
```

**Success Criteria**: 100+ E2E tests | 100% audit coverage | 5/5 gates passing | 0 type errors

---

## File Mapping Reference

### FitFlow Source Files
| Pattern | File |
|---------|------|
| Testing | `packages/e2e-tests/fixtures/test-helpers.ts` |
| RBAC | `packages/api/src/middleware/rbac.ts` |
| State Machine | `packages/api/src/services/class-state-machine.ts` |
| Audit | `packages/api/src/routers/audit.ts` |
| tRPC | `packages/api/src/trpc.ts`, `packages/api/src/routers/admin.ts` |
| Schema | `packages/database/prisma/schema.prisma` |

### Ziggie Target Files
| Pattern | File |
|---------|------|
| Testing | `tests/agents/agent-test-helpers.ts` |
| RBAC | `control-center/backend/middleware/agent_rbac.py` |
| State Machine | `control-center/backend/services/agent_state_machine.py` |
| Audit | `control-center/backend/services/audit_log.py` |
| tRPC | `control-center/backend/src/routers/agent-communication.ts` |
| Quality Gates | `tests/quality_gates/agent_quality_gates.py` |
| Schema | `control-center/backend/prisma/schema.prisma` |

---

**End of Quick Reference**

For detailed implementation examples and full code, see `FITFLOW_PATTERN_INTEGRATION_BRAINSTORM.md`.
