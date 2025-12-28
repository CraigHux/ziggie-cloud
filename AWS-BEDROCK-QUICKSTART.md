# AWS Bedrock Quick Start Guide - Ziggie Cloud

> **Fast implementation guide for integrating AWS Bedrock into existing n8n + Flowise setup**

---

## 1. Enable Bedrock Access (5 minutes)

```bash
# Login to AWS Console
# Navigate to: Bedrock → Model Access (eu-north-1)
# Enable these models:
- Anthropic Claude 3.5 Sonnet v2
- Anthropic Claude 3 Haiku
- Amazon Titan Text Express
- Amazon Titan Embeddings G1
```

**Note**: Model access approval is instant for most models.

---

## 2. Create IAM User for n8n/Flowise (10 minutes)

### Create Policy

Save as `bedrock-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:eu-north-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
        "arn:aws:bedrock:eu-north-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
        "arn:aws:bedrock:eu-north-1::foundation-model/amazon.titan-text-express-v1"
      ]
    }
  ]
}
```

### Create User

```bash
# Create IAM user
aws iam create-user --user-name n8n-bedrock-user

# Attach policy
aws iam put-user-policy \
  --user-name n8n-bedrock-user \
  --policy-name BedrockInvokeAccess \
  --policy-document file://bedrock-policy.json

# Generate access key
aws iam create-access-key --user-name n8n-bedrock-user
```

**Save the Access Key ID and Secret Access Key** - you'll need them next.

---

## 3. Configure n8n (15 minutes)

### Add AWS Credentials

1. Open n8n UI → Settings → Credentials
2. Click "Add Credential" → Search "AWS"
3. Select "AWS API"
4. Fill in:
   - **Access Key ID**: (from step 2)
   - **Secret Access Key**: (from step 2)
   - **Region**: `eu-north-1`
5. Save as "AWS Bedrock"

### Create Test Workflow

```json
{
  "nodes": [
    {
      "name": "Manual Trigger",
      "type": "n8n-nodes-base.manualTrigger",
      "position": [250, 300]
    },
    {
      "name": "AWS Bedrock",
      "type": "n8n-nodes-base.awsBedrock",
      "position": [450, 300],
      "parameters": {
        "resource": "text",
        "operation": "message",
        "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
        "prompt": "Write a 30-second warmup instruction for a fitness class",
        "maxTokens": 500,
        "temperature": 0.7
      },
      "credentials": {
        "awsApi": {
          "id": "1",
          "name": "AWS Bedrock"
        }
      }
    }
  ],
  "connections": {
    "Manual Trigger": {
      "main": [[{"node": "AWS Bedrock", "type": "main", "index": 0}]]
    }
  }
}
```

**Test**: Execute manually, verify response.

---

## 4. Configure Flowise (10 minutes)

### Add AWS Bedrock Chat Model

1. Open Flowise UI
2. Go to Credentials → Add New Credential
3. Select "AWS Bedrock API"
4. Fill in:
   - **AWS Access Key ID**: (from step 2)
   - **AWS Secret Access Key**: (from step 2)
   - **Region**: `eu-north-1`
5. Save as "Bedrock-EU-North"

### Create Test Chatbot

1. Create new chatflow
2. Add nodes:
   - **Chat Model**: AWS Bedrock Chat
     - Model: `anthropic.claude-3-haiku-20240307-v1:0`
     - Temperature: 0.7
     - Max Tokens: 1024
     - Credentials: Bedrock-EU-North
   - **Memory**: Buffer Memory
   - **Chain**: Conversation Chain
3. Connect: Memory → Chain ← Chat Model
4. Test with: "Hello, how are you?"

---

## 5. Model Selection Guide

### Quick Decision Matrix

| Use Case | Model | Cost/1M tokens | Reason |
|----------|-------|----------------|--------|
| **Simple chatbot** | Claude 3 Haiku | $0.25 / $1.25 | Fastest, cheapest |
| **AI instructor scripts** | Claude 3.5 Sonnet | $3.00 / $15.00 | Best quality/cost ratio |
| **Code generation** | Claude 3.5 Sonnet | $3.00 / $15.00 | Excellent at code |
| **Game narrative** | Claude 3.5 Sonnet | $3.00 / $15.00 | Creative writing |
| **Summarization** | Titan Text Express | $0.20 / $0.60 | Ultra-cheap |

### Model IDs for Copy-Paste

```text
Claude 3.5 Sonnet v2:  anthropic.claude-3-5-sonnet-20241022-v2:0
Claude 3 Haiku:        anthropic.claude-3-haiku-20240307-v1:0
Titan Text Express:    amazon.titan-text-express-v1
Titan Text Premier:    amazon.titan-text-premier-v1:0
Llama 3.1 70B:         meta.llama3-1-70b-instruct-v1:0
```

---

## 6. Python SDK Example (5 minutes)

### Install SDK

```bash
pip install boto3
```

### Simple Script

```python
import boto3
import json

# Initialize
bedrock = boto3.client('bedrock-runtime', region_name='eu-north-1')

# Define prompt
prompt = "Generate a 5-minute HIIT workout description"

# Call Claude 3 Haiku
response = bedrock.invoke_model(
    modelId='anthropic.claude-3-haiku-20240307-v1:0',
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.7,
        "messages": [{"role": "user", "content": prompt}]
    })
)

# Parse response
result = json.loads(response['body'].read())
print(result['content'][0]['text'])
```

**Run**: `python test_bedrock.py`

---

## 7. Cost Monitoring Setup (5 minutes)

### Enable Cost Alerts

```bash
# Create billing alarm for $50/month threshold
aws cloudwatch put-metric-alarm \
  --alarm-name bedrock-cost-alert \
  --alarm-description "Alert if Bedrock monthly cost exceeds $50" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 86400 \
  --evaluation-periods 1 \
  --threshold 50 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=ServiceName,Value=AmazonBedrock \
  --region us-east-1
```

**Note**: Billing metrics only available in `us-east-1` region.

### View Current Costs

```bash
# Check current month Bedrock costs
aws ce get-cost-and-usage \
  --time-period Start=$(date -d "$(date +%Y-%m-01)" +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --filter file://bedrock-filter.json
```

`bedrock-filter.json`:
```json
{
  "Dimensions": {
    "Key": "SERVICE",
    "Values": ["Amazon Bedrock"]
  }
}
```

---

## 8. Migration Checklist

### Week 1: Testing

- [ ] Enable Bedrock model access in eu-north-1
- [ ] Create IAM user with credentials
- [ ] Test Claude 3 Haiku in n8n (sample workflow)
- [ ] Test Claude 3 Haiku in Flowise (sample chatbot)
- [ ] Compare quality vs current GPT-3.5 Turbo

### Week 2: Single Workload Migration

- [ ] Choose 1 low-risk chatbot to migrate
- [ ] Update Flowise chatflow to use Bedrock
- [ ] Run parallel A/B test (50% Bedrock, 50% OpenAI)
- [ ] Monitor latency and user satisfaction
- [ ] Document any prompt adjustments needed

### Week 3-4: Gradual Rollout

- [ ] Migrate AI instructor script generation (n8n → Claude 3.5 Sonnet)
- [ ] Migrate remaining chatbots (Flowise → Claude 3 Haiku)
- [ ] Update code generation workflows (n8n → Claude 3.5 Sonnet)
- [ ] Keep OpenAI for image generation (DALL-E)

### Week 5: Optimization

- [ ] Implement multi-model routing (Haiku for simple, Sonnet for complex)
- [ ] Set up CloudWatch dashboards for token usage
- [ ] Calculate actual cost savings
- [ ] Document lessons learned

---

## 9. Troubleshooting

### Issue: "Access Denied" when invoking model

**Solution**:
1. Verify model access enabled in Bedrock Console (eu-north-1)
2. Check IAM policy includes correct model ARN
3. Confirm credentials are for correct AWS account

### Issue: High latency (>5 seconds)

**Solution**:
1. Check region - ensure using `eu-north-1` (not us-east-1)
2. Use streaming for long responses
3. Consider Claude 3 Haiku for speed-critical tasks

### Issue: Unexpected costs

**Solution**:
1. Check CloudWatch for token usage by model
2. Verify max_tokens settings (cap at 1000 for chatbots)
3. Review if using Opus ($15/$75) when Sonnet ($3/$15) would work

---

## 10. Quick Reference Commands

```bash
# Test Bedrock access
aws bedrock list-foundation-models --region eu-north-1

# Invoke model via CLI
aws bedrock-runtime invoke-model \
  --model-id anthropic.claude-3-haiku-20240307-v1:0 \
  --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":1024,"messages":[{"role":"user","content":"Hello"}]}' \
  --region eu-north-1 \
  output.json

# View response
cat output.json | jq -r '.content[0].text'

# Check current costs
aws ce get-cost-and-usage \
  --time-period Start=2025-12-01,End=2025-12-23 \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["Amazon Bedrock"]}}'
```

---

## Support Resources

- **AWS Bedrock Docs**: https://docs.aws.amazon.com/bedrock/
- **n8n Bedrock Node**: https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-base.awsbedrock/
- **Flowise AWS Setup**: https://docs.flowiseai.com/integrations/langchain/chat-models/aws-bedrock
- **Anthropic Claude Docs**: https://docs.anthropic.com/claude/reference/bedrock

---

**Total Setup Time**: ~50 minutes

**Expected Savings**: 50-70% vs OpenAI GPT-4 for equivalent workloads
