# A/B Testing Guide for Ziggie

> **Purpose**: Implementation guide for A/B testing and experimentation in the Ziggie ecosystem
> **Languages**: Python (FastAPI), TypeScript (Node.js/React)
> **Last Updated**: 2025-12-28

---

## Table of Contents

1. [A/B Testing Fundamentals](#1-ab-testing-fundamentals)
2. [Platform Comparison](#2-platform-comparison)
3. [Custom Implementation](#3-custom-implementation)
4. [GrowthBook Integration](#4-growthbook-integration)
5. [Optimizely Integration](#5-optimizely-integration)
6. [Statistical Analysis](#6-statistical-analysis)
7. [Best Practices](#7-best-practices)
8. [Monitoring and Reporting](#8-monitoring-and-reporting)

---

## 1. A/B Testing Fundamentals

### Key Concepts

```
Variant A (Control): The current/default experience
Variant B (Treatment): The new experience being tested
Traffic Split: Percentage of users in each variant (e.g., 50/50)
Conversion: The desired action (click, purchase, signup)
Statistical Significance: Confidence that results aren't random (usually 95%)
```

### Test Types

| Type | Description | Use Case |
|------|-------------|----------|
| A/B Test | 2 variants | Simple changes |
| A/B/n Test | 3+ variants | Multiple options |
| Multivariate | Multiple elements | Complex pages |
| Feature Flag | On/off | Gradual rollouts |

### Sample Size Calculation

```python
import math

def calculate_sample_size(
    baseline_rate: float,      # Current conversion rate (e.g., 0.05 for 5%)
    minimum_effect: float,     # Minimum detectable effect (e.g., 0.20 for 20% lift)
    significance: float = 0.95,  # Statistical significance
    power: float = 0.80         # Statistical power
) -> int:
    """Calculate required sample size per variant."""

    z_alpha = 1.96 if significance == 0.95 else 2.58  # 95% or 99%
    z_beta = 0.84 if power == 0.80 else 1.28  # 80% or 90%

    p1 = baseline_rate
    p2 = baseline_rate * (1 + minimum_effect)

    pooled_p = (p1 + p2) / 2

    numerator = (z_alpha * math.sqrt(2 * pooled_p * (1 - pooled_p)) +
                 z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    denominator = (p2 - p1) ** 2

    return int(math.ceil(numerator / denominator))

# Example: 5% baseline, 20% minimum lift
# ~3,900 users per variant needed
sample_size = calculate_sample_size(0.05, 0.20)
```

---

## 2. Platform Comparison

### Decision Matrix

| Platform | Type | Cost | Self-Hosted | Best For |
|----------|------|------|-------------|----------|
| Custom | DIY | $0 | Yes | Simple tests |
| GrowthBook | Open Source | Free-$$ | Yes | Feature flags + experiments |
| Optimizely | Enterprise | $$$$ | No | Large scale |
| LaunchDarkly | SaaS | $$$ | No | Feature management |
| Split.io | SaaS | $$ | No | Developer-first |
| PostHog | Open Source | Free-$$ | Yes | Product analytics |

### Ziggie Recommendation

```
Development Phase: Custom implementation
Growth Phase: GrowthBook (self-hosted)
Scale Phase: Optimizely or LaunchDarkly
```

---

## 3. Custom Implementation

### Database Schema

```sql
-- Experiments table
CREATE TABLE experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'draft',  -- draft, running, paused, completed
    traffic_percentage INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    ended_at TIMESTAMP
);

-- Variants table
CREATE TABLE experiment_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID REFERENCES experiments(id),
    name VARCHAR(50) NOT NULL,
    weight INTEGER DEFAULT 50,  -- Traffic weight
    is_control BOOLEAN DEFAULT false,
    config JSONB DEFAULT '{}'
);

-- Assignments table (which user got which variant)
CREATE TABLE experiment_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID REFERENCES experiments(id),
    variant_id UUID REFERENCES experiment_variants(id),
    user_id VARCHAR(100) NOT NULL,
    assigned_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(experiment_id, user_id)
);

-- Events table (conversions and metrics)
CREATE TABLE experiment_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID REFERENCES experiments(id),
    variant_id UUID REFERENCES experiment_variants(id),
    user_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_value NUMERIC,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_assignments_experiment_user ON experiment_assignments(experiment_id, user_id);
CREATE INDEX idx_events_experiment_variant ON experiment_events(experiment_id, variant_id);
CREATE INDEX idx_events_created_at ON experiment_events(created_at);
```

### Python Service

```python
# services/experiment_service.py
import hashlib
import random
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from models.experiment import Experiment, Variant, Assignment, Event

class ExperimentService:
    def __init__(self, db: Session):
        self.db = db

    def get_variant(
        self,
        experiment_name: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get or assign a variant for a user in an experiment."""

        experiment = self.db.query(Experiment).filter(
            Experiment.name == experiment_name,
            Experiment.status == 'running'
        ).first()

        if not experiment:
            return None

        # Check existing assignment
        assignment = self.db.query(Assignment).filter(
            Assignment.experiment_id == experiment.id,
            Assignment.user_id == user_id
        ).first()

        if assignment:
            variant = self.db.query(Variant).get(assignment.variant_id)
            return {"variant": variant.name, "config": variant.config}

        # Check traffic allocation
        if experiment.traffic_percentage < 100:
            hash_val = int(hashlib.md5(
                f"{experiment_name}:{user_id}".encode()
            ).hexdigest(), 16)
            if (hash_val % 100) >= experiment.traffic_percentage:
                return None  # Not in experiment

        # Assign variant based on weights
        variants = self.db.query(Variant).filter(
            Variant.experiment_id == experiment.id
        ).all()

        total_weight = sum(v.weight for v in variants)
        random_val = random.randint(1, total_weight)

        cumulative = 0
        selected_variant = None
        for variant in variants:
            cumulative += variant.weight
            if random_val <= cumulative:
                selected_variant = variant
                break

        # Save assignment
        assignment = Assignment(
            experiment_id=experiment.id,
            variant_id=selected_variant.id,
            user_id=user_id
        )
        self.db.add(assignment)
        self.db.commit()

        return {
            "variant": selected_variant.name,
            "config": selected_variant.config
        }

    def track_event(
        self,
        experiment_name: str,
        user_id: str,
        event_type: str,
        event_value: float = None,
        metadata: Dict = None
    ):
        """Track a conversion event."""

        experiment = self.db.query(Experiment).filter(
            Experiment.name == experiment_name
        ).first()

        if not experiment:
            return

        assignment = self.db.query(Assignment).filter(
            Assignment.experiment_id == experiment.id,
            Assignment.user_id == user_id
        ).first()

        if not assignment:
            return

        event = Event(
            experiment_id=experiment.id,
            variant_id=assignment.variant_id,
            user_id=user_id,
            event_type=event_type,
            event_value=event_value,
            metadata=metadata or {}
        )
        self.db.add(event)
        self.db.commit()

    def get_results(self, experiment_name: str) -> Dict[str, Any]:
        """Get experiment results with statistics."""

        experiment = self.db.query(Experiment).filter(
            Experiment.name == experiment_name
        ).first()

        if not experiment:
            return None

        results = {}
        variants = self.db.query(Variant).filter(
            Variant.experiment_id == experiment.id
        ).all()

        for variant in variants:
            assignments = self.db.query(Assignment).filter(
                Assignment.variant_id == variant.id
            ).count()

            conversions = self.db.query(Event).filter(
                Event.variant_id == variant.id,
                Event.event_type == 'conversion'
            ).count()

            results[variant.name] = {
                "users": assignments,
                "conversions": conversions,
                "rate": conversions / assignments if assignments > 0 else 0
            }

        return results
```

### FastAPI Endpoints

```python
# api/experiments.py
from fastapi import APIRouter, Depends
from services.experiment_service import ExperimentService

router = APIRouter(prefix="/experiments", tags=["experiments"])

@router.get("/{experiment_name}/variant")
async def get_variant(
    experiment_name: str,
    user_id: str,
    service: ExperimentService = Depends(get_experiment_service)
):
    variant = service.get_variant(experiment_name, user_id)
    return variant or {"variant": None}

@router.post("/{experiment_name}/track")
async def track_event(
    experiment_name: str,
    user_id: str,
    event_type: str,
    event_value: float = None,
    service: ExperimentService = Depends(get_experiment_service)
):
    service.track_event(experiment_name, user_id, event_type, event_value)
    return {"status": "tracked"}

@router.get("/{experiment_name}/results")
async def get_results(
    experiment_name: str,
    service: ExperimentService = Depends(get_experiment_service)
):
    return service.get_results(experiment_name)
```

### TypeScript Client

```typescript
// lib/experiments.ts

interface Variant {
  variant: string | null;
  config?: Record<string, any>;
}

class ExperimentClient {
  private baseUrl: string;
  private userId: string;
  private cache: Map<string, Variant> = new Map();

  constructor(baseUrl: string, userId: string) {
    this.baseUrl = baseUrl;
    this.userId = userId;
  }

  async getVariant(experimentName: string): Promise<Variant> {
    // Check cache first
    if (this.cache.has(experimentName)) {
      return this.cache.get(experimentName)!;
    }

    const response = await fetch(
      `${this.baseUrl}/experiments/${experimentName}/variant?user_id=${this.userId}`
    );
    const variant = await response.json();

    this.cache.set(experimentName, variant);
    return variant;
  }

  async trackConversion(
    experimentName: string,
    eventType: string = 'conversion',
    eventValue?: number
  ): Promise<void> {
    await fetch(
      `${this.baseUrl}/experiments/${experimentName}/track`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: this.userId,
          event_type: eventType,
          event_value: eventValue
        })
      }
    );
  }
}

// React Hook
export function useExperiment(experimentName: string) {
  const [variant, setVariant] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const client = useExperimentClient();

  useEffect(() => {
    client.getVariant(experimentName).then((result) => {
      setVariant(result.variant);
      setLoading(false);
    });
  }, [experimentName]);

  const trackConversion = useCallback((eventType = 'conversion') => {
    client.trackConversion(experimentName, eventType);
  }, [experimentName]);

  return { variant, loading, trackConversion };
}

// Usage
function PricingPage() {
  const { variant, loading, trackConversion } = useExperiment('pricing-test');

  if (loading) return <Loading />;

  return (
    <div>
      {variant === 'control' && <PricingA />}
      {variant === 'variant_b' && <PricingB />}

      <button onClick={() => trackConversion()}>
        Sign Up
      </button>
    </div>
  );
}
```

---

## 4. GrowthBook Integration

### Docker Setup

```yaml
# docker-compose addition
services:
  growthbook:
    image: growthbook/growthbook:latest
    container_name: ziggie-growthbook
    ports:
      - "3100:3000"
      - "3101:3100"
    environment:
      - MONGODB_URI=mongodb://ziggie:${MONGO_PASSWORD}@mongodb:27017/growthbook
      - JWT_SECRET=${GROWTHBOOK_JWT_SECRET}
      - ENCRYPTION_KEY=${GROWTHBOOK_ENCRYPTION_KEY}
      - API_HOST=http://localhost:3100
      - APP_ORIGIN=http://localhost:3100
    depends_on:
      - mongodb
    networks:
      - ziggie-network
```

### Python SDK

```python
# pip install growthbook

from growthbook import GrowthBook, Attributes, InMemoryFeatureCache

# Initialize with features
gb = GrowthBook(
    api_host="http://localhost:3100",
    client_key="sdk-abc123",
    enabled=True
)

# Load features
gb.load_features()

# Set user attributes
gb.set_attributes({
    "id": user.id,
    "email": user.email,
    "plan": user.plan,
    "country": user.country
})

# Check experiment variant
variant = gb.run({
    "key": "pricing-experiment",
    "variations": ["control", "variant_a", "variant_b"]
})

print(f"User is in variant: {variant.value}")

# Track conversion
if variant.in_experiment:
    # Your analytics tracking
    track_event("experiment_conversion", {
        "experiment": "pricing-experiment",
        "variant": variant.value
    })
```

### TypeScript SDK

```typescript
// npm install @growthbook/growthbook-react

import { GrowthBook, GrowthBookProvider, useFeature, useExperiment } from '@growthbook/growthbook-react';

// Initialize
const gb = new GrowthBook({
  apiHost: 'http://localhost:3100',
  clientKey: 'sdk-abc123',
  enableDevMode: process.env.NODE_ENV !== 'production',
  trackingCallback: (experiment, result) => {
    // Send to your analytics
    analytics.track('experiment_viewed', {
      experimentId: experiment.key,
      variationId: result.variationId
    });
  }
});

// Load features and set attributes
await gb.loadFeatures();
gb.setAttributes({
  id: user.id,
  email: user.email,
  plan: user.plan
});

// React Component
function App() {
  return (
    <GrowthBookProvider growthbook={gb}>
      <PricingPage />
    </GrowthBookProvider>
  );
}

function PricingPage() {
  const { value } = useExperiment({
    key: 'pricing-experiment',
    variations: ['control', 'variant_a', 'variant_b']
  });

  return (
    <div>
      {value === 'control' && <OriginalPricing />}
      {value === 'variant_a' && <NewPricingA />}
      {value === 'variant_b' && <NewPricingB />}
    </div>
  );
}
```

---

## 5. Optimizely Integration

### Python Full Stack SDK

```python
# pip install optimizely-sdk

from optimizely import optimizely

# Initialize
optimizely_client = optimizely.Optimizely(
    sdk_key="YOUR_SDK_KEY",
    datafile_access_token="YOUR_ACCESS_TOKEN"
)

# Activate experiment
user_id = "user123"
user_attributes = {
    "plan": "premium",
    "country": "US"
}

variation = optimizely_client.activate(
    "pricing_experiment",
    user_id,
    user_attributes
)

if variation == "control":
    show_original_pricing()
elif variation == "variant_a":
    show_new_pricing()

# Track conversion
optimizely_client.track(
    "purchase",
    user_id,
    user_attributes,
    {"revenue": 9900}  # In cents
)
```

### TypeScript Web SDK

```typescript
// npm install @optimizely/optimizely-sdk

import * as optimizelySdk from '@optimizely/optimizely-sdk';

const optimizely = optimizelySdk.createInstance({
  sdkKey: 'YOUR_SDK_KEY'
});

await optimizely.onReady();

// Activate experiment
const userId = 'user123';
const userAttributes = {
  plan: 'premium',
  country: 'US'
};

const variation = optimizely.activate(
  'pricing_experiment',
  userId,
  userAttributes
);

// React hook pattern
function usePricingExperiment() {
  const [variation, setVariation] = useState<string | null>(null);

  useEffect(() => {
    const userId = getUserId();
    const v = optimizely.activate('pricing_experiment', userId);
    setVariation(v);
  }, []);

  return variation;
}
```

---

## 6. Statistical Analysis

### Z-Test for Proportions

```python
import scipy.stats as stats
import numpy as np

def calculate_significance(
    control_conversions: int,
    control_total: int,
    treatment_conversions: int,
    treatment_total: int
) -> dict:
    """Calculate statistical significance between two variants."""

    # Conversion rates
    p1 = control_conversions / control_total
    p2 = treatment_conversions / treatment_total

    # Pooled proportion
    pooled = (control_conversions + treatment_conversions) / (control_total + treatment_total)

    # Standard error
    se = np.sqrt(pooled * (1 - pooled) * (1/control_total + 1/treatment_total))

    # Z-score
    z = (p2 - p1) / se

    # P-value (two-tailed)
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    # Confidence interval
    ci_95 = stats.norm.interval(0.95, loc=p2-p1, scale=se)

    # Relative lift
    lift = (p2 - p1) / p1 if p1 > 0 else 0

    return {
        "control_rate": p1,
        "treatment_rate": p2,
        "lift": lift,
        "z_score": z,
        "p_value": p_value,
        "significant": p_value < 0.05,
        "confidence_interval": ci_95
    }

# Example usage
results = calculate_significance(
    control_conversions=150,
    control_total=3000,
    treatment_conversions=180,
    treatment_total=3000
)

print(f"Control Rate: {results['control_rate']:.2%}")
print(f"Treatment Rate: {results['treatment_rate']:.2%}")
print(f"Lift: {results['lift']:.2%}")
print(f"P-Value: {results['p_value']:.4f}")
print(f"Significant: {results['significant']}")
```

### Bayesian Analysis

```python
from scipy import stats
import numpy as np

def bayesian_ab_test(
    control_conversions: int,
    control_total: int,
    treatment_conversions: int,
    treatment_total: int,
    simulations: int = 100000
) -> dict:
    """Bayesian A/B test using Beta distributions."""

    # Prior: Beta(1, 1) = Uniform
    # Posterior: Beta(conversions + 1, non-conversions + 1)

    control_alpha = control_conversions + 1
    control_beta = control_total - control_conversions + 1

    treatment_alpha = treatment_conversions + 1
    treatment_beta = treatment_total - treatment_conversions + 1

    # Sample from posteriors
    control_samples = np.random.beta(control_alpha, control_beta, simulations)
    treatment_samples = np.random.beta(treatment_alpha, treatment_beta, simulations)

    # Probability that treatment > control
    prob_treatment_better = np.mean(treatment_samples > control_samples)

    # Expected lift
    lift_samples = (treatment_samples - control_samples) / control_samples
    expected_lift = np.mean(lift_samples)

    # Credible interval for lift
    lift_ci = np.percentile(lift_samples, [2.5, 97.5])

    return {
        "prob_treatment_better": prob_treatment_better,
        "expected_lift": expected_lift,
        "lift_credible_interval": lift_ci,
        "control_mean": control_samples.mean(),
        "treatment_mean": treatment_samples.mean()
    }

# Example
results = bayesian_ab_test(150, 3000, 180, 3000)
print(f"Probability Treatment is Better: {results['prob_treatment_better']:.1%}")
print(f"Expected Lift: {results['expected_lift']:.1%}")
```

---

## 7. Best Practices

### Experiment Design

```
1. Hypothesis First
   Bad: "Let's test a new button color"
   Good: "We believe a green CTA will increase clicks by 15% because green signals 'go'"

2. One Variable at a Time
   Bad: Test new headline + button + layout together
   Good: Test one element, measure, then test next

3. Sufficient Sample Size
   Calculate required sample BEFORE starting
   Run experiment until you hit the number (not until you see significance)

4. Avoid Peeking
   Don't stop early when you see promising results
   This inflates false positive rate
```

### Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| Peeking | Early stopping inflates errors | Pre-define sample size |
| Too many variants | Requires larger sample | Max 3-4 variants |
| Segment analysis | Multiple testing problem | Pre-register segments |
| Short duration | Novelty effect | Run for at least 2 weeks |
| Contamination | Users see both variants | Consistent assignment |

### Experiment Documentation Template

```markdown
## Experiment: [Name]

### Hypothesis
We believe [change] will [impact] for [users] because [reason].

### Metrics
- Primary: Conversion rate
- Secondary: Revenue per user, Time on page
- Guardrail: Page load time, Error rate

### Variants
- Control (50%): Current experience
- Treatment (50%): [Description of change]

### Sample Size
- Required: 3,900 per variant
- Duration: ~2 weeks at current traffic

### Results
- Start Date: 2025-01-15
- End Date: 2025-01-29
- Winner: Treatment
- Lift: +18% (95% CI: [12%, 24%])
- P-value: 0.002

### Decision
Ship treatment to 100% of users.
```

---

## 8. Monitoring and Reporting

### Real-Time Dashboard Query

```sql
-- Experiment summary dashboard
WITH experiment_data AS (
    SELECT
        e.name as experiment_name,
        v.name as variant_name,
        v.is_control,
        COUNT(DISTINCT a.user_id) as users,
        COUNT(DISTINCT CASE WHEN ev.event_type = 'conversion' THEN ev.user_id END) as conversions
    FROM experiments e
    JOIN experiment_variants v ON e.id = v.experiment_id
    LEFT JOIN experiment_assignments a ON v.id = a.variant_id
    LEFT JOIN experiment_events ev ON a.variant_id = ev.variant_id
        AND a.user_id = ev.user_id
    WHERE e.status = 'running'
    GROUP BY e.name, v.name, v.is_control
)
SELECT
    experiment_name,
    variant_name,
    is_control,
    users,
    conversions,
    ROUND(conversions::numeric / NULLIF(users, 0) * 100, 2) as conversion_rate
FROM experiment_data
ORDER BY experiment_name, is_control DESC;
```

### Grafana Dashboard

```json
{
  "panels": [
    {
      "title": "Experiment Conversion Rates",
      "type": "timeseries",
      "targets": [
        {
          "expr": "sum(experiment_conversions{experiment=\"$experiment\"}) by (variant) / sum(experiment_users{experiment=\"$experiment\"}) by (variant)"
        }
      ]
    },
    {
      "title": "Cumulative Users per Variant",
      "type": "stat",
      "targets": [
        {
          "expr": "sum(experiment_users{experiment=\"$experiment\"}) by (variant)"
        }
      ]
    }
  ]
}
```

### Alerting Rules

```yaml
# prometheus/alerts/experiments.yml
groups:
  - name: experiments
    rules:
      - alert: ExperimentSampleReached
        expr: sum(experiment_users) by (experiment) >= experiment_required_sample
        labels:
          severity: info
        annotations:
          summary: "Experiment {{ $labels.experiment }} reached required sample size"

      - alert: ExperimentConversionDrop
        expr: |
          (sum(rate(experiment_conversions[1h])) by (experiment, variant) /
           sum(rate(experiment_users[1h])) by (experiment, variant)) < 0.01
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "Conversion rate dropped significantly in {{ $labels.experiment }}"
```

---

## Quick Reference

### Experiment Lifecycle

```
1. DESIGN -> Define hypothesis, metrics, sample size
2. BUILD -> Implement variants, tracking
3. QA -> Test both variants work correctly
4. LAUNCH -> Start experiment, monitor
5. ANALYZE -> Wait for sample size, calculate results
6. DECIDE -> Ship winner or iterate
7. CLEANUP -> Remove losing variant code
```

### Code Patterns

```python
# Python - Simple variant check
variant = experiment_service.get_variant("pricing-test", user_id)
if variant == "treatment":
    price = 9.99
else:
    price = 14.99

# Track conversion
experiment_service.track("pricing-test", user_id, "purchase", price)
```

```typescript
// TypeScript/React
const { variant, trackConversion } = useExperiment('pricing-test');

return (
  <div>
    <Price amount={variant === 'treatment' ? 9.99 : 14.99} />
    <button onClick={() => trackConversion('purchase')}>
      Buy Now
    </button>
  </div>
);
```

### Statistical Thresholds

| Metric | Minimum | Recommended |
|--------|---------|-------------|
| Confidence Level | 90% | 95% |
| Statistical Power | 80% | 80% |
| Minimum Sample | 100/variant | 1000/variant |
| Minimum Duration | 1 week | 2 weeks |

---

*A/B Testing Guide for Ziggie AI Ecosystem*
*Part of LOW priority gap completion (#45)*
