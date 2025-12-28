# Ziggie Control Center API Documentation

> **Version**: 1.0.0
> **Base URL**: `http://localhost:54112`
> **Last Updated**: 2025-12-28

---

## Overview

The Ziggie Control Center Backend provides a RESTful API for managing the AI development ecosystem. It includes endpoints for system monitoring, service control, agent management, knowledge base operations, and LLM integration.

### Authentication

Most endpoints require authentication via Bearer token:

```
Authorization: Bearer <your-jwt-token>
```

Public endpoints (no auth required):
- Health checks (`/health/*`)
- LLM status (`/api/llm/status`)
- Root endpoint (`/`)

### Rate Limiting

API endpoints are rate-limited using SlowAPI:
- General endpoints: 60 requests/minute
- Service control: 10 requests/minute
- Health endpoints: 100 requests/minute

### Response Format

All responses follow this structure:

```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2025-12-28T12:00:00.000000"
}
```

Error responses:

```json
{
  "success": false,
  "error": "Error message",
  "code": 400
}
```

---

## Health Endpoints

Base path: `/health`

### GET /health
Basic health check - returns 200 if service is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-28T12:00:00.000000",
  "version": "1.0.0"
}
```

### GET /health/detailed
Detailed health check with system metrics.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-28T12:00:00.000000",
  "version": "1.0.0",
  "system": {
    "cpu_percent": 25.5,
    "cpu_count": 8,
    "memory_percent": 60.2,
    "memory_used_gb": 15.5,
    "memory_available_gb": 16.5,
    "memory_total_gb": 32.0,
    "disk_percent": 45.3,
    "disk_used_gb": 234.5,
    "disk_free_gb": 277.5,
    "disk_total_gb": 512.0
  },
  "python_version": "3.11.x",
  "process_id": 12345,
  "working_directory": "C:\\Ziggie\\control-center\\backend"
}
```

Status values: `healthy`, `warning` (>90% usage), `critical` (>95% usage)

### GET /health/ready
Kubernetes readiness probe.

**Response:**
```json
{
  "ready": true,
  "status": "ready",
  "checks": {
    "service": true,
    "system": true
  },
  "timestamp": "2025-12-28T12:00:00.000000"
}
```

### GET /health/live
Kubernetes liveness probe.

**Response:**
```json
{
  "alive": true,
  "timestamp": "2025-12-28T12:00:00.000000"
}
```

### GET /health/startup
Kubernetes startup probe.

**Response:**
```json
{
  "startup_complete": true,
  "timestamp": "2025-12-28T12:00:00.000000",
  "version": "1.0.0"
}
```

---

## System Endpoints

Base path: `/api/system`

### GET /api/system/stats
Get current system statistics (CPU, RAM, Disk).

**Rate Limit:** 60/minute

**Response:**
```json
{
  "success": true,
  "timestamp": "2025-12-28T12:00:00.000000",
  "cpu": {
    "usage_percent": 25.5,
    "count": 8,
    "frequency": {
      "current": 3600.0,
      "min": 800.0,
      "max": 4500.0
    }
  },
  "memory": {
    "total": 34359738368,
    "available": 17179869184,
    "used": 17179869184,
    "percent": 50.0,
    "total_gb": 32.0,
    "used_gb": 16.0,
    "available_gb": 16.0
  },
  "disk": {
    "total": 549755813888,
    "used": 274877906944,
    "free": 274877906944,
    "percent": 50.0,
    "total_gb": 512.0,
    "used_gb": 256.0,
    "free_gb": 256.0
  }
}
```

---

## Services Endpoints

Base path: `/api/services`

### GET /api/services
Get list of all configured services and their status.

**Rate Limit:** 60/minute

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | int | 1 | Page number (1-indexed) |
| page_size | int | 50 | Items per page (max 200) |
| offset | int | null | Alternative to page: start offset |

**Response:**
```json
{
  "success": true,
  "services": [
    {
      "id": "comfyui",
      "name": "ComfyUI",
      "status": "running",
      "pid": 12345,
      "port": 8188,
      "uptime": 3600
    }
  ],
  "count": 5,
  "meta": {
    "page": 1,
    "page_size": 50,
    "total": 5,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### POST /api/services/{service_name}/start
Start a specific service.

**Rate Limit:** 10/minute

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| service_name | string | Service identifier |

**Response:**
```json
{
  "success": true,
  "message": "Service started successfully",
  "service": {
    "name": "comfyui",
    "status": "running",
    "pid": 12345
  }
}
```

### POST /api/services/{service_name}/stop
Stop a specific service.

**Rate Limit:** 10/minute

### POST /api/services/{service_name}/restart
Restart a specific service.

**Rate Limit:** 10/minute

---

## Agents Endpoints

Base path: `/api/agents`

### GET /api/agents
Get list of all agents in the hierarchy.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| level | string | null | Filter by level (L1, L2, L3) |
| status | string | null | Filter by status (active, idle, error) |
| page | int | 1 | Page number |
| page_size | int | 50 | Items per page |

**Response:**
```json
{
  "success": true,
  "agents": [
    {
      "id": "L1.1",
      "name": "Art Director",
      "level": "L1",
      "status": "active",
      "last_run": "2025-12-28T11:30:00.000000",
      "responsibilities": ["Visual direction", "Style guides"]
    }
  ],
  "count": 584,
  "meta": {
    "page": 1,
    "total": 584,
    "total_pages": 12
  }
}
```

### GET /api/agents/{agent_id}
Get detailed information about a specific agent.

**Response:**
```json
{
  "success": true,
  "agent": {
    "id": "L1.1",
    "name": "Art Director",
    "level": "L1",
    "role": "Oversees visual direction and style consistency",
    "objective": "Maintain cohesive visual identity across all game assets",
    "status": "active",
    "responsibilities": [
      "Visual direction oversight",
      "Style guide enforcement",
      "Asset quality review"
    ],
    "permissions": {
      "read_write": ["assets/", "config/"],
      "read_only": ["knowledge-base/"]
    }
  }
}
```

---

## Knowledge Base Endpoints

Base path: `/api/knowledge`

### GET /api/knowledge/files
Get list of knowledge base files.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| agent | string | null | Filter by agent directory |
| page | int | 1 | Page number |
| page_size | int | 50 | Items per page |

**Response:**
```json
{
  "success": true,
  "files": [
    {
      "path": "C:/ai-game-dev-system/knowledge-base/comfyui/workflows.md",
      "name": "workflows.md",
      "agent": "art-director",
      "size": 15234,
      "modified": "2025-12-28T10:00:00.000000"
    }
  ],
  "count": 60,
  "meta": {
    "total": 60,
    "page": 1
  }
}
```

### GET /api/knowledge/creators
Get list of knowledge creators.

**Response:**
```json
{
  "success": true,
  "creators": [
    {
      "id": "creator-1",
      "name": "InstaSD",
      "platform": "YouTube",
      "specialty": "ComfyUI Workflows"
    }
  ],
  "total_creators": 38
}
```

### GET /api/knowledge/search
Search knowledge base content.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| q | string | Search query |
| agent | string | Filter by agent |

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "file": "ip-adapter-guide.md",
      "matches": 5,
      "snippet": "...IP-Adapter workflow configuration..."
    }
  ],
  "total": 12
}
```

---

## LLM Endpoints

Base path: `/api/llm`

### GET /api/llm
Get LLM API information and available endpoints.

**Response:**
```json
{
  "service": "Ziggie LLM API",
  "version": "1.0.0",
  "ollama_url": "http://localhost:11434",
  "endpoints": {
    "status": "GET /api/llm/status",
    "models": "GET /api/llm/models",
    "generate": "POST /api/llm/generate",
    "chat": "POST /api/llm/chat"
  }
}
```

### GET /api/llm/status
Get Ollama service status (public endpoint).

**Response:**
```json
{
  "status": "online",
  "ollama_version": "0.1.x",
  "url": "http://localhost:11434"
}
```

### GET /api/llm/models
List available Ollama models (requires auth).

**Response:**
```json
{
  "models": [
    {
      "name": "llama3.2",
      "size": "4.7GB",
      "modified": "2025-12-28T10:00:00.000000"
    }
  ]
}
```

### POST /api/llm/generate
Generate text completion (requires auth).

**Request Body:**
```json
{
  "model": "llama3.2",
  "prompt": "Explain game asset pipelines",
  "stream": false,
  "temperature": 0.7,
  "max_tokens": 1024
}
```

**Response:**
```json
{
  "response": "Game asset pipelines are...",
  "model": "llama3.2",
  "created_at": "2025-12-28T12:00:00.000000"
}
```

### POST /api/llm/chat
Chat completion with history (requires auth).

**Request Body:**
```json
{
  "model": "llama3.2",
  "messages": [
    {"role": "system", "content": "You are a game development assistant."},
    {"role": "user", "content": "How do I optimize textures?"}
  ],
  "stream": false,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "message": {
    "role": "assistant",
    "content": "To optimize textures..."
  },
  "model": "llama3.2"
}
```

---

## WebSocket Endpoints

### WS /ws
Real-time system statistics (public, no auth).

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:54112/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

**Message Format (every 2 seconds):**
```json
{
  "type": "system_stats",
  "timestamp": "2025-12-28T12:00:00.000000",
  "cpu": {
    "usage": 25.5
  },
  "memory": {
    "percent": 60.2,
    "used_gb": 15.5,
    "total_gb": 32.0
  },
  "disk": {
    "percent": 45.3,
    "used_gb": 234.5,
    "total_gb": 512.0
  }
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Missing or invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource does not exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

---

## Interactive Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:54112/docs
- **ReDoc**: http://localhost:54112/redoc
- **OpenAPI JSON**: http://localhost:54112/openapi.json

---

## Code Examples

### Python (requests)

```python
import requests

BASE_URL = "http://localhost:54112"

# Health check
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# Get system stats (with auth)
headers = {"Authorization": "Bearer your-token"}
response = requests.get(f"{BASE_URL}/api/system/stats", headers=headers)
print(response.json())
```

### JavaScript (fetch)

```javascript
const BASE_URL = 'http://localhost:54112';

// Health check
fetch(`${BASE_URL}/health`)
  .then(res => res.json())
  .then(data => console.log(data));

// Get agents with auth
fetch(`${BASE_URL}/api/agents`, {
  headers: {
    'Authorization': 'Bearer your-token'
  }
})
  .then(res => res.json())
  .then(data => console.log(data));
```

### cURL

```bash
# Health check
curl http://localhost:54112/health

# Get system stats
curl -H "Authorization: Bearer your-token" http://localhost:54112/api/system/stats

# Chat with LLM
curl -X POST http://localhost:54112/api/llm/chat \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"model":"llama3.2","messages":[{"role":"user","content":"Hello"}]}'
```

---

*Ziggie Control Center API Documentation*
*Version 1.0.0 - Created 2025-12-28*
