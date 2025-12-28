# FitFlow Pattern Integration for Ziggie Agent Architecture

**Date**: 2025-12-21
**Purpose**: Brainstorm how FitFlow's proven enterprise patterns can upscale Ziggie's agent management system
**FitFlow Achievement**: 584 story points, 986+ E2E tests, 14 sprints @ 100% delivery, 10/10 quality standard
**Ziggie Context**: 1,884 AI agents (12 L1, 144 L2, 1,728 L3) + Control Center + Game Development Platform

---

## Executive Summary

FitFlow has demonstrated enterprise-grade patterns across authentication, testing, state management, audit logging, and API design that are directly applicable to Ziggie's agent orchestration challenges. This document outlines specific integration strategies.

### Key Opportunities

1. **tRPC Agent-to-Agent Communication** - Type-safe inter-agent messaging
2. **RBAC for Agent Access Control** - Hierarchical agent permissions
3. **State Machine Agent Workflows** - Validated agent state transitions
4. **E2E Testing for Agent Validation** - 986+ test pattern adaptation
5. **Audit Logging for Agent Actions** - SOC 2/GDPR compliant tracking
6. **Sprint Methodology for Agent Development** - 7-phase execution model

---

## 1. Testing Patterns: E2E Tests for Agent Validation

### FitFlow Pattern (986+ E2E Tests)

```typescript
// Pattern: Authenticated session creation with JWT + database session
// File: packages/e2e-tests/fixtures/test-helpers.ts

export const session = {
  async createAuthenticatedSession(
    context: BrowserContext,
    userEmail: string,
    options?: { emailVerified?: boolean; role?: Role }
  ): Promise<string> {
    // 1. Create user in database
    const user = await prisma.user.upsert({
      where: { email: userEmail },
      update: { emailVerified: options?.emailVerified !== false ? new Date() : null, role: options?.role || 'END_USER' },
      create: { email: userEmail, name: userEmail.split('@')[0], emailVerified: new Date(), role: options?.role || 'END_USER' }
    })

    // 2. Encode JWT with NEXTAUTH_SECRET
    const encodedToken = await encode({
      token: { id: user.id, email: user.email, name: user.name, role: user.role, emailVerified: user.emailVerified },
      secret: process.env.NEXTAUTH_SECRET!,
      salt: 'authjs.session-token',
      maxAge: 30 * 24 * 60 * 60
    })

    // 3. Create database session with JWT as sessionToken
    await prisma.session.create({
      data: { sessionToken: encodedToken, userId: user.id, expires: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) }
    })

    // 4. Set cookie in browser context
    await context.addCookies([{
      name: 'authjs.session-token',
      value: encodedToken,
      domain: 'localhost',
      path: '/',
      httpOnly: true,
      sameSite: 'Lax'
    }])

    return encodedToken
  }
}
```

### Ziggie Adaptation: Agent Execution Testing

**Use Case**: Validate agent outputs, state transitions, inter-agent communication

```typescript
// C:/Ziggie/tests/agents/agent-test-helpers.ts

import { test, expect } from '@playwright/test'
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export const TEST_AGENTS = {
  l1_artDirector: {
    agentId: 'L1-ART-001',
    name: 'ARTEMIS (Art Director)',
    tier: 'L1',
    permissions: ['CREATE_CONCEPT', 'APPROVE_ASSET', 'ASSIGN_L2_AGENT']
  },
  l2_characterPipeline: {
    agentId: 'L2-CHAR-001',
    name: 'Character Pipeline Agent',
    tier: 'L2',
    permissions: ['GENERATE_CHARACTER', 'REQUEST_REVIEW']
  },
  l3_colorValidator: {
    agentId: 'L3-COLOR-001',
    name: 'Color Palette Validator',
    tier: 'L3',
    permissions: ['VALIDATE_COLORS']
  }
}

export const agentSession = {
  /**
   * Create an agent execution context for testing
   * Similar to FitFlow's authenticated session pattern
   */
  async createAgentContext(agentId: string, permissions: string[]): Promise<string> {
    // 1. Create agent record in database
    const agent = await prisma.agent.upsert({
      where: { id: agentId },
      update: { lastActiveAt: new Date(), permissions },
      create: {
        id: agentId,
        name: TEST_AGENTS[agentId]?.name || agentId,
        tier: TEST_AGENTS[agentId]?.tier || 'L3',
        status: 'ACTIVE',
        permissions,
        createdAt: new Date()
      }
    })

    // 2. Create execution token (JWT-like for agent auth)
    const executionToken = await generateAgentToken({
      agentId: agent.id,
      tier: agent.tier,
      permissions: agent.permissions,
      expiresIn: 3600
    })

    // 3. Create execution session in database
    await prisma.agentSession.create({
      data: {
        sessionToken: executionToken,
        agentId: agent.id,
        expiresAt: new Date(Date.now() + 3600 * 1000)
      }
    })

    return executionToken
  },

  /**
   * Simulate agent task execution
   */
  async executeAgentTask(
    agentId: string,
    taskType: string,
    input: any,
    expectedOutput?: any
  ): Promise<any> {
    const session = await this.createAgentContext(agentId, TEST_AGENTS[agentId].permissions)

    // Execute task via API
    const response = await fetch('http://localhost:8000/api/agents/execute', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Agent-Token': session
      },
      body: JSON.stringify({ taskType, input })
    })

    const result = await response.json()

    // Validate output if expected
    if (expectedOutput) {
      expect(result.output).toMatchObject(expectedOutput)
    }

    return result
  }
}
```

**Example Agent Test**:

```typescript
// C:/Ziggie/tests/agents/character-pipeline.spec.ts

test.describe('Character Pipeline Agent - L2-CHAR-001', () => {
  test.beforeEach(async ({ page }) => {
    // Create L1 Art Director session (can assign tasks to L2)
    await agentSession.createAgentContext(
      TEST_AGENTS.l1_artDirector.agentId,
      TEST_AGENTS.l1_artDirector.permissions
    )
  })

  test('should generate character concept from text prompt', async () => {
    const result = await agentSession.executeAgentTask(
      TEST_AGENTS.l2_characterPipeline.agentId,
      'GENERATE_CHARACTER_CONCEPT',
      {
        prompt: 'Warrior cat archer, medieval fantasy, isometric view',
        style: 'STYLIZED',
        faction: 'BLUE'
      },
      {
        status: 'COMPLETED',
        outputType: 'IMAGE',
        format: 'PNG',
        resolution: '1024x1024'
      }
    )

    expect(result.status).toBe('COMPLETED')
    expect(result.output.url).toMatch(/^https:\/\/.*\.png$/)
  })

  test('should validate against L3 color agent before completion', async () => {
    // Mock L3 agent validation
    const characterResult = await agentSession.executeAgentTask(
      TEST_AGENTS.l2_characterPipeline.agentId,
      'GENERATE_CHARACTER_CONCEPT',
      { prompt: 'Test character', style: 'STYLIZED', faction: 'BLUE' }
    )

    // L3 color validator should auto-trigger
    const validationLog = await prisma.agentTaskLog.findFirst({
      where: {
        taskId: characterResult.taskId,
        agentId: TEST_AGENTS.l3_colorValidator.agentId,
        action: 'VALIDATE_COLORS'
      }
    })

    expect(validationLog).not.toBeNull()
    expect(validationLog?.status).toBe('COMPLETED')
  })

  test('should handle L1 approval workflow', async () => {
    // 1. L2 generates concept
    const concept = await agentSession.executeAgentTask(
      TEST_AGENTS.l2_characterPipeline.agentId,
      'GENERATE_CHARACTER_CONCEPT',
      { prompt: 'Test', style: 'STYLIZED', faction: 'BLUE' }
    )

    // 2. Request L1 review
    const reviewRequest = await agentSession.executeAgentTask(
      TEST_AGENTS.l2_characterPipeline.agentId,
      'REQUEST_L1_REVIEW',
      { conceptId: concept.conceptId }
    )

    expect(reviewRequest.status).toBe('PENDING_REVIEW')

    // 3. L1 approves
    const approval = await agentSession.executeAgentTask(
      TEST_AGENTS.l1_artDirector.agentId,
      'APPROVE_CONCEPT',
      { conceptId: concept.conceptId, approved: true }
    )

    expect(approval.status).toBe('APPROVED')
  })
})
```

**Key Insights**:
- **Pattern Reuse**: FitFlow's session management → Agent execution context
- **Type Safety**: Same Zod validation patterns for agent inputs/outputs
- **Test Isolation**: Each test creates clean agent state (like FitFlow user state)
- **Audit Trail**: Every agent action logged (like FitFlow audit logs)

---

## 2. Auth Patterns: RBAC for Agent Access Control

### FitFlow Pattern (Hierarchical Role System)

```typescript
// File: packages/api/src/middleware/rbac.ts

type Role = 'SUPER_ADMIN' | 'ADMIN' | 'CONTENT_EDITOR' | 'INSTRUCTOR' | 'END_USER'

const ROLE_HIERARCHY: Record<Role, number> = {
  END_USER: 1,
  INSTRUCTOR: 2,
  CONTENT_EDITOR: 3,
  ADMIN: 4,
  SUPER_ADMIN: 5,
}

export const requireAdmin = requireRole(['ADMIN', 'SUPER_ADMIN'])
export const requireInstructor = requireRole(['INSTRUCTOR', 'CONTENT_EDITOR', 'ADMIN', 'SUPER_ADMIN'])

export const adminProcedure = authProcedure.use(requireAdmin)
export const instructorProcedure = authProcedure.use(requireInstructor)
```

### Ziggie Adaptation: Agent Tier Hierarchy

**Use Case**: L1 agents can delegate to L2, L2 can delegate to L3, but not reverse

```typescript
// C:/Ziggie/control-center/backend/middleware/agent_rbac.py

from enum import Enum
from typing import List

class AgentTier(Enum):
    L3 = 1  # Micro-tasks (1,728 agents)
    L2 = 2  # Specialized (144 agents)
    L1 = 3  # Primary (12 agents)
    SYSTEM = 4  # Control Center

TIER_HIERARCHY = {
    AgentTier.L3: 1,
    AgentTier.L2: 2,
    AgentTier.L1: 3,
    AgentTier.SYSTEM: 4
}

class AgentPermission(Enum):
    # L3 Permissions (lowest)
    EXECUTE_TASK = "execute_task"
    REPORT_STATUS = "report_status"

    # L2 Permissions
    DELEGATE_TO_L3 = "delegate_to_l3"
    AGGREGATE_L3_RESULTS = "aggregate_l3_results"
    REQUEST_L1_REVIEW = "request_l1_review"

    # L1 Permissions
    DELEGATE_TO_L2 = "delegate_to_l2"
    APPROVE_ASSET = "approve_asset"
    MODIFY_PIPELINE = "modify_pipeline"
    CREATE_WORKFLOW = "create_workflow"

    # SYSTEM Permissions (highest)
    MANAGE_AGENTS = "manage_agents"
    MODIFY_PERMISSIONS = "modify_permissions"
    ACCESS_AUDIT_LOGS = "access_audit_logs"

def has_permission(agent_tier: AgentTier, required_permission: AgentPermission) -> bool:
    """
    Check if agent tier has permission based on hierarchy
    Similar to FitFlow's hasRole() function
    """
    permission_map = {
        AgentTier.L3: [AgentPermission.EXECUTE_TASK, AgentPermission.REPORT_STATUS],
        AgentTier.L2: [
            AgentPermission.EXECUTE_TASK,
            AgentPermission.REPORT_STATUS,
            AgentPermission.DELEGATE_TO_L3,
            AgentPermission.AGGREGATE_L3_RESULTS,
            AgentPermission.REQUEST_L1_REVIEW
        ],
        AgentTier.L1: [
            AgentPermission.EXECUTE_TASK,
            AgentPermission.REPORT_STATUS,
            AgentPermission.DELEGATE_TO_L3,
            AgentPermission.AGGREGATE_L3_RESULTS,
            AgentPermission.REQUEST_L1_REVIEW,
            AgentPermission.DELEGATE_TO_L2,
            AgentPermission.APPROVE_ASSET,
            AgentPermission.MODIFY_PIPELINE,
            AgentPermission.CREATE_WORKFLOW
        ],
        AgentTier.SYSTEM: list(AgentPermission)  # All permissions
    }

    return required_permission in permission_map.get(agent_tier, [])

def require_tier(allowed_tiers: List[AgentTier]):
    """
    FastAPI dependency for tier-based access control
    Similar to FitFlow's requireRole middleware
    """
    async def tier_checker(agent_token: str = Header(..., alias="X-Agent-Token")):
        # Decode agent token (JWT-like)
        agent_data = decode_agent_token(agent_token)
        agent_tier = AgentTier[agent_data['tier']]

        if agent_tier not in allowed_tiers:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required tier: {[t.name for t in allowed_tiers]}. Your tier: {agent_tier.name}"
            )

        return agent_data

    return tier_checker

# FastAPI route decorators (similar to adminProcedure, instructorProcedure)
@router.post("/assets/approve", dependencies=[Depends(require_tier([AgentTier.L1, AgentTier.SYSTEM]))])
async def approve_asset(asset_id: str, agent: dict = Depends(require_tier([AgentTier.L1]))):
    """Only L1 agents can approve assets"""
    return await approve_asset_logic(asset_id, agent['agentId'])

@router.post("/tasks/delegate-to-l3", dependencies=[Depends(require_tier([AgentTier.L2, AgentTier.L1]))])
async def delegate_to_l3(task: DelegateTask, agent: dict = Depends(require_tier([AgentTier.L2, AgentTier.L1]))):
    """L2 and L1 agents can delegate to L3"""
    return await delegate_task_logic(task, agent['agentId'])
```

**Database Schema for Agent RBAC**:

```prisma
// C:/Ziggie/control-center/backend/prisma/schema.prisma

enum AgentTier {
  L3
  L2
  L1
  SYSTEM
}

enum AgentPermission {
  EXECUTE_TASK
  REPORT_STATUS
  DELEGATE_TO_L3
  AGGREGATE_L3_RESULTS
  REQUEST_L1_REVIEW
  DELEGATE_TO_L2
  APPROVE_ASSET
  MODIFY_PIPELINE
  CREATE_WORKFLOW
  MANAGE_AGENTS
  MODIFY_PERMISSIONS
  ACCESS_AUDIT_LOGS
}

model Agent {
  id          String   @id @default(cuid())
  name        String
  tier        AgentTier
  permissions AgentPermission[]
  status      AgentStatus       @default(ACTIVE)
  createdAt   DateTime          @default(now())

  // Agent sessions (like User sessions in FitFlow)
  sessions    AgentSession[]

  // Audit trail (like AuditLog in FitFlow)
  actions     AgentAuditLog[]

  @@index([tier])
  @@index([status])
}

model AgentSession {
  id           String   @id @default(cuid())
  sessionToken String   @unique
  agentId      String
  agent        Agent    @relation(fields: [agentId], references: [id], onDelete: Cascade)
  expiresAt    DateTime
  createdAt    DateTime @default(now())

  @@index([agentId])
}

model AgentAuditLog {
  id          String   @id @default(cuid())
  action      AgentAction
  agentId     String
  agent       Agent    @relation(fields: [agentId], references: [id])
  entityType  String   // "ASSET", "TASK", "WORKFLOW", etc.
  entityId    String
  metadata    Json?
  ipAddress   String?
  createdAt   DateTime @default(now())

  @@index([action])
  @@index([agentId])
  @@index([entityType, entityId])
  @@index([createdAt])
}
```

**Key Insights**:
- **Direct Pattern Mapping**: FitFlow RBAC (5 roles) → Agent RBAC (4 tiers)
- **Permission Enforcement**: Same middleware pattern (requireRole → require_tier)
- **Audit Trail**: Every agent action logged with metadata
- **Session Management**: Agent sessions tracked like user sessions

---

## 3. Sprint Methodology: 7-Phase Agent Development

### FitFlow Pattern (7-Phase Sprint Execution)

```
Phase 0: Planning (5%)       -> Sprint setup, task assignment
Phase 1: Infrastructure (10%) -> Database, migrations, foundations
Phase 2: Implementation (50%) -> Parallel agent execution (CORE PHASE)
Phase 3: Integration (15%)    -> TypeScript verification, cross-agent merge
Phase 4: E2E Testing (10%)    -> Full test suite execution
Phase 5: Quality Gates (5%)   -> 7-gate verification
Phase 6: Documentation (5%)   -> Evidence, retrospective
```

### Ziggie Adaptation: Agent Development Sprint

**Use Case**: Develop new L2 agent with 12 L3 sub-agents

```
Phase 0: Agent Planning (5%)
├── Define L2 agent responsibilities
├── Identify 12 L3 sub-agents needed
├── Create agent specification (Markdown doc)
└── Assign to development team

Phase 1: Agent Infrastructure (10%)
├── Create agent database schema (Prisma migration)
├── Set up agent API endpoints (FastAPI routes)
├── Configure agent permissions (RBAC rules)
└── Create agent test fixtures

Phase 2: Agent Implementation (50%) - PARALLEL EXECUTION
├── Wave 1: Core L2 Agent Logic
│   ├── Input validation (Zod schemas)
│   ├── Task orchestration (state machine)
│   └── L3 agent delegation
├── Wave 2: L3 Sub-Agent Implementation (12 agents)
│   ├── L3-1 through L3-6 (parallel)
│   └── L3-7 through L3-12 (parallel)
└── Wave 3: Integration Layer
    ├── Result aggregation
    └── Error handling

Phase 3: Agent Integration (15%)
├── TypeScript verification (0 errors)
├── Python type checking (mypy)
├── Cross-agent communication tests
└── API contract validation

Phase 4: Agent E2E Testing (10%)
├── Individual L3 agent tests (12 test files)
├── L2 orchestration tests
├── Inter-agent communication tests
└── Error scenario tests (100% coverage)

Phase 5: Quality Gates (5%)
├── Gate 1: TypeScript/Python 0 errors
├── Gate 2: E2E test pass rate ≥65%
├── Gate 3: All agent builds successful
├── Gate 4: Linting passed
└── Gate 5: Agent state validation

Phase 6: Agent Documentation (5%)
├── Agent specification (Markdown)
├── API documentation (OpenAPI)
├── Test evidence (screenshots)
└── Lessons learned
```

**Example: Character Pipeline Agent Sprint**

```markdown
# Sprint: Character Pipeline Agent (L2-CHAR-001)

## Phase 0: Planning
- L2 Agent: Character Pipeline Agent
- L3 Sub-Agents:
  1. L3-CHAR-PROMPT-001: Prompt Enhancement
  2. L3-CHAR-STYLE-001: Style Transfer
  3. L3-CHAR-COLOR-001: Color Palette Validator
  4. L3-CHAR-PROP-001: Equipment/Prop Validator
  5. L3-CHAR-POSE-001: Pose Validator
  6. L3-CHAR-ANATOMY-001: Anatomy Checker
  7. L3-CHAR-LIGHT-001: Lighting Validator
  8. L3-CHAR-SHADOW-001: Shadow Consistency
  9. L3-CHAR-RESOLUTION-001: Resolution Upscaler
  10. L3-CHAR-FORMAT-001: Format Converter
  11. L3-CHAR-METADATA-001: Metadata Extractor
  12. L3-CHAR-STORAGE-001: Asset Storage

## Phase 2: Implementation (Wave-Based)

### Wave 1: L2 Core Logic (1 agent)
- Input: Text prompt + style parameters
- Process: Orchestrate 12 L3 agents in sequence
- Output: Final character asset + metadata

### Wave 2: L3 Agents 1-6 (parallel)
- Each agent: Input validation → Processing → Output
- Execution: Parallel (6 agents simultaneously)

### Wave 3: L3 Agents 7-12 (parallel)
- Each agent: Input validation → Processing → Output
- Execution: Parallel (6 agents simultaneously)

## Phase 4: E2E Testing
- 12 L3 agent tests (1 per agent)
- 1 L2 orchestration test
- 3 integration tests (L2 → L3 communication)
- Total: 16 E2E tests
```

**Key Insights**:
- **Wave-Based Execution**: Same parallel pattern as FitFlow (Marcus → Alex → Chen)
- **Quality Gates**: Adapted for agent validation instead of code quality
- **Documentation Standard**: Same 10/10 quality requirement

---

## 4. Quality Gates: Agent Output Validation

### FitFlow Pattern (5-Gate Verification)

```
Gate 1: TypeScript Errors = 0
Gate 2: E2E Test Pass Rate ≥65%
Gate 3: Production Builds = All packages
Gate 4: Linting = No errors
Gate 5: Database Migrations = All applied
```

### Ziggie Adaptation: Agent Quality Gates

```
Gate 1: Agent State Validation
├── All agents in expected state (ACTIVE/IDLE/PROCESSING)
├── No agents stuck in ERROR state
└── Session cleanup (no orphaned sessions)

Gate 2: Agent E2E Test Pass Rate ≥65%
├── Individual agent tests
├── Inter-agent communication tests
└── Workflow orchestration tests

Gate 3: Agent API Contract Validation
├── All endpoints return expected schemas
├── OpenAPI spec matches implementation
└── Type safety (Pydantic validation)

Gate 4: Agent Performance Benchmarks
├── Task completion time < threshold
├── Memory usage < limit
└── API response time < 200ms

Gate 5: Agent Audit Log Integrity
├── All actions logged
├── No missing audit entries
└── Metadata complete
```

**Example Gate Implementation**:

```python
# C:/Ziggie/tests/quality_gates/agent_quality_gates.py

import asyncio
from typing import Dict, List
from enum import Enum

class GateStatus(Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"

class AgentQualityGates:
    """
    Adapted from FitFlow's quality gate framework
    Validates agent system health and readiness
    """

    async def gate_1_agent_state_validation(self) -> Dict:
        """Gate 1: Verify all agents in valid states"""
        agents = await prisma.agent.find_many()

        error_agents = [a for a in agents if a.status == 'ERROR']
        stuck_agents = [a for a in agents if a.lastActiveAt < datetime.now() - timedelta(hours=1)]
        orphaned_sessions = await prisma.agentSession.count(where={'expiresAt': {'lt': datetime.now()}})

        passed = len(error_agents) == 0 and len(stuck_agents) == 0 and orphaned_sessions == 0

        return {
            'gate': 'Gate 1: Agent State Validation',
            'status': GateStatus.PASSED if passed else GateStatus.FAILED,
            'details': {
                'total_agents': len(agents),
                'error_agents': len(error_agents),
                'stuck_agents': len(stuck_agents),
                'orphaned_sessions': orphaned_sessions
            }
        }

    async def gate_2_e2e_test_pass_rate(self) -> Dict:
        """Gate 2: E2E test pass rate (FitFlow standard: ≥65%)"""
        # Run pytest with agent tests
        result = subprocess.run(
            ['pytest', 'tests/agents/', '--json-report', '--json-report-file=test_results.json'],
            capture_output=True
        )

        with open('test_results.json') as f:
            test_data = json.load(f)

        total = test_data['summary']['total']
        passed = test_data['summary']['passed']
        pass_rate = (passed / total * 100) if total > 0 else 0

        return {
            'gate': 'Gate 2: E2E Test Pass Rate',
            'status': GateStatus.PASSED if pass_rate >= 65 else GateStatus.FAILED,
            'details': {
                'total_tests': total,
                'passed_tests': passed,
                'pass_rate': f"{pass_rate:.1f}%",
                'threshold': '≥65%'
            }
        }

    async def gate_3_api_contract_validation(self) -> Dict:
        """Gate 3: Validate API contracts match OpenAPI spec"""
        # Load OpenAPI spec
        with open('openapi.yaml') as f:
            spec = yaml.safe_load(f)

        violations = []

        # Test each endpoint
        for path, methods in spec['paths'].items():
            for method, definition in methods.items():
                response = await test_endpoint(method, path, definition)
                if not validate_schema(response, definition['responses']['200']['content']['application/json']['schema']):
                    violations.append(f"{method.upper()} {path}")

        return {
            'gate': 'Gate 3: API Contract Validation',
            'status': GateStatus.PASSED if len(violations) == 0 else GateStatus.FAILED,
            'details': {
                'total_endpoints': len(spec['paths']),
                'violations': violations
            }
        }

    async def run_all_gates(self) -> Dict:
        """Run all quality gates (parallel execution like FitFlow)"""
        gates = await asyncio.gather(
            self.gate_1_agent_state_validation(),
            self.gate_2_e2e_test_pass_rate(),
            self.gate_3_api_contract_validation(),
            self.gate_4_performance_benchmarks(),
            self.gate_5_audit_log_integrity()
        )

        all_passed = all(g['status'] == GateStatus.PASSED for g in gates)

        return {
            'sprint': 'Agent Development Sprint',
            'timestamp': datetime.now().isoformat(),
            'gates': gates,
            'overall_status': 'PASSED' if all_passed else 'FAILED',
            'quality_rating': f"{sum(1 for g in gates if g['status'] == GateStatus.PASSED)}/5"
        }
```

**Key Insights**:
- **Same Structure**: 5 gates, same pass/fail criteria
- **Agent-Specific**: Adapted for agent validation vs code quality
- **Parallel Execution**: Run all gates simultaneously (like FitFlow)

---

## 5. tRPC Patterns: Agent-to-Agent Communication

### FitFlow Pattern (Type-Safe API)

```typescript
// File: packages/api/src/routers/admin.ts

export const adminRouter = createTRPCRouter({
  getUsers: adminProcedure
    .input(z.object({
      search: z.string().optional(),
      role: z.enum(['SUPER_ADMIN', 'ADMIN', 'CONTENT_EDITOR', 'INSTRUCTOR', 'END_USER']).optional(),
      limit: z.number().min(1).max(100).default(20),
      cursor: z.string().optional(),
    }))
    .query(async ({ ctx, input }) => {
      const items = await ctx.prisma.user.findMany({
        where: { /* filters */ },
        take: input.limit + 1,
        cursor: input.cursor ? { id: input.cursor } : undefined,
      })

      let nextCursor: string | undefined
      if (items.length > input.limit) {
        const nextItem = items.pop()
        nextCursor = nextItem?.id
      }

      return { items, nextCursor }
    })
})
```

### Ziggie Adaptation: tRPC for Agent Communication

**Use Case**: Type-safe inter-agent messaging with validation

```typescript
// C:/Ziggie/control-center/backend/src/routers/agent-communication.ts

import { z } from 'zod'
import { createTRPCRouter, l1Procedure, l2Procedure, l3Procedure } from '../trpc'
import { TRPCError } from '@trpc/server'

// Agent task schemas
const agentTaskSchema = z.object({
  taskType: z.enum(['GENERATE_ASSET', 'VALIDATE_ASSET', 'APPROVE_ASSET', 'DELEGATE_TASK']),
  input: z.record(z.any()),
  priority: z.enum(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']).default('MEDIUM'),
  metadata: z.record(z.string()).optional()
})

const delegateTaskSchema = z.object({
  fromAgentId: z.string(),
  toAgentId: z.string(),
  taskType: z.string(),
  input: z.record(z.any()),
  deadline: z.date().optional()
})

export const agentCommunicationRouter = createTRPCRouter({
  /**
   * L2 Agent: Delegate task to L3 agent
   * Requires L2 or L1 tier (enforced by l2Procedure middleware)
   */
  delegateToL3: l2Procedure
    .input(delegateTaskSchema)
    .mutation(async ({ ctx, input }) => {
      // Validate target agent tier
      const targetAgent = await ctx.prisma.agent.findUnique({
        where: { id: input.toAgentId },
        select: { tier: true, status: true }
      })

      if (!targetAgent) {
        throw new TRPCError({ code: 'NOT_FOUND', message: 'Target agent not found' })
      }

      if (targetAgent.tier !== 'L3') {
        throw new TRPCError({
          code: 'BAD_REQUEST',
          message: 'Can only delegate to L3 agents from this endpoint'
        })
      }

      if (targetAgent.status !== 'ACTIVE') {
        throw new TRPCError({
          code: 'CONFLICT',
          message: `Target agent is ${targetAgent.status}, not ACTIVE`
        })
      }

      // Create task delegation
      const task = await ctx.prisma.agentTask.create({
        data: {
          fromAgentId: input.fromAgentId,
          toAgentId: input.toAgentId,
          taskType: input.taskType,
          input: input.input,
          status: 'PENDING',
          deadline: input.deadline,
          createdAt: new Date()
        }
      })

      // Audit log
      await ctx.prisma.agentAuditLog.create({
        data: {
          action: 'TASK_DELEGATED',
          agentId: input.fromAgentId,
          entityType: 'TASK',
          entityId: task.id,
          metadata: {
            toAgentId: input.toAgentId,
            taskType: input.taskType
          }
        }
      })

      return task
    }),

  /**
   * L3 Agent: Report task completion
   */
  reportTaskCompletion: l3Procedure
    .input(z.object({
      taskId: z.string(),
      status: z.enum(['COMPLETED', 'FAILED']),
      output: z.record(z.any()).optional(),
      error: z.string().optional()
    }))
    .mutation(async ({ ctx, input }) => {
      const task = await ctx.prisma.agentTask.findUnique({
        where: { id: input.taskId },
        include: { fromAgent: true, toAgent: true }
      })

      if (!task) {
        throw new TRPCError({ code: 'NOT_FOUND', message: 'Task not found' })
      }

      // Verify agent ownership
      if (task.toAgentId !== ctx.agent.id) {
        throw new TRPCError({
          code: 'FORBIDDEN',
          message: 'You are not assigned to this task'
        })
      }

      // Update task
      const updated = await ctx.prisma.agentTask.update({
        where: { id: input.taskId },
        data: {
          status: input.status,
          output: input.output,
          error: input.error,
          completedAt: new Date()
        }
      })

      // Audit log
      await ctx.prisma.agentAuditLog.create({
        data: {
          action: 'TASK_COMPLETED',
          agentId: ctx.agent.id,
          entityType: 'TASK',
          entityId: task.id,
          metadata: { status: input.status }
        }
      })

      // Notify parent agent (L2)
      await notifyAgentTaskComplete(task.fromAgentId, task.id, input.status)

      return updated
    }),

  /**
   * L1 Agent: Approve asset (after L2 generation)
   */
  approveAsset: l1Procedure
    .input(z.object({
      assetId: z.string(),
      approved: z.boolean(),
      feedback: z.string().optional()
    }))
    .mutation(async ({ ctx, input }) => {
      const asset = await ctx.prisma.asset.findUnique({
        where: { id: input.assetId },
        include: { creatorAgent: true }
      })

      if (!asset) {
        throw new TRPCError({ code: 'NOT_FOUND', message: 'Asset not found' })
      }

      // Update asset status
      const updated = await ctx.prisma.asset.update({
        where: { id: input.assetId },
        data: {
          status: input.approved ? 'APPROVED' : 'REJECTED',
          reviewerId: ctx.agent.id,
          reviewFeedback: input.feedback,
          reviewedAt: new Date()
        }
      })

      // Audit log
      await ctx.prisma.agentAuditLog.create({
        data: {
          action: input.approved ? 'ASSET_APPROVED' : 'ASSET_REJECTED',
          agentId: ctx.agent.id,
          entityType: 'ASSET',
          entityId: asset.id,
          metadata: {
            creatorAgentId: asset.creatorAgent.id,
            feedback: input.feedback
          }
        }
      })

      // Notify creator agent (L2)
      await notifyAgentAssetReview(asset.creatorAgent.id, asset.id, input.approved)

      return updated
    })
})
```

**tRPC Middleware for Agent Auth**:

```typescript
// C:/Ziggie/control-center/backend/src/trpc.ts

import { initTRPC, TRPCError } from '@trpc/server'
import { PrismaClient, AgentTier } from '@prisma/client'
import { decodeAgentToken } from './utils/agent-auth'

const prisma = new PrismaClient()

interface AgentContext {
  prisma: typeof prisma
  headers?: Headers
}

interface AuthenticatedAgentContext extends AgentContext {
  agent: {
    id: string
    name: string
    tier: AgentTier
    permissions: string[]
  }
}

const t = initTRPC.context<AgentContext>().create()

// Base agent authentication middleware
const agentAuthMiddleware = t.middleware(async ({ ctx, next }) => {
  const token = ctx.headers?.get('X-Agent-Token')

  if (!token) {
    throw new TRPCError({
      code: 'UNAUTHORIZED',
      message: 'Agent token required'
    })
  }

  // Decode JWT token
  const agentData = await decodeAgentToken(token)

  // Fetch full agent from database
  const agent = await ctx.prisma.agent.findUnique({
    where: { id: agentData.agentId },
    select: {
      id: true,
      name: true,
      tier: true,
      permissions: true,
      status: true
    }
  })

  if (!agent) {
    throw new TRPCError({
      code: 'UNAUTHORIZED',
      message: 'Agent not found'
    })
  }

  if (agent.status !== 'ACTIVE') {
    throw new TRPCError({
      code: 'FORBIDDEN',
      message: `Agent is ${agent.status}, not ACTIVE`
    })
  }

  return next({
    ctx: {
      ...ctx,
      agent
    } as AuthenticatedAgentContext
  })
})

// Tier-specific procedures (like adminProcedure, instructorProcedure in FitFlow)
const requireL1 = t.middleware(async ({ ctx, next }) => {
  const agentCtx = ctx as AuthenticatedAgentContext
  if (agentCtx.agent.tier !== 'L1') {
    throw new TRPCError({
      code: 'FORBIDDEN',
      message: 'L1 tier required'
    })
  }
  return next({ ctx })
})

const requireL2 = t.middleware(async ({ ctx, next }) => {
  const agentCtx = ctx as AuthenticatedAgentContext
  if (!['L1', 'L2'].includes(agentCtx.agent.tier)) {
    throw new TRPCError({
      code: 'FORBIDDEN',
      message: 'L2 or L1 tier required'
    })
  }
  return next({ ctx })
})

export const agentProcedure = t.procedure.use(agentAuthMiddleware)
export const l1Procedure = agentProcedure.use(requireL1)
export const l2Procedure = agentProcedure.use(requireL2)
export const l3Procedure = agentProcedure  // All authenticated agents
```

**Key Insights**:
- **Type Safety**: Zod validation ensures inter-agent messages are type-safe
- **Middleware Pattern**: Same RBAC enforcement as FitFlow (adminProcedure → l1Procedure)
- **Audit Trail**: Every agent communication logged
- **Error Handling**: Same TRPCError patterns for consistent error responses

---

## 6. Audit Logging: SOC 2/GDPR Compliant Agent Tracking

### FitFlow Pattern (Enterprise Audit Log)

```typescript
// File: packages/database/prisma/schema.prisma

model AuditLog {
  id          String   @id @default(cuid())
  action      String   // 'USER_SUSPENDED', 'ROLE_CHANGED', etc.
  entityType  String   // 'User', 'Class', etc.
  entityId    String
  userId      String   // Who performed the action
  adminId     String?  // Admin who performed action (if admin action)
  ipAddress   String?  // From x-forwarded-for
  metadata    Json?    // Additional context
  createdAt   DateTime @default(now())

  @@index([action])
  @@index([entityType, entityId])
  @@index([userId])
  @@index([createdAt])
}

// Usage in admin router
await ctx.prisma.auditLog.create({
  data: {
    action: 'USER_SUSPENDED',
    entityType: 'USER',
    entityId: userId,
    userId: ctx.user.id,
    ipAddress: ctx.headers?.get('x-forwarded-for') || null,
    metadata: { reason, duration },
  },
})
```

### Ziggie Adaptation: Agent Action Audit Log

**Use Case**: Track every agent action for debugging, compliance, and accountability

```prisma
// C:/Ziggie/control-center/backend/prisma/schema.prisma

enum AgentAction {
  // Task Management
  TASK_CREATED
  TASK_DELEGATED
  TASK_STARTED
  TASK_COMPLETED
  TASK_FAILED

  // Asset Management
  ASSET_GENERATED
  ASSET_APPROVED
  ASSET_REJECTED
  ASSET_DELETED

  // Agent Lifecycle
  AGENT_ACTIVATED
  AGENT_DEACTIVATED
  AGENT_PERMISSION_CHANGED
  AGENT_CONFIG_UPDATED

  // Workflow
  WORKFLOW_STARTED
  WORKFLOW_COMPLETED
  WORKFLOW_FAILED

  // System
  SYSTEM_ERROR
  RATE_LIMIT_EXCEEDED
}

model AgentAuditLog {
  id          String      @id @default(cuid())
  action      AgentAction
  agentId     String
  agent       Agent       @relation(fields: [agentId], references: [id])
  entityType  String      // "TASK", "ASSET", "WORKFLOW", etc.
  entityId    String
  metadata    Json?       // Task details, error messages, etc.
  ipAddress   String?     // For HTTP-based agent APIs
  duration    Int?        // Task execution time (ms)
  createdAt   DateTime    @default(now())

  // For audit trail queries
  @@index([action])
  @@index([agentId])
  @@index([entityType, entityId])
  @@index([createdAt])
}
```

**Audit Log Service** (Similar to FitFlow's audit logging):

```python
# C:/Ziggie/control-center/backend/services/audit_log.py

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
import httpx

class AgentAction(Enum):
    TASK_CREATED = "TASK_CREATED"
    TASK_DELEGATED = "TASK_DELEGATED"
    TASK_COMPLETED = "TASK_COMPLETED"
    ASSET_GENERATED = "ASSET_GENERATED"
    ASSET_APPROVED = "ASSET_APPROVED"
    # ... all actions

class AgentAuditLogger:
    """
    Enterprise-grade audit logging for agent actions
    Adapted from FitFlow's SOC 2/GDPR compliant logging
    """

    @staticmethod
    async def log_action(
        action: AgentAction,
        agent_id: str,
        entity_type: str,
        entity_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        duration: Optional[int] = None
    ) -> str:
        """
        Log agent action to database with full audit trail
        Returns: Audit log ID
        """
        audit_log = await prisma.agentauditlog.create(
            data={
                'action': action.value,
                'agentId': agent_id,
                'entityType': entity_type,
                'entityId': entity_id,
                'metadata': metadata or {},
                'ipAddress': ip_address,
                'duration': duration,
                'createdAt': datetime.utcnow()
            }
        )

        return audit_log.id

    @staticmethod
    async def log_task_delegation(
        from_agent_id: str,
        to_agent_id: str,
        task_id: str,
        task_type: str,
        ip_address: Optional[str] = None
    ):
        """Log task delegation from L2 to L3 agent"""
        await AgentAuditLogger.log_action(
            action=AgentAction.TASK_DELEGATED,
            agent_id=from_agent_id,
            entity_type='TASK',
            entity_id=task_id,
            metadata={
                'toAgentId': to_agent_id,
                'taskType': task_type,
                'timestamp': datetime.utcnow().isoformat()
            },
            ip_address=ip_address
        )

    @staticmethod
    async def log_asset_approval(
        agent_id: str,
        asset_id: str,
        approved: bool,
        feedback: Optional[str] = None,
        duration: Optional[int] = None
    ):
        """Log L1 asset approval/rejection"""
        await AgentAuditLogger.log_action(
            action=AgentAction.ASSET_APPROVED if approved else AgentAction.ASSET_REJECTED,
            agent_id=agent_id,
            entity_type='ASSET',
            entity_id=asset_id,
            metadata={
                'approved': approved,
                'feedback': feedback,
                'timestamp': datetime.utcnow().isoformat()
            },
            duration=duration
        )

    @staticmethod
    async def get_agent_history(
        agent_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        action: Optional[AgentAction] = None,
        limit: int = 100,
        cursor: Optional[str] = None
    ) -> Dict:
        """
        Query agent action history with filters
        Similar to FitFlow's getAuditLogs endpoint
        """
        where = {'agentId': agent_id}

        if start_date or end_date:
            where['createdAt'] = {}
            if start_date:
                where['createdAt']['gte'] = start_date
            if end_date:
                where['createdAt']['lte'] = end_date

        if action:
            where['action'] = action.value

        items = await prisma.agentauditlog.find_many(
            where=where,
            take=limit + 1,
            cursor={'id': cursor} if cursor else None,
            order_by={'createdAt': 'desc'}
        )

        next_cursor = None
        if len(items) > limit:
            next_cursor = items.pop().id

        return {
            'items': items,
            'nextCursor': next_cursor,
            'total': await prisma.agentauditlog.count(where=where)
        }

    @staticmethod
    async def export_audit_logs(
        start_date: datetime,
        end_date: datetime,
        format: str = 'csv'
    ) -> str:
        """
        Export audit logs for compliance (SOC 2 requirement)
        Similar to FitFlow's exportAuditLogs
        """
        logs = await prisma.agentauditlog.find_many(
            where={
                'createdAt': {
                    'gte': start_date,
                    'lte': end_date
                }
            },
            order_by={'createdAt': 'desc'}
        )

        if format == 'csv':
            # Generate CSV
            headers = ['id', 'action', 'agentId', 'entityType', 'entityId', 'createdAt', 'duration']
            rows = [[log.id, log.action, log.agentId, log.entityType, log.entityId, log.createdAt.isoformat(), log.duration or ''] for log in logs]

            csv_content = '\\n'.join([','.join(headers)] + [','.join(map(str, row)) for row in rows])
            return csv_content

        # JSON format
        return json.dumps([log.dict() for log in logs], indent=2)
```

**Usage in Agent Endpoints**:

```python
# C:/Ziggie/control-center/backend/routers/agents.py

from fastapi import APIRouter, Depends
from services.audit_log import AgentAuditLogger, AgentAction

router = APIRouter()

@router.post("/tasks/delegate")
async def delegate_task(
    task: DelegateTaskRequest,
    agent: dict = Depends(require_tier([AgentTier.L2, AgentTier.L1]))
):
    """L2 delegates task to L3"""
    # Create task
    task_record = await create_task_logic(task)

    # Audit log
    await AgentAuditLogger.log_task_delegation(
        from_agent_id=agent['agentId'],
        to_agent_id=task.toAgentId,
        task_id=task_record.id,
        task_type=task.taskType,
        ip_address=request.client.host
    )

    return task_record

@router.post("/assets/approve")
async def approve_asset(
    approval: AssetApprovalRequest,
    agent: dict = Depends(require_tier([AgentTier.L1]))
):
    """L1 approves asset"""
    start_time = time.time()

    # Approve asset
    asset = await approve_asset_logic(approval)

    # Audit log with duration
    await AgentAuditLogger.log_asset_approval(
        agent_id=agent['agentId'],
        asset_id=approval.assetId,
        approved=approval.approved,
        feedback=approval.feedback,
        duration=int((time.time() - start_time) * 1000)  # ms
    )

    return asset
```

**Key Insights**:
- **SOC 2 Compliance**: Same 7-year retention design as FitFlow
- **GDPR Compliance**: IP address tracking, metadata, exportable
- **Performance**: Indexed on action, agentId, entityType, createdAt (like FitFlow)
- **Export**: CSV/JSON export for compliance audits

---

## 7. State Machine: Agent Workflow Validation

### FitFlow Pattern (Content Workflow State Machine)

```typescript
// File: packages/api/src/services/class-state-machine.ts

const STATE_TRANSITIONS: Record<ClassStatus, ClassStatus[]> = {
  DRAFT: ['SUBMITTED'],
  SUBMITTED: ['UNDER_REVIEW'],
  UNDER_REVIEW: ['APPROVED', 'CHANGES_REQUESTED', 'REJECTED'],
  CHANGES_REQUESTED: ['SUBMITTED'], // Allow resubmission
  APPROVED: ['PUBLISHED'],
  REJECTED: [], // Terminal state
  PUBLISHED: [], // Terminal state
}

export function validateTransition(currentStatus: ClassStatus, newStatus: ClassStatus): void {
  const allowedTransitions = STATE_TRANSITIONS[currentStatus] || []

  if (!allowedTransitions.includes(newStatus)) {
    throw new TRPCError({
      code: 'BAD_REQUEST',
      message: `Invalid state transition: ${currentStatus} → ${newStatus}`
    })
  }
}
```

### Ziggie Adaptation: Agent Task State Machine

**Use Case**: Enforce valid agent task state transitions

```python
# C:/Ziggie/control-center/backend/services/agent_state_machine.py

from enum import Enum
from typing import Dict, List
from fastapi import HTTPException

class AgentTaskStatus(Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW_REQUESTED = "REVIEW_REQUESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

# Valid state transitions (similar to FitFlow's STATE_TRANSITIONS)
STATE_TRANSITIONS: Dict[AgentTaskStatus, List[AgentTaskStatus]] = {
    AgentTaskStatus.PENDING: [AgentTaskStatus.ASSIGNED, AgentTaskStatus.CANCELLED],
    AgentTaskStatus.ASSIGNED: [AgentTaskStatus.IN_PROGRESS, AgentTaskStatus.CANCELLED],
    AgentTaskStatus.IN_PROGRESS: [
        AgentTaskStatus.REVIEW_REQUESTED,
        AgentTaskStatus.COMPLETED,
        AgentTaskStatus.FAILED,
        AgentTaskStatus.CANCELLED
    ],
    AgentTaskStatus.REVIEW_REQUESTED: [
        AgentTaskStatus.APPROVED,
        AgentTaskStatus.REJECTED,
        AgentTaskStatus.CANCELLED
    ],
    AgentTaskStatus.APPROVED: [AgentTaskStatus.COMPLETED],
    AgentTaskStatus.REJECTED: [AgentTaskStatus.ASSIGNED],  # Reassign task
    AgentTaskStatus.COMPLETED: [],  # Terminal state
    AgentTaskStatus.FAILED: [AgentTaskStatus.ASSIGNED],  # Retry
    AgentTaskStatus.CANCELLED: []  # Terminal state
}

class AgentStateMachine:
    """
    State machine for agent task workflows
    Adapted from FitFlow's class-state-machine.ts
    """

    @staticmethod
    def validate_transition(current_status: AgentTaskStatus, new_status: AgentTaskStatus) -> None:
        """
        Validate state transition
        Raises HTTPException if invalid
        """
        allowed_transitions = STATE_TRANSITIONS.get(current_status, [])

        if new_status not in allowed_transitions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid state transition: {current_status.value} → {new_status.value}. "
                       f"Allowed: {[t.value for t in allowed_transitions]}"
            )

    @staticmethod
    async def assign_task(task_id: str, agent_id: str) -> dict:
        """
        Assign task to agent (PENDING → ASSIGNED)
        """
        task = await prisma.agenttask.find_unique(where={'id': task_id})

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        current_status = AgentTaskStatus(task.status)
        AgentStateMachine.validate_transition(current_status, AgentTaskStatus.ASSIGNED)

        updated = await prisma.agenttask.update(
            where={'id': task_id},
            data={
                'status': AgentTaskStatus.ASSIGNED.value,
                'assignedAgentId': agent_id,
                'assignedAt': datetime.utcnow()
            }
        )

        # Audit log
        await AgentAuditLogger.log_action(
            action=AgentAction.TASK_ASSIGNED,
            agent_id=agent_id,
            entity_type='TASK',
            entity_id=task_id,
            metadata={'previousStatus': current_status.value}
        )

        return updated

    @staticmethod
    async def start_task(task_id: str, agent_id: str) -> dict:
        """
        Start task execution (ASSIGNED → IN_PROGRESS)
        """
        task = await prisma.agenttask.find_unique(where={'id': task_id})

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if task.assignedAgentId != agent_id:
            raise HTTPException(status_code=403, detail="Task not assigned to you")

        current_status = AgentTaskStatus(task.status)
        AgentStateMachine.validate_transition(current_status, AgentTaskStatus.IN_PROGRESS)

        updated = await prisma.agenttask.update(
            where={'id': task_id},
            data={
                'status': AgentTaskStatus.IN_PROGRESS.value,
                'startedAt': datetime.utcnow()
            }
        )

        await AgentAuditLogger.log_action(
            action=AgentAction.TASK_STARTED,
            agent_id=agent_id,
            entity_type='TASK',
            entity_id=task_id,
            metadata={'previousStatus': current_status.value}
        )

        return updated

    @staticmethod
    async def request_review(task_id: str, agent_id: str, output: dict) -> dict:
        """
        Request L1 review (IN_PROGRESS → REVIEW_REQUESTED)
        Similar to FitFlow's submitForReview
        """
        task = await prisma.agenttask.find_unique(where={'id': task_id})

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        current_status = AgentTaskStatus(task.status)
        AgentStateMachine.validate_transition(current_status, AgentTaskStatus.REVIEW_REQUESTED)

        updated = await prisma.agenttask.update(
            where={'id': task_id},
            data={
                'status': AgentTaskStatus.REVIEW_REQUESTED.value,
                'output': output,
                'reviewRequestedAt': datetime.utcnow()
            }
        )

        await AgentAuditLogger.log_action(
            action=AgentAction.REVIEW_REQUESTED,
            agent_id=agent_id,
            entity_type='TASK',
            entity_id=task_id,
            metadata={'previousStatus': current_status.value, 'outputKeys': list(output.keys())}
        )

        # Notify L1 agent
        await notify_l1_review_needed(task_id)

        return updated

    @staticmethod
    async def approve_task(task_id: str, l1_agent_id: str, feedback: str = None) -> dict:
        """
        L1 approves task (REVIEW_REQUESTED → APPROVED)
        Similar to FitFlow's approveClass
        """
        task = await prisma.agenttask.find_unique(where={'id': task_id})

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        current_status = AgentTaskStatus(task.status)
        AgentStateMachine.validate_transition(current_status, AgentTaskStatus.APPROVED)

        updated = await prisma.agenttask.update(
            where={'id': task_id},
            data={
                'status': AgentTaskStatus.APPROVED.value,
                'reviewerId': l1_agent_id,
                'reviewFeedback': feedback,
                'reviewedAt': datetime.utcnow()
            }
        )

        await AgentAuditLogger.log_action(
            action=AgentAction.TASK_APPROVED,
            agent_id=l1_agent_id,
            entity_type='TASK',
            entity_id=task_id,
            metadata={'previousStatus': current_status.value, 'feedback': feedback}
        )

        # Notify L2 agent
        await notify_agent_task_approved(task.assignedAgentId, task_id)

        return updated

    @staticmethod
    async def reject_task(
        task_id: str,
        l1_agent_id: str,
        feedback: str,
        reassign: bool = True
    ) -> dict:
        """
        L1 rejects task (REVIEW_REQUESTED → REJECTED → ASSIGNED)
        Similar to FitFlow's requestChanges
        """
        task = await prisma.agenttask.find_unique(where={'id': task_id})

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        current_status = AgentTaskStatus(task.status)
        AgentStateMachine.validate_transition(current_status, AgentTaskStatus.REJECTED)

        new_status = AgentTaskStatus.ASSIGNED if reassign else AgentTaskStatus.REJECTED

        updated = await prisma.agenttask.update(
            where={'id': task_id},
            data={
                'status': new_status.value,
                'reviewerId': l1_agent_id,
                'reviewFeedback': feedback,
                'reviewedAt': datetime.utcnow(),
                'rejectionCount': task.rejectionCount + 1
            }
        )

        await AgentAuditLogger.log_action(
            action=AgentAction.TASK_REJECTED,
            agent_id=l1_agent_id,
            entity_type='TASK',
            entity_id=task_id,
            metadata={
                'previousStatus': current_status.value,
                'feedback': feedback,
                'reassigned': reassign
            }
        )

        # Notify L2 agent
        await notify_agent_task_rejected(task.assignedAgentId, task_id, feedback)

        return updated
```

**Workflow Visualization**:

```
Agent Task State Machine (similar to FitFlow's class workflow)

PENDING ──────────────────────────────────────────┐
   │                                              │
   │ assign_task()                                │
   ▼                                              │
ASSIGNED                                          │
   │                                              │
   │ start_task()                                 │
   ▼                                              │
IN_PROGRESS                                       │ cancel_task()
   │                                              │
   │ request_review()                             │
   ▼                                              │
REVIEW_REQUESTED ─────────────────────────────────┤
   │        │                                     │
   │        │ reject_task(reassign=True)          │
   │        └───────────┐                         │
   │                    ▼                         │
   │                 REJECTED                     │
   │                    │                         │
   │                    │ reassign                │
   │                    └───────► ASSIGNED        │
   │                                              │
   │ approve_task()                               │
   ▼                                              │
APPROVED                                          │
   │                                              │
   │ complete_task()                              │
   ▼                                              ▼
COMPLETED                                    CANCELLED
(terminal)                                   (terminal)
```

**Key Insights**:
- **Same Pattern**: STATE_TRANSITIONS dict with validation
- **Workflow Enforcement**: Invalid transitions throw errors
- **Audit Trail**: Every state change logged
- **Business Rules**: Rejection → Reassignment workflow (like FitFlow's CHANGES_REQUESTED → SUBMITTED)

---

## 8. Database Schema Patterns

### FitFlow Pattern (User + Session + Audit)

```prisma
model User {
  id            String    @id @default(cuid())
  email         String    @unique
  role          Role      @default(END_USER)
  emailVerified DateTime?

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

model AuditLog {
  id          String   @id @default(cuid())
  action      String
  entityType  String
  entityId    String
  userId      String
  metadata    Json?
  createdAt   DateTime @default(now())

  @@index([action])
  @@index([userId])
}
```

### Ziggie Adaptation (Agent + Session + Audit)

```prisma
// C:/Ziggie/control-center/backend/prisma/schema.prisma

model Agent {
  id          String      @id @default(cuid())
  name        String
  tier        AgentTier
  permissions AgentPermission[]
  status      AgentStatus @default(ACTIVE)
  config      Json?       // Agent-specific configuration
  createdAt   DateTime    @default(now())
  lastActiveAt DateTime?

  // Relationships (same pattern as User model)
  sessions    AgentSession[]
  auditLogs   AgentAuditLog[]
  tasksAssigned AgentTask[] @relation("AssignedTasks")
  tasksCreated  AgentTask[] @relation("CreatedTasks")

  @@index([tier])
  @@index([status])
}

model AgentSession {
  id           String   @id @default(cuid())
  sessionToken String   @unique
  agentId      String
  agent        Agent    @relation(fields: [agentId], references: [id], onDelete: Cascade)
  expiresAt    DateTime
  createdAt    DateTime @default(now())

  @@index([agentId])
  @@index([expiresAt])
}

model AgentTask {
  id                String          @id @default(cuid())
  taskType          String
  status            AgentTaskStatus @default(PENDING)
  priority          TaskPriority    @default(MEDIUM)

  // Agent relationships
  creatorAgentId    String
  creatorAgent      Agent           @relation("CreatedTasks", fields: [creatorAgentId], references: [id])
  assignedAgentId   String?
  assignedAgent     Agent?          @relation("AssignedTasks", fields: [assignedAgentId], references: [id])
  reviewerId        String?

  // Task data
  input             Json
  output            Json?
  error             String?
  reviewFeedback    String?

  // Timestamps
  createdAt         DateTime        @default(now())
  assignedAt        DateTime?
  startedAt         DateTime?
  completedAt       DateTime?
  reviewedAt        DateTime?
  deadline          DateTime?

  // Metrics
  duration          Int?            // Execution time in ms
  rejectionCount    Int             @default(0)

  @@index([status])
  @@index([assignedAgentId])
  @@index([createdAt])
}

model AgentAuditLog {
  id          String      @id @default(cuid())
  action      AgentAction
  agentId     String
  agent       Agent       @relation(fields: [agentId], references: [id])
  entityType  String
  entityId    String
  metadata    Json?
  ipAddress   String?
  duration    Int?
  createdAt   DateTime    @default(now())

  @@index([action])
  @@index([agentId])
  @@index([entityType, entityId])
  @@index([createdAt])
}
```

**Key Insights**:
- **Same Relationships**: Agent → Session (1:many), Agent → AuditLog (1:many)
- **Same Indexes**: Optimized for common queries (status, tier, createdAt)
- **Task Tracking**: Similar to FitFlow's Class → ContentWorkflow relationship

---

## Conclusion: Integration Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Implement Agent RBAC (tier-based permissions)
- [ ] Set up Agent Session management (JWT tokens)
- [ ] Create Agent Audit Log database schema
- [ ] Write basic audit logging service

### Phase 2: Testing Infrastructure (Week 3-4)
- [ ] Adapt FitFlow's test-helpers for agent testing
- [ ] Create agent execution test fixtures
- [ ] Write first 10 agent E2E tests
- [ ] Set up quality gates framework

### Phase 3: State Machine (Week 5-6)
- [ ] Implement AgentStateMachine class
- [ ] Define all valid state transitions
- [ ] Add state validation to task endpoints
- [ ] Write state transition tests

### Phase 4: tRPC Integration (Week 7-8)
- [ ] Set up tRPC server for agent communication
- [ ] Implement tier-based procedures (l1Procedure, l2Procedure, l3Procedure)
- [ ] Create agent communication routers
- [ ] Write inter-agent communication tests

### Phase 5: Sprint Methodology (Week 9-10)
- [ ] Document 7-phase agent development process
- [ ] Create agent sprint templates
- [ ] Train team on wave-based execution
- [ ] Run first agent development sprint

### Success Metrics
- **Testing**: 100+ E2E tests for agent validation
- **Audit**: 100% agent action coverage in audit logs
- **Quality**: 5/5 quality gates passing
- **Methodology**: 10/10 sprint execution standard
- **Type Safety**: 0 TypeScript/Python type errors

---

**End of Brainstorm Document**

This integration strategy leverages FitFlow's 584-story-point, 986-test, 14-sprint track record to bring enterprise-grade patterns to Ziggie's 1,884-agent architecture. Every pattern has been battle-tested in production and adapted for agent orchestration.
