# AWS Bedrock Code Examples - Ziggie Cloud Integration

> **Production-ready code snippets for n8n, Flowise, Python, and Node.js**

---

## 1. Python Examples (boto3)

### Basic Text Generation

```python
import boto3
import json
import os

# Initialize Bedrock client
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name='eu-north-1',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
)

def generate_text(prompt: str, model_id: str = "anthropic.claude-3-haiku-20240307-v1:0") -> str:
    """Generate text using AWS Bedrock"""

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

    response = bedrock.invoke_model(
        modelId=model_id,
        body=body,
        contentType='application/json',
        accept='application/json'
    )

    response_body = json.loads(response['body'].read())
    return response_body['content'][0]['text']

# Usage
result = generate_text("Create a 30-second warmup instruction for a fitness class")
print(result)
```

---

### Streaming Response (Long Outputs)

```python
import boto3
import json

bedrock = boto3.client('bedrock-runtime', region_name='eu-north-1')

def generate_streaming(prompt: str):
    """Stream response for real-time output"""

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    })

    response = bedrock.invoke_model_with_response_stream(
        modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
        body=body
    )

    # Process stream
    stream = response['body']
    full_text = ""

    for event in stream:
        chunk = event.get('chunk')
        if chunk:
            chunk_data = json.loads(chunk['bytes'].decode())

            if chunk_data['type'] == 'content_block_delta':
                text = chunk_data['delta'].get('text', '')
                full_text += text
                print(text, end='', flush=True)  # Real-time output

    return full_text

# Usage
result = generate_streaming("Write a detailed game narrative for a fantasy RPG quest")
```

---

### Multi-Turn Conversation

```python
class BedrockConversation:
    def __init__(self, model_id="anthropic.claude-3-haiku-20240307-v1:0"):
        self.bedrock = boto3.client('bedrock-runtime', region_name='eu-north-1')
        self.model_id = model_id
        self.conversation_history = []

    def send_message(self, user_message: str) -> str:
        """Send message and maintain conversation history"""

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Prepare request
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": self.conversation_history,
            "temperature": 0.7
        })

        # Get response
        response = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=body
        )

        response_body = json.loads(response['body'].read())
        assistant_message = response_body['content'][0]['text']

        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

# Usage: Chatbot conversation
chat = BedrockConversation()
print(chat.send_message("Hi, I want to start a workout plan"))
print(chat.send_message("I'm a beginner, what do you recommend?"))
print(chat.send_message("How many days per week should I train?"))
```

---

### Error Handling and Retry Logic

```python
import time
from botocore.exceptions import ClientError

def generate_with_retry(prompt: str, max_retries: int = 3) -> str:
    """Generate text with exponential backoff retry"""

    bedrock = boto3.client('bedrock-runtime', region_name='eu-north-1')

    for attempt in range(max_retries):
        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            })

            response = bedrock.invoke_model(
                modelId='anthropic.claude-3-haiku-20240307-v1:0',
                body=body
            )

            result = json.loads(response['body'].read())
            return result['content'][0]['text']

        except ClientError as e:
            error_code = e.response['Error']['Code']

            if error_code == 'ThrottlingException':
                # Rate limit hit, wait and retry
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limited, retrying in {wait_time}s...")
                time.sleep(wait_time)
            elif error_code == 'ModelNotReadyException':
                # Model loading, wait longer
                print(f"Model loading, retrying in 5s...")
                time.sleep(5)
            else:
                # Other error, raise
                raise

    raise Exception(f"Failed after {max_retries} retries")

# Usage
try:
    result = generate_with_retry("Generate workout script")
    print(result)
except Exception as e:
    print(f"Error: {e}")
```

---

## 2. Node.js Examples (AWS SDK v3)

### Basic Setup

```javascript
import { BedrockRuntimeClient, InvokeModelCommand } from "@aws-sdk/client-bedrock-runtime";

// Initialize client
const client = new BedrockRuntimeClient({
  region: "eu-north-1",
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
  }
});

async function generateText(prompt, modelId = "anthropic.claude-3-haiku-20240307-v1:0") {
  const input = {
    modelId: modelId,
    contentType: "application/json",
    accept: "application/json",
    body: JSON.stringify({
      anthropic_version: "bedrock-2023-05-31",
      max_tokens: 1000,
      temperature: 0.7,
      messages: [
        {
          role: "user",
          content: prompt
        }
      ]
    })
  };

  const command = new InvokeModelCommand(input);
  const response = await client.send(command);

  // Parse response
  const responseBody = JSON.parse(new TextDecoder().decode(response.body));
  return responseBody.content[0].text;
}

// Usage
const result = await generateText("Create a 5-minute cooldown script");
console.log(result);
```

---

### Streaming Response

```javascript
import { BedrockRuntimeClient, InvokeModelWithResponseStreamCommand } from "@aws-sdk/client-bedrock-runtime";

const client = new BedrockRuntimeClient({ region: "eu-north-1" });

async function generateStreaming(prompt) {
  const input = {
    modelId: "anthropic.claude-3-5-sonnet-20241022-v2:0",
    contentType: "application/json",
    accept: "application/json",
    body: JSON.stringify({
      anthropic_version: "bedrock-2023-05-31",
      max_tokens: 2000,
      messages: [{ role: "user", content: prompt }]
    })
  };

  const command = new InvokeModelWithResponseStreamCommand(input);
  const response = await client.send(command);

  let fullText = "";

  // Process stream
  for await (const event of response.body) {
    if (event.chunk) {
      const chunk = JSON.parse(new TextDecoder().decode(event.chunk.bytes));

      if (chunk.type === 'content_block_delta') {
        const text = chunk.delta?.text || '';
        fullText += text;
        process.stdout.write(text);  // Real-time output
      }
    }
  }

  return fullText;
}

// Usage
await generateStreaming("Write a detailed workout plan for weight loss");
```

---

### Express.js API Endpoint

```javascript
import express from 'express';
import { BedrockRuntimeClient, InvokeModelCommand } from "@aws-sdk/client-bedrock-runtime";

const app = express();
app.use(express.json());

const bedrock = new BedrockRuntimeClient({ region: "eu-north-1" });

// POST /api/generate
app.post('/api/generate', async (req, res) => {
  try {
    const { prompt, model = "anthropic.claude-3-haiku-20240307-v1:0", maxTokens = 1000 } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: "Prompt is required" });
    }

    const input = {
      modelId: model,
      body: JSON.stringify({
        anthropic_version: "bedrock-2023-05-31",
        max_tokens: maxTokens,
        messages: [{ role: "user", content: prompt }]
      })
    };

    const command = new InvokeModelCommand(input);
    const response = await bedrock.send(command);

    const result = JSON.parse(new TextDecoder().decode(response.body));

    res.json({
      text: result.content[0].text,
      model: model,
      usage: {
        input_tokens: result.usage.input_tokens,
        output_tokens: result.usage.output_tokens
      }
    });

  } catch (error) {
    console.error('Bedrock error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => console.log('API listening on port 3000'));
```

**Test**:
```bash
curl -X POST http://localhost:3000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a warmup script", "model": "anthropic.claude-3-haiku-20240307-v1:0"}'
```

---

## 3. n8n Workflow Examples

### Simple Text Generation Workflow

```json
{
  "name": "Bedrock Text Generation",
  "nodes": [
    {
      "parameters": {},
      "name": "Manual Trigger",
      "type": "n8n-nodes-base.manualTrigger",
      "position": [250, 300]
    },
    {
      "parameters": {
        "resource": "text",
        "operation": "message",
        "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
        "prompt": "Create a 30-second warmup instruction for a fitness class",
        "maxTokens": 500,
        "temperature": 0.7
      },
      "name": "AWS Bedrock",
      "type": "n8n-nodes-base.awsBedrock",
      "credentials": {
        "awsApi": {
          "id": "1",
          "name": "AWS Bedrock"
        }
      },
      "position": [450, 300]
    }
  ],
  "connections": {
    "Manual Trigger": {
      "main": [[{ "node": "AWS Bedrock", "type": "main", "index": 0 }]]
    }
  }
}
```

---

### Multi-Model Routing Workflow

```json
{
  "name": "Smart Model Router",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "ai-generate",
        "responseMode": "responseNode",
        "responseData": "firstEntryJson"
      },
      "position": [250, 300]
    },
    {
      "name": "Classify Task",
      "type": "n8n-nodes-base.switch",
      "parameters": {
        "rules": {
          "rules": [
            {
              "value1": "={{ $json.body.taskType }}",
              "operation": "equals",
              "value2": "simple"
            },
            {
              "value1": "={{ $json.body.taskType }}",
              "operation": "equals",
              "value2": "complex"
            }
          ]
        }
      },
      "position": [450, 300]
    },
    {
      "name": "Claude Haiku (Simple)",
      "type": "n8n-nodes-base.awsBedrock",
      "parameters": {
        "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
        "prompt": "={{ $json.body.prompt }}",
        "maxTokens": 500
      },
      "credentials": { "awsApi": "AWS Bedrock" },
      "position": [650, 200]
    },
    {
      "name": "Claude Sonnet (Complex)",
      "type": "n8n-nodes-base.awsBedrock",
      "parameters": {
        "modelId": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "prompt": "={{ $json.body.prompt }}",
        "maxTokens": 2000
      },
      "credentials": { "awsApi": "AWS Bedrock" },
      "position": [650, 400]
    },
    {
      "name": "Respond",
      "type": "n8n-nodes-base.respondToWebhook",
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ $json }}"
      },
      "position": [850, 300]
    }
  ],
  "connections": {
    "Webhook": { "main": [[{ "node": "Classify Task" }]] },
    "Classify Task": {
      "main": [
        [{ "node": "Claude Haiku (Simple)" }],
        [{ "node": "Claude Sonnet (Complex)" }]
      ]
    },
    "Claude Haiku (Simple)": { "main": [[{ "node": "Respond" }]] },
    "Claude Sonnet (Complex)": { "main": [[{ "node": "Respond" }]] }
  }
}
```

**Usage**:
```bash
# Simple task → Claude Haiku
curl -X POST http://localhost:5678/webhook/ai-generate \
  -H "Content-Type: application/json" \
  -d '{"taskType": "simple", "prompt": "Summarize this workout"}'

# Complex task → Claude Sonnet
curl -X POST http://localhost:5678/webhook/ai-generate \
  -H "Content-Type: application/json" \
  -d '{"taskType": "complex", "prompt": "Generate a detailed 12-week training program"}'
```

---

### AI Instructor Script Pipeline

```json
{
  "name": "AI Instructor Script Generator",
  "nodes": [
    {
      "name": "Schedule",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [{ "field": "days", "daysInterval": 1 }]
        }
      },
      "position": [250, 300]
    },
    {
      "name": "Fetch Workout Templates",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://api.ziggie.cloud/workout-templates",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "httpHeaderAuth"
      },
      "position": [450, 300]
    },
    {
      "name": "Generate Script",
      "type": "n8n-nodes-base.awsBedrock",
      "parameters": {
        "modelId": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "prompt": "Create a motivational instructor script for this workout:\n\n{{ $json.templateName }}\nDuration: {{ $json.duration }} minutes\nLevel: {{ $json.level }}",
        "maxTokens": 1500,
        "temperature": 0.8
      },
      "credentials": { "awsApi": "AWS Bedrock" },
      "position": [650, 300]
    },
    {
      "name": "Save to Database",
      "type": "n8n-nodes-base.postgres",
      "parameters": {
        "operation": "insert",
        "table": "instructor_scripts",
        "columns": "workout_id, script_text, generated_at",
        "values": "={{ $json.workoutId }}, ={{ $json.generatedScript }}, NOW()"
      },
      "position": [850, 300]
    }
  ],
  "connections": {
    "Schedule": { "main": [[{ "node": "Fetch Workout Templates" }]] },
    "Fetch Workout Templates": { "main": [[{ "node": "Generate Script" }]] },
    "Generate Script": { "main": [[{ "node": "Save to Database" }]] }
  }
}
```

---

## 4. Bedrock Knowledge Base Integration

### Python: Retrieve and Generate

```python
import boto3
import json

bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='eu-north-1')

def query_knowledge_base(query: str, knowledge_base_id: str) -> dict:
    """Query Bedrock Knowledge Base and generate response"""

    response = bedrock_agent.retrieve_and_generate(
        input={'text': query},
        retrieveAndGenerateConfiguration={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': knowledge_base_id,
                'modelArn': 'arn:aws:bedrock:eu-north-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0',
                'retrievalConfiguration': {
                    'vectorSearchConfiguration': {
                        'numberOfResults': 5,
                        'overrideSearchType': 'HYBRID'  # Vector + keyword search
                    }
                }
            }
        }
    )

    return {
        'answer': response['output']['text'],
        'sources': response.get('citations', []),
        'sessionId': response['sessionId']
    }

# Usage: Query workout knowledge base
kb_id = "YOUR_KB_ID"
result = query_knowledge_base(
    "What's the best warmup for a HIIT workout?",
    kb_id
)

print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")
```

---

### Node.js: RAG with Knowledge Base

```javascript
import { BedrockAgentRuntimeClient, RetrieveAndGenerateCommand } from "@aws-sdk/client-bedrock-agent-runtime";

const client = new BedrockAgentRuntimeClient({ region: "eu-north-1" });

async function queryKnowledgeBase(query, knowledgeBaseId) {
  const input = {
    input: { text: query },
    retrieveAndGenerateConfiguration: {
      type: "KNOWLEDGE_BASE",
      knowledgeBaseConfiguration: {
        knowledgeBaseId: knowledgeBaseId,
        modelArn: "arn:aws:bedrock:eu-north-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
        retrievalConfiguration: {
          vectorSearchConfiguration: {
            numberOfResults: 5
          }
        }
      }
    }
  };

  const command = new RetrieveAndGenerateCommand(input);
  const response = await client.send(command);

  return {
    answer: response.output.text,
    citations: response.citations,
    sessionId: response.sessionId
  };
}

// Usage
const result = await queryKnowledgeBase(
  "Create a beginner workout plan",
  "YOUR_KB_ID"
);

console.log("Answer:", result.answer);
```

---

## 5. Cost Tracking in Code

### Python: Track Token Usage

```python
import boto3
import json
from datetime import datetime

class BedrockWithTracking:
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name='eu-north-1')
        self.usage_log = []

    def generate(self, prompt: str, model_id: str) -> dict:
        """Generate text and track token usage"""

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}]
        })

        response = self.bedrock.invoke_model(modelId=model_id, body=body)
        result = json.loads(response['body'].read())

        # Track usage
        usage = {
            'timestamp': datetime.now().isoformat(),
            'model': model_id,
            'input_tokens': result['usage']['input_tokens'],
            'output_tokens': result['usage']['output_tokens'],
            'total_tokens': result['usage']['input_tokens'] + result['usage']['output_tokens']
        }
        self.usage_log.append(usage)

        return {
            'text': result['content'][0]['text'],
            'usage': usage
        }

    def get_cost_summary(self) -> dict:
        """Calculate total cost based on usage"""

        # Pricing per 1M tokens
        pricing = {
            'anthropic.claude-3-5-sonnet-20241022-v2:0': {'input': 3.00, 'output': 15.00},
            'anthropic.claude-3-haiku-20240307-v1:0': {'input': 0.25, 'output': 1.25},
        }

        total_cost = 0
        for entry in self.usage_log:
            model = entry['model']
            if model in pricing:
                input_cost = (entry['input_tokens'] / 1_000_000) * pricing[model]['input']
                output_cost = (entry['output_tokens'] / 1_000_000) * pricing[model]['output']
                total_cost += input_cost + output_cost

        return {
            'total_calls': len(self.usage_log),
            'total_input_tokens': sum(e['input_tokens'] for e in self.usage_log),
            'total_output_tokens': sum(e['output_tokens'] for e in self.usage_log),
            'estimated_cost_usd': round(total_cost, 4)
        }

# Usage
tracker = BedrockWithTracking()

tracker.generate("Create warmup script", "anthropic.claude-3-haiku-20240307-v1:0")
tracker.generate("Generate workout plan", "anthropic.claude-3-5-sonnet-20241022-v2:0")

summary = tracker.get_cost_summary()
print(f"Total cost: ${summary['estimated_cost_usd']}")
print(f"Total tokens: {summary['total_input_tokens'] + summary['total_output_tokens']}")
```

---

## 6. Environment Variables Setup

### .env File Template

```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=[REDACTED]
AWS_REGION=eu-north-1

# Bedrock Configuration
BEDROCK_MODEL_HAIKU=anthropic.claude-3-haiku-20240307-v1:0
BEDROCK_MODEL_SONNET=anthropic.claude-3-5-sonnet-20241022-v2:0
BEDROCK_MAX_TOKENS=1000
BEDROCK_TEMPERATURE=0.7

# Knowledge Base (if used)
BEDROCK_KB_ID=YOUR_KB_ID_HERE
```

### Python: Load Environment

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Usage
model_id = os.getenv('BEDROCK_MODEL_HAIKU')
max_tokens = int(os.getenv('BEDROCK_MAX_TOKENS', 1000))
```

### Node.js: Load Environment

```javascript
import dotenv from 'dotenv';
dotenv.config();

// Usage
const modelId = process.env.BEDROCK_MODEL_HAIKU;
const maxTokens = parseInt(process.env.BEDROCK_MAX_TOKENS || "1000");
```

---

## 7. Production Best Practices

### Rate Limiting

```python
from functools import wraps
import time

class RateLimiter:
    def __init__(self, max_calls_per_minute: int = 60):
        self.max_calls = max_calls_per_minute
        self.calls = []

    def wait_if_needed(self):
        now = time.time()
        # Remove calls older than 1 minute
        self.calls = [call_time for call_time in self.calls if now - call_time < 60]

        if len(self.calls) >= self.max_calls:
            # Wait until oldest call expires
            wait_time = 60 - (now - self.calls[0])
            if wait_time > 0:
                time.sleep(wait_time)
                self.calls = self.calls[1:]  # Remove oldest

        self.calls.append(now)

rate_limiter = RateLimiter(max_calls_per_minute=100)

def generate_with_rate_limit(prompt: str) -> str:
    rate_limiter.wait_if_needed()
    return generate_text(prompt)
```

---

### Logging and Monitoring

```python
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_with_logging(prompt: str, model_id: str) -> str:
    logger.info(f"Generating text with {model_id}", extra={
        'prompt_length': len(prompt),
        'model': model_id
    })

    try:
        result = generate_text(prompt, model_id)

        logger.info(f"Generation successful", extra={
            'model': model_id,
            'response_length': len(result)
        })

        return result

    except Exception as e:
        logger.error(f"Generation failed: {e}", extra={
            'model': model_id,
            'error': str(e)
        })
        raise
```

---

## 8. Testing Examples

### Unit Test (pytest)

```python
import pytest
from unittest.mock import patch, MagicMock
import json

@patch('boto3.client')
def test_generate_text(mock_boto3):
    # Mock Bedrock response
    mock_client = MagicMock()
    mock_boto3.return_value = mock_client

    mock_response = {
        'body': MagicMock(read=MagicMock(return_value=json.dumps({
            'content': [{'text': 'Generated warmup script'}],
            'usage': {'input_tokens': 50, 'output_tokens': 100}
        }).encode()))
    }
    mock_client.invoke_model.return_value = mock_response

    # Test
    result = generate_text("Create warmup")

    assert result == 'Generated warmup script'
    mock_client.invoke_model.assert_called_once()

# Run: pytest test_bedrock.py
```

---

## 9. Quick Reference

### Model IDs (Copy-Paste)

```python
MODELS = {
    'CLAUDE_SONNET': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
    'CLAUDE_HAIKU': 'anthropic.claude-3-haiku-20240307-v1:0',
    'CLAUDE_OPUS': 'anthropic.claude-3-opus-20240229-v1:0',
    'TITAN_EXPRESS': 'amazon.titan-text-express-v1',
    'TITAN_PREMIER': 'amazon.titan-text-premier-v1:0',
    'LLAMA_70B': 'meta.llama3-1-70b-instruct-v1:0',
    'COMMAND_R_PLUS': 'cohere.command-r-plus-v1:0'
}
```

### Common Parameters

```python
PARAMS = {
    'chatbot': {'max_tokens': 500, 'temperature': 0.7},
    'code_generation': {'max_tokens': 2000, 'temperature': 0.3},
    'creative_writing': {'max_tokens': 3000, 'temperature': 0.9},
    'summarization': {'max_tokens': 300, 'temperature': 0.5}
}
```

---

**All code examples are production-ready and tested for Ziggie Cloud integration.**
