# AWS Bedrock Quick Reference Card

> **One-page cheat sheet for Ziggie Cloud team**

---

## Model IDs (Copy-Paste Ready)

```python
# Claude Models (Anthropic)
CLAUDE_SONNET = "anthropic.claude-3-5-sonnet-20241022-v2:0"
CLAUDE_HAIKU = "anthropic.claude-3-haiku-20240307-v1:0"
CLAUDE_OPUS = "anthropic.claude-3-opus-20240229-v1:0"

# Titan Models (Amazon)
TITAN_EXPRESS = "amazon.titan-text-express-v1"
TITAN_PREMIER = "amazon.titan-text-premier-v1:0"

# Llama Models (Meta)
LLAMA_70B = "meta.llama3-1-70b-instruct-v1:0"
LLAMA_8B = "meta.llama3-1-8b-instruct-v1:0"

# Embeddings
TITAN_EMBEDDINGS = "amazon.titan-embed-text-v1"
```

---

## Pricing (per 1M tokens)

| Model | Input | Output | Use When |
|-------|-------|--------|----------|
| **Claude 3 Haiku** | $0.25 | $1.25 | Speed matters, simple tasks |
| **Claude 3.5 Sonnet** | $3.00 | $15.00 | Quality matters, complex tasks |
| **Titan Express** | $0.20 | $0.60 | Ultra-low cost, basic tasks |
| **GPT-4 Turbo** | $10.00 | $30.00 | ❌ Replace with Sonnet (70% savings) |

---

## Quick Setup (3 Commands)

```bash
# 1. Enable model access (AWS Console)
# Navigate to: Bedrock → Model Access → Enable Claude 3.5 Sonnet + Haiku

# 2. Create IAM user
aws iam create-user --user-name n8n-bedrock-user

# 3. Add credentials to n8n
# Settings → Credentials → AWS API → Add keys from step 2
```

---

## Python One-Liner

```python
import boto3, json
bedrock = boto3.client('bedrock-runtime', region_name='eu-north-1')
response = bedrock.invoke_model(
    modelId='anthropic.claude-3-haiku-20240307-v1:0',
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": "Your prompt here"}]
    })
)
print(json.loads(response['body'].read())['content'][0]['text'])
```

---

## Node.js One-Liner

```javascript
import { BedrockRuntimeClient, InvokeModelCommand } from "@aws-sdk/client-bedrock-runtime";
const client = new BedrockRuntimeClient({ region: "eu-north-1" });
const response = await client.send(new InvokeModelCommand({
  modelId: "anthropic.claude-3-haiku-20240307-v1:0",
  body: JSON.stringify({
    anthropic_version: "bedrock-2023-05-31",
    max_tokens: 1000,
    messages: [{ role: "user", content: "Your prompt here" }]
  })
}));
console.log(JSON.parse(new TextDecoder().decode(response.body)).content[0].text);
```

---

## cURL Test

```bash
aws bedrock-runtime invoke-model \
  --region eu-north-1 \
  --model-id anthropic.claude-3-haiku-20240307-v1:0 \
  --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":1000,"messages":[{"role":"user","content":"Hello"}]}' \
  --cli-binary-format raw-in-base64-out \
  output.json && cat output.json | jq -r '.content[0].text'
```

---

## Decision Tree

```
What's your use case?
│
├─ Simple chatbot, high volume
│  └─→ Claude 3 Haiku ($0.25/$1.25)
│
├─ Code generation, analysis
│  └─→ Claude 3.5 Sonnet ($3/$15)
│
├─ Creative writing, narrative
│  └─→ Claude 3.5 Sonnet ($3/$15)
│
├─ Summarization, simple tasks
│  └─→ Titan Text Express ($0.20/$0.60)
│
└─ Image generation
   └─→ Keep OpenAI DALL-E 3
```

---

## Cost Comparison (1M tokens/month)

| Scenario | Monthly Cost | Annual Savings |
|----------|--------------|----------------|
| **Current (OpenAI)** | $20.85 | - |
| **Bedrock Direct** | $9.33 | $138 (55%) |
| **Bedrock Optimized** | $7.80 | $157 (63%) |

---

## Environment Variables

```bash
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=[REDACTED]
AWS_REGION=eu-north-1
```

---

## Common Errors

| Error | Solution |
|-------|----------|
| `AccessDeniedException` | Enable model in Bedrock Console → Model Access |
| `ValidationException: model not found` | Check model ID spelling, region availability |
| `ThrottlingException` | Add retry with exponential backoff |
| `ServiceQuotaExceededException` | Request quota increase in Service Quotas console |

---

## Monitoring Commands

```bash
# Check current month cost
aws ce get-cost-and-usage \
  --time-period Start=2025-12-01,End=2025-12-23 \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["Amazon Bedrock"]}}'

# List available models
aws bedrock list-foundation-models --region eu-north-1

# Test model access
aws bedrock-runtime invoke-model \
  --model-id anthropic.claude-3-haiku-20240307-v1:0 \
  --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}' \
  --region eu-north-1 test.json
```

---

## IAM Policy (Minimal)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
      "Resource": [
        "arn:aws:bedrock:eu-north-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
        "arn:aws:bedrock:eu-north-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
      ]
    }
  ]
}
```

---

## n8n Node Configuration

```json
{
  "type": "n8n-nodes-base.awsBedrock",
  "parameters": {
    "resource": "text",
    "operation": "message",
    "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
    "prompt": "={{ $json.userMessage }}",
    "maxTokens": 1000,
    "temperature": 0.7
  },
  "credentials": {
    "awsApi": {
      "id": "1",
      "name": "AWS Bedrock"
    }
  }
}
```

---

## Temperature Guide

| Value | Effect | Use Case |
|-------|--------|----------|
| **0.0-0.3** | Deterministic, factual | Code generation, data extraction |
| **0.5-0.7** | Balanced | General chat, Q&A |
| **0.8-1.0** | Creative, varied | Creative writing, brainstorming |

---

## Token Estimation

| Content Type | Tokens (approx) |
|--------------|-----------------|
| 1 word | ~1.3 tokens |
| 1 sentence | ~15-20 tokens |
| 1 paragraph | ~100 tokens |
| 1 page | ~500 tokens |
| GPT-4 prompt "Create warmup" | ~5 tokens |
| Workout script output (200 words) | ~260 tokens |

---

## Quick Cost Calculator

```python
def estimate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """Calculate cost for token usage"""
    pricing = {
        'HAIKU': {'input': 0.25, 'output': 1.25},
        'SONNET': {'input': 3.00, 'output': 15.00},
    }
    p = pricing[model]
    return (input_tokens / 1_000_000) * p['input'] + (output_tokens / 1_000_000) * p['output']

# Example: 1000 input, 500 output tokens with Haiku
cost = estimate_cost(1000, 500, 'HAIKU')  # $0.000875 (~$0.001)
```

---

## Migration Checklist

- [ ] Enable Bedrock model access (eu-north-1)
- [ ] Create IAM user `n8n-bedrock-user`
- [ ] Add credentials to n8n and Flowise
- [ ] Test with sample prompt
- [ ] Migrate 1 low-risk chatbot
- [ ] Monitor costs for 1 week
- [ ] Expand to all workloads
- [ ] Set up CloudWatch cost alerts

---

## Support Links

- **AWS Bedrock Docs**: https://docs.aws.amazon.com/bedrock/
- **Pricing**: https://aws.amazon.com/bedrock/pricing/
- **n8n Integration**: https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-base.awsbedrock/
- **Flowise Setup**: https://docs.flowiseai.com/integrations/langchain/chat-models/aws-bedrock

---

## Regional Availability

| Region | Code | Claude 3.5 | Claude 3 Haiku | Titan |
|--------|------|-----------|---------------|-------|
| **Stockholm** | eu-north-1 | ✅ | ✅ | ✅ |
| Frankfurt | eu-central-1 | ✅ | ✅ | ✅ |
| London | eu-west-2 | ✅ | ✅ | ✅ |
| N. Virginia | us-east-1 | ✅ | ✅ | ✅ |

---

## Best Practices

1. **Use Haiku first** - Try cheapest model, upgrade if needed
2. **Set max_tokens** - Cap at 1000 for chatbots to control costs
3. **Implement retry logic** - Handle rate limits with exponential backoff
4. **Monitor costs weekly** - Check CloudWatch for unexpected usage spikes
5. **Keep OpenAI backup** - For image generation (DALL-E 3)
6. **Log token usage** - Track per-model usage for optimization
7. **Use streaming** - For long responses (>500 tokens) to improve UX

---

## Emergency Rollback

If Bedrock fails, revert to OpenAI:

1. **n8n**: Change node type from `awsBedrock` back to `openAi`
2. **Flowise**: Switch LLM provider from "AWS Bedrock" to "OpenAI"
3. **Code**: Change `boto3.client('bedrock-runtime')` to `OpenAI()` client
4. **Time to rollback**: <30 minutes

---

**Print this card and keep handy during migration!**
