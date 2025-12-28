# AWS Bedrock Cost Calculator - Ziggie Cloud

> **Interactive cost comparison for OpenAI vs AWS Bedrock migration**

---

## Current OpenAI Costs (Baseline)

### Assumed Current Usage

| Workload | Monthly Tokens (Input) | Monthly Tokens (Output) | Model | Cost/Month |
|----------|------------------------|-------------------------|-------|------------|
| AI Instructor Scripts | 300,000 | 200,000 | GPT-4 Turbo | $3.00 + $6.00 = **$9.00** |
| Flowise Chatbots | 500,000 | 400,000 | GPT-3.5 Turbo | $0.25 + $0.60 = **$0.85** |
| Code Generation | 200,000 | 150,000 | GPT-4 Turbo | $2.00 + $4.50 = **$6.50** |
| Game Narrative | 150,000 | 100,000 | GPT-4 | $1.50 + $3.00 = **$4.50** |
| **TOTAL** | **1,150,000** | **850,000** | - | **$20.85** |

### OpenAI Pricing Reference (2025)

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Context Window |
|-------|----------------------|------------------------|----------------|
| GPT-4 Turbo | $10.00 | $30.00 | 128K tokens |
| GPT-4 | $30.00 | $60.00 | 8K tokens |
| GPT-3.5 Turbo | $0.50 | $1.50 | 16K tokens |
| DALL-E 3 | $0.040/image (1024x1024) | - | - |

---

## AWS Bedrock Alternative Costs

### Scenario 1: Direct Replacement (Same Models)

| Workload | Monthly Tokens (Input) | Monthly Tokens (Output) | Model | Cost/Month |
|----------|------------------------|-------------------------|-------|------------|
| AI Instructor Scripts | 300,000 | 200,000 | Claude 3.5 Sonnet | $0.90 + $3.00 = **$3.90** |
| Flowise Chatbots | 500,000 | 400,000 | Claude 3 Haiku | $0.13 + $0.50 = **$0.63** |
| Code Generation | 200,000 | 150,000 | Claude 3.5 Sonnet | $0.60 + $2.25 = **$2.85** |
| Game Narrative | 150,000 | 100,000 | Claude 3.5 Sonnet | $0.45 + $1.50 = **$1.95** |
| **TOTAL** | **1,150,000** | **850,000** | - | **$9.33** |

**Savings**: $20.85 - $9.33 = **$11.52/month (55% reduction)**

---

### Scenario 2: Optimized Multi-Model (Recommended)

**Strategy**: Use Claude 3 Haiku for simple tasks, Claude 3.5 Sonnet only for complex

| Workload | Input | Output | Model | Cost |
|----------|-------|--------|-------|------|
| AI Instructor Scripts (Complex) | 200,000 | 150,000 | Claude 3.5 Sonnet | $0.60 + $2.25 = **$2.85** |
| AI Instructor Scripts (Simple) | 100,000 | 50,000 | Claude 3 Haiku | $0.03 + $0.06 = **$0.09** |
| Flowise Chatbots | 500,000 | 400,000 | Claude 3 Haiku | $0.13 + $0.50 = **$0.63** |
| Code Generation (Complex) | 150,000 | 120,000 | Claude 3.5 Sonnet | $0.45 + $1.80 = **$2.25** |
| Code Generation (Simple) | 50,000 | 30,000 | Titan Text Express | $0.01 + $0.02 = **$0.03** |
| Game Narrative | 150,000 | 100,000 | Claude 3.5 Sonnet | $0.45 + $1.50 = **$1.95** |
| **TOTAL** | **1,150,000** | **850,000** | - | **$7.80** |

**Savings**: $20.85 - $7.80 = **$13.05/month (63% reduction)**

---

### Scenario 3: Maximum Cost Optimization

**Strategy**: Use cheapest models wherever quality acceptable

| Workload | Input | Output | Model | Cost |
|----------|-------|--------|-------|------|
| AI Instructor Scripts | 300,000 | 200,000 | Claude 3 Haiku | $0.08 + $0.25 = **$0.33** |
| Flowise Chatbots | 500,000 | 400,000 | Claude 3 Haiku | $0.13 + $0.50 = **$0.63** |
| Code Generation | 200,000 | 150,000 | Claude 3.5 Sonnet | $0.60 + $2.25 = **$2.85** |
| Game Narrative | 150,000 | 100,000 | Llama 3.1 70B | $0.15 + $0.10 = **$0.25** |
| **TOTAL** | **1,150,000** | **850,000** | - | **$4.06** |

**Savings**: $20.85 - $4.06 = **$16.79/month (81% reduction)**

**Risk**: Quality may be lower for creative tasks (AI instructor, narrative)

---

## Annual Cost Projection

| Scenario | Monthly Cost | Annual Cost | Annual Savings vs OpenAI |
|----------|--------------|-------------|--------------------------|
| **Current (OpenAI)** | $20.85 | $250.20 | - |
| **Scenario 1 (Direct)** | $9.33 | $111.96 | **$138.24 (55%)** |
| **Scenario 2 (Optimized)** | $7.80 | $93.60 | **$156.60 (63%)** |
| **Scenario 3 (Max Savings)** | $4.06 | $48.72 | **$201.48 (81%)** |

---

## Bedrock Model Pricing Reference (2025)

### Text Generation Models

| Provider | Model | Input (per 1M) | Output (per 1M) | Context | Best For |
|----------|-------|----------------|-----------------|---------|----------|
| **Anthropic** | Claude 3.5 Sonnet v2 | $3.00 | $15.00 | 200K | Complex reasoning, code |
| **Anthropic** | Claude 3 Opus | $15.00 | $75.00 | 200K | Highest quality |
| **Anthropic** | Claude 3 Haiku | $0.25 | $1.25 | 200K | Speed, high volume |
| **Amazon** | Titan Text Premier | $0.50 | $1.50 | 32K | Balanced |
| **Amazon** | Titan Text Express | $0.20 | $0.60 | 8K | Simple tasks |
| **Meta** | Llama 3.1 405B | $2.65 | $3.50 | 128K | Open source, large |
| **Meta** | Llama 3.1 70B | $0.99 | $0.99 | 128K | Balanced OS |
| **Meta** | Llama 3.1 8B | $0.22 | $0.22 | 128K | Ultra-low cost |
| **Cohere** | Command R+ | $2.50 | $10.00 | 128K | RAG, search |
| **AI21** | Jamba 1.5 Large | $2.00 | $8.00 | 256K | Long context |

### Embedding Models

| Provider | Model | Cost per 1M tokens | Dimensions |
|----------|-------|-------------------|------------|
| **Amazon** | Titan Embeddings G1 | $0.10 | 1536 |
| **Cohere** | Embed English v3 | $0.10 | 1024 |
| **Cohere** | Embed Multilingual v3 | $0.10 | 1024 |

---

## Cost Calculator Spreadsheet

### Custom Usage Calculation

**Formula**: `(Input_Tokens / 1,000,000) × Input_Price + (Output_Tokens / 1,000,000) × Output_Price`

#### Example: AI Instructor Script Generation

**Current (GPT-4 Turbo)**:
- Input: 300,000 tokens/month
- Output: 200,000 tokens/month
- Cost: `(300,000 / 1,000,000) × $10 + (200,000 / 1,000,000) × $30 = $3 + $6 = $9`

**Bedrock (Claude 3.5 Sonnet)**:
- Input: 300,000 tokens/month
- Output: 200,000 tokens/month
- Cost: `(300,000 / 1,000,000) × $3 + (200,000 / 1,000,000) × $15 = $0.90 + $3 = $3.90`

**Savings**: $9 - $3.90 = **$5.10/month per workload**

---

## ROI Analysis

### Time Investment vs Cost Savings

| Activity | Time Required | Annual Savings (Scenario 2) |
|----------|---------------|----------------------------|
| Initial Setup | 2 hours | - |
| Migration Testing | 4 hours | - |
| Workflow Updates | 3 hours | - |
| Monitoring Setup | 1 hour | - |
| **Total** | **10 hours** | **$156.60/year** |

**Hourly ROI**: $156.60 / 10 hours = **$15.66/hour**

**Payback Period**: Immediate (month 1 savings > setup time)

---

## Hidden Costs to Consider

### Additional Bedrock Costs

| Component | Cost | When Applicable |
|-----------|------|-----------------|
| **Data Transfer** | $0.09/GB out | If sending large responses to external systems |
| **Provisioned Throughput** | $X/hour | Only if reserved capacity needed (not typical) |
| **Knowledge Base Storage** | $0.24/OCU-hour | Only if using Bedrock Knowledge Bases |
| **Custom Models** | $1000+ setup | Only if fine-tuning models |

**For typical usage**: Zero additional costs beyond per-token pricing

### AWS Account Management

| Item | Cost |
|------|------|
| IAM user | Free |
| CloudWatch basic monitoring | Free (first 10 metrics) |
| S3 for knowledge bases | $0.023/GB-month (if used) |

---

## Cost Monitoring Setup

### CloudWatch Metrics to Track

```bash
# 1. Token usage by model
aws cloudwatch get-metric-statistics \
  --namespace AWS/Bedrock \
  --metric-name InputTokens \
  --dimensions Name=ModelId,Value=anthropic.claude-3-5-sonnet-20241022-v2:0 \
  --start-time 2025-12-01T00:00:00Z \
  --end-time 2025-12-23T23:59:59Z \
  --period 86400 \
  --statistics Sum

# 2. Estimated charges
aws cloudwatch get-metric-statistics \
  --namespace AWS/Billing \
  --metric-name EstimatedCharges \
  --dimensions Name=ServiceName,Value=AmazonBedrock \
  --start-time 2025-12-01T00:00:00Z \
  --end-time 2025-12-23T23:59:59Z \
  --period 86400 \
  --statistics Maximum \
  --region us-east-1
```

### Cost Alerts

```bash
# Alert if daily cost exceeds $5
aws cloudwatch put-metric-alarm \
  --alarm-name bedrock-daily-cost-alert \
  --alarm-description "Alert if daily Bedrock cost exceeds $5" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 86400 \
  --evaluation-periods 1 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=ServiceName,Value=AmazonBedrock \
  --region us-east-1
```

---

## Break-Even Analysis

### Scenarios Where Bedrock May NOT Save Money

1. **Very Low Usage** (<100K tokens/month): Setup time > savings
2. **Image-Heavy Workflows**: Must keep OpenAI DALL-E anyway
3. **Existing OpenAI Enterprise Contracts**: May have volume discounts
4. **Multi-Cloud Restrictions**: If AWS not allowed in infrastructure

### When Bedrock Makes Sense

✅ **100K+ tokens/month**: Setup time justified
✅ **Text-heavy workloads**: No image generation needs
✅ **AWS-centric infrastructure**: Already using AWS services
✅ **GDPR/EU data residency**: Need eu-north-1 hosting
✅ **Multi-model strategy**: Want flexibility to switch models

---

## Recommended Migration Path

### Phase 1: Test (Week 1) - $0 Migration Cost

- Migrate 1 low-risk chatbot (10K tokens/month)
- Expected savings: ~$0.50/month
- Validate quality and latency

### Phase 2: AI Instructor (Week 2-3) - Highest Savings

- Migrate AI instructor script generation
- Current cost: $9/month (GPT-4)
- New cost: $3.90/month (Claude 3.5 Sonnet)
- **Savings**: $5.10/month

### Phase 3: Chatbots (Week 4) - High Volume

- Migrate all Flowise chatbots
- Current cost: $0.85/month (GPT-3.5)
- New cost: $0.63/month (Claude 3 Haiku)
- **Savings**: $0.22/month

### Phase 4: Code + Narrative (Month 2) - Complete Migration

- Migrate remaining workloads
- Current cost: $11/month
- New cost: $4.80/month
- **Savings**: $6.20/month

**Total Projected Savings**: $11.52/month = **$138/year**

---

## Final Recommendation

**Adopt Scenario 2: Optimized Multi-Model Strategy**

- **Annual Savings**: $156.60 (63% reduction)
- **Setup Time**: 10 hours one-time
- **Payback**: Immediate (month 1)
- **Risk**: Low (gradual migration, keep OpenAI backup)

**Key Actions**:
1. Start with AI instructor scripts (highest savings)
2. Use Claude 3 Haiku for chatbots (high volume)
3. Keep Claude 3.5 Sonnet for complex tasks (code, narrative)
4. Monitor costs weekly for first month

---

## Cost Tracking Template

### Monthly Usage Log

| Month | Total Input Tokens | Total Output Tokens | Total Cost | Notes |
|-------|-------------------|---------------------|------------|-------|
| Jan 2025 | 1,150,000 | 850,000 | $7.80 | Baseline month |
| Feb 2025 | - | - | - | - |
| Mar 2025 | - | - | - | - |

### Model Usage Breakdown

| Model | Input Tokens | Output Tokens | Cost | % of Total |
|-------|--------------|---------------|------|------------|
| Claude 3.5 Sonnet | 500,000 | 400,000 | $7.50 | 96% |
| Claude 3 Haiku | 600,000 | 420,000 | $0.68 | 9% |
| Titan Text Express | 50,000 | 30,000 | $0.03 | <1% |
| **Total** | **1,150,000** | **850,000** | **$8.21** | **100%** |

---

**Use this calculator to validate actual usage before committing to full migration.**
