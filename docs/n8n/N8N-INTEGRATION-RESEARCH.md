# n8n Workflow Integration Research Report

> **Agent**: L1 n8n Workflow Integration Research Agent
> **Date**: 2025-12-28
> **Scope**: Production configuration, security, workflow templates, MCP integration
> **Status**: COMPLETE

---

## Executive Summary

This research document provides comprehensive n8n configuration and integration patterns for the Ziggie AI Game Development ecosystem. The analysis covers existing workflow configurations, production Docker setup, webhook security, custom node development patterns, AI/LLM integrations, and backup/restore procedures.

### Key Findings

| Category | Status | Details |
|----------|--------|---------|
| **Existing Workflows** | 4 workflows | asset-generation, batch-generation, quality-check, meshy-3d |
| **Docker Configuration** | Production-ready | PostgreSQL backend, SSL via nginx, health checks |
| **Security** | Partial | Basic auth enabled, needs API key hardening |
| **AI Integration** | Configured | OpenAI, Anthropic, Ollama, ComfyUI connected |
| **Backup/Restore** | Implemented | CLI and API export, 7/4/3 retention policy |

---

## 1. Existing n8n Workflow Analysis

### 1.1 Asset Generation Pipeline (`asset-generation-pipeline.json`)

**Purpose**: Generate game assets via ComfyUI with S3 upload

**Workflow Structure**:
```
Webhook Trigger → Validate Input → ComfyUI Generate → Wait →
Check Status → Extract Output → Download → Post-Process →
S3 Upload → Build Response → Discord Notify → Webhook Response
```

**Key Features**:
- Input validation for asset_type, prompt, faction_color, output_format
- Enhanced prompts per asset type (unit_sprite, building, terrain_tile, hero, effect, prop)
- Faction color HSV shift mapping (red=0.0, blue=0.55, green=0.33, gold=0.12)
- 120-second ComfyUI timeout
- S3 tagging (asset_type, faction, generated_by)
- Discord webhook notifications

**Configuration**:
- Webhook path: `/generate-asset`
- ComfyUI endpoint: `http://localhost:8188/prompt`
- S3 bucket: `ziggie-assets-prod` (eu-north-1)

### 1.2 Batch Asset Generation (`batch-generation.json`)

**Purpose**: Process multiple asset generation requests in parallel

**Workflow Structure**:
```
Batch Webhook → Validate Batch → Split Assets → Prepare Asset →
Call Generation Pipeline → Collect Result → Aggregate Results →
Build Summary → Should Notify? → Discord Batch Notification → Batch Response
```

**Key Features**:
- Maximum batch size: 50 assets
- Batch interval: 5 seconds between groups of 3
- Success/failure aggregation
- Success rate calculation

**Configuration**:
- Webhook path: `/batch-generate`
- Internal call: `http://localhost:5678/webhook/generate-asset`
- Timeout: 180 seconds per asset

### 1.3 Quality Check Pipeline (`quality-check.json`)

**Purpose**: Validate generated assets against quality thresholds

**Workflow Structure**:
```
Quality Webhook → Validate QC Input → Download Asset →
Analyze Quality → Meets Threshold? → Build Pass/Fail Response →
Merge Responses → QC Response + Discord Notification
```

**Quality Checks**:
- File size (1KB < size < 10MB)
- Format validation (PNG, WebP, JPEG)
- Transparency support check
- Dimensions validation (placeholder for PIL integration)

**Quality Ratings**:
- AAA: 90%+ checks passed
- AA: 75%+ checks passed
- A: 50%+ checks passed
- Poor: <50% checks passed

### 1.4 Meshy Image-to-3D Pipeline (`n8n-workflow-meshy.json`)

**Purpose**: Convert 2D concept art to 3D models via Meshy.ai

**Workflow Structure**:
```
Webhook Trigger → Get Meshy API Key (AWS Secrets) → Parse API Key →
Create Meshy Task → Extract Task ID → Poll Task Status →
Check Complete → Success/Error Response → Download GLB →
Upload to S3 → Respond to Webhook
```

**Key Features**:
- AWS Secrets Manager integration
- 5-second polling interval
- 60 poll maximum (5-minute timeout)
- GLB model download and S3 upload
- Meshy-4 AI model with quad topology

---

## 2. Production Docker Configuration

### 2.1 Current Configuration (`hostinger-vps/docker-compose.yml`)

```yaml
n8n:
  image: n8nio/n8n:latest
  container_name: ziggie-n8n
  restart: unless-stopped
  ports:
    - "5678:5678"
  environment:
    # Authentication
    - N8N_BASIC_AUTH_ACTIVE=true
    - N8N_BASIC_AUTH_USER=${N8N_USER:-admin}
    - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}

    # Host configuration
    - N8N_HOST=${VPS_DOMAIN}
    - N8N_PROTOCOL=https
    - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
    - WEBHOOK_URL=https://${VPS_DOMAIN}/
    - GENERIC_TIMEZONE=Europe/London

    # Database (PostgreSQL backend)
    - DB_TYPE=postgresdb
    - DB_POSTGRESDB_HOST=postgres
    - DB_POSTGRESDB_PORT=5432
    - DB_POSTGRESDB_DATABASE=n8n
    - DB_POSTGRESDB_USER=ziggie
    - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}

    # GitHub OAuth
    - N8N_GITHUB_CLIENT_ID=${GITHUB_CLIENT_ID}
    - N8N_GITHUB_CLIENT_SECRET=${GITHUB_CLIENT_SECRET}

    # AI/LLM API Keys
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
  volumes:
    - n8n_data:/home/node/.n8n
    - ./n8n-workflows:/home/node/.n8n/workflows
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_healthy
```

### 2.2 Recommended Production Enhancements

```yaml
n8n:
  image: n8nio/n8n:1.70.2  # Pin specific version
  container_name: ziggie-n8n
  restart: unless-stopped
  ports:
    - "5678:5678"
  environment:
    # === CORE SETTINGS ===
    - N8N_HOST=${VPS_DOMAIN}
    - N8N_PROTOCOL=https
    - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
    - WEBHOOK_URL=https://${VPS_DOMAIN}/webhook/
    - GENERIC_TIMEZONE=Europe/Stockholm
    - N8N_LOG_LEVEL=info

    # === SECURITY ===
    - N8N_BASIC_AUTH_ACTIVE=true
    - N8N_BASIC_AUTH_USER=${N8N_USER}
    - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
    - N8N_JWT_AUTH_ACTIVE=false
    - N8N_DISABLE_PRODUCTION_MAIN_PROCESS=false

    # === EXECUTION ===
    - EXECUTIONS_MODE=queue  # Use Redis queue for reliability
    - QUEUE_BULL_REDIS_HOST=redis
    - QUEUE_BULL_REDIS_PORT=6379
    - QUEUE_BULL_REDIS_PASSWORD=${REDIS_PASSWORD}
    - EXECUTIONS_DATA_PRUNE=true
    - EXECUTIONS_DATA_MAX_AGE=168  # 7 days
    - EXECUTIONS_DATA_SAVE_ON_ERROR=all
    - EXECUTIONS_DATA_SAVE_ON_SUCCESS=all
    - EXECUTIONS_DATA_SAVE_MANUAL_EXECUTIONS=true

    # === DATABASE ===
    - DB_TYPE=postgresdb
    - DB_POSTGRESDB_HOST=postgres
    - DB_POSTGRESDB_PORT=5432
    - DB_POSTGRESDB_DATABASE=n8n
    - DB_POSTGRESDB_USER=ziggie
    - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
    - DB_POSTGRESDB_SCHEMA=public
    - DB_POSTGRESDB_SSL_ENABLED=false

    # === WEBHOOKS ===
    - N8N_PAYLOAD_SIZE_MAX=50  # MB
    - N8N_METRICS=true
    - N8N_DIAGNOSTICS_ENABLED=false  # Privacy

    # === EXTERNAL CREDENTIALS ===
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    - MESHY_API_KEY=${MESHY_API_KEY}
    - ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}
  volumes:
    - n8n_data:/home/node/.n8n
    - ./n8n-workflows:/home/node/.n8n/workflows:ro  # Read-only mount
    - ./n8n-custom-nodes:/home/node/.n8n/custom:ro
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_healthy
  healthcheck:
    test: ["CMD-SHELL", "curl -f http://localhost:5678/healthz || exit 1"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 30s
  deploy:
    resources:
      limits:
        memory: 2G
        cpus: '2'
      reservations:
        memory: 512M
        cpus: '0.5'
```

### 2.3 Worker Mode Configuration (High-Volume)

For high-volume asset generation, run n8n with separate worker processes:

```yaml
n8n-main:
  image: n8nio/n8n:1.70.2
  container_name: ziggie-n8n-main
  command: n8n start
  environment:
    - EXECUTIONS_MODE=queue
    - EXECUTIONS_PROCESS=main
    # ... other env vars

n8n-worker:
  image: n8nio/n8n:1.70.2
  container_name: ziggie-n8n-worker
  command: n8n worker
  environment:
    - EXECUTIONS_MODE=queue
    - EXECUTIONS_PROCESS=worker
    - QUEUE_HEALTH_CHECK_ACTIVE=true
    # ... other env vars
  deploy:
    replicas: 2  # Scale workers as needed
```

---

## 3. Webhook Security Configuration

### 3.1 Current Security Model

**Implemented**:
- Basic authentication (N8N_BASIC_AUTH_ACTIVE)
- HTTPS via nginx reverse proxy
- Rate limiting (nginx: 10r/s for API, 30r/s general)
- X-Frame-Options, X-Content-Type-Options headers

**Gaps**:
- No webhook-specific authentication tokens
- No IP allowlisting
- No request signing verification

### 3.2 Recommended Security Enhancements

#### 3.2.1 Webhook Authentication Token

Add header-based authentication to workflows:

```javascript
// Validate Input node - add at the beginning
const authHeader = $input.first().json.headers?.['x-webhook-token'];
const expectedToken = $env.WEBHOOK_AUTH_TOKEN;

if (!authHeader || authHeader !== expectedToken) {
  throw new Error('Unauthorized: Invalid or missing webhook token');
}
```

#### 3.2.2 Request Signing (HMAC)

```javascript
// Signature validation for external webhooks
const crypto = require('crypto');

const payload = JSON.stringify($input.first().json.body);
const signature = $input.first().json.headers?.['x-signature-256'];
const secret = $env.WEBHOOK_SIGNING_SECRET;

const expectedSignature = 'sha256=' + crypto
  .createHmac('sha256', secret)
  .update(payload)
  .digest('hex');

if (!crypto.timingSafeEqual(
  Buffer.from(signature || ''),
  Buffer.from(expectedSignature)
)) {
  throw new Error('Invalid request signature');
}
```

#### 3.2.3 IP Allowlisting (nginx)

```nginx
# In nginx.conf - n8n webhook location
location /webhook/ {
    # Allow internal services
    allow 172.28.0.0/16;  # Docker network

    # Allow specific external IPs (e.g., GitHub Actions, trusted services)
    allow 140.82.112.0/20;  # GitHub
    allow 192.30.252.0/22;  # GitHub

    # Deny all others
    deny all;

    proxy_pass http://n8n/webhook/;
    # ... other proxy settings
}
```

#### 3.2.4 Rate Limiting per Webhook

```nginx
# Define per-path rate limiting zones
limit_req_zone $binary_remote_addr zone=webhook_generate:10m rate=5r/s;
limit_req_zone $binary_remote_addr zone=webhook_batch:10m rate=1r/s;
limit_req_zone $binary_remote_addr zone=webhook_qc:10m rate=10r/s;

# Apply to specific webhooks
location /webhook/generate-asset {
    limit_req zone=webhook_generate burst=10 nodelay;
    proxy_pass http://n8n/webhook/generate-asset;
}

location /webhook/batch-generate {
    limit_req zone=webhook_batch burst=3 nodelay;
    proxy_pass http://n8n/webhook/batch-generate;
}

location /webhook/quality-check {
    limit_req zone=webhook_qc burst=20 nodelay;
    proxy_pass http://n8n/webhook/quality-check;
}
```

### 3.3 Environment Variables for Security

Add to `.env`:

```bash
# n8n Webhook Security
WEBHOOK_AUTH_TOKEN=your-secure-random-token-here
WEBHOOK_SIGNING_SECRET=your-hmac-signing-secret-here

# Allowed webhook sources (comma-separated CIDRs)
WEBHOOK_ALLOWED_IPS=172.28.0.0/16,140.82.112.0/20,192.30.252.0/22
```

---

## 4. Custom Node Development Patterns

### 4.1 ComfyUI Integration Node

Create a custom node for ComfyUI integration:

```javascript
// File: n8n-custom-nodes/nodes/ComfyUI/ComfyUI.node.ts

import {
  IExecuteFunctions,
  INodeExecutionData,
  INodeType,
  INodeTypeDescription,
} from 'n8n-workflow';

export class ComfyUI implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'ComfyUI',
    name: 'comfyUI',
    icon: 'file:comfyui.svg',
    group: ['transform'],
    version: 1,
    subtitle: '={{$parameter["operation"]}}',
    description: 'Generate images using ComfyUI',
    defaults: {
      name: 'ComfyUI',
    },
    inputs: ['main'],
    outputs: ['main'],
    credentials: [
      {
        name: 'comfyUIApi',
        required: false,
      },
    ],
    properties: [
      {
        displayName: 'Operation',
        name: 'operation',
        type: 'options',
        noDataExpression: true,
        options: [
          {
            name: 'Generate Image',
            value: 'generate',
            description: 'Generate an image from a prompt',
          },
          {
            name: 'Check Status',
            value: 'status',
            description: 'Check generation status',
          },
          {
            name: 'Get History',
            value: 'history',
            description: 'Get generation history',
          },
          {
            name: 'List Models',
            value: 'models',
            description: 'List available checkpoint models',
          },
        ],
        default: 'generate',
      },
      {
        displayName: 'ComfyUI Host',
        name: 'host',
        type: 'string',
        default: 'http://localhost:8188',
        description: 'ComfyUI server URL',
      },
      {
        displayName: 'Prompt',
        name: 'prompt',
        type: 'string',
        typeOptions: {
          rows: 4,
        },
        default: '',
        displayOptions: {
          show: {
            operation: ['generate'],
          },
        },
      },
      {
        displayName: 'Negative Prompt',
        name: 'negativePrompt',
        type: 'string',
        typeOptions: {
          rows: 2,
        },
        default: 'blurry, low quality, distorted',
        displayOptions: {
          show: {
            operation: ['generate'],
          },
        },
      },
      {
        displayName: 'Width',
        name: 'width',
        type: 'number',
        default: 1024,
        displayOptions: {
          show: {
            operation: ['generate'],
          },
        },
      },
      {
        displayName: 'Height',
        name: 'height',
        type: 'number',
        default: 1024,
        displayOptions: {
          show: {
            operation: ['generate'],
          },
        },
      },
      {
        displayName: 'Checkpoint Model',
        name: 'checkpoint',
        type: 'string',
        default: 'sd_xl_base_1.0.safetensors',
        displayOptions: {
          show: {
            operation: ['generate'],
          },
        },
      },
      {
        displayName: 'Prompt ID',
        name: 'promptId',
        type: 'string',
        default: '',
        displayOptions: {
          show: {
            operation: ['status', 'history'],
          },
        },
      },
    ],
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const items = this.getInputData();
    const returnData: INodeExecutionData[] = [];

    const operation = this.getNodeParameter('operation', 0) as string;
    const host = this.getNodeParameter('host', 0) as string;

    for (let i = 0; i < items.length; i++) {
      try {
        let responseData: any;

        if (operation === 'generate') {
          const prompt = this.getNodeParameter('prompt', i) as string;
          const negativePrompt = this.getNodeParameter('negativePrompt', i) as string;
          const width = this.getNodeParameter('width', i) as number;
          const height = this.getNodeParameter('height', i) as number;
          const checkpoint = this.getNodeParameter('checkpoint', i) as string;

          const workflow = this.buildWorkflow(prompt, negativePrompt, width, height, checkpoint);

          const response = await this.helpers.request({
            method: 'POST',
            url: `${host}/prompt`,
            body: { prompt: workflow, client_id: 'n8n-custom-node' },
            json: true,
          });

          responseData = { prompt_id: response.prompt_id, status: 'queued' };

        } else if (operation === 'status') {
          const promptId = this.getNodeParameter('promptId', i) as string;

          const response = await this.helpers.request({
            method: 'GET',
            url: `${host}/history/${promptId}`,
            json: true,
          });

          responseData = response[promptId] || { status: 'not_found' };

        } else if (operation === 'history') {
          const response = await this.helpers.request({
            method: 'GET',
            url: `${host}/history`,
            json: true,
          });

          responseData = response;

        } else if (operation === 'models') {
          const response = await this.helpers.request({
            method: 'GET',
            url: `${host}/object_info`,
            json: true,
          });

          const checkpoints = response.CheckpointLoaderSimple?.input?.required?.ckpt_name?.[0] || [];
          responseData = { checkpoints };
        }

        returnData.push({ json: responseData });
      } catch (error) {
        if (this.continueOnFail()) {
          returnData.push({ json: { error: error.message } });
          continue;
        }
        throw error;
      }
    }

    return [returnData];
  }

  private buildWorkflow(
    prompt: string,
    negativePrompt: string,
    width: number,
    height: number,
    checkpoint: string
  ): object {
    return {
      "3": {
        "inputs": {
          "seed": Math.floor(Math.random() * 1000000000),
          "steps": 25,
          "cfg": 7,
          "sampler_name": "euler_ancestral",
          "scheduler": "normal",
          "denoise": 1,
          "model": ["4", 0],
          "positive": ["6", 0],
          "negative": ["7", 0],
          "latent_image": ["5", 0]
        },
        "class_type": "KSampler"
      },
      "4": {
        "inputs": { "ckpt_name": checkpoint },
        "class_type": "CheckpointLoaderSimple"
      },
      "5": {
        "inputs": { "width": width, "height": height, "batch_size": 1 },
        "class_type": "EmptyLatentImage"
      },
      "6": {
        "inputs": { "text": prompt, "clip": ["4", 1] },
        "class_type": "CLIPTextEncode"
      },
      "7": {
        "inputs": { "text": negativePrompt, "clip": ["4", 1] },
        "class_type": "CLIPTextEncode"
      },
      "8": {
        "inputs": { "samples": ["3", 0], "vae": ["4", 2] },
        "class_type": "VAEDecode"
      },
      "9": {
        "inputs": { "filename_prefix": "n8n_", "images": ["8", 0] },
        "class_type": "SaveImage"
      }
    };
  }
}
```

### 4.2 MCP Gateway Integration Node

```javascript
// File: n8n-custom-nodes/nodes/MCPGateway/MCPGateway.node.ts

import {
  IExecuteFunctions,
  INodeExecutionData,
  INodeType,
  INodeTypeDescription,
} from 'n8n-workflow';

export class MCPGateway implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'MCP Gateway',
    name: 'mcpGateway',
    icon: 'file:mcp.svg',
    group: ['transform'],
    version: 1,
    subtitle: '={{$parameter["backend"] + "/" + $parameter["tool"]}}',
    description: 'Route requests through MCP Gateway to backend services',
    defaults: {
      name: 'MCP Gateway',
    },
    inputs: ['main'],
    outputs: ['main'],
    properties: [
      {
        displayName: 'MCP Gateway URL',
        name: 'gatewayUrl',
        type: 'string',
        default: 'http://mcp-gateway:8080',
      },
      {
        displayName: 'Backend',
        name: 'backend',
        type: 'options',
        options: [
          { name: 'ComfyUI', value: 'comfyui' },
          { name: 'Unity', value: 'unity' },
          { name: 'Unreal', value: 'unreal' },
          { name: 'Godot', value: 'godot' },
          { name: 'Sim Studio', value: 'sim_studio' },
          { name: 'Local LLM', value: 'local_llm' },
          { name: 'n8n', value: 'n8n' },
        ],
        default: 'comfyui',
      },
      {
        displayName: 'Tool',
        name: 'tool',
        type: 'string',
        default: '',
        description: 'The tool name to call on the backend',
      },
      {
        displayName: 'Arguments',
        name: 'arguments',
        type: 'json',
        default: '{}',
        description: 'JSON arguments to pass to the tool',
      },
    ],
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const items = this.getInputData();
    const returnData: INodeExecutionData[] = [];

    for (let i = 0; i < items.length; i++) {
      const gatewayUrl = this.getNodeParameter('gatewayUrl', i) as string;
      const backend = this.getNodeParameter('backend', i) as string;
      const tool = this.getNodeParameter('tool', i) as string;
      const args = this.getNodeParameter('arguments', i) as object;

      try {
        const response = await this.helpers.request({
          method: 'POST',
          url: `${gatewayUrl}/route`,
          body: {
            backend,
            tool,
            arguments: args,
          },
          json: true,
        });

        returnData.push({ json: response });
      } catch (error) {
        if (this.continueOnFail()) {
          returnData.push({ json: { error: error.message } });
          continue;
        }
        throw error;
      }
    }

    return [returnData];
  }
}
```

### 4.3 Custom Node Installation

```dockerfile
# Dockerfile for n8n with custom nodes
FROM n8nio/n8n:1.70.2

USER root

# Copy custom nodes
COPY --chown=node:node ./n8n-custom-nodes /home/node/.n8n/custom

# Install custom node dependencies
WORKDIR /home/node/.n8n/custom
RUN npm install

USER node
WORKDIR /home/node

CMD ["n8n", "start"]
```

---

## 5. AI/LLM Integration Patterns

### 5.1 OpenAI Integration Workflow

```json
{
  "name": "AI Prompt Enhancement",
  "nodes": [
    {
      "parameters": {
        "resource": "chat",
        "operation": "sendMessage",
        "model": "gpt-4o",
        "messages": {
          "values": [
            {
              "role": "system",
              "content": "You are an expert game asset prompt engineer. Enhance the given prompt for AI image generation, making it more detailed and specific for game asset creation. Focus on: visual style, lighting, perspective, and game-ready quality."
            },
            {
              "role": "user",
              "content": "={{ $json.prompt }}"
            }
          ]
        },
        "options": {
          "maxTokens": 500,
          "temperature": 0.7
        }
      },
      "name": "Enhance Prompt with GPT-4",
      "type": "@n8n/n8n-nodes-langchain.openAi",
      "typeVersion": 1
    }
  ]
}
```

### 5.2 Anthropic Claude Integration

```json
{
  "name": "Asset Quality Review",
  "nodes": [
    {
      "parameters": {
        "resource": "chat",
        "model": "claude-3-5-sonnet-20241022",
        "messages": {
          "values": [
            {
              "role": "user",
              "content": [
                {
                  "type": "image",
                  "image": "={{ $json.imageUrl }}"
                },
                {
                  "type": "text",
                  "text": "Analyze this game asset image. Rate it on a scale of AAA/AA/A/Poor based on:\n1. Visual quality and detail\n2. Style consistency\n3. Game-readiness (transparency, edges)\n4. Overall appeal\n\nProvide a JSON response with ratings and recommendations."
                }
              ]
            }
          ]
        },
        "options": {
          "maxTokens": 1000
        }
      },
      "name": "Claude Asset Review",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "credentials": {
        "httpHeaderAuth": {
          "name": "Anthropic API"
        }
      }
    }
  ]
}
```

### 5.3 Local Ollama Integration

```json
{
  "name": "Local LLM Processing",
  "nodes": [
    {
      "parameters": {
        "method": "POST",
        "url": "http://ollama:11434/api/generate",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "model",
              "value": "llama3.2:latest"
            },
            {
              "name": "prompt",
              "value": "={{ $json.prompt }}"
            },
            {
              "name": "stream",
              "value": false
            },
            {
              "name": "options",
              "value": {
                "temperature": 0.7,
                "num_predict": 500
              }
            }
          ]
        },
        "options": {
          "timeout": 120000
        }
      },
      "name": "Ollama Generate",
      "type": "n8n-nodes-base.httpRequest"
    }
  ]
}
```

### 5.4 Flowise LangChain Integration

```json
{
  "name": "Flowise Chain Execution",
  "nodes": [
    {
      "parameters": {
        "method": "POST",
        "url": "http://flowise:3000/api/v1/prediction/{{ $json.flowId }}",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "question",
              "value": "={{ $json.input }}"
            },
            {
              "name": "overrideConfig",
              "value": {
                "temperature": 0.8,
                "maxTokens": 1000
              }
            }
          ]
        }
      },
      "name": "Execute Flowise Chain",
      "type": "n8n-nodes-base.httpRequest"
    }
  ]
}
```

---

## 6. Workflow Templates

### 6.1 Agent Orchestration Workflow

```json
{
  "name": "Agent Orchestration Pipeline",
  "description": "Deploy and coordinate AI agents for game development tasks",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "orchestrate-agents",
        "responseMode": "responseNode"
      },
      "name": "Agent Trigger",
      "type": "n8n-nodes-base.webhook"
    },
    {
      "parameters": {
        "jsCode": "// Parse agent deployment request\nconst request = $input.first().json;\n\nconst agents = request.agents || ['ARTEMIS', 'HEPHAESTUS'];\nconst task = request.task;\nconst priority = request.priority || 'normal';\n\n// Define agent capabilities\nconst agentCapabilities = {\n  'ARTEMIS': { role: 'Art Director', skills: ['visual_direction', 'style_guides'] },\n  'LEONIDAS': { role: 'Character Artist', skills: ['character_design', 'animation'] },\n  'GAIA': { role: 'Environment Artist', skills: ['terrain', 'buildings', 'props'] },\n  'VULCAN': { role: 'VFX Artist', skills: ['particles', 'effects', 'shaders'] },\n  'HEPHAESTUS': { role: 'Tech Art Director', skills: ['optimization', 'lod', 'performance'] },\n  'DAEDALUS': { role: 'Pipeline Architect', skills: ['ci_cd', 'automation'] },\n  'ARGUS': { role: 'QA Lead', skills: ['testing', 'validation'] }\n};\n\n// Build agent deployment plan\nconst deploymentPlan = agents.map(agent => ({\n  agentId: agent,\n  ...agentCapabilities[agent],\n  task: task,\n  status: 'pending'\n}));\n\nreturn { json: { deploymentPlan, priority } };"
      },
      "name": "Build Deployment Plan",
      "type": "n8n-nodes-base.code"
    },
    {
      "parameters": {
        "fieldToSplitOut": "deploymentPlan"
      },
      "name": "Split Agents",
      "type": "n8n-nodes-base.splitOut"
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://sim-studio:8001/api/agents/deploy",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify($json) }}"
      },
      "name": "Deploy Agent",
      "type": "n8n-nodes-base.httpRequest"
    }
  ]
}
```

### 6.2 Knowledge Base Update Workflow

```json
{
  "name": "Knowledge Base Update Pipeline",
  "description": "Update knowledge base with new research and documentation",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [{ "field": "hours", "hoursInterval": 6 }]
        }
      },
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger"
    },
    {
      "parameters": {
        "url": "http://mcp-gateway:8080/memory/read_graph"
      },
      "name": "Read Current Graph",
      "type": "n8n-nodes-base.httpRequest"
    },
    {
      "parameters": {
        "jsCode": "// Analyze graph for stale entries\nconst graph = $input.first().json;\nconst now = Date.now();\nconst staleThreshold = 7 * 24 * 60 * 60 * 1000; // 7 days\n\nconst staleEntities = graph.entities?.filter(entity => {\n  const lastUpdated = new Date(entity.updatedAt || entity.createdAt).getTime();\n  return (now - lastUpdated) > staleThreshold;\n}) || [];\n\nreturn { json: { staleEntities, totalEntities: graph.entities?.length || 0 } };"
      },
      "name": "Find Stale Entries",
      "type": "n8n-nodes-base.code"
    },
    {
      "parameters": {
        "conditions": {
          "number": [{ "value1": "={{ $json.staleEntities.length }}", "operation": "larger", "value2": 0 }]
        }
      },
      "name": "Has Stale Entries?",
      "type": "n8n-nodes-base.if"
    }
  ]
}
```

### 6.3 Monitoring and Alerts Workflow

```json
{
  "name": "System Health Monitoring",
  "description": "Monitor Docker services and send alerts on failures",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [{ "field": "minutes", "minutesInterval": 5 }]
        }
      },
      "name": "Health Check Schedule",
      "type": "n8n-nodes-base.scheduleTrigger"
    },
    {
      "parameters": {
        "jsCode": "// Define services to check\nconst services = [\n  { name: 'ziggie-api', url: 'http://ziggie-api:8000/health' },\n  { name: 'mcp-gateway', url: 'http://mcp-gateway:8080/health' },\n  { name: 'ollama', url: 'http://ollama:11434/api/tags' },\n  { name: 'flowise', url: 'http://flowise:3000/api/v1/ping' },\n  { name: 'sim-studio', url: 'http://sim-studio:8001/health' },\n  { name: 'comfyui', url: 'http://comfyui:8188/system_stats' }\n];\n\nreturn services.map(s => ({ json: s }));"
      },
      "name": "List Services",
      "type": "n8n-nodes-base.code"
    },
    {
      "parameters": {
        "method": "GET",
        "url": "={{ $json.url }}",
        "options": {
          "timeout": 5000,
          "allowUnauthorizedCerts": true
        }
      },
      "name": "Check Service",
      "type": "n8n-nodes-base.httpRequest",
      "continueOnFail": true
    },
    {
      "parameters": {
        "jsCode": "// Aggregate health results\nconst results = $input.all();\nconst unhealthy = results.filter(r => r.json.error || r.json.statusCode >= 400);\n\nif (unhealthy.length > 0) {\n  return { json: { status: 'unhealthy', failedServices: unhealthy.map(u => u.json) } };\n}\nreturn { json: { status: 'healthy', checkedServices: results.length } };"
      },
      "name": "Aggregate Results",
      "type": "n8n-nodes-base.code"
    },
    {
      "parameters": {
        "conditions": {
          "string": [{ "value1": "={{ $json.status }}", "operation": "equals", "value2": "unhealthy" }]
        }
      },
      "name": "Is Unhealthy?",
      "type": "n8n-nodes-base.if"
    },
    {
      "parameters": {
        "method": "POST",
        "url": "={{ $env.DISCORD_WEBHOOK_URL }}",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "embeds",
              "value": [{
                "title": "Service Health Alert",
                "color": 15158332,
                "description": "One or more services are unhealthy",
                "fields": "={{ $json.failedServices.map(s => ({ name: s.name || 'Unknown', value: s.error || 'Error' })) }}"
              }]
            }
          ]
        }
      },
      "name": "Send Alert",
      "type": "n8n-nodes-base.httpRequest"
    }
  ]
}
```

---

## 7. Backup and Restore Procedures

### 7.1 Existing Backup Implementation

Located at: `C:\Ziggie\hostinger-vps\backup\scripts\backup-n8n.sh`

**Backup Methods**:
1. **CLI Export**: `n8n export:workflow --all` and `n8n export:credentials --all`
2. **API Export**: REST API fallback via `/api/v1/workflows`
3. **Data Directory**: Direct copy of `/home/node/.n8n`

**Retention Policy**:
- Daily: 7 backups
- Weekly: 4 backups (Sundays)
- Monthly: 3 backups (1st of month)

### 7.2 Recommended Backup Schedule (Cron)

```bash
# /etc/cron.d/n8n-backup
# Run daily at 02:45 UTC
45 2 * * * root /opt/ziggie/scripts/backup-n8n.sh >> /var/log/n8n-backup.log 2>&1

# Cleanup old backups weekly
0 3 * * 0 root /opt/ziggie/scripts/cleanup-backups.sh >> /var/log/backup-cleanup.log 2>&1
```

### 7.3 S3 Backup Upload

Add to `backup-n8n.sh`:

```bash
# Upload to S3 after local backup
if [ -f "${ARCHIVE_FILE}" ]; then
    aws s3 cp "${ARCHIVE_FILE}" \
        "s3://ziggie-backups/n8n/${BACKUP_TYPE}/" \
        --storage-class STANDARD_IA \
        --region eu-north-1

    echo "Uploaded to S3: s3://ziggie-backups/n8n/${BACKUP_TYPE}/$(basename ${ARCHIVE_FILE})"
fi
```

### 7.4 Restore Procedure

Located at: `C:\Ziggie\hostinger-vps\backup\scripts\restore-n8n.sh`

**Restore Methods**:
1. **CLI Import**: `n8n import:workflow --input=workflows.json`
2. **Data Directory Restore**: Volume mount restoration
3. **Manual Workflow Import**: For individual workflow JSON files

**Pre-Restore Checklist**:
- [ ] Stop n8n container
- [ ] Backup current state
- [ ] Verify backup file integrity
- [ ] Restore data
- [ ] Start n8n container
- [ ] Verify workflows via health check

### 7.5 Disaster Recovery Plan

```bash
#!/bin/bash
# disaster-recovery-n8n.sh

set -euo pipefail

echo "=== n8n Disaster Recovery ==="

# 1. Download latest backup from S3
LATEST_BACKUP=$(aws s3 ls s3://ziggie-backups/n8n/daily/ --recursive | sort | tail -1 | awk '{print $4}')
aws s3 cp "s3://ziggie-backups/n8n/${LATEST_BACKUP}" /tmp/n8n-recovery.tar.gz

# 2. Stop current n8n
docker stop ziggie-n8n || true

# 3. Clear corrupted data
docker volume rm ziggie_n8n_data || true
docker volume create ziggie_n8n_data

# 4. Restore from backup
/opt/ziggie/scripts/restore-n8n.sh /tmp/n8n-recovery.tar.gz

# 5. Restart n8n
docker start ziggie-n8n

# 6. Verify health
for i in {1..30}; do
    if curl -sf http://localhost:5678/healthz; then
        echo "n8n recovered successfully"
        exit 0
    fi
    sleep 2
done

echo "ERROR: n8n recovery failed"
exit 1
```

---

## 8. MCP Server Integration

### 8.1 n8n <-> MCP Gateway Communication

The MCP Gateway provides a unified interface for n8n to communicate with multiple backends:

```
n8n Workflow
    │
    ▼
┌─────────────────┐
│   HTTP Request  │
│   to MCP Gateway│
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│           MCP Gateway (Port 8080)       │
├─────────────────────────────────────────┤
│  /route - Route to specific backend     │
│  /unified_generate - Auto-select backend│
│  /search_kb - Search knowledge base     │
│  /status - Check backend health         │
└────────┬────────────────────────────────┘
         │
    ┌────┴────┬────────┬────────┬────────┐
    ▼         ▼        ▼        ▼        ▼
ComfyUI   Unity    Unreal   Godot   Ollama
(8188)    (8080)   (stdio)  (stdio)  (11434)
```

### 8.2 Workflow to MCP Pattern

```json
{
  "name": "MCP Unified Asset Generation",
  "nodes": [
    {
      "parameters": {
        "method": "POST",
        "url": "http://mcp-gateway:8080/unified_generate",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            { "name": "prompt", "value": "={{ $json.prompt }}" },
            { "name": "type", "value": "image" },
            { "name": "enhance_prompt", "value": true }
          ]
        }
      },
      "name": "MCP Generate",
      "type": "n8n-nodes-base.httpRequest"
    }
  ]
}
```

### 8.3 Memory Graph Updates via n8n

```json
{
  "name": "Update Memory Graph",
  "nodes": [
    {
      "parameters": {
        "method": "POST",
        "url": "http://mcp-gateway:8080/memory/create_entities",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "entities",
              "value": [
                {
                  "name": "={{ $json.entityName }}",
                  "entityType": "={{ $json.entityType }}",
                  "observations": "={{ $json.observations }}"
                }
              ]
            }
          ]
        }
      },
      "name": "Create Entity",
      "type": "n8n-nodes-base.httpRequest"
    }
  ]
}
```

---

## 9. Security Configuration Summary

### 9.1 Environment Variables Required

```bash
# Core n8n Security
N8N_ENCRYPTION_KEY=<32-character-key>
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=<strong-password>

# Webhook Security
WEBHOOK_AUTH_TOKEN=<random-token>
WEBHOOK_SIGNING_SECRET=<hmac-secret>

# API Keys (store in AWS Secrets Manager)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
MESHY_API_KEY=...
ELEVENLABS_API_KEY=...

# Database
DB_POSTGRESDB_PASSWORD=<strong-password>
REDIS_PASSWORD=<strong-password>
```

### 9.2 AWS Secrets Manager Integration

The n8n entrypoint script (`n8n-entrypoint.sh`) fetches secrets from AWS:

```bash
# Secrets stored in AWS Secrets Manager
ziggie/prod/n8n-encryption-key
ziggie/prod/postgres-master
ziggie/prod/openai-api-key
ziggie/prod/anthropic-api-key
ziggie/prod/meshy-api-key
ziggie/prod/elevenlabs-api-key
```

### 9.3 Security Checklist

- [x] HTTPS enabled via nginx
- [x] Basic authentication enabled
- [x] Rate limiting configured
- [x] Security headers set (X-Frame-Options, etc.)
- [ ] Webhook token authentication (IMPLEMENT)
- [ ] HMAC request signing (IMPLEMENT)
- [ ] IP allowlisting for webhooks (IMPLEMENT)
- [ ] Per-webhook rate limits (IMPLEMENT)
- [ ] Audit logging for workflow executions (IMPLEMENT)

---

## 10. Performance Optimization

### 10.1 Execution Queue Mode

Enable Redis-backed execution queue for reliability:

```yaml
environment:
  - EXECUTIONS_MODE=queue
  - QUEUE_BULL_REDIS_HOST=redis
  - QUEUE_BULL_REDIS_PORT=6379
  - QUEUE_BULL_REDIS_PASSWORD=${REDIS_PASSWORD}
```

### 10.2 Resource Limits

```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '2'
    reservations:
      memory: 512M
```

### 10.3 Execution Pruning

```yaml
environment:
  - EXECUTIONS_DATA_PRUNE=true
  - EXECUTIONS_DATA_MAX_AGE=168  # 7 days
```

### 10.4 Webhook Timeout Optimization

- ComfyUI generation: 120 seconds
- Meshy.ai processing: 300 seconds (5 minutes)
- Quality check: 30 seconds
- Standard API calls: 30 seconds

---

## 11. Troubleshooting Guide

### 11.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Webhook returns 502 | n8n not running | Check `docker ps`, restart container |
| Workflow stuck | Execution queue full | Increase worker count, check Redis |
| Credentials not found | Missing encryption key | Verify N8N_ENCRYPTION_KEY |
| S3 upload fails | IAM permissions | Check AWS credentials and bucket policy |
| ComfyUI timeout | Slow generation | Increase timeout, check GPU |

### 11.2 Debug Commands

```bash
# Check n8n logs
docker logs ziggie-n8n --tail 100 -f

# Check n8n health
curl http://localhost:5678/healthz

# List active workflows
docker exec ziggie-n8n n8n list:workflow

# Export workflow for debugging
docker exec ziggie-n8n n8n export:workflow --id=<workflow-id>

# Check execution history
docker exec ziggie-n8n n8n list:execution

# Test webhook connectivity
curl -X POST http://localhost:5678/webhook/generate-asset \
  -H "Content-Type: application/json" \
  -d '{"asset_type":"unit_sprite","prompt":"test cat warrior"}'
```

---

## 12. Appendix: File Locations

| File | Path | Purpose |
|------|------|---------|
| Docker Compose | `C:\Ziggie\hostinger-vps\docker-compose.yml` | Service definitions |
| n8n Entrypoint | `C:\Ziggie\scripts\n8n-entrypoint.sh` | Startup with AWS secrets |
| Backup Script | `C:\Ziggie\hostinger-vps\backup\scripts\backup-n8n.sh` | Workflow backup |
| Restore Script | `C:\Ziggie\hostinger-vps\backup\scripts\restore-n8n.sh` | Workflow restore |
| Nginx Config | `C:\Ziggie\hostinger-vps\nginx\nginx.conf` | Reverse proxy |
| Asset Pipeline | `C:\Ziggie\n8n-workflows\asset-generation-pipeline.json` | ComfyUI integration |
| Batch Pipeline | `C:\Ziggie\n8n-workflows\batch-generation.json` | Parallel processing |
| Quality Check | `C:\Ziggie\n8n-workflows\quality-check.json` | Asset validation |
| Meshy Pipeline | `C:\Ziggie\integrations\meshy\n8n-workflow-meshy.json` | 3D model generation |
| Env Template | `C:\Ziggie\hostinger-vps\.env.example` | Configuration template |

---

## 13. Next Steps and Recommendations

### 13.1 Immediate Actions (P0)

1. **Implement webhook authentication tokens** - Add X-Webhook-Token validation to all workflows
2. **Configure per-webhook rate limits** - Prevent abuse of generation endpoints
3. **Pin n8n version** - Change from `latest` to specific version (e.g., `1.70.2`)

### 13.2 Short-Term (P1)

1. **Build custom ComfyUI node** - Replace HTTP requests with dedicated node
2. **Create MCP Gateway node** - Simplify backend routing
3. **Implement HMAC signing** - For external webhook callers
4. **Set up S3 backup automation** - Daily uploads to S3

### 13.3 Long-Term (P2)

1. **Scale to worker mode** - Separate main and worker processes
2. **Build comprehensive monitoring dashboard** - Grafana integration
3. **Create workflow templates library** - Reusable patterns for common tasks
4. **Implement audit logging** - Track all workflow executions

---

*Document generated by L1 n8n Workflow Integration Research Agent*
*Last Updated: 2025-12-28*
