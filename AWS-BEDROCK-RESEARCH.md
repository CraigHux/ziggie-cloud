# AWS Bedrock Research for Ziggie Cloud Ecosystem

> **Last Updated**: 2025-12-23
> **Context**: Evaluating AWS Bedrock as alternative/supplement to OpenAI GPT-4
> **Current Setup**: Flowise chatbots + n8n workflows in EU-North-1 (Stockholm)

---

## Executive Summary

AWS Bedrock provides managed access to foundation models from Amazon, Anthropic, Meta, Cohere, and AI21 Labs. Key advantages for Ziggie Cloud:
- **Multi-vendor access**: Reduce OpenAI lock-in with Claude, Llama, Titan options
- **Regional deployment**: Available in EU-North-1 (Stockholm) for GDPR compliance
- **Serverless**: Pay-per-token, no infrastructure management
- **Enterprise features**: Knowledge Bases for RAG, Guardrails, model customization

**Critical Decision**: Claude 3.5 Sonnet costs 20-30% more on Bedrock vs direct Anthropic API, but provides unified AWS billing and simplified compliance.

---

## 1. AWS Bedrock Available Models (2025)

### Foundation Models by Provider

| Provider | Model | Input (per 1M tokens) | Output (per 1M tokens) | Use Case |
|----------|-------|----------------------|------------------------|----------|
| **Anthropic** | Claude 3.5 Sonnet v2 | $3.00 | $15.00 | Code, analysis, complex reasoning |
| **Anthropic** | Claude 3 Opus | $15.00 | $75.00 | Highest quality, research |
| **Anthropic** | Claude 3 Haiku | $0.25 | $1.25 | Fast responses, high volume |
| **Amazon** | Titan Text Premier | $0.50 | $1.50 | Cost-effective general use |
| **Amazon** | Titan Text Express | $0.20 | $0.60 | Simple tasks, chat |
| **Meta** | Llama 3.1 405B | $2.65 | $3.50 | Open weights, large scale |
| **Meta** | Llama 3.1 70B | $0.99 | $0.99 | Balanced performance/cost |
| **Meta** | Llama 3.1 8B | $0.22 | $0.22 | Ultra-low cost |
| **Cohere** | Command R+ | $2.50 | $10.00 | RAG, search, multilingual |
| **AI21 Labs** | Jamba 1.5 Large | $2.00 | $8.00 | Long context (256K tokens) |

### Regional Availability (EU-North-1 Stockholm)

**Available in eu-north-1**:
- ✅ Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku
- ✅ Titan Text Express, Titan Text Premier
- ✅ Llama 3.1 (8B, 70B, 405B)
- ✅ Command R+
- ❌ Some models limited to us-east-1/us-west-2

**Verification Required**: Check AWS Bedrock Console → Model Access in eu-north-1 for current availability.

---

## 2. Cost Comparison: Bedrock vs Direct API Calls

### Claude 3.5 Sonnet: Bedrock vs Anthropic Direct

| Metric | AWS Bedrock | Anthropic API | Delta |
|--------|-------------|---------------|-------|
| **Input** | $3.00/1M tokens | $3.00/1M tokens | Same |
| **Output** | $15.00/1M tokens | $15.00/1M tokens | Same |
| **Billing** | AWS unified bill | Separate vendor | - |
| **Rate Limits** | Higher (enterprise) | Standard tier limits | Bedrock advantage |
| **Latency** | ~100-200ms overhead | Direct connection | API slightly faster |

**Note**: Pricing is equivalent as of 2025. Bedrock previously had 20-30% markup but pricing has aligned.

### OpenAI GPT-4 Turbo vs Claude 3.5 Sonnet (Bedrock)

| Model | Input/1M | Output/1M | Quality | Speed |
|-------|----------|-----------|---------|-------|
| **GPT-4 Turbo** | $10.00 | $30.00 | Excellent | Fast |
| **Claude 3.5 Sonnet** | $3.00 | $15.00 | Excellent | Fast |
| **Savings** | -70% | -50% | Comparable | Comparable |

**Recommendation**: Migrate GPT-4 workloads to Claude 3.5 Sonnet for 50-70% cost reduction.

### Cost Estimation: 1M Tokens/Month Usage

**Scenario**: AI instructor scripts + chatbots + code generation

| Workload | Input Tokens | Output Tokens | Model | Monthly Cost |
|----------|--------------|---------------|-------|--------------|
| AI Instructor Scripts | 300K | 200K | Claude 3.5 Sonnet | $3.90 |
| Flowise Chatbots | 400K | 300K | Claude 3 Haiku | $0.48 |
| Code Generation | 200K | 100K | Claude 3.5 Sonnet | $2.10 |
| Game Narrative | 100K | 100K | Titan Text Premier | $0.20 |
| **Total** | **1M** | **700K** | **Mixed** | **$6.68** |

**OpenAI GPT-4 Equivalent**: $10.00 (input) + $21.00 (output) = **$31.00/month**

**Savings**: $24.32/month (78% reduction) by using model-appropriate tiering.

---

## 3. Integration with n8n Workflows

### AWS Bedrock Node (Native)

n8n has native AWS Bedrock support as of version 1.0+:

```typescript
// n8n AWS Bedrock node configuration
{
  "resource": "text",
  "operation": "message",
  "modelId": "anthropic.claude-3-5-sonnet-20241022-v2:0",
  "prompt": "={{ $json.userMessage }}",
  "maxTokens": 1000,
  "temperature": 0.7,
  "credentials": "awsBedrockApi"
}
```

### Custom HTTP Node (Alternative)

If native node unavailable, use AWS SDK via HTTP:

```json
{
  "method": "POST",
  "url": "https://bedrock-runtime.eu-north-1.amazonaws.com/model/anthropic.claude-3-5-sonnet-20241022-v2:0/invoke",
  "authentication": "predefinedCredentialType",
  "nodeCredentialType": "awsApi",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1000,
    "messages": [
      {
        "role": "user",
        "content": "={{ $json.prompt }}"
      }
    ]
  }
}
```

### Workflow Pattern: Multi-Model Routing

```text
Trigger (Webhook)
  ↓
Switch Node (by task type)
  ├─→ Complex reasoning → Claude 3.5 Sonnet
  ├─→ Simple chat → Claude 3 Haiku
  ├─→ Code generation → Claude 3.5 Sonnet
  └─→ Summarization → Titan Text Express
  ↓
Response
```

---

## 4. Integration with Flowise

### Bedrock as LLM Provider in Flowise

**Setup Steps**:

1. **Add AWS Bedrock Credentials**:
   - In Flowise UI → Credentials → Add Credential
   - Select "AWS Bedrock API"
   - Enter:
     - AWS Access Key ID
     - AWS Secret Access Key
     - Region: `eu-north-1`

2. **Configure Chat Model**:
   - Add "AWS Bedrock Chat" node
   - Select Model: `anthropic.claude-3-5-sonnet-20241022-v2:0`
   - Configure parameters:
     - Temperature: 0.7
     - Max Tokens: 2048
     - Top P: 0.9

3. **Connect to Chat Flow**:
   ```
   [Document Loader] → [Text Splitter] → [Embeddings] → [Vector Store]
                                                              ↓
   [User Input] ─────────────────────────────────→ [AWS Bedrock Chat] → [Output]
   ```

### Bedrock Models in Flowise (Supported)

| Model ID | Flowise Display Name | Use Case |
|----------|---------------------|----------|
| `anthropic.claude-3-5-sonnet-20241022-v2:0` | Claude 3.5 Sonnet | General purpose |
| `anthropic.claude-3-haiku-20240307-v1:0` | Claude 3 Haiku | Fast responses |
| `amazon.titan-text-premier-v1:0` | Titan Text Premier | Cost-effective |
| `meta.llama3-1-70b-instruct-v1:0` | Llama 3.1 70B | Open source option |

### RAG Configuration with Bedrock Knowledge Bases

**Advanced Pattern**: Use Bedrock Knowledge Bases instead of Flowise vector stores

```text
[Document Loader] → Upload to S3
                         ↓
              Bedrock Knowledge Base (auto-sync)
                         ↓
[User Query] → RetrieveAndGenerate API → [Claude 3.5 Sonnet] → [Response]
```

**Advantage**: Automatic embedding generation, managed vector store, no Flowise infrastructure.

---

## 5. Claude 3.5 Sonnet: Bedrock vs Anthropic API

### Feature Comparison

| Feature | AWS Bedrock | Anthropic Direct API |
|---------|-------------|---------------------|
| **Pricing** | $3/$15 per 1M tokens | $3/$15 per 1M tokens |
| **Latency** | +100-200ms overhead | Direct connection |
| **Rate Limits** | 10,000 RPM (enterprise) | 5,000 RPM (standard) |
| **Context Window** | 200K tokens | 200K tokens |
| **Billing** | Unified AWS bill | Separate Anthropic bill |
| **Compliance** | AWS SOC2/HIPAA/GDPR | Anthropic compliance docs |
| **Streaming** | ✅ Supported | ✅ Supported |
| **Function Calling** | ✅ Supported | ✅ Supported |
| **Vision** | ✅ Supported | ✅ Supported |
| **Regional Data** | Stays in eu-north-1 | Routed to Anthropic US |

### When to Use Bedrock

✅ **Use AWS Bedrock when**:
- You want unified AWS billing
- You need higher rate limits (enterprise workloads)
- You require data residency in EU (GDPR)
- You want to use Bedrock Knowledge Bases
- You're already on AWS infrastructure

### When to Use Direct Anthropic API

✅ **Use Anthropic Direct when**:
- You need lowest possible latency (100-200ms matters)
- You want to avoid AWS account complexity
- You're multi-cloud (not AWS-centric)
- You want direct access to newest Claude features first

---

## 6. Bedrock Knowledge Bases for RAG Applications

### Architecture

```text
Data Sources (S3, Confluence, Salesforce, Web Crawlers)
                    ↓
      Bedrock Knowledge Base (Managed)
        ├─ Auto-chunking
        ├─ Embeddings (Titan Embeddings G1)
        └─ Vector Store (OpenSearch Serverless)
                    ↓
      RetrieveAndGenerate API
                    ↓
      Claude 3.5 Sonnet (Generation)
```

### Use Cases for Ziggie Cloud

| Use Case | Knowledge Base Source | LLM |
|----------|----------------------|-----|
| **AI Instructor Scripts** | S3 bucket with workout templates | Claude 3.5 Sonnet |
| **Game Narrative** | Lore documents in Confluence | Claude 3.5 Sonnet |
| **Code Generation** | GitHub repo documentation | Claude 3.5 Sonnet |
| **Customer Support** | FAQ + support tickets | Claude 3 Haiku |

### Setup Example: AI Instructor Knowledge Base

```bash
# 1. Upload data to S3
aws s3 sync ./workout-templates s3://ziggie-kb-workout-templates --region eu-north-1

# 2. Create Knowledge Base (via Console or CLI)
aws bedrock-agent create-knowledge-base \
  --name "AI-Instructor-Workouts" \
  --role-arn "arn:aws:iam::ACCOUNT_ID:role/BedrockKBRole" \
  --knowledge-base-configuration '{
    "type": "VECTOR",
    "vectorKnowledgeBaseConfiguration": {
      "embeddingModelArn": "arn:aws:bedrock:eu-north-1::foundation-model/amazon.titan-embed-text-v1"
    }
  }' \
  --storage-configuration '{
    "type": "OPENSEARCH_SERVERLESS",
    "opensearchServerlessConfiguration": {
      "collectionArn": "arn:aws:aoss:eu-north-1:ACCOUNT_ID:collection/xyz",
      "vectorIndexName": "workout-index",
      "fieldMapping": {
        "vectorField": "embedding",
        "textField": "text",
        "metadataField": "metadata"
      }
    }
  }' \
  --region eu-north-1

# 3. Create Data Source
aws bedrock-agent create-data-source \
  --knowledge-base-id "KB_ID" \
  --name "S3-Workout-Templates" \
  --data-source-configuration '{
    "type": "S3",
    "s3Configuration": {
      "bucketArn": "arn:aws:s3:::ziggie-kb-workout-templates"
    }
  }' \
  --region eu-north-1

# 4. Sync data
aws bedrock-agent start-ingestion-job \
  --knowledge-base-id "KB_ID" \
  --data-source-id "DS_ID" \
  --region eu-north-1
```

### Querying Knowledge Base

```python
import boto3

bedrock = boto3.client('bedrock-agent-runtime', region_name='eu-north-1')

response = bedrock.retrieve_and_generate(
    input={'text': 'Create a 30-minute HIIT workout for beginners'},
    retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
            'knowledgeBaseId': 'KB_ID',
            'modelArn': 'arn:aws:bedrock:eu-north-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0',
            'retrievalConfiguration': {
                'vectorSearchConfiguration': {
                    'numberOfResults': 5
                }
            }
        }
    }
)

print(response['output']['text'])
```

### Pricing for Knowledge Bases

| Component | Cost |
|-----------|------|
| **Storage** | OpenSearch Serverless: $0.24/OCU-hour + $0.024/GB-month |
| **Embeddings** | Titan Embeddings: $0.10/1M tokens |
| **Retrieval** | $0.00001 per query |
| **Generation** | Standard model pricing (e.g., Claude 3.5 Sonnet) |

**Example**: 10GB knowledge base, 10K queries/month
- Storage: ~$25/month (1 OCU + 10GB)
- Embeddings: One-time $0.50 (5M tokens)
- Retrieval: $0.10/month
- Generation: $6.68/month (from earlier estimate)
- **Total**: ~$32/month

---

## 7. IAM Setup for Bedrock Access

### IAM Policy for n8n/Flowise

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockInference",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:eu-north-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
        "arn:aws:bedrock:eu-north-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
        "arn:aws:bedrock:eu-north-1::foundation-model/amazon.titan-text-premier-v1:0"
      ]
    },
    {
      "Sid": "BedrockKnowledgeBase",
      "Effect": "Allow",
      "Action": [
        "bedrock:Retrieve",
        "bedrock:RetrieveAndGenerate"
      ],
      "Resource": "arn:aws:bedrock:eu-north-1:ACCOUNT_ID:knowledge-base/*"
    }
  ]
}
```

### IAM User Setup for n8n

```bash
# 1. Create IAM user
aws iam create-user --user-name n8n-bedrock-user

# 2. Attach policy
aws iam put-user-policy \
  --user-name n8n-bedrock-user \
  --policy-name BedrockAccess \
  --policy-document file://bedrock-policy.json

# 3. Create access key
aws iam create-access-key --user-name n8n-bedrock-user
```

### Security Best Practices

1. **Least Privilege**: Only grant access to models you use
2. **Rotate Keys**: Rotate access keys every 90 days
3. **Use Secrets Manager**: Store keys in AWS Secrets Manager, not env vars
4. **Enable CloudTrail**: Log all Bedrock API calls for audit
5. **Cost Alerts**: Set up billing alarms for unexpected usage

---

## 8. Example API Calls Using AWS SDK

### Python Example: Claude 3.5 Sonnet

```python
import boto3
import json

# Initialize client
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name='eu-north-1'
)

# Prepare request
model_id = 'anthropic.claude-3-5-sonnet-20241022-v2:0'
prompt = "Generate a 5-minute warmup script for a fitness class"

body = json.dumps({
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1000,
    "temperature": 0.7,
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ]
})

# Invoke model
response = bedrock.invoke_model(
    modelId=model_id,
    body=body
)

# Parse response
response_body = json.loads(response['body'].read())
completion = response_body['content'][0]['text']

print(completion)
```

### Node.js Example: Streaming Response

```javascript
import { BedrockRuntimeClient, InvokeModelWithResponseStreamCommand } from "@aws-sdk/client-bedrock-runtime";

const client = new BedrockRuntimeClient({ region: "eu-north-1" });

const modelId = "anthropic.claude-3-5-sonnet-20241022-v2:0";
const prompt = "Create a game narrative for a fantasy RPG";

const input = {
  modelId: modelId,
  contentType: "application/json",
  accept: "application/json",
  body: JSON.stringify({
    anthropic_version: "bedrock-2023-05-31",
    max_tokens: 2000,
    messages: [
      {
        role: "user",
        content: prompt
      }
    ]
  })
};

const command = new InvokeModelWithResponseStreamCommand(input);
const response = await client.send(command);

// Stream response
for await (const event of response.body) {
  if (event.chunk) {
    const chunk = JSON.parse(new TextDecoder().decode(event.chunk.bytes));
    if (chunk.type === 'content_block_delta') {
      process.stdout.write(chunk.delta.text);
    }
  }
}
```

### cURL Example: Titan Text Express

```bash
aws bedrock-runtime invoke-model \
  --region eu-north-1 \
  --model-id amazon.titan-text-express-v1 \
  --body '{"inputText":"Summarize this workout session","textGenerationConfig":{"maxTokenCount":512,"temperature":0.5}}' \
  --cli-binary-format raw-in-base64-out \
  output.json

cat output.json | jq -r '.results[0].outputText'
```

---

## 9. Migration Strategy from OpenAI to Bedrock

### Phase 1: Parallel Testing (Week 1-2)

1. **Setup**: Create Bedrock IAM user, configure n8n credentials
2. **Test**: Run 10% of Flowise chatbot traffic through Claude 3 Haiku
3. **Monitor**: Compare latency, quality, cost
4. **Adjust**: Fine-tune prompts for Claude if needed

### Phase 2: Gradual Migration (Week 3-4)

| Workload | Current | Target | Reason |
|----------|---------|--------|--------|
| AI Instructor Scripts | GPT-4 | Claude 3.5 Sonnet | 50% cost reduction |
| Simple Chatbots | GPT-3.5 Turbo | Claude 3 Haiku | 60% cost reduction |
| Code Generation | GPT-4 | Claude 3.5 Sonnet | Better code quality |
| Game Narrative | GPT-4 | Claude 3.5 Sonnet | Creative writing strength |

### Phase 3: Optimization (Week 5-6)

1. **Model Tiering**: Route simple queries to Haiku, complex to Sonnet
2. **Knowledge Bases**: Migrate Flowise RAG to Bedrock Knowledge Bases
3. **Monitoring**: Set up CloudWatch dashboards for token usage
4. **Cost Analysis**: Compare actual vs projected savings

### Rollback Plan

Keep OpenAI credentials active for 30 days. If Bedrock fails:
1. Switch n8n workflows back to OpenAI nodes
2. Revert Flowise LLM providers to OpenAI
3. Document failure reasons for future retry

---

## 10. Recommended Architecture for Ziggie Cloud

### Hybrid Multi-Model Strategy

```text
User Request
     ↓
n8n Workflow (Router)
     ├─→ Complex Reasoning → Bedrock: Claude 3.5 Sonnet
     ├─→ Simple Chat → Bedrock: Claude 3 Haiku
     ├─→ Code Generation → Bedrock: Claude 3.5 Sonnet
     ├─→ Image Generation → OpenAI: DALL-E 3 (Bedrock doesn't have)
     └─→ Embedding → Bedrock: Titan Embeddings G1
     ↓
Response
```

### Cost Optimization Rules

1. **Use Haiku First**: Try Claude 3 Haiku ($0.25/$1.25) for all new tasks
2. **Upgrade on Demand**: If quality insufficient, escalate to Sonnet
3. **Avoid Opus**: Reserve for critical research tasks only ($15/$75)
4. **Cache Prompts**: Use Bedrock prompt caching for repeated system prompts (50% discount)

### Monitoring & Alerts

```bash
# CloudWatch Alarm: Monthly cost exceeds $50
aws cloudwatch put-metric-alarm \
  --alarm-name bedrock-monthly-cost \
  --alarm-description "Alert if Bedrock costs exceed $50/month" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 86400 \
  --evaluation-periods 1 \
  --threshold 50 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=ServiceName,Value=AmazonBedrock
```

---

## 11. Action Items

### Immediate (Week 1)

- [ ] Enable Bedrock model access in AWS Console (eu-north-1)
- [ ] Create IAM user `n8n-bedrock-user` with policy from Section 7
- [ ] Add AWS Bedrock credentials to n8n
- [ ] Test Claude 3 Haiku with sample Flowise chatbot
- [ ] Compare response quality vs GPT-3.5 Turbo

### Short-term (Week 2-4)

- [ ] Migrate 1 Flowise chatbot to Bedrock Claude 3 Haiku
- [ ] Create n8n workflow for AI instructor script generation (Claude 3.5 Sonnet)
- [ ] Set up CloudWatch cost monitoring
- [ ] Document prompt adjustments needed for Claude vs GPT-4

### Long-term (Month 2-3)

- [ ] Evaluate Bedrock Knowledge Bases for game narrative RAG
- [ ] Migrate all Flowise chatbots to Bedrock
- [ ] Implement multi-model routing in n8n (Haiku → Sonnet escalation)
- [ ] Retire OpenAI API keys (keep emergency backup)

---

## 12. Key Takeaways

### Pros of AWS Bedrock

✅ **Cost**: 50-70% savings vs GPT-4 using Claude 3.5 Sonnet
✅ **Choice**: Multiple models (Claude, Llama, Titan) for different tasks
✅ **Integration**: Native n8n/Flowise support, unified AWS billing
✅ **Compliance**: EU data residency, AWS SOC2/HIPAA certification
✅ **Scalability**: Managed service, auto-scaling, high rate limits

### Cons of AWS Bedrock

❌ **Latency**: 100-200ms overhead vs direct API calls
❌ **Complexity**: AWS IAM setup, region verification required
❌ **Image Generation**: No DALL-E equivalent (keep OpenAI for images)
❌ **Newer Features**: Anthropic API gets Claude updates first

### Final Recommendation

**Adopt Bedrock for text generation workloads, keep OpenAI for image generation.**

**Migration Priority**:
1. AI Instructor Scripts (GPT-4 → Claude 3.5 Sonnet): Highest savings
2. Flowise Chatbots (GPT-3.5 → Claude 3 Haiku): High volume, 60% savings
3. Code Generation (GPT-4 → Claude 3.5 Sonnet): Better quality + cost savings
4. Game Narrative (GPT-4 → Claude 3.5 Sonnet): Claude excels at creative writing

**Estimated Annual Savings**: $288/year (based on 1M tokens/month)

---

## References

- AWS Bedrock Documentation: https://docs.aws.amazon.com/bedrock/
- Claude Model Pricing: https://aws.amazon.com/bedrock/pricing/
- n8n AWS Bedrock Integration: https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-base.awsbedrock/
- Flowise AWS Bedrock: https://docs.flowiseai.com/integrations/langchain/chat-models/aws-bedrock

---

*Research compiled for Ziggie Cloud ecosystem evaluation*
*Target: Reduce LLM vendor lock-in, optimize costs, maintain EU compliance*
