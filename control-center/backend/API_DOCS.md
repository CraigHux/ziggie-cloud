# Control Center Backend API Documentation

Base URL: `http://127.0.0.1:8080`

## Table of Contents
- [Health & Status](#health--status)
- [System Monitoring](#system-monitoring)
- [Service Control](#service-control)
- [Knowledge Base](#knowledge-base)
- [WebSockets](#websockets)

---

## Health & Status

### GET /
Root endpoint with API information.

**Response:**
```json
{
  "name": "Control Center Backend",
  "version": "1.0.0",
  "status": "running"
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## System Monitoring

### GET /api/system/stats
Get current system statistics (CPU, RAM, Disk usage).

**Response:**
```json
{
  "success": true,
  "timestamp": "2025-11-07T12:34:56.789",
  "cpu": {
    "usage_percent": 45.2,
    "count": 8,
    "frequency": {
      "current": 2400.0,
      "min": 800.0,
      "max": 3600.0
    }
  },
  "memory": {
    "total": 17179869184,
    "available": 8589934592,
    "used": 8589934592,
    "percent": 50.0,
    "total_gb": 16.0,
    "used_gb": 8.0,
    "available_gb": 8.0
  },
  "disk": {
    "total": 1000000000000,
    "used": 500000000000,
    "free": 500000000000,
    "percent": 50.0,
    "total_gb": 931.32,
    "used_gb": 465.66,
    "free_gb": 465.66
  }
}
```

### GET /api/system/processes
Get list of running processes (top 50 by CPU usage).

**Response:**
```json
{
  "success": true,
  "count": 50,
  "processes": [
    {
      "pid": 1234,
      "name": "python.exe",
      "cpu_percent": 15.5,
      "memory_percent": 2.3,
      "status": "running"
    }
  ]
}
```

### GET /api/system/ports
Get list of open ports in configured range (3000-9000).

**Response:**
```json
{
  "success": true,
  "count": 5,
  "ports": [
    {
      "port": 8080,
      "pid": 5678,
      "process_name": "python.exe",
      "status": "LISTEN",
      "address": "127.0.0.1"
    }
  ]
}
```

---

## Service Control

### GET /api/services
List all configured services and their status.

**Response:**
```json
{
  "success": true,
  "count": 2,
  "services": [
    {
      "name": "ComfyUI",
      "status": "running",
      "pid": 9876,
      "port": 8188
    },
    {
      "name": "Knowledge Base Scheduler",
      "status": "stopped",
      "pid": null,
      "port": null
    }
  ]
}
```

### GET /api/services/{service_name}/status
Get status of a specific service.

**Parameters:**
- `service_name`: Service identifier (e.g., "comfyui", "kb_scheduler")

**Response:**
```json
{
  "success": true,
  "name": "ComfyUI",
  "status": "running",
  "pid": 9876,
  "port": 8188
}
```

### POST /api/services/{service_name}/start
Start a service.

**Parameters:**
- `service_name`: Service identifier

**Response (Success):**
```json
{
  "success": true,
  "pid": 9876,
  "message": "Service comfyui started successfully"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Service comfyui is already running"
}
```

### POST /api/services/{service_name}/stop
Stop a running service.

**Parameters:**
- `service_name`: Service identifier

**Response:**
```json
{
  "success": true,
  "message": "Service comfyui stopped successfully"
}
```

### GET /api/services/{service_name}/logs
Get recent logs from a service.

**Parameters:**
- `service_name`: Service identifier
- `lines`: Number of lines to retrieve (default: 100)

**Response:**
```json
{
  "success": true,
  "logs": [
    "2025-11-07 12:34:56 - INFO - Server started",
    "2025-11-07 12:35:00 - INFO - Request processed"
  ],
  "total_lines": 1523
}
```

---

## Knowledge Base

### GET /api/knowledge/stats
Get overall knowledge base statistics.

**Response:**
```json
{
  "total_creators": 150,
  "total_files": 487,
  "total_size_bytes": 15728640,
  "total_size_mb": 15.0,
  "recent_files_7d": 23,
  "files_by_agent": {
    "art-director": 85,
    "character-pipeline": 120,
    "knowledge-base": 282
  },
  "last_scan": "2025-11-07T12:34:56.789",
  "kb_status": "active"
}
```

### GET /api/knowledge/files
List knowledge base files with pagination.

**Query Parameters:**
- `agent`: Filter by agent name (optional)
- `category`: Filter by category (optional)
- `limit`: Number of results (default: 50, max: 500)
- `offset`: Pagination offset (default: 0)

**Response:**
```json
{
  "total": 487,
  "limit": 50,
  "offset": 0,
  "files": [
    {
      "path": "C:/meowping-rts/ai-agents/knowledge-base/L1-foundation/file.md",
      "name": "file.md",
      "agent": "knowledge-base",
      "size": 4096,
      "modified": "2025-11-07T10:30:00",
      "category": "L1-foundation"
    }
  ]
}
```

### GET /api/knowledge/files/{file_id}
Get detailed information about a specific KB file.

**Parameters:**
- `file_id`: Base64 encoded file path

**Response:**
```json
{
  "path": "C:/path/to/file.md",
  "name": "file.md",
  "size": 4096,
  "created": "2025-11-01T08:00:00",
  "modified": "2025-11-07T10:30:00",
  "insights": {
    "title": "Document Title",
    "sections": 5,
    "word_count": 1250,
    "confidence": 85,
    "has_code": true,
    "has_links": true
  }
}
```

### GET /api/knowledge/creators
List YouTube creators from the database.

**Query Parameters:**
- `priority`: Filter by priority tier (optional)
- `search`: Search by name or focus (optional)

**Response:**
```json
{
  "total": 150,
  "creators": [
    {
      "id": "creator-123",
      "name": "Creator Name",
      "focus": "Game Development",
      "priority": "high",
      "channel_url": "https://youtube.com/@creator"
    }
  ],
  "priority_tiers": {
    "high": "Daily monitoring",
    "medium": "Weekly monitoring",
    "low": "Monthly monitoring"
  }
}
```

### GET /api/knowledge/creators/{creator_id}
Get detailed information about a specific creator.

**Parameters:**
- `creator_id`: Creator identifier

**Response:**
```json
{
  "id": "creator-123",
  "name": "Creator Name",
  "focus": "Game Development",
  "priority": "high",
  "channel_url": "https://youtube.com/@creator",
  "related_files": 15,
  "files": [
    {
      "path": "C:/path/to/file.md",
      "name": "creator-123-insights.md"
    }
  ]
}
```

### POST /api/knowledge/scan
Trigger a manual knowledge base scan.

**Query Parameters:**
- `creator_id`: Scan specific creator (optional)
- `priority`: Scan by priority tier (optional)

**Response:**
```json
{
  "status": "started",
  "pid": 12345,
  "command": "python manage.py scan",
  "message": "Scan job started. Check /api/knowledge/jobs for status.",
  "timestamp": "2025-11-07T12:34:56.789"
}
```

### GET /api/knowledge/jobs
Get knowledge base scan job history.

**Response:**
```json
{
  "total": 15,
  "jobs": [
    {
      "log_file": "scan_20251107_123456.log",
      "timestamp": "2025-11-07T12:34:56",
      "size": 8192,
      "status": "completed",
      "videos_processed": 25,
      "insights_extracted": 150
    }
  ]
}
```

### GET /api/knowledge/search
Search knowledge base content.

**Query Parameters:**
- `query`: Search query (required, min 2 chars)
- `agent`: Filter by agent name (optional)
- `limit`: Number of results (default: 20, max: 100)

**Response:**
```json
{
  "query": "unity optimization",
  "total_matches": 42,
  "results": [
    {
      "path": "C:/path/to/file.md",
      "name": "optimization-guide.md",
      "agent": "character-pipeline",
      "match_count": 8,
      "preview": "Unity optimization techniques include..."
    }
  ]
}
```

---

## WebSockets

### WS /api/system/ws
Real-time system statistics updates (every 2 seconds).

**Message Format:**
```json
{
  "type": "system_stats",
  "timestamp": "2025-11-07T12:34:56.789",
  "cpu": {
    "usage_percent": 45.2
  },
  "memory": {
    "total": 17179869184,
    "used": 8589934592,
    "percent": 50.0,
    "used_gb": 8.0,
    "total_gb": 16.0
  },
  "disk": {
    "total": 1000000000000,
    "used": 500000000000,
    "percent": 50.0,
    "used_gb": 465.66,
    "total_gb": 931.32
  }
}
```

**Example (JavaScript):**
```javascript
const ws = new WebSocket('ws://127.0.0.1:8080/api/system/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('CPU:', data.cpu.usage_percent + '%');
    console.log('RAM:', data.memory.percent + '%');
};
```

### WS /api/services/ws
Real-time service status updates (every 2 seconds).

**Message Format:**
```json
{
  "type": "service_status",
  "timestamp": "2025-11-07T12:34:56.789",
  "services": [
    {
      "name": "ComfyUI",
      "status": "running",
      "pid": 9876,
      "port": 8188
    }
  ]
}
```

**Example (JavaScript):**
```javascript
const ws = new WebSocket('ws://127.0.0.1:8080/api/services/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    data.services.forEach(service => {
        console.log(service.name + ':', service.status);
    });
};
```

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error message description"
}
```

HTTP Status Codes:
- `200` - Success
- `404` - Not Found
- `500` - Internal Server Error

---

## CORS Configuration

The backend allows requests from:
- `http://localhost:3000` (React dev server)

To add more origins, edit `config.py`:
```python
CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
```

---

## Service Configuration

Configured services (in `config.py`):

1. **ComfyUI**
   - Port: 8188
   - Command: `C:\ComfyUI\python_embeded\python.exe -s main.py --windows-standalone-build --cpu`
   - Working Directory: `C:\ComfyUI`

2. **Knowledge Base Scheduler**
   - No specific port
   - Command: `python manage.py schedule`
   - Working Directory: `C:\meowping-rts\ai-agents`

To add a new service:
```python
"my_service": {
    "name": "My Service",
    "command": ["python", "script.py"],
    "cwd": r"C:\path\to\service",
    "port": 3000,
    "log_file": "my_service.log"
}
```

---

## Testing

Run the test suite:
```bash
python test_server.py
```

This will test all endpoints and report results.
