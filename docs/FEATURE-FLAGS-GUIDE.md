# Feature Flags Guide for Ziggie

> **Purpose**: Implementation guide for feature flags in the Ziggie ecosystem
> **Languages**: Python (FastAPI), TypeScript (Node.js/React)
> **Last Updated**: 2025-12-28

---

## Table of Contents

1. [Feature Flag Strategies](#1-feature-flag-strategies)
2. [Environment Variable Approach](#2-environment-variable-approach)
3. [Database-Backed Flags](#3-database-backed-flags)
4. [Third-Party Solutions](#4-third-party-solutions)
5. [Python Implementation](#5-python-implementation)
6. [TypeScript Implementation](#6-typescript-implementation)
7. [Best Practices](#7-best-practices)
8. [Testing Feature Flags](#8-testing-feature-flags)

---

## 1. Feature Flag Strategies

### When to Use Feature Flags

| Scenario | Flag Type | Duration |
|----------|-----------|----------|
| Gradual rollout | Release flag | Days-weeks |
| A/B testing | Experiment flag | Weeks |
| Kill switch | Ops flag | Permanent |
| Premium features | Permission flag | Permanent |
| Beta features | Permission flag | Months |

### Flag Types

```
Release Flags     -> Feature is ready, controlling rollout
Experiment Flags  -> Testing variations for optimization
Ops Flags         -> Circuit breakers, kill switches
Permission Flags  -> User/tenant-based access control
```

### Decision Matrix: Build vs Buy

| Factor | DIY (Env/DB) | LaunchDarkly | Unleash | GrowthBook |
|--------|--------------|--------------|---------|------------|
| Cost | $0 | $$$ | $ | $$ |
| Setup Time | Hours | Minutes | Hours | Hours |
| Scale | Limited | Enterprise | Medium | Medium |
| Analytics | Manual | Built-in | Basic | Built-in |
| Self-hosted | Yes | No | Yes | Yes |

**Ziggie Recommendation**: Start with environment variables, migrate to Unleash when complexity grows.

---

## 2. Environment Variable Approach

### Basic Configuration

```bash
# .env file
FEATURE_AI_INSTRUCTOR=true
FEATURE_SOCIAL_FEED=false
FEATURE_MULTI_REGION=false
FEATURE_ADVANCED_ANALYTICS=true
FEATURE_COMFYUI_INTEGRATION=true
```

### Python Implementation

```python
# config/features.py
import os
from functools import lru_cache

class FeatureFlags:
    """Simple environment-based feature flags."""

    @staticmethod
    def _get_bool(key: str, default: bool = False) -> bool:
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')

    @property
    def ai_instructor(self) -> bool:
        return self._get_bool('FEATURE_AI_INSTRUCTOR')

    @property
    def social_feed(self) -> bool:
        return self._get_bool('FEATURE_SOCIAL_FEED')

    @property
    def multi_region(self) -> bool:
        return self._get_bool('FEATURE_MULTI_REGION')

    @property
    def advanced_analytics(self) -> bool:
        return self._get_bool('FEATURE_ADVANCED_ANALYTICS')

    @property
    def comfyui_integration(self) -> bool:
        return self._get_bool('FEATURE_COMFYUI_INTEGRATION')

@lru_cache()
def get_features() -> FeatureFlags:
    return FeatureFlags()

# Usage
features = get_features()
if features.ai_instructor:
    # Enable AI instructor functionality
    pass
```

### TypeScript Implementation

```typescript
// config/features.ts

interface FeatureFlags {
  aiInstructor: boolean;
  socialFeed: boolean;
  multiRegion: boolean;
  advancedAnalytics: boolean;
  comfyuiIntegration: boolean;
}

function getEnvBool(key: string, defaultValue: boolean = false): boolean {
  const value = process.env[key]?.toLowerCase();
  if (!value) return defaultValue;
  return ['true', '1', 'yes', 'on'].includes(value);
}

export const features: FeatureFlags = {
  aiInstructor: getEnvBool('FEATURE_AI_INSTRUCTOR'),
  socialFeed: getEnvBool('FEATURE_SOCIAL_FEED'),
  multiRegion: getEnvBool('FEATURE_MULTI_REGION'),
  advancedAnalytics: getEnvBool('FEATURE_ADVANCED_ANALYTICS'),
  comfyuiIntegration: getEnvBool('FEATURE_COMFYUI_INTEGRATION'),
};

// Usage
if (features.aiInstructor) {
  // Enable AI instructor functionality
}
```

---

## 3. Database-Backed Flags

### Schema Design

```sql
-- PostgreSQL schema
CREATE TABLE feature_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    enabled BOOLEAN DEFAULT false,
    percentage INTEGER DEFAULT 100,  -- For gradual rollout
    user_ids TEXT[],  -- Specific user access
    tenant_ids TEXT[],  -- Tenant-based access
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for fast lookups
CREATE INDEX idx_feature_flags_name ON feature_flags(name);
CREATE INDEX idx_feature_flags_enabled ON feature_flags(enabled);
```

### Python Database Implementation

```python
# models/feature_flag.py
from sqlalchemy import Column, String, Boolean, Integer, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database import Base

class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String)
    enabled = Column(Boolean, default=False)
    percentage = Column(Integer, default=100)
    user_ids = Column(ARRAY(String), default=[])
    tenant_ids = Column(ARRAY(String), default=[])
    metadata = Column(JSON, default={})
```

```python
# services/feature_service.py
from functools import lru_cache
from typing import Optional
import hashlib
from sqlalchemy.orm import Session
from models.feature_flag import FeatureFlag

class FeatureFlagService:
    def __init__(self, db: Session):
        self.db = db
        self._cache = {}

    def is_enabled(
        self,
        flag_name: str,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> bool:
        """Check if a feature flag is enabled for the given context."""

        flag = self.db.query(FeatureFlag).filter(
            FeatureFlag.name == flag_name
        ).first()

        if not flag or not flag.enabled:
            return False

        # Check user-specific access
        if flag.user_ids and user_id:
            if user_id in flag.user_ids:
                return True

        # Check tenant-specific access
        if flag.tenant_ids and tenant_id:
            if tenant_id in flag.tenant_ids:
                return True

        # Percentage rollout
        if flag.percentage < 100 and user_id:
            hash_value = int(hashlib.md5(
                f"{flag_name}:{user_id}".encode()
            ).hexdigest(), 16)
            if (hash_value % 100) >= flag.percentage:
                return False

        return True

    def get_all_flags(self) -> dict:
        """Get all feature flags as a dictionary."""
        flags = self.db.query(FeatureFlag).all()
        return {f.name: f.enabled for f in flags}
```

### FastAPI Integration

```python
# api/features.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.feature_service import FeatureFlagService
from database import get_db

router = APIRouter(prefix="/features", tags=["features"])

def get_feature_service(db: Session = Depends(get_db)) -> FeatureFlagService:
    return FeatureFlagService(db)

@router.get("/{flag_name}")
async def check_feature(
    flag_name: str,
    user_id: str = None,
    service: FeatureFlagService = Depends(get_feature_service)
):
    return {"enabled": service.is_enabled(flag_name, user_id)}

@router.get("/")
async def list_features(
    service: FeatureFlagService = Depends(get_feature_service)
):
    return service.get_all_flags()
```

---

## 4. Third-Party Solutions

### Unleash (Self-Hosted)

```yaml
# docker-compose addition for Unleash
services:
  unleash:
    image: unleashorg/unleash-server:latest
    container_name: ziggie-unleash
    ports:
      - "4242:4242"
    environment:
      - DATABASE_URL=postgres://ziggie:${POSTGRES_PASSWORD}@postgres:5432/unleash
      - DATABASE_SSL=false
    depends_on:
      - postgres
    networks:
      - ziggie-network
```

### Python Unleash Client

```python
# pip install UnleashClient

from UnleashClient import UnleashClient

client = UnleashClient(
    url="http://localhost:4242/api",
    app_name="ziggie-api",
    custom_headers={"Authorization": API_KEY}
)

client.initialize_client()

# Check feature
if client.is_enabled("ai-instructor"):
    # Feature is enabled
    pass

# With context
context = {
    "userId": user.id,
    "tenantId": user.tenant_id,
    "environment": "production"
}

if client.is_enabled("social-feed", context):
    pass
```

### TypeScript Unleash Client

```typescript
// npm install unleash-client

import { initialize, isEnabled } from 'unleash-client';

const unleash = initialize({
  url: 'http://localhost:4242/api',
  appName: 'ziggie-frontend',
  customHeaders: { Authorization: process.env.UNLEASH_API_KEY }
});

unleash.on('ready', () => {
  if (isEnabled('ai-instructor')) {
    // Feature is enabled
  }
});

// With context
const context = {
  userId: user.id,
  tenantId: user.tenantId,
  environment: 'production'
};

if (isEnabled('social-feed', context)) {
  // Feature is enabled for this user
}
```

### GrowthBook (Analytics-Focused)

```typescript
// npm install @growthbook/growthbook

import { GrowthBook } from '@growthbook/growthbook';

const gb = new GrowthBook({
  apiHost: 'https://cdn.growthbook.io',
  clientKey: process.env.GROWTHBOOK_CLIENT_KEY,
  enableDevMode: process.env.NODE_ENV !== 'production',
  trackingCallback: (experiment, result) => {
    // Track experiment exposure
    analytics.track('experiment_viewed', {
      experimentId: experiment.key,
      variationId: result.variationId
    });
  }
});

// Load features from GrowthBook
await gb.loadFeatures();

// Check feature
if (gb.isOn('ai-instructor')) {
  // Feature is enabled
}

// Get feature value (for multivariate)
const variant = gb.getFeatureValue('button-color', 'blue');
```

---

## 5. Python Implementation

### Complete Feature Flag Module

```python
# features/__init__.py
from enum import Enum
from typing import Optional, Dict, Any, Callable
from functools import wraps
import os
import hashlib
import logging

logger = logging.getLogger(__name__)

class FlagType(Enum):
    RELEASE = "release"
    EXPERIMENT = "experiment"
    OPS = "ops"
    PERMISSION = "permission"

class FeatureFlag:
    def __init__(
        self,
        name: str,
        flag_type: FlagType = FlagType.RELEASE,
        default: bool = False,
        description: str = ""
    ):
        self.name = name
        self.flag_type = flag_type
        self.default = default
        self.description = description

    def is_enabled(
        self,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        # Check environment variable first
        env_value = os.getenv(f"FEATURE_{self.name.upper()}")
        if env_value is not None:
            return env_value.lower() in ('true', '1', 'yes')

        return self.default

class FeatureManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._flags = {}
        return cls._instance

    def register(self, flag: FeatureFlag) -> FeatureFlag:
        self._flags[flag.name] = flag
        return flag

    def is_enabled(
        self,
        flag_name: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        flag = self._flags.get(flag_name)
        if not flag:
            logger.warning(f"Unknown feature flag: {flag_name}")
            return False
        return flag.is_enabled(user_id, context)

    def all_flags(self) -> Dict[str, bool]:
        return {name: flag.is_enabled() for name, flag in self._flags.items()}

# Singleton instance
feature_manager = FeatureManager()

# Register flags
AI_INSTRUCTOR = feature_manager.register(FeatureFlag(
    name="ai_instructor",
    flag_type=FlagType.RELEASE,
    default=True,
    description="AI-powered workout instructor"
))

SOCIAL_FEED = feature_manager.register(FeatureFlag(
    name="social_feed",
    flag_type=FlagType.RELEASE,
    default=False,
    description="Social activity feed"
))

COMFYUI_INTEGRATION = feature_manager.register(FeatureFlag(
    name="comfyui_integration",
    flag_type=FlagType.RELEASE,
    default=True,
    description="ComfyUI asset generation"
))

# Decorator for feature-gated functions
def feature_required(flag_name: str):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not feature_manager.is_enabled(flag_name):
                raise HTTPException(
                    status_code=404,
                    detail="Feature not available"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@feature_required("ai_instructor")
async def generate_workout_script():
    pass
```

---

## 6. TypeScript Implementation

### Complete Feature Flag Module

```typescript
// features/index.ts

export enum FlagType {
  RELEASE = 'release',
  EXPERIMENT = 'experiment',
  OPS = 'ops',
  PERMISSION = 'permission',
}

interface FeatureFlagConfig {
  name: string;
  type: FlagType;
  default: boolean;
  description: string;
}

interface FeatureContext {
  userId?: string;
  tenantId?: string;
  environment?: string;
  [key: string]: any;
}

class FeatureFlag {
  constructor(private config: FeatureFlagConfig) {}

  get name(): string {
    return this.config.name;
  }

  isEnabled(context?: FeatureContext): boolean {
    // Check environment variable
    const envKey = `FEATURE_${this.config.name.toUpperCase()}`;
    const envValue = process.env[envKey];

    if (envValue !== undefined) {
      return ['true', '1', 'yes'].includes(envValue.toLowerCase());
    }

    return this.config.default;
  }
}

class FeatureManager {
  private static instance: FeatureManager;
  private flags: Map<string, FeatureFlag> = new Map();

  private constructor() {}

  static getInstance(): FeatureManager {
    if (!FeatureManager.instance) {
      FeatureManager.instance = new FeatureManager();
    }
    return FeatureManager.instance;
  }

  register(config: FeatureFlagConfig): FeatureFlag {
    const flag = new FeatureFlag(config);
    this.flags.set(config.name, flag);
    return flag;
  }

  isEnabled(flagName: string, context?: FeatureContext): boolean {
    const flag = this.flags.get(flagName);
    if (!flag) {
      console.warn(`Unknown feature flag: ${flagName}`);
      return false;
    }
    return flag.isEnabled(context);
  }

  getAllFlags(): Record<string, boolean> {
    const result: Record<string, boolean> = {};
    this.flags.forEach((flag, name) => {
      result[name] = flag.isEnabled();
    });
    return result;
  }
}

// Singleton instance
export const featureManager = FeatureManager.getInstance();

// Register flags
export const AI_INSTRUCTOR = featureManager.register({
  name: 'ai_instructor',
  type: FlagType.RELEASE,
  default: true,
  description: 'AI-powered workout instructor',
});

export const SOCIAL_FEED = featureManager.register({
  name: 'social_feed',
  type: FlagType.RELEASE,
  default: false,
  description: 'Social activity feed',
});

export const COMFYUI_INTEGRATION = featureManager.register({
  name: 'comfyui_integration',
  type: FlagType.RELEASE,
  default: true,
  description: 'ComfyUI asset generation',
});

// React Hook
export function useFeatureFlag(flagName: string): boolean {
  return featureManager.isEnabled(flagName);
}

// React Component wrapper
export function FeatureGate({
  flag,
  children,
  fallback = null
}: {
  flag: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}): React.ReactElement | null {
  const isEnabled = useFeatureFlag(flag);
  return isEnabled ? <>{children}</> : <>{fallback}</>;
}

// Usage in React
// <FeatureGate flag="social_feed">
//   <SocialFeedComponent />
// </FeatureGate>
```

---

## 7. Best Practices

### Naming Conventions

```
DO:
- feature_ai_instructor (snake_case)
- feature-ai-instructor (kebab-case)
- FEATURE_AI_INSTRUCTOR (env vars)

DON'T:
- new_feature_2
- temp_fix
- johns_feature
```

### Flag Lifecycle

```
1. CREATE: Add flag with default=false
2. DEVELOP: Implement feature behind flag
3. TEST: Enable in staging, test thoroughly
4. ROLLOUT: Gradual percentage increase (10% -> 25% -> 50% -> 100%)
5. CLEANUP: Remove flag code after 100% rollout
```

### Documentation Template

```markdown
## Feature Flag: ai_instructor

- **Status**: Active
- **Type**: Release
- **Owner**: @craig
- **Created**: 2025-01-15
- **Target Removal**: 2025-03-01

### Description
Enables AI-powered workout instructor that generates personalized scripts.

### Rollout Plan
- 2025-01-15: Internal testing (5%)
- 2025-01-22: Beta users (25%)
- 2025-02-01: All users (100%)
- 2025-03-01: Flag removal

### Metrics to Monitor
- Script generation latency
- User engagement rate
- Error rate
```

### Technical Debt Prevention

```python
# Add expiration tracking
class FeatureFlag:
    def __init__(
        self,
        name: str,
        expiration_date: Optional[datetime] = None,
        ...
    ):
        self.expiration_date = expiration_date

    def check_expiration(self):
        if self.expiration_date and datetime.now() > self.expiration_date:
            logger.warning(
                f"Feature flag '{self.name}' has expired! "
                f"Please remove it from the codebase."
            )
```

---

## 8. Testing Feature Flags

### Unit Testing

```python
# Python
import pytest
from unittest.mock import patch

def test_feature_enabled():
    with patch.dict(os.environ, {'FEATURE_AI_INSTRUCTOR': 'true'}):
        assert feature_manager.is_enabled('ai_instructor') is True

def test_feature_disabled():
    with patch.dict(os.environ, {'FEATURE_AI_INSTRUCTOR': 'false'}):
        assert feature_manager.is_enabled('ai_instructor') is False
```

```typescript
// TypeScript
describe('Feature Flags', () => {
  beforeEach(() => {
    process.env.FEATURE_AI_INSTRUCTOR = 'true';
  });

  afterEach(() => {
    delete process.env.FEATURE_AI_INSTRUCTOR;
  });

  it('should return true when flag is enabled', () => {
    expect(featureManager.isEnabled('ai_instructor')).toBe(true);
  });
});
```

### Integration Testing

```python
# Test both paths
@pytest.mark.parametrize("flag_value,expected", [
    ("true", 200),
    ("false", 404),
])
def test_feature_gated_endpoint(client, flag_value, expected):
    with patch.dict(os.environ, {'FEATURE_AI_INSTRUCTOR': flag_value}):
        response = client.get("/api/ai-instructor/scripts")
        assert response.status_code == expected
```

### E2E Testing

```typescript
// Playwright test
test('AI instructor feature when enabled', async ({ page }) => {
  // Set feature flag via API or environment
  await page.goto('/settings');

  // Feature should be visible
  await expect(page.locator('[data-testid="ai-instructor-section"]')).toBeVisible();
});

test('AI instructor feature when disabled', async ({ page }) => {
  // Disable feature
  process.env.FEATURE_AI_INSTRUCTOR = 'false';

  await page.goto('/settings');

  // Feature should not be visible
  await expect(page.locator('[data-testid="ai-instructor-section"]')).not.toBeVisible();
});
```

---

## Quick Reference

### Environment Variables

```bash
# Enable features
export FEATURE_AI_INSTRUCTOR=true
export FEATURE_SOCIAL_FEED=true
export FEATURE_COMFYUI_INTEGRATION=true

# Disable features
export FEATURE_MULTI_REGION=false
export FEATURE_ADVANCED_ANALYTICS=false
```

### Common Patterns

```python
# Simple check
if feature_manager.is_enabled('ai_instructor'):
    do_something()

# With fallback
result = ai_generate() if feature_manager.is_enabled('ai_instructor') else manual_generate()

# Decorator
@feature_required('social_feed')
async def get_activity_feed():
    pass
```

```typescript
// React conditional rendering
{features.aiInstructor && <AIInstructor />}

// Component wrapper
<FeatureGate flag="social_feed" fallback={<ComingSoon />}>
  <SocialFeed />
</FeatureGate>
```

---

*Feature Flags Guide for Ziggie AI Ecosystem*
*Part of LOW priority gap completion (#43)*
